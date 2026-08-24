# 49 — M11 Phase H-1: Generalization Evidence Record and CTO Closure Package

**Status:** 🟢 **RATIFIED — CTO CLOSURE DECISION RECORDED: CLOSE WITH
GOVERNANCE FOLLOW-UP (Option B, §19; disposition detail in §21).**
This document records completed diagnostic evidence, an independent audit of
it, and the CTO's final closure decision. Ratification of this record does
not authorize any implementation change, does not modify Document 47,
`judge.py`, the H-1 runner, or the historical Run 1 artifact, and does not
authorize a second execution — see §21 for the explicit governance boundary.
Follows the same "review, not ratification" convention as
[40_Document32_CTO_Decision_Review.md](40_Document32_CTO_Decision_Review.md)
and the same draft/addendum convention as
[48_M11_Phase_H_Property_Axis_Evidence_and_Scope_Addendum.md](48_M11_Phase_H_Property_Axis_Evidence_and_Scope_Addendum.md).
**Date:** 2026-08-23. **Ratified:** 2026-08-23.

**Governance-record note, stated plainly before anything else:** this
document was commissioned describing Reviewer 3's disposition as *"PASS WITH
GOVERNANCE FOLLOW-UP"* and citing *"20/20 ratified controls passed."*
Reviewer 3's actual recorded disposition (this session, prior turn) was
**`CONDITIONAL`**, not `PASS` — a distinct enum value the review's own
instructions defined precisely, and the two are not interchangeable. The
underlying count is **4 ratified controls (G1, G2, G4a, G6), each replicated
5 times, yielding 20 trial-level observations that all matched their
control's expected verdict** — not 20 independent controls. Both
corrections are recorded here verbatim rather than silently adopting the
stronger/larger framing, because silently strengthening an audit's own
conclusion is exactly the kind of provenance drift this document exists to
prevent. The substantive conclusions are otherwise unaffected: methodology
sound for the narrow authorized claim, no Run 2 currently justified, no
implementation change authorized, G7 unresolved, G8 carried forward.

---

## 1. Experiment Identity

`M11 Phase H-1 — Generalization Matrix`, experiment id
`M11-PhaseH1-Generalization-run1`, runner
[`backend/scripts/run_m11_phase_h1_generalization.py`](../../backend/scripts/run_m11_phase_h1_generalization.py).

## 2. Authorization Identity

Designed, corrected per CTO instruction (G3 demoted from an assumed oracle;
G4a/G4b restructured into a genuine one-variable minimal pair; matrix
partitioned into ratified positive/negative controls, unratified boundary
probes, and one intentional ambiguity probe), independently adjudicated by
Reviewer 2 against Document 47 §7.3.1's actual ratified and open-boundary
text, and executed under explicit CTO live-execution authorization — all
within this session. **No file in the repository records this chain
independently of this document and its own §7 below** — see the provenance
note in §7.

## 3. Historical Run 1 Artifact Path

