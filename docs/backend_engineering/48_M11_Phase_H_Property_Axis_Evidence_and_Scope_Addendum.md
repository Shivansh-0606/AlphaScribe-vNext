# 48 — M11 Phase H: Property-Axis Evidence Log and Non-Generalization Scope Addendum

**Status:** 🔵 **DRAFT — PREPARED FOR REVIEWER 2 / CTO REVIEW. NOT RATIFIED.**
This document evaluates the M11 Phase H Rev 5 M-04/M-05 controlled-pair
experiment against [Document 47](47_Hallucination_Detection_Architecture_Decision_Pack.md)
as it actually stands in the repository today. It does not itself amend,
ratify, or modify Document 47, does not change `judge.py`, `schemas.py`, or
`judge_gate.py`, does not change `JUDGE_SELF_CONSISTENCY_GATE_VERSION`, does
not create or modify any evaluation case or golden-dataset entry, and does
not authorize any live provider call or new experiment. Everything below is
a documentation-only record, following the same "review, not ratification"
convention as
[40_Document32_CTO_Decision_Review.md](40_Document32_CTO_Decision_Review.md)
and the same "smallest possible addition, no silent rewrite" convention as
[37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md](37_Document33_Amendment_Financials_Acquisition_Request_Endpoint.md).
**Date:** 2026-08-22.

---

## 1. Experiment identifier, oracle, and observed result

**Experiment:** `M11-PhaseH-Rev5-M04-M05-run1`, executed 2026-08-22, raw
output preserved unmodified at
[`backend/evaluation/self_consistency/phase_h_m04_m05_controlled_pair/results/phase_h_rev5_run1.json`](../../backend/evaluation/self_consistency/phase_h_m04_m05_controlled_pair/results/phase_h_rev5_run1.json).
**This file is historical evidence and is not touched by this addendum.**

| Case | Claim | Evidence | Human oracle (`human_applicability`) | Human oracle (`human_expected_support`) |
|---|---|---|---|---|
| M-04 | Total revenue (Hardware+Software+Services) expected to grow in Q3 | Hardware segment generated $40M in Q2 revenue | `APPLICABLE` | `UNSUPPORTED` |
| M-05 | Total units shipped (Direct+Retail+Wholesale) expected to grow in Q3 | Direct channel shipped 40,000 units in Q2 | `APPLICABLE` | `UNSUPPORTED` |

**Observed live Stage-1 result**, 5 repeats per case, `nvidia/nemotron-3-super-120b-a12b`, temperature 0.0, all outputs parsed successfully (no malformed/schema-invalid output, no parse-recovery path exercised):

- M-04: `NOT_APPLICABLE` 5/5.
- M-05: `NOT_APPLICABLE` 4/5, `APPLICABLE` 1/5 (trial 4). The one `APPLICABLE` trial proceeded to Stage 2 and returned `UNSUPPORTED` — the only trial whose end-to-end outcome matches the oracle's full expected verdict.

**Dominant failure rationale, quoted verbatim from the raw artifact** (M-04 trial 0): *"a different underlying quantity (segment-level revenue vs. total revenue)"*; (M-05 trial 2): *"different aggregation levels of the units shipped metric, thus different underlying quantities."* All nine `NOT_APPLICABLE` trials independently state this same reasoning: a component figure offered against its own aggregate is treated as a different underlying quantity, not a scope variation of the same one.

## 2. What Document 47 already states — this is not a new rule

Direct inspection of [Document 47 §7.3.1](47_Hallucination_Detection_Architecture_Decision_Pack.md), the **"Property axis — what it is measured over (frozen, Revision 6)"** block (ratified 2026-08-19, three days before this experiment ran), already states:

> "Evidence concerns the **same property** as the claim when it concerns that same underlying quantity or business fact, **a stated direct component of it, or the aggregate of which it is a stated direct component**."

and, immediately below its four-dimension list (modality, polarity, tense/aspect, granularity/units):

