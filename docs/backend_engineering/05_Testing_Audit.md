# Testing Audit

**Status:** Audit · **Milestone:** Backend Engineering M1 · **Date:** 2026-08-03
**Scope:** `backend/tests/` (15 files, 1,404 LOC, ~93 tests) + `backend/eval_scorecard.py` @ `7404b67`.
No test was modified. `pytest.ini`'s `addopts` was not touched, per `CLAUDE.md`.

---

## 1. Summary

| Layer | State | Verdict |
|---|---|---|
| Unit | 4 files, ~18 tests, all in `llm.py`/`auth`-adjacent territory | ❌ **Inverted** — the most intricate pure logic in the backend has zero direct tests |
| Integration / E2E | 11 files, ~75 tests, all live HTTP against a running server | ✅ **Broad and genuinely good** — but non-hermetic and unrunnable in CI |
| API contract | none | ❌ **Absent** — nothing verifies backend responses against the frontend Zod schemas |
| Streaming | 1 test | ⚠️ **Token coverage** — the one known SSE defect (D-1) is untested and untestable by it |
| Coverage measurement | none | ❌ `pytest-cov` is not installed; coverage is **unknown**, not merely low |
| CI | none | ❌ No `.github/`, no pipeline, no automated gate of any kind |

The headline finding is a **coverage inversion**: 93 tests exercise CRUD and
auth flows over HTTP, while the four highest-complexity pure functions in the
codebase — LLM JSON repair, the citation/claim regexes, the retrieval fusion
math, and the chunker — have no direct test at all.

---

## 2. Inventory

### 2.1 Files

| File | LOC | Kind | Requires |
|---|---|---|---|
| `conftest.py` | 33 | shared `login()` helper | running server |
| `backend_test.py` | 148 | E2E: health, ingest, generate, SSE, report fetch | server + Mongo + **live LLM** |
| `backend_test_iter2.py` | 175 | E2E: samples, filings, tickers, trending, rescore, compare | server + Mongo + LLM |
| `backend_test_iter3.py` | 139 | E2E: company search, `ensure` | server + **live SEC/EDGAR/yfinance network** |
| `backend_test_iter4.py` | 85 | E2E: follow-up context, company name | server + LLM |
| `backend_test_iter5.py` | 104 | E2E: audio ingest validation paths | server |
| `backend_test_iter6.py` | 133 | E2E: delete, jobs collection, scoping | server + Mongo |
| `test_auth.py` | 79 | E2E: register/login/logout/me | server + Mongo |
| `test_account.py` | 152 | E2E: password change, logout-all, delete account | server + Mongo |
| `test_password_reset.py` | 142 | E2E: OTP flow, rate limiting, single-use | server + Mongo |
| `test_reports_scoping.py` | 156 | E2E: cross-tenant read/delete/list scoping | server + Mongo |
| `test_ssrf_guard.py` | 46 | **unit** — `assert_public_url` | none |
| `test_gemini_key_isolation.py` | 62 | **unit** — contextvar key isolation | none |
| `test_llm_retry.py` | 58 | **unit** — retry vs `NonRetryableLLMError` | none |
| `test_llm_validate.py` | 91 | **unit** — `validate_key` dispatch + redaction | none |

### 2.2 Execution model

`pytest.ini`: `-n 2 --dist loadscope`, `required_plugins = pytest-xdist`. Two
fixed workers, module/class-pinned so the shared live backend is not raced
across workers. Correct for the design; **not modified.**

`conftest.login()` registers a fresh UUID-suffixed user per module and manually
re-stores the session cookie as non-Secure, because `requests` will not resend
a `Secure` cookie over plain `http://`. A clean, well-documented harness
workaround.

---

## 3. Unit Coverage

### 3.1 What is covered

| Test | Target | Quality |
|---|---|---|
| `test_ssrf_guard.py` | `llm.assert_public_url` — loopback, private, link-local, metadata IP | ✅ Good; covers the exact threat |
| `test_gemini_key_isolation.py` | `set_llm_context`/`_active` — server key never leaks into a BYOK call | ✅ Good; tests a real security invariant |
| `test_llm_retry.py` | `chat_text` — 4 attempts on transient, 1 on `NonRetryableLLMError` | ✅ Good; monkeypatches `_generate_sync` |
| `test_llm_validate.py` | `validate_key` dispatch, empty key, unknown provider, failure propagation, `redact_key_from_error` | ✅ Good |

All four are hermetic — no network, no Mongo, no server. They are the only
tests in the repository that can run in CI today.

### 3.2 What is not covered — the inversion

Every function below is **pure** (no I/O, deterministic, trivially testable)
and has **zero direct test coverage**:

