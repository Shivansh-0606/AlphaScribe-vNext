# 76 — Document 75 CTO Implementation Authorization Ratification Record

**Status:** 🟢 **DOCUMENT 75 — M15 IMPLEMENTATION AUTHORIZATION —
CTO-RATIFIED.** This document records the CTO's ratification of
[75_M15_Implementation_Authorization_Decision.md](75_M15_Implementation_Authorization_Decision.md)
— the M15 Implementation Authorization Decision for **C-4 "What Changed
Since Last Review."** It is a **separate governance act**, distinct from
Document 75 itself:

```text
D75 = implementation authorization decision
D76 = ratification of that decision
```

Document 75 proposed the terms under which C-4 implementation **would** be
authorized, against the already-ratified M15 API contract
([Document 70, Revision R4](70_M15_What_Changed_API_Contract_Proposal.md),
ratified by [Document 72](72_Document70_R4_CTO_Ratification_Record.md)) and
the already-ratified M15 architecture
([Document 73, Revision R1](73_M15_Architecture_Decision_Pack.md), ratified
by [Document 74](74_Document73_R1_CTO_Architecture_Ratification_Record.md)).
**This record ratifies that decision.** It does not perform the
implementation-authorization design (Document 75 already did that), it does
not originate or independently redesign the implementation authorization,
it does not redesign C-4, and it does not reinterpret or amend Documents
70, 73, or 75. **The ratified decision is: Document 75 is the M15
implementation authorization for C-4 "What Changed Since Last Review."**

**Implementation authorization ratification authorizes C-4 implementation
only, strictly within the boundaries of Document 70 R4 + Document 73 R1 +
Document 75. It does NOT authorize commit, push, merge, deployment,
release, or production rollout — each remains a separate, later, distinct
CTO gate** (§16, §17).

