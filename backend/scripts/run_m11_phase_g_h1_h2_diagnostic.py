"""M11 Phase G — CTO-authorized H1/H2 cross-domain diagnostic.

DIAGNOSTIC ONLY. Not part of any permanent corpus: the 4 cases below are
defined as inline literals, isolated from evaluation/self_consistency/cases/
and evaluation/self_consistency/v2_regression/cases/ (the permanent held-out
sets) and from evaluation/golden_dataset/ entirely. Pair A reuses Case 06's
actual claim/evidence text read-only for reference; Case 06's own fixture
file is never opened or written by this script.

Reuses judge.invoke_applicability_judge / invoke_support_judge exactly as
Phase E's own live validation did -- unmodified, no new production runner.
Mirrors evaluate_model_judged_support's own Stage 1 -> branch -> conditional
Stage 2 control flow externally, the same way every prior M11 diagnostic
script in this session has (run_m11_modality_diagnostic.py,
run_m11_phase_e_live_validation.py) -- read-only imports throughout.

Usage:
    python backend/scripts/run_m11_phase_g_h1_h2_diagnostic.py
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

_RESULTS_DIR = _BACKEND_ROOT / "evaluation" / "self_consistency" / "phase_g_h1_h2_diagnostic" / "results"
_OUTPUT_PATH = _RESULTS_DIR / "phase_g_run1.json"

_VERDICT_RECOVERY_RE = re.compile(r'"(applicability|verdict)"\s*:\s*"([A-Z_]+)"')


def _recover_supplementary(error_message: str) -> dict | None:
    m = _VERDICT_RECOVERY_RE.search(error_message)
    return {"field": m.group(1), "value": m.group(2)} if m else None


# Pair A reuses Case 06's actual claim/evidence text verbatim (read from the
# permanent fixture at design time, not at run time -- the fixture file
# itself is never opened by this script). Confirmed byte-identical against
# backend/evaluation/self_consistency/v2_regression/cases/
# v2_regression_06_disclosure_uncertainty.json immediately before this run.
DIAGNOSTIC_CASES = [
    {
        "case_id": "pair_a_financial_anchor_case06",
        "domain": "financial (Case 06, unchanged)",
        "claim": "The company expects revenue growth next quarter.",
        "evidence": "The company has not determined whether it will provide revenue guidance for next quarter.",
        "expected_applicability": "APPLICABLE",
        "expected_final_verdict": "UNSUPPORTED",
        "ambiguity_note": "Phase F finding: genuinely contested; not treated as ground truth here.",
    },
    {
        "case_id": "pair_b_project_launch_meta_relevance",
        "domain": "project management (non-financial)",
        "claim": "The organization expects the project to launch in June.",
        "evidence": "The organization has not decided whether it will announce a launch date for the project.",
        "expected_applicability": "APPLICABLE",
        "expected_final_verdict": "UNSUPPORTED",
        "ambiguity_note": (
            "Clearer than Case 06 (launch-date announcements are typically committed to only once "
            "readiness is reasonably assured -- a tighter practical coupling than standing IR guidance "
            "policy), but not fully unambiguous -- see human adjudication."
        ),
    },
    {
        "case_id": "pair_c_project_launch_meta_irrelevance_control",
        "domain": "project management (non-financial)",
        "claim": "The organization expects the project to launch in June.",
        "evidence": "The organization has not decided whether it will publish its employee attendance policy.",
        "expected_applicability": "NOT_APPLICABLE",
        "expected_final_verdict": "NOT_APPLICABLE",
        "ambiguity_note": "Low ambiguity -- attendance-policy disclosure has no plausible bearing on launch timing.",
    },
    {
        "case_id": "pair_d_project_launch_object_level_control",
        "domain": "project management (non-financial)",
        "claim": "The organization expects the project to launch in June.",
        "evidence": "The organization completed the final launch-readiness review.",
        "expected_applicability": "APPLICABLE",
        "expected_final_verdict": "UNSUPPORTED",
        "ambiguity_note": "Low ambiguity -- direct object-level readiness fact, no meta-level indirection.",
    },
]


@dataclass(frozen=True)
class RepetitionResult:
    case_id: str
    repetition_index: int
    timestamp: str
    stage1_success: bool
    stage1_applicability: str | None
    stage1_rationale: str | None
    stage1_error: str | None
    stage1_supplementary_recovery: dict | None
    stage2_called: bool
    stage2_success: bool | None
    stage2_verdict: str | None
    stage2_rationale: str | None
    stage2_error: str | None
    stage2_supplementary_recovery: dict | None
    final_verdict: str | None
    final_status: str | None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _run_one_repetition(case: dict, repetition_index: int) -> RepetitionResult:
    claim, evidence = case["claim"], case["evidence"]
    try:
        applicability_result = await judge_module.invoke_applicability_judge(claim, evidence)
    except Exception as e:  # noqa: BLE001
        return RepetitionResult(
            case_id=case["case_id"], repetition_index=repetition_index, timestamp=_now(),
            stage1_success=False, stage1_applicability=None, stage1_rationale=None,
            stage1_error=str(e), stage1_supplementary_recovery=_recover_supplementary(str(e)),
            stage2_called=False, stage2_success=None, stage2_verdict=None,
            stage2_rationale=None, stage2_error=None, stage2_supplementary_recovery=None,
            final_verdict=None, final_status="INCONCLUSIVE",
        )

    if applicability_result.applicability == "NOT_APPLICABLE":
        status, _ = _JUDGE_VERDICT_TO_STATUS["NOT_APPLICABLE"]
        return RepetitionResult(
            case_id=case["case_id"], repetition_index=repetition_index, timestamp=_now(),
            stage1_success=True, stage1_applicability="NOT_APPLICABLE",
            stage1_rationale=applicability_result.rationale, stage1_error=None,
            stage1_supplementary_recovery=None,
            stage2_called=False, stage2_success=None, stage2_verdict=None,
            stage2_rationale=None, stage2_error=None, stage2_supplementary_recovery=None,
            final_verdict="NOT_APPLICABLE", final_status=status,
        )

    try:
        support_result = await judge_module.invoke_support_judge(claim, evidence)
    except Exception as e:  # noqa: BLE001
        return RepetitionResult(
            case_id=case["case_id"], repetition_index=repetition_index, timestamp=_now(),
            stage1_success=True, stage1_applicability="APPLICABLE",
            stage1_rationale=applicability_result.rationale, stage1_error=None,
            stage1_supplementary_recovery=None,
            stage2_called=True, stage2_success=False, stage2_verdict=None,
            stage2_rationale=None, stage2_error=str(e),
            stage2_supplementary_recovery=_recover_supplementary(str(e)),
            final_verdict=None, final_status="INCONCLUSIVE",
        )

    status, _ = _JUDGE_VERDICT_TO_STATUS[support_result.verdict]
    return RepetitionResult(
        case_id=case["case_id"], repetition_index=repetition_index, timestamp=_now(),
        stage1_success=True, stage1_applicability="APPLICABLE",
        stage1_rationale=applicability_result.rationale, stage1_error=None,
        stage1_supplementary_recovery=None,
        stage2_called=True, stage2_success=True, stage2_verdict=support_result.verdict,
        stage2_rationale=support_result.rationale, stage2_error=None, stage2_supplementary_recovery=None,
        final_verdict=support_result.verdict, final_status=status,
    )


async def _run_all(repeats: int) -> list[RepetitionResult]:
    results: list[RepetitionResult] = []
    for case in DIAGNOSTIC_CASES:
        for i in range(repeats):
            results.append(await _run_one_repetition(case, i))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    results = asyncio.run(_run_all(args.repeats))

    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": _now(),
        "note": (
            "M11 Phase G CTO-authorized H1/H2 cross-domain diagnostic. DIAGNOSTIC ONLY -- these 4 cases "
            "are isolated, not part of any permanent corpus, and do not authorize gate promotion."
        ),
        "architecture_version": judge_module.JUDGE_ARCHITECTURE_VERSION,
        "gate_version_at_run_time": judge_gate.JUDGE_SELF_CONSISTENCY_GATE_VERSION,
        "provider_base_url": _active().get("base_url"),
        "model": _active().get("light"),
        "temperature": 0.0,
        "repeats_per_case": args.repeats,
        "cases": DIAGNOSTIC_CASES,
        "results": [asdict(r) for r in results],
    }
    _OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
