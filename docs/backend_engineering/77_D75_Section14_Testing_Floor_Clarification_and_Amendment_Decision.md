# 77 — D75 §14 Testing-Floor Clarification and Amendment Decision — M15 C-4

**Status:** 🟡 **PROPOSED — BOUNDED AMENDMENT / CLARIFICATION OF DOCUMENT 75
§14. DRAFT / PENDING CTO REVIEW. NOT YET RATIFIED.** This document proposes
one narrowly-scoped governance amendment to
[Document 75](75_M15_Implementation_Authorization_Decision.md) **§14
(Testing / Evaluation Requirements)** — and to nothing else. Document 75 is
already ratified
([Document 76](76_Document75_CTO_Implementation_Authorization_Ratification_Record.md)),
so this amendment is recorded **as a separate, auditable governance
document — Document 75 is NOT modified in place**. Creating this document
does **not** enact the amendment: a separate, subsequent CTO
**ratification** of this document (a future Document 78) is required before
the amendment takes effect (§16, §17).

**Type:** Governance / bounded amendment-and-clarification decision
(documentation only — no source code, test, configuration, schema,
migration, index, route, LangGraph node, MongoDB collection, Redis usage,
provider, evaluation-infrastructure, or frontend file created or modified
to produce it; Documents 67–76 read, not modified. The only file this task
creates is this document.

**Date:** 2026-09-07.

**Precedent / lineage.** This document is a governance **amendment /
clarification** applied *after* a ratified authorization, recorded as its
own artifact rather than by editing the ratified document — the same
discipline this chain already uses for post-ratification corrections
(Document 72's handling of the blocked Document 71 review; Document 74's
treatment of Document 70 as a frozen input). It follows Document 75's own
governance-ladder framing and Document 76's ratification-record form,
applied one step further down the chain: a **bounded amendment of a single
sub-clause of an already-ratified decision**, preceding its own future,
separate ratification. It does not redesign or reinterpret Document 70 R4,
Document 73 R1, Document 74, Document 75 (beyond the one §14 sub-clause
named here), or Document 76.

---

## 0. What This Document Is and Is Not

**Is:** a proposed decision that, **if and when ratified by a separate CTO
act (a future Document 78)**, would **amend the governance role of exactly
one item in Document 75 §14** — the golden-dataset `report`-mode
evaluation-evidence bullet — so that it is classified as
evaluation/validation evidence and tracked follow-up work, **not** a
mandatory prerequisite for M15 / C-4 implementation being considered
complete under Document 75 §14, and **not** a bar to a subsequent,
separately-governed commit-authorization review. It also records, for
audit, why this amendment is being made now and what it deliberately does
not touch.

**Is not:** a retroactive claim that Document 75 "never required" this
evidence (§9); a statement that the evidence is unnecessary, invalid, or
no longer wanted (§7); a weakening of any **other** Document 75 §14
testing requirement (§10); an amendment to Document 70 R4, Document 73 R1,
Document 74, Document 76, AH-1, AH-2, the process-local result-retention
invariant, the financial-comparison requirements, the narrative
single-`chat_json`-call architecture, the citation requirements, the
security requirements, or the observability requirements (§10); an
authorization to build, modify, or extend any evaluation infrastructure —
adapter, loader, case-evaluator, fixtures, corpus-generation machinery, or
LLM-evaluation tooling (§12); an implementation authorization, an
architecture decision, a contract change, or a commit / push / merge /
deployment / release authorization (§14); a self-ratification (§17); and
it does not create Document 78 (§16).

---

## 1. Document Metadata

| Field | Value |
|---|---|
| Document number | 77 |
| Title | D75 §14 Testing-Floor Clarification and Amendment Decision — M15 C-4 |
| Amends | **Document 75 §14 only** — specifically the governance role of the golden-dataset `report`-mode evaluation-evidence item (§4) |
| Does NOT amend | Documents 70 R4, 72, 73 R1, 74, 76; every other Document 75 section and every other Document 75 §14 item (§10) |
| Milestone | M15 = C-4 "What Changed Since Last Review" (Document 68 §4; Document 72 §5; Document 74 §6; Document 75 §1; Document 76 §1) |
| Governance stage | Bounded post-ratification amendment / clarification proposal — draft, pre-CTO-review |
| Predecessor gate | Document 76 — Document 75 CTO Implementation Authorization Ratification Record (🟢 CTO-RATIFIED, 2026-09-06) |
| Successor gate (not created here) | CTO ratification of this amendment — a future, separate Document 78 |
| Revision of this record | Initial issue — no prior revision |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Status / Authority

🟡 **PROPOSED — CTO DECISION REQUIRED. NOT RATIFIED. AMENDMENT NOT YET IN
EFFECT.**

**Governance ladder (each a distinct CTO act; none confers the next):**

| # | Stage | Status |
|---|---|---|
| 1 | Milestone selection | 🟢 CTO-RATIFIED (Document 68, via Document 69) — **M15 = C-4** |
| 2 | API contract ratification | 🟢 CTO-RATIFIED (Document 70 R4, via Document 72) |
| 3 | Architecture ratification | 🟢 CTO-RATIFIED (Document 73 R1, via Document 74) |
| 4 | Implementation authorization | 🟢 CTO-RATIFIED (Document 75, via Document 76) |
| 4a | **D75 §14 golden-dataset-item amendment** | 🟡 **PROPOSED HERE — NOT YET RATIFIED** |
| 5 | Commit authorization | NOT CREATED — a separate, later, distinct CTO act |
| 6 | Push / merge / deployment authorization | NOT CREATED — a separate, later, distinct CTO act |

This document performs exactly one act: **proposing** the bounded §14
amendment described in §6 for CTO review. It does not enact it, and it
performs no stage beyond that proposal — in particular it does not confer,
imply, or advance stage 5 or stage 6.

---

## 3. Governance Preconditions (verified this session, read-only)

| Fact | Source | Verified state |
|---|---|---|
| Document 70, Revision R4 | its own status; Document 72 | 🟢 CTO-RATIFIED — the M15 API contract; **not touched by this amendment** |
| Document 72 | its own status | 🟢 CTO-RATIFIED — Document 70 R4 API-contract ratification |
| Document 73, Revision R1 | its own status; Document 74 | 🟢 CTO-RATIFIED — the M15 architecture; AH-1 and AH-2 resolved; **not touched by this amendment** |
| Document 74 | its own status | 🟢 CTO-RATIFIED — Document 73 R1 architecture ratification |
| Document 75 | its own status; Document 76 | 🟢 CTO-RATIFIED (via Document 76) — the M15 implementation authorization. Its §14 defines the "minimum testing floor" (§4 below). **Only the governance role of one §14 item is amended by this document; Document 75 is not edited in place.** |
| Document 76 | its own status | 🟢 CTO-RATIFIED — Document 75 ratification record. Its §14 carries the Document 75 §14 floor forward by restatement (§15 below). **Not touched by this amendment.** |
| M15 / C-4 implementation | the working-tree implementation and its CTO technical review | Implemented; passed architectural review; passed a CTO **technical review** with bounded remediation items; the hermetic implementation-test evidence is in place and green (§11). The one open technical-review item is **G-2** — the golden-dataset `report`-mode evidence has not been generated, and the framework required to generate it is outside Document 75 §15's authorized scope (§5). |

No governance state above is changed by this document. Each is cited, not
re-decided. The only genuinely open question this document resolves is the
one it names: the **governance role** of the golden-dataset `report`-mode
evaluation-evidence item in Document 75 §14.

---

## 4. The Exact Document 75 §14 Language Being Amended

Document 75 §14 is titled *"Testing / Evaluation Requirements (minimum, for
implementation to be considered complete)"* and opens:

