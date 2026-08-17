"""Unit checks for infrastructure/observability/{logging,metrics,tracing}.py.

    python backend/tests/unit/test_observability.py
"""
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from infrastructure.observability.logging import (
    CorrelationIdFilter,
    get_correlation_id,
    install_correlation_filter,
    set_correlation_id,
)
from infrastructure.observability.metrics import (
    comparison_explanation_runs_total,
    deadline_exceeded_total,
    http_requests_total,
    llm_tokens_total,
    render_latest,
    report_cache_lookups_total,
    retrieval_duration_seconds,
    track_redis_errors,
)
from infrastructure.observability.tracing import instrument_node


def test_correlation_id_defaults_to_none():
    set_correlation_id(None)
    assert get_correlation_id() is None


def test_correlation_id_round_trips():
    set_correlation_id("job-abc-123")
    try:
        assert get_correlation_id() == "job-abc-123"
    finally:
        set_correlation_id(None)


def test_correlation_filter_injects_a_dash_when_unset():
    set_correlation_id(None)
    f = CorrelationIdFilter()
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "msg", None, None)
    assert f.filter(record) is True
    assert record.correlation_id == "-"


def test_correlation_filter_injects_the_active_id():
    set_correlation_id("req-42")
    try:
        f = CorrelationIdFilter()
        record = logging.LogRecord("test", logging.INFO, __file__, 1, "msg", None, None)
        f.filter(record)
        assert record.correlation_id == "req-42"
    finally:
        set_correlation_id(None)


def test_install_correlation_filter_attaches_and_fires():
    # Fixed for A1: attaches to the logger's HANDLER, not its own .filters
    # list — a bare getLogger() has no handler until one is added, so this
    # test gives it one and checks that handler's filters, matching what
    # install_correlation_filter() now actually does.
    logger = logging.getLogger("test.correlation." + __name__)
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    try:
        install_correlation_filter(logger)
        set_correlation_id("attached-id")
        try:
            record = logging.LogRecord("test", logging.INFO, __file__, 1, "msg", None, None)
            assert all(f.filter(record) for f in handler.filters)
            assert record.correlation_id == "attached-id"
        finally:
            set_correlation_id(None)
    finally:
        logger.removeHandler(handler)


def test_correlation_id_reaches_a_real_child_logger_via_propagation():
    # M6 A1 regression test (doc 26's own recommendation): exercises the
    # REAL propagation path — a named child logger (exactly how the app
    # logs, e.g. logging.getLogger("alphascribe")) propagating up to an
    # ancestor's handler — instead of calling CorrelationIdFilter.filter()
    # directly. This is the shape of test that would have caught A1: the
    # bug was that install_correlation_filter() attached to the wrong
    # object, invisible to a test that bypasses the logger hierarchy.
    import io

    parent = logging.getLogger("test.correlation.parent." + __name__)
    parent.handlers.clear()
    parent.propagate = False
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("corr=%(correlation_id)s %(message)s"))
    parent.addHandler(handler)
    install_correlation_filter(parent)

    child = logging.getLogger("test.correlation.parent." + __name__ + ".child")
    child.setLevel(logging.INFO)

    set_correlation_id("propagated-id")
    try:
        child.info("hello from a real child logger")
    finally:
        set_correlation_id(None)
        parent.removeHandler(handler)

    assert "corr=propagated-id hello from a real child logger" in stream.getvalue()


def test_metrics_counter_increments_and_renders():
    before_body, content_type = render_latest()
    http_requests_total.labels(method="GET", path="/api/health", status="200").inc()
    after_body, _ = render_latest()
    assert b"alphascribe_http_requests_total" in after_body
    assert after_body != before_body
    assert content_type.startswith("text/plain")


def test_tracing_creates_real_spans():
    # A fresh TracerProvider + in-memory exporter, independent of the
    # process-global one setup_tracing() installs — proves span creation
    # works without depending on (or polluting) global OTel state.
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test")

    with tracer.start_as_current_span("test.span", attributes={"job_id": "j1"}):
        pass

    spans = exporter.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].name == "test.span"
    assert spans[0].attributes["job_id"] == "j1"


