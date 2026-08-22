"""M11 Phase C correction — real save -> load round-trip fidelity for
`evaluation/regression/result_store.py` (Document 47 §8's JudgeDetail).

Distinct from test_evaluation_regression_baseline.py's own tests, which only
inspect `baseline.case.status` after a round-trip — none of them exercise
`judge_detail`'s nested-dataclass reconstruction at all. These tests drive
the real `save_result` -> `find_baseline`/`result_from_dict` path end to end
and inspect the loaded `BehaviorEvaluation.judge_detail` directly, proving
the fix rather than just the constructor in isolation.

Isolated tmp_path throughout — never the real backend/evaluation/results/.

    python -m pytest backend/tests/unit/test_evaluation_regression_result_store_roundtrip.py -v
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from evaluation.adapters.types import ExecutionMetadata
from evaluation.core.types import BehaviorEvaluation, CaseEvaluationResult, JudgeDetail, MetricResult
from evaluation.regression.result_store import find_baseline, result_from_dict, save_result
from evaluation.regression.types import EvaluationResult


def _case_result(behavior_evaluations, **overrides) -> CaseEvaluationResult:
    payload = dict(
        case_id="c1", surface="research", dataset_version=1, case_version=1,
        mode="fixture", evaluation_version="v1",
        execution=ExecutionMetadata(provider="gemini", model="gemini-flash"),
        behavior_evaluations=behavior_evaluations,
        metrics=[MetricResult("citation_expectation", 1, "PASS", "ok")],
        status="PASS", failure_reasons=[],
    )
    payload.update(overrides)
    return CaseEvaluationResult(**payload)


def _eval_result(case_result: CaseEvaluationResult, **overrides) -> EvaluationResult:
    payload = dict(
        run_id="run-1", timestamp="2026-01-01T00:00:00+00:00", code_revision="abc123",
        schema_version=None, case=case_result, verdict="PASS", verdict_reason="ok",
    )
    payload.update(overrides)
    return EvaluationResult(**payload)


# ---------------------------------------------------------------------------
# A. Deterministic evaluation: judge_detail=None survives the round-trip as None
# ---------------------------------------------------------------------------

def test_deterministic_behavior_judge_detail_stays_none_after_roundtrip(tmp_path):
    deterministic = BehaviorEvaluation("b1", "keyword_variant", "PASS", "matched")
    assert deterministic.judged_by == "deterministic"
    assert deterministic.judge_detail is None

    saved_path = save_result(_eval_result(_case_result([deterministic])), results_dir=tmp_path)
    loaded = result_from_dict(json.loads(saved_path.read_text(encoding="utf-8")))

    loaded_behavior = loaded.case.behavior_evaluations[0]
    assert loaded_behavior.judged_by == "deterministic"
    assert loaded_behavior.judge_detail is None
    assert loaded.case == _case_result([deterministic])  # full semantic equivalence


# ---------------------------------------------------------------------------
# B. Judged evaluation: JudgeDetail's nested dataclass must round-trip as a
# real JudgeDetail instance, every field preserved.
# ---------------------------------------------------------------------------

def _judged_behavior() -> BehaviorEvaluation:
    return BehaviorEvaluation(
        "b1", "model_judged_support", "PASS", "judge verdict SUPPORTED: matches",
        judged_by="model",
        judge_detail=JudgeDetail(
            judge_model="gemini-2.0-flash-lite",
            judge_prompt_version="v1",
            verdict="SUPPORTED",
            rationale="matches",
        ),
    )


def test_judged_behavior_judge_detail_reconstructs_as_real_dataclass(tmp_path):
    judged = _judged_behavior()
    saved_path = save_result(_eval_result(_case_result([judged])), results_dir=tmp_path)

    # Prove it against the actual persisted JSON, not a re-serialized copy —
    # judge_detail really is a plain dict on disk at this point.
    raw = json.loads(saved_path.read_text(encoding="utf-8"))
    raw_judge_detail = raw["case"]["behavior_evaluations"][0]["judge_detail"]
    assert isinstance(raw_judge_detail, dict)  # confirms this test exercises the real gap, not a strawman

    loaded = result_from_dict(raw)
    loaded_behavior = loaded.case.behavior_evaluations[0]

    assert type(loaded_behavior.judge_detail) is JudgeDetail
    assert loaded_behavior.judged_by == "model"
    assert loaded_behavior.judge_detail.verdict == "SUPPORTED"
    assert loaded_behavior.judge_detail.rationale == "matches"
    assert loaded_behavior.judge_detail.judge_model == "gemini-2.0-flash-lite"
    assert loaded_behavior.judge_detail.judge_prompt_version == "v1"

    # Semantic equivalence of the whole loaded case, not just the fields
    # enumerated above — would fail pre-fix since a raw dict is never equal
    # to a JudgeDetail instance for a frozen dataclass's own __eq__.
    assert loaded.case == _case_result([judged])
    assert loaded_behavior == judged


def test_roundtrip_survives_find_baseline_lookup_too(tmp_path):
    # find_baseline is the real production caller of this deserialization
    # path (via _all_results_for_case -> result_from_dict) — confirms the
    # fix holds through that entry point as well, not only result_from_dict
    # called directly.
    judged = _judged_behavior()
    save_result(_eval_result(_case_result([judged])), results_dir=tmp_path)

    baseline, reason = find_baseline(_case_result([judged]), schema_version=None, results_dir=tmp_path)
    assert baseline is not None
    loaded_behavior = baseline.case.behavior_evaluations[0]
    assert type(loaded_behavior.judge_detail) is JudgeDetail
    assert loaded_behavior.judge_detail.verdict == "SUPPORTED"


# ---------------------------------------------------------------------------
# C. M11 Phase E — structured-applicability JudgeDetail shape. Old files
# (saved before applicability/applicability_rationale existed, missing those
# keys entirely) must keep loading; new staged results must round-trip every
# field, including the new ones.
# ---------------------------------------------------------------------------

def test_old_shape_judge_detail_missing_applicability_keys_still_loads(tmp_path):
    # Hand-written dict simulating a file genuinely persisted before M11
    # Phase E existed — save_result()/asdict() would always include the new
    # keys (as None) for a freshly-constructed JudgeDetail, so this bypasses
    # that path to prove the real backward-compat case: keys absent, not
    # merely None.
    raw = {
        "run_id": "run-old", "timestamp": "2026-01-01T00:00:00+00:00", "code_revision": "abc123",
        "schema_version": None, "verdict": "PASS", "verdict_reason": "ok",
        "case": {
            "case_id": "c1", "surface": "research", "dataset_version": 1, "case_version": 1,
            "mode": "fixture", "evaluation_version": "v1",
            "execution": {"provider": "gemini", "model": "gemini-flash"},
            "behavior_evaluations": [{
                "behavior_id": "b1", "match_rule": "model_judged_support", "status": "PASS",
                "reason": "judge verdict SUPPORTED: matches", "judged_by": "model",
                "judge_detail": {
                    "judge_model": "gemini-2.0-flash-lite", "judge_prompt_version": "v3-na4",
                    "verdict": "SUPPORTED", "rationale": "matches",
                    # no "applicability" / "applicability_rationale" keys at all, and no
                    # "applicability_prompt_version" / "support_prompt_version" either
                    # (M11 Phase H governance correction, added one phase later still)
                },
            }],
            "metrics": [{"name": "citation_expectation", "value": 1, "status": "PASS", "detail": "ok"}],
            "status": "PASS", "failure_reasons": [],
        },
    }
    loaded = result_from_dict(raw)
    detail = loaded.case.behavior_evaluations[0].judge_detail
    assert type(detail) is JudgeDetail
    assert detail.verdict == "SUPPORTED"
    assert detail.applicability is None  # defaulted, not fabricated
    assert detail.applicability_rationale is None
    assert detail.applicability_prompt_version is None  # defaulted, not fabricated
    assert detail.support_prompt_version is None


def test_new_staged_shape_judge_detail_round_trips_all_fields(tmp_path):
    judged = BehaviorEvaluation(
        "b1", "model_judged_support", "FAIL", "judge verdict UNSUPPORTED: does not confirm",
        judged_by="model",
        judge_detail=JudgeDetail(
            judge_model="nvidia/nemotron-3-super-120b-a12b",
            judge_prompt_version="structured-applicability-v1",
            verdict="UNSUPPORTED",
            rationale="does not confirm",
            applicability="APPLICABLE",
            applicability_rationale="same underlying property",
            applicability_prompt_version="v1",
            support_prompt_version="v1",
        ),
    )
    saved_path = save_result(_eval_result(_case_result([judged])), results_dir=tmp_path)

    raw = json.loads(saved_path.read_text(encoding="utf-8"))
    raw_judge_detail = raw["case"]["behavior_evaluations"][0]["judge_detail"]
    assert raw_judge_detail["applicability"] == "APPLICABLE"  # persisted, not dropped
    assert raw_judge_detail["applicability_prompt_version"] == "v1"  # persisted, not dropped
    assert raw_judge_detail["support_prompt_version"] == "v1"

    loaded = result_from_dict(raw)
    detail = loaded.case.behavior_evaluations[0].judge_detail
    assert detail.applicability == "APPLICABLE"
    assert detail.applicability_rationale == "same underlying property"
    assert detail.judge_prompt_version == "structured-applicability-v1"
    assert detail.applicability_prompt_version == "v1"
    assert detail.support_prompt_version == "v1"
    assert loaded.case == _case_result([judged])  # full semantic equivalence, new fields included


def test_new_staged_not_applicable_shape_round_trips(tmp_path):
    # The NOT_APPLICABLE terminal case: verdict/rationale mirror Stage 1's
    # own decision (Stage 2 never ran) — proven through a real save/load, not
    # just a constructor call.
    judged = BehaviorEvaluation(
        "b1", "model_judged_support", "INCONCLUSIVE", "judge verdict NOT_APPLICABLE: different entity",
        judged_by="model",
        judge_detail=JudgeDetail(
            judge_model="nvidia/nemotron-3-super-120b-a12b",
            judge_prompt_version="structured-applicability-v1",
            verdict="NOT_APPLICABLE",
            rationale="different entity",
            applicability="NOT_APPLICABLE",
            applicability_rationale="different entity",
            applicability_prompt_version="v1",
            # support_prompt_version left at its None default -- Stage 2 never ran
        ),
    )
    saved_path = save_result(_eval_result(_case_result([judged])), results_dir=tmp_path)
    loaded = result_from_dict(json.loads(saved_path.read_text(encoding="utf-8")))
    detail = loaded.case.behavior_evaluations[0].judge_detail
    assert detail.applicability == "NOT_APPLICABLE"
    assert detail.verdict == "NOT_APPLICABLE"
    assert detail.applicability_prompt_version == "v1"
    assert detail.support_prompt_version is None  # Stage 2 never ran
    assert loaded.case == _case_result([judged])


def test_mixed_deterministic_and_judged_behaviors_both_reconstruct_correctly(tmp_path):
    # A realistic case: one deterministic behavior, one judged — proves the
    # fix doesn't special-case away the (still-common) deterministic path.
    deterministic = BehaviorEvaluation("b1", "keyword_variant", "PASS", "matched")
    judged = BehaviorEvaluation(
        "b2", "model_judged_support", "FAIL", "judge verdict CONTRADICTED: mismatch",
        judged_by="model",
        judge_detail=JudgeDetail(
            judge_model="gemini-2.0-flash-lite", judge_prompt_version="v1",
            verdict="CONTRADICTED", rationale="mismatch",
        ),
    )
    saved_path = save_result(
        _eval_result(_case_result([deterministic, judged], status="FAIL", failure_reasons=["b2: mismatch"])),
        results_dir=tmp_path,
    )
    loaded = result_from_dict(json.loads(saved_path.read_text(encoding="utf-8")))

    b1_loaded, b2_loaded = loaded.case.behavior_evaluations
    assert b1_loaded.judge_detail is None
    assert b1_loaded.judged_by == "deterministic"
    assert type(b2_loaded.judge_detail) is JudgeDetail
    assert b2_loaded.judge_detail.verdict == "CONTRADICTED"
    assert loaded.case.status == "FAIL"


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
