# Backend Architecture Review

**Status:** Audit · **Milestone:** Backend Engineering M1 · **Date:** 2026-08-03
**Scope:** `backend/` as it exists on `main` @ `7404b67`. No code was modified.

---

## 1. Current Architecture

### 1.1 Physical shape

```
backend/
  server.py            1208 LOC   FastAPI app: 31 routes, job registry, pipeline runner,
                                  Pydantic request models, CORS, startup/shutdown
  eval_scorecard.py     265 LOC   offline quality harness (drives the live HTTP API)
  agents/
    llm.py              427 LOC   provider routing, retry, JSON repair, SSRF guard
    ingest.py           331 LOC   EDGAR / BSE / yfinance / PDF fetch + chunk + store
    nodes.py            310 LOC   5 LangGraph nodes + conditional router
    auth.py             239 LOC   scrypt hashing, sessions, OTP, rate limiting
    retrieval.py        220 LOC   BM25 + dense + cross-encoder, chunker
    indian_companies.py 167 LOC   static data (159 tickers)
    sample_data.py      136 LOC   static data
    company_index.py    130 LOC   SEC ticker universe, lazy-loaded
    scoring.py           66 LOC   RAGAS-lite scorecard (pure, dependency-free)
    notify.py            46 LOC   Resend OTP email over httpx
    graph.py             44 LOC   graph wiring
    state.py             58 LOC   AgentState TypedDicts
    schemas.py           34 LOC   LLM output Pydantic schemas
```

~2,100 LOC of domain code behind a 1,208-LOC transport module. There is no
package boundary between them beyond `import agents.*`.

### 1.2 Runtime topology

```
Next.js (web/, :3001) ──REST + SSE (cookie creds)──► FastAPI (:8001, single process)
                                                        │
                                     ┌──────────────────┼─────────────────────┐
                                     ▼                  ▼                     ▼
                            MongoDB (:27017)     LangGraph pipeline    external HTTP
                            users, sessions,     (in-process, per-job  SEC EDGAR, BSE,
                            password_resets,      asyncio.Task)        yfinance, Resend,
                            filings, chunks,             │             LLM providers
                            companies, jobs,             ▼
                            reports                fastembed ONNX models
                                                   (in-process, lazy singletons)
```

Everything is one process. Job state, SSE fan-out, embedding models, the
rate-limit counter, and the compiled graph all live in module-level Python
globals. This is a deliberate single-instance design (documented in
`docs/planning/03-Technical-Architecture.md` §7), not an accident — but it is
the constraint that shapes every finding below.

### 1.3 Request lifecycles

**Synchronous** (28 of 31 routes): `route → current_user dependency → agents
function → motor → response`. Median depth 2 calls. Nothing surprising.

**Asynchronous** (report generation, 3 routes): `POST /reports/generate` →
validate → cache probe → concurrency cap → insert `jobs` doc → create
`asyncio.Task(_run_pipeline)` → return `{job_id}`. The task streams
`graph.astream()` events into a per-job `asyncio.Queue` *and* appends them to
`JOBS[id]["events"]` *and* `$push`es each to Mongo. `GET
/reports/{id}/stream` replays `job["events"]`, then drains the queue,
skipping the first N to avoid duplicates (`server.py:978-1006`).

---

## 2. Layer Boundaries

There are effectively **two** layers, not four:

| Nominal layer | Where it actually lives | Verdict |
|---|---|---|
| Transport / API | `server.py` | present |
| Application / use case | `server.py` (`_run_pipeline`, `generate_report`) | **fused into transport** |
| Domain | `agents/nodes.py`, `graph.py`, `state.py`, `scoring.py` | present, thin |
| Infrastructure / persistence | `agents/ingest.py`, `agents/retrieval.py`, `agents/auth.py`, inline `db.*` calls in `server.py` | **fused into domain** |

### 2.1 Concrete boundary crossings

