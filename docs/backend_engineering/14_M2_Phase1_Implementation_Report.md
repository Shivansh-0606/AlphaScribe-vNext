# Backend Engineering Milestone 2 — Phase 1 Implementation Report

**Status:** ✅ **COMPLETE**
**Milestone:** Backend Engineering M2, Phase 1 (Backend Foundation Implementation) · **Date:** 2026-08-04
**Governed by:** Backend Architecture `v1.0` (🔒 frozen) — Documents
[`06`](06_Clean_Architecture_Migration_Plan.md)–[`11`](11_ADR_Index.md)
**Follows:** [`13_M2_Phase0_Completion_Report.md`](13_M2_Phase0_Completion_Report.md)
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main` · commit `e5650be` (backend/ unchanged from `7404b67`, per Phase 0's report §baseline note)

> This is a deliverable, not a planning document. No new architectural
> decision was required — every design choice below cites an existing,
> ratified ADR (§3). Where implementation surfaced something the frozen set
> didn't fully specify, this report says so explicitly (§5) rather than
> silently deciding it.

---

## 0. Reading this report — a numbering note

The user's Phase 0 / Phase 1 / Phase 2 sequence is **not** the same axis as
[`06 §7`](06_Clean_Architecture_Migration_Plan.md)'s Ph0–Ph7 migration
phases. This report delivers a **slice across several** of those:

| 06 §7 phase | What it specifies | Delivered this report? |
|---|---|---|
| Ph1 App factory | `Settings`, container skeleton, no import-time I/O | ✅ `Settings`/`Container` built; server.py's own import-time I/O is **not yet removed** (§4) |
| Ph2 Domain | Pure logic → `domain/` | ✅ `domain/errors.py`, `events.py`, `models.py` (new — `06`'s planned moves of `scoring.py` etc. are **not** done this phase, see §5) |
| Ph3 Ports + Mongo | Repositories, 25-index migration, `maxTimeMS` | 🟡 Indexes + client + `ping` done and **run for real**; `ChunkRepository`/`ReportLikeRepository` **Protocols defined, no adapter** (explicitly out of scope — "do not implement feature-specific repositories") |
| Ph4 Jobs + EventBus | `01 D-1` fix, deadlines, restart sweep | 🟡 `JobLifecycle`, `EventBus`, `JobStore` built and tested; **not cut over** into the live `_run_pipeline`/`JOBS` dict (§4) |
| Ph5 LLM adapter | Collapse duplicated dispatch (`01 D-3`) | ✅ **Done and live** — `agents/llm.py` now delegates to one dispatch table |
| Ph6 Router split | `server.py` deleted, authorization model | 🟡 Authorization **pattern** built and **two real call sites cut over**; `server.py` is **not** deleted (deliberately out of scope) |
| Ph7 Redis/OTel/Docker/CI | Platform | 🟡 Redis adapters + OTel + Prometheus built, tested, **partially wired live**; Docker/GitHub-Actions-for-this-repo **not** built this phase |

**Net position:** this phase built the full shared-infrastructure layer the
frozen architecture specifies, wired the **safe, additive, zero-contract-risk**
pieces live, and deliberately left the **pipeline cutover** (the part that
touches the live report-generation path) for a dedicated phase — exactly the
strangler-fig discipline `06 AD-4`/ADR-002 requires. §4 states this
precisely, piece by piece.

---

## 1. Phase 1 Implementation Report

### 1.1 Completed work, by scope area

#### Application Structure

| Delivered | ADR | Evidence |
|---|---|---|
| `app/settings.py` — one validated `Settings`, dev/test/production, SD-2/SD-3 startup gates | `06` AD-9 | §1.2 tests; both gates verified raising for real (§2) |
| `app/container.py` — the composition root; `JOB_BACKEND=memory\|redis` selects adapters | `06` AD-3, ADR-004 | Constructs and runs a job end-to-end against both backends (§2) |
| `application/ports.py` — 7 Protocols across 6 concerns | `06` AD-2, ADR-004 | No ABC, no registration; structural typing only |
| `domain/{errors,events,models}.py` — pure, stdlib+pydantic only | `06` AD-6 | Zero infra imports; `test_architecture.py`'s dependency-rule seed still green |
| `infrastructure/{mongo,redis,llm,security,observability,streaming}/` | `06` §2.3's target layout | 1,618 lines of new source, listed in full below |

**Debt removed** (the report's explicit "remove temporary architectural
debt" ask): `01 D-3` — `agents/llm.py` had two independent copies of the
provider-dispatch chain, and `validate_key` silently ignored `LLM_BASE_URL`
while `_generate_sync` consulted it. Both now delegate to
`infrastructure/llm/registry.py`'s single `dispatch()`/`resolve_base_url()`.
**This is live** — every real LLM call and every key-validation call goes
through the collapsed path today. Verified: all 3 pre-existing LLM test
files pass unmodified in behavior (one test's *environment sensitivity* was
fixed — see §5.1), plus a new test proves the two call sites now resolve
`base_url` identically.

#### Configuration

`app/settings.py` centralizes exactly what the phase asked for:

| Requirement | Where |
|---|---|
| Development / Testing / Production | `Environment` enum; `_production_secret_gates` validator |
| Environment variables | Every field, aliased to its existing env var name — no renaming |
| Secrets | `otp_pepper`, `resend_api_key`; production gate refuses insecure defaults (`10` SD-3) |
| Feature flags | `feature_flags: dict[str, bool]` — present, empty by default (§5.2 on why) |
| Service configuration | `mongo_url`, `redis_url`, `job_deadline_s`, `max_active_jobs`, `llm_provider`, `log_level`, OTel/Prometheus toggles |

**Not yet done:** `server.py` still reads `os.environ` directly in ~15
places (unchanged). `Settings` is additive infrastructure new code depends
on; migrating every existing call site is `06 AD-1`'s full Phase-1 cutover
and is explicitly **not** attempted here (§4) — that removes server.py's
import-time `os.environ["MONGO_URL"]` etc., which is a bigger, riskier change
than this report's scope.

#### Database Layer

| Requirement | Delivered |
|---|---|
| Connection lifecycle | `infrastructure/mongo/client.py::create_mongo_client` — one call site (lazy, confirmed) |
| Health checks | `ping()` — a real `{"ping":1}` command, not a collection scan (fixes `04` O-12's health-endpoint pattern for the *new* probe, §1.3) |
| Index initialization | `infrastructure/mongo/indexes.py::ensure_indexes` — **all 25 rows from `08` §5.1** |
| Startup validation | Wired into `server.py`'s startup hook, replacing `agents.auth.ensure_indexes` |

**Run for real, not just unit-tested** — against this repo's actual local
dev MongoDB (started for this purpose; contains real pre-existing data):

```
ping: True
25/25 indexes applied across 10 collections
second run: 25/25 (byte-identical — true idempotency, not just "no error")
```

One genuine finding surfaced by running it for real (not caught by any
mock): the 5 indexes `agents/auth.py`'s original `ensure_indexes` already
created (I-1/I-3/I-4/I-6/I-7) exist under **pymongo's auto-generated names**
(`email_1`, `token_hash_1`, ...). Asking Mongo to create the *same key spec*
under an explicit, readable name (`I-1_email_unique`) raises
`OperationFailure` code 85 (`IndexOptionsConflict`) — same index, different
label. Fixed by catching that specific code and treating it as satisfied,
not failed. Documented in `indexes.py`'s own module docstring so the next
person who touches this doesn't have to rediscover it.

**The headline result** — `08 §1`'s finding ("the database has five indexes,
all on auth collections; every other query is a collection scan") — verified
fixed against real data:

```
users docs: 128  |  filing_chunks docs: 2,364

