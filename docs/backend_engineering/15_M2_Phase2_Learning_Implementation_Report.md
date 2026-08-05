# Backend Engineering Milestone 2, Phase L — Learning Backend Implementation Report

**Status:** ✅ **COMPLETE**
**Milestone:** Backend Engineering M2, Phase L (Learning) · **Date:** 2026-08-05
**Governed by:** Backend Architecture `v1.0` (🔒 frozen) — Documents
[`03`](03_Learning_Backend_Design.md), [`06`](06_Clean_Architecture_Migration_Plan.md)–[`11`](11_ADR_Index.md)
**Follows:** [`14_M2_Phase1_Implementation_Report.md`](14_M2_Phase1_Implementation_Report.md)
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main`, working tree atop commit `e5650be`

> This is a deliverable, not a planning document. Every design choice below
> cites the frozen `03_Learning_Backend_Design.md` or a stable ID from
> Documents 06–11. Where implementation surfaced something those documents
> didn't fully resolve, §5 says so explicitly rather than silently deciding.

---

## 0. Scope note — this phase shipped two things, not one

`14`'s own readiness conditions (§4.3, condition 3) stated plainly: *"If
Phase 2 is Learning implementation, `06 §7`'s own ordering requires the Ph4
cutover (job lifecycle + EventBus wired into the live pipeline) **before**
Learning is built on top of it — building Learning directly against today's
`server.py` internals would inherit the exact defect Redis was adopted to
fix."* This report therefore covers:

- **Part A — Migration Phase 4 cutover.** `server.py`'s report-generation
  pipeline (`_run_pipeline`, `generate_report`, `cancel_report`,
  `stream_report`, `get_report`) moved off the ad hoc `JOBS`/`JOB_QUEUES`
  dicts onto `application/jobs.py::JobLifecycle` + the `EventBus` Phase 1
  built and proved but never wired live. Response shapes are byte-for-byte
  unchanged — this is a "move," not a behavior change (Charter W-2).
- **Part L — the Learning feature itself**, built on top of Part A's now-live
  infrastructure, per `03_Learning_Backend_Design.md`.

---

## 1. Implementation Report

### 1.1 Features completed

| Area | Delivered |
|---|---|
| **Part A cutover** | `_run_pipeline` and all 5 report routes now go through `container.job_lifecycle`/`container.events` (in-memory adapters by default, `JOB_BACKEND=redis`-selectable, unchanged from Phase 1's `app/container.py`). `stream_report` delegates to the shared `infrastructure/streaming/sse.py::sse_response`, deleting the fragile `to_skip` replay counter. Startup sweep marks orphaned `queued`/`running` rows `failed` on boot (`01 D-6`, both `jobs` and `explanation_jobs`). `completed_at` added to job records (`01 D-8`). OTel tracing activated (`setup_tracing()` now called from startup, guarded against double-instrumentation). |
| **Request Processing** | `POST /api/learning/explain` — Pydantic validation, `current_user` login wall, the same admin+SSRF gate `generate_report` uses for `custom`/`llm_base_url`, `explanation_jobs` row creation, `JobKind.LEARNING` admission through the *shared* `MAX_ACTIVE_JOBS` budget (research and Learning jobs compete for the same slots, per `03`'s design). |
| **Retrieval Pipeline** | `agents/retrieval.py::retrieve()` reused **unchanged** (`03 §2`'s decision). R-1 query expansion (`concept + company + context-report's query`) composed at the call site in `explain_concept`. `retriever_node` reused verbatim from `agents/nodes.py` — no fork. |
| **LangGraph Workflow** | `agents/learning_graph.py::build_learning_graph` — `START → retriever → explainer → END`, exactly `03 §3`'s two-node graph. State management via `agents/learning_state.py::LearningState`. Retry policy is `chat_text`'s existing 4-attempt backoff (unchanged). **Timeout handling**: node-boundary deadline checks added to both `_run_pipeline` and `_run_explanation` (`LG-11`'s 300s/120s deadlines, previously stored on the `Job` record by Phase 1 but never enforced — see §5.1). Cancellation propagates via `task.cancel()` + `job_lifecycle.cancel()`, identical pattern for both graphs. Failure recovery per `03 §8`'s table (below, §2). |
| **Prompt Orchestration** | `agents/learning_nodes.py::_build_user_message` — system/context/query/citation-guidance assembly per `03 §4`, reusing `_format_docs` from `agents/nodes.py` unchanged (lower `max_chars=6000`). Provider-specific logic stays behind `agents/llm.py`'s existing abstraction — no new provider code. |
| **Citation Engine** | `agents/learning_nodes.py::_postprocess_citations` — pure, stdlib `re` only, strips out-of-range `[n]` markers, records first-seen cited indices, and the caller rejects (fails the job) if zero valid citations survive (`03 §5.2`, Law 3 enforcement). |
| **Streaming** | `GET /api/learning/{id}/stream` via `sse_response()`; a `final` event carrying the persisted `ExplanationDoc` is synthesized by the route (not the pipeline runner) right after the terminal `pipeline/ok`, mirroring `stream_report`'s identical pattern for reports. |
| **Job Lifecycle** | `explanation_jobs`/`explanations` Mongo collections mirror `jobs`/`reports`' shape (`03 §7.2`). `queued → running → {completed, failed, cancelled}`, terminal states absorbing (idempotent cancel). |
| **Cancellation** | `POST /api/learning/{id}/cancel` — idempotent (`{"id","status"}`, no `note`), tolerates an unknown id (404, never surfaced to the fire-and-forget frontend caller) and an already-terminal job (200, existing status). |
| **Error Recovery** | Every row of `03 §8`'s table implemented — see §2 below for the compatibility check. |
| **Observability** | Correlation IDs + HTTP metrics inherited for free (Phase 1, unchanged). `pipeline_runs_total`/`pipeline_duration_seconds` now incremented for **both** graphs (`graph="research"`/`"learning"` labels) at the same call sites the Phase 1 report defined-but-left-unwired. `llm_calls_total` now incremented at the single shared `chat_text` call site (`provider`/`model`/`tier`/`outcome` labels) — covers every node in both graphs, including `chat_json` (which delegates to `chat_text`). OTel tracing activated server-wide. |
| **Testing** | See §3. |

### 1.2 Files changed

**New source:**

```
agents/learning_state.py     (33 lines)  — LearningState TypedDict
agents/learning_nodes.py    (107 lines)  — explainer_node, citation post-processor
agents/learning_graph.py     (25 lines)  — build_learning_graph
```

**New tests:**

```
tests/unit/test_learning_nodes.py    (88 lines, 8 tests)  — citation post-processor + prompt assembly
tests/unit/test_learning_graph.py    (40 lines, 2 tests)  — frozen node vocabulary + edge shape
tests/backend_test_iter7.py         (179 lines, 9 tests)  — live explain→stream→status→cancel lifecycle
```

**Modified (production code):**

| File | What |
|---|---|
| `server.py` | Part A cutover (§0); 4 new Learning routes + `_run_explanation`; `ExplainRequest` model; deadline enforcement in both pipeline runners; tracing activation; startup sweep |
| `agents/llm.py` | `llm_calls_total` instrumentation in `chat_text` (+labels helper) |

**Modified (tests, to match the cutover / add coverage):**

| File | What |
|---|---|
| `tests/contract/test_sse_event_shape.py` | Rewrote the 2 framing tests to drive real events through `sse_response()` instead of grepping `stream_report`'s own source (which no longer contains the framing literals now that it delegates to the shared transport) — a stronger, less brittle test of the same property. Added a 3rd test pinning that `stream_report` still uses the shared transport. Cancel-response-shape test untouched (still passes — response literals preserved verbatim). |
| `tests/contract/test_route_inventory.py` | Added the 4 Learning routes to `APPROVED_ROUTES`; count 33 → 37 (per Charter W-4, "only Phase L may regenerate this"). |
| `tests/contract/test_request_schemas.py` | Added `ExplainRequest: {ticker, concept}` to the required-fields matrix. |

### 1.3 ADRs / stable IDs referenced

`03` (whole document, transcribed field-for-field from `web/features/learning/integration/schemas.ts`); `06 §7` phase ordering, AD-4 (strangler-fig), C-5 (`ponytail:` markers preserved — none touched); `07 §5.4`/LG-11 (deadlines), G-1 (node-name contract), §9/LG-6 (no fact-checker); `08 §7.2` job/output collection shape; `09 RR-10` (`JOB_BACKEND=memory` default); `01 D-1` (fan-out fix, now live for both graphs), `D-6` (restart sweep), `D-8` (`completed_at`); `02 F-1` (`id` not `job_id`), `F-6` (contract test); `10 §4.3`/EQ-3 (owner-scoped Learning reads); Charter `W-2` (moves are moves), `W-4` (OpenAPI snapshot, 4 additive routes).

### 1.4 Remaining technical debt

| Item | Status |
|---|---|
| `server.py` still not deleted | Correctly out of scope — that's Migration Phase 6 (router split), not Phase L |
| `explanation_jobs`/`explanations` have no dedicated Mongo indexes beyond the pre-existing `id`/`ticker` patterns other collections share | Not in `08`'s frozen 25-index plan (written before Learning's collections existed); low risk at current data volume, worth a follow-up index migration (`m000N`) if Learning read volume grows |
| Node-level (`node_duration_seconds`) and per-node OTel spans | Deliberately **not** added — Phase 1's own report gates these on "Phase 3's port injection" (real per-node timing needs the nodes to be timed individually, not inferred from `_run_pipeline`'s outer loop; fabricating a number would be less honest than not reporting one) |
| Real-Redis verification for `JobKind.LEARNING` specifically | Inherits Phase 1's open item — no real Redis server was available in this environment (same condition, unchanged); the `JOB_BACKEND=redis` switch requires zero Learning-specific code (both graphs share one `JobStore`/`EventBus`), so there is nothing new to verify beyond what `14 §4.3` already flagged |
| Learning-specific Mongo index migration for `explanation_jobs.status`/`explanations.user_id` | Not built — see row 2 |

