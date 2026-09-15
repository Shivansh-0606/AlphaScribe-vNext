# 84 — M16 Milestone Selection Record

**Status:** 🟡 **M16 MILESTONE SELECTION — PROPOSED. DRAFT / PENDING CTO
REVIEW. NOT RATIFIED.** This document performs the **formal M16
milestone-selection** governance act reserved by
[Document 81 §7](81_Post_M15_Backend_AI_Roadmap_Reconciliation.md) /
[Document 82 §4](82_Document81_CTO_Ratification_Record.md) and made ready
by the Filing Q&A scope pre-decision
[Document 83](83_Filing_QA_Scope_Pre_Decision.md). **It proposes the
selection: M16 = Filing Q&A (FQA v1), constrained to single-turn +
stateless + single-filing as established by Document 83.** Selecting the
milestone authorizes progression to the **M16 API Contract** governance
stage only — it authorizes no contract, no architecture, no
source/test/schema/infrastructure change, no retrieval strategy, no
provider selection, no LangGraph change, no persistence, no
implementation, no commit, and no push (§10, §11).

**Type:** Governance / milestone-selection decision record (documentation
only — no source code, test, schema, API route, migration, index,
configuration, infrastructure, LangGraph topology, MongoDB
collection/schema, Redis, provider, RAG, or evaluation-infrastructure file
created or modified to produce this record; Documents 67–83 read, not
modified. The only file this task creates is this document.

**Date:** 2026-09-08.

**Predecessor gate:** [Document 83](83_Filing_QA_Scope_Pre_Decision.md) —
Filing Q&A Scope Pre-Decision (🟡 DRAFT / PENDING CTO REVIEW as recorded;
this selection is made *under* the scope boundary D83 proposes and is
itself subject to CTO ratification — §14).

**Structural precedent (cited, unmodified):**
[68_M15_Formal_Milestone_Selection_Record.md](68_M15_Formal_Milestone_Selection_Record.md)
— the most recent formal milestone-selection record; its section
skeleton, its "selection authorizes the contract stage only" boundary,
and its candidate-disposition form are reused here.

---

## 0. What This Document Is and Is Not

**Is:** the formal record that **M16 is Filing Q&A (FQA v1)**, bounded
exactly as Document 83 establishes (single-turn + stateless +
single-filing), with the alternatives considered and rejected for M16
recorded, and the downstream governance sequence stated.

**Is not:** an M16 API contract; an M16 architecture decision pack; an
implementation authorization; a request/response schema; a retrieval,
provider, prompt, LangGraph, MongoDB, Redis, or persistence design; a
citation-schema definition; a commit or push authorization. It broadens
nothing in Document 83 and reopens nothing in Documents 67–82.

---

## 1. Document Metadata

| Field | Value |
|---|---|
| Document number | 84 |
| Title | M16 Milestone Selection Record |
| Milestone | **M16 = Filing Q&A (FQA v1)** — single-turn + stateless + single-filing (Document 83) |
| Governance stage | Formal milestone selection (this act) |
| Predecessor gate | Document 83 — Filing Q&A Scope Pre-Decision; and Document 82 — Document 81 CTO Ratification Record (🟢 CTO-RATIFIED, 2026-09-08) |
| Successor gate (NOT created here) | CTO ratification of this selection, then a separate M16 API Contract Proposal |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Governance Position

🟡 **PROPOSED — CTO DECISION REQUIRED. NOT RATIFIED.**

```text
M15 / C-4 CLOSED (f8c0664, pushed; Documents 79 / 80)
        ↓
Post-M15 Backend & AI Roadmap Reconciliation (Doc 81)   🟢 CTO-RATIFIED via Doc 82 — Filing Q&A is the recommended direction
        ↓
Filing Q&A Scope Pre-Decision (Doc 83)                  🟡 DRAFT / PENDING CTO REVIEW — single-turn + stateless + single-filing
        ↓
Formal M16 milestone selection (THIS — Doc 84)          🟡 PROPOSED — pending CTO review
        ↓  CTO milestone-selection ratification          NOT YET PERFORMED
M16 API Contract proposal                               NOT CREATED
        ↓  CTO contract ratification
M16 Architecture Decision Pack                          NOT CREATED
        ↓  CTO architecture ratification
M16 Implementation Authorization Decision               NOT CREATED
        ↓
implementation → technical review → commit authorization → push authorization → post-push review → M16 closure
```

This document performs exactly one act: **proposing the formal selection
of M16.** It does not perform, and does not imply, any later stage.

---

## 3. Authority / Basis for the Selection

This selection rests entirely on already-recorded governance; it invents
nothing:

- **Document 81** (Post-M15 Backend & AI Roadmap Reconciliation) ranked
  **Filing Q&A — bounded single-turn / stateless / single-filing** as the
  strongest eligible next Backend & AI direction, with C-2 as the
  eligible-today alternative, DRS blocked, C-3 frontend-track, and C-5
  maintenance.
- **Document 82** ratified Document 81 as the authoritative Post-M15
  Backend & AI roadmap position — while explicitly **not** selecting M16.
- **Document 83** (Filing Q&A Scope Pre-Decision) evaluated and proposed
  the FQA v1 scope boundary (single-turn + stateless + single-filing),
  recommending **APPROVE**, and named the DRS boundary this scope respects.

Document 84 is the distinct, subsequent act Documents 81 / 82 reserved:
**turning the recommended, scope-bounded direction into a selected
milestone.**

---

## 4. Formal M16 Selection Statement

> **M16 is formally selected as Filing Q&A (FQA v1), constrained to
> single-turn, stateless, single-filing operation as established by
> Document 83.**

The selection is **proposed** here; it becomes effective only on a
separate CTO ratification of this document (§14). Until then, M16's
selection status is **DRAFT / PENDING CTO REVIEW**.

---

## 5. Authoritative Scope (incorporated from Document 83 — preserved exactly, not broadened)

M16 = FQA v1 is bounded by the three Document 83 constraints. Each is
carried forward verbatim in substance; none is reinterpreted or widened.

### 5.1 Single-turn

- one user request;
- one bounded answer;
- no conversational continuation;
- no follow-up turn as part of the v1 feature;
- no thread / session identifier;
- no server-remembered conversational exchange.

A user asking a second question issues a second, independent request. This
document does **not** design the API for this behaviour.

### 5.2 Stateless

FQA v1 is **stateless with respect to durable user / research-session
state.** This does **not** invalidate the existing **AH-2** transient
async-job lifecycle. Preserved as-is (not newly created):

- transient job state where already established;
- process-local result buffering where applicable;
- TTL-bounded operational lifecycle;
- **no durable research-session state.**

**No new persistence is introduced by this selection.**

### 5.3 Single-filing

FQA v1 operates against **one explicitly identified filing**, preserving
the established `(ticker, doc_id)` filing-identity boundary (Documents 59,
64). Explicitly excluded from v1:

- cross-filing joins;
- cross-filing comparisons;
- corpus-wide synthesis;
- multi-filing research;
- portfolio-level research;
- durable research sessions.

This document does **not** decide retrieval mechanics.

---

## 6. DRS Boundary (preserved — not resolved here)

**FQA v1 does not require Durable Research Sessions.** DRS remains BLOCKED
(Document 58 §10; Document 81 §4.DRS).

- A single-turn request establishes no durable research session.
- Stateless operation creates no persistent research state.
- Single-filing scope prevents cross-filing research workflows from
  expanding the feature.
- **Multi-turn continuation, durable conversational state, resumable
  research, or cross-filing research would require separate governance and
  are outside M16 v1 scope.** A conversational FQA specifically would
  require the DRS product decision + ADR + authorized new collection that
  Document 58 §10 requires.

This document does **not** attempt to resolve any future DRS architecture.
The v1 scope boundary is not a permanent architectural prohibition on a
stateful future FQA — that is a matter for a separately governed later
version (Document 83 §6).

---

## 7. Why FQA Is M16 (summary — Documents 81 / 82 / 83 are the basis; no new design)

- **FQA provides meaningful user value beyond the fixed Filing Analysis
  outputs** — users can ask targeted questions of one filing rather than
  only receiving the four fixed M14 outputs, the M15 change brief, or the
  raw text.
- **It is a strong next Backend & AI product direction** — a named line in
  the frozen product roadmap (`docs/master-plan/03_Feature_Roadmap.md` →
  AI Financial Copilot → Filing Q&A) and the natural M12 → M13 → M14 → M15
  continuation.
- **The bounded v1 scope provides useful functionality while controlling
  architectural risk** — single-turn / stateless / single-filing
  forecloses the "Filing Analysis → chatbot" scope-creep vector
  (Document 62 R-1) at the boundary.
- **It can leverage existing filing retrieval / citation / job
  infrastructure** — the out-of-graph async job + SSE + cancel pattern,
  the `doc_id` filing-scope retrieval hook, the deterministic citation
  validator, and the AH-2 result-buffer pattern — **where later contract
  and architecture reviews validate that reuse** (not decided here).
- **It avoids prematurely creating Durable Research Sessions** — no new
  persistence, no per-user history, no session store (§5, §6).
- **It is a more appropriate Backend & AI milestone than C-3**, which
  remains a frontend-track initiative.
- **C-2 remains a legitimate alternative** but is not selected for M16.
- **C-5 remains maintenance**, not a milestone.
- **C-4 / M15 is complete and must not be reopened.**

No quantitative product metric or unsupported claim is asserted.

---

## 8. Alternatives Considered (recorded, not re-decided)

| Candidate | Disposition for M16 |
|---|---|
| **C-2 — Structured Filing-Section Extraction** | **Remains an eligible future Backend & AI candidate** (Document 81 §7). **Not selected for M16.** **Not** characterized as an M14 defect or a remediation requirement — the M14 §20.1 section-location bar passed and remains an accepted ceiling. |
| **C-3 — Financial Visualization** | **Remains primarily frontend-track** and outside M16 Backend & AI selection (Document 58 §9; Document 81 §4.C-3). |
| **C-5 — Governance / maintenance hygiene** | **Remains maintenance work**, not the primary milestone (Document 81 §4.C-5). Includes version-controlling the D67–D83 chain — a separate governance-hygiene activity. |
| **Durable Research Sessions** | **Remains BLOCKED** and outside M16 (Document 58 §10; Document 81 §4.DRS). |
| **C-4 — "What Changed Since Last Review"** | **Already completed as M15** (commit `f8c06649e94f45c388bbecf3eeedb9e5340f2024`; Documents 79 / 80). **Not eligible for reselection.** M15 is not reopened. |

---

## 9. Preserved Constraints (carried forward without reinterpretation)

- **AH-1 remains preserved** — the M15 `report`-mode structured-schema
  resolution, unchanged.
- **AH-2 remains preserved** — the process-local, TTL-bounded, in-process
  job-result buffer; single-backend-process `POST → completion → GET`
  lifecycle; no new MongoDB collection; no Redis or cross-process
  final-result persistence; no cross-process reconstruction; SSE does not
  bypass the invariant.
- **The Document 77 / 78 golden-dataset classification remains preserved**
  — golden-dataset evaluation is evaluation / validation evidence and
  tracked future work, **not** a completion or commit-review gate; not
  reopened.
- **DRS remains blocked.**
- **No durable research-session state** in FQA v1.
- **No cross-filing** in FQA v1.
- **No multi-turn** in FQA v1.
- **M15 remains closed.**

---

## 10. Critical Governance Boundary

**Document 84 selects M16 only.**

**Document 84 does NOT:**

- define the M16 API contract;
- define request / response schemas;
- choose a retrieval strategy;
- choose an LLM / provider / model;
- define prompt architecture;
- define LangGraph usage;
- define MongoDB schema;
- define Redis usage;
- define persistence architecture;
- define a detailed citation schema;
- authorize source-code changes;
- authorize tests beyond later contract / architecture planning;
- authorize evaluation infrastructure;
- authorize deployment;
- authorize release;
- authorize a commit;
- authorize a push.

All of the above require later, separate governance acts (§11, §12).

---

## 11. Future Governance Sequence (expected — none performed here)

```text
 1. CTO review of Document 84
 2. Separate ratification of Document 84
 3. M16 API Contract Proposal
 4. API Contract CTO review / ratification
 5. M16 Architecture Decision Pack
 6. Architecture CTO review / ratification
 7. M16 Implementation Authorization
 8. Implementation
 9. CTO technical review
10. Commit authorization
11. Commit
12. Push authorization
13. Push
14. Post-push review
15. M16 closure
```

Each is a distinct CTO governance act that does not confer the next — the
same uncollapsed ladder Documents 62 §13, 67 §8, and the full M15 chain
(Documents 68 → 80) define. **Document 84 performs none of steps 1–15.**

---

## 12. Open Questions Left for Later Governance (not answered here)

Implementation-stage questions, owed to the M16 API Contract and M16
Architecture Decision Pack (and, where applicable, later implementation):

- API request / response contract;
- retrieval granularity;
- evidence selection;
- citation representation;
- model / provider configuration;
- prompt design;
- structured output format;
- validation behaviour;
- job-kind details;
- timeout / deadline;
- observability;
- rate limiting;
- security boundaries;
- evaluation methodology.

**None of these is answered by Document 84.** Each is deferred to the
named downstream artifact.

---

## 13. Repository / Working-Tree State and Provenance

Recorded by read-only inspection this session on 2026-09-08. **No `git`
mutation was performed** — no `add` / stage, `commit`, `push`, `amend`,
`rebase`, `merge`, `reset`, `restore`, `stash`, or `clean`.

- `HEAD = origin/main = f8c06649e94f45c388bbecf3eeedb9e5340f2024`
  (`f8c0664`, "feat(m15): implement change brief"), ahead/behind `0 / 0`.
- Document number 84 was verified free before creation (highest existing
  Backend & AI governance document was 83).
- **Documents 67–83 were read, not modified.** The M15 chain (Documents
  70 R4 / 72, 73 R1 / 74, 75 / 76, 77 / 78, 79 / 80), the Post-M15
  reconciliation and its ratification (Documents 81 / 82), and the Filing
  Q&A scope pre-decision (Document 83) remain as written and are cited,
  not reinterpreted.
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
  ?? docs/backend_engineering/67_...md through 83_...md            (pre-existing untracked governance documents — not modified)
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/84_M16_Milestone_Selection_Record.md`). It is
  untracked and not yet version-controlled. Staging or committing it is a
  separate, subsequently CTO-authorized step, not performed here.

---

## 14. Decision State / Next Governance Step

**Current state:** 🟡 **DRAFT / PENDING CTO REVIEW — NOT RATIFIED.**

- The M16 selection statement (§4) is **proposed**, not ratified. This
  document does not claim it is already ratified.
- **The next governance step is CTO review and ratification of this
  milestone-selection record.** Only after that would an M16 API Contract
  Proposal be created — a separate CTO-gated act — followed by the M16
  architecture and implementation-authorization artifacts, each subject to
  the FQA v1 scope boundary in §5.

---

**🟡 M16 MILESTONE SELECTION — PROPOSED. DRAFT / PENDING CTO REVIEW. NOT
RATIFIED. THIS DOCUMENT FORMALLY PROPOSES THE SELECTION: M16 = FILING Q&A
(FQA v1), CONSTRAINED TO SINGLE-TURN + STATELESS + SINGLE-FILING OPERATION
EXACTLY AS ESTABLISHED BY DOCUMENT 83 — ONE REQUEST, ONE BOUNDED ANSWER,
NO CONVERSATIONAL CONTINUATION, NO THREAD / SESSION IDENTIFIER, NO
SERVER-REMEMBERED EXCHANGE; STATELESS WITH RESPECT TO DURABLE USER /
RESEARCH-SESSION STATE WHILE THE EXISTING AH-2 TRANSIENT ASYNC-JOB
LIFECYCLE (TRANSIENT JOB STATE, PROCESS-LOCAL RESULT BUFFERING,
TTL-BOUNDED LIFECYCLE) IS PRESERVED AND NO NEW PERSISTENCE IS INTRODUCED;
AND OPERATING AGAINST ONE EXPLICITLY IDENTIFIED FILING VIA THE ESTABLISHED
`(ticker, doc_id)` IDENTITY, WITH CROSS-FILING JOINS / COMPARISONS /
CORPUS-WIDE SYNTHESIS / MULTI-FILING / PORTFOLIO-LEVEL RESEARCH / DURABLE
RESEARCH SESSIONS ALL EXCLUDED FROM v1. FQA v1 DOES NOT REQUIRE DURABLE
RESEARCH SESSIONS; MULTI-TURN CONTINUATION, DURABLE CONVERSATIONAL STATE,
RESUMABLE RESEARCH, OR CROSS-FILING RESEARCH WOULD REQUIRE SEPARATE
GOVERNANCE AND ARE OUTSIDE M16 v1 SCOPE — THIS IS A v1 SCOPE DECISION, NOT
A PERMANENT ARCHITECTURAL PROHIBITION, AND NO FUTURE DRS ARCHITECTURE IS
RESOLVED HERE. FQA WAS SELECTED OVER C-2 (WHICH REMAINS AN ELIGIBLE FUTURE
BACKEND & AI CANDIDATE, NOT AN M14 DEFECT OR REMEDIATION REQUIREMENT),
C-3 (WHICH REMAINS FRONTEND-TRACK), C-5 (WHICH REMAINS MAINTENANCE), AND
DRS (WHICH REMAINS BLOCKED); C-4 / M15 IS COMPLETE AND NOT ELIGIBLE FOR
RESELECTION AND IS NOT REOPENED. AH-1 AND AH-2 REMAIN PRESERVED; THE
DOCUMENT 77 / 78 GOLDEN-DATASET CLASSIFICATION REMAINS PRESERVED; M15
REMAINS CLOSED. DOCUMENT 84 SELECTS M16 ONLY — IT DOES NOT DEFINE THE M16
API CONTRACT, REQUEST / RESPONSE SCHEMAS, RETRIEVAL STRATEGY,
LLM / PROVIDER / MODEL, PROMPT ARCHITECTURE, LANGGRAPH USAGE, MONGODB
SCHEMA, REDIS USAGE, PERSISTENCE ARCHITECTURE, OR CITATION SCHEMA, AND
AUTHORIZES NO SOURCE-CODE CHANGE, NO TESTS BEYOND LATER CONTRACT /
ARCHITECTURE PLANNING, NO EVALUATION INFRASTRUCTURE, NO DEPLOYMENT, NO
RELEASE, NO COMMIT, AND NO PUSH. DOCUMENTS 67–83 WERE READ, NOT MODIFIED.
NO SOURCE, TEST, OR CONFIGURATION FILE WAS CREATED OR MODIFIED. NO STAGE.
NO COMMIT. NO PUSH. NO MERGE / REBASE / RESET / AMEND. THE NEXT GOVERNANCE
STEP IS CTO REVIEW AND RATIFICATION OF THIS MILESTONE-SELECTION RECORD,
FOLLOWED BY A SEPARATE M16 API CONTRACT PROPOSAL.**
