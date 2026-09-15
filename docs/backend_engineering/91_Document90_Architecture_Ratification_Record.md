# 91 — Document 90 Architecture Ratification Record

**Status:** 🟠 **DRAFT / PENDING CTO REVIEW — PROPOSED ARCHITECTURE
RATIFICATION OF DOCUMENT 90. NOT RATIFIED. THIS RECORD DOES NOT
SELF-RATIFY. THIS RECORD MAY BE CTO-REVIEWED AND APPROVED FOR
RATIFICATION NOW, SUBJECT TO COMPLETION OF THE DOCUMENT 88 / 89
API-CONTRACT RATIFICATION CHAIN — THE FORMAL RATIFICATION OF DOCUMENT 90
DOES NOT TAKE EFFECT UNTIL BOTH THIS RECORD'S OWN SEPARATE CTO
RATIFICATION AND THAT CHAIN'S COMPLETION (INCLUDING DOCUMENT 89'S OWN
FORMAL RATIFICATION) HAVE OCCURRED.**

This document is the authoritative ratification record for
[90_M16_Filing_QA_Architecture_Decision_Pack.md](90_M16_Filing_QA_Architecture_Decision_Pack.md)
— the **M16 Architecture Decision Pack — Filing Q&A (FQA v1)**. It
performs **exactly one** governance act: the **formal ratification of
Document 90 as the M16 Filing Q&A (FQA v1) implementation architecture**.
**This record may itself be CTO-reviewed and approved for ratification
now — but that approval does not, by itself, bring Document 90's
architecture ratification into effect.** Effect requires **both**: (a)
this record's own separate CTO ratification, **and** (b) completion of
the Document 88 / 89 API-contract ratification chain, including Document
89's own formal ratification (§4, §7, §14). **Neither condition alone is
sufficient, and at the time of this record neither has occurred.** It is
a **separate governance act**, distinct from Document 90 itself: it
ratifies the architecture Document 90 already proposed — it does **not**
perform the architecture design (Document 90 already did that), it does
**not** redesign M16 / FQA v1, it does **not** create any new architecture
decision, and it does **not** reinterpret, amend, or supersede Documents
83, 84, 85, 86, 87 Revision 2, 88, 89, or 90. **The decision this record
proposes is: Document 90, as reviewed and approved, becomes the ratified
M16 Filing Q&A (FQA v1) architecture once — and only once — both
prerequisite conditions above are satisfied.**

**Architecture ratification, once effective, authorizes progression to a
future, separate M16 Implementation Authorization Decision only — it does
NOT, itself, authorize implementation** (§13, §14).