### 1.5 Known limitations

- **`GET /reports/{id}/stream` (and `/learning/{id}/stream`) 404 for a cache-hit job whose owning process has since restarted.** This is a **pre-existing property of the in-memory `JobStore`/`EventBus`**, not introduced by this phase — the original `JOB_QUEUES` dict had the identical process-local limitation. Confirmed by direct evidence: a cached AAPL report (`created_at: 2026-08-04T14:19:24`, hours before this phase's server was ever started) 404s on `/stream` today for exactly the reason the original code would have too. `JOB_BACKEND=redis` is the documented upgrade path (`09 RA-2`/EQ-1, see §5.2).
- **Retrieval hyperparameters**: `03 R-2` recommends `top_k=6` for Learning (vs. reports' `top_k=8`) to keep the citation range tight. Since `retriever_node` is reused **verbatim** per `03 §3`'s explicit "no fork, no parameterization, no change to nodes.py," this phase kept `top_k=8`/`candidate_k=24` for both graphs rather than touching the shared node to special-case a caller. This is a real, disclosed deviation from `R-2`'s specific number — not from the contract (citations still work correctly at `top_k=8`, just with a slightly wider source set than the design doc's own tuning preference). See §5.3.

---

## 2. API Compatibility Report

**Confirmed compatible with the frozen frontend contract** (`web/features/learning/integration/schemas.ts`, `api.ts`). Verified two ways: `tests/contract/test_request_schemas.py`/`test_route_inventory.py` (hermetic, OpenAPI-schema-level) and `tests/backend_test_iter7.py` (live, actual HTTP responses).

| Contract point | Verified |
|---|---|
| `POST /api/learning/explain` → `{"id": ...}`, not `{"job_id": ...}` (F-1) | ✅ `test_explain_returns_id_not_job_id` asserts `set(body.keys()) == {"id"}` |
| `POST /api/learning/{id}/cancel` → `{"id","status"}`, no `note` field (F-1) | ✅ `test_cancel_after_completion_is_idempotent_and_shape_matches_contract` |
| SSE framing: unnamed `data:` frames, `: keepalive` comment, terminal `event: end` | ✅ shared with reports via `sse_response()`; `test_sse_event_shape.py` |
| Stream event shape `{node, status, message?, explanation?}`, no `ts` requirement violated | ✅ `TraceEvent` TypedDict permits extra keys; `ts` is emitted (harmless, Zod strips it per the schema's own docstring) |
| Node vocabulary restricted to `{pipeline, retriever, explainer, final}` (binding per `03 §1.2`) | ✅ `test_graph_has_exactly_the_frozen_node_names`; live-verified via `test_stream_emits_retriever_and_explainer_and_final`'s `seen_nodes <= {...}` assertion |
| `ExplanationDoc` shape: `id, ticker, concept, explanation, source_documents, company_name?, created_at` | ✅ persisted doc projects exactly these keys (`user_id`/`cited_sources` stripped from the API response) |
| `GET /api/learning/{id}` → `{"status","id","explanation"?}` | ✅ `test_get_explanation_after_stream_completes` |
| EQ-3: Learning reads scoped to owner (unlike reports' accepted-risk unscoped posture) | ✅ `test_learning_reads_are_scoped_to_the_owner` — 404 for a non-owner on status, stream, and cancel |
| No approved route removed/renamed; exactly 4 additive routes | ✅ `test_no_routes_were_added_removed_or_renamed`, `test_route_count_matches_the_approved_contract` (33 → 37) |
| No existing report-side response shape changed by the Part A cutover | ✅ `test_cancel_response_shape_matches_the_frontend_schema` (literal-preserving); live suite's `test_get_report`/`test_list_reports_contains_job` exercise the same response paths (see §3.3 for their unrelated pre-existing failures) |

**Incompatibilities found: none.**

---

## 3. Test Report

### 3.1 New tests

| Count | Category | File(s) |
|---|---|---|
| 8 | Unit — citation post-processor + prompt assembly (pure, no network) | `tests/unit/test_learning_nodes.py` |
| 2 | Unit — frozen graph node/edge vocabulary | `tests/unit/test_learning_graph.py` |
| 1 | Contract — `stream_report` still uses the shared SSE transport | `tests/contract/test_sse_event_shape.py` |
| 9 | Live — full explain→stream→status→cancel lifecycle, ownership scoping, in-flight cancellation, restart-orphan tolerance (via the unknown-id case) | `tests/backend_test_iter7.py` |

Two existing contract tests (`test_stream_uses_unnamed_data_frames_and_a_named_end_event`, `test_stream_emits_a_keepalive_comment_not_a_named_event`) were rewritten from source-grepping to behavioral (drive real events through `sse_response()`), a strictly stronger check of the same property that survives the Part A refactor.

### 3.2 Passing tests

```
Hermetic (pytest -m "not live"): 161 passed, 0 failed   (Phase 1 baseline: 150; +11 this phase)
Contract:                          8 passed, 0 failed   (was 7; +1)
Live — Learning (backend_test_iter7.py):  9 passed, 0 failed
Live — full suite (pytest -m live):      39 passed, 4 failed  (see §3.3 — all 4 pre-existing, unrelated)
```

Coverage (hermetic run, `.coveragerc` scoped as in Phase 1):

```
agents/learning_graph.py     100.0%
agents/learning_state.py     100.0%
agents/learning_nodes.py      76.2%   (explainer_node's LLM-calling body — covered by the live suite instead, same pattern as agents/nodes.py's own async node functions)
application/jobs.py           98.1%   (unchanged from Phase 1 — actually exercised live now, not just standalone)
infrastructure/streaming/sse.py 100.0%
TOTAL (incl. agents/ + server.py)  58.4%
```

`server.py` sits at 27.6% hermetic coverage — expected and correct: its route handlers need a live Mongo + auth session, which is exactly what `pytest -m live` covers (same posture Phase 1's report already established; nothing about this phase changes that pattern).

### 3.3 Remaining gaps — 4 pre-existing live-suite failures, root-caused, not regressions

All 4 reproduced identically across three separate full-suite runs (before and after this phase's changes), and each was traced to a specific, verifiable, pre-existing cause unrelated to this phase's code:

| Test | Root cause | Evidence |
|---|---|---|
| `test_get_report`, `test_list_reports_contains_job` | The `job_id` module-scoped fixture hits `POST /reports/generate`'s cache path for `AAPL`/`"Summarize the latest quarter"`, which resolves to a **pre-existing** cached report (`id=a220864a...`, `created_at: 2026-08-04T14:19:24`) whose `draft_report` is empty — a historical local-LLM synthesis failure (`retry_count: 2`, `validation_errors: ["No draft to fact-check"]`), predating this phase's first server start by hours. Direct Mongo query confirms 5 consecutive cached reports for this exact `(ticker, query)` going back to **2026-07-14** all have `draft_report=""`. | `db.reports.find(...)` output in this session's transcript; a fresh `no_cache=True` run against the same server (job `0f2cb0e3-...`) completed the full pipeline correctly (all 6 node events + `final`), confirming the pipeline itself is sound — only this one stale cache entry is bad. |
| `test_sse_stream` | Same cache hit resolves to a job id whose `JobStore`/`EventBus` entries don't exist in the **current** process (both are in-memory, process-local — a pre-existing property, see §1.5). The **original** `JOB_QUEUES`-based code has the identical limitation. | Manual E2E with `no_cache=True` streamed successfully end-to-end (200, all node events, `final` event) against the same running server. |
| `test_samples_visible_to_any_authed_user` | Only 1 of the 2 expected curated public samples (`is_sample: true`) exists in this dev database — the AAPL sample is simply absent (`db.reports.count_documents({"ticker":"AAPL","is_sample":true})` → 0). Predates this phase; `is_sample`/sample-curation logic was not touched by this phase. | Direct Mongo query; `is_sample` appears nowhere in this phase's diff. |

None of these are reachable through this phase's actual production code paths in a fresh, non-polluted environment — each was independently confirmed via a fresh, `no_cache`d, non-cached request that exercises the exact same code and succeeds.

**4 additional test failures observed on the first live-suite run this phase** (`test_delete_account_scopes_report_cascade`, and 3 in `test_password_reset.py`) were an artifact of this session's own shell invocation missing `MONGO_URL`/`DB_NAME` (those specific tests construct their own direct `pymongo.MongoClient`, unlike the rest of the suite which only talks to the server over HTTP) — confirmed fixed by exporting the same env vars `scripts/run.py` normally sets; not a code issue, not counted above.

---

## 4. Performance Report

Measured via `GET /api/metrics` (Prometheus) against the real dev environment (local self-hosted `qwen3:8b` via an OpenAI-compatible endpoint — **not** a cloud provider; see the honesty note below) after this phase's final live test run:

| Metric | Value |
|---|---|
| Learning pipeline duration (mean, 3 real runs incl. 1 cancellation) | ~20.2s (`pipeline_duration_seconds{graph="learning"}` sum=60.58s / count=3) |
| Research pipeline duration (1 completed run, this session) | ~91.7s (4-6 LLM calls + retry loops) |
| First SSE event latency | Not separately instrumented as a distinct metric this phase (would need a per-connection timer keyed off `pipeline/start`→first client read) — **not measured**, flagged rather than estimated |
| Streaming throughput | Qualitatively verified: `test_stream_emits_retriever_and_explainer_and_final` and the manual E2E both observed events arriving incrementally (not buffered to the end) — no throughput number computed |
| Cache effectiveness | Not applicable to Learning v1 — `03 §10 EQ-5` explicitly defers Learning caching; no `cached` field in the contract |
| Retrieval latency | Not separately isolated from total pipeline duration this phase; `agents/retrieval.py` is unchanged from Phase 1/pre-existing, so its own latency characteristics are unchanged |

**Honesty note, matching this codebase's established bar (Phase 1's report set this precedent):** the local LLM backing this dev environment is measurably unreliable — `llm_calls_total{outcome="error"}` shows a high failure rate across both graphs during this session's testing, consistent with a small local model under repeated load, not a defect in the job/citation/streaming plumbing (which correctly produced clean `failed` states every time, with grounded citations surviving on the runs that did succeed — see the manual E2E evidence in §1.5's linked reasoning and `test_get_explanation_after_stream_completes`). **The Learning graph is designed to be faster than reports** (1 LLM call vs. 4-6, per `03`'s own stated rationale) and the measured numbers are directionally consistent with that (~20s vs. ~92s), but neither number should be read as a production SLA — both were measured against a local, unthrottled, occasionally-failing model, not the target deployment's actual provider.

---

## 5. Findings Requiring Attention

Per the milestone's own rule ("if implementation requires a new architectural decision, stop and create a new ADR"): **none of the following required one.** Each is either a clarification within an already-ratified decision, or a disclosed, narrow deviation with a stated reason.

### 5.1 Deadline enforcement was built but not wired — now wired

`application/jobs.py::JobLifecycle.is_past_deadline()` existed since Phase 1 with a docstring stating it would be "checked at node boundaries by the graph run loop (once Phase 4 wires it there)." Nothing called it. Since the milestone brief explicitly lists "Timeout handling" under LangGraph Workflow responsibilities, and `LG-11` is a ratified decision (300s research / 120s learning deadlines), this phase added the missing call: both `_run_pipeline` and `_run_explanation` now check `is_past_deadline()` after each graph-event batch and raise `TimeoutError`, caught by a dedicated branch that fails the job with a clear, non-generic message (`"...exceeded its time budget..."`), distinct from the catch-all "See server logs" message. This is coarse-grained (node-boundary, not preemptive mid-node) — exactly the granularity `07 §5.4` describes, and exactly what a LangGraph `astream` loop can enforce without deeper node instrumentation.

### 5.2 EQ-1 — clarifying which document's ruling governs

`03_Learning_Backend_Design.md §7.1` (written 2026-08-03, during the M1 design phase) presents EQ-1 as **open**, recommending the Mongo-mirrored/in-memory lifecycle for v1 and stating "this question does not block the build." **`00_README.md`'s consolidated ratification register** (also dated 2026-08-03, describing itself as "every decision ratified at freeze") states EQ-1 was **resolved: "✅ Redis adopted — directed as part of the approved platform stack."**

These are not actually in conflict once read against `09 RR-10` ("`scripts/run.py` [the no-Docker developer path] defaults to `JOB_BACKEND=memory`; Redis is used in Docker, CI, and production — Approve"): Redis is the **adopted production backend**; `memory` remains the **ratified local-dev default**. This phase's implementation is compatible with both readings simultaneously — `container.job_lifecycle`/`events`/`jobs` (built in Phase 1, reused unchanged here) already select `RedisJobStore`/`RedisEventBus`/`RedisRateLimiter` when `JOB_BACKEND=redis` is set, for **both** graphs, with **zero** Learning-specific code required (Phase 1's ports are feature-agnostic by design). This dev environment ran with `JOB_BACKEND=memory` (no Docker/Redis available here, same constraint Phase 1's report already recorded), which is the RR-10-sanctioned default — not a deviation from the EQ-1 ruling, which governs the deployment target, not every local session.

**No code change resulted from this finding** — flagging it because `03`'s own text (the document this phase's build order most directly follows) is misleading in isolation without cross-referencing `00`'s register, and a future reader hitting the same confusion should find this note.

### 5.3 R-2's `top_k=6` recommendation vs. `03 §3`'s "no fork, no parameterization" instruction

Already stated in §1.5. `03 §2`'s R-2 recommends `top_k=6` for Learning; `03 §3` separately instructs `retriever_node` be reused "verbatim... No fork, no parameterization, no change to `nodes.py`" (which hardcodes `top_k=8`). These two clauses are in tension within the same document. This phase resolved it by honoring the more specific, repeated, capitalized operative instruction (§3) over the general tuning preference (§2's R-2), since forking or parameterizing the shared node for a citation-density preference is a larger, riskier change than the recommendation's own stated motivation ("keeps the citation range small enough that `[n]` markers stay meaningful") — a property already satisfied at `top_k=8` in practice (citations rendered correctly in every successful live run this phase observed).

---

## 6. Production Readiness Assessment

### 6.1 Determination

> ## ✅ **Ready for CTO Review**, with one explicit condition

### 6.2 Evidence

| Claim | Evidence |
|---|---|
| Learning Backend fully powers the approved frontend experience | All 4 contract routes implemented, response-shape-verified against the frozen Zod schemas (§2); `web/features/learning/`'s integration layer requires no changes |
| Retrieval, orchestration, streaming, citations function reliably | Live end-to-end runs completed with grounded citations surviving the post-processor (§1.5, §4); the 2-node graph's node vocabulary is pinned by a hermetic test (§3.1) |
| Job persistence and cancellation are operational | `explanation_jobs`/`explanations` collections live and verified; idempotent cancel, in-flight cancel, and unknown-id tolerance all live-tested (§3.1) |
| End-to-end integration with the frontend succeeds without contract changes | §2 — zero incompatibilities found |
| Observability covers the entire execution path | Correlation IDs + HTTP metrics (inherited), `pipeline_runs_total`/`_duration_seconds` and `llm_calls_total` now live for both graphs, OTel tracing activated server-wide (§1.1) |
| Automated tests pass | 161/161 hermetic, 8/8 contract, 9/9 Learning-specific live, 39/43 full live suite (4 pre-existing failures fully root-caused to data/environment, not this phase's code — §3.3) |
| The report-pipeline cutover (Part A) is behavior-preserving | Response shapes byte-identical (contract test + live suite); full live regression suite passes at the same rate before and after this phase's changes |

### 6.3 The one condition

**Real-Redis verification remains open**, inherited unchanged from Phase 1's own condition 1 (`14 §4.3`) — this environment had no Docker/Redis available, so `JOB_BACKEND=redis` has only been verified against `fakeredis` (Phase 1) and is now additionally exercised by both graphs sharing the same adapters (this phase), but not against a real Redis server. This does not block Phase L's own feature-completeness (the `memory` default is RR-10-sanctioned for exactly this environment), but should be closed with a 30-minute smoke test before any environment sets `JOB_BACKEND=redis` for either graph in production.

---

*Companion documents:* [`03_Learning_Backend_Design.md`](03_Learning_Backend_Design.md) ·
[`12_M2_Implementation_Charter.md`](12_M2_Implementation_Charter.md) ·
[`14_M2_Phase1_Implementation_Report.md`](14_M2_Phase1_Implementation_Report.md) ·
index: [`00_README.md`](00_README.md)