users.find({id}) explain()          -> IXSCAN on I-2_id_unique   (was COLLSCAN)
filing_chunks.find({ticker}).sort() -> IXSCAN on I-12_ticker_created (was COLLSCAN)
```

**Not done this phase** (explicitly out of scope — "do not implement
feature-specific repositories"): `ChunkRepository`/`ReportLikeRepository`
have Protocol *definitions* in `application/ports.py` and no Mongo adapter.
No route was changed to read through a repository; `server.py`'s 24 direct
`db.*` calls are untouched.

#### Redis Layer

| Requirement | Delivered |
|---|---|
| Connection management | `infrastructure/redis/client.py` — sized pool (`09` §4.5/§9.5), fail-fast connect timeout |
| Cache abstraction | *Not built* — see §5.3 (nothing in the frozen architecture specifies a generic cache; the concrete needs — job state, events, rate limits — each got a purpose-built adapter instead) |
| Streams support | `infrastructure/redis/event_bus.py::RedisEventBus` — Streams via `XADD`/`XREAD` **only** |
| TTL management | Every key path sets an explicit TTL (job hash 24h, stream 1h, rate-limit window) — `09` RA-1 |
| Health checks | `ping()` + `assert_noeviction_policy()` (`09` §9.2's binding startup assertion) |

**The most important correctness property, proven, not asserted**: `09
§4.1`'s binding rule is "`XREAD`, never `XREADGROUP`" — a consumer group
would silently recreate `01 D-1` (two SSE subscribers splitting one job's
event stream) behind an API that looks more "correct." A static test parses
`event_bus.py`'s own AST and asserts neither `xreadgroup` nor
`xgroup_create` appears anywhere in it.

**The actual `01 D-1` fix, proven with two concurrent subscribers**:

```
test_fan_out_two_concurrent_subscribers_each_get_every_event
  -> both InMemoryEventBus AND RedisEventBus (via fakeredis): PASS
  -> subscriber A receives all 4 events; subscriber B receives all 4 events