> "**Direct component and aggregate relationships are applicable but may be insufficient.** Evidence about a stated direct component of the claim's quantity (e.g. **a segment's revenue offered against a total-revenue claim**), or about the aggregate of which the claim's quantity is a stated direct component (e.g. total revenue offered against a segment-revenue claim), clears the property axis. Clearing the property axis is not support: such evidence commonly fails to establish the claim's specific proposition, and is then `UNSUPPORTED`."

M-04's exact fact pattern (segment revenue vs. total revenue) is Document 47's own worked example. M-05 (channel units shipped vs. total units shipped) is the same relationship in a different domain, consistent with §7.3.1's "warehouse inventory → total inventory, where the aggregate is explicitly defined" pattern.

**Conclusion, stated plainly and not overclaimed:** the semantic rule this task's CTO-decision background describes — *"a literal direct component of an aggregate quantity is APPLICABLE to the aggregate claim's property axis"* — is **already CTO-ratified policy**, recorded in Document 47 Revision 6, §7.3.1. It is not a new governance decision. What Phase H's M-04/M-05 experiment supplies is **empirical evidence that the currently-deployed judge does not yet implement it** (§3 below), plus a scope question §7.3.1 does not yet address (§4 below).

## 3. Root cause: a prompt-implementation gap, not a policy gap

Direct search of [`backend/evaluation/core/judge.py`](../../backend/evaluation/core/judge.py) for `granularity`, `component`, and `aggregate` returns **zero matches**. The Stage-1 applicability prompt (`_APPLICABILITY_SYSTEM_PROMPT`, judge.py lines 150-188) enumerates exactly three tolerated variation dimensions verbatim:

> "...even when it differs from CLAIM in tense or time period... in modality... or in polarity..."

Document 47 §7.3.1 Revision 6 enumerates **four**: modality, polarity, tense/aspect, and **granularity/units** — "segment versus consolidated... A stated direct component or aggregate of the claim's quantity is the same property at a different granularity." The fourth dimension, the one that directly governs M-04/M-05, was never carried into the judge's actual prompt text. `JUDGE_PROMPT_VERSION`/`JUDGE_ARCHITECTURE_VERSION` (judge.py:25, :129) have not been bumped since Revision 6 was ratified — consistent with the prompt never having been revisited to reflect it.

This is the most defensible explanation for the 9/10 combined `NOT_APPLICABLE` result: the model was never told, in-prompt, that a component/aggregate relationship is a granularity difference rather than a quantity difference, so it defaulted to the more conservative (and, per §7.3.1, incorrect) reading in nine of ten trials, and reached the §7.3.1-consistent reading in one.

**No inference beyond the evidence is drawn here about *why* one trial diverged from the other nine at temperature 0** — see the prior forensic analysis (M11 Phase H Forensic Analysis, delivered earlier this session, not a committed document) for that separate question. This addendum's scope is the policy-to-prompt gap, which is independent of whatever mechanism produced the 1/5 vs. 4/5 split.

## 4. Scope clarification proposed — not yet in Document 47, not yet ratified

Document 47 §7.3.1 resolves the literal component/aggregate case (§2 above) and separately leaves an **"Open boundary — the related-but-distinct metric tier"** unresolved (gross margin vs. operating margin — `MORE EVIDENCE REQUIRED`). Neither of those two provisions states whether the property axis extends to relationships that are related to a component/aggregate pair but are not themselves a literal part-whole relationship. Direct search of Document 47 for "causal," "prerequisite," "milestone," and "correlated metric" returns no matches — **this boundary does not exist in Document 47 today in any form**, ratified or open.

The following non-generalization boundary is recorded here **as a proposed clarification for Reviewer 2 and CTO consideration**, distinct from and narrower in scope than §7.3.1's existing open "related-but-distinct metric tier":

