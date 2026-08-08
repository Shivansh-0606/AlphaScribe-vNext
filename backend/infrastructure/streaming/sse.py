"""Reusable SSE transport (M2 Phase 1 "Streaming Infrastructure" scope).

Generic over any `EventBus.subscribe()` iterator — the SAME helper is meant
to serve both the existing report stream (once Phase 4/6 cuts
`stream_report` over to the new job lifecycle) and the future Learning
stream, so the framing is defined exactly once.

Framing matches what tests/contract/test_sse_event_shape.py already proved
the shipped frontend (web/lib/api/sse-client.ts) actually expects — NOT what
the stale API doc describes (01 D-11): unnamed `data:` frames, a `: keepalive`
comment (never a named event — comments never fire `onmessage`), and a
terminal named `event: end`.

Wired into server.py's live `GET /reports/{job_id}/stream` and
`GET /learning/{id}/stream` since the Migration Phase 4/L cutover (both call
`sse_response()` directly) — this module has been the live SSE path since
then, not merely a standalone-proven target awaiting cutover (a stale claim
this docstring carried past that cutover; corrected in M6 — see
`docs/backend_engineering/26_M6_Observability_Architecture_Review.md` A3).
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import AsyncIterator

from fastapi.responses import StreamingResponse

from domain.events import TraceEvent
from infrastructure.observability.logging import get_correlation_id
from infrastructure.observability.metrics import sse_session_duration_seconds, sse_sessions_total
from infrastructure.observability.tracing import get_tracer

_KEEPALIVE_NODE = "_keepalive"  # matches infrastructure/redis/event_bus.py's sentinel

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}

logger = logging.getLogger("alphascribe")


async def _frame_events(events: AsyncIterator[TraceEvent], *, stream_name: str) -> AsyncIterator[str]:
    # M6 — SSE instrumentation (04 O-2/O-10 adjacent: the pipeline trace
    # exists but a stream *session's* own lifecycle — how long a client
    # stayed connected, how many events it actually received before
    # disconnecting/erroring — was invisible). One span for the whole
    # session; a request-scoped correlation id (already set by server.py's
    # middleware) ties it back to the HTTP access log line.
    start = time.monotonic()
    count = 0
    outcome = "unknown"
    correlation_id = get_correlation_id()
    with get_tracer().start_as_current_span(f"sse.{stream_name}"):
        try:
            async for ev in events:
                if ev.get("node") == _KEEPALIVE_NODE:
                    yield ": keepalive\n\n"
                    continue
                count += 1
                yield f"data: {json.dumps(ev, default=str)}\n\n"
            # The upstream EventBus iterator only exhausts naturally after a
            # terminal event (is_terminal_event) — reaching here means the
            # stream genuinely completed. Recorded BEFORE the final yield,
            # not after: a well-behaved client stops calling __anext__() the
            # moment it sees "event: end" and never resumes this generator
            # past that yield, so `aclose()` raises GeneratorExit AT that
            # suspended yield — indistinguishable from a real disconnect if
            # outcome were only set after it. This is the fix for a real bug
            # a first version of this code had: every normal completion was
            # being counted as "cancelled" (caught by the GeneratorExit
            # handler below), because that handler ran unconditionally.
            outcome = "completed"
            yield "event: end\ndata: {}\n\n"
        except (GeneratorExit, asyncio.CancelledError):
            # Client disconnected mid-stream — must re-raise un-swallowed
            # (a generator that eats GeneratorExit is a bug). Only downgrade
            # to "cancelled" if the stream hadn't already completed (see the
            # comment above) — the terminal yield being closed immediately
            # after is the expected shape of every successful stream, not a
            # cancellation.
            if outcome != "completed":
                outcome = "cancelled"
            raise
        except Exception:
            outcome = "error"
            raise
        finally:
            duration = time.monotonic() - start
            sse_sessions_total.labels(stream_name=stream_name, outcome=outcome).inc()
            sse_session_duration_seconds.labels(stream_name=stream_name).observe(duration)
            logger.info(
                "sse stream %s ended: correlation_id=%s events=%d duration_s=%.2f outcome=%s",
                stream_name, correlation_id, count, duration, outcome,
            )


def sse_response(events: AsyncIterator[TraceEvent], *, stream_name: str = "stream") -> StreamingResponse:
    """The one place `media_type`/headers/terminal-framing are decided —
    every SSE endpoint (existing and future) should construct its response
    through this, not re-derive the framing per route. `stream_name` is a
    label only (e.g. "report", "learning") — not part of the wire framing."""
    return StreamingResponse(
        _frame_events(events, stream_name=stream_name), media_type="text/event-stream", headers=SSE_HEADERS
    )