> **This section defines the minimum testing floor implementation must
> clear before it may be considered complete for the purposes of a future
> commit-authorization request (§16).**

Its **eighth and final** requirement bullet reads, verbatim:

> - **Evaluation evidence**: at minimum, a small set of golden-dataset
>   cases for the `report`-mode narrative path (proposed
>   `surface: "change_brief"`, per Document 73 R1 §22), run through the
>   existing golden-dataset loader/adapter/case-evaluator framework
>   unmodified, as evidence the narrative engine grounds claims as
>   intended — this is evaluation evidence, not a per-request quality gate
>   (§11.3, OCD-5/AAQ-4 remain separately open for whether a formal gate
>   is ever adopted).

**The area amended by this document is precisely:** the *governance role*
of that eighth bullet — the fact that it is listed among the items of a
"minimum testing floor implementation must clear before it may be
considered complete for the purposes of a future commit-authorization
request." Document 76 §14 restates this same floor, including "a small
`report`-mode golden-dataset evaluation set run through the existing
framework unmodified as grounding evidence" (§15 below).

**Nothing else in Document 75 §14, and no other Document 75 section, is
amended** (§10).

---

## 5. What Prompted This Amendment (recorded for audit — not a
reinterpretation)

The M15 / C-4 implementation has been built and has undergone a CTO
technical review. That review surfaced a bounded governance ambiguity,
tracked as **G-2**:

