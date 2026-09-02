# 64 — M14 Filing Analysis API Contract

**Status:** 🟢 **CTO-RATIFIED (2026-08-31) — M14 FILING ANALYSIS API
CONTRACT.** The CTO ratified this document as the M14 Filing Analysis API
Contract on 2026-08-31 (full record: §22). **M14 = C-1 Filing Analysis**
(formally selected by Document 63). Ratification **freezes the externally
observable M14 contract** (§4–§17, per the §5.1 boundary) — the four-output
roster, the fixed full output set with no client-selectable parameter, the
per-output flat cited narrative representation (§8.2), the Important Changes
filing-local invariant (INV-IC, §8.1), and the citation / provenance
requirements §11.1–§11.9 — with **CQ-1 / CQ-2 / CQ-3 resolved by the separate
CTO decision of 2026-08-31** (§18). **Ratification of this contract does NOT
ratify any architecture, does NOT authorize implementation, and grants no
commit or push authorization** — each is a separate, subsequent CTO act
(§20, §22). Every §19 item (**OAQ-1…OAQ-10**) remains an **open architecture
question**, not a contract decision; **C-2** remains neither selected nor
rejected (architecture may determine sequencing); **Filing Q&A** remains
excluded from M14. It makes **no architecture decision** — every
architecture-level question it touches is recorded as an **Open Architecture
Question / Architecture Handoff item** (§19), not resolved.
**Governance ladder (each a distinct CTO act; none confers the next):**
`M14 formally selected` (Document 63, done) ≠ `contract ratified` (this
document, **done 2026-08-31 — §22**) ≠ `architecture ratified` (a later
Architecture Decision Pack — Document 65 — **not created**, **not
authorized by this ratification**) ≠ `implementation authorized` ≠
`commit authorized` ≠ `push authorized`.
**Type:** API / contract decision artifact (research / design / governance
only — no source code, test, schema / migration / index, endpoint, route,
LangGraph node, retrieval / RAG change, MongoDB collection, Redis usage,
provider selection, or frontend file created or modified to produce it).
**Depends on (CTO-ratified, unmodified — read, not altered):**
[62_Post_M13_Backend_AI_Roadmap_Reconciliation.md](62_Post_M13_Backend_AI_Roadmap_Reconciliation.md)
(C-1 Filing Analysis = the ratified preferred roadmap direction; §6 C-1, §7,
§9, §10) and
[63_M14_Formal_Milestone_Selection_Record.md](63_M14_Formal_Milestone_Selection_Record.md)
(the separate CTO decision formally selecting M14 = C-1 Filing Analysis).
**Companion (NOT created here, required before implementation):** an
*M14 Filing Analysis Architecture Decision Pack* — it, not this document,
resolves the chunk-vs-section question, the C-2 sequencing question, RAG /
retrieval, persistence, LangGraph topology, model / provider, caching, Redis,
and the frontend integration pattern (§16, §19).
**Structural precedent (cited, unmodified):**
[59_M13_Filing_Content_Read_API_Contract.md](59_M13_Filing_Content_Read_API_Contract.md)
(the M13 contract — its `(ticker, doc_id)` filing identity, its error-envelope
reuse, its exclusions discipline, and its OD / AG register are reused here),
[43_M9_API_Contract_Decision_Pack.md](43_M9_API_Contract_Decision_Pack.md)
(the most recent contract for an **LLM-backed, grounded, cited** capability —
its job / status / SSE / cancel route family, its citation contract, and its
partial-evidence contract are the closest genre precedent), and
[42_M9_Product_Decision_Explanation_Semantics.md](42_M9_Product_Decision_Explanation_Semantics.md)
(the grounded / cited / non-recommending AI-output semantics pattern).
**Roadmap position:** Document 62 §9 recommends C-1 as the preferred
direction; Document 63 formally selects it as M14. This contract was the
next authorized governance activity after Document 63 (Document 62 §13;
Document 63 §8) — "selection authorizes progression to the
contract-governance stage only" — and is now CTO-ratified (§22); the next
authorized activity is the Architecture Decision Pack (Document 65).
**Date:** 2026-08-30.
**Revision R1 (2026-08-30) — CTO conditional-pass revision, pre-ratification.**
CTO review result: **CONDITIONAL PASS — CONTRACT REVISION REQUIRED BEFORE
RATIFICATION.** This revision: (1) adds §5.1 stating exactly what a
ratified contract freezes (externally observable product / API behaviour)
versus what stays an Architecture Decision Pack concern (persistence,
caching, retrieval strategy, execution topology, provider / model
selection, and similar mechanisms) unless a ratified clause explicitly
requires a mechanism; (2) marks **CQ-1** and **CQ-2** as
**ratification-blocking** and **CQ-3** as **resolve-before-ratification and
state explicitly in the final API contract** (§17, §18, §21) *(all three
later RESOLVED by the CTO on 2026-08-31 — see the CTO Decisions note
below)*; (3) promotes
former CQ-5 to a **contract invariant INV-IC** — "Important Changes" is
filing-local only (§6, §8); (4) expands §11 into testable subsections
§11.1–§11.9 (claim definition, filing-local evidence, anchor
representation, citation reuse, contiguity, insufficient- / partial-
evidence, malformed / partial-ingest) **without** selecting an
anchor-discovery mechanism (that stays OAQ-9). **No scope change. No
architecture decision. No implementation / commit / push authorization.
Status unchanged: 🟡 PROPOSED — CTO DECISION REQUIRED. NOT RATIFIED.**
**Revision R2 (2026-08-30) — CTO conditional-pass revision, pre-ratification.**
Fixes an internal governance contradiction: §6 listed persistence
mechanisms (new MongoDB collection / index / schema / migration) as flat
M14 exclusions while §19 OAQ-5 leaves the persistence model open — the
former could be read as foreclosing the latter. R2 reframes §6's
**mechanism-naming** exclusions (persistence, new retrieval infrastructure,
LangGraph topology, ingestion, provider) as "**not authorized by this
contract / not an M14 deliverable**", adds **§6.1** (how to read those
exclusions) and **§19.3** (a contradiction sweep verifying every OAQ stays
genuinely open to the Architecture Decision Pack), and clarifies OAQ-1 /
OAQ-3 / OAQ-5 / OAQ-7 / OAQ-8 cells accordingly. **Persistence is not
decided or pre-approved here; a design needing a new collection / index /
schema / migration would go through architecture ratification plus the
normal schema-change governance, never as pre-authorized by Document 64.**
Product-scope exclusions (Filing Q&A, chatbot, cross-filing, Durable
Sessions, alerts, INV-IC, C-2 as a delivered M14 feature, G8 / H-1 / G7)
are **unchanged and remain firm**. **No scope change. No architecture
decision. No implementation / commit / push authorization. Status
unchanged: 🟡 PROPOSED — CTO DECISION REQUIRED. NOT RATIFIED.**
**CTO Decisions applied (2026-08-31) — pre-ratification.** The three
outstanding contract questions were resolved by the CTO and folded into the
contract body: **CQ-1** — the M14 output roster is exactly four outputs
(Filing Summary, Risk Factors Digest, MD&A Digest, Important Changes), no
others (§8); **CQ-2** — a **fixed full output set**, **no** client-selectable
output parameter — a request asks for Filing Analysis of the filing and
receives all four outputs (§7, §9.2); **CQ-3** — the per-output response
representation is Document 43's **flat cited narrative**: each output is
`narrative` + `sources[]` + `cited_source_indices` (§8, §9.3, §11.3),
stated explicitly and testably. These are product / API-contract decisions
only. **No architecture decision** — chunk-vs-section, retrieval / RAG,
persistence, caching, execution topology, LangGraph topology, and provider /
model selection all remain OAQ-owned and open (§19); OAQ-1…OAQ-10 unchanged;
C-2 neither selected nor rejected; Filing Q&A still excluded. **Status
unchanged: 🟡 PROPOSED — CTO DECISION REQUIRED. NOT RATIFIED** — the CTO
performs the separate contract-ratification act after reviewing this updated
proposal. **No implementation / commit / push authorization.**
**CTO Ratification (2026-08-31).** The CTO ratified this document as the
**M14 Filing Analysis API Contract** — status `🟡 PROPOSED` → `🟢
CTO-RATIFIED`. Full record: **§22**. Ratification freezes the externally
observable M14 contract (§4–§17); CQ-1 / CQ-2 / CQ-3 stand resolved by the
separate CTO decision of 2026-08-31. It does **not** ratify architecture,
authorize implementation, or grant commit / push authorization; OAQ-1…OAQ-10
remain open architecture questions; C-2 stays neither selected nor rejected;
Filing Q&A stays excluded. **No `docs/backend_engineering/65` created; no
architecture work begun.** Cumulative provenance: **CTO Revisions R1–R2 +
CTO Decisions 2026-08-31 applied; CTO-RATIFIED 2026-08-31 (§22).**

---

## 0. What This Document Is and Is Not

**Is:** the CTO-ratified M14 API contract (§22) for one bounded, grounded,
filing-scoped AI analysis capability — the API surface's identity and auth
model, the
semantic shape of its inputs and outputs, its citation / provenance
requirement, its validation and error semantics, its determinism and
observability expectations, its acceptance criteria, and a complete register
of what the architecture phase must still decide. Structured after Documents
59 and 43.

**Is not:**

- an implementation, implementation authorization, commit authorization, or
  push authorization;
- an **architecture decision** — it does not choose chunk-vs-section
  representation, whether C-2 must precede C-1, whether RAG / retrieval is
  introduced, the retrieval algorithm, the persistence model, any MongoDB
  collection / index / schema, LangGraph topology, model / provider
  selection, a caching strategy, Redis usage, or any frontend
  implementation. Where any of these bears on the contract it is filed in
  §19 as an **Open Architecture Question (OAQ)** or **Architecture Handoff
  (AH)** item, explicitly unresolved;
- an **architecture decision pack**, an implementation authorization, or a
  commit / push authorization — this document is the **CTO-ratified M14 API
  contract** (§22), and that ratification grants **none** of those: the §9
  **endpoint form** (sync vs async, route family, SSE) stays architecture
  (OAQ-4), as does persistence (OAQ-5) and every other §19 item. CQ-1 / CQ-2
  / CQ-3 are resolved by the separate CTO decision of 2026-08-31 (§8, §8.2,
  §18);
- a Filing **Q&A** design, a conversational / chatbot design, a cross-filing
  analysis design, a durable-research-session design, or an
  alerts / background-intelligence design — all are **out of M14 scope**
  (§6);
- a reopening of M13, H-1, or G8; a re-ratification of Document 62; or an
  amendment to Documents 58–63.

---

## 1. Governance Preconditions (verified this session, read-only)

| Fact | Source | Verified state |
|---|---|---|
| M13 — Filing Content Reading | Document 62 §1.1; `git log` | **COMPLETE / PUBLISHED** (`244ca5c`; governance reconciliation `f1c18c3`); `HEAD = origin/main = f1c18c3`, `0/0` |
| Document 62 | its §16 | **CTO-RATIFIED (2026-08-30)** — authoritative Post-M13 roadmap position; C-1 = **preferred roadmap direction**, **not** an M14 selection by itself |
| Document 63 | its §1, §Status | **M14 = C-1 Filing Analysis — FORMALLY SELECTED** (separate CTO decision, 2026-08-30); contract / architecture / implementation / commit / push all **NOT** authorized |
| chunk-vs-section question | Document 62 §7; Document 63 §6 | **OPEN** — belongs to the M14 contract / architecture phase |
| C-2 Structured Filing Extraction | Document 62 §6 C-2, §8; Document 63 §6 | **NOT selected as M14; NOT rejected.** May become a technical sequencing prerequisite — an open architecture decision |
| Filing Q&A | Document 62 §6 C-1(2), §10; Document 63 §7 | **Excluded** from C-1 / M14; a later, separately scoped capability |
| Durable Research Sessions | Document 62 §6 C-4; Document 63 §7 | `BLOCKED`; **out of M14 scope** |
| G8 | Document 62 §4.2 | **BLOCKED / CARRIED FORWARD** — unchanged, not touched here |
| H-1 | Document 62 §4.1 | **CLOSED WITH GOVERNANCE FOLLOW-UP** — unchanged, not touched here |
| M14 contract / architecture / implementation | Document 63 §5 | **NONE proposed or ratified** before this document. This document is the M14 API **contract** — proposed here, **CTO-ratified 2026-08-31** (§22). M14 architecture and implementation remain **not proposed / not authorized**. |