| # | Crossing | Evidence | Impact |
|---|---|---|---|
| B-1 | Domain queries the database directly | `agents/retrieval.py:160` — `retrieve()` issues `db.filing_chunks.find(...).sort(...)` and owns the 2000-doc cap | Retrieval algorithm cannot be tested or reused without Mongo. There is no repository seam. |
| B-2 | Motor handle injected into graph nodes | `graph.py:19` `partial(retriever_node, db=db)`; `nodes.py:39` `retriever_node(state, *, db)` | The domain's dependency is a concrete driver object, not an interface. Duck-typing makes it *stubbable*, but nothing declares the contract. |
| B-3 | Business logic in the transport module | `server.py:730-750` assembles the report document, calls `compute_scorecard`, joins `companies` for the display name, and inserts | The definition of "a report" lives in an HTTP handler. Learning will need the same assembly and has nowhere to share it from. |
| B-4 | Persistence vocabulary in the API layer | 24 direct `db.<collection>.<op>` calls in `server.py` | Collection names and query shapes are spread across the route table. Changing report scoping means auditing 8 handlers. |
| B-5 | Cross-layer lock sharing | `agents/llm.py:150` defines `GEMINI_LOCK`; `server.py:426` imports it into the audio-transcription route | Temporal coupling between a route handler and a provider adapter's internal concurrency control. Correct today, invisible to a future editor of either side. |
| B-6 | Import-time environment + I/O | `server.py:42` `os.environ["MONGO_URL"]`, `:44` client construction, `:77` `build_graph(db)`, `:84` `_active()` logged | `import server` requires a full environment and a Mongo URL. This is *why* the test suite is live-HTTP-only (§5 of the Testing Audit). |

### 2.2 What the boundaries get right

- **No circular imports.** `agents/*` never imports `server`. The dependency
  graph is a DAG.
- **`agents/` modules take `db` explicitly** rather than reaching for a global
  — stated as a convention in `auth.py:6-7` and honored consistently.
- **All LLM access funnels through `llm.py`.** No node imports a provider SDK.
  The one exception (`server.py:425` importing `google.generativeai` for audio)
  is documented and correctly shares `GEMINI_LOCK`.
- **`scoring.py` is genuinely pure** — no I/O, no deps, testable as-is.

---

## 3. Clean Architecture Compliance

Scored against the dependency rule (inner layers must not know about outer
ones) and the entity/use-case/adapter separation.

| Principle | Compliance | Detail |
|---|---|---|
| Dependency rule (inward-pointing) | ⚠️ **Partial** | Domain → infrastructure edges at B-1, B-2. `nodes.py` imports `.retrieval` (which owns Mongo) at line 40. |
| Entities independent of frameworks | ✅ **Pass** | `state.py` is plain `TypedDict`; `schemas.py` is Pydantic-only (a serialization concern, acceptable); `scoring.py` is stdlib. |
| Use cases independent of UI | ⚠️ **Partial** | The report use case *is* `_run_pipeline`, a private coroutine in the FastAPI module, coupled to `JOBS`/`JOB_QUEUES` globals. |
| Interface adapters isolate I/O | ❌ **Fail** | No adapter layer. Mongo access is direct from both transport and domain. |
| Frameworks at the edge | ✅ **Pass** | FastAPI appears only in `server.py`; LangGraph only in `graph.py`/`nodes.py`. |
| Testable without externals | ❌ **Fail** | `import server` needs env + Mongo; `retrieve()` needs Mongo; nodes need a live LLM unless module attributes are monkeypatched. |

**Net:** the codebase is a well-factored **two-tier layered application**, not a
Clean Architecture one. That is a legitimate choice at this size — the
recommendation below is *not* "introduce ports and adapters everywhere", it is
targeted at the two seams that Learning will otherwise duplicate (B-1, B-3).

---

## 4. SOLID Violations

### S — Single Responsibility

**V-1 · `_run_pipeline` (`server.py:678-799`) — High.** One 120-line coroutine
owns seven responsibilities: LLM context binding, job status transitions, event
fan-out to three sinks (memory list, queue, Mongo), graph streaming, report
document assembly, scorecard computation, and error classification/redaction.
Any Learning equivalent will copy 60% of it.

**V-2 · `server.py` as a module — High.** Route table, request models, cookie
policy, in-memory job registry + reaper, pipeline runner, exception handler,
CORS, warmup, and shutdown. 1,208 lines with no internal module boundary.