1. Document 75 §14's eighth bullet asks for the golden-dataset
   `report`-mode evidence to be produced *"through the existing
   golden-dataset loader/adapter/case-evaluator framework **unmodified**."*
2. The existing framework, as inspected during the technical review,
   **cannot accept a `report`-mode `change_brief` case without
   modification**: `evaluation/golden_dataset/models.py` defines a closed
   `Surface` literal that does not include `"change_brief"`;
   `evaluation/self_consistency/` defines an even narrower `Surface`; there
   is no `evaluation/adapters/change_brief.py`; and the golden-dataset
   loader tests assert an exact surface set.
3. Document 75 §15 (the authorization boundary) enumerates the additive
   changes implementation is authorized to make — `JobKind.CHANGE_BRIEF`,
   `job_deadline_change_brief_s`, the four routes, the §14 tests, and
   documentation updates — and **does not authorize** modifying evaluation
   infrastructure. Document 76 §11 / §15 do not expand that list.
4. Consequently the golden-dataset `report`-mode evidence **cannot be
   generated within the authorized M15 scope**, yet it is listed among the
   items of a "floor implementation must clear before it may be considered
   complete." Read strictly, that makes an unauthorized-and-therefore-
   unbuildable artifact a blocker on implementation completion and on a
   commit-authorization review.

This document does **not** claim that reading was wrong, unintended, or
absent from Document 75 — Document 75 §14 and Document 76 §14 say what they
say, and Document 76 ratified them. This document instead makes a **new,
explicit, forward-looking governance decision** about the role that one
item plays, so the ambiguity is resolved by an auditable act rather than
by silent reinterpretation (§9).

---

## 6. The Amendment Decision

**If, and only if, this document is separately ratified by the CTO (a
future Document 78), the following amendment to Document 75 §14 takes
effect:**

> **The golden-dataset `report`-mode evaluation-evidence item (Document 75
> §14, eighth bullet) is reclassified as evaluation / validation evidence
> and tracked follow-up work. It is no longer a mandatory prerequisite
> for (a) the M15 / C-4 implementation being considered complete under
> Document 75 §14, or (b) the opening or continuation of a separate,
> subsequently-governed commit-authorization review. Every other Document
> 75 §14 requirement remains a mandatory floor item, unchanged.**

Operationally, once ratified:

- Document 75 §14's opening framing ("minimum testing floor implementation
  must clear before it may be considered complete for the purposes of a
  future commit-authorization request") continues to apply **in full** to
  the first seven bullets (unit tests; integration/contract tests;
  deterministic financial-comparison tests; narrative grounding / citation
  validation tests; process-local lifecycle tests; M14 regression
  coverage; security / validation coverage) and to the §14 closing
  disclaimer.
- The eighth bullet is **moved, in governance role, from "mandatory floor
  item" to "evaluation evidence — desirable, tracked, and to be undertaken
  only if and when separately authorized."** Its wording in Document 75 is
  preserved (Document 75 is not edited); this document is the record that
  its *governance role* has been amended.
- The still-open OCD-5 / AAQ-4 question (whether a formal §20.1-style
  evaluation gate is ever adopted for C-4) is **unaffected** — it remains
  exactly as open as Document 75 §11 and Document 76 §15 leave it. This
  amendment does not resolve it, does not pre-empt it, and does not
  schedule it.

This is the **only** substantive act of this document.

---

## 7. Required Distinction — The Golden-Dataset Evidence Remains Valuable

This amendment does **not** diminish the golden-dataset `report`-mode
evidence. Explicitly:

- It **remains legitimate evaluation evidence** for the `report`-mode
  narrative path.
- It **remains desirable, tracked follow-up evidence** — to be undertaken
  only if and when separately authorized, and expected to be produced.
- It **remains relevant to evaluating narrative-mode quality** (whether the
  narrative engine grounds claims as intended across a held-out case set),
  a question the hermetic implementation tests do not, and are not
  designed to, answer (§11).