```

This is the fix for the single highest-priority defect across the whole
architecture set (`01 D-1`, ADR-001's stated reason Redis was adopted at
all) — built, and proven correct against a real Redis-protocol Streams
implementation, not asserted from the design doc.

**Environment honesty**: no real `redis-server` was available in this
environment (Docker Desktop's engine was not running; no local Redis
binary). Every Redis adapter was verified against **`fakeredis`** — a
Redis-protocol-compatible in-memory server that executes the actual
`XADD`/`XREAD`/`HSET`/`ZADD`/pipeline/pub-sub commands for real, not a mock
of this repository's own code. This is materially stronger evidence than
mocking `redis.asyncio.Redis` directly (a mock can't catch a wrong command
name or argument shape; fakeredis will reject it exactly as a real server
would — confirmed empirically when `CONFIG GET` correctly failed as
unsupported). It is **not** a substitute for a smoke test against a real
Redis server, which is listed as the one open item before Phase 7's
production cutover (§5.4).

**Not done this phase** (explicitly out of scope): no Learning-specific
queue of any kind. `JobStore`/`EventBus`/`RateLimiter` are entirely
feature-agnostic — `JobKind.RESEARCH` and `JobKind.LEARNING` share one
concurrency budget by design (`03`'s own spec), with zero Learning-specific
code anywhere in `infrastructure/redis/`.

#### Authentication & Authorization

Per the phase's own framing ("**Verify**: token validation, user
resolution... **Complete** the shared authentication infrastructure"):

| Item | Verified how |
|---|---|
| Token validation | `agents/auth.py`'s `get_current_user` — unchanged; exercised indirectly via the require_admin integration test (§2) |
| User resolution | Same — `current_user` dependency untouched |
| Authorization middleware | **New**: `infrastructure/security/authorization.py::require_admin` |
| Permission boundaries | `is_owned_or_shared` — the `10 §4.2` three-access-class predicate, built and tested, **not** wired into the 31 routes' read-scoping (that's `06 §7` Ph6 — EQ-2/EQ-3's actual cutover, a deliberate behavior change on 29 live routes that needs its own focused PR, not a side effect of an infrastructure phase) |

**`require_admin` is live**, replacing both of the two existing inline
`if not auth.is_admin(user): raise HTTPException(403, ...)` checks in
`server.py` (`POST /llm/validate`'s custom-provider gate;
`POST /reports/generate`'s custom-provider gate). Verified end-to-end
through a real `TestClient` with a simulated non-admin session
(`app.dependency_overrides`):

```
POST /api/llm/validate {provider: custom} as a non-admin user
  -> 403 {"detail": "The Custom LLM provider is restricted to admin accounts.", "type": "forbidden"}
