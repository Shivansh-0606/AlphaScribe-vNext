# 72 — Document 70 Revision R4 CTO Ratification Record

**Status:** 🟢 **DOCUMENT 70, REVISION R4 — CTO RATIFIED / ACCEPTED.** This
document records the CTO's ratification of
[70_M15_What_Changed_API_Contract_Proposal.md](70_M15_What_Changed_API_Contract_Proposal.md)
**at Revision R4** — the latest, and only, artifact present in the
repository. It is a **separate governance act**, distinct from Document 70
itself: it ratifies the contract position Document 70 already recorded — it
does not perform the proposal (Document 70 already did that), it does not
redesign C-4, and it is **not** a reinterpretation of
[71_Document70_CTO_Ratification_Record.md](71_Document70_CTO_Ratification_Record.md)
as having ratified anything. **The ratified decision is: the Document 70
API contract, Revision R4, is the ratified M15 = C-4 — "What Changed Since
Last Review" — API contract.** Ratification authorizes progression to the
**M15 Architecture Decision Pack** gate only — see §8, §9.

**Type:** Governance / ratification decision record (documentation only —
no source code, test, schema, API route, migration, index, configuration,
infrastructure, LangGraph topology, MongoDB collection/schema, Redis,
provider, RAG, or architecture artifact created or modified to produce this
record; Document 70 and Documents 67–69, 71 read, not modified. The only
file this task creates is this document.

**Date:** 2026-09-06.

**Precedent / lineage.** This record follows the same standalone
decision-record form
[69_Document68_CTO_Ratification_Record.md](69_Document68_CTO_Ratification_Record.md)
established for ratifying a prior document without modifying it. It is the
**second** attempt at a Document 70 ratification record:
[71_Document70_CTO_Ratification_Record.md](71_Document70_CTO_Ratification_Record.md)
recorded the **first** attempt, which found Document 70's own
governance-status markers self-contradictory and therefore did **not**
ratify it (§4 below restates that history). Document 71 is **not**
superseded, retracted, or rewritten by this record — it remains the
accurate historical account of that blocked review. This record is the
**distinct, subsequent ratification act** performed now that Document 70's
markers have been corrected to a single, consistent state.

---

## 1. Document Metadata

| Field | Value |
|---|---|
| Document number | 72 |
| Title | Document 70 Revision R4 CTO Ratification Record |
| Ratifies | Document 70 — M15 API Contract Proposal — C-4 "What Changed Since Last Review" |
| Ratified revision | **Revision R4** (exact — no later revision exists or is claimed) |
| Milestone | M15 = C-4 (Document 68 §4; Document 69 §2) |
| Governance stage | API contract ratification (this act) |
| Predecessor gate | Document 70 R4, corrected to "CTO-reviewed, approved for ratification, not yet ratified" |
| Related prior record | Document 71 — blocked ratification review (historical; not modified, not superseded) |
| Successor gate (not created here) | M15 Architecture Decision Pack |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Ratification Target and Exact Revision

**Target: Document 70 — M15 API Contract Proposal — C-4 "What Changed
Since Last Review," Revision R4.**

Verified this session, read-only, before recording this ratification:

- Document 70's top-line Status banner (line 3) and closing ALL-CAPS block
  (final paragraph) both now read: *"🟡 M15 API CONTRACT PROPOSAL —
  CTO-REVIEWED, APPROVED FOR RATIFICATION, NOT YET RATIFIED (REVISION
  R4)."*
- Document 70's §1 Governance-stage row, §2 governance-ladder diagram, §3
  preconditions table, and roadmap-position paragraph all agree with the
  banner — **all current governance markers state the same thing**:
  CTO-reviewed, approved for ratification, not yet ratified, Revision R4.
- Document 70's header carries exactly four revision-note blocks: R1, R2,
  R3, R4. **No `Revision R5` block exists anywhere in the file.**
- `docs/backend_engineering/` was listed in full: the highest-numbered file
  prior to this task was `71_Document70_CTO_Ratification_Record.md`. No
  second Document-70-shaped file, and no Document 70 revision beyond R4,
  exists anywhere in the repository.
- `git status --short` and `git log` show Document 70 as untracked (never
  committed) — there is no commit history suggesting a superseding
  revision was ever pushed elsewhere.

**No discrepancy was found. Revision R4 is confirmed as the correct and
only ratification target. This record ratifies Revision R4 exactly, and
makes no claim about, and does not ratify, any revision beyond R4.** If a
Revision R5 is later introduced, it requires its own, separate CTO review
and ratification; this record does not, and cannot, extend to it.

---

## 3. Governance History / Provenance

| Document | Role | Governance act performed |
|---|---|---|
| **Document 67** | Post-M14 Backend & AI Roadmap Reconciliation | **Recommendation.** CTO-ratified (2026-09-03); identified C-4 as the strongest recommended direction for the next Backend & AI milestone. |
| **Document 68** | Formal M15 Milestone Selection Record | **Selection.** Formally selected **M15 = C-4 — "What Changed Since Last Review."** |
| **Document 69** | Document 68 CTO Ratification Record | **Selection ratification.** Ratified the M15 milestone selection recorded in Document 68. |
| **Document 70 (R1→R4)** | M15 API Contract Proposal | **Contract proposal.** Defines the proposed externally observable API contract for C-4, revised through four CTO-directed correction passes to R4, then corrected for an internal governance-status contradiction. |
| **Document 71** | Document 70 CTO Ratification Review | **Blocked ratification review (historical).** Found Document 70's governance-status markers self-contradictory; did not ratify. Restated in §4 below; not modified, not superseded, not reinterpreted as a ratification. |
| **Document 72 (THIS)** | Document 70 Revision R4 CTO Ratification Record | **Contract ratification.** The distinct, subsequent act that ratifies Document 70 at Revision R4, now that its governance-status markers are corrected and consistent. |

These six roles are not interchangeable and this record does not conflate
them.

---

## 4. Prior Blocked Review and Subsequent Correction

Document 71 recorded a CTO ratification **review** of Document 70 at
Revision R4 that did **not** conclude in ratification: Document 70's
canonical Status banner and closing block read "DRAFT / PENDING CTO
REVIEW," while its roadmap-position paragraph and §1 Governance-stage row
read "CTO-reviewed... approved for ratification" — a direct, internal
contradiction Document 71 declined to paper over. Document 71 explicitly
stated the required next step: correcting Document 70's own status
wording, in a separate, subsequent task, before any ratification record
could rely on "CTO-reviewed" as a precondition.

That correction has since been made **directly to Document 70** (not to
Document 71) — a minimal, mechanical edit to Document 70's status banner,
closing block, §2 governance-ladder diagram, and §3 preconditions table, so
that all of Document 70's governance-status markers now consistently state:
**CTO-reviewed, approved for ratification, not yet ratified (Revision
R4).** Verification this session (§2 above) confirms that correction was
applied, is now internally consistent throughout Document 70, and did not
alter any substantive API-contract semantics — the correction touched only
governance-status wording.

**Document 71 is not modified, retracted, or reinterpreted by this
fact.** It remains the accurate historical record of the blocked review
that identified the problem. This record (Document 72) is the **separate,
subsequent ratification act** that Document 71 itself said would still be
required once the correction existed.

---

## 5. CTO Ratification Decision

**🟢 DOCUMENT 70, REVISION R4 — CTO RATIFIED / ACCEPTED.**

The CTO has reviewed Document 70 at Revision R4, confirmed its
governance-status markers now agree, confirmed the status correction did
not alter substantive API-contract semantics, and issued: **🟢 DOCUMENT 70
REVISION R4 — RATIFIED.** This document records that ratification.

**The ratified decision is: the Document 70 API contract, Revision R4, is
the ratified M15 = C-4 — "What Changed Since Last Review" — API
contract.**

**This ratification is of the API contract — not of the architecture, and
not of implementation.** It does not re-derive, redesign, or extend the
contract, and it does not authorize M15 architecture or implementation
(§8).

---

## 6. Ratified Contract Scope (preserved in substance from Document 70, Revision R4 — not invented or modified here)

### 6.1 Comparison modes

- **`period` mode** → financial period-to-period changes, producing
  `"financial"`-category items only.
- **`report` mode** → report-to-report narrative changes, producing
  `"narrative"`-category items only.
- The two modes are **mutually exclusive**; a single request evaluates
  **exactly one** mode; the two item categories never appear together in
  one response. **No combined- or mixed-mode request exists.** **No third,
  filing-to-filing mode exists in v1** (OCD-1 — explicitly deferred, not
  adopted).

### 6.2 Financial comparison (`period` mode)

- **Metric identity** uses the existing `Metric.provider_label` — exact
  string-equality matching only. **No invented canonical metric mapping**
  is introduced; `Metric.canonical_metric` remains `null` for every metric
  today, and provider relabeling across periods remains a documented
  limitation (observed as one removed metric plus one newly-appearing
  metric), not silently smoothed over.
- **Eligibility rule**: any nonzero delta, or any appearing/disappearing
  metric, qualifies — mechanical and deterministic, with no invented
  materiality threshold and **no arbitrary materiality label introduced**
  (a possible future `significance` label is OCD-2, distinct from OCD-6's
  possible future magnitude filter — neither adopted).
- **Financial citation shape** — `{index, statement_type, period_end,
  metric}` — retained exactly as defined: self-evidencing, no model
  involved; a `changed` item cites both statement sides, a `new` item cites
  `current` only, a `removed` item cites `baseline` only.

### 6.3 Narrative comparison (`report` mode)

- Baseline/current report comparison, reusing
  `agents/comparison_explanation.py`'s existing grounding and
  citation-validation logic without modification to how a claim is
  grounded.
- **Eligibility rule** (non-numeric, no materiality threshold): a
  substantive semantic difference, expressible as one discrete claim,
  grounded in report evidence on **both** sides.
- **Narrative change claims require evidence from both the baseline and
  current reports** — every narrative item's `sources[]` must include at
  least one entry citing `baseline_report_id` and at least one citing
  `current_report_id`. This requirement is unweakened.
- **Narrative citation shape** — `{index, report_id, field}` — retained
  exactly as defined, reusing the existing model-facing `report_number` →
  real-`report_id` mapping.
- `items[]`'s discrete-item representation remains an **explicitly
  acknowledged additive transformation** beyond the engine's current
  single-narrative output (AH-1, §7) — this ratification does not claim
  the architecture already implements it.

### 6.4 Citation models remain distinct

The financial shape (`{index, statement_type, period_end, metric}`) and
the narrative shape (`{index, report_id, field}`) are **retained as
distinct** — neither merged into a new generic shape, nor is any new
citation system introduced. Both populate the same governing citation
convention (`sources[]` + `cited_source_indices`, inline `[n]` markers),
reused unmodified.

### 6.5 Comparison points and state semantics

- **Comparison points (`baseline`/`current`) are explicitly
  caller-supplied** — never defaulted, never inferred from metadata or
  chronology (field position alone establishes direction).
- **No implicit "last user visit" state** and **no Durable Research
  Sessions semantics** are introduced, directly or indirectly.
- The three-value state vocabulary (`complete` / `partial` /
  `insufficient_evidence`), defined per mode, is retained unchanged.
- C-4 remains stateless / on-demand; no MongoDB collection, index, schema,
  or migration is required or authorized by this ratification (AH-2, §7).

### 6.6 Error / job / BYOK / SSRF boundaries

The existing nine-class error taxonomy (zero new classes), the existing
async job/`JobStatus`/SSE/cancel family (without prescribing a specific
`JobKind` identifier), and the existing BYOK/SSRF boundaries
(`require_admin` + `assert_public_url`) all remain part of the ratified
contract exactly as Document 70 already defines them — neither expanded
nor narrowed by this ratification.

None of §6.1–§6.6 is redesigned, invented, or modified by this ratification
— it is a summary of what Document 70 already defines, not a new decision.

---

## 7. Explicit Unresolved Decisions (not silently resolved by this ratification)

### 7.1 Open Contract Decisions (Document 70 §22 — still require a future, explicit CTO decision)

| # | Question | Status after this ratification |
|---|---|---|
| **OCD-1** | Add a third, filing-to-filing `comparison_type`? | Still open. Not adopted. |
| **OCD-2** | Add a `significance`/materiality **label** field per item? | Still open. Not adopted. |
| **OCD-3** | Allow `current_report_id`/`current_period_end` to default rather than stay explicit? | Still open. Not adopted — explicit-only stands. |
| **OCD-4** | Numeric value of the C-4 job deadline? | Still open — operational tuning, not a contract question. |
| **OCD-5** | Apply a §20.1-style evidence/validation gate to C-4? | Still open in specific design. |
| **OCD-6** | Add a minimum-magnitude filter threshold for `period`-mode items? | Still open. Not adopted. |

### 7.2 Architecture Handoff items (Document 70 §22.1 — mechanism-level, not CTO contract decisions)

| # | Item | Mechanism status |
|---|---|---|
| **AH-1** | `report`-mode narrative `items[]` transformation | Mechanism **not** selected — remains open for the architecture phase. |
| **AH-2** | Job-result retention between `POST` and `GET` | Mechanism **not** selected — remains open for the architecture phase. |

**This ratification explicitly does NOT resolve OCD-1 through OCD-6 or
AH-1/AH-2.** They remain exactly as open as Document 70 itself left them —
Document 70 does not explicitly resolve any of them, and this record does
not either. Every one of these items is owed to a future **M15
Architecture Decision Pack** and, where applicable, a subsequent CTO
decision — neither of which this record creates.

---

## 8. Explicit Non-Authorizations

**Ratification of Document 70 does NOT authorize:**

- M15 architecture implementation;
- M15 Architecture Decision Pack approval;
- C-4 production implementation;
- MongoDB schema, collection, index, or migration realization;
- Redis implementation;
- LangGraph implementation;
- frontend implementation;
- production deployment;
- commit;
- push;
- merge;
- release.

**Architecture remains the next separate governance artifact. Implementation
remains blocked until architecture is reviewed/ratified and implementation
authorization is explicitly, separately granted.** This ratification
confirms only that the API contract is fixed; it does not advance any
downstream gate.

---

## 9. Governance Ladder / Next Gate (preserved, not collapsed)

```text
Roadmap reconciliation
≠
Milestone selection
≠
Milestone ratification
≠
API contract
≠
API contract ratification                  🟢 THIS DOCUMENT (72)
≠
Architecture
≠
Architecture ratification
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
Doc 67 (recommendation)     🟢 CTO-RATIFIED (2026-09-03)
  ↓
Doc 68 (selection)          🟢 CTO-RATIFIED via Doc 69 (2026-09-04)
  ↓
Doc 69 (selection ratif.)   🟢 CTO-RATIFIED (2026-09-04)
  ↓
Doc 70 R4 (contract)        🟡 → corrected to CTO-reviewed, approved for ratification
  ↓
Doc 71 (ratification review) 🔴 BLOCKED (historical — status contradiction found)
  ↓
[Document 70 corrected — governance markers now consistent]
  ↓
Doc 72 (THIS)                🟢 CTO RATIFIED — API CONTRACT RATIFICATION
  ↓
STOP — no downstream gate authorized by this record
  ↓
M15 Architecture Decision Pack   (the next legitimate governance gate — NOT created here)
  ↓
Architecture Review / Ratification   (NOT performed here)
  ↓
Implementation Authorization          (NOT performed here)
```

This record performs exactly one stage: **API contract ratification.** It
is not used as a substitute for, or a shortcut past, architecture,
architecture ratification, implementation authorization, or any later
stage.

---

## 10. Repository / Document Provenance

Recorded by read-only `git` inspection this session. **This is a
point-in-time snapshot observed during the creation of this record on
2026-09-06**, not a claim about repository state at any later reading
time. **No `git` mutation was performed** — no `add`/stage, no `commit`,
no `push`, no `amend`, no `rebase`, no `merge`, no `reset`, no `restore`,
no `stash`, no `clean`.

- `HEAD = origin/main = be4949b` (M14 implementation commit), unchanged.
- Document number 72 was verified free before creation (highest existing
  Backend & AI governance document was 71; no Document 72 existed prior to
  this task).
- **Document 70 was read at Revision R4, not modified.** Its
  governance-status markers were verified consistent (§2). Its contract
  position is restated here in substance, not amended.
- **Document 71 was read, not modified.** It remains the accurate
  historical record of the blocked ratification review (§4) — not
  superseded, not retracted, not reinterpreted as having ratified anything.
- Documents 67, 68, and 69 were read, not modified. They remain 🟢
  CTO-RATIFIED and are cited, not reinterpreted.
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval/RAG code, MongoDB collection, Redis
  component, provider, configuration, infrastructure, or frontend file was
  created or modified. `.gitignore` was not modified.
- The working tree is **not** Git-clean. It contains known, pre-existing,
  unrelated items this document does **not** stage, modify, rename,
  delete, or clean:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/   (untracked, M11 evidence)
  ?? current_period_end`                                          (untracked, unexplained pre-existing artifact — not created by this task; not touched)
  ?? docs/backend_engineering/67_Post_M14_Backend_AI_Roadmap_Reconciliation.md
  ?? docs/backend_engineering/68_M15_Formal_Milestone_Selection_Record.md
  ?? docs/backend_engineering/69_Document68_CTO_Ratification_Record.md
  ?? docs/backend_engineering/70_M15_What_Changed_API_Contract_Proposal.md
  ?? docs/backend_engineering/71_Document70_CTO_Ratification_Record.md
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/72_Document70_R4_CTO_Ratification_Record.md`).
  It is **untracked and not yet version-controlled.** Staging or
  committing it is a separate, subsequently CTO-authorized step.

