# M6 — Metrics Catalog

**Milestone:** Backend Engineering M6 · **Date:** 2026-08-05
**Scrape endpoint:** `GET /api/metrics` (public, Prometheus text format;
matches `/health`'s posture — scrape it from a private network in a real
deployment, `10` SD-5).

All metrics live in `backend/infrastructure/observability/metrics.py` as
module-level `prometheus_client` objects on the default global registry —
one process, one registry (no need for a custom `CollectorRegistry` until
multiple independent registries are actually required).

---

## Active (real call site, verified via `/metrics` on a running instance)

| Metric | Type | Labels | Call site | Since |
|---|---|---|---|---|
| `alphascribe_http_requests_total` | Counter | `method, path, status` | request-timing middleware | M2 Phase 1 |
| `alphascribe_http_request_duration_seconds` | Histogram | `method, path` | request-timing middleware | M2 Phase 1 |
| `alphascribe_pipeline_runs_total` | Counter | `graph, status` | both pipeline tasks' terminal branches | M2 Phase L |
| `alphascribe_pipeline_duration_seconds` | Histogram | `graph` | both pipeline tasks' `finally` | M2 Phase L |
| `alphascribe_llm_calls_total` | Counter | `provider, model, tier, outcome` | `agents/llm.py`'s retry loop | M2 Phase L |
| `alphascribe_node_duration_seconds` | Histogram | `graph, node` | `instrument_node()` wrapper, both graphs | **M6** |
| `alphascribe_deadline_exceeded_total` | Counter | `graph, node` | LG-11 deadline checks (`server.py`, both graphs) | **M6** |
| `alphascribe_auth_failures_total` | Counter | `reason` | `POST /auth/login` (`bad_credentials`, `rate_limited`) | **M6** |
| `alphascribe_authz_denied_total` | Counter | `endpoint, class` | `_deny_cross_tenant()` (`class=owner_scoped`), `require_admin()` (`class=admin`) | **M6** |
| `alphascribe_redis_errors_total` | Counter | `op, kind` | `RateLimiter.hit`, `JobStore.create`, `EventBus.publish` (highest-value site per adapter — §5 of `19`) | **M6** |
| `alphascribe_jobs_active` | Gauge | `kind` | `JobLifecycle.start()` (inc) / pipeline `finally` (dec) | **M6** |

## Active (added 2026-08-08 follow-up pass)

| Metric | Type | Labels | Call site |
|---|---|---|---|
| `alphascribe_retrieval_duration_seconds` | Histogram | (none) | `agents/retrieval.py::retrieve()` |
| `alphascribe_llm_tokens_total` | Counter | `provider, model, kind=input\|output` | `agents/llm.py::chat_text`, populated via a `usage_sink` threaded through `dispatch()`; best-effort — zero/absent for providers whose SDK response doesn't expose usage |
| `alphascribe_report_cache_lookups_total` | Counter | `result=hit\|miss` | `server.py::generate_report`'s SI-1 cache lookup |
| `alphascribe_sse_sessions_total` | Counter | `stream_name, outcome=completed\|error\|cancelled` | `infrastructure/streaming/sse.py::_frame_events` |
| `alphascribe_sse_session_duration_seconds` | Histogram | `stream_name` | same |

## Defined, not yet incremented (honest, inspectable via `/metrics` as zero/absent)

| Metric | Type | Labels | Blocked on |
|---|---|---|---|
| `alphascribe_ratelimit_degraded` | Gauge | (none) | `09` §8.1's fail-open policy is implemented in `agents/auth.py`'s in-memory limiter, not the `RedisRateLimiter` port this gauge belongs to — that port is built-and-tested-standalone, not yet the live `/auth/login` path. See `19` §3. |

## Label cardinality notes

- `path` on `http_requests_total`/`_duration_seconds` uses the **matched
  route template** (`request.scope["route"].path`), never the raw URL — no
  unbounded cardinality from path parameters (`/reports/{job_id}` stays one
  series, not one per UUID).
- `node` on `node_duration_seconds`/`deadline_exceeded_total` is bounded to
  the 5 research-graph + 2 learning-graph node names — fixed, small set.
- `reason`/`kind`/`op` label values are internal enum-like strings chosen at
  the call site (`bad_credentials`, `rate_limited`, exception class names,
  adapter operation names) — bounded, not user input.

## Cross-references

- Catalog origin: `04` §3.3, `07` §7.2, `09` §12, `10` §13 (all cited in
  `metrics.py`'s own module docstring as the sources this catalog formalizes).
- Dashboard queries built on this catalog: [`22`](22_M6_Dashboard_Specification.md).
- Alert rules built on this catalog: [`23`](23_M6_Alerting_Specification.md).
