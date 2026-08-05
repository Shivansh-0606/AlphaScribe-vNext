"""OpenTelemetry setup (M2 Phase 1 "Logging & Observability" scope).

`setup_tracing()` is safe to call with no collector running: an OTLP
exporter with nothing listening on the far end fails its export attempts in
a background thread and logs a warning — it does not raise, block startup,
or affect request handling (confirmed empirically; see the Phase 1 report's
Test Report). When `otel_exporter_endpoint` is unset, no exporter is
attached at all — spans are still created (so instrumentation stays
exercised in every environment) but go nowhere, which is the correct
default for local dev without a collector.

FastAPI/pymongo/httpx auto-instrumentation is applied via the standard
opentelemetry-instrumentation-* packages (06 §0.1's approved stack) — no
hand-rolled span wrapping.
"""
from __future__ import annotations

import logging
import time

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from infrastructure.observability.metrics import node_duration_seconds

logger = logging.getLogger("alphascribe")

_SERVICE_NAME = "alphascribe-backend"


def setup_tracing(app, *, otel_exporter_endpoint: str = "") -> TracerProvider:
    provider = TracerProvider(resource=Resource.create({SERVICE_NAME: _SERVICE_NAME}))

    if otel_exporter_endpoint:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otel_exporter_endpoint)))
        logger.info("OpenTelemetry: exporting traces to %s", otel_exporter_endpoint)
    else:
        logger.info("OpenTelemetry: no OTEL_EXPORTER_OTLP_ENDPOINT set — spans created, not exported")

    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    PymongoInstrumentor().instrument(tracer_provider=provider)
    HTTPXClientInstrumentor().instrument(tracer_provider=provider)
    # M6 — safe with JOB_BACKEND=memory (the RR-10 default): instruments the
    # redis-py client class itself, so it's a no-op until a real
    # redis.asyncio.Redis is actually constructed (app/container.py, only
    # under JOB_BACKEND=redis).
    RedisInstrumentor().instrument(tracer_provider=provider)
    return provider


def get_tracer(name: str = _SERVICE_NAME):
    return trace.get_tracer(name)


def instrument_node(graph: str, name: str, fn):
    """M6 — wraps one LangGraph node with a span + `node_duration_seconds`
    (04 O-8: "no timing in the trace... breaks for the two parallel nodes
    whose events interleave nondeterministically" — a span per node fixes
    this independently of the app-level trace event ordering).

    Applied once per node at graph-build time (agents/graph.py,
    agents/learning_graph.py's `g.add_node(...)` calls) — agents/nodes.py
    and agents/learning_nodes.py stay untouched, pure functions.

    `trace.get_tracer()` is deliberately called INSIDE `wrapped`, not once
    at wrap time: `graph = build_graph(db)` runs at server.py import time,
    before `setup_tracing()` (which installs the real TracerProvider) runs
    in the startup event — resolving the tracer eagerly here would bind
    permanently to the pre-startup no-op provider (a well-known OTel
    footgun). Node calls only happen per-request, long after startup.
    """

    async def wrapped(*args, **kwargs):
        start = time.monotonic()
        with trace.get_tracer(_SERVICE_NAME).start_as_current_span(f"{graph}.{name}"):
            try:
                return await fn(*args, **kwargs)
            finally:
                node_duration_seconds.labels(graph=graph, node=name).observe(time.monotonic() - start)

    wrapped.__name__ = getattr(fn, "__name__", name)
    return wrapped
