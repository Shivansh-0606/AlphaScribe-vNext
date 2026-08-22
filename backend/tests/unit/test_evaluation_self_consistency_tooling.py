"""M11 self-consistency evaluation tooling (Document 47 §9.1) — hermetic
tests only. `invoke_judge` is mocked throughout (same idiom Phase C's own
tests already use, patched here at `evaluation.self_consistency.runner`'s
own import binding) — this file never makes a live provider call. A
separate, explicitly-labeled real pilot run (not part of this suite)
produces the actual empirical evidence.

    python -m pytest backend/tests/unit/test_evaluation_self_consistency_tooling.py -v
"""
import asyncio
import dataclasses
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest  # noqa: E402
from pydantic import ValidationError  # noqa: E402

import evaluation.self_consistency.runner as runner_module  # noqa: E402
from agents.schemas import JudgeVerdictSchema  # noqa: E402
from evaluation.self_consistency.cases import HeldOutCase, HeldOutSetIntegrityError, load_held_out_set  # noqa: E402
from evaluation.self_consistency.runner import CaseAgreement, aggregate, run_case_repeats  # noqa: E402

_REAL_CASES_DIR = Path(__file__).resolve().parents[2] / "evaluation" / "self_consistency" / "cases"


def _case(**overrides) -> HeldOutCase:
    payload = dict(
        case_id="sc1", surface="research", provenance="test fixture",
        claim="Revenue grew 5%.", evidence="Revenue grew 5% year-over-year.",
        reference_verdict="SUPPORTED", reference_rationale="matches",
    )
    payload.update(overrides)
    return HeldOutCase(**payload)


@pytest.fixture()
def mock_invoke_judge(monkeypatch):
    """Patches evaluation.self_consistency.runner.invoke_judge — the name
    bound in that module's own namespace, not evaluation.core.judge's."""
    state = {"queue": [], "calls": []}

    async def _fake(claim, evidence):
        state["calls"].append((claim, evidence))
        if not state["queue"]:
            raise AssertionError("mock_invoke_judge exhausted its queued responses")
        item = state["queue"].pop(0)
        if isinstance(item, Exception):
            raise item
        verdict, rationale = item
        return JudgeVerdictSchema(verdict=verdict, rationale=rationale)

    monkeypatch.setattr(runner_module, "invoke_judge", _fake)

    def _queue(*items):
        state["queue"].extend(items)

    _queue.calls = lambda: state["calls"]
    return _queue


def _ts():
    return "2026-08-18T00:00:00+00:00"


# ---------------------------------------------------------------------------
# 1. Held-out dataset loads correctly
# ---------------------------------------------------------------------------

def test_real_held_out_set_loads_and_is_research_learning_only():
    cases = load_held_out_set(_REAL_CASES_DIR)
    assert len(cases) >= 6
    assert {c.surface for c in cases} <= {"research", "learning"}
    verdicts = {c.reference_verdict for c in cases}
    assert {"SUPPORTED", "CONTRADICTED", "UNSUPPORTED"} <= verdicts  # meaningful mixture, this task's own §1


def test_held_out_set_loads_from_directory(tmp_path):
    (tmp_path / "c1.json").write_text(_case().model_dump_json(), encoding="utf-8")
    cases = load_held_out_set(tmp_path)
    assert len(cases) == 1
    assert cases[0].case_id == "sc1"


def test_held_out_set_rejects_comparison_explanation_surface(tmp_path):
    # Surface is a closed Literal ("research"|"learning") -- comparison_explanation
    # cannot even be constructed, let alone loaded (this task's own §1: "Do NOT
    # use Comparison Explanation cases").
    with pytest.raises(ValidationError):
        _case(surface="comparison_explanation")


# ---------------------------------------------------------------------------
# 2. Malformed held-out case is rejected
# ---------------------------------------------------------------------------

def test_malformed_case_missing_claim_is_rejected(tmp_path):
    (tmp_path / "bad.json").write_text('{"case_id": "x", "surface": "research"}', encoding="utf-8")
    with pytest.raises(HeldOutSetIntegrityError, match="schema validation failed"):
        load_held_out_set(tmp_path)


def test_malformed_case_invalid_json_is_rejected(tmp_path):
    (tmp_path / "bad.json").write_text("{not json", encoding="utf-8")
    with pytest.raises(HeldOutSetIntegrityError, match="invalid JSON"):
        load_held_out_set(tmp_path)


def test_duplicate_case_id_is_rejected(tmp_path):
    (tmp_path / "a.json").write_text(_case(case_id="dup").model_dump_json(), encoding="utf-8")
    (tmp_path / "b.json").write_text(_case(case_id="dup").model_dump_json(), encoding="utf-8")
    with pytest.raises(HeldOutSetIntegrityError, match="duplicate case_id"):
        load_held_out_set(tmp_path)


