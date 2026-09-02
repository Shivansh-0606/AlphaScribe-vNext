# 66 — M14 Filing Analysis Implementation Authorization Proposal

**Status:** 🟢 **IMPLEMENTATION AUTHORIZED — 2026-09-02. COMMIT / PUSH NOT
AUTHORIZED.** The *separate M14 Implementation Authorization* that Documents
62 §13, 63 §4 / §8, 64 §20, and 65 §25 / §27.5 all reserve as a distinct,
subsequent CTO governance act **was issued on 2026-09-02** and is recorded
in §18 (synchronized from the CTO implementation-authorization companion
record of the same date — §18 of this document expressly provides for the
decision to be "recorded in §18 **or** a companion record"). This document
proposed — and the CTO decision then granted, within Documents 64 / 65 and
§4 / §5 bounds — an exact implementation scope, the exact capabilities
engineering was authorized to build, the source / test / configuration areas
that could be touched, the areas that stay prohibited, and the gates that
remain binding. **Commit is not authorized and push is not authorized** by
that decision; each remains a further, separate CTO act (§12.3 / §12.4).
The §20.1 STOP/CONTINUE gate is recorded PASS against the CTO-agreed quality
bar (§18). No MongoDB schema / collection / index / migration realization is
authorized (§9). C-2 remains neither selected nor rejected (§8).
**Type:** Governance / implementation-authorization proposal (documentation
only — no source code, test, schema, migration, index, route, handler,
LangGraph node, prompt, retrieval / RAG code, MongoDB collection, Redis
component, provider, configuration, infrastructure, or frontend file created
or modified to produce it). Documents 58–65 read, not modified. The only
file this task creates is this document.
**Governance chain (each a distinct CTO act; none confers the next):**
`Document 62` (Post-M13 roadmap; C-1 = preferred direction — 🟢 CTO-RATIFIED
2026-08-30) →
`Document 63` (M14 = C-1 Filing Analysis — FORMALLY SELECTED 2026-08-30) →
`Document 64` (M14 Filing Analysis API Contract — 🟢 CTO-RATIFIED
2026-08-31; the frozen externally observable contract) →
`Document 65` (M14 Filing Analysis Architecture Decision Pack — 🟢
CTO-RATIFIED 2026-08-31 §27; the ratified architecture) →
**`Document 66` (THIS — implementation-authorization proposal; the CTO
implementation-authorization decision is now recorded in §18 — 🟢 issued
2026-09-02)** →
CTO implementation-authorization decision (🟢 2026-09-02, §18) → engineering
implementation → technical review → commit authorization (separate, not yet
granted) → push authorization (separate, not yet granted).
**Authoritative inputs (CTO-ratified, unmodified — read, not altered):**
[64_M14_Filing_Analysis_API_Contract.md](64_M14_Filing_Analysis_API_Contract.md)
is the frozen API contract; where this proposal and Document 64 could appear
to differ, **Document 64 governs**.
[65_M14_Filing_Analysis_Architecture_Decision_Pack.md](65_M14_Filing_Analysis_Architecture_Decision_Pack.md)
is the CTO-ratified architecture (its §27 ratification record, its §1.1
decision-status legend, its §7 OAQ treatments, its §12 / §12.1 persistence
split, its §17 security, its §18 observability, its §19 performance / cost,
its §20 / §20.1 STOP/CONTINUE gate, its §22 decision summary, its §23
implementation constraints); where this proposal and Document 65 could
appear to differ, **Document 65 governs**.
**Structural precedent (cited, unmodified):**
[54_M10_Governance_Authorization_Reconciliation_Record.md](54_M10_Governance_Authorization_Reconciliation_Record.md),
[56_M12_Governance_Authorization_Reconciliation_Record.md](56_M12_Governance_Authorization_Reconciliation_Record.md),
[61_M13_Governance_Authorization_Reconciliation_Record.md](61_M13_Governance_Authorization_Reconciliation_Record.md)
(the short standalone governance-decision-record form; note those are
*post-implementation reconciliation* records — this document is the
*pre-implementation* authorization proposal the M14 chain deliberately
un-folds, per Document 63 §Precedent).
**Date:** 2026-08-31.

---

## 0. What This Document Is and Is Not

**Is:** a governance proposal that assembles everything the CTO needs to
decide whether — and with exactly what bounds — to authorize M14 Filing
Analysis engineering. It restates the ratified scope (Document 64) and the
ratified architecture (Document 65) as an implementation boundary, names the
precise source / test / configuration surface that boundary implies, names
what stays out, and carries the §20.1 STOP/CONTINUE validation gate forward
unweakened. It maps every required element (§Required-content coverage map)
to a section.

**Is not:** an implementation; an implementation authorization; an
architecture change; a contract change; a re-ratification of Document 64 or
65; a reinterpretation, weakening, or expansion of Documents 62–65; a
schema / migration / index authorization; a clearance of the §20.1 gate; a
selection or rejection of C-2; a commit authorization; a push authorization;
a frontend authorization. It creates no route, handler, node, schema,
migration, index, collection, Redis component, prompt, retrieval module,
test, or configuration value. It resolves no open matter that Documents
64 / 65 leave open.

---

## Required-content coverage map

| # | Required element | Section |
|---|---|---|
| 1 | Exact M14 implementation scope | §4 |
| 2 | Exact capabilities authorized for engineering | §5 |
| 3 | Source / test / configuration areas that may be modified | §6 |
| 4 | Areas that remain prohibited | §7 |
| 5 | The §20.1 STOP/CONTINUE validation gate | §8.1 |
| 6 | Required spike / evidence before CONTINUE | §8.2 |
| 7 | Exact FAIL / STOP conditions | §8.3 |
| 8 | Required behaviour on FAIL | §8.4 |
| 9 | §20.1 FAIL does NOT automatically authorize or select C-2 | §8.5 |
| 10 | C-2 remains subject to separate CTO governance | §8.6 |
| 11 | MongoDB physical schema realization stays on the `08` + ADR path | §9.1 |
| 12 | No unauthorized collections, indexes, migrations, or schema changes | §9.2 |
| 13 | Testing and validation expectations | §10 |
| 14 | Security and observability requirements inherited | §11 |
| 15 | Explicit prohibition on scope expansion | §12.1 |
| 16 | Explicit prohibition on architecture changes without separate governance | §12.2 |
| 17 | Explicit prohibition on commit authorization | §12.3 |
| 18 | Explicit prohibition on push authorization | §12.4 |
| 19 | Implementation authorization ≠ §20.1 gate clearance | §12.5 |
| 20 | Implementation authorization ≠ MongoDB schema realization authorization | §12.6 |

---

## 1. Governance Preconditions (verified this session, read-only)

