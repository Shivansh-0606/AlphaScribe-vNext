"""Unit check for evaluation/adapters/research.py (M10 Phase 2).

Mocks server.graph.ainvoke — the same compiled singleton `_run_pipeline`
calls — so these tests are about the ADAPTER's own translate/normalize/
error-boundary responsibility, not the graph's internal node behavior
(already covered by tests/unit/test_nodes_pure.py and friends). No live
provider, no live Mongo.

    python -m pytest backend/tests/unit/test_evaluation_adapter_research.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

import pytest  # noqa: E402

import server  # noqa: E402
from evaluation.adapters import research  # noqa: E402
from evaluation.adapters.types import (  # noqa: E402
    AdapterInvocationError,
    MalformedAIOutputError,
    UnsupportedExecutionModeError,
)
from evaluation.golden_dataset.models import BenchmarkCase  # noqa: E402

_CASE_PAYLOAD = {
    "case_id": "research_seed",
    "surface": "research",
    "dataset_version": 1,
    "case_version": 1,
    "context": {"ticker": "aapl", "query": "How did revenue perform?"},
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


def _patch_ainvoke(monkeypatch, result=None, *, error=None):
    captured = {}

    async def fake_ainvoke(initial_state, config=None):
        captured["state"] = initial_state
        captured["config"] = config
        if error is not None:
            raise error
        return result

    monkeypatch.setattr(server.graph, "ainvoke", fake_ainvoke)
    return captured


def test_translates_case_and_delegates_to_existing_graph_singleton(monkeypatch):
    captured = _patch_ainvoke(monkeypatch, result={
        "source_documents": [], "draft_report": "brief [1]",
        "fact_check_status": True, "verified_claims": [],
    })
    import asyncio
    result = asyncio.run(research.run(_case()))
    # Delegation proof: the adapter never reimplements Research — the only
    # way `captured["state"]` gets populated is via server.graph.ainvoke.
    assert captured["state"]["ticker"] == "AAPL"
    assert captured["state"]["query"] == "How did revenue perform?"
    assert result.case_id == "research_seed"
    assert result.surface == "research"
    assert result.mode == "live"


def test_grounded_when_fact_check_passes_with_citation(monkeypatch):
    _patch_ainvoke(monkeypatch, result={
        "source_documents": [{"source": "10-Q"}],
        "draft_report": "Revenue grew [1].",
        "fact_check_status": True,
        "verified_claims": [],
    })
    import asyncio
    result = asyncio.run(research.run(_case()))
    assert result.output.grounding_verdict == "grounded"
    assert result.output.citations[0].valid is True


def test_error_when_draft_empty(monkeypatch):
    _patch_ainvoke(monkeypatch, result={
        "source_documents": [], "draft_report": "", "fact_check_status": False, "verified_claims": [],
    })
    import asyncio
    result = asyncio.run(research.run(_case()))
    assert result.output.grounding_verdict == "error"


def test_ungrounded_when_fact_check_failed(monkeypatch):
    _patch_ainvoke(monkeypatch, result={
        "source_documents": [{"source": "10-Q"}],
        "draft_report": "Revenue grew [1].",
        "fact_check_status": False,
        "verified_claims": [{"claim": "x", "supported": False, "reason": "no evidence"}],
    })
    import asyncio
    result = asyncio.run(research.run(_case()))
    assert result.output.grounding_verdict == "ungrounded"
    assert result.output.limitations_stated == ["x"]


def test_failure_propagation_wraps_ainvoke_exception(monkeypatch):
    _patch_ainvoke(monkeypatch, error=RuntimeError("boom"))
    import asyncio
    with pytest.raises(AdapterInvocationError):
        asyncio.run(research.run(_case()))


def test_malformed_final_state_raises(monkeypatch):
    _patch_ainvoke(monkeypatch, result=None)  # ainvoke returning None is not a usable final state
    import asyncio
    with pytest.raises(MalformedAIOutputError):
        asyncio.run(research.run(_case()))


def test_fixture_mode_not_supported_yet(monkeypatch):
    import asyncio
    with pytest.raises(UnsupportedExecutionModeError):
        asyncio.run(research.run(_case(), mode="fixture"))


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
