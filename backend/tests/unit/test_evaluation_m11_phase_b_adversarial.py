"""M11 Phase B — adversarial deterministic case (Document 47 Sec19 step 2,
Sec5-B, Sec7.4). Zero new evaluator code: this exercises the shipped
`comparison_explanation_aapl_msft_adversarial_growth.json` case through the
REAL, unmodified M10 Phase 2 adapter (FIXTURE mode) and Phase 3 evaluator
(`evaluate_case`) — proving the pre-existing `keyword_variant`(absence)
mechanism, combined with adversarially-authored fixture content, correctly
distinguishes a "tricked" (inverted) narrative from a correct one, fully
deterministically. No LLM/provider call: the same one stub point
`tests/unit/test_evaluation_adapter_comparison_explanation.py` already
established (`agents.llm._generate_sync`) is reused, not reinvented.

    python -m pytest backend/tests/unit/test_evaluation_m11_phase_b_adversarial.py -v
"""
import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

import pytest  # noqa: E402

import agents.llm as llm  # noqa: E402
import server  # noqa: E402
from evaluation.adapters import comparison_explanation as adapter  # noqa: E402
from evaluation.core.case_evaluator import evaluate_case  # noqa: E402
from evaluation.golden_dataset.loader import load_dataset  # noqa: E402

_CASE_ID = "comparison_explanation_aapl_msft_adversarial_growth"
_CASES_DIR = Path(__file__).resolve().parents[2] / "evaluation" / "golden_dataset" / "cases"


def _load_case():
    cases = load_dataset(_CASES_DIR)
    matches = [c for c in cases if c.case_id == _CASE_ID]
    assert len(matches) == 1, f"expected exactly one {_CASE_ID!r} case, found {len(matches)}"
    return matches[0]


@pytest.fixture()
def stub_llm(monkeypatch):
    # Same idiom as test_evaluation_adapter_comparison_explanation.py's own
    # stub_llm fixture — the one LLM stub point in this codebase. Tracks
    # call count too, so tests can confirm zero *additional*, unstubbed
    # provider access occurred beyond this single interception point.
    state = {"text": None, "calls": 0}

    def _generate_sync(system, user, model, usage_sink=None, temperature=None):
        state["calls"] += 1
        if state["text"] is None:
            raise AssertionError("stub_llm() was not configured with a response")
        return state["text"]

    monkeypatch.setattr(llm, "_generate_sync", _generate_sync)

    def _set(payload):
        state["text"] = payload if isinstance(payload, str) else json.dumps(payload)

    _set.calls = lambda: state["calls"]
    return _set


def _tricked_payload():
    # The adversarial trap: inverts the fixture's actual growth relationship
    # (MSFT +9% > AAPL +4%) into a claim that Apple grew faster.
    return {
        "narrative": "Apple grew faster than Microsoft this quarter [1].",
        "sources": [{"index": 1, "report_number": 1, "field": "extracted_data"}],
        "cited_source_indices": [1],
        "limitations": [],
    }


def _correct_payload():
    # Correctly reflects the fixture: Microsoft's growth rate exceeds Apple's.
    return {
        "narrative": "Microsoft grew faster than Apple this quarter [1].",
        "sources": [{"index": 1, "report_number": 2, "field": "extracted_data"}],
        "cited_source_indices": [1],
        "limitations": [],
    }


def _behavior_status(case_result, behavior_id: str) -> str:
    matches = [b for b in case_result.behavior_evaluations if b.behavior_id == behavior_id]
    assert len(matches) == 1
    return matches[0].status


async def _run_and_evaluate(case):
    # M11 Phase C: evaluate_case is now async (Document 47 §7.2's judge
    # call) — combined into one coroutine so each test needs only one
    # asyncio.run(), same as before this phase.
    result = await adapter.run(case, mode="fixture")
    return await evaluate_case(case, result)


# ---------------------------------------------------------------------------
# Catches the adversarial trap: an inverted narrative must FAIL
# ---------------------------------------------------------------------------

