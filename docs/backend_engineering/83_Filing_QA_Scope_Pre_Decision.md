# 83 — Filing Q&A Scope Pre-Decision

## 1. Document Status

🟡 **DRAFT / PENDING CTO REVIEW. NOT RATIFIED.**

This is a **documentation-only governance pre-decision**. It answers
exactly one substantive question (§2) and proposes a scope boundary for
**Filing Q&A version 1**, to be settled **before** any formal M16
milestone selection.

**This document is not, and does not create:** an implementation, an M16
API contract, an M16 architecture decision pack, an implementation
authorization, or a milestone selection. It contains no request/response
schema, no route list, no retrieval design, no persistence design — those
belong to the later M16 contract and architecture phases (§11).

**Type:** governance decision-record proposal (documentation only — no
source code, test, configuration, schema, migration, index, route,
LangGraph node/topology, MongoDB collection, Redis usage, provider,
evaluation-infrastructure, deployment, or frontend file created or
modified to produce it; `.gitignore` untouched. Documents 67–82 read, not
modified. The only file this task creates is this document.

**Date:** 2026-09-08.

**Predecessor gate:** [Document 82](82_Document81_CTO_Ratification_Record.md)
— Document 81 CTO Ratification Record (🟢 CTO-RATIFIED, 2026-09-08), whose
§3 names "the separate Filing Q&A scope pre-decision" as the next
substantive governance act. This document is that artifact.

---

## 2. Decision Question

> **Should Filing Q&A version 1 be formally constrained to
> single-turn + stateless + single-filing?**

Exactly one question. This document evaluates that boundary (§4–§8) and
records a **recommendation** and a **decision status** (§9, §13). It does
not decide anything the M16 contract or architecture phases own (§11).

---

## 3. Governance Lineage (preserved, not rewritten)

```text
D67  — Post-M14 Backend & AI Roadmap Reconciliation        🟢 CTO-RATIFIED (2026-09-03)
D68 / D69 — M15 Milestone Selection = C-4 + Ratification    🟢 CTO-RATIFIED
D70 R4 / D72 — M15 / C-4 API Contract + Ratification        🟢 CTO-RATIFIED
D71  — blocked D70 ratification review                     🔴 BLOCKED (historical — superseded by D72)
D73 R1 / D74 — M15 / C-4 Architecture Pack + Ratification   🟢 CTO-RATIFIED (AH-1, AH-2 resolved)
D75 / D76 — M15 Implementation Authorization + Ratification 🟢 CTO-RATIFIED
D77 / D78 — D75 §14 Testing-Floor Clarification + Ratif.    🟢 CTO-RATIFIED (golden-dataset eval = tracked future work, not a gate)
D79 / D80 — M15 / C-4 Milestone Closure + Ratification      🟢 CTO-RATIFIED — M15 / C-4 CLOSED
D81  — Post-M15 Backend & AI Roadmap Reconciliation         🟢 recorded 2026-09-08
D82  — D81 Ratification                                     🟢 CTO-RATIFIED — Filing Q&A is the recommended next direction
D83  — Filing Q&A Scope Pre-Decision (THIS)                 🟡 DRAFT / PENDING CTO REVIEW
       ↓
CTO ratification of this pre-decision                       NOT PERFORMED
       ↓
Formal M16 milestone-selection record                       NOT CREATED — a separate, later CTO act
```

Documents 67–82 are cited, not reinterpreted or reopened.

---

## 4. Current Post-M15 Position (preserved facts — not re-decided here)

- **M15 / C-4 "What Changed Since Last Review" is complete and CLOSED**
  (Documents 79 / 80); commit `f8c06649e94f45c388bbecf3eeedb9e5340f2024`,
  reviewed, pushed.
- **C-4 is no longer the active milestone candidate** — it is completed
  work, removed from the candidate pool (Document 81 §3 / §6).
- **Document 81 recommends Filing Q&A** as the strongest next Backend & AI
  direction, bounded as single-turn / stateless / single-filing, and
  **conditional on this scope pre-decision** (Document 81 §7).
- **Document 82 ratifies Document 81** as the authoritative Post-M15
  roadmap position.
- **Filing Q&A has NOT been selected as M16.** M16 selection remains a
  separate, subsequent CTO governance act (Documents 81 §7 / 82 §4).
- **C-2 Structured Filing-Section Extraction remains an eligible Backend &
  AI candidate** — the alternative if this scope pre-decision is not made
  (Document 81 §7); not promoted as remediation of any accepted ceiling.
- **C-3 Financial Visualization remains a frontend-track initiative**, not
  a Backend & AI milestone.
- **C-5 governance / register hygiene remains maintenance**, not a
  milestone.
- **Durable Research Sessions remain BLOCKED** — product decision + ADR +
  new collection all still missing (Document 58 §10; Document 81 §4.DRS).
- **AH-1 remains preserved** — the M15 `report`-mode structured-schema
  resolution, unchanged.
- **AH-2 remains preserved** — the process-local, TTL-bounded, in-process
  job-result buffer; single-backend-process `POST → completion → GET`
  lifecycle; no new MongoDB collection; no Redis or cross-process
  final-result persistence; no cross-process reconstruction; SSE does not
  bypass the invariant. It is a standing constraint on every new
  async-job Backend & AI surface.
- **Documents 77 / 78 remain authoritative** on the golden-dataset
  testing-floor clarification: golden-dataset `report`-mode evaluation is
  evaluation / validation evidence and tracked future work, **not** a
  completion or commit-review gate. Nothing here reopens or reinterprets
  that.

"Filing Q&A" is a named line in the frozen product roadmap
(`docs/master-plan/03_Feature_Roadmap.md` → **AI Financial Copilot →
Filing Q&A**).

---

## 5. Proposed Filing Q&A v1 Scope

The proposed boundary has three constraints. Each is stated as an
externally observable v1 limit, not an implementation detail.

### 5.1 Single-turn

- **One user request produces one bounded answer.** The request carries
  the question and the filing identity; the response is a single grounded
  answer (with citations) plus an honest "insufficient evidence" state
  when the filing does not support an answer.
- **No conversational continuation is part of v1.** No follow-up turn,
  no "ask a follow-up", no server-remembered prior question or answer, no
  thread id. A user who wants to ask a second question issues a second,
  independent request.

### 5.2 Stateless

- **The request does not depend on durable user research state.** The
  answer is a pure function of (the question, the identified filing's own
  persisted content). No per-user history, no "since last question", no
  saved-reasoning store, no research-session record is read or written.
- **No persistent conversation or research-session state is required or
  created.** Transient job-result retention for the answer follows the
  existing **AH-2** pattern (process-local, TTL-bounded, single-process
  `POST → GET`), exactly as M14 Filing Analysis and M15 Change Brief
  already do — this is *not* durable research state.

### 5.3 Single-filing

- **The request operates against exactly one explicitly identified
  filing** (the established `(ticker, doc_id)` filing identity — Document
  59; Document 64). The caller names the filing; there is no default and
  no implicit "most recent".
- **No cross-filing research in this scope.** v1 does not join, compare,
  or aggregate across two or more filings, and does not synthesize an
  answer from a corpus. Cross-filing question answering is a different,
  broader capability (§8 Option C) requiring its own governance.

---

## 6. DRS Boundary

The proposed scope is deliberately shaped so Filing Q&A v1 **does not
brush Durable Research Sessions**, which remain BLOCKED.

- **A single-turn request does not establish a durable research session.**
  With no follow-up turn, no thread id, and no server-remembered prior
  exchange, there is no session to persist or resume — the defining
  characteristic of DRS is absent by construction.
- **Stateless operation avoids persistent research state.** No per-user
  history store, no saved reasoning, no saved sources, no "resume
  research" pointer is read or written. There is nothing DRS-shaped to
  leak into.
- **Single-filing scope prevents cross-filing research workflows from
  expanding the feature.** A capability confined to one explicitly named
  filing cannot grow into a multi-source research workspace without a
  visible, separately governed scope change.
- **Multi-turn continuation or durable research-session semantics are
  outside this v1 scope and would require separate governance.** A
  conversational Filing Q&A (§8 Option B) would need a per-user, durable,
  resumable conversation store — structurally the same class of state as
  DRS — and must not be built without the DRS product decision + ADR +
  authorized new collection that Document 58 §10 requires.

**This is a v1 scope decision, not a permanent architectural
prohibition.** It does not claim that every future form of Filing Q&A
must remain stateless. A later, separately governed FQA version may
revisit multi-turn or stateful behaviour through its own contract,
architecture, and — where durable per-user state is involved — the DRS
governance path. This pre-decision only fixes the boundary of **v1**.

---

## 7. Product and Engineering Analysis (bounded v1 scope)

| Dimension | Assessment for single-turn / stateless / single-filing |
|---|---|
| **User value** | **High and real.** Users can ask targeted questions of one filing ("what's the customer-concentration risk here?", "how is revenue recognised?") — deeper than the four fixed M14 outputs and the M15 change brief, without needing to read the raw text. A named "AI Financial Copilot" roadmap line. The bounded form still delivers the core value; the conversational wrapper is convenience, not the substance. |
| **Implementation complexity** | **Medium — a sixth instance of a proven pattern.** Reuses the M9.1 / M14 / M15 out-of-graph async job + SSE + cancel route family, the `agents/retrieval.py` `doc_id` filing-scope hook, the deterministic citation validator, and the AH-2 result-buffer pattern. No new infrastructure class. |
| **Architectural risk** | **Low–Medium.** The named top scope-creep vector is "Filing Analysis → chatbot" (Document 62 R-1); this scope forecloses it at the boundary. No LangGraph topology change (out-of-graph, matching M9.1 / M14 / M15). No new provider. |
| **Persistence requirements** | **None new.** Reads one filing's already-persisted content (`filings` / `filing_chunks`). No new write path, no new collection. Transient answer retention = AH-2 pattern. |
| **Interaction with AH-2** | **Inherits AH-2 unchanged.** A single-turn answer job is process-local, TTL-bounded, single-process `POST → GET`, `reused` always false — identical to M14 / M15. It neither challenges nor extends the invariant; the single-process deployment ceiling carries forward. |
| **DRS leakage risk** | **None in this scope (§6).** No session, no per-user history, no cross-filing workspace. The conversational and cross-filing forms — explicitly excluded — are where DRS risk lives. |
| **Retrieval complexity** | **Bounded.** Retrieval is scoped to one filing via the existing `doc_id` hook — no corpus-wide search, no cross-document ranking. The exact retrieval mechanism (whole-filing vs. chunk-retrieval vs. section-scoped) is an M16 architecture decision (§11), not fixed here. |
| **Citation requirements** | **Reuse, not reinvention.** The established convention (inline `[n]` markers + indexed `sources[]` + `cited_source_indices`, deterministic post-hoc validation, model never trusted with real anchors) applies. Whether the source-reference shape reuses M14's `{doc_id, chunk_start, chunk_end}` or a variant is an M16 contract decision (§11). Grounding law: zero grounded citations = failed generation, never a fabricated answer. |
| **Testing burden** | **Bounded and precedented.** Hermetic route-family tests (validation, lifecycle, ownership/non-disclosure, SSE), deterministic citation-validation tests, an "insufficient evidence / no answer" path, AH-2 deployment-invariant tests, M14/M15 regression — the same shape as the M15 §14 floor. A grounding/answerability evaluation set may be desirable as tracked evidence (an M16 decision, per the D77/D78 precedent — not made here). |
| **Operational complexity** | **Low.** One new `JobKind`, one new `job_deadline_*_s` setting, one outcome-labelled metric, one OTel span — the exact additive footprint M14 and M15 each had. Single-process deployment ceiling unchanged. |
| **Future extensibility** | **Preserved, not foreclosed.** A bounded v1 is a clean base a later version can extend to multi-turn or cross-filing through its own governance. Shipping the stateful form first would create durable research infrastructure before the product need is proven and before DRS governance exists. |

**Conclusion of the analysis:** the bounded v1 scope delivers meaningful,
roadmap-aligned user value using proven infrastructure, with no new
persistence, no AH-2 change, and no DRS exposure — i.e. it provides the
value **without prematurely creating durable research infrastructure.**

---

## 8. Alternatives Considered

### Option A — Single-turn + stateless + single-filing (bounded v1) — **preferred**

The proposed scope. Highest value-to-risk ratio for v1: real user value,
proven pattern, no new persistence, AH-2-consistent, DRS-clean,
extensible later.

### Option B — Multi-turn conversational Filing Q&A

Would introduce conversation-continuation semantics: a thread identity,
server-remembered prior turns, and a per-user durable, resumable
conversation store. That store is **structurally the same class of state
as Durable Research Sessions**. It also amplifies the "Filing Analysis →
chatbot" scope-creep vector (Document 62 R-1) and the drift/grounding
surface. **Rejected for v1** — it requires the DRS product decision + ADR
+ authorized new collection that Document 58 §10 requires, none of which
exists.

### Option C — Cross-filing Filing Q&A

Would answer questions across two or more filings (or a corpus):
multi-document retrieval, cross-document ranking, and answer synthesis
that is closer to open research than to reading one document. Broader
retrieval infrastructure and broader "research" semantics. **Rejected for
v1** — a distinct, larger capability that should be its own separately
scoped milestone if ever pursued; folding it into FQA v1 would make the
scope unbounded.

**Why Option A for v1:** it is the only option that delivers the named
roadmap value while (a) requiring no new persistence and no DRS-class
governance, (b) inheriting AH-2 unchanged, (c) foreclosing the chatbot
scope-creep vector at the boundary, and (d) leaving multi-turn and
cross-filing as clean, separately governed future extensions rather than
premature commitments.

---

## 9. CTO Recommendation

Three levels are kept explicitly distinct:

- **Analysis (§7):** the bounded v1 scope provides meaningful user value
  without prematurely creating durable research infrastructure; it
  inherits AH-2 unchanged and stays clear of DRS.
- **Recommendation (this section):** **APPROVE — Filing Q&A v1 should be
  formally constrained to single-turn + stateless + single-filing.** This
  matches the CTO's stated preliminary recommendation and Document 81's
  recommended bound.
- **Formal decision status:** 🟡 **DRAFT / PENDING CTO REVIEW — NOT
  RATIFIED.** This document does **not** claim the scope decision is
  ratified. Ratification is a separate, subsequent CTO act (§13).

---

## 10. Explicit Non-Authorization

This scope pre-decision — **even once ratified** — does **NOT** authorize:

- M16 milestone selection;
- creation of an M16 API contract;
- any architecture design or M16 architecture decision pack;
- implementation of Filing Q&A (or of C-2, or of anything);
- any source-code change;
- any schema change;
- any MongoDB collection, index, or migration;
- any Redis persistence;
- any LangGraph implementation or topology change;
- any frontend implementation;
- any evaluation-infrastructure work (the M15 golden-dataset `report`-mode
  follow-up remains tracked future work per Documents 77 / 78 and is not
  reopened);
- any deployment or release;
- a commit, a push, or a merge.

**The scope decision must not silently become an implementation
authorization.** Its only effect, once ratified, is to fix the v1 scope
boundary that the subsequent M16 selection, contract, and architecture
artifacts must respect.

---

## 11. Open Questions for the Later M16 Contract / Architecture (not resolved here)

Recorded so they are visibly deferred, not silently assumed:

- **Retrieval mechanism** within the single filing — whole-filing context
  vs. chunk-retrieval vs. section-scoped (interacts with C-2 if that is
  ever built). M16 architecture.
- **Answer citation shape** — reuse M14's `{doc_id, chunk_start,
  chunk_end}` anchor, or a variant. M16 contract.
- **"No answer" / insufficient-evidence semantics** and the state
  vocabulary (reuse of `complete` / `partial` / `insufficient_evidence`
  or a narrower set). M16 contract.
- **Grounding / answerability evaluation gate** — whether a §20.1-style
  gate applies to answer quality before shipping (an M16 decision,
  following the D77 / D78 precedent that such evidence need not be a
  hard commit gate). M16 architecture.
- **Job deadline value, `JobKind` identifier, metric labels, span name** —
  operational, M16 architecture / implementation.
- **BYOK / SSRF** — expected reuse of the existing `require_admin` +
  `assert_public_url` boundary verbatim; confirm in the M16 contract.
- **Route family and identity** — expected reuse of the async
  `POST/GET/GET-stream/POST-cancel` shape under a company/filing-scoped
  path with `(ticker, doc_id)` identity and 404 non-disclosure; fixed in
  the M16 contract.
- **Frontend surface** — a filing Q&A UI is out of backend scope; a
  frontend-track concern.

None of the above is decided by this pre-decision.

---

## 12. Repository Provenance

Recorded by read-only inspection this session on 2026-09-08. **No `git`
mutation was performed** — no `add` / stage, `commit`, `push`, `amend`,
`rebase`, `merge`, `reset`, `restore`, `stash`, or `clean`.

- `HEAD = origin/main = f8c06649e94f45c388bbecf3eeedb9e5340f2024`
  (`f8c0664`), ahead/behind `0 / 0`.
- Document number 83 was verified free before creation (highest existing
  Backend & AI governance document was 82).
- **Documents 67–82 were read, not modified.** The M15 chain (Documents
  70 R4 / 72, 73 R1 / 74, 75 / 76, 77 / 78, 79 / 80) and the Post-M15
  reconciliation and its ratification (Documents 81 / 82) remain as
  written and are cited, not reinterpreted.
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
  ?? docs/backend_engineering/67_...md through 82_...md            (pre-existing untracked governance documents — not modified)
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/83_Filing_QA_Scope_Pre_Decision.md`). It is
  untracked and not yet version-controlled. Staging or committing it is a
  separate, subsequently CTO-authorized step, not performed here.

