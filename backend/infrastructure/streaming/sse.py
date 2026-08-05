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

NOT wired into server.py's live `GET /reports/{job_id}/stream` this phase —
that handler still uses its own single-`asyncio.Queue` generator exactly as
today (01 D-1 unfixed there; fixing it in place is explicitly Migration
Phase 4 work, 06 §7, because it needs the job lifecycle — application/jobs.py
— cut over at the same time, not this phase's job lifecycle module used only
standalone). This module is the target `stream_report` migrates onto, built
and proven correct in isolation first — the same strangler-fig discipline as
everything else in this phase (06 AD-4).
"""
from __future__ import annotations

import json
import logging
import time
from typing import AsyncIterator

from fastapi.responses import StreamingResponse

from domain.events import TraceEvent
from infrastructure.observability.logging import get_correlation_id
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
    correlation_id = get_correlation_id()
    with get_tracer().start_as_current_span(f"sse.{stream_name}"):
        try:
            async for ev in events:
                if ev.get("node") == _KEEPALIVE_NODE:
                    yield ": keepalive\n\n"
                    continue
                count += 1
                yield f"data: {json.dumps(ev, default=str)}\n\n"
            yield "event: end\ndata: {}\n\n"
        finally:
            logger.info(
                "sse stream %s ended: correlation_id=%s events=%d duration_s=%.2f",
                stream_name, correlation_id, count, time.monotonic() - start,
            )


def sse_response(events: AsyncIterator[TraceEvent], *, stream_name: str = "stream") -> StreamingResponse:
    """The one place `media_type`/headers/terminal-framing are decided —
    every SSE endpoint (existing and future) should construct its response
    through this, not re-derive the framing per route. `stream_name` is a
    label only (e.g. "report", "learning") — not part of the wire framing."""
    return StreamingResponse(
        _frame_events(events, stream_name=stream_name), media_type="text/event-stream", headers=SSE_HEADERS
    )
