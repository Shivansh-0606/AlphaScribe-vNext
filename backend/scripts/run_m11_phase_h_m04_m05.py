"""M11 Phase H Revision 5 — CTO-authorized live execution of the frozen
M-04/M-05 controlled-pair experiment.

FROZEN CASE TEXT (verbatim from the approved Phase H Revision 5 design;
transcribed once here, not re-derived or reworded at execution time):

M-04 (financial):
  claim:    "The company's total revenue -- the combined revenue across its
             three reporting segments, Hardware, Software, and Services --
             is expected to grow in Q3."
  evidence: "The Hardware segment, one of the company's three reporting
             segments, generated $40 million in Q2 revenue."
  human_applicability (frozen oracle): APPLICABLE
  human_expected_support (frozen oracle): UNSUPPORTED

M-05 (operational -- units shipped, the flow-quantity correction from
Revision 5):
  claim:    "The company's total units shipped -- the combined units
             shipped across its three distribution channels, Direct,
             Retail, and Wholesale -- is expected to grow in Q3."
  evidence: "The Direct channel, one of the company's three distribution
             channels, shipped 40,000 units in Q2."
  human_applicability (frozen oracle): APPLICABLE
  human_expected_support (frozen oracle): UNSUPPORTED

EVIDENCE ONLY. Does not authorize gate promotion, judge promotion, or
production readiness. Reuses judge.invoke_applicability_judge /
invoke_support_judge exactly as approved and unmodified in Phase E and
every prior M11 diagnostic script this session -- no new production
runner, no edit to judge.py/schemas.py/behaviors.py/types.py/judge_gate.py.
Mirrors evaluate_model_judged_support's own Stage 1 -> branch -> conditional
Stage 2 control flow externally, read-only, the same pattern used by
run_m11_modality_diagnostic.py, run_m11_phase_e_live_validation.py, and
run_m11_phase_g_h1_h2_diagnostic.py.

Usage:
    python backend/scripts/run_m11_phase_h_m04_m05.py

M11 Phase H governance correction (post-Rev-5, pre-any-Rev-6-execution):
judge.py/types.py/behaviors.py have since been edited elsewhere in this
session (Stage-1 prompt text, and additive APPLICABILITY_PROMPT_VERSION/
SUPPORT_PROMPT_VERSION provenance fields, Document 47 §9.1 step 4) --
this script still makes no edit to any of them, but the "unmodified" claim
above describes their state as of Rev 5's own execution, not their current
state. This script's own RepetitionResult/payload now additionally record
stage1_prompt_version/stage2_prompt_version (per-trial) and
applicability_prompt_version/support_prompt_version (top-level), read from
judge_module at call time, so a future run reflects whatever those
constants are at that time -- this file's own control flow and case data
are otherwise untouched. THIS SCRIPT HAS NOT BEEN RE-RUN: the historical
phase_h_rev5_run1.json artifact predates this code change and is
unmodified; it has no such fields at all, which is itself the intended
disambiguator against any future artifact this script produces.

M11 Phase H Rev 6 preflight fix (this change): this file's title above still
correctly names the Revision 5 design this script's FROZEN_CASES/methodology
were authored under (that provenance is unchanged and not rewritten here) --
but its own run identity (experiment_id, output filename) previously still
said "Rev5", which would have collided with and silently overwritten Rev 5's
own historical artifact had this script been re-run. experiment_id is now
"M11-PhaseH-Rev6-M04-M05-run1", output is now phase_h_rev6_run1.json (same
results directory, established per-run-not-per-experiment file-naming
precedent -- compare phase_g_h1_h2_diagnostic/results/phase_g_run1.json), and
main() now refuses to run at all (fail-closed, before any live call) if that
destination already exists. Still not run: no live call was made to produce
this note.
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

_RESULTS_DIR = _BACKEND_ROOT / "evaluation" / "self_consistency" / "phase_h_m04_m05_controlled_pair" / "results"
_OUTPUT_PATH = _RESULTS_DIR / "phase_h_rev6_run1.json"

_VERDICT_RECOVERY_RE = re.compile(r'"(applicability|verdict)"\s*:\s*"([A-Z_]+)"')


def _recover_supplementary(error_message: str) -> dict | None:
    m = _VERDICT_RECOVERY_RE.search(error_message)
    return {"field": m.group(1), "value": m.group(2)} if m else None


# Frozen per Phase H Revision 5 -- not modified, paraphrased, or reworded here.
FROZEN_CASES = [
    {
        "case_id": "M-04",
        "domain": "financial",
        "claim": (
            "The company's total revenue — the combined revenue across its three "
            "reporting segments, Hardware, Software, and Services — is expected to "
            "grow in Q3."
        ),
        "evidence": (
            "The Hardware segment, one of the company's three reporting segments, "
            "generated $40 million in Q2 revenue."
        ),
        "human_applicability": "APPLICABLE",
        "human_expected_support": "UNSUPPORTED",
    },
    {
        "case_id": "M-05",
        "domain": "operational (logistics / units shipped)",
        "claim": (
            "The company's total units shipped — the combined units shipped across "
            "its three distribution channels, Direct, Retail, and Wholesale — is "
            "expected to grow in Q3."
        ),
        "evidence": (
            "The Direct channel, one of the company's three distribution channels, "
            "shipped 40,000 units in Q2."
        ),
        "human_applicability": "APPLICABLE",
        "human_expected_support": "UNSUPPORTED",
    },
]


@dataclass(frozen=True)
class RepetitionResult:
    case_id: str
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

    try:
        applicability_result = await judge_module.invoke_applicability_judge(claim, evidence)
    except Exception as e:  # noqa: BLE001 -- Stage 1 failure recorded as-is, never silently discarded.
        return RepetitionResult(
            case_id=case["case_id"], trial_number=trial_number, timestamp=_now(),
            provider_base_url=cfg.get("base_url"), model=cfg.get("light"), temperature=0.0,
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
            case_id=case["case_id"], trial_number=trial_number, timestamp=_now(),
            provider_base_url=cfg.get("base_url"), model=cfg.get("light"), temperature=0.0,
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
            case_id=case["case_id"], trial_number=trial_number, timestamp=_now(),
            provider_base_url=cfg.get("base_url"), model=cfg.get("light"), temperature=0.0,
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
        case_id=case["case_id"], trial_number=trial_number, timestamp=_now(),
        provider_base_url=cfg.get("base_url"), model=cfg.get("light"), temperature=0.0,
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
    for case in FROZEN_CASES:
        for i in range(repeats):
            results.append(await _run_one_trial(case, i))
    return results


def _ensure_output_does_not_exist(path: Path) -> None:
    """Fail-closed collision guard (M11 Phase H Rev 6 preflight fix): refuses
    to proceed -- before any live call is made -- if `path` already exists,
    rather than silently overwriting a prior run's artifact. Standalone so it
    can be exercised directly by a test/import-time check without invoking
    main()'s argparse/asyncio.run machinery. Rev 5's own artifact was never
    protected by this guard (it predates this fix); this only protects
    whatever _OUTPUT_PATH currently points at."""
    if path.exists():
        print(
            f"refusing to overwrite existing artifact: {path} -- fail-closed guard "
            "(M11 Phase H Rev 6 preflight fix). Delete or rename it first if a "
            "genuine rerun of THIS identity is intended, or bump the experiment_id/"
            "output filename above first if this is meant to be a new experiment.",
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
        "experiment_id": "M11-PhaseH-Rev6-M04-M05-run1",
        "generated_at": _now(),
        "note": (
            "M11 Phase H Revision 6, CTO-authorized live execution of the frozen M-04/M-05 "
            "controlled pair, post prompt-provenance governance correction (Document 47 "
            "§9.1 step 4 -- APPLICABILITY_PROMPT_VERSION/SUPPORT_PROMPT_VERSION now "
            "distinguish this run's Stage-1/Stage-2 prompt identity from Rev 5's). "
            "EVIDENCE ONLY -- does not promote the judge, does not validate "
            "or promote the gate, does not authorize production readiness."
        ),
        "architecture_version": judge_module.JUDGE_ARCHITECTURE_VERSION,
        "applicability_prompt_version": judge_module.APPLICABILITY_PROMPT_VERSION,
        "support_prompt_version": judge_module.SUPPORT_PROMPT_VERSION,
        "gate_version_at_run_time": judge_gate.JUDGE_SELF_CONSISTENCY_GATE_VERSION,
        "repeats_per_case": args.repeats,
        "cases": FROZEN_CASES,
        "results": [asdict(r) for r in results],
    }
    _OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