[`backend/evaluation/self_consistency/phase_h1_generalization_matrix/results/phase_h1_generalization_run1.json`](../../backend/evaluation/self_consistency/phase_h1_generalization_matrix/results/phase_h1_generalization_run1.json) —
MD5 `59d28c3d76e28973f911b55432a09c05` (recorded here as the value confirmed
at the time of this document's authoring; unmodified by this document).

## 4. Execution Status

Complete. 10 cases, 50 Stage-1 calls, 28 Stage-2 calls, 78 total live calls,
zero structured-output failures, zero recovery-path invocations. No Run 2
has been executed or authorized.

## 5. Reviewer 3 Disposition

**`CONDITIONAL`** (Reviewer 3's own recorded enum value — see the
governance-record note above for the correction against this task's supplied
"PASS WITH GOVERNANCE FOLLOW-UP" framing). Substance: Run 1 substantially
supports the narrow authorized diagnostic claim; a specific, bounded
finding (G8, §14 below) must be carried forward and documented, not
resolved, before H-1 is treated as fully closed.

## 6. Methodology Assessment

Reviewer 3 found the executed methodology internally consistent with the
authorized design (four-way case partition, Stage 1 → conditional Stage 2
control flow matching production exactly, full provenance recording) and
capable of detecting instability where present (confirmed by G3's own
observed 3/2 split within the same run). Reviewer 3 also identified, and
this document preserves rather than smooths over: surface-phrasing
homogeneity across all 10 cases; structural overlap between G1 and G4a as
positive-control mechanisms; and a plausible lexical-overlap alternative
explanation for the G4a/G4b minimal-pair result. None of these were found to
be closure-blocking.

## 7. Accounting / Provenance Resolution

Resolved, with one honestly-stated residual gap. The runner's exact source
at execution time is git-verifiable (present, unmodified, at commit
`2e5e50d`). The result artifact's file-modification timestamp matches its
own internal `generated_at` field exactly, evidencing it has not been
altered since generation. The reported 78 total calls were independently
recounted from raw trial records (50 Stage-1 + 28 Stage-2) and reconcile
exactly. **Residual gap, not resolved by this document:** the H-1 design,
its CTO-mandated corrections, and the Reviewer 2 adjudication were never
written to any repository file before this document — they existed only in
conversational form. This document is the first persistent record of that
chain; no earlier document exists to cite for it.

## 8. Ratified Controls — 4 Controls / 20 Trial-Level Observations

| Control | Expected | Observed (5 trials each) | Result |
|---|---|---|---|
| G1 — component→aggregate | APPLICABLE | 5/5 APPLICABLE | Matches |
| G2 — aggregate→component | APPLICABLE | 5/5 APPLICABLE | Matches |
| G4a — explicit multi-component | APPLICABLE | 5/5 APPLICABLE | Matches |
| G6 — correlated metric (negative) | NOT_APPLICABLE | 5/5 NOT_APPLICABLE | Matches |

All 20 trial-level observations across these 4 controls matched their
control's expected verdict, on wording never used in the prior M-04/M-05
experiments. Reviewer 3's own audit notes G6 is an "easy" negative (zero
shared quantity at all) and G1/G4a share a similar single-hop mechanism —
both caveats preserved in §6 above, not omitted here.

## 9. G3 Finding — Classification: Observed

3/5 APPLICABLE, 2/5 NOT_APPLICABLE on a two-hop nested-component case
(team ⊂ division ⊂ company). Rationale text diverged visibly across trials:
two trials explicitly reasoned the chain was "not a direct" component
(correctly invoking directness as disqualifying); one trial explicitly
mislabeled the two-hop relationship as "direct." **This is recorded as
observed genuine semantic instability, not as a new policy.** No
transitive-component applicability rule is adopted by this record.

## 10. G4b Finding — Classification: Observed / Confounded

Identical 5/5 APPLICABLE result to its paired control G4a. **Useful**: no
observed difference occurred when the evidence-side membership restatement
was removed while the claim-side enumeration was held constant. **Confounded**:
the word "finished goods" appears verbatim in both the claim's enumerated
component list and the evidence in both G4a and G4b, so the identical result
is equally explained by simple lexical overlap as by genuine reasoning about
explicit-vs-implicit membership statements. This record does not adopt
"claim-side enumeration is sufficient" as a rule — it is preserved as a
useful-but-confounded single-case observation only.

## 11. G5a Finding — Classification: Observed

5/5 NOT_APPLICABLE on a gross-margin-vs-operating-income pair, directly
instantiating Document 47 §7.3.1's own still-open "related-but-distinct
metric tier" (`MORE EVIDENCE REQUIRED`). Recorded as an observation of
current model behavior on an explicitly open boundary — **not** adopted as
policy, and the open boundary itself remains exactly as open as §7.3.1
already states.

## 12. G5b Finding — Classification: Observed

