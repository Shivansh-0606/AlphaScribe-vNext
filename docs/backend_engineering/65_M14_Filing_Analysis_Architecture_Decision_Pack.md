# 65 — M14 Filing Analysis Architecture Decision Pack

**Status:** 🟢 **CTO-RATIFIED (2026-08-31) — M14 FILING ANALYSIS
ARCHITECTURE.** This document determines *how* M14 Filing Analysis should be
built; it does **not** build it. The CTO architecture ratification is
recorded as a dated governance record in **§27** (2026-08-31). **Ratification
does NOT authorize implementation, commit, push, MongoDB schema realization,
or C-2. M14 implementation is NOT AUTHORIZED. Commit is NOT AUTHORIZED. Push
is NOT AUTHORIZED.** Architecture ratification is a distinct CTO act that
does **not** by itself authorize implementation (§24, §25, §27). The §20.1
STOP/CONTINUE validation gate remains binding and is **not** cleared by this
ratification.
**Type:** Architecture decision pack (research / design / governance only —
no source code, test, schema, migration, index, route, LangGraph node,
retrieval / RAG code, MongoDB collection, Redis infrastructure, prompt,
frontend, configuration, or evaluation code created or modified to produce
it). The only file this task creates is this document.
**Governance chain:**
`Document 62` (Post-M13 roadmap; C-1 = preferred direction) →
`Document 63` (M14 = C-1 Filing Analysis — FORMALLY SELECTED) →
`Document 64` (**M14 Filing Analysis API Contract — 🟢 CTO-RATIFIED
2026-08-31**; the authoritative source of M14 externally observable
behaviour) →
**`Document 65` (THIS — architecture decision pack — 🟢 CTO-RATIFIED
2026-08-31, §27)** →
**next stage: Separate M14 Implementation Authorization** (its own
scope-bound CTO act — NOT created by this ratification) → engineering →
technical review → commit → push.
**Contract authority:** [64_M14_Filing_Analysis_API_Contract.md](64_M14_Filing_Analysis_API_Contract.md)
is the ratified contract. This pack **does not change, reinterpret, weaken,
or expand it.** Where this pack and Document 64 could appear to differ,
Document 64 governs and this pack is wrong.
**Decision status of everything in this pack.** **The §24
architecture-ratification gate is now cleared (2026-08-31); the dated
ratification record is §27.** The "Recommended decision" wording below is
retained as written; **§27 (not this pack body)** states which
recommendations the CTO adopted as **RATIFIED ARCHITECTURE DECISIONS**
(OAQ-3, OAQ-4, OAQ-6, OAQ-7, OAQ-8, OAQ-9, OAQ-10), which are adopted as
**CONDITIONAL** on the §20.1 validation gate (OAQ-1, OAQ-2), and which is
adopted as a **RATIFIED LOGICAL ARCHITECTURE DECISION ONLY** with schema
realization **delegated** to an external governance chain (OAQ-5; §12.1
schema governance). The decision-status legend is §1.1; the proposal-time
per-OAQ status column is §22; the ratified per-OAQ status is §27.2.
**This ratification authorizes nothing further.** Architecture ratification
(§24, §27) is a distinct CTO act that, even when granted, does **not** by
itself authorize implementation, commit, push, or any MongoDB schema
realization (§12.1, §24, §25).
**Structural precedent (cited, unmodified):**
[60_M13_Filing_Content_Reading_Architecture_Decision_Pack.md](60_M13_Filing_Content_Reading_Architecture_Decision_Pack.md)
(the M13 architecture-pack pattern),
[41_M9_Pre_Implementation_Architecture_Decision_Pack.md](41_M9_Pre_Implementation_Architecture_Decision_Pack.md)
and [43_M9_API_Contract_Decision_Pack.md](43_M9_API_Contract_Decision_Pack.md)
(the M9.1 async-LLM-capability architecture — the closest genre precedent, an
LLM-backed grounded/cited capability built **out of graph**),
[07_LangGraph_Architecture.md](07_LangGraph_Architecture.md) (🔒 v1.0 —
frozen; G-1 node-name contract, §2.3 reducer rule, LG-1/LG-11/LG-12),
[08_MongoDB_Data_Architecture.md](08_MongoDB_Data_Architecture.md) (the
schema-change governance authority).
**Date:** 2026-08-31.

---

## 0. What This Document Is and Is Not

**Is:** an evidence-backed evaluation of every open architecture question
Document 64 carried forward (OAQ-1…OAQ-10), plus independent evaluation of
data representation, execution, retrieval/analysis, citation-anchor
discovery, persistence, AI execution, and API/runtime; a recommended
architecture with rationale, operational consequences, rejected
alternatives, and every new governance dependency named; and an explicit
acceptance-criteria gate for future CTO architecture ratification.

**Is not:** an implementation; an implementation authorization; a commit or
push authorization; a change to Document 64; a new API contract; a schema,
migration, index, collection, route, handler, LangGraph node, prompt,
retrieval module, Redis component, frontend component, test for new
functionality, or production configuration; a decision that C-2 precedes or
does not precede C-1 in a way that rewrites Document 63; a roadmap
re-sequencing (§20 identifies that as a **separate** governance decision if
it becomes necessary). It resolves no contract question — CQ-1/CQ-2/CQ-3 are
already CTO-resolved in Document 64 §18 and are treated here as frozen
inputs.

---

## 1. Document Status

| Item | State |
|---|---|
| M14 | **= C-1 Filing Analysis** — formally selected (Document 63) |
| Document 64 (M14 API Contract) | **🟢 CTO-RATIFIED (2026-08-31)** — externally observable behaviour frozen |
| Document 65 (this architecture pack) | **🟢 CTO-RATIFIED (2026-08-31) — M14 FILING ANALYSIS ARCHITECTURE** (dated governance record: §27). Implementation remains **NOT AUTHORIZED**. |
| M14 architecture | **CTO-RATIFIED (2026-08-31)** — OAQ-3/4/6/7/8/9/10 ratified; OAQ-1/OAQ-2 ratified **as conditional** on the §20.1 gate; OAQ-5 ratified **as the logical decision only** (§27.2; §1.1 legend) |
| §20.1 STOP/CONTINUE validation gate | **BINDING — not cleared by ratification** (implementation-phase gate) |
| MongoDB schema realization (`filing_analyses`, `filing_analysis_jobs`, indexes) | **NOT AUTHORIZED** — requires `08_MongoDB_Data_Architecture.md` + ADR chain (§12.1), a step distinct from and subsequent to this ratification |
| M14 implementation | **NOT AUTHORIZED** |
| Commit | **NOT AUTHORIZED** |
| Push | **NOT AUTHORIZED** |
| C-2 Structured Filing Extraction | **neither selected nor rejected** (Document 62 §6 C-2; Document 63 §6; Document 64 §16). This pack assesses C-2 sequencing (§20) but does **not** decide, select, reject, or implement it. |
| Filing Q&A | **excluded from M14** (Document 64 §6). This pack introduces no conversational Q&A. |

**The M14 Filing Analysis architecture is now CTO-RATIFIED (2026-08-31;
§27) — implementation is not.** §27 adopts the §7 / §22 architecture
decisions per the §1.1 legend (ratified / conditional / logical-only /
external-dependency); it authorizes no implementation, commit, push,
MongoDB schema realization, or C-2. Document 64 remains the frozen
API-contract authority.

### 1.1 Decision-status legend

Every decision-bearing statement in this pack carries (explicitly, or by the
§22 status column) exactly one of these statuses. The future
architecture-ratification record must be able to sort every item into one of
these buckets and say precisely which the CTO ratified.

| Status | Meaning | At §24 ratification |
|---|---|---|
| **PROPOSAL-TIME RECOMMENDATION** | This pack's recommended answer, with rationale and rejected alternatives. **Not yet decided.** | Becomes **RATIFIED** only if the ratification record explicitly adopts it. |
| **RATIFIED ARCHITECTURE DECISION** | Recorded by the CTO ratification record (§27.2, 2026-08-31): OAQ-3, OAQ-4, OAQ-6, OAQ-7, OAQ-8, OAQ-9, OAQ-10. OAQ-1 / OAQ-2 are ratified **as conditional**; OAQ-5 as a **logical decision only**. | Set by the ratification record (§27), not by this pack body. |
| **CONDITIONAL DECISION** | A recommendation whose validity depends on an empirical result not yet available. Ratifying it ratifies *the conditional structure*, not an unconditional claim. | Ratified **as conditional**; the condition (§20.1 gate) still applies. |
| **IMPLEMENTATION VALIDATION GATE** | An explicit STOP/CONTINUE checkpoint the implementation phase must clear before proceeding (§20.1). | Ratified **as a gate**; not pre-cleared by ratification. |
| **EXTERNAL GOVERNANCE DEPENDENCY** | A change that requires its own separate governance chain (schema/data governance §12.1; roadmap re-sequencing §20.1; route-inventory under implementation authorization). | **Not** authorized by architecture ratification; recorded as still-owed. |
| **UNRESOLVED / NON-RATIFIED MATTER** | A question this pack does not settle and does not ask ratification to settle. | Remains open; the ratification record names it as such. |

---

## 2. Governance Context

- **Document 62** ratified C-1 Filing Analysis as the preferred roadmap
  direction and left the chunk-vs-section question OPEN (§7).
- **Document 63** formally selected M14 = C-1 Filing Analysis as a distinct
  CTO act, authorizing progression to the contract-governance stage only.
- **Document 64** is the CTO-ratified M14 API Contract. It froze the
  **externally observable** M14 behaviour (§4–§17 of Document 64) and
  explicitly reserved OAQ-1…OAQ-10 to *this* pack (Document 64 §5.1, §19,
  §22). CQ-1 (four-output roster), CQ-2 (fixed full set, no selection
  parameter), and CQ-3 (flat cited narrative representation) were resolved
  by a separate CTO decision of 2026-08-31 and are frozen contract inputs.
- **This pack** is the next authorized governance activity after Document 64
  ratification (Document 64 §20, §21, §22).

**No governance state above is changed by this document.** It is cited, not
re-decided.

---

## 3. Contract Authority — frozen inputs this pack must not touch

The following are ratified by Document 64 and are **inputs**, not decisions,
for this pack. This pack preserves each without reinterpretation.

| # | Frozen by Document 64 | Where |
|---|---|---|
| C-1 | **Exactly four outputs:** Filing Summary, Risk Factors Digest, MD&A Digest, Important Changes. No additional M14 output. | §8, §18 (CQ-1) |
| C-2 | **Fixed full output set.** Every request returns all four outputs. **No** client-selectable output subset parameter. | §7, §9.2, §18 (CQ-2) |
| C-3 | **Response representation = flat cited narrative:** each output is `narrative` + `sources[]` + `cited_source_indices` + output `state`. Not to be replaced by an architecture-driven shape. | §8.2, §9.3, §18 (CQ-3) |
| C-4 | **Grounding:** every substantive factual claim grounded in the selected filing's own persisted content; no cross-filing citations; no fabrication. | §11.1–§11.2 |
| C-5 | **Citation anchor representation floor (frozen):** `{ doc_id, chunk_start, chunk_end }` — contiguous `chunk_idx` range, both endpoints present in the filing's persisted chunks, `chunk_start ≤ chunk_end`. **How anchors are *discovered* is architecture (OAQ-9); the representation is frozen.** | §11.3, §11.5, §11.9 |
| C-6 | **`insufficient_evidence` / `partial` / `complete` semantics**, and **malformed / partial-ingest behaviour** (analyse present well-formed chunks; valid anchors only; honest state; no fabrication). | §11.6, §11.7, §11.8, §10 |
| C-7 | **INV-IC:** "Important Changes" derived **only** from material change language evidenced *within the selected filing itself* — never previous-filing comparison, cross-filing diff, historical trend analysis, or implicit temporal comparison; absent such language → `insufficient_evidence`, never fabrication. | §8.1 |
| C-8 | **Filing identity = `(ticker, doc_id)`** (company-namespaced); mismatch → 404. `current_user` on every route; corpus has no `user_id` (no ownership scoping on the filing corpus). | §7, §10, §15 |
| C-9 | **Scope exclusions:** no conversational Filing Q&A, no generic chatbot, no conversational memory, no cross-filing analysis, no durable research sessions, no alerts / background intelligence, no ingestion redesign, no new provider dependency. Additive only — no existing route changes. | §6, §10 (Invariant) |
| C-10 | **Determinism expectation:** LLM output need not be bit-identical; the **output schema** must be stable per schema version; analysis depends only on the filing + versioned prompt / schema / model — no session, no other filing. | §12 |
| C-11 | **`_id` / `embedding` never in any response.** Metadata echoed verbatim from the `filings` row. | §9.3, Document 59 §5.2 |

If any recommendation in this pack conflicts with the above, the
recommendation is defective and the contract governs.

---

## 4. Architectural Principles

1. **Contract defines WHAT; this pack defines HOW.** Document 64's frozen
   observable behaviour is the specification. This pack chooses mechanisms
   to satisfy it — nothing more.
2. **Existing code is evidence and a compatibility constraint, not an
   architectural decision.** M13's thin read adapter, the report pipeline's
   retriever, the LangGraph, the job lifecycle, and the LLM abstraction are
   inspected as *what exists*; each is adopted, extended, or bypassed on
   merit, not by default.
3. **Additive-only.** M14 changes no existing route, no existing collection
   shape, no existing graph, no existing provider path. Every new mechanism
   is opt-in for M14 alone.
4. **Reuse the proven pattern for a grounded / cited LLM capability.** M9.1
   (Comparison-Explanation) is the precedent: an async job, a flat cited
   narrative, execution-time authorization, identity-keyed dedup,
   out-of-graph orchestration with its own tracing span. M14 follows it,
   adjusted for four outputs and a single-filing evidence source.
5. **Behavioural requirement ≠ architecture decision.** Where Document 64
   states an observable requirement (grounded, cited, honest
   `insufficient_evidence`, no fabrication), this pack chooses a mechanism
   and keeps the mechanism replaceable.
6. **Name every governance dependency.** Any new collection / index /
   schema / migration goes through `08` + the ADR chain at architecture
   ratification (Document 64 §6.1, §19.3). Any LangGraph topology change is
   a stop-and-CR item. Any new frontend `node` vocabulary is a G-1
   cross-team contract. None is pre-authorized.
7. **Honest uncertainty.** Where static evidence cannot settle a question
   (notably section-location quality on real filings, §7/OAQ-1), this pack
   says so and defines a decision gate rather than inventing certainty.

---

## 5. System Context

### 5.1 Existing components (verified this session by direct read)

