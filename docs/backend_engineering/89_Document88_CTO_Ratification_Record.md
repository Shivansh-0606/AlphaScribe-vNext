# 89 — Document 88 CTO Ratification Record

**Status:** 🟡 **DOCUMENT 89 — DRAFT / PENDING CTO REVIEW — PROPOSED
RATIFICATION OF DOCUMENT 88. NOT YET RATIFIED. THIS RECORD DOES NOT
SELF-RATIFY AND TAKES EFFECT ONLY ON ITS OWN SEPARATE CTO REVIEW AND
RATIFICATION.**

**Document 88 has been CTO-reviewed and approved for ratification, but is
NOT YET RATIFIED** — its formal ratification is the single act this
record (Document 89) proposes, and it takes effect only when Document 89
is itself separately CTO-ratified. Document 88 is the authoritative
ratification record for Document 87 Revision 2's API contract; on Document
89's ratification, Document 88 becomes formally ratified and the M16 =
Filing Q&A (FQA v1) API contract (Document 87 Revision 2) stands ratified
through Document 88. This document **proposes** that CTO ratification
record for
[88_Document87_CTO_Ratification_Record.md](88_Document87_CTO_Ratification_Record.md)
— it records Document 88's CTO-reviewed / approved-for-ratification
outcome and, on its own CTO ratification, formally ratifies and confirms
Document 88. It is a **separate governance act**, distinct from Document
88 itself: it accepts Document 88's single governance act — it does not
re-perform that act, it does not re-ratify or re-open Document 87 Revision
2's contract, it does not create or change any contract, it makes no
architecture decision, and it makes no additional governance decision.
**The conclusion recorded here, put forward for CTO ratification, is:
Document 88 correctly performed its single governance act — ratifying
Document 87 Revision 2 as the M16 Filing Q&A (FQA v1) API contract — and
is approved for ratification; on this record's own CTO ratification,
Document 88 stands formally ratified as that authoritative ratification
record.**