- **In scope for the already-ratified component/aggregate rule (§2):** evidence that is a stated literal direct component of the claim's quantity, or the stated literal aggregate of which the claim's quantity is a component (segment→total revenue, channel→total units shipped, warehouse→total inventory where the aggregate is explicitly defined).
- **Proposed as explicitly out of scope, pending ratification:**
  - **Causal prerequisites** — evidence establishing a precondition for the claim's quantity, not a part of it (e.g. "the factory received regulatory approval" offered against "total output will grow").
  - **Milestones** — evidence about a discrete event on a path toward the claim, not a component of the claim's quantity itself.
  - **Correlated metrics** — evidence about a different metric that empirically moves together with the claim's quantity but is not a stated part or whole of it.
  - **Merely related metrics** — the same shape as §7.3.1's own still-open "related-but-distinct metric tier" (gross margin vs. operating margin); this addendum does not attempt to resolve that tier and explicitly defers to §7.3.1's existing `MORE EVIDENCE REQUIRED` status for it.
  - **Meta-level disclosure/process facts** — evidence about whether or how something will be disclosed (Document 47 §7.3.1's own explicit-absence rule already governs this territory for the `UNSUPPORTED`-vs-`NOT_APPLICABLE` question; this addendum does not reopen that).
  - **Unrelated facts** — evidence with no stated part-whole, causal, or correlational relationship to the claim's quantity at all; unaffected by any of the above.

**This section is not a Document 47 amendment.** It is offered as the smallest addition needed to prevent the already-ratified component/aggregate rule from being generalized, by a future prompt change, beyond literal part-whole relationships — a risk this document's drafting made concrete once the fix for M-04/M-05 was traced to a missing prompt dimension. Folding this into Document 47 (as a future Revision 7, narrower in scope than Revision 6) is a separate, subsequent CTO/Reviewer-2 act, not performed here.

## 5. Governance provenance gap — recorded, not resolved

The M-04/M-05 case pair and its `human_applicability`/`human_expected_support` oracle values exist **only** as literals inside
[`backend/scripts/run_m11_phase_h_m04_m05.py`](../../backend/scripts/run_m11_phase_h_m04_m05.py)
(lines 74-105) and in the results JSON the same script writes. Direct search
of Document 47, the
[Requirements Traceability Matrix](../governance/Requirements_Traceability_Matrix.md),
and `evaluation/self_consistency/cases.py`/`cases/` finds no independent
registration of "Phase H," "M-04," or "M-05" anywhere outside that one
script and its own output. The oracle is self-declared by the same artifact
that produced the results being measured against it, and "Phase H Revision
5" has no header, freeze date, or ratification record of its own in Document
47 the way Revisions 1–6 do. This is a real gap, distinct from the §7.3.1
policy content — it concerns the experiment's own governance standing, not
whether its finding is correct. No action is taken on it here; it is
recorded so Reviewer 2/CTO can decide whether formal registration (as a
Document 47 revision, a §7.3.1 worked example, or a held-out
`evaluation/self_consistency/cases.py` entry) is warranted before this
experiment is cited as evidence in any future decision.

## 6. Explicit non-actions (this addendum only)

- `judge.py`, `schemas.py`, `judge_gate.py`: **not modified.**
- `JUDGE_SELF_CONSISTENCY_GATE_VERSION`: **unchanged, still `0`.**
- `JUDGE_PROMPT_VERSION` / `JUDGE_ARCHITECTURE_VERSION`: **unchanged.**
- No evaluation case, fixture, or golden-dataset entry created or modified.
- `phase_h_rev5_run1.json`: **unmodified, preserved as historical evidence.**
- No live provider call made in the preparation of this document.
- No new experiment started or authorized.
- Document 47: **not edited.** Its ratified content is quoted, not altered.
- No production judge behavior has changed as a result of this document.

## 7. Remaining CTO / Reviewer-2 decision required

1. **Confirm §2's reading is correct**: that Document 47 §7.3.1 Revision 6 already covers the M-04/M-05 fact pattern, so no new component/aggregate policy decision is needed — only a prompt-implementation fix (out of scope here, and gated on Reviewer 2 per this task's own instruction).
2. **Rule on §4's proposed non-generalization boundary**: whether to ratify it (as a future, narrower Document 47 revision), request changes to its category list, or decline to formalize it and rely on case-by-case judgment instead.
3. **Rule on §5's provenance gap**: whether Phase H/M-04/M-05 needs formal registration in Document 47 or the held-out case set before being relied upon further, or whether this addendum's citation is sufficient standing for now.
4. **Authorize (separately, later) the actual judge-prompt change** implementing §2's already-ratified rule and §4's boundary (if ratified) — explicitly not requested or performed by this document.
