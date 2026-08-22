"""M11 Phase H-1 -- CTO-authorized generalization-validation DIAGNOSTIC
experiment for the Document 47 SS7.3.1 component/aggregate granularity rule.

DIAGNOSTIC / SELF-CONSISTENCY ONLY. Not part of any permanent corpus, not a
Document 47 revision, not a golden-dataset case, not wired into
evaluation.core.case_evaluator or evaluation.core.judge_gate at all -- the
same isolation discipline evaluation/self_consistency/runner.py's own
docstring already states for the self-consistency tooling. Produces evidence
for a later, separate CTO/Reviewer-2 decision; promotes nothing by itself.

This is a NEW, independently-named experiment (not a Phase H revision): it
tests whether the already-shipped Rev 6 component/aggregate fix generalizes
beyond the frozen M-04/M-05 pair, not whether Rev 6 fixed M-04/M-05 (that
question is already closed, see phase_h_rev6_run1.json). Reuses
judge.invoke_applicability_judge / invoke_support_judge exactly as every
prior M11 diagnostic script this session has -- no new production runner, no
edit to judge.py/schemas.py/behaviors.py/types.py/judge_gate.py, no edit to
JUDGE_ARCHITECTURE_VERSION/APPLICABILITY_PROMPT_VERSION/SUPPORT_PROMPT_VERSION,
no edit to Document 47, no edit to any Rev 5/Rev 6 historical artifact. Its
own output directory and filename are new and cannot collide with either.

CASE MATRIX -- four-way partition (CTO-mandated correction of this
experiment's original design draft):

  ratified_positive_control   -- Document 47 SS7.3.1 already explicitly
                                  supports APPLICABLE; cited verbatim below.
  ratified_negative_control   -- SS7.3.1 already explicitly supports
                                  NOT_APPLICABLE; cited verbatim below.
  unratified_boundary_probe   -- SS7.3.1 is silent or explicitly declines to
                                  resolve this relationship (its own "Open
                                  boundary" language, or a relationship SS7.3.1
                                  never addresses at all, e.g. nesting depth
                                  or causal prerequisites). expected_stage1
                                  is deliberately None -- NOT a guess by this
                                  script's author, and NOT to be treated as
                                  frozen until Reviewer 2 independently
                                  ratifies an interpretation.
  intentional_ambiguity_probe -- constructed so the source text itself does
                                  not establish population/membership
                                  boundaries. expected_stage1 is None by
                                  design, not merely pending adjudication --
                                  the point of this probe is to observe
                                  whether the judge's own rationale
                                  acknowledges the ambiguity, not to score it
                                  against a "correct" answer.

READING THE RESULTS -- CTO correction #6, binding on any future analysis of
this script's output: every category above except the two ratified controls
is represented by at most two cases (most by exactly one). A single case's
5-repetition outcome characterizes THAT CASE across 5 trials -- it must
never be read as characterizing its entire semantic category. Report
case-level stability (does this one case's 5 trials agree with each other)
and cross-case directional evidence (do several probes in the same bucket
point the same way) only. No per-category "accuracy" or "rate" number is
computed by this script or authorized by this docstring.

G4a/G4b are a genuine one-variable minimal pair (CTO-mandated correction):
the claim's own aggregate definition ("the sum of raw materials,
work-in-progress, and finished goods") is IDENTICAL in both cases; only the
EVIDENCE differs -- G4a's evidence explicitly states "one of the three
components comprising total inventory," G4b's does not. No other wording
differs between them.

G3 (CTO-mandated correction): originally drafted assigning APPLICABLE to a
two-hop transitive-membership case (team subset of division subset of
company). That assignment is removed here -- Document 47 SS7.3.1 states
applicability for "a stated direct component" (one hop) and does not address
whether the rule composes across a chain. G3 is filed as an
unratified_boundary_probe with expected_stage1_applicability=None, not
assigned APPLICABLE by this script's own authority.

Usage:
    python backend/scripts/run_m11_phase_h1_generalization.py
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

_BACKEND_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, str(_BACKEND_ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(_BACKEND_ROOT / ".env")

from agents.llm import _active  # noqa: E402
from evaluation.core import judge as judge_module  # noqa: E402 (read-only import)
from evaluation.core import judge_gate  # noqa: E402 (read-only import)
from evaluation.core.behaviors import _JUDGE_VERDICT_TO_STATUS  # noqa: E402 (read-only import, exact fidelity)

_RESULTS_DIR = _BACKEND_ROOT / "evaluation" / "self_consistency" / "phase_h1_generalization_matrix" / "results"
_OUTPUT_PATH = _RESULTS_DIR / "phase_h1_generalization_run1.json"

_VERDICT_RECOVERY_RE = re.compile(r'"(applicability|verdict)"\s*:\s*"([A-Z_]+)"')


def _recover_supplementary(error_message: str) -> dict | None:
    m = _VERDICT_RECOVERY_RE.search(error_message)
    return {"field": m.group(1), "value": m.group(2)} if m else None


# ---------------------------------------------------------------------------
# CASE MATRIX -- 10 cases, none reusing M-04/M-05 wording. Every case not in
# a "ratified_*" bucket has expected_stage1_applicability=None: an absent
# oracle value here is a deliberate refusal to freeze it, not an omission.
# ---------------------------------------------------------------------------
CASES = [
    {
        "case_id": "G1-component-to-aggregate",
        "category": "ratified_positive_control",
        "relationship_label": "component",
        "membership_status": "explicit",
        "manipulated_variable": None,
        "paired_with": None,
        "claim": "The company's total operating expenses are expected to increase in Q3.",
        "evidence": (
            "Research and development expense, one of the company's three operating "
            "expense categories, was $22 million in Q2."
        ),
        "expected_stage1_applicability": "APPLICABLE",
        "expected_stage2_support": "UNSUPPORTED",
        "oracle_status": "RATIFIED",
        "oracle_citation": (
            "Document 47 SS7.3.1, 'Direct component and aggregate relationships are "
            "applicable but may be insufficient': 'Evidence about a stated direct "
            "component of the claim's quantity (e.g. a segment's revenue offered "
            "against a total-revenue claim)... clears the property axis.'"
        ),
        "oracle_rationale": (
            "R&D expense is a stated direct component of total operating expenses -- "
            "same underlying quantity at a different granularity, per SS7.3.1's own "
            "worked example structure."
        ),
    },
    {
        "case_id": "G2-aggregate-to-component",
        "category": "ratified_positive_control",
        "relationship_label": "aggregate",
        "membership_status": "explicit",
        "manipulated_variable": "reference direction (vs. G1)",
        "paired_with": "G1-component-to-aggregate",
        "claim": (
            "The company's marketing expense, one of its three operating expense "
            "categories, is expected to increase in Q3."
        ),
        "evidence": "Total operating expenses were $58 million in Q2.",
        "expected_stage1_applicability": "APPLICABLE",
        "expected_stage2_support": "UNSUPPORTED",
        "oracle_status": "RATIFIED",
        "oracle_citation": (
            "Document 47 SS7.3.1: '...or about the aggregate of which the claim's "
            "quantity is a stated direct component (e.g. total revenue offered "
            "against a segment-revenue claim), clears the property axis.' -- the "
            "reverse direction is explicitly named, not assumed symmetric by this script."
        ),
        "oracle_rationale": (
            "Reverse of G1: claim is the component, evidence is the aggregate. "
            "SS7.3.1 states this direction explicitly."
        ),
    },
    {
        "case_id": "G3-nested-component-unratified",
        "category": "unratified_boundary_probe",
        "relationship_label": "nested_component",
        "membership_status": "explicit_at_each_hop",
        "manipulated_variable": "transitive/nesting depth",
        "paired_with": None,
        "claim": "The company's total company-wide headcount is expected to grow in Q3.",
        "evidence": (
            "Within the Engineering division, the Backend team -- one of Engineering's "
            "four teams -- had 40 employees at the end of Q2. Engineering is one of "
            "the company's three divisions."
        ),
        "expected_stage1_applicability": None,
        "expected_stage2_support": None,
        "oracle_status": "UNRATIFIED",
        "oracle_citation": (
            "Document 47 SS7.3.1 states applicability for 'a stated direct component' "
            "(one hop) or 'the aggregate of which it is a stated direct component' -- "
            "it does not address a component-of-a-component (two-hop transitive) "
            "relationship at all."
        ),
        "oracle_rationale": (
            "CTO-mandated correction: this case was originally assigned APPLICABLE by "
            "this experiment's draft design on the assumption that SS7.3.1's rule "
            "composes transitively. That assumption is not ratified and is removed "
            "here. Whether Backend-team headcount counts as a 'stated direct "
            "component' of company-wide headcount two hops up the org chart is left "
            "to Reviewer 2, not assigned by this script."
        ),
    },
    {
        "case_id": "G4a-explicit-multicomponent",
        "category": "ratified_positive_control",
        "relationship_label": "component",
        "membership_status": "explicit",
        "manipulated_variable": None,
        "paired_with": "G4b-implicit-membership-minimal-pair",
        "claim": (
            "The company's total inventory, the sum of raw materials, "
            "work-in-progress, and finished goods, is expected to decrease in Q3."
        ),
        "evidence": (
            "Finished goods inventory, one of the three components comprising total "
            "inventory, was $15 million at the end of Q2."
        ),
        "expected_stage1_applicability": "APPLICABLE",
        "expected_stage2_support": "UNSUPPORTED",
        "oracle_status": "RATIFIED",
        "oracle_citation": (
            "Document 47 SS7.3.1's direct-component rule, same shape as G1, with an "
            "explicit multi-component enumeration in the claim."
        ),
        "oracle_rationale": (
            "Finished goods is one of three explicitly enumerated components of the "
            "claimed total, and the evidence itself restates that membership."
        ),
    },
    {
        "case_id": "G4b-implicit-membership-minimal-pair",
        "category": "unratified_boundary_probe",
        "relationship_label": "component",
        "membership_status": "inferred_from_claim_enumeration_only",
        "manipulated_variable": "membership stated in evidence: yes (G4a) vs. no (G4b)",
        "paired_with": "G4a-explicit-multicomponent",
        "claim": (
            "The company's total inventory, the sum of raw materials, "
            "work-in-progress, and finished goods, is expected to decrease in Q3."
        ),
        "evidence": "Finished goods inventory was $15 million at the end of Q2.",
        "expected_stage1_applicability": None,
        "expected_stage2_support": None,
        "oracle_status": "UNRATIFIED",
        "oracle_citation": (
            "Document 47 SS7.3.1 does not specify whether the explicit membership "
            "statement must appear in the evidence itself, or whether the claim's own "
            "enumeration (which names 'finished goods' as one of the total's three "
            "parts) is sufficient on its own."
        ),
        "oracle_rationale": (
            "CTO-mandated minimal pair against G4a: claim text is byte-identical to "
            "G4a's (same aggregate definition, same three named components); only "
            "the evidence's own explicit membership phrase is removed. This isolates "
            "exactly one variable -- whether removing the evidence-side restatement "
            "of membership (while the claim-side enumeration is still present) "
            "changes the Stage-1 outcome. No aggregate definition is removed from "
            "either case, unlike this experiment's original (corrected) draft."
        ),
    },
    {
        "case_id": "G5a-related-margin-pair",
        "category": "unratified_boundary_probe",
        "relationship_label": "related",
        "membership_status": "not_applicable",
        "manipulated_variable": None,
        "paired_with": "G5b-related-volume-revenue-pair",
        "claim": "The company's operating income is expected to increase in Q3.",
        "evidence": "Gross margin increased from 40% to 43% in Q2.",
        "expected_stage1_applicability": None,
        "expected_stage2_support": None,
        "oracle_status": "UNRATIFIED",
        "oracle_citation": (
            "Document 47 SS7.3.1, 'Open boundary -- the related-but-distinct metric "
            "tier (MORE EVIDENCE REQUIRED; not resolved by this revision)' -- this "
            "case restates that section's own gross-margin/operating-margin example "
            "in new wording; the boundary is explicitly, textually still open."
        ),
        "oracle_rationale": "Directly instantiates SS7.3.1's own named open boundary.",
    },
    {
        "case_id": "G5b-related-volume-revenue-pair",
        "category": "unratified_boundary_probe",
        "relationship_label": "related",
        "membership_status": "not_applicable",
        "manipulated_variable": "metric pair identity (vs. G5a)",
        "paired_with": "G5a-related-margin-pair",
        "claim": "The company's total revenue is expected to grow in Q3.",
        "evidence": "Units sold increased 12% year-over-year in Q2.",
        "expected_stage1_applicability": None,
        "expected_stage2_support": None,
        "oracle_status": "UNRATIFIED",
        "oracle_citation": "Same open boundary as G5a (SS7.3.1), a different metric pair.",
        "oracle_rationale": (
            "Second, distinct related-metric pair -- one case cannot represent this "
            "category (CTO correction #6 applies to reading either G5a or G5b alone)."
        ),
    },
    {
        "case_id": "G6-correlated-metric-negative-control",
        "category": "ratified_negative_control",
        "relationship_label": "correlated",
        "membership_status": "not_applicable",
        "manipulated_variable": None,
        "paired_with": None,
        "claim": "The company's revenue is expected to grow in Q3.",
        "evidence": "The company's employee satisfaction score improved in Q2.",
        "expected_stage1_applicability": "NOT_APPLICABLE",
        "expected_stage2_support": None,
        "oracle_status": "RATIFIED",
        "oracle_citation": (
            "Document 47 SS7.3.1 metric/disclosure relevance rule: evidence about 'a "
            "genuinely different underlying quantity or business fact' is "
            "NOT_APPLICABLE. Employee satisfaction shares no quantity, no stated "
            "component/aggregate relationship, and no disclosure category with revenue."
        ),
        "oracle_rationale": "No plausible aggregation reading exists for this pair at all.",
    },
    {
        "case_id": "G7-causal-prerequisite",
        "category": "unratified_boundary_probe",
        "relationship_label": "prerequisite",
        "membership_status": "not_applicable",
        "manipulated_variable": None,
        "paired_with": None,
        "claim": "The company's production output is expected to increase in Q3.",
        "evidence": "The company completed its planned capacity expansion in Q2.",
        "expected_stage1_applicability": None,
        "expected_stage2_support": None,
        "oracle_status": "UNRATIFIED",
        "oracle_citation": (
            "Not addressed anywhere in Document 47's ratified or explicitly-open "
            "text. The causal-prerequisite exclusion proposed in this session's own "
            "prior governance addendum (Document 48 SS4) is an unratified proposal, "
            "not frozen policy -- it cannot be cited here as an answer."
        ),
        "oracle_rationale": (
            "Capacity expansion is an enabling condition for production output, not a "
            "stated part or the aggregate of production output itself. Whether "
            "Document 47's property axis excludes causal prerequisites is exactly "
            "what is unresolved."
        ),
    },
    {
        "case_id": "G8-ambiguous-membership",
        "category": "intentional_ambiguity_probe",
        "relationship_label": "ambiguous",
        "membership_status": "unknown",
        "manipulated_variable": None,
        "paired_with": None,
        "claim": "The company's total North American sales are expected to grow in Q3.",
        "evidence": "Sales in the western United States grew 8% in Q2.",
        "expected_stage1_applicability": None,
        "expected_stage2_support": None,
        "oracle_status": "UNRATIFIED_BY_DESIGN",
        "oracle_citation": (
            "N/A -- the source text itself does not establish whether 'western United "
            "States' exhaustively partitions, or merely overlaps with undefined "
            "boundaries within, 'North America' (Canada/Mexico status unstated)."
        ),
        "oracle_rationale": (
            "Deliberately ambiguous population boundary. The diagnostic purpose is to "
            "observe whether the judge's own rationale acknowledges this uncertainty, "
            "not to score its verdict against a correct answer -- no oracle value is "
            "frozen for this case, by design, not merely pending adjudication."
        ),
    },
]

_EXPECTED_CATEGORIES = {
    "ratified_positive_control",
    "ratified_negative_control",
    "unratified_boundary_probe",
    "intentional_ambiguity_probe",
}
assert {c["category"] for c in CASES} <= _EXPECTED_CATEGORIES, "unknown category label in CASES"
assert len({c["case_id"] for c in CASES}) == len(CASES), "duplicate case_id in CASES"


@dataclass(frozen=True)
class RepetitionResult:
    case_id: str
    category: str
    relationship_label: str
    membership_status: str
    trial_number: int
    timestamp: str
    provider_base_url: str | None
    model: str | None
    temperature: float
    stage1_success: bool
    stage1_raw_error: str | None
    stage1_applicability: str | None
    stage1_rationale: str | None
    stage1_supplementary_recovery: dict | None
    stage1_prompt_version: str | None
    stage2_called: bool
    stage2_success: bool | None
    stage2_raw_error: str | None
    stage2_verdict: str | None
    stage2_rationale: str | None
    stage2_supplementary_recovery: dict | None
    stage2_prompt_version: str | None
    final_verdict: str | None
    final_status: str | None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _run_one_trial(case: dict, trial_number: int) -> RepetitionResult:
    claim, evidence = case["claim"], case["evidence"]
    cfg = _active()
    common = dict(
        case_id=case["case_id"], category=case["category"],
        relationship_label=case["relationship_label"], membership_status=case["membership_status"],
        trial_number=trial_number, timestamp=_now(),
        provider_base_url=cfg.get("base_url"), model=cfg.get("light"), temperature=0.0,
    )

    try:
        applicability_result = await judge_module.invoke_applicability_judge(claim, evidence)
    except Exception as e:  # noqa: BLE001 -- Stage 1 failure recorded as-is, never silently discarded.
        return RepetitionResult(
            **common,
            stage1_success=False, stage1_raw_error=str(e), stage1_applicability=None,
            stage1_rationale=None, stage1_supplementary_recovery=_recover_supplementary(str(e)),
            stage1_prompt_version=judge_module.APPLICABILITY_PROMPT_VERSION,
            stage2_called=False, stage2_success=None, stage2_raw_error=None, stage2_verdict=None,
            stage2_rationale=None, stage2_supplementary_recovery=None, stage2_prompt_version=None,
            final_verdict=None, final_status="INCONCLUSIVE",
        )

    if applicability_result.applicability == "NOT_APPLICABLE":
        status, _ = _JUDGE_VERDICT_TO_STATUS["NOT_APPLICABLE"]
        return RepetitionResult(
            **common,
            stage1_success=True, stage1_raw_error=None, stage1_applicability="NOT_APPLICABLE",
            stage1_rationale=applicability_result.rationale, stage1_supplementary_recovery=None,
            stage1_prompt_version=judge_module.APPLICABILITY_PROMPT_VERSION,
            stage2_called=False, stage2_success=None, stage2_raw_error=None, stage2_verdict=None,
            stage2_rationale=None, stage2_supplementary_recovery=None, stage2_prompt_version=None,
            final_verdict="NOT_APPLICABLE", final_status=status,
        )

    try:
        support_result = await judge_module.invoke_support_judge(claim, evidence)
    except Exception as e:  # noqa: BLE001 -- Stage 2 failure recorded as-is, never silently discarded.
        return RepetitionResult(
            **common,
            stage1_success=True, stage1_raw_error=None, stage1_applicability="APPLICABLE",
            stage1_rationale=applicability_result.rationale, stage1_supplementary_recovery=None,
            stage1_prompt_version=judge_module.APPLICABILITY_PROMPT_VERSION,
            stage2_called=True, stage2_success=False, stage2_raw_error=str(e), stage2_verdict=None,
            stage2_rationale=None, stage2_supplementary_recovery=_recover_supplementary(str(e)),
            stage2_prompt_version=judge_module.SUPPORT_PROMPT_VERSION,
            final_verdict=None, final_status="INCONCLUSIVE",
        )

    status, _ = _JUDGE_VERDICT_TO_STATUS[support_result.verdict]
    return RepetitionResult(
        **common,
        stage1_success=True, stage1_raw_error=None, stage1_applicability="APPLICABLE",
        stage1_rationale=applicability_result.rationale, stage1_supplementary_recovery=None,
        stage1_prompt_version=judge_module.APPLICABILITY_PROMPT_VERSION,
        stage2_called=True, stage2_success=True, stage2_raw_error=None,
        stage2_verdict=support_result.verdict, stage2_rationale=support_result.rationale,
        stage2_supplementary_recovery=None,
        stage2_prompt_version=judge_module.SUPPORT_PROMPT_VERSION,
        final_verdict=support_result.verdict, final_status=status,
    )


async def _run_all(repeats: int) -> list[RepetitionResult]:
    results: list[RepetitionResult] = []
    for case in CASES:
        for i in range(repeats):
            results.append(await _run_one_trial(case, i))
    return results


def _ensure_output_does_not_exist(path: Path) -> None:
    """Fail-closed collision guard, identical in spirit and behavior to
    run_m11_phase_h_m04_m05.py's own guard of the same name (CTO instruction:
    reuse the pattern, never overwrite a historical artifact). Refuses to
    proceed -- before any live call -- if `path` already exists. This
    experiment's own output directory/filename are new and can never collide
    with phase_h_rev5_run1.json or phase_h_rev6_run1.json, which live in a
    different results directory entirely; this guard additionally protects
    against colliding with a prior run of THIS script."""
    if path.exists():
        print(
            f"refusing to overwrite existing artifact: {path} -- fail-closed guard "
            "(M11 Phase H-1 generalization experiment). Delete or rename it first if "
            "a genuine rerun of THIS identity is intended, or bump the output "
            "filename above first if this is meant to be a new run.",
            file=sys.stderr,
        )
        raise SystemExit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    _ensure_output_does_not_exist(_OUTPUT_PATH)

    results = asyncio.run(_run_all(args.repeats))

    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "experiment_id": "M11-PhaseH1-Generalization-run1",
        "generated_at": _now(),
        "note": (
            "M11 Phase H-1, CTO-authorized diagnostic/self-consistency generalization "
            "probe for the Document 47 SS7.3.1 component/aggregate granularity rule, "
            "run independently of and subsequent to the M-04/M-05 Rev 5/Rev 6 "
            "experiments. EVIDENCE ONLY -- does not promote the judge, does not "
            "validate or promote the gate, does not authorize production readiness, "
            "does not resolve any unratified boundary this case matrix probes. "
            "Per-category n=1 or n=2 case counts must not be read as statistically "
            "representative of an entire semantic category (see module docstring)."
        ),
        "architecture_version": judge_module.JUDGE_ARCHITECTURE_VERSION,
        "applicability_prompt_version": judge_module.APPLICABILITY_PROMPT_VERSION,
        "support_prompt_version": judge_module.SUPPORT_PROMPT_VERSION,
        "gate_version_at_run_time": judge_gate.JUDGE_SELF_CONSISTENCY_GATE_VERSION,
        "repeats_per_case": args.repeats,
        "cases": CASES,
        "results": [asdict(r) for r in results],
    }
    _OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
