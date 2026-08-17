"""M10 Phase 4 — local JSON result persistence and baseline lookup (Document
45 §12, Document 46 §4-§5's frozen eligibility/compatibility rules).

Stdlib `json`/`pathlib` only. Every function accepts an explicit
`results_dir` (defaulting to the real, git-ignored `backend/evaluation/
results/`) so tests can point at an isolated tmp_path instead of the real
directory — the same isolation discipline evaluation/golden_dataset/
loader.py's own tests already use.
"""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from evaluation.adapters.types import ExecutionMetadata
from evaluation.core.types import BehaviorEvaluation, CaseEvaluationResult, MetricResult
from evaluation.regression.types import EvaluationResult

RESULTS_DIR = Path(__file__).resolve().parents[1] / "results"


def _case_to_dict(case: CaseEvaluationResult) -> dict:
    return asdict(case)  # every field is itself a (nested) dataclass -> asdict recurses cleanly


def _case_from_dict(data: dict) -> CaseEvaluationResult:
    return CaseEvaluationResult(
        case_id=data["case_id"],
        surface=data["surface"],
        dataset_version=data["dataset_version"],
        case_version=data["case_version"],
        mode=data["mode"],
        evaluation_version=data["evaluation_version"],
        execution=ExecutionMetadata(**data["execution"]),
        behavior_evaluations=[BehaviorEvaluation(**b) for b in data["behavior_evaluations"]],
        metrics=[MetricResult(**m) for m in data["metrics"]],
        status=data["status"],
        failure_reasons=list(data["failure_reasons"]),
    )


def result_to_dict(result: EvaluationResult) -> dict:
    return {
        "run_id": result.run_id,
        "timestamp": result.timestamp,
        "code_revision": result.code_revision,
        "schema_version": result.schema_version,
        "verdict": result.verdict,
        "verdict_reason": result.verdict_reason,
        "case": _case_to_dict(result.case),
    }


def result_from_dict(data: dict) -> EvaluationResult:
    return EvaluationResult(
        run_id=data["run_id"],
        timestamp=data["timestamp"],
        code_revision=data["code_revision"],
        schema_version=data.get("schema_version"),
        case=_case_from_dict(data["case"]),
        verdict=data["verdict"],
        verdict_reason=data["verdict_reason"],
    )


def save_result(result: EvaluationResult, *, results_dir: Path = RESULTS_DIR) -> Path:
    """One flat JSON file per (case, run) — Document 45 §12. Filename is not
    part of the frozen contract (only the record's own fields are); chosen
    to be globbable by case_id for baseline lookup below."""
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / f"{result.case.case_id}__{result.run_id}.json"
    path.write_text(json.dumps(result_to_dict(result), indent=2), encoding="utf-8")
    return path


def _all_results_for_case(case_id: str, *, results_dir: Path) -> list[EvaluationResult]:
    if not results_dir.exists():
        return []
    results = []
    for path in results_dir.glob(f"{case_id}__*.json"):
        try:
            results.append(result_from_dict(json.loads(path.read_text(encoding="utf-8"))))
        except (json.JSONDecodeError, KeyError):
            continue  # a malformed/partial result file must not break baseline lookup for every other case
    return results


def find_baseline(
    current: CaseEvaluationResult, *, schema_version: str | None, results_dir: Path = RESULTS_DIR,
) -> tuple[EvaluationResult | None, str]:
    """Document 46 §4/§5: the most recent prior FIXTURE-mode result matching
    the five-field compatibility key (case_id, dataset_version, case_version,
    evaluation_version, schema_version), eligible only if its own `status` is
    PASS or FAIL. If the single most recent compatible result is
    INCONCLUSIVE, it is NOT eligible and older results are never searched
    (Document 46 §4 — an inconclusive run breaks the baseline chain).

    Returns (baseline_or_None, reason) — `reason` explains a None result for
    use as the comparison's verdict_reason.
    """
    candidates = [
        r for r in _all_results_for_case(current.case_id, results_dir=results_dir)
        if r.case.mode == "fixture"
        and r.case.dataset_version == current.dataset_version
        and r.case.case_version == current.case_version
        and r.case.evaluation_version == current.evaluation_version
        and r.schema_version == schema_version
    ]
    if not candidates:
        return None, "no compatible prior FIXTURE-mode result exists"

    candidates.sort(key=lambda r: r.timestamp, reverse=True)
    most_recent = candidates[0]
    if most_recent.case.status == "INCONCLUSIVE":
        return None, (
            f"most recent compatible result (run_id={most_recent.run_id!r}) is INCONCLUSIVE — "
            "not eligible as a baseline; older results are not searched (Document 46 §4)"
        )
    return most_recent, "eligible baseline found"