# ---------------------------------------------------------------------------
# 3-5. Fixed claim/evidence, repeat count respected, every repeat is fresh
# ---------------------------------------------------------------------------

def test_repeat_count_is_respected(mock_invoke_judge):
    mock_invoke_judge(*[("SUPPORTED", "r") for _ in range(4)])
    measurements = asyncio.run(run_case_repeats(_case(), repeats=4, timestamp_fn=_ts))
    assert len(measurements) == 4
    assert [m.repetition_index for m in measurements] == [0, 1, 2, 3]


def test_claim_and_evidence_identical_across_all_repetitions(mock_invoke_judge):
    case = _case(claim="Fixed claim text.", evidence="Fixed evidence text.")
    mock_invoke_judge(*[("SUPPORTED", "r") for _ in range(5)])
    asyncio.run(run_case_repeats(case, repeats=5, timestamp_fn=_ts))
    calls = mock_invoke_judge.calls()
    assert len(calls) == 5
    assert all(c == ("Fixed claim text.", "Fixed evidence text.") for c in calls)  # never regenerated


def test_each_repetition_is_a_fresh_invocation_no_caching(mock_invoke_judge):
    # Different verdicts queued per call -- if the runner cached/reused the
    # first result, every measurement would show the same (first) verdict.
    mock_invoke_judge(("SUPPORTED", "a"), ("CONTRADICTED", "b"), ("UNSUPPORTED", "c"))
    measurements = asyncio.run(run_case_repeats(_case(), repeats=3, timestamp_fn=_ts))
    assert [m.verdict for m in measurements] == ["SUPPORTED", "CONTRADICTED", "UNSUPPORTED"]
    assert len(mock_invoke_judge.calls()) == 3  # three real calls, not one deduplicated call


# ---------------------------------------------------------------------------
# 6-7. Verdict distribution and agreement rate calculated correctly
# ---------------------------------------------------------------------------

def test_verdict_distribution_and_agreement_rate(mock_invoke_judge):
    mock_invoke_judge(
        ("SUPPORTED", "a"), ("SUPPORTED", "b"), ("SUPPORTED", "c"), ("CONTRADICTED", "d"),
    )
    case = _case(reference_verdict="SUPPORTED")
    measurements = asyncio.run(run_case_repeats(case, repeats=4, timestamp_fn=_ts))
    report = aggregate([case], measurements)
    assert report.total_cases == 1
    case_report = report.cases[0]
    assert case_report.verdict_distribution == {"SUPPORTED": 3, "CONTRADICTED": 1}
    assert case_report.agreement_rate == 0.75  # 3/4, the modal verdict's share
    assert case_report.modal_verdict == "SUPPORTED"
    assert case_report.matches_reference is True


def test_perfect_agreement_is_1_0(mock_invoke_judge):
    mock_invoke_judge(*[("CONTRADICTED", "x") for _ in range(5)])
    case = _case(reference_verdict="CONTRADICTED")
    measurements = asyncio.run(run_case_repeats(case, repeats=5, timestamp_fn=_ts))
    report = aggregate([case], measurements)
    assert report.cases[0].agreement_rate == 1.0
    assert report.cases[0].matches_reference is True


def test_modal_verdict_disagreeing_with_reference_is_flagged(mock_invoke_judge):
    mock_invoke_judge(("UNSUPPORTED", "a"), ("UNSUPPORTED", "b"), ("SUPPORTED", "c"))
    case = _case(reference_verdict="SUPPORTED")  # judge mostly says UNSUPPORTED
    measurements = asyncio.run(run_case_repeats(case, repeats=3, timestamp_fn=_ts))
    report = aggregate([case], measurements)
    assert report.cases[0].modal_verdict == "UNSUPPORTED"
    assert report.cases[0].matches_reference is False  # disagreement characterization, this task's own §5


# ---------------------------------------------------------------------------
# 8. INCONCLUSIVE/failure reported separately from verdict disagreement
# ---------------------------------------------------------------------------

def test_failures_reported_separately_from_verdict_distribution(mock_invoke_judge):
    mock_invoke_judge(
        ("SUPPORTED", "a"), RuntimeError("provider unavailable"), ("SUPPORTED", "b"),
    )
    case = _case()
    measurements = asyncio.run(run_case_repeats(case, repeats=3, timestamp_fn=_ts))
    assert [m.success for m in measurements] == [True, False, True]
    assert measurements[1].verdict is None
    assert measurements[1].error is not None

    report = aggregate([case], measurements)
    case_report = report.cases[0]
    assert case_report.successes == 2
    assert case_report.failures == 1
    assert case_report.repetitions == 3
    assert "RuntimeError" not in case_report.verdict_distribution  # failure never counted as a verdict
    assert sum(case_report.verdict_distribution.values()) == 2  # only successes counted
    assert case_report.agreement_rate == 1.0  # computed over the 2 successes only, both SUPPORTED


