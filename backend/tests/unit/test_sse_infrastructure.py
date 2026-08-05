"""Unit check for infrastructure/streaming/sse.py — the framing that
tests/contract/test_sse_event_shape.py already proved the shipped frontend
expects: unnamed `data:` frames, a `: keepalive` comment, terminal
`event: end`. End-to-end here through a real EventBus (in-memory), not a
hand-built event list — proves the transport composes with the actual port,
not just with dict literals.

    python backend/tests/unit/test_sse_infrastructure.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from infrastructure.redis.event_bus import InMemoryEventBus
from infrastructure.streaming.sse import SSE_HEADERS, sse_response


async def _collect_frames(response, limit=20):
    out = []
    async for chunk in response.body_iterator:
        out.append(chunk)
        if len(out) >= limit or (out and out[-1] == "event: end\ndata: {}\n\n"):
            break
    return out


def test_end_to_end_through_a_real_event_bus():
    async def run():
        bus = InMemoryEventBus()
        job_id = "job-sse-1"
        await bus.publish(job_id, {"node": "pipeline", "status": "start"})
        await bus.publish(job_id, {"node": "retriever", "status": "ok", "count": 3})
        await bus.publish(job_id, {"node": "pipeline", "status": "ok"})  # terminal

        response = sse_response(bus.subscribe(job_id))
        frames = await asyncio.wait_for(_collect_frames(response), timeout=5)

        assert frames[0] == 'data: {"node": "pipeline", "status": "start"}\n\n'
        assert frames[1] == 'data: {"node": "retriever", "status": "ok", "count": 3}\n\n'
        assert frames[2] == 'data: {"node": "pipeline", "status": "ok"}\n\n'
        assert frames[3] == "event: end\ndata: {}\n\n"
        assert len(frames) == 4  # nothing after the terminal frame

    asyncio.run(run())


def test_keepalive_sentinel_becomes_a_comment_not_a_named_event():
    async def fake_events():
        yield {"node": "_keepalive", "status": "ok"}
        yield {"node": "pipeline", "status": "ok"}  # terminal, stop iteration after this

    response = sse_response(fake_events())
    frames = asyncio.run(asyncio.wait_for(_collect_frames(response), timeout=5))
    assert frames[0] == ": keepalive\n\n"
    assert "event:" not in frames[0]  # never a named event — comments don't fire onmessage


def test_headers_match_the_existing_report_stream_contract():
    assert SSE_HEADERS == {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Connection": "keep-alive",
    }


def test_media_type_is_event_stream():
    async def empty():
        return
        yield  # pragma: no cover — makes this an async generator

    response = sse_response(empty())
    assert response.media_type == "text/event-stream"


if __name__ == "__main__":
    test_end_to_end_through_a_real_event_bus()
    test_keepalive_sentinel_becomes_a_comment_not_a_named_event()
    test_headers_match_the_existing_report_stream_contract()
    test_media_type_is_event_stream()
    print("ok: SSE transport — real EventBus end-to-end, keepalive framing, headers, media type")