No governance state above is changed by this document. It is cited, not
re-decided.

---

## 2. Existing Architecture Dependency (inspected this session, cited — not modified)

Every contract choice in §4–§17 is derived from, and constrained by, this
table. **No file below is modified by this document.**

| Component | File / location | Verified finding |
|---|---|---|
| Persisted filing text | `backend/agents/ingest.py::ingest_document`; Document 59 §1 | Ingest chunks raw text (`chunk_text`, `chunk_size=900`, `overlap=120`) → `filing_chunks` rows (`{doc_id, ticker, source, chunk_idx, text, created_at, embedding?}`) + one `filings` metadata row (`{doc_id, ticker, company_name?, source, num_chunks, char_count, created_at}`). Raw text truncated at `200_000` chars before chunking. **Chunks carry `chunk_idx` + `text` only — no section identity, no headings** (Document 59 §1; `FilingViewer.tsx`: "they carry no headings of their own"). |
| Filing identity (ratified) | Document 59 §3.1 (CTO-RESOLVED, OD-1) | A filing is addressed by **`ticker` + `doc_id` together**, company-namespaced. `doc_id` is the `uuid4` per-filing key; `ticker` is the required namespacing segment. A `doc_id` under a different `ticker` "does not exist for the requested company" → 404. |
| M13 read endpoint | `backend/server.py`; Document 59 | `GET /api/companies/{ticker}/filings/{doc_id}/content` returns the ordered `content.chunks: [{chunk_idx, text}]` envelope + `filings` metadata, verbatim. **RAG-free, LLM-free** by design (Document 59 §12). |
| Filing metadata list | `backend/server.py` (`GET /filings`) | `{"filings": [<metadata rows>]}`, `current_user` required, unknown ticker → `200 {"filings": []}` (no 404). |
| LLM access boundary | `backend/agents/llm.py`; `CLAUDE.md` | **All** LLM access is `chat_text` / `chat_json` only — multi-provider (Gemini / OpenAI-compatible / Anthropic), per-request key + base_url via a `contextvar`. Nodes must not call provider SDKs directly. Provider→model mapping in `infrastructure/llm/registry.py`. |
| Async job / stream infra | `backend/application/jobs.py`; `backend/domain/models.py`; `infrastructure/streaming/sse.py`; Document 43 §3 | `JobKind` (`RESEARCH`, `LEARNING`, `COMPARISON_EXPLANATION`), `JobStatus` (`QUEUED·RUNNING·COMPLETED·FAILED·CANCELLED`), one shared `MAX_ACTIVE_JOBS` admission budget, generic `sse_response()` (unnamed `data:` frames, `: keepalive`, terminal `event: end`). Every existing AI-generating surface (Research, Learning, Comparison-Explanation) is an **async job with optional SSE + cancel**, not a synchronous call. |
| Retrieval | `backend/agents/retrieval.py`; Document 62 §5.3 | Hybrid BM25 + dense (`fastembed`) + rerank, **consumed only by the report pipeline's `retriever` node** — not wired to any filing-scoped surface. |
| LangGraph pipeline | `backend/agents/graph.py`; `07_LangGraph_Architecture.md` (🔒 v1.0) | `retriever → (extractor ‖ tone) → synthesizer → fact_checker` + conditional `fact_check_router`. The architecture is **frozen**; any topology change is a stop-and-CR item (`CLAUDE.md`; Document 62 R-9). |
| Citation convention | `backend/agents/learning_nodes.py::_postprocess_citations`; `web/.../schemas.ts`; Document 43 §10 | Inline `[n]` markers in the narrative + a parallel indexed `sources` list + a separate `cited_source_indices` (actually-referenced subset). Grounding law: zero grounded citations = **failed** generation, not a degraded success (Document 42 §7). |
| `SourceReference` component | `docs/design/09_Component_Inventory.md`; Document 43 §10 | `{label, target}`. `FilingViewer` usage rule: **"Analysis always anchored to the filing (source traceability)."** |
| `FilingViewer` (frozen spec) | `docs/design/09_Component_Inventory.md` §FilingViewer; `web/components/research/FilingViewer.tsx` | **Variants: "Filing content", "Filing analysis".** M13 built "Filing content" only. "Filing analysis" — `analysis`, `source anchors`, `AI Thinking / Streaming` states, `Empty (uncovered)` — is unbuilt and is what M14 targets on the frontend (frontend work itself is **out of M14 backend scope** — AH-6). |
| Product roadmap line | `docs/master-plan/03_Feature_Roadmap.md` §"SEC Filing Analysis" | Named roadmap deliverables: **10-K Analysis, 10-Q Analysis, Filing Summaries, Risk Factors, Management Discussion, Important Changes.** M14's slice of this line is the **four outputs fixed in §8** (Filing Summary, Risk Factors Digest, MD&A Digest, Important Changes). |
| Error envelope + taxonomy | `backend/app/api/errors.py`; `backend/domain/errors.py`; Document 43 §3 | `{"detail": <msg>, "type": <code>}`. `NotFoundError`(404), `ValidationError`(422), `ConflictError`(409), `AuthorizationError`(403), `RateLimitedError`(429), `DeadlineExceededError`(504), `InfrastructureError`(502), `LLMProviderError`(502). |
| Auth | `backend/server.py` — `Depends(current_user)` on every tool route | One dependency, identical everywhere. The corpus (`companies`, `filings`, `filing_chunks`) **has no `user_id`** (`08` RI-5 — shared by every tenant by design). `GET /filings` and the M13 content read apply **no ownership scoping**. |
| Route-inventory contract | `backend/tests/contract/test_route_inventory.py` | Exact-set guard, `assert len(APPROVED_ROUTES) == 43`. Additive-only discipline; each new route is one explicit entry. Updating it is part of a **separately authorized** implementation, not this contract. |
| Observability | `backend/infrastructure/observability/`; Document 59 §11 | Every route already emits `alphascribe_http_requests_total{method,path,status}` + `alphascribe_http_request_duration_seconds{method,path}`. Per-endpoint OTel spans + module `logger`. `llm_calls_total` / `llm_tokens_total` are automatic via `chat_*`. |

---

## 3. Problem Definition

| Capability | State today | Evidence |
|---|---|---|
| Ingest + persist filing text (chunked) | **Exists** (M13 and earlier) | `filing_chunks` rows with `chunk_idx`; `filings` metadata |
| Read one filing's text (HTTP) | **Exists** (M13) | `GET /companies/{ticker}/filings/{doc_id}/content` |
| AI analysis scoped to **one specific filing** | **Missing** | No route, no contract, no node; Document 62 §6 C-1(1): "no filing summary, no Risk-Factors digest, no MD&A digest, no 'important changes' for one document" |
| `FilingViewer` "Filing analysis" variant | **Missing** | Frozen component spec; only "Filing content" shipped in M13 |
| Section identity within a filing | **Missing** | Chunks are ~900-char slices with no headings (Document 59 §1); "which chunks are the Risk Factors" is unknown → the chunk-vs-section question (Document 62 §7) |

**What a user cannot do today:** get a grounded, filing-specific summary,
Risk-Factors digest, MD&A digest, or "what changed" read for a single 10-K /
10-Q, anchored to that filing's own text. The whole-company AI brief
(`/reports/generate`) and the raw filing text (`.../content`) both exist;
nothing bridges them at the single-filing level.

---

## 4. Purpose and User Value  *(contract item 1)*

**Purpose.** Deliver the first bounded slice of the roadmap's "SEC Filing
Analysis" line: grounded AI analysis of **one** ingested filing, anchored to
that filing's own persisted text, presented through the frozen `FilingViewer`
"Filing analysis" variant.

**User value.** Highest of the Document 62 candidates (Document 62 §8
ranking): it turns
the raw filing text M13 made readable into a usable research artifact —
a filing summary and section digests a user would otherwise spend an hour
extracting by hand — while staying inside the "Trusted AI" pillar (every
claim traceable to a `chunk_idx` range in the filing). It completes the
unbuilt half of the `FilingViewer` spec and establishes the grounded
single-filing-analysis foundation that a **later, separately scoped** Filing
Q&A capability could build on (Q&A itself is **not** in M14 — §6).

**Non-value / explicitly not claimed:** M14 is not a research-time-saver for
*cross-filing* work, not a monitoring capability, and not a conversational
assistant. Its value is bounded to "one filing, fixed analysis outputs,
fully cited".

---

## 5. M14 Scope — Bounded Filing Analysis  *(contract item 2)*

**In scope for M14 (this ratified contract):**

1. A backend capability that, given one filing identified by the ratified
   `(ticker, doc_id)` pair (§2; Document 59 §3.1), produces a **fixed,
   bounded set of grounded analysis outputs** for that filing (§8).
2. An authenticated HTTP surface for requesting that analysis and retrieving
   its result, additive to the existing route inventory, `current_user`
   gated, using the existing `{detail, type}` error envelope (§9, §10).
3. A **contract-level citation / provenance requirement**: every material
   claim in every analysis output is anchored to the filing's own content
   (§11).
4. Honest **insufficient-evidence** and **empty** semantics — the capability
   never fabricates analysis for a filing it cannot ground against (§8, §10).
5. Reuse of the existing LLM access boundary (`agents/llm.py` `chat_*`) and
   the existing BYOK request-field convention (§9, §15). This is a **fourth
   LLM surface** after Research, Comparison-Explanation, and Learning
   (Document 62 §5.3, R-9).

**Bounded by construction — M14 is one filing, fixed outputs, fully cited.**
Anything requiring conversation, memory, multiple filings, new ingestion,
new retrieval infrastructure, or new persistence is either excluded (§6) or
deferred to the architecture phase (§16, §19) — never assumed in by this
contract.

**Not decided by this contract (architecture phase — §19):** whether the
analysis operates over M13's existing unstructured chunks or requires
structured section boundaries first (chunk-vs-section, OAQ-1); whether C-2
must precede C-1 (§16, OAQ-2); whether retrieval / RAG is introduced
(OAQ-3); whether the endpoint is synchronous or an async job + stream
(OAQ-4); whether analysis output is persisted (OAQ-5); LangGraph topology
(OAQ-7); model / provider (OAQ-8).

### 5.1 Contract-vs-architecture boundary — what ratification freezes, and what it does not

**A ratified M14 contract freezes only *externally observable* product / API
behaviour** — the things a client, a reviewer, or a test can see from
outside the backend:

- the capability boundary and exclusions (§5, §6), including the
  Filing Q&A / chatbot / cross-filing / durable-sessions / alerts exclusions
  and the "fixed analysis outputs only" rule;
- the input identity and required filing context expressed as *observable
  behaviour* (§7) — `(ticker, doc_id)` addressing, "reads only this filing's
  own persisted text", "no acquisition / ingest trigger", "no provider call
  for filing data";
- the fixed output roster and output semantics (§8), including the
  **Important Changes** filing-local invariant (INV-IC, §8.1);
- the citation / provenance obligations (§11) — every substantive factual
  claim carries a valid, filing-local, human-verifiable anchor;
- validation, status codes, and error envelope (§10);
- the client-observable determinism / reproducibility guarantees (§12);
- the security / access-control posture (§15);
- the observability *signals that must exist* (§14) — not their metric
  names.

**A ratified M14 contract does NOT freeze, and the *M14 Filing Analysis
Architecture Decision Pack* remains the sole authority for:** the
persistence model (whether analysis is stored at all, and where — OAQ-5);
caching and Redis usage (OAQ-6); retrieval / RAG strategy and any retrieval
algorithm (OAQ-3); execution topology — synchronous vs async job, SSE, and
any LangGraph graph / node change (OAQ-4, OAQ-7); provider / model / tier
selection beyond BYOK passthrough (OAQ-8); the chunk-vs-section
representation and the anchor-discovery mechanism (OAQ-1, OAQ-9); storage,
collection, and index design (AH-2); and every other internal mechanism.