def test_all_failures_yields_none_agreement_not_zero(mock_invoke_judge):
    mock_invoke_judge(RuntimeError("x"), RuntimeError("y"))
    case = _case()
    measurements = asyncio.run(run_case_repeats(case, repeats=2, timestamp_fn=_ts))
    report = aggregate([case], measurements)
    assert report.cases[0].successes == 0
    assert report.cases[0].failures == 2
    assert report.cases[0].agreement_rate is None  # never a fabricated 0.0
    assert report.cases[0].modal_verdict is None
    assert report.cases[0].matches_reference is None


def test_overall_totals_separate_successes_and_failures(mock_invoke_judge):
    mock_invoke_judge(("SUPPORTED", "a"), RuntimeError("x"))
    case = _case()
    measurements = asyncio.run(run_case_repeats(case, repeats=2, timestamp_fn=_ts))
    report = aggregate([case], measurements)
    assert report.total_invocations == 2
    assert report.total_successes == 1
    assert report.total_failures == 1


# ---------------------------------------------------------------------------
# 9-10. judge_model / judge_prompt_version retained
# ---------------------------------------------------------------------------

def test_judge_model_and_prompt_version_retained_per_measurement(mock_invoke_judge):
    mock_invoke_judge(("SUPPORTED", "a"))
    measurements = asyncio.run(run_case_repeats(_case(), repeats=1, timestamp_fn=_ts))
    m = measurements[0]
    assert m.judge_model is not None
    assert m.judge_prompt_version is not None


def test_judge_models_and_versions_surfaced_in_report(mock_invoke_judge):
    mock_invoke_judge(("SUPPORTED", "a"), ("SUPPORTED", "b"))
    case = _case()
    measurements = asyncio.run(run_case_repeats(case, repeats=2, timestamp_fn=_ts))
    report = aggregate([case], measurements)
    assert len(report.judge_models) >= 1
    assert len(report.judge_prompt_versions) >= 1


def test_failed_measurement_has_no_model_or_version_fabricated(mock_invoke_judge):
    mock_invoke_judge(RuntimeError("x"))
    measurements = asyncio.run(run_case_repeats(_case(), repeats=1, timestamp_fn=_ts))
    assert measurements[0].judge_model is None
    assert measurements[0].judge_prompt_version is None


# ---------------------------------------------------------------------------
# 11. Rationale is not used for agreement
# ---------------------------------------------------------------------------

def test_varying_rationale_text_does_not_affect_agreement_rate(mock_invoke_judge):
    # Same verdict every time, wildly different rationale text -- agreement
    # must be 1.0 regardless (Document 47 §7.3/§8: rationale is
    # documentation only, never re-parsed or matched as structured truth;
    # this task's own §6 explicitly forbids a rationale-similarity metric).
    mock_invoke_judge(
        ("SUPPORTED", "The figures line up exactly."),
        ("SUPPORTED", "Yes, evidence confirms this."),
        ("SUPPORTED", "Matches: 94.9B, +6%."),
    )
    case = _case(reference_verdict="SUPPORTED")
    measurements = asyncio.run(run_case_repeats(case, repeats=3, timestamp_fn=_ts))
    report = aggregate([case], measurements)
    assert report.cases[0].agreement_rate == 1.0
    # Confirm rationale text itself never enters CaseAgreement at all.
    assert not any("rationale" in f.name for f in dataclasses.fields(CaseAgreement))


# ---------------------------------------------------------------------------
# 12. No gate promotion occurs anywhere in this tooling
# ---------------------------------------------------------------------------

def test_tooling_never_imports_judge_gate_or_case_evaluator():
    import evaluation.self_consistency.cases as cases_mod
    import evaluation.self_consistency.runner as runner_mod
    for mod in (cases_mod, runner_mod):
        assert "judge_gate" not in mod.__dict__
        assert "case_evaluator" not in mod.__dict__
        assert "evaluate_case" not in mod.__dict__
        assert "JUDGE_SELF_CONSISTENCY_GATE_VERSION" not in mod.__dict__


def test_gate_constant_unchanged_after_running_tooling(mock_invoke_judge):
    from evaluation.core import judge_gate
    before = judge_gate.JUDGE_SELF_CONSISTENCY_GATE_VERSION
    mock_invoke_judge(("SUPPORTED", "a"))
    asyncio.run(run_case_repeats(_case(), repeats=1, timestamp_fn=_ts))
    assert judge_gate.JUDGE_SELF_CONSISTENCY_GATE_VERSION == before == 0


if __name__ == "__main__":
    print("This test file uses pytest fixtures (monkeypatch, mock_invoke_judge, tmp_path) — run via pytest:")
    print("  python -m pytest backend/tests/unit/test_evaluation_self_consistency_tooling.py -v")