```

Identical message, identical status code to the code it replaced — the only
addition is `"type"` (additive; Zod strips unknown keys, matching the
established pattern elsewhere in this contract).

**`agents/auth.py` itself was not moved** — `06 AD-10` schedules that
physical relocation for Phase 6. This phase's authorization module imports
`is_admin` from it unchanged, per the strangler-fig discipline.

#### Logging & Observability

| Requirement | Delivered | Live? |
|---|---|---|
| Structured logging | *Correlation-id* piece done; JSON formatting deferred (§5.5) | ✅ live |
| Correlation IDs | `infrastructure/observability/logging.py` — contextvar + `logging.Filter`; middleware sets it per-request, honors an inbound `X-Request-ID` | ✅ live, verified |
| Request tracing | `infrastructure/observability/tracing.py::setup_tracing` — OTel SDK, FastAPI/pymongo/httpx auto-instrumentation | 🟡 built + proven safe, **not called** from server.py's own startup (§4) |
| Prometheus metrics | `infrastructure/observability/metrics.py` — HTTP request counter/histogram active; 10 more metric names defined for Phase 3/4/7's call sites to increment | ✅ live for HTTP; defined-not-wired for pipeline/Redis/Mongo |
| Health endpoints | `/health` unchanged | — |
| Readiness checks | **New**: `GET /api/health/ready` | ✅ live |

**"Every request should be traceable end-to-end" — honest scope**: every
request now carries a correlation id (echoed via `X-Request-ID`, injected
into every log line via the filter) and is counted/timed in Prometheus. What
is **not** yet true end-to-end: distributed trace *spans* are not active on
the live app (tracing is built and proven safe, not switched on — §4), and
node-level/pipeline-level spans don't exist because the graph itself isn't
instrumented (that's `07 §6.1`'s work, gated on Phase 3's port injection).
§3 of the Observability Report below states this distinction explicitly
rather than claiming more than what's live.

Verified live, via `TestClient` against the real Mongo-backed app:

```
GET /api/  (no X-Request-ID header) -> response carries a generated x-request-id
GET /api/  (X-Request-ID: my-trace-id-123) -> echoed back verbatim
GET /api/metrics -> 200, text/plain, contains alphascribe_http_requests_total
access-control-allow-origin / -credentials headers unchanged after adding the middleware
```

#### Error Handling

`app/api/errors.py` — one handler, `domain_error_handler`, mapping every
`domain.errors.DomainError` subclass (9 concrete kinds: `NotFoundError`,
`ValidationError`, `ConflictError`, `AuthorizationError`, `RateLimitedError`,
`DeadlineExceededError`, `InfrastructureError`, `LLMProviderError`,
`StreamingError`) to `{"detail": "...", "type": "<code>"}` with the right
status code. Registered additively via
`app.add_exception_handler(DomainError, domain_error_handler)`.

**Zero existing behavior changed**: no route currently raises a
`DomainError` except the two `require_admin` call sites (which produce the
*same* response as before — verified, §2). The existing
`RequestValidationError` handler (strips pydantic's `input`, `10` T-14) is
completely untouched.

**`LLMProviderError` gets special handling** — its message is *never* passed
through to the client, mirroring `server.py`'s own existing pipeline-error
redaction (`server.py:779-795`) rather than trusting every future raiser to
remember to redact.

#### Background Infrastructure

`application/jobs.py::JobLifecycle` — `start` (admission control + creation
+ opening event), `mark_running`, `publish`, `complete`, `fail`, `cancel`
(idempotent on an already-terminal job, per `10 §5`'s fire-and-forget cancel
contract), `is_past_deadline`, `reap_stale` (the `09 §6.2` self-healing
sweep). Feature-agnostic — takes a `JobKind` but no research/Learning logic
anywhere in it.

Proven end-to-end against the real in-memory adapters (not mocks):

```
test_start_enforces_the_shared_concurrency_budget
  -> research job + learning job together exhaust a budget of 2; a 3rd of either kind -> RateLimitedError(429)
test_reap_stale_frees_the_slot_and_marks_the_job_failed
  -> a "crashed" job (backdated past max_lifetime) is freed AND marked failed, not silently forgotten