| Component | File | Verified state — relevance to M14 |
|---|---|---|
| Persisted filing text | `backend/agents/ingest.py::ingest_document` (277–320); `backend/agents/retrieval.py::chunk_text` (107–141) | `chunk_text` packs paragraphs (`\n\n` split) to `chunk_size≈900`, sentence-splits oversize paragraphs, prepends a 120-char tail of the previous chunk as overlap. Raw text truncated at `200_000` chars before chunking. **No headings, no section identity, no Item numbering** in the output. |
| `filing_chunks` collection | `ingest.py:298–311`; `08` §4.4 | `{ doc_id, ticker, source, chunk_idx (0-based int, ingest order), text, created_at (one value for the whole filing), embedding? (384-dim `BAAI/bge-small-en-v1.5`) }`. ~100–2,000 rows per filing. |
| `filings` collection | `ingest.py:312–320`; `08` §4.3 | `{ doc_id (uuid4 PK), ticker, company_name?, source (free text; EDGAR: `"10-Q 0000320193-24-000081 filed 2024-08-02"`; BSE / text ingest differ), num_chunks, char_count, created_at }`. Re-ingest mints a **new** `doc_id`; prior chunks are not replaced (`retrieval.py:161` ponytail note). |
| Indexes | `backend/infrastructure/mongo/indexes.py` | filings: I-10 `{ticker:1, created_at:-1}`, I-11 `{ticker:1, source:1}`. filing_chunks: I-12 `{ticker:1, created_at:-1}`, I-13 `{doc_id:1}` (single field). **No `{doc_id:1, chunk_idx:1}` compound index** (Document 59 OD-4, delegated). |
| M13 read endpoint | `backend/server.py:929–998` | `GET /companies/{ticker}/filings/{doc_id}/content` — thin adapter: `filings.find_one({ticker, doc_id})` (404 on miss), `filing_chunks.find({doc_id}, {_id:0, embedding:0}).sort("chunk_idx",1)` + Python re-sort, malformed rows omitted + `logger.warning`, frozen envelope. **No provider call, no acquisition, no write.** |
| Hybrid retriever | `backend/agents/retrieval.py::retrieve` (144–232) | BM25 (`rank_bm25`) + dense (`fastembed` `BAAI/bge-small-en-v1.5`, cached vectors) + cross-encoder rerank (`Xenova/ms-marco-MiniLM-L-6-v2`); graceful BM25-only degrade. **Ticker-scoped** (`{"ticker": ticker.upper()}`), `.sort("created_at",-1).to_list(2000)`, `top_k=8`, `candidate_k=24`. **Consumed only by the report pipeline's `retriever` node.** Not `doc_id`-scoped. |
| LangGraph | `backend/agents/graph.py`; `07` (🔒 v1.0) | One compiled `research` graph: `retriever → (extractor ‖ tone) → synthesizer → fact_checker` + conditional `fact_check_router` (accept / retry / give_up). `learning_graph` is a **separate** 2-node graph. **G-1: node names are a cross-team API contract** (frontend `streamStages.ts`). **LG-1:** a distinct capability gets its own graph, not a parameterized one. **LG-11:** one wall-clock deadline per job at node boundaries. `07` topology change = stop-and-CR. |
| LLM abstraction | `backend/agents/llm.py` | `chat_text` / `chat_json` only. Providers: gemini (env default), openai, anthropic, groq, openrouter, deepseek, mistral, custom. Per-request key + base_url via `_LLM_CTX` contextvar (`set_llm_context` / `reset_llm_context`). `chat_text` owns a 4-attempt retry/backoff loop; `NonRetryableLLMError` for deterministic faults. `chat_json` = schema-hint guardrail + JSON extraction + Pydantic validate (raises `ValueError`). Symbolic `DEFAULT_LIGHT_MODEL` / `DEFAULT_HEAVY_MODEL`. Optional `temperature`. SSRF guard `assert_public_url` + `require_admin` for custom base_url. `llm_calls_total` / `llm_tokens_total` automatic. |
| Job lifecycle | `backend/application/jobs.py`; `backend/domain/models.py` | `JobLifecycle` (start with shared `MAX_ACTIVE_JOBS` admission + opening `pipeline/start` event; mark_running; publish; complete; fail(safe_message); cancel — idempotent on terminal; is_past_deadline; reap_stale). `JobKind` = `RESEARCH`, `LEARNING`, `COMPARISON_EXPLANATION` (M9.1 added exactly one). `JobStatus` = `QUEUED·RUNNING·COMPLETED·FAILED·CANCELLED`. `Job` is Redis/in-memory job state; **Mongo is the system of record for the output artifact**. `JOB_BACKEND=memory` default; Redis optional. |
| SSE transport | `backend/infrastructure/streaming/sse.py` | `sse_response(events, stream_name=...)` — generic. Unnamed `data:{json}` frames, `: keepalive` comment, terminal `event: end\ndata:{}`. `TraceEvent` = `{node, status, message?, ts?}`. Live path for `/reports/{id}/stream` and `/learning/{id}/stream`. |
| Comparison-Explanation (M9.1) | `backend/server.py:1804–2190`; `indexes.py` I-28…I-31; Document 43 | 4-route family; job creation via **partial unique index** on `active_identity_key` (I-29) as the atomic dedup mechanism (not check;await;insert); two collections — `comparison_explanation_jobs` (job mirror, TTL 30d) + `comparison_explanations` (durable artifact, `identity_key` unique I-31, no TTL); `_run_comparison_explanation` does execution-time authorization, deadline check, identity + evidence-fingerprint compute, read-before-generate, `insert_one` + `DuplicateKeyError` adopt-or-replace, `pipeline.comparison_explanation` span, **no LangGraph** (Document 43 §16 rejected a graph-shaped label for a nodeless capability). |
| Job deadlines | `backend/app/settings.py:55–60` | research `300s`, learning `120s`, comparison_explanation `60s`, grace `30s`. |
| Error taxonomy | `backend/domain/errors.py`; Document 43 §3 | `NotFoundError`(404), `ValidationError`(422), `ConflictError`(409), `AuthorizationError`(403), `RateLimitedError`(429), `DeadlineExceededError`(504), `InfrastructureError`(502), `LLMProviderError`(502). Envelope `{ "detail", "type" }`. |
| Frozen frontend component | `docs/design/09_Component_Inventory.md` §FilingViewer; `web/components/research/FilingViewer.tsx` | `FilingViewer` **"Filing analysis" variant** — `analysis`, `source anchors`, `AI Thinking / Streaming`, `Empty (uncovered)` — is unbuilt. **Frontend work is out of M14 backend scope** (Document 64 §6, AH-6). |

### 5.2 What M14 must add (net-new, additive)

1. An async job capability that, given `(ticker, doc_id)`, produces the four
   Document 64 §8 outputs, each a flat cited narrative with validated
   filing-local anchors, and honest `complete` / `partial` /
   `insufficient_evidence` state.
2. An HTTP surface for it (route family — OAQ-4).
3. A per-output section-location + evidence-selection + summarise + cite +
   validate flow (OAQ-1, OAQ-3, OAQ-9, OAQ-10).
4. Persistence of the result and a job mirror (OAQ-5) — **subject to schema
   governance**.
5. Observability, failure handling, determinism controls, security posture
   (§15–§18).

---

## 6. Architecture Constraints

| ID | Constraint | Source |
|---|---|---|
| AC-1 | No change to the `research` LangGraph or `07` v1.0 topology unless a stop-and-CR is separately approved. | `07`; Document 62 R-9 |
| AC-2 | No change to `agents/ingest.py`, `chunk_text`, chunk size, or overlap. | Document 64 §6 |
| AC-3 | LLM access only via `agents/llm.py` `chat_text` / `chat_json`; no direct provider SDK use; no new provider dependency. | `CLAUDE.md`; Document 64 §6 |
| AC-4 | No new MongoDB collection / index / schema / migration is authorized by Document 64. Any such change is introduced only at **architecture ratification** via `08` + the ADR chain. | Document 64 §6.1, §19.3 |
| AC-5 | Additive-only: `GET /filings`, the M13 `.../content` read, `/reports/generate`, and every existing route are byte-for-byte unchanged. | Document 64 §10 Invariant |
| AC-6 | Response representation is the frozen flat cited narrative (`narrative` + `sources[]` + `cited_source_indices` + `state`). No architecture-driven replacement. | Document 64 §8.2, §9.3 (CQ-3) |
| AC-7 | Citation anchor representation is frozen (`{doc_id, chunk_start, chunk_end}`, contiguous, present, `start ≤ end`). Discovery mechanism is architecture-owned. | Document 64 §11.3, §11.9 |
| AC-8 | INV-IC preserved; no cross-document comparison of any kind for Important Changes. | Document 64 §8.1 |
| AC-9 | No conversational Filing Q&A, no conversational memory, no cross-filing analysis. | Document 64 §6 |
| AC-10 | Route-inventory exact-set contract (`assert len(APPROVED_ROUTES) == 43`) is updated only under implementation authorization (AH-9), not here. | Document 64 §2, §19.2 |
| AC-11 | `current_user` on every M14 route; no ownership scoping on the filing corpus (it has no `user_id`); job records, if owned, scope `GET`/`cancel` only. | Document 64 §15 |
| AC-12 | Determinism: stable output schema per version; no dependence on session, request history, or other filings. | Document 64 §12 |

---

## 7. OAQ-1 … OAQ-10

Each OAQ is addressed with the twelve required elements: **(1) Question,
(2) Context, (3) Contract constraints, (4) Candidate alternatives,
(5) Evaluation criteria, (6) Trade-offs, (7) Recommended decision,
(8) Rationale, (9) Operational consequences, (10) Implementation
implications, (11) Rejected alternatives and why, (12) New governance
dependency.**

---

### OAQ-1 — Chunk-vs-section representation

1. **Question.** Does M14 analysis operate over M13's ordered unstructured
   chunks as-is, over a retrieval-selected subset of them, or does it
   require a *structured section representation* (Risk Factors / MD&A /
   Item boundaries) that does not exist today?
2. **Context.** `filing_chunks` are ~900-char paragraph-packed slices with
   no headings and no Item/section identity (`chunk_text`, verified §5.1).
   SEC 10-K/10-Q have canonical Item numbering (Item 1A Risk Factors, Item 7
   MD&A), but that structure is **not persisted**. Two of the four M14
   outputs — **Risk Factors Digest** and **MD&A Digest** — are inherently
   section-scoped: producing them requires knowing *which* chunks are those
   sections. BSE annual reports and `POST /ingest/text` documents have no
   reliable Item structure at all.
3. **Contract constraints.** Document 64 §7 requires the *only* evidence
   source to be this filing's own persisted chunks, in canonical
   `chunk_idx` identity/order, and states *how much* / *how selected* is
   OAQ-1/OAQ-3 (not decided by the contract). §7 also states the contract
   does **not** assume `M13 chunks → RAG → LLM`. §8 fixes the four outputs.
   §11 requires every substantive factual claim to carry a valid
   filing-local `chunk_idx`-range anchor. §16 keeps C-2 neither selected nor
   rejected. Nothing in Document 64 requires a structured-section store.
4. **Candidate alternatives.**
   - **A. Whole-filing pass per output** — hand every chunk (in order) to
     the model for each of the four outputs; the model itself finds the
     relevant material.
   - **B. Analysis-time section location over unstructured chunks** — a
     lightweight in-request pass (heuristic heading detection over chunk
     text + short LLM classification for ambiguous chunks) labels candidate
     `chunk_idx` ranges as "risk factors", "MD&A", "other narrative",
     "change language"; the digests summarise those ranges. **No persisted
     section store.**
   - **C. C-2 first** — build and persist a structured
     `filing_sections` representation (at ingest or via backfill), then C-1
     consumes it. (This is the C-2 milestone, not M14.)
   - **D. Hybrid of A and B** — B for large filings, A for small filings
     (below a chunk-count threshold), with retrieval (OAQ-3) as the
     large-filing selector.
5. **Evaluation criteria.** Digest quality (does "Risk Factors Digest"
   actually cover the risk factors?); additivity (no schema change, no
   ingest change); latency/cost on large filings; robustness on
   non-EDGAR filings; contract compliance (grounded, cited, honest
   `insufficient_evidence`); reversibility (can be swapped for C-2 later
   without contract change).
6. **Trade-offs.** A is simplest and most robust to filing shape but is
   cost/latency-prohibitive on 2,000-chunk filings and dilutes the model's
   focus. B is additive and section-aware but its *quality* on real filings
   is **not knowable from static evidence** — heuristic + light-LLM section
   location may misclassify, especially on BSE/text filings. C is the
   highest-quality path but is a separate milestone and a schema change,
   and re-sequences the roadmap. D bounds cost while keeping quality on
   small filings.
7. **Recommended decision — CONDITIONAL (status: CONDITIONAL DECISION +
   IMPLEMENTATION VALIDATION GATE, §1.1).** Adopt **D: hybrid** — analysis
   operates over the **existing unstructured chunks**; section location is
   performed **at analysis time** (Alternative B mechanism) for filings
   above a chunk-count threshold (an operational config value, §10 / §19 —
   not a Document 64 contract term), and a whole-filing pass (Alternative A)
   is used below it. **C-2 is NOT adopted as an M14 deliverable and is NOT a
   proven hard technical prerequisite** — and this conclusion is **not**
   converted here into an unconditional claim: it is **conditional on the
   §20.1 implementation-phase STOP/CONTINUE validation gate**. If that gate
   **fails**, implementation **STOPS at the gate**; the engineer does **not**
   redesign the architecture, does **not** implement C-2, and does **not**
   touch Document 63 — a **separate CTO governance decision** (§20.1)
   determines whether C-2 is inserted/re-sequenced or another architecture
   path is taken. **The failure path is not pre-authorization of C-2.**
8. **Rationale.** It is the only path that is additive (no schema change,
   no ingest change), section-aware, contract-compliant, and reversible.
   The unresolved risk (section-location quality) is isolated behind an
   explicit gate rather than assumed away. Filing Summary and Important
   Changes are less section-dependent (they draw on whole-filing narrative
   / self-described change language) and are robust under D regardless.
9. **Operational consequences.** Digest outputs on filings where section
   location is weak will frequently and *correctly* return `partial` or
   `insufficient_evidence` (Document 64 §11.6/§11.7) rather than a
   fabricated digest — this is contract-compliant behaviour, and must be
   communicated as expected for non-EDGAR / poorly-structured filings.
   Whole-filing passes on small filings are cheap; large filings incur the
   retrieval + map-reduce cost (OAQ-10).
10. **Implementation implications.** A section-classification step
    (heuristic + optional `chat_json` light-model call) over chunk text; a
    threshold config value; no change to `filing_chunks` rows. The section
    labels are **in-request only**, not written back.
11. **Rejected alternatives.** **A alone** — cost/latency on large filings,
    weak focus. **C (C-2 first) as the M14 architecture** — it is a
    different milestone, a schema change, and a roadmap re-sequencing;
    adopting it here would silently change Document 63's selection and
    exceed this pack's authority. **Persisting the analysis-time section
    labels** — that *is* C-2 by another name and pulls a schema-governance
    dependency M14 does not need.
12. **New governance dependency.** None for D itself (additive, in-request).
    **Conditional:** if the §20 gate fails, a **separate CTO roadmap
    re-sequencing decision** (C-2 before C-1) — not made here, not a
    rewrite of Document 63.

---

### OAQ-2 — C-2 sequencing

1. **Question.** Must C-2 Structured Filing Extraction precede C-1, or can
   C-1 proceed without it?
2. **Context.** Document 62 §7 and Document 63 §6 left this OPEN; Document
   64 §16 keeps C-2 *neither selected nor rejected* and permits the
   architecture phase to conclude "C-2 first" — which would re-order the
   roadmap as a **separate** governance decision. The technical crux is
   OAQ-1: whether analysis-time section location over unstructured chunks
   meets the quality bar for the two digest outputs.
3. **Contract constraints.** Document 64 §16: this pack must **not** decide
   C-2 in a way that rewrites Document 63, must **not** implement C-2, must
   **not** change M14 selection. If re-sequencing is needed it is a
   separate governance decision. INV-IC and the four-output roster are
   fixed regardless.
4. **Candidate alternatives.**
   - **A. C-1 proceeds now** on the OAQ-1(D) hybrid; C-2 remains a future,
     independent roadmap item.
   - **B. C-2 first** — sequence C-2 as the next milestone; C-1 follows.
   - **C. Conditional** — C-1 proceeds now, with an explicit early gate; if
     the gate fails, escalate to a re-sequencing decision.
5. **Evaluation criteria.** Whether static + M13 evidence *proves* C-1
   cannot meet the contract without C-2 (it does not); time-to-value;
   reversibility; governance cleanliness (no silent Document 63 change).
6. **Trade-offs.** A risks shipping weak digests if section location is
   poor. B delays all M14 value for a milestone that may not be strictly
   necessary and is itself unspecified. C ships value early, isolates the
   risk, and keeps re-sequencing as a clean, explicit, separate governance
   act.
7. **Recommended decision.** **C — Conditional (status: CONDITIONAL
   DECISION + IMPLEMENTATION VALIDATION GATE, §1.1). C-2 is NOT a proven
   hard technical prerequisite for C-1** — this conclusion stands and is
   **not** softened, but it is **not** an unconditional claim: it holds
   *conditional on the §20.1 STOP/CONTINUE gate*. M14 proceeds on the
   OAQ-1(D) architecture **subject to** that gate. If the gate **fails**,
   implementation **STOPS**; the engineer does **not** redesign, does
   **not** implement C-2, does **not** rewrite Document 63; a **separate CTO
   governance decision** (§20.1) determines whether C-2 is
   inserted/re-sequenced or another architecture path is chosen. **This
   failure path does not pre-authorize C-2.** This pack neither makes that
   decision nor pre-empts it.
8. **Rationale.** The available evidence (M13 chunk shape, `chunk_text`
   behaviour, SEC Item conventions) is sufficient to design a plausible
   section-location mechanism but **not** sufficient to *prove* it meets a
   quality bar — that is an empirical question. Declaring "C-2 required"
   would invent certainty; declaring "C-2 never needed" would also. The
   honest position is "not required as a blocker, gated, escalation path
   defined."
9. **Operational consequences.** The §20 gate is a real deliverable of the
   implementation phase (a spike + a go/no-go). If invoked, M14 pauses
   pending the re-sequencing decision; no C-2 work happens without its own
   selection.
10. **Implementation implications.** The first implementation task after
    authorization is the section-location spike + quality assessment,
    *before* wiring the full four-output flow.
11. **Rejected alternatives.** **B (C-2 first)** — not evidence-supported as
    necessary; delays value; would re-order the roadmap without a
    demonstrated need. **A (proceed unconditionally)** — hides a real,
    unquantified quality risk.
