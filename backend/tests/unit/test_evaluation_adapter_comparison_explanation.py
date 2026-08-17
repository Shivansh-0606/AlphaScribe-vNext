"""Unit check for evaluation/adapters/comparison_explanation.py (M10 Phase 2).

Reuses the exact stub idioms tests/unit/test_comparison_explanation_execution.py
already established: `agents.llm._generate_sync` is the one LLM stub point
(no mocked graph/function needed for FIXTURE mode — the REAL
generate_explanation runs, proving this adapter delegates rather than
reimplements it), and a minimal fake `db.reports` for LIVE mode's
`_resolve_authorized_reports` delegation. No live provider, no live Mongo.

    python -m pytest backend/tests/unit/test_evaluation_adapter_comparison_explanation.py -v
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

import pytest  # noqa: E402

import agents.llm as llm  # noqa: E402
import server  # noqa: E402
from evaluation.adapters import comparison_explanation as adapter  # noqa: E402
from evaluation.adapters.types import (  # noqa: E402
    AdapterInvocationError,
    InvalidBenchmarkInputError,
    ProviderExecutionError,
)
from evaluation.golden_dataset.models import BenchmarkCase  # noqa: E402

_CASE_PAYLOAD = {
    "case_id": "comparison_seed",
    "surface": "comparison_explanation",
    "dataset_version": 1,
    "case_version": 1,
    "context": {"report_ids": ["r1", "r2"]},
    "expected_behaviors": [
        {"behavior_id": "b1", "type": "presence", "description": "d",
         "match_rule": "keyword_variant", "variants": ["x"]},
    ],
    "citation_expectation": {},
}


def _case(**overrides) -> BenchmarkCase:
    payload = dict(_CASE_PAYLOAD)
    payload.update(overrides)
    return BenchmarkCase.model_validate(payload)


def _report(rid: str, **fields) -> dict:
    return {
        "id": rid, "ticker": rid.upper(), "is_sample": True,
        "extracted_data": {"revenue": "$1B"}, "sentiment_analysis": {}, "scorecard": {},
        **fields,
    }


def _valid_payload(*, limitations=None):
    return {
        "narrative": "R1 has higher revenue than R2 [1].",
        "sources": [{"index": 1, "report_number": 1, "field": "extracted_data"}],
        "cited_source_indices": [1],
        "limitations": limitations or [],
    }


def _payload_citing_field(*, report_number: int, field: str, limitations=None):
    return {
        "narrative": "A claim about the company [1].",
        "sources": [{"index": 1, "report_number": report_number, "field": field}],
        "cited_source_indices": [1],
        "limitations": limitations or [],
    }


@pytest.fixture()
def stub_llm(monkeypatch):
    # Same idiom as tests/unit/test_comparison_explanation_execution.py's own
    # stub_llm fixture — the one LLM stub point in this codebase.
    state = {"text": None}

    def _generate_sync(system, user, model, usage_sink=None):
        if state["text"] is None:
            raise AssertionError("stub_llm() was not configured with a response")
        return state["text"]

    monkeypatch.setattr(llm, "_generate_sync", _generate_sync)

    def _set(payload):
        state["text"] = payload if isinstance(payload, str) else json.dumps(payload)

    return _set


def _match(doc, filt):
    for k, v in filt.items():
        if k == "$or":
            if not any(_match(doc, sub) for sub in v):
                return False
            continue
        if isinstance(v, dict) and "$in" in v:
            if doc.get(k) not in v["$in"]:
                return False
            continue
        if doc.get(k) != v:
            return False
    return True


class _FakeCursor:
    def __init__(self, docs):
        self._docs = docs

    async def to_list(self, n):
        return self._docs[:n]


class _FakeReportsCollection:
    def __init__(self, docs):
        self._docs = docs

    def find(self, filt, projection=None):
        return _FakeCursor([dict(d) for d in self._docs if _match(d, filt)])


class _FakeDB:
    def __init__(self, report_docs):
        self.reports = _FakeReportsCollection(report_docs)


@pytest.fixture()
def fake_db(monkeypatch):
    def _install(report_docs):
        db = _FakeDB(report_docs)
        monkeypatch.setattr(server, "db", db)
        return db
    return _install


# --- FIXTURE mode: real generate_explanation, no Mongo -----------------------

def test_fixture_mode_runs_the_real_generate_explanation(stub_llm):
    stub_llm(_valid_payload())
    case = _case(context={"report_ids": ["r1", "r2"], "fixture_reports": [_report("r1"), _report("r2")]})
    result = asyncio.run(adapter.run(case, mode="fixture"))
    assert result.mode == "fixture"
    assert result.output.grounding_verdict == "grounded"
    assert result.output.text == "R1 has higher revenue than R2 [1]."
    cited = [c for c in result.output.citations if c.valid]
    assert cited and cited[0].source_id == "r1:extracted_data"
    # Positive case (Reviewer 2 regression): a populated citation field
    # (extracted_data is non-empty in _report()) must be reported eligible.
    assert cited[0].eligible is True


def test_citation_of_empty_field_is_not_eligible_but_is_referenced_and_valid(stub_llm):
    # Reviewer 2 regression: `eligible` must reflect actual field presence
    # (Document 45 §13's "available as citable evidence"), independent of
    # whether the model cited it. r1's sentiment_analysis is empty ({}) in
    # _report() by default. The model cites it anyway;
    # validate_and_map_citations accepts this structurally (it only checks
    # report_number range + field name, never field content), so the citation
    # legitimately reaches _normalize as referenced+valid — but it must NOT
    # be reported as eligible, since no sentiment_analysis evidence actually
    # existed to offer the model. Exercises the real adapter normalization
    # path, not a mock of it.
    stub_llm(_payload_citing_field(report_number=1, field="sentiment_analysis"))
    case = _case(context={"report_ids": ["r1", "r2"], "fixture_reports": [_report("r1"), _report("r2")]})
    result = asyncio.run(adapter.run(case, mode="fixture"))
    assert result.output.grounding_verdict == "grounded"  # structurally valid, not a GroundingError

    empty_field_citation = next(
        c for c in result.output.citations if c.source_id == "r1:sentiment_analysis"
    )
    assert empty_field_citation.eligible is False
    assert empty_field_citation.referenced is True
    assert empty_field_citation.valid is True


def test_fixture_mode_without_fixture_reports_raises_invalid_input():
    case = _case()  # no fixture_reports in context
    with pytest.raises(InvalidBenchmarkInputError):
        asyncio.run(adapter.run(case, mode="fixture"))


def test_fixture_mode_grounding_error_maps_to_ungrounded_not_raised(stub_llm):
    stub_llm(_valid_payload() | {"cited_source_indices": []})  # zero-citation-reject
    case = _case(context={"report_ids": ["r1", "r2"], "fixture_reports": [_report("r1"), _report("r2")]})
    result = asyncio.run(adapter.run(case, mode="fixture"))
    assert result.output.grounding_verdict == "ungrounded"


def test_fixture_mode_other_failure_raises_provider_execution_error(stub_llm):
    stub_llm("this is not json at all { garbage")
    case = _case(context={"report_ids": ["r1", "r2"], "fixture_reports": [_report("r1"), _report("r2")]})
    with pytest.raises(ProviderExecutionError):
        asyncio.run(adapter.run(case, mode="fixture"))


# --- LIVE mode: delegates to server._resolve_authorized_reports --------------

def test_live_mode_delegates_to_existing_report_resolution(fake_db, stub_llm):
    fake_db([_report("r1"), _report("r2")])
    stub_llm(_valid_payload())
    result = asyncio.run(adapter.run(_case(), mode="live"))
    assert result.mode == "live"
    assert result.output.grounding_verdict == "grounded"


def test_live_mode_insufficient_resolved_reports_raises_invalid_input(fake_db):
    fake_db([_report("r1")])  # only one of the two requested ids exists
    with pytest.raises(InvalidBenchmarkInputError):
        asyncio.run(adapter.run(_case(), mode="live"))


def test_live_mode_resolution_failure_wrapped_as_adapter_invocation_error(monkeypatch):
    async def _boom(report_ids, user_id):
        raise RuntimeError("mongo down")

    monkeypatch.setattr(server, "_resolve_authorized_reports", _boom)
    with pytest.raises(AdapterInvocationError):
        asyncio.run(adapter.run(_case(), mode="live"))


def test_too_few_report_ids_rejected_before_any_resolution():
    case = _case(context={"report_ids": ["r1"]})
    with pytest.raises(InvalidBenchmarkInputError):
        asyncio.run(adapter.run(case, mode="fixture"))


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