| Function | LOC | Complexity | Why it matters |
|---|---|---|---|
| `llm.chat_json` JSON-repair ladder (`llm.py:394-423`) | ~30 | **Highest in the codebase** — four fallback branches: bare `json.loads`, regex `{…}`/`[…]` extraction, brace re-wrapping of naked `k: v` pairs, JSON-Schema-envelope unwrapping, plus bare-array-to-single-list-field coercion | Every structured LLM output in the product passes through it. Each branch exists because a real model produced that malformation. **Not one branch is tested.** |
| `llm._schema_hint` (`llm.py:335-354`) | ~20 | Recursive over nested Pydantic models and `list[Model]` | Generates the prompt text that determines whether the model returns valid JSON at all |
| `llm._strip_code_fence` (`llm.py:357-363`) | 7 | regex | Used on **every** brief and every JSON response |
| `llm._retry_after_seconds` (`llm.py:302-307`) | 6 | two provider-specific regexes | Controls backoff; a silent regex failure degrades to fixed backoff invisibly |
| `nodes._extract_candidate_claims` (`nodes.py:198-220`) | ~22 | sentence split + numeric regex + dedupe + cap | **Decides what gets fact-checked.** A regex miss means a fabricated number is never verified — and the `ponytail:` note at :200 already documents a known blind spot that no test pins down |
| `nodes._format_docs` (`nodes.py:21-32`) | 12 | budget-aware truncation | Silently drops sources past `max_chars`; an off-by-one changes which sources the model can cite |
| `scoring.compute_scorecard` (`scoring.py:35-66`) | ~30 | 3 metrics, 2 divide-by-zero guards, citation range filtering | **Every quality claim about this product** rests on it. `eval_scorecard.py --selftest` checks the *aggregation* math over it, never the function itself |
| `retrieval.chunk_text` (`retrieval.py:104-138`) | ~35 | paragraph packing → sentence splitting → overlap stitching | Determines every chunk boundary in the corpus. Retrieval quality is downstream of it |
| `retrieval._minmax` + fusion (`retrieval.py:70-76, 191-218`) | ~30 | normalization edge cases (all-equal → 0.5), two weighting regimes, CE blend | The `dense_norm is None` branch (BM25-only degradation) is a documented production path and is untested |
| `ingest._clean_html` (`ingest.py:15-26`) | 12 | 9 chained regexes | Every EDGAR filing's text quality |
| `ingest._bse_pdf_url` (`ingest.py:194-204`) | 11 | **hostname allowlist — a security check** | Prevents fetching an arbitrary URL from an untrusted third-party feed. Untested |
| `ingest._fmt_num` (`ingest.py:85-94`) | 10 | unit scaling | Every yfinance-sourced figure |
| `auth.hash_password`/`verify_password`/`_hash_otp` (`auth.py:81-108`) | ~28 | scrypt + HMAC | Covered *indirectly* through HTTP flows; no direct test that a wrong password fails or that the OTP pepper is applied |
| `auth._recent_hits` window pruning (`auth.py:52-74`) | ~22 | time-window logic with an unbounded-memory guard | The DoS guard described in the comment at :54-56 has no test |

**14 pure functions, ~275 LOC of the most intricate logic in the backend, zero
direct tests.** Every one is testable with `assert` and a literal — no fixture,
no mock, no server.

### 3.3 Why the inversion happened

Architecture Review **D-4**: `import server` executes `os.environ["MONGO_URL"]`,
constructs a Mongo client, and compiles the LangGraph at import time
(`server.py:42-77`). Nothing in `backend/` can be imported without a full
environment, so the path of least resistance was to test everything over HTTP
against a running instance. The four hermetic unit tests all target
`agents/llm.py` and `agents/auth.py` — the two modules with no import-time side
effects.

The fix is not a testing change; it is the app-factory change in D-4. But
**none of the 14 functions above need it** — they live in `agents/*` modules
that already import cleanly. They are untested by habit, not by obstruction.

---

## 4. Integration Coverage

### 4.1 What is covered — genuinely strong

| Area | Tests | Notes |
|---|---|---|
| Auth lifecycle | ~20 | register, duplicate, login, wrong password, logout, logout-all, session invalidation, `me` without session → 401 |
| Password reset | 6 | end-to-end OTP, wrong OTP, single-use, rate limiting, identical response for known/unknown email (timing-leak defense) |
| Account management | 6 | password change invalidates other sessions, delete-account cascade + scoping |
| Multi-tenant scoping | 5 | other user cannot see / delete my report; samples visible to all; cannot delete a sample |
| Login wall | 8 | `test_anonymous_*` — every tool route rejects an unauthenticated caller |
| Ingest | 6 | text, empty→400, company name persistence, samples, audio validation (bad ext / empty / oversized) |
| Pipeline E2E | 8 | generate → job → SSE → report, hybrid retriever, financials/guidance present, follow-up context, scorecard present |
| Reports CRUD | 10 | list, get, delete + verification, delete-nonexistent → 404, compare (ok / 1-valid / 5-ids → 422), rescore |
| Companies | 9 | search (US, India, empty), ensure (already-ingested, refresh, invalid, 404) |
| Health | 4 | shape, retrieval status before/after pipeline |