def test_tricked_narrative_fails_the_adversarial_behavior(stub_llm):
    case = _load_case()
    stub_llm(_tricked_payload())
    case_result = asyncio.run(_run_and_evaluate(case))
    assert _behavior_status(case_result, "does_not_invert_growth_comparison") == "FAIL"
    assert case_result.status == "FAIL"


# ---------------------------------------------------------------------------
# A correct narrative passes — this is not a "reject everything" trap
# ---------------------------------------------------------------------------

def test_correct_narrative_passes_the_adversarial_behavior(stub_llm):
    case = _load_case()
    stub_llm(_correct_payload())
    case_result = asyncio.run(_run_and_evaluate(case))
    assert _behavior_status(case_result, "does_not_invert_growth_comparison") == "PASS"
    assert case_result.status == "PASS"


# ---------------------------------------------------------------------------
# Determinism: identical input -> identical result, every time
# ---------------------------------------------------------------------------

def test_repeated_evaluation_is_deterministic(stub_llm):
    case = _load_case()
    stub_llm(_tricked_payload())

    result_1 = asyncio.run(_run_and_evaluate(case))
    result_2 = asyncio.run(_run_and_evaluate(case))

    assert result_1.status == result_2.status == "FAIL"
    assert result_1.behavior_evaluations == result_2.behavior_evaluations
    assert result_1.metrics == result_2.metrics


# ---------------------------------------------------------------------------
# No LLM/provider call occurs outside the one stubbed interception point
# ---------------------------------------------------------------------------

def test_no_unstubbed_provider_access_occurs(stub_llm):
    case = _load_case()
    stub_llm(_correct_payload())  # stub_llm IS the setter; calling it configures the payload
    asyncio.run(adapter.run(case, mode="fixture"))
    # generate_explanation makes exactly one chat_json call per run — if the
    # adapter, the evaluator, or anything Document 47's new mechanism touches
    # ever bypassed the stub, this count (or the test itself) would not hold.
    assert stub_llm.calls() == 1


# ---------------------------------------------------------------------------
# Comparison Explanation-specific citation identity (Document 47 Sec7.0 Revision
# 4): Citation.source_id here is f"{report_id}:{field_name}", NOT a positional
# index, and NOT the narrative's own [n] marker number — confirmed unaffected
# by this new case, since keyword_variant never touches source_id at all.
# ---------------------------------------------------------------------------

def test_new_case_citations_use_comparison_explanation_report_id_field_identity(stub_llm):
    case = _load_case()
    stub_llm(_correct_payload())
    result = asyncio.run(adapter.run(case, mode="fixture"))
    source_ids = {c.source_id for c in result.output.citations}
    # Confirms adapter behavior directly rather than assuming it: every
    # source_id is "<report_id>:<field>", never a bare index like "1"/"2".
    assert all(":" in sid for sid in source_ids), source_ids
    assert any(sid.startswith("seed-report-aapl-002:") for sid in source_ids)
    assert any(sid.startswith("seed-report-msft-002:") for sid in source_ids)


# ---------------------------------------------------------------------------
# Regression compatibility with M10: the new case doesn't disturb the
# existing seed dataset's own loader-level invariants.
# ---------------------------------------------------------------------------

def test_new_case_does_not_change_the_seed_dataset_match_rule_set():
    cases = load_dataset(_CASES_DIR)
    assert len(cases) == 4
    match_rules = {b.match_rule for c in cases for b in c.expected_behaviors}
    assert match_rules == {"keyword_variant", "citation_required", "limitation_reference"}


def test_existing_seed_case_untouched():
    cases = load_dataset(_CASES_DIR)
    original = next(c for c in cases if c.case_id == "comparison_explanation_aapl_msft")
    assert original.case_version == 1
    assert [b.behavior_id for b in original.expected_behaviors] == [
        "no_buy_sell_recommendation", "cites_comparison_metric",
    ]


if __name__ == "__main__":
    print("This test file uses pytest fixtures (stub_llm) — run via pytest, not as a standalone script:")
    print("  python -m pytest backend/tests/unit/test_evaluation_m11_phase_b_adversarial.py -v")
