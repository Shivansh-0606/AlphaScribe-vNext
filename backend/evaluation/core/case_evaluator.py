"""M10 Phase 3 — the case evaluation flow (Document 45 §10, §13):

    Benchmark Case -> Expected Behaviors -> Metric Evaluators
                    -> Metric Results -> Case Evaluation Result

Implements exactly Document 45 §13's four metrics (citation coverage,
grounding status, expected-characteristic coverage, case pass/fail) — no
metric beyond these four, matching §13's own "no metric beyond these four is
defined for M10" and this task's §8 instruction not to invent new metrics.

Existing production scoring/citation logic (agents/scoring.py's
compute_scorecard, agents/comparison_explanation.py's
validate_and_map_citations, agents/learning_nodes.py's
_postprocess_citations) is deliberately NOT called again here — Phase 2's
adapters already wrapped all three (Document 45 §14) to produce the
surface-blind NormalizedOutput this module consumes. Calling them a second
time here would duplicate Phase 2's own job and reintroduce the report-shape
coupling Document 45 §6 principle 3 explicitly rejects.
"""
from __future__ import annotations

from evaluation.adapters.types import AdapterResult, NormalizedOutput
from evaluation.core.behaviors import evaluate_behavior, no_output_reason
from evaluation.core.types import BehaviorEvaluation, CaseEvaluationResult, MetricResult, Status
from evaluation.golden_dataset.models import BenchmarkCase

# Bumped when this module's metric/status logic changes — Document 45 §12/§17's
# evaluation_version, so a metric-definition change is distinguishable from a
# model/prompt change in any later (Phase 4) comparison.
EVALUATION_VERSION = "v1"


def _citation_expectation_metric(case: BenchmarkCase, output: NormalizedOutput) -> MetricResult:
    reason = no_output_reason(output)
    if reason:
        return MetricResult("citation_expectation", None, "INCONCLUSIVE", reason)

    valid_ids = {c.source_id for c in output.citations if c.valid}
    n_valid = len(valid_ids)
    exp = case.citation_expectation

    if n_valid < exp.min_valid_citations:
        return MetricResult(
            "citation_expectation", n_valid, "FAIL",
            f"{n_valid} valid citation(s), need >= {exp.min_valid_citations}",
        )
    missing_required = [sid for sid in exp.required_source_ids if sid not in valid_ids]
    if missing_required:
        return MetricResult(
            "citation_expectation", n_valid, "FAIL",
            f"required source(s) not validly cited: {missing_required}",
        )
    return MetricResult("citation_expectation", n_valid, "PASS", "citation floor met")


def _citation_coverage_metric(output: NormalizedOutput) -> MetricResult:
    # Document 45 §13: diagnostic only — never gates case pass/fail on its
    # own (that's citation_expectation's job, above). Status here reflects
    # only whether the value was computable, not a pass/fail judgment on the
    # coverage number itself (Document 45 never defines a coverage floor).
    #
    # Reviewer 2 fix: guard on no_output_reason the same way
    # _citation_expectation_metric already does. Research/Learning adapters
    # can populate `citations` with eligible=True entries derived purely
    # from source_documents length even when the run produced no text at
    # all (synthesizer/fact-checker/explainer failure after a successful
    # retrieval) — without this guard, that "no attempt was made" case
    # computed a real 0.0/PASS coverage, indistinguishable from "output
    # existed and validly cited none of the eligible evidence". The two
    # must not collapse to the same number (same principle as §13's
    # E==0 -> null rule, applied one level earlier).
    reason = no_output_reason(output)
    if reason:
        return MetricResult("citation_coverage", None, "INCONCLUSIVE", reason)

    eligible = [c for c in output.citations if c.eligible]
    if not eligible:
        return MetricResult("citation_coverage", None, "INCONCLUSIVE", "no eligible evidence to cover")
    valid = [c for c in eligible if c.valid]
    coverage = len(valid) / len(eligible)
    return MetricResult("citation_coverage", coverage, "PASS", f"{len(valid)}/{len(eligible)} eligible sources validly cited")