| Fact | Source | Verified state |
|---|---|---|
| M13 — Filing Content Reading | Document 62 §1; `git log` | **COMPLETE / PUBLISHED** (`244ca5c`; governance reconciliation `f1c18c3`); `HEAD = origin/main = f1c18c3`, `0/0` |
| Document 62 (Post-M13 Roadmap Reconciliation) | its §16 | **🟢 CTO-RATIFIED (2026-08-30)** — C-1 = preferred roadmap direction; authorizes no implementation |
| Document 63 (M14 Formal Milestone Selection) | its §1, §5 | **M14 = C-1 Filing Analysis — FORMALLY SELECTED (2026-08-30)** — authorizes progression to the contract-governance stage only |
| Document 64 (M14 Filing Analysis API Contract) | its §Status, §20, §22 | **🟢 CTO-RATIFIED (2026-08-31)** — freezes the externally observable M14 contract (§4–§17); CQ-1 / CQ-2 / CQ-3 resolved (§18); grants no architecture, implementation, commit, or push authorization |
| Document 65 (M14 Filing Analysis Architecture Decision Pack) | its §Status, §27 | **🟢 CTO-RATIFIED (2026-08-31)** — OAQ-3/4/6/7/8/9/10 ratified architecture decisions; OAQ-1 / OAQ-2 ratified **as conditional** on §20.1; OAQ-5 ratified as a **logical decision only**; **implementation NOT AUTHORIZED**; §20.1 STOP/CONTINUE gate **binding and not cleared** |
| §20.1 STOP/CONTINUE validation gate | Document 65 §20, §20.1, §23 item 9, §27.3 | **BINDING — not pre-cleared by architecture ratification.** The section-location spike + go/no-go runs FIRST in implementation, before wiring the full four-output flow |
| MongoDB schema realization (`filing_analyses`, `filing_analysis_jobs`, indexes) | Document 64 §6 / §6.1; Document 65 §12.1, §23 item 7, §27.2 (OAQ-5), §27.3 | **NOT AUTHORIZED** by contract or architecture ratification — requires the separate `08_MongoDB_Data_Architecture.md` + ADR governance chain; fallbacks B → D → C apply if withheld |
| C-2 Structured Filing Extraction | Document 62 §6 C-2; Document 63 §6; Document 64 §16; Document 65 §20, §20.1, §27.2 (OAQ-1 / OAQ-2), §27.3 | **Neither selected nor rejected.** A §20.1 FAIL does **not** select or authorize it; only a separate CTO governance decision may insert / re-sequence it |
| Filing Q&A | Document 64 §6, §6.1; Document 63 §7 | **Excluded from M14** — firm product-scope exclusion, not re-openable by architecture or implementation |
| G8 / H-1 / G7 / judge / self-consistency gate | Document 62 §4; Document 64 §6 | **Out of M14 scope** — unchanged, not touched |
| Route inventory | Document 64 §2; Document 65 §23 item 8 | Exact-set guard `assert len(APPROVED_ROUTES) == 43`; the M14 additive routes move it to **47** as one reviewed change, **only** under implementation authorization (AH-9) |

**No governance state above is changed by this document. It is cited, not
re-decided.**

---

## 2. Governance Ladder Position

```text
Document 62  CTO-RATIFIED POST-M13 ROADMAP           (C-1 = preferred direction)
        ↓  separate CTO decision
Document 63  M14 = C-1 FILING ANALYSIS — FORMALLY SELECTED
        ↓  contract-governance stage
Document 64  M14 FILING ANALYSIS API CONTRACT — 🟢 CTO-RATIFIED (2026-08-31)
        ↓  architecture-governance stage
Document 65  M14 FILING ANALYSIS ARCHITECTURE DECISION PACK — 🟢 CTO-RATIFIED (2026-08-31, §27)
        ↓  CTO architecture ratification — DONE (grants NO code)
Document 66  M14 IMPLEMENTATION AUTHORIZATION PROPOSAL   ← THIS DOCUMENT — 🟢 IMPLEMENTATION AUTHORIZED (2026-09-02, §18)
        ↓  CTO implementation-authorization decision   (separate scope-bound CTO act — 🟢 ISSUED 2026-09-02; §18)
Engineering implementation  (done, under §18)
        ↓
Technical review  (a validation fact — not an authorization)  — PASSED
        ↓
Commit authorization  (separate CTO act — NOT yet granted)   →   Push authorization  (separate CTO act — NOT yet granted)
```

**No stage confers the next.** `architecture ratification →
implementation authorization` is **false** (Document 65 §24, §25).
`implementation authorization → commit authorization` is **false**.
`implementation authorization → push authorization` is **false**.
`implementation authorization → §20.1 gate clearance` is **false** (§12.5).
`implementation authorization → MongoDB schema realization authorization` is
**false** (§12.6).

---

## 3. Purpose of This Proposal

Document 65 is CTO-ratified architecture. Its §25 / §27.5 name the next
governance stage as **"Separate M14 Implementation Authorization"** and
explicitly do **not** create it. This document is that artifact, in
proposal form: it exists so the CTO can make one bounded decision —
*authorize M14 engineering within exactly these limits, or not* — with the
scope, the modifiable surface, the prohibitions, and the binding gates all
stated in one place and traceable to Documents 64 and 65.

It changes nothing. It proposes.

---

## 4. Exact M14 Implementation Scope  *(required element 1)*

The scope proposed for authorization is **exactly** the CTO-ratified
Document 65 architecture that satisfies the CTO-ratified Document 64
contract — **no more**. Restated as an implementation boundary:

**In scope (proposed):**

1. **One additive backend capability** that, given a filing identified by
   the ratified `(ticker, doc_id)` pair, produces the **exact four Document
   64 §8 outputs** — Filing Summary, Risk Factors Digest, MD&A Digest,
   Important Changes — always all four, **no** client-selectable subset
   (Document 64 CQ-1 / CQ-2). Each output is the frozen **flat cited
   narrative**: `narrative` + `sources[]` + `cited_source_indices` + `state`
   (`complete` / `partial` / `insufficient_evidence`), per Document 64 §8.2
   (CQ-3).
2. **An additive async HTTP surface** for it — the Document 65 §13 four-route
   family (`POST` create/reuse, `GET` status/result, `GET …/stream` SSE,
   `POST …/cancel`), `current_user` on every route, additive to the route
   inventory (43 → 47).
3. **The Document 65 §9 per-output analysis flow:** resolve `(ticker,
   doc_id)` (404 on miss, non-disclosure) → load ordered `{chunk_idx, text}`
   chunks (embedding projected out) → size check against the OAQ-10
   threshold → whole-filing candidate set (small filings) **or**
   retrieval-scoped selection via the existing hybrid retriever with an
   **additive `doc_id` filter** (large filings) → per output: `chat_json`
   (HEAVY) with `[n]` markers → **deterministic citation validator** →
   `state` assignment → assemble the four-output response.
4. **The Document 65 §10 / OAQ-9 anchor mechanism:** numbered-candidate
   generation + a deterministic post-processor that resolves `[n]` →
   `{doc_id, chunk_start, chunk_end}`, coalesces adjacency, enforces
   Document 64 §11.3–§11.5, builds `sources[]` / `cited_source_indices`, and
   applies §11.6 / §11.7 state rules — mirroring
   `learning_nodes._postprocess_citations`.
5. **The Document 65 §11 / OAQ-7 execution model:** out-of-graph async
   orchestration under a `pipeline.filing_analysis` OTel span, reusing
   `JobLifecycle` / `sse_response` / the shared `MAX_ACTIVE_JOBS` budget.
   **No LangGraph graph or node.**
6. **The Document 65 §14 / OAQ-8 model strategy:** `DEFAULT_HEAVY_MODEL` for
   the four output generations, `DEFAULT_LIGHT_MODEL` for section
   classification, BYOK passthrough via `set_llm_context` /
   `reset_llm_context`, `chat_json` + per-output Pydantic schemas. **No new
   provider, no default-provider change.**