- It is **not being declared unnecessary.**
- It is **not being declared invalid.**

The amendment changes **where this evidence sits in the governance ladder**
— from a completion / commit-review prerequisite to a tracked evaluation
deliverable — and nothing about its worth.

---

## 8. Required Distinction — It Is Not This Implementation / Commit Gate

Once this amendment is ratified, the **absence** of the golden-dataset
`report`-mode evidence must **not**:

- invalidate the M15 / C-4 implementation;
- invalidate the technical-review PASS already established for that
  implementation;
- prevent the implementation from being **considered complete under the
  amended Document 75 §14** (i.e., once the first seven §14 bullets and the
  §14 closing disclaimer are satisfied, which the technical review
  records as the case);
- prevent a **separate, subsequently-governed commit-authorization review**
  from being opened or continued **solely** because that evaluation
  evidence has not yet been generated.

This distinction is deliberate and must be read as explicit: the
golden-dataset evidence is **evaluation evidence and tracked follow-up**,
**not** a gate on implementation completion or on a commit-authorization
review under Document 75 §14.

---

## 9. No Retroactive Reinterpretation

This document does **not** state, and must not be read to imply, that
"Document 75 never required this evidence." It did list it — inside the
§14 floor — and Document 76 ratified §14 as written. Those readings, and
the provenance of Documents 75 and 76, **stand as historical record,
unchanged.**

What this document does is make a **new governance decision, dated
2026-09-07, effective only upon its own separate ratification**, that
**amends the governance role** of that one item going forward. The
sequence is auditable and preserved:

- **2026-09-06** — Document 75 §14 lists the golden-dataset `report`-mode
  evidence among the minimum-floor items; Document 76 ratifies Document 75
  (including §14) as written.
- **2026-09-07** — Document 77 (this document) proposes the bounded
  amendment of that one item's role, citing the G-2 technical-review
  finding as the reason.
- **future** — Document 78 (not created here) records the CTO's decision
  on this proposal.

Document 75's text is not rewritten; Document 76 is not amended; both
remain the accurate record of what was decided when. This document is the
accurate record of the amendment.

---

## 10. Scope Limitation — What This Amendment Does NOT Touch

This amendment modifies **only** the governance status of the
golden-dataset `report`-mode evaluation-evidence item in Document 75 §14.
It does **not** amend, weaken, reinterpret, or reopen any of the
following, each of which remains in force exactly as ratified:

- the **Document 70 R4 API contract** (request/response shapes, the two
  mutually-exclusive `period` / `report` modes, citation shapes, state
  vocabulary, error taxonomy, job/SSE behavior, security boundaries);
- the **Document 73 R1 architecture**;
- the **Document 74 architecture ratification**;
- **Document 75's implementation scope generally** (§4–§10, §15, §16 of
  Document 75) — every boundary there stands;
- the **Document 76 ratification**;
- **AH-1** (the structured-schema narrative-items resolution);
- **AH-2** and the **process-local result-retention invariant** (a
  completed result exists only in the process that computed it; restart
  loss accepted; cross-process `GET` unsupported; no sticky sessions; no
  Redis or MongoDB final-result persistence; no cross-process
  reconstruction; SSE does not bypass the invariant);
- the **deterministic, LLM-free financial-comparison requirements**
  (exact `Metric.provider_label` alignment, deterministic citations, no
  invented canonical metric mapping, bit-identical output);
- the **narrative single-`chat_json`-call architecture** (bounded
  two-report evidence, one structured call, bounded output, no iterative
  or continuation generation);
- the **citation requirements** (mode-specific shapes kept distinct;
  mandatory baseline + current grounding for every narrative item;
  deterministic per-item citation validation);
- the **security requirements** (SSRF guarding, BYOK boundaries, input
  validation, ownership / non-disclosure, zero new error classes);
- the **observability requirements** (the `pipeline.change_brief` span, the
  `change_brief_runs_total{outcome, comparison_type}` counter,
  correlation-id logging, logging discipline);
- the **general unit / integration / regression testing requirements** —
  the first seven bullets of Document 75 §14 remain **mandatory floor
  items**, unchanged and unweakened.

**No other Document 75 §14 testing requirement is weakened.** This is a
narrowly-scoped amendment of one item's role; it is not a precedent for,
and does not generalize to, any other testing requirement in this
milestone or elsewhere.

---

## 11. Existing Implementation Evidence Preserved