**V-3 · `ensure_company` (`server.py:569-656`) — Medium.** Encodes the entire
source-selection policy (US → EDGAR 10-Q → 10-K → yfinance; India → BSE →
yfinance) inline in a route handler, interleaved with ingest calls and error
translation. This is domain policy sitting in transport.

### O — Open/Closed

**V-4 · Provider dispatch is a closed if/elif chain — High.**
`llm.py:244-252` (`_generate_sync`) and `llm.py:273-280` (`validate_key._run`)
contain **two independent copies of the same provider→function dispatch**.
Adding a provider requires edits in four places (`PROVIDER_DEFAULTS`,
`PROVIDER_BASE_URL`, and both dispatch chains). The duplication is a live
drift hazard: `validate_key` resolves `base_url` differently
(`base_url or PROVIDER_BASE_URL.get(provider)`, line 270) than `_active()`
does (which also consults `LLM_BASE_URL` env, line 100). A `custom` provider
validated successfully can therefore be dispatched against a different URL at
generation time.

**V-5 · Retrieval fusion weights are hard-coded — Low.** `retrieval.py:199-204`
embeds 0.55/0.40/0.05 and the 0.7/0.3 rerank blend as literals in the loop, with
a duplicated branch for the BM25-only case. Tuning means editing the algorithm.

### L — Liskov

No inheritance hierarchies exist in `backend/`. **Not applicable — no violations.**

### I — Interface Segregation

**V-6 · Whole-database handle passed everywhere — Medium.** `retriever_node`
needs exactly one collection (`filing_chunks`); it receives the entire
database. Same for `ingest_document` (three collections) and every `auth.*`
function. Nothing communicates which collections a function touches short of
reading it.

### D — Dependency Inversion

**V-7 · Nodes bind to concrete module functions — Medium.** `nodes.py:8`
imports `chat_json`/`chat_text` directly. There is no injection point, so the
only way to test a node is `monkeypatch.setattr` on the module attribute —
which is exactly what `test_llm_retry.py` does. Works, but couples every test
to the import layout.

**V-8 · Global mutable singletons — Medium.** `JOBS`/`JOB_QUEUES`
(`server.py:52-53`), `_EMBEDDER`/`_RERANKER` (`retrieval.py:18-19`), `_hits`
(`auth.py:49`), `graph` (`server.py:77`). All process-scoped, none injectable,
all correctly flagged in-code as single-instance-only.

---

## 5. Coupling Analysis

### 5.1 Module dependency graph

```
server.py ──► agents.auth, agents.notify, agents.graph, agents.ingest,
              agents.sample_data, agents.scoring, agents.retrieval,
              agents.company_index, agents.llm          (fan-out: 9)

agents.graph ──► agents.state, agents.nodes
agents.nodes ──► agents.state, agents.schemas, agents.llm, agents.retrieval
agents.ingest ──► agents.retrieval
agents.company_index ──► agents.indian_companies
agents.auth ──► (stdlib + pymongo only)
agents.scoring ──► (stdlib only)
agents.llm ──► (stdlib + pydantic; SDKs imported lazily inside functions)
```

No cycles. Depth ≤ 3. This is healthy.

### 5.2 Fan-in / instability

| Module | Fan-in | Fan-out | Instability (Ce/(Ca+Ce)) | Note |
|---|---|---|---|---|
| `agents/llm.py` | 4 (nodes, server, 3 tests) | 0 | 0.00 | Maximally stable, correctly so. But V-4's internal duplication means the stable module has two divergent code paths. |
| `agents/retrieval.py` | 3 (nodes, ingest, server) | 0 | 0.00 | Stable — yet it owns a Mongo query (B-1). A stable module with a hidden infrastructure dependency is the worst place for one. |
| `agents/state.py` | 2 | 0 | 0.00 | Fine. |
| `agents/scoring.py` | 2 (server, eval harness) | 0 | 0.00 | Clean. |
| `server.py` | 0 | 9 | 1.00 | Maximally unstable, correctly so (it is the composition root) — but it also holds use-case logic (V-1), which should not live in the most volatile module. |

### 5.3 Non-import coupling (the coupling that actually hurts)

