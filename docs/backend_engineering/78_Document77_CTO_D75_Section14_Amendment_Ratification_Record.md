# 78 — Document 77 CTO D75 §14 Amendment Ratification Record

**Status:** 🟢 **CTO-RATIFIED — DOCUMENT 77.** This document records the
CTO's ratification of
[77_D75_Section14_Testing_Floor_Clarification_and_Amendment_Decision.md](77_D75_Section14_Testing_Floor_Clarification_and_Amendment_Decision.md)
— the bounded amendment / clarification of **Document 75 §14** (Testing /
Evaluation Requirements). It is a **separate governance act**, distinct
from Document 77 itself: it ratifies the amendment Document 77 already
proposed — it does not perform the amendment design (Document 77 already
did that), it does not re-decide any ratified stage, it does not redesign
C-4, and it does not reinterpret Documents 70 R4, 72, 73 R1, 74, 75
(beyond making effective the one §14 sub-clause amendment Document 77
names), or 76. **The ratified decision is: Document 77 is ratified, and
its Document 75 §14 amendment (Document 77 §6) is now in effect.**

**Effect of this ratification, effective upon this document (D78):** the
golden-dataset `report`-mode evaluation-evidence item in Document 75 §14
(its eighth bullet) is reclassified as **evaluation / validation evidence
and tracked future work** — no longer a mandatory prerequisite for M15 /
C-4 implementation being considered complete under Document 75 §14, and no
longer a bar to opening or continuing a separate commit-authorization
review solely because that evidence is absent. **The first seven Document
75 §14 testing-floor requirements remain mandatory and unchanged.**

**D78 performs one governance act: ratification of Document 77. It does not
authorize implementation, commit, push, merge, deployment, or release**
(§12, §17).