7. **The Document 65 §20 / §20.1 section-location spike + STOP/CONTINUE
   validation gate**, executed **first**, before wiring the full
   four-output flow (§8).
8. **Persistence — logical only, physically gated:** the OAQ-5 logical
   two-collection pattern (`filing_analyses` + `filing_analysis_jobs`) may
   be implemented **only after** the separate `08_MongoDB_Data_Architecture.md`
   + ADR schema-governance chain approves the physical realization;
   otherwise fallbacks **B → D → C** apply (Document 65 §12, §12.1). See §9.
9. **Additive tests** for the new functionality and the route-inventory
   contract update (43 → 47).
10. **Operational/runtime configuration values** — the OAQ-10 whole-filing
    threshold (recommended `~120` chunks / `~110 KB`) and the
    `job_deadline_filing_analysis_s` deadline (recommended `180`) — set at
    recommended starting values, tunable later **without** a Document 64
    contract change or a Document 65 re-ratification (Document 65 §19, §25).

**Out of scope (restated, firm):** everything in §7. In particular: no
Filing Q&A, no chatbot, no conversational memory, no cross-filing analysis,
no ingestion change, no LangGraph topology change, no new provider, no new
retrieval infrastructure, no new Redis / caching layer, no C-2 / structured
section store, no frontend, and no change to any existing route or to
Documents 58–65.

---

## 5. Exact Capabilities Authorized for Engineering  *(required element 2)*

If the CTO issues the implementation-authorization decision, engineering
would be authorized to perform **exactly** the following, and nothing that
is not a direct consequence of them:

| # | Authorized capability | Bounded by |
|---|---|---|
| C-a | **Run the §20.1 section-location spike first** and produce its evidence package (§8.2) for the CTO go/no-go, before wiring the full four-output flow. | Document 65 §20, §20.1, §23 item 9 |
| C-b | **Add the four additive routes** of Document 65 §13 as new handlers (in `backend/server.py` or the appropriate router module), `current_user` on each, using the existing `{detail, type}` error envelope and taxonomy with **zero additions**. | Document 64 §9, §10; Document 65 §13, §15 |
| C-c | **Add exactly one `JobKind.FILING_ANALYSIS` enum member** and wire it into the existing `JobLifecycle` (shared `MAX_ACTIVE_JOBS` admission, `mark_running`, `publish`, `complete` / `fail` / `cancel`). | Document 65 §4 OAQ-4, §11, §22 |
| C-d | **Add exactly one setting** `job_deadline_filing_analysis_s` (recommended `180`) as operational configuration; enforce it with an explicit wall-clock deadline check at step boundaries in the orchestration function. | Document 65 §11, §19, §23 item 10 |
| C-e | **Implement the out-of-graph async orchestration function** under a `pipeline.filing_analysis` OTel span, emitting progress `TraceEvent`s (`pipeline` / `sectioning` / `analyzing` / `validating` / `final`) through the existing `JobLifecycle.publish` / `sse_response` path. **No LangGraph graph or node.** | Document 65 §7 OAQ-7, §11, §23 item 6 |
| C-f | **Implement the per-output analysis flow** (Document 65 §9): the size check, the section-classification step (heuristic + optional `chat_json` LIGHT call), the whole-filing / retrieval-scoped branch, the per-output `chat_json` HEAVY call with per-output Pydantic schemas. | Document 64 §8, §8.2; Document 65 §9, §14 |
| C-g | **Add an additive, opt-in `doc_id` (and optional `chunk_idx` window) parameter to the existing retrieval path** (`backend/agents/retrieval.py`) so BM25 + dense + rerank can select top-K candidate chunks within one filing. **No change to report-pipeline callers or their behaviour; no new embedding model, no new reranker, no new vector store.** | Document 65 §7 OAQ-3, §9, §22, §27.2 |
| C-h | **Implement the deterministic citation validator module** — marker resolution, adjacency coalescing, `chunk_idx`-range presence check against the filing's persisted set, orphan-index check, `sources[]` / `cited_source_indices` construction, state assignment — fully deterministic and unit-testable. `sources[]` / `cited_source_indices` are **built by the validator**, never trusted verbatim from the model. | Document 64 §11.3–§11.8; Document 65 §10 OAQ-9, §23 items 2–4 |
| C-i | **Author the M14 prompts, retrieval query strings, and prompt / output-schema version identifiers** (AH-1 / AH-4 / AH-5), version-pinned so Document 65 §16 determinism holds; frame filing text as untrusted data (AH-8). | Document 64 §19.2; Document 65 §14, §17, §23 item 10 |
| C-j | **Set the operational config values** — the OAQ-10 threshold and the deadline — at their recommended starting values, and the AH-7 outcome-metric name / shape. | Document 65 §18, §19, §23 item 10 |
| C-k | **Update `backend/tests/contract/test_route_inventory.py`** so `APPROVED_ROUTES` moves from 43 to 47 as **one reviewed change** (AH-9); add additive unit tests and an additive live-HTTP suite for the new capability. | Document 64 §17; Document 65 §23 items 8, 12 |
| C-l | **Implement OAQ-5 persistence — conditionally.** Implement the logical two-collection pattern **only if and after** the `08_MongoDB_Data_Architecture.md` + ADR chain approves the physical realization; if that chain withholds approval, implement fallback **B** (single durable collection), else **D** (bounded Redis short-TTL cache, `reused` best-effort), else **C** (no persistence, recompute per request — contract-legal). | Document 65 §12, §12.1, §23 item 7; §9 below |