12. **New governance dependency.** A **potential** separate CTO roadmap
    re-sequencing decision, invoked only if the §20 gate fails. **Recorded,
    not triggered.** Document 63 is not modified.

---

### OAQ-3 — Retrieval / RAG

1. **Question.** Is retrieval introduced into this new filing-scoped
   surface, or does analysis run whole-filing over ordered chunks? Which
   retrieval algorithm, if any?
2. **Context.** The report pipeline's hybrid retriever is **ticker-scoped**
   and consumed only by the `retriever` node (§5.1). M14 is **filing-local**
   (one `doc_id`). Large filings (~2,000 chunks, ~200 KB) exceed a
   comfortable single-prompt budget for four outputs.
3. **Contract constraints.** Document 64 §6: no new embedding pipeline, no
   reranker redesign, no ingestion-time embedding change; whether/how
   retrieval is used is OAQ-3. §7: evidence source is *this filing's own*
   chunks only; no cross-filing retrieval. §11: anchors must resolve to
   present `chunk_idx` ranges of this filing.
4. **Candidate alternatives.**
   - **A. No retrieval** — whole-filing pass for every output (see
     OAQ-1/A).
   - **B. Filing-scoped reuse of the existing hybrid scorer** — add a
     `doc_id` filter to `retrieve()` (or a thin filing-scoped wrapper) so
     BM25 + dense (cached vectors) + rerank select the top-K candidate
     chunks *within one filing* for each named section query.
   - **C. New filing-scoped retriever** — a purpose-built vector index /
     store for M14.
   - **D. Deterministic heuristic selection only** — regex/heading match
     for "risk factors" / "management's discussion" headings, no scoring
     model.
5. **Evaluation criteria.** Reuse vs new infrastructure; cost/latency on
   large filings; recall of the right chunks per section; determinism
   (§12); additivity; graceful degradation offline.
6. **Trade-offs.** A is simplest but unbounded cost. B reuses proven,
   already-loaded models and cached embeddings; its scoring is
   non-deterministic at the margins but bounded and reproducible enough
   given a fixed candidate set. C is net-new infrastructure the contract
   forbids as an M14 deliverable. D is deterministic but brittle on
   non-standard filings.
7. **Recommended decision.** **A + B hybrid, threshold-gated (see OAQ-10).**
   For filings at or below the chunk-count threshold → **A (no retrieval,
   whole-filing pass)**. Above it → **B (filing-scoped reuse of the
   existing hybrid scorer)**: add an optional `doc_id` filter to the
   existing `retrieve()` path (an additive extension of an existing
   component — no new embedding model, no new reranker, no new store), used
   to select top-K candidate chunks per named section. D's heading
   heuristics feed B as a pre-filter for the digest sections.
8. **Rationale.** It bounds LLM input regardless of filing size, reuses
   models already loaded for the report pipeline (zero new dependency),
   preserves offline degradation (BM25-only), and keeps the report
   pipeline's retriever behaviour untouched (the `doc_id` filter is opt-in).
9. **Operational consequences.** First M14 analysis of a large filing whose
   chunks lack cached embeddings triggers on-the-fly embedding (already the
   existing fallback in `retrieve()`), a one-time cost. Retrieval adds a
   bounded per-output latency component. Offline / model-load-failure →
   BM25-only selection, still contract-compliant.
10. **Implementation implications.** An additive `doc_id` (and optional
    `chunk_idx` window) parameter on the retrieval path; a per-section query
    string set (fixed, versioned — part of the prompt/version scheme, AH);
    a threshold config. No change to report-pipeline callers.
11. **Rejected alternatives.** **C (new retriever/store)** — forbidden as an
    M14 deliverable; unnecessary given B. **D alone** — brittle on
    non-EDGAR filings; would raise the `insufficient_evidence` rate beyond
    what B achieves. **A alone** — unbounded cost on large filings.
12. **New governance dependency.** If B's ordered filing-scoped reads
    warrant the **`{doc_id:1, chunk_idx:1}` compound index** (Document 59
    OD-4), that index is introduced via `08` + ADR at architecture
    ratification (AC-4). No other dependency.

---

### OAQ-4 — Endpoint form (execution topology at the API boundary)

1. **Question.** Synchronous single response vs async job + status +
   optional SSE + cancel; exact route family / path segment; is a new
   `JobKind` added?
2. **Context.** Every existing AI-generating surface (Research, Learning,
   Comparison-Explanation) is async job + status + optional SSE + cancel.
   M14 produces four outputs, each with section location + retrieval + a
   heavy-model summarise-and-cite call + anchor validation → realistically
   tens of seconds to a few minutes.
3. **Contract constraints.** Document 64 §9 marks the endpoint form
   `[architecture-dependent → OAQ-4]` and permits sync *or* async. §9.2:
   `current_user`; BYOK field set verbatim; **no output-selection
   parameter**. §9.3: response carries the four outputs + per-output flat
   cited narrative + state; `_id`/`embedding` never returned. §10: reuse the
   existing error envelope + taxonomy with zero additions. AC-5/AC-10:
   additive routes only; route-count contract updated only under
   implementation authorization.
4. **Candidate alternatives.**
   - **A. Synchronous** — `GET /companies/{ticker}/filings/{doc_id}/analysis`
     computes and returns all four outputs in one response.
   - **B. Async job family (mirror M9.1)** — `POST …/analysis` (create/reuse
     job → `{id, status, reused}`), `GET …/analysis/{id}` (status; result
     when completed), `GET …/analysis/{id}/stream` (SSE), `POST
     …/analysis/{id}/cancel`. New `JobKind.FILING_ANALYSIS`.
   - **C. Async without SSE** — `POST` + `GET` polling only.
5. **Evaluation criteria.** Latency vs HTTP timeout risk; alignment with
   the frozen `FilingViewer` "AI Thinking / Streaming" states; reuse of
   `JobLifecycle` / `sse_response` / `MAX_ACTIVE_JOBS`; cancellation;
   consistency with M9.1.
6. **Trade-offs.** A is simplest but a minutes-long synchronous request is
   fragile (proxy/load-balancer timeouts) and gives no progress signal for
   the `FilingViewer` streaming states. B is the established pattern, gets
   admission control / cancel / deadline / SSE for free, and matches the
   frontend spec — at the cost of one new `JobKind` and four new routes. C
   loses the streaming UX the component spec calls for.
7. **Recommended decision.** **B — async job + status + optional SSE +
   cancel, 4-route family, mirroring Comparison-Explanation (Document 43
   §5).** Route family:
   `POST   /api/companies/{ticker}/filings/{doc_id}/analysis`,
   `GET    /api/companies/{ticker}/filings/{doc_id}/analysis/{id}`,
   `GET    /api/companies/{ticker}/filings/{doc_id}/analysis/{id}/stream`,
   `POST   /api/companies/{ticker}/filings/{doc_id}/analysis/{id}/cancel`.
   Add exactly one `JobKind.FILING_ANALYSIS` member. Add one
   `job_deadline_filing_analysis_s` setting (recommend `180`).
8. **Rationale.** Reuses `JobLifecycle` (shared `MAX_ACTIVE_JOBS`
   admission), `sse_response` framing, `JobStatus` verbatim, the M9.1
   two-collection job pattern, and the frozen `TraceEvent` shape. Matches
   the `FilingViewer` "Filing analysis" streaming states. Keeps the
   response shape exactly Document 64 §9.3.
9. **Operational consequences.** M14 jobs share the one `MAX_ACTIVE_JOBS`
   budget with Research/Learning/Comparison-Explanation — a burst of M14
   analyses can starve report generation and vice versa; the shared budget
   is the accepted design (03 / Document 43 §3). A `deadline_exceeded`-style
   outcome signal is needed for tuning `180s` (§18).
10. **Implementation implications.** New route handlers; `JobKind` enum
    member; deadline setting; `APPROVED_ROUTES` gains 4 entries and the
    exact-set count test is updated (AC-10 / AH-9 — under implementation
    authorization, not here).
11. **Rejected alternatives.** **A (synchronous)** — timeout-fragile at M14
    latencies; no progress signal for the frozen streaming UX. **C (no
    SSE)** — the `FilingViewer` spec explicitly has `AI Thinking /
    Streaming` states.
12. **New governance dependency.** `JobKind.FILING_ANALYSIS` + four
    `APPROVED_ROUTES` entries + the route-count contract-test update — done
    under **implementation authorization** (AH-9), not pre-authorized by
    Document 64. `job_deadline_filing_analysis_s` is configuration, set at
    implementation. No schema dependency from OAQ-4 itself (see OAQ-5).

---

### OAQ-5 — Persistence model

1. **Question.** Is analysis output persisted at all? If so, in what
   representation and where — a new field, a new collection, on-demand only?
2. **Context.** A filing is immutable after ingest (re-ingest mints a new
   `doc_id`), so an analysis for a fixed `(doc_id, prompt-version,
   schema-version, provider, model)` is durably valid — it can never go
   stale for that `doc_id` (unlike M9.1's partial-result staleness, which
   arose because compared *reports* could still be generating). M14 analysis
   is expensive (§OAQ-10). Comparison-Explanation persists its artifact in a
   dedicated collection + a job-mirror collection with TTL.
3. **Contract constraints.** Document 64 §6 / §6.1 / §19.1 OAQ-5: **no new
   MongoDB collection / index / schema / migration is authorized or
   pre-approved by the contract**; whether persistence is needed and by what
   mechanism is OAQ-5, *genuinely open*; a design needing a new collection
   is introduced via **architecture ratification + `08` / ADR schema-change
   governance**, never as pre-authorized. §12: reproducibility via identity
   + reuse is the *recommended* model **if** persistence is adopted;
   on-demand with no persistence is *also permitted*.
4. **Candidate alternatives.**
   - **A. Persist — two collections (mirror M9.1).** `filing_analyses`
     (durable artifact, unique index on an **analysis identity key** =
     `doc_id` + `prompt_version` + `output_schema_version` + `provider` +
     `model`; no TTL) + `filing_analysis_jobs` (job mirror; partial unique
     index on `active_identity_key`; 30-day TTL). `reused: true` on
     identity match.
   - **B. Persist — one field / one collection minimal.** Store only the
     final artifact document, no job-mirror collection (job state stays in
     the existing `JobStore` / Redis).
   - **C. On-demand, no persistence.** Recompute on every request; contract
     only requires grounded + cited (§12).
   - **D. Redis short-TTL result cache.** No new Mongo collection; a
     bounded-TTL cache of the last-N analyses.
5. **Evaluation criteria.** Cost of recompute vs storage; dedup/`reused`
   semantics (Document 64 §12); durability correctness (safe because the
   filing is immutable); governance weight (new collection = schema
   governance); consistency with M9.1; restart-safety of in-flight jobs.
6. **Trade-offs.** A gives the strongest dedup + durability + M9.1
   consistency + restart-safe job records, at the cost of **two new
   collections + ~3 new indexes → a schema-governance dependency**. B is
   lighter (one collection) but loses durable job records (no crash-restart
   sweep for M14 jobs — acceptable, matching Research today). C avoids all
   schema governance but pays full recompute cost every time a user
   re-opens the same filing's analysis — wasteful given immutability. D
   avoids Mongo governance but is a cache (bounded, evictable), not a
   durable artifact, and reintroduces a Redis dependency the report path
   only optionally has.
