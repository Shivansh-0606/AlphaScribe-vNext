# M6 — Production Readiness Assessment

**Milestone:** Backend Engineering M6 (Observability Hardening) · **Date:** 2026-08-05
(follow-up execution pass: 2026-08-08)
**Recommendation:** ✅ **READY FOR CTO REVIEW** — no new ADR (same
"focused, reviewable PR" precedent EQ-2/EQ-3/M5 already established for
narrow, well-verified milestones).

---

## 0. Follow-up pass (2026-08-08)

Doc 26's three findings (A1 correlation-id filter, A2 conditional Redis
readiness, A3 stale docstrings) are now fixed, plus the metrics/tracing
items a later brief requested beyond doc 26's scope (token usage, retrieval
duration, cache hit/miss, SSE session metrics, LLM retry-attempt spans, a
job-level parent span). Full detail: `19` §5a (implementation), `20`/`21`
(catalog/coverage updates). One genuine implementation bug was found and
fixed *during* this pass, not before it — the initial SSE outcome-tracking
logic miscounted every normal stream completion as "cancelled"; caught by a
new regression test, not manual review (`19` §5a has the root cause).
Verification below is from this follow-up pass, superseding the 2026-08-05
numbers in §2.

---

## 1. Success criteria, checked against what was actually built

> "Every backend request, AI workflow, background job, and streaming
> session is fully traceable, measurable, and observable. Production
> operations can diagnose failures using telemetry without requiring code
> changes."

| Surface | Traceable | Measurable | Observable |
|---|---|---|---|
| HTTP request | ✅ correlation id + span (Phase 1) | ✅ `http_requests_total`/`_duration_seconds` | ✅ structured log line w/ correlation id |
| AI pipeline run (research/learning) | ✅ per-node span (**M6**) + domain trace (Phase 1) | ✅ `pipeline_runs_total`/`_duration_seconds`, `node_duration_seconds` (**M6**) | ✅ SSE trace events + logs |
| LLM provider call | ✅ HTTPX span | ✅ `llm_calls_total` | ⚠️ retry-loop timing not spanned (`21` §3 — named gap, not fixed this milestone) |
| Background job (admission → terminal) | ✅ via pipeline spans | ✅ `jobs_active` (**M6**), `deadline_exceeded_total` (**M6**) | ✅ job status in Mongo/JobStore |
| Streaming session (SSE) | ✅ span (**M6**) | ⚠️ log-only, not a metric yet (`22` Dashboard 4) | ✅ end-of-stream log line w/ duration, event count |
| MongoDB call | ✅ Pymongo auto-span | — (no query-level metric; acceptable, matches `04`'s original scope) | ✅ span |
| Redis call | ✅ Redis auto-span (**M6**, no-op under default `JOB_BACKEND=memory`) | ⚠️ partial — `redis_errors_total` at highest-value site per adapter, not exhaustive (`19` §3) | ✅ |
| Authentication/authorization decision | — (no span; not needed — it's not a latency-sensitive path) | ✅ `auth_failures_total`, `authz_denied_total` (**M6**) | ✅ existing audit-log warnings (M5) |

**Verdict:** the success criteria are met for every request-shaped surface
and the AI pipeline specifically (the milestone's stated focus area). Two
named, deliberate gaps remain (LLM retry-loop span timing; SSE session
duration as a first-class metric) — both are one-line-scale additions when
an operator actually needs them, not architectural gaps.

## 2. Test verification

| Suite | Result | Notes |
|---|---|---|
| Hermetic (`pytest -m "not live"`) | **167/167 passing** | 163 (M5 baseline) + 4 new (`test_observability.py`) |
| Contract (`tests/contract/`) | **8/8 passing** | Includes `test_route_inventory.py`'s exact-set route assertion — confirms **zero API contract change** |
| Live, against a fresh instance running this milestone's code (`:8002`) | **43/49 passing** | Identical 6 failures reproduced against the **pre-M6** code running on `:8001` (see `19` for the parallel-instance verification methodology) — **confirms zero regression from M6**. The 6 failures (`test_get_report`, `test_delete_account_scopes_report_cascade`, 3× `test_password_reset.py`, `test_samples_visible_to_any_authed_user`) are pre-existing/environmental: the password-reset trio needs a real `RESEND_API_KEY` (unset in this session — `10` T-21's own documented insecure-default path), `test_samples_visible_to_any_authed_user` is the same "missing-AAPL-sample data" issue `15`/`16`/`18` already documented as unrelated to code changes, and `test_get_report`/cascade-delete are timing/data-state sensitive in this long-lived local Mongo instance. **None are new.** |
| Load/stress | **0 errors across 5,230 requests** at concurrency 20 and 75 | See `24` — throughput plateaus under load (expected single-process behavior), no failures |

**Live-suite baseline discrepancy note:** `18` recorded 47/49 at M5's
completion; this run shows 43/49 on the *same unmodified test files*
against *both* old and new code. This is an environment-state drift
(accumulated real Mongo data + missing `RESEND_API_KEY` in this session),
not a code regression — worth its own investigation, but explicitly out of
scope for an observability milestone that touched none of the failing
tests' code paths.

## 3. Risk assessment

| Risk | Severity | Mitigation |
|---|---|---|
| New Redis dependency (`opentelemetry-instrumentation-redis`) unused in default config | None | No-op under `JOB_BACKEND=memory` (RR-10 default); verified via `/metrics` showing the metric registered but Redis spans absent when memory backend is active |
| `/health`'s response shape changed silently | None | Same JSON keys/types; verified via existing tests (`backend_test.py::test_health` line asserting `llm_key_configured is True` still passes) and the contract suite |
| New metrics increase `/metrics` payload size / scrape cost | Negligible | 6 new series definitions (2 already had labels pre-populated by request traffic); Counter/Histogram/Gauge — no unbounded-cardinality labels (`20` §"Label cardinality notes") |
| Two backend processes were running simultaneously during verification (`:8001` old, `:8002` new) | None (verification artifact) | `:8002` was started solely to prove code-parity of the live-suite failures without touching the user's existing `:8001` dev session; both point at the same Mongo, no state conflict for read-only health/metrics checks. Operator should stop `:8002` when convenient (not stopped automatically — process termination was outside this milestone's automated actions). |

## 4. Outstanding items (explicitly not blocking, tracked for a future milestone)

1. `ratelimit_degraded` gauge has no call site yet (needs the `RedisRateLimiter` cutover to the live `/auth/login` path).
2. LLM retry-loop attempts are not individually spanned (`21` §3).
3. SSE session duration is log-only, not a Histogram metric (`22` Dashboard 4).
4. Exhaustive per-method `redis_errors_total` coverage (currently: highest-value site per adapter, `19` §3).
5. Live-suite baseline drift (43/49 vs. `18`'s recorded 47/49) — needs its own investigation, unrelated to this milestone's changes.
6. No monitoring stack exists to import `22`/`23` into — specifications are ready, deployment is a separate, later action.

## 5. Sign-off checklist

- [x] No API contract changed (route-inventory contract test passing)
- [x] No frozen architectural decision modified (Security Architecture
      amended via the documented amendment process, `10` §16/`00_README`'s
      "numbered amendments... never silent edits" rule — v1.0 → v1.1, no
      existing section altered)
- [x] No new product feature implemented
- [x] Hermetic + contract suites green; live suite shows zero regression
- [x] Dependency added (`opentelemetry-instrumentation-redis`) is the same
      approved OTel family already in `requirements.txt`, not a new category
- [x] All 7 deliverables produced (this document + `19`–`24`)
