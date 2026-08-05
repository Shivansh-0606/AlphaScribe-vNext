"""Unit check for infrastructure/observability/tracing.py's setup_tracing().

Manually verified safe against the real server.app during Phase 1 development
(no route-surface change, a real request still 200s after instrumentation —
see the Phase 1 report's Test Report) — this persists that as a repeatable
test using a minimal FastAPI app instead of the full server.py, so it runs
fast and hermetically alongside everything else, and captures coverage of
setup_tracing() itself (which the ad-hoc verification didn't, since it was
never turned into a test file).

    python backend/tests/unit/test_tracing_setup.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from infrastructure.observability.tracing import get_tracer, setup_tracing


def _minimal_app() -> FastAPI:
    app = FastAPI()

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    return app


def test_setup_tracing_with_no_exporter_endpoint_does_not_break_requests():
    # A single call per process: OpenTelemetry's global TracerProvider can
    # only be installed once (a second call is a documented, warned no-op,
    # not a crash) — exercised in isolation here rather than calling
    # setup_tracing() a second time in this same test module, which would
    # only prove that specific idempotency guard rather than this module's
    # own behavior.
    app = _minimal_app()
    before_paths = set(app.openapi()["paths"])
    provider = setup_tracing(app, otel_exporter_endpoint="")
    assert provider is not None

    app.openapi_schema = None  # instrumentation can add middleware; force a rebuild
    after_paths = set(app.openapi()["paths"])
    assert before_paths == after_paths, "instrumentation must not change the route surface"

    with TestClient(app) as client:
        r = client.get("/ping")
        assert r.status_code == 200
        assert r.json() == {"ok": True}


def test_setup_tracing_with_an_otlp_endpoint_configured_does_not_raise():
    # No real collector is listening — setup itself must still succeed;
    # export failures happen later, in a background thread, and are the
    # module's own documented, deliberate behavior (logged, not raised).
    #
    # Runs AFTER the no-exporter test above, in the same process: OTel's
    # global TracerProvider can only be installed once per process, so this
    # second call logs "Overriding of current TracerProvider is not
    # allowed" / "Attempting to instrument while already instrumented" —
    # informational warnings from OTel's own idempotency guard, not a
    # failure. setup_tracing() still returns a valid (local) provider object
    # either way, which is what this test asserts.
    app = _minimal_app()
    provider = setup_tracing(app, otel_exporter_endpoint="http://localhost:1/v1/traces")
    assert provider is not None


def test_get_tracer_returns_a_usable_tracer():
    tracer = get_tracer("test-tracer")
    with tracer.start_as_current_span("unit-test-span") as span:
        assert span is not None


if __name__ == "__main__":
    test_setup_tracing_with_no_exporter_endpoint_does_not_break_requests()
    test_setup_tracing_with_an_otlp_endpoint_configured_does_not_raise()
    test_get_tracer_returns_a_usable_tracer()
    print("ok: setup_tracing — safe with no exporter, safe with an unreachable OTLP endpoint, get_tracer usable")