| ID | Kind | Where | Why it matters |
|---|---|---|---|
| C-1 | **Content coupling** — shared mutable dict | `JOBS[id]["events"]` is appended by `_run_pipeline.push` (`server.py:699`) and iterated by the SSE generator (`server.py:985`), with correctness resting on the queue being unconsumed at first read | See D-1 below: two concurrent SSE readers on one job silently split the event stream. |
| C-2 | **Common coupling** — shared global lock | `GEMINI_LOCK` (B-5) | Audio route and LLM adapter must stay in sync forever. |
| C-3 | **Temporal coupling** | `record_hit` must precede the DB await in `/auth/login` (`server.py:226`) and `/auth/reset-password` (`server.py:263`) or the rate limiter races | Correct today and well-commented, but enforced only by comment. |
| C-4 | **Stamp coupling** | `db` handle (V-6) | — |
| C-5 | **Data-format coupling, undeclared** | `[n]` citation markers produced in `nodes.py:164`, consumed by `scoring.py:_CITATION_RE` and by `web/lib/markdown/citations.ts` | A three-way contract across two languages with no shared definition and no test. |
| C-6 | **Contract coupling, unverified** | Backend response shapes ↔ `web/features/*/integration/schemas.ts` Zod schemas | Nothing verifies them against each other. See the API Coverage Audit. |

---

## 6. Technical Debt Register

Ordered by (severity × likelihood of being hit during the Learning build).

| ID | Severity | Item | Evidence | Cost to fix now |
|---|---|---|---|---|
| **D-1** | **High** | **Single-consumer SSE queue.** `JOB_QUEUES[id]` is one `asyncio.Queue`. Two concurrent `GET /reports/{id}/stream` connections (two browser tabs, or a reconnect before the first socket is reaped) each `await q.get()`, so events are distributed *between* them — each client sees a partial stream, and the `to_skip` replay logic (`server.py:989-996`) silently mis-skips. | `server.py:975-1006` | ~30 LOC: replace the single queue with a per-connection subscriber list. **Learning will inherit this defect verbatim if the pattern is copied.** |
| **D-2** | **High** | **`POST /reports/rescore` has no scoping and no authorization.** Any authenticated user triggers a full-collection read + write over *every* report in the database, including other tenants'. | `server.py:1116-1128` (`db.reports.find({})`) | ~2 LOC (admin gate via existing `auth.is_admin`), or delete the endpoint — it has no frontend consumer. |
| **D-3** | High | **Duplicated provider dispatch with divergent `base_url` resolution** (V-4). A validated custom key can be dispatched to a different endpoint than the one validated. | `llm.py:244-252` vs `llm.py:270-280` | ~15 LOC: one dispatch table, one resolver. |
| **D-4** | Medium | **No unit-testable seam.** Import-time env + Mongo (B-6) forces every test to be a live-HTTP test against a running server + live LLM + live network. | `server.py:42-77`; `backend/tests/conftest.py` | Moderate: move app construction into a factory. Not required for Learning, but it is why coverage is unmeasurable. |
| **D-5** | Medium | **Report reads are unscoped (IDOR-by-obscurity).** `GET /reports/{id}` and `POST /reports/compare` return any report to any authenticated caller who knows the UUID. This is *acknowledged in-code* as an accepted risk (`server.py:1059-1064`), not an oversight. | `server.py:1019-1037`, `:1135-1147` | ~4 LOC per endpoint. Decision needed (see Engineering Question EQ-3). |
| **D-6** | Medium | **Job registry is process-local.** `JOBS`/`JOB_QUEUES` do not survive a restart; the Mongo mirror preserves *events* but not the queue, so an in-flight job after a restart is permanently stuck at `running` with no producer. `GET /reports/{id}` returns the stale `running` status forever. | `server.py:52-53`, `:1027-1031` | Needs a startup sweep marking orphaned `running` jobs as `failed`. ~10 LOC. |
| **D-7** | Medium | **`/health` does two unindexed full-collection counts** on every call. A liveness probe on a 10s interval is a self-inflicted, growing load. It also reports `llm_key_configured` for Gemini env keys only, ignoring the other six providers. | `server.py:187-198` | ~5 LOC. |
| **D-8** | Low | **No `completed_at` / duration recorded on jobs.** The Testing & QA Plan §4 asks for "median report time" as a release gate; the data to compute it is not persisted. | `server.py:751-757` | ~3 LOC. |
| **D-9** | Low | **Chunk re-ingest never dedupes** — stale chunks coexist with fresh ones for the same ticker. | `retrieval.py:158-159` (marked `ponytail:`) | Deliberate, documented, with a stated upgrade path. Leave. |
| **D-10** | Low | **Numeric-only fact-checking.** A purely qualitative fabrication extracts zero claims and is trivially accepted at faithfulness 1.0. | `nodes.py:200-205` (marked `ponytail:`) | Deliberate, documented. Relevant to Learning: see the Learning Design §4. |
| **D-11** | Low | **`docs/planning/03-Technical-Architecture.md` §7 and `05-API-Documentation.md` are stale** — both state "No auth/authorization yet — all endpoints open" and `CORS_ORIGINS="*"`. Both are false since Phase 4; auth is a full login wall and CORS defaults to `http://localhost:3001`. The API doc's SSE event shape (`event: pipeline`, `{"stage":...}`) does not match the implementation (`data:` only, `{"node":...}`). | `docs/planning/03-…md:57-63`, `05-…md:3,63-70` | Doc-only. Flagged, not fixed (docs are human-owned per `.hermes.md`). |

