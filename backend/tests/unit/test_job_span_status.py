"""M6 fast-follow regression coverage: the job-level parent span
(`pipeline.research` / `pipeline.learning`, server.py) must report ERROR
status when the job actually failed/timed out/was cancelled, and must NOT
be marked ERROR on success.

Exercises the REAL `_run_pipeline`/`_run_explanation` module-level functions
(not a span-status helper tested in isolation) — only `server.graph` /
`server.learning_graph` (to avoid a real LLM call) and `server.db` (to avoid
a live Mongo dependency in the hermetic suite) are stubbed; `container` is
untouched and uses its real in-memory adapters (JOB_BACKEND=memory, the
hermetic default — no network either way).

    python backend/tests/unit/test_job_span_status.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import StatusCode

import server


class _AsyncNoop:
    async def __call__(self, *a, **k):
        return None


class _FakeCollection:
    def __getattr__(self, name):
        return _AsyncNoop()


class _FakeDB:
    """Enough of motor's interface for _run_pipeline/_run_explanation to
    complete without a live Mongo — every collection.method() call is a
    no-op coroutine returning None, which every call site already handles
    (`comp.get(...) if comp else None`, etc.)."""

    def __getattr__(self, name):
        return _FakeCollection()


class _FakeGraphSuccess:
    async def astream(self, initial, config):
        yield {"noop_node": {}}  # a normal terminal step; no trace events to push


class _FakeGraphRaises:
    def __init__(self, exc):
        self._exc = exc

    async def astream(self, initial, config):
        raise self._exc
        yield  # pragma: no cover — makes this an async generator function


def _tracer_for(exporter: InMemorySpanExporter):
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    tracer = provider.get_tracer("test")
    return lambda *a, **k: tracer


def _find_span(exporter: InMemorySpanExporter, name: str):
    spans = [s for s in exporter.get_finished_spans() if s.name == name]
    assert len(spans) == 1, f"expected exactly one {name!r} span, got {len(spans)}: " \
                             f"{[s.name for s in exporter.get_finished_spans()]}"
    return spans[0]


def test_research_success_span_is_not_marked_error():
    exporter = InMemorySpanExporter()
    real_db, real_graph, real_tracer = server.db, server.graph, server.get_tracer
    server.db = _FakeDB()
    server.graph = _FakeGraphSuccess()
    server.get_tracer = _tracer_for(exporter)
    try:
        asyncio.run(server._run_pipeline("job-span-ok", "AAPL", "how's revenue?"))
    finally:
        server.db, server.graph, server.get_tracer = real_db, real_graph, real_tracer

    span = _find_span(exporter, "pipeline.research")
    assert span.status.status_code != StatusCode.ERROR, span.status


def test_research_generic_exception_span_is_marked_error():
    exporter = InMemorySpanExporter()
    real_db, real_graph, real_tracer = server.db, server.graph, server.get_tracer
    server.db = _FakeDB()
    server.graph = _FakeGraphRaises(RuntimeError("provider exploded"))
    server.get_tracer = _tracer_for(exporter)
    try:
        asyncio.run(server._run_pipeline("job-span-fail", "AAPL", "how's revenue?"))
    finally:
        server.db, server.graph, server.get_tracer = real_db, real_graph, real_tracer

    span = _find_span(exporter, "pipeline.research")
    assert span.status.status_code == StatusCode.ERROR, span.status


def test_research_timeout_span_is_marked_error():
    exporter = InMemorySpanExporter()
    real_db, real_graph, real_tracer = server.db, server.graph, server.get_tracer
    server.db = _FakeDB()
    server.graph = _FakeGraphRaises(TimeoutError("job exceeded its deadline"))
    server.get_tracer = _tracer_for(exporter)
    try:
        asyncio.run(server._run_pipeline("job-span-timeout", "AAPL", "how's revenue?"))
    finally:
        server.db, server.graph, server.get_tracer = real_db, real_graph, real_tracer

    span = _find_span(exporter, "pipeline.research")
    assert span.status.status_code == StatusCode.ERROR, span.status


def test_learning_success_span_is_not_marked_error():
    exporter = InMemorySpanExporter()
    real_db, real_graph, real_tracer = server.db, server.learning_graph, server.get_tracer
    server.db = _FakeDB()
    server.learning_graph = _FakeGraphSuccess()
    server.get_tracer = _tracer_for(exporter)
    try:
        asyncio.run(server._run_explanation("job-lspan-ok", "AAPL", "moat", "explain the moat", None))
    finally:
        server.db, server.learning_graph, server.get_tracer = real_db, real_graph, real_tracer

    span = _find_span(exporter, "pipeline.learning")
    assert span.status.status_code != StatusCode.ERROR, span.status


def test_learning_generic_exception_span_is_marked_error():
    exporter = InMemorySpanExporter()
    real_db, real_graph, real_tracer = server.db, server.learning_graph, server.get_tracer
    server.db = _FakeDB()
    server.learning_graph = _FakeGraphRaises(RuntimeError("provider exploded"))
    server.get_tracer = _tracer_for(exporter)
    try:
        asyncio.run(server._run_explanation("job-lspan-fail", "AAPL", "moat", "explain the moat", None))
    finally:
        server.db, server.learning_graph, server.get_tracer = real_db, real_graph, real_tracer

    span = _find_span(exporter, "pipeline.learning")
    assert span.status.status_code == StatusCode.ERROR, span.status


if __name__ == "__main__":
    test_research_success_span_is_not_marked_error()
    test_research_generic_exception_span_is_marked_error()
    test_research_timeout_span_is_marked_error()
    test_learning_success_span_is_not_marked_error()
    test_learning_generic_exception_span_is_marked_error()
    print("ok: job-level span status reflects real success/failure/timeout outcomes, "
          "for both research and learning pipelines")