def test_instrument_node_records_duration_and_returns_value():
    import asyncio

    async def fake_node(state):
        return {"ok": True, **state}

    wrapped = instrument_node("test_graph", "test_node", fake_node)
    before_body, _ = render_latest()
    result = asyncio.run(wrapped({"x": 1}))
    after_body, _ = render_latest()
    assert result == {"ok": True, "x": 1}
    assert b"alphascribe_node_duration_seconds" in after_body
    assert after_body != before_body


def test_instrument_node_propagates_exceptions():
    import asyncio

    async def failing_node(state):
        raise ValueError("boom")

    wrapped = instrument_node("test_graph", "failing_node", failing_node)
    try:
        asyncio.run(wrapped({}))
        raise AssertionError("expected ValueError to propagate")
    except ValueError:
        pass
    # the duration observation in `finally` must still have landed
    body, _ = render_latest()
    assert b'node="failing_node"' in body


def test_track_redis_errors_counts_then_reraises():
    import asyncio

    async def _boom():
        async with track_redis_errors("test.op"):
            raise ConnectionError("redis down")

    before_body, _ = render_latest()
    try:
        asyncio.run(_boom())
        raise AssertionError("expected ConnectionError to propagate")
    except ConnectionError:
        pass
    after_body, _ = render_latest()
    assert b'op="test.op"' in after_body
    assert after_body != before_body


def test_deadline_exceeded_total_is_a_real_counter():
    before_body, _ = render_latest()
    deadline_exceeded_total.labels(graph="research", node="synthesizer").inc()
    after_body, _ = render_latest()
    assert b"alphascribe_deadline_exceeded_total" in after_body
    assert after_body != before_body


def test_comparison_explanation_runs_total_covers_deadline_exceeded_without_a_graph_label():
    """M9.1's corrective pass (Document 43 §16/§20): a comparison-explanation
    deadline is NOT recorded via deadline_exceeded_total (that metric's
    graph/node labels are tied to LangGraph node-boundary semantics this
    single-chat_json-call capability doesn't have) — it's the `outcome` label
    on this capability-appropriate, kind-shaped counter instead."""
    before_body, _ = render_latest()
    comparison_explanation_runs_total.labels(outcome="failed_deadline_exceeded").inc()
    after_body, _ = render_latest()
    assert b"alphascribe_comparison_explanation_runs_total" in after_body
    assert b'outcome="failed_deadline_exceeded"' in after_body
    assert b'graph="comparison_explanation"' not in after_body
    assert after_body != before_body


def test_retrieval_duration_seconds_is_a_real_metric():
    before_body, _ = render_latest()
    retrieval_duration_seconds.observe(0.05)
    after_body, _ = render_latest()
    assert b"alphascribe_retrieval_duration_seconds" in after_body
    assert after_body != before_body


def test_report_cache_lookups_total_tracks_hit_and_miss():
    before_body, _ = render_latest()
    report_cache_lookups_total.labels(result="hit").inc()
    report_cache_lookups_total.labels(result="miss").inc()
    after_body, _ = render_latest()
    assert b'result="hit"' in after_body
    assert b'result="miss"' in after_body
    assert after_body != before_body


def test_llm_tokens_total_is_a_real_counter():
    before_body, _ = render_latest()
    llm_tokens_total.labels(provider="gemini", model="gemini-2.0-flash", kind="input").inc(123)
    after_body, _ = render_latest()
    assert b"alphascribe_llm_tokens_total" in after_body
    assert after_body != before_body


if __name__ == "__main__":
    test_correlation_id_defaults_to_none()
    test_correlation_id_round_trips()
    test_correlation_filter_injects_a_dash_when_unset()
    test_correlation_filter_injects_the_active_id()
    test_install_correlation_filter_attaches_and_fires()
    test_correlation_id_reaches_a_real_child_logger_via_propagation()
    test_metrics_counter_increments_and_renders()
    test_tracing_creates_real_spans()
    test_instrument_node_records_duration_and_returns_value()
    test_instrument_node_propagates_exceptions()
    test_track_redis_errors_counts_then_reraises()
    test_deadline_exceeded_total_is_a_real_counter()
    test_retrieval_duration_seconds_is_a_real_metric()
    test_report_cache_lookups_total_tracks_hit_and_miss()
    test_llm_tokens_total_is_a_real_counter()
    print("ok: correlation-id logging filter, Prometheus counter + /metrics rendering, real OTel span "
          "creation, LangGraph node instrumentation, Redis error tracking, deadline metric, "
          "retrieval/cache/token metrics")