**Type:** Governance / ratification decision record (documentation only —
no source code, test, configuration, schema, migration, index, route,
handler, LangGraph node / topology, MongoDB collection / schema, Redis
usage, retrieval / RAG code, provider, evaluation-infrastructure, or
frontend file created or modified to produce it; Documents 67–88 read,
not modified. The only file this task creates is this document.

**Date:** 2026-09-10.

**Precedent / lineage.** This record follows the standalone
ratification-record form the M15 / M16 chain has used since
[Document 69](69_Document68_CTO_Ratification_Record.md), and most recently
[Document 72](72_Document70_R4_CTO_Ratification_Record.md) (API contract
ratification),
[Document 85](85_Document83_CTO_Ratification_Record.md) (scope
ratification),
[Document 86](86_Document84_CTO_Ratification_Record.md) (selection
ratification), and
[Document 88](88_Document87_CTO_Ratification_Record.md) (the API contract
ratification this record now puts forward for CTO ratification). It
proposes ratification of a ratification record without rewriting Document
88, Document 87, or any earlier document.

---

## 1. Purpose

Document 89 **proposes exactly one governance act, for CTO ratification**:
**formally ratifying Document 88 as the CTO Ratification Record for
Document 87 Revision 2.** It proposes no other act, and it does not
self-ratify — it is itself DRAFT / PENDING CTO REVIEW.

**Document 89 does not ratify, re-ratify, create, or change the M16 API
contract.** The M16 API contract is the substantive artifact established
by Document 87 Revision 2; Document 88 is the record that ratifies it.
Document 89 **records that Document 88 has been CTO-reviewed and approved
for ratification and, on Document 89's own CTO ratification, formally
ratifies Document 88 itself** — confirming that Document 88 correctly
performed its single act (ratifying Document 87 Revision 2), is internally
consistent, and stands as the authoritative ratification record for the
M16 Filing Q&A (FQA v1) API contract. Until Document 89 is itself
CTO-ratified, Document 88's formal ratification has not occurred.

**This is a ratification of a ratification record — not an API-contract
decision, not an architecture decision, not an architecture
authorization, and not an implementation authorization.** It does not
re-derive, redesign, extend, or narrow the contract, and it does not
advance any downstream gate (§8, §11, §14).

---

## 2. Ratification Target

**Target: Document 88 — Document 87 CTO Ratification Record (the Document
87 Revision 2 API Contract Ratification Record), as written; no revision
label exists or is claimed.**

Document 88's substantive act — CTO-reviewed and approved for
ratification; formally ratified on this record's own CTO ratification:

> **Document 87 Revision 2's externally observable request / response,
> citation, error, state, job, and SSE semantics are ratified by Document
> 88 as the M16 = Filing Q&A (FQA v1) API contract, strictly within the
> ratified single-turn + stateless + single-filing scope of Documents 83 /
> 85 and the M16 selection of Documents 84 / 86; that ratified status is
> established and held by Document 88 as the separate authoritative record
> — and takes formal effect when Document 89 (this record) is itself
> CTO-ratified — and Document 88 does not edit Document 87 or its embedded
> status metadata.**

Verified this session, read-only, before recording this ratification:

- Document 88 exists at
  `docs/backend_engineering/88_Document87_CTO_Ratification_Record.md` and
  is the Document 87 Revision 2 API Contract Ratification Record.
- Document 88 performs a **single governance act** — the ratification of
  Document 87 Revision 2 — and states in §§1, 6, 7, 10, 14 that it does
  not create or select the contract, makes no architecture decision, and
  authorizes no implementation.
- Document 88 incorporates a **CTO-directed correction pass** that
  resolved a governance-integrity wording issue: it no longer states that
  Document 87's own in-file status "transitions … by this record." As
  corrected, Document 88 ratifies the **substance** of Document 87
  Revision 2, **holds** the ratified status as the separate authoritative
  record, and explicitly **does not edit Document 87 or its embedded
  status metadata** (Document 88 §§1, 3, 6, 11, 12, 14). No revision
  label is used on Document 88; the correction was applied in place.
- Document 88 §5 restates the Document 87 Revision 2 contract **in
  substance** (single-turn + stateless + single-filing; `(ticker,
  doc_id)`; four-route async family; route inventory `51 → 55`; job
  lifecycle; cancellation semantics; SSE final-frame semantics; `answered`
  / `insufficient_evidence`; zero-content filing behaviour; frozen
  citation structure; deterministic citation-**structure** validation with
  semantic grounding deferred to evaluation; BYOK; SSRF; the existing
  nine-class error taxonomy; AH-1 / AH-2; DRS outside M16) — "not
  invented, not modified, not extended, not narrowed."
- Document 88's final line reads exactly *"DOCUMENT 88 D87 REVISION 2 API
  CONTRACT RATIFICATION RECORD COMPLETE — AWAITING CTO REVIEW."*

**No discrepancy in Document 88's single governance act or its substance
was found. On its own CTO ratification, this record ratifies Document 88
exactly as written.**

---

## 3. The Governance-Level Distinction (preserved, not collapsed)

| Level | Artifact | What it is |
|---|---|---|
| **Substantive contract** | **Document 87 Revision 2** | The M16 = Filing Q&A (FQA v1) **API contract** — the externally observable request / response, citation, error, state, job, and SSE semantics. |
| **Authoritative ratification record** | **Document 88** | The **record that ratifies** Document 87 Revision 2 and **holds** the ratified status as a separate authoritative document; **CTO-reviewed and approved for ratification, not yet formally ratified** (that occurs on Document 89's own ratification). It does not edit Document 87 or its embedded status metadata. |
| **Ratification of the ratification record** | **Document 89 (THIS)** | The **proposed record that ratifies Document 88** (this document — DRAFT / PENDING CTO REVIEW; NOT YET RATIFIED; does not self-ratify) — confirming Document 88 correctly performed its single act and stands as the authoritative ratification record. |

```text
D83   =  FQA v1 scope decision
D85   =  ratification of the D83 scope decision
D84   =  M16 milestone selection
D86   =  ratification of the D84 milestone selection
D87 R2 =  M16 API Contract Proposal — the substantive FQA API contract
D88   =  ratification of the D87 Revision 2 API contract (authoritative ratification record — CTO-reviewed / approved for ratification; NOT YET RATIFIED)
D89   =  ratification of Document 88 (PROPOSED — DRAFT / PENDING CTO REVIEW; NOT YET RATIFIED)   ← THIS DOCUMENT
```

- **Document 89 does not modify Document 87 or Document 88.** Both are
  read as frozen input; neither file is edited by this task.
- **Document 89 does not claim to change Document 87's or Document 88's
  embedded status metadata**, and does not synchronize Document 87's
  in-file historical status marker (§5.3, §12).
- **Document 89 does not create or change the API contract.** The contract
  is Document 87 Revision 2's; the record that ratifies it is Document 88,
  which is CTO-reviewed and approved for ratification but not yet formally
  ratified. Document 89 (this record) is the **proposed** ratification of
  Document 88 and is itself DRAFT / PENDING CTO REVIEW; Document 88's
  formal ratification occurs only on Document 89's own CTO ratification.

---

## 4. Predecessor Governance State

| Artifact | Role | State as of this record |
|---|---|---|
| **Document 79 / 80** — M15 / C-4 Milestone Closure + Ratification | M15 milestone closure | 🟢 CTO-RATIFIED — **M15 / C-4 CLOSED** |
| **Document 81 / 82** — Post-M15 Backend & AI Roadmap Reconciliation + Ratification | Roadmap position; recommended Filing Q&A | 🟢 CTO-RATIFIED |
| **Document 83 / 85** — Filing Q&A Scope Pre-Decision + Ratification | The FQA v1 **scope decision** (single-turn + stateless + single-filing) | 🟢 CTO-RATIFIED |
| **Document 84 / 86** — M16 Milestone Selection + Ratification | The **M16 milestone selection** (M16 = FQA v1) | 🟢 CTO-RATIFIED |
| **Document 87 Revision 2** — M16 API Contract Proposal — Filing Q&A (FQA v1) | The **M16 API contract** (substantive artifact) | CTO-reviewed / approved for ratification; formal contract ratification is carried by Document 88 and takes effect on Document 89's ratification. Its own in-file banner remains a pre-ratification marker (historical metadata — §5.3) |
| **Document 88** — Document 87 Revision 2 API Contract Ratification Record | The **authoritative ratification record** for the M16 API contract; incorporates a CTO-directed correction pass | 🟡 **CTO-REVIEWED / APPROVED FOR RATIFICATION — NOT YET RATIFIED.** Its formal ratification is the act Document 89 proposes and occurs only on Document 89's own CTO ratification |
| **Document 89 (THIS)** | The proposed ratification record for Document 88 | 🟡 DRAFT / PENDING CTO REVIEW — NOT YET RATIFIED; does not self-ratify |
| **M16 Architecture Decision Pack** | The next substantive governance stage | **Does not exist** |

At the moment of this record: M15 / C-4 is closed; the FQA v1 scope is
ratified (D83 / D85); the M16 selection is ratified (D84 / D86); the M16
API contract (D87 R2) has been CTO-reviewed and approved for ratification,
its formal ratification carried by D88; **D88 itself is CTO-reviewed and
approved for ratification — NOT YET RATIFIED**, its formal ratification
being the act this record proposes; **Document 89 (this record) is DRAFT /
PENDING CTO REVIEW — NOT YET RATIFIED** and does not self-ratify; the M16
Architecture Decision Pack does not exist; M16 implementation is not
authorized. **On Document 89's own CTO ratification, Document 88 becomes
formally ratified, the D87 R2 contract stands ratified through it, and the
M16 Architecture Decision Pack becomes the next substantive governance
artifact.**

---

## 5. What Document 88 Did — the Act This Record Confirms

### 5.1 Document 88's single act

Document 88 performed exactly one governance act: **it ratified Document
87 Revision 2 as the M16 = Filing Q&A (FQA v1) API contract** — a
governance act that has been CTO-reviewed and approved for ratification.
It did not create, author, or select the contract (Document 87 did that);
it did not make an architecture decision; it did not authorize
implementation. This record confirms that Document 88 performed that
single act correctly and completely, and — on this record's own CTO
ratification — formally ratifies it. Until then, Document 88's formal
ratification has not occurred.

### 5.2 The CTO-directed correction Document 88 incorporates

Document 88, as first drafted, contained a governance-integrity wording
issue — it stated that Document 87 Revision 2's own in-file status
"transitions … by this record," which would imply Document 88 physically
edits Document 87 while Document 88 also states Document 87 is not
modified. A **CTO-directed correction pass** resolved this in place (no
revision label): Document 88 now ratifies the **substance** of Document 87
Revision 2, **holds** the ratified status itself as the separate
authoritative record, and explicitly **does not edit Document 87 or its
embedded status metadata** (Document 88 §§1, 3, 6, 11, 12, 14). **On its
own CTO ratification, this record ratifies Document 88 as so corrected.**
The correction was a wording-consistency fix to Document 88 only; it
changed no contract
semantics, no scope, no architecture boundary, no OAQ ownership, and no
authorization boundary.

### 5.3 Document 87's embedded status metadata — not synchronized here

Document 87 Revision 2's own in-file Status banner and closing block still
read *"🟡 M16 API CONTRACT PROPOSAL — DRAFT / PENDING CTO REVIEW (REVISION
2). NOT RATIFIED,"* and its Revision 2 note still records *"🟠 CONDITIONAL
PASS — NOT YET APPROVED FOR RATIFICATION."* **Document 89 does not edit
Document 87, does not edit Document 88, and does not synchronize Document
87's embedded historical status marker.** As established by Document 88
(§§3, 6, 11, 12), the ratified status of the M16 API contract is
**established and held by Document 88** as the separate authoritative
record — taking formal effect when Document 88 is itself ratified (on
Document 89's ratification); where Document 88 and Document 87's embedded
marker differ on ratification status, **Document 88 is authoritative**.
Aligning Document
87's own status-marker wording is a **separate, separately-authorized
mechanical metadata correction** to Document 87 — **not performed by
Document 88 and not performed by Document 89** — and it would not alter
the substance ratified.

---

## 6. Document 87 Revision 2 Contract — Preserved

**Ratifying Document 88 re-affirms, and changes nothing in, the Document
87 Revision 2 contract as Document 88 already restates it in substance.
Nothing below is invented, modified, extended, narrowed, or re-decided by
this record.**

- **Product boundary** — FQA v1 is **single-turn** (one request, one
  bounded answer; no conversational continuation; no thread / session
  identifier; no server-remembered exchange); **stateless with respect to
  durable conversational / research state** (no durable research state, no
  persistent or resumable session, no per-user Q&A history store);
  **single-filing** (the answer is drawn only from one explicitly
  identified filing's own persisted content; no cross-filing research, no
  corpus synthesis, no portfolio research); **filing identity is exactly
  `(ticker, doc_id)`**; **DRS remains outside M16**.
- **Four-route async family** — `POST` create / `GET` status / `GET`
  stream / `POST` cancel, under the `qa` path segment, filing-scoped
  prefix `/api/companies/{ticker}/filings/{doc_id}/qa`; a synchronous
  variant is a non-goal.
- **Route inventory `51 → 55`** — additive-only, exactly four new
  entries.
- **Job lifecycle** — `JobStatus` reused verbatim: `queued` → `running` →
  `completed` | `failed` | `cancelled`; the shared `MAX_ACTIVE_JOBS`
  admission budget applies (exceeded → 429 `rate_limited`); a dedicated
  FQA job-deadline configuration exists with its **numeric value as
  operational configuration**, not fixed by the contract. Create response
  `{"id": …, "status": "queued", "reused": false}`; `reused` is always
  `false`. Completed response carries the frozen `answer` object
  `{ticker, doc_id, question, answer_text, sources[],
  cited_source_indices, state, coverage_boundaries, created_at,
  prompt_version, schema_version}`; the `answer` key is omitted unless
  `completed`; `question` echoes the normalized (whitespace-trimmed)
  value.
- **Cancellation semantics** — a `queued` / `running` job → `200 {"id":
  …, "status": "cancelled"}`; a **terminal job → idempotent `200`** with
  its current unchanged `status`, never an error; unknown / foreign job id
  → 404 `not_found` (non-disclosure).
- **SSE final-frame semantics** — the established `sse_response()` framing
  verbatim; **exactly one** unnamed `data:` frame with `node == "final"`
  (`{"node": "final", "status": "ok", "answer": {…}}`), emitted **only**
  for a `completed` job (including the `insufficient_evidence` /
  zero-content completion), **never** for `failed` / `cancelled`; then the
  named terminal `event: end` frame; the `final` payload is built from the
  same transient result buffer as `GET` and carries the identical
  retention constraint.
- **`answered` / `insufficient_evidence`** — a **closed two-value `state`
  enum**, no third value. `answered` iff the server can return a bounded
  `answer` object satisfying all of Document 87 Revision 2 §9.1's
  deterministic conditions (≥ 1 surviving valid citation; all §8-A
  citation-structure invariants; citation-safe output bound satisfied
  without degrading; a present, well-formed `coverage_boundaries` list).
  `insufficient_evidence` is the **deterministic outcome whenever the
  server cannot return such a bounded `answer` object**; when returned,
  `sources == []`, `cited_source_indices == []`, a short honest bounded
  `answer_text`, `coverage_boundaries` names the reason. It is **not an
  error** (successful `200 / completed`) and does not imply no substantive
  claim was ever grounded.
- **Zero-content filing behavior** — a filing that **resolves** but has
  **zero usable persisted content** completes successfully as `200` /
  `completed` / `state == "insufficient_evidence"` / empty `sources` /
  empty `cited_source_indices` / a bounded honest `answer_text` / a
  `coverage_boundaries` entry — **never a 404, never a 502**.
- **Citation structure** — the established `[n]` markers + parallel
  indexed `sources[]` + `cited_source_indices` subset convention is the
  **sole** mechanism (no new syntax, no new mechanism); the **external
  locator shape is frozen** as exactly `{index, doc_id, chunk_start,
  chunk_end}` (1-based unique `index`; `doc_id` the identified filing's;
  `chunk_start` / `chunk_end` a real retrievable range; every entry
  server-constructed and deterministic, never taken from the model
  verbatim).
- **Deterministic structural citation validation** — the runtime
  deterministically enforces a bounded set of **citation-structure
  invariants** on every returned (bounded) `answer` object: markers map to
  declared, valid, unique `sources[]` indices; the frozen locator shape;
  every locator resolves to the **identified** filing and **never
  another**; `cited_source_indices` is the exact structural subset; no
  orphaned / dangling markers; citation-safe output bounding; **zero
  surviving valid citations ⇒ `insufficient_evidence`**.
- **Semantic grounding as an evaluation concern** — whether a cited
  passage *substantiates* a natural-language claim, and whether
  unrestricted `answer_text` prose *contains* a substantive factual claim
  that requires a citation, are **semantic** questions, **not
  deterministically decidable at runtime**, deferred to Document 87
  Revision 2 §20 OAQ-4 (a held-out evaluation set, following the D77 / D78
  precedent). The contract does **not** claim deterministic runtime
  validation can prove semantic substantiation of arbitrary
  natural-language claims; the product requirement that every substantive
  factual claim be grounded in the identified filing and carry a valid
  citation is **preserved and unweakened**, met by prompt-construction
  design (OAQ-5) and verified by the OAQ-4 evaluation architecture.
- **BYOK** — `llm_provider` / `llm_api_key` / `llm_base_url` / `llm_model`
  reused **verbatim** from every prior contract; all optional; omitting
  them uses the server's configured key; **`llm_api_key` is never
  persisted and never logged**; all LLM access is through the established
  `chat_*` boundary.
- **SSRF** — `current_user` gating on every route (unauthenticated →
  401); a custom `llm_provider` (`"custom"`) or custom `llm_base_url` from
  a non-admin → 403 `forbidden` (`require_admin`); a custom `llm_base_url`
  → the established `assert_public_url` guard → a private / loopback /
  link-local address → `HTTPException(400, …)` with the established
  message. Job records are owner-scoped (`GET` / `stream` / `cancel` by a
  non-owner → 404 non-disclosure); the filing corpus is **shared, not
  owner-scoped**, matching M13 / M14.
- **Existing error taxonomy** — **zero new error classes**; every FQA
  failure maps onto the existing nine-class `backend/domain/errors.py`
  taxonomy; the one established **`400`-without-`type`** SSRF-guard
  response reproduces the M14 / M15 deviation exactly.
- **AH-1 / AH-2** — preserved; "stateless" means no durable user /
  conversational / research-session state and is **not** reinterpreted as
  a prohibition on the transient operational execution state the platform
  requires (§9).
- **DRS remains outside M16** — BLOCKED; a v1 scope decision, not a
  permanent architectural prohibition (§10).

Output / validation behaviour (422 for missing / empty / whitespace-only
or over-deployed-maximum `question`, bare `POST {}`, or empty `ticker`;
`200` + `insufficient_evidence` for a well-formed but unanswerable
question; three indistinguishable 404 filing-not-found cases; no numeric
literal fixed — question length, answer length, and `sources[]` count are
operational configuration; citation-safe output bounding; exactly one
logical answer-generation request per job, transport retries producing no
additional model completion permitted, a structured-output-repair
completion not permitted as drafted) is preserved exactly as Document 87
Revision 2 defines it and Document 88 restates it.

---

## 7. Governance Act Performed

**🟡 DOCUMENT 88 — CTO-REVIEWED / APPROVED FOR RATIFICATION — NOT YET
RATIFIED.** Formal ratification is the act this record (Document 89)
proposes; it takes effect only on Document 89's own separate CTO
ratification.

The CTO has reviewed Document 88, confirmed it performs exactly one
governance act (ratifying Document 87 Revision 2), confirmed it is
internally consistent — including the CTO-directed correction pass that
resolved the status-metadata-authority wording (§5.2) — confirmed it
restates the Document 87 Revision 2 contract in substance without
inventing, modifying, extending, or narrowing it, confirmed it makes no
architecture decision and authorizes no implementation, and found it
**approved for ratification**. This document **proposes** that
ratification: on this record's own separate CTO ratification, Document 88
stands **🟢 RATIFIED**. Document 89 is itself submitted for separate CTO
review; it does not self-ratify.

**The conclusion recorded here, proposed for CTO ratification:**

- **Document 88 is approved for ratification as the authoritative CTO
  Ratification Record for Document 87 Revision 2; on this record's own CTO
  ratification, it becomes formally ratified.**
- **The M16 = Filing Q&A (FQA v1) API contract (Document 87 Revision 2)
  has been CTO-reviewed and approved for ratification**, with Document 88
  as the authoritative ratification record that carries it; the contract
  stands formally ratified through Document 88 once Document 88 is itself
  ratified (on Document 89's ratification).
- **Document 88's formal ratification is proposed by this record
  (Document 89)**, which is itself DRAFT / PENDING CTO REVIEW and takes
  effect only on its own CTO ratification; Document 89 does not edit
  Document 88 or Document 87, and does not synchronize Document 87's
  embedded historical status marker (§5.3).
- **The next substantive governance artifact, once Document 89 is itself
  CTO-ratified and Document 88 thereby formally ratified, is the M16
  Architecture Decision Pack** (§14).

On CTO ratification of this record, Document 88 becomes formally ratified,
the D87 R2 API contract stands ratified through it, and the M16 governance
ladder stands at exactly the point where the API contract and its
ratification record both stand formally accepted; the architecture stage
is next, and **no further**.

---

## 8. Architecture Boundary — What This Ratification Does NOT Decide

**Ratifying Document 88 — the act this record proposes, effective on
Document 89's own CTO ratification — confirms only that the API contract's
ratification record (Document 88) is approved and thereby formally
ratified. It does NOT decide, resolve, or ratify any of the following** —
each remains owned by the **M16 Architecture Decision Pack**
or a later, separate governance act, exactly as Document 87 Revision 2 §20
and Document 88 §7 leave it:

- **retrieval implementation** within the filing, and the internal
  retrieval / storage / passage representation *behind* the frozen
  `{index, doc_id, chunk_start, chunk_end}` external locator (D87 R2 §20
  OAQ-1);
- **`JobKind` realization** — a new `JobKind.FILING_QA` member vs. another
  mechanism (OAQ-2);
- **the transient result-retention mechanism** — the M15 AH-2 in-process
  buffer vs. another bounded mechanism (OAQ-3);
- **prompt-construction discipline** (OAQ-5);
- **model tier** and the architectural enforcement of "exactly one
  logical answer-generation request" / single-generation implementation
  (OAQ-7);
- **model / provider selection**;
- **the semantic answer-quality / grounding evaluation architecture** —
  whether a held-out evaluation set is produced and whether it is a hard
  ship gate (OAQ-4; follows the D77 / D78 precedent);
- **the numeric values of every operational bound** — max `question`
  length, max `answer_text` length, max `sources[]` count, FQA job
  deadline, any FQA-specific rate limit, and their defaults (OAQ-6);
- **any MongoDB collection, index, schema, or migration**;
- **any Redis persistence**;
- **any LangGraph topology or node**;
- **any frontend implementation** (including citation-target rendering);
- **any deployment topology**.

**This record resolves none of Document 87 Revision 2's Open Architecture
Questions (OAQ-1 through OAQ-8).** They remain exactly as open as Document
87 Revision 2 and Document 88 leave them, and are owed to the M16
Architecture Decision Pack and, where applicable, a subsequent CTO
decision — neither of which this record creates.

---

## 9. AH-1 / AH-2 Boundary (preserved — not resolved, not reinterpreted)

- **"Stateless" means stateless with respect to durable user /
  conversational / research-session state** — no per-user Q&A history
  store, no saved conversation, no resumable session, no watchlist, no
  "since your last question".
- **"Stateless" does NOT prohibit the transient operational execution
  state the platform already uses** — a job record in the `JobStatus`
  lifecycle, and a bounded, best-effort mechanism for holding a completed
  answer between the completing `POST` and a client's `GET` (or the SSE
  `final` frame). That transient execution state is the M15 **AH-2** class
  of mechanism (process-local, TTL-bounded, single-backend-process
  `POST → GET` lifecycle), preserved as a **distinct, already-ratified
  concept** — neither invalidated nor extended by this record. The
  contract's only constraint on it: it must not become a durable,
  cross-request, per-user Q&A store (that would reopen DRS); the mechanism
  choice is D87 R2 §20 OAQ-3 (architecture).
- **AH-1 remains preserved** — the M15 `report`-mode structured-schema
  resolution, unchanged.
- **`reused` is always `false`** regardless of the retention mechanism
  chosen.

**This ratification does not reinterpret "stateless" as a prohibition on
transient job execution state, and does not select or design the
retention mechanism.**

---

## 10. DRS Boundary (preserved — BLOCKED and outside M16; not made permanent)

- **Durable Research Sessions remain BLOCKED and outside M16 scope.**
  Filing Q&A v1 does not require DRS. Multi-turn conversational
  continuation, durable / resumable research state, cross-filing research,
  corpus synthesis, and portfolio research are outside v1.
- **This is a v1 scope decision, not a permanent architectural
  prohibition against any future stateful Filing Q&A.** Any future
  expansion toward those capabilities would require its **own separate
  governance** — for a conversational or resumable form specifically, the
  DRS product decision + ADR + authorized new collection that Document 58
  §10 requires (Documents 83 §6 / 85 §5).
- **This record does not resolve, redesign, or pre-empt any future DRS
  requirement or architecture.**

---

## 11. Non-Authorizations

**Ratification of Document 88 does NOT authorize, and must not be read to
authorize, any of the following:**

- **creating or changing the M16 API contract**, or any request /
  response schema, error taxonomy, citation representation, state
  vocabulary, or wire behaviour;
- **any architecture decision or M16 Architecture Decision Pack** —
  FastAPI structure, service / repository classes, LangGraph, retrieval
  implementation, the internal representation behind the frozen locator,
  embedding / vector architecture, prompt architecture, model tier, a
  specific LLM / model, deployment topology;
- **any source-code, test, or configuration change**;
- **any evaluation-infrastructure work** — the M15 golden-dataset
  `report`-mode follow-up remains tracked future work per Documents 77 /
  78 and is **not** reopened; Document 87 Revision 2 §20 OAQ-4 remains an
  open architecture question, not an authorization;
- **any MongoDB collection / index / schema / migration work**, an
  `08_MongoDB_Data_Architecture.md` amendment, **any Redis persistence**,
  **any LangGraph implementation or topology change**, or **any frontend
  work**;
- **any deployment or release**;
- **any commit, push, or merge**, or any other `git` mutation;
- **any modification of Document 87 or Document 88**, or any
  synchronization of Document 87's embedded historical status metadata;
- **any future DRS work** (§10).

**The M16 architecture and M16 implementation remain future governance
stages. Implementation remains blocked until the M16 Architecture Decision
Pack is reviewed and ratified and an M16 Implementation Authorization is
explicitly, separately granted.** Ratification of this record confirms
only that the API contract's ratification record (Document 88) is
approved and thereby formally ratified; it does not advance any
downstream gate.

---

## 12. Provenance

Recorded by read-only inspection this session on 2026-09-10. **No `git`
mutation was performed** — no `add` / stage, `commit`, `push`, `amend`,
`rebase`, `merge`, `reset`, `restore`, `stash`, or `clean`.

- `git rev-parse HEAD` = `git rev-parse origin/main` =
  `f8c06649e94f45c388bbecf3eeedb9e5340f2024` (`f8c0664`, "feat(m15):
  implement change brief").
- `git rev-list --left-right --count origin/main...HEAD` = `0	0`;
  `git branch -vv` = `* main f8c0664 [origin/main] feat(m15): implement
  change brief` — clean upstream tracking, no divergence, nothing to
  push, nothing to pull.
- Document number 89 was verified free before creation (highest existing
  Backend & AI governance document was 88; no Document 89 existed prior to
  this task).
- **Document 88 was read, not modified.** It performs a single governance
  act (ratifying Document 87 Revision 2), incorporates a CTO-directed
  correction pass applied in place (no revision label), and holds the
  ratified status of the M16 API contract as the separate authoritative
  record without editing Document 87 or its embedded status metadata.
  Document 88 has been CTO-reviewed and approved for ratification but is
  **not yet formally ratified** — that occurs on this record's own CTO
  ratification. **Document 88's own final-line marker, "DOCUMENT 88 D87
  REVISION 2 API CONTRACT RATIFICATION RECORD COMPLETE — AWAITING CTO
  REVIEW," is Document 88's pre-ratification metadata and is not modified
  by this task.**
- **Document 87 was read at Revision 2, not modified.** Its in-file Status
  banner and closing block still read *"🟡 M16 API CONTRACT PROPOSAL —
  DRAFT / PENDING CTO REVIEW (REVISION 2). NOT RATIFIED,"* and its
  Revision 2 note still records *"🟠 CONDITIONAL PASS — NOT YET APPROVED
  FOR RATIFICATION."* **Those embedded markers are not edited or
  synchronized by this task and remain in place as historical metadata**;
  the ratified status of the M16 API contract is carried by Document 88.
  Document 88 is itself CTO-reviewed and approved for ratification but not
  yet formally ratified; this record (DRAFT / PENDING CTO REVIEW) proposes
  that ratification and does not itself hold or confer status, nor
  self-ratify, until it is CTO-ratified.
- **Documents 83, 84, 85, 86, 87, and 88 were read, not modified** — cited
  as frozen input, not reinterpreted. The full prior chain (Documents
  67–82) remains 🟢 CTO-RATIFIED and is cited, not reinterpreted.
  Documents 77 / 78 remain authoritative on the golden-dataset
  testing-floor classification.
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval / RAG code, MongoDB collection, Redis
  component, provider, configuration, evaluation-infrastructure,
  deployment, or frontend file was created or modified. `.gitignore` was
  not modified.
- Known pre-existing, unrelated working-tree items — **not** staged,
  modified, renamed, deleted, or cleaned by this task:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated — not touched)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/  (untracked, M11 evidence — not touched)
  ?? both                                                          (untracked, 0-byte stray shell-tooling artifact — not touched)
  ?? current_period_end`                                          (untracked, 0-byte stray shell-tooling artifact — not touched)
  ?? NOT                                                           (untracked, 0-byte stray shell-tooling artifact — not touched)
  ?? expect                                                        (untracked, 0-byte stray shell-tooling artifact — not touched)
  ?? empty)                                                        (untracked, 0-byte stray shell-tooling artifact — not touched)
  ?? docs/backend_engineering/67_...md through 88_...md            (pre-existing untracked governance documents — not modified)
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/89_Document88_CTO_Ratification_Record.md`).
  It is untracked and not yet version-controlled. Staging or committing it
  is a separate, subsequently CTO-authorized step, not performed here.

---

## 13. Resulting Governance State

```text
D67  — Post-M14 Backend & AI Roadmap Reconciliation        🟢 CTO-RATIFIED
D68 / D69 — M15 Milestone Selection = C-4 + Ratification    🟢 CTO-RATIFIED
D70 R4 / D72 — M15 / C-4 API Contract + Ratification        🟢 CTO-RATIFIED
D73 R1 / D74 — M15 / C-4 Architecture Pack + Ratification   🟢 CTO-RATIFIED (AH-1, AH-2 resolved)
D75 / D76 — M15 Implementation Authorization + Ratification 🟢 CTO-RATIFIED
D77 / D78 — D75 §14 Testing-Floor Clarification + Ratif.    🟢 CTO-RATIFIED (golden-dataset eval = tracked future work)
D79 / D80 — M15 / C-4 Milestone Closure + Ratification      🟢 CTO-RATIFIED — M15 / C-4 CLOSED
D81 / D82 — Post-M15 Roadmap Reconciliation + Ratification  🟢 CTO-RATIFIED
D83 / D85 — Filing Q&A Scope Pre-Decision + Ratification    🟢 CTO-RATIFIED — single-turn + stateless + single-filing
D84 / D86 — M16 Milestone Selection + Ratification          🟢 CTO-RATIFIED — M16 = Filing Q&A (FQA v1)
D87 R2 — M16 API Contract (substantive FQA API contract)    🟡 CTO-REVIEWED / APPROVED FOR RATIFICATION — formal contract ratification carried by D88 (pending); D87 embedded marker not edited/synchronized
D88  — D87 Revision 2 API Contract Ratification Record      🟡 CTO-REVIEWED / APPROVED FOR RATIFICATION — NOT YET RATIFIED; formal ratification is the act D89 proposes
D89  — D88 CTO Ratification Record (THIS)                  🟡 DRAFT / PENDING CTO REVIEW — NOT YET RATIFIED; proposes ratification of D88; does not self-ratify
       ↓
(on D89 ratification)                                       D88 becomes 🟢 CTO-RATIFIED; the D87 R2 contract stands ratified through D88
       ↓
M16 Architecture Decision Pack                              NOT CREATED — the next substantive governance artifact, once D89 is ratified
```

- **The M16 API contract and its authoritative ratification record are
  both CTO-reviewed and approved for ratification, and neither is yet
  formally ratified:** Document 87 Revision 2 is the substantive M16 =
  Filing Q&A (FQA v1) API contract; Document 88 is the authoritative
  ratification record that carries its ratification. **Document 89 (this
  record) is the proposed ratification of Document 88 and is itself DRAFT
  / PENDING CTO REVIEW — NOT YET RATIFIED; it does not self-ratify.**
- **On Document 89's own CTO ratification, Document 88 becomes formally
  🟢 CTO-RATIFIED, the D87 R2 API contract stands ratified through it, and
  the M16 Architecture Decision Pack becomes the next substantive
  governance artifact.**
- **The M16 governance ladder stands at: milestone selected and ratified;
  API contract CTO-reviewed and approved for ratification (D87 R2), its
  ratification record (D88) approved and awaiting the ratification this
  record proposes; Document 89 itself pending CTO review; Architecture
  Decision Pack stage next once Document 89 is ratified.** No architecture
  or implementation artifact exists or is authorized.
- M15 / C-4 remains closed and is not reopened. C-2 remains an eligible
  Backend & AI alternative (not selected, not a defect); C-3 remains
  frontend-track; C-5 remains maintenance; **DRS remains BLOCKED**. AH-1
  and AH-2 remain preserved. Documents 77 / 78 remain authoritative. Zero
  new error classes.

---

## 14. Next Governance Artifact

**The next substantive governance artifact — once Document 89 is itself
CTO-ratified and Document 88 is thereby formally ratified — is the M16
Architecture Decision Pack** — a new "M16 … Architecture Decision Pack"
document, **not created here and not begun here**, that will decide the
retrieval mechanism within the filing, the internal passage / storage
representation behind the frozen external locator, the `JobKind`
realization, the transient result-retention mechanism,
prompt-construction discipline, model tier and the single-generation
enforcement mechanism, the semantic-grounding evaluation architecture,
and the numeric values of every operational bound — strictly within the
API contract fixed by Document 87 Revision 2 (ratified through Document
88, in force once Document 88 is ratified) and the ratified single-turn +
stateless + single-filing scope. It is subject to its own separate CTO
review and ratification.

Subsequent stages, each a distinct CTO act (none performed here):

```text
M16 Architecture Decision Pack → CTO architecture ratification
        ↓
M16 Implementation Authorization → CTO ratification
        ↓
implementation → technical review → commit authorization → commit →
push authorization → push → post-push review → M16 closure → closure ratification
```

**Document 89 identifies the M16 Architecture Decision Pack as the next
governance stage but does NOT authorize architecture implementation, any
architecture decision, or any of the stages above.**

---

**🟡 DOCUMENT 89 — DRAFT / PENDING CTO REVIEW — PROPOSED RATIFICATION OF
DOCUMENT 88. NOT YET RATIFIED; DOES NOT SELF-RATIFY; TAKES EFFECT ONLY ON
ITS OWN SEPARATE CTO REVIEW AND RATIFICATION. DOCUMENT 88 ITSELF IS
CTO-REVIEWED AND APPROVED FOR RATIFICATION BUT IS NOT YET FORMALLY
RATIFIED — ITS FORMAL RATIFICATION IS THE ACT THIS RECORD PROPOSES AND
OCCURS ONLY ON THIS RECORD'S OWN SEPARATE CTO RATIFICATION. THIS RECORD
PROPOSES EXACTLY ONE GOVERNANCE ACT FOR CTO RATIFICATION: FORMALLY
RATIFYING DOCUMENT 88 AS THE CTO RATIFICATION RECORD FOR DOCUMENT 87
REVISION 2. THE GOVERNANCE-LEVEL
DISTINCTION IS PRESERVED AND NOT COLLAPSED: DOCUMENT 87 REVISION 2 IS THE
SUBSTANTIVE
M16 = FILING Q&A (FQA v1) API CONTRACT; DOCUMENT 88 IS THE AUTHORITATIVE
RECORD THAT RATIFIES DOCUMENT 87 REVISION 2 AND HOLDS THE RATIFIED
CONTRACT STATUS AS A SEPARATE DOCUMENT WITHOUT EDITING DOCUMENT 87 OR ITS
EMBEDDED STATUS METADATA, AND IS ITSELF CTO-REVIEWED / APPROVED FOR
RATIFICATION — NOT YET RATIFIED; DOCUMENT 89 IS THE RECORD THAT PROPOSES
TO RATIFY DOCUMENT 88. DOCUMENT 89 DOES NOT MODIFY DOCUMENT 87 OR DOCUMENT 88, DOES NOT
CREATE OR CHANGE THE API CONTRACT, DOES NOT RE-RATIFY OR RE-OPEN DOCUMENT
87 REVISION 2, AND DOES NOT SYNCHRONIZE DOCUMENT 87'S EMBEDDED HISTORICAL
STATUS METADATA — DOCUMENT 87'S IN-FILE BANNER STILL READS "DRAFT /
PENDING CTO REVIEW (REVISION 2). NOT RATIFIED", IS DOCUMENT 87'S
PRE-RATIFICATION METADATA, AND IS NOT MODIFIED BY THIS TASK; THE RATIFIED
STATUS OF THE M16 API CONTRACT IS CARRIED BY DOCUMENT 88; DOCUMENT 88
ITSELF IS CTO-REVIEWED AND APPROVED FOR RATIFICATION BUT NOT YET FORMALLY
RATIFIED, AND THIS RECORD (DRAFT / PENDING CTO REVIEW) PROPOSES THAT
RATIFICATION WITHOUT SELF-RATIFYING; ON THIS RECORD'S OWN CTO
RATIFICATION, DOCUMENT 88 BECOMES FORMALLY CTO-RATIFIED AND THE D87 R2
CONTRACT STANDS RATIFIED THROUGH IT. WHERE DOCUMENT 88 AND DOCUMENT 87'S
EMBEDDED MARKER DIFFER ON RATIFICATION STATUS, DOCUMENT 88 IS
AUTHORITATIVE. THE GOVERNANCE LINEAGE IS: D83 = FQA v1 SCOPE DECISION;
D85 = RATIFICATION OF THE D83 SCOPE DECISION; D84 = M16 MILESTONE
SELECTION; D86 = RATIFICATION OF THE D84 MILESTONE SELECTION; D87
REVISION 2 = M16 API CONTRACT (SUBSTANTIVE); D88 = RATIFICATION OF THE
D87 REVISION 2 API CONTRACT (CTO-REVIEWED / APPROVED FOR RATIFICATION —
NOT YET RATIFIED); D89 = PROPOSED RATIFICATION OF DOCUMENT 88 (DRAFT /
PENDING CTO REVIEW — NOT YET RATIFIED). DOCUMENT 88 IS CONFIRMED TO PERFORM A
SINGLE GOVERNANCE ACT, TO BE INTERNALLY CONSISTENT INCLUDING THE
CTO-DIRECTED CORRECTION PASS THAT RESOLVED THE STATUS-METADATA-AUTHORITY
WORDING, AND TO RESTATE THE DOCUMENT 87 REVISION 2 CONTRACT IN SUBSTANCE
WITHOUT INVENTING, MODIFYING, EXTENDING, OR NARROWING IT. THE DOCUMENT 87
REVISION 2 CONTRACT (CTO-REVIEWED / APPROVED FOR RATIFICATION) IS
PRESERVED: FQA v1 IS SINGLE-TURN,
STATELESS WITH RESPECT TO DURABLE CONVERSATIONAL / RESEARCH STATE, AND
SINGLE-FILING, WITH FILING IDENTITY EXACTLY `(ticker, doc_id)`, NO
CROSS-FILING RESEARCH, NO CORPUS SYNTHESIS, NO PORTFOLIO RESEARCH, AND DRS
OUTSIDE M16; A FOUR-ROUTE ASYNC FAMILY (`POST` CREATE, `GET` STATUS,
`GET` STREAM, `POST` CANCEL) UNDER THE `qa` PATH SEGMENT WITH ROUTE
INVENTORY `51 → 55`; THE `queued → running → completed | failed |
cancelled` JOB LIFECYCLE ON THE SHARED `MAX_ACTIVE_JOBS` BUDGET WITH A
DEDICATED FQA JOB-DEADLINE CONFIGURATION WHOSE NUMERIC VALUE IS
OPERATIONAL; CREATE RESPONSE `{id, status: "queued", reused: false}` WITH
`reused` ALWAYS `false`; THE FROZEN COMPLETED `answer` OBJECT WITH
`question` ECHOING THE NORMALIZED VALUE AND THE `answer` KEY OMITTED
UNLESS `completed`; IDEMPOTENT CANCELLATION SEMANTICS (TERMINAL JOB →
`200` UNCHANGED STATUS; UNKNOWN / FOREIGN ID → 404 NON-DISCLOSURE); SSE
FINAL-FRAME SEMANTICS (ONE UNNAMED `data:` FRAME WITH `node == "final"`,
EMITTED ONCE ONLY FOR A `completed` JOB INCLUDING THE
`insufficient_evidence` / ZERO-CONTENT COMPLETION, NEVER FOR `failed` /
`cancelled`, BUILT FROM THE SAME TRANSIENT BUFFER AS `GET`); THE CLOSED
TWO-VALUE `state` ENUM `{answered, insufficient_evidence}` WITH
DETERMINISTIC §9.1 / §9.2 DEFINITIONS; ZERO-CONTENT FILING BEHAVIOR
(RESOLVING `(ticker, doc_id)` WITH NO USABLE CONTENT → `200` / `completed`
/ `insufficient_evidence` / EMPTY `sources` / EMPTY `cited_source_indices`
/ `coverage_boundaries` ENTRY — NEVER A 404, NEVER A 502); THE `[n]` /
`sources[]` / `cited_source_indices` CITATION STRUCTURE WITH THE FROZEN
`{index, doc_id, chunk_start, chunk_end}` EXTERNAL LOCATOR;
DETERMINISTIC RUNTIME CITATION-STRUCTURE VALIDATION ONLY, WITH SEMANTIC
GROUNDING (WHETHER A CITED PASSAGE SUBSTANTIATES A CLAIM; WHETHER
UNRESTRICTED PROSE CONTAINS A SUBSTANTIVE FACTUAL CLAIM REQUIRING A
CITATION) AS AN EVALUATION CONCERN (D87 R2 §20 OAQ-4), NOT
DETERMINISTICALLY DECIDABLE AT RUNTIME, THE PRODUCT GROUNDING REQUIREMENT
PRESERVED AND UNWEAKENED; BYOK FIELDS REUSED VERBATIM WITH `llm_api_key`
NEVER PERSISTED OR LOGGED; THE SSRF BOUNDARY (`current_user` ON EVERY
ROUTE; CUSTOM PROVIDER / BASE URL BY A NON-ADMIN → 403; `assert_public_url`
GUARD → `HTTPException(400, …)` ON A PRIVATE ADDRESS; OWNER-SCOPED JOB
RECORDS; SHARED FILING CORPUS LIKE M13 / M14); THE EXISTING NINE-CLASS
ERROR TAXONOMY WITH ZERO NEW ERROR CLASSES AND THE ONE
`400`-WITHOUT-`type` SSRF-GUARD RESPONSE REPRODUCING M14 / M15 EXACTLY;
AH-1 AND AH-2 PRESERVED — "STATELESS" IS NOT REINTERPRETED AS A
PROHIBITION ON THE TRANSIENT OPERATIONAL EXECUTION STATE THE PLATFORM
REQUIRES. DOCUMENT 89 DECIDES NO ARCHITECTURE — RETRIEVAL IMPLEMENTATION,
THE INTERNAL PASSAGE REPRESENTATION BEHIND THE FROZEN LOCATOR, `JobKind`
REALIZATION, THE RETENTION MECHANISM, PROMPT CONSTRUCTION, MODEL TIER,
MODEL / PROVIDER SELECTION, THE SINGLE-GENERATION ENFORCEMENT, THE
EVALUATION ARCHITECTURE, THE OPERATIONAL NUMERIC BOUNDS, AND ANY MONGODB
COLLECTION / INDEX / MIGRATION, REDIS PERSISTENCE, LANGGRAPH TOPOLOGY,
FRONTEND IMPLEMENTATION, OR DEPLOYMENT TOPOLOGY REMAIN OWNED BY THE M16
ARCHITECTURE DECISION PACK OR LATER GOVERNANCE (D87 R2 §20 OAQ-1 THROUGH
OAQ-8, NONE RESOLVED HERE). RATIFICATION OF THIS RECORD AUTHORIZES NO
API-CONTRACT CREATION OR CHANGE, NO ARCHITECTURE DECISION, NO
IMPLEMENTATION, NO
EVALUATION INFRASTRUCTURE (THE M15 GOLDEN-DATASET `report`-MODE FOLLOW-UP
REMAINS TRACKED FUTURE WORK PER DOCUMENTS 77 / 78 AND IS NOT REOPENED), NO
MONGODB / REDIS / LANGGRAPH / FRONTEND WORK, NO DEPLOYMENT OR RELEASE, NO
COMMIT / PUSH / MERGE OR ANY OTHER GIT MUTATION, AND NO FUTURE DRS WORK.
M15 / C-4 REMAINS CLOSED AND IS NOT REOPENED; C-2 REMAINS AN ELIGIBLE
ALTERNATIVE; C-3 REMAINS FRONTEND-TRACK; C-5 REMAINS MAINTENANCE;
DOCUMENTS 77 / 78 REMAIN AUTHORITATIVE; ZERO NEW ERROR CLASSES. DOCUMENTS
67–88 WERE READ, NOT MODIFIED; DOCUMENT 87 AND DOCUMENT 88 WERE NOT
MODIFIED AND DOCUMENT 87'S EMBEDDED HISTORICAL STATUS METADATA WAS NOT
SYNCHRONIZED. NO SOURCE, TEST, OR CONFIGURATION FILE WAS CREATED OR
MODIFIED. NO STAGE. NO COMMIT. NO PUSH. NO MERGE / REBASE / RESET / AMEND.
ONCE DOCUMENT 89 IS ITSELF CTO-RATIFIED, DOCUMENT 88 BECOMES FORMALLY
RATIFIED AND THE NEXT SUBSTANTIVE GOVERNANCE ARTIFACT IS THE M16
ARCHITECTURE DECISION PACK — NOT CREATED HERE, NOT BEGUN HERE, AND NOT
AUTHORIZED FOR IMPLEMENTATION BY THIS RECORD.**

DOCUMENT 89 D88 RATIFICATION RECORD COMPLETE — AWAITING CTO REVIEW
