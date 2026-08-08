# M6 — Observability Implementation Report

**Milestone:** Backend Engineering M6 (Observability Hardening) · **Date:** 2026-08-05
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main`
**Predecessor:** M5 — EQ-3 Authorization Cutover ([`18`](18_M5_EQ3_Authorization_Cutover_Report.md)), ✅ CTO-approved 2026-08-05
**Scope authority:** `17` §7's recommended 5-milestone roadmap (EQ-3 cutover →
**observability hardening** → test hardening → ...); doc 04's original audit
(§6 item 9) explicitly deferred OTel/Prometheus "same trigger as EQ-1 (a
second instance)" — superseded by `06` §0.1's later ratification adding
redis/OTel/Prometheus/pydantic-settings/pytest-cov to the approved stack.

---

## 1. Starting position (not greenfield)

M2 Phase 1 already built and M2 Phase L already activated a substantial
observability layer. This milestone's own pre-implementation audit found:

| Capability | State found | Evidence |
|---|---|---|
| Correlation IDs | ✅ Live — request middleware + logging filter | `server.py`'s `_correlation_id_and_metrics` middleware |
| OTel tracing | ✅ Activated — FastAPI/pymongo/httpx auto-instrumented | `setup_tracing()` called at startup |
| `/metrics` endpoint | ✅ Live | `infrastructure/observability/metrics.py::render_latest` |
| `/health`, `/health/ready` | ✅ Live (with defects — §3 below) | `server.py:224-255` |
| `http_requests_total` / `_duration_seconds` | ✅ Active | request middleware |
| `pipeline_runs_total` / `_duration_seconds` | ✅ Active, both graphs | `server.py`'s pipeline task functions |
| `llm_calls_total` | ✅ Active | `agents/llm.py`'s retry loop |
| `node_duration_seconds`, `deadline_exceeded_total`, `auth_failures_total`, `authz_denied_total`, `redis_errors_total`, `jobs_active` | ❌ Defined, never incremented | `infrastructure/observability/metrics.py`'s own docstring: "belong to Phases 3/4/7" |
| LangGraph node spans | ❌ None | no `get_tracer()` call site anywhere in `agents/` |
| Redis OTel instrumentation | ❌ Package not installed | `requirements.txt` |
| SSE session observability | ❌ None | `infrastructure/streaming/sse.py` had no timing/logging |

This milestone's real scope was therefore **closing the gap between what
Phase 1/L defined and what actually has a call site** — not building
observability from zero.

## 2. What this milestone built

1. **`deadline_exceeded_total`** — incremented at both LG-11 deadline-check
   sites (`server.py`, research + learning), labeled with the last node that
   completed before the deadline fired.
2. **`authz_denied_total`** — incremented in `_deny_cross_tenant()`
   (`class=owner_scoped`) and `require_admin()`
   (`infrastructure/security/authorization.py`, `class=admin`) — both are
   already the single choke points every denial routes through (M5's own
   design), so this needed no new call sites, only the increment.
3. **`auth_failures_total`** — incremented on bad-credential and
   rate-limited `/auth/login` attempts.
4. **`jobs_active`** — incremented on `JobLifecycle.start()` success,
   decremented in each pipeline task's `finally` block (guarantees exactly
   one decrement per admitted job regardless of which terminal branch ran).
5. **`redis_errors_total`** — a shared `track_redis_errors(op)` async
   context manager (`infrastructure/observability/metrics.py`), applied at
   the highest-value call site per Redis adapter (`RateLimiter.hit`,
   `JobStore.create`, `EventBus.publish`). Not exhaustive — see §5.
6. **LangGraph node spans + `node_duration_seconds`** — a single
   `instrument_node(graph, name, fn)` wrapper
   (`infrastructure/observability/tracing.py`), applied once per node at
   `g.add_node(...)` time in both `agents/graph.py` and
   `agents/learning_graph.py`. `agents/nodes.py` / `learning_nodes.py` are
   untouched — the node functions stay pure. Fixes `04` O-8 (no per-node
   timing) independently of the app-level trace event ordering, which stays
   nondeterministic for the two parallel nodes by design.
7. **Redis OTel auto-instrumentation** — `opentelemetry-instrumentation-redis`
   added (same approved family as the existing pymongo/httpx/fastapi
   instrumentors, `06` §0.1) and wired into `setup_tracing()`. A no-op under
   the `JOB_BACKEND=memory` default (`09` RR-10) — it instruments the
   `redis-py` client class, which is simply never constructed in that mode.
8. **SSE session observability** — `infrastructure/streaming/sse.py`'s
   `_frame_events` now wraps each stream in an OTel span and logs a single
   line on stream end (`stream_name`, correlation id, event count,
   duration). Covers both live SSE endpoints (`/reports/{id}/stream`,
   `/learning/{id}/stream}`), which already shared this one module.
9. **Health endpoint fixes (O-12, O-13)** — `/health` now uses
   `estimated_document_count()` (O(1) metadata read) instead of
   `count_documents({})` (full collection scan), and resolves the
   configured LLM provider via `agents.llm._active()` instead of a
   hardcoded Gemini-only env check. **Response shape unchanged** — no
   contract impact (confirmed by the route-inventory and shape tests
   listed in §4).
10. **Load/stress validation** — `backend/scripts/load_test.py` (see
    [`24`](24_M6_Load_Test_Report.md)).

## 3. Explicitly not done, and why

| Item | Decision | Reason |
|---|---|---|
| A third `/health/live` route | **Not added** | `tests/contract/test_route_inventory.py` is an exact-set contract guard on `06` C-1; `04` §5.3's original recommendation was a **2-endpoint** split (`/health` = liveness, `/health/ready` = readiness) — `/health` already fills the liveness role once its I/O is fixed (item 9 above). A third endpoint would be a genuine, undocumented API-contract addition, which this milestone's own charter forbids ("Do not modify API contracts"). |
| `ratelimit_degraded` gauge call site | **Left unwired** (as `metrics.py` already documented) | Its call site is `09` §8.1's fail-open policy, which lives in the **live** `/auth/login` rate limiter (`agents/auth.py`'s in-memory counter) — the `RedisRateLimiter` port this gauge would naturally sit in is built-and-tested-standalone, not yet cut over to that live path. Wiring a gauge for a code path that doesn't exist yet would be a fabricated signal. Belongs to whichever milestone does that cutover. |
| Exhaustive `redis_errors_total` coverage (every adapter method) | **Partial — highest-value call site per adapter** | `ponytail:` the remaining Redis adapter methods (`get`, `set_status`, `subscribe`, `history`, `reap`) are covered by the OTel `RedisInstrumentor` auto-instrumentation (item 7) at the span level, just not the Prometheus counter. Upgrade path: wrap the rest with the same `track_redis_errors()` context manager if per-op error-rate alerting (not just tracing) is needed on those paths. |
| Dashboards / alert rules as live infra | **Specification documents, not a deployed Grafana/Alertmanager** | No monitoring stack exists in this repo or its deployment target yet (`scripts/run.py` starts backend + frontend + a portable Mongo only). See [`22`](22_M6_Dashboard_Specification.md) / [`23`](23_M6_Alerting_Specification.md). |

## 4. Verification

- **Hermetic suite:** 167/167 passing (`pytest -m "not live"`) — 163 baseline
  (M5) + 4 new unit tests for this milestone's own instrumentation
  (`tests/unit/test_observability.py`).
- **Contract suite:** 8/8 passing, including `test_route_inventory.py`'s
  exact-set route assertion — confirms zero API surface change.
- **Live suite:** see [`25`](25_M6_Production_Readiness_Assessment.md) for
  the run captured against the already-running local stack.

## 5a. Addendum (2026-08-08) — doc 26 fixes + brief's expanded metrics/tracing list

Follow-up execution pass implementing doc 26's three findings plus the
additional metrics/tracing items a later brief requested beyond doc 26's own
scope. Gap-checked against the live repo before touching anything (per that
brief's own Step 1) — see its gap summary in-conversation for the full
before/after inventory.

**Doc 26 fixes:**
- **A1** (`infrastructure/observability/logging.py`): `install_correlation_filter()`
  now attaches to the target's **handlers**, not the logger's own `.filters`
  list — the actual root cause (`Logger.filters` is only consulted by that
  logger's own `.handle()`; every real log call in this app goes through a
  named child logger, which propagates to ancestor **handlers**, never
  re-invoking an ancestor logger's `.filter()`). New regression test exercises
  a real child logger through real propagation, not `CorrelationIdFilter.filter()`
  called directly (the shape of test that would have caught A1 originally).
- **A2** (`server.py::health_ready`, `app/container.py`): readiness now verifies
  Redis via `infrastructure/redis/client.py::ping()`, but only when
  `container.job_backend == "redis"` — `Container` gained `job_backend`/
  `redis_client` fields (`redis_client` is `None` under the `memory` default,
  so the check is skipped entirely, never a new mandatory dependency).
- **A3** (`app/container.py`, `infrastructure/streaming/sse.py`): both
  docstrings corrected to state what's actually live.
- **Hygiene**: `metrics.py`'s module comment no longer claims
  `pipeline_runs_total`/etc. are unwired — they've been active since Phase L.

**New instrumentation (beyond doc 26, from the follow-up brief's explicit list):**
- `retrieval_duration_seconds` — wired into `agents/retrieval.py::retrieve()`,
  no labels (single series — avoids per-ticker/per-query cardinality).
- `llm_tokens_total` (`provider`, `model`, `kind=input|output`) — a
  `usage_sink: dict | None = None` optional kwarg threads through
  `infrastructure/llm/registry.py::dispatch()` and the three `_gen_*`
  functions in `agents/llm.py`, populated best-effort from each SDK's
  response object (never raises if a provider's usage shape differs).
  `validate_key`'s call site doesn't pass one — unaffected, fully backward
  compatible.
- `report_cache_lookups_total` (`result=hit|miss`) — wired at the SI-1 cache
  lookup in `server.py::generate_report`.
- `sse_sessions_total` (`stream_name`, `outcome=completed|error|cancelled`) +
  `sse_session_duration_seconds` — wired into `_frame_events`. **A real bug
  was found and fixed while implementing this**: the first version counted
  every normal completion as `cancelled`, because a well-behaved SSE client
  stops consuming immediately after the terminal `event: end` frame, which
  raises `GeneratorExit` at that exact suspended yield — indistinguishable
  from a genuine disconnect unless `outcome` is set to `"completed"` *before*
  the terminal yield, not after (execution never resumes past a yield the
  caller doesn't request again). Caught by the new regression tests in
  `tests/unit/test_sse_infrastructure.py`, not by manual review.
- LLM retry-attempt spans — each `chat_text` attempt is now its own child
  span (`llm.attempt`), closing the trace-coverage gap doc 21 had named as
  deferred.
- Job-level parent span — `server.py`'s two pipeline task functions now open
  a `pipeline.{graph}` span (attributes: `job_id`) wrapping the
  `graph.astream()` loop, entered/exited manually (not `with`) so it wraps
  the pre-existing `try/except/finally` without reindenting it; the
  pre-existing `finally` guarantees the exit runs exactly once. Without this,
  each node's span rooted its own independent trace (the background task
  outlives the request span that would otherwise be the parent).

**Reused, not rebuilt:** MongoDB/Redis per-operation visibility stays on the
existing OTel spans rather than a duplicate Prometheus counter — same
reasoning as `19` §3's original call, now also matching the brief's own
"do not rewrite working infrastructure unnecessarily" instruction.

**Engineering Question raised, not resolved unilaterally:** the brief
requires liveness to have zero external-service dependency, but `/health`
(this app's liveness endpoint — there is no separate `/health/live`) does
two Mongo reads. Adding a new zero-I/O route is a route-inventory contract
change; stripping the existing fields breaks tests asserting on them. Left
`/health` as-is (cheap reads, not the O-12 full scans) pending a product/CTO
ruling on which constraint yields.

**Verification:** 173/173 hermetic+contract (168 prior + 5 new: 2 SSE outcome
tests, 3 retrieval/cache/token metric-existence tests), live suite 43/49 on a
fresh instance — **identical failure set**
to the pre-existing baseline (`test_get_report`, `test_delete_account_scopes_report_cascade`,
`test_samples_visible_to_any_authed_user`, 3× `test_password_reset.py`),
confirming zero regressions. Real pipeline run against the live instance
populated `retrieval_duration_seconds` (2 observations, ~1.0s and ~1.0s),
`report_cache_lookups_total{result="miss"}`, and both `sse_sessions_total`
outcomes (`completed` and `cancelled`) with real traffic — not just unit-test
values.

## 5. Files touched

| File | Change |
|---|---|
| `backend/server.py` | metric imports + increments (deadline, authz, auth, jobs_active); `/health` O-12/O-13 fix; SSE call sites pass `stream_name` |
| `backend/infrastructure/observability/metrics.py` | `track_redis_errors()` helper |
| `backend/infrastructure/observability/tracing.py` | `instrument_node()`; `RedisInstrumentor` wired into `setup_tracing()` |
| `backend/infrastructure/security/authorization.py` | `authz_denied_total` in `require_admin()` |
| `backend/infrastructure/redis/{rate_limiter,job_store,event_bus}.py` | `track_redis_errors()` at one call site each |
| `backend/infrastructure/streaming/sse.py` | span + end-of-stream log line, `stream_name` param |
| `backend/agents/graph.py`, `backend/agents/learning_graph.py` | nodes wrapped with `instrument_node()` |
| `backend/requirements.txt` | `+opentelemetry-instrumentation-redis` |
| `backend/scripts/load_test.py` | new — load/stress script |
| `backend/tests/unit/test_observability.py` | +4 tests |
| `docs/backend_engineering/00_README.md`, `10_Backend_Security_Architecture.md`, `11_ADR_Index.md` | M5 approval sync, `SI-1` invariant, M6 registration |
