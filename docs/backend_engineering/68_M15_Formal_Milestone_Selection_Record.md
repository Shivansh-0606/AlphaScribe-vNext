# 68 — M15 Formal Milestone Selection Record

**Status:** 🟢 **M15 MILESTONE FORMALLY SELECTED — M15 = C-4 "WHAT CHANGED
SINCE LAST REVIEW."** This document records a **separate CTO
milestone-selection decision**, taken subsequent to and **distinct from**
the CTO ratification of
[67_Post_M14_Backend_AI_Roadmap_Reconciliation.md](67_Post_M14_Backend_AI_Roadmap_Reconciliation.md).
It performs the "formal M15 milestone selection" gate that Document 67 §8 /
§14.3 explicitly reserved as its own subsequent CTO act. **Selecting the
milestone authorizes progression to the contract-governance stage only. It
authorizes no contract, no architecture, no source/test/schema/
infrastructure change, no RAG, no persistence, no LangGraph change, no
implementation, no commit, and no push** — see §5, §7, §8.

**Type:** Governance / milestone-selection decision record (documentation
only — no source code, test, schema, API route, migration, index,
configuration, infrastructure, LangGraph topology, MongoDB
collection/schema, Redis, provider, RAG, G8, H-1, or Gate state created or
modified to produce this record; Documents 62–67 read, not modified. The
only file this task creates is this document.

**Date:** 2026-09-04.

**Precedent / lineage.** This record follows the exact genre and role of
[63_M14_Formal_Milestone_Selection_Record.md](63_M14_Formal_Milestone_Selection_Record.md)
— the CTO ratification of the preceding Post-M{N} roadmap reconciliation
(there, Document 62; here, Document 67) established a **preferred / recommended
direction**; formal milestone selection is deliberately **un-folded** as its
own distinct, subsequent CTO act. This record is that act for M15, written
in the same short standalone decision-record form as
[54_M10_Governance_Authorization_Reconciliation_Record.md](54_M10_Governance_Authorization_Reconciliation_Record.md),
[56_M12_Governance_Authorization_Reconciliation_Record.md](56_M12_Governance_Authorization_Reconciliation_Record.md),
[61_M13_Governance_Authorization_Reconciliation_Record.md](61_M13_Governance_Authorization_Reconciliation_Record.md),
and
[63_M14_Formal_Milestone_Selection_Record.md](63_M14_Formal_Milestone_Selection_Record.md).
None of those precedents is modified by this document.

---

## 0. What This Document Is and Is Not

**Is:** a record of one CTO governance decision — the formal selection of
C-4 "What Changed Since Last Review" as the M15 milestone — plus a precise
statement of the governance state that selection creates and the gates that
still stand between M15 and implementation.

**Is not:** a contract, an API contract proposal, an architecture decision
pack, a scope freeze, an implementation authorization, a commit
authorization, a push authorization, an amendment to any frozen or
historical document, a reopening of M14, or a reopening of H-1 / G8. It
resolves **none** of C-4's open design questions — the reference /
comparison-semantics question, the meaning and breadth of "changed," and
every other item Document 67 §4 (C-4) / §10 left open stay exactly as open
as Document 67 left them (§6 below). It creates no endpoint, no schema, no
index, no migration, no test, no LangGraph node, no `window.claude`-style
runtime, and introduces no dependency.

---

## 1. Governance Position (this record's place in the ladder)

```text
M14
  ↓
CLOSED / PUBLISHED                        (be4949b; §2)
  ↓
DOC 67                                    (Post-M14 Backend & AI Roadmap Reconciliation; §3)
  ↓
CTO-RATIFIED                              (2026-09-03, Document 67 §14)
  ↓
C-4 RECOMMENDED                           (preferred next Backend & AI direction, NOT yet M15; §3, §4)
  ↓
FORMAL M15 SELECTION                      ← THIS DOCUMENT (68)
  ↓
🟢 M15 = C-4 — WHAT CHANGED SINCE LAST REVIEW   (§4)
  ↓
STOP                                      (§7 — no downstream gate is authorized by this record)
  ↓
M15 API CONTRACT                          (next authorized governance activity — NOT created here; §8)
  ↓
M15 ARCHITECTURE                          (NOT created here; §8)
  ↓
IMPLEMENTATION AUTHORIZATION              (its own separate, scope-bound CTO act — NOT this document; §8)
```

None of these stages is collapsed or skipped by this record.

---

## 2. M14 Baseline (established, not reopened)

M14 Filing Analysis is **CLOSED / PUBLISHED**. This record does not reopen
it; the following is restated so this record is self-contained, exactly as
Document 67 §2 established it:

```text
M14 (Filing Analysis)                     COMPLETE / VALIDATED (§20.1 PASS) / IMPLEMENTATION-AUTHORIZED (Doc 66 §18) /
                                           COMMITTED (be4949b) / PUSHED / post-push verified — CLOSED / PUBLISHED
Delivered commit                          be4949b (be4949b5b33ea73cfedf81c03bebbdaa953772b8)
Document 64 (M14 API Contract)            🟢 CTO-RATIFIED / FROZEN (2026-08-31) — remains the ratified M14 contract
Document 65 (M14 Architecture Pack)       🟢 CTO-RATIFIED / FROZEN (2026-08-31, §27) — remains the ratified M14 architecture decision pack
Document 66 (M14 Impl. Auth. Proposal)    🟢 §18 IMPLEMENTATION AUTHORIZED (2026-09-02) — remains the implementation authorization record
§20.1 OAQ-1(D) validation gate            PASSED (0 false positives / 0 false negatives; byte-identical over N=5) — Document 65 §27.2/§27.3; evidence in
                                           backend/evaluation/m14_section_location_spike/latest.md
```

**M14's accepted architectural ceilings remain ceilings, not defects
requiring automatic remediation.** Fallback-C persistence (process-local),
the bounded N=5 / 4-filing §20.1 corpus (not a universal
section-detection claim), and the one honest MSFT MD&A partial-boundary
case are unchanged, accepted limits — Document 67 §2.3 restated this and
this record restates it again, unmodified. **No M14 artifact, no M14 source,
and no M14 evidence is touched, re-evaluated, or reopened by this record.**

---

## 3. Document 67 Authority

- **Document 67 is the authoritative Post-M14 Backend & AI Roadmap
  Reconciliation.** It is 🟢 CTO-RATIFIED (2026-09-03, its §14) as the
  authoritative Post-M14 Backend & AI roadmap position.
- **Document 67 identified C-4 "What Changed Since Last Review" as the
  strongest eligible Backend & AI candidate** — the only candidate
  favourable or neutral on every one of its seven explicit comparison
  criteria (Document 67 §5), favourable on both decisive gates (a named
  frozen-MVP roadmap line; free of any governance block or missing
  prerequisite decision), and recommended as the next Backend & AI
  direction (Document 67 §7).
- **Document 67 intentionally did not itself select M15.** Its own header,
  §7, §9, §14.1, and §14.3 state this in terms: ratification "does **not**
  constitute formal M15 milestone selection"; "C-4 remains the recommended
  candidate / direction and does not become M15 through this ratification
  alone"; "Formal M15 selection remains a separate CTO governance decision."
- **This record performs that separate, subsequent formal M15 selection.**
  It consumes the "Formal M15 Selection" step named in Document 67 §8's
  governance-sequence diagram and §14.5's identical rendering, and it does
  not touch, reinterpret, re-ratify, or amend Document 67 — Document 67 is
  cited here, not edited.

**The distinction is preserved exactly as required:** *Document 67
recommended C-4; this record selects C-4 as M15.* Recommendation and
selection remain two distinct governance acts, as they were for M14
(Document 62 recommended C-1; Document 63 selected C-1 as M14).

---

## 4. Formal M15 Decision

**🟢 M15 — SELECTED.**

**M15 = C-4 — "What Changed Since Last Review."**

A grounded change brief for a single company against a prior reference
point, drawing on data the platform may already have on hand for that
purpose — prior `reports`, the M12 multi-period `financial_statements`, and
optionally M14 filing analyses — is hereby **formally selected as the M15
milestone**. Which of these inputs is actually used, how the comparison
point is identified, and whether any new persistence is introduced remain
undecided here and are governed by the M15 contract and architecture
phases (§6).
This advances C-4 from the "recommended next Backend & AI direction" status
established by Document 67 to "formally selected milestone," and thereby
opens the M15 **contract-governance stage**. It does nothing else. C-4's
substance, scope, exclusions, and every open design question are **unchanged
from Document 67 §4 (C-4) / §6 (candidate dispositions) / §10 (open
decisions)** — see §6 below.

**Basis for selection (restated from Document 67's existing record; no new
rationale introduced):**

1. **Named line in the frozen product roadmap.** C-4 is a named line in the
   🧊 Frozen `docs/master-plan/03_Feature_Roadmap.md` — "Company Research →
   What Changed Since Last Review" (Document 67 §7, criterion K1).
2. **Free of any governance block or missing prerequisite decision** needed
   to *begin* the contract phase (Document 67 §7, criterion K2) — unlike
   Durable Research Sessions (BLOCKED) or Filing Q&A (needs a prior
   product-scope decision).
3. **An eligible Backend & AI milestone** (Document 67 §7, criterion K3) —
   unlike C-3, which Document 58 §9 / Document 62 §6 / Document 67 §4
   classify as a frontend-track initiative.
4. **Heavy reuse of hardened infrastructure with no forced new persistence**
   in its minimal form (Document 67 §7, criteria K4/K7) — the `reports`
   collection, the M12 `financials.periods[]` series, the M9.1
   comparison-explanation diff pattern, and the M14 out-of-graph
   async-job + deterministic-citation pattern, following the M14
   fallback-C precedent.
5. **Direct continuation of the M12 → M13 → M14 application-capability
   track**, with real standalone user value (retention / repeat
   engagement) rather than an infrastructure-only or navigation-only
   capability (Document 67 §5's comparison of C-4 against C-2).

This selection **decides nothing** about C-4's design. It is a milestone
identity decision, not a scope, contract, or architecture decision.

---

## 5. Candidate Dispositions (preserved from Document 67, not reinterpreted)

### C-2 — Structured Filing-Section Extraction

- **Not selected for M15.**
- **Remains a legitimate future candidate** (Document 67 §4.C-2, §6) — the
  credible eligible Backend & AI alternative to C-4 if the CTO later elects
  to pay down section-representation infrastructure debt.
- **M14 §20.1 passed** (§2 above; Document 65 §27.2/§27.3).
- **Therefore C-2 is not being promoted as M14 remediation.** A §20.1
  **PASS** does not select, trigger, or require C-2; this record does not
  reinterpret that governance fact. C-2's disposition is unchanged from
  Document 67 §4.C-2 / §6.

### C-3 — Financial Visualization

- **A frontend / product-track candidate — not a Backend & AI M15
  milestone.** Unchanged from Document 58 §9, Document 62 §6 C-3, and
  Document 67 §4.C-3 / §6 (criterion K3: "not a Backend & AI milestone").
  It may proceed under frontend governance independently of this record.

### Filing Q&A

- **Remains separately scoped.** Named as a "later, separately scoped
  capability" that M14 establishes the foundation for (Document 62 §6
  C-1(2); Document 64 §4; Document 67 §3.FQA).
- **Not included in M15 by this selection record.** It is gated on a prior
  CTO / product scope decision (single-turn structured vs. multi-turn
  conversational — Document 67 §4.FQA, §6) that has not been made. Its
  disposition is unchanged: a future candidate, not this milestone.

### Durable Research Sessions

- **Remains BLOCKED.** Document 58 §10 / Document 62 §6 C-4(5) / Document 67
  §4.DRS: ineligible as a milestone until the CTO issues the product
  decision **and** the ADR **and** authorizes the new collection that
  Document 58 §10 requires. None of those three exists. This record does
  **not** unblock it.
- **Must not be smuggled into C-4 through implicit user/session
  persistence.** This is restated as a binding constraint on the
  downstream M15 contract / architecture phases, exactly as Document 67
  §4.C-4 / §7 / OD-4 already required: C-4's reference point must not
  resolve to a durable per-user session/history store, a new "sessions"
  collection, or a watchlist. Document 62 §6 C-4(8)'s exclusion list ("no
  durable sessions … no new collection … no watchlist") governs and is
  carried forward unchanged.

### C-5 — Governance Hygiene

- **Remains governance maintenance / parallel work — not selected as the
  Backend & AI product milestone.** Unchanged from Document 62 §6 C-5 and
  Document 67 §4.C-5 / §6 / §8. The stale-register items it names
  (`00_README.md`, `planning/07-Roadmap-Milestones.md`, Document 58 §28)
  are unaffected by this selection and remain open per Document 67 §10
  (OD-11, OD-12).

---

## 6. C-4 Scope Boundary — Open Questions (preserved, not resolved)

This record **does not design C-4**. Every open question Document 67 §4.C-4
and §10 (OD-2 through OD-7) surfaced remains open and is **not** answered
here. It is restated so this record is self-contained:

| Open area | Status after this selection |
|---|---|
| **Reference / comparison semantics** | **Unresolved.** Document 67 §4.C-4 distinguished four possible semantics — (1) a prior research artifact, (2) a prior reporting period, (3) an explicitly selected comparison point, (4) durable user/session state — and found the existing material points toward (1)–(3) and **away from** (4), without conclusively fixing which of (1)–(3) is intended. **This record does not resolve this.** In particular, this record does **not** redefine C-4 as "changes since this user's last visit" — no existing authoritative document defines it that way; the phrase in Document 62 §6 C-4(1) ("since last time") is informal framing, not a ratified definition, and is contradicted by that same candidate's own exclusion list (§6 C-4(8), Document 67 D-4). This is **OD-2 — CTO/product decision required**, owed to the M15 contract phase. |
| **Meaning and breadth of "changed"** | **Unresolved** — financials-only, narrative-only, or both (Document 62 §6 C-4(6); Document 67 OD-3). Owed to the M15 contract. |
| **Comparison inputs** | **Unresolved** in detail — `reports`, `financial_statements.periods[]`, and optionally M14 filing analyses are the identified *candidate* inputs (Document 67 §4.C-4), not a fixed input set. |
| **State semantics** | **Unresolved** — whether M15 reuses the `complete` / `partial` / `insufficient_evidence` vocabulary verbatim, and how, is an M15 contract decision. Not assumed here. |
| **Persistence** | **Unresolved (OD-5)** — on-demand (M14 fallback-C precedent) vs. a durable store (which would trigger the `08_MongoDB_Data_Architecture.md` + ADR chain and the "no new collection" scrutiny). Not decided here. |
| **Retrieval** | **Unresolved (OD-6)** — Document 67 §4.C-4 judged retrieval "likely not required" but left it an architecture-phase decision, not an assumption. |
| **Validation** | **Unresolved (OD-7)** — whether a §20.1-style validation gate applies to change-detection quality is an architecture-phase decision. |
| **Output contract** | **Unresolved** — envelope shape, citation representation, error taxonomy reuse: all owed to the M15 API Contract (§8). |
| **Error behavior** | **Unresolved** — no error semantics are defined by this record; the existing Document 43 §3 / `domain/errors.py` taxonomy reuse discipline is the only constraint carried forward (no new error types absent a demonstrated need, per every prior contract's convention). |
| **Orchestration** | **Unresolved** — whether M15 follows the out-of-graph async-job pattern (M9.1 / M14 precedent) is the expected shape per Document 67 §4.C-4, but the M15 architecture decision pack makes this decision, not this record. |

A legitimate outcome of the M15 contract / architecture phase is a decision
that narrows, splits, or re-bounds C-4 based on these open questions. This
record selects the **milestone identity**, not its design.

---

## 7. Explicit Non-Authorization

**Formal M15 selection does NOT authorize:**

- M15 API contract implementation or ratification;
- M15 architecture implementation or ratification;
- production code;
- tests;
- MongoDB schema, collection, index, or migration realization;
- Redis changes;
- LangGraph changes;
- retrieval redesign;
- frontend implementation;
- implementation authorization;
- commit;
- push;
- merge;
- deployment;
- release.

To be precise:

> **Selection of M15 authorizes progression to the contract-governance
> stage. It does not authorize implementation.** The next gate after this
> record is the **M15 API Contract** — not implementation.

No code, test, schema, index, migration, configuration, infrastructure,
LangGraph, MongoDB, or Redis change is authorized by this record. The M15
contract proposal, its ratification, the M15 architecture decision pack,
its ratification, and a separate implementation-authorization decision must
all occur — in that order, each a distinct CTO act — before any C-4 source
code may be written (§1, §8).

---

## 8. Downstream Governance

**The next authorized governance activity is preparation of the M15
contract proposal** — a new "M15 … API Contract" artifact — subject to the
project's normal governance process (`docs/governance/` change-request and
ratification chain, mirroring how Documents 64 / 65 were produced and
ratified for M14).

**The governance ladder is preserved and not collapsed:**

```text
Roadmap reconciliation
≠
Milestone selection
≠
API contract
≠
Architecture
≠
Implementation authorization
≠
Implementation
≠
Review
≠
Commit authorization
≠
Push authorization
```

Each stage is a distinct CTO act; none confers the next. This record
performs exactly one stage: **Milestone selection.**

The frontend track (C-3 Financial Visualization) and the governance-hygiene
track (C-5) remain independent of this milestone selection, exactly as
Document 67 §8 records.

---

## 9. Existing Governance State (preserved, unchanged)

This decision changes none of the following. They are restated so this
record is self-contained:

```text
M14 (Filing Analysis)             CLOSED / PUBLISHED (be4949b) — unchanged
Document 64 (M14 API Contract)    🟢 CTO-RATIFIED / FROZEN — read, not modified
Document 65 (M14 Architecture)    🟢 CTO-RATIFIED / FROZEN — read, not modified
Document 66 (M14 Impl. Auth.)     🟢 §18 IMPLEMENTATION AUTHORIZED — read, not modified
Document 67 (Post-M14 Reconc.)    🟢 CTO-RATIFIED (2026-09-03) — read, not modified; cited as the basis for this decision
C-2 Structured Filing Extraction  FUTURE CANDIDATE — not selected, not rejected, not promoted as M14 remediation (§5)
C-3 Financial Visualization       FRONTEND / PRODUCT TRACK — not a Backend & AI milestone (§5)
Filing Q&A                        SEPARATELY SCOPED — not included in M15 (§5)
Durable Research Sessions         BLOCKED — unchanged (§5)
C-5 Governance Hygiene            GOVERNANCE MAINTENANCE — not a product milestone (§5)
G8                                 BLOCKED / CARRIED FORWARD — unchanged
H-1                                CLOSED WITH GOVERNANCE FOLLOW-UP — unchanged
Gate (JUDGE_SELF_CONSISTENCY_GATE_VERSION)   0 — unchanged
G7                                 NO ARCHITECTURE CHANGE — unchanged
```

Neither H-1 nor G8 blocks, gates, or drives M15. Both remain standing debt
the CTO may separately choose to address; neither is reopened here.

---

## 10. Repository / Working-Tree State

Recorded by read-only `git` inspection this session. **This is a
point-in-time snapshot observed during the creation of this record on
2026-09-04**, not a claim about repository state at any later reading time.
**No `git` mutation was performed** — no `add` / stage, no `commit`, no
`push`, no `amend`, no `rebase`, no `merge`, no `reset`, no `stash`, no
`clean`.

- **M14 publication state is synchronized:** `HEAD` = `origin/main` =
  `be4949b5b33ea73cfedf81c03bebbdaa953772b8`. The M14 implementation commit
  `be4949b` is unchanged and was not inspected in a way that could alter it.
- **No conflicting M15 selection record existed prior to this task** —
  verified by inspecting `docs/backend_engineering/` (highest prior document
  number: 67) and by a repository-wide search for an existing M15 selection
  reference (none found).
- **The working tree is NOT Git-clean.** It contains known, pre-existing,
  unrelated changes and artifacts that this document does **not** stage,
  modify, rename, delete, or clean:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated test-flake hardening — H-2)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/   (untracked — M11 Phase H-1 evidence)
  ?? docs/backend_engineering/67_Post_M14_Backend_AI_Roadmap_Reconciliation.md   (untracked; committing it is a separate CTO-authorized step)
  ```

- **This document adds one further untracked file — itself**
  (`docs/backend_engineering/68_M15_Formal_Milestone_Selection_Record.md`).
  It is **untracked and not yet version-controlled.** Committing it is a
  separate, subsequently CTO-authorized step (the model Document 63's
  eventual commit, and the M14 chain's `be4949b`, followed).

---

## 11. Provenance and Constraints Honoured

- Created: 2026-09-04. Sole new file:
  `docs/backend_engineering/68_M15_Formal_Milestone_Selection_Record.md`.
  Document number 68 was verified free before creation (highest existing
  Backend & AI governance document was 67).
- No source code, test, schema, index, migration, configuration, or
  infrastructure file was created or modified. No LangGraph topology,
  MongoDB collection/schema, or Redis state was touched. No dependency was
  introduced. No RAG or provider work was performed. No frontend file was
  touched. `.gitignore` was not modified.
- **Documents 62–67 were read, not modified.** Document 67 remains
  🟢 CTO-RATIFIED and is cited, not restated as a new interpretation.
  Documents 64, 65, and 66 remain unmodified and unreopened. No frozen or
  historical governance record was rewritten; the decision is recorded in
  this new artifact instead.
- The M14 implementation commit `be4949b` was not altered. Nothing was
  staged, committed, or pushed.
- No date, timestamp, decision number, or authorization wording was
  fabricated. No retroactive authorization is claimed. No prior governance
  decision is re-interpreted or duplicated — Document 67 is cited, not
  restated as a new interpretation. No new rationale unsupported by the
  existing governance record was introduced for the §4 decision.
- Known unrelated working-tree items
  (`web/features/workspace-home/ui/CompanySearch.test.tsx`;
  `backend/evaluation/self_consistency/phase_h1_generalization_matrix/`)
  were not staged, modified, renamed, or deleted.

---

**M15 IS FORMALLY SELECTED = C-4 "WHAT CHANGED SINCE LAST REVIEW." THIS IS A
SEPARATE CTO MILESTONE-SELECTION DECISION, DISTINCT FROM THE CTO RATIFICATION
OF DOCUMENT 67. DOCUMENT 67 RECOMMENDED C-4; THIS RECORD SELECTS C-4 AS M15.
NO M15 CONTRACT PROPOSED OR RATIFIED. NO M15 ARCHITECTURE PROPOSED OR
RATIFIED. NO IMPLEMENTATION, COMMIT, PUSH, MERGE, OR DEPLOYMENT AUTHORIZATION
GRANTED. NO C-4 DESIGN DECISION IS MADE HERE — REFERENCE/COMPARISON
SEMANTICS, THE MEANING AND BREADTH OF "CHANGED," COMPARISON INPUTS, STATE
SEMANTICS, PERSISTENCE, RETRIEVAL, VALIDATION, OUTPUT CONTRACT, ERROR
BEHAVIOR, AND ORCHESTRATION ALL REMAIN OPEN, OWED TO THE M15 CONTRACT /
ARCHITECTURE PHASES. C-4 IS NOT REDEFINED AS "CHANGES SINCE THIS USER'S LAST
VISIT." C-2 STRUCTURED FILING EXTRACTION REMAINS A FUTURE CANDIDATE, NOT
SELECTED, NOT REJECTED, AND NOT PROMOTED AS M14 REMEDIATION — THE §20.1 BAR
PASSED. C-3 FINANCIAL VISUALIZATION REMAINS A FRONTEND / PRODUCT-TRACK
CANDIDATE, NOT A BACKEND & AI MILESTONE. FILING Q&A REMAINS SEPARATELY
SCOPED AND IS NOT INCLUDED IN M15. DURABLE RESEARCH SESSIONS REMAINS BLOCKED
AND MUST NOT BE SMUGGLED INTO C-4 THROUGH IMPLICIT USER/SESSION PERSISTENCE.
C-5 GOVERNANCE HYGIENE REMAINS GOVERNANCE MAINTENANCE, NOT A PRODUCT
MILESTONE. G8 REMAINS BLOCKED / CARRIED FORWARD. H-1 REMAINS CLOSED WITH
GOVERNANCE FOLLOW-UP. M14 REMAINS CLOSED / PUBLISHED AND IS NOT REOPENED.
DOCUMENTS 62–67 NOT MODIFIED. NO SOURCE, TEST, SCHEMA, OR INFRASTRUCTURE
FILE CREATED OR MODIFIED. NO STAGE. NO COMMIT. NO PUSH. NO MERGE / REBASE /
RESET / AMEND. THE NEXT AUTHORIZED GOVERNANCE ACTIVITY IS PREPARATION OF THE
M15 API CONTRACT, SUBJECT TO THE NORMAL GOVERNANCE PROCESS; SELECTION
AUTHORIZES PROGRESSION TO THE CONTRACT-GOVERNANCE STAGE ONLY, NOT
IMPLEMENTATION.**
