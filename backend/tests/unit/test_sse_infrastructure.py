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

from infrastructure.observability.metrics import render_latest
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


def test_session_metrics_record_completed_outcome():
    async def fake_events():
        yield {"node": "pipeline", "status": "ok"}  # terminal

    before_body, _ = render_latest()
    response = sse_response(fake_events(), stream_name="m6_test_completed")
    asyncio.run(asyncio.wait_for(_collect_frames(response), timeout=5))
    after_body, _ = render_latest()

    # prometheus_client renders labels alphabetically, not definition order —
    # check independently rather than assume a fixed label ordering.
    assert b'alphascribe_sse_sessions_total{outcome="completed",stream_name="m6_test_completed"}' in after_body
    assert after_body != before_body


def test_mid_stream_cancellation_records_cancelled_not_completed():
    # M6 fast-follow regression test for the original outcome-classification
    # bug: a real InMemoryEventBus (not a hand-built fake iterator), no
    # terminal event ever published (the job is still "running" from the
    # stream's point of view), one frame consumed, then the SAME close
    # mechanism Starlette's StreamingResponse actually uses on a real client
    # disconnect — body_iterator.aclose() — mid-stream, before "event: end".
    async def run():
        bus = InMemoryEventBus()
        job_id = "job-sse-cancel"
        await bus.publish(job_id, {"node": "pipeline", "status": "start"})

        response = sse_response(bus.subscribe(job_id), stream_name="m6_test_cancel")
        it = response.body_iterator
        first = await asyncio.wait_for(it.__anext__(), timeout=5)
        assert first == 'data: {"node": "pipeline", "status": "start"}\n\n'
        await it.aclose()

    before_body, _ = render_latest()
    asyncio.run(run())
    after_body, _ = render_latest()

    assert b'alphascribe_sse_sessions_total{outcome="cancelled",stream_name="m6_test_cancel"}' in after_body
    # And NOT counted as completed — the bug this regresses against.
    assert b'alphascribe_sse_sessions_total{outcome="completed",stream_name="m6_test_cancel"}' not in after_body
    assert after_body != before_body


def test_session_metrics_record_error_outcome_and_reraise():
    async def failing_events():
        yield {"node": "pipeline", "status": "start"}
        raise RuntimeError("provider blew up mid-stream")

    response = sse_response(failing_events(), stream_name="m6_test_error")
    try:
        asyncio.run(asyncio.wait_for(_collect_frames(response), timeout=5))
        raise AssertionError("expected RuntimeError to propagate out of the SSE generator")
    except RuntimeError as e:
        assert "provider blew up" in str(e)

    body, _ = render_latest()
    assert b'alphascribe_sse_sessions_total{outcome="error",stream_name="m6_test_error"}' in body


if __name__ == "__main__":
    test_end_to_end_through_a_real_event_bus()
    test_keepalive_sentinel_becomes_a_comment_not_a_named_event()
    test_headers_match_the_existing_report_stream_contract()
    test_media_type_is_event_stream()
    test_session_metrics_record_completed_outcome()
    test_mid_stream_cancellation_records_cancelled_not_completed()
    test_session_metrics_record_error_outcome_and_reraise()
    print("ok: SSE transport — real EventBus end-to-end, keepalive framing, headers, media type, "
          "session outcome metrics (completed/cancelled/error)")