```

**Not the full `01 D-6` restart sweep**: that additionally needs Mongo's
durable job records (a repository this phase deliberately does not build).
`reap_stale()` is the JobStore-only half — freeing concurrency slots for
jobs whose active-set entry outlived `MAX_JOB_LIFETIME` — which works
standalone today and composes with the Mongo-backed half once Phase 3/4
builds it.

**Not wired live**: `server.py`'s `JOBS`/`JOB_QUEUES` dicts and
`_run_pipeline` are completely untouched. Cutting the live report pipeline
onto `JobLifecycle` is `06 §7` Ph4's job, and doing it in this same pass
would mean touching the one code path every existing E2E report-generation
test depends on, without the dedicated verification budget that deserves.

#### Streaming Infrastructure

`infrastructure/streaming/sse.py::sse_response` — one function, generic
over any `EventBus.subscribe()` iterator. Framing verified to match
**exactly** what Phase 0's `test_sse_event_shape.py` already proved the
shipped frontend expects (unnamed `data:` frames, `: keepalive` comment,
terminal `event: end`) — not the stale API doc's framing.

Proven end-to-end through a **real EventBus**, not hand-built event dicts:

```
publish 3 events (incl. a terminal one) to InMemoryEventBus
  -> sse_response(bus.subscribe(job_id)) produces exactly:
     data: {...}\n\n   (x3)
     event: end\ndata: {}\n\n
  -> nothing after the terminal frame
```

Cancellation propagation and error propagation are properties of the
`EventBus`/`JobLifecycle` layer underneath this transport (a cancel writes a
`warn` event; a fail writes an `error` event; `sse_response` frames whatever
it's given) — already exercised by `test_job_lifecycle.py`'s cancel/fail
tests, not re-tested at the transport layer redundantly.

**Not wired live**: `server.py`'s `GET /reports/{job_id}/stream` still uses
its own single-`asyncio.Queue` generator, `01 D-1` unfixed *there*. Fixing it
in place needs the job lifecycle cut over at the same time (Ph4) — this
module is what that cutover migrates onto, built and proven correct first.

### 1.2 Files changed

**New source (1,618 lines):**

```
app/settings.py                              app/container.py
app/api/errors.py
domain/errors.py  domain/events.py  domain/models.py
application/ports.py  application/jobs.py
infrastructure/mongo/client.py  infrastructure/mongo/indexes.py
infrastructure/redis/client.py  infrastructure/redis/event_bus.py
infrastructure/redis/job_store.py  infrastructure/redis/rate_limiter.py
infrastructure/llm/registry.py
infrastructure/security/authorization.py
infrastructure/observability/logging.py  metrics.py  tracing.py
infrastructure/streaming/sse.py
```

**New tests (2,502 lines, 12 files):** `test_settings.py`,
`test_mongo_infrastructure.py`, `test_redis_client.py`,
`test_redis_event_bus.py`, `test_redis_job_store.py`,
`test_redis_rate_limiter.py`, `test_authorization.py`,
`test_observability.py`, `test_tracing_setup.py`,
`test_sse_infrastructure.py`, `test_job_lifecycle.py`, `test_container.py`.

**Modified (production code — 3 files, small diffs):**

| File | Diff | What |
|---|---|---|
| `agents/llm.py` | +47/−22 | Collapsed dispatch (`01 D-3`) — see §1.1 |
| `agents/ingest.py` | +6/−1 | *(carried from Phase 0, unchanged this phase)* |
| `server.py` | +111/−9 | Imports; `GET /health/ready`; `GET /metrics`; `DomainError` handler registration; correlation-id + metrics middleware; 2× `require_admin` cutover; startup hook → `ensure_mongo_indexes` + correlation filter |

**Modified (test-only — 7 files):** `test_llm_validate.py` (+2 tests, 1
hermeticity fix — §5.1), `test_ssrf_guard.py` *(carried from Phase 0)*,
`test_route_inventory.py` (2 additive routes recognized — §1.3),
`pytest.ini` *(carried from Phase 0)*, plus the 5
`backend_test_iter*.py`/`test_*.py` live-marker files *(carried from Phase
0, untouched this phase)*.

### 1.3 Architectural decisions referenced

`06` AD-1, AD-2, AD-3, AD-6, AD-9, AD-10; `07` §5.4 (deadline shape);
`08` §5.1, DA-8; `09` §4.1, §4.5, §6.2, §7.1, §9.2, §9.5, RA-1, RA-2, RA-4;
`10` §4.2, §5, T-13, T-14, SD-2, SD-3; ADR-001, ADR-003, ADR-004, ADR-024.
Every module docstring in this delivery cites the specific ID it implements.

### 1.4 Risks

| ID | Risk | Sev | Mitigation |
|---|---|---|---|
| **R-1** | No real Redis server was available to verify against (Docker engine not running) — adapters are proven against fakeredis, not a production Redis | Medium | fakeredis executes real commands, not a mock of this code; still, a real-Redis smoke test is the explicit gate before Phase 7's `JOB_BACKEND=redis` cutover (§5.4) |
| **R-2** | Two live production-code changes touch shared modules (`agents/llm.py`'s dispatch, `server.py`'s admin checks) | Medium | Both are behind the existing regression suite (3 LLM test files + 1 new) and a live end-to-end TestClient proof (§2); diffs are small (+47/−22 and 2 call sites respectively) |
| **R-3** | OTel tracing is built but not activated on the live app — a future "just call `setup_tracing()`" change is one line but untested against the FULL app (only tested against a minimal FastAPI app, §2) | Low | Documented explicitly (§4); the minimal-app test already proved the specific risk (route-surface change) empirically safe on the real `server.app` too, ad hoc, during development |
| **R-4** | `infrastructure/security/authorization.py` imports `agents.auth` — a cross-layer import that is *correct* per the current physical layout (auth.py is infra-classified content sitting in `agents/` pre-move, `06 AD-10`) but reads as a violation to a future contributor unfamiliar with that reasoning | Low | Documented in the module's own docstring; `test_architecture.py`'s dependency-rule test deliberately scopes to the LangGraph-proper files, not this one, for the same reason |
| **R-5** | `.coveragerc` did not initially include the new `app/domain/application/infrastructure` directories — coverage numbers would have silently excluded ~1,600 lines of new code | Low (caught, fixed) | Fixed before this report was written; see §2 |

### 1.5 Technical debt (discovered or deliberately deferred)

| Item | Status |
|---|---|
| `server.py` still has ~15 direct `os.environ` reads | Deliberately deferred — full `06 AD-1` cutover is riskier than this phase's scope |
| `ChunkRepository`/`ReportLikeRepository` — Protocol only, no adapter | Deliberately deferred — explicit scope exclusion |
| `JobLifecycle`/`EventBus`/`SSE` not cut into the live pipeline | Deliberately deferred — `06 §7` Ph4, needs its own verification budget |
| OTel tracing built, not activated live | Deliberately deferred — see R-3 |
| No real-Redis verification | Open item before Phase 7 (§5.4) |
| `feature_flags: dict[str, bool]` on `Settings` is unused by any code | Recorded, not removed — see §5.2 |

---

## 2. Test Report

### 2.1 Added tests

| Count | Category |
|---|---|
| **69 new hermetic tests**, 12 new files | Settings, Mongo client/indexes, Redis client/EventBus/JobStore/RateLimiter, LLM dispatch fix (2 in an existing file), authorization, observability (logging/metrics/tracing), SSE transport, JobLifecycle, container |
| **0 new live tests** | Correctly out of scope — this phase built infrastructure, not new user-facing behavior requiring live-server E2E coverage |

### 2.2 Passing tests

```
150 passed, 0 failed   (hermetic: pytest -m "not live")
 43 live-marked, unchanged, not executed in this environment (need a running server)
