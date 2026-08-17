"""Unit check for evaluation/core/case_evaluator.py (M10 Phase 3).

Pure, dependency-free — no DB, no network, no LLM. Repeated-call determinism
is asserted directly (this task's §13): same inputs -> byte-identical result.

    python backend/tests/unit/test_evaluation_core_case_evaluator.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.adapters.types import AdapterResult, Citation, ExecutionMetadata, NormalizedOutput
from evaluation.core.case_evaluator import EVALUATION_VERSION, evaluate_case
from evaluation.golden_dataset.models import BenchmarkCase


def _case(**overrides) -> BenchmarkCase:
    payload = {
        "case_id": "c1",
        "surface": "research",
        "dataset_version": 1,
        "case_version": 1,
        "context": {"ticker": "AAPL", "query": "q"},
        "expected_behaviors": [
            {"behavior_id": "b1", "type": "presence", "description": "d",
             "match_rule": "keyword_variant", "variants": ["revenue grew"]},
        ],
        "citation_expectation": {},
    }
    payload.update(overrides)
    return BenchmarkCase.model_validate(payload)


def _adapter_result(case: BenchmarkCase, **overrides) -> AdapterResult:
    output_payload = dict(
        text="Revenue grew 5% [1].",
        citations=[Citation(source_id="1", eligible=True, referenced=True, valid=True)],
        grounding_verdict="grounded",
        limitations_stated=[],
    )
    output_payload.update(overrides.pop("output", {}))
    return AdapterResult(
        case_id=case.case_id, surface=case.surface, mode="live",
        output=NormalizedOutput(**output_payload),
        execution=ExecutionMetadata(provider="gemini", model="gemini-flash"),
        **overrides,
    )


def test_all_rules_pass_yields_overall_pass():
    case = _case()
    result = evaluate_case(case, _adapter_result(case))
    assert result.status == "PASS"
    assert result.failure_reasons == []
    assert result.evaluation_version == EVALUATION_VERSION


def test_one_rule_failing_yields_overall_fail():
    case = _case(expected_behaviors=[
        {"behavior_id": "b1", "type": "presence", "description": "d",
         "match_rule": "keyword_variant", "variants": ["revenue declined"]},  # won't match
    ])
    result = evaluate_case(case, _adapter_result(case))
    assert result.status == "FAIL"
    assert any("b1" in r for r in result.failure_reasons)


def test_multiple_failures_all_reported():
    case = _case(expected_behaviors=[
        {"behavior_id": "b1", "type": "presence", "description": "d",
         "match_rule": "keyword_variant", "variants": ["not present"]},
        {"behavior_id": "b2", "type": "presence", "description": "d",
         "match_rule": "citation_required", "reference": "x"},
    ], citation_expectation={"min_valid_citations": 5})  # unmeetable floor
    result = evaluate_case(case, _adapter_result(case))
    assert result.status == "FAIL"
    reasons = " ".join(result.failure_reasons)
    assert "b1" in reasons
    assert "citation_expectation" in reasons


def test_inconclusive_rule_yields_overall_inconclusive_when_nothing_fails():
    case = _case(surface="learning", context={"ticker": "MSFT", "concept": "margin"}, expected_behaviors=[
        {"behavior_id": "b1", "type": "acknowledgment", "description": "d",
         "match_rule": "limitation_reference", "reference": "gap"},
    ], known_limitations=["gap"])
    adapter_result = _adapter_result(case, output={"text": "explained [1]"})  # Learning -> always inconclusive
    result = evaluate_case(case, adapter_result)
    assert result.status == "INCONCLUSIVE"


def test_fail_takes_priority_over_unrelated_inconclusive():
    case = _case(surface="learning", context={"ticker": "MSFT", "concept": "margin"}, expected_behaviors=[
        {"behavior_id": "b1", "type": "presence", "description": "d",
         "match_rule": "keyword_variant", "variants": ["not present anywhere"]},  # definite FAIL
        {"behavior_id": "b2", "type": "acknowledgment", "description": "d",
         "match_rule": "limitation_reference", "reference": "gap"},  # Learning -> INCONCLUSIVE
    ], known_limitations=["gap"])
    adapter_result = _adapter_result(case, output={"text": "explained clearly [1]"})
    result = evaluate_case(case, adapter_result)
    assert result.status == "FAIL"  # not masked by b2's inconclusive
    assert any("b1" in r for r in result.failure_reasons)


def test_mixed_results_pass_fail_inconclusive_metrics_all_present():
    case = _case()
    result = evaluate_case(case, _adapter_result(case))
    metric_names = {m.name for m in result.metrics}
    assert metric_names == {
        "citation_expectation", "citation_coverage", "grounding_status", "expected_characteristic_coverage",
    }


def test_case_adapter_result_mismatch_raises():
    case = _case()
    other = _case(case_id="different")
    try:
        evaluate_case(case, _adapter_result(other))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for mismatched case/adapter_result")


def test_deterministic_repeated_evaluation():
    case = _case()
    adapter_result = _adapter_result(case)
    r1 = evaluate_case(case, adapter_result)
    r2 = evaluate_case(case, adapter_result)
    assert r1 == r2  # frozen dataclasses compare structurally


def test_grounding_error_yields_case_inconclusive():
    case = _case()
    result = evaluate_case(case, _adapter_result(case, output={
        "text": "", "citations": [], "grounding_verdict": "error", "limitations_stated": [],
    }))
    assert result.status == "INCONCLUSIVE"


def test_grounding_ungrounded_yields_case_fail():
    case = _case()
    result = evaluate_case(case, _adapter_result(case, output={
        "text": "Revenue grew [1].",
        "citations": [Citation(source_id="1", eligible=True, referenced=True, valid=True)],
        "grounding_verdict": "ungrounded",
        "limitations_stated": [],
    }))
    assert result.status == "FAIL"
    assert any("grounding_status" in r for r in result.failure_reasons)


def _citation_coverage(result):
    return next(m for m in result.metrics if m.name == "citation_coverage")


def test_citation_coverage_inconclusive_when_no_output_despite_eligible_citations():
    # Reviewer 2 regression: the Research adapter (evaluation/adapters/
    # research.py) builds `citations` from len(source_documents) regardless
    # of whether `draft_report` came back empty — so a run that retrieved
    # evidence but never produced text (grounding_verdict="error") can still
    # carry eligible=True citations. citation_coverage must read this as
    # "nothing to measure" (INCONCLUSIVE), not compute a real 0.0/PASS that
    # would misrepresent "no attempt was made" as "output existed and cited
    # none of the eligible evidence".
    case = _case()
    result = evaluate_case(case, _adapter_result(case, output={
        "text": "",
        "citations": [Citation(source_id=str(i), eligible=True, referenced=False, valid=False)
                      for i in range(1, 6)],
        "grounding_verdict": "error",
        "limitations_stated": [],
    }))
    coverage = _citation_coverage(result)
    assert coverage.value is None
    assert coverage.status == "INCONCLUSIVE"


def test_citation_coverage_zero_when_genuine_output_cites_nothing_valid():
    # Distinguishing case: real output text exists, eligible evidence
    # exists, but nothing was validly cited — this IS a computable 0.0,
    # and must stay PASS (citation_coverage never gates on its own value,
    # only on whether it was computable) rather than collapsing into the
    # no-output INCONCLUSIVE case above.
    case = _case()
    result = evaluate_case(case, _adapter_result(case, output={
        "text": "Revenue grew this quarter.",
        "citations": [Citation(source_id=str(i), eligible=True, referenced=False, valid=False)
                      for i in range(1, 6)],
        "grounding_verdict": "ungrounded",
        "limitations_stated": [],
    }))
    coverage = _citation_coverage(result)
    assert coverage.value == 0.0
    assert coverage.status == "PASS"


if __name__ == "__main__":
    test_all_rules_pass_yields_overall_pass()
    test_one_rule_failing_yields_overall_fail()
    test_multiple_failures_all_reported()
    test_inconclusive_rule_yields_overall_inconclusive_when_nothing_fails()
    test_fail_takes_priority_over_unrelated_inconclusive()
    test_mixed_results_pass_fail_inconclusive_metrics_all_present()
    test_case_adapter_result_mismatch_raises()
    test_deterministic_repeated_evaluation()
    test_grounding_error_yields_case_inconclusive()
    test_grounding_ungrounded_yields_case_fail()
    test_citation_coverage_inconclusive_when_no_output_despite_eligible_citations()
    test_citation_coverage_zero_when_genuine_output_cites_nothing_valid()
    print("ok: evaluate_case — rollup status, metrics, determinism, mismatch guard")