def _grounding_status_metric(output: NormalizedOutput) -> MetricResult:
    if output.grounding_verdict == "grounded":
        status: Status = "PASS"
    elif output.grounding_verdict == "error":
        status = "INCONCLUSIVE"  # the surface didn't complete — not a quality verdict
    else:  # "ungrounded" — a completed run that failed its own grounding check
        status = "FAIL"
    return MetricResult("grounding_status", output.grounding_verdict, status,
                         f"grounding_verdict={output.grounding_verdict!r}")


def _characteristic_coverage_metric(behavior_evals: list[BehaviorEvaluation]) -> MetricResult:
    determinable = [b for b in behavior_evals if b.status != "INCONCLUSIVE"]
    if not determinable:
        return MetricResult("expected_characteristic_coverage", None, "INCONCLUSIVE",
                             "no expected_behaviors could be determined")
    passed = [b for b in determinable if b.status == "PASS"]
    coverage = len(passed) / len(determinable)
    status: Status = "PASS" if len(passed) == len(determinable) else "FAIL"
    return MetricResult("expected_characteristic_coverage", coverage, status,
                         f"{len(passed)}/{len(determinable)} determinable behaviors passed")


def _overall_status(
    behavior_evals: list[BehaviorEvaluation], citation_metric: MetricResult, grounding_metric: MetricResult,
) -> tuple[Status, list[str]]:
    # Document 45 §13's "Case pass/fail": Boolean AND of citation floor met,
    # grounding status = grounded, all required expected_behaviors satisfied.
    # FAIL takes priority over INCONCLUSIVE (this task's §12): a definite,
    # known problem must not be masked by an unrelated unknown elsewhere.
    fail_reasons = [f"{b.behavior_id}: {b.reason}" for b in behavior_evals if b.status == "FAIL"]
    if citation_metric.status == "FAIL":
        fail_reasons.append(f"citation_expectation: {citation_metric.detail}")
    if grounding_metric.status == "FAIL":
        fail_reasons.append(f"grounding_status: {grounding_metric.detail}")
    if fail_reasons:
        return "FAIL", fail_reasons

    inconclusive_reasons = [f"{b.behavior_id}: {b.reason}" for b in behavior_evals if b.status == "INCONCLUSIVE"]
    if citation_metric.status == "INCONCLUSIVE":
        inconclusive_reasons.append(f"citation_expectation: {citation_metric.detail}")
    if grounding_metric.status == "INCONCLUSIVE":
        inconclusive_reasons.append(f"grounding_status: {grounding_metric.detail}")
    if inconclusive_reasons:
        return "INCONCLUSIVE", inconclusive_reasons

    return "PASS", []


def evaluate_case(case: BenchmarkCase, adapter_result: AdapterResult) -> CaseEvaluationResult:
    """The Phase 3 entry point: one BenchmarkCase + the AdapterResult Phase 2
    produced for it -> one CaseEvaluationResult. Deterministic — identical
    inputs always produce an identical result; no randomness, no network
    call, no LLM call anywhere in this function or anything it calls."""
    if case.case_id != adapter_result.case_id or case.surface != adapter_result.surface:
        raise ValueError(
            f"case/adapter_result mismatch: case={case.case_id!r}/{case.surface!r} vs "
            f"adapter_result={adapter_result.case_id!r}/{adapter_result.surface!r}"
        )

    output = adapter_result.output
    behavior_evals = [
        evaluate_behavior(b, output, surface=case.surface) for b in case.expected_behaviors
    ]
    citation_metric = _citation_expectation_metric(case, output)
    coverage_metric = _citation_coverage_metric(output)
    grounding_metric = _grounding_status_metric(output)
    characteristic_metric = _characteristic_coverage_metric(behavior_evals)

    status, failure_reasons = _overall_status(behavior_evals, citation_metric, grounding_metric)

    return CaseEvaluationResult(
        case_id=case.case_id,
        surface=case.surface,
        dataset_version=case.dataset_version,
        case_version=case.case_version,
        mode=adapter_result.mode,
        evaluation_version=EVALUATION_VERSION,
        execution=adapter_result.execution,
        behavior_evaluations=behavior_evals,
        metrics=[citation_metric, coverage_metric, grounding_metric, characteristic_metric],
        status=status,
        failure_reasons=failure_reasons,
    )
