"""Unit check for evaluation/regression/compare.py — Document 46 §6's
complete, frozen regression truth table, every row. All tests use an
isolated tmp_path.

    python -m pytest backend/tests/unit/test_evaluation_regression_compare.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.adapters.types import ExecutionMetadata
from evaluation.core.types import CaseEvaluationResult, MetricResult
from evaluation.regression.compare import compare
from evaluation.regression.result_store import save_result
from evaluation.regression.types import EvaluationResult


def _case_result(**overrides) -> CaseEvaluationResult:
    payload = dict(
        case_id="c1", surface="comparison_explanation", dataset_version=1, case_version=1,
        mode="fixture", evaluation_version="v1",
        execution=ExecutionMetadata(provider="gemini", model="gemini-flash"),
        behavior_evaluations=[],
        metrics=[
            MetricResult("citation_coverage", 1.0, "PASS", "ok"),
            MetricResult("expected_characteristic_coverage", 1.0, "PASS", "ok"),
        ],
        status="PASS", failure_reasons=[],
    )
    payload.update(overrides)
    return CaseEvaluationResult(**payload)


def _eval_result(case_result: CaseEvaluationResult, **overrides) -> EvaluationResult:
    payload = dict(
        run_id="run-baseline", timestamp="2026-01-01T00:00:00+00:00", code_revision="abc123",
        schema_version="s1", case=case_result, verdict="PASS", verdict_reason="ok",
    )
    payload.update(overrides)
    return EvaluationResult(**payload)


def _seed_baseline(tmp_path, status: str, **case_overrides):
    save_result(_eval_result(_case_result(status=status, **case_overrides)), results_dir=tmp_path)


# --- LIVE-mode current is never a comparison target (Reviewer regression) --
# Document 45 §11.1: "FIXTURE MODE is the only mode eligible as a regression
# baseline OR comparison target." The baseline side was already correctly
# filtered by find_baseline(); these prove the symmetric, previously-missing
# check on the *current* side.

def test_live_current_against_fixture_pass_baseline_yields_inconclusive_not_regression(tmp_path):
    _seed_baseline(tmp_path, "PASS")
    current = _case_result(mode="live", status="FAIL")
    verdict, reason = compare(current, schema_version="s1", results_dir=tmp_path)
    assert verdict == "INCONCLUSIVE"
    assert "LIVE-mode" in reason


def test_live_current_against_fixture_fail_baseline_yields_inconclusive_not_pass(tmp_path):
    _seed_baseline(tmp_path, "FAIL")
    current = _case_result(mode="live", status="PASS")
    verdict, reason = compare(current, schema_version="s1", results_dir=tmp_path)
    assert verdict == "INCONCLUSIVE"
    assert "LIVE-mode" in reason


def test_live_current_never_calls_find_baseline(tmp_path, monkeypatch):
    # Proves the short-circuit happens BEFORE any baseline lookup, not just
    # that the final verdict happens to come out right.
    import evaluation.regression.compare as compare_module

    def _fail_if_called(*args, **kwargs):
        raise AssertionError("find_baseline() must not be called for a LIVE-mode current result")

    monkeypatch.setattr(compare_module, "find_baseline", _fail_if_called)

    _seed_baseline(tmp_path, "PASS")  # an eligible baseline exists and must still be ignored
    verdict, reason = compare(_case_result(mode="live", status="FAIL"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "INCONCLUSIVE"


def test_fixture_current_still_calls_find_baseline(tmp_path, monkeypatch):
    # Sanity check on the spy itself — the guard must not over-trigger and
    # block the legitimate FIXTURE path.
    import evaluation.regression.compare as compare_module

    calls = []
    original = compare_module.find_baseline

    def _spy(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(compare_module, "find_baseline", _spy)

    _seed_baseline(tmp_path, "PASS")
    verdict, reason = compare(_case_result(mode="fixture", status="PASS"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "PASS"
    assert len(calls) == 1


# --- No eligible baseline -----------------------------------------------

def test_no_baseline_current_pass_yields_inconclusive(tmp_path):
    verdict, reason = compare(_case_result(status="PASS"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "INCONCLUSIVE"


def test_no_baseline_current_fail_yields_inconclusive(tmp_path):
    verdict, reason = compare(_case_result(status="FAIL"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "INCONCLUSIVE"


def test_no_baseline_current_inconclusive_yields_inconclusive(tmp_path):
    verdict, reason = compare(_case_result(status="INCONCLUSIVE"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "INCONCLUSIVE"


# --- Eligible PASS baseline -----------------------------------------------

def test_pass_to_pass_no_drop_yields_pass(tmp_path):
    _seed_baseline(tmp_path, "PASS")
    verdict, reason = compare(_case_result(status="PASS"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "PASS"


def test_pass_to_fail_yields_regression(tmp_path):
    _seed_baseline(tmp_path, "PASS")
    verdict, reason = compare(_case_result(status="FAIL"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "REGRESSION"
    assert "baseline PASS" in reason


def test_pass_to_pass_soft_metric_drop_yields_warning(tmp_path):
    _seed_baseline(tmp_path, "PASS", metrics=[
        MetricResult("citation_coverage", 1.0, "PASS", "ok"),
        MetricResult("expected_characteristic_coverage", 1.0, "PASS", "ok"),
    ])
    current = _case_result(status="PASS", metrics=[
        MetricResult("citation_coverage", 0.5, "PASS", "dropped"),
        MetricResult("expected_characteristic_coverage", 1.0, "PASS", "ok"),
    ])
    verdict, reason = compare(current, schema_version="s1", results_dir=tmp_path)
    assert verdict == "WARNING"
    assert "citation_coverage" in reason


def test_pass_to_pass_soft_metric_improves_stays_pass(tmp_path):
    _seed_baseline(tmp_path, "PASS", metrics=[MetricResult("citation_coverage", 0.5, "PASS", "ok")])
    current = _case_result(status="PASS", metrics=[MetricResult("citation_coverage", 1.0, "PASS", "improved")])
    verdict, reason = compare(current, schema_version="s1", results_dir=tmp_path)
    assert verdict == "PASS"


def test_pass_to_pass_none_metric_values_do_not_trigger_warning(tmp_path):
    # citation_coverage INCONCLUSIVE (None value) on both sides — nothing
    # comparable, must not be misread as a "drop".
    _seed_baseline(tmp_path, "PASS", metrics=[MetricResult("citation_coverage", None, "INCONCLUSIVE", "no evidence")])
    current = _case_result(status="PASS", metrics=[MetricResult("citation_coverage", None, "INCONCLUSIVE", "no evidence")])
    verdict, reason = compare(current, schema_version="s1", results_dir=tmp_path)
    assert verdict == "PASS"


# --- Eligible FAIL baseline -----------------------------------------------

def test_fail_to_pass_yields_pass_not_improvement(tmp_path):
    _seed_baseline(tmp_path, "FAIL")
    verdict, reason = compare(_case_result(status="PASS"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "PASS"
    assert "IMPROVEMENT" in reason  # explicitly notes it's not that state


def test_fail_to_fail_yields_unchanged_failure(tmp_path):
    _seed_baseline(tmp_path, "FAIL")
    verdict, reason = compare(_case_result(status="FAIL"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "UNCHANGED_FAILURE"


# --- current INCONCLUSIVE, any eligible baseline --------------------------

def test_pass_baseline_current_inconclusive_yields_inconclusive(tmp_path):
    _seed_baseline(tmp_path, "PASS")
    verdict, reason = compare(_case_result(status="INCONCLUSIVE"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "INCONCLUSIVE"


def test_fail_baseline_current_inconclusive_yields_inconclusive(tmp_path):
    _seed_baseline(tmp_path, "FAIL")
    verdict, reason = compare(_case_result(status="INCONCLUSIVE"), schema_version="s1", results_dir=tmp_path)
    assert verdict == "INCONCLUSIVE"


# --- Multiple cases / metrics / determinism --------------------------------

def test_multiple_cases_are_independent(tmp_path):
    save_result(_eval_result(_case_result(case_id="c1", status="PASS")), results_dir=tmp_path)
    save_result(_eval_result(_case_result(case_id="c2", status="FAIL")), results_dir=tmp_path)
    v1, _ = compare(_case_result(case_id="c1", status="FAIL"), schema_version="s1", results_dir=tmp_path)
    v2, _ = compare(_case_result(case_id="c2", status="FAIL"), schema_version="s1", results_dir=tmp_path)
    assert v1 == "REGRESSION"     # c1: baseline PASS -> current FAIL
    assert v2 == "UNCHANGED_FAILURE"  # c2: baseline FAIL -> current FAIL


def test_deterministic_repeated_comparison(tmp_path):
    _seed_baseline(tmp_path, "PASS")
    current = _case_result(status="PASS")
    r1 = compare(current, schema_version="s1", results_dir=tmp_path)
    r2 = compare(current, schema_version="s1", results_dir=tmp_path)
    assert r1 == r2


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
