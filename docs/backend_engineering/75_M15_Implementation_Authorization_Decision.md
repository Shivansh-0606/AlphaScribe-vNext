# 75 — M15 Implementation Authorization Decision — C-4 "What Changed Since Last Review"

**Status:** 🟡 **PROPOSED M15 IMPLEMENTATION AUTHORIZATION DECISION —
DRAFT / PENDING CTO REVIEW. NOT YET RATIFIED.** This document proposes the
terms under which implementation of C-4 **would** be authorized against
the already-ratified M15 API contract
([Document 70, Revision R4](70_M15_What_Changed_API_Contract_Proposal.md),
ratified by [Document 72](72_Document70_R4_CTO_Ratification_Record.md))
and the already-ratified M15 architecture
([Document 73, Revision R1](73_M15_Architecture_Decision_Pack.md), ratified
by [Document 74](74_Document73_R1_CTO_Architecture_Ratification_Record.md)).
**Creating this document does NOT authorize implementation.** It is a
proposal, submitted for CTO review; a separate, subsequent CTO
**ratification** of this document is required before any implementation
work may begin (§16, §19).

**Ratification status (recorded 2026-09-06, after this document was
written — mechanical status note, no change to the authorization scope
below).** The separate, subsequent CTO ratification anticipated above has
since been performed: this proposal was **ratified by
[Document 76 — Document 75 CTO Implementation Authorization Ratification
Record](76_Document75_CTO_Implementation_Authorization_Ratification_Record.md)**.
Per Document 76, M15 / C-4 implementation is formally authorized strictly
within the boundaries of Document 70 R4 + Document 73 R1 + this document.
The "DRAFT / PENDING CTO REVIEW — NOT YET RATIFIED" wording in this header
and in the closing block is preserved as the record of this document's
state *when written*; **Document 76 is the authoritative ratification
record.** Commit, push, merge, deployment, release, and production rollout
remain separately gated (Document 76 §16 / §17).

