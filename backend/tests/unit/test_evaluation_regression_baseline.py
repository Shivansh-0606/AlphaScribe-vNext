"""Unit check for evaluation/regression/result_store.py's baseline eligibility
and compatibility rules (M10 Phase 4, Document 46 §4/§5). All tests use an
isolated tmp_path — never the real backend/evaluation/results/.

    python -m pytest backend/tests/unit/test_evaluation_regression_baseline.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.adapters.types import ExecutionMetadata
from evaluation.core.types import CaseEvaluationResult, MetricResult
from evaluation.regression.result_store import find_baseline, save_result
from evaluation.regression.types import EvaluationResult


def _case_result(**overrides) -> CaseEvaluationResult:
    payload = dict(
        case_id="c1", surface="comparison_explanation", dataset_version=1, case_version=1,
        mode="fixture", evaluation_version="v1",
        execution=ExecutionMetadata(provider="gemini", model="gemini-flash"),
        behavior_evaluations=[], metrics=[MetricResult("citation_expectation", 1, "PASS", "ok")],
        status="PASS", failure_reasons=[],
    )
    payload.update(overrides)
    return CaseEvaluationResult(**payload)


def _eval_result(case_result: CaseEvaluationResult, **overrides) -> EvaluationResult:
    payload = dict(
        run_id="run-1", timestamp="2026-01-01T00:00:00+00:00", code_revision="abc123",
        schema_version="s1", case=case_result, verdict="PASS", verdict_reason="ok",
    )
    payload.update(overrides)
    return EvaluationResult(**payload)


def test_valid_pass_baseline_is_eligible(tmp_path):
    save_result(_eval_result(_case_result(status="PASS")), results_dir=tmp_path)
    baseline, reason = find_baseline(_case_result(), schema_version="s1", results_dir=tmp_path)
    assert baseline is not None
    assert baseline.case.status == "PASS"


def test_valid_fail_baseline_is_eligible(tmp_path):
    save_result(_eval_result(_case_result(status="FAIL")), results_dir=tmp_path)
    baseline, reason = find_baseline(_case_result(), schema_version="s1", results_dir=tmp_path)
    assert baseline is not None
    assert baseline.case.status == "FAIL"


def test_inconclusive_result_not_eligible_and_no_backward_search(tmp_path):
    # An older PASS exists, but the MOST RECENT compatible result is
    # INCONCLUSIVE — Document 46 §4: not eligible, do not search past it.
    save_result(_eval_result(_case_result(status="PASS"), run_id="run-old",
                              timestamp="2026-01-01T00:00:00+00:00"), results_dir=tmp_path)
    save_result(_eval_result(_case_result(status="INCONCLUSIVE"), run_id="run-new",
                              timestamp="2026-01-02T00:00:00+00:00"), results_dir=tmp_path)
    baseline, reason = find_baseline(_case_result(), schema_version="s1", results_dir=tmp_path)
    assert baseline is None
    assert "INCONCLUSIVE" in reason
    assert "run-new" in reason  # names the blocking result, not the older pass


def test_live_mode_result_never_eligible(tmp_path):
    save_result(_eval_result(_case_result(mode="live", status="PASS")), results_dir=tmp_path)
    baseline, reason = find_baseline(_case_result(mode="fixture"), schema_version="s1", results_dir=tmp_path)
    assert baseline is None


def test_no_prior_result_is_no_baseline(tmp_path):
    baseline, reason = find_baseline(_case_result(), schema_version="s1", results_dir=tmp_path)
    assert baseline is None
    assert "no compatible" in reason


def test_incompatible_case_id_excluded(tmp_path):
    save_result(_eval_result(_case_result(case_id="other", status="PASS")), results_dir=tmp_path)
    baseline, reason = find_baseline(_case_result(case_id="c1"), schema_version="s1", results_dir=tmp_path)
    assert baseline is None


def test_incompatible_dataset_version_excluded(tmp_path):
    save_result(_eval_result(_case_result(dataset_version=1, status="PASS")), results_dir=tmp_path)
    baseline, reason = find_baseline(_case_result(dataset_version=2), schema_version="s1", results_dir=tmp_path)
    assert baseline is None


def test_incompatible_case_version_excluded(tmp_path):
    save_result(_eval_result(_case_result(case_version=1, status="PASS")), results_dir=tmp_path)
    baseline, reason = find_baseline(_case_result(case_version=2), schema_version="s1", results_dir=tmp_path)
    assert baseline is None


def test_incompatible_evaluation_version_excluded(tmp_path):
    save_result(_eval_result(_case_result(evaluation_version="v1", status="PASS")), results_dir=tmp_path)
    baseline, reason = find_baseline(_case_result(evaluation_version="v2"), schema_version="s1", results_dir=tmp_path)
    assert baseline is None


def test_incompatible_schema_version_excluded(tmp_path):
    save_result(_eval_result(_case_result(status="PASS"), schema_version="s1"), results_dir=tmp_path)
    baseline, reason = find_baseline(_case_result(), schema_version="s2", results_dir=tmp_path)
    assert baseline is None


def test_none_schema_version_matches_none(tmp_path):
    # Research/Learning today (Document 46 §7) — schema_version is null for
    # both baseline and current; null must still compare equal to null.
    save_result(_eval_result(_case_result(surface="research", status="PASS"), schema_version=None),
                results_dir=tmp_path)
    baseline, reason = find_baseline(_case_result(surface="research"), schema_version=None, results_dir=tmp_path)
    assert baseline is not None


def test_provider_model_code_revision_not_part_of_compatibility_key(tmp_path):
    # Document 46 §5: explicitly excluded from the identity key.
    save_result(_eval_result(
        _case_result(status="PASS", execution=ExecutionMetadata(provider="openai", model="gpt-x")),
        code_revision="deadbeef-dirty",
    ), results_dir=tmp_path)
    current = _case_result(execution=ExecutionMetadata(provider="gemini", model="gemini-flash"))
    baseline, reason = find_baseline(current, schema_version="s1", results_dir=tmp_path)
    assert baseline is not None  # still eligible despite different provider/model/code_revision


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
