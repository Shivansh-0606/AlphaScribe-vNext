"""Prometheus metrics (M2 Phase 1 "Observability" scope; 04 §3.3, 07 §7.2,
09 §12, 10 §13 catalogs). Uses the default global CollectorRegistry via
`prometheus_client`'s module-level metric objects — the standard pattern for
a single-process app (no need for a custom registry until multiple
independent registries are actually required, which nothing here does).

Only the metrics with a REAL call site wired THIS phase are listed as
"active" below; the rest are DEFINED (so Phase 3/4+ business-logic code has
something to import and increment immediately, without a metrics-plumbing
PR of its own later) but are zero/absent until that code lands — an honest,
inspectable state via GET /metrics, not a claim that pipeline-level
observability is complete (it isn't; see the Phase 1 report's Observability
Report for exactly what "Every request should be traceable end-to-end" does
and does not yet cover).
"""
from __future__ import annotations

import contextlib

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

# --- ACTIVE this phase — wired via server.py's request-timing middleware ---
http_requests_total = Counter(
    "alphascribe_http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
http_request_duration_seconds = Histogram(
    "alphascribe_http_request_duration_seconds", "HTTP request duration", ["method", "path"]
)

# --- DEFINED, not yet incremented anywhere (07 §7.2 / 09 §12 / 10 §13
# catalogs) — the pipeline/job/Redis/Mongo call sites that would increment
# these belong to Phases 3/4/7, explicitly out of this phase's scope. ---
pipeline_runs_total = Counter(
    "alphascribe_pipeline_runs_total", "Pipeline runs", ["graph", "status"]
)
pipeline_duration_seconds = Histogram(
    "alphascribe_pipeline_duration_seconds", "Pipeline duration", ["graph"]
)
node_duration_seconds = Histogram(
    "alphascribe_node_duration_seconds", "Per-node duration", ["graph", "node"]
)
deadline_exceeded_total = Counter(
    "alphascribe_deadline_exceeded_total", "Job deadline exceedances", ["graph", "node"]
)
llm_calls_total = Counter(
    "alphascribe_llm_calls_total", "LLM calls", ["provider", "model", "tier", "outcome"]
)
auth_failures_total = Counter(
    "alphascribe_auth_failures_total", "Authentication failures", ["reason"]
)
authz_denied_total = Counter(
    "alphascribe_authz_denied_total", "Authorization denials", ["endpoint", "class"]
)
redis_errors_total = Counter(
    "alphascribe_redis_errors_total", "Redis errors", ["op", "kind"]
)
ratelimit_degraded = Gauge(
    "alphascribe_ratelimit_degraded", "1 when the rate limiter is running degraded (fail-open)"
)
jobs_active = Gauge(
    "alphascribe_jobs_active", "Currently active jobs", ["kind"]
)


def render_latest() -> tuple[bytes, str]:
    """Returns (body, content_type) for the /metrics route — kept as a
    one-line seam so server.py's route handler needs no prometheus_client
    import of its own."""
    return generate_latest(), CONTENT_TYPE_LATEST


@contextlib.asynccontextmanager
async def track_redis_errors(op: str):
    """M6 — one shared try/except so `redis_errors_total` doesn't need
    hand-rolled boilerplate at every Redis adapter call site (`09` §12
    catalog). Re-raises after counting: this is observability, not
    fail-open/fail-closed policy — each adapter's own error handling (or
    lack of it) is unchanged."""
    try:
        yield
    except Exception as e:  # noqa: BLE001 — counted by type, then re-raised untouched
        redis_errors_total.labels(op=op, kind=type(e).__name__).inc()
        raise