**Type:** Governance / implementation-authorization proposal (documentation
only — no source code, test, schema, migration, index, route, LangGraph
node, MongoDB collection, Redis usage, configuration, or frontend file
created or modified to produce it; Documents 67–74 read, not modified. The
only file this task creates is this document.

**Date:** 2026-09-06.

**Precedent / lineage.** This document follows the same proposal-then-
ratification pattern already established twice in this governance chain —
Document 70 (API contract proposal) preceded its ratification (Document
72); Document 73 (architecture decision pack) preceded its ratification
(Document 74). This document is the **third instance of that pattern**,
one governance step further down the chain: an **implementation-
authorization proposal**, preceding its own future, separate ratification.
It does not redesign or reinterpret Document 70, 73, or their ratification
records — it is bounded strictly to the question this stage of the ladder
asks: *is implementation now authorized against what is already ratified?*

---

## 0. What This Document Is and Is Not

**Is:** a proposed decision that, **if and when ratified by a separate
CTO act**, would authorize implementation of C-4 strictly within the scope
already fixed by Document 70 R4 (the ratified API contract) and Document
73 R1 (the ratified architecture) — including the bounded set of source
changes, tests, configuration, and documentation updates that
implementation requires, and an explicit list of what remains
unauthorized regardless.

**Is not:** an implementation authorization in itself (§16, §19); a
redesign or reinterpretation of Document 70, 73, or their ratification
records (Documents 72, 74); a resolution of Document 70's six Open
Contract Decisions or Document 73's four Open Architectural Questions
beyond the one bounded meta-question this document does resolve (§11); a
commit, push, merge, deployment, or release authorization (§16); an
architecture decision; a reopening of M14; a promotion of C-2; an
introduction of Durable Research Sessions; or authorization for any
unrelated frontend, cleanup, or evaluation-artifact work.

---

## 1. Document Metadata

| Field | Value |
|---|---|
| Document number | 75 |
| Title | M15 Implementation Authorization Decision — C-4 "What Changed Since Last Review" |
| Milestone | M15 = C-4 (Document 68 §4; Document 72 §5; Document 74 §6) |
| Governance stage | Implementation-authorization proposal — draft, pre-CTO-review |
| Predecessor gate | Document 74 — Document 73 R1 CTO Architecture Ratification Record (🟢 CTO-RATIFIED, 2026-09-06) |
| Successor gate (not created here) | CTO ratification of this decision, then a separate commit authorization, then a separate push/merge/deployment authorization |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Status / Authority

🟡 **PROPOSED — CTO DECISION REQUIRED. NOT RATIFIED. DOES NOT AUTHORIZE
IMPLEMENTATION.**

**Governance ladder — six explicitly distinct stages, restated here
because this document's entire purpose is to keep them from collapsing:**

| # | Stage | Status |
|---|---|---|
| 1 | Milestone selection | 🟢 CTO-RATIFIED (Document 68, via Document 69) — **M15 = C-4** |
| 2 | API contract ratification | 🟢 CTO-RATIFIED (Document 70 R4, via Document 72) |
| 3 | Architecture ratification | 🟢 CTO-RATIFIED (Document 73 R1, via Document 74) |
| 4 | **Implementation authorization** | 🟡 **PROPOSED HERE — NOT YET RATIFIED** |
| 5 | Commit authorization | NOT CREATED — a separate, later, distinct CTO act |
| 6 | Push / merge / deployment authorization | NOT CREATED — a separate, later, distinct CTO act |

None of stages 1–3 confers stage 4. Stage 4, even once ratified, confers
neither stage 5 nor stage 6. This document performs no stage beyond
*proposing* stage 4.

---

## 3. Governance Preconditions (verified this session, read-only)

| Fact | Source | Verified state |
|---|---|---|
| Document 67 | its own status | 🟢 CTO-RATIFIED — recommended C-4 |
| Document 68 | its own status | 🟢 CTO-RATIFIED via Document 69 — **M15 = C-4** formally selected |
| Document 69 | its own status | 🟢 CTO-RATIFIED — milestone-selection ratification |
| Document 70, Revision R4 | its own status, §1 | 🟢 CTO-RATIFIED via Document 72 — API contract fixed |
| Document 71 | historical | Blocked ratification review of an earlier, internally-inconsistent state of Document 70 — superseded by Document 72's successful ratification; not reinterpreted here |
| Document 72 | its own status | 🟢 CTO-RATIFIED — Document 70 R4 is the ratified M15 API contract |
| Document 73, Revision R1 | its own status | 🟢 CTO-RATIFIED via Document 74 — architecture fixed; AH-1 and AH-2 resolved |
| Document 74 | its own status | 🟢 CTO-RATIFIED — Document 73 R1 is the ratified M15 architecture; explicitly states implementation is NOT YET AUTHORIZED |
| Implementation authorization | Document 74 §18, §20 | **NONE proposed or ratified before this document.** This document is the implementation-authorization **proposal** — not yet reviewed, not ratified |

No governance state above is changed by this document. It is cited, not
re-decided. The only question genuinely open at this stage of the ladder
is the one this document proposes an answer to: whether implementation may
now proceed within the already-fixed contract and architecture.

---

## 4. Scope of Proposed Authorization

**If ratified, this decision would authorize implementation only for:**

**M15 — C-4 "What Changed Since Last Review,"** and **only** within the
boundaries already fixed by:

- Document 70, Revision R4 (the ratified API contract) — request/response
  shapes, citation shapes, state semantics, error taxonomy, job/SSE
  behavior, security boundaries; and
- Document 73, Revision R1 (the ratified architecture) — the two-engine
  design, AH-1's and AH-2's resolutions, the process-local deployment
  invariant, the orchestration and LLM-boundary decisions.

**This document does not extend, narrow, or reinterpret either.** Any
implementation detail not already fixed by Document 70 R4 or Document 73
R1 remains an ordinary engineering decision made during implementation,
not a new governance grant made here.

---

## 5. Modes (preserved exactly — no third v1 mode)

Implementation, if authorized, is scoped to **exactly the two ratified
modes**, mutually exclusive, one per request:

- **`period`** — financial changes.
- **`report`** — narrative changes.

**No third comparison mode (including the filing-to-filing mode Document
70's OCD-1 already declined to adopt) is authorized by this decision.** A
combined or mixed-mode request remains undefined and unauthorized.

---

## 6. Financial Implementation Boundary (preserved exactly from Document 73 R1)

If authorized, the `period`-mode implementation must:

- perform **deterministic computation only** — **no LLM involvement of any
  kind** in the financial comparison path;
- align metrics by **exact `Metric.provider_label` string equality** —
  **no invented canonical metric mapping**, no fuzzy matching, no new
  vocabulary-normalization layer;
- produce **deterministic citations** — the financial source shape
  (`{index, statement_type, period_end, metric}`) built directly from the
  two resolved statement identities, with no model-trust boundary
  involved;
- preserve the **Document 70 R4 financial citation contract exactly** —
  this shape is not altered, extended, or merged with the narrative shape.

**None of the above may be relaxed for implementation convenience.** If
implementation discovers a genuine obstacle to any of these boundaries,
that is a governance issue to raise separately (§11), not a license to
deviate silently.

---

## 7. Narrative Implementation Boundary (preserved exactly from Document 73 R1)

If authorized, the `report`-mode implementation must:

- operate over a **bounded, exactly-two-report evidence input**
  (`build_evidence_payload`, reused unmodified);
- issue **exactly one structured `chat_json` call** per request — no
  multi-pass generation, no additional LLM calls;
- produce a **bounded structured item list** — bounded in principle by the
  fixed evidence-payload size and the single call's own output-token
  budget (Document 73 R1 §10/§11), **not by a new, contract-visible
  `max_items` field**; this is an architectural bound, not a guaranteed
  application-level item-count ceiling;
- apply **deterministic per-item citation validation** — reusing
  `validate_and_map_citations`'s duplicate/undeclared-rejection logic,
  extended with the mandatory both-sides check below;
- enforce **mandatory baseline + current grounding, unweakened**: every
  emitted narrative item must cite at least one source mapping to the
  baseline report and at least one mapping to the current report; an item
  failing this check is dropped, never surfaced;
- preserve the **Document 70 R4 narrative citation contract exactly** —
  `{index, report_id, field}`, unmerged with the financial shape.

**No unbounded narrative-generation mechanism is authorized** — a design
that could produce an arbitrarily long item list without the bounds above
(e.g., iterative multi-call generation, or a mechanism that keeps
requesting more items until some external stop condition) is out of scope
for this authorization.

---

## 8. Process-Local Result Invariant (AH-2 — preserved exactly from Documents 73/74)

If authorized, implementation must preserve, without weakening or working
around, the deployment invariant Document 73 R1 §12.1/§12.2 established
and Document 74 §10 ratified:

- **Completed results exist only in the backend process that executed the
  job.** No mechanism may make a result reconstructible or visible from
  any other process.
- **Restart loss is accepted.** A process restart discarding an
  in-flight-retrievable result is correct, intended behavior — not a bug
  implementation should "fix" by adding persistence.
- **Cross-process `GET` is unsupported.** A `GET` reaching a different
  backend process than the one that ran the job must not be made to work.
- **No sticky-session workaround.** Implementation must not introduce
  load-balancer session affinity or any equivalent routing trick to paper
  over cross-process unavailability.
- **No Redis final-result persistence.** The existing `RedisEventBus`'s
  cross-process-capable trace-event transport (when `JOB_BACKEND=redis`)
  must not be extended, or repurposed, to carry the completed result
  payload cross-process.
- **No MongoDB final-result persistence.** No new collection, document
  shape, or write path for the completed `changes` payload is authorized.
- **No cross-process reconstruction** of a result by any other means
  (e.g., recomputing it on a different process on a cache-miss) —
  reconstruction is not a substitute for retention and is not authorized
  as a workaround.
- **SSE does not bypass this invariant.** The synthetic `final` frame
  remains constructed from the same process-local buffer as `GET`; it
  carries the identical constraint, not an exemption.

**This is the single most load-bearing boundary in this authorization.**
An implementation that quietly reaches for a shared store to make the
lifecycle "just work" across processes would violate this decision even
if every other boundary in this document were respected.

---

## 9. Infrastructure Boundaries (what this decision does not authorize introducing)

**Unless an already-authorized existing mechanism is required by Document
70 R4 or Document 73 R1** (§10 below enumerates what already qualifies),
this decision does **not** authorize introducing:

- any MongoDB schema, collection, index, or migration change;
- any Redis usage for result persistence (as distinct from the
  already-existing job-status/event-bus infrastructure, §10);
- any LangGraph involvement;
- any new durable research-session infrastructure, in any form;
- any frontend implementation;
- any deployment infrastructure change.

If implementation determines any of the above is genuinely necessary to
satisfy the ratified contract or architecture, that is a **governance
issue to raise separately** (via the normal schema-change/ADR chain
Document 70 §16 and Document 73 §12 both already name) — **not something
this decision pre-authorizes by implication.**

---

## 10. Existing Infrastructure Reuse (what this decision does authorize using, unmodified)

Where appropriate, and exactly as Document 73 R1 §6/§16 already specifies,
implementation **may** reuse the following already-existing, already-
authorized infrastructure and patterns from M14 and earlier milestones,
**without changing their existing behavior or contracts, except for the
explicitly authorized additive extensions stated here**:

- the existing async **job lifecycle** (`JobLifecycle`, `JobStore`,
  `EventBus`, the shared `MAX_ACTIVE_JOBS` admission budget) — extended
  only by the one additive `JobKind.CHANGE_BRIEF` enum member and the one
  additive `job_deadline_change_brief_s` settings entry Document 73 R1
  §16 already names;
- the existing **citation-validation** logic
  (`validate_and_map_citations`) as a building block for the new,
  per-item, both-sides check (§7);
- the existing **report-resolution query pattern**
  (`_resolve_authorized_reports`'s shape), extended with the additive
  `ticker`-match clause Document 73 R1 §10/§25 already identifies as a
  compatible extension, not a new mechanism;
- the existing **financial-statement read path** used by
  `GET /companies/{ticker}/financials`;
- the existing **observability patterns** (the `pipeline.<capability>`
  root-span convention, the `<capability>_runs_total{outcome}` counter
  convention, correlation-id logging) — §14;
- the existing **result-buffer mechanism** (the M14
  `_FILING_ANALYSIS_RESULTS` in-process, TTL-bounded pattern) as the
  concrete realization of AH-2 (§8);
- the existing **security boundaries** — SSRF guarding
  (`require_admin` + `assert_public_url`), BYOK contextvar threading, and
  the existing nine-class error taxonomy (§12).

**Reuse must not alter the ratified M14 or M15 contracts.** Any change to
an existing route, schema, or contract behavior outside C-4's own new
surface is out of scope for this authorization and would itself require
separate governance.

---

## 11. Open Decisions (preserved — not silently resolved, with one bounded exception stated explicitly)

**This decision does not resolve, reinterpret, or narrow any of Document
70's six Open Contract Decisions or Document 73's four Open Architectural
Questions**, with exactly **one bounded exception**, stated explicitly
below rather than left implicit.

### 11.1 The one meta-question this decision does resolve

**Bounded resolution**: *whether the existence of six unresolved OCDs and
four unresolved AAQs, by itself, blocks implementation authorization.*
This decision resolves that meta-question **no** — consistent with, and
not extending beyond, Document 70's own statement that none of its OCDs
"blocks contract ratification on its own" and Document 73's identical
framing for its AAQs. **This resolves nothing about the substance of any
individual OCD or AAQ** — each remains exactly as open as before; this
decision only confirms that their existence does not, by itself, prevent
implementation from proceeding within the boundaries already fixed
elsewhere in this document.

### 11.2 Contract-level Open Contract Decisions (Document 70 §22 — unchanged, not architecture's or implementation's to resolve)

| # | Question | Status |
|---|---|---|
| OCD-1 | Add a third, filing-to-filing `comparison_type`? | Still open. Not adopted. Not authorized by this decision. |
| OCD-2 | Add a `significance`/materiality label field? | Still open. Not adopted. |
| OCD-3 | Allow `current_*` to default rather than stay explicit? | Still open. Not adopted. |
| OCD-4 | Numeric value of the C-4 job deadline? | Still open at the governance level. Implementation will necessarily assign a concrete value as an operational parameter — this is an ordinary engineering decision made *during* implementation, not a governance resolution made *by* this document. |
| OCD-5 | Apply a §20.1-style evidence/validation gate to C-4? | Still open in specific design. |
| OCD-6 | Add a minimum-magnitude filter threshold for `period`-mode items? | Still open. Not adopted. |

### 11.3 Architecture-level Open Architectural Questions (Document 73 §24 — unchanged, not implementation's to resolve)

| # | Item | Status |
|---|---|---|
| AAQ-1 | Exact numeric value of `job_deadline_change_brief_s` | Same as OCD-4 above — an implementation-time operational parameter, not resolved here. |
| AAQ-2 | Exact prompt wording and model tier for `report`-mode generation | Implementation will necessarily choose specific wording and a tier — an ordinary engineering decision within the architecture's already-fixed boundaries (§7), not a governance resolution made here. |
| AAQ-3 | Future multi-instance deployment support | Still open, explicitly out of M15 scope (§8). Not authorized, not scheduled, not solved by this decision. |
| AAQ-4 | Whether OCD-5's validation gate is adopted for C-4 | Still open — a contract-level decision, not this document's to make. |

---

## 12. Security (preserved exactly — not weakened for implementation convenience)

If authorized, implementation must preserve, unweakened, every security
boundary Document 70 R4 and Document 73 R1 already establish:

- **SSRF protection** — `require_admin` + `assert_public_url`, applied
  identically to any custom BYOK provider/base URL, with no exception
  carved out for C-4.
- **BYOK boundaries** — the existing per-request `contextvar` threading,
  unmodified; `period` mode touches no BYOK context at all, since it makes
  no LLM call.
- **Input validation** — the discriminated request model's
  `comparison_type`-conditional field requirements, existence/ownership/
  ticker-match checks, and the existing 422/404 mapping (Document 70 §15),
  applied exactly as specified.
- **Authorization / ownership** — job records and report references
  owner-scoped exactly as every existing job kind and the existing
  `reports` ownership check already enforce; no relaxation of
  non-disclosure behavior (a foreign or nonexistent reference remains
  indistinguishable, 404).
- **Error handling** — the existing nine-class `domain/errors.py` taxonomy
  only; **zero new error classes** are authorized by this decision.

**No security control may be weakened, bypassed, or special-cased for C-4
implementation convenience.** Any perceived need to do so is a governance
issue to raise separately, not a license implementation may exercise
unilaterally.

---

## 13. Observability

If authorized, implementation must preserve and extend observability
consistent with Document 73 R1 §20:

- one root `pipeline.change_brief` span, with child spans per logical step
  (`resolve_references`, and either `compute_financial_delta` or
  `generate_narrative` + `validate_citations`);
- a new `change_brief_runs_total{outcome, comparison_type}` counter,
  following the existing `<capability>_runs_total{outcome}` naming
  precedent;
- correlation-id logging inherited automatically via the existing
  middleware — no new logging mechanism;
- no logging of BYOK material, raw provider responses on failure, or raw
  report/filing content beyond the existing discipline.

**Observability infrastructure must not become a substitute for, or a
variant of, result persistence.** A trace event, a log line, or a metric
label is not an authorized channel for reconstructing or retrieving a
completed job's result outside the process-local mechanism §8 describes —
using observability tooling to work around §8's invariant is explicitly
not authorized.

---

## 14. Testing / Evaluation Requirements (minimum, for implementation to be considered complete)

**This section defines the minimum testing floor implementation must
clear before it may be considered complete for the purposes of a future
commit-authorization request (§16).** It does not itself authorize
commit, and it does not claim that clearing this floor establishes
universal, production-grade correctness — only that the specific,
bounded properties below are verified.

- **Unit tests** (pure-function, hermetic style, per
  `test_comparison_explanation_pure.py`'s pattern): the financial-delta
  function's full eligibility rule — `changed`/`new`/`removed`
  classification, `percent_delta` null-on-zero/absent-baseline,
  unit-mismatch exclusion, currency-mismatch short-circuit, deterministic
  ordering — using in-memory fixtures only, no DB, no network.
- **Integration / contract tests** (hermetic fake-Mongo + real ASGI style,
  per `test_comparison_explanation_endpoint.py`/
  `test_filing_analysis_endpoint.py`'s pattern): the full
  `/api/companies/{ticker}/changes` route family for both modes — request
  validation, independent per-id ownership/ticker checks, create/status/
  stream/cancel lifecycle, and `complete`/`partial`/`insufficient_evidence`
  state transitions.
- **Deterministic financial comparison tests**: hand-authored
  `FinancialStatement` pairs covering every §6 case explicitly (changed,
  new, removed, unit mismatch, currency mismatch, zero baseline) — with
  bit-identical output asserted across repeated identical requests.
- **Narrative grounding / citation validation tests**: explicit assertions
  that (a) an item citing only one side is dropped and never surfaces, (b)
  zero groundable candidates yields `insufficient_evidence`, and (c) the
  narrative source shape never mixes with the financial source shape.
- **Process-local lifecycle tests** (Document 73 R1 §22's deployment-
  invariant tests, carried forward as a requirement here, not merely a
  suggestion): same-process completed-result `GET`; result expiration;
  post-restart unavailability (simulated via a fresh buffer instance);
  unsupported cross-instance behavior (simulated via two independent
  buffer instances); SSE `final`-frame behavior under the same invariant.
- **Regression coverage against relevant M14 behavior**: the route-
  inventory guard test is updated by exactly the four new C-4 routes, no
  more, no fewer, and the existing M14/M9.1 route family's own tests are
  confirmed unaffected (run, not modified) by C-4's additions.
- **Security / validation coverage**: BYOK/SSRF tests exercised
  identically to existing contracts (custom provider + non-admin → 403;
  custom `llm_base_url` → SSRF guard); ownership/non-disclosure tests for
  both job records and report references.
- **Evaluation evidence**: at minimum, a small set of golden-dataset cases
  for the `report`-mode narrative path (proposed `surface: "change_brief"`,
  per Document 73 R1 §22), run through the existing golden-dataset
  loader/adapter/case-evaluator framework unmodified, as evidence the
  narrative engine grounds claims as intended — this is evaluation
  evidence, not a per-request quality gate (§11.3, OCD-5/AAQ-4 remain
  separately open for whether a formal gate is ever adopted).

**This bounded suite does not, by itself, constitute a claim of universal
production-grade correctness.** It verifies the specific properties listed
above; anything beyond that scope (load behavior at production scale,
long-tail data-quality issues, adversarial inputs beyond what these tests
construct) is not claimed to be covered by clearing this floor.

---

## 15. Explicit Authorization Boundary — What This Decision Would Authorize, If Ratified

**If, and only if, this document is separately ratified by the CTO, that
ratification would authorize:**

- source-code implementation strictly within the M15/C-4 scope fixed by
  Document 70 R4 and Document 73 R1 (§4–§10 above), including the one
  additive `JobKind.CHANGE_BRIEF` domain-model enum member Document 73 R1
  §16 already names, and nothing broader;
- the corresponding tests described in §14;
- necessary, bounded configuration changes — specifically, the one
  additive `job_deadline_change_brief_s` settings entry Document 73 R1
  §16 already names, and nothing broader;
- necessary documentation updates directly supporting implementation
  (e.g., updating the route-inventory guard's documented list, or an
  implementation-notes addendum) — not new governance documents.

---

## 16. Explicit Non-Authorizations

**This decision — even once ratified — would NOT authorize:**

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
- contract changes outside an explicitly governed amendment process.

**Commit authorization and push/merge/deployment authorization remain two
further, separate, distinct CTO acts** (governance-ladder stages 5 and 6,
§2), neither created nor implied by this document, and neither creatable
by ratifying this document alone.

**And, restated because it is the single most important fact about this
document: creating Document 75 — this document itself — does not authorize
implementation.** Only a subsequent, separate CTO ratification of this
document would do that, and even that ratification would authorize
implementation only, not commit, push, merge, deployment, or release.

---

## 17. Repository / Governance Hygiene

This task creates exactly one new file. It does not modify:

- Documents 67–74 (all read, none modified);
- any unrelated workspace item, including the pre-existing, unrelated
  `web/features/workspace-home/ui/CompanySearch.test.tsx` modification;
- the unrelated, untracked M11 evidence directory
  (`backend/evaluation/self_consistency/phase_h1_generalization_matrix/`);
- the two unexplained, pre-existing untracked artifacts (`both`,
  `` current_period_end` ``) present in the working tree before this task
  began — not created by this task, not touched by it;
- any excluded frontend change;
- any unrelated evaluation artifact.

**Nothing is cleaned, deleted, staged, committed, or pushed by this
task.**

---

## 18. Governance Ladder (restated, not collapsed)

```text
Doc 67 (recommendation)              🟢 CTO-RATIFIED
  ↓
Doc 68 (milestone selection)         🟢 CTO-RATIFIED via Doc 69   — STAGE 1
  ↓
Doc 69 (selection ratification)      🟢 CTO-RATIFIED
  ↓
Doc 70 R4 (API contract)             🟢 CTO-RATIFIED via Doc 72   — STAGE 2
  ↓
Doc 71 (ratification review)         🔴 BLOCKED (historical — superseded)
  ↓
Doc 72 (API-contract ratification)   🟢 CTO-RATIFIED
  ↓
Doc 73 R1 (architecture pack)        🟢 CTO-RATIFIED via Doc 74   — STAGE 3
  ↓
Doc 74 (architecture ratification)   🟢 CTO-RATIFIED
  ↓
Doc 75 (THIS) — implementation       🟡 PROPOSED — pending CTO     — STAGE 4
              authorization decision     review, NOT YET RATIFIED
  ↓
Implementation authorization         NOT YET RATIFIED
  ↓
Implementation                       NOT AUTHORIZED
  ↓
Commit authorization                 NOT CREATED                  — STAGE 5
  ↓
Push / merge / deployment            NOT CREATED                  — STAGE 6
  authorization
```

This document performs exactly one act: **proposing** stage 4 for CTO
review. It does not perform, and does not imply, stage 4's ratification,
or any of stages 5–6.

---

## 19. Next Governance Gate

**The next legitimate governance action, if the CTO accepts this proposal,
is this document's own ratification** — a distinct act from drafting it —
recorded in a future, separate document (mirroring Document 72's
ratification of Document 70, and Document 74's ratification of Document
73). Only after that ratification may implementation begin. Even then, a
further, separate commit-authorization decision, and a further, separate
push/merge/deployment-authorization decision, remain required before any
code reaches `main` or a deployed environment.

---

## 20. Repository / Working-Tree State and Provenance

Recorded by read-only inspection this session. **This is a point-in-time
snapshot observed during the creation of this proposal on 2026-09-06**,
not a claim about repository state at any later reading time. **No `git`
mutation was performed** — no `add`/stage, no `commit`, no `push`, no
`amend`, no `rebase`, no `merge`, no `reset`, no `restore`, no `stash`, no
`clean`.

- `HEAD = origin/main = be4949b` (M14 implementation commit), unchanged.
- Document number 75 was verified free before creation (highest existing
  Backend & AI governance document was 74).
- Documents 67–74 were read, not modified. Their ratified content is
  cited, not amended, above.
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval/RAG code, MongoDB collection, Redis
  component, provider, configuration, infrastructure, or frontend file was
  created or modified. `.gitignore` was not modified.
- Known pre-existing, unrelated working-tree items were not staged,
  modified, renamed, or deleted:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/   (untracked, M11 evidence)
  ?? both                                                          (untracked, unexplained pre-existing artifact — not created by this task; not touched)
  ?? current_period_end`                                          (untracked, unexplained pre-existing artifact — not created by this task; not touched)
  ?? docs/backend_engineering/67_...md through 74_...md            (pre-existing untracked governance documents)
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/75_M15_Implementation_Authorization_Decision.md`).
  It is untracked and not yet version-controlled. Staging or committing it
  is a separate, subsequently CTO-authorized step.

---

**🟡 PROPOSED M15 IMPLEMENTATION AUTHORIZATION DECISION — DRAFT / PENDING
CTO REVIEW. NOT YET RATIFIED. CREATING THIS DOCUMENT DOES NOT AUTHORIZE
IMPLEMENTATION.** IF RATIFIED BY A SEPARATE, SUBSEQUENT CTO ACT, THIS
DECISION WOULD AUTHORIZE C-4 IMPLEMENTATION STRICTLY WITHIN THE RATIFIED
DOCUMENT 70 R4 API CONTRACT AND RATIFIED DOCUMENT 73 R1 ARCHITECTURE —
EXACTLY THE TWO MUTUALLY EXCLUSIVE MODES (`period`, `report`), NO THIRD
MODE; THE DETERMINISTIC, LLM-FREE FINANCIAL PATH WITH NO INVENTED
CANONICAL METRIC MAPPING; THE BOUNDED, SINGLE-`chat_json`-CALL NARRATIVE
PATH WITH MANDATORY, UNWEAKENED BASELINE+CURRENT GROUNDING; AND THE
PROCESS-LOCAL RESULT INVARIANT (AH-2) UNWEAKENED — NO CROSS-PROCESS `GET`,
NO STICKY SESSIONS, NO REDIS OR MONGODB FINAL-RESULT PERSISTENCE, NO
CROSS-PROCESS RECONSTRUCTION, SSE INCLUDED. EXISTING M14/M9.1
INFRASTRUCTURE (JOB LIFECYCLE, CITATION VALIDATION, OBSERVABILITY, THE
IN-PROCESS RESULT BUFFER, SECURITY/SSRF/BYOK BOUNDARIES) MAY BE REUSED
UNMODIFIED. ALL SIX OPEN CONTRACT DECISIONS (OCD-1 THROUGH OCD-6) AND ALL
FOUR OPEN ARCHITECTURAL QUESTIONS (AAQ-1 THROUGH AAQ-4) REMAIN EXPLICITLY
UNRESOLVED, WITH ONLY ONE BOUNDED META-QUESTION RESOLVED (THEIR EXISTENCE
DOES NOT BLOCK IMPLEMENTATION AUTHORIZATION). A MINIMUM TESTING FLOOR (§14)
IS REQUIRED BEFORE IMPLEMENTATION MAY BE CONSIDERED COMPLETE, WITHOUT
CLAIMING UNIVERSAL PRODUCTION-GRADE CORRECTNESS. THIS DECISION — EVEN ONCE
RATIFIED — WOULD NOT AUTHORIZE COMMIT, PUSH, MERGE, DEPLOYMENT, RELEASE,
PRODUCTION ROLLOUT, UNRELATED CLEANUP, M14 REOPENING, C-2 PROMOTION, DRS
IMPLEMENTATION, UNRELATED FRONTEND WORK, ARCHITECTURAL REDESIGN, OR
CONTRACT CHANGES OUTSIDE A GOVERNED AMENDMENT. DOCUMENTS 67–74 WERE NOT
MODIFIED. NO SOURCE, TEST, SCHEMA, CONFIGURATION, OR INFRASTRUCTURE FILE
WAS CREATED OR MODIFIED. NO STAGE. NO COMMIT. NO PUSH. NO MERGE / REBASE /
RESET / AMEND. THE NEXT LEGITIMATE GOVERNANCE ACTION IS CTO REVIEW AND
RATIFICATION OF THIS PROPOSAL — NOT IMPLEMENTATION.**