Coverage of **externally observable behavior** is broad, and the security
tests (scoping, login wall, timing-equal responses) are better than typical.

### 4.2 Gaps

| ID | Gap | Impact |
|---|---|---|
| **T-1** | **Non-hermetic.** `backend_test_iter3.py` hits **live SEC EDGAR and Yahoo Finance**; pipeline tests make **real, billed LLM calls**. Tests depend on third-party availability, rate limits, and an API key with budget. | The suite cannot run in CI, cannot run offline, and fails for reasons unrelated to the code. |
| **T-2** | **No CI.** No `.github/workflows`, no pipeline configuration anywhere in the repo. Nothing runs these tests automatically. | Every quality gate in `docs/planning/06-Testing-QA-Plan.md` §5 is manual. |
| **T-3** | **No coverage measurement.** `pytest-cov` is absent from `requirements.txt`; no `.coveragerc`, no coverage config in `pytest.ini`. | Coverage is *unknown*. The §3.2 gap list was produced by reading code, and nothing prevents it from silently regrowing. |
| **T-4** | **Failure paths largely untested.** No test asserts the LLM-error redaction actually holds end-to-end (a provider error containing a key must not reach the response body) — the unit test covers `redact_key_from_error` in isolation, not the `/reports/generate` path at `server.py:779-795`. No test covers `MAX_ACTIVE_JOBS` → 429 despite the Testing Plan listing it. No test covers the truncation guard producing a user-visible 422. |
| **T-5** | **`POST /reports/rescore` is tested for success only** (`test_rescore_reports`) — nothing asserts it should *not* be callable by a non-admin, which is precisely the defect in [`01`](01_Backend_Architecture_Review.md) D-2 / [`02`](02_API_Coverage_Audit.md) §4.5. The test currently **locks in** the unscoped behavior. |
| **T-6** | **No test for restart recovery.** An in-flight job after a process restart is permanently stuck at `running` (D-6); nothing covers it. |
| **T-7** | **`/ingest/pdf` has no test.** Audio has five; PDF — including the scanned-PDF → 422 path called out in the Testing Plan §3 — has none. |

---

## 5. API Contract Tests

**None exist.** This is the highest-value, lowest-cost gap in the audit.

The real contract is the pair (backend response shape ↔
`web/features/*/integration/schemas.ts` Zod schema). Nothing verifies it:

- No test asserts a backend response validates against a frontend schema.
- No OpenAPI snapshot test — FastAPI serves `/openapi.json` for free and
  nothing consumes it.
- No shared schema artifact between the two halves; the Zod schemas are
  hand-transcribed from Pydantic models, with the transcription accuracy
  documented only in comments (`company-research/integration/schemas.ts:3-10`).

### 5.1 What this misses today

API Coverage Audit **F-7**: `GET /reports` projects out `source_documents`
(`server.py:1050`) while `reportDocSchema` marks it **required**. Safe only
because list responses use a different schema — but the two definitions of "a
report" have already diverged with nothing watching.

### 5.2 What it will miss tomorrow

The Learning build's most likely failure is **F-1**: returning `{job_id}`
instead of `{id}` by copying the report handler. That is a one-word bug that
fails silently server-side (the response is a valid 200) and surfaces to the
user as a generic validation error. A contract test catches it in seconds; no
existing test catches it at all.

### 5.3 Recommendation

Two tests, both hermetic:

1. **OpenAPI snapshot** (~10 LOC): assert `app.openapi()` matches a committed
   JSON fixture. Any accidental path, method, or response-model change fails
   loudly, with the diff as the review artifact.
2. **Response-shape assertions per endpoint family** (~60 LOC): for each of the
   4 Learning routes and the report lifecycle, assert the response body has
   exactly the key set the Zod schema requires. Plain `assert set(body) >= {…}`
   — no cross-language tooling, no codegen, no new dependency.

---

## 6. Streaming Tests

**One test: `test_sse_stream` (`backend_test.py:89-120`).**

What it does: opens `GET /reports/{job_id}/stream`, iterates lines with a 180s
budget, collects `node` values from `data:` payloads, breaks on `event: end`,
and asserts a `final` event was seen.

### 6.1 What it verifies

✅ The stream returns 200 · ✅ events are line-framed and JSON-parseable ·
✅ a `final` event arrives · ✅ `event: end` terminates.

### 6.2 What is untested