5/5 NOT_APPLICABLE on a units-sold-vs-revenue pair (a multiplicative, not
additive, relationship — deliberately kept analytically distinct from G5a
per the original design). Rationale explicitly distinguished this from a
stated component/aggregate relationship. Recorded as an observation only,
under the same open boundary as G5a — not collapsed into a single "related
metric" conclusion, and not adopted as policy.

## 13. G7 — Explicitly Unresolved

5/5 NOT_APPLICABLE on a causal-prerequisite case (capacity expansion vs.
production output). Because no trial returned APPLICABLE, the rationale-path
analysis (distinguishing an intended causal reading from a possible
modality misreading) had nothing to classify — this is stated explicitly,
not silently passed over. **G7 is not classified as passed, failed, or
resolved.** No causal-prerequisite exclusion rule is ratified, proposed as
ratified, or implied by this record. It remains exactly as unresolved as it
was before this run — the single fact newly established is that the
specific pre-registered risk of modality-conflation did not appear in any
of the 5 rationales.

## 14. G8 — Carry-Forward Finding (Dedicated Section)

**1. What was observed.** In all 5 of 5 trials, the judge returned
APPLICABLE for a claim about "total North American sales" given evidence
about "western United States" sales, with every rationale asserting the
region is a "stated component" or "direct component" of the claimed
aggregate. **No such statement exists anywhere in the evidence text** — the
source never uses "one of," an enumeration, or any membership marker; the
regional boundary (Canada/Mexico inclusion, exhaustiveness of "western
United States") is entirely unestablished by the text. Zero of the 5 trials
hedged or flagged this absence.

**2. Why it matters to grounded financial research.** AlphaScribe's stated
purpose is grounded, source-traceable AI research output. A judge that
treats plausible real-world geographic containment as if the source text
had explicitly stated it — with no hedge, 5/5 times — is exhibiting exactly
the shape of failure a hallucination-detection judge exists to catch:
confident assertion of a relationship the source does not establish.

**3. Why it is not yet an implementation requirement.** G8 is a single case
(one geographic ambiguity, one wording), oracle-free by design. It
establishes that this specific behavior is reproducible for this specific
case — not that it generalizes across ambiguous-membership cases broadly,
not a rate, not a production defect measurement. Document 47 §9.1's gate
remains at version 0 specifically because no `model_judged_support` result,
including this one, is yet trusted for production-equivalent decisions.

**4. Architectural concerns it may affect (if the CTO later authorizes
further work):** evidence classification (does "plausible but unstated"
membership warrant its own category, distinct from "explicit"?); grounding
(does an inferred-membership APPLICABLE verdict undermine the
support-classification stage's own grounding claim?); citation semantics and
source attribution (none of AlphaScribe's existing citation machinery
currently distinguishes a citation resting on stated vs. inferred
membership); explicit-vs-inferred claims generally (a distinction the
production pipeline does not currently make anywhere); and model-output
trustworthiness disclosure (whether `JudgeDetail` should ever record *how*
an applicability conclusion was reached, not only *what* it concluded). No
technical implementation is prescribed here for any of these — this section
names where a future architectural decision might need to look, nothing more.

**5. Decision remaining for the CTO.** Whether this finding warrants opening
a new architectural investigation (parallel to how Document 47 itself
originated), whether it should simply remain a documented, monitored
limitation, or whether it changes any risk assessment already on record
elsewhere (e.g., Document 47 §9's own "false confidence is the primary risk
this document exists to prevent" framing, `10_Backend_Security_Architecture.md`'s
`SR-5` residual-risk acceptance).

**6. Whether future architecture work should account for it.** This
document does not decide that question — it is exactly the open decision
named in item 5, deliberately left to the CTO.

## 15. Run 2 Decision

**RUN2 NOT REQUIRED.** Reviewer 3 found Run 1 sufficient for the narrow
authorized diagnostic claim and identified no unresolved methodological
defect that only a second execution could resolve. This is not a claim that
H-1 proves generalization broadly — only that another execution is not
currently justified under the scope actually authorized.

## 16. Implementation Decision

**NO IMPLEMENTATION CHANGE AUTHORIZED BY H-1.** H-1's findings, including
G8, may inform future architecture or policy work, but do not themselves
authorize any code, prompt, schema, or gate change. Any future G8-related
remediation requires its own, separate architectural decision and CTO
authorization — none is granted here.

## 17. Governance Implications

Document 47 §7.3.1's already-ratified component/aggregate rule (§8 above)
is supported, not amended, by this evidence. The related-but-distinct
metric tier (G5a/G5b) and the causal-prerequisite question (G7) remain
exactly as open as Document 47 and this session's prior addendum
(Document 48) already left them. G8 introduces a new, previously
undocumented observation that did not exist in Document 47 or Document 48's
scope — it is net-new evidence, not a resolution of anything already open.

## 18. Open Decisions

1. Whether to formally ratify this document (or supersede it) as the H-1
   closure record.
2. Which CTO decision option (§19) to select.
3. Whether G8 warrants a dedicated future architectural investigation.
4. Whether the related-but-distinct metric tier (§7.3.1's own open boundary)
   should be revisited given G5a/G5b's observations — not required, but now
   possible with two additional data points on record.

**Resolved 2026-08-23, under CTO governance authority:** Item 1 — this
document is ratified as the H-1 closure record. Item 2 — Option B selected
(§19, §21). Items 3 and 4 remain open and are carried forward per §21's
governance boundary — resolving H-1's closure does not resolve them.

## 19. CTO Decision Options

**Option A — CLOSE.** Close H-1; treat G7 and G8 as documented limitations
for future consideration, with no further governance action required now.

**Option B — CLOSE WITH GOVERNANCE FOLLOW-UP. [SELECTED — see §21]** Close
H-1 while explicitly carrying G7 and G8 into the next relevant
architecture/governance work item (e.g., a future Document 47 revision or a
dedicated evidence-classification investigation).

**Option C — HOLD.** Do not close H-1 if the CTO determines any finding
above conflicts with an existing frozen requirement. No new experiment is
selected under this option unless separately authorized.

## 20. Audit / Provenance References

Reviewer 2 adjudication (this session, prior turn) — G3/G4b/G5a/G5b/G7
classified UNRESOLVED, G8 classified UNRATIFIED_BY_DESIGN, against Document
47 §7.3.1's cited text. CTO live-execution authorization and execution
report (this session). Reviewer 3 independent audit (this session, prior
turn) — disposition `CONDITIONAL`, Run 2 decision `RUN2_NOT_JUSTIFIED`. Run 1
artifact MD5 `59d28c3d76e28973f911b55432a09c05`, git HEAD `2e5e50d` for the
runner's source. All of the above exist only as conversational record prior
to this document — see §7's residual provenance gap.

## 21. CTO Final Governance Disposition

Recorded 2026-08-23, under CTO governance authority, closing M11 Phase H-1
(Option B, §19 selected).

```text
Reviewer 3 disposition:
CONDITIONAL

Ratified controls:
4

Repetitions per ratified control:
5

Matching trial-level observations:
20

Interpretation:
4 ratified controls x 5 repetitions = 20 matching trial-level observations
(not 20 independent controls)

Unratified probes:
Behavioral observations only

Run 2:
Not required / not authorized

Implementation:
Not authorized by H-1

G7:
Unresolved

G8:
Carried forward

Final CTO disposition:
CLOSE WITH GOVERNANCE FOLLOW-UP
```

**Governance boundary.** H-1 is closed, as of this disposition, for its
narrow authorized diagnostic purpose only. G7, G8, grounding semantics,
explicit-vs-inferred evidence, geographic inference, citation/evidence
classification, and related AI reliability behavior are carried forward as
open items — they are not silently appended to H-1's scope. Any future work
on them, including a Run 2, requires its own separate governance or
architecture authorization identifying a new experiment identity, a new
immutable output path, the exact unresolved hypothesis, and the reason Run 1
cannot answer it. This document grants no such authorization.

H-1 work stops as of this disposition. Control returns to the CTO for the
next separately authorized architecture/governance task.