### 6.1 Debt the audit deliberately does **not** flag

`ponytail:`-marked shortcuts (`ingest.py:216-218`, `retrieval.py:158`,
`llm.py:110-113`, `llm.py:169-170`, `auth.py:45-46`, `notify.py:22-29`,
`nodes.py:200-205`) are recorded deliberate simplifications with stated
ceilings and upgrade paths. They are correctly marked and should be preserved,
not "fixed". They are listed here only where a Learning decision depends on
them (D-9, D-10).

---

## 7. Engineering Questions Raised

| ID | Question | Conflict |
|---|---|---|
| **EQ-1** | See Learning Design §7 — Redis. | The Milestone brief specifies a "Redis job lifecycle"; Redis is absent from `requirements.txt`, from every governance document, and from the codebase. `CLAUDE.md` requires confirming nothing already installed does the job before adding a dependency, and the existing job lifecycle already runs on Mongo. **Blocking a dependency decision, not the design** — both variants are specified in the Learning Design. |
| **EQ-2** | Should `POST /reports/rescore` (D-2) be admin-gated or deleted? It has no frontend consumer and currently lets any user rewrite every tenant's scorecards. | Not covered by any approved contract. Recommend deletion; needs a call. |
| **EQ-3** | Should report reads (D-5) stay unscoped? The in-code comment records it as an accepted risk from before the login wall. Learning must either inherit the same posture or diverge from it. | `docs/planning/09-Auth-and-Accounts-Plan.md` does not rule on read scoping. Recommend scoping Learning to the owner and revisiting reports separately. |

---

## 8. Recommendations (targeted, not a rewrite)

Ranked by leverage against the Learning build specifically. Nothing here
proposes restructuring `agents/` or introducing an adapter layer.

1. **Fix D-1 before Learning ships.** Learning's SSE endpoint is a copy of the
   report one; fixing the fan-out once, in a shared helper, means both features
   get it. Copying it means shipping a known defect twice.
2. **Extract the job lifecycle into one module** (`agents/jobs.py`): create,
   status transition, event push (memory + subscribers + Mongo), reap, cancel.
   This is the single change that stops V-1 from being duplicated. ~120 LOC
   moved, no behavior change.
3. **Collapse the provider dispatch (D-3)** to one table before adding any new
   LLM call site.
4. **Admin-gate or delete `/reports/rescore` (D-2).**
5. Leave B-1/B-2/V-6 alone. A repository layer for two features is speculative
   abstraction; revisit if a third persistence-backed feature appears.

---

*Cross-references: `02_API_Coverage_Audit.md` (contract surface),
`03_Learning_Backend_Design.md` (D-1/V-1 inheritance),
`04_Observability_Audit.md` (D-7, D-8), `05_Testing_Audit.md` (D-4).*