---

## 11. Ratification Conclusion

**This record ratifies Document 70's API contract at Revision R4 — and
only Revision R4. It does not ratify, reference, or assume any revision
beyond R4; no Revision R5 exists in the repository (§2).**

**This is a ratification of an API contract — not an architecture
decision, not an architecture authorization, and not an implementation
authorization.** The two-mode design, financial and narrative comparison
semantics, both mode-specific citation shapes, the both-sides narrative
grounding requirement, explicit caller-supplied comparison points, the
absence of last-visit/DRS semantics, and the existing error/job/BYOK/SSRF
boundaries are all ratified exactly as Document 70 defines them (§6) — none
redesigned, none invented. All six Open Contract Decisions and both
Architecture Handoff items remain explicitly unresolved (§7). No
architecture, schema, infrastructure, implementation, commit, or push is
authorized by this record (§8). The next legitimate governance artifact is
the **M15 Architecture Decision Pack** — not created here, not begun here.

---

**🟢 DOCUMENT 70, REVISION R4 — CTO RATIFIED / ACCEPTED. THIS RECORD
RATIFIES THE M15 = C-4 — "WHAT CHANGED SINCE LAST REVIEW" — API CONTRACT AT
REVISION R4 EXACTLY, AND MAKES NO CLAIM ABOUT ANY REVISION BEYOND R4 — NO
REVISION R5 EXISTS IN THE REPOSITORY. DOCUMENT 71'S PRIOR BLOCKED
RATIFICATION REVIEW IS PRESERVED AS ACCURATE HISTORY, NOT MODIFIED, NOT
SUPERSEDED, AND NOT REINTERPRETED AS HAVING RATIFIED ANYTHING — THIS RECORD
IS THE DISTINCT, SUBSEQUENT RATIFICATION ACT THAT BECAME POSSIBLE ONLY
AFTER DOCUMENT 70'S GOVERNANCE-STATUS MARKERS WERE CORRECTED TO A SINGLE,
CONSISTENT STATE. THE TWO-MODE DESIGN (`period` FINANCIAL, `report`
NARRATIVE) REMAINS MUTUALLY EXCLUSIVE WITH NO COMBINED OR MIXED MODE AND NO
THIRD, FILING-TO-FILING MODE IN V1. FINANCIAL METRIC IDENTITY REMAINS
`Metric.provider_label` WITH NO INVENTED CANONICAL MAPPING AND NO ARBITRARY
MATERIALITY LABEL. NARRATIVE CHANGES REMAIN REQUIRED TO BE GROUNDED IN
EVIDENCE FROM BOTH THE BASELINE AND CURRENT REPORTS, UNWEAKENED. THE
FINANCIAL (`{index, statement_type, period_end, metric}`) AND NARRATIVE
(`{index, report_id, field}`) CITATION SHAPES REMAIN DISTINCT AND UNMERGED.
COMPARISON POINTS REMAIN EXPLICITLY CALLER-SUPPLIED — NO "LAST USER VISIT"
STATE AND NO DURABLE RESEARCH SESSIONS SEMANTICS EXIST. EXISTING
ERROR/JOB/BYOK/SSRF BOUNDARIES REMAIN PART OF THE RATIFIED CONTRACT
UNCHANGED. ALL SIX OPEN CONTRACT DECISIONS (OCD-1 THROUGH OCD-6) AND BOTH
ARCHITECTURE HANDOFF ITEMS (AH-1, AH-2) REMAIN EXPLICITLY UNRESOLVED. THIS
RATIFICATION DOES NOT AUTHORIZE M15 ARCHITECTURE IMPLEMENTATION, M15
ARCHITECTURE DECISION PACK APPROVAL, C-4 PRODUCTION IMPLEMENTATION, MONGODB
SCHEMA/COLLECTION/INDEX/MIGRATION REALIZATION, REDIS IMPLEMENTATION,
LANGGRAPH IMPLEMENTATION, FRONTEND IMPLEMENTATION, PRODUCTION DEPLOYMENT,
COMMIT, PUSH, MERGE, OR RELEASE. DOCUMENTS 67–71 WERE NOT MODIFIED. NO
SOURCE, TEST, SCHEMA, OR INFRASTRUCTURE FILE WAS CREATED OR MODIFIED. NO
STAGE. NO COMMIT. NO PUSH. NO MERGE / REBASE / RESET / AMEND. THE NEXT
LEGITIMATE GOVERNANCE ARTIFACT IS THE M15 ARCHITECTURE DECISION PACK — NOT
IMPLEMENTATION.**
