"""M10 Phase 4 — real fixture end-to-end test (Document 45 §20/§24, this
task's own "Real Fixture" requirement): load the real golden dataset (Phase
1), run the real Comparison Explanation adapter in FIXTURE mode (Phase 2, no
mocking of adapter/evaluation logic — only agents.llm._generate_sync is
stubbed, the same idiom every other Comparison Explanation test in this repo
already uses), evaluate it (Phase 3, unmodified), and confirm the resulting
artifact can participate in Phase 4's own baseline comparison. Isolated
tmp_path results dir throughout — never the real backend/evaluation/results/,
never a live provider.

    python -m pytest backend/tests/unit/test_evaluation_regression_fixture_e2e.py -v
"""
import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

import pytest  # noqa: E402

import agents.llm as llm  # noqa: E402
from agents.comparison_explanation import SCHEMA_VERSION  # noqa: E402
from evaluation.adapters import comparison_explanation  # noqa: E402
from evaluation.core.case_evaluator import evaluate_case  # noqa: E402
from evaluation.golden_dataset.loader import load_dataset  # noqa: E402
from evaluation.regression.compare import compare  # noqa: E402
from evaluation.regression.git_info import get_code_revision  # noqa: E402
from evaluation.regression.result_store import save_result  # noqa: E402
from evaluation.regression.types import EvaluationResult  # noqa: E402

_REAL_CASES_DIR = Path(__file__).resolve().parents[2] / "evaluation" / "golden_dataset" / "cases"
_FIXTURE_CASE_ID = "comparison_explanation_aapl_msft"


@pytest.fixture()
def stub_llm(monkeypatch):
    state = {"payload": None}

    def _generate_sync(system, user, model, usage_sink=None, temperature=None):
        return json.dumps(state["payload"])

    monkeypatch.setattr(llm, "_generate_sync", _generate_sync)

    def _set(payload: dict):
        state["payload"] = payload

    return _set


def _valid_payload():
    return {
        "narrative": "Fixture Co. B grew faster than Fixture Co. A [1].",
        "sources": [{"index": 1, "report_number": 2, "field": "extracted_data"}],
        "cited_source_indices": [1],
        "limitations": [],
    }


async def _run_and_record(case, results_dir: Path) -> EvaluationResult:
    adapter_result = await comparison_explanation.run(case, mode="fixture")
    case_result = await evaluate_case(case, adapter_result)
    verdict, reason = compare(case_result, schema_version=SCHEMA_VERSION, results_dir=results_dir)
    result = EvaluationResult(
        run_id=str(uuid.uuid4()), timestamp=datetime.now(timezone.utc).isoformat(),
        code_revision=get_code_revision(), schema_version=SCHEMA_VERSION,
        case=case_result, verdict=verdict, verdict_reason=reason,
    )
    save_result(result, results_dir=results_dir)
    return result


def test_real_seed_dataset_has_a_fixture_capable_comparison_explanation_case():
    # Phase 1: the real, shipped dataset (not a synthetic test fixture).
    cases = load_dataset(_REAL_CASES_DIR)
    case = next((c for c in cases if c.case_id == _FIXTURE_CASE_ID), None)
    assert case is not None
    assert case.surface == "comparison_explanation"
    assert isinstance(case.context.get("fixture_reports"), list)
    assert len(case.context["fixture_reports"]) >= 2


def test_full_pipeline_first_run_is_inconclusive_with_no_baseline(tmp_path, stub_llm):
    # Phase 1 -> Phase 2 -> Phase 3 -> Phase 4, real code throughout (only
    # the LLM call itself is stubbed).
    cases = load_dataset(_REAL_CASES_DIR)
    case = next(c for c in cases if c.case_id == _FIXTURE_CASE_ID)
    stub_llm(_valid_payload())

    result = asyncio.run(_run_and_record(case, tmp_path))

    assert result.case.mode == "fixture"
    assert result.case.status == "PASS"      # the real adapter + real evaluator agree the case passed
    assert result.verdict == "INCONCLUSIVE"  # but no prior baseline existed yet
    assert result.schema_version == SCHEMA_VERSION


def test_first_run_artifact_participates_in_second_run_baseline_comparison(tmp_path, stub_llm):
    # This is the CTO's explicit requirement: "verify the resulting artifact
    # can participate in baseline comparison" — proven by actually using
    # run 1's saved artifact as run 2's baseline, through the real
    # find_baseline/compare code path, not asserted by inspection alone.
    cases = load_dataset(_REAL_CASES_DIR)
    case = next(c for c in cases if c.case_id == _FIXTURE_CASE_ID)
    stub_llm(_valid_payload())

    first = asyncio.run(_run_and_record(case, tmp_path))
    assert first.verdict == "INCONCLUSIVE"

    second = asyncio.run(_run_and_record(case, tmp_path))
    assert second.verdict == "PASS"  # first run's PASS artifact was found and used as the baseline

    saved_files = list(tmp_path.glob(f"{_FIXTURE_CASE_ID}__*.json"))
    assert len(saved_files) == 2  # both runs' artifacts persisted


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
