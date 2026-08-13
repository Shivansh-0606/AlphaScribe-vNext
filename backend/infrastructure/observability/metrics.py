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

# --- ACTIVE (M2 Phase L + M6 — 07 §7.2 / 09 §12 / 10 §13 catalogs). This
# comment previously read "DEFINED, not yet incremented anywhere... belong
# to Phases 3/4/7" — stale past Phase L and M6 landing real call sites for
# all of these (hygiene fix, M6; see docs/backend_engineering/
# 26_M6_Observability_Architecture_Review.md §3). ---
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
jobs_active = Gauge(
    "alphascribe_jobs_active", "Currently active jobs", ["kind"]
)
retrieval_duration_seconds = Histogram(
    "alphascribe_retrieval_duration_seconds", "Hybrid retrieval duration (agents/retrieval.py::retrieve)"
)
llm_tokens_total = Counter(
    "alphascribe_llm_tokens_total", "LLM token usage, where the provider reports it",
    ["provider", "model", "kind"],  # kind: input | output
)
report_cache_lookups_total = Counter(
    "alphascribe_report_cache_lookups_total", "generate_report's (ticker,query) cache lookups (SI-1)",
    ["result"],  # hit | miss
)
sse_sessions_total = Counter(
    "alphascribe_sse_sessions_total", "SSE stream sessions", ["stream_name", "outcome"]
)
sse_session_duration_seconds = Histogram(
    "alphascribe_sse_session_duration_seconds", "SSE stream session duration", ["stream_name"]
)

# --- ACTIVE — M8 Step 5 (Document 39 §18: "Build the acquire(identity) use
# case", application/financials.py::AcquireFinancialsUseCase), following the
# llm_calls_total{outcome} convention (Document 36 §18 / Document 37 §8's
# "acquisition_request_total{outcome}"-style recommendation, applied at the
# use-case layer, not the future endpoint layer). ---
acquisition_attempts_total = Counter(
    "alphascribe_acquisition_attempts_total", "M8 financial-statement acquisition attempts",
    ["statement_type", "outcome"],
)
acquisition_duration_seconds = Histogram(
    "alphascribe_acquisition_duration_seconds", "AcquireFinancialsUseCase.acquire() duration", ["statement_type"]
)

# --- DEFINED, not yet incremented anywhere — its call site is 09 §8.1's
# fail-open policy, implemented today in agents/auth.py's in-memory rate
# limiter, not the RedisRateLimiter port this gauge belongs to (that port
# is built-and-tested-standalone, not yet cut into the live /auth/login
# path — a separate milestone's cutover). Wiring this before that cutover
# exists would be a fabricated signal, not an early one. ---
ratelimit_degraded = Gauge(
    "alphascribe_ratelimit_degraded", "1 when the rate limiter is running degraded (fail-open)"
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