**Type:** Governance / architecture ratification decision record
(documentation only — no source code, test, configuration, schema,
migration, index, route, endpoint, LangGraph node / topology, retrieval /
RAG change, MongoDB collection, Redis usage, provider selection,
evaluation infrastructure, metrics-catalog change, or frontend file
created or modified to produce it; `.gitignore` untouched. Documents
63–90 read, not modified; no backend source file modified. The only file
this task creates is this document.

**Date:** 2026-09-11.

**Precedent / lineage.** This record follows the same standalone
decision-record form established by
[74_Document73_R1_CTO_Architecture_Ratification_Record.md](74_Document73_R1_CTO_Architecture_Ratification_Record.md)
for ratifying an **architecture decision pack** without modifying it,
applied here one milestone later to Document 90 (the M16 pack) instead of
Document 73 (the M15 pack). It performs exactly one governance act:
ratifying Document 90 as the M16 FQA v1 architecture. It does not
reinterpret Document 87 Revision 2 (the frozen API contract — its
Documents 88 / 89 ratification chain remains incomplete, pending Document
89's own ratification gate), Document 88 or Document 89 (the pending
API-contract ratification chain), or Documents 83 / 85 / 84 / 86 (the
ratified scope and milestone selection) — all are cited as frozen input,
not amended.

---

## 1. Purpose

This document exists to place a single, unambiguous, authoritative
governance record on the milestone ladder: the **formal ratification of
the M16 Filing Q&A (FQA v1) architecture as specified in Document 90**.

Document 90 is the substantive artifact — it contains every architecture
decision (retrieval, evidence representation, `JobKind` realization,
transient retention, AH-2 compliance, generation, citation validation,
model / BYOK, output bounding, evaluation requirement, security, SSRF,
ownership, observability, performance, failure / retry, M14 / M15 reuse,
testing architecture, deployment). Document 90 has passed CTO review and
is **APPROVED FOR RATIFICATION**, but is **not yet ratified**.

This record (Document 91) is the **separate authoritative instrument**
that ratifies Document 90. It:

- adds no architecture decision, and reinterprets none;
- does not modify Document 90 or any other governance document;
- does not authorize implementation, source-code changes, test / config
  changes, schema / index / migration work, Redis persistence, LangGraph
  changes, frontend work, evaluation infrastructure, deployment, release,
  or any Git mutation (§13);
- states explicitly that **architecture ratification ≠ implementation
  authorization** (§14);
- identifies the next governance artifact as the separate **M16
  Implementation Authorization Decision** (§15) — reachable only once
  Document 90's architecture ratification actually takes effect.

Document 91 itself is **DRAFT / PENDING CTO REVIEW** and does not
self-ratify (banner; §7). **Even once Document 91 is itself CTO-ratified,
Document 90's architecture ratification does not take effect until the
Document 88 / 89 API-contract ratification chain — including Document
89's own formal ratification — is also complete** (§7, §14).

---

## 2. Document Metadata

| Field | Value |
|---|---|
| Document number | 91 |
| Title | Document 90 Architecture Ratification Record |
| Ratifies | Document 90 — M16 Architecture Decision Pack — Filing Q&A (FQA v1) |
| Ratified revision | Document 90 as-published — **no revision marker present** (§3) |
| Milestone | M16 = Filing Q&A (FQA v1) (Documents 84 / 86) |
| Product scope | single-turn + stateless + single-filing (Documents 83 / 85) |
| Frozen API contract | Document 87 Revision 2 (frozen input); Documents 88 / 89 ratification chain **not yet complete** — pending Document 89's own ratification gate (§4) |
| Governance stage | Architecture ratification (this act) |
| Predecessor gate | Document 90, CTO-reviewed, **APPROVED FOR RATIFICATION**, not yet ratified |
| Prerequisite gate | Document 88 / 89 API-contract ratification chain — **not yet complete**; pending Document 89's own formal ratification (§4) |
| This document's own status | DRAFT / PENDING CTO REVIEW — does not self-ratify |
| Effective only when | **BOTH** (a) this document is itself CTO-ratified, **AND** (b) the Document 88 / 89 chain above is formally complete (§7, §14) — neither condition alone is sufficient |
| Successor gate (NOT created here) | A separate, future **M16 Implementation Authorization Decision** |
| Files created by this task | this document only |
| Files modified by this task | none |
| Git mutations by this task | none |

---

## 3. Exact Ratification Target and Document 90 Revision Identity

**Target: Document 90 — M16 Architecture Decision Pack — Filing Q&A
(FQA v1), as published in
[90_M16_Filing_QA_Architecture_Decision_Pack.md](90_M16_Filing_QA_Architecture_Decision_Pack.md).**

Verified this session, read-only, before recording this ratification:

- Document 90's top-line Status banner reads: *"🟡 M16 ARCHITECTURE
  DECISION PACK — PROPOSAL / PENDING CTO REVIEW. NOT RATIFIED. NOT AN
  IMPLEMENTATION AUTHORIZATION."*
- **Document 90 carries no revision marker.** There is **no
  `Revision R1`, `Revision R2`, or `Revision N` block anywhere in the
  file** — it exists as a single, un-revised proposal artifact. The
  "Revision 2" strings that appear in Document 90 refer to **Document 87
  Revision 2** (the frozen API contract input), not to Document 90's own
  revision state.
- `docs/backend_engineering/` was listed in full: the highest-numbered
  file prior to this task was `90_M16_Filing_QA_Architecture_Decision_Pack.md`.
  No second Document-90-shaped file, and no Document 90 revision, exists
  anywhere in the repository.
- Document 90's own closing attestation and terminal line
  (*"DOCUMENT 90 M16 FILING Q&A ARCHITECTURE DECISION PACK COMPLETE —
  AWAITING CTO REVIEW"*) confirm it is the current, complete architecture
  artifact for M16.

**No discrepancy was found. Document 90 as-published — with no revision
identifier — is confirmed as the correct and only architecture-ratification
target.** This record ratifies that artifact exactly, and makes no claim
about, and does not ratify, any later revision. If a Document 90 revision
is ever introduced, it requires its own separate CTO review and
ratification; this record does not, and cannot, extend to it.

---

## 4. Predecessor Governance State (verified, not re-decided)

The following governance state is taken as **established and frozen
input** to this ratification. This record does not re-run, re-open, or
re-decide any of it.

| Prior artifact | Governance act it performed | State carried into this record |
|---|---|---|
| **Document 83** — Filing Q&A Scope Pre-Decision | Proposed FQA v1 scope = single-turn + stateless + single-filing | Ratified via Document 85. Frozen. |
| **Document 85** — Document 83 CTO Ratification Record | Ratified the FQA v1 scope | 🟢 CTO-RATIFIED. FQA v1 scope is authoritative. |
| **Document 84** — M16 Milestone Selection Record | Proposed M16 = Filing Q&A (FQA v1) | Ratified via Document 86. Frozen. |
| **Document 86** — Document 84 CTO Ratification Record | Ratified the M16 selection | 🟢 CTO-RATIFIED. M16 = Filing Q&A (FQA v1). |
| **Document 87 Revision 2** — M16 API Contract Proposal | Fixed the externally observable request / response, citation, error, state, job, and SSE semantics for FQA v1 | CTO-reviewed and approved along the Documents 88 / 89 ratification chain; that chain is **not yet formally complete** (below). Frozen input to Document 90 and to this record regardless. Not reopened. |
| **Document 88** — Document 87 CTO Ratification Record | CTO-reviewed and **approved for ratification** of the Document 87 Revision 2 API contract — **not yet formally ratified itself** | Part of the API-contract ratification chain; its formal ratification is pending Document 89 (below). Not modified here. |
| **Document 89** — Document 88 CTO Ratification Record | **Proposes** the formal ratification of Document 88; is itself **DRAFT / PENDING CTO REVIEW, NOT YET RATIFIED** | The terminal gate whose own completion would finalize Document 88's ratification and the contract's fully-ratified status. **Not yet ratified.** Not modified here. |
| **Document 90** — M16 Architecture Decision Pack — FQA v1 | Proposed the implementation architecture, strictly within the Document 87 Revision 2 contract and the Documents 83 / 85 scope; resolved every Open Architecture Question the contract left to the pack | **CTO-reviewed, APPROVED FOR RATIFICATION, not yet ratified.** This is the target of the present record. |

**Current governance state at the moment of this record:**

- M15 / C-4 is **closed** (Documents 79 / 80) and is not reopened.
- FQA v1 **scope is ratified** (Documents 83 / 85).
- M16 is **selected and ratified** (Documents 84 / 86).
- The **Document 87 Revision 2 API contract** has been CTO-reviewed and
  approved along the Documents 88 / 89 ratification chain: Document 88 is
  CTO-reviewed and **approved for ratification**; Document 89 — the
  record whose own ratification would finalize Document 88's — remains
  **DRAFT / PENDING CTO REVIEW, NOT YET RATIFIED**. **The chain's formal
  ratification is therefore not yet complete.**
- Document 90 has **passed CTO review and is APPROVED FOR RATIFICATION**,
  but **is not yet ratified**.
- **Document 91's own eventual CTO ratification, by itself, does NOT
  bring Document 90's architecture ratification into effect** while the
  Document 88 / 89 chain above remains incomplete — both conditions must
  hold together (§7).
- **M16 implementation is NOT authorized.**

Consistent with Document 90 §1 and §26, and with the Document 74
precedent, this architecture ratification **presupposes the eventual
completion** of the Document 88 / 89 API-contract ratification chain —
which, at the time of this record, remains pending Document 89's own
ratification gate; it does not pre-empt, substitute for, complete, or
re-perform that chain.

---

## 5. Governance Lineage

| Document | Role | Governance act performed |
|---|---|---|
| **Document 83** | Filing Q&A Scope Pre-Decision | **Scope pre-decision.** FQA v1 = single-turn + stateless + single-filing. |
| **Document 85** | Document 83 CTO Ratification Record | **Scope ratification.** |
| **Document 84** | M16 Milestone Selection Record | **Milestone selection.** M16 = Filing Q&A (FQA v1). |
| **Document 86** | Document 84 CTO Ratification Record | **Milestone-selection ratification.** |
| **Document 87 Revision 2** | M16 API Contract Proposal | **API contract.** Externally observable FQA v1 semantics. |
| **Document 88** | Document 87 CTO Ratification Record | **Proposed API-contract ratification** — CTO-reviewed, approved for ratification, **not yet formally ratified itself**. |
| **Document 89** | Document 88 CTO Ratification Record | **Terminal API-contract ratification wrapper** — itself **DRAFT / PENDING CTO REVIEW, NOT YET RATIFIED**. |
| **Document 90** | M16 Architecture Decision Pack — FQA v1 | **Architecture decision pack.** Proposes how the ratified contract is realized behind the contract line; resolves the pack-owned Open Architecture Questions. |
| **Document 91 (THIS)** | Document 90 Architecture Ratification Record | **Architecture ratification.** The distinct act that ratifies Document 90 as the M16 FQA v1 architecture — on this record's own separate CTO ratification. |

These nine roles are **not interchangeable** and this record does not
conflate them. In particular: **Document 91 is an architecture
ratification, not an implementation authorization** (§13, §14) — a
further, separate, subsequent CTO act that this record does not perform
and does not imply.

---

## 6. CTO Architecture-Review Outcome Recorded

The CTO has reviewed Document 90 and issued: **DOCUMENT 90 — APPROVED FOR
RATIFICATION.** This record captures that outcome and performs the
corresponding ratification (§7). Review confirmed, without requiring any
change to Document 90:

- the architecture stays **strictly behind the Document 87 Revision 2 API
  contract** — no externally observable behaviour is fixed, weakened, or
  extended (Document 90 §1);
- the FQA v1 **product scope** (single-turn, stateless with respect to
  durable conversational / research state, single-filing, `(ticker,
  doc_id)` identity) is preserved in every decision (Document 90 §2);
- the pack is **additive and code-only** — one module, four routes, one
  additive `JobKind` member, an operational-config set, one metrics
  counter, one in-process buffer dict — and changes no existing route,
  node, collection, index, graph, or contract (Document 90 §3, §19);
- every Open Architecture Question the contract delegated to the pack is
  resolved within the pack, with no new dependency, provider, store,
  embedder, reranker, SSE mechanism, job protocol, or error class
  (Document 90 §0, §4, §19);
- **AH-1 and AH-2 are preserved**, not reinterpreted (Document 90 §9);
- **DRS remains BLOCKED and outside M16** (Document 90 §2, §25);
- the established **security, SSRF, ownership, BYOK, error-taxonomy, SSE,
  observability, and deployment** constraints are reused verbatim
  (Document 90 §11, §15, §16, §18, §21).

---

## 7. Governance Act Performed — Architecture Ratification Decision

**DOCUMENT 90 — M16 ARCHITECTURE DECISION PACK — FILING Q&A (FQA v1) IS
PROPOSED FOR FORMAL RATIFICATION AS THE M16 FQA v1 IMPLEMENTATION
ARCHITECTURE**, exactly as reviewed and approved.

**This record may be CTO-reviewed and approved for ratification now,
subject to completion of the Document 88 / 89 API-contract ratification
chain.** Formal ratification of Document 90 under this record does
**NOT** take effect until **both**:

1. **Document 91 is itself CTO-ratified** — its own separate review and
   ratification act, distinct from Document 90's (banner; §2); **and**
2. **the Document 88 / 89 API-contract ratification chain is formally
   complete — including Document 89's own formal ratification** (§4).

**Neither condition alone is sufficient.** If Document 91 is CTO-ratified
while the Document 88 / 89 chain remains incomplete, Document 90's
architecture ratification remains **HELD PENDING** — it does **not** take
effect on Document 91's ratification date alone, and Document 90 remains
CTO-reviewed / APPROVED FOR RATIFICATION / not yet ratified until the
chain also completes. Conversely, the Document 88 / 89 chain completing
does not, by itself, ratify Document 90 — Document 91's own separate CTO
ratification is still independently required. **At the time of this
record, neither condition has occurred.**

This is the **single** governance act this record performs, effective
only once both conditions above hold. It:

- **confirms** the architecture position already recorded in Document
  90 §§3–24;
- **does not** re-derive, redesign, extend, narrow, or reinterpret that
  architecture;
- **does not** modify Document 90 — Document 90's text, decisions,
  rationale, boundaries, and attestations stand exactly as published;
- **does not** create any new architecture decision, architecture
  decision pack, or "ratification-of-Document-91" record;
- **does not** authorize implementation (§13, §14).

**Separately and explicitly: M16 implementation is NOT authorized.**
Architecture ratification and implementation authorization are two
distinct, sequential CTO acts; this record performs (proposes, pending
its own CTO review **and** the Document 88 / 89 chain's completion) only
the first.

**Document 91's own status:** DRAFT / PENDING CTO REVIEW. This record does
not self-ratify; the ratification it proposes takes effect only once
**both** (a) Document 91's own separate CTO review and ratification, and
(b) the Document 88 / 89 API-contract ratification chain's own formal
completion (including Document 89's formal ratification), have occurred.

---

## 8. Architecture Decisions Being Ratified (Document 90, preserved exactly)

The ratification covers **all** of Document 90's architecture decisions
and boundaries. It preserves each exactly as Document 90 specifies; the
restatements below are pointers to Document 90, **not** new or amended
decisions.

### 8.1 Deterministic candidate universe and candidate capping (Document 90 §5, §23 row 1)

Ratified exactly as specified:

- an **ordered candidate universe** — the filing's ordered chunks
  (`chunk_idx` ascending, as `_load_ordered_filing_chunks` returns them);
- with universe size `N`, cap `K = MAX_CANDIDATE_CHUNKS`: **`N ≤ K` means
  every chunk is a candidate**;
- **`N > K` uses the defined deterministic stride-selection algorithm** —
  `stride = ceil(N / K)`, select `U[0], U[stride], U[2·stride], …`;
- **highest-`chunk_idx` completion where required** — if integer striding
  yields fewer than `K`, append the not-yet-selected chunks with the
  highest `chunk_idx`, in order, until exactly `K` are selected;
- the selected set is **re-sorted by `chunk_idx`** and **deterministically
  numbered** `1..K` for the model;
- the selection is a pure function of `(U, K)` — **independent of any
  model output**, reproducible run-to-run;
- **bounded by `MAX_CANDIDATE_CHUNKS`**, with each excerpt trimmed to
  `MAX_CANDIDATE_CHARS`;
- **first and last coverage preserved** — the filing's first and last
  chunk are always represented (head-and-tail coverage, never a silently
  dropped tail).

### 8.2 Candidate coverage semantics (Document 90 §5.1, §5.2, §23 row 1)

Ratified exactly as specified:

- the architecture **distinguishes the full candidate universe considered
  from the bounded, model-facing candidate subset** — "full-filing
  candidate mode" names the universe considered, not what is placed in
  the prompt;
- **partial / incomplete candidate coverage is explicitly disclosed** via
  a machine-readable `coverage_boundaries` reason string on the completed
  `answer` object (the M14 `_cap_boundary` pattern);
- **partial candidate coverage does NOT, by itself, determine `state`**;
- **`state` remains governed solely by the Document 87 Revision 2 §9.1 /
  §9.2 `answered` / `insufficient_evidence` semantics** — a bounded or
  partially-covered candidate set that still satisfies §9.1 is
  `answered`, **carrying** the coverage disclosure; `insufficient_evidence`
  occurs only under the §9.2 conditions;
- retrieval success is **never** interpreted as proof that the complete
  filing was searched; this invariant makes **no** semantic-grounding
  judgement.

### 8.3 Retrieval degradation (Document 90 §5, §5.1, §18, §23 row 14)

Ratified exactly as specified.

**Recoverable degradation — job continues with a bounded candidate set
and a `coverage_boundaries` disclosure, no error, no new state:**

- dense embedder / cross-encoder reranker unavailable → **BM25-only**
  ranking;
- retrieval returns an empty ranked list → **deterministic
  evenly-spaced sampling** across the ordered filing;
- in both cases the job **continues with coverage disclosure**; `state`
  is still decided only by §11 / Document 87 Revision 2 §9.1–§9.2.

**Unrecoverable failure — job `fails` and maps to the existing `502
infrastructure_error` taxonomy member (Document 87 Revision 2 §12), with
no new error class and no Document 87 Revision 2 behaviour change:**

- database / persistence-layer failure;
- chunk-loading failure (`_load_ordered_filing_chunks` raises);
- filing-resolution failure (`db.filings.find_one` raises);
- any unhandled retrieval-infrastructure failure that is not one of the
  graceful-degrade paths.

**Zero-content is preserved as a data condition, not an infrastructure
failure** — a resolved filing with zero usable persisted content
completes as **`200 / completed / insufficient_evidence`**, empty
`sources` / `cited_source_indices`, a bounded honest `answer_text`, and a
`coverage_boundaries` entry — **never a 404, never a 502**.

### 8.4 Generation invariant (Document 90 §10, §18, §23 row 6)

Ratified exactly as specified:

- **at most one logical answer-generation request per FQA job**;
- **zero model calls on the deterministic empty-candidate / zero-content
  `insufficient_evidence` paths**;
- **exactly one generation call when generation is required and
  candidates exist** — one `chat_json` call, HEAVY tier, over an output
  schema whose only model-trusted field is `answer_text`;
- **no repair generation** — malformed / unrepairable structured model
  output surfaces as `502 llm_provider_error`, never a second model
  call (a structured-output-repair completion is not permitted by
  Document 87 Revision 2 §17.1 as drafted);
- **no refinement loop** — no iterative-refinement branch, no conditional
  second call, no "generate more" path;
- **transport-level retries inside `agents/llm.py` that create no
  additional model completion do not constitute additional completions**
  and remain permitted and unchanged.

### 8.5 Citation architecture (Document 90 §11, §23 row 7)

Ratified exactly as specified:

- **deterministic structural citation validation** — `resolve_and_validate`
  (M14 pattern) runs on every returned answer: parse `[n]` markers, keep
  only in-range markers, coalesce strictly contiguous cited `chunk_idx`
  into inclusive ranges, build 1-based unique `sources[]` in the frozen
  `{index, doc_id, chunk_start, chunk_end}` shape (every `doc_id` equal to
  the path `doc_id`), rewrite `[n]` → `[source_index]`, strip orphans,
  compute `cited_source_indices` as the exact structural subset, enforce
  the structural invariants;
- **semantic grounding remains an evaluation concern** — whether a cited
  passage *substantiates* a claim, and whether prose contains an uncited
  substantive claim, are semantic questions handled offline by the §14
  evaluation architecture (Document 87 Revision 2 §20 OAQ-4), never a
  runtime gate, never an error path;
- **`FilingQACitationStructureError` remains module-internal** — a
  structurally unrepairable result raises this marker class
  (`ValueError` subclass), which the orchestrator catches and degrades to
  `insufficient_evidence`; it is **never published as an error**;
- **no expansion of the external error taxonomy** — the nine-class
  `backend/domain/errors.py` taxonomy is unchanged; zero new error
  classes; no third `state` value; no new citation syntax or mechanism.

### 8.6 The existing Document 87 API contract remains unchanged (Document 90 §1, §23)

Ratified exactly as specified. Every externally observable behaviour of
Document 87 Revision 2 is treated as immutable frozen input: the
four-route async `qa` family, the route inventory `51 → 55`, the create
response `200 {id, status:"queued", reused:false}` with `reused` always
`false`, the `queued → running → completed | failed | cancelled`
lifecycle on the shared `MAX_ACTIVE_JOBS` budget, the frozen completed
`answer` object shape, idempotent cancellation, the SSE `final`-frame
semantics, the closed two-value `state` enum `{answered,
insufficient_evidence}` with the §9.1 / §9.2 definitions, zero-content
filing behaviour, the `[n]` / `sources[]` / `cited_source_indices`
citation convention with the frozen external locator, deterministic
runtime citation-**structure** validation only, the BYOK field set, the
`require_admin` + `assert_public_url` SSRF boundary, owner-scoped job
records with a shared filing corpus, the nine-class error taxonomy with
the one `400`-without-`type` SSRF-guard response, the
one-logical-answer-generation rule, and the numeric-bound-as-operational-
configuration treatment. This record **does not alter Document 87
Revision 2** in any way (§9).

### 8.7 AH-1 / AH-2 remain preserved (Document 90 §8, §9, §23 rows 4–5)

Ratified exactly as specified — see §10 of this record.

### 8.8 DRS remains outside M16 (Document 90 §2, §25, §23)

Ratified exactly as specified — see §11 of this record.

### 8.9 Document 90's remaining architecture decisions and boundaries (Document 90 §6, §7, §8, §12, §13, §14, §16, §17, §19, §20, §21, §22, §24)

Ratified exactly as specified, without restatement-by-omission implying
any change:

- **Evidence / passages representation** (§6) — reuse of the existing
  unstructured `filing_chunks` corpus; internal ordered list,
  model-facing numbered excerpts, external frozen locator built by the
  deterministic validator via contiguous coalescing; no
  `filing_qa_passages` collection, no persisted chunk-range store, no
  re-chunking, no embedding persistence.
- **Async `JobKind` realization** (§7) — one additive `str, Enum` member
  `JobKind.FILING_QA = "filing_qa"` in `backend/domain/models.py` (a code
  enum addition, not a schema / index / migration); the existing
  `JobStatus` lifecycle and the shared `MAX_ACTIVE_JOBS` admission
  budget; an operational `job_deadline_filing_qa_s`.
- **Transient result retention** (§8) — a process-local, TTL-bounded
  in-process buffer `_FILING_QA_RESULTS`, a direct peer of
  `_FILING_ANALYSIS_RESULTS` / `_CHANGE_BRIEF_RESULTS`: written on
  `completed`, owner-scoped read, oldest-first eviction, expiry sweep,
  popped on cancel and every failure path, `GET` after expiry →
  `{status:"completed"}` with no `answer` key, the SSE `final` frame
  built from this same buffer and no other mechanism (no `final` frame if
  the buffer entry is expired / unavailable); `reused` always `false`; no
  result collection, no Redis cache, no cross-process persistence, no
  `08_MongoDB_Data_Architecture.md` amendment.
- **Model / provider / BYOK architecture** (§12) — all LLM access through
  `agents/llm.py` `chat_json`; HEAVY tier; no light-model step; BYOK
  fields threaded per request via the `contextvar`; `llm_api_key` never
  persisted, never logged; `PROMPT_VERSION` / `SCHEMA_VERSION` constants;
  `prompt_version` non-null for FQA. No provider / model dependency is
  selected or added; `agents/llm.py` is not changed.
- **Output bounding** (§13) — every bound is operational configuration
  with a recommended starting value and **no contract literal**; the
  `answer_text` / `sources[]` bound is applied **citation-safely** by the
  validator and **degrades to `insufficient_evidence`** rather than
  raw-truncating or partially citing; the candidate cap (§8.1 above) is
  distinct, discloses via `coverage_boundaries`, and does **not** set
  `state`.
- **Evaluation architecture** (§14) — **requirement recorded only**; the
  held-out FQA semantic-evaluation concern (substantiation, uncited-claim
  detection, answerability calibration) follows the D77 / D78 precedent
  as **desirable tracked future work, not a hard commit / ship gate**;
  `agents/scoring.py` is available as a dependency-free scoring
  primitive; **nothing is built or authorized** — no dataset, harness,
  runner, CI gate, scorecard, or `backend/evaluation/` addition.
- **Observability** (§16) — one `pipeline.filing_qa` span;
  `retrieving` / `answering` / `validating` SSE `TraceEvent` frames then
  the `final` frame then `event: end`; reuse of `jobs_active` and
  `retrieval_duration_seconds`; one additive
  `filing_qa_runs_total{outcome}` counter recorded as a requirement; a
  `20_M6_Metrics_Catalog.md` addendum is a **separate documentation
  task**, not performed or authorized here.
- **Performance / resource controls** (§17) — single-filing surface cap;
  at most one generation call; shared `MAX_ACTIVE_JOBS` admission;
  per-kind deadline enforced at node boundaries; `MAX_CANDIDATE_CHUNKS` ×
  `MAX_CANDIDATE_CHARS` prompt-size bounds; no client work knob; the
  inherited stale-job reaper; a fixed, version-pinned grounding-only
  `_SYSTEM` prompt.
- **M14 / M15 infrastructure reuse** (§19) — `JobLifecycle`, `JobStatus`,
  the shared budget, `sse_response()` + the `final`-frame injection
  pattern, `agents/llm.py` + the BYOK contextvar, `agents/retrieval.py` +
  the opt-in `doc_id` filter, `_load_ordered_filing_chunks` +
  `db.filings.find_one`, the `resolve_and_validate` /
  `_coalesce_contiguous` patterns, the in-process buffer mechanism,
  `require_admin` / `assert_public_url`, `RUNNING_TASKS`, the tracer and
  Prometheus registry, `agents/scoring.py`, and the `domain/errors.py`
  taxonomy — **reused unchanged**; net-new surface is one module, four
  routes, one enum member, an operational-config set, one counter, and
  one buffer dict.
- **Testing architecture** (§20) — **requirement recorded only**;
  hermetic unit tests for `agents/filing_qa.py` with a fake `chat_fn`
  (deterministic evenly-spaced capping is reproducible, bounded,
  head-and-tail spanning, model-output-independent; partial coverage does
  not downgrade `state`; validator behaviour; citation-safe bounding
  degradation; zero-content / empty-candidate → `insufficient_evidence`
  with zero model calls; recoverable degradation continues;
  adversarial-instruction grounding holds or degrades) plus an additive
  `backend_test_iter*.py` live-HTTP contract suite (route-inventory guard
  `51 → 55` — exactly four new entries; response shapes; SSE `final`-frame
  semantics; the 422 / 404 / `insufficient_evidence` boundaries; frozen
  locator shape; error-taxonomy `type` values, zero new classes; SSRF
  `400` / `403`; non-owner `404`), run under the **existing `pytest.ini`
  with `addopts` (`-n 2 --dist loadscope`) untouched**; semantic-support
  assertions are out of the contract floor. **Writing any test file or
  editing `pytest.ini` is not authorized.**
- **Deployment implications** (§21) — **no change to deployment
  topology**; no new service, container, process, or port; the
  single-instance operational invariant (the buffer, `RUNNING_TASKS`, the
  auth rate-limiter) carried forward; new environment variables are
  operational configuration with recommended defaults; **no MongoDB
  migration, no index, no Redis, no new model download**; `scripts/run.py`
  and the three-service dev topology unaffected. **No infra change, no
  deploy, no release, no env-file edit in a real environment is
  authorized.**
- **Alternatives rejected** (§22) — a persisted section store, a new
  vector store / embedder / reranker, a LangGraph subgraph, a durable
  Mongo / Redis result store, a structured-output-repair second call, a
  light-model pre-classification step, identity-keyed result reuse
  (`reused: true`), a runtime semantic-support gate, and an owner-scoped
  filing corpus — all remain rejected for the reasons Document 90 §22
  states; this record does not reopen any of them.
- **Implementation constraints** (§24) — Document 90 §24's enumeration of
  what a *subsequent* Implementation Authorization act would and would
  not authorize is preserved verbatim in effect; nothing in that list is
  authorized by this record (§13).

### 8.10 Existing security, ownership, BYOK, SSRF, error, SSE, observability, and deployment constraints remain preserved (Document 90 §11, §15, §16, §18, §21)

Ratified exactly as specified — see §12 of this record.

---

## 9. Contract Preservation — Explicit Boundary

**Document 87 Revision 2 is the M16 API contract — CTO-reviewed and
approved along the Documents 88 / 89 ratification chain, whose own formal
completion remains pending Document 89's ratification gate (§4) — and is
treated here as a frozen, non-negotiable input regardless of that pending
completion.** Document 90 is the architecture realizing that contract;
this record confirms the architecture, not the contract.

**This record does NOT:**

- alter, weaken, extend, or reinterpret **Document 87 Revision 2**;
- alter, reinterpret, or supersede **Document 88**;
- alter, reinterpret, or supersede **Document 89**;
- alter, amend, reinterpret, or supersede **Document 90**;
- alter the ratified **Documents 83 / 85** scope or **Documents 84 / 86**
  milestone selection.

Document 90's own contract-impact position — that every architecture
decision fits **strictly behind** the Document 87 Revision 2 contract
line, fixing only what is behind the contract and changing no observable
behaviour — is confirmed by this ratification. **If any architectural
issue were found that required changing the ratified contract, this
record would name it as a governance boundary / problem rather than
change the contract.** No such issue exists.

---

## 10. AH-1 / AH-2 — Preserved Exactly

**AH-1 and AH-2 are ratified exactly as Document 90 §8 and §9 carry them
forward — not differently, not reinterpreted.**

- **AH-1** (the M15 `report`-mode structured-schema resolution) is
  **untouched and not reinterpreted** by Document 90 or by this record.
- **AH-2** — Document 90 §8's process-local, TTL-bounded in-process
  result buffer **is** the M15 AH-2 class of mechanism, carried forward
  unchanged in kind:
  - process-local, TTL-bounded, single-backend-process
    `POST → completion → GET` (or SSE `final`) lifecycle;
  - **no new MongoDB collection; no Redis or cross-process final-result
    persistence; no cross-process reconstruction**; SSE does not bypass
    the invariant — the `final` frame reads the same transient buffer as
    `GET` and reconstructs nothing from any other store if that buffer is
    expired / unavailable;
  - it is **transient operational job state**, explicitly **distinct from
    durable user / conversational / research-session state**;
  - by construction (single dict, TTL, entry cap, owner-scoped read,
    popped on any terminal-not-`completed` path) it **cannot become a
    durable, cross-request, per-user Q&A store** — the only constraint
    Document 87 Revision 2 §13.4 places on it.
- `"Stateless"` is **not** reinterpreted as a prohibition on this
  transient job state.

This record **does not authorize** any promotion of the buffer to a
durable store, any multi-instance shared cache, or any change to AH-1's
resolution.

---

## 11. DRS Boundary

**Durable Research Sessions (DRS) remain BLOCKED and outside M16**,
exactly as Document 90 §2 and §25 carry the boundary forward.

- No durable Q&A store is designed, proposed, or authorized.
- The §8 / §9 retention mechanism is explicitly forbidden from becoming a
  durable, cross-request, per-user store.
- Multi-turn conversation, saved conversations, resumable sessions,
  "since your last question" state, cross-filing comparison, corpus
  synthesis, and portfolio research are **not** in M16.
- Any future stateful / conversational FQA remains gated on the separate
  DRS governance (Document 58 §10; Documents 83 §6 / 85 §5).

**This record does not resolve, pre-empt, schedule, or authorize any DRS
work.**

---

## 12. Security and Operational Boundaries — Preserved Exactly

**Ratified exactly as Document 90 §11, §15, §16, §18, and §21 state — no
new security or operational behaviour is introduced beyond what Document
90 already establishes:**

- **Authentication / ownership** — `current_user` on all four routes;
  unauthenticated → 401 (existing middleware, no body change); job
  records **owner-scoped** — `GET` / `stream` / `cancel` by a non-owner
  → `404` non-disclosure; the buffer read is owner-scoped too.
- **Shared filing corpus** — `filings` / `filing_chunks` carry no
  `user_id`; any authenticated user may ask about any ingested filing,
  matching M13 / M14 (and deliberately unlike M15's owner-scoped
  `reports`). Recorded as an explicit M16 alignment choice, not a new
  behaviour.
- **BYOK** — `llm_provider` / `llm_api_key` / `llm_base_url` /
  `llm_model` threaded per request via `set_llm_context(...)` /
  `reset_llm_context(...)`; `llm_api_key` **never persisted, never
  logged**; a per-request custom provider / base URL is not retained
  after the job completes.
- **SSRF** — a custom `llm_provider == "custom"` or any `llm_base_url` by
  a non-admin → `require_admin(user)` → `403 forbidden`; any custom
  `llm_base_url` → `assert_public_url(url)`; a loopback / private /
  link-local address → `HTTPException(400, detail=…)` with the
  established message and **no `type` field** — the M14 / M15 deviation
  reproduced **exactly**, not newly invented.
- **Error taxonomy** — zero new error classes; the full failure surface
  maps onto the existing nine-class `backend/domain/errors.py` taxonomy
  (Document 90 §18); recoverable retrieval degradation is not a failure;
  unrecoverable DB / retrieval infrastructure failure → existing `502
  infrastructure_error`; zero-content filing → `200 /
  insufficient_evidence` as a data condition.
- **SSE** — the frozen platform SSE contract: unnamed `data:`
  `TraceEvent` frames at node boundaries, the `final` frame once and only
  on `completed` (including `insufficient_evidence`), never on `failed` /
  `cancelled`, built from the same transient buffer as `GET`, then the
  named `event: end`. No new SSE mechanism.
- **Prompt-injection posture** — the user's `question` and the filing
  text are **untrusted data, never instructions**; the version-pinned
  `_SYSTEM` prompt is grounding-only, no outside knowledge, no
  instruction-following from data, no recommendation.
- **Secret handling** — no secret, no raw provider response, and no raw
  filing text beyond what existing routes already log is written to logs
  on any path; `fail()` receives only a redacted / generic message.
- **Observability** — one `pipeline.filing_qa` span; reuse of
  `jobs_active` and `retrieval_duration_seconds`; one additive
  `filing_qa_runs_total{outcome}` counter recorded as a requirement; a
  metrics-catalog edit, dashboard / alerting change, and tracing-backend
  change are **not** authorized.
- **Deployment** — no topology change; the single-instance operational
  invariant carried forward; new environment variables are operational
  configuration; **no MongoDB migration / index, no Redis, no new model
  download, no deploy, no release**.

This record **does not authorize** any change to `require_admin` /
`assert_public_url` / auth middleware, a per-user filing-ownership check,
an IP-based rate limiter, a new error / exception class, a new retry loop,
a circuit breaker, a metrics-catalog edit, or any infrastructure /
deployment change.

---

## 13. Explicit Implementation Non-Authorization

**Architecture ratification does not constitute implementation
authorization.** This record does **NOT**:

- alter Document 90;
- alter Document 87 (Revision 2);
- alter Document 88;
- alter Document 89;
- create any implementation detail beyond Document 90;
- authorize M16 implementation;
- authorize any source-code change;
- authorize any test change or any test-file creation;
- authorize any configuration change (including the `fqa_*` operational
  config, `job_deadline_filing_qa_s`, or any environment variable in a
  real environment);
- authorize any MongoDB schema / collection / index / migration work, or
  an `08_MongoDB_Data_Architecture.md` amendment;
- authorize any Redis persistence or Redis component;
- authorize any LangGraph node / topology change;
- authorize any frontend work;
- authorize any evaluation infrastructure — dataset, harness, runner, CI
  gate, scorecard, or `backend/evaluation/` addition (only the
  requirement is recorded — Document 90 §14);
- authorize a `20_M6_Metrics_Catalog.md` amendment;
- authorize any deployment or release;
- authorize any commit, push, or merge;
- authorize any DRS work;
- create another architecture decision pack;
- create another ratification-of-Document-91 record.

**Implementation requires a separate, explicit M16 Implementation
Authorization Decision after this architecture ratification. Commit and
push remain separate, later gates.** Nothing in this record advances any
stage beyond architecture ratification itself.

---

## 14. Architecture Ratification ≠ Implementation Authorization

**ARCHITECTURE RATIFICATION ≠ IMPLEMENTATION AUTHORIZATION.**

These are two distinct, sequential CTO acts. This record performs only
the first — and, further, **the first does not itself take effect until
its own prerequisite gate (the Document 88 / 89 API-contract ratification
chain) is complete**, in addition to Document 91's own CTO ratification
(§7). Ratifying Document 90 fixes *how* M16 FQA v1 will be built if and
when implementation is authorized; it does **not** authorize building it,
and it does not authorize any of the acts enumerated in §13. **A stage
being CTO-reviewed and approved is not the same as that stage's effect
being reached — each stage below requires the stage(s) above it to be
formally, not merely provisionally, complete.**

```text
Roadmap reconciliation
≠
Milestone selection
≠
Milestone-selection ratification
≠
API contract
≠
API-contract ratification
≠
Architecture decision pack
≠
Architecture ratification                  🟠 THIS DOCUMENT (91) — DRAFT / PENDING CTO REVIEW
≠
Implementation authorization
≠
Implementation
≠
Technical review
≠
Commit authorization
≠
Push authorization
```

```text
Doc 83 / 85  — FQA v1 scope + ratification              🟢 CTO-RATIFIED
  ↓
Doc 84 / 86  — M16 selection + ratification              🟢 CTO-RATIFIED
  ↓
Doc 87 R2    — M16 API contract                          🟡 CTO-reviewed / approved along Doc 88 / 89 chain
  ↓
Doc 88       — D87 R2 ratification record                🟡 CTO-reviewed, approved for ratification —
                                                             NOT yet formally ratified itself
  ↓
Doc 89       — Terminal ratification of Doc 88            🟡 DRAFT / PENDING CTO REVIEW — NOT YET RATIFIED
                                                          ⚠ PREREQUISITE GATE — Doc 89's OWN formal
                                                             ratification must complete before Doc 90's
                                                             architecture ratification (Doc 91) can take
                                                             effect
  ═══════ chain completion — NOT YET REACHED ═══════
Doc 90       — M16 Architecture Decision Pack (FQA v1)    🟡 CTO-reviewed, APPROVED FOR RATIFICATION,
                                                             not yet ratified
  ↓
Doc 91 (THIS) — Document 90 Architecture Ratification     🟠 DRAFT / PENDING CTO REVIEW. MAY be
                Record                                       CTO-reviewed / approved for ratification now
                                                             — but Doc 90's ratification is HELD PENDING
                                                             and does NOT take effect until the Doc 88/89
                                                             gate above also completes (§7)
  ↓
STOP — Doc 90's architecture ratification does not take effect until BOTH Doc 91 is itself CTO-ratified
       AND the Doc 88 / 89 chain (Doc 89's own formal ratification) is complete — no downstream gate is
       authorized by this record either way
  ↓
M16 Implementation Authorization Decision   (NOT created here — a future, separate CTO act, reachable
                                              only once Doc 90's architecture ratification has actually
                                              taken effect)
  ↓
implementation → technical review → commit authorization → commit →
push authorization → push → post-push review → M16 closure → closure ratification   (NOT authorized)
```

This record performs exactly one stage: **architecture ratification** —
and only proposes it, since that stage's own *effect* is additionally
gated on the Document 88 / 89 chain completing (§7). It is not a
substitute for, or a shortcut past, the API-contract-ratification gate,
implementation authorization, or any later stage. **Document 91 does not
become an implementation-authorization record**, and Document 91's own
CTO ratification does not, by itself, complete the Document 88 / 89
chain or bring Document 90's architecture ratification into effect.

---

## 15. Next Governance Artifact

**Only once Document 90's architecture ratification actually takes
effect — which requires BOTH (a) Document 91's own separate CTO
ratification AND (b) completion of the Document 88 / 89 API-contract
ratification chain, including Document 89's own formal ratification
(§7) — is the next legitimate governance artifact a separate, explicit
M16 Implementation Authorization Decision** — a distinct CTO act, not
created, performed, or pre-empted here — followed (each a further
distinct act) by implementation, technical review, commit authorization,
commit, push authorization, push, post-push review, M16 closure, and
closure ratification.

**Document 91's own CTO ratification, by itself, does not reach this
next artifact.** If Document 91 is CTO-ratified while the Document 88 / 89
chain remains incomplete, the M16 Implementation Authorization Decision is
**not yet** a legitimate next step — the ladder remains held at the
prerequisite gate (§7, §14) until that chain also completes.

**M16 implementation is NOT authorized.** This record does not create the
M16 Implementation Authorization Decision, does not create any further
ratification-of-Document-91 wrapper, and does not create another
architecture decision pack.

---

## 16. Provenance — Repository / Working-Tree State

Recorded by **read-only** `git` inspection this session on 2026-09-11.
**This is a point-in-time snapshot** observed during the creation of this
record, not a claim about repository state at any later reading time.
**No `git` mutation was performed** — no `add` / stage, no `commit`, no
`push`, no `amend`, no `rebase`, no `merge`, no `reset`, no `restore`, no
`stash`, no `clean`.

- `git rev-parse HEAD` = `git rev-parse origin/main` =
  `f8c06649e94f45c388bbecf3eeedb9e5340f2024` (`f8c0664`, *"feat(m15):
  implement change brief"*).
- `git rev-list --left-right --count origin/main...HEAD` = `0	0` — clean
  upstream tracking, no divergence, nothing ahead or behind.
- Recent history (unchanged by this task): `f8c0664` feat(m15) →
  `be4949b` feat(m14) → `f1c18c3` docs(m13) → `244ca5c` feat(m13) →
  `b4e90a0` M12.
- Document number 91 was verified free before creation (highest existing
  Backend & AI governance document was 90; no Document 91 existed prior
  to this task — confirmed by directory listing).
- **Documents 63–90 were read, not modified.** Documents 83 / 85, 84 /
  86 (scope + selection), 87 Revision 2 / 88 / 89 (API contract +
  ratification chain), and 90 (architecture pack) are cited as **frozen
  input**, not reinterpreted. Document 74 is cited as the structural
  precedent for an architecture-ratification record.
- **Document 90 was read at its as-published state — no revision marker —
  and not modified** (§3).
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval / RAG code, MongoDB collection, Redis
  component, provider, configuration, evaluation-infrastructure,
  metrics-catalog, deployment, or frontend file was created or modified.
  `.gitignore` was not modified.
- The working tree is **not** Git-clean. It contains known, pre-existing,
  unrelated items this document does **not** stage, modify, rename,
  delete, or clean:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated — not touched)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/  (untracked, M11 evidence — not touched)
  ?? both / NOT / expect / empty) / current_period_end`          (untracked, 0-byte stray shell-tooling artifacts — not created by this task, not touched)
  ?? docs/backend_engineering/67_...md through 90_...md           (pre-existing untracked governance documents — not modified)
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/91_Document90_Architecture_Ratification_Record.md`).
  It is **untracked and not yet version-controlled.** Staging or
  committing it is a separate, subsequently CTO-authorized step, not
  performed here.

---

## 17. Resulting Governance State

**Resulting governance state depends on which prerequisite(s) have
actually completed — this record does not collapse the two.**

### 17.1 (A) If Document 91 is CTO-ratified but the Document 88 / 89 chain is not yet complete

- Document 91 itself is approved for ratification, but **Document 90's
  architecture ratification is HELD PENDING and does NOT take effect**
  (§7). Document 90 remains exactly as before this record's own
  ratification: **CTO-reviewed, APPROVED FOR RATIFICATION, not yet
  ratified.**
- The M16 governance ladder does **not** advance past the
  API-contract-ratification gate (§14) — it does **not** reach
  "architecture-ratified."
- **M16 implementation remains NOT authorized**, and no M16
  Implementation Authorization Decision is a legitimate next step (§15).

### 17.2 (B) Only once BOTH (i) Document 91 is itself CTO-ratified AND (ii) the Document 88 / 89 chain — including Document 89's own formal ratification — is complete

- **Document 90 — M16 Architecture Decision Pack — Filing Q&A (FQA v1)
  stands formally ratified** as the M16 FQA v1 implementation
  architecture, as reviewed and approved, with every decision and
  boundary in Document 90 §§3–24 preserved exactly.
- The M16 governance ladder stands at the **architecture-ratified**
  point and **no further**.
- **M16 implementation remains NOT authorized.**
- **Document 87 Revision 2** (the M16 API contract, its Documents 88 / 89
  ratification chain now formally complete), the ratified **Documents
  83 / 85** scope, and the ratified **Documents 84 / 86** milestone
  selection are unchanged.
- **AH-1 and AH-2 remain preserved**; **DRS remains BLOCKED and outside
  M16**; **M15 / C-4 remains closed** (Documents 79 / 80) and is not
  reopened; C-2 remains an eligible Backend & AI alternative; Documents
  77 / 78 remain authoritative on the golden-dataset testing-floor
  classification.

### 17.3 State at the time of this record

**Neither prerequisite condition has been satisfied at the time this
record is written.** Document 91 is **DRAFT / PENDING CTO REVIEW**
(banner; §2); the Document 88 / 89 API-contract ratification chain is
**not yet complete**, with Document 89 itself **DRAFT / PENDING CTO
REVIEW, NOT YET RATIFIED** (§4). Document 90 therefore remains
**CTO-reviewed, APPROVED FOR RATIFICATION, not yet ratified**, and its
architecture ratification under this record has **not** taken effect —
state §17.1 above applies, not §17.2.

---

## 18. Final Attestation

**🟠 DOCUMENT 91 — DRAFT / PENDING CTO REVIEW — PROPOSED ARCHITECTURE
RATIFICATION OF DOCUMENT 90. THIS RECORD DOES NOT SELF-RATIFY. THIS
RECORD MAY BE CTO-REVIEWED AND APPROVED FOR RATIFICATION NOW, SUBJECT TO
COMPLETION OF THE DOCUMENT 88 / 89 API-CONTRACT RATIFICATION CHAIN. THE
FORMAL RATIFICATION OF DOCUMENT 90 THAT THIS RECORD PROPOSES DOES **NOT**
TAKE EFFECT UNTIL **BOTH** (A) THIS RECORD'S OWN SEPARATE CTO REVIEW AND
RATIFICATION AND (B) THE DOCUMENT 88 / 89 API-CONTRACT RATIFICATION CHAIN
IS FORMALLY COMPLETE — INCLUDING DOCUMENT 89'S OWN FORMAL RATIFICATION —
HAVE OCCURRED. NEITHER CONDITION ALONE IS SUFFICIENT, AND AT THE TIME OF
THIS RECORD NEITHER HAS OCCURRED: DOCUMENT 89 REMAINS DRAFT / PENDING CTO
REVIEW, NOT YET RATIFIED, AND DOCUMENT 91 ITSELF REMAINS DRAFT / PENDING
CTO REVIEW. IT PROPOSES EXACTLY ONE GOVERNANCE ACT: THE FORMAL
RATIFICATION OF DOCUMENT 90 — M16 ARCHITECTURE DECISION PACK — FILING Q&A
(FQA v1) — AS THE RATIFIED M16 FQA v1 IMPLEMENTATION ARCHITECTURE,
EXACTLY AS REVIEWED AND APPROVED, EFFECTIVE ONLY ONCE BOTH PREREQUISITE
CONDITIONS ABOVE ARE SATISFIED. DOCUMENT 90 IS TO BE RATIFIED
AS-PUBLISHED — NO REVISION MARKER IS PRESENT IN THE FILE, AND THIS RECORD
MAKES NO CLAIM ABOUT ANY LATER REVISION. THIS RECORD DOES NOT MODIFY
DOCUMENT 90, DOES NOT REINTERPRET DOCUMENT 90, DOES NOT SILENTLY AMEND
DOCUMENT 90, AND CREATES NO NEW ARCHITECTURE DECISION. PRESERVED EXACTLY
AS DOCUMENT 90 SPECIFIES: (1) THE DETERMINISTIC ORDERED
CANDIDATE UNIVERSE AND CANDIDATE CAPPING — N ≤ K MEANS ALL CHUNKS; N > K
USES THE DEFINED DETERMINISTIC STRIDE-SELECTION ALGORITHM WITH
HIGHEST-`chunk_idx` COMPLETION WHERE REQUIRED, RE-SORT BY `chunk_idx`,
DETERMINISTIC NUMBERING, INDEPENDENT OF MODEL OUTPUT, BOUNDED BY
`MAX_CANDIDATE_CHUNKS`, FIRST-AND-LAST COVERAGE PRESERVED; (2) CANDIDATE
COVERAGE SEMANTICS — FULL CANDIDATE UNIVERSE DISTINGUISHED FROM THE
MODEL-FACING SUBSET, PARTIAL CANDIDATE COVERAGE EXPLICITLY DISCLOSED VIA
`coverage_boundaries`, PARTIAL COVERAGE NOT ITSELF DETERMINING `state`,
`state` REMAINING GOVERNED BY DOCUMENT 87 REVISION 2 §9.1 / §9.2
`answered` / `insufficient_evidence` SEMANTICS; (3) RETRIEVAL DEGRADATION
— RECOVERABLE (DENSE / RERANKER UNAVAILABLE → BM25-ONLY; EMPTY RETRIEVAL
RESULT → DETERMINISTIC SAMPLING; CONTINUE WITH COVERAGE DISCLOSURE) VS
UNRECOVERABLE (DATABASE / PERSISTENCE FAILURE, CHUNK-LOADING FAILURE,
FILING-RESOLUTION FAILURE, UNHANDLED RETRIEVAL INFRASTRUCTURE FAILURE →
EXISTING `502 infrastructure_error`), WITH ZERO-CONTENT PRESERVED AS A
DATA CONDITION (`200 / completed / insufficient_evidence`, NEVER 404,
NEVER 502) RATHER THAN AN INFRASTRUCTURE FAILURE; (4) THE GENERATION
INVARIANT — AT MOST ONE LOGICAL ANSWER-GENERATION REQUEST, ZERO MODEL
CALLS ON DETERMINISTIC EMPTY / ZERO-CONTENT PATHS, EXACTLY ONE GENERATION
WHEN REQUIRED AND CANDIDATES EXIST, NO REPAIR GENERATION, NO REFINEMENT
LOOP, TRANSPORT RETRIES NOT CONSTITUTING ADDITIONAL COMPLETIONS; (5) THE
CITATION ARCHITECTURE — DETERMINISTIC STRUCTURAL CITATION VALIDATION,
SEMANTIC GROUNDING REMAINING AN EVALUATION CONCERN,
`FilingQACitationStructureError` REMAINING MODULE-INTERNAL, NO EXPANSION
OF THE EXTERNAL ERROR TAXONOMY; (6) THE EXISTING DOCUMENT 87 API CONTRACT
UNCHANGED; (7) AH-1 AND AH-2 PRESERVED; (8) DRS OUTSIDE M16; (9) DOCUMENT
90'S REMAINING ARCHITECTURE DECISIONS AND BOUNDARIES EXACTLY AS SPECIFIED
(EVIDENCE REPRESENTATION, `JobKind.FILING_QA` ADDITIVE ENUM MEMBER,
TRANSIENT `_FILING_QA_RESULTS` RETENTION WITH `reused` ALWAYS `false`,
MODEL / PROVIDER / BYOK, CITATION-SAFE OUTPUT BOUNDING, EVALUATION
REQUIREMENT RECORDED ONLY, OBSERVABILITY, PERFORMANCE, FAILURE / RETRY,
M14 / M15 REUSE, TESTING ARCHITECTURE RECORDED ONLY WITH `pytest.ini`
`addopts` UNTOUCHED, DEPLOYMENT WITH NO TOPOLOGY CHANGE, REJECTED
ALTERNATIVES); (10) THE EXISTING SECURITY, OWNERSHIP, BYOK, SSRF, ERROR,
SSE, OBSERVABILITY, AND DEPLOYMENT CONSTRAINTS PRESERVED. ARCHITECTURE
RATIFICATION ≠ IMPLEMENTATION AUTHORIZATION. THIS RECORD DOES NOT ALTER
DOCUMENT 90, 87, 88, OR 89; DOES NOT CREATE IMPLEMENTATION DETAILS BEYOND
DOCUMENT 90; DOES NOT AUTHORIZE IMPLEMENTATION, SOURCE-CODE CHANGES,
TEST / CONFIG CHANGES, MONGODB SCHEMA / COLLECTION / INDEX / MIGRATION
WORK, REDIS PERSISTENCE, LANGGRAPH CHANGES, FRONTEND WORK, EVALUATION
INFRASTRUCTURE, A METRICS-CATALOG EDIT, DEPLOYMENT / RELEASE, OR
COMMIT / PUSH / MERGE; DOES NOT AUTHORIZE DRS; AND CREATES NEITHER ANOTHER
ARCHITECTURE DECISION PACK NOR ANOTHER RATIFICATION-OF-DOCUMENT-91 RECORD.
NO GIT STATE WAS STAGED, COMMITTED, PUSHED, MERGED, REBASED, RESET,
CLEANED, STASHED, OR AMENDED. `HEAD = origin/main = f8c0664`, `0	0`
DIVERGENCE. DOCUMENTS 63–90 WERE READ, NOT MODIFIED; NO SOURCE, TEST,
SCHEMA, CONFIGURATION, EVALUATION, OR UNRELATED WORKING-TREE FILE WAS
CREATED OR MODIFIED; THE ONLY FILE THIS TASK CREATES IS THIS DOCUMENT.
ONLY ONCE DOCUMENT 90'S ARCHITECTURE RATIFICATION ACTUALLY TAKES EFFECT —
REQUIRING BOTH THIS RECORD'S OWN CTO RATIFICATION AND THE DOCUMENT 88 / 89
API-CONTRACT RATIFICATION CHAIN'S FORMAL COMPLETION, INCLUDING DOCUMENT
89'S OWN FORMAL RATIFICATION — IS THE NEXT GOVERNANCE ARTIFACT THE
SEPARATE M16 IMPLEMENTATION AUTHORIZATION DECISION. THIS RECORD'S OWN CTO
RATIFICATION ALONE DOES NOT REACH THAT NEXT ARTIFACT WHILE THE DOCUMENT
88 / 89 CHAIN REMAINS INCOMPLETE. M16 IMPLEMENTATION IS NOT AUTHORIZED.**

DOCUMENT 91 D90 ARCHITECTURE RATIFICATION RECORD COMPLETE — AWAITING CTO REVIEW
