"""Contract test: the SSE stream's event envelope and cancellation response
shape must match what web/lib/api/sse-client.ts and
company-research/integration/schemas.ts actually expect — not what
05-API-Documentation.md claims (that doc is stale per 01 D-11: it describes
`event: pipeline` / `{"stage":...}` framing that was never implemented).

This cannot exercise a live stream hermetically (that needs a running job —
covered by the existing `test_sse_stream` in backend_test.py, marked `live`).
What IS hermetic and worth locking down here: the exact wire framing every
SSE endpoint (reports today, Learning too) emits through the shared
`infrastructure/streaming/sse.py::sse_response` transport, and the cancel
endpoint's response model — both exercisable without a running server.

M2 Phase 4 note: `stream_report` now delegates its framing entirely to
`sse_response()` (01 D-1's fan-out fix — see 14_M2_Phase1_Implementation_Report.md
§Streaming Infrastructure), so this asserts against the real transport by
driving actual events through it, rather than grepping `stream_report`'s own
source for framing literals that no longer live there.

    python -m pytest backend/tests/contract/test_sse_event_shape.py -v
"""
import asyncio
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_contract_test")

import server  # noqa: E402


def _collect_frames(events: list[dict]) -> list[str]:
    async def _gen():
        for ev in events:
            yield ev

    async def _drive():
        response = server.sse_response(_gen())
        return [chunk async for chunk in response.body_iterator]

    return asyncio.run(_drive())


def test_stream_uses_unnamed_data_frames_and_a_named_end_event():
    """web/lib/api/sse-client.ts:26-37 attaches a plain `onmessage` handler
    (unnamed `data:` frames) and a named `end` event listener. The shared SSE
    transport must keep emitting exactly that framing — a named `event:
    pipeline` frame (what the stale API doc describes) would silently stop
    reaching the frontend's onmessage handler at all."""
    frames = _collect_frames([{"node": "pipeline", "status": "start"}])
    assert frames[0].startswith("data: ")
    assert frames[0].endswith("\n\n")
    assert frames[-1] == "event: end\ndata: {}\n\n"
    joined = "".join(frames)
    assert "event: pipeline" not in joined
    assert "event: done" not in joined


def test_stream_emits_a_keepalive_comment_not_a_named_event():
    # SSE comments (`: ...`) never fire onmessage/addEventListener — that is
    # exactly why keepalive is a comment and not a real event.
    frames = _collect_frames([{"node": "_keepalive", "status": "ok"}])
    assert frames[0] == ": keepalive\n\n"


def test_stream_report_uses_the_shared_sse_transport():
    """Guards against a future regression back to a bespoke per-route
    generator (01 D-1's original defect) — stream_report must construct its
    response through sse_response(), not hand-roll StreamingResponse again."""
    src = inspect.getsource(server.stream_report)
    assert "sse_response(" in src


def test_cancel_response_shape_matches_the_frontend_schema():
    """cancelReportResponseSchema (company-research/integration/schemas.ts)
    requires {job_id, status} with an optional `note` — server.py's two
    return sites for POST /reports/{job_id}/cancel must both satisfy it."""
    src = inspect.getsource(server.cancel_report)
    # Both return statements construct a dict with these two required keys.
    assert src.count('"job_id": job_id') >= 2
    assert src.count('"status"') >= 2


if __name__ == "__main__":
    test_stream_uses_unnamed_data_frames_and_a_named_end_event()
    test_stream_emits_a_keepalive_comment_not_a_named_event()
    test_stream_report_uses_the_shared_sse_transport()
    test_cancel_response_shape_matches_the_frontend_schema()
    print("ok: SSE framing matches sse-client.ts, not the stale API doc; cancel response shape intact")
