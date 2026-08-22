"""M11 Phase E — CTO-authorized controlled live validation of the
structured-applicability architecture (Document 47 Phase D's Option B),
against the same 9 held-out cases and methodology used for v3-na1..v3-na4.

EVIDENCE ONLY. Does not touch JUDGE_SELF_CONSISTENCY_GATE_VERSION, does not
modify `evaluation/self_consistency/runner.py` (its Measurement/aggregate are
built for one fused call; this script's own two-stage control flow mirrors
`evaluate_model_judged_support`'s, calling `judge.invoke_applicability_judge`/
`invoke_support_judge` directly — the same "bypass the runner, call the judge
module directly" approach `runner.py` itself already uses for the single-call
path), does not modify `evaluation/core/behaviors.py`, `judge.py`,
`schemas.py`, `types.py`, or any held-out case file. Everything imported here
is read-only.

Usage:
    python backend/scripts/run_m11_phase_e_live_validation.py
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
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
from evaluation.self_consistency import runner as runner_module  # noqa: E402 (read-only import, mtime-checked)
from evaluation.self_consistency.cases import HeldOutCase, load_held_out_set  # noqa: E402

_CASES_DIR = _BACKEND_ROOT / "evaluation" / "self_consistency" / "v2_regression" / "cases"
_RESULTS_DIR = _BACKEND_ROOT / "evaluation" / "self_consistency" / "v2_regression" / "results"
_OUTPUT_PATH = _RESULTS_DIR / "structured_applicability_v1_run1.json"

_VERDICT_RECOVERY_RE = re.compile(r'"(applicability|verdict)"\s*:\s*"([A-Z_]+)"')


def _recover_supplementary(error_message: str) -> dict | None:
    """Best-effort, diagnostics-only extraction from raw text that failed
    strict schema validation — never fed into official Stage-1/Stage-2
    counts or the final verdict distribution (this task's own Structured-
    Output Track section)."""
    m = _VERDICT_RECOVERY_RE.search(error_message)
    return {"field": m.group(1), "value": m.group(2)} if m else None


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
    final_verdict: str | None  # the disclosed judge_detail.verdict-equivalent, or None if no stage reached a verdict
    final_status: str | None   # BehaviorEvaluation.status-equivalent, via the real _JUDGE_VERDICT_TO_STATUS table
    judge_model: str | None
    architecture_version: str


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _run_one_repetition(case: HeldOutCase, repetition_index: int) -> RepetitionResult:
    """Mirrors evaluate_model_judged_support's own control flow exactly
    (Stage 1 -> branch -> conditional Stage 2), against the held-out case's
    already-fixed (claim, evidence) pair — the same selector-bypass
    `run_case_repeats` already applies for the single-call path."""
    judge_model = _active().get("light")

    try:
        applicability_result = await judge_module.invoke_applicability_judge(case.claim, case.evidence)
    except Exception as e:  # noqa: BLE001 — Stage 1 failure: INCONCLUSIVE-equivalent, Stage 2 never called.
        return RepetitionResult(
            case_id=case.case_id, repetition_index=repetition_index, timestamp=_now(),
            stage1_success=False, stage1_applicability=None, stage1_rationale=None,
            stage1_error=str(e), stage1_supplementary_recovery=_recover_supplementary(str(e)),
            stage2_called=False, stage2_success=None, stage2_verdict=None,
            stage2_rationale=None, stage2_error=None, stage2_supplementary_recovery=None,
            final_verdict=None, final_status="INCONCLUSIVE",
            judge_model=None, architecture_version=judge_module.JUDGE_ARCHITECTURE_VERSION,
        )

    if applicability_result.applicability == "NOT_APPLICABLE":
        status, _ = _JUDGE_VERDICT_TO_STATUS["NOT_APPLICABLE"]
        return RepetitionResult(
            case_id=case.case_id, repetition_index=repetition_index, timestamp=_now(),
            stage1_success=True, stage1_applicability="NOT_APPLICABLE",
            stage1_rationale=applicability_result.rationale, stage1_error=None,
            stage1_supplementary_recovery=None,
            stage2_called=False, stage2_success=None, stage2_verdict=None,
            stage2_rationale=None, stage2_error=None, stage2_supplementary_recovery=None,
            final_verdict="NOT_APPLICABLE", final_status=status,
            judge_model=judge_model, architecture_version=judge_module.JUDGE_ARCHITECTURE_VERSION,
        )

    # applicability_result.applicability == "APPLICABLE" -- Stage 2 runs.
    try:
        support_result = await judge_module.invoke_support_judge(case.claim, case.evidence)
    except Exception as e:  # noqa: BLE001 — Stage 2 failure: INCONCLUSIVE-equivalent, no fabricated verdict.
        return RepetitionResult(
            case_id=case.case_id, repetition_index=repetition_index, timestamp=_now(),
            stage1_success=True, stage1_applicability="APPLICABLE",
            stage1_rationale=applicability_result.rationale, stage1_error=None,
            stage1_supplementary_recovery=None,
            stage2_called=True, stage2_success=False, stage2_verdict=None,
            stage2_rationale=None, stage2_error=str(e),
            stage2_supplementary_recovery=_recover_supplementary(str(e)),
            final_verdict=None, final_status="INCONCLUSIVE",
            judge_model=None, architecture_version=judge_module.JUDGE_ARCHITECTURE_VERSION,
        )

    status, _ = _JUDGE_VERDICT_TO_STATUS[support_result.verdict]
    return RepetitionResult(
        case_id=case.case_id, repetition_index=repetition_index, timestamp=_now(),
        stage1_success=True, stage1_applicability="APPLICABLE",
        stage1_rationale=applicability_result.rationale, stage1_error=None,
        stage1_supplementary_recovery=None,
        stage2_called=True, stage2_success=True, stage2_verdict=support_result.verdict,
        stage2_rationale=support_result.rationale, stage2_error=None, stage2_supplementary_recovery=None,
        final_verdict=support_result.verdict, final_status=status,
        judge_model=judge_model, architecture_version=judge_module.JUDGE_ARCHITECTURE_VERSION,
    )


async def _run_all(cases: list[HeldOutCase], repeats: int) -> list[RepetitionResult]:
    results: list[RepetitionResult] = []
    for case in cases:
        for i in range(repeats):
            results.append(await _run_one_repetition(case, i))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()

    cases = load_held_out_set(_CASES_DIR)
    if len(cases) != 9:
        print(f"expected 9 held-out cases, found {len(cases)}", file=sys.stderr)
        raise SystemExit(2)

    results = asyncio.run(_run_all(cases, args.repeats))

    _RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": _now(),
        "note": (
            "M11 Phase E CTO-authorized controlled live validation of the structured-applicability "
            "architecture. EVIDENCE ONLY -- does not authorize gate promotion. "
            "JUDGE_SELF_CONSISTENCY_GATE_VERSION is not read or written by this script."
        ),
        "architecture_version": judge_module.JUDGE_ARCHITECTURE_VERSION,
        "legacy_prompt_version": judge_module.JUDGE_PROMPT_VERSION,
        "gate_version_at_run_time": judge_gate.JUDGE_SELF_CONSISTENCY_GATE_VERSION,
        "provider_base_url": _active().get("base_url"),
        "model": _active().get("light"),
        "temperature": 0.0,
        "repeats_per_case": args.repeats,
        "held_out_case_count": len(cases),
        "results": [asdict(r) for r in results],
    }
    _OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
