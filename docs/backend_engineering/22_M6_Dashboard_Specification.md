# M6 — Dashboard Specification

**Milestone:** Backend Engineering M6 · **Date:** 2026-08-05
**Status:** Specification only — no Grafana (or equivalent) instance exists
in this repo or its deployment target. `scripts/run.py`'s local stack is
backend + frontend + a portable Mongo; there is no monitoring stack to
deploy a live dashboard into yet. These panels are PromQL queries against
the catalog in [`20`](20_M6_Metrics_Catalog.md), ready to import into
Grafana (or any Prometheus-compatible dashboard tool) the day one exists —
building the panels now, in a form nothing can render yet, would be
speculative work with no way to verify it's even correct.

---

## Dashboard 1 — Service Health (operator's first screen)

| Panel | Query | Notes |
|---|---|---|
| Request rate | `sum(rate(alphascribe_http_requests_total[5m])) by (path)` | Top-N by volume |
| Error rate (5xx) | `sum(rate(alphascribe_http_requests_total{status=~"5.."}[5m])) / sum(rate(alphascribe_http_requests_total[5m]))` | Alert threshold in `23` |
| Latency p50/p95/p99 | `histogram_quantile(0.95, sum(rate(alphascribe_http_request_duration_seconds_bucket[5m])) by (le, path))` | Per-route, catches one slow endpoint hiding in an aggregate average |
| Active jobs | `alphascribe_jobs_active` | By `kind` (research/learning); compare against `MAX_ACTIVE_JOBS` (07 §5) to see admission-control headroom |

## Dashboard 2 — AI Pipeline (research + learning)

| Panel | Query | Notes |
|---|---|---|
| Pipeline outcome rate | `sum(rate(alphascribe_pipeline_runs_total[15m])) by (graph, status)` | `completed` vs `failed` vs `cancelled`, both graphs |
| Pipeline duration | `histogram_quantile(0.95, sum(rate(alphascribe_pipeline_duration_seconds_bucket[15m])) by (le, graph))` | Compare against `JOB_DEADLINE_RESEARCH_S`/`_LEARNING_S` (LG-11) |
| Per-node duration | `histogram_quantile(0.95, sum(rate(alphascribe_node_duration_seconds_bucket[15m])) by (le, graph, node))` | Which node is the bottleneck — first fully-quantitative answer to `04` O-8 |
| Deadline exceedances | `sum(rate(alphascribe_deadline_exceeded_total[1h])) by (graph, node)` | Which node a pathological job is usually stuck in when LG-11 fires |
| LLM call outcome | `sum(rate(alphascribe_llm_calls_total[15m])) by (provider, model, outcome)` | Provider-level error-rate comparison |

## Dashboard 3 — Security & Auth

| Panel | Query | Notes |
|---|---|---|
| Login failures | `sum(rate(alphascribe_auth_failures_total[15m])) by (reason)` | `bad_credentials` vs `rate_limited` — a spike in the former is a brute-force signal (T-04) |
| Authorization denials | `sum(rate(alphascribe_authz_denied_total[15m])) by (endpoint, class)` | Cross-tenant probing (T-07/T-08) shows up here — `_deny_cross_tenant()`/`require_admin()` already audit-log each one (M5), this is the aggregate view |
| Redis error rate | `sum(rate(alphascribe_redis_errors_total[5m])) by (op, kind)` | Only non-zero under `JOB_BACKEND=redis` |

## Dashboard 4 — Streaming (SSE)

Not yet metric-backed (M6 shipped SSE **logging + spans**, not a counter —
see `19` §2 item 8) — this panel set queries the log stream / trace backend
instead of `/metrics`:

| Panel | Source | Notes |
|---|---|---|
| Active/ended stream sessions | log line `sse stream {name} ended: ... events=N duration_s=D` | One line per session end; a log-based count over time, not PromQL |
| Session duration distribution | same log line, `duration_s` field | If this needs to be a first-class panel, promote it to a Histogram metric (`sse_session_duration_seconds`) — not built this milestone; genuinely deferrable until a real operator asks for it |

## Import mechanics (when a Grafana instance exists)

Standard Prometheus datasource pointed at `GET /api/metrics`
(`SD-5`: scrape from a private network). No `PROMETHEUS_ENABLED=false`
handling exists — the endpoint is always on; gating it is a future flag if
ever needed, not built (YAGNI — no current requirement to disable it).