**Rule for reading this document.** Where a clause states an *externally
observable* requirement that constrains implementation (for example
"outputs must be grounded and cited", "insufficient evidence must be
surfaced honestly", "no fabricated content"), that clause is a **behavioural
requirement**, not an architecture decision — the mechanism that satisfies
it stays open in §19. A mechanism is frozen by this contract **only** where
a clause names it explicitly as *required* (for example the
`chunk_idx`-range anchor *representation* floor in §11 — a wire-observable
shape, not a discovery mechanism). Absent such an explicit clause, no
mechanism is decided.

**Corollary — mechanism-naming exclusions (§6).** Where a §6 exclusion names
an internal mechanism (a new MongoDB collection / index / schema /
migration, Redis, a caching layer, a new embedding pipeline, a LangGraph
topology change, an ingestion change, a new provider), it means **(a)** M14
does not *deliver* that mechanism as part of its surface and **(b)** this
contract and its ratification *authorize* no such change — Document 64
pre-approves nothing. It does **not** mean the *M14 Filing Analysis
Architecture Decision Pack* is barred from **evaluating** or **selecting**
that mechanism where the externally observable behaviour frozen here
genuinely requires it. A mechanism the pack selects that needs a new
collection / index / schema / migration is introduced through **architecture
ratification plus the normal schema-change governance**
(`08_MongoDB_Data_Architecture.md` / the ADR chain) — never as something
this contract already permitted. See §6.1 and §19.3.

---

## 6. Explicit Non-Goals / Exclusions  *(contract item 3)*

M14 Filing Analysis **does NOT include, and this contract does NOT define:**

- **Conversational Filing Q&A** — multi-turn or single-turn conversational
  interaction over a filing. Filing Q&A is a **later, separately scoped
  capability** (Document 62 §6 C-1(2), §10; Document 63 §7); M14 produces
  **fixed analysis outputs only**, never a chat turn.
- **A generic filing chatbot** or any general-purpose conversational agent.
- **Conversational memory / session state** of any kind.
- **Cross-filing** comparison, trend analysis, multi-filing aggregation, or
  cross-filing conversational analysis.
- **"Important Changes" implemented as any form of comparison across
  documents** — previous-filing comparison, cross-filing diff, historical
  trend analysis, or implicit temporal comparison. The **Important Changes**
  output is **filing-local only**: derived solely from material change
  language evidenced *within the selected filing itself* (contract invariant
  **INV-IC**, §8.1).
- **Durable Research Sessions** (Document 62 §6 C-4 — `BLOCKED`; Document 63
  §7).
- **Alerts, notifications, watchlists, scheduling, or background / ambient
  filing intelligence** of any kind.
- **Ingestion redesign as part of M14** — this contract authorizes no change
  to `agents/ingest.py`, `chunk_text`, chunk size, or overlap, and M14
  delivers none. *(If the Architecture Decision Pack finds that structured
  section extraction — which may touch ingestion — is a prerequisite, that
  is **C-2 / OAQ-2**, a separate milestone with its own governance (§16); it
  is not an M14 ingestion change and is not foreclosed here — §6.1.)*
- **Provider redesign or a new provider dependency** — LLM access stays
  through `agents/llm.py` (`chat_text` / `chat_json`); this contract adds no
  provider. *(Selecting which of the already-supported providers / models /
  tiers is the M14 default is **OAQ-8** — a selection among existing
  providers, not a redesign or a new dependency — §6.1.)*
- **New retrieval / RAG infrastructure as part of M14** — this contract
  authorizes no new embedding pipeline, no reranker redesign, and no
  ingestion-time embedding change; M14 delivers none. *(Whether, and how,
  retrieval is used — the existing hybrid retriever, a filing-scoped read
  over this filing's own persisted chunks, or none — is **OAQ-3** for the
  Architecture Decision Pack; any index that choice needs, e.g. Document 59
  OD-4's `{doc_id, chunk_idx}` compound index, is introduced through the
  normal schema-change governance, not foreclosed here — §6.1.)*
- **New MongoDB collection / index / schema / migration; Redis usage; a
  caching layer — none is authorized by this contract, and none is
  pre-approved.** *(Whether M14 needs persistence at all, and if so what
  mechanism — a new field on an existing document, a new collection,
  on-demand computation with no persistence, … — is **OAQ-5**, genuinely
  open for the Architecture Decision Pack to evaluate and decide. If that
  pack concludes a new collection / index / schema / migration is warranted,
  it is introduced through **its own architecture ratification plus the
  normal schema-change governance** (`08_MongoDB_Data_Architecture.md` / the
  ADR chain) — never as something Document 64 already permitted — §6.1.)*
- **LangGraph topology change as part of M14** — this contract modifies no
  graph and authorizes none. *(Whether M14 needs a new scoped graph, a new
  node, or out-of-graph reuse of the synthesizer / fact-checker pattern is
  **OAQ-7**; any topology change the Architecture Decision Pack proposes
  against frozen `07` v1.0 is a **stop-and-CR item** handled through that
  process (§16; Document 62 R-9) — not foreclosed here — §6.1.)*
- **Frontend implementation** — the `FilingViewer` "Filing analysis" variant
  wiring is a frontend concern handed off (AH-6), not defined here.
- **Structured filing-section extraction delivered as an M14 feature (C-2)**
  — not selected as M14. *(Whether C-2 must be sequenced **before** C-1 as a
  separate prerequisite milestone is **OAQ-2** (§16) — C-2 is **not
  rejected** and **not decided** here.)*
- **Financial visualization (C-3), "What Changed Since Last Review" (C-4),
  governance hygiene (C-5)** — separate Document 62 candidates, not M14.
- **Any G8 / H-1 / G7 / judge / self-consistency-gate work.**
- **Any change to Documents 58–63 or to the M13 implementation.**

If a future document references Filing Q&A in relation to M14, it may
describe M14 only as a **foundation** a separately scoped Q&A capability
could later build on — never as delivering any part of Q&A.

### 6.1 How to read the mechanism-naming exclusions above

The exclusions in §6 fall into two kinds, and they are read differently.

**Product-scope exclusions (firm — architecture cannot re-open them):**
conversational Filing Q&A; a generic filing chatbot; conversational memory /
session state; cross-filing comparison / trend / aggregation; the Important
Changes filing-local invariant (INV-IC, §8.1); Durable Research Sessions;
alerts / notifications / watchlists / background intelligence; structured
section extraction *delivered as an M14 feature*; C-3 / C-4 / C-5; and any
G8 / H-1 / G7 / judge / self-consistency-gate work. These bound **what M14
is**. They stay out regardless of any architecture finding.

**Mechanism-naming exclusions (bounded, not prohibitive):** a new MongoDB
collection / index / schema / migration; Redis; a caching layer; a new
embedding pipeline; a LangGraph topology change; an ingestion change; a new
provider. Each of these means **exactly two things and no more**:

1. **M14's *delivered* surface does not include that mechanism** as a
   product capability; and
2. **this contract, and its ratification, authorize no such change** —
   Document 64 pre-approves no schema, no collection, no index, no
   migration, no graph change, no provider, no cache.

It does **not** mean the *M14 Filing Analysis Architecture Decision Pack* is
barred from **evaluating** — or, where the externally observable behaviour
this contract freezes (§5.1, §8, §11) genuinely requires it, **selecting** —
that mechanism. Per the §5.1 rule, the contract constrains observable
behaviour; it does not choose, and does not forbid the architecture phase
from choosing, the mechanism that satisfies it. If the Architecture Decision
Pack concludes a named mechanism is necessary, it is adopted through
**architecture ratification plus whatever schema-change / ADR / CR
governance that mechanism normally requires** (for a new collection / index
/ schema / migration: `08_MongoDB_Data_Architecture.md` + the ADR chain; for
a LangGraph change: the stop-and-CR path) — **never** by reading it as
already authorized by Document 64.

**Net effect on §19:** every OAQ in §19.1 stays genuinely open. §19.3
records the explicit pairing of each OAQ with its related §6 exclusion and
confirms none is foreclosed.

---

## 7. Inputs and Required Filing Context  *(contract item 4)*

**Client-supplied identity (contract-level, ratified shape reused):**

| Input | Type | Required | Notes |
|---|---|---|---|
| `ticker` | `str` (path) | **required** | Normalised `.strip().upper()` in the handler, matching `list_filings` / `get_financials` / the M13 content read. Empty after normalisation → `ValidationError` (422). |
| `doc_id` | `str` (path) | **required** | The `filings.doc_id` value (opaque `uuid4`). A `(ticker, doc_id)` that matches no `filings` row **for that ticker** → 404 (§10; Document 59 §3.1 / OD-6). |
| BYOK fields — `llm_provider`, `llm_api_key`, `llm_base_url`, `llm_model` | `str \| None` | optional | Reused **verbatim** from `GenerateRequest` / `ExplainRequest` (Document 43 §3, §6). `llm_api_key` never persisted. `custom` provider / `llm_base_url` set → existing `require_admin` + `assert_public_url` SSRF guard applies unchanged. |
| *(no output-selection parameter)* | — | **n/a** | **CQ-2 — RESOLVED (CTO, 2026-08-31):** M14 uses a **fixed full output set**. There is **no** client-selectable output parameter, query string, or body field for choosing outputs. A request asks for Filing Analysis of `(ticker, doc_id)` and always receives the complete four-output set (§8, §9.2, §9.3). |

**Server-derived filing context the capability consumes:** the filing's
persisted content and metadata, obtained through an **existing** read path
(the M13 `.../content` envelope shape and/or its underlying
`filings` + `filing_chunks` access — Document 59 §1, §5). The contract
requires only that:

- the **only** evidence source is this filing's own persisted chunks. The
  frozen semantics for any chunk-based evidence and any citation anchor are:
  **canonical filing-local identity** `(doc_id, chunk_idx)` (an anchor may
  only reference this filing — §11.2), and **canonical `chunk_idx` ordering**
  (the ascending reading order M13 froze — Document 59 §6), against which
  `chunk_idx` anchors are validated (§11.3, §11.5). **This does not imply
  whole-filing traversal, sequential consumption of every chunk, or the
  absence of retrieval-selected context** — *how much* of the filing is used
  and *how* that analysis context is selected (a whole-filing pass, a
  retrieval-selected subset, structured sections) is **OAQ-1 / OAQ-3**,
  owned by the Architecture Decision Pack (§19). This contract freezes the
  *identity and order semantics* of chunk evidence, not the *amount or
  selection* of analysis context, and makes no RAG / retrieval decision;
- it performs **no acquisition / ingest trigger** and **no provider call for
  filing data** — if `(ticker, doc_id)` has no persisted content, that is
  the empty / insufficient-evidence path (§8, §10), not a fetch;
- it introduces **no new read port / repository / collection** to do so
  unless the architecture phase decides one is warranted (AH-2).

**What "required filing context" resolves to concretely — OAQ-1.** Whether
the analysis needs (a) the ordered raw chunks as-is, (b) a
retrieval-selected subset of chunks, or (c) structured section boundaries
(Risk Factors / MD&A / …) that do not exist today, is the **chunk-vs-section
question** and is **left open for the architecture phase** (Document 62 §7;
§16, §19). This contract does **not** assume `M13 chunks → RAG → LLM`.

---

## 8. Expected Analysis Outputs  *(contract item 5)*

**Bounded, fixed output set — CTO-RESOLVED (2026-08-31).** M14 exposes
**exactly the four outputs** in the table below — **no more, no fewer**
(**CQ-1 — RESOLVED**). The set is **fixed and complete**: every Filing
Analysis request returns all four outputs, and there is **no**
client-selectable output parameter (**CQ-2 — RESOLVED**; §7, §9.2). Each
output is represented as Document 43's **flat cited narrative** —
`narrative` + `sources[]` + `cited_source_indices` (**CQ-3 — RESOLVED**;
§8.2, §9.3, §11.3). Grounded-and-cited is a hard requirement for every
output (§11). The four outputs are the M14 slice of the roadmap's "SEC
Filing Analysis" line (§2).

| # | Output (exact name) | Intent | Grounding requirement |
|---|---|---|---|
| 1 | **Filing Summary** | A plain-language overview of the filing (form type, period, what it covers). | Every substantive factual claim anchored to a `chunk_idx` range in this filing (§11). |
| 2 | **Risk Factors Digest** | The filing's principal risk disclosures, condensed. | Anchored to the chunk range(s) the risks are drawn from. Whether those ranges are located by retrieval, by an LLM classification pass, or by structured section boundaries is **OAQ-9** — not decided here. |
| 3 | **MD&A Digest** | The filing's Management Discussion & Analysis narrative, condensed. | As above. |
| 4 | **Important Changes** | Material change language **evidenced within the selected filing's own text** (e.g. "we have revised our guidance", "a new risk factor is", "effective this quarter") — see **INV-IC** (§8.1). | Anchored to the chunk range(s) the change language appears in (§11). |

### 8.1 Important Changes — contract invariant (INV-IC)

**Promoted from former CQ-5 by CTO Revision R1. This is a frozen contract
invariant, not an open question.**

> **The "Important Changes" output MUST be derived only from material change
> language evidenced within the selected filing itself.**

It **MUST NOT** be produced as, or from, any of:

- a previous-filing comparison;
- a cross-filing diff;
- historical trend analysis;
- an implicit temporal comparison (e.g. "revenue is up" inferred by
  comparing this filing to a remembered earlier value).

If the selected filing's own text contains no self-described material
change language, **Important Changes** is returned in the
insufficient-evidence state (§11.6), never fabricated and never filled by
reaching outside the filing. INV-IC does not narrow or widen M14's product
scope beyond this clarification — it fixes *where the evidence may come
from*.

**Output semantics (contract-level, mirroring Document 42 / 43):**

- **Grounded, Level-2 interpretation** — condensation and plain-language
  interpretation of what the filing says; **sourced** causal statements
  permitted, **unsupported** causal statements prohibited (Document 42 §5).
- **Non-recommending** — no buy / sell / hold or investment-advice framing
  (Document 42; `CLAUDE.md` product rules).
- **Fixed, non-conversational** — each output is a self-contained artifact,
  not a reply to a question.
- **Honest partial / insufficient evidence** — if the filing's persisted
  content does not support a given output (e.g. no MD&A content is present),
  that output is returned in an explicit **insufficient-evidence** state
  with named boundaries (Document 42 §11 "Option C"), **never** fabricated
  or interpolated. Zero grounded citations for an output that claims to be
  complete = a **failed** generation, not a degraded success (Document 42
  §7; §10, §11).
- **Empty filing** — a known `(ticker, doc_id)` with zero persisted chunks
  (Document 59 §8 / OD-7) yields an honest "no analysable content" result,
  not a 404 and not fabricated analysis (§10).

### 8.2 Per-output response representation — CTO-RESOLVED (2026-08-31, CQ-3)

**Each of the four outputs is represented as Document 43's flat cited
narrative.** Per output, the shape is exactly three fields:

| Field | Type | Meaning | Testable rule |
|---|---|---|---|
| `narrative` | `string` | The plain-language, grounded, non-recommending analysis text for that output, carrying inline `[n]` citation markers. | Non-empty for a `complete` or `partial` output; empty for `insufficient_evidence` (§11.6). Every substantive factual claim carries a `[n]` marker (§11.1–§11.2). |
| `sources` | `array` of `{ index, doc_id, chunk_start, chunk_end[, …] }` | The indexed anchor list the `[n]` markers reference; every anchor is a contiguous `chunk_idx` range of **this** filing (§11.3, §11.5). | `index` values are 1-based and unique; `doc_id` = the requested filing; `chunk_start ≤ chunk_end`, both present in the filing's persisted chunks. |
| `cited_source_indices` | `array` of `int` | The subset of `sources` indices actually referenced by a `[n]` marker in `narrative`. | Non-empty for `complete` / `partial`; empty for `insufficient_evidence`. Every `[n]` in `narrative` ⊆ `cited_source_indices` ⊆ `sources` indices; no orphans (§11.4). |

Each output additionally carries its **state** (`complete` / `partial` /
`insufficient_evidence`, §11.6–§11.7) and, for `partial` /
`insufficient_evidence`, the enumerated coverage-boundary list §11.7 /
§11.6 require. No per-claim tree, no lightly structured per-output object —
the flat `narrative + sources[] + cited_source_indices` shape is the frozen
externally observable representation, and a conformance test depends on it
exactly.

This is the **response** representation only. It is **distinct from** any
*storage* representation, which remains architecture and is **not** decided
here (OAQ-5).

---

## 9. API-Level Request / Response Contract  *(contract item 6)*

> **What is settled here vs still open.** **CTO-RESOLVED (2026-08-31):** the
> output roster (exactly the four outputs of §8, CQ-1), the fixed full set
> with **no** output-selection parameter (CQ-2), and the per-output
> **flat cited narrative** representation `narrative` + `sources[]` +
> `cited_source_indices` + state (CQ-3, §8.2). **Still architecture, NOT
> decided here:** the **endpoint form** — synchronous vs async job + status
> + optional SSE + cancel, the route family / path segment, and any new
> `JobKind` — is **OAQ-4**; persistence of the payload is **OAQ-5**. Parts
> marked **[convention-justified]** reuse an existing ratified repository
> pattern; parts marked **[architecture-dependent → OAQ-n]** are confirmed
> or replaced by the Architecture Decision Pack.

### 9.1 Endpoint family — [architecture-dependent → OAQ-4]

Every existing AI-generating surface in this repository (Research, Learning,
Comparison-Explanation) is an **async job + status + optional SSE + cancel**
family, never a synchronous call (§2; Document 43 §3, §5, §17). Filing
Analysis is generative and latency-bearing, so the **recommended** shape,
reusing the ratified `(ticker, doc_id)` filing identity (Document 59 §3.1),
is a 4-route family:

```text
POST   /api/companies/{ticker}/filings/{doc_id}/analysis            → create/reuse an analysis job
GET    /api/companies/{ticker}/filings/{doc_id}/analysis/{id}       → status; result when completed
GET    /api/companies/{ticker}/filings/{doc_id}/analysis/{id}/stream → SSE progress + terminal result
POST   /api/companies/{ticker}/filings/{doc_id}/analysis/{id}/cancel → owner-scoped, idempotent-on-terminal
```

**Not decided here (OAQ-4):** synchronous single-response vs async job;
whether SSE is included; the exact path segment (`/analysis` vs
`/analyze` vs a top-level family); whether a new `JobKind` member is added
(Document 43 added exactly one — `COMPARISON_EXPLANATION`; M14 would by the
same pattern add one, but that is an architecture/implementation step, not
this contract). Route-inventory arithmetic (currently `43`) is **not**
ratified by this document — the count changes only when
`test_route_inventory.py` is updated in a separately authorized
implementation (Document 43 §21 precedent).

### 9.2 Request — [convention-justified] except where noted

- **Auth:** `current_user`, identical to every tool route. `ticker` in the
  path is a namespacing / validation segment, **not** an authorization
  scope (the corpus has no `user_id` — §2, §15).
- **Body (on the creating call):** the **BYOK field set verbatim**
  (`llm_provider` / `llm_api_key` / `llm_base_url` / `llm_model`, all
  `Optional[str] = None`) — Document 43 §6. Custom-provider admin-gate +
  SSRF guard applies unchanged.
- **No filing text in the body** — identity crosses the wire, not content;
  the capability resolves the filing server-side from `(ticker, doc_id)`.
- **No output-selection parameter (CQ-2 — RESOLVED).** The request contract
  defines **no** query string or body field for choosing which outputs to
  produce. Every request for Filing Analysis of `(ticker, doc_id)` returns
  the complete fixed four-output set (§8). Subset selection is not part of
  the M14 contract.

### 9.3 Responses — shapes [architecture-dependent → OAQ-4/OAQ-5], field semantics [convention-justified]

- **Creating call →** minimal `{ "id": str, "status": <JobStatus enum
  value>, "reused": bool }` (Document 43 §7 shape) **if** the async pattern
  is adopted; `reused: true` on an identity match against an existing
  artifact (§12). If a synchronous shape is chosen instead (OAQ-4), the
  creating call returns the analysis result directly.
- **Status / result call →** `{ "id", "status", "analysis"? }`, with
  `analysis` present **only** when `status == "completed"` (Document 43 §8
  merged-endpoint shape).
- **`analysis` payload →** the **complete fixed four-output set** (§8:
  Filing Summary, Risk Factors Digest, MD&A Digest, Important Changes) —
  always all four, never a subset (CQ-1 / CQ-2 — RESOLVED). **Each output is
  the flat cited narrative** `{ narrative, sources[], cited_source_indices }`
  plus its state (`complete` / `partial` / `insufficient_evidence`), per
  Document 43 and §8.2 / §11.3 (CQ-3 — RESOLVED). The frozen, testable part
  is: **four outputs, all present, each with those three fields and their
  §8.2 / §11 semantics.** The concrete field-key spellings and whether the
  container is an object keyed by output or an array are wire details for the
  ratified text / the schema, not decided here.
- **Metadata echoed:** the filing's identity + `filings` metadata fields
  (`doc_id`, `ticker`, `company_name?`, `source`, `created_at`) verbatim,
  matching the M13 content envelope (Document 59 §5.1). No new derived
  metadata field is introduced by this contract.
- **`_id` / `embedding` never in any response** (Document 59 §5.2).

### 9.4 What §9 does NOT define

Persistence of the `analysis` payload (OAQ-5); the store / collection / index
(AH-2); the internal job runner (AH-3); the LangGraph graph or node (OAQ-7);
the prompt(s) (AH-4); the model / provider defaults beyond BYOK passthrough
(OAQ-8); the frontend consumption code (AH-6).

---

## 10. Validation and Error Semantics  *(contract item 7)*

**Reuse the existing envelope and taxonomy with no additions** (§2; Document
59 §9; Document 43 §12).

| Condition | Mechanism | HTTP | Envelope |
|---|---|---|---|
| Unauthenticated | `current_user` | 401 | existing auth envelope |
| `ticker` empty after normalisation | `ValidationError` | 422 | `{"detail", "type": "validation_error"}` |
| `(ticker, doc_id)` matches no `filings` row for that ticker (incl. a `doc_id` under a different ticker) | `NotFoundError` | 404 | `{"detail", "type": "not_found"}` — non-disclosure semantics unchanged (Document 59 §3.1 / OD-6) |
| Known filing, **zero** persisted chunks | **not an error** | 200 | honest "no analysable content" result (§8); mirrors Document 59 OD-7 (200 + empty), not a 404 |
| An output cannot be produced with **every** substantive factual claim grounded in filing-local evidence | that output → **`insufficient_evidence`** (no claims, machine-readable "what could not be grounded", empty `cited_source_indices`) — **not** a fabricated body, **not** an HTTP error | 200-level (or completed job) with that output marked `insufficient_evidence` | **§11.6**; Document 42 §7 |
| Some but not all of an output's coverage can be grounded | that output → **`partial`** (only grounded claims; non-empty `cited_source_indices`; enumerated coverage-boundary list) — **not** a failure | 200-level | **§11.7**; Document 42 §11 |
| Malformed / gapped / partial-ingest chunks for the filing | analyse the **present well-formed chunks**; anchors reference present ranges only; affected outputs → `partial` / `insufficient_evidence` with the ingest limit named; **no fabrication** | 200-level | **§11.8**; Document 59 OD-8; mechanism delegated → **AH-5** |
| Admission budget exceeded (`MAX_ACTIVE_JOBS`) | `RateLimitedError` (if async) | 429 | `{"detail", "type": "too_many_jobs"}` — applies automatically to any new job kind |
| Custom provider from non-admin | existing `require_admin` | 403 | existing shape |
| LLM provider failure during generation | `LLMProviderError` → job `fail(safe_message)` (async) or `502` (sync) | job `status: "failed"` / 502 | redacted message only — **no raw provider text, no key fragment, no stack trace** ever reaches the client (Document 43 §12, §19) |
| Malformed / unvalidatable model output | `chat_json` `ValueError` → same fail path | as above | as above |
| Job deadline exceeded (if async) | `DeadlineExceededError` | job `status: "failed"` / 504 | generic message |
| Client cancels (if async) | existing `JobLifecycle.cancel()` | job `status: "cancelled"` | idempotent on terminal (Document 43 §13) |
| Synchronous Mongo / infra failure while reading the filing | `InfrastructureError` | 502 | `{"detail": "…", "type": "infrastructure_error"}`, `logger.exception` first — M12 / M13 precedent |

**Invariant:** nothing in this capability changes the shape, status codes, or
behaviour of `GET /filings`, the M13 `.../content` read, `/reports/generate`,
or any existing route. M14 is **100% additive**.

**Malformed / gapped chunk sequence** (Document 59 OD-8) — the
externally observable requirement is frozen in **§11.8** (analyse present
well-formed chunks; valid anchors only; honest `partial` /
`insufficient_evidence`; no fabrication). The detection / handling
*mechanism* (skip-and-warn, threshold, surface shape) is delegated to
**AH-5** (§19.2), consistent with M13 delegating OD-8 to its implementation
phase.

---

## 11. Citation / Provenance Requirements (contract level)  *(contract item 8)*

**Hard, externally observable requirements — not deferrable, not an
architecture decision.** Every rule below is stated so a conformance test or
a human reviewer can check it against a response **without knowing how the
implementation found the evidence.** The anchor-*discovery* mechanism
(retrieval score, LLM classification, structured-section lookup, or another)
is **not** decided here — it is **OAQ-9** (§19).

### 11.1 What constitutes a "claim"

- A **claim** is a discrete assertion, in an analysis output, about what the
  selected filing states, discloses, reports, or characterises.
- A **substantive factual claim** is a claim that a reader could check
  against the filing text: a specific statement about a figure, a fact, a
  disclosure, a risk, a change, a management assertion, or an
  interpretation of such. Examples: "the filing reports revenue of $X for
  the period", "the filing adds a new risk factor about supply
  concentration", "management attributes the margin decline to input
  costs".
- **Non-substantive text** — headings, section labels, connective phrasing,
  and generic framing that asserts nothing checkable ("the filing discusses
  several risks", "this section summarises management's outlook") — is
  **not** a substantive factual claim and does **not** require its own
  anchor.
- Numeric quantities, named events, dates, and direct or paraphrased
  management statements are **always** substantive factual claims.

### 11.2 Grounding obligation (filing-local evidence)

- **Every substantive factual claim in every analysis output MUST be
  supported by at least one citation whose anchor points to filing-local
  evidence** — a chunk range of **this** filing (the one addressed by the
  request's `(ticker, doc_id)`) that a reviewer can open and read to verify
  the claim.
- "Filing-local" is absolute: an anchor MUST NOT reference another filing, a
  report, financial-statement data, or any external source. There are **no
  cross-filing citations** (§6; INV-IC for Important Changes).
- A substantive factual claim that cannot be tied to filing-local evidence
  MUST NOT appear in a "complete" output — it is dropped and its absence is
  recorded as a partial-evidence boundary (§11.7), or, if it was essential
  to the output, the output becomes insufficient-evidence (§11.6). It is
  **never** emitted ungrounded and **never** grounded by fabrication.

### 11.3 Anchor representation (wire-observable floor — frozen)

- The **minimum** anchor is a **contiguous `chunk_idx` range** of this
  filing: `{ doc_id, chunk_start, chunk_end }` where `doc_id` is the filing
  under analysis, `chunk_start` and `chunk_end` are `chunk_idx` values that
  are **present** in the filing's persisted chunks, and
  `chunk_start ≤ chunk_end`. A single-chunk anchor has
  `chunk_start == chunk_end`.
- This **representation** is frozen (it is a wire-observable shape, per
  §5.1). If the architecture phase later introduces structured sections
  (OAQ-1), an anchor MAY *additionally* carry a section identifier — but the
  `chunk_idx`-range remains mandatory and is the verification floor.
- **Citation wire shape (existing convention, Document 43 §10, reused
  verbatim):** inline `[n]` markers in each narrative, a parallel indexed
  `sources` list, and a `cited_source_indices` subset naming the indices
  actually referenced. Each `sources[n]` entry contains at least one anchor
  as above. `SourceReference` `{label, target}` is reused; no new citation
  syntax is introduced.

### 11.4 A citation may support multiple claims

- **One citation (one `sources[]` entry / one `[n]` index) MAY be referenced
  by more than one claim** within the same output when those claims draw on
  the same filing-local evidence. Re-citing the same index is expected and
  correct; it is not a defect.
- The same underlying chunk range MAY appear under more than one `sources[]`
  index if that aids readability, but an implementation **SHOULD** prefer a
  single index per distinct chunk range.
- Every index that appears in any `[n]` marker MUST appear in
  `cited_source_indices`; every entry in `cited_source_indices` MUST be
  referenced by at least one `[n]` marker (no orphan citations).

### 11.5 Anchor contiguity

- A single anchor's `chunk_start..chunk_end` range **MUST be contiguous**
  (every `chunk_idx` in the inclusive range is part of the cited evidence).
- A claim whose evidence is spread across **non-adjacent** parts of the
  filing MUST be represented as **multiple citations**, each with its own
  contiguous anchor — **not** as one anchor spanning unrelated chunks with
  irrelevant text in between.
- A contiguous range MAY legitimately span several chunks (e.g. a
  multi-paragraph risk factor). The test is "is the whole inclusive range
  evidence for the claim", not range length.

### 11.6 Insufficient-evidence semantics

- An output is returned in the **`insufficient_evidence`** state when it
  cannot be produced with **every** substantive factual claim grounded in
  filing-local evidence — for example a requested output whose subject
  matter is simply absent from the filing's persisted text.
- An `insufficient_evidence` output MUST:
  - contain **no** substantive factual claims (grounded or otherwise) — it
    is not a degraded narrative;
  - name, in a machine-readable list, **what could not be grounded** (the
    output kind, and a short reason such as "no MD&A content present in this
    filing's persisted text");
  - carry an empty `cited_source_indices`.
- An `insufficient_evidence` output is **not** an HTTP error; it is a valid
  200-level result (or, for an async job, a completed job whose result
  marks that output insufficient). It is distinct from the whole-filing
  **empty** case (§8 / §10: known `(ticker, doc_id)`, zero persisted
  chunks → "no analysable content").

### 11.7 Partial-evidence semantics

- An output is returned in the **`partial`** state when **some but not all**
  of its intended coverage can be grounded in filing-local evidence.
- A `partial` output MUST:
  - contain **only** grounded substantive factual claims — a `partial`
    output that contains any ungrounded substantive factual claim is
    **invalid**;
  - carry a non-empty `cited_source_indices`;
  - include an explicit, enumerated **coverage-boundary list** naming what
    was omitted for lack of filing-local evidence (e.g. "risk factor
    disclosures for segment Y not present in persisted text").
- `partial` is distinct from `insufficient_evidence`: `partial` has *some*
  grounded content, `insufficient_evidence` has *none*.
- A `complete` output MUST have a non-empty `cited_source_indices`, **zero**
  ungrounded substantive factual claims, and **no** coverage-boundary list.
  An output that would otherwise be `complete` but has an empty
  `cited_source_indices` is a **failed** generation (or `insufficient_
  evidence`), never a silent pass (Document 42 §7; Document 43 §9–§10).

### 11.8 Malformed / partial-ingest behaviour

- If the selected filing's persisted chunks are **incomplete or malformed**
  — a gap in the `chunk_idx` sequence, a missing or empty `text`, an
  unassemblable row (Document 59 §8 / OD-8) — Filing Analysis operates over
  the **well-formed chunks that are present**.
- In that case:
  - **every** citation anchor MUST still reference a **present, well-formed**
    contiguous chunk range (an anchor pointing at an absent or malformed
    `chunk_idx` is **invalid**);
  - any output whose grounding is **materially affected** by the ingest
    defect MUST be returned as `partial` (or `insufficient_evidence` if
    nothing usable remains), with the ingest limitation named among its
    coverage boundaries (§11.7);
  - the capability MUST NOT fabricate content to bridge a gap and MUST NOT
    silently present reduced coverage as `complete`.
- The **detection / handling mechanism** for malformed rows (skip-and-warn,
  a `partial` flag surface, a threshold) is delegated — **AH-5** (§19.2),
  matching M13's own delegation of OD-8 to its implementation phase. The
  **observable requirement** above (valid anchors only; honest `partial` /
  `insufficient_evidence`; no fabrication) is frozen here.

### 11.9 What §11 does NOT decide

The **mechanism** that locates the chunk range backing a claim — retrieval
score, an LLM classification pass, structured-section lookup, or anything
else — is **OAQ-9** (and interacts with OAQ-1 / OAQ-3). §11 freezes that a
**valid, filing-local, human-verifiable anchor MUST exist for every
substantive factual claim**, and freezes the anchor's **wire
representation** (§11.3); it does **not** freeze how that anchor is
produced.

---

## 12. Determinism / Reproducibility Expectations  *(contract item 9)*

LLM generation is inherently non-deterministic; this contract does **not**
require bit-identical regeneration.

- **Reproducibility via identity + reuse (recommended, mirrors Document 43
  §14).** IF the architecture phase adopts persisted analysis (OAQ-5), a
  stored analysis artifact SHOULD be keyed by an **analysis identity** =
  `filing identity (ticker, doc_id)` + `prompt version` + `output-schema
  version` + `provider identity` + `model identity`, and a request matching
  an existing identity SHOULD return the existing artifact
  (`reused: true`, Document 43 §7 / §15) rather than regenerate.
- **On-demand path.** IF analysis is computed on demand with no persistence
  (also permitted — OAQ-5), the contract requires only that each response be
  **grounded and cited** per §11; run-to-run textual variation is expected
  and acceptable.
- **Schema stability.** Regardless of path, the **output schema** (field
  names, citation shape, state enum) MUST be stable across runs for a given
  schema version — only the generated prose may vary.
- **No hidden state.** Analysis of a filing depends only on that filing's
  persisted content + the versioned prompt/schema/model — never on prior
  requests, session history, or other filings (a corollary of the §6
  no-memory / no-cross-filing exclusions).

**Persistence itself is NOT decided here** (OAQ-5). The two bullets above
are written so the contract is complete under *either* architecture outcome.

---

## 13. Performance / Reliability Requirements  *(contract item 10)*

Stated only where already justified by repository facts; anything needing
measurement is deferred.

- **Bounded input.** A filing's persisted text is ≤ ~200 KB
  (`ingest.py` truncates at `200_000` chars — Document 59 §7), ~100–2,000
  chunks. Whole-filing analysis is therefore a *bounded* LLM workload, not
  an unbounded one — but a single whole-filing pass on a large filing may be
  costly (Document 62 §7). Whether to pass the whole filing or a
  retrieval-scoped subset is **OAQ-3**, not a performance decision made
  here.
- **Reliability.** Reuse the existing job admission ceiling
  (`MAX_ACTIVE_JOBS`, shared, not per-kind) if the async pattern is adopted
  — no new rate limiter (Document 43 §3, §19). A generation failure must
  never fail or slow the M13 `.../content` read or any existing route
  (§10 invariant).
- **Graceful degradation.** A provider outage surfaces as a failed
  generation with a redacted message (§10), never a crash and never
  fabricated output.
- **No latency SLO is frozen here.** A target response / job-completion time
  is **CQ-4** (§18). The *mechanism* for meeting it depends on the
  whole-filing-vs-scoped decision (OAQ-3) and on model selection (OAQ-8) —
  architecture, not contract. The *product-level* latency / freshness
  expectation is not a ratification pre-condition but **must be resolved
  before implementation authorization** (§20).
- **No caching / no Redis.** Whether any caching exists is **OAQ-6**;
  this contract adds none.

---

## 14. Observability Requirements  *(contract item 11)*

**Reuse only; no metric name is frozen here** (Document 43 §20; Document 59
§11 precedent).

- **HTTP layer:** the new route(s) emit
  `alphascribe_http_requests_total{method,path,status}` +
  `alphascribe_http_request_duration_seconds{method,path}` automatically via
  the request-timing middleware — no new instrumentation.
- **LLM layer:** `llm_calls_total` / `llm_tokens_total` are automatic via
  `chat_json` / `chat_text` — no new code.
- **Job layer (if async):** admission / active-job gauges apply
  automatically once a job kind exists.
- **Outcome signal (required to be *observable*, mechanism deferred):** it
  MUST be possible to distinguish, in aggregate,
  `completed-complete` / `completed-partial` / `failed` /
  `insufficient-evidence` analysis outcomes (at minimum via structured
  logs), so a systemic grounding-data problem is visible. Exact
  metric name / shape → implementation (AH-7).
- **Tracing:** a per-endpoint OTel span using the existing
  `get_tracer().start_as_current_span(...)` convention and the module
  `logger`, matching every M8 / M12 / M13 code path.
- **No raw provider text, key material, or prompt content in logs or
  metrics** (§15).

---

## 15. Security / Access-Control Expectations  *(contract item 12)*

- **Authentication:** `current_user` dependency, unchanged — no new
  auth concept, decorator, or scope parameter.
- **Authorization / corpus visibility:** the corpus (`companies`, `filings`,
  `filing_chunks`) has **no `user_id`** and is shared across all tenants by
  design (`08` RI-5; Document 59 §10). `GET /filings` and the M13 content
  read apply **no ownership scoping**; this contract adds none — any
  authenticated user may analyse any ingested filing, the same visibility
  the filing text already has. (Job ownership, if the async pattern is
  adopted, still scopes *the job record* — `GET`/`cancel` by a non-owner →
  404, Document 43 §13 — but not the filing corpus.)
- **BYOK / managed-AI:** inherits the existing policy verbatim — same
  fields, same `set_llm_context` / `reset_llm_context` threading, same
  custom-provider `require_admin` + `assert_public_url` SSRF guard
  (Document 43 §6, §19). No new credential path. `llm_api_key` never
  persisted, never logged.
- **Prompt-injection surface (noted, handoff — AH-8).** Filing text is
  attacker-influenceable in principle (corpus-poisoning trade-off is
  documented and accepted — `10` §6.4 / SQ-1). The analysis prompt design
  MUST treat filing content as untrusted data, not instructions; the
  concrete mitigation is an implementation / architecture concern, recorded
  here so it is not lost.
- **Output safety:** every failure path surfaces only a redacted, generic
  message (§10). Non-recommending output constraint (§8) is also a safety
  boundary, not only a product one.
- **No secrets, no fork/PR CI implications** — this is a read + generate
  surface with no new stored credential.

---

## 16. C-2 Structured Filing Extraction — Handling

**C-2 is NOT M14. C-2 has NOT been rejected.** (Document 62 §6 C-2, §8;
Document 63 §6.)

- This contract does **not** assume `M13 chunks → RAG → LLM → Filing
  Analysis`, and does **not** assume `C-2 → M14`. Both are premature.
- Whether Filing Analysis can operate effectively over M13's existing
  **unstructured** chunks, or **requires** structured section extraction
  (C-2) first, is the **chunk-vs-section question** and is an **open
  contract / architecture decision** (OAQ-1 / OAQ-2, §19). Document 62 §7
  and Document 63 §6 leave it open; this contract keeps it open.
- The architecture phase MAY legitimately conclude that **C-2 must be
  sequenced before C-1** — which would re-order the roadmap. This contract
  is written so it remains valid under either outcome: §7's "required
  filing context" and §8's output grounding are expressed in terms of
  "chunk range(s) the content is drawn from", identifying *how* those ranges
  are found (retrieval / classification / structured sections) as the open
  question.
- If C-2 is sequenced first, this contract's §4–§15 remain the target for
  the Filing Analysis capability that follows C-2; only the "how ranges are
  identified" mechanism changes.

**This section resolves nothing about C-2.** It records that the question is
alive and belongs downstream.

---

## 17. Acceptance Criteria  *(contract item 13)*

A testable checklist — **not** an implementation, and **not** a licence to
build. The "contract-ratification acceptance" items are governance gates
that must be **true and on record** before this document is ratified; the
"downstream implementation acceptance" items are checked later, after
architecture ratification and implementation authorization (mirroring
Document 62 §14 / Document 59 §14).

**Ratification pre-conditions (CQ-1 / CQ-2 / CQ-3) — SATISFIED by CTO
decision dated 2026-08-31:**

- [x] **CQ-1 — RESOLVED (CTO, 2026-08-31).** The contract names the exact
      roster: exactly four outputs — Filing Summary, Risk Factors Digest,
      MD&A Digest, Important Changes — no others (§8, §18).
- [x] **CQ-2 — RESOLVED (CTO, 2026-08-31).** Fixed full output set; **no**
      client-selectable output parameter — every request returns all four
      outputs (§7, §9.2, §18).
- [x] **CQ-3 — RESOLVED (CTO, 2026-08-31), and stated explicitly.**
      Per-output response representation is Document 43's flat cited
      narrative — `narrative` + `sources[]` + `cited_source_indices` plus
      output state — specified as a testable field table in §8.2 (§9.3,
      §11.3, §18).

These were the three ratification pre-conditions for Document 64; all are
now resolved. CQ-4 (latency expectation) was never a ratification
pre-condition and is gated to implementation authorization (§18, §20). The
CTO **performed the contract-ratification act on 2026-08-31** (§22); the
items below are now **asserted on record**.

**Contract-ratification acceptance (asserted by the CTO ratification of
2026-08-31 — §22):**

- [x] The bounded scope (§5), the §5.1 contract-vs-architecture boundary,
      and the exclusion list (§6) are accepted as the M14 Filing Analysis
      boundary — Filing Q&A / chatbot / cross-filing / durable-sessions /
      alerts explicitly out.
- [x] **INV-IC (§8.1)** is accepted as a contract invariant: "Important
      Changes" is derived **only** from material change language evidenced
      within the selected filing itself — never a previous-filing
      comparison, cross-filing diff, historical trend analysis, or implicit
      temporal comparison.
- [x] The citation / provenance requirements (§11, subsections §11.1–§11.9)
      are accepted as hard, externally observable, non-deferrable
      obligations — including the `chunk_idx`-range anchor **representation**
      floor (§11.3) — while the anchor-**discovery mechanism** stays open
      (OAQ-9).
- [x] The validation / error semantics (§10) reuse the existing envelope and
      taxonomy with **zero** additions; `insufficient_evidence` / `partial`
      / malformed-ingest behaviour follow §11.6 / §11.7 / §11.8.
- [x] The determinism statement (§12) is accepted as complete under either
      persistence outcome.
- [x] Every architecture-level question is recorded in §19 as OPEN, not
      resolved — in particular chunk-vs-section, C-2 sequencing, RAG /
      retrieval strategy, persistence, caching, execution topology,
      LangGraph, and model / provider (§5.1).
- [x] **No §6 exclusion forecloses an OAQ.** Each §19.1 OAQ is verified
      genuinely open to the Architecture Decision Pack by the §19.3
      contradiction sweep; the §6 mechanism-naming exclusions are read per
      §6.1 (not authorized / not an M14 deliverable — not prohibited for
      architecture evaluation).
- [x] **Persistence is neither decided nor pre-approved.** This contract
      authorizes **no** new MongoDB collection / index / schema / migration,
      Redis usage, or caching layer (OAQ-5 / OAQ-6); and it does **not** bar
      the Architecture Decision Pack from selecting a persistence design that
      needs one — such a design is introduced via architecture ratification
      plus the normal schema-change governance (`08` / ADR chain), never as
      pre-authorized here (§6.1, §19.3).
- [x] This ratification grants **no** architecture approval and **no**
      implementation, commit, or push authorization.

**Downstream implementation acceptance (checked later, not by this
document):**

- [ ] The M14 **Architecture Decision Pack** is CTO-ratified and frozen,
      resolving OAQ-1…OAQ-10 (§19).
- [ ] Route inventory gains only the additive M14 route(s); **zero** existing
      routes change; `GET /filings` and the M13 `.../content` read are
      byte-for-byte unchanged.
- [ ] A successful Filing Analysis response contains **exactly the four
      outputs** — Filing Summary, Risk Factors Digest, MD&A Digest, Important
      Changes — always all four, never more, never a client-selected subset
      (§8, CQ-1 / CQ-2).
- [ ] The request has **no** output-selection parameter (query or body);
      subset selection is not accepted (§7, §9.2, CQ-2).
- [ ] Each output is the flat cited narrative — `narrative` + `sources[]` +
      `cited_source_indices` + state — per the §8.2 field table; no
      per-claim tree, no alternative per-output object shape (§8.2, §9.3,
      §11.3, CQ-3).
- [ ] Every **substantive factual claim** (§11.1) in a `complete` output is
      backed by ≥1 citation whose anchor is filing-local (§11.2); a
      `complete` output has zero ungrounded substantive factual claims and a
      non-empty `cited_source_indices` (§11.7).
- [ ] Every `sources[]` anchor is `{ doc_id = this filing, chunk_start ≤
      chunk_end }`, both `chunk_idx` values **present** in the filing's
      persisted chunks, and the range is **contiguous** (§11.3, §11.5);
      evidence spread across non-adjacent chunks is multiple citations, not
      one spanning anchor.
- [ ] Every `[n]` marker resolves to a `sources` entry; every used index is
      in `cited_source_indices`; no orphan `cited_source_indices` entries
      (§11.4). A citation may be referenced by multiple claims (§11.4).
- [ ] `insufficient_evidence` outputs contain **no** substantive factual
      claims, name what could not be grounded, and have an empty
      `cited_source_indices` (§11.6); `partial` outputs contain **only**
      grounded claims plus an enumerated coverage-boundary list (§11.7); the
      two states are never conflated.
- [ ] The **Important Changes** output is filing-local only — no
      previous-filing comparison, cross-filing diff, trend analysis, or
      implicit temporal comparison (**INV-IC**, §8.1); absent self-described
      change language → `insufficient_evidence`, never fabricated.
- [ ] Over a malformed / partial-ingest filing: analysis uses present
      well-formed chunks, every anchor references a present range, affected
      outputs are `partial` / `insufficient_evidence` with the ingest limit
      named, and nothing is fabricated (§11.8).
- [ ] No failure path returns raw provider text, an API-key fragment, or a
      stack trace (§10, §15).
- [ ] BYOK fields, when supplied, thread through `set_llm_context` /
      `reset_llm_context` exactly as `_run_pipeline` / `_run_explanation`
      already do — no separate credential path (§15).
- [ ] Analysis of a filing depends only on that filing's persisted content +
      the versioned prompt / schema / model — no session, no other filing
      (§12).
- [ ] A known filing with zero persisted chunks yields an honest "no
      analysable content" result, not a 404 and not fabricated analysis
      (§8, §10).
- [ ] A separate CTO **implementation-authorization** decision is issued
      after contract + architecture ratification; commit and push
      authorization remain further separate acts (§20).

---

## 18. Contract-Level Questions (CQ) — Status  *(contract item 14)*

**Contract / product** questions (mechanism-only questions are in §19, not
here — per the Document 43 §23 discipline of not disguising a mechanism
choice as a contract ambiguity). **CQ-1, CQ-2, and CQ-3 were RESOLVED by CTO
decision dated 2026-08-31** and are folded into the contract body (§7, §8,
§8.2, §9); the rows below retain the questions for traceability. CQ-5 is
closed (INV-IC). CQ-4 / CQ-6 / CQ-7 are notes carried for the CTO's
ratification review — none is a ratification pre-condition. **These
resolutions do not ratify the contract** — the CTO performs that separate
act (§20).

| ID | Question | Status |
|---|---|---|
| **CQ-1** | **Exact M14 output roster.** | **RESOLVED (CTO, 2026-08-31).** M14 exposes **exactly four** outputs — **Filing Summary, Risk Factors Digest, MD&A Digest, Important Changes** — and no others (§8). |
| **CQ-2** | **Fixed full set vs client-selectable subset.** | **RESOLVED (CTO, 2026-08-31).** **Fixed full output set**; **no** client-selectable output parameter. A request asks for Filing Analysis of the filing and receives all four outputs (§7, §9.2, §9.3). |
| **CQ-3** | **Per-output response representation.** | **RESOLVED (CTO, 2026-08-31).** Document 43's **flat cited narrative**: each output is `narrative` + `sources[]` + `cited_source_indices` plus output state, specified as a testable field table in **§8.2** (§9.3, §11.3). Explicit and testable. Distinct from the *storage* representation, which stays architecture (OAQ-5). |
| **CQ-4** | **Latency / freshness expectation.** Any product-level target for time-to-result? | **Not a ratification pre-condition.** The *mechanism* for meeting a latency / freshness target is architecture (depends on OAQ-3 / OAQ-8). The **product-level latency / freshness expectation itself must be resolved before *implementation authorization*** (§20) — not required for contract ratification, and this proposal does not set it. |
| **CQ-5** | ~~"Important Changes" scope confirmation.~~ | **RESOLVED by CTO Revision R1 → promoted to contract invariant `INV-IC` (§8.1): Important Changes is filing-local only.** No longer an open question. Row retained for traceability. |
| **CQ-6** | **Companion artifact numbering.** This contract assumes the next artifact is an *M14 Filing Analysis Architecture Decision Pack* at the next free document number (65; **not created here**). | Governance-hygiene confirmation only; not a ratification pre-condition. |
| **CQ-7** | **Does ratifying this contract satisfy Document 62 §14 item 2 ("C-1 scope is frozen"), or is a separate wording step needed?** | Governance sequencing; see §20. Not a ratification pre-condition for *this* document; a CTO note at ratification. |

---

## 19. Open Architecture Questions / Architecture Handoff Items  *(contract item 15)*

**None of the following is decided by this contract.** Each is handed to the
*M14 Filing Analysis Architecture Decision Pack*. Ratifying this contract
does **not** resolve, pre-bias, or time-bound any of them.

### 19.1 Open Architecture Questions (OAQ) — must be resolved by the Architecture Decision Pack

| ID | Open question | Why it is out of contract scope |
|---|---|---|
| **OAQ-1** | **Chunk-vs-section.** Does analysis operate over M13's ordered unstructured chunks as-is, over a retrieval-selected chunk subset, or does it require structured section boundaries (Risk Factors / MD&A / …) that do not exist today? | Document 62 §7 / Document 63 §6 leave it explicitly OPEN. **Genuinely open:** the §6 ingestion exclusion bounds *M14*; if structured sections are found necessary that is C-2 / OAQ-2, a separate milestone (§16), not a foreclosed option (§6.1). |
| **OAQ-2** | **C-2 sequencing.** Must C-2 Structured Filing Extraction precede C-1, or can C-1 proceed without it? A legitimate outcome is "C-2 first" (re-sequences the roadmap). | §16; Document 62 §7. C-2 is **not rejected** by §6 — only C-2 *delivered as an M14 feature* is out (§6.1). |
| **OAQ-3** | **RAG / retrieval.** Is retrieval introduced into this new filing-scoped surface (a first — the retriever is report-pipeline-only today), or does analysis run whole-filing over ordered chunks? Which retrieval algorithm, if any? | Explicitly forbidden to decide at contract stage. **Genuinely open:** §6 excludes only *new retrieval infrastructure as an M14 deliverable*, not the pack's evaluation of whether/how retrieval, a filing-scoped read, or none is used — including any index via the normal schema-change governance (§6.1). |
| **OAQ-4** | **Endpoint form.** Synchronous single response vs async job + status + optional SSE + cancel; exact route family / path segment; whether a new `JobKind` member is added. | §9.1; existing convention *recommends* async but does not bind M14. |
| **OAQ-5** | **Persistence model.** Is analysis output persisted at all? If so, in what representation and where — a new field on an existing document, a new collection, on-demand computation with no persistence, …? | Forbidden to decide; §12 holds under either answer. **Genuinely open — this was the R2 contradiction fix:** §6 / §6.1 authorize and pre-approve **no** new collection / index / schema / migration, and do **not** bar the pack from selecting a persistence design that needs one — such a design is introduced via architecture ratification + `08` / ADR schema-change governance, never as pre-authorized here. |
| **OAQ-6** | **Caching.** Any response / artifact caching? Any Redis usage? | Forbidden to decide; §13 adds none. **Genuinely open** on the same terms as OAQ-5 (§6.1). |
| **OAQ-7** | **LangGraph topology.** A new scoped graph, a new node in the frozen graph, or reuse of the synthesizer / fact-checker pattern out-of-graph? Any topology change is a stop-and-CR item against frozen `07` v1.0. | Forbidden to decide; Document 62 R-9. **Genuinely open:** §6 excludes an *M14-delivered* topology change, not the pack's proposal of one — which travels the stop-and-CR path (§6.1, §16). |
| **OAQ-8** | **Model / provider selection.** Default provider / model / tier for the analysis pass (beyond the existing BYOK passthrough). | Forbidden to decide. **Genuinely open:** choosing the M14 default among *already-supported* providers / models is a selection, not the "provider redesign / new dependency" §6 excludes (§6.1). |
| **OAQ-9** | **Chunk-range → claim mechanism.** How the chunk range backing a given claim is located (retrieval score, LLM classification pass, structured-section lookup). The *requirement* that a valid anchor exist is frozen (§11); the mechanism is not. | Depends on OAQ-1 / OAQ-3. |
| **OAQ-10** | **Whole-filing vs scoped cost strategy.** For large filings (~2,000 chunks), whether a single pass, a map-reduce over chunk windows, or a retrieval-scoped pass is used. | Performance architecture, not contract. |

### 19.2 Architecture Handoff items (AH) — implementation / architecture detail with a frozen requirement above them

| ID | Handoff | Frozen requirement it serves |
|---|---|---|
| **AH-1** | Prompt version + output-schema version scheme (for §12 identity / reuse). | §12 reproducibility. |
| **AH-2** | Filing-content read path for the analysis capability — reuse the M13 `.../content` access, or a new `doc_id`-scoped port; **no new port unless justified** (Document 59 AG-1 / OD-A precedent). | §7 "no new read port unless warranted". |
| **AH-3** | Job-runner / background-task code (if OAQ-4 → async). | §9 job semantics. |
| **AH-4** | Prompt wording / structure for each §8 output; untrusted-content handling (AH-8). | §8 semantics; §15 injection posture. |
| **AH-5** | Behaviour over a malformed / partial-ingest filing (Document 59 OD-8, delegated). | §10 malformed-chunk row. |
| **AH-6** | Frontend `FilingViewer` "Filing analysis" variant wiring (AI Thinking / Streaming / Empty-uncovered states, source anchors). | Out of M14 **backend** scope (§6); the contract to consume is §8–§11. |
| **AH-7** | Exact outcome metric name / shape for the §14 observability signal. | §14 "outcome signal must be observable". |
| **AH-8** | Concrete prompt-injection mitigation for filing text as untrusted input. | §15 security posture. |
| **AH-9** | `test_route_inventory.py` `APPROVED_ROUTES` update + route-count arithmetic. | §10 additive-only invariant; done only under implementation authorization. |
| **AH-10** | `docs/backend_engineering/00_README.md` / `11_ADR_Index.md` index rows for M14 artifacts (the GH-1 / GH-2 hygiene pattern — Document 59 AG-3). | Governance-register hygiene; a numbered amendment, not this document's to perform. |

### 19.3 Contradiction sweep — every OAQ verified genuinely open to the Architecture Decision Pack  *(CTO Revision R2)*

**Governing rule:** *the contract may constrain externally observable
behaviour, but must not accidentally prohibit the Architecture Decision Pack
from evaluating implementation mechanisms needed to satisfy that behaviour.*

| OAQ | Related §6 exclusion | Contradiction? | Resolution — OAQ remains open |
|---|---|---|---|
| **OAQ-1** chunk-vs-section | "Ingestion redesign as part of M14" | No | §6 bounds *M14*. If structured sections are needed that is **C-2 / OAQ-2**, a separate prerequisite milestone (§16). The pack may still reach that finding; nothing here forecloses it. |
| **OAQ-3** RAG / retrieval | "New retrieval / RAG infrastructure as part of M14" | Latent risk → **fixed in R2** | §6 now excludes only *new retrieval infrastructure as an M14 deliverable*. The pack may evaluate whether/how retrieval, a filing-scoped read, or none is used — including any index that choice requires, via the normal schema-change governance (§6.1). |
| **OAQ-5** persistence model | "New MongoDB collection / index / schema / migration; Redis; caching" | **This was the BLOCKING contradiction → fixed in R2** | §6 now states **none is authorized or pre-approved by this contract**. Whether persistence is needed, and by what mechanism, is OAQ-5 — open. A design needing a new collection / index / schema / migration is introduced via **architecture ratification + `08` / ADR schema-change governance**, never as pre-authorized by Document 64 (§6.1). |
| **OAQ-6** caching | same bullet as OAQ-5 | Same latent risk → **fixed in R2** | Same resolution as OAQ-5: not authorized, not pre-approved, not foreclosed (§6.1). |
| **OAQ-7** LangGraph topology | "LangGraph topology change as part of M14" | No (already scoped "not modified *by this contract*"; "stop-and-CR") → wording tightened in R2 | §6 excludes an *M14-delivered* topology change; a pack proposal against frozen `07` v1.0 travels the **stop-and-CR** path and stays available (§6.1, §16, Document 62 R-9). |
| **OAQ-8** model / provider | "Provider redesign or a new provider dependency" | No → clarified in R2 | Choosing the M14 default among *already-supported* providers / models is a **selection**, not a redesign or new dependency (§6.1). |

**Result:** every OAQ in §19.1 is verified **genuinely open** to the *M14
Filing Analysis Architecture Decision Pack*. No §6 exclusion prohibits the
pack from evaluating — or, where the frozen externally observable behaviour
requires it, selecting — an implementation mechanism. **No mechanism is
decided, frozen, or pre-approved by this contract**, and no persistence
implementation is authorized.

---

## 20. Governance Status and Authorization Sequence

**M14 milestone:** 🟢 `FORMALLY SELECTED` (Document 63).
**This contract (Document 64):** 🟢 `CTO-RATIFIED (2026-08-31)` — the M14
Filing Analysis API Contract (§22). CQ-1 / CQ-2 / CQ-3 resolved by the
separate CTO decision of 2026-08-31 (§18).
**M14 architecture:** 🔴 `NOT PROPOSED / NOT RATIFIED` (the Architecture
Decision Pack — Document 65 — does not exist; contract ratification does
**not** create or authorize it).
**M14 implementation:** 🔴 `NOT AUTHORIZED` (a separate CTO act after
architecture ratification).
**M14 commit / push:** 🔴 `NOT AUTHORIZED` (each a separate CTO act after
technical review).

```text
Document 62  CTO-RATIFIED POST-M13 ROADMAP  (C-1 = preferred roadmap direction)
        ↓  separate CTO decision
Document 63  M14 = C-1 FILING ANALYSIS — FORMALLY SELECTED
        ↓  contract-governance stage begins
Document 64  M14 FILING ANALYSIS API CONTRACT   ← THIS DOCUMENT — 🟢 CTO-RATIFIED (2026-08-31)
             (provenance: CTO Revisions R1–R2 + CTO Decisions 2026-08-31 applied; CTO-RATIFIED 2026-08-31 — §22)
        ↓  CTO contract ratification — ✅ DONE (2026-08-31, §22)
             [froze the externally observable behaviour §4–§17 — four-output roster, fixed full set,
              flat cited narrative (§8.2), INV-IC, §11.1–§11.9; CQ-1 / CQ-2 / CQ-3 resolved (§18);
              did NOT ratify architecture (§5.1); granted NO code / commit / push]
M14 Filing Analysis Architecture Decision Pack (Document 65)   ← NEXT — NOT created here; resolves §19 OAQ-1…OAQ-10
        ↓  CTO architecture ratification   [freezes architecture; grants NO code]
Separate M14 implementation-authorization decision   ← its own scope-bound CTO act
        ↓
Engineering implementation
        ↓
Technical review
        ↓
Commit authorization  (separate)   →   Push authorization  (separate)
```

**No stage is collapsible.** The CTO **ratified this contract on 2026-08-31**
(§22). That ratification froze only the *externally observable* M14 contract
(§4–§17, per the §5.1 boundary) — the four-output roster, the fixed full set
with no selection parameter, the flat cited narrative (§8.2), INV-IC, and
§11.1–§11.9 — with CQ-1 / CQ-2 / CQ-3 resolved by the separate CTO decision
of 2026-08-31 (§18). It did **not** ratify or authorize any architecture
(persistence, caching, retrieval strategy, execution topology, provider /
model, chunk-vs-section representation, anchor-discovery mechanism — all
§19), did **not** approve or create the Architecture Decision Pack (Document
65), did **not** authorize writing a route / handler / node / schema /
prompt / frontend, did **not** authorize the `APPROVED_ROUTES` update, and
did **not** authorize a commit or a push. **Contract ratification does not
imply architecture authorization, implementation authorization, commit
authorization, or push authorization** — each is a separate, subsequent CTO
act (§22). The terms `APPROVED TO BUILD`, `IMPLEMENTATION READY`, and
`AUTHORIZED` are **not** applied to M14 implementation anywhere in this
document.

**Existing governance state — unchanged by this document:** M13 COMPLETE /
PUBLISHED; Document 62 CTO-RATIFIED; Document 63 M14 FORMALLY SELECTED;
Document 58 UNRATIFIED / HISTORICAL / CONSUMED (not retroactively ratified);
Documents 59 / 60 / 61 FROZEN / untouched; G8 BLOCKED / CARRIED FORWARD; H-1
CLOSED WITH GOVERNANCE FOLLOW-UP; Gate (`JUDGE_SELF_CONSISTENCY_GATE_VERSION`)
= 0.

---

## 21. CTO Decisions — Status

**Resolved by CTO decision dated 2026-08-31 — no further CTO action needed on
these:**

1. **CQ-1 and CQ-2 — RESOLVED.** Roster fixed at exactly four outputs
   (Filing Summary, Risk Factors Digest, MD&A Digest, Important Changes);
   fixed full set; no client-selectable output parameter (§7, §8, §9.2–§9.3,
   §17, §18). — **DONE.**
2. **CQ-3 — RESOLVED.** Per-output response representation is Document 43's
   flat cited narrative — `narrative` + `sources[]` + `cited_source_indices`
   plus output state — specified as a testable field table in §8.2 (§9.3,
   §11.3, §18). — **DONE.**
3. **Contract ratification — DONE (CTO, 2026-08-31; §22).** The CTO ratified
   Document 64 as the M14 Filing Analysis API Contract. Ratification froze
   the externally observable M14 contract (§4–§17): the bounded M14 scope,
   the §5.1 contract-vs-architecture boundary, and the §6 exclusions (Filing
   Q&A / chatbot / cross-filing / durable-sessions / alerts out); **INV-IC**
   (§8.1); the citation / provenance requirements §11.1–§11.9 including the
   `chunk_idx`-range anchor **representation floor** (§11.3), with the
   anchor-**discovery mechanism** left open as **OAQ-9**; and the validation
   / error / determinism / observability / security sections (§10, §12–§15)
   as convention-reuse. It resolved **no** §19 item — chunk-vs-section, C-2
   sequencing, RAG / retrieval strategy, persistence, caching, execution
   topology, LangGraph, and model / provider all remain **OPEN** (§5.1,
   §19).

**The one remaining CTO governance act at this stage:**

4. **Prepare and ratify the *M14 Filing Analysis Architecture Decision Pack*
   (Document 65).** It — not this contract — resolves OAQ-1…OAQ-10. It is
   **NOT** created by this document, and contract ratification neither
   creates nor authorizes it. — **NEXT (separate CTO-governed step).**
5. **Architecture ratification / implementation authorization / commit
   authorization / push authorization** — **NOT** granted by this contract's
   ratification; each is a separate, subsequent CTO act in the §20 ladder
   (architecture ratification → implementation authorization → engineering →
   technical review → commit → push). — **NOT GRANTED HERE.**

---

## 22. CTO Ratification (2026-08-31)

Recorded from the CTO's ratification decision of 2026-08-31, following the
pattern of Document 59 §16 and Document 62 §16. §0–§21 above are **unchanged
in substance** — the only edits made to record this ratification are the
status line, the §20 authorization block and ladder, §21, this section, the
closing block, and **status-consistency wording** (a ratified contract is no
longer described as a "proposal"; the header changelog gains a dated "CTO
Ratification (2026-08-31)" entry). No scope, exclusion, acceptance-criterion,
OAQ, INV-IC, or citation requirement was changed. This section records the
decision and the status transition (`🟡 PROPOSED — CTO DECISION REQUIRED.
NOT RATIFIED` → `🟢 CTO-RATIFIED`).

**Decision: RATIFIED.** The CTO ratified Document 64 as the **M14 Filing
Analysis API Contract**. The ratified position, recorded verbatim:

- **M14 = C-1 Filing Analysis** — formally selected by Document 63; this
  ratification does not re-open or re-perform that selection.
- **Contract status: 🟢 CTO-RATIFIED (2026-08-31).** The externally
  observable M14 contract behaviour is ratified: the four-output roster
  (Filing Summary, Risk Factors Digest, MD&A Digest, Important Changes — §8);
  the fixed full output set with **no** client-selectable output parameter
  (§7, §9.2); the per-output **flat cited narrative** representation
  `narrative` + `sources[]` + `cited_source_indices` + output state (§8.2,
  §9.3); the validation / error semantics (§10); the citation / provenance
  requirements §11.1–§11.9 including the `chunk_idx`-range anchor
  **representation floor** (§11.3); the determinism, observability, and
  security expectations (§12, §14, §15); and the §5, §5.1, §6 scope /
  boundary / exclusions.
- **CQ-1, CQ-2, CQ-3 — resolved by the separate CTO decision of 2026-08-31**
  (§18). This ratification adopts those resolutions into the ratified
  contract; it did not itself decide them.
- **INV-IC (§8.1) is a ratified contract invariant.** "Important Changes" is
  derived **only** from material change language evidenced within the
  selected filing itself — never a previous-filing comparison, cross-filing
  diff, historical trend analysis, or implicit temporal comparison; absent
  such evidence, the `insufficient_evidence` state applies, never
  fabrication.
- **OAQ-1 through OAQ-10 remain open architecture questions, not contract
  decisions** (§19). This ratification resolves none of them and does not
  pre-bias any. Specifically unresolved and reserved to the *M14 Filing
  Analysis Architecture Decision Pack* where applicable: persistence model
  (OAQ-5), retrieval / RAG strategy (OAQ-3), caching / Redis (OAQ-6),
  execution topology — sync vs async, SSE, route family (OAQ-4), LangGraph
  topology (OAQ-7), model / provider selection (OAQ-8), chunk-vs-section
  representation (OAQ-1), the anchor-discovery mechanism (OAQ-9), and the
  whole-filing-vs-scoped cost strategy (OAQ-10).
- **C-2 Structured Filing Extraction — neither selected nor rejected** (§16,
  OAQ-2). Whether C-2 must be sequenced before C-1 is an architecture
  determination; this ratification does not make it.
- **Filing Q&A remains excluded from M14** (§6): no multi-turn or single-turn
  conversational filing Q&A, no generic filing chatbot, no conversational
  memory / session state. M14 produces fixed analysis outputs only.
- **No architecture ratification is granted by this contract ratification.**
  The Architecture Decision Pack (Document 65) does not exist, is not created
  here, and is not authorized by this act; it is a separate, subsequent
  CTO-governed step.
- **No implementation authorization is granted.**
- **No commit authorization is granted.**
- **No push authorization is granted.**

**Governance ladder (unchanged; no stage confers the next):**

```text
Document 63  M14 = C-1 FILING ANALYSIS — FORMALLY SELECTED
        ↓
Document 64  M14 FILING ANALYSIS API CONTRACT — 🟢 CTO-RATIFIED (2026-08-31)   ← COMPLETE
        ↓   (separate CTO act — NOT granted by contract ratification)
Document 65  M14 Filing Analysis Architecture Decision Pack   ← NEXT (not created here)
        ↓   CTO architecture ratification            (separate CTO act)
Implementation authorization                          (separate CTO act)
        ↓
Engineering implementation  →  Technical review
        ↓
Commit authorization  (separate)   →   Push authorization  (separate)
```

**Contract ratification does NOT imply — and this section explicitly
disclaims — any of:** `Contract Ratification → Architecture Authorization`;
`Contract Ratification → Implementation Authorization`; `Contract
Ratification → Commit Authorization`; `Contract Ratification → Push
Authorization`.

**Existing governance state — unchanged by this ratification:** M13 COMPLETE
/ PUBLISHED; Document 62 CTO-RATIFIED (2026-08-30); Document 63 M14 FORMALLY
SELECTED (2026-08-30); Document 58 UNRATIFIED / HISTORICAL / CONSUMED (not
retroactively ratified); Documents 59 / 60 / 61 frozen / untouched; G8
BLOCKED / CARRIED FORWARD; H-1 CLOSED WITH GOVERNANCE FOLLOW-UP; Gate
(`JUDGE_SELF_CONSISTENCY_GATE_VERSION`) = 0.

**Recording note.** This section records a decision already issued by the
CTO; it creates no authorization of its own. Adding it changed only this
document, in the working tree — nothing was staged, committed, or pushed,
and no `docs/backend_engineering/65` was created. Cumulative provenance:
**CTO Revisions R1–R2 + CTO Decisions 2026-08-31 applied; CTO-RATIFIED
2026-08-31.**

---

**NO IMPLEMENTATION PERFORMED. NO ARCHITECTURE DECISION MADE. NO SOURCE,
TEST, SCHEMA, INDEX, MIGRATION, ROUTE, LANGGRAPH, RETRIEVAL / RAG, MONGODB,
REDIS, PROVIDER, OR FRONTEND FILE CREATED OR MODIFIED. THIS DOCUMENT IS
🟢 CTO-RATIFIED (2026-08-31, §22) AS THE M14 FILING ANALYSIS API CONTRACT.
M14 IS FORMALLY SELECTED (DOCUMENT 63). RATIFICATION FROZE ONLY THE
EXTERNALLY OBSERVABLE M14 CONTRACT (§4–§17) — FOUR-OUTPUT ROSTER, FIXED FULL
SET WITH NO CLIENT SELECTION PARAMETER, FLAT CITED NARRATIVE (§8.2), INV-IC,
§11.1–§11.9 — AND GRANTS NO ARCHITECTURE RATIFICATION, NO IMPLEMENTATION
AUTHORIZATION, AND NO COMMIT OR PUSH AUTHORIZATION; EACH IS A SEPARATE,
SUBSEQUENT CTO ACT. THE CHUNK-VS-SECTION QUESTION REMAINS OPEN, AS DOES THE
ANCHOR-DISCOVERY MECHANISM (OAQ-9), AND EVERY §19 ITEM (OAQ-1…OAQ-10). C-2 IS NEITHER SELECTED NOR REJECTED AND
MAY BE A TECHNICAL SEQUENCING PREREQUISITE — AN OPEN ARCHITECTURE DECISION.
FILING Q&A / GENERIC CHATBOT / CROSS-FILING ANALYSIS / DURABLE SESSIONS /
ALERTS ARE OUT OF M14 SCOPE. "IMPORTANT CHANGES" IS FILING-LOCAL ONLY
(INV-IC, §8.1) — NO PREVIOUS-FILING COMPARISON, CROSS-FILING DIFF, TREND
ANALYSIS, OR IMPLICIT TEMPORAL COMPARISON. CQ-1 / CQ-2 / CQ-3 ARE RESOLVED
BY CTO DECISION (2026-08-31), FOLDED INTO §7 / §8 / §8.2 / §9 / §18: FOUR
OUTPUTS ONLY (FILING SUMMARY, RISK FACTORS DIGEST, MD&A DIGEST, IMPORTANT
CHANGES), FIXED FULL SET WITH NO CLIENT SELECTION PARAMETER, FLAT CITED
NARRATIVE (NARRATIVE + SOURCES[] + CITED_SOURCE_INDICES). THESE ARE
PRODUCT / API-CONTRACT DECISIONS ONLY; RESOLVING THEM DID NOT RATIFY THE
CONTRACT. NO RAG, RETRIEVAL, PERSISTENCE, CACHING, REDIS, OR
LANGGRAPH-TOPOLOGY DECISION WAS MADE. §6'S MECHANISM-NAMING EXCLUSIONS BOUND
WHAT THIS CONTRACT AUTHORIZES AND WHAT M14 DELIVERS; THEY DO **NOT** BAR THE
ARCHITECTURE DECISION PACK FROM EVALUATING OR SELECTING A MECHANISM
(INCLUDING A NEW COLLECTION / INDEX / SCHEMA / MIGRATION FOR PERSISTENCE)
NEEDED TO SATISFY THE FROZEN OBSERVABLE BEHAVIOUR — ANY SUCH MECHANISM IS
INTRODUCED VIA ARCHITECTURE RATIFICATION PLUS NORMAL SCHEMA-CHANGE
GOVERNANCE, NEVER AS PRE-AUTHORIZED HERE (§6.1, §19.3, REVISION R2). NO
PERSISTENCE IMPLEMENTATION IS AUTHORIZED; OAQ-5 REMAINS OPEN. C-2 REMAINS
NEITHER SELECTED NOR REJECTED. FILING Q&A REMAINS EXCLUDED FROM M14. G8
REMAINS BLOCKED / CARRIED FORWARD. H-1 REMAINS CLOSED WITH GOVERNANCE
FOLLOW-UP. M13 REMAINS COMPLETE / PUBLISHED. DOCUMENTS 58–63 NOT MODIFIED.
NO `docs/backend_engineering/65` CREATED. NO STAGE. NO COMMIT. NO PUSH. NO
MERGE / REBASE / RESET / RESTORE / CLEAN. THE NEXT AUTHORIZED GOVERNANCE
ACTIVITY IS PREPARATION OF THE M14 FILING ANALYSIS ARCHITECTURE DECISION
PACK (DOCUMENT 65 — NOT CREATED HERE), AS A SEPARATE CTO-GOVERNED STEP.**