| ID | Untested behavior | Severity |
|---|---|---|
| **T-8** | **Concurrent consumers.** The known single-queue defect (D-1) — two readers on one job split the event stream — is invisible to a single-connection test. This is the defect the Learning stream would inherit. **Nothing in the suite would catch it.** | **High** |
| **T-9** | **Replay-on-reconnect.** The `to_skip` dedupe logic (`server.py:989-996`) is subtle, comment-heavy, and exercised by no test. Connecting mid-job and asserting no duplicate events is the obvious missing case. | High |
| **T-10** | Keepalive emission after 120s idle | Low (slow to test) |
| **T-11** | Streaming a job that has already finished (queue drained, sentinel consumed) | Medium — relevant to the Learning cache question EQ-5 |
| **T-12** | Streaming an unknown job id → 404; streaming another user's job | Medium — the scoping suite covers `GET /reports/{id}` but `test_anonymous_stream_rejected` only covers the unauthenticated case |
| **T-13** | Cancel-mid-stream: `pipeline/warn` event emitted, stream terminates cleanly | Medium — cancel is tested as an endpoint, never through the stream |
| **T-14** | Event **ordering** and the `pipeline/start` → … → `pipeline/ok` envelope | Medium — the frontend's `deriveStage` depends entirely on this envelope |

T-8 and T-9 are both testable hermetically against a *fake* job (push events
into the registry directly), needing no LLM and no network — once D-4's import
problem is addressed, or immediately if the shared `agents/jobs.py` proposed in
the Learning Design §6.1 is written as an importable module.

---

## 7. The Quality Harness (`eval_scorecard.py`)

Not a test suite, and correctly not treated as one: it drives the live HTTP API
across many `(ticker, query)` pairs and aggregates scorecards into defensible
average faithfulness / context-precision / answer-relevance figures. `--selftest`
verifies the **aggregation** math without calling the API.

Gap: `--selftest` validates the harness's own arithmetic, not
`scoring.compute_scorecard` (§3.2). The function whose output the harness
averages is itself unverified.

---

## 8. Prioritized Recommendations

| # | Action | Fixes | Cost |
|---|---|---|---|
| 1 | Unit-test `chat_json`'s four JSON-repair branches with literal malformed strings | §3.2 (highest-complexity untested code) | ~40 LOC, hermetic |
| 2 | Unit-test `compute_scorecard`, `_extract_candidate_claims`, `chunk_text`, `_minmax`/fusion incl. the BM25-only branch | §3.2 | ~80 LOC, hermetic |
| 3 | OpenAPI snapshot test + response-key assertions for the Learning routes | §5 — catches the `id`/`job_id` class of bug (F-1) | ~70 LOC |
| 4 | Concurrent-consumer + reconnect-replay streaming tests | T-8, T-9 — the defect Learning would inherit | ~50 LOC, needs `agents/jobs.py` importable |
| 5 | Add `pytest-cov`; publish a baseline number | T-3 | 1 dep, 2 LOC config |
| 6 | Mark network-dependent tests (`@pytest.mark.live`) so a hermetic subset can run without SEC/yfinance/LLM | T-1 | ~10 LOC of markers |
| 7 | Minimal CI running only the hermetic subset | T-2 | one workflow file |
| 8 | Test that a non-admin cannot call `/reports/rescore` — **after** EQ-2 is decided | T-5, D-2 | ~8 LOC |
| 9 | Unit-test `_bse_pdf_url`'s hostname allowlist (a security control) | §3.2 | ~10 LOC |

Items 1, 2, 3 and 9 total ~200 lines, require **no running server, no network,
no API key, and no new dependency**, and cover the code most likely to fail
silently. Item 5 adds `pytest-cov` — the one dependency this audit recommends
adding, because coverage cannot otherwise be measured at all.

`pytest.ini`'s `addopts` needs no change for any of the above.

---

## 9. Alignment with the Approved Testing Plan

`docs/planning/06-Testing-QA-Plan.md` (2026-07-12) is largely accurate but
carries three stale/unmet items:

| Plan claim | Reality |
|---|---|
| §1 "Unit: retrieval fusion, PDF extraction, claim regex, scorecard math…" | **None of these four have unit tests.** The listed scope is aspirational, not descriptive. |
| §1 "Frontend — [FILL: RTL / Playwright?]" | Resolved since: `web/` has 286 vitest tests across 62 files plus a Playwright config. The plan is stale. |
| §4 three of five performance benchmarks | **Not computable** — the timing data is not persisted. See Observability Audit §3.2. |
| §5 quality gates | All manual; no CI enforces any of them (T-2). |

Updating that document is out of scope here (docs are human-owned per
`.hermes.md`); the divergences are recorded for whoever owns it.

---

*Cross-references: `01_Backend_Architecture_Review.md` (D-1, D-2, D-4, D-6),
`02_API_Coverage_Audit.md` (F-1, F-6, F-7), `03_Learning_Backend_Design.md` §6.1
and §9, `04_Observability_Audit.md` §3.2.*