**Type:** Governance / ratification decision record (documentation only —
no source code, test, configuration, schema, migration, index, route,
LangGraph node, MongoDB collection, Redis usage, provider,
evaluation-infrastructure, or frontend file created or modified to produce
it; Document 77 and Documents 70–76 read, not modified. The only file this
task creates is this document.

**Date:** 2026-09-07.

**Precedent / lineage.** This record follows the same standalone
decision-record form
[72_Document70_R4_CTO_Ratification_Record.md](72_Document70_R4_CTO_Ratification_Record.md)
and
[74_Document73_R1_CTO_Architecture_Ratification_Record.md](74_Document73_R1_CTO_Architecture_Ratification_Record.md)
established for ratifying a prior document without modifying it — applied
one governance step further down the chain, ratifying a **bounded
post-ratification amendment** (Document 77) of a single sub-clause of an
already-ratified decision (Document 75 §14). This record performs exactly
one governance act: ratifying Document 77 and making its Document 75 §14
amendment effective. It does not reinterpret Document 71 (the historical
blocked API-contract ratification review), Document 75, or Document 76 —
each is cited, not amended.

---

## 0. What This Document Is and Is Not

**Is:** the record of one CTO governance decision — ratification of
Document 77's bounded amendment of Document 75 §14 — plus a precise
restatement of what that ratification makes effective, what it preserves
unchanged, what it explicitly does **not** authorize, and the gate that
stands next.

**Is not:** an origination or independent redesign of the amendment
(Document 77 already made that decision — this record ratifies it, it does
not re-derive it); a rewrite of Document 75 or Document 76 (neither is
edited by this record); a retroactive claim that Document 75 "never
required" the golden-dataset evidence (§8); a statement that the
golden-dataset evidence is unnecessary, invalid, or no longer wanted (§7);
a claim that the golden-dataset evidence has been generated (it has not —
§16); a weakening of any **other** Document 75 §14 testing requirement
(§9); an amendment to Document 70 R4, Document 73 R1, Document 74, Document
76, AH-1, AH-2, the process-local result-retention invariant, the
financial-comparison requirements, the narrative single-`chat_json`-call
architecture, the citation requirements, the security requirements, or the
observability requirements (§10); an authorization to build, modify, or
extend any evaluation infrastructure (§11); an implementation
authorization, an architecture decision, a contract change, or a commit /
push / merge / deployment / release authorization (§12); and it does not
create Document 79 or any downstream gate.

---

## 1. Document Metadata

| Field | Value |
|---|---|
| Document number | 78 |
| Title | Document 77 CTO D75 §14 Amendment Ratification Record |
| Ratifies | Document 77 — D75 §14 Testing-Floor Clarification and Amendment Decision — M15 C-4 |
| Ratified state | Document 77 **as present in the repository** — its initial and only issue (no prior revision), with the two mechanical wording substitutions in §6 / §7 already applied |
| Milestone | M15 = C-4 "What Changed Since Last Review" (Document 68 §4; Document 72 §5; Document 74 §6; Document 75 §1; Document 76 §1; Document 77 §1) |
| Governance stage | Amendment ratification (this act) — makes the Document 75 §14 amendment in Document 77 §6 effective |
| Predecessor gate | Document 77 — D75 §14 Testing-Floor Clarification and Amendment Decision (CTO-reviewed, approved for ratification) |
| Related prior records | Document 75 (M15 implementation authorization — 🟢 ratified via Document 76); Document 76 (Document 75 ratification record — 🟢 ratified). Neither modified, neither reinterpreted here. |
| Successor gate (not created here) | A separate M15 / C-4 commit-authorization review, then a separate push / merge / deployment authorization |
| Revision of this record | Initial issue — no prior revision |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Exact Ratification Target

**Target: Document 77 — D75 §14 Testing-Floor Clarification and Amendment
Decision — M15 C-4, as present in the repository.**

Verified this session, read-only, before recording this ratification:

- Document 77's top-line Status banner and closing ALL-CAPS block read:
  *"🟡 PROPOSED — BOUNDED AMENDMENT / CLARIFICATION OF DOCUMENT 75 §14.
  DRAFT / PENDING CTO REVIEW. NOT YET RATIFIED."* Document 77 §14 / §16 /
  §17 explicitly state that a *separate, subsequent CTO ratification of
  Document 77 (a future Document 78)* is required before its Document 75
  §14 amendment takes effect. **This record is that act** — exactly as
  Document 72 ratified Document 70 after its proposal, and Document 74
  ratified Document 73 after its proposal.
- Document 77 carries **no revision-note block.** It was drafted once, with
  two subsequent in-place mechanical wording substitutions (its §6 and §7
  bullets: *"owed to a future, separately-authorized effort"* →
  *"to be undertaken only if and when separately authorized"*) that
  removed a possible mandatory-future-commitment reading without altering
  the amendment's substantive decision, the historical interpretation of
  Documents 75 / 76, the effective-date or ratification semantics, or the
  scope limitations. This record ratifies Document 77 in that single
  state.
- `docs/backend_engineering/` was listed in full: the highest-numbered
  file prior to this task was
  `77_D75_Section14_Testing_Floor_Clarification_and_Amendment_Decision.md`.
  No second Document-77-shaped file exists anywhere in the repository, and
  no Document 78 existed before this task.
- `git status --short` shows Document 77 as untracked (never committed) —
  there is no commit history suggesting a superseding revision was ever
  pushed elsewhere.

**No discrepancy was found. Document 77, in its single present state, is
confirmed as the correct and only amendment-ratification target.** This
record ratifies that state exactly. If a later, numbered revision of
Document 77 is ever introduced, it requires its own separate CTO review
and ratification; this record does not, and cannot, extend to it.

---

## 3. Governance Preconditions (verified this session, read-only)

| Fact | Source | Verified state |
|---|---|---|
| Document 70, Revision R4 | its own status; Document 72 | 🟢 CTO-RATIFIED — the M15 API contract; **not touched by this ratification** |
| Document 72 | its own status | 🟢 CTO-RATIFIED — Document 70 R4 API-contract ratification |
| Document 73, Revision R1 | its own status; Document 74 | 🟢 CTO-RATIFIED — the M15 architecture; AH-1 and AH-2 resolved; **not touched by this ratification** |
| Document 74 | its own status | 🟢 CTO-RATIFIED — Document 73 R1 architecture ratification |
| Document 75 | its own status; Document 76 | 🟢 CTO-RATIFIED (via Document 76) — the M15 implementation authorization. Its §14 defines the "minimum testing floor." **Only the governance role of one §14 item is amended, via Document 77; Document 75 is not edited in place by Document 77 or by this record.** |
| Document 76 | its own status | 🟢 CTO-RATIFIED — Document 75 ratification record. Its §14 carries the Document 75 §14 floor forward by restatement (§13 below). **Not touched by this ratification.** |
| Document 77 | its own status; §14 / §16 / §17 | Bounded amendment proposal of Document 75 §14, CTO-reviewed, approved for ratification; explicitly requires a separate Document 78 to take effect. **This record is that Document 78.** |
| M15 / C-4 implementation | the working-tree implementation and its CTO technical review | Implemented; passed architectural review; **passed a CTO technical review** with bounded remediation applied; the hermetic implementation-test evidence is in place and green (§9). The one open technical-review item was **G-2** — the golden-dataset `report`-mode evidence has not been generated, and the framework required to generate it is outside Document 75 §15's authorized scope. G-2 is **CLOSED by this ratification** (§16). |

No governance state above is changed by this document beyond making
Document 77's Document 75 §14 amendment effective. Each precondition is
cited, not re-decided.

---

## 4. Governance Lineage

| Document | Role | Governance act performed |
|---|---|---|
| **Document 67** | Post-M14 Backend & AI Roadmap Reconciliation | **C-4 recommendation.** CTO-ratified. |
| **Document 68** | M15 Formal Milestone Selection Record | **M15 = C-4 selection.** |
| **Document 69** | Document 68 CTO Ratification Record | **Selection ratification.** |
| **Document 70 (R1→R4)** | M15 API Contract Proposal | **API contract.** |
| **Document 72** | Document 70 Revision R4 CTO Ratification Record | **API-contract ratification.** |
| **Document 73 (R1)** | M15 Architecture Decision Pack | **Architecture decision.** Resolves AH-1 and AH-2. |
| **Document 74** | Document 73 Revision R1 CTO Architecture Ratification Record | **Architecture ratification.** |
| **Document 75** | M15 Implementation Authorization Decision | **Implementation authorization decision.** |
| **Document 76** | Document 75 CTO Implementation Authorization Ratification Record | **Ratification of Document 75.** |
| **Document 77** | D75 §14 Testing-Floor Clarification and Amendment Decision | **Bounded amendment / clarification of Document 75 §14** (the golden-dataset `report`-mode evaluation-evidence item's governance role). |
| **Document 78 (THIS)** | Document 77 CTO D75 §14 Amendment Ratification Record | **Ratification of Document 77.** The distinct act that makes Document 77's Document 75 §14 amendment effective. |

```text
D75  → M15 implementation authorization
D76  → ratification of D75
D77  → bounded amendment / clarification of D75 §14
D78  → ratification of D77
       ↓
G-2 CLOSED
       ↓
M15 / C-4 Commit Authorization Review        (a separate, future CTO act — NOT performed here)
```

These are **distinct governance acts** and this record does not collapse
them. In particular: **Document 77 is the amendment decision; Document 78
is its ratification.** Document 78 did not originate the amendment, did
not independently redesign it, does not ratify itself, and does not create
any downstream document. **D78 does NOT authorize commit.** Commit
authorization remains a separate future CTO act; push / merge / deployment
remain separate later gates.

---

## 5. CTO Amendment-Review Decision

The CTO has reviewed Document 77 and issued: **🟢 DOCUMENT 77 — APPROVED
FOR RATIFICATION.** This document records that ratification. Review
confirmed:

- Document 77 amends **only** the governance role of the golden-dataset
  `report`-mode evaluation-evidence item in Document 75 §14 (its eighth
  bullet) — and nothing else (Document 77 §1, §4, §10);
- Document 77 does **not** rewrite Document 75 or Document 76, and does
  **not** claim Document 75 "never required" the evidence — it makes a
  new, forward-looking, auditable decision effective only upon this
  ratification (Document 77 §9);
- the first seven Document 75 §14 requirements remain mandatory floor
  items, unweakened (Document 77 §6, §10);
- the golden-dataset evidence remains legitimate, desirable, tracked
  evaluation evidence relevant to narrative-mode quality (Document 77 §7);
- hermetic implementation tests are a **different evidence class** from the
  golden-dataset set and are not claimed equivalent to it (Document 77
  §11);
- any future engineering required to produce the golden-dataset evidence
  requires its own separate authorization (Document 77 §12);
- Document 77 authorizes **no** implementation, architecture, contract, or
  evaluation-infrastructure work, and **no** commit / push / merge /
  deployment / release (Document 77 §14).

---

## 6. Ratification Decision

**🟢 DOCUMENT 77 — CTO-RATIFIED.**

**Document 77 is formally ratified, and its Document 75 §14 amendment
(Document 77 §6) is now in effect as of this document (D78).** This
confirms the decision Document 77 §6 already recorded. It does **not**
re-derive, redesign, extend, or narrow that amendment, and it does **not**
authorize commit, push, merge, deployment, release, or production rollout
(§12).

**The ratified amendment, restated in Document 77's own terms:**

> The golden-dataset `report`-mode evaluation-evidence item (Document 75
> §14, eighth bullet) is reclassified as evaluation / validation evidence
> and tracked follow-up work. It is no longer a mandatory prerequisite for
> (a) the M15 / C-4 implementation being considered complete under
> Document 75 §14, or (b) the opening or continuation of a separate,
> subsequently-governed commit-authorization review. Every other Document
> 75 §14 requirement remains a mandatory floor item, unchanged.

---

## 7. What Is Now In Effect

Effective upon this document (D78), and using Document 77's exact
terminology and decision framing:

- The **golden-dataset `report`-mode evidence item** in Document 75 §14
  (its eighth bullet) is **reclassified as evaluation / validation
  evidence and tracked future work** — moved, in governance role, from
  "mandatory floor item" to "evaluation evidence — desirable, tracked, and
  to be undertaken only if and when separately authorized." Its wording in
  Document 75 is **preserved** (Document 75 is not edited); this record
  and Document 77 together are the auditable record that its *governance
  role* has been amended.
- That item is **no longer a mandatory prerequisite** for the M15 / C-4
  implementation to be considered complete under Document 75 §14 — the
  implementation is considered complete under the amended §14 once the
  first seven §14 bullets and the §14 closing disclaimer are satisfied,
  which the CTO technical review records as the case.
- That item's absence is **no longer a bar** to opening or continuing a
  separate commit-authorization review **solely because that evidence is
  absent**.
- The **first seven Document 75 §14 testing-floor requirements** (unit
  tests; hermetic integration / contract tests for the full route family
  across both modes; deterministic financial-comparison tests with
  bit-identical output; narrative grounding / citation-validation tests;
  process-local lifecycle / AH-2 deployment-invariant tests; M14 / M9.1
  regression coverage; security / validation coverage) **remain mandatory
  and unchanged.** The §14 closing disclaimer (this bounded suite is not a
  claim of universal production-grade correctness) also stands.
- The **golden-dataset `report`-mode evidence remains legitimate and
  valuable evaluation evidence** — relevant to evaluating narrative-mode
  quality (whether the narrative engine grounds claims as intended across
  a held-out case set), desirable, and tracked. It is **not** declared
  unnecessary and **not** declared invalid.
- **Hermetic implementation tests are not equivalent to the golden-dataset
  evidence.** They are a different class of evidence: the hermetic tests
  verify the implementation's specific, bounded, deterministic properties
  on constructed inputs; the golden-dataset set would measure the
  narrative engine's grounding behavior across a held-out case corpus.
  This ratification does not substitute one class for the other or claim
  the hermetic suite "covers" what the golden-dataset set would.
- **Future work required to produce the golden-dataset evidence requires
  separate authorization** — including any extension of the `Surface`
  model, any adapter, any surface-dispatch wiring, any update to the
  loader's exact-set tests, and authoring the case corpus. None of it is
  performed or pre-authorized by this ratification (§11).
- The still-open **OCD-5 / AAQ-4** question (whether a formal §20.1-style
  evaluation gate is ever adopted for C-4) is **unaffected** — it remains
  exactly as open as Document 75 §11 and Document 76 §15 leave it. This
  ratification does not resolve it, does not pre-empt it, and does not
  schedule it.

---

## 8. Historical Provenance Preserved

This ratification **preserves the historical record** exactly as Document
77 §9 states it, and adds nothing that contradicts it:

- **Document 75 §14 originally included the golden-dataset `report`-mode
  evidence as part of its testing floor** — it did list it, inside the
  §14 "minimum testing floor implementation must clear before it may be
  considered complete."
- **Document 76 ratified Document 75 as written** — including §14, whose
  restatement of the floor Document 76 §14 carries forward.
- **Document 77 is a new, forward-looking amendment** — dated 2026-09-07,
  making a new governance decision about the *role* of that one item, not
  a discovery about the past.
- **Document 78 (this record) is the separate ratification of Document
  77** — the distinct act that makes Document 77's amendment effective.
- **Document 75 and Document 76 are not rewritten by Document 78.** Both
  remain the accurate record of what was decided when.

This record does **not** state or imply that "Document 75 never required
this evidence," and does **not** retroactively reinterpret Document 75 or
Document 76. The amendment operates going forward, from the moment of this
ratification.

---

## 9. First Seven Document 75 §14 Floor Requirements Remain Mandatory

This ratification confirms that the following Document 75 §14 requirements
remain **mandatory floor items, unchanged and unweakened**, and that the
M15 / C-4 implementation's CTO technical review recorded them as satisfied
by the hermetic / relevant implementation-test evidence, which **remains
valid**:

1. **Unit tests** — the financial-delta function's full eligibility rule
   (`changed` / `new` / `removed` classification; `percent_delta`
   null-on-zero / absent-baseline; unit-mismatch exclusion;
   currency-mismatch short-circuit; deterministic ordering), in-memory
   fixtures only.
2. **Integration / contract tests** — the full
   `/api/companies/{ticker}/changes` route family for both modes (request
   validation; independent per-id ownership / ticker checks; create /
   status / stream / cancel lifecycle; `complete` / `partial` /
   `insufficient_evidence` state transitions), hermetic fake-Mongo +
   real ASGI.
3. **Deterministic financial-comparison tests** — hand-authored
   `FinancialStatement` pairs covering every case, with bit-identical
   output asserted across repeated identical requests.
4. **Narrative grounding / citation-validation tests** — a one-sided item
   is dropped and never surfaces; zero groundable candidates yields
   `insufficient_evidence`; the narrative source shape never mixes with
   the financial source shape.
5. **Process-local lifecycle tests** (Document 73 R1 §22's
   deployment-invariant tests) — same-process completed-result `GET`;
   result expiration; post-restart unavailability; unsupported
   cross-instance behavior; SSE `final`-frame behavior under the same
   invariant.
6. **Regression coverage against relevant M14 behavior** — the
   route-inventory guard updated by exactly the four new C-4 routes, no
   more, no fewer; the existing M14 / M9.1 route family confirmed
   unaffected.
7. **Security / validation coverage** — BYOK / SSRF exercised identically
   to existing contracts; ownership / non-disclosure tests for both job
   records and report references.

The §14 closing disclaimer (this bounded suite does not, by itself,
constitute a claim of universal production-grade correctness) also
remains in force. **No other Document 75 §14 testing requirement is
weakened by this ratification, and this ratification does not generalize
to any other testing requirement in this milestone or elsewhere.**

---

## 10. Existing Architecture Preserved

This ratification introduces **no new architectural decision** and
preserves the following exactly as ratified — none is amended, weakened,
reinterpreted, or reopened:

- **Document 70 R4** — the M15 API contract (request / response shapes;
  the two mutually-exclusive `period` / `report` modes; citation shapes;
  state vocabulary; error taxonomy; job / SSE behavior; security
  boundaries);
- **Document 73 R1** — the M15 architecture;
- **Document 74** — the architecture ratification;
- **Document 75** — its implementation scope generally, in full, **except
  for the narrowly amended §14 item** whose governance role is
  reclassified per Document 77 §6;
- **Document 76** — the Document 75 ratification;
- **AH-1** — the structured-schema narrative-items resolution;
- **AH-2** and the **process-local result-retention invariant** — a
  completed result exists only in the backend process that computed it;
  restart loss is accepted; cross-process `GET` is unsupported; no sticky
  sessions; no Redis or MongoDB final-result persistence; no cross-process
  reconstruction; SSE does not bypass the invariant; `RedisEventBus`
  remains event delivery only;
- the **deterministic, LLM-free financial-comparison requirements** —
  exact `Metric.provider_label` alignment; deterministic citations; no
  invented canonical metric mapping; bit-identical output;
- the **narrative single-`chat_json`-call architecture** — bounded
  two-report evidence; one structured call; bounded output; no iterative
  or continuation generation;
- the **citation requirements** — mode-specific shapes kept distinct;
  mandatory baseline + current grounding for every narrative item;
  deterministic per-item citation validation;
- the **security requirements** — SSRF guarding; BYOK boundaries; input
  validation; ownership / non-disclosure; zero new error classes;
- the **observability requirements** — the `pipeline.change_brief` span;
  the `change_brief_runs_total{outcome, comparison_type}` counter;
  correlation-id logging; the logging discipline.

**The existing M15 / C-4 technical PASS remains unchanged** by this
ratification.

---

## 11. No Evaluation-Infrastructure Authorization

Consistent with Document 77 §12, **this ratification does NOT authorize:**

- creation of an evaluation adapter (e.g. `evaluation/adapters/change_brief.py`);
- creation of, or modification of, a golden-dataset loader;
- modification of any evaluation infrastructure
  (`evaluation/golden_dataset/`, `evaluation/adapters/`,
  `evaluation/core/`, `evaluation/self_consistency/`, or their tests);
- any new evaluation code;
- any new fixtures;
- any new corpus-generation machinery;
- any new LLM-evaluation infrastructure.

Any future engineering required to generate the golden-dataset
`report`-mode evidence requires its own separate authorization, and is
neither performed nor pre-authorized here.

---

## 12. Explicit Non-Authorizations

**Ratifying Document 77 does NOT authorize:**

- application implementation;
- additional M15 implementation of any kind;
- any architecture change;
- any API-contract change;
- evaluation adapter creation;
- golden-dataset loader modification;
- any evaluation-infrastructure change;
- any new evaluation code;
- any new fixtures or corpus-generation machinery;
- any MongoDB schema / collection / index / migration change;
- any Redis result persistence;
- any LangGraph change;
- Durable Research Sessions, in any form;
- any frontend work;
- commit;
- push;
- merge;
- deployment;
- release;
- production rollout;
- unrelated cleanup of any kind;
- reopening M14;
- promoting C-2.

**A separate M15 / C-4 commit-authorization review remains required**
before any C-4 code reaches `main` or a deployed environment, and a
further separate push / merge / deployment authorization after that —
neither created nor implied by this record. **D78 performs one governance
act: ratification of Document 77.**

---

## 13. Effect on Document 76 §14 (carry-forward — Document 76 not modified)

Document 76 §14 ("Testing / Evaluation Floor — carried forward — Document
75 §14") **restates** the Document 75 §14 floor, including "a small
`report`-mode golden-dataset evaluation set run through the existing
framework unmodified as grounding evidence." Because Document 76 §14 is a
**carry-forward restatement of Document 75 §14** — not an independent
requirement — Document 76 §14's restatement of that one item is now read
**under the amended governance role** established by Document 77 §6 and
made effective by this record, by reference. **Document 76 is not edited,
not amended, and not reinterpreted beyond that mechanical consequence of
its own "carried forward — Document 75 §14" framing** (Document 77 §15).

---

## 14. Governance Ladder (restated, not collapsed)

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
Implementation-authorization ratification
≠
Bounded amendment of D75 §14 (D77)
≠
Amendment ratification (D78)                       🟢 THIS DOCUMENT
≠
Implementation / technical review
≠
Commit authorization
≠
Push / merge / deployment authorization
```

```text
D67  → C-4 recommendation                 🟢 CTO-RATIFIED
  ↓
D68  → M15 = C-4 selection                🟢 CTO-RATIFIED via D69
  ↓
D69  → selection ratification             🟢 CTO-RATIFIED
  ↓
D70 R4 → API contract                     🟢 CTO-RATIFIED via D72
  ↓
D72  → API-contract ratification          🟢 CTO-RATIFIED
  ↓
D73 R1 → architecture decision            🟢 CTO-RATIFIED via D74
  ↓
D74  → architecture ratification          🟢 CTO-RATIFIED
  ↓
D75  → M15 implementation authorization   🟢 CTO-RATIFIED via D76
  ↓
D76  → ratification of D75                🟢 CTO-RATIFIED
  ↓
D77  → bounded amendment of D75 §14       🟢 CTO-RATIFIED via D78
  ↓
D78  → ratification of D77 (THIS)         🟢 CTO-RATIFIED — D75 §14 amendment now in effect
  ↓
G-2 CLOSED                                (governance blocker resolved — NOT by generating the evidence, §16)
  ↓
M15 / C-4 Commit Authorization Review     NOT CREATED — a separate, future CTO act
  ↓
Commit / Push / Merge / Deployment        NOT AUTHORIZED
```

This record performs exactly one stage: **amendment ratification.** It is
not a substitute for, or a shortcut past, the commit-authorization review
or any later stage. **Document 78 does not become a commit-authorization
record.**

---

## 15. Effective Governance State

Recorded as of this document (D78). **This does not imply the
golden-dataset `report`-mode evidence has been generated — it has not**
(§16).

| Item | State |
|---|---|
| M15 / C-4 implementation | 🟢 Technical PASS |
| Document 75 | 🟢 Ratified (via Document 76) |
| Document 76 | 🟢 Ratified |
| Document 77 | 🟢 Ratified via Document 78 |
| G-2 | 🟢 CLOSED |
| Golden-dataset `report`-mode evidence | 🟡 Future evaluation work |
| Evaluation infrastructure | 🔴 Not authorized |
| Commit authorization | 🔴 Separate future gate |
| Commit | 🔴 Not authorized |
| Push / merge / deployment | 🔴 Not authorized |

---

## 16. G-2 Closure

**G-2 — the governance ambiguity identified by the M15 / C-4 CTO technical
review (an evaluation-evidence item listed inside the Document 75 §14
"minimum testing floor" that cannot be produced within Document 75 §15's
authorized scope) — is CLOSED by this ratification.**

G-2 is closed **not by generating the golden-dataset evidence** — it has
**not** been generated — but by ratifying Document 77's reclassification
of that one item's governance role: it is now evaluation / validation
evidence and tracked future work, not a mandatory prerequisite for
implementation completion under Document 75 §14 and not a bar to a
separate commit-authorization review. The golden-dataset `report`-mode
evidence remains legitimate, desirable, tracked evaluation work, to be
undertaken only if and when separately authorized (§7, §11).

---

## 17. Next Gate

**The next legitimate governance action is a separate M15 / C-4
commit-authorization review** — a distinct CTO act from this ratification —
conducted against the amended Document 75 §14 (the first seven mandatory
floor items plus the §14 closing disclaimer). **This record does not
perform, open, or pre-decide that review, and does not authorize commit.**
Only after a commit-authorization decision may code be committed; and only
after that, a further separate push / merge / deployment authorization,
each a distinct CTO act, none collapsed.

---

## 18. Repository / Document Provenance

Recorded by read-only `git` inspection this session. **This is a
point-in-time snapshot observed during the creation of this record on
2026-09-07**, not a claim about repository state at any later reading
time. **No `git` mutation was performed** — no `add`/stage, no `commit`,
no `push`, no `amend`, no `rebase`, no `merge`, no `reset`, no `restore`,
no `stash`, no `clean`.

- `HEAD = origin/main = be4949b` (M14 implementation commit), unchanged.
- Document number 78 was verified free before creation (highest existing
  Backend & AI governance document was 77; no Document 78 existed prior to
  this task).
- **Document 77 was read in its single present state, not modified.** It
  carries no revision-note block. Its amendment decision is restated here
  in substance, not amended.
- **Documents 70–76 were read, not modified.** Their ratified content is
  cited, not amended. Document 75 is **not** edited in place by this
  record; Document 76 is **not** edited (§13).
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval / RAG code, MongoDB collection, Redis
  component, provider, configuration, evaluation-infrastructure, or
  frontend file was created or modified. `.gitignore` was not modified.
- The working tree carries the in-progress, uncommitted M15 / C-4
  implementation and its tests (created and technically reviewed under
  Documents 75 / 76 / 77 in prior tasks) plus known, pre-existing,
  unrelated items. **None of these were staged, modified, renamed,
  deleted, or cleaned by this task:**

  ```text
   M backend/agents/schemas.py                                     (M15 impl — prior task, uncommitted)
   M backend/app/settings.py                                       (M15 impl — prior task, uncommitted)
   M backend/domain/models.py                                      (M15 impl — prior task, uncommitted)
   M backend/infrastructure/observability/metrics.py               (M15 impl — prior task, uncommitted)
   M backend/server.py                                             (M15 impl — prior task, uncommitted)
   M backend/tests/contract/test_route_inventory.py                (M15 impl — prior task, uncommitted)
   M backend/tests/unit/test_settings.py                           (M15 impl — prior task, uncommitted)
   M web/features/workspace-home/ui/CompanySearch.test.tsx         (pre-existing, unrelated — not touched)
  ?? backend/agents/change_brief_financial.py                      (M15 impl — prior task, uncommitted)
  ?? backend/agents/change_brief_narrative.py                      (M15 impl — prior task, uncommitted)
  ?? backend/tests/unit/test_change_brief_*.py                     (M15 impl — prior task, uncommitted)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/   (untracked, M11 evidence — not touched)
  ?? both                                                          (untracked, unexplained pre-existing artifact — not created by this task; not touched)
  ?? current_period_end`                                          (untracked, unexplained pre-existing artifact — not created by this task; not touched)
  ?? docs/backend_engineering/67_...md through 77_...md            (pre-existing untracked governance documents — not modified)
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/78_Document77_CTO_D75_Section14_Amendment_Ratification_Record.md`).
  It is untracked and not yet version-controlled. Staging or committing it
  is a separate, subsequently CTO-authorized step.

---

**🟢 DOCUMENT 77 — CTO-RATIFIED. THIS RECORD RATIFIES DOCUMENT 77 — THE
BOUNDED AMENDMENT / CLARIFICATION OF DOCUMENT 75 §14 — AND MAKES ITS
AMENDMENT (DOCUMENT 77 §6) EFFECTIVE AS OF THIS DOCUMENT (D78). EFFECTIVE
NOW: THE GOLDEN-DATASET `report`-MODE EVALUATION-EVIDENCE ITEM IN DOCUMENT
75 §14 (ITS EIGHTH BULLET) IS RECLASSIFIED AS EVALUATION / VALIDATION
EVIDENCE AND TRACKED FUTURE WORK — NO LONGER A MANDATORY PREREQUISITE FOR
M15 / C-4 IMPLEMENTATION BEING CONSIDERED COMPLETE UNDER DOCUMENT 75 §14,
AND NO LONGER A BAR TO OPENING OR CONTINUING A SEPARATE
COMMIT-AUTHORIZATION REVIEW SOLELY BECAUSE THAT EVIDENCE IS ABSENT. THE
FIRST SEVEN DOCUMENT 75 §14 TESTING-FLOOR REQUIREMENTS (UNIT;
INTEGRATION / CONTRACT; DETERMINISTIC FINANCIAL; NARRATIVE GROUNDING /
CITATION; PROCESS-LOCAL LIFECYCLE; M14 REGRESSION; SECURITY / VALIDATION)
AND THE §14 CLOSING DISCLAIMER REMAIN MANDATORY AND UNCHANGED. THE
GOLDEN-DATASET EVIDENCE REMAINS LEGITIMATE AND VALUABLE EVALUATION
EVIDENCE RELEVANT TO NARRATIVE-MODE QUALITY; IT IS NOT DECLARED
UNNECESSARY OR INVALID, AND IT HAS NOT BEEN GENERATED. HERMETIC TESTS ARE
A DIFFERENT EVIDENCE CLASS FROM THE GOLDEN DATASET AND ARE NOT CLAIMED
EQUIVALENT TO IT. THIS IS NOT A RETROACTIVE CLAIM THAT DOCUMENT 75 "NEVER
REQUIRED" THE EVIDENCE — DOCUMENT 75 §14 ORIGINALLY LISTED IT IN THE
TESTING FLOOR, DOCUMENT 76 RATIFIED DOCUMENT 75 AS WRITTEN, DOCUMENT 77 IS
THE FORWARD-LOOKING AMENDMENT, AND DOCUMENT 78 IS ITS SEPARATE
RATIFICATION; DOCUMENT 75 AND DOCUMENT 76 ARE NOT REWRITTEN. FUTURE WORK
REQUIRED TO PRODUCE THE GOLDEN-DATASET EVIDENCE REQUIRES SEPARATE
AUTHORIZATION. THIS RATIFICATION INTRODUCES NO NEW ARCHITECTURAL DECISION
AND PRESERVES DOCUMENT 70 R4, DOCUMENT 73 R1, DOCUMENT 74, DOCUMENT 75
(EXCEPT THE NARROWLY AMENDED §14 ITEM), DOCUMENT 76, AH-1, AH-2,
PROCESS-LOCAL RESULT RETENTION, DETERMINISTIC FINANCIAL COMPARISON, THE
NARRATIVE SINGLE-`chat_json` ARCHITECTURE, THE CITATION REQUIREMENTS, THE
SECURITY REQUIREMENTS, AND THE OBSERVABILITY REQUIREMENTS. THE EXISTING
M15 / C-4 TECHNICAL PASS REMAINS UNCHANGED. G-2 IS CLOSED — NOT BY
GENERATING THE EVIDENCE, BUT BY RATIFYING ITS RECLASSIFICATION. THIS
DOCUMENT DOES NOT AUTHORIZE APPLICATION OR ADDITIONAL M15 IMPLEMENTATION,
ARCHITECTURE OR API-CONTRACT CHANGES, EVALUATION ADAPTER CREATION,
GOLDEN-DATASET LOADER MODIFICATION, EVALUATION-INFRASTRUCTURE CHANGES, NEW
EVALUATION CODE, NEW FIXTURES OR CORPUS MACHINERY, MONGODB CHANGES, REDIS
RESULT PERSISTENCE, LANGGRAPH CHANGES, DURABLE RESEARCH SESSIONS, FRONTEND
WORK, UNRELATED CLEANUP, M14 REOPENING, C-2 PROMOTION, COMMIT, PUSH,
MERGE, DEPLOYMENT, RELEASE, OR PRODUCTION ROLLOUT. D78 PERFORMS ONE
GOVERNANCE ACT: RATIFICATION OF DOCUMENT 77. IT DOES NOT AUTHORIZE
IMPLEMENTATION, COMMIT, PUSH, MERGE, DEPLOYMENT, OR RELEASE. A SEPARATE
M15 / C-4 COMMIT-AUTHORIZATION REVIEW REMAINS REQUIRED, AND PUSH / MERGE /
DEPLOYMENT REMAIN SEPARATE LATER GATES. DOCUMENTS 70–77 WERE NOT MODIFIED —
DOCUMENT 75 IS NOT EDITED IN PLACE, DOCUMENT 76 IS NOT EDITED. NO
APPLICATION SOURCE, TEST, CONFIGURATION, MONGODB, REDIS, FRONTEND, OR
EVALUATION-INFRASTRUCTURE FILE WAS CREATED OR MODIFIED. NO STAGE. NO
COMMIT. NO PUSH. NO MERGE / REBASE / RESET / AMEND. THE NEXT LEGITIMATE
GOVERNANCE ACTION IS A SEPARATE M15 / C-4 COMMIT-AUTHORIZATION REVIEW —
NOT IMPLEMENTATION, AND NOT COMMIT.**