**Type:** Governance / implementation-authorization ratification decision
record (documentation only — no source code, test, configuration, schema,
migration, index, route, LangGraph node, MongoDB collection, Redis usage,
or provider change created or modified to produce it; Document 75 and
Documents 67–74 read, not modified. The only file this task creates is
this document.

**Date:** 2026-09-06.

**Precedent / lineage.** This record follows the same standalone
decision-record form already established twice in this governance chain for
ratifying a prior document without modifying it —
[72_Document70_R4_CTO_Ratification_Record.md](72_Document70_R4_CTO_Ratification_Record.md)
(ratifying an API contract) and
[74_Document73_R1_CTO_Architecture_Ratification_Record.md](74_Document73_R1_CTO_Architecture_Ratification_Record.md)
(ratifying an architecture decision pack) — applied one governance step
further down the ladder, ratifying an **implementation-authorization
decision** (Document 75). This record performs exactly one governance act:
ratifying Document 75 as the M15 C-4 implementation authorization. It does
not reinterpret Document 71 (the historical blocked API-contract
ratification review) — cited, not amended.

---

## 0. What This Document Is and Is Not

**Is:** the record of one CTO governance decision — ratification of
Document 75's M15 implementation-authorization decision for C-4 — plus a
precise restatement of what that ratification authorizes, what it
preserves unchanged, what it explicitly does **not** authorize, and the
gates that stand next.

**Is not:** an origination or independent redesign of the implementation
authorization (Document 75 already made that decision — this record
ratifies it, it does not re-derive it); a redesign or reinterpretation of
Document 70, 73, or 75; a resolution or reinterpretation of Document 70's
six Open Contract Decisions or Document 73's four Open Architectural
Questions; a commit, push, merge, deployment, release, or production-
rollout authorization; an architecture decision; an API-contract
amendment; a reopening of M14; a promotion of C-2; an introduction of
Durable Research Sessions; or an authorization for any unrelated frontend,
cleanup, or evaluation-artifact work.

---

## 1. Document Metadata

| Field | Value |
|---|---|
| Document number | 76 |
| Title | Document 75 CTO Implementation Authorization Ratification Record |
| Ratifies | Document 75 — M15 Implementation Authorization Decision — C-4 "What Changed Since Last Review" |
| Ratified state | Document 75 **as present in the repository** — its initial and only issue; no revision marker exists or is claimed (§2) |
| Milestone | M15 = C-4 (Document 68 §4; Document 72 §5; Document 74 §6; Document 75 §1) |
| Governance stage | Implementation-authorization ratification (this act) — governance-ladder stage 4, completed |
| Predecessor gate | Document 75 — M15 Implementation Authorization Decision (CTO-reviewed, approved for ratification) |
| Related prior records | Document 71 (historical, blocked API-contract ratification review — not modified, not reinterpreted); Document 72 (Document 70 R4 API-contract ratification); Document 74 (Document 73 R1 architecture ratification) |
| Successor gates (not created here) | A separate commit authorization (stage 5), then a separate push / merge / deployment authorization (stage 6) |
| Revision of this record | Initial issue — no prior revision |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Exact Ratification Target

**Target: Document 75 — M15 Implementation Authorization Decision — C-4
"What Changed Since Last Review," as present in the repository.**

Verified this session, read-only, before recording this ratification:

- Document 75's top-line Status banner and closing ALL-CAPS block both
  read: *"🟡 PROPOSED M15 IMPLEMENTATION AUTHORIZATION DECISION — DRAFT /
  PENDING CTO REVIEW. NOT YET RATIFIED."* Document 75 §16 / §19 explicitly
  state that **creating Document 75 does not authorize implementation**,
  and that a *separate, subsequent CTO ratification of Document 75* is the
  required next act. **This record is that act** — exactly as Document 72
  ratified Document 70 after its proposal, and Document 74 ratified
  Document 73 after its proposal.
- Document 75 carries **no revision-note block.** It was drafted once, with
  two subsequent in-place wording corrections (its own §10 infrastructure-
  reuse constraint language; its own §15 placement of the additive
  `JobKind.CHANGE_BRIEF` enum member as source-code implementation, not a
  configuration change) — neither correction altered a scope, contract,
  architecture, or governance decision, and neither was marked as a
  numbered revision (Document 75 §20). This record ratifies Document 75 in
  that single state.
- `docs/backend_engineering/` was listed in full: the highest-numbered
  file prior to this task was `75_M15_Implementation_Authorization_Decision.md`.
  No second Document-75-shaped file exists anywhere in the repository, and
  no Document 76 existed before this task.
- `git status --short` shows Document 75 as untracked (never committed) —
  there is no commit history suggesting a superseding revision was ever
  pushed elsewhere.

**No discrepancy was found. Document 75, in its single present state, is
confirmed as the correct and only implementation-authorization-ratification
target.** This record ratifies that state exactly. If a later, numbered
revision of Document 75 is ever introduced, it requires its own separate
CTO review and ratification; this record does not, and cannot, extend to
it.

---

## 3. Document 75 Provenance

Document 75 was created on 2026-09-06 as the M15 Implementation
Authorization Decision — the **third instance** of the proposal-then-
ratification pattern this governance chain already ran twice: Document 70
(API contract proposal) → Document 72 (its ratification); Document 73
(architecture decision pack) → Document 74 (its ratification). Document 75
is the implementation-authorization proposal; **this record (Document 76)
is its ratification.**

Document 75 itself:

- did not resolve Document 70's six Open Contract Decisions or Document
  73's four Open Architectural Questions, beyond the one bounded meta-
  question it explicitly names (§15.1 below);
- did not modify Documents 67–74 (all read, not modified);
- created exactly one file — itself;
- performed no `git` mutation, staged nothing, committed nothing, pushed
  nothing.

This record ratifies Document 75 **as it stands** — the pre-correction
draft is not a separate ratification target, and the two in-place wording
corrections are part of the single state being ratified.

---

## 4. Governance Lineage

| Document | Role | Governance act performed |
|---|---|---|
| **Document 67** | Post-M14 Backend & AI Roadmap Reconciliation | **C-4 recommendation.** CTO-ratified (2026-09-03); recommended C-4 as the preferred next Backend & AI direction. Did not select M15. |
| **Document 68** | M15 Formal Milestone Selection Record | **M15 = C-4 selection.** Formally selected the milestone. |
| **Document 69** | Document 68 CTO Ratification Record | **Selection ratification.** Ratified the M15 = C-4 milestone selection. |
| **Document 70 (R1→R4)** | M15 API Contract Proposal | **API contract.** Defines the externally observable request/response, citation, error, state, and job/SSE semantics for C-4, revised through four CTO-directed passes to Revision R4. |
| **Document 71** | Document 70 CTO Ratification Review | **Historical blocked ratification review** — found Document 70's governance-status markers self-contradictory; did not ratify. Not modified, not superseded, not reinterpreted here. |
| **Document 72** | Document 70 Revision R4 CTO Ratification Record | **API-contract ratification.** Document 70 R4 ratified as the M15 = C-4 API contract. |
| **Document 73 (R1)** | M15 Architecture Decision Pack | **Architecture decision.** Determines *how* the ratified API contract is realized; resolves architecture handoff items AH-1 and AH-2. |
| **Document 74** | Document 73 Revision R1 CTO Architecture Ratification Record | **Architecture ratification.** Document 73 R1 ratified as the M15 C-4 architecture. |
| **Document 75** | M15 Implementation Authorization Decision | **Implementation authorization decision.** Proposes the terms under which C-4 implementation would be authorized within Document 70 R4 + Document 73 R1. |
| **Document 76 (THIS)** | Document 75 CTO Implementation Authorization Ratification Record | **Ratification of Document 75.** The distinct act that ratifies Document 75 as the M15 C-4 implementation authorization. |

```text
D67  → C-4 recommendation
D68  → M15 = C-4 selection
D69  → selection ratification
D70 R4 → API contract
D72  → API contract ratification
D73 R1 → architecture decision
D74  → architecture ratification
D75  → implementation authorization decision
D76  → ratification of D75
```

These are **distinct governance acts** and this record does not collapse
them. In particular: **Document 75 is the implementation-authorization
decision; Document 76 is its ratification.** Document 76 did not originate
that authorization and did not independently redesign it.

---

## 5. CTO Implementation-Authorization-Review Decision

The CTO has reviewed Document 75 and issued: **🟢 DOCUMENT 75 — APPROVED
FOR IMPLEMENTATION-AUTHORIZATION RATIFICATION.** This document records that
ratification. Review confirmed:

- Document 75 authorizes implementation **only** for M15 — C-4 "What
  Changed Since Last Review," and **only** within the boundaries already
  fixed by Document 70 R4 (the ratified API contract), Document 73 R1 (the
  ratified architecture), and Document 75's own explicitly stated
  implementation boundaries (§§4–16 of Document 75);
- the exact two modes — `period` (financial changes) and `report`
  (narrative changes) — are preserved, mutually exclusive, one per
  request, with no third comparison mode;
- the deterministic, LLM-free financial architecture is preserved exactly
  (§8 below);
- the bounded, single-`chat_json`-call narrative architecture is preserved
  exactly, with no iterative or unbounded generation mechanism (§9 below);
- the AH-2 process-local result invariant is preserved exactly, unweakened
  (§10 below);
- infrastructure reuse is bounded to the two additive extensions Document
  73 R1 §16 already names, with no unrelated infrastructure redesign (§11,
  §12 below);
- every Open Contract Decision and Open Architectural Question remains
  exactly as open as Document 75 left it (§15 below);
- Document 75 authorizes **implementation only** — not commit, push,
  merge, deployment, release, or production rollout (§16 below).

---

## 6. Implementation Authorization Ratification Decision

**🟢 DOCUMENT 75 — M15 IMPLEMENTATION AUTHORIZATION — CTO-RATIFIED.**

**Document 75 is formally ratified as the M15 implementation authorization
for C-4 "What Changed Since Last Review."** This confirms the decision
already recorded in Document 75's §§0–20. It does **not** re-derive,
redesign, extend, or narrow that authorization, and it does **not**
authorize commit, push, merge, deployment, release, or production rollout
(§16).

**Effect of this ratification:** M15 / C-4 implementation is now formally
authorized — strictly within the combined boundaries of Document 70 R4 +
Document 73 R1 + Document 75, and nothing broader (§7, §17).

---

## 7. Ratified Implementation Authorization Scope

**This ratification confirms that Document 75 authorizes implementation
only within:**

- **M15 — C-4 "What Changed Since Last Review"** — this milestone and this
  capability only;
- **Document 70, Revision R4** — the ratified API contract (request/
  response shapes, citation shapes, state vocabulary, error taxonomy,
  job/SSE behavior, security boundaries);
- **Document 73, Revision R1** — the ratified architecture (the two-engine
  design, the AH-1 and AH-2 resolutions, the process-local deployment
  invariant, the orchestration and LLM-boundary decisions);
- **Document 75's explicitly defined implementation boundaries** — the
  bounded set of source changes, tests, configuration, and documentation
  updates enumerated in Document 75 §15, and the explicit non-
  authorization list in Document 75 §16.

**Any implementation detail not already fixed by Document 70 R4 or Document
73 R1 remains an ordinary engineering decision made during implementation
— not a new governance grant conferred by this ratification.** This record
does not extend, narrow, or reinterpret the contract or the architecture.

### 7.1 The two modes — preserved exactly

Implementation is scoped to **exactly the two ratified modes**, mutually
exclusive, one per request:

- **`period`** — financial changes.
- **`report`** — narrative changes.

**No third comparison mode** (including the filing-to-filing mode Document
70's OCD-1 declined to adopt) is authorized. A combined or mixed-mode
request remains undefined and unauthorized.

---

## 8. Ratified Financial Architecture (preserved exactly — Document 73 R1 / Document 75 §6)

The `period`-mode implementation authorized by this ratification **must
preserve**, without relaxation for implementation convenience:

- **Deterministic financial computation only** — no LLM involvement of any
  kind on the financial comparison path.
- **Exact `Metric.provider_label` alignment** — metric identity by exact
  string equality; **no invented canonical metric mapping**, no fuzzy
  matching, no new vocabulary-normalization layer. `Metric.canonical_metric`
  remains `null` for every metric today, and provider relabeling across
  periods remains a documented, accepted limitation, not silently solved.
- **Deterministic citations** — the financial source shape
  (`{index, statement_type, period_end, metric}`) built directly from the
  two resolved statement identities, with no model-trust boundary
  involved.
- **Document 70 R4 financial citation semantics preserved exactly** — the
  financial citation shape is not altered, extended, or merged with the
  narrative shape.

If implementation discovers a genuine obstacle to any of these boundaries,
that is a governance issue to raise separately — not a license to deviate
silently.

---

## 9. Ratified Narrative Architecture (preserved exactly — Document 73 R1 / Document 75 §7)

The `report`-mode implementation authorized by this ratification **must
preserve**:

- **Bounded, exactly-two-report evidence input** (`build_evidence_payload`,
  reused unmodified, called with `[baseline_report, current_report]`);
- **exactly one structured `chat_json` call per request** — no multi-pass
  generation, no additional LLM calls;
- **bounded structured output** — bounded in principle by the fixed
  evidence-payload size and the single call's own output-token budget
  (Document 73 R1 §10/§11); this is an architectural bound, **not** a new
  contract-visible `max_items` field and **not** a guaranteed
  application-level item-count ceiling;
- **deterministic per-item citation validation** — reusing
  `validate_and_map_citations`'s duplicate/undeclared-rejection logic,
  extended with the mandatory both-sides check;
- **mandatory baseline + current grounding, unweakened** — every emitted
  narrative item must cite at least one source mapping to the baseline
  report and at least one mapping to the current report; an item failing
  this check is dropped, never surfaced;
- **Document 70 R4 narrative citation semantics preserved exactly** —
  `{index, report_id, field}`, unmerged with the financial shape.

**No iterative generation, no continuation loop, and no unbounded
narrative-generation mechanism is authorized.** A design that could
produce an arbitrarily long item list without the bounds above (iterative
multi-call generation, or a mechanism that keeps requesting more items
until an external stop condition) is out of scope for this authorization.

---

## 10. Ratified Process-Local Result Invariant (AH-2 — preserved exactly — Documents 73 R1 §12.1/§12.2, 74 §10, 75 §8)

This ratification **explicitly ratifies** the process-local result
invariant, to be preserved by implementation without weakening or working
around it:

- **Completed results exist only in the backend process that executed the
  job.** No mechanism may make a result reconstructible or visible from
  any other process.
- **Restart loss is accepted.** A process restart discarding an
  in-flight-retrievable result is correct, intended behavior — not a bug
  to "fix" by adding persistence.
- **Cross-process `GET` is unsupported.** A `GET` reaching a different
  backend process than the one that ran the job must not be made to work.
- **No sticky-session workaround.** No load-balancer session affinity or
  equivalent routing trick to paper over cross-process unavailability.
- **No Redis final-result persistence.** The existing `RedisEventBus`'s
  cross-process-capable trace-event transport (when `JOB_BACKEND=redis`)
  must not be extended or repurposed to carry the completed result
  payload cross-process.
- **No MongoDB final-result persistence.** No new collection, document
  shape, or write path for the completed `changes` payload is authorized.
- **No cross-process reconstruction** by any other means (e.g.,
  recomputing on a different process on a cache-miss) — reconstruction is
  not a substitute for retention and is not authorized as a workaround.
- **SSE does not bypass the invariant.** The synthetic `final` frame is
  constructed from the same process-local buffer as `GET`; it carries the
  identical constraint, not an exemption.

This is the single most load-bearing boundary in the authorization. An
implementation that quietly reaches for a shared store to make the
lifecycle "just work" across processes would violate this ratified
decision even if every other boundary were respected. Horizontal
multi-instance support for this lifecycle remains **explicitly out of M15
scope** (AAQ-3, §15) — a separate, future architecture decision, not
solved and not pre-empted here.

---

## 11. Ratified Infrastructure Boundaries (preserved exactly — Document 75 §9 / §10)

This ratification preserves Document 75's infrastructure boundaries and
**does not expand them**:

- **Additive `JobKind.CHANGE_BRIEF`** — the one additive domain-model enum
  member Document 73 R1 §16 already names, and nothing broader.
- **Additive `job_deadline_change_brief_s`** — the one additive settings
  entry Document 73 R1 §16 already names, and nothing broader. Its
  concrete numeric value is an implementation-time bounded operational
  choice, **not** a governance constant pre-ratified by this record (§15.1,
  §15.2 — OCD-4 / AAQ-1).
- **Reuse of existing infrastructure without changing existing behavior or
  contracts, except for the explicitly authorized additive extensions
  above** — the existing async job lifecycle (`JobLifecycle`, `JobStore`,
  `EventBus`, the shared `MAX_ACTIVE_JOBS` admission budget); the existing
  citation-validation logic (`validate_and_map_citations`) as a building
  block for the new per-item both-sides check; the existing report-
  resolution query pattern, extended only with the additive `ticker`-match
  clause Document 73 R1 §10/§25 already identifies as a compatible
  extension; the existing financial-statement read path; the existing
  observability patterns; the existing in-process, TTL-bounded result-
  buffer mechanism (the M14 `_FILING_ANALYSIS_RESULTS` pattern) as the
  concrete realization of AH-2; and the existing security boundaries
  (SSRF guarding, BYOK contextvar threading, the existing nine-class error
  taxonomy).
- **No unrelated infrastructure redesign.** Any change to an existing
  route, schema, or contract behavior outside C-4's own new surface is out
  of scope and would itself require separate governance. This ratification
  does not pre-authorize any MongoDB schema/collection/index/migration
  change, any Redis usage for result persistence, any LangGraph
  involvement, any new durable research-session infrastructure, any
  frontend implementation, or any deployment infrastructure change.

---

## 12. Existing Infrastructure Reuse (ratified as authorized, unmodified)

Consistent with Document 73 R1 §6/§16 and Document 75 §10, implementation
**may** reuse the already-existing, already-authorized infrastructure and
patterns from M14 and earlier milestones **without changing their existing
behavior or contracts**, except for the two explicitly authorized additive
extensions in §11. **Reuse must not alter the ratified M14 or M15
contracts.** This ratification authorizes *using* that infrastructure; it
authorizes no change *to* it beyond the two named additive extensions.

---

## 13. Ratified Security / Observability Boundary (preserved exactly — Documents 73 R1, 75 §12 / §13)

- **SSRF protection** — `require_admin` + `assert_public_url`, applied
  identically to any custom BYOK provider/base URL, with no exception
  carved out for C-4.
- **BYOK boundaries** — the existing per-request `contextvar` threading,
  unmodified; `period` mode touches no BYOK context at all, since it makes
  no LLM call.
- **Input validation / authorization / ownership** — the discriminated
  request model's conditional field requirements, existence/ownership/
  ticker-match checks, the existing 422/404 mapping, and owner-scoped job
  records and report references, all applied exactly as specified;
  non-disclosure behavior is not relaxed (a foreign or nonexistent
  reference remains indistinguishable, 404).
- **Error handling** — the existing nine-class `domain/errors.py` taxonomy
  only; **zero new error classes** authorized.
- **Observability** — one root `pipeline.change_brief` span with per-step
  child spans; a new `change_brief_runs_total{outcome, comparison_type}`
  counter following the existing naming precedent; correlation-id logging
  inherited via existing middleware; no logging of BYOK material, raw
  provider responses on failure, or raw report/filing content beyond
  existing discipline. Observability tooling is **not** an authorized
  channel for reconstructing or retrieving a completed job's result
  outside the process-local mechanism §10 describes.

**No security control may be weakened, bypassed, or special-cased for C-4
implementation convenience.**

---

## 14. Testing / Evaluation Floor (carried forward — Document 75 §14)

Document 75 §14 defines the **minimum testing floor** implementation must
clear before it may be considered complete for the purposes of a future
commit-authorization request. This ratification carries that floor forward
as a requirement — unit tests for the financial-delta eligibility rule;
hermetic integration/contract tests for the full `/api/companies/{ticker}/
changes` route family across both modes; deterministic financial-
comparison tests with bit-identical output asserted across repeated
identical requests; narrative grounding / citation-validation tests
(one-sided item dropped; zero groundable candidates →
`insufficient_evidence`; narrative and financial source shapes never
mixed); process-local lifecycle tests (same-process `GET`; expiration;
post-restart unavailability; unsupported cross-instance behavior; SSE
`final`-frame behavior under the same invariant); regression coverage
against relevant M14 behavior (route-inventory guard updated by exactly
the four new C-4 routes, no more, no fewer); security/validation coverage
(BYOK/SSRF, ownership/non-disclosure); and a small `report`-mode
golden-dataset evaluation set run through the existing framework unmodified
as grounding evidence.

**Clearing this floor does not, by itself, constitute a claim of universal
production-grade correctness**, and it does **not** authorize commit — it
verifies the specific bounded properties Document 75 §14 lists.

---

## 15. Open Decisions Preserved (not silently resolved — Document 70 §22, Document 73 §24, Document 75 §11)

**This ratification does not resolve, reinterpret, or narrow any of
Document 70's six Open Contract Decisions or Document 73's four Open
Architectural Questions.**

### 15.1 The one bounded meta-question — confirmed, not extended

Document 75 §11.1 resolves exactly one bounded meta-question: *whether the
existence of six unresolved OCDs and four unresolved AAQs, by itself,
blocks implementation authorization.* Document 75 answers **no**,
consistent with Document 70's and Document 73's own statements that none of
their open items "blocks ratification on its own." **This ratification
confirms that bounded meta-resolution and extends it no further.** It
resolves **nothing** about the substance of any individual OCD or AAQ —
each remains exactly as open as before.

### 15.2 Contract-level Open Contract Decisions (Document 70 §22 — unchanged)

| # | Question | Status after this ratification |
|---|---|---|
| **OCD-1** | Add a third, filing-to-filing `comparison_type`? | Still open. Not adopted. Not authorized. |
| **OCD-2** | Add a `significance`/materiality label field? | Still open. Not adopted. |
| **OCD-3** | Allow `current_*` to default rather than stay explicit? | Still open. Not adopted — explicit-only stands. |
| **OCD-4** | Numeric value of the C-4 job deadline? | Still open at the governance level. Implementation will necessarily assign a concrete value as an operational parameter — an **implementation-time bounded decision**, not a governance resolution made by, or pre-ratified by, this record. |
| **OCD-5** | Apply a §20.1-style evidence/validation gate to C-4? | Still open in specific design. |
| **OCD-6** | Add a minimum-magnitude filter threshold for `period`-mode items? | Still open. Not adopted. |

### 15.3 Open Architectural Questions (Document 73 §24 — unchanged)

| # | Item | Status after this ratification |
|---|---|---|
| **AAQ-1** | Exact numeric value of `job_deadline_change_brief_s` | Same as OCD-4 — an implementation-time operational parameter, **not** resolved here and **not** converted into a pre-ratified governance constant by this record. |
| **AAQ-2** | Exact prompt wording and model tier for `report`-mode generation | Still open — an ordinary engineering decision within the architecture's already-fixed boundaries (§9), not a governance resolution made here. |
| **AAQ-3** | Future multi-instance deployment support | Still open, explicitly out of M15 scope (§10). Not authorized, not scheduled, not solved. |
| **AAQ-4** | Whether OCD-5's validation gate is adopted for C-4 | Still open — a contract-level decision, not this record's to make. |

### 15.4 Explicit statement on the implementation-selected deadline value

Document 75 permits implementation to select a concrete value for the C-4
job deadline (`job_deadline_change_brief_s`) as an operational parameter.
**This ratification confirms that this is an implementation-time bounded
decision — not a retroactive architecture or contract decision, and not a
governance constant.** The value implementation picks does **not** become
a pre-ratified governance constant by virtue of this ratification; OCD-4
and AAQ-1 remain open at the governance level regardless of the operational
value implementation assigns.

---

## 16. Explicit Non-Authorizations

**This ratification — even though it makes M15 / C-4 implementation
formally authorized — does NOT authorize:**

- commit;
- push;
- merge;
- deployment;
- release;
- production rollout;
- unrelated cleanup of any kind;
- reopening M14;
- promoting C-2;
- implementing Durable Research Sessions;
- unrelated frontend work;
- architectural redesign of any kind;
- API-contract amendment outside a separately governed amendment process.

**Commit authorization and push / merge / deployment authorization remain
two further, separate, distinct CTO acts** (governance-ladder stages 5 and
6, §18), neither created nor implied by this record, and neither creatable
by this ratification.

**Document 76 did not originate the implementation authorization and did
not independently redesign it.** Document 75 made that decision; this
record ratifies it. The scope, the two modes, the financial and narrative
boundaries, the AH-2 invariant, the infrastructure boundaries, and the
open-decision preservation are all exactly as Document 75 states them —
none redesigned, none invented, none expanded here.

---

## 17. Ratification Status

**After this record (Document 76):**

- **M15 / C-4 implementation is formally authorized** — strictly within the
  combined boundaries of **Document 70 R4** (the ratified API contract) +
  **Document 73 R1** (the ratified architecture) + **Document 75** (the
  ratified implementation authorization, including its explicit §15
  authorized-work list and §16 non-authorization list).
- **The two modes** (`period` — financial changes; `report` — narrative
  changes) are preserved exactly, mutually exclusive, one per request, no
  third mode.
- **The deterministic, LLM-free financial architecture** and the
  **bounded, single-`chat_json`-call narrative architecture with mandatory
  unweakened baseline + current grounding** are preserved exactly.
- **The AH-2 process-local result invariant** is preserved exactly,
  unweakened.
- **Every OCD and every AAQ** remains exactly as open as before; only the
  one bounded meta-question (§15.1) is resolved, and only as Document 75
  already resolved it.

**However — and equally binding:**

- **commit, push, merge, deployment, release, and production rollout
  remain separately gated.** Each is a distinct, later CTO act (§18, §19).
  This ratification advances the governance ladder exactly one stage — from
  "implementation authorization proposed" to "implementation authorization
  ratified" — and no further.

---

## 18. Governance Ladder (restated, not collapsed)

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
Architecture ratification
≠
Implementation authorization decision
≠
Implementation-authorization ratification        🟢 THIS DOCUMENT (76)
≠
Implementation
≠
Technical review
≠
Commit authorization
≠
Push / merge / deployment authorization
```

```text
Doc 67 (recommendation)               🟢 CTO-RATIFIED (2026-09-03)
  ↓
Doc 68 (milestone selection)          🟢 CTO-RATIFIED via Doc 69      — STAGE 1
  ↓
Doc 69 (selection ratification)       🟢 CTO-RATIFIED
  ↓
Doc 70 R4 (API contract)              🟢 CTO-RATIFIED via Doc 72      — STAGE 2
  ↓
Doc 71 (ratification review)          🔴 BLOCKED (historical — superseded by Doc 72's success)
  ↓
Doc 72 (API-contract ratification)    🟢 CTO-RATIFIED
  ↓
Doc 73 R1 (architecture pack)         🟢 CTO-RATIFIED via Doc 74      — STAGE 3
  ↓
Doc 74 (architecture ratification)    🟢 CTO-RATIFIED
  ↓
Doc 75 (implementation authorization  🟢 CTO-RATIFIED via Doc 76      — STAGE 4
        decision)
  ↓
Doc 76 (THIS)                         🟢 IMPLEMENTATION AUTHORIZATION RATIFIED
  ↓
Implementation                        AUTHORIZED — within Doc 70 R4 + Doc 73 R1 + Doc 75 only
  ↓
Commit authorization                  NOT CREATED — a separate, later, distinct CTO act   — STAGE 5
  ↓
Push / merge / deployment             NOT CREATED — a separate, later, distinct CTO act   — STAGE 6
  authorization
```

This record performs exactly one stage: **implementation-authorization
ratification** (stage 4, completed). It is not a substitute for, or a
shortcut past, commit authorization (stage 5), push/merge/deployment
authorization (stage 6), or any later stage. **Document 76 does not become
a commit-authorization record.**

---

## 19. Next Gate

**The next legitimate governance action is C-4 implementation itself**,
carried out strictly within the boundaries of Document 70 R4 + Document 73
R1 + Document 75, and cleared against the minimum testing floor Document 75
§14 defines. **Only after implementation is complete and reviewed** may a
separate, explicit **commit-authorization** decision be sought; and only
after that, a further separate **push / merge / deployment-authorization**
decision. Each is a distinct CTO act, none collapsed, none implied by this
record.

---

## 20. Repository / Document Provenance

Recorded by read-only `git` inspection this session. **This is a
point-in-time snapshot observed during the creation of this record on
2026-09-06**, not a claim about repository state at any later reading
time. **No `git` mutation was performed** — no `add`/stage, no `commit`,
no `push`, no `amend`, no `rebase`, no `merge`, no `reset`, no `restore`,
no `stash`, no `clean`.

- `HEAD = origin/main = be4949b` (M14 implementation commit), unchanged.
- Document number 76 was verified free before creation (highest existing
  Backend & AI governance document was 75; no Document 76 existed prior to
  this task).
- **Document 75 was read in its single present state, not modified.** It
  carries no revision-note block (§2). Its implementation-authorization
  decision is restated here in substance, not amended.
- **Document 71 was read, not modified.** It remains the accurate
  historical record of the blocked API-contract ratification review — not
  superseded, not retracted, not reinterpreted.
- **Documents 72 and 74 were read, not modified.** They remain the
  accurate records of the API-contract ratification and the architecture
  ratification respectively — not reinterpreted.
- Documents 67, 68, 69, 70, and 73 were read, not modified. They remain 🟢
  CTO-RATIFIED (Document 70 at Revision R4; Document 73 at Revision R1) and
  are cited, not reinterpreted.
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval/RAG code, MongoDB collection, Redis
  component, provider, configuration, infrastructure, or frontend file was
  created or modified. `.gitignore` was not modified. No MongoDB schema
  and no Redis infrastructure was touched.
- The working tree is **not** Git-clean. It contains known, pre-existing,
  unrelated items this document does **not** stage, modify, rename,
  delete, or clean:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/   (untracked, M11 evidence)
  ?? both                                                          (untracked, unexplained pre-existing artifact — not created by this task; not touched)
  ?? current_period_end`                                          (untracked, unexplained pre-existing artifact — not created by this task; not touched)
  ?? docs/backend_engineering/67_Post_M14_Backend_AI_Roadmap_Reconciliation.md
  ?? docs/backend_engineering/68_M15_Formal_Milestone_Selection_Record.md
  ?? docs/backend_engineering/69_Document68_CTO_Ratification_Record.md
  ?? docs/backend_engineering/70_M15_What_Changed_API_Contract_Proposal.md
  ?? docs/backend_engineering/71_Document70_CTO_Ratification_Record.md
  ?? docs/backend_engineering/72_Document70_R4_CTO_Ratification_Record.md
  ?? docs/backend_engineering/73_M15_Architecture_Decision_Pack.md
  ?? docs/backend_engineering/74_Document73_R1_CTO_Architecture_Ratification_Record.md
  ?? docs/backend_engineering/75_M15_Implementation_Authorization_Decision.md
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/76_Document75_CTO_Implementation_Authorization_Ratification_Record.md`).
  It is **untracked and not yet version-controlled.** Staging or
  committing it is a separate, subsequently CTO-authorized step.

---

## 21. Ratification Conclusion

**This record ratifies Document 75's M15 implementation-authorization
decision for C-4 "What Changed Since Last Review" — in the single state
Document 75 is present in the repository, with no revision claimed beyond
that.**

**This is a ratification of an implementation-authorization decision — not
its origination, not an independent redesign of it, not an architecture
decision, not an API-contract amendment, and not a commit, push, merge,
deployment, release, or production-rollout authorization.** The
implementation scope (M15 / C-4 only), the two mutually exclusive modes
(`period`, `report`), the deterministic LLM-free financial path with exact
`Metric.provider_label` alignment and no invented canonical metric
mapping, the bounded single-`chat_json`-call narrative path with mandatory
unweakened baseline + current grounding and no iterative or unbounded
generation, the D70 R4 financial and narrative citation semantics, the
AH-2 process-local result invariant, the two additive infrastructure
extensions (`JobKind.CHANGE_BRIEF`, `job_deadline_change_brief_s`) with no
unrelated infrastructure redesign, and the preserved-open OCD-1 through
OCD-6 and AAQ-1 through AAQ-4 are all ratified exactly as Document 75
states them — none redesigned, none invented, none expanded. The
implementation-selected job-deadline value remains an implementation-time
bounded operational choice, not a pre-ratified governance constant. No
source code, test, configuration, schema, or infrastructure file was
created or modified. Nothing was staged, committed, or pushed. **After
this record, M15 / C-4 implementation is formally authorized within the
boundaries of Document 70 R4 + Document 73 R1 + Document 75 — while commit,
push, merge, deployment, release, and production rollout remain separately
gated.**

---

**🟢 DOCUMENT 75 — M15 IMPLEMENTATION AUTHORIZATION — CTO-RATIFIED. THIS
RECORD RATIFIES DOCUMENT 75 AS THE M15 IMPLEMENTATION AUTHORIZATION FOR C-4
"WHAT CHANGED SINCE LAST REVIEW," IN ITS SINGLE PRESENT STATE, AND MAKES NO
CLAIM ABOUT ANY LATER REVISION. D75 = IMPLEMENTATION AUTHORIZATION
DECISION; D76 = RATIFICATION OF THAT DECISION — D76 DID NOT ORIGINATE OR
INDEPENDENTLY REDESIGN THE AUTHORIZATION. IMPLEMENTATION IS AUTHORIZED ONLY
WITHIN M15 / C-4, DOCUMENT 70 REVISION R4 (RATIFIED API CONTRACT), DOCUMENT
73 REVISION R1 (RATIFIED ARCHITECTURE), AND DOCUMENT 75'S EXPLICITLY
DEFINED IMPLEMENTATION BOUNDARIES. EXACTLY TWO MUTUALLY EXCLUSIVE MODES ARE
PRESERVED — `period` (FINANCIAL CHANGES) AND `report` (NARRATIVE CHANGES) —
WITH NO THIRD MODE. THE FINANCIAL PATH REMAINS DETERMINISTIC WITH NO LLM ON
THE FINANCIAL PATH, EXACT `Metric.provider_label` ALIGNMENT, DETERMINISTIC
CITATIONS, NO INVENTED CANONICAL METRIC MAPPING, AND D70 R4 FINANCIAL
CITATION SEMANTICS INTACT. THE NARRATIVE PATH REMAINS BOUNDED TWO-REPORT
EVIDENCE, ONE STRUCTURED `chat_json` CALL, BOUNDED STRUCTURED OUTPUT,
DETERMINISTIC PER-ITEM CITATION VALIDATION, MANDATORY BASELINE + CURRENT
GROUNDING, AND D70 R4 NARRATIVE CITATION SEMANTICS INTACT — WITH NO
ITERATIVE GENERATION, NO CONTINUATION LOOP, AND NO UNBOUNDED
NARRATIVE-GENERATION MECHANISM. THE AH-2 PROCESS-LOCAL RESULT INVARIANT IS
RATIFIED UNWEAKENED: COMPLETED RESULTS EXIST ONLY IN THE PROCESS THAT
EXECUTED THE JOB; RESTART LOSS IS ACCEPTED; CROSS-PROCESS `GET` IS
UNSUPPORTED; NO STICKY-SESSION WORKAROUND; NO REDIS FINAL-RESULT
PERSISTENCE; NO MONGODB FINAL-RESULT PERSISTENCE; NO CROSS-PROCESS
RECONSTRUCTION; SSE DOES NOT BYPASS THE INVARIANT. INFRASTRUCTURE
BOUNDARIES ARE PRESERVED AND NOT EXPANDED: ADDITIVE `JobKind.CHANGE_BRIEF`;
ADDITIVE `job_deadline_change_brief_s`; REUSE OF EXISTING INFRASTRUCTURE
WITHOUT CHANGING EXISTING BEHAVIOR OR CONTRACTS EXCEPT FOR THOSE EXPLICITLY
AUTHORIZED ADDITIVE EXTENSIONS; NO UNRELATED INFRASTRUCTURE REDESIGN. ALL
SIX OPEN CONTRACT DECISIONS (OCD-1 THROUGH OCD-6) AND ALL FOUR OPEN
ARCHITECTURAL QUESTIONS (AAQ-1 THROUGH AAQ-4) REMAIN EXPLICITLY UNRESOLVED;
ONLY THE ONE BOUNDED META-QUESTION (THAT THEIR EXISTENCE DOES NOT BLOCK
IMPLEMENTATION AUTHORIZATION) IS CONFIRMED, EXACTLY AS DOCUMENT 75 ALREADY
RESOLVED IT. THE IMPLEMENTATION-SELECTED JOB-DEADLINE VALUE IS AN
IMPLEMENTATION-TIME BOUNDED OPERATIONAL CHOICE, NOT A PRE-RATIFIED
GOVERNANCE CONSTANT — OCD-4 AND AAQ-1 REMAIN OPEN AT THE GOVERNANCE LEVEL.
THIS RECORD DOES NOT AUTHORIZE COMMIT, PUSH, MERGE, DEPLOYMENT, RELEASE,
PRODUCTION ROLLOUT, UNRELATED CLEANUP, M14 REOPENING, C-2 PROMOTION,
DURABLE RESEARCH SESSIONS, UNRELATED FRONTEND WORK, ARCHITECTURAL REDESIGN,
OR API-CONTRACT AMENDMENT OUTSIDE A SEPARATELY GOVERNED PROCESS. LINEAGE:
D67 → C-4 RECOMMENDATION; D68 → M15 = C-4 SELECTION; D69 → SELECTION
RATIFICATION; D70 R4 → API CONTRACT; D72 → API-CONTRACT RATIFICATION; D73
R1 → ARCHITECTURE DECISION; D74 → ARCHITECTURE RATIFICATION; D75 →
IMPLEMENTATION AUTHORIZATION DECISION; D76 → RATIFICATION OF D75 — DISTINCT
ACTS, NOT COLLAPSED. DOCUMENTS 67–75 WERE NOT MODIFIED. NO SOURCE, TEST,
CONFIGURATION, MONGODB SCHEMA, REDIS INFRASTRUCTURE, OR FRONTEND FILE WAS
CREATED OR MODIFIED. NO STAGE. NO COMMIT. NO PUSH. NO MERGE / REBASE /
RESET / AMEND. AFTER THIS RECORD, M15 / C-4 IMPLEMENTATION IS FORMALLY
AUTHORIZED WITHIN THE BOUNDARIES OF D70 R4 + D73 R1 + D75; COMMIT, PUSH,
MERGE, DEPLOYMENT, RELEASE, AND PRODUCTION ROLLOUT REMAIN SEPARATELY GATED.
THE NEXT LEGITIMATE GOVERNANCE ACTION IS C-4 IMPLEMENTATION ITSELF — NOT
COMMIT, AND NOT DEPLOYMENT.**