The M15 / C-4 implementation has **already undergone the CTO technical
review**, and the hermetic / relevant implementation-test evidence
produced for it **remains valid** and is not disturbed by this amendment:
the pure financial-engine unit tests; the hermetic fake-Mongo + real-ASGI
route-family integration/contract tests for both modes; the deterministic
financial-comparison tests (bit-identical output across repeated identical
requests); the narrative grounding / citation-validation tests (one-sided
item dropped and never surfaced; zero groundable candidates →
`insufficient_evidence`; narrative and financial source shapes never
mixed); the process-local lifecycle / AH-2 deployment-invariant tests; the
M14/M9.1 regression coverage; and the security / non-disclosure coverage —
i.e., the first seven bullets of Document 75 §14.

**These hermetic tests are not equivalent to the golden-dataset
evaluation set.** They are a **different class of evidence**: the hermetic
tests verify the *implementation's* specific, bounded, deterministic
properties on constructed inputs; the golden-dataset set would measure the
*narrative engine's grounding behavior* across a held-out case corpus.
This amendment exists **precisely so that this distinction is not
blurred** — it does not substitute one class of evidence for the other,
and it does not claim the hermetic suite "covers" what the golden-dataset
set would. It only reclassifies the governance *role* of the missing
golden-dataset item, leaving both evidence classes described accurately.

---

## 12. No Evaluation-Infrastructure Authorization

**This clarification does NOT authorize:**

- creation of an evaluation adapter (e.g. `evaluation/adapters/change_brief.py`);
- creation of, or changes to, a golden-dataset loader;
- modification of any evaluation infrastructure
  (`evaluation/golden_dataset/`, `evaluation/adapters/`,
  `evaluation/core/`, `evaluation/self_consistency/`, or their tests);
- any new evaluation code;
- any new fixtures;
- any new corpus-generation machinery;
- any new LLM-evaluation infrastructure.

Any future engineering required to generate the golden-dataset
`report`-mode evidence — including extending the `Surface` model, adding an
adapter, wiring surface dispatch, updating the loader's exact-set tests,
and authoring the case corpus — **requires its own separate
authorization**, and is neither performed nor pre-authorized here.

---

## 13. No Implementation Changes

Creating this document does not, and this task did not, modify:

- application source code;
- tests;
- configuration;
- any MongoDB schema, collection, index, or migration;
- any Redis component or usage;
- any frontend file;
- any evaluation-infrastructure file.

**G-2 is not "fixed" by generating the missing evidence.** The governance
decision proposed in §6 is the only intended change. The pre-existing,
unrelated working-tree items present before this task began were not
staged, modified, renamed, deleted, or cleaned (§18).

---

## 14. Explicit Non-Authorizations

**This document — even once ratified — would NOT authorize:**

- additional implementation of any kind;
- any architecture change;
- any API-contract change;
- any evaluation-infrastructure work (§12);
- commit;
- push;
- merge;
- deployment;
- release;
- production rollout;
- unrelated cleanup;
- reopening M14;
- promoting C-2;
- implementing Durable Research Sessions;
- unrelated frontend work.

Its only substantive act is the bounded amendment / clarification of
Document 75 §14 described in §6. **A separate, later commit-authorization
review remains required** before any M15 / C-4 code reaches `main` or a
deployed environment, and a further separate push / merge / deployment
authorization after that — neither created nor implied by this document.

---

## 15. Effect on Document 76 §14 (carry-forward — Document 76 not modified)

