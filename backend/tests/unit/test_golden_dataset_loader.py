"""Unit check for evaluation/golden_dataset/loader.py's load_dataset (M10
Phase 1, Document 45 §7, §9). Uses isolated tmp_path directories only — never
touches the shipped seed dataset except in the one sanity test at the bottom.

    python backend/tests/unit/test_golden_dataset_loader.py
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest

from evaluation.golden_dataset.loader import DatasetIntegrityError, load_dataset

_VALID_CASE = {
    "case_id": "c1",
    "surface": "research",
    "dataset_version": 1,
    "case_version": 1,
    "context": {"ticker": "AAPL", "query": "q"},
    "expected_behaviors": [
        {"behavior_id": "b1", "type": "presence", "description": "d",
         "match_rule": "keyword_variant", "variants": ["x"]},
    ],
    "citation_expectation": {},
}


def _write(dir_: Path, filename: str, payload) -> Path:
    path = dir_ / filename
    if isinstance(payload, str):
        path.write_text(payload, encoding="utf-8")
    else:
        path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _case(case_id: str, **overrides) -> dict:
    payload = dict(_VALID_CASE)
    payload.update(overrides)
    payload["case_id"] = case_id
    return payload


def test_valid_dataset_returns_typed_cases(tmp_path):
    _write(tmp_path, "c1.json", _case("c1"))
    cases = load_dataset(tmp_path)
    assert len(cases) == 1
    assert cases[0].case_id == "c1"
    assert cases[0].surface == "research"


def test_multiple_valid_cases_all_returned(tmp_path):
    _write(tmp_path, "c1.json", _case("c1"))
    _write(tmp_path, "c2.json", _case("c2", surface="learning",
                                       context={"ticker": "MSFT", "concept": "margin"}))
    _write(tmp_path, "c3.json", _case("c3", surface="comparison_explanation",
                                       context={"report_ids": ["r1", "r2"]}))
    cases = load_dataset(tmp_path)
    assert {c.case_id for c in cases} == {"c1", "c2", "c3"}
    assert {c.surface for c in cases} == {"research", "learning", "comparison_explanation"}


def test_malformed_json_reported_with_file_path(tmp_path):
    bad = _write(tmp_path, "broken.json", "{not valid json")
    with pytest.raises(DatasetIntegrityError) as exc:
        load_dataset(tmp_path)
    assert str(bad) in exc.value.errors
    assert "invalid JSON" in exc.value.errors[str(bad)]


def test_schema_validation_failure_reported_with_file_path(tmp_path):
    bad = _write(tmp_path, "bad_schema.json", _case("bad_schema", expected_behaviors=[]))
    with pytest.raises(DatasetIntegrityError) as exc:
        load_dataset(tmp_path)
    assert str(bad) in exc.value.errors
    assert "schema validation failed" in exc.value.errors[str(bad)]


def test_unsupported_surface_reported(tmp_path):
    bad = _write(tmp_path, "bad_surface.json", _case("bad_surface", surface="not_a_real_surface"))
    with pytest.raises(DatasetIntegrityError) as exc:
        load_dataset(tmp_path)
    assert "schema validation failed" in exc.value.errors[str(bad)]


def test_duplicate_case_id_across_files_reported(tmp_path):
    _write(tmp_path, "aaa_first.json", _case("dup"))
    second = _write(tmp_path, "bbb_second.json", _case("dup"))
    with pytest.raises(DatasetIntegrityError) as exc:
        load_dataset(tmp_path)
    # Files are processed in sorted order — "aaa_first.json" loads clean and
    # is the one recorded in seen_ids; "bbb_second.json" is the one reported.
    assert str(second) in exc.value.errors
    assert "duplicate case_id" in exc.value.errors[str(second)]


def test_empty_dataset_directory_reported(tmp_path):
    with pytest.raises(DatasetIntegrityError) as exc:
        load_dataset(tmp_path)
    assert "no benchmark case files found" in str(exc.value)


def test_all_problems_collected_in_one_pass(tmp_path):
    _write(tmp_path, "good.json", _case("good"))
    _write(tmp_path, "broken.json", "{not json")
    _write(tmp_path, "bad_schema.json", _case("bad_schema", expected_behaviors=[]))
    with pytest.raises(DatasetIntegrityError) as exc:
        load_dataset(tmp_path)
    # One exception, two distinct problem files reported — the valid file is
    # not silently returned alongside a partial failure.
    assert len(exc.value.errors) == 2


def test_seed_dataset_loads_successfully():
    # The shipped M10 Phase 1 seed cases (Document 45 §9's real directory) —
    # a sanity check that what ships actually loads, still fully hermetic
    # (file I/O + Pydantic only, no AI/Mongo call).
    cases_dir = Path(__file__).resolve().parents[2] / "evaluation" / "golden_dataset" / "cases"
    cases = load_dataset(cases_dir)
    assert len(cases) >= 3
    surfaces = {c.surface for c in cases}
    assert surfaces == {"research", "learning", "comparison_explanation"}
    match_rules = {b.match_rule for c in cases for b in c.expected_behaviors}
    assert match_rules == {"keyword_variant", "citation_required", "limitation_reference"}


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
