"""Unit check for evaluation/adapters/learning.py (M10 Phase 2).

Mocks server.learning_graph.ainvoke — the same compiled singleton
`_run_explanation` calls — for the same reason test_evaluation_adapter_
research.py mocks server.graph.ainvoke: this tests the adapter's own
translate/normalize/error-boundary responsibility, not node internals
(already covered by tests/unit/test_learning_nodes.py, test_learning_graph.py).

    python -m pytest backend/tests/unit/test_evaluation_adapter_learning.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

import pytest  # noqa: E402

import server  # noqa: E402
from evaluation.adapters import learning  # noqa: E402
from evaluation.adapters.types import (  # noqa: E402
    AdapterInvocationError,
    MalformedAIOutputError,
    UnsupportedExecutionModeError,
)
from evaluation.golden_dataset.models import BenchmarkCase  # noqa: E402

_CASE_PAYLOAD = {
    "case_id": "learning_seed",
    "surface": "learning",
    "dataset_version": 1,
    "case_version": 1,
    "context": {"ticker": "msft", "concept": "operating margin"},
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
        if error is not None:
            raise error
        return result

    monkeypatch.setattr(server.learning_graph, "ainvoke", fake_ainvoke)
    return captured


def test_translates_case_and_delegates_to_existing_graph_singleton(monkeypatch):
    captured = _patch_ainvoke(monkeypatch, result={
        "source_documents": [], "explanation": "Margin means [1].", "cited_sources": [1],
    })
    import asyncio
    result = asyncio.run(learning.run(_case()))
    assert captured["state"]["ticker"] == "MSFT"
    assert captured["state"]["concept"] == "operating margin"
    assert result.case_id == "learning_seed"
    assert result.surface == "learning"


def test_grounded_when_explanation_and_citations_present(monkeypatch):
    _patch_ainvoke(monkeypatch, result={
        "source_documents": [{"source": "10-Q"}],
        "explanation": "Margin means profit relative to revenue [1].",
        "cited_sources": [1],
    })
    import asyncio
    result = asyncio.run(learning.run(_case()))
    assert result.output.grounding_verdict == "grounded"
    assert result.output.citations[0].referenced is True


def test_error_when_explanation_empty(monkeypatch):
    # explainer_node's own two failure paths (LLM error, zero-citation-reject)
    # both return this shape.
    _patch_ainvoke(monkeypatch, result={"source_documents": [], "explanation": "", "cited_sources": []})
    import asyncio
    result = asyncio.run(learning.run(_case()))
    assert result.output.grounding_verdict == "error"


def test_failure_propagation_wraps_ainvoke_exception(monkeypatch):
    _patch_ainvoke(monkeypatch, error=RuntimeError("boom"))
    import asyncio
    with pytest.raises(AdapterInvocationError):
        asyncio.run(learning.run(_case()))


def test_malformed_final_state_raises(monkeypatch):
    _patch_ainvoke(monkeypatch, result=None)
    import asyncio
    with pytest.raises(MalformedAIOutputError):
        asyncio.run(learning.run(_case()))


def test_fixture_mode_not_supported_yet(monkeypatch):
    import asyncio
    with pytest.raises(UnsupportedExecutionModeError):
        asyncio.run(learning.run(_case(), mode="fixture"))


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
