# 74 — Document 73 Revision R1 CTO Architecture Ratification Record

**Status:** 🟢 **DOCUMENT 73, REVISION R1 — CTO ARCHITECTURE RATIFIED.**
This document records the CTO's ratification of
[73_M15_Architecture_Decision_Pack.md](73_M15_Architecture_Decision_Pack.md)
**at Revision R1** — the latest, and only, revision present in the
repository. It is a **separate governance act**, distinct from Document 73
itself: it ratifies the architecture Document 73 already proposed — it
does not perform the architecture design (Document 73 already did that),
it does not redesign C-4, and it does not reinterpret Document 70, 71, or
72. **The ratified decision is: Document 73, Revision R1, is the ratified
M15 C-4 architecture.** Architecture ratification authorizes progression
to a future, **separate implementation-authorization decision only** — it
does **not**, itself, authorize implementation (§18).

**Type:** Governance / architecture ratification decision record
(documentation only — no source code, test, schema, migration, index,
route, LangGraph node, MongoDB collection, Redis usage, or provider change
created or modified to produce it; Document 73 and Documents 67–72 read,
not modified. The only file this task creates is this document.

**Date:** 2026-09-06.

**Precedent / lineage.** This record follows the same standalone
decision-record form
[72_Document70_R4_CTO_Ratification_Record.md](72_Document70_R4_CTO_Ratification_Record.md)
established for ratifying a prior document without modifying it — applied
one governance step further down the chain, ratifying an **architecture
decision pack** (Document 73) rather than an **API contract** (Document
70). This record performs exactly one governance act: ratifying Document
73 Revision R1 as the M15 C-4 architecture. It does not reinterpret
Document 71 (the historical blocked API-contract ratification review) or
Document 72 (the API-contract ratification) — both are cited, not amended.

---

## 1. Document Metadata

| Field | Value |
|---|---|
| Document number | 74 |
| Title | Document 73 Revision R1 CTO Architecture Ratification Record |
| Ratifies | Document 73 — M15 Architecture Decision Pack — C-4 "What Changed Since Last Review" |
| Ratified revision | **Revision R1** (exact — no later revision exists or is claimed) |
| Milestone | M15 = C-4 (Document 68 §4; Document 72 §5) |
| Governance stage | Architecture ratification (this act) |
| Predecessor gate | Document 73 R1, CTO-reviewed, approved for architecture ratification |
| Related prior records | Document 71 (historical, blocked API-contract ratification review — not modified, not reinterpreted); Document 72 (Document 70 R4 API-contract ratification — not modified, not reinterpreted) |
| Successor gate (not created here) | A separate, future implementation-authorization decision |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Exact Architecture Ratification Target

**Target: Document 73 — M15 Architecture Decision Pack — C-4 "What Changed
Since Last Review," Revision R1.**

Verified this session, read-only, before recording this ratification:

- Document 73's top-line Status banner reads: *"🟠 M15 ARCHITECTURE
  DECISION PACK — DRAFT / PENDING CTO REVIEW (REVISION R1)."*
- Document 73 carries exactly one revision-note block, **Revision R1**
  (dated 2026-09-06, a targeted correction addressing AH-2's deployment
  invariant and AH-1's output-bound clarification following CTO review).
  **No `Revision R2` block exists anywhere in the file.**
- `docs/backend_engineering/` was listed in full: the highest-numbered
  file prior to this task was `73_M15_Architecture_Decision_Pack.md`. No
  second Document-73-shaped file, and no Document 73 revision beyond R1,
  exists anywhere in the repository.
- `git status --short` shows Document 73 as untracked (never committed) —
  there is no commit history suggesting a superseding revision was ever
  pushed elsewhere.

**No discrepancy was found. Revision R1 is confirmed as the correct and
only architecture-ratification target.** This record ratifies Revision R1
exactly, and makes no claim about, and does not ratify, any revision
beyond R1. If a Revision R2 is later introduced, it requires its own,
separate CTO review and ratification; this record does not, and cannot,
extend to it.

---

## 3. R1 Provenance

Document 73 was first drafted (no revision marker) as the initial M15
Architecture Decision Pack, then revised once, to **Revision R1**, in a
targeted correction pass following CTO review. That correction:

1. Made AH-2's process-locality an **explicit, stated deployment
   invariant** (§12.1 of Document 73) rather than a deferred operational
   concern.
2. Clarified that `RedisEventBus`'s cross-process-capable trace-event
   transport does **not** lift that invariant, because the SSE `final`
   frame's payload is still constructed from the same process-local result
   buffer (§12.2 of Document 73).
3. Clarified that `report`-mode's generated item list is bounded in
   principle by the existing evidence-payload size and the model's
   output-token budget, without fixing a new hard numeric cap (§10, §11 of
   Document 73).
4. Added explicit architecture-level test requirements for the deployment
   invariant (§22 of Document 73).
5. Reframed the contract-impact conclusion (§25 of Document 73) to
   distinguish Document 70's internal coherence from the deployment
   invariant the chosen AH-2 mechanism introduces — without proposing any
   change to Document 70.

This record ratifies Document 73 **as corrected by Revision R1** — the
pre-R1 draft is not a separate ratification target.

---

## 4. Governance Lineage

| Document | Role | Governance act performed |
|---|---|---|
| **Document 67** | Post-M14 Backend & AI Roadmap Reconciliation | **Recommendation.** C-4 recommended. |
| **Document 68** | Formal M15 Milestone Selection Record | **Milestone selection.** M15 = C-4 formally selected. |
| **Document 69** | Document 68 CTO Ratification Record | **Milestone-selection ratification.** |
| **Document 70 (R1→R4)** | M15 API Contract Proposal | **API contract.** |
| **Document 71** | Document 70 CTO Ratification Review | **Historical blocked ratification review** — found Document 70's governance-status markers self-contradictory; did not ratify. Not modified, not superseded, not reinterpreted here. |
| **Document 72** | Document 70 Revision R4 CTO Ratification Record | **API-contract ratification.** Document 70 R4 ratified as the M15 = C-4 API contract. Not modified, not reinterpreted here. |
| **Document 73 (R1)** | M15 Architecture Decision Pack | **Architecture decision pack.** Proposes how the ratified API contract is realized; resolves AH-1 and AH-2. |
| **Document 74 (THIS)** | Document 73 Revision R1 CTO Architecture Ratification Record | **Architecture ratification.** The distinct act that ratifies Document 73 R1 as the M15 C-4 architecture. |

These eight roles are not interchangeable and this record does not
conflate them. In particular: **Document 74 is an architecture
ratification, not an implementation authorization** (§18) — a further,
separate, subsequent CTO act that this record does not perform and does
not imply.

---

## 5. CTO Architecture-Review Decision

The CTO has reviewed Document 73 at Revision R1 and issued: **🟢 DOCUMENT
73 REVISION R1 — APPROVED FOR ARCHITECTURE RATIFICATION.** This document
records that ratification. Review confirmed:

- the two-mode architecture (`period`/`report`) is preserved and remains
  mutually exclusive, with no third mode introduced (§7);
- AH-1 and AH-2 are resolved as Document 73 R1 states, not differently
  (§8, §9);
- the AH-2 deployment invariant is stated explicitly and is preserved,
  not weakened (§10);
- no new persistence, Redis usage, or LangGraph involvement is introduced
  beyond what Document 73 R1 already proposes (§11, §12);
- Document 70 R4 (the ratified API contract) is treated as frozen input,
  not reopened or reinterpreted (§17).

---

## 6. Architecture Ratification Decision

**🟢 DOCUMENT 73, REVISION R1 — CTO ARCHITECTURE RATIFIED.**

**Document 73 Revision R1 is formally ratified as the M15 C-4
architecture.** This confirms the architecture position already recorded
in Document 73 R1's §§3–26. It does **not** re-derive, redesign, or extend
that architecture, and it does **not** authorize implementation (§18).

**Separately and explicitly: M15 implementation is NOT YET AUTHORIZED.**
Architecture ratification and implementation authorization are two
distinct, sequential CTO acts; this record performs only the first.

---

## 7. Ratified Architectural Scope

### 7.1 Two-mode architecture (preserved exactly)

C-4 supports **exactly two mutually exclusive comparison modes**:

- **`period`** → financial comparison, `"financial"`-category items only.
- **`report`** → narrative comparison, `"narrative"`-category items only.

**No third comparison mode is introduced by this ratification.** A single
request evaluates exactly one mode; the shared orchestration shell (one
`JobKind`, one route family, one response envelope) handles both, while
the domain comparison logic stays fully separate (Document 73 §13,
ratified unchanged).

### 7.2 Existing infrastructure reuse (preserved, not expanded)

The justified reuse Document 73 R1 identifies is ratified as-is: the
existing `JobLifecycle`/`JobStore`/`EventBus` async-job infrastructure, the
`agents/comparison_explanation.py` evidence-extraction and
citation-validation machinery, the `agents/llm.py` `chat_json` boundary,
the existing error taxonomy, and the existing observability conventions.
**This ratification does not authorize any change to the reused
components themselves**, and does not extend reuse into any unrelated
architectural change beyond what Document 73 R1 specifies.

---

## 8. AH-1 Ratification — Financial and Narrative Comparison Mechanisms

**AH-1 is ratified exactly as Document 73 R1 resolves it — not
differently.**

### 8.1 Financial path (`period` mode) — ratified

- **Deterministic, pure where applicable, LLM-free.** The financial-delta
  computation involves no model call of any kind.
- **Based on the existing `Metric.provider_label` identity** — exact
  string-equality matching only; `Metric.canonical_metric` remains `null`
  for every metric today. **No new canonical financial ontology is
  introduced or authorized.** Provider relabeling across periods remains a
  documented, accepted limitation, not solved by this architecture.
- **Deterministic citation construction** — the financial source shape
  (`{index, statement_type, period_end, metric}`) is self-evidencing,
  built directly from the two resolved statement identities; no model is
  involved in producing or validating it.
- **Bounded** per Document 73 R1's own constraints: at most two document
  reads, one eligibility pass over the aligned metric maps — no
  unbounded computation.
- **This ratification does not introduce an LLM into the deterministic
  financial computation** merely because C-4 is an AI product — Document
  73 R1's explicit reasoning for LLM-free financial comparison (its §14
  LLM Boundary) is preserved unchanged.

### 8.2 Narrative path (`report` mode) — ratified

- **Bounded two-report evidence** — `build_evidence_payload`, reused
  unmodified, called with exactly `[baseline_report, current_report]`.
- **Structured comparison via one `chat_json` call**, as Document 73 R1
  defines — no additional LLM call, no two-pass generation.
- **Structured item output** — a new, list-shaped Pydantic schema
  requesting discrete claims directly from the model (the AH-1 mechanism
  resolution itself, §9 below), not a decomposition of a single generated
  narrative.
- **Deterministic per-item citation validation** — reusing
  `validate_and_map_citations`'s duplicate/undeclared-rejection logic as a
  building block, extended with a new per-item both-sides check.
- **Mandatory baseline + current grounding, unweakened**: every narrative
  item must cite at least one source mapping to the baseline report and at
  least one mapping to the current report. **This ratification does not
  weaken this requirement in any way.**

### 8.3 AH-1 output boundedness — ratified

The narrative item list has an **architectural finite bound** through:

- the bounded, fixed-size (2-report) evidence input; and
- the single `chat_json` call's own model output-token budget /
  structured-output constraints.

**This ratification does not introduce a new contract-visible `max_items`
field** — no such field exists in Document 70, and none is added here.
**This bound is architectural, not a deterministic application-level
item-count guarantee** — it constrains the list from growing without
limit as a consequence of bounded inputs and a bounded single model call,
but it is not equivalent to a hard, enforced numeric ceiling on item
count. This distinction, as Document 73 R1 itself draws it, is preserved
exactly.

---

## 9. AH-2 Ratification — Job-Result Retention Mechanism

**AH-2 is ratified exactly as Document 73 R1 resolves it: the M14
in-process, TTL-bounded, non-durable result buffer pattern
(`_FILING_ANALYSIS_RESULTS` precedent). No new MongoDB collection, no new
Redis usage, no new caching layer is introduced or authorized.**

This mechanism was chosen, and remains ratified, because it requires zero
new schema/collection/index/migration governance, avoids a new Redis
caching layer this task is not authorized to add, and directly mirrors the
most recent, most analogous shipped precedent (M14). The rejected
alternatives — a durable Mongo collection (M9.1-style) and a new
Redis-backed cache — remain rejected for the reasons Document 73 R1 §12
states; this ratification does not reopen that choice.

---

## 10. Deployment Invariant (critical — preserved exactly, not weakened)

**The completed C-4 result exists only in the backend process that
executed the job.** This ratification preserves, verbatim in substance,
Document 73 R1 §12.1/§12.2's explicit invariant:

- **`POST → job → result → GET` must remain process-local.** A completed
  job's result is retrievable only from the one backend process that ran
  it.
- **Cross-process `GET` is unsupported.** A `GET` request routed to a
  different backend process than the one that ran the job cannot
  retrieve the result — there is no cross-process lookup path.
- **Backend restart may lose the completed result.** This is accepted,
  intended behavior of the ratified mechanism, not a defect.
- **Horizontal multi-instance deployment for this lifecycle is outside
  M15 scope.** This ratification does not extend M15 to support it.
- **SSE must respect the same result-buffer invariant.** The SSE `final`
  frame's payload is constructed from the same process-local buffer as
  `GET` — it carries the identical constraint, not an exemption from it.
- **Redis trace/event capability must not be interpreted as cross-process
  final-result persistence.** `RedisEventBus`'s cross-process-capable raw
  trace-event delivery (when `JOB_BACKEND=redis` is configured) does
  **not** mean the completed result payload is available cross-process —
  the result payload and the trace-event stream are retained by two
  different mechanisms with two different scopes, and only the trace
  events are cross-process-capable.

**This ratification does not weaken or reinterpret this invariant in any
way.** It does not introduce sticky sessions, Redis-backed final-result
persistence, or MongoDB persistence to work around it. If horizontal
multi-instance support for this lifecycle is ever required, that is a
**separate, future architecture decision** (Document 73 R1's AAQ-3, §16
below) — not solved, and not pre-empted, by this ratification.

---

## 11. Persistence / State Boundary

**Ratified exactly as Document 73 R1 §15 states:** C-4 requires no new
durable persistence. It reads two existing, already-persisted collections
(`reports`, `financial_statements`) read-only. The only retained state is
the process-local, bounded, TTL-limited, transient job-result retention
described in §10 above.

**This ratification does not introduce:**

- Durable Research Sessions, in any form;
- user research history;
- last-visit state;
- durable C-4 comparison state;
- MongoDB persistence beyond the existing, unmodified `reports`/
  `financial_statements` reads;
- Redis result persistence.

**Future scalability work remains future work.** Document 73 R1's AAQ-3
(whether a future multi-instance deployment requires a mechanism lifting
§10's invariant) is retained as an explicitly open, unresolved item — this
ratification does not solve it, does not schedule it, and does not
authorize any work toward it.

---

## 12. Orchestration Decision

**Ratified exactly as Document 73 R1 §13/§14 states: ordinary asynchronous
service orchestration — no LangGraph.** One top-level orchestration
function branches on `comparison_type` into the two independent
comparison engines; both share only the outer orchestration shell (job
lifecycle calls, route handlers, response-envelope assembly, error
mapping), never the domain comparison logic. This ratification does not
add LangGraph merely because it exists in the platform's preferred stack —
Document 73 R1's reasoning (no multi-step agentic reasoning exists to
justify it; both `comparison_explanation.py` and `filing_analysis.py`
already establish the out-of-graph precedent for single-call surfaces) is
preserved unchanged.

---

## 13. LLM Boundary

**Ratified exactly as Document 73 R1 §14 states:**

- **`period` mode: no LLM, ever.** Confirmed and preserved (§8.1 above).
- **`report` mode: exactly one `chat_json` call per request**, against the
  new structured list-output schema, with deterministic preprocessing
  (`build_evidence_payload`) and deterministic post-generation validation
  (per-item citation checks) bracketing the one point where model
  reasoning occurs. Retry/failure behavior reuses the existing
  `chat_json` mechanism unmodified; no new retry policy is introduced.

---

## 14. Validation / Evidence / Citation Boundary

**Ratified exactly as Document 73 R1 §17 (validation), §9–§10 (evidence and
citation) state, with no silent alteration of Document 70's contract:**

- **Contract validation** (request shape, comparison-reference existence/
  ownership/ticker-match, per-item citation validation, evidence
  completeness) is deterministic and runs on every request, distinct from
  **model-quality evaluation** (the offline golden-dataset and, if later
  adopted, self-consistency frameworks), which never gates an individual
  request.
- **Baseline/current grounding** — every narrative item must be grounded
  on both sides (§8.2 above); financial items are self-evidencing,
  requiring no model-trust boundary at all.
- **Deterministic financial evidence** — citations for `period`-mode items
  are constructed directly from the resolved statement identities, not
  claimed or validated against a model's assertion.
- **Model-output validation** — malformed JSON is rejected at the
  `chat_json`/Pydantic parsing layer; semantic (citation) validation is
  the separate, deterministic step described in §8.2.

---

## 15. Security / Observability Boundary

**Ratified exactly as Document 73 R1 §19 (security) and §20
(observability) state — no new security behavior is introduced beyond
what R1 already establishes:**

- **SSRF boundaries**: `require_admin` + `assert_public_url`, reused
  unmodified for any custom BYOK provider/base URL.
- **BYOK boundaries**: the existing per-request `contextvar` threading,
  reused unmodified; `period` mode never touches BYOK context at all.
- **Untrusted content / prompt-injection posture**: report
  `extracted_data`/`sentiment_analysis` content remains untrusted data fed
  to the model, never treated as instruction — the same posture Document
  70 and Document 64 already establish.
- **Secret handling**: no BYOK material, raw provider responses on
  failure, or raw report/filing content beyond existing discipline is
  logged.
- **Observability**: one root `pipeline.change_brief` span with per-step
  child spans; a new `change_brief_runs_total{outcome, comparison_type}`
  counter following the existing `<capability>_runs_total{outcome}`
  naming precedent; correlation-id logging inherited automatically. No
  new instrumentation beyond what Document 73 R1 specifies is
  introduced or authorized.

---

## 16. Open Decisions and Future Work (preserved unresolved — not silently decided)

**This ratification does not resolve, and explicitly preserves as open,
every item Document 73 R1 itself leaves open:**

### 16.1 Contract-level Open Contract Decisions (Document 70 §22 — not architecture's to resolve)

| # | Question | Status after this ratification |
|---|---|---|
| **OCD-1** | Add a third, filing-to-filing `comparison_type`? | Still open. Not adopted. |
| **OCD-2** | Add a `significance`/materiality label field? | Still open. Not adopted. |
| **OCD-3** | Allow `current_*` to default rather than stay explicit? | Still open. Not adopted. |
| **OCD-4** | Numeric value of the C-4 job deadline? | Still open — operational tuning. |
| **OCD-5** | Apply a §20.1-style evidence/validation gate to C-4? | Still open in specific design. |
| **OCD-6** | Add a minimum-magnitude filter threshold for `period`-mode items? | Still open. Not adopted. |

### 16.2 Open Architectural Questions (Document 73 §24 — architecture-level, not resolved by this ratification)

| # | Item | Status after this ratification |
|---|---|---|
| **AAQ-1** | Exact numeric value of `job_deadline_change_brief_s` | Still open — implementation-time operational tuning. |
| **AAQ-2** | Exact prompt wording and model tier for `report`-mode generation | Still open — implementation detail. |
| **AAQ-3** | If/when M15 must support horizontal multi-instance deployment for the `POST → GET` lifecycle, what mechanism lifts the §10 invariant | Still open — explicitly scoped out of M15 by this architecture; remains future work, not solved here. |
| **AAQ-4** | Whether OCD-5's validation gate is adopted for C-4 | Still open — a contract-level decision, not architecture's to make. |

**This ratification explicitly does NOT:**

- silently resolve OCD-1 through OCD-6;
- resolve AH-1 or AH-2 any differently than Document 73 R1 already does;
- convert AAQ-3 (future multi-instance scalability work) into current
  architecture — it remains future work, explicitly deferred.

---

## 17. Explicit Contract Boundary

**Document 70, Revision R4, is already ratified (Document 72) and is
treated here as a frozen, non-negotiable input.** Document 73 R1 is the
architecture realizing that contract; this ratification confirms the
architecture, not the contract. **Architecture ratification does NOT
authorize modification of Document 70.**

Document 73 R1's own contract-impact assessment (§25) found Document 70's
contract internally coherent, with no insufficiency or contradiction —
this ratification confirms that finding. **If any architectural issue were
found that would require changing the ratified contract, this record would
name it as a governance boundary/problem rather than change the contract.**
No such issue exists: AH-1 and AH-2 are both resolved without requiring
any change to Document 70, and the one implementation-level nuance
Document 73 R1 records (a `ticker`-match clause needed in the report-
resolution query) is a compatible extension of an existing query shape,
not a contract gap.

---

## 18. Explicit Implementation Non-Authorization

**Architecture ratification does not constitute implementation
authorization.** This record does NOT authorize:

- application code changes;
- production implementation;
- test implementation;
- MongoDB schema creation;
- MongoDB migration;
- Redis implementation;
- LangGraph implementation;
- frontend implementation;
- deployment;
- release;
- commit;
- push;
- merge.

**Implementation requires a separate, explicit authorization decision
after architecture ratification. Commit and push remain separate, later
gates.** Nothing in this record advances any stage beyond architecture
ratification itself.

---

## 19. Governance Ladder

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
Architecture ratification                  🟢 THIS DOCUMENT (74)
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
Doc 67 (recommendation)          🟢 CTO-RATIFIED
  ↓
Doc 68 (milestone selection)     🟢 CTO-RATIFIED via Doc 69
  ↓
Doc 69 (selection ratification)  🟢 CTO-RATIFIED
  ↓
Doc 70 R4 (API contract)         🟢 CTO-RATIFIED via Doc 72
  ↓
Doc 71 (ratification review)     🔴 BLOCKED (historical — superseded by Doc 72's success)
  ↓
Doc 72 (API-contract ratification) 🟢 CTO-RATIFIED
  ↓
Doc 73 R1 (architecture pack)    🟠 → CTO-reviewed, approved for architecture ratification
  ↓
Doc 74 (THIS)                    🟢 CTO ARCHITECTURE RATIFIED
  ↓
STOP — no downstream gate authorized by this record
  ↓
Implementation authorization decision   (NOT created here — a future, separate CTO act)
  ↓
Implementation / commit / push          (NOT authorized)
```

This record performs exactly one stage: **architecture ratification.** It
is not used as a substitute for, or a shortcut past, implementation
authorization or any later stage. **Document 74 does not become an
implementation-authorization record.**

---

## 20. Next Gate

**The next legitimate governance action is a separate, explicit
implementation-authorization decision** — a distinct act from this
ratification — followed by implementation, then commit, then push, each a
distinct CTO act, none collapsed. **M15 implementation is NOT YET
AUTHORIZED.**

---

## 21. Repository / Document Provenance

Recorded by read-only `git` inspection this session. **This is a
point-in-time snapshot observed during the creation of this record on
2026-09-06**, not a claim about repository state at any later reading
time. **No `git` mutation was performed** — no `add`/stage, no `commit`,
no `push`, no `amend`, no `rebase`, no `merge`, no `reset`, no `restore`,
no `stash`, no `clean`.

- `HEAD = origin/main = be4949b` (M14 implementation commit), unchanged.
- Document number 74 was verified free before creation (highest existing
  Backend & AI governance document was 73; no Document 74 existed prior to
  this task).
- **Document 73 was read at Revision R1, not modified.** No Revision R2
  exists (§2).
- **Document 71 was read, not modified.** It remains the accurate
  historical record of the blocked API-contract ratification review — not
  superseded, not retracted, not reinterpreted.
- **Document 72 was read, not modified.** It remains the accurate record
  of Document 70 R4's API-contract ratification — not reinterpreted.
- Documents 67, 68, 69, and 70 were read, not modified. They remain 🟢
  CTO-RATIFIED (or, for Document 70, corrected and ratified) and are
  cited, not reinterpreted.
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
  ?? both                                                          (untracked, unexplained pre-existing artifact — not created by this task; not touched)
  ?? current_period_end`                                          (untracked, unexplained pre-existing artifact — not created by this task; not touched)
  ?? docs/backend_engineering/67_Post_M14_Backend_AI_Roadmap_Reconciliation.md
  ?? docs/backend_engineering/68_M15_Formal_Milestone_Selection_Record.md
  ?? docs/backend_engineering/69_Document68_CTO_Ratification_Record.md
  ?? docs/backend_engineering/70_M15_What_Changed_API_Contract_Proposal.md
  ?? docs/backend_engineering/71_Document70_CTO_Ratification_Record.md
  ?? docs/backend_engineering/72_Document70_R4_CTO_Ratification_Record.md
  ?? docs/backend_engineering/73_M15_Architecture_Decision_Pack.md
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/74_Document73_R1_CTO_Architecture_Ratification_Record.md`).
  It is **untracked and not yet version-controlled.** Staging or
  committing it is a separate, subsequently CTO-authorized step.

---

**🟢 DOCUMENT 73, REVISION R1 — CTO ARCHITECTURE RATIFIED. THIS RECORD
RATIFIES THE M15 C-4 ARCHITECTURE AT REVISION R1 EXACTLY, AND MAKES NO
CLAIM ABOUT ANY REVISION BEYOND R1 — NO REVISION R2 EXISTS IN THE
REPOSITORY. THE TWO-MODE ARCHITECTURE (`period` FINANCIAL, `report`
NARRATIVE) REMAINS MUTUALLY EXCLUSIVE WITH NO THIRD MODE. AH-1 IS RATIFIED:
THE FINANCIAL PATH IS DETERMINISTIC, LLM-FREE, BASED ON THE EXISTING
`Metric.provider_label` IDENTITY WITH NO INVENTED CANONICAL ONTOLOGY; THE
NARRATIVE PATH USES BOUNDED TWO-REPORT EVIDENCE, ONE STRUCTURED
`chat_json` CALL, DETERMINISTIC PER-ITEM CITATION VALIDATION, AND
MANDATORY, UNWEAKENED BASELINE+CURRENT GROUNDING; THE OUTPUT LIST IS
ARCHITECTURALLY BOUNDED BY EVIDENCE SIZE AND MODEL TOKEN BUDGET, NOT BY A
NEW CONTRACT FIELD, AND THIS IS NOT A DETERMINISTIC ITEM-COUNT GUARANTEE.
AH-2 IS RATIFIED: JOB-RESULT RETENTION REUSES THE M14 IN-PROCESS,
TTL-BOUNDED BUFFER — NO NEW MONGODB COLLECTION, NO NEW REDIS USAGE. THE
DEPLOYMENT INVARIANT IS PRESERVED EXACTLY, NOT WEAKENED: THE COMPLETED
RESULT EXISTS ONLY IN THE BACKEND PROCESS THAT EXECUTED THE JOB;
`POST → GET` MUST REMAIN PROCESS-LOCAL; CROSS-PROCESS `GET` IS
UNSUPPORTED; A RESTART MAY LOSE THE RESULT; HORIZONTAL MULTI-INSTANCE
DEPLOYMENT FOR THIS LIFECYCLE IS OUTSIDE M15 SCOPE; SSE RESPECTS THE SAME
INVARIANT; REDIS TRACE/EVENT CROSS-PROCESS CAPABILITY IS NOT CROSS-PROCESS
FINAL-RESULT PERSISTENCE. NO STICKY SESSIONS, NO REDIS-BACKED
FINAL-RESULT PERSISTENCE, AND NO MONGODB PERSISTENCE ARE INTRODUCED. NO
LANGGRAPH INVOLVEMENT — ORDINARY SERVICE ORCHESTRATION IS RATIFIED. NO
DURABLE RESEARCH SESSIONS, USER HISTORY, LAST-VISIT STATE, OR DURABLE C-4
COMPARISON STATE ARE INTRODUCED. DOCUMENT 70'S RATIFIED CONTRACT IS TREATED
AS FROZEN AND IS NOT MODIFIED, NOT REOPENED, AND NOT REINTERPRETED. ALL SIX
OPEN CONTRACT DECISIONS (OCD-1 THROUGH OCD-6) AND ALL FOUR OPEN
ARCHITECTURAL QUESTIONS (AAQ-1 THROUGH AAQ-4), INCLUDING FUTURE
MULTI-INSTANCE SCALABILITY WORK (AAQ-3), REMAIN EXPLICITLY UNRESOLVED AND
ARE NOT CONVERTED INTO CURRENT ARCHITECTURE BY THIS RATIFICATION.
**SEPARATELY AND EXPLICITLY: M15 IMPLEMENTATION IS NOT YET AUTHORIZED.**
THIS RECORD DOES NOT AUTHORIZE APPLICATION CODE CHANGES, PRODUCTION
IMPLEMENTATION, TEST IMPLEMENTATION, MONGODB SCHEMA CREATION OR MIGRATION,
REDIS IMPLEMENTATION, LANGGRAPH IMPLEMENTATION, FRONTEND IMPLEMENTATION,
DEPLOYMENT, RELEASE, COMMIT, PUSH, OR MERGE. DOCUMENTS 67–73 WERE NOT
MODIFIED. NO SOURCE, TEST, SCHEMA, OR INFRASTRUCTURE FILE WAS CREATED OR
MODIFIED. NO STAGE. NO COMMIT. NO PUSH. NO MERGE / REBASE / RESET / AMEND.
THE NEXT LEGITIMATE GOVERNANCE ACTION IS A SEPARATE, EXPLICIT
IMPLEMENTATION-AUTHORIZATION DECISION — NOT IMPLEMENTATION ITSELF.**
