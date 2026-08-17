"""M10 Phase 4 — regression comparison (Document 45 §18, Document 46 §6's
complete, frozen truth table — reproduced verbatim below, one branch per row).

Deterministic: given the same stored results, the same current
CaseEvaluationResult, and the same schema_version, `compare()` always
returns the same verdict. No randomness, no network call, no LLM call.
"""
from __future__ import annotations

from pathlib import Path

from evaluation.core.types import CaseEvaluationResult
from evaluation.regression.result_store import RESULTS_DIR, find_baseline
from evaluation.regression.types import Verdict

# Document 45 §18's WARNING row: "citation_coverage or expected_characteristic_
# coverage is strictly lower than the baseline run's value for the same metric."
_SOFT_METRICS = ("citation_coverage", "expected_characteristic_coverage")


def _metric_value(case: CaseEvaluationResult, name: str) -> float | None:
    for m in case.metrics:
        if m.name == name and isinstance(m.value, (int, float)):
            return float(m.value)
    return None


def _warning_reason(baseline: CaseEvaluationResult, current: CaseEvaluationResult) -> str | None:
    for name in _SOFT_METRICS:
        b = _metric_value(baseline, name)
        c = _metric_value(current, name)
        if b is not None and c is not None and c < b:
            return f"{name} dropped from {b} to {c}"
    return None


def compare(
    current: CaseEvaluationResult, *, schema_version: str | None, results_dir: Path = RESULTS_DIR,
) -> tuple[Verdict, str]:
    """Document 46 §6's truth table, implemented exactly:

    | Baseline                          | Current      | Verdict          |
    |------------------------------------|--------------|------------------|
    | No eligible baseline                | PASS         | INCONCLUSIVE     |
    | No eligible baseline                | FAIL         | INCONCLUSIVE     |
    | No eligible baseline                | INCONCLUSIVE | INCONCLUSIVE     |
    | Eligible, baseline PASS             | PASS, no drop| PASS             |
    | Eligible, baseline PASS             | PASS, drop   | WARNING          |
    | Eligible, baseline PASS             | FAIL         | REGRESSION       |
    | Eligible, baseline FAIL             | PASS         | PASS             |
    | Eligible, baseline FAIL             | FAIL         | UNCHANGED_FAILURE|
    | Eligible (any)                      | INCONCLUSIVE | INCONCLUSIVE     |
    | Most recent compatible = INCONCLUSIVE| (any)       | INCONCLUSIVE (handled inside find_baseline) |
    | current.mode != "fixture"            | (any)       | INCONCLUSIVE (handled here, before any lookup) |

    Document 45 §11.1: "FIXTURE MODE is the only mode eligible as a
    regression baseline **or comparison target**." The baseline side is
    already filtered by find_baseline() (mode=="fixture" in its own query);
    this guard is the symmetric check on the *current* side — a LIVE result
    is recorded (Document 45 §12: mode:"live" is a valid EvaluationResult)
    for integration verification only, and must never itself be compared
    against a stored baseline. Checked first, before any baseline lookup —
    a LIVE current result has no business consulting the baseline store at
    all.
    """
    if current.mode != "fixture":
        return "INCONCLUSIVE", (
            f"current result mode={current.mode!r} — LIVE-mode results are never eligible as a "
            "regression comparison target (Document 45 §11.1); recorded for integration "
            "verification only, not compared against any baseline"
        )

    baseline_result, no_baseline_reason = find_baseline(current, schema_version=schema_version, results_dir=results_dir)

    if baseline_result is None:
        return "INCONCLUSIVE", no_baseline_reason

    baseline = baseline_result.case

    if current.status == "INCONCLUSIVE":
        return "INCONCLUSIVE", "current run is INCONCLUSIVE (no quality signal to compare)"

    if baseline.status == "PASS" and current.status == "PASS":
        warn = _warning_reason(baseline, current)
        if warn:
            return "WARNING", warn
        return "PASS", "matches baseline (PASS -> PASS, no soft-metric drop)"

    if baseline.status == "PASS" and current.status == "FAIL":
        return "REGRESSION", "baseline PASS, current FAIL"

    if baseline.status == "FAIL" and current.status == "PASS":
        return "PASS", "baseline FAIL, current PASS (not IMPROVEMENT — Document 45 §18)"

    if baseline.status == "FAIL" and current.status == "FAIL":
        return "UNCHANGED_FAILURE", "baseline FAIL, current FAIL — nothing newly broke"

    raise AssertionError(  # unreachable: Status is a 3-value Literal, all 2x2 combinations covered above
        f"unreachable status combination: baseline={baseline.status!r}, current={current.status!r}"
    )