7. **Recommended decision — split into two distinct things (status:
   PROPOSAL-TIME RECOMMENDATION for the logical decision; EXTERNAL
   GOVERNANCE DEPENDENCY for the realization, §1.1 / §12.1).**
   - **Architecture decision (this pack's recommendation):** **durable
     persistence is the recommended M14 architecture** — a durable analysis
     artifact keyed by an analysis identity, plus a job mirror, using the
     M9.1 two-collection *logical* pattern (**A**).
   - **Schema / data-governance authority (NOT this pack's to grant):** the
     **exact MongoDB collection and index realization** — collection names,
     index specs, canonical data-architecture placement, any migration,
     and any production deployment of a schema change — **remains subject to
     the existing `08_MongoDB_Data_Architecture.md` + ADR governance
     chain.** Architecture ratification of *this* pack records the *logical*
     persistence decision only and does **not** authorize creating or
     modifying any collection or index (§12.1).
   - **Fallbacks (preserved), selected only if the schema-governance chain
     withholds approval:** **B** — a single durable artifact collection
     (job state stays in the existing `JobStore`); **D** — no new Mongo
     collection at all → a bounded Redis short-TTL result cache, `reused`
     best-effort; **C** — no persistence (recompute per request;
     contract-legal, wasteful) as the last resort. None of B/D/C is removed
     by this revision.
8. **Rationale.** The filing's immutability makes a persisted analysis
   *unconditionally* reusable for its identity key — the strongest possible
   dedup case, and materially cheaper than recompute. A matches the M9.1
   architecture the whole team already understands, and gives restart-safe
   job records. The schema-governance dependency is real and named, not
   hidden.
9. **Operational consequences.** Storage grows ~one artifact per distinct
   `(doc_id, prompt/schema/provider/model)` tuple — bounded and small
   (four short narratives + anchor lists per filing). A prompt-version or
   schema-version bump invalidates prior artifacts implicitly (new identity
   key) — no migration, old rows age out only if a TTL is added (not
   recommended for the durable collection; recommended for the job mirror).
10. **Implementation implications.** Two `create_index` calls added to
    `ensure_indexes` (`filing_analyses.analysis_identity_key` unique;
    `filing_analysis_jobs.active_identity_key` partial-unique +
    `created_at` TTL) — **only** after `08` + ADR approval. Job-run flow
    mirrors `_run_comparison_explanation`: read-before-generate,
    `insert_one` + `DuplicateKeyError` adopt-or-replace.
11. **Rejected alternatives.** **C (no persistence) as the primary
    design** — wasteful given immutability; weak `reused` semantics. **A
    new field on `filings`** — mixes an AI artifact into the immutable
    ingest record (`08` RI-2 "immutable historical record"); rejected.
    **Persisting into `reports`** — different domain, different lifecycle;
    rejected.
12. **New governance dependency — YES, explicit.** Two new MongoDB
    collections (`filing_analyses`, `filing_analysis_jobs`) + their indexes.
    **Introduced only via `08_MongoDB_Data_Architecture.md` + the ADR
    chain, as part of CTO architecture ratification.** Document 64
    pre-approves none of it (§6.1). The §24 ratification gate lists this as
    a required approval.

---

### OAQ-6 — Caching / Redis

1. **Question.** Any response / artifact caching? Any Redis usage beyond the
   existing job/event machinery?
2. **Context.** Redis in this repo backs the job store, event bus, SSE
   replay, and rate limiter; `JOB_BACKEND=memory` is the default and Redis
   is optional. The report path adds no response cache.
3. **Contract constraints.** Document 64 §13: "No caching / no Redis. …
   this contract adds none." §19.1 OAQ-6: caching/Redis is genuinely open,
   on the same terms as OAQ-5 (not authorized, not pre-approved, not
   foreclosed).
4. **Candidate alternatives.** A. No new cache (rely on OAQ-5 persistence).
   B. Redis result cache with TTL. C. In-process LRU cache.
5. **Evaluation criteria.** Necessity given OAQ-5; new dependency weight;
   correctness (staleness is a non-issue — filings are immutable);
   multi-instance behaviour.
6. **Trade-offs.** A adds nothing and is sufficient *if* OAQ-5(A/B) is
   approved. B is only needed as OAQ-5's fallback and reintroduces a Redis
   dependency the report path treats as optional. C is instance-local and
   lost on restart.
7. **Recommended decision.** **A — no new caching layer and no new Redis
   usage for M14.** M14's async job model *reuses* the existing
   `JobStore` / `EventBus` (job state + SSE), which is job infrastructure,
   not a cache. The "don't recompute" benefit comes from OAQ-5 persistence.
   **Fallback:** only if *no* new Mongo collection is approved (OAQ-5(D))
   does a bounded Redis short-TTL result cache enter scope — as a separate,
   explicitly-flagged architecture decision, not adopted here.
8. **Rationale.** Caching would be redundant with OAQ-5(A/B) and premature
   (Document 64 §13; the "don't build ahead of evidence" discipline). The
   existing job/SSE Redis use is not new.
9. **Operational consequences.** None new. M14 works with
   `JOB_BACKEND=memory` exactly as Research does.
10. **Implementation implications.** None (no cache code).
11. **Rejected alternatives.** **B / C** — unnecessary given OAQ-5; add a
    dependency for a payload that does not need it.
12. **New governance dependency.** None (recommended path). The fallback
    Redis cache, if ever invoked, is a separate architecture decision under
    the same "no pre-authorization" rule.

---

### OAQ-7 — LangGraph topology

1. **Question.** A new scoped graph, a new node in the frozen `research`
   graph, or out-of-graph orchestration reusing the synthesizer /
   fact-checker *pattern*?
2. **Context.** `07` is 🔒 v1.0 frozen. **G-1**: node names are a
   frontend-coupled API contract. **LG-1**: a distinct capability with
   different UI stages gets its **own** graph, not a parameterized one.
   **M9.1 (Comparison-Explanation) chose out-of-graph** — Document 43 §16
   explicitly rejected a graph-shaped tracing label for a nodeless
   capability. M14's flow is a fixed pipeline (section-locate → per-output:
   select chunks → summarise+cite → validate anchors → set state) with no
   conditional routing that benefits from a graph state machine.
3. **Contract constraints.** Document 64 §6: no LangGraph topology change is
   an M14 deliverable; any change the architecture proposes against frozen
   `07` v1.0 is a **stop-and-CR item** (§16; Document 62 R-9). §19.1 OAQ-7:
   genuinely open.
4. **Candidate alternatives.**
   - **A. Out-of-graph orchestration** (mirror M9.1) — a plain async
     function with its own `pipeline.filing_analysis` tracing span; per-step
     `TraceEvent`s published through `JobLifecycle.publish` / SSE.
   - **B. New dedicated M14 LangGraph** — e.g. `sectioner → analyzer(×4) →
     validator`, its own compiled graph (LG-1 style).
   - **C. New node(s) in the frozen `research` graph** — parameterized by a
     `mode`.
5. **Evaluation criteria.** Does M14 need graph semantics (conditional
   routing, retry loops, fan-in reducers)? G-1 / frontend-sign-off cost;
   `07` stop-and-CR cost; consistency with M9.1; testability.
6. **Trade-offs.** A needs no `07` change, no new graph vocabulary, and
   matches the M9.1 precedent; it forgoes LangGraph's built-in
   node-boundary deadline checks (M14 must do its own deadline checks — a
   small, explicit cost). B gives graph structure M14 does not currently
   need and triggers LG-1 + a new G-1 node set + frontend sign-off. C
   violates LG-1 (reintroduces `mode` coupling) and is a stop-and-CR
   against the frozen graph.
7. **Recommended decision.** **A — out-of-graph orchestration. No change to
   the `research` graph, no new LangGraph, no `07` topology change.** M14
   Filing Analysis is a plain async orchestration function with its own
   `pipeline.filing_analysis` OTel span, publishing progress `TraceEvent`s
   via the existing `JobLifecycle` / `sse_response` path.
8. **Rationale.** M14's flow is deterministic and linear — no conditional
   edges, no retry-loop routing, no parallel-branch state-merge. LangGraph's
   value (LG-1's justification) is a *cross-team UI stage contract for a
   multi-node conditional flow*; M14 does not have that shape. M9.1 already
   established that a bounded grounded/cited LLM capability lives
   out-of-graph. This keeps `07` v1.0 untouched.
9. **Operational consequences.** M14 owns its own wall-clock deadline check
   (mirroring `_run_comparison_explanation`'s explicit `is_past_deadline`
   check) rather than getting LG-11's node-boundary checks for free. Per-run
   tracing is a single `pipeline.filing_analysis` span with child spans per
   LLM call (the `llm.attempt` spans come for free from `chat_text`).
10. **Implementation implications.** An orchestration function; a fixed set
    of progress event `node` labels (e.g. `pipeline`, `sectioning`,
    `analyzing`, `validating`, `final`) — these become a **G-1-style
    cross-team contract** for the `FilingViewer` streaming states and need
    frontend registration (frontend is out of M14 backend scope — AH-6).
11. **Rejected alternatives.** **B (new graph)** — no current need for graph
    semantics; triggers LG-1 + new G-1 vocabulary + `07` change +
    frontend-sign-off overhead for zero functional gain. **C (node in
    `research` graph)** — violates LG-1; stop-and-CR against a frozen graph;
    couples M14 stages into a state the report UI has no stage for.
12. **New governance dependency.** **None against `07`** (no topology
    change). A **new SSE `node` vocabulary** for M14 is a G-1-style
    cross-team contract requiring frontend sign-off — recorded as an
    architecture-handoff item, not a `07` amendment. If a future need for
    graph semantics emerges (e.g. a per-output fact-check/retry loop), that
    is a **stop-and-CR item against `07`** and a separate governance
    decision — flagged, not taken.

---

### OAQ-8 — Model / provider selection

1. **Question.** Default provider / model / tier for the analysis pass,
   beyond the existing BYOK passthrough.
2. **Context.** `agents/llm.py` provides symbolic `DEFAULT_LIGHT_MODEL` /
   `DEFAULT_HEAVY_MODEL` tiers resolved per provider; gemini is the env
   default; BYOK fields (`llm_provider` / `llm_api_key` / `llm_base_url` /
   `llm_model`) thread through `set_llm_context`. `chat_json` enforces
   structured output against a Pydantic schema.
3. **Contract constraints.** Document 64 §6: LLM access stays through
   `agents/llm.py`; no new provider, no new provider dependency; selecting
   the M14 default *among already-supported providers/models* is OAQ-8, not
   a redesign. §12: stable output schema per version; low run-to-run
   variance is desirable but bit-identical output is not required. §15: BYOK
   inherits the existing policy verbatim (SSRF guard, `require_admin` for
   custom).
4. **Candidate alternatives.** A. Heavy tier for all four output
   generations + light tier for section classification. B. Light tier
   throughout (cheaper, weaker grounding). C. Heavy tier throughout
   (including classification). D. A fixed concrete model (e.g. a specific
   Gemini/Anthropic model) rather than the symbolic tier.
5. **Evaluation criteria.** Grounding/citation quality vs cost; structured-
   output reliability; determinism; provider-agnosticism; BYOK
   compatibility.
6. **Trade-offs.** A balances quality (heavy for the summarise-and-cite
   work that must stay grounded) against cost (light for the mechanical
   section-classification pass). B is cheapest but risks weaker grounding
   and more `insufficient_evidence` / citation-validation failures. C
   over-pays for classification. D breaks provider-agnosticism and BYOK.
7. **Recommended decision.** **A — reuse the existing tier abstraction
   verbatim.** The four **output generations** use `DEFAULT_HEAVY_MODEL`;
   the **section-classification** pass (OAQ-1) uses `DEFAULT_LIGHT_MODEL`.
   **BYOK passthrough exactly as Research / Learning / Comparison-
   Explanation** (`set_llm_context` from the request BYOK fields). **No new
   provider, no default-provider change** (gemini stays the env default).
   Structured output enforced via `chat_json` against a Pydantic schema per
   output. `temperature` set low (favouring determinism per Document 64
   §12) — the exact value is an implementation tuning knob, not frozen here.
8. **Rationale.** Zero new dependency (Document 64 §6 compliant); heavy tier
   where grounding fidelity matters; light tier where the task is
   mechanical; BYOK preserved so a user's key/provider/model choice governs
   M14 exactly as it governs Research.
9. **Operational consequences.** M14 cost per analysis ≈ 1 light call
   (classification, large filings) + up to ~4–8 heavy calls (four outputs,
   possibly map-reduce on large filings — OAQ-10). Comparable to a Research
   report run (up to 6 heavy calls). Provider rate limits / quota are the
   user's (BYOK) or the operator's (env key), same as today.
10. **Implementation implications.** `chat_json` calls with per-output
    Pydantic schemas; `set_llm_context` / `reset_llm_context` around the
    run (mirroring `_run_comparison_explanation`); no change to
    `agents/llm.py`.
11. **Rejected alternatives.** **B (light throughout)** — grounding risk.
    **C (heavy throughout)** — wasteful for classification. **D (fixed
    model)** — breaks provider-agnosticism, BYOK, and the "no provider
    redesign" constraint.
12. **New governance dependency.** None (selection among already-supported
    providers/models — Document 64 §6.1 explicitly not a redesign or new
    dependency).

---

### OAQ-9 — Chunk-range → claim (anchor-discovery) mechanism

1. **Question.** How does the system *discover* the `{doc_id, chunk_start,
   chunk_end}` anchor backing each substantive factual claim, given the
   **representation** is frozen by Document 64 §11.3?
2. **Context.** Document 64 §11.3 froze the wire representation and the
   `[n]` / `sources[]` / `cited_source_indices` shape (reused from
   `learning_nodes._postprocess_citations`), and §11.9 explicitly left the
   *discovery mechanism* to architecture. The candidate evidence per output
   comes from OAQ-1 (section location) + OAQ-3 (retrieval / whole-filing
   selection).
3. **Contract constraints.** Document 64 §11.2 (every substantive factual
   claim → ≥1 filing-local anchor), §11.3 (representation floor —
   contiguous, present `chunk_idx`, `start ≤ end`), §11.4 (a citation may
   back multiple claims; no orphan `cited_source_indices`), §11.5
   (contiguity; non-adjacent evidence → multiple citations), §11.6 / §11.7
   (`insufficient_evidence` / `partial` when a claim cannot be grounded),
   §11.8 (anchors reference present well-formed ranges only; no fabrication
   over ingest gaps). §11.9: the mechanism is **not** frozen.
4. **Candidate alternatives.**
   - **A. Numbered-candidate + post-process (mirror `learning_nodes`).**
     Give the model, per output, a numbered list of candidate chunks (each
     with its `chunk_idx` and text); prompt it to attach `[n]` markers to
     every substantive claim; a **deterministic post-processor** maps each
     `[n]` → the candidate's `chunk_idx`, coalesces adjacent cited chunks
     into contiguous `{chunk_start, chunk_end}` ranges, drops out-of-range /
     hallucinated markers, enforces §11.4/§11.5, and demotes any
     ungrounded substantive claim (drop + record boundary, or → `partial` /
     `insufficient_evidence`).
   - **B. Embedding-similarity attribution.** After the model writes the
     narrative, embed each sentence and match to the highest-similarity
     chunk(s) to synthesise anchors.
   - **C. Structured-output anchors.** Require the model to emit, per claim,
     an explicit `{chunk_start, chunk_end}` object via `chat_json`.
   - **D. LLM self-report of ranges + LLM verifier.** The model names
     ranges; a second LLM pass verifies each.
5. **Evaluation criteria.** Determinism and testability of validation;
   fidelity (does the anchor actually support the claim?); reuse of the
   proven `learning_nodes` pattern; robustness to model hallucination;
   cost.
6. **Trade-offs.** A's *validation* step is fully deterministic and
   unit-testable (marker in range? contiguous? present? cited-index set
   consistent?), and reuses shipped code; its weakness is that a marker in
   range does not *prove* the chunk supports the claim (the prompt +
   candidate curation carry that burden). B is post-hoc and fuzzy —
   similarity ≠ support — and non-deterministic. C is clean but weaker
   models routinely mis-emit nested structured anchors (see `chat_json`'s
   recovery heuristics), and it still needs A's validation on top. D
   doubles LLM cost and adds a non-deterministic verifier.
7. **Recommended decision.** **A — numbered-candidate generation +
   deterministic post-processing validation.** Per output: (i) the
   candidate chunk set (from OAQ-1/OAQ-3) is presented to the model as a
   numbered list carrying `chunk_idx`; (ii) the model emits `narrative` with
   `[n]` markers on every substantive factual claim; (iii) a deterministic
   validator resolves markers → `{doc_id, chunk_start, chunk_end}` anchors,
   coalesces adjacency, enforces §11.3–§11.5, builds `sources[]` and
   `cited_source_indices`, and applies §11.6/§11.7 state rules for any
   substantive claim left unmarked or with an unresolvable marker.
8. **Rationale.** The **observable** result is exactly Document 64's frozen
   representation; the **validation** is deterministic and testable
   (satisfying §24's "citation architecture satisfies the contract" gate);
   the pattern is already shipped and understood
   (`_postprocess_citations`); it degrades honestly (ungrounded claim →
   dropped / `partial` / `insufficient_evidence`, never fabricated).
9. **Operational consequences.** Prompt quality and candidate-set curation
   are the levers for *fidelity*; the validator guarantees *structural*
   correctness unconditionally. A high rate of dropped markers on a given
   filing surfaces as `partial` / `insufficient_evidence` — a visible
   signal, not a silent failure (§18 observability).
10. **Implementation implications.** A candidate-numbering step; a
    deterministic validator module (marker resolution, adjacency
    coalescing, range-presence check against the filing's `chunk_idx` set,
    orphan-index check); per-output state assignment. No new data.
11. **Rejected alternatives.** **B (similarity attribution)** — fuzzy,
    non-deterministic, "similar" ≠ "supports". **C (structured anchors from
    the model)** — unreliable on weaker models; still needs A's validator.
    **D (LLM verifier)** — 2× cost, non-deterministic, no clear gain over A
    for structural correctness.
12. **New governance dependency.** None (uses existing chunk data + the
    existing citation-post-process pattern). OAQ-9 remains *architecture*,
    not contract — Document 64 §11.9 is satisfied without amending it.

---

### OAQ-10 — Whole-filing vs scoped cost strategy

1. **Question.** For large filings (~2,000 chunks), does M14 run a single
   pass, a map-reduce over chunk windows, or a retrieval-scoped pass?
2. **Context.** `char_count ≤ ~200 000` (ingest truncation), ~100–2,000
   chunks. A single prompt containing 2,000 chunks × ~900 chars ≈ 1.8 MB of
   text ≈ far beyond a comfortable heavy-model context window, ×4 outputs.
3. **Contract constraints.** Document 64 §13: "a single whole-filing pass
   on a large filing may be costly … Whether to pass the whole filing or a
   retrieval-scoped subset is OAQ-3, not a performance decision made here."
   §12: analysis depends only on the filing + versioned prompt/schema/model.
   CQ-4 (latency expectation) is **not** a ratification pre-condition and is
   gated to implementation authorization (Document 64 §18, §20).
4. **Candidate alternatives.** A. Always whole-filing. B. Always
   retrieval-scoped. C. Threshold hybrid (whole-filing below N chunks;
   retrieval-scoped map-reduce above). D. Always map-reduce over fixed
   windows.
5. **Evaluation criteria.** Bounded LLM input regardless of filing size;
   quality on small filings (whole-filing is strictly better — full
   context); determinism; latency within the OAQ-4 deadline; cost.
6. **Trade-offs.** A blows the context window / cost on large filings. B
   under-serves small filings that would benefit from full context. C gets
   the best of both but needs a tuned threshold. D adds map-reduce overhead
   even for tiny filings.
7. **Recommended decision.** **C — threshold hybrid.** If the filing's
   chunk count ≤ a threshold (recommend ~120 chunks ≈ ~110 KB, comfortably
   within a heavy-model context window with headroom for prompt + four
   output schemas) → **whole-filing pass**, all chunks as the candidate set
   for every output. Above the threshold → **retrieval-scoped selection
   (OAQ-3/B) per named section, then a bounded summarise pass** (map-reduce
   only if the selected candidate set itself exceeds the budget). The
   threshold is an **operational config value**, set at implementation and
   tunable, **not frozen here**.
8. **Rationale.** Bounds per-output LLM input to a fixed budget for any
   filing; preserves full-context quality where it is affordable; keeps the
   worst-case call count (~1 light + ~4–8 heavy) comparable to a Research
   run; keeps latency inside a `180s` deadline (OAQ-4).
9. **Operational consequences.** Latency and cost scale with filing size
   only up to the threshold, then flatten. The threshold and the deadline
   are the two tuning knobs; `deadline_exceeded`-style outcomes (§18) are
   the tuning signal. CQ-4's product-level latency expectation must be set
   before implementation authorization (Document 64 §18) — this pack
   supplies the cost model that decision needs, not the number.
10. **Implementation implications.** A threshold config; a size check at the
    start of the run; two code paths (whole-filing / scoped) sharing the
    same summarise-and-cite + validate steps.
11. **Rejected alternatives.** **A** — unbounded. **B** — needlessly
    degrades small-filing quality. **D** — map-reduce overhead for filings
    that do not need it.
12. **New governance dependency.** None (config + code paths). Informs, but
    does not set, the CQ-4 latency expectation the CTO gates before
    implementation authorization.

---

## 8. Data / Filing Representation

**Decision.** M14 consumes the **existing `filing_chunks` representation
unchanged** — `{chunk_idx, text}` per chunk, `chunk_idx` ascending is the
authoritative order (Document 59 §6). No change to `chunk_text`, chunk size,
overlap, `filings`, or `filing_chunks` schema (AC-2).

- **Read path.** Reuse the M13 access shape (`filings.find_one({ticker,
  doc_id})` → 404 on miss; `filing_chunks.find({doc_id}, {_id:0,
  embedding:0}).sort("chunk_idx",1)` + Python re-sort). Whether this is
  reached via the M13 handler's logic, a shared internal helper, or a thin
  `doc_id`-scoped read port is an **implementation** choice bounded by
  Document 64 AH-2 ("no new read port unless justified") — not decided here.
- **Section identity** is derived **at analysis time** (OAQ-1) and is
  **not persisted** — deriving it does not modify `filing_chunks`.
- **Overlap.** The 120-char prepended overlap means adjacent chunk texts
  share a boundary tail; the anchor validator (OAQ-9) treats `chunk_idx`
  ranges as the unit of citation, so overlap is transparent to citations.
- **Chunk-vs-section strategy:** OAQ-1(D) — unstructured chunks + analysis-
  time section location; **C-2 not adopted, not a proven prerequisite,
  gated (§20).**
- **Implications for existing M13 data:** none. M14 reads it; M13's read
  endpoint and its data are untouched (AC-5). Re-ingested filings (new
  `doc_id`) are analysed independently per `doc_id`, consistent with the
  `(ticker, doc_id)` identity (C-8).

**Malformed / partial ingest (Document 64 §11.8 / §10).** M14 analyses the
present well-formed chunks (as the M13 handler already filters — `chunk_idx`
int + `text` str); every anchor must reference a present `chunk_idx` range;
an output whose grounding is materially affected → `partial` /
`insufficient_evidence` with the ingest limitation named; no fabrication.

---

## 9. Analysis & Retrieval Architecture

**Per-output flow (all four outputs, always produced — CQ-1/CQ-2):**

```text
resolve (ticker, doc_id) → 404 on miss                       [reuse M13 access]
load ordered chunks {chunk_idx, text}  (embedding projected out)
size check:  ≤ threshold → whole-filing candidate set        [OAQ-10]
             >  threshold → per-section retrieval selection   [OAQ-3/B, OAQ-1]
for each of the 4 outputs:
    candidate chunk set  ← whole-filing OR section-scoped selection
    chat_json(HEAVY, per-output schema, low temperature):
        narrative with [n] markers on every substantive factual claim   [OAQ-8, OAQ-9]
    deterministic validator:                                            [OAQ-9]
        resolve [n] → {doc_id, chunk_start, chunk_end}
        coalesce adjacency; enforce §11.3–§11.5
        build sources[] + cited_source_indices
        assign state: complete | partial | insufficient_evidence        [§11.6/§11.7]
assemble the 4-output response (flat cited narrative each)              [CQ-3]
```

- **Retrieval:** OAQ-3 — reuse the existing hybrid scorer with an additive
  `doc_id` filter for large filings; whole-filing for small. No new
  embedding model, no new store.
- **Determinism:** low `temperature`; fixed candidate ordering (by
  `chunk_idx`); a fixed, versioned per-section query set; the validator is
  fully deterministic. Run-to-run prose varies (permitted, §12); structure
  and anchors are stable given the same candidate set.
- **Context-window / cost:** bounded by the OAQ-10 threshold; worst case
  ~1 light + ~4–8 heavy `chat_*` calls per analysis.
- **`FilingViewer` "Filing analysis" variant** consumes this via SSE
  progress events + the completed artifact (frontend out of M14 backend
  scope — AH-6).

**Important Changes (INV-IC, C-7).** The candidate set for this output is
selected by matching **self-described change language within the filing**
("we have revised", "effective this quarter", "a new risk factor", "changed
from", …) — a fixed lexical/semantic cue set over *this filing's* chunks
only. **No previous filing is loaded, embedded, compared, or referenced.**
Absent such language → `insufficient_evidence` (§11.6). The architecture
makes cross-document comparison *structurally impossible* for this output:
the analysis function is given exactly one `doc_id`'s chunks and no other
input.

---

## 10. Citation / Evidence Architecture

**Frozen contract representation (Document 64 §8.2, §11.3 — not touched
here):**
- Per output: `narrative` (string, inline `[n]`), `sources[]` (indexed
  anchor list), `cited_source_indices` (referenced subset), `state`.
- Anchor floor: `{ doc_id, chunk_start, chunk_end }` — contiguous, both
  endpoints present in the filing's `chunk_idx` set, `chunk_start ≤
  chunk_end`.

**Architecture-owned anchor discovery + validation (OAQ-9 — A):**

| Stage | Mechanism | Determinism |
|---|---|---|
| Candidate curation | OAQ-1 section location + OAQ-3 selection produce a numbered candidate list per output, each entry carrying `chunk_idx` + text. | Deterministic given the filing (BM25/dense scoring is bounded; candidates re-sorted by `chunk_idx` before numbering). |
| Marker emission | `chat_json` HEAVY: the model attaches `[n]` to every substantive factual claim (§11.1 definition supplied in the prompt). | Non-deterministic prose; the *set* of grounded claims is what matters. |
| Marker resolution | Deterministic: `[n]` → candidate `chunk_idx`; adjacent cited `chunk_idx` coalesced into `{chunk_start, chunk_end}`; out-of-range / unknown `[n]` dropped (mirrors `_postprocess_citations`). | Fully deterministic. |
| Structural validation | `sources[]` indices 1-based unique; every `[n]` ⊆ `cited_source_indices` ⊆ `sources` indices (no orphans, §11.4); every anchor range contiguous and present (§11.3, §11.5, §11.8). | Fully deterministic, unit-testable. |
| State assignment | `complete` = every substantive claim marked + non-empty `cited_source_indices` + no boundary list. `partial` = some grounded, some dropped → enumerated coverage-boundary list. `insufficient_evidence` = no groundable substantive claim → no claims, empty citations, machine-readable reason. | Deterministic given the marker-resolution result. |

**What the architecture guarantees vs what the prompt carries.** The
validator *guarantees* structural correctness (representation, contiguity,
presence, orphan-free, state consistency) unconditionally. Semantic
*fidelity* (the cited chunk actually supports the claim) is carried by
(a) candidate curation quality and (b) prompt design (an AH item) — and any
residual gap surfaces honestly as `partial` / `insufficient_evidence`, never
as a fabricated pass.

**No cross-filing citations** — the analysis function receives one
`doc_id`'s chunks; an anchor to any other `doc_id` is structurally
impossible.

---

## 11. Execution / Orchestration Architecture

**Decision:** OAQ-7(A) — **out-of-graph async orchestration**, mirroring
`_run_comparison_explanation`.

- **No LangGraph.** A plain async function under a
  `pipeline.filing_analysis` OTel span. `07` v1.0 untouched.
- **Job model:** OAQ-4(B) — `JobLifecycle.start` (shared `MAX_ACTIVE_JOBS`
  admission), `mark_running`, per-step `publish` (SSE), `complete` / `fail`
  / `cancel`. New `JobKind.FILING_ANALYSIS`.
- **Progress `TraceEvent` `node` values (proposed, G-1-style cross-team
  contract):** `pipeline` (start / ok / error), `sectioning`, `analyzing`
  (per output — `message` names which), `validating`, `final`. Frontend
  registration is an AH item (frontend out of scope).
- **Timeout / deadline:** one wall-clock deadline
  (`job_deadline_filing_analysis_s`, recommend `180`), checked explicitly
  at step boundaries in the orchestration function (M14 does not get LG-11's
  automatic node-boundary checks — it does its own, as
  `_run_comparison_explanation` does). Past deadline → job `failed` with a
  generic message; any outputs already completed are **not** partially
  returned (a single terminal artifact — mirrors M9.1).
- **Cancellation:** `POST …/analysis/{id}/cancel` → owner-scoped (job
  record owner), idempotent on terminal (`JobLifecycle.cancel`). In-flight
  LLM calls: the same honest limitation as every other capability —
  `task.cancel()` stops the awaiting coroutine at the next `await`, not a
  running provider HTTP call inside `asyncio.to_thread` (Document 43 §13).
  Cancellation guarantees the result is not published / persisted.
- **Request lifecycle:** `POST` → admission + create-or-reuse job (identity
  dedup, OAQ-5) → `{id, status, reused}`; client polls `GET …/{id}` or
  opens `…/{id}/stream`; result present only when `status == "completed"`.
- **Concurrency:** shared `MAX_ACTIVE_JOBS` with Research / Learning /
  Comparison-Explanation (accepted design). No per-kind M14 limiter unless
  operationally evidenced later (Document 43 §23 pattern).
- **Restart safety:** if OAQ-5(A) is approved, `filing_analysis_jobs` gives
  durable job records for a crash-restart sweep; if OAQ-5(B/D), M14 jobs
  are Redis/in-memory only and a crash loses in-flight M14 job state — the
  same posture Research has today (acceptable).

---

## 12. Persistence / Caching Architecture

**Decision:** OAQ-5(A) recommended — two new collections, **conditional on
`08` + ADR schema-change approval at architecture ratification**; OAQ-6 — no
new cache / no new Redis.

| Collection | Purpose | Key / index | TTL |
|---|---|---|---|
| `filing_analyses` | Durable analysis artifact (the four outputs + per-output flat cited narrative + state + coverage boundaries + `generated_at`). | Unique on **analysis identity** = `doc_id` + `prompt_version` + `output_schema_version` + `provider` + `model`. | None (durable, like `comparison_explanations`). |
| `filing_analysis_jobs` | Job mirror (status, events, identity, timestamps). | `id` unique; **partial unique** on `active_identity_key` (≤ 1 active job per identity — atomic dedup, mirrors I-29); `created_at`. | 30 days (mirrors I-25 / I-30). |

- **Dedup / `reused`:** read-before-generate on `filing_analyses` by
  identity key; `insert_one` + `DuplicateKeyError` adopt (mirrors
  `_run_comparison_explanation`). Because the filing is immutable, a
  completed artifact is **unconditionally** reusable for its identity — no
  evidence-fingerprint staleness check is needed (simpler than M9.1).
- **Invalidation:** implicit — a `prompt_version` / `output_schema_version`
  bump changes the identity key; old artifacts are simply never matched
  again (no migration). The durable collection has no TTL; if storage ever
  matters, a TTL is a later, separate decision.
- **Fallbacks (if governance withholds approval):** (B) single
  `filing_analyses` collection, job state stays in `JobStore`; (D) no new
  collection → Redis short-TTL result cache, `reused` best-effort; (C) no
  persistence → recompute every request (contract-legal, §12, but
  wasteful).
- **No response cache, no Redis result cache** in the recommended path
  (OAQ-6). The existing job/event/SSE Redis use is not new and not a cache.

**This is the pack's principal new governance dependency** and is a §24
ratification-gate item.

### 12.1 Schema / index realization is NOT authorized by architecture ratification

> **Architecture decision:** durable persistence is the *recommended* M14
> architecture (§OAQ-5, §12).
>
> **Schema / data-governance authority:** the exact MongoDB
> collection/index realization remains subject to the existing
> `08_MongoDB_Data_Architecture.md` + ADR governance chain.

**The following do NOT become authorized — implicitly or otherwise — merely
because Document 65 is later architecture-ratified:**

- creating MongoDB collections (`filing_analyses`, `filing_analysis_jobs`,
  or any other);
- modifying existing MongoDB collections;
- creating indexes (the analysis-identity unique index, the
  `active_identity_key` partial-unique index, the optional
  `{doc_id:1, chunk_idx:1}` compound index, or any other);
- changing the canonical data architecture (`08_MongoDB_Data_Architecture.md`);
- migrations or backfills;
- production deployment of any schema change.

Each of the above requires its **own** approval through the
`08_MongoDB_Data_Architecture.md` + ADR chain, as a step **distinct from and
subsequent to** architecture ratification of this pack. Document 64 §6.1 /
§19.3 already state that Document 64 pre-approves none of it; this section
states that **architecture ratification of Document 65 also pre-approves
none of it.** If that chain withholds approval, fallbacks B → D → C apply
(§OAQ-5, §12). The two-collection *logical* recommendation is retained; only
its *realization* is gated.

---

## 13. API / Runtime Architecture

**Decision:** OAQ-4(B) — async 4-route family, additive.

```text
POST   /api/companies/{ticker}/filings/{doc_id}/analysis            → {id, status, reused}
GET    /api/companies/{ticker}/filings/{doc_id}/analysis/{id}       → {id, status, analysis?}
GET    /api/companies/{ticker}/filings/{doc_id}/analysis/{id}/stream → SSE (data: TraceEvent; event: end)
POST   /api/companies/{ticker}/filings/{doc_id}/analysis/{id}/cancel → {id, status}
```

- **Request:** `current_user` (C-8); path `ticker` normalised
  `.strip().upper()` (empty → `ValidationError` 422); `(ticker, doc_id)`
  mismatch → `NotFoundError` 404 (non-disclosure, Document 59 OD-6). Body:
  BYOK field set **verbatim** (`llm_provider` / `llm_api_key` /
  `llm_base_url` / `llm_model`, all `Optional[str] = None`); custom provider
  / `llm_base_url` → existing `require_admin` + `assert_public_url`.
  **No output-selection field** (CQ-2) — the request contract defines none.
- **Response (`analysis` payload):** the four outputs
  (Filing Summary, Risk Factors Digest, MD&A Digest, Important Changes),
  always all four, each `{ narrative, sources[], cited_source_indices,
  state }` (+ coverage-boundary list for `partial` /
  `insufficient_evidence`). Echo `filings` metadata verbatim
  (`doc_id, ticker, company_name?, source, created_at`); never `_id` /
  `embedding` (C-11). Exact key spellings / container shape (object-keyed
  vs array) are wire details for the implementation, within Document 64
  §9.3.
- **Error propagation (reuse taxonomy, zero additions — Document 64 §10):**
  401 unauthenticated; 422 `ValidationError`; 404 `NotFoundError`;
  403 `require_admin`; 429 `RateLimitedError` (admission budget);
  502 `LLMProviderError` / `InfrastructureError` (redacted message only —
  never raw provider text, key fragments, or stack traces);
  504 `DeadlineExceededError` (async deadline). `insufficient_evidence` /
  `partial` are **200-level** results, not errors.
- **Idempotency:** `POST` is idempotent per analysis identity via the
  partial-unique `active_identity_key` (OAQ-5) — concurrent requests for the
  same identity attach to one job / artifact, never both generate.
- **Resource limits:** shared `MAX_ACTIVE_JOBS`; per-analysis LLM-call
  budget bounded by the OAQ-10 threshold; `job_deadline_filing_analysis_s`.
- **Timeout semantics:** the async deadline (`180s` recommended); no
  minutes-long synchronous HTTP request.
- **Observability:** §18.

---

## 14. AI Model / Provider Architecture

**Decision:** OAQ-8(A).

- **Access:** `agents/llm.py` `chat_text` / `chat_json` only. No direct SDK
  use. No new provider, no new dependency (AC-3).
- **Tiers:** `DEFAULT_HEAVY_MODEL` for the four output generations;
  `DEFAULT_LIGHT_MODEL` for section classification (OAQ-1, large filings).
- **BYOK:** request BYOK fields → `set_llm_context(...)` around the run,
  `reset_llm_context` in `finally` (mirrors `_run_comparison_explanation`).
  A user's provider/model/key governs M14 exactly as it governs Research.
- **Structured output enforcement:** `chat_json` with a per-output Pydantic
  schema (fields: `narrative`, and the marker convention; `sources` /
  `cited_source_indices` are **built by the deterministic validator**, not
  trusted from the model — OAQ-9). `chat_json`'s existing recovery
  heuristics and `ValueError`-on-invalid apply.
- **Retries:** `chat_text`'s existing 4-attempt backoff loop; `NonRetryable
  LLMError` (truncation / bad config) fails fast. No new retry logic.
- **Failure handling:** a provider failure after retries → the output that
  needed it is marked `insufficient_evidence` (if isolated) or the job
  `fails` with a redacted message (if the whole run cannot proceed). Never
  a fabricated output.
- **Determinism:** low `temperature` (exact value = implementation tuning);
  fixed candidate ordering; versioned prompts/schemas. Bit-identical output
  is not promised (§12).
- **Observability:** `llm_calls_total` / `llm_tokens_total` and `llm.attempt`
  spans come for free from `chat_text`.

---

## 15. Reliability / Failure Handling

| Failure | Behaviour | Source |
|---|---|---|
| `(ticker, doc_id)` unknown / cross-ticker | 404 `NotFoundError`, non-disclosure | Document 64 §10; Document 59 OD-6 |
| Known filing, zero persisted chunks | 200-level "no analysable content" result (all four outputs `insufficient_evidence`), not 404, not fabricated | Document 64 §8, §10; Document 59 OD-7 |
| Malformed / gapped chunks | Analyse present well-formed chunks; anchors reference present ranges only; affected outputs → `partial` / `insufficient_evidence` with ingest limitation named; no fabrication | Document 64 §11.8; AH-5 (mechanism delegated) |
| Section location weak for a digest | That output → `partial` / `insufficient_evidence` with a coverage boundary; other outputs unaffected | OAQ-1; Document 64 §11.6/§11.7 |
| One output cannot ground any substantive claim | That output → `insufficient_evidence` (no claims, empty citations, machine-readable reason) | Document 64 §11.6 |
| Provider failure (after `chat_text` retries) | Isolated → that output `insufficient_evidence`; run-wide → job `failed`, redacted message | §14; Document 64 §10 |
| Malformed / unvalidatable model output | `chat_json` `ValueError` → same as provider failure path | §14 |
| Admission budget exceeded | 429 `RateLimitedError` on `POST` | Document 64 §10 |
| Deadline exceeded | Job `failed` / 504; no partial artifact returned | §11; Document 43 precedent |
| Client cancels | Job `cancelled`; result not published / persisted; running provider call not force-killed (honest limitation) | §11; Document 43 §13 |
| Mongo / infra failure | 502 `InfrastructureError`, safe message, `logger.exception` first | Document 64 §10 |
| Existing routes | **Unchanged** — a M14 failure never fails or slows `GET /filings`, the M13 read, `/reports/generate`, or any existing route | AC-5; Document 64 §10 Invariant |

**No new error type is introduced** (Document 64 §10 — reuse the taxonomy
with zero additions).

---

## 16. Determinism

- **Contract expectation (C-10):** output *schema* stable per version;
  analysis depends only on the filing + versioned prompt / schema / model;
  no session, no request history, no other filing.
- **Architecture guarantees:** the analysis function's inputs are exactly
  `(doc_id's chunks, prompt_version, output_schema_version, provider,
  model)` — structurally no other input is reachable (no session store, no
  second `doc_id`, no clock-dependent branch). Candidate ordering is fixed
  (`chunk_idx`). The validator (OAQ-9) is fully deterministic. `temperature`
  is low.
- **What is not deterministic (and is permitted, §12):** the exact prose of
  each `narrative` across runs. The *set of grounded substantive claims*,
  the *anchors*, and the *state* are stable to the extent the model's claim
  selection is stable given a fixed candidate set — and the validator makes
  the *structure* deterministic regardless.
- **Reproducibility:** via OAQ-5 identity + reuse (`reused: true` on
  identity match) — a stored artifact for an identity is returned verbatim,
  making a repeated request bit-identical. Under the no-persistence
  fallback, repeated requests may differ in prose only.

---

## 17. Security

- **AuthN:** `current_user` on all four routes; no new auth concept
  (C-8, AC-11).
- **AuthZ:** the filing corpus has no `user_id` and is shared across tenants
  by design (`08` RI-5) — any authenticated user may analyse any ingested
  filing, exactly the visibility `GET /filings` and the M13 read already
  have. Job records (if persisted, OAQ-5) are owner-scoped: `GET`/`cancel`
  by a non-owner → 404 (non-disclosure, Document 43 §13).
- **BYOK:** existing policy verbatim — SSRF guard `assert_public_url` +
  `require_admin` for a custom `llm_base_url`; `llm_api_key` never
  persisted, never logged (redaction on error, `redact_key_from_error`).
- **Prompt injection (Document 64 §15, AH-8):** filing text is
  attacker-influenceable in principle (corpus-poisoning trade-off is
  documented and accepted — `10` §6.4 / SQ-1). The analysis prompts MUST
  frame filing content as untrusted data, not instructions; the concrete
  mitigation (delimiting, instruction-hierarchy prompting) is an AH item.
  The deterministic anchor validator (OAQ-9) is a second line of defence —
  an injected "cite chunk 999" is dropped as out-of-range.
- **Output safety:** non-recommending constraint (no buy/sell/hold — §8) is
  a safety boundary; every failure path emits only a redacted generic
  message.
- **No new stored credential, no fork/PR CI implication** — read + generate
  surface only.
- **DoS surface:** a user could enqueue many large-filing analyses;
  bounded by the shared `MAX_ACTIVE_JOBS` admission budget. A stricter
  per-kind limit is a possible later operational decision (not needed at
  architecture stage — Document 43 §23 pattern).

---

## 18. Observability

**Reuse-only; no metric name is frozen here (Document 64 §14; Document 43
§20 pattern).**

- **HTTP layer:** the four routes emit
  `alphascribe_http_requests_total{method,path,status}` +
  `..._duration_seconds` automatically.
- **LLM layer:** `llm_calls_total` / `llm_tokens_total` + `llm.attempt`
  spans — automatic via `chat_text`.
- **Job layer:** `MAX_ACTIVE_JOBS` admission / active-job gauges apply once
  `JobKind.FILING_ANALYSIS` exists.
- **Tracing:** one `pipeline.filing_analysis` span per run + child spans
  per LLM call + per step (`sectioning`, `analyzing`, `validating`).
- **Outcome signal (required observable; mechanism = AH-7):** it MUST be
  possible to distinguish, in aggregate, per-output
  `complete` / `partial` / `insufficient_evidence` / `failed` and per-run
  `completed` / `failed` / `cancelled` / `deadline_exceeded` — so a
  systemic section-location or grounding problem is visible (and to tune the
  OAQ-10 threshold and the OAQ-4 deadline). Exact metric name/shape →
  implementation.
- **Anchor-validation signal (recommended):** rate of dropped / out-of-range
  `[n]` markers per run — a spike indicates prompt drift or injection.
- **No raw provider text, key material, or prompt content in logs or
  metrics.**

---

## 19. Performance / Cost

| Dimension | Envelope |
|---|---|
| Input size | ≤ ~200 KB text / ≤ ~2,000 chunks per filing (ingest truncation). |
| LLM calls per analysis | ~1 light (section classification, large filings only) + ~4–8 heavy (four outputs; up to ~2× on the largest filings if a selected candidate set still needs a bounded map-reduce). Comparable to a Research run (up to 6 heavy). |
| Bounding mechanism | OAQ-10 threshold: whole-filing ≤ ~120 chunks; retrieval-scoped above. Per-output LLM input is a fixed budget regardless of filing size. |
| Latency | Target the OAQ-4 deadline (`180s` recommended). The **product-level latency / freshness expectation (CQ-4)** is **not** set here — Document 64 §18 gates it to implementation authorization; this pack supplies the cost model. |
| Recompute avoidance | OAQ-5 persistence + identity dedup: a repeated analysis of the same `(doc_id, prompt/schema/provider/model)` is a cheap read (`reused: true`). |
| Concurrency cost | Shared `MAX_ACTIVE_JOBS` budget — M14 competes with Research / Learning / Comparison-Explanation (accepted). |
| Storage cost | ~one small artifact per distinct analysis identity per filing (four short narratives + anchor lists). Job mirror TTL 30d. |
| Offline / model-load failure | BM25-only retrieval; analysis still runs; quality lower, `insufficient_evidence` rate higher — contract-compliant. |

**The `~120 chunk` / `~110 KB` whole-filing threshold and the `180s`
deadline are OPERATIONAL / RUNTIME CONFIGURATION, not architecture or
contract constants.** They are recommended starting values, tuned against
the §18 outcome signals after deployment. **They are NOT part of the frozen
Document 64 API contract** (Document 64 §9 fixes the request/response
*shape*, not any size or time budget; CQ-4 latency is separately gated to
implementation authorization — Document 64 §18). **Re-tuning either value
later does NOT require a Document 64 contract change and does NOT require a
re-ratification of this pack** — it is an architecture/runtime tuning
parameter change, made through normal configuration governance. This
revision does not invent any new fixed threshold; `~120` / `~110 KB` /
`180s` remain the pack's *recommended* (not frozen) values.

---

## 20. C-2 Sequencing Assessment

**Finding: C-2 Structured Filing Extraction is NOT a proven hard technical
prerequisite for C-1 under the recommended architecture (OAQ-1(D) +
OAQ-3(A/B) + OAQ-9(A)). This finding is CONDITIONAL — it rests on an
empirical question that static evidence cannot settle.**

- **Technical evidence FOR proceeding without C-2:** `filing_chunks` already
  contains the full filing text in reading order; SEC 10-K/10-Q use
  canonical Item headings that are present *in the chunk text* even though
  not persisted as structure; analysis-time section location (heuristic
  heading match + a light LLM classification pass) is a well-understood
  technique; Filing Summary and Important Changes are not strongly
  section-dependent; the contract's honest `insufficient_evidence` /
  `partial` states (§11.6/§11.7) make a weak-section-location outcome
  *contract-compliant*, not a violation.
- **Technical evidence AGAINST (the risk):** the *quality* of analysis-time
  section location for **Risk Factors Digest** and **MD&A Digest** on real
  filings — especially BSE annual reports and `POST /ingest/text` documents
  with no reliable Item structure — is **not knowable from static
  inspection**. If section location is poor, those two digests will
  frequently return `partial` / `insufficient_evidence`, which is honest but
  low-value.
- **The validation gate (an IMPLEMENTATION VALIDATION GATE, §1.1; a
  deliverable of the implementation phase, before wiring the full flow):**
  an early spike runs analysis-time section location over a
  **representative sample** of ingested filings (at minimum: EDGAR 10-K,
  EDGAR 10-Q, BSE annual report, plain-text ingest).
  - **Required evidence the spike must produce:** for each output that
    depends on section location (Risk Factors Digest, MD&A Digest), a
    reviewer-checkable record of, per sampled filing, whether the located
    chunk range(s) actually cover that filing's real section, and the
    resulting output `state` (`complete` / `partial` /
    `insufficient_evidence`); the same for a control set of Filing Summary
    and Important Changes outputs; and the aggregate
    `partial` / `insufficient_evidence` rate split by filing source
    (EDGAR vs non-EDGAR).
  - **The pass/fail quality bar is CTO-agreed, not proposed here.** This
    pack does **not** invent a numeric threshold. The CTO sets the bar
    (e.g. an acceptable section-coverage rate for EDGAR filings and an
    acceptable `insufficient_evidence` rate for non-EDGAR filings) when the
    spike evidence is presented, or delegates the bar to the
    architecture-ratification record. Until a bar is set, the gate is
    **not** cleared.
- **If the gate PASSES:** M14 proceeds on this architecture; C-2 remains a
  future, independent roadmap item.
- **If the gate FAILS:** the consequence is a **roadmap re-sequencing**:
  the CTO is asked, **as a separate governance decision**, whether to
  insert C-2 (a persisted structured-section representation, its own
  contract + architecture + implementation) *before* completing C-1.
  - This pack does **not** make that decision.
  - This pack does **not** rewrite Document 63 or change the M14 selection.
  - This pack does **not** implement C-2 or any structured-extraction code.
  - The re-sequencing, if invoked, is a new governance artifact / decision
    in its own right.
- **Roadmap / governance consequence (recorded):** M14 completion is gated
  on either (a) the spike passing, or (b) a separate CTO re-sequencing
  decision. Either way, C-2's status ("neither selected nor rejected")
  is unchanged by this pack.

### 20.1 The validation gate is an explicit implementation-phase STOP/CONTINUE gate

The §20 validation gate is **not advisory**. It is a hard STOP/CONTINUE
checkpoint the implementation phase must reach and clear **before** wiring
the full four-output flow.

- **CONTINUE** — only if the spike evidence meets the CTO-agreed quality bar
  (§20). Implementation then proceeds on the OAQ-1(D) architecture. C-2
  remains a future, independent roadmap item.
- **STOP** — if the spike evidence does **not** meet the bar, or no bar has
  been set. On STOP, the implementation engineer:
  1. **STOPS at the gate.** No further M14 wiring proceeds.
  2. **Does NOT silently redesign the architecture.** A different
     section-location or analysis approach is a new architecture matter,
     not an engineer's unilateral substitution.
  3. **Does NOT implement C-2, structured-section extraction, or any
     equivalent, automatically.** The failure of this gate is **not**
     pre-authorization of C-2 in any form.
  4. **Does NOT rewrite, re-sequence, or reinterpret Document 63.** The M14
     selection is untouched.
  5. **Escalates to a separate CTO governance decision**, which — and only
     which — determines whether to (a) insert / re-sequence C-2 before
     completing C-1 (its own selection, contract, architecture,
     implementation chain), (b) adopt a different architecture path for the
     section-dependent outputs, or (c) accept a reduced-quality outcome for
     those outputs under the contract's honest `partial` /
     `insufficient_evidence` semantics.
- **The failure path confers no authorization.** It does not authorize C-2
  work, does not authorize a schema change, does not authorize
  implementation, commit, or push. It produces a decision *request* to the
  CTO and nothing else.
- **C-2 is not a proven hard technical prerequisite** — this pack's
  conclusion — **and** the gate exists precisely because that conclusion is
  *conditional* on an empirical result. Ratifying this pack ratifies the
  conditional structure (recommendation + gate + escalation), not an
  unconditional "C-1 without C-2" claim.

### 20.2 What the architecture-ratification record must be able to distinguish

The future §24 ratification record must state, item by item, which of these
each ratified element is (§1.1 legend):

| Category | Example in this pack | What ratification does |
|---|---|---|
| **Ratified architecture** | The out-of-graph orchestration (OAQ-7), the async 4-route job shape (OAQ-4), the numbered-candidate + deterministic-validator citation mechanism (OAQ-9), the existing-tiers model strategy (OAQ-8), the threshold-hybrid cost strategy (OAQ-10). | Adopted as the M14 architecture. |
| **Conditional validation assumption** | "C-1 can proceed without C-2" (OAQ-1 / OAQ-2). | Adopted **as conditional** on §20.1; not an unconditional claim. |
| **Implementation validation gate** | The §20 / §20.1 section-location spike + STOP/CONTINUE gate. | Adopted **as a gate**; not pre-cleared. |
| **External governance dependency** | The `filing_analyses` / `filing_analysis_jobs` collections + indexes (§12.1); the optional `{doc_id:1, chunk_idx:1}` index (OAQ-3); the `JobKind` + route-inventory change (OAQ-4); a possible C-2 re-sequencing decision (§20.1). | **Not** authorized by ratification; recorded as still-owed to `08` + ADR / implementation authorization / a separate CTO decision. |
| **Unresolved / non-ratified matter** | The empirical section-location quality itself; the CTO-agreed quality bar (if not set at ratification); the exact schema realization. | Remains open; the ratification record names it. |

---

## 21. Alternatives Rejected (consolidated)

| Rejected | Where | Why |
|---|---|---|
| Whole-filing pass for every output, all filing sizes | OAQ-1/A, OAQ-10/A | Unbounded context/cost on ~2,000-chunk filings. |
| Adopt C-2 (structured section store) as the M14 architecture | OAQ-1/C, OAQ-2/B | Different milestone; schema change; silently re-sequences Document 63; exceeds this pack's authority. |
| Persist analysis-time section labels back to Mongo | §8 | That is C-2 by another name; pulls an unneeded schema dependency. |
| New purpose-built filing-scoped retriever / vector store | OAQ-3/C | Net-new infrastructure the contract forbids as an M14 deliverable; unnecessary given the existing hybrid scorer + a `doc_id` filter. |
| Synchronous endpoint | OAQ-4/A | Minutes-long HTTP request is timeout-fragile; no progress signal for the frozen `FilingViewer` streaming states. |
| Async without SSE | OAQ-4/C | The `FilingViewer` "Filing analysis" spec has `AI Thinking / Streaming` states. |
| No persistence (recompute every request) as the primary model | OAQ-5/C | Wasteful given filing immutability; weak `reused` semantics. New field on `filings` — mixes an AI artifact into an immutable ingest record. |
| Redis / in-process result cache in the recommended path | OAQ-6/B, OAQ-6/C | Redundant with OAQ-5 persistence; premature; adds a dependency. |
| New M14 LangGraph, or a new node in the `research` graph | OAQ-7/B, OAQ-7/C | M14 has no conditional-routing / retry-loop shape; triggers LG-1 + new G-1 vocabulary + `07` stop-and-CR + frontend sign-off for zero functional gain; a `mode`-parameterized graph violates LG-1. |
| Light tier throughout / heavy tier throughout / a fixed concrete model | OAQ-8/B,C,D | Grounding risk / wasteful / breaks provider-agnosticism + BYOK. |
| Embedding-similarity or LLM-verifier anchor attribution; model-emitted structured anchors trusted without validation | OAQ-9/B,C,D | Non-deterministic / fuzzy / unreliable on weaker models; A's deterministic validator is testable and reuses shipped code. |
| Always map-reduce over fixed windows | OAQ-10/D | Overhead for filings that fit in one pass. |

---

## 22. Architecture Decision Summary

> **Post-ratification note (2026-08-31):** the "Decision status" column
> below is the **proposal-time** view. The **ratified** status of each OAQ
> is recorded in **§27.2** — OAQ-3 / OAQ-4 / OAQ-6 / OAQ-7 / OAQ-8 / OAQ-9 /
> OAQ-10 as **RATIFIED ARCHITECTURE DECISIONS**; OAQ-1 / OAQ-2 as
> **CONDITIONAL ARCHITECTURE DECISIONS** (§20.1 gate preserved, not
> pre-cleared); OAQ-5 as a **RATIFIED LOGICAL ARCHITECTURE DECISION ONLY**
> (schema realization delegated to `08` + ADR, §12.1).

| OAQ | Recommended decision | Decision status (§1.1) | New governance dependency? |
|---|---|---|---|
| **OAQ-1** Chunk-vs-section | **Unstructured chunks + analysis-time section location** (hybrid: whole-filing small, section-scoped large). **C-2 not adopted, not a proven hard prerequisite.** | **CONDITIONAL DECISION + IMPLEMENTATION VALIDATION GATE** (§20.1 STOP/CONTINUE). | Conditional: a **separate CTO governance decision** (C-2 insert/re-sequence *or* another path) **iff** the §20.1 gate fails — the failure path is **not** C-2 pre-authorization. |
| **OAQ-2** C-2 sequencing | **C-2 not a proven hard prerequisite** (conclusion retained, not softened). Conditional; STOP/CONTINUE escalation defined, not triggered. | **CONDITIONAL DECISION + IMPLEMENTATION VALIDATION GATE** (§20.1). | Same as OAQ-1 (recorded, not triggered; not pre-authorization of C-2). |
| **OAQ-3** Retrieval / RAG | **Whole-filing (small) + filing-scoped reuse of the existing hybrid scorer with an additive `doc_id` filter (large).** No new embedding model / reranker / store. | PROPOSAL-TIME RECOMMENDATION. | Possible **`{doc_id:1, chunk_idx:1}` index** (Doc 59 OD-4) — **EXTERNAL GOVERNANCE DEPENDENCY**, via `08` + ADR (§12.1). |
| **OAQ-4** Endpoint form | **Async job + status + optional SSE + cancel — 4-route family, mirroring M9.1.** One new `JobKind.FILING_ANALYSIS`. Deadline `180s` (recommended, operational — §19). | PROPOSAL-TIME RECOMMENDATION. | `JobKind` member + 4 `APPROVED_ROUTES` entries + route-count test — **EXTERNAL GOVERNANCE DEPENDENCY**, under **implementation authorization** (AH-9), not architecture ratification. Deadline = operational config (§19). |
| **OAQ-5** Persistence | **Logical decision:** durable persistence recommended (M9.1 two-collection *logical* pattern). **Realization:** exact collections/indexes/migrations remain subject to `08` + ADR (§12.1). Fallbacks B → D → C preserved. | **PROPOSAL-TIME RECOMMENDATION** for the *logical* decision; **EXTERNAL GOVERNANCE DEPENDENCY** for the *realization*. | **YES — schema/index realization via `08_MongoDB_Data_Architecture.md` + ADR, a step DISTINCT FROM and SUBSEQUENT TO architecture ratification (§12.1).** Architecture ratification authorizes **no** collection, index, migration, or schema deployment. Principal §24 gate item. |
| **OAQ-6** Caching / Redis | **No new cache, no new Redis usage.** (Fallback only if OAQ-5(D).) | PROPOSAL-TIME RECOMMENDATION. | None (recommended path). |
| **OAQ-7** LangGraph topology | **Out-of-graph async orchestration** (mirror M9.1). **No `07` change, no new graph, no new node.** | PROPOSAL-TIME RECOMMENDATION. | None against `07`. New SSE `node` vocabulary = G-1-style cross-team contract — **EXTERNAL GOVERNANCE DEPENDENCY** (frontend sign-off, AH-6). |
| **OAQ-8** Model / provider | **Existing tiers verbatim** — HEAVY for outputs, LIGHT for classification. BYOK passthrough unchanged. No new provider, no default change, no new provider/model architecture. | PROPOSAL-TIME RECOMMENDATION. | None. |
| **OAQ-9** Anchor discovery | **Numbered-candidate generation + deterministic post-processing validation** (mirror `learning_nodes._postprocess_citations`). Frozen Document 64 representation preserved; discovery mechanism is architecture-owned and testable. | PROPOSAL-TIME RECOMMENDATION. | None. |
| **OAQ-10** Cost strategy | **Threshold hybrid** — whole-filing ≤ ~120 chunks; retrieval-scoped (+ bounded map-reduce) above. **Threshold + deadline = operational config, not a Document 64 contract term (§19); retunable without a contract change or a re-ratification.** | PROPOSAL-TIME RECOMMENDATION. | None. Informs (does not set) the CQ-4 latency expectation. |

**Unresolved / explicitly deferred (§1.1):** OAQ-1 and OAQ-2 carry a
**genuine empirical uncertainty** (section-location quality) resolved by the
§20 / §20.1 STOP/CONTINUE gate, not by this pack — and this pack's "C-2 is
not a proven hard prerequisite" conclusion is retained but is **not**
converted into an unconditional claim. OAQ-5's *logical* persistence
recommendation stands; its **schema/index realization is an external
governance dependency** (`08` + ADR, §12.1), not implied by architecture
ratification. No other OAQ is left implicitly resolved.

---

## 23. Implementation Constraints

The implementation phase (a **separate** authorization) must observe:

1. **Additive only** — zero change to any existing route, collection shape,
   graph, provider path, or `chunk_text` (AC-1…AC-5).
2. **Response representation is exactly Document 64 §8.2** — `narrative` +
   `sources[]` + `cited_source_indices` + `state` per output; four outputs
   always; no selection parameter.
3. **`sources[]` / `cited_source_indices` are built by the deterministic
   validator**, never trusted verbatim from the model.
4. **Anchor floor is exactly `{doc_id, chunk_start, chunk_end}`** —
   contiguous, present, `start ≤ end` — validated on every anchor.
5. **INV-IC** — the Important Changes code path receives exactly one
   `doc_id`'s chunks and no other document input; no comparison of any kind.
6. **No `07` change** without a separately-approved stop-and-CR.
7. **No new MongoDB collection / index / schema change / migration / schema
   deployment** without its **own** approval through the
   `08_MongoDB_Data_Architecture.md` + ADR chain — **a step distinct from
   and subsequent to architecture ratification of this pack** (§12.1).
   Architecture ratification authorizes none of it. If that chain withholds
   approval, fallbacks B → D → C apply (§OAQ-5).
8. **New routes + `JobKind` + route-count test** only under implementation
   authorization; `APPROVED_ROUTES` count moves from 43 to 47 as one
   reviewed change (AH-9).
9. **Section-location spike + §20 / §20.1 STOP/CONTINUE validation gate
   FIRST**, before wiring the full four-output flow. **On CONTINUE**,
   proceed. **On STOP** (evidence below the CTO-agreed bar, or no bar set):
   halt M14 wiring; do **not** redesign the architecture unilaterally; do
   **not** implement C-2 / structured-section extraction automatically; do
   **not** rewrite or re-sequence Document 63; **escalate to a separate CTO
   governance decision** (§20.1). The STOP path grants **no** authorization
   of any kind.
10. **Prompts, retrieval query strings, prompt/schema version identifiers,
    the OAQ-10 threshold, the deadline value, and the outcome-metric
    name/shape** are implementation deliverables (AH-1, AH-4, AH-5, AH-7),
    not frozen here — but each is version-pinned so §16 determinism holds.
11. **Frontend** (`FilingViewer` "Filing analysis" variant, SSE `node`
    registration) is **out of M14 backend scope** (AH-6) — a separate
    frontend track, requiring frontend sign-off on the `node` vocabulary.
12. **Tests for new functionality are written during implementation**, not
    here.

---

## 24. Architecture Ratification Gate

> **Ratification status (2026-08-31):** this gate has been **assessed and
> cleared for architecture ratification** — the M14 Filing Analysis
> architecture is **🟢 CTO-RATIFIED** (dated governance record: **§27**;
> per-criterion disposition: **§27.4**). The criteria below are preserved
> verbatim as the **basis of record**. Ratification does **not** pre-clear
> the §20.1 STOP/CONTINUE implementation-phase gate and does **not**
> authorize implementation, commit, push, or MongoDB schema realization.

**Gate criteria (basis of record — the following were required to be true
and on record for CTO architecture ratification of M14):**

- [ ] **Every OAQ (1–10) is explicitly resolved, or formally deferred with
      justification.** (This pack resolves 3–10; OAQ-1/OAQ-2 are deferred to
      the §20 empirical gate with justification.)
- [ ] **No conflict with Document 64.** The architecture preserves the
      four-output roster, the fixed full set / no selection parameter, the
      flat cited narrative representation, the citation anchor floor,
      grounding, `insufficient_evidence` / `partial` / `complete` / malformed-
      ingest semantics, INV-IC, the scope exclusions, and additive-only.
- [ ] **C-2 sequencing consequence explicitly recorded** (§20) — including
      the decision gate and the "separate re-sequencing governance
      decision" escalation, with no silent change to Document 63.
- [ ] **Citation architecture satisfies the contract** — the OAQ-9
      mechanism produces exactly the frozen representation; the validator is
      deterministic and unit-testable; ungrounded claims degrade to
      `partial` / `insufficient_evidence`, never fabrication.
- [ ] **Important Changes invariant preserved** — the architecture makes
      cross-document comparison structurally impossible for that output
      (single `doc_id` input).
- [ ] **Failure semantics defined** (§15) — reusing the existing taxonomy
      with zero additions; existing routes provably unaffected.
- [ ] **Determinism expectations addressed** (§16) — stable schema per
      version; inputs limited to filing + versioned prompt/schema/model;
      deterministic validator; reproducibility via identity + reuse.
- [ ] **Observability addressed** (§18) — the per-output / per-run outcome
      signal is defined as a requirement (mechanism = AH-7); anchor-drop
      signal recommended.
- [ ] **Security addressed** (§17) — auth, corpus visibility, BYOK/SSRF,
      prompt-injection posture (AH-8), output safety.
- [ ] **Performance / cost implications addressed** (§19) — bounded LLM
      input; cost model supplied for the CTO's CQ-4 latency decision.
- [ ] **Implementation boundary preserved** — Document 65 defines decisions,
      not code; no route, handler, node, prompt, retrieval module,
      migration, collection, Redis component, frontend, test, source schema,
      or production config is created here.
- [ ] **Schema-governance approval for OAQ-5's new collections + indexes**
      (`filing_analyses`, `filing_analysis_jobs`, and the optional
      `{doc_id:1, chunk_idx:1}` index) is obtained through
      `08_MongoDB_Data_Architecture.md` + the ADR chain, **or** a
      persistence fallback (OAQ-5 B/D/C) is explicitly selected.
- [ ] **The new SSE `node` vocabulary** (OAQ-7 / §11) has frontend sign-off
      as a G-1-style cross-team contract, **or** is explicitly deferred to
      the frontend track.
- [ ] **The OAQ-1 / OAQ-2 "C-1 without C-2" conclusion is ratified only as a
      CONDITIONAL DECISION** (§1.1) — the §20.1 STOP/CONTINUE gate remains
      in force, is not pre-cleared by ratification, and its failure path
      (a separate CTO governance decision; no silent redesign; no automatic
      C-2; no Document 63 change) is recorded. **The conclusion that C-2 is
      not a proven hard technical prerequisite is retained and is not
      converted into an unconditional claim.**
- [ ] **The ratification record sorts every ratified element into the §1.1
      legend** — ratified architecture / conditional validation assumption /
      implementation validation gate / external governance dependency /
      unresolved matter (§20.2 table) — so it states exactly what the CTO
      ratified and what remained conditional or delegated.

**Architecture ratification of this pack, even when granted, does NOT
authorize — and MUST NOT be read as authorizing:**

- **implementation** (a separate, subsequent CTO act — §25);
- **commit** or **push** (each a further separate CTO act — §25);
- **any MongoDB schema realization** — creating or modifying collections,
  creating indexes, changing the canonical data architecture, migrations,
  or production deployment of a schema change (each requires its own
  `08_MongoDB_Data_Architecture.md` + ADR approval — §12.1);
- **any C-2 / structured-section-extraction work** — the §20.1 failure path
  produces a CTO decision *request*, not an authorization;
- **clearing the §20.1 validation gate** — the gate is ratified *as a
  gate*, not as satisfied.

`architecture ratification → implementation authorization` is **false**.
`architecture ratification → MongoDB schema authorization` is **false**.

---

## 25. Governance / Authorization Boundaries

```text
Document 63  M14 = C-1 FILING ANALYSIS — FORMALLY SELECTED
        ↓
Document 64  M14 FILING ANALYSIS API CONTRACT — 🟢 CTO-RATIFIED (2026-08-31)
        ↓
Document 65  M14 FILING ANALYSIS ARCHITECTURE DECISION PACK   ← THIS DOCUMENT — 🟢 CTO-RATIFIED (2026-08-31; §27)
        ↓   CTO architecture ratification  DONE (2026-08-31; §24 gate; §27 record; grants NO code)
Separate M14 Implementation Authorization   ← NEXT STAGE  (its own scope-bound CTO act — NOT created here)
        ↓
Engineering implementation
        ↓
Technical review
        ↓
Commit authorization  (separate)   →   Push authorization  (separate)
```

- **No stage confers the next.** Architecture ratification ≠ implementation
  authorization ≠ commit ≠ push. `architecture ratification →
  implementation authorization` is **false**.
- **Architecture ratification ≠ MongoDB schema authorization.** The
  `filing_analyses` / `filing_analysis_jobs` collections and every index /
  migration / schema deployment require their **own** approval through
  `08_MongoDB_Data_Architecture.md` + the ADR chain — a step distinct from
  and subsequent to architecture ratification (§12.1). `architecture
  ratification → MongoDB schema authorization` is **false**.
- **Ratification authorizes nothing further.** Architecture ratification
  (§27, 2026-08-31) adopts the architecture; it is **not** implementation,
  commit, push, or MongoDB schema authorization. The next stage is a
  **separate M14 Implementation Authorization** decision — its own
  scope-bound CTO act, **not** created by this ratification.
- **C-2** stays *neither selected nor rejected*. §20 / §20.1 define an
  implementation-phase STOP/CONTINUE validation gate; on STOP, escalation
  is to a **separate** CTO governance decision. That failure path is **not**
  pre-authorization of C-2, does **not** permit a silent architecture
  redesign, and does **not** modify Document 63. This pack takes none of
  those steps.
- **The `~120 chunk` / `~110 KB` threshold and the `180s` deadline are
  operational configuration**, not Document 64 contract terms; re-tuning
  them later needs no contract change and no re-ratification (§19).
- **Document 63** is not modified. **Document 64** is not modified. The M14
  selection and the ratified contract are unchanged. Document 64's
  four-output roster, fixed full output set, CQ-1/CQ-2/CQ-3 resolution
  (recorded in Document 64 §18), INV-IC (filing-local only), the frozen
  citation representation, architecture-owned citation *discovery*, and the
  Filing Q&A exclusion all stand unchanged.
- **Existing governance state — unchanged by this document:** M13 COMPLETE /
  PUBLISHED; Document 62 CTO-RATIFIED; Document 63 M14 FORMALLY SELECTED;
  Document 64 CTO-RATIFIED (2026-08-31); Documents 58–61 frozen / untouched;
  G8 BLOCKED / CARRIED FORWARD; H-1 CLOSED WITH GOVERNANCE FOLLOW-UP; Gate
  (`JUDGE_SELF_CONSISTENCY_GATE_VERSION`) = 0.

---

## 26. Revision History

| Rev | Date | Change |
|---|---|---|
| Draft 1 | 2026-08-31 | Initial architecture proposal. Addresses OAQ-1…OAQ-10 (12-point treatment each); recommends unstructured-chunks + analysis-time section location (OAQ-1, C-2 gated §20), whole-filing/filing-scoped retrieval hybrid (OAQ-3), async 4-route job family (OAQ-4), two-collection persistence conditional on schema governance (OAQ-5), no new cache (OAQ-6), out-of-graph orchestration — no `07` change (OAQ-7), existing tiers verbatim (OAQ-8), numbered-candidate + deterministic validator anchor discovery (OAQ-9), threshold cost hybrid (OAQ-10). Names every new governance dependency. Defines the §24 architecture-ratification gate. **Status: 🟠 PROPOSAL — NOT RATIFIED.** |
| Draft 2 | 2026-08-31 | CTO conditional-pass governance tightening (**status unchanged: 🟠 PROPOSAL — NOT RATIFIED**). (1) OAQ-1/OAQ-2/§20: the "C-1 without C-2" conclusion is retained but made explicitly **conditional**; the §20 validation gate is defined as an implementation-phase **STOP/CONTINUE** gate (new §20.1) with STOP behaviour (halt; no silent redesign; no automatic C-2; no Document 63 change; escalate to a separate CTO governance decision) and an explicit statement that the failure path is **not** pre-authorization of C-2; the gate's required evidence is specified and the quality bar is left CTO-agreed (no invented number); new §20.2 defines what the ratification record must distinguish. (2) OAQ-5/§12: split the **logical persistence decision** (recommended) from the **schema/index realization** (subject to `08` + ADR); new §12.1 states architecture ratification authorizes no collection/index/migration/schema deployment; fallbacks B/D/C retained; two-collection recommendation retained. (3) New §1.1 decision-status legend; §22 gains a status column. (4) §19: `~120 chunk` / `~110 KB` threshold and `180s` deadline stated as operational config, not Document 64 contract terms, retunable without a contract change. (5) §24/§25: explicit "`architecture ratification → implementation authorization`" and "`architecture ratification → MongoDB schema authorization`" are **false**. No architecture decision changed; no scope expanded; historical Draft 1 entry not rewritten. |
| Ratification | 2026-08-31 | **CTO architecture ratification recorded as a new dated governance record — §27.** Document status → 🟢 CTO-RATIFIED (2026-08-31) — M14 FILING ANALYSIS ARCHITECTURE. Per-OAQ ratified status in §27.2 (OAQ-1/OAQ-2 conditional; OAQ-3/4/6/7/8/9/10 ratified; OAQ-5 logical decision only); §24 gate disposition in §27.4; governance ladder next stage = **Separate M14 Implementation Authorization** (§27.5). Historical Draft 1 / Draft 2 provenance unchanged. Implementation, commit, push, MongoDB schema realization, and C-2 remain **NOT AUTHORIZED**; the §20.1 STOP/CONTINUE gate remains **binding and uncleared**. No architecture decision changed; Document 63 and Document 64 not modified. |

---

## 27. CTO Architecture Ratification Record — 2026-08-31

**This is a new dated governance record.** It does not rewrite the §26
Draft 1 / Draft 2 provenance, does not modify Document 63 or Document 64,
and does not authorize implementation, commit, push, MongoDB schema
realization, or C-2.

### 27.1 Decision

On **2026-08-31** the CTO **ratifies the M14 Filing Analysis architecture**
defined by this pack. The document status changes from
🟠 ARCHITECTURE PROPOSAL — NOT YET RATIFIED to **🟢 CTO-RATIFIED
(2026-08-31) — M14 FILING ANALYSIS ARCHITECTURE**. The ratification is
consistent with the pack's current Draft 2 contents (§7, §12, §12.1, §19,
§20, §20.1, §22, §24) and adopts each OAQ at the status in §27.2, sorted
into the §1.1 decision-status legend.

**Document 64 remains the frozen M14 API-contract authority.** Where this
pack and Document 64 could appear to differ, Document 64 governs (§3, §25).
**Implementation remains NOT AUTHORIZED** — a separate CTO act (§27.5, §25).

### 27.2 Per-OAQ ratified status

| OAQ | Ratified status | What is ratified | What ratification does NOT do |
|---|---|---|---|
| **OAQ-1** — Chunk-vs-section | **CONDITIONAL ARCHITECTURE DECISION** | The recommended **hybrid whole-filing / section-scoped architecture over the existing `filing_chunks`**, with **analysis-time section location**. The **§20.1 STOP/CONTINUE validation gate is preserved**. The statement that **C-2 is not a proven hard technical prerequisite** is preserved. | **FAIL of the §20.1 gate means STOP.** FAIL does **not** authorize C-2. Only a **separate CTO governance decision** may insert / re-sequence C-2 or choose another architecture path. **Document 63 is not modified.** |
| **OAQ-2** — C-2 sequencing | **CONDITIONAL ARCHITECTURE DECISION** | The **conditional conclusion that C-2 is not currently established as a hard technical prerequisite** for C-1. The **separate governance decision requirement if §20.1 fails** is preserved. | **C-2 remains neither selected nor rejected.** No C-2 selection, contract, architecture, or implementation is authorized. |
| **OAQ-3** — Retrieval / RAG | **RATIFIED ARCHITECTURE DECISION** | **Hybrid whole-filing / retrieval-scoped** strategy; **reuse of the existing BM25 + dense + rerank infrastructure**; **`doc_id` filtering**; **no new vector store**; **no new embedding model**; **no new reranker**; **BM25-only degradation offline**. | The optional `{doc_id:1, chunk_idx:1}` compound index stays an **external governance dependency** (`08` + ADR, §12.1) — not authorized here. |
| **OAQ-4** — Endpoint form | **RATIFIED ARCHITECTURE DECISION** | **Async job + status + optional SSE + cancel**; **M9.1-style route family**. | The new **`JobKind` is an implementation consequence and is NOT authorization to modify source now**; `APPROVED_ROUTES` and the route-count test change only under a separate implementation authorization. |
| **OAQ-5** — Persistence | **RATIFIED LOGICAL ARCHITECTURE DECISION ONLY** | **Durable persistence** using the **logical two-collection pattern** — `filing_analyses` and `filing_analysis_jobs`. **Fallbacks B / D / C are preserved.** | **Architecture ratification does NOT authorize MongoDB schema realization:** no collection creation; no index creation or modification; no migration; no schema deployment; no canonical MongoDB architecture change. **Physical realization requires the separate `08_MongoDB_Data_Architecture.md` + ADR governance chain** (§12.1), distinct from and subsequent to this ratification. |
| **OAQ-6** — Caching / Redis | **RATIFIED ARCHITECTURE DECISION** | **No new M14 caching layer**; **existing Redis `JobStore` / `EventBus` usage only**. Redis caching **remains fallback-only** if applicable under the OAQ-5 persistence path. | No new Redis caching architecture is authorized. |
| **OAQ-7** — LangGraph topology | **RATIFIED ARCHITECTURE DECISION** | **Out-of-graph async orchestration**; **no modification to the frozen research LangGraph**; **no new LangGraph graph or node**. | **Future LangGraph topology changes require a separate stop-and-CR governance** decision. The new SSE `node` vocabulary remains a G-1-style cross-team contract owed to frontend sign-off. |
| **OAQ-8** — Model / provider | **RATIFIED ARCHITECTURE DECISION** | **Reuse of the existing tier abstraction** — `DEFAULT_HEAVY_MODEL` for the four outputs, `DEFAULT_LIGHT_MODEL` for section classification; the **existing BYOK / provider abstraction**; **`chat_json` + Pydantic schemas**. | **No new provider or model architecture is authorized.** |
| **OAQ-9** — Anchor discovery | **RATIFIED ARCHITECTURE DECISION** | **Numbered candidate generation**; **LLM `[n]` markers**; **deterministic citation post-processing**; **resolve to chunk ranges**; **coalesce adjacent ranges**; **enforce the Document 64 citation invariants**; **preserve the frozen external citation representation**. | **Document 64 is not altered.** |
| **OAQ-10** — Cost strategy | **RATIFIED ARCHITECTURE DECISION** | **Threshold hybrid** — whole-filing for smaller filings; retrieval-scoped analysis for larger filings; **bounded map-reduce only when necessary**. **`~120` chunks, `~110 KB`, and `180s` are operational / runtime configuration, NOT contract constants**, and **remain tunable without contract re-ratification**. | No change to Document 64; the CQ-4 latency expectation stays gated to implementation authorization. |

### 27.3 Statements of record

- **Document 64 remains the frozen API-contract authority.**
- **Document 65 architecture is now CTO-RATIFIED on 2026-08-31.**
- Document 65 ratification does **NOT** authorize **implementation**.
- Document 65 ratification does **NOT** authorize **commit**.
- Document 65 ratification does **NOT** authorize **push**.
- Document 65 ratification does **NOT** authorize **MongoDB schema
  realization**.
- Document 65 ratification does **NOT** authorize **C-2**.
- **§20.1 remains a binding implementation-phase STOP/CONTINUE validation
  gate.** Architecture ratification does **NOT** clear §20.1.
- Architecture ratification does **NOT** modify **Document 63**.
- **C-2 remains neither selected nor rejected.**
- **Filing Q&A remains excluded from M14.**
- **Document 64's four-output contract remains unchanged.**
- **INV-IC remains unchanged.**
- **The frozen citation representation remains unchanged.**
- **No new provider / model architecture is authorized.**
- **No new Redis caching architecture is authorized.**
- **No new LangGraph architecture is authorized.**
- **No new vector store is authorized.**
- **No new embedding / reranker stack is authorized.**

### 27.4 §24 gate disposition

The §24 gate criteria are the **basis of record** for this ratification:

- **Every OAQ (1–10) is resolved or formally deferred with justification**
  (§27.2). OAQ-3 / OAQ-4 / OAQ-6 / OAQ-7 / OAQ-8 / OAQ-9 / OAQ-10 are
  ratified architecture decisions; OAQ-1 / OAQ-2 are deferred to the §20 /
  §20.1 empirical gate and ratified **as conditional**; OAQ-5's logical
  decision is ratified with realization delegated.
- **No conflict with Document 64** — the architecture preserves the
  four-output roster, the fixed full set / no selection parameter, the flat
  cited narrative representation, the citation anchor floor, grounding,
  `insufficient_evidence` / `partial` / `complete` / malformed-ingest
  semantics, INV-IC, the scope exclusions, and additive-only.
- **C-2 sequencing consequence recorded** (§20) with no silent change to
  Document 63.
- **Citation architecture satisfies the contract** — the OAQ-9 mechanism
  produces exactly the frozen representation and its validator is
  deterministic and unit-testable.
- **Important Changes invariant preserved** — a single `doc_id` input makes
  cross-document comparison structurally impossible for that output.
- **Failure semantics, determinism, observability, security, and
  performance / cost** are addressed (§15–§19), reusing the existing error
  taxonomy with zero additions.
- **Implementation boundary preserved** — no route, handler, node, prompt,
  retrieval module, migration, collection, Redis component, frontend, test,
  source schema, or production config is created by this ratification.
- **Still-owed external governance dependencies:** the OAQ-5
  `filing_analyses` / `filing_analysis_jobs` collections + indexes and the
  optional `{doc_id:1, chunk_idx:1}` index via
  `08_MongoDB_Data_Architecture.md` + the ADR chain (§12.1); the OAQ-4
  `JobKind` + `APPROVED_ROUTES` + route-count test under implementation
  authorization; the OAQ-7 SSE `node` vocabulary via frontend sign-off; a
  possible C-2 re-sequencing decision only if the §20.1 gate fails.
- **The OAQ-1 / OAQ-2 "C-1 without C-2" conclusion is ratified only as a
  CONDITIONAL DECISION** — the §20.1 STOP/CONTINUE gate is **not
  pre-cleared** by this ratification, and its failure path (a separate CTO
  governance decision; no silent redesign; no automatic C-2; no Document 63
  change) stands. The conclusion that C-2 is not a proven hard technical
  prerequisite is retained and is **not** converted into an unconditional
  claim.

`architecture ratification → implementation authorization` is **false**.
`architecture ratification → MongoDB schema authorization` is **false**.

### 27.5 Governance ladder — next stage

`Document 65` architecture ratification (2026-08-31) is **complete**. The
**next stage is a separate M14 Implementation Authorization** decision — its
own scope-bound CTO act. **This task does not create that authorization
record.** No stage confers the next (§24, §25).

---

**NO IMPLEMENTATION PERFORMED. NO SOURCE, TEST, SCHEMA, INDEX, MIGRATION,
ROUTE, HANDLER, LANGGRAPH NODE, PROMPT, RETRIEVAL, MONGODB COLLECTION, REDIS,
FRONTEND, EVALUATION, OR CONFIGURATION FILE CREATED OR MODIFIED — THIS TASK
IS A GOVERNANCE-RECORD UPDATE ONLY. THIS DOCUMENT'S M14 FILING ANALYSIS
ARCHITECTURE IS 🟢 CTO-RATIFIED (2026-08-31; §27); IMPLEMENTATION, COMMIT,
PUSH, MONGODB SCHEMA REALIZATION, AND C-2 REMAIN NOT AUTHORIZED, AND THE
§20.1 STOP/CONTINUE GATE REMAINS BINDING AND UNCLEARED. M14 = C-1 FILING
ANALYSIS (DOCUMENT 63). DOCUMENT 64 IS THE 🟢 CTO-RATIFIED M14 API CONTRACT
AND IS NOT MODIFIED BY THIS DOCUMENT; ITS FROZEN OBSERVABLE BEHAVIOUR (FOUR
OUTPUTS, FIXED FULL SET, FLAT CITED NARRATIVE, CITATION ANCHOR FLOOR,
GROUNDING, INV-IC, SCOPE EXCLUSIONS) IS PRESERVED WITHOUT REINTERPRETATION.
OAQ-1…OAQ-10 ARE CTO-RATIFIED PER §27 AT THE STATUS RECORDED THERE — OAQ-3 /
OAQ-4 / OAQ-6 / OAQ-7 / OAQ-8 / OAQ-9 / OAQ-10 AS RATIFIED ARCHITECTURE
DECISIONS; OAQ-1 / OAQ-2 AS CONDITIONAL ARCHITECTURE DECISIONS; OAQ-5 AS A
RATIFIED LOGICAL ARCHITECTURE DECISION ONLY (SCHEMA REALIZATION DELEGATED TO
`08` + ADR). OAQ-1 / OAQ-2 CARRY A GENUINE EMPIRICAL UNCERTAINTY RESOLVED BY
THE §20 DECISION GATE, NOT INVENTED AWAY. C-2 IS NEITHER SELECTED NOR
REJECTED; IF THE §20 GATE FAILS, C-2-BEFORE-C-1 IS A SEPARATE ROADMAP
RE-SEQUENCING GOVERNANCE DECISION — NOT MADE HERE, NOT A REWRITE OF DOCUMENT
63, NOT C-2 IMPLEMENTATION. NEW GOVERNANCE DEPENDENCIES ARE NAMED (OAQ-5 NEW
COLLECTIONS + INDEXES VIA `08` + ADR; OAQ-3 OPTIONAL COMPOUND INDEX; OAQ-4
JOBKIND + ROUTES + ROUTE-COUNT TEST UNDER IMPLEMENTATION AUTHORIZATION; OAQ-7
SSE NODE VOCABULARY AS A G-1 CROSS-TEAM CONTRACT; CONDITIONAL C-2
RE-SEQUENCING). THE §20 VALIDATION GATE IS AN EXPLICIT IMPLEMENTATION-PHASE
STOP/CONTINUE GATE (§20.1); ON STOP THE ENGINEER HALTS, DOES NOT REDESIGN
THE ARCHITECTURE, DOES NOT IMPLEMENT C-2 AUTOMATICALLY, DOES NOT REWRITE
DOCUMENT 63, AND ESCALATES TO A SEPARATE CTO GOVERNANCE DECISION — THAT
FAILURE PATH IS NOT PRE-AUTHORIZATION OF C-2. THE `~120` CHUNK / `~110 KB`
THRESHOLD AND THE `180S` DEADLINE ARE OPERATIONAL CONFIGURATION, NOT
DOCUMENT 64 CONTRACT TERMS, RETUNABLE WITHOUT A CONTRACT CHANGE (§19).
FILING Q&A REMAINS EXCLUDED FROM M14. **`ARCHITECTURE RATIFICATION →
IMPLEMENTATION AUTHORIZATION` IS FALSE. `ARCHITECTURE RATIFICATION → MONGODB
SCHEMA AUTHORIZATION` IS FALSE** — THE `filing_analyses` /
`filing_analysis_jobs` COLLECTIONS AND EVERY INDEX / MIGRATION / SCHEMA
DEPLOYMENT REQUIRE THEIR OWN `08_MongoDB_Data_Architecture.md` + ADR
APPROVAL, DISTINCT FROM AND SUBSEQUENT TO ARCHITECTURE RATIFICATION (§12.1).
ARCHITECTURE RATIFICATION IS A SEPARATE CTO ACT (§24) AND, EVEN WHEN
GRANTED, AUTHORIZES NO IMPLEMENTATION, COMMIT, PUSH, OR SCHEMA REALIZATION
(§25). ARCHITECTURE RATIFICATION IS RECORDED IN §27 (2026-08-31) AS A DATED
GOVERNANCE RECORD; IT CLEARS NEITHER THE §20.1 STOP/CONTINUE GATE NOR ANY
IMPLEMENTATION / COMMIT / PUSH / SCHEMA STEP. NO STAGE. NO
COMMIT. NO PUSH. NO MERGE / REBASE / RESET / RESTORE / CLEAN. DOCUMENTS
58–64 NOT MODIFIED. NO ADDITIONAL DOCUMENT CREATED.**