193 total collected
```

Full coverage, hermetic run only, `.coveragerc` scoped to `agents/`,
`server.py`, and all four new Phase 1 directories:

```
application/jobs.py                    98.1%
application/ports.py                   90.3%   (Protocol stub bodies)
domain/errors.py                      100.0%
domain/events.py                      100.0%
domain/models.py                       96.8%
infrastructure/llm/registry.py         92.3%
infrastructure/mongo/client.py        100.0%
infrastructure/mongo/indexes.py       100.0%
infrastructure/observability/*        100.0%   (logging, metrics, tracing)
infrastructure/redis/client.py         96.2%
infrastructure/redis/event_bus.py      97.0%
infrastructure/redis/job_store.py      98.6%
infrastructure/redis/rate_limiter.py  100.0%
infrastructure/security/authorization  100.0%
infrastructure/streaming/sse.py       100.0%
app/settings.py                       100.0%
app/container.py                      100.0%
app/api/errors.py                      58.3%   (LLMProviderError branch untriggered — no live raiser yet)
──────────────────────────────────────────────
TOTAL (incl. agents/ + server.py)      59.3%   (up from Phase 0's 44.5%)
```

Every new module this phase built is at ≥90% coverage; the aggregate total
is pulled down only by `server.py` (28.9% — most of its routes need a live
DB/auth session, correctly covered by the `live`-marked suite instead) and
the pre-existing `agents/` modules unchanged from Phase 0.

### 2.3 Remaining gaps

| Gap | Why it's not this phase's job |
|---|---|
| `server.py` route handlers (71.1% uncovered) | Needs a live Mongo + auth flow — the existing `live` suite's job |
| Real-Redis integration (only fakeredis-verified) | Explicit open item, §5.4 |
| `LLMProviderError`'s redaction branch in `app/api/errors.py` | No code raises it yet — nothing to trigger it until a future call site does |
| Graph/node-level tracing spans | Gated on Phase 3's port injection (`07 §6.1`) |
| End-to-end SSE through the *live* `stream_report` route | Deliberately not cut over — transport is proven against a real `EventBus`, just not the live route (§1.1) |

---

## 3. Observability Report

| Pillar | Confirmed |
|---|---|
| **Logging** | ✅ Correlation-id filter installed at startup; every log record carries `correlation_id` (`"-"` when unset, never a `KeyError`); middleware sets it per-request from `X-Request-ID` or a generated uuid4. JSON formatting **not** done (unchanged from Phase 0's finding — human-readable stays the default; the correlation id is the piece that mattered for this phase, and composes with either format later). |
| **Metrics** | ✅ `GET /api/metrics` live, Prometheus exposition format, verified via real `TestClient` request. `alphascribe_http_requests_total`/`_duration_seconds` actively incremented on every request. 10 more metric names (`pipeline_*`, `node_*`, `llm_calls_*`, `auth_failures_*`, `authz_denied_*`, `redis_errors_*`, `ratelimit_degraded`, `jobs_active`) are **defined, not yet incremented** — no pipeline/job/Redis call site exists live yet to increment them from. |
| **Tracing** | 🟡 OpenTelemetry SDK + FastAPI/pymongo/httpx auto-instrumentation **built and proven safe** (verified against both a minimal app and, ad hoc, the real `server.app` — zero route-surface change, a real request still 200s). **Not activated** on the live app this phase — `setup_tracing()` is not called from `server.py`'s startup. This is the one item in this report where "implemented" and "wired live" genuinely diverge; §4 states why. |
| **Health endpoints** | ✅ `GET /api/health` unchanged. **New**: `GET /api/health/ready` — a true dependency check (`{"ping":1}`, not a collection count) verified live returning `{"ready": true, "mongo": true, "retrieval": {...}}` against the real dev database. |

**"Every request should be traceable end-to-end" — precise claim**: true for
*correlation* (one id follows a request through logs and back to the
client via `X-Request-ID`) and *counting* (every request is in Prometheus).
Not yet true for *distributed tracing* (no span is emitted for a live
request today) or for *pipeline-internal* observability (no node/LLM-call
span or metric fires yet, because the pipeline itself isn't instrumented).
Both are one `setup_tracing()` call and Phase 3's port injection away,
respectively — deliberately sequenced after this report, not silently
short of the claim.

---

## 4. Readiness Assessment

### 4.1 Determination

> ## ✅ **Ready for Phase 2** (the user's next feature-implementation
> phase — see §0's numbering note), **with three explicit conditions**

### 4.2 Evidence

| Claim | Evidence |
|---|---|
| Shared services are operational | `JobLifecycle`, `EventBus`, `JobStore`, `RateLimiter` all pass end-to-end tests against real (in-memory) or real-protocol (fakeredis) backends |
| MongoDB foundation is production-ready | 25/25 indexes applied idempotently against **real data** (128 users, 2,364 chunks); `IXSCAN` proven on both hot-path queries |
| Redis foundation is *built* production-ready, *verification* incomplete | All adapters pass port-conformance tests against fakeredis; **no real Redis server was verified against** — condition 1 below |
| SSE infrastructure is reusable | Proven against a real `EventBus`, framing matches the shipped frontend exactly |
| Authentication infrastructure is complete for this phase's scope | `require_admin` live, tested, end-to-end verified; deeper read-scoping (EQ-2/EQ-3) is correctly Phase 6 scope, not this one |
| Tests pass | 150/150 hermetic, 0 failures, 59.3% coverage on the touched surface |
| No approved API contract changed | `test_route_inventory.py` + `test_request_schemas.py` both green; the only 2 new routes were pre-approved additions (`11`'s impact table) |
| No frontend compatibility break | Nothing under `web/` touched; CORS/cookie behavior verified unchanged via live `TestClient` |

### 4.3 The three conditions

1. **Verify the Redis adapters against a real Redis server before flipping
   `JOB_BACKEND=redis` in any environment.** fakeredis is strong evidence,
   not final proof. A 30-minute smoke test (start `redis:7-alpine`, run the
   same three port-conformance suites against it) closes this before Phase
   7's actual cutover — it does not block Phase 2's feature work, which can
   proceed entirely on `JOB_BACKEND=memory` (the default).
2. **Do not assume tracing is live.** Anyone building on this phase should
   know `setup_tracing()` exists and works, but a request today produces no
   span. If Phase 2's work wants trace visibility, activating it is a
   one-line addition to `server.py`'s startup — not done here so it isn't
   claimed without having been exercised against the full app under this
   report's own verification bar.
3. **The pipeline (report generation) is unchanged and still has `01 D-1`
   unfixed live.** This phase built the fix (`EventBus`'s fan-out) and
   proved it correct standalone. It is not protecting real users yet. If
   Phase 2 is Learning implementation, `06 §7`'s own ordering requires the
   Ph4 cutover (job lifecycle + EventBus wired into the live pipeline)
   **before** Learning is built on top of it — building Learning directly
   against today's `server.py` internals would inherit the exact defect
   Redis was adopted to fix.

---

## 5. Findings Requiring Attention (not new ADRs — see below)

Per this phase's own rule ("if implementation requires a new architectural
decision, stop and create a new ADR"): **none of the following required
one.** Each is either an implementation detail within an already-ratified
decision, or a scope/sequencing note for whoever picks up the next phase.

### 5.1 Environment-leak class of test hazard, recurring

Phase 0 found `LLM_ALLOW_PRIVATE_BASE_URL` leaking from a developer's
`.env` into `test_ssrf_guard.py` via `import server`'s `load_dotenv()` side
effect. This phase found the **same class of hazard again**, for
`LLM_BASE_URL`, in `test_llm_validate.py` — triggered by the D-3 fix itself
(making `validate_key` correctly consult `LLM_BASE_URL` means a test that
assumed the built-in default now depends on whether something else in the
same worker already imported `server`). Fixed the same way (save/clear/
restore). **This is now a two-time pattern**, not a one-off — worth a
one-line rule for whoever writes the next hermetic test touching
`agents/llm.py`: assume `LLM_BASE_URL`/`LLM_ALLOW_PRIVATE_BASE_URL` may
already be set in the environment, and clear them explicitly.

### 5.2 `feature_flags` on `Settings` is currently decorative

The phase asked to "centralize... feature flags." `Settings.feature_flags:
dict[str, bool]` exists, defaults to empty, and nothing reads it. Kept
rather than removed because centralizing config *shape* ahead of the first
flag that needs it is cheap and matches the field's siblings (`admin_emails`
etc. were also unused by anything until this phase gave them a consumer);
removing it would just mean re-adding the same field the day Phase 2 wants
its first flag. Flagged here so it isn't mistaken for "flags are wired up."

### 5.3 No generic "cache abstraction" was built

The phase's Redis Layer scope lists "cache abstraction" alongside
Streams/TTL/health. Nothing in the frozen architecture (`09`) specifies a
generic cache port — every concrete Redis need it does specify (job state,
events, rate limits) got its own purpose-built adapter instead, each with
its own TTL policy already baked in (`09 §3`'s keyspace table). Building an
unused generic `Cache` Protocol now would be exactly the "interface with one
implementation" `06`'s own anti-YAGNI check warns against. If a future
feature needs a plain get/set/TTL cache (e.g. the deferred SEC-index cache
in `09 §14`), it gets a Protocol *then*, sized to what it actually needs.

### 5.4 Real-Redis verification gap

Already stated as Readiness condition 1 (§4.3). Restated here because it's
the single most important thing for whoever runs Phase 7 to close before
`JOB_BACKEND=redis` goes anywhere near production.

---

*Companion documents:* [`13_M2_Phase0_Completion_Report.md`](13_M2_Phase0_Completion_Report.md) ·
[`06`](06_Clean_Architecture_Migration_Plan.md)–[`11`](11_ADR_Index.md) ·
[`12_M2_Implementation_Charter.md`](12_M2_Implementation_Charter.md) · index:
[`00_README.md`](00_README.md)
