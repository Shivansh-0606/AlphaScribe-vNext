# Backend Engineering Milestone 2 — Phase 0 Completion Report

**Status:** ✅ **COMPLETE**
**Milestone:** Backend Engineering M2, Phase 0 (Foundation & Safety Net) · **Date:** 2026-08-04
**Governed by:** Backend Architecture `v1.0` (🔒 frozen) — Documents
[`06`](06_Clean_Architecture_Migration_Plan.md)–[`11`](11_ADR_Index.md)
**Executed per:** [`12_M2_Implementation_Charter.md`](12_M2_Implementation_Charter.md)
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main` · commit `e5650be`

> This is a deliverable, not a planning document — no architecture was
> redesigned, no ADR was needed (§6), and every change is bounded to what
> Phase 0 authorizes: tests, CI, and one isolated bug fix discovered while
> writing a security regression test (§1.3).

---

## 0. Scope discipline — what this phase did and did not touch

| Constraint | Held? |
|---|---|
| No Learning Backend functionality implemented | ✅ |
| No API behavior changed | ✅ — verified empirically, §3 |
| No frontend contract changed | ✅ — nothing under `web/` touched |
| No new architectural decision | ✅ — see §6 |
| `pytest.ini` `addopts` unmodified | ✅ verified byte-identical (§4.5) |
| `backend_test_iter*.py` kept, not deleted | ✅ |
| No unnecessary tooling introduced | ✅ — no linter/formatter added (none existed); no Dockerfile (Phase 7 scope) |

**Total production-code footprint: one file, one bug fix, 6 lines.**
Everything else is new test files, two config files (`pytest.ini` markers
section, new `.coveragerc`), one dependency (`pytest-cov`), and one new CI
workflow. `git diff --stat` for every touched non-test file:

```
backend/agents/ingest.py   | 6 +++++-   (security fix, §1.3)
backend/pytest.ini         | 6 ++++++   (markers section, additive)
backend/requirements.txt   | 1 +        (pytest-cov)
```

---

## 1. Completed Tasks

### 1.1 Testing safety net — 72 new hermetic tests, 11 new files

| File | Tests | Covers |
|---|---|---|
| `tests/unit/test_scoring.py` | 9 | `compute_scorecard` — faithfulness, context precision, answer relevance, overall, graceful defaults (05 §3.2 highest-priority gap) |
| `tests/unit/test_chunking.py` | 7 | `chunk_text` — paragraph packing, sentence-split overflow, overlap stitching, CRLF/blank-line normalization |
| `tests/unit/test_retrieval_fusion.py` | 6 | `_minmax` edge cases; `retrieve()`'s **BM25-only degradation branch** (05 §3.2: "a documented production path… untested"), empty-corpus path, ticker normalization |
| `tests/unit/test_nodes_pure.py` | 8 | `_extract_candidate_claims` (numeric filter, dedupe, 12-cap, bps/pp/$ units) and `_format_docs` (numbering, atomic budget truncation) |
| `tests/unit/test_ingest_helpers.py` | 10 | `_clean_html`, `_fmt_num`, and `_bse_pdf_url`'s hostname allowlist — **found and fixed a real bypass, §1.3** |
| `tests/unit/test_llm_json_repair.py` | 11 | `chat_json`'s full JSON-repair ladder (all branches — clean, fenced, embedded-in-prose, brace-less, schema-envelope, bare-array), `_strip_code_fence`, `_retry_after_seconds`, `_schema_hint` |
| `tests/unit/test_auth_pure.py` | 8 | scrypt hash/verify roundtrip, OTP pepper is load-bearing, sliding-window rate limiter incl. stale-hit pruning and the no-leak-on-unseen-key guard |
| `tests/unit/test_server_helpers.py` | 4 | session-cookie policy (`HttpOnly`/`Secure`/`SameSite=Lax`/`Max-Age`), the app-wide 422 `input`-stripping handler |
| `tests/unit/test_architecture.py` | 2 | Dependency-rule seed (06 AD-5) — see §1.2 |
| `tests/contract/test_route_inventory.py` | 2 | Exact route-surface match against the 31 approved routes |
| `tests/contract/test_request_schemas.py` | 2 | Every request model's required-field set vs. the frozen frontend Zod schemas |
| `tests/contract/test_sse_event_shape.py` | 3 | SSE framing matches `sse-client.ts`, not the stale API doc; cancel response shape |

Every new test was run and is green (§4). Style matches the existing suite
exactly — plain functions, module-attribute monkeypatch + restore, a
`__main__` runner block — per `test_ssrf_guard.py`/`test_llm_retry.py`'s
established convention. No test framework, fixture library, or mocking
package was introduced.

### 1.2 Dependency-rule guard — scoped honestly, not aspirationally

`06 AD-5` specifies an import-matrix test over `domain/`, `application/`,
`agents/`, `infrastructure/`, `app/` — **none of which exist yet** (they land
across Migration Phases 1–3). Writing that test today against non-existent
directories would either vacuously pass or need rewriting at every phase.

`tests/unit/test_architecture.py` instead guards what's real right now: the
five files that are actually the "agents (LangGraph)" layer in `06 §2.2`'s
diagram (`graph.py`, `nodes.py`, `state.py`, `schemas.py`, `retrieval.py`) must
not import `motor`/`pymongo`/`redis`/`fastapi`/`starlette` directly, and
nothing under `agents/` may import `server.py`.

This surfaced a real scoping subtlety worth recording: my first draft applied
that rule to **every** file under `backend/agents/`, which failed on
`auth.py`'s `from pymongo.errors import DuplicateKeyError`. That's correct
behavior, not a violation — `06 §2.3`/`AD-10` already classifies `auth.py` as
destined for `infrastructure/security/`, not the LangGraph layer; today's flat
`agents/` directory is a pre-refactor grab-bag, and the test now reflects the
*logical* layer boundary rather than the *physical* directory. This becomes
the seed the full AD-5 matrix grows into once Phase 3 physically relocates
these modules.

### 1.3 🔴 Security fix discovered while writing a regression test

**`_bse_pdf_url`'s hostname allowlist (`agents/ingest.py:194-204`) had a
domain-suffix bypass.** The frozen security doc (`10` T-19) rated this control
"✅ Mitigated… ❌ untested." Writing the "untested" part's test proved the
"Mitigated" part wrong:

```python
urlparse("https://evilbseindia.com/x.pdf").hostname.endswith("bseindia.com")
# -> True — "evilbseindia.com" is a distinct, attacker-registerable domain,
#    not bseindia.com or a subdomain of it, but the string-suffix check
#    can't tell the difference.
```

**Fix applied** (`agents/ingest.py`, 6 lines): match the exact host or a
proper subdomain (`host == "bseindia.com" or host.endswith(".bseindia.com")`),
not a bare string suffix. Verified: the exploit case now returns `None`; every
legitimate BSE URL shape still resolves exactly as before (`tests/unit/test_ingest_helpers.py`, 4 passing cases covering both).

**Why fixed now rather than deferred as an Engineering Question:** per the M2
charter's conflict procedure (§6 of this report), a *new architectural
decision* stops and gets an EQ. This is not one — the *intent* ("only trust
BSE's own host") was already ratified; only the implementation of that intent
was wrong. The fix has zero API/contract surface (the function is reachable
only via the best-effort `fetch_bse_annual_report`, `06` C-8), changes no
external behavior for any legitimate input, and is a one-line correctness fix
squarely inside Phase 0's own mandate to "identify… security risks… prepare
the codebase… without changing external behavior." Flagged prominently here
rather than buried, precisely so this judgment call is reviewable.

### 1.4 Test hermeticity — 43 live tests correctly categorized, zero deleted

All 10 pre-existing HTTP-integration files (`backend_test.py`,
`backend_test_iter2-6.py`, `test_account.py`, `test_auth.py`,
`test_password_reset.py`, `test_reports_scoping.py` — 43 tests) now carry
`pytestmark = pytest.mark.live`, added as a 4-line block each with no other
change (`git diff --stat`, §0). `06 C-6` — nothing was deleted or consolidated.

`pytest.ini` gained a `markers =` section registering `live` — **additive
only**; `addopts` is byte-identical to before (`git diff` confirms, and the
file's own "AGENT: do NOT modify addopts" instruction was read and honored
literally, not just in spirit).

### 1.5 🟡 Real test-isolation bug found and fixed (not mine to have caused, but mine to fix)

Running the new hermetic suite alongside the pre-existing one surfaced a
genuine, pre-existing hazard: **`test_ssrf_guard.py` failed** the moment it
ran in the same pytest-xdist worker as anything that imports `server` (which
several of my new contract/unit tests do, for good reason — §1.6).

Root cause: `server.py` calls `load_dotenv()` at import time, and a
developer's local `backend/.env` in this repo sets
`LLM_ALLOW_PRIVATE_BASE_URL=true` — a legitimate local-LLM escape hatch
(`llm.py`'s own docstring: "only set for a single-user/local instance"). Once
anything imports `server` in a worker process, that setting leaks into
`os.environ` for the rest of that worker's session, silently disabling the
SSRF guard for every subsequent test — including one that exists specifically
to prove the guard works.

**Fixed in the test, not production code**: `test_ssrf_guard.py` now saves,
clears, and restores `LLM_ALLOW_PRIVATE_BASE_URL` around its own assertions —
4 lines, matching the existing save/restore pattern already used elsewhere in
this suite (e.g. `test_otp_hash_changes_if_the_pepper_changes`). A security
regression test must not be at the mercy of an incidental environment leak
from an unrelated import in the same process.

**Also fixed at the CI layer**: `backend-ci.yml`'s hermetic job explicitly
sets `LLM_ALLOW_PRIVATE_BASE_URL: ""`, so a maintainer's local `.env` habit can
never silently pass or fail CI depending on what they happen to have set for
their own local-Ollama workflow.

### 1.6 API contract validated against the live app object, not against the docs

Every contract assertion in `tests/contract/` reads `app.openapi()` from the
**actual running FastAPI app object**, imported hermetically (no live Mongo
needed — motor/pymongo clients connect lazily; `app.openapi()` touches no
database). This is deliberately stronger than diffing against
`docs/planning/05-API-Documentation.md`, which `01 D-11` already flagged as
stale — and the SSE contract test (`test_sse_event_shape.py`) proves that
staleness directly: it asserts the *real* framing (`sse-client.ts`'s
unnamed-`data:`-frame + named-`end`-event contract) and asserts the *stale
doc's* framing (`event: pipeline`, `event: done`) is **absent** from the
implementation.

### 1.7 CI/CD

Added `.github/workflows/backend-ci.yml` — two jobs:

- **`hermetic`** (runs on every push/PR, no secrets): installs deps, runs
  `pytest -n 2 --dist loadscope -m "not live" --cov`, uploads a coverage
  artifact. Uses the project's exact xdist invocation, unmodified.
- **`live`** (main-branch only, gated per `10 SD-12` — never on a fork PR):
  a documented skeleton that no-ops with an explicit `::notice::` until a
  maintainer populates `CI_MONGO_URL`/`CI_GEMINI_API_KEY` repo secrets. It does
  not silently fail; it visibly explains why it isn't running.

**Deliberately not added**: lint/format/type-check (none configured for
`backend/` today — adding one is a tooling decision outside "strengthen what
exists," and the charter says not to introduce unnecessary tooling); a
Dockerfile or Docker-build job (no Dockerfile exists — that's `06 §7` Phase 7
scope, not Phase 0).

---

## 2. Repository Readiness Report

### 2.1 Determination

> ## ✅ **Ready for implementation, with minor issues**

### 2.2 Evidence

| Verification | Method | Result |
|---|---|---|
| Route surface matches `06 C-1` | `test_route_inventory.py` against the live `app.openapi()` | ✅ 31/31, exact match |
| Request contracts match the frozen frontend | `test_request_schemas.py`, 11 models | ✅ exact required-field match |
| SSE framing matches the shipped frontend, not the stale doc | `test_sse_event_shape.py` | ✅ |
| Dependency rule (LangGraph layer) | `test_architecture.py` | ✅ clean today |
| `agents/` never imports `server.py` | `test_architecture.py` | ✅ |
| Auth cookie policy | `test_server_helpers.py` | ✅ HttpOnly/Secure/SameSite/Max-Age all correct |
| 422 error handler strips secrets app-wide | `test_server_helpers.py` | ✅ |
| SSRF guard | `test_ssrf_guard.py` (fixed for isolation, §1.5) | ✅ |
| Key isolation, retry policy, key validation | pre-existing 3 files | ✅ unmodified, still green |
| Full hermetic suite | `pytest -m "not live"` | ✅ **81/81 passing** |
| `pytest.ini` `addopts` unmodified | `git diff` | ✅ byte-identical |

### 2.3 "Minor issues" — why not a clean "Ready"

| # | Issue | Severity | Blocking? |
|---|---|---|---|
| 1 | `import server` takes **~23 seconds** (cold) due to eager imports of `langgraph`, `fastembed`, and three LLM SDKs at module scope. Every hermetic test file that imports `server` pays this once per worker. | Low — a CI/local-dev friction cost, not a correctness issue | No — resolved structurally by `06 AD-1`'s Phase 1 app factory, not a Phase 0 fix |
| 2 | `@app.on_event("startup"/"shutdown")` — deprecated FastAPI API, emits `DeprecationWarning` on every import (visible in the pytest output, §4). | Low | No — `06 MR-10` already tracks this for the Phase 1 `lifespan` migration |
| 3 | The `.env`-leak isolation hazard (§1.5) is fixed in the one test it broke, but the *mechanism* (any hermetic test that imports `server` inherits whatever the developer's local `.env` says) still exists for any *future* test that asserts something env-sensitive. | Medium | No — flagged; the durable fix is `06 AD-1` (no import-time `os.environ` reads); CI is hardened now (§1.5) |
| 4 | Response shapes have **zero typed contract** at the OpenAPI level — no handler declares `response_model=`, so `test_request_schemas.py` could only validate *requests*, not responses (§3.3). | Medium | No — already the exact, cited gap in `05 F-6`/`02`; the fix (`06 AD-11` typed DTOs) is Phase 6 scope, not Phase 0 |

None of these block starting Phase 1. All four are either already-tracked
consequences of decisions this milestone already ratified, or (item 3) a
freshly-hardened but not fully eliminated hazard whose permanent fix is the
same Phase 1 work that was already scheduled next.

---

## 3. API Compatibility Report

### 3.1 Determination

> ## ✅ **Fully compatible**

### 3.2 What was checked

| Area | Check | Result |
|---|---|---|
| Request schema | `test_request_schemas.py` — required fields, 11 models | ✅ match |
| Response schema | See §3.3 — **not independently verifiable today**, but nothing observed changed it | ⚠️ see below |
| HTTP status codes | Not re-derivable without a live call; no behavior-affecting code changed except `_bse_pdf_url` (internal, unreachable via any route directly) | ✅ unaffected |
| Error payloads | 422 stripping verified directly (`test_server_helpers.py`) | ✅ |
| SSE event format | `test_sse_event_shape.py` — matches `sse-client.ts` | ✅ |
| Cancellation semantics | `test_sse_event_shape.py` — response shape intact; behavior (idempotent, fire-and-forget tolerant) unchanged, no code touched | ✅ |

### 3.3 The one honest caveat

Response bodies carry **no typed OpenAPI schema today** — FastAPI only
generates one for a handler with a `response_model` or a typed return
annotation, and none of the 31 handlers have either (confirmed by inspecting
`app.openapi()['paths'][...]['responses']` directly: every 200 response's
schema is `{}`). This means:

- **Nothing in this repository — before or after Phase 0 — has ever
  mechanically verified response shapes against the frontend.** That is
  exactly what `05 F-6` already said; Phase 0 makes it a *proven*, checked
  fact rather than an audit claim.
- I did **not** add `response_model=` annotations to close this gap. Doing so
  is itself a considered design change (`06 AD-11`, ADR-006 — transport DTOs
  separate from domain models) scoped to **Phase 6**, and retrofitting it onto
  31 handlers now would be real production-code surface far beyond "tests
  only," for a phase explicitly gated on "no new architectural decisions."

**No incompatibility was found or introduced.** The one thing that changed
production behavior (`_bse_pdf_url`, §1.3) has no route, no contract, and no
frontend surface.

---

## 4. Test Coverage Report

### 4.1 Existing coverage (before Phase 0)

Measured by running only the 4 pre-existing hermetic files
(`test_ssrf_guard.py`, `test_gemini_key_isolation.py`, `test_llm_retry.py`,
`test_llm_validate.py` — 9 tests):

```
TOTAL                          977    843  13.7%
```

`server.py` was **never imported by any hermetic test** — 0% is not shown
because it was never measured at all. `agents/llm.py` was the only module with
meaningful coverage (46.2%), from the 3 files that already targeted it.

### 4.2 Added coverage (after Phase 0)

Full hermetic suite (`pytest -m "not live"`, 81 tests, `.coveragerc` scoped to
`agents/` + `server.py`):

```
Name                      Stmts   Miss  Cover
---------------------------------------------
agents\auth.py              113     56  50.4%
agents\company_index.py      81     62  23.5%
agents\ingest.py            169    122  27.8%
agents\llm.py               208     46  77.9%
agents\nodes.py             130     89  31.5%
agents\notify.py             17      9  47.1%
agents\retrieval.py         148     56  62.2%
server.py                   631    452  28.4%
---------------------------------------------
TOTAL                      1608    892  44.5%
```
6 files at 100%: `graph.py`, `indian_companies.py`, `sample_data.py`,
`schemas.py`, `state.py`, `scoring.py`.

| Module | Before | After | Δ |
|---|---|---|---|
| `agents/scoring.py` | 0% | **100%** | new — every metric branch |
| `agents/llm.py` | 46.2% | **77.9%** | the full JSON-repair ladder |
| `agents/retrieval.py` | 0% | **62.2%** | `chunk_text`, `_minmax`, the BM25-only branch |
| `agents/auth.py` | not measured | **50.4%** | first hermetic test of this module, ever |
| `agents/nodes.py` | 0% | 31.5% | pure helpers only — the LLM-calling nodes themselves stay untested until `06 AD-7` port injection lands (Phase 3) |
| `agents/ingest.py` | 0% | 27.8% | pure helpers + the security fix's regression test |
| `server.py` | not measured | **28.4%** | first hermetic test of this module, ever |

**Honest caveat on `graph.py`'s 100%**: this is a side effect of `import
server` executing `build_graph(db)` at module scope, not a demonstration that
the graph's topology or routing logic is verified. Real graph-behavior tests
(state merge, conditional routing, event envelope — `07 §8`) are explicitly
Phase 3/4 work, once nodes take port injection and can run against fakes
instead of a real `db` handle.

### 4.3 Remaining gaps (by design, not oversight)

| Gap | Why it's not Phase 0's job |
|---|---|
| `server.py`'s route handlers themselves (the 71.6% still uncovered) | Need a live Mongo + auth flow; that's the existing `live`-marked suite's job, not the hermetic one |
| LLM-calling nodes (`extractor`, `tone`, `synthesizer`, `fact_checker`, `retriever`'s DB path) | Need port injection (`06 AD-7`) to fake cleanly — Phase 3 |
| Response-shape contract | Needs `response_model=` DTOs (`06 AD-11`) — Phase 6 |
| Graph topology / event envelope / retry-loop behavior | `07 §8` — needs the port-injected nodes from Phase 3 first |

### 4.4 High-risk areas (untested code most likely to fail silently)

Ranked by (blast radius × distance from any test, before vs. after this phase):

| Area | Before | After |
|---|---|---|
| `chat_json` repair ladder | **zero tests**, highest complexity in the backend | 11 tests, every branch |
| `_bse_pdf_url` allowlist | zero tests, **and was actually broken** | 4 tests, bug fixed |
| `compute_scorecard` | zero tests, every quality claim rests on it | 9 tests, 100% coverage |
| Retrieval fusion / BM25-only path | zero tests, documented-but-unverified degradation | 6 tests, both paths covered |
| **Route/request contract vs. frontend** | zero automated checks, ever | 4 tests, running against the live app object |
| Graph node bodies (LLM calls) | zero tests | **still zero** — correctly deferred to Phase 3, not silently skipped |
| Response-shape contract | zero tests, zero *schema* to test against | **still zero** — correctly deferred to Phase 6, not silently skipped |

---

## 5. Milestone Recommendation

> ## ✅ **Proceed to Phase 1**

### Justification

1. **Every Phase 0 exit criterion in `06 §7.1` is met**: hermetic suite runs
   with no server/network/API key (81/81 green); an OpenAPI-equivalent
   contract check exists and passes (`app.openapi()`-based, stronger than a
   static snapshot); a coverage baseline is published (44.5% hermetic,
   §4.2); CI runs the hermetic job.
2. **The frozen architecture held up under actual code contact.** Every
   empirical check — route count, request-schema shapes, SSE framing,
   dependency direction — matched what Documents 01–11 already claimed. No
   drift, no surprise, and **no new ADR is required** (§6).
3. **The one real bug found (§1.3) is fixed, isolated, and tested** — it does
   not touch the phase boundary the way a contract or architecture change
   would.
4. **The one real process hazard found (§1.5) is fixed at both the test and
   the CI layer**, and its durable fix is already scheduled as Phase 1's
   first deliverable (`06 AD-1`) — Phase 0 didn't just find it, it confirmed
   exactly why Phase 1 is designed the way it is.
5. **No condition needs to be attached.** The "minor issues" in §2.3 are
   either already-tracked Phase 1/3/6 work or fully mitigated for now.

### What Phase 1 inherits, concretely

- A green hermetic CI gate that will catch a route/request-contract
  regression the moment one is introduced.
- A coverage floor (44.5%) that should only go up.
- A dependency-rule test that already knows what "clean" looks like for the
  LangGraph layer, ready to be widened into the full AD-5 matrix the moment
  `domain/`/`application/`/`infrastructure/` exist.
- One less real vulnerability than it would have otherwise.

---

## 6. Engineering Questions & New ADRs

**None raised. None required.**

Two decisions were made *within* this phase and are recorded here for
traceability rather than escalated, because both are implementation of
already-ratified intent, not new design:

| Decision | Ratified basis | Why no EQ/ADR |
|---|---|---|
| Fix `_bse_pdf_url`'s hostname bypass now (§1.3) | `10` T-19 — the control was already *intended* to allowlist `bseindia.com`; only the implementation was wrong | Bug fix, zero external surface |
| Fix `test_ssrf_guard.py`'s environment sensitivity now (§1.5) | `06 AD-1`/ADR-003 already explains *why* import-time env mutation is a problem and *how* Phase 1 removes it structurally | Test-only fix confirming an already-ratified diagnosis, not a new one |

If either judgment call is disagreed with, both are single, isolated,
easily-reverted diffs (§0) — nothing downstream depends on them.

---

## 7. Technical Debt Discovered (net-new to the register)

Everything else found during this phase was **already** in the frozen debt
register (`01` D-1…D-11, `05` T-1…T-14) — Phase 0 didn't discover new debt so
much as *confirm* the existing register's accuracy against real code. The two
genuinely new items:

| ID (proposed) | Finding | Severity | Where it's tracked now |
|---|---|---|---|
| **T-19 (amended)** | `_bse_pdf_url`'s allowlist was not just untested but actually bypassable | was Medium (untested) → now fixed, `10 §2` should be marked ✅ verified on next doc revision | Fixed in this phase (§1.3) |
| **New — "import-time env leak"** | `import server`'s `load_dotenv()` mutates process-wide `os.environ` in a way that can silently alter another test's behavior in the same worker | Medium | Confirmed as exactly the failure mode `06 AD-1`/ADR-003 already targets; no new tracking needed beyond this report |

---

## 8. Recommended Implementation Order (unchanged)

This phase found nothing that should reorder `06 §7`'s authoritative sequence.
Restated for convenience, not as a new decision:

```
Ph0 (this report) ──► Ph1 App factory ──► Ph2 Domain ──► Ph3 Ports + Mongo
                                                              │
                                             ┌────────────────┴───────┐
                                             ▼                        │
                                       Ph4 Jobs + EventBus             │
                                             │                        │
                              ┌──────────────┴──────────┐             │
                              ▼                         ▼             ▼
                        PhL Learning            Ph5 LLM adapter  (independent)
                              │                         │
                              │                         ▼
                              │                  Ph6 Router split
                              └──────────────┬──────────┘
                                             ▼
                                Ph7 Redis + OTel/Prom + Docker + CI
```

**One concrete addition for Phase 1's task list**, surfaced by this phase's
findings: when `06 AD-1`'s `create_app()` factory removes import-time
`os.environ` reads, also confirm it removes the `load_dotenv()` side effect
that caused §1.5 — that is the structural fix this report's workaround is
standing in for.

---

*Companion documents:* [`06`](06_Clean_Architecture_Migration_Plan.md)–[`11`](11_ADR_Index.md)
· [`12_M2_Implementation_Charter.md`](12_M2_Implementation_Charter.md) · index:
[`00_README.md`](00_README.md)