Document 76 §14 ("Testing / Evaluation Floor — carried forward — Document
75 §14") **restates** the Document 75 §14 floor, including "a small
`report`-mode golden-dataset evaluation set run through the existing
framework unmodified as grounding evidence." Because Document 76 §14 is a
**carry-forward restatement of Document 75 §14** — not an independent
requirement — once this amendment is ratified, Document 76 §14's
restatement of that one item is read **under the amended governance role**
established here, by reference. **Document 76 is not edited, not amended,
and not reinterpreted beyond that mechanical consequence of its own
"carried forward — Document 75 §14" framing.** If the CTO prefers Document
76 §14 to carry an explicit pointer to this amendment, that is a separate,
optional mechanical-hygiene edit, not part of this decision.

---

## 16. Governance Lineage

```text
D67  → C-4 recommendation                         🟢 CTO-RATIFIED
D68  → M15 = C-4 selection                        🟢 CTO-RATIFIED via D69
D69  → selection ratification                     🟢 CTO-RATIFIED
D70 R4 → API contract                             🟢 CTO-RATIFIED via D72
D72  → API-contract ratification                  🟢 CTO-RATIFIED
D73 R1 → architecture decision                    🟢 CTO-RATIFIED via D74
D74  → architecture ratification                  🟢 CTO-RATIFIED
D75  → M15 implementation authorization           🟢 CTO-RATIFIED via D76
D76  → ratification of D75                        🟢 CTO-RATIFIED
       ↓
D77  → bounded amendment / clarification of       🟡 PROPOSED HERE —
       D75 §14 (this document)                       pending CTO review
       ↓
D78  → future separate ratification of D77        NOT CREATED — a future,
                                                     separate CTO act
```

These are **distinct governance acts** and this document does not collapse
them. In particular: **Document 77 is a bounded amendment proposal;
Document 78 is its ratification.** Document 77 does not originate the M15
authorization, does not re-decide any ratified stage, does not ratify
itself, and does not create Document 78.

---

## 17. Ratification Status Required

**This document is a decision awaiting CTO review and ratification.** It
does not take effect on creation. The next legitimate governance action,
if the CTO accepts this proposal, is this document's own ratification — a
distinct act from drafting it — recorded in a future, separate document
(Document 78), mirroring Document 72's ratification of Document 70 and
Document 74's ratification of Document 73. Only after that ratification is
the Document 75 §14 amendment in §6 in effect. Even then, a further,
separate commit-authorization review, and a further, separate
push / merge / deployment authorization, remain required.

**Ratification status after Document 77 (this document): the amendment is
PROPOSED, not in effect.** Until Document 78 ratifies it, Document 75 §14
stands exactly as ratified via Document 76.

---

## 18. Repository / Working-Tree State and Provenance

Recorded by read-only inspection this session. **This is a point-in-time
snapshot observed during the creation of this proposal on 2026-09-07**,
not a claim about repository state at any later reading time. **No `git`
mutation was performed** — no `add`/stage, no `commit`, no `push`, no
`amend`, no `rebase`, no `merge`, no `reset`, no `restore`, no `stash`, no
`clean` beyond removing one 0-byte accidental tooling artifact this
session itself created (see below).

- `HEAD = origin/main = be4949b` (M14 implementation commit), unchanged.
- Document number 77 was verified free before creation (highest existing
  Backend & AI governance document was 76; no Document 77 existed prior to
  this task).
- **Documents 70–76 were read, not modified.** Their ratified content is
  cited, not amended, above. Document 75 is **not** edited in place; this
  document is the separate, auditable amendment record.
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval/RAG code, MongoDB collection, Redis
  component, provider, configuration, evaluation-infrastructure, or
  frontend file was created or modified. `.gitignore` was not modified.
- The working tree carries the in-progress, uncommitted M15 / C-4
  implementation and its tests (created and technically reviewed under
  Documents 75 / 76 in prior tasks) plus known, pre-existing, unrelated
  items. **None of these were staged, modified, renamed, deleted, or
  cleaned by this task:**

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
  ?? docs/backend_engineering/67_...md through 76_...md            (pre-existing untracked governance documents — not modified)
  ```

- One 0-byte file named `404)` — an accidental artifact created by this
  session's own shell tooling on 2026-09-07, not user work and not one of
  the named pre-existing artifacts — was removed. No other file was
  cleaned or deleted.
- This document adds one further untracked file — itself
  (`docs/backend_engineering/77_D75_Section14_Testing_Floor_Clarification_and_Amendment_Decision.md`).
  It is untracked and not yet version-controlled. Staging or committing it
  is a separate, subsequently CTO-authorized step.

---

**🟡 PROPOSED — BOUNDED AMENDMENT / CLARIFICATION OF DOCUMENT 75 §14.
DRAFT / PENDING CTO REVIEW. NOT YET RATIFIED. THIS DOCUMENT PROPOSES
EXACTLY ONE GOVERNANCE ACT: AMENDING THE ROLE OF THE GOLDEN-DATASET
`report`-MODE EVALUATION-EVIDENCE ITEM IN DOCUMENT 75 §14 (ITS EIGHTH
BULLET) SO THAT IT IS CLASSIFIED AS EVALUATION / VALIDATION EVIDENCE AND
TRACKED FOLLOW-UP WORK — NOT A MANDATORY PREREQUISITE FOR M15 / C-4
IMPLEMENTATION BEING CONSIDERED COMPLETE UNDER DOCUMENT 75 §14, AND NOT A
BAR TO A SEPARATE, SUBSEQUENTLY-GOVERNED COMMIT-AUTHORIZATION REVIEW. THE
GOLDEN-DATASET EVIDENCE REMAINS LEGITIMATE, DESIRABLE, TRACKED EVALUATION
EVIDENCE RELEVANT TO NARRATIVE-MODE QUALITY; IT IS NOT DECLARED
UNNECESSARY OR INVALID. THIS IS NOT A RETROACTIVE CLAIM THAT DOCUMENT 75
"NEVER REQUIRED" THE EVIDENCE — DOCUMENT 75 §14 AND DOCUMENT 76'S
RATIFICATION STAND AS HISTORICAL RECORD; DOCUMENT 77 IS A NEW,
FORWARD-LOOKING, AUDITABLE GOVERNANCE DECISION EFFECTIVE ONLY ON ITS OWN
SEPARATE RATIFICATION. THE FIRST SEVEN DOCUMENT 75 §14 BULLETS (UNIT;
INTEGRATION/CONTRACT; DETERMINISTIC FINANCIAL; NARRATIVE GROUNDING /
CITATION; PROCESS-LOCAL LIFECYCLE; M14 REGRESSION; SECURITY / VALIDATION)
REMAIN MANDATORY FLOOR ITEMS, UNWEAKENED. NO OTHER DOCUMENT 75 TESTING
REQUIREMENT IS WEAKENED, AND THIS AMENDMENT DOES NOT GENERALIZE TO ANY
OTHER REQUIREMENT. THIS AMENDMENT DOES NOT TOUCH DOCUMENT 70 R4, DOCUMENT
73 R1, DOCUMENT 74, DOCUMENT 76, AH-1, AH-2, PROCESS-LOCAL RESULT
RETENTION, THE FINANCIAL-COMPARISON REQUIREMENTS, THE NARRATIVE
SINGLE-CALL ARCHITECTURE, THE CITATION REQUIREMENTS, THE SECURITY
REQUIREMENTS, OR THE OBSERVABILITY REQUIREMENTS. THE EXISTING M15
IMPLEMENTATION HAS ALREADY BEEN TECHNICALLY REVIEWED AND ITS HERMETIC TEST
EVIDENCE REMAINS VALID; HERMETIC TESTS ARE A DIFFERENT EVIDENCE CLASS FROM
THE GOLDEN DATASET AND ARE NOT CLAIMED EQUIVALENT TO IT. THIS DOCUMENT
DOES NOT AUTHORIZE ANY EVALUATION ADAPTER, LOADER, INFRASTRUCTURE CHANGE,
NEW EVALUATION CODE, FIXTURES, CORPUS-GENERATION MACHINERY, OR LLM
EVALUATION INFRASTRUCTURE — ANY SUCH ENGINEERING REQUIRES SEPARATE
AUTHORIZATION. IT DOES NOT AUTHORIZE ADDITIONAL IMPLEMENTATION,
ARCHITECTURE OR CONTRACT CHANGES, COMMIT, PUSH, MERGE, DEPLOYMENT, OR
RELEASE — A LATER SEPARATE COMMIT-AUTHORIZATION REVIEW REMAINS REQUIRED.
LINEAGE: D75 → M15 IMPLEMENTATION AUTHORIZATION; D76 → RATIFICATION OF
D75; D77 → BOUNDED AMENDMENT / CLARIFICATION OF D75 §14; D78 → FUTURE
SEPARATE RATIFICATION OF D77 (NOT CREATED HERE). NO APPLICATION SOURCE,
TEST, CONFIGURATION, MONGODB, REDIS, FRONTEND, OR EVALUATION-INFRASTRUCTURE
FILE WAS CREATED OR MODIFIED. DOCUMENTS 70–76 WERE NOT MODIFIED — DOCUMENT
75 IS NOT EDITED IN PLACE. NO STAGE. NO COMMIT. NO PUSH. NO MERGE /
REBASE / RESET / AMEND. THE NEXT LEGITIMATE GOVERNANCE ACTION IS CTO
REVIEW AND RATIFICATION OF THIS AMENDMENT (A FUTURE DOCUMENT 78) — NOT
IMPLEMENTATION, AND NOT COMMIT.**
