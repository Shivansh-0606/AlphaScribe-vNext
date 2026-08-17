"""Unit check for backend/scripts/run_evaluation.py (M10 Phase 4).

Two techniques, chosen per what each test needs:
- Argument-validation paths that never touch an LLM: real subprocess
  invocation (`subprocess.run`), exactly how a user actually runs the CLI.
- Paths that exercise a real (fixture-mode) evaluation run: the script is
  loaded in-process via importlib so `agents.llm._generate_sync` can be
  monkeypatched (the same stub point tests/unit/test_comparison_explanation_
  execution.py already established) — a real subprocess has no way to reach
  an in-process monkeypatch. `main()` is called directly with `sys.argv`
  patched; `SystemExit` is caught to inspect the exit code.

All runs use an isolated `--results-dir tmp_path` — never the real
backend/evaluation/results/. No live provider is ever called.

    python -m pytest backend/tests/unit/test_evaluation_regression_cli.py -v
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

import pytest  # noqa: E402

import agents.llm as llm  # noqa: E402

_SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "run_evaluation.py"
_FIXTURE_CASE_ID = "comparison_explanation_aapl_msft"

_spec = importlib.util.spec_from_file_location("_run_evaluation_cli", _SCRIPT_PATH)
run_evaluation = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(run_evaluation)


def _valid_payload():
    return {
        "narrative": "Fixture Co. B grew faster than Fixture Co. A [1].",
        "sources": [{"index": 1, "report_number": 2, "field": "extracted_data"}],
        "cited_source_indices": [1],
        "limitations": [],
    }


def _forbidden_recommendation_payload():
    # Fails the seed case's own no_buy_sell_recommendation (absence) behavior.
    return {
        "narrative": "You should buy Fixture Co. B over Fixture Co. A [1].",
        "sources": [{"index": 1, "report_number": 2, "field": "extracted_data"}],
        "cited_source_indices": [1],
        "limitations": [],
    }


@pytest.fixture()
def stub_llm(monkeypatch):
    state = {"payload": None}

    def _generate_sync(system, user, model, usage_sink=None):
        return json.dumps(state["payload"])

    monkeypatch.setattr(llm, "_generate_sync", _generate_sync)

    def _set(payload: dict):
        state["payload"] = payload

    return _set


def _run_main(monkeypatch, argv: list[str]) -> int:
    monkeypatch.setattr(sys, "argv", ["run_evaluation.py", *argv])
    with pytest.raises(SystemExit) as exc:
        run_evaluation.main()
    return exc.value.code


# --- Argument validation (real subprocess — no LLM involved) ---------------

def test_help_flag_exits_zero():
    result = subprocess.run(
        [sys.executable, str(_SCRIPT_PATH), "--help"], capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0
    assert "--mode" in result.stdout


def test_invalid_dataset_dir_exits_2(tmp_path):
    empty_dir = tmp_path / "empty_dataset"
    empty_dir.mkdir()
    result = subprocess.run(
        [sys.executable, str(_SCRIPT_PATH), "--dataset-dir", str(empty_dir)],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 2
    assert "dataset error" in result.stderr


def test_unknown_case_id_exits_2():
    result = subprocess.run(
        [sys.executable, str(_SCRIPT_PATH), "--case-id", "does_not_exist"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 2
    assert "unknown case_id" in result.stderr


def test_invalid_mode_choice_exits_2():
    result = subprocess.run(
        [sys.executable, str(_SCRIPT_PATH), "--mode", "not_a_real_mode"],
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 2  # argparse's own invalid-choice exit code


# --- Real (fixture-mode) evaluation runs (in-process, stubbed LLM) ---------

def test_successful_fixture_run_exits_zero_and_prints_text(tmp_path, stub_llm, monkeypatch, capsys):
    stub_llm(_valid_payload())
    code = _run_main(monkeypatch, [
        "--mode", "fixture", "--case-id", _FIXTURE_CASE_ID, "--results-dir", str(tmp_path),
    ])
    out = capsys.readouterr().out
    assert code == 0
    assert "INCONCLUSIVE" in out  # first-ever run: no baseline yet
    assert _FIXTURE_CASE_ID in out


def test_second_run_against_saved_baseline_is_pass(tmp_path, stub_llm, monkeypatch, capsys):
    stub_llm(_valid_payload())
    _run_main(monkeypatch, ["--mode", "fixture", "--case-id", _FIXTURE_CASE_ID, "--results-dir", str(tmp_path)])
    capsys.readouterr()  # discard first run's output

    code = _run_main(monkeypatch, ["--mode", "fixture", "--case-id", _FIXTURE_CASE_ID, "--results-dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "PASS" in out
    assert "REGRESSION" not in out


def test_regression_detected_exits_one(tmp_path, stub_llm, monkeypatch, capsys):
    stub_llm(_valid_payload())
    _run_main(monkeypatch, ["--mode", "fixture", "--case-id", _FIXTURE_CASE_ID, "--results-dir", str(tmp_path)])
    capsys.readouterr()

    stub_llm(_forbidden_recommendation_payload())  # now fails no_buy_sell_recommendation
    code = _run_main(monkeypatch, ["--mode", "fixture", "--case-id", _FIXTURE_CASE_ID, "--results-dir", str(tmp_path)])
    out = capsys.readouterr().out
    assert code == 1
    assert "REGRESSION" in out


def test_incompatible_baseline_dataset_version_reports_inconclusive(tmp_path, stub_llm, monkeypatch):
    from evaluation.adapters.types import ExecutionMetadata
    from evaluation.core.types import CaseEvaluationResult, MetricResult
    from evaluation.regression.result_store import save_result
    from evaluation.regression.types import EvaluationResult

    # Seed a baseline under a different dataset_version — Document 46 §5's
    # compatibility key must exclude it.
    stale = CaseEvaluationResult(
        case_id=_FIXTURE_CASE_ID, surface="comparison_explanation", dataset_version=999, case_version=1,
        mode="fixture", evaluation_version="v1", execution=ExecutionMetadata(provider="p", model="m"),
        behavior_evaluations=[], metrics=[], status="PASS", failure_reasons=[],
    )
    save_result(
        EvaluationResult(run_id="stale-run", timestamp="2020-01-01T00:00:00+00:00", code_revision="x",
                          schema_version="v1", case=stale, verdict="PASS", verdict_reason="ok"),
        results_dir=tmp_path,
    )

    stub_llm(_valid_payload())
    code = _run_main(monkeypatch, ["--mode", "fixture", "--case-id", _FIXTURE_CASE_ID, "--results-dir", str(tmp_path)])
    assert code == 0  # INCONCLUSIVE is not a failure exit code


def test_json_output_format(tmp_path, stub_llm, monkeypatch, capsys):
    stub_llm(_valid_payload())
    _run_main(monkeypatch, [
        "--mode", "fixture", "--case-id", _FIXTURE_CASE_ID, "--results-dir", str(tmp_path), "--format", "json",
    ])
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert isinstance(payload, list) and len(payload) == 1
    assert payload[0]["case"]["case_id"] == _FIXTURE_CASE_ID
    assert payload[0]["verdict"] == "INCONCLUSIVE"


if __name__ == "__main__":
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