---

## 13. Decision State / Next Governance Step

**Current state:** 🟡 **DRAFT / PENDING CTO REVIEW — NOT RATIFIED.**

```text
D83 (THIS) — Filing Q&A Scope Pre-Decision           🟡 DRAFT / PENDING CTO REVIEW
        ↓  CTO ratification of this pre-decision      NOT PERFORMED
Formal M16 milestone-selection record                NOT CREATED — a separate CTO act
        ↓  CTO milestone-selection decision
M16 API Contract → CTO contract ratification         NOT CREATED
        ↓
M16 Architecture Decision Pack → CTO ratification    NOT CREATED
        ↓
M16 Implementation Authorization → CTO ratification  NOT CREATED
        ↓
implementation → technical review → commit authorization → push authorization → closure → closure ratification
```

**The next governance step is CTO review and ratification of this scope
pre-decision.** Only after that would a formal M16 milestone-selection
record be created — a separate CTO act — followed by the M16 contract,
architecture, and implementation-authorization artifacts, each subject to
this v1 scope boundary.

---

**🟡 FILING Q&A SCOPE PRE-DECISION — DRAFT / PENDING CTO REVIEW. NOT
RATIFIED. THIS DOCUMENT ANSWERS EXACTLY ONE QUESTION — SHOULD FILING Q&A
v1 BE FORMALLY CONSTRAINED TO SINGLE-TURN + STATELESS + SINGLE-FILING —
AND RECOMMENDS **APPROVE**, WHILE EXPLICITLY DISTINGUISHING ANALYSIS,
RECOMMENDATION, AND (UN-RATIFIED) DECISION STATUS. THE BOUNDED v1 SCOPE
DELIVERS MEANINGFUL, ROADMAP-ALIGNED USER VALUE USING THE PROVEN M9.1 /
M14 / M15 ASYNC + CITATION-VALIDATION PATTERN, WITH NO NEW PERSISTENCE,
AH-2 INHERITED UNCHANGED, AND NO DURABLE RESEARCH SESSIONS EXPOSURE: A
SINGLE-TURN REQUEST ESTABLISHES NO DURABLE SESSION, STATELESS OPERATION
CREATES NO PERSISTENT RESEARCH STATE, AND SINGLE-FILING SCOPE PREVENTS
CROSS-FILING RESEARCH WORKFLOWS. MULTI-TURN CONVERSATIONAL (OPTION B) AND
CROSS-FILING (OPTION C) FORMS ARE OUTSIDE v1 AND WOULD REQUIRE THEIR OWN
GOVERNANCE — OPTION B SPECIFICALLY REQUIRES THE DRS PRODUCT DECISION + ADR
+ NEW COLLECTION THAT DOCUMENT 58 §10 REQUIRES. THIS IS A v1 SCOPE
DECISION, NOT A PERMANENT ARCHITECTURAL PROHIBITION ON A STATEFUL FUTURE
FQA. M15 / C-4 REMAINS CLOSED; C-4 IS NOT THE ACTIVE CANDIDATE; D81 / D82
STAND; FILING Q&A IS NOT SELECTED AS M16 AND M16 SELECTION REMAINS A
SEPARATE FUTURE ACT; C-2 REMAINS AN ELIGIBLE ALTERNATIVE; C-3 REMAINS
FRONTEND-TRACK; C-5 REMAINS MAINTENANCE; DURABLE RESEARCH SESSIONS REMAIN
BLOCKED; AH-1 AND AH-2 REMAIN PRESERVED; DOCUMENTS 77 / 78 REMAIN
AUTHORITATIVE ON THE GOLDEN-DATASET TESTING-FLOOR CLARIFICATION. THIS
PRE-DECISION — EVEN ONCE RATIFIED — AUTHORIZES NO M16 SELECTION, NO API
CONTRACT, NO ARCHITECTURE, NO IMPLEMENTATION, NO SOURCE / SCHEMA /
MONGODB / REDIS / LANGGRAPH / FRONTEND / EVALUATION-INFRASTRUCTURE CHANGE,
NO DEPLOYMENT, NO RELEASE, AND NO COMMIT / PUSH / MERGE. DOCUMENTS 67–82
WERE READ, NOT MODIFIED. NO SOURCE, TEST, OR CONFIGURATION FILE WAS
CREATED OR MODIFIED. NO STAGE. NO COMMIT. NO PUSH. THE NEXT GOVERNANCE
STEP IS CTO REVIEW AND RATIFICATION OF THIS SCOPE PRE-DECISION.**