**Not a capability grant:** the AH-6 frontend work (`FilingViewer` "Filing
analysis" variant, SSE `node` registration) is a **separate frontend
track** requiring frontend sign-off on the `node` vocabulary as a
G-1-style cross-team contract — **not** authorized by this backend
implementation authorization.

---

## 6. Source / Test / Configuration Areas That May Be Modified  *(required element 3)*

The modifiable surface implied by §5, and **nothing outside it**:

**Source (additive only):**

- `backend/server.py` (or the appropriate router module) — **add** the four
  M14 route handlers. No existing handler changed.
- `backend/domain/models.py` — **add** the `JobKind.FILING_ANALYSIS` enum
  member. `JobStatus` unchanged.
- `backend/agents/retrieval.py` — **add** an optional, opt-in `doc_id`
  (and optional `chunk_idx` window) parameter to the retrieval path.
  Existing report-pipeline call sites and their behaviour unchanged.
- **New M14-only modules** (additive files): the async orchestration /
  job-runner function; the section-classification step; the deterministic
  citation validator; the per-output Pydantic schemas; the M14 prompt /
  query-string / version-identifier module(s).

**Configuration:**

- `backend/app/settings.py` — **add** `job_deadline_filing_analysis_s`
  (recommended `180`) and, if needed, the OAQ-10 threshold value as
  operational configuration. Both are runtime-tunable without a Document 64
  contract change or a Document 65 re-ratification (Document 65 §19).

**Tests:**

- `backend/tests/contract/test_route_inventory.py` — `APPROVED_ROUTES`
  43 → 47 as one reviewed change (AH-9).
- `backend/tests/unit/` — **add** hermetic unit tests for the new
  capability (see §10).
- The additive per-feature live-HTTP suite pattern
  (`backend_test_iter*.py`) — **add** an M14 suite. Existing
  `backend_test*.py` suites are additive and kept (per `CLAUDE.md`).

**Conditional (only after separate `08` + ADR approval — see §9):**

- `backend/infrastructure/mongo/indexes.py` / the `ensure_indexes` path —
  **add** the two M14 indexes (`filing_analyses.analysis_identity_key`
  unique; `filing_analysis_jobs.active_identity_key` partial-unique +
  `created_at` TTL) and, if OAQ-3 warrants it, the optional
  `{doc_id:1, chunk_idx:1}` compound index. **Not touched without that
  separate approval.**

**Explicitly NOT modifiable** (see §7): `backend/agents/ingest.py`,
`chunk_text`, chunk size, overlap; `backend/agents/graph.py` /
`07_LangGraph_Architecture.md` topology; `backend/agents/llm.py` internals;
any existing route's shape or behaviour; `pytest.ini` `addopts`
(`-n 2 --dist loadscope`, per `CLAUDE.md`); any frontend file; Documents
58–65.

---

## 7. Areas That Remain Prohibited  *(required element 4)*

Prohibited even with implementation authorization; each requires its own
separate governance act (or is permanently out of scope):

| Prohibited | Why / gate | Source |
|---|---|---|
| Any change to `agents/ingest.py`, `chunk_text`, chunk size, or overlap | AC-2 — ingestion is untouched by M14 | Document 64 §6; Document 65 §6 AC-2 |
| Any LangGraph topology change — new graph, new node, `mode`-parameterised graph, or any edit to frozen `07` v1.0 | AC-1 / OAQ-7 — a topology change is a separate stop-and-CR governance item | Document 65 §7 OAQ-7, §23 item 6, §27.2 |
| Any new provider, new provider dependency, direct provider-SDK use, or default-provider change | AC-3 / OAQ-8 — LLM access stays through `agents/llm.py` `chat_*` | Document 64 §6; Document 65 §14, §27.3 |
| Any new embedding model, reranker, or vector store | OAQ-3 — reuse the existing hybrid scorer only | Document 65 §7 OAQ-3, §27.3 |
| Any new Redis usage or caching layer beyond the existing `JobStore` / `EventBus` | OAQ-6 — no new M14 caching architecture | Document 65 §7 OAQ-6, §12, §27.3 |
| Any new MongoDB collection, index, migration, schema change, or schema deployment **without** the separate `08_MongoDB_Data_Architecture.md` + ADR approval | AC-4 / §12.1 — see §9 | Document 64 §6 / §6.1; Document 65 §12.1, §23 item 7, §27.2 |
| Any change to an existing route's shape, status codes, or behaviour (`GET /filings`, the M13 `.../content` read, `/reports/*`, learning, compare-explain) | AC-5 — M14 is 100% additive; existing routes byte-for-byte unchanged | Document 64 §10 invariant; Document 65 §6 AC-5 |
| C-2 / structured filing-section extraction / persisting analysis-time section labels | Neither selected nor rejected; a §20.1 FAIL does not authorize it (§8.5) | Document 64 §16; Document 65 §8, §20.1, §27.2 |
| Conversational Filing Q&A, generic chatbot, conversational memory / session state, cross-filing / multi-filing analysis, durable research sessions, alerts / notifications / watchlists / background intelligence | Firm product-scope exclusions — not re-openable by architecture or implementation | Document 64 §6, §6.1 |
| Any comparison across documents for "Important Changes" (previous-filing comparison, cross-filing diff, trend analysis, implicit temporal comparison) | INV-IC — the Important Changes code path receives exactly one `doc_id`'s chunks and no other document input | Document 64 §8.1; Document 65 §23 item 5 |
| Any frontend change (`FilingViewer` "Filing analysis" variant, SSE `node` registration) | AH-6 — a separate frontend track requiring frontend sign-off | Document 64 §6; Document 65 §11, §23 item 11 |
| Any G8 / H-1 / G7 / judge / self-consistency-gate work; any change to `JUDGE_SELF_CONSISTENCY_GATE_VERSION` | Out of M14 scope | Document 62 §4; Document 64 §6 |
| Any edit to `pytest.ini` `addopts` | `-n 2 --dist loadscope` is assumed by the suites | `CLAUDE.md` |
| Any change to Documents 58–65 or to the M13 implementation | Cited, not modified | Document 64 §6; Document 65 §25 |
| Scope expansion of any kind | §12.1 | this document §12.1 |
| Architecture change of any kind without separate CTO governance | §12.2 | this document §12.2 |
| Commit | §12.3 — a separate CTO act after technical review | Document 62 §2.1 |
| Push | §12.4 — a separate CTO act after commit authorization | Document 62 §2.1 |

---

## 8. The §20.1 STOP/CONTINUE Validation Gate

Carried forward from Document 65 §20 / §20.1 **verbatim in substance**.
Implementation authorization does **not** clear it, pre-clear it, or set
its quality bar (§12.5).

### 8.1 The gate  *(required element 5)*

The Document 65 §20 section-location validation gate is a **hard
implementation-phase STOP/CONTINUE checkpoint** that the implementation
phase must reach and clear **before wiring the full four-output flow**. It
is the **first** implementation task after authorization (Document 65 §23
item 9), not a step deferred to the end.

- **CONTINUE** — only if the spike evidence meets the **CTO-agreed quality
  bar** (§8.2). Implementation then proceeds on the ratified OAQ-1(D)
  architecture; C-2 remains a future, independent roadmap item.
- **STOP** — if the spike evidence does **not** meet the bar, **or no bar
  has been set** (Document 65 §20: "Until a bar is set, the gate is **not**
  cleared").

**The quality bar is CTO-agreed, not proposed here.** This document invents
no numeric threshold. The CTO sets the bar (for example an acceptable
section-coverage rate for EDGAR filings and an acceptable
`insufficient_evidence` rate for non-EDGAR filings) **either** in the
implementation-authorization decision (§18) **or** when the spike evidence
is presented, **or** delegates it — as Document 65 §20 provides.

### 8.2 Required spike / evidence before CONTINUE  *(required element 6)*

An early spike runs analysis-time section location over a **representative
sample** of ingested filings — **at minimum: EDGAR 10-K, EDGAR 10-Q, BSE
annual report, plain-text (`POST /ingest/text`) ingest**.

The spike **must** produce, as a reviewer-checkable record:

1. For each output that depends on section location (**Risk Factors
   Digest**, **MD&A Digest**), per sampled filing: whether the located
   chunk range(s) actually cover that filing's real section, and the
   resulting output `state` (`complete` / `partial` /
   `insufficient_evidence`).
2. The same record for a **control set** of **Filing Summary** and
   **Important Changes** outputs.
3. The **aggregate `partial` / `insufficient_evidence` rate, split by
   filing source** (EDGAR vs non-EDGAR).

The spike evidence is presented to the CTO for the go/no-go. CONTINUE
requires the evidence to meet the CTO-agreed bar; absent a bar, the gate is
not cleared and the outcome is STOP.

### 8.3 Exact FAIL / STOP conditions  *(required element 7)*

The gate is **FAIL / STOP** when **any** of the following holds:

- the spike evidence does **not** meet the CTO-agreed quality bar; **or**
- **no** quality bar has been set (by the CTO in §18, at evidence
  presentation, or by delegation); **or**
- the required spike evidence (§8.2 items 1–3) is **not** produced in
  reviewer-checkable form.

Otherwise the gate is **CONTINUE**.

### 8.4 Required behaviour on FAIL  *(required element 8)*

On STOP, the implementation engineer **must**, per Document 65 §20.1:

1. **STOP at the gate.** No further M14 wiring proceeds.
2. **Not silently redesign the architecture.** A different section-location
   or analysis approach is a new architecture matter, not an engineer's
   unilateral substitution.
3. **Not implement C-2, structured-section extraction, or any equivalent,
   automatically.** The failure of this gate is **not** pre-authorization of
   C-2 in any form (§8.5).
4. **Not rewrite, re-sequence, or reinterpret Document 63.** The M14
   selection is untouched.
5. **Escalate to a separate CTO governance decision**, which — and only
   which — determines whether to (a) insert / re-sequence C-2 before
   completing C-1 (its own selection, contract, architecture,
   implementation chain), (b) adopt a different architecture path for the
   section-dependent outputs, or (c) accept a reduced-quality outcome for
   those outputs under the contract's honest `partial` /
   `insufficient_evidence` semantics.

**The failure path confers no authorization** — not C-2 work, not a schema
change, not implementation, not commit, not push. It produces a decision
*request* to the CTO and nothing else.

### 8.5 §20.1 FAIL does NOT automatically authorize or select C-2  *(required element 9)*

A §20.1 FAIL / STOP **does not**:

- authorize any C-2 / structured-section-extraction work;
- select C-2 as a milestone or re-sequence the roadmap;
- rewrite, re-sequence, or reinterpret Document 63;
- authorize a schema change, an ingestion change, a LangGraph change,
  implementation, commit, or push.

The failure path is **explicitly not** pre-authorization of C-2 in any form
(Document 65 §20, §20.1, §27.2 OAQ-1 / OAQ-2, §27.3).

### 8.6 C-2 remains subject to separate CTO governance  *(required element 10)*

**C-2 Structured Filing Extraction remains neither selected nor rejected.**
Whether C-2 is inserted / re-sequenced before completing C-1, or another
path is chosen, is decided **only** by a **separate CTO governance
decision** with its own selection → contract → architecture →
implementation chain (Document 63 §6; Document 64 §16; Document 65 §20.1
point 5, §27.2, §27.3). This document does not make, pre-empt, or
pre-authorize that decision.

---

## 9. MongoDB Physical Schema Realization Remains Separately Governed

### 9.1 The `08` + ADR path is still required  *(required element 11)*

Document 65's OAQ-5 was ratified as a **RATIFIED LOGICAL ARCHITECTURE
DECISION ONLY** (Document 65 §27.2). The **physical realization** of the
two-collection pattern — collection creation, index creation / modification,
migration, schema deployment, and any change to the canonical
`08_MongoDB_Data_Architecture.md` data architecture — **remains subject to
its separately required `08_MongoDB_Data_Architecture.md` + ADR governance
path**, a step **distinct from and subsequent to** both architecture
ratification and this implementation authorization (Document 64 §6 / §6.1;
Document 65 §12.1, §23 item 7, §27.2, §27.3).

Implementation authorization **does not** authorize schema realization
(§12.6). If the `08` + ADR chain withholds approval, the ratified
**fallbacks B → D → C** apply (Document 65 §12, §12.1):

- **B** — a single durable `filing_analyses` collection; job state stays in
  the existing `JobStore`.
- **D** — no new Mongo collection; a bounded Redis short-TTL result cache,
  `reused` best-effort.
- **C** — no persistence; recompute per request (contract-legal under
  Document 64 §12, wasteful).

### 9.2 No unauthorized collections, indexes, migrations, or schema changes  *(required element 12)*

The following **do not** become authorized by this implementation
authorization and remain owed to the `08_MongoDB_Data_Architecture.md` +
ADR chain, each as its own approval:

- creating MongoDB collections (`filing_analyses`,
  `filing_analysis_jobs`, or any other);
- modifying existing MongoDB collections;
- creating or modifying indexes (the analysis-identity unique index, the
  `active_identity_key` partial-unique index, the optional
  `{doc_id:1, chunk_idx:1}` compound index, or any other);
- migrations or backfills;
- changing the canonical data architecture
  (`08_MongoDB_Data_Architecture.md`);
- production deployment of any schema change.

Until that chain approves, engineering implements a fallback (B → D → C) and
touches **no** collection or index (§6 "Conditional" surface stays
untouched).

---

## 10. Testing and Validation Expectations  *(required element 13)*

The implementation phase must produce, at minimum:

**Gate first.**

- The §20.1 section-location **spike evidence package** (§8.2), produced and
  presented for the CTO go/no-go **before** the full four-output flow is
  wired (Document 65 §23 item 9).

**Hermetic unit tests** (`backend/tests/unit/`, TestClient + fake-Mongo):

- the four routes — creation / status / SSE / cancel — including
  `current_user` enforcement and `(ticker, doc_id)` 404 non-disclosure;
- the **deterministic citation validator** — marker-in-range, contiguity
  (§11.5), endpoint presence (§11.3), orphan-free `[n]` ⊆
  `cited_source_indices` ⊆ `sources` (§11.4), adjacency coalescing, and
  `complete` / `partial` / `insufficient_evidence` state assignment
  (§11.6 / §11.7) — asserted as **fully deterministic** (Document 65 §10,
  §16);
- **INV-IC** — the Important Changes path receives exactly one `doc_id`'s
  chunks and no other document input; absent self-described change language
  → `insufficient_evidence`, never fabricated (Document 64 §8.1);
- `insufficient_evidence` vs `partial` vs `complete` semantics never
  conflated; `complete` has non-empty `cited_source_indices` and zero
  ungrounded substantive claims;
- malformed / partial-ingest behaviour — analyse present well-formed chunks;
  every anchor references a present range; affected outputs → `partial` /
  `insufficient_evidence` with the ingest limit named; no fabrication
  (Document 64 §11.8);
- known filing with zero persisted chunks → honest "no analysable content"
  200-level result, not a 404, not fabricated (Document 64 §10);
- error taxonomy reuse with **zero additions**; no failure path returns raw
  provider text, an API-key fragment, or a stack trace (Document 64 §10,
  §15);
- BYOK fields thread through `set_llm_context` / `reset_llm_context` exactly
  as `_run_pipeline` / `_run_explanation` do; no separate credential path;
- `_id` / `embedding` never present in any response;
- analysis depends only on the filing + versioned prompt / schema / model —
  no session, no other filing (Document 64 §12).

**Contract / regression:**

- `test_route_inventory.py` exact-set guard passes at **47**; every existing
  route is **byte-for-byte unchanged**; `GET /filings` and the M13
  `.../content` read are unaffected (Document 64 §17; Document 65 §23
  item 8).
- `pytest.ini` `addopts` unchanged.

**Additive live-HTTP suite** — a new `backend_test_iter*.py`-style suite for
the M14 capability, additive, not superseding existing suites (`CLAUDE.md`).

**Validation facts are not authorizations.** A technical-review PASS is a
validation fact only; it is **not** commit authorization and **not** push
authorization (Document 62 §2.1; §12.3 / §12.4).

---

## 11. Security and Observability Requirements Inherited  *(required element 14)*

Inherited **verbatim** from the ratified contract (Document 64 §14, §15) and
the ratified architecture (Document 65 §17, §18). Implementation adds
nothing beyond these and weakens none of them.

### 11.1 Security (inherited)

- **AuthN:** `current_user` on all four routes; **no** new auth concept,
  decorator, or scope parameter.
- **AuthZ / corpus visibility:** the filing corpus has **no `user_id`** and
  is shared across tenants by design (`08` RI-5); any authenticated user may
  analyse any ingested filing — the same visibility `GET /filings` and the
  M13 read already have. **Job records are owner-scoped:** `GET` / `cancel`
  by a non-owner → **404** (non-disclosure).
- **BYOK:** existing policy verbatim — SSRF guard `assert_public_url` +
  `require_admin` for a custom `llm_base_url`; `llm_api_key` **never
  persisted, never logged** (`redact_key_from_error`).
- **Prompt injection (AH-8):** filing text is attacker-influenceable in
  principle (accepted residual risk — `10` §6.4 / SQ-1). Analysis prompts
  **MUST** frame filing content as untrusted **data, not instructions**;
  the deterministic anchor validator is the **second line of defence** — an
  injected "cite chunk 999" is dropped as out-of-range.
- **Output safety:** non-recommending constraint (no buy / sell / hold) is a
  safety boundary; every failure path emits only a **redacted generic
  message** — no raw provider text, key fragments, or stack traces.
- **No new stored credential; no fork/PR CI implication** — read + generate
  surface only.
- **DoS surface:** bounded by the shared `MAX_ACTIVE_JOBS` admission budget;
  a stricter per-kind limit is a possible later operational decision, not an
  architecture-stage need.

### 11.2 Observability (inherited — reuse only, no metric name frozen)

- **HTTP layer:** the four routes emit
  `alphascribe_http_requests_total{method,path,status}` +
  `..._duration_seconds` automatically.
- **LLM layer:** `llm_calls_total` / `llm_tokens_total` + `llm.attempt`
  spans — automatic via `chat_*`.
- **Job layer:** `MAX_ACTIVE_JOBS` admission / active-job gauges apply once
  `JobKind.FILING_ANALYSIS` exists.
- **Tracing:** one `pipeline.filing_analysis` span per run + child spans per
  step (`sectioning`, `analyzing`, `validating`) and per LLM call.
- **Required outcome signal (mechanism = AH-7):** it **MUST** be possible to
  distinguish, in aggregate, per-output
  `complete` / `partial` / `insufficient_evidence` / `failed` and per-run
  `completed` / `failed` / `cancelled` / `deadline_exceeded` — so a
  systemic section-location or grounding problem is visible, and to tune the
  OAQ-10 threshold and the OAQ-4 deadline. Exact metric name / shape →
  implementation.
- **Recommended:** rate of dropped / out-of-range `[n]` markers per run — a
  spike indicates prompt drift or injection.
- **No raw provider text, key material, or prompt content in logs or
  metrics.**

---

## 12. Authorization Boundaries and Prohibitions

### 12.1 Explicit prohibition on scope expansion  *(required element 15)*

The authorized scope is **exactly** §4 / §5. Engineering **must not** expand
it — no additional output, no output-selection parameter, no extra route, no
Filing Q&A affordance, no cross-filing capability, no persisted section
store, no new provider / model / retrieval / cache / LangGraph mechanism,
no frontend. Any expansion requires a **new** governance decision
(contract and/or architecture and/or a fresh implementation authorization).
The ratified Document 64 contract and Document 65 architecture bound the
work; this authorization does not widen them.

### 12.2 Explicit prohibition on architecture changes without separate governance  *(required element 16)*

Implementation authorization **is not** an architecture-change license. Any
deviation from the Document 65 ratified architecture — a different
section-location approach, a LangGraph graph / node, a new retrieval stack,
a different persistence design, a new provider architecture, a new caching
architecture — is a **new architecture matter** requiring its **own**
CTO governance (a Document 65 amendment or a successor pack, and for
LangGraph the stop-and-CR path). The engineer does **not** substitute
architecture unilaterally (Document 65 §20.1 point 2, §23 item 6, §24).

### 12.3 Explicit prohibition on commit authorization  *(required element 17)*

This proposal grants **no commit authorization**, and neither does the
CTO implementation-authorization decision it prepares. Commit is a
**separate, subsequent CTO act** taken **after** technical review
(Document 62 §2.1; Document 65 §25). Implementation authorization permits
work in the working tree only.

### 12.4 Explicit prohibition on push authorization  *(required element 18)*

This proposal grants **no push authorization**, and neither does the
CTO implementation-authorization decision it prepares. Push is a
**further separate CTO act** taken **after** commit authorization
(Document 62 §2.1; Document 65 §25).

### 12.5 Implementation authorization ≠ §20.1 gate clearance  *(required element 19)*

Issuing the implementation-authorization decision lets engineering **begin**
the bounded work — **starting with the §20.1 spike**. It does **not** clear,
pre-clear, or satisfy the §20.1 STOP/CONTINUE gate, and it does **not** set
the gate's quality bar. The gate is cleared **only** by spike evidence
meeting the CTO-agreed bar, assessed at the gate during implementation
(§8). `implementation authorization → §20.1 gate clearance` is **false**
(Document 65 §20, §20.1, §24, §27.3).

### 12.6 Implementation authorization ≠ MongoDB schema realization authorization  *(required element 20)*

Even fully authorized to implement, engineering **may not** create or modify
any MongoDB collection or index, run any migration or backfill, change the
canonical data architecture, or deploy any schema change **without** the
separate `08_MongoDB_Data_Architecture.md` + ADR approval (§9). Until that
approval, a fallback (B → D → C) applies.
`implementation authorization → MongoDB schema realization authorization` is
**false** (Document 64 §6.1; Document 65 §12.1, §24, §25, §27.2, §27.3).

---

## 13. Acceptance Criteria for the CTO Implementation-Authorization Decision

All of the following are **true and on record** (they are the basis on which
the CTO **issued** the decision — §18, 2026-09-02):

- [x] Document 64 is 🟢 CTO-RATIFIED (2026-08-31) — the frozen externally
      observable M14 contract (§4–§17), CQ-1 / CQ-2 / CQ-3 resolved.
- [x] Document 65 is 🟢 CTO-RATIFIED (2026-08-31, §27) — OAQ-3/4/6/7/8/9/10
      ratified; OAQ-1 / OAQ-2 conditional on §20.1; OAQ-5 logical decision
      only.
- [x] The exact implementation scope (§4), the exact authorized capabilities
      (§5), the modifiable surface (§6), and the prohibited surface (§7) are
      stated and traceable to Documents 64 and 65.
- [x] The §20.1 STOP/CONTINUE gate (§8.1), its required spike evidence
      (§8.2), its FAIL/STOP conditions (§8.3), the required behaviour on
      FAIL (§8.4), the "FAIL ≠ C-2 authorization" statement (§8.5), and the
      "C-2 stays under separate CTO governance" statement (§8.6) are carried
      forward unweakened.
- [x] The MongoDB schema-realization carve-out (§9) and the "no unauthorized
      collections / indexes / migrations / schema changes" statement (§9.2)
      are stated.
- [x] Testing / validation expectations (§10) and inherited security /
      observability requirements (§11) are stated.
- [x] The scope-expansion (§12.1), architecture-change (§12.2), commit
      (§12.3), push (§12.4), §20.1-clearance (§12.5), and
      schema-realization (§12.6) prohibitions are explicit.
- [x] **The CTO issues the M14 Implementation Authorization decision**
      (§18) — its own scope-bound act, setting the §20.1 quality bar.
      **ISSUED 2026-09-02** (§18; synchronized from the CTO companion record
      of the same date).
- [x] Technical review PASS — a validation fact, not an authorization.
      **Recorded 2026-09-02.**
- [ ] Commit authorization — a further separate CTO act. **NOT GRANTED
      HERE.**
- [ ] Push authorization — a further separate CTO act. **NOT GRANTED
      HERE.**

The implementation-authorization item is now satisfied (§18, 2026-09-02).
M14 status is **IMPLEMENTATION AUTHORIZED / COMMIT + PUSH NOT AUTHORIZED**:
the M14 implementation was produced under §18 and passed technical review,
but **no commit and no push is authorized** — each remains a further,
separate CTO act (§12.3 / §12.4).

---

## 14. What This Proposal Does NOT Do

- It does **not** itself grant authorization. §18 **records** the CTO's
  separate implementation-authorization decision of 2026-09-02 (implementation
  only); **commit and push are not authorized** by it.
- It does **not** ratify or amend Documents 62, 63, 64, or 65, and does not
  reinterpret or weaken them.
- It does **not** clear or pre-clear the §20.1 STOP/CONTINUE gate. §18
  records the CTO's finding that the agreed quality bar was met (0 FP /
  0 FN across the validated corpus; byte-identical over N=5); the gate
  definition in Document 65 §20.1 remains binding and is not amended here.
- It does **not** authorize any MongoDB collection, index, migration, or
  schema change.
- It does **not** select, reject, sequence, or pre-authorize C-2.
- It does **not** authorize any LangGraph, provider, retrieval, embedding,
  reranker, vector-store, Redis, caching, or frontend change.
- It does **not** create source, test, schema, migration, index, route,
  handler, node, prompt, retrieval, MongoDB, Redis, configuration,
  infrastructure, or frontend files.
- It does **not** stage, commit, push, rebase, merge, reset, restore, or
  clean Git state.
- It does **not** create any document beyond itself.

---

## 15. Repository / Working-Tree State (read-only inspection this session)

- **Publication state synchronized:** `HEAD` = `origin/main` =
  `f1c18c37f0650b4f66f1ad4b8b6a6e0579f67e09`; ahead/behind `0 / 0`. No `git`
  mutation was performed — no `add` / stage, `commit`, `push`, `amend`,
  `rebase`, `merge`, `reset`, `restore`, `stash`, or `clean`.
- **The working tree is NOT Git-clean.** It contains known, pre-existing,
  unrelated changes and artifacts this document does **not** stage, modify,
  rename, delete, or clean:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx   (pre-existing, unrelated test-flake hardening)
  ?? docs/backend_engineering/58_Post_M12_Backend_AI_Roadmap_Reconciliation.md   (untracked governance proposal)
  ?? docs/backend_engineering/62_Post_M13_Backend_AI_Roadmap_Reconciliation.md   (untracked; committing it is a separate CTO-authorized step)
  ?? docs/backend_engineering/63_M14_Formal_Milestone_Selection_Record.md         (untracked)
  ?? docs/backend_engineering/64_M14_Filing_Analysis_API_Contract.md              (untracked)
  ?? docs/backend_engineering/65_M14_Filing_Analysis_Architecture_Decision_Pack.md (untracked)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/          (untracked — M11 Phase H-1 evidence)
  ?? FROZEN
  ?? Semantic
  ?? _)
  ?? file
  ?? or
  ?? structured                                             (untracked zero-byte editor/hook artifacts)
  ```

- **This document adds one further untracked file — itself**
  (`docs/backend_engineering/66_M14_Filing_Analysis_Implementation_Authorization_Proposal.md`).
  It is **untracked and not yet version-controlled.** Committing it is a
  separate, subsequently CTO-authorized step.

---

## 16. Provenance and Constraints Honoured

- Created: 2026-08-31. Sole new file:
  `docs/backend_engineering/66_M14_Filing_Analysis_Implementation_Authorization_Proposal.md`.
  Document number 66 was verified free before creation (highest existing
  Backend & AI governance document was 65); the `backend_engineering/`
  series uses sequential integers, and Documents 62 §13 / 63 §4 §8 /
  64 §20 / 65 §25 §27.5 explicitly name "Separate M14 Implementation
  Authorization" as the required next governance artifact.
- No source code, test, schema, index, migration, route, handler, LangGraph
  node, prompt, retrieval / RAG, MongoDB, Redis, provider, configuration,
  infrastructure, or frontend file was created or modified.
- **Documents 58–65 were read, not modified.** Documents 64 and 65 remain
  🟢 CTO-RATIFIED and are treated as the authoritative contract and
  architecture; no clause of either is reinterpreted, weakened, or
  expanded.
- No `git` state was staged, committed, pushed, rebased, merged, reset,
  restored, or cleaned. The M13 commits `244ca5c` / `f1c18c3` were not
  inspected in a way that could alter them.
- No date, decision number, or authorization wording was fabricated. No
  retroactive authorization is claimed. No prior governance decision is
  re-interpreted or duplicated — Documents 62–65 are cited, not restated as
  new interpretations.
- **Synchronization, 2026-09-02:** §18 was filled in from the CTO M14
  implementation-authorization companion record issued 2026-09-02, and the
  header status line, the governance-chain THIS-entry, the §17 Revision
  History, and the closing statement were updated to match §18. No other
  section was altered. Documents 63–65 were **not** touched. No source,
  test, schema, index, migration, route, handler, LangGraph, prompt,
  retrieval, MongoDB, Redis, provider, configuration, infrastructure, or
  frontend file was created or modified by this synchronization, and no
  `git` state was staged, committed, pushed, rebased, merged, reset,
  restored, or cleaned.
- This document does not itself grant authorization; it now **records** the
  CTO's separate implementation-authorization decision of 2026-09-02 (§18).
  Commit and push remain further, separate, un-granted CTO acts.

---

## 17. Revision History

| Rev | Date | Change |
|---|---|---|
| Draft 1 | 2026-08-31 | Initial M14 Implementation Authorization Proposal. Defines the exact implementation scope (§4), exact authorized capabilities (§5), modifiable source / test / configuration surface (§6), prohibited surface (§7), the §20.1 STOP/CONTINUE gate with required spike evidence, FAIL/STOP conditions, required behaviour on FAIL, and the "FAIL ≠ C-2 authorization" / "C-2 stays under separate CTO governance" statements (§8), the MongoDB schema-realization carve-out (§9), testing / validation expectations (§10), inherited security / observability requirements (§11), and the scope-expansion / architecture-change / commit / push / §20.1-clearance / schema-realization prohibitions (§12). Traceable to Documents 64 and 65 throughout; neither modified. **Status: 🟠 PROPOSED — CTO IMPLEMENTATION-AUTHORIZATION DECISION REQUIRED. NOT AUTHORIZED.** |
| Authorization Recorded | 2026-09-02 | §18 synchronized with the CTO M14 implementation-authorization companion record issued 2026-09-02: Decision **🟢 AUTHORIZED** within Documents 64 / 65 and §4 / §5 bounds; §20.1 quality bar recorded as met (0 false positives / 0 false negatives across the validated corpus, byte-identical over N=5 runs per validated filing, unestablished end boundary → `partial` not `complete`); the nine CTO conditions / carve-outs recorded verbatim in substance (incl. no MongoDB schema / collection / index / migration authorization, fallback-C L-2 / L-3 ceiling accepted, `ponytail:` ceilings accepted, C-2 unchanged, H-2 / M11 Phase H-1 / H-3 excluded from M14 scope). **Commit and push remain separate, un-granted CTO acts.** The header status line, the governance-chain THIS-entry, and the closing statement were synchronized to match §18; no other section altered. Documents 63–65 not touched; no source, test, schema, index, migration, route, or infrastructure file created or modified by this synchronization. **Status: 🟢 IMPLEMENTATION AUTHORIZED (2026-09-02) — COMMIT / PUSH NOT AUTHORIZED.** |

---

## 18. CTO Implementation-Authorization Decision

**🟢 AUTHORIZED — 2026-09-02.** Synchronized here from the CTO
implementation-authorization companion record issued 2026-09-02 (the
governance channel). This block **records** that decision verbatim in
substance; it does not restate, re-interpret, weaken, or expand it, and it
grants nothing beyond it.

| Field | Value |
|---|---|
| Decision | **🟢 AUTHORIZED** — implement the M14 Filing Analysis capability. |
| Date | 2026-09-02 |
| Authority | CTO governance decision for AlphaScribe vNext M14 Filing Analysis. |
| Scope | Implementation of the M14 Filing Analysis capability within the bounds established by Documents 64 and 65 and the implementation constraints established by Document 66 §§1–17 (exact scope §4; exact authorized capabilities §5; modifiable source / test / configuration surface §6; prohibited surface §7). |
| §20.1 quality bar | The implementation is authorized on the basis that the bounded OAQ-1(D) realization validation has **passed** the agreed §20.1 bar: representative target-present and target-absent filings were correctly discriminated with **0 false positives and 0 false negatives** across the validated corpus, and the realization was **byte-identical across N=5 repeated runs** for each validated filing. Where an end boundary cannot be established reliably, the implementation **must represent the affected coverage as `partial`**, not claim `complete` coverage. |
| Conditions / carve-outs | **1.** Authorization is limited to the M14 Filing Analysis implementation described by Documents 64–66. **2.** The fixed four-output roster and contract semantics of Document 64 remain authoritative. **3.** **No** MongoDB schema, collection, index, or migration realization is authorized by this decision; any such realization requires the separately mandated `08_MongoDB_Data_Architecture.md` + ADR governance chain and authorization. **4.** The currently permitted fallback-C process-local persistence is authorized within the documented L-2 / L-3 operational ceilings; durable persistence is **not** implied by this decision. **5.** The bounded OAQ-1(D) realization does **not** constitute a claim of universal filing-section-detection accuracy beyond the validated corpus and the documented heuristic / LLM architecture. **6.** Known operational and heuristic ceilings documented by `ponytail:` markers remain accepted limitations of this implementation unless separately revisited. **7.** M14 implementation authorization does **not** authorize commit, push, merge, release, deployment, or any subsequent milestone. **8.** Unrelated working-tree changes — the pre-existing `web/features/workspace-home/ui/CompanySearch.test.tsx` modification (H-2) and the M11 Phase H-1 artifacts under `backend/evaluation/self_consistency/phase_h1_generalization_matrix/` — are excluded from M14 scope. **9.** Generated zero-byte shell-pollution artifacts (H-3) are not repository scope and must remain excluded from the M14 changeset. |
| Commit authorization | **NOT granted by this decision** — a further, separate CTO act after technical review (§12.3). |
| Push authorization | **NOT granted by this decision** — a further, separate CTO act after commit authorization (§12.4). |
| MongoDB schema realization | **NOT granted by this decision** — requires the separate `08_MongoDB_Data_Architecture.md` + ADR chain (§9). |
| CTO disposition | M14 implementation may proceed to final commit-readiness review within the above bounds. |

The M14 implementation was produced under this authorization and has passed
CTO technical review. Commit and push remain **separate, un-granted CTO
acts** (§12.3 / §12.4); this block does not confer either.

---

**NO SOURCE, TEST, SCHEMA, INDEX, MIGRATION, ROUTE, HANDLER, LANGGRAPH NODE,
PROMPT, RETRIEVAL / RAG, MONGODB COLLECTION, REDIS, PROVIDER, CONFIGURATION,
INFRASTRUCTURE, OR FRONTEND FILE WAS CREATED OR MODIFIED TO PRODUCE OR
SYNCHRONIZE THIS DOCUMENT. THIS DOCUMENT NOW RECORDS THE 🟢 M14
IMPLEMENTATION-AUTHORIZATION DECISION ISSUED 2026-09-02 (§18), SYNCHRONIZED
FROM THE CTO COMPANION RECORD OF THE SAME DATE; IT GRANTS NOTHING BEYOND
THAT DECISION, AND COMMIT / PUSH ARE NOT PART OF IT. DOCUMENT 64 IS THE
🟢 CTO-RATIFIED M14 API CONTRACT AND DOCUMENT 65 IS THE 🟢 CTO-RATIFIED M14
ARCHITECTURE; NEITHER IS MODIFIED, REINTERPRETED, WEAKENED, OR EXPANDED
HERE. THE §20.1 STOP/CONTINUE VALIDATION GATE REMAINS BINDING AND IS NOT
CLEARED OR PRE-CLEARED BY IMPLEMENTATION AUTHORIZATION; ITS QUALITY BAR IS
CTO-AGREED, NOT SET HERE. A §20.1 FAIL DOES NOT AUTHORIZE OR SELECT C-2; C-2
REMAINS NEITHER SELECTED NOR REJECTED AND SUBJECT TO SEPARATE CTO
GOVERNANCE. MONGODB PHYSICAL SCHEMA REALIZATION (COLLECTIONS, INDEXES,
MIGRATIONS, SCHEMA CHANGES) REMAINS ON THE SEPARATE
`08_MongoDB_Data_Architecture.md` + ADR PATH; FALLBACKS B → D → C APPLY IF
WITHHELD. FILING Q&A / CHATBOT / CONVERSATIONAL MEMORY / CROSS-FILING /
DURABLE SESSIONS / ALERTS REMAIN OUT OF M14 SCOPE. NO LANGGRAPH, PROVIDER,
RETRIEVAL, EMBEDDING, RERANKER, VECTOR-STORE, REDIS, CACHING, OR FRONTEND
CHANGE IS AUTHORIZED. IMPLEMENTATION AUTHORIZATION ≠ §20.1 GATE CLEARANCE ≠
MONGODB SCHEMA REALIZATION AUTHORIZATION ≠ COMMIT AUTHORIZATION ≠ PUSH
AUTHORIZATION. NO SCOPE EXPANSION. NO ARCHITECTURE CHANGE WITHOUT SEPARATE
GOVERNANCE. DOCUMENTS 58–65 NOT MODIFIED. NO STAGE. NO COMMIT. NO PUSH. NO
MERGE / REBASE / RESET / RESTORE / CLEAN. THE NEXT GOVERNANCE ACTS ARE THE
CTO'S SEPARATE COMMIT AUTHORIZATION (AFTER TECHNICAL REVIEW) AND, AFTER
THAT, PUSH AUTHORIZATION — NEITHER GRANTED BY THE §18 DECISION.**
