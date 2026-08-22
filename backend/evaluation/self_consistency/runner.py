"""M11 self-consistency evaluation tooling (Document 47 §9.1) — repeated
judge invocation over a fixed held-out claim/evidence set, and aggregation
of the resulting verdict measurements.

This module PRODUCES EVIDENCE ONLY for a later, separate CTO/reviewer
gate-promotion decision (§9.1 step 6). It never imports
evaluation.core.judge_gate or evaluation.core.case_evaluator, never reads or
writes JUDGE_SELF_CONSISTENCY_GATE_VERSION, and never feeds a result into
case-level PASS/FAIL — there is no code path from here into evaluate_case at
all. Reuses evaluation/core/judge.py::invoke_judge exactly as Phase C built
it (no second LLM abstraction, no provider SDK call, no new dependency) —
called directly with a fixed (claim, evidence) pair, bypassing Phase C's own
deterministic claim/evidence *selector* entirely, since the whole point of
this tooling is that the pair is already fixed by the held-out case, not
discovered from a NormalizedOutput each time (this task's own §2: "Do NOT
regenerate the claim... Do NOT execute the full LIVE ... pipeline").
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Callable

from agents.llm import _active
from evaluation.core.judge import JUDGE_PROMPT_VERSION, invoke_judge
from evaluation.self_consistency.cases import HeldOutCase


@dataclass(frozen=True)
class Measurement:
    """One judge invocation's outcome (Document 47 §9.1 steps 3-4). On
    failure, every judge-detail field is None and `error` carries the
    message — an infrastructure failure is never fabricated into a verdict
    (the same discipline Document 47 §7.3 applies to evaluate_model_judged_support,
    applied here to measurement instead of case evaluation)."""

    case_id: str
    repetition_index: int
    timestamp: str
    success: bool
    verdict: str | None
    rationale: str | None
    judge_model: str | None
    judge_prompt_version: str | None
    error: str | None = None


async def run_case_repeats(
    case: HeldOutCase, *, repeats: int, timestamp_fn: Callable[[], str],
) -> list[Measurement]:
    """Document 47 §9.1 steps 2-3: `repeats` INDEPENDENT judge calls against
    the exact same (case.claim, case.evidence) pair. Never regenerated,
    never cached, never deduplicated between repeats (this task's own §4) —
    each iteration is a fresh `invoke_judge` call. `timestamp_fn` is
    injected rather than calling datetime.now() directly in this module,
    matching EvaluationResult.timestamp's own established convention
    (evaluation/regression/types.py) of stamping time at the caller, not
    inside deterministic/reusable logic."""
    measurements: list[Measurement] = []
    for i in range(repeats):
        try:
            result = await invoke_judge(case.claim, case.evidence)
        except Exception as e:  # noqa: BLE001 — same broad boundary Document 47 §7.3
            # already established for evaluate_model_judged_support: every
            # judge-execution failure kind is one infrastructure signal, not
            # a taxonomy to build here.
            measurements.append(Measurement(
                case_id=case.case_id, repetition_index=i, timestamp=timestamp_fn(),
                success=False, verdict=None, rationale=None,
                judge_model=None, judge_prompt_version=None, error=str(e),
            ))
            continue
        measurements.append(Measurement(
            case_id=case.case_id, repetition_index=i, timestamp=timestamp_fn(),
            success=True, verdict=result.verdict, rationale=result.rationale,
            judge_model=_active().get("light"), judge_prompt_version=JUDGE_PROMPT_VERSION,
            error=None,
        ))
    return measurements


@dataclass(frozen=True)
class CaseAgreement:
    """Per-case verdict agreement (Document 47 §9.1 steps 3/5). `agreement_rate`
    is computed over successful invocations only — None (never a fabricated
    0.0) if every repetition for this case failed. `matches_reference` is
    None (not False) when there is no modal verdict to compare, for the same
    reason: absence of evidence is not evidence of disagreement."""

    case_id: str
    reference_verdict: str
    repetitions: int
    verdict_distribution: dict[str, int]
    successes: int
    failures: int
    agreement_rate: float | None
    modal_verdict: str | None
    matches_reference: bool | None


@dataclass(frozen=True)
class AggregateReport:
    """Overall self-consistency evidence (Document 47 §9.1 steps 3/5-6) —
    the complete input to a later CTO/reviewer judgment call. No pass/fail
    verdict of its own: this task's own explicit instruction not to invent
    an acceptance threshold means this report states measurements, not a
    recommendation."""

    cases: list[CaseAgreement]
    total_cases: int
    total_invocations: int
    total_successes: int
    total_failures: int
    overall_verdict_distribution: dict[str, int]
    overall_agreement_rate_mean: float | None
    judge_models: list[str]
    judge_prompt_versions: list[str]


def aggregate(cases: list[HeldOutCase], measurements: list[Measurement]) -> AggregateReport:
    """Document 47 §9.1 steps 3/5. VERDICT agreement only — rationale is
    never compared (§7.3/§8: documentation only, this task's own §6).
    Infrastructure failures (Measurement.success is False) are counted and
    reported SEPARATELY from verdict disagreement (this task's own §5) —
    a case where every repeat errored has an agreement_rate of None, not a
    0.0 that would misrepresent "couldn't measure" as "measured and
    disagreed"."""
    by_case_id = {c.case_id: c for c in cases}
    by_case: dict[str, list[Measurement]] = {}
    for m in measurements:
        by_case.setdefault(m.case_id, []).append(m)

    case_reports: list[CaseAgreement] = []
    for case_id, case_measurements in by_case.items():
        case = by_case_id[case_id]
        successes = [m for m in case_measurements if m.success]
        failures = [m for m in case_measurements if not m.success]
        dist = dict(Counter(m.verdict for m in successes))

        modal_verdict: str | None = None
        agreement_rate: float | None = None
        if successes:
            modal_verdict, modal_count = Counter(m.verdict for m in successes).most_common(1)[0]
            agreement_rate = modal_count / len(successes)

        case_reports.append(CaseAgreement(
            case_id=case_id,
            reference_verdict=case.reference_verdict,
            repetitions=len(case_measurements),
            verdict_distribution=dist,
            successes=len(successes),
            failures=len(failures),
            agreement_rate=agreement_rate,
            modal_verdict=modal_verdict,
            matches_reference=(modal_verdict == case.reference_verdict) if modal_verdict is not None else None,
        ))

    all_successes = [m for m in measurements if m.success]
    overall_dist = dict(Counter(m.verdict for m in all_successes))
    per_case_rates = [c.agreement_rate for c in case_reports if c.agreement_rate is not None]
    overall_agreement_rate_mean = (sum(per_case_rates) / len(per_case_rates)) if per_case_rates else None

    return AggregateReport(
        cases=case_reports,
        total_cases=len(by_case),
        total_invocations=len(measurements),
        total_successes=len(all_successes),
        total_failures=len(measurements) - len(all_successes),
        overall_verdict_distribution=overall_dist,
        overall_agreement_rate_mean=overall_agreement_rate_mean,
        judge_models=sorted({m.judge_model for m in all_successes if m.judge_model}),
        judge_prompt_versions=sorted({m.judge_prompt_version for m in all_successes if m.judge_prompt_version}),
    )
