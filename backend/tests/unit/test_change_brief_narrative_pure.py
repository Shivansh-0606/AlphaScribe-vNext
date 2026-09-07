"""Unit checks for agents/change_brief_narrative.py's pure per-item citation
validation and state determination (M15 / C-4, Document 70 R4 §8.3 / §12 /
§13 / §14.2; Document 73 R1 §10). No DB, no network, no LLM.

    python -m pytest backend/tests/unit/test_change_brief_narrative_pure.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.change_brief_narrative import (  # noqa: E402
    _has_evidence,
    build_prompt,
    validate_items,
)
from agents.comparison_explanation import build_evidence_payload  # noqa: E402
from agents.schemas import (  # noqa: E402
    ChangeBriefNarrativeItemSchema,
    ChangeBriefNarrativeLimitationSchema,
    ChangeBriefNarrativeSchema,
    ChangeBriefNarrativeSourceSchema,
)

BASE = {"id": "rb", "ticker": "AAPL", "company_name": "Apple",
        "extracted_data": {"guidance": "up"}, "sentiment_analysis": {}, "scorecard": {}}
CURR = {"id": "rc", "ticker": "AAPL", "company_name": "Apple",
        "extracted_data": {"guidance": "down"}, "sentiment_analysis": {}, "scorecard": {}}


def _item(summary, explanation, sources, cited):
    return ChangeBriefNarrativeItemSchema(
        summary=summary, explanation=explanation,
        sources=[ChangeBriefNarrativeSourceSchema(**s) for s in sources],
        cited_source_indices=cited,
    )


def _both_sided(summary="guidance cut"):
    return _item(
        summary, "guidance was up [1] and is now down [2]",
        [{"index": 1, "report_number": 1, "field": "extracted_data"},
         {"index": 2, "report_number": 2, "field": "extracted_data"}],
        [1, 2],
    )


def _one_sided():
    return _item(
        "only current mentions buybacks", "current adds a buyback programme [1]",
        [{"index": 1, "report_number": 2, "field": "extracted_data"}],
        [1],
    )


def _schema(items, limitations=None):
    return ChangeBriefNarrativeSchema(items=items, limitations=limitations or [])


# --- both-sides grounding --------------------------------------------------

def test_both_sided_item_is_kept_and_report_numbers_map_to_real_ids():
    out = validate_items(_schema([_both_sided()]), BASE, CURR)
    (item,) = out["items"]
    assert item["category"] == "narrative"
    ids = {s["report_id"] for s in item["sources"]}
    assert ids == {"rb", "rc"}  # 1 -> baseline id, 2 -> current id
    assert item["cited_source_indices"] == [1, 2]
    assert out["state"] == "complete" and out["coverage_boundaries"] == []


def test_one_sided_item_is_dropped_and_never_surfaces():
    out = validate_items(_schema([_both_sided(), _one_sided()]), BASE, CURR)
    assert [i["summary"] for i in out["items"]] == ["guidance cut"]
    assert out["state"] == "partial"  # a candidate was dropped for one-sidedness
    assert any("only one side" in b for b in out["coverage_boundaries"])


def test_all_candidates_dropped_is_insufficient_evidence():
    out = validate_items(_schema([_one_sided()]), BASE, CURR)
    assert out["items"] == [] and out["state"] == "insufficient_evidence"


def test_nothing_eligible_with_zero_candidates_is_complete_not_insufficient():
    out = validate_items(_schema([]), BASE, CURR)
    assert out["items"] == [] and out["state"] == "complete"
    assert out["coverage_boundaries"] == []


def test_zero_eligible_items_plus_model_limitation_is_partial_not_complete():
    """T-3 / M-1 regression: both reports carry valid evidence, the model
    produces zero eligible items but names a one-sided-evidence limitation
    (a candidate difference it could not corroborate on both sides). Per
    Document 70 R4 §14.2 `complete` requires that "none was left unresolved
    by an evidence gap" — so this must be `partial`, with the gap surfaced
    in `coverage_boundaries`, NOT `complete`."""
    lim = ChangeBriefNarrativeLimitationSchema(topic="new buyback programme", missing_side="baseline")
    out = validate_items(_schema([], [lim]), BASE, CURR)
    assert out["items"] == []
    assert out["state"] == "partial"
    assert len(out["coverage_boundaries"]) == 1
    assert "new buyback programme" in out["coverage_boundaries"][0]
    assert "baseline" in out["coverage_boundaries"][0]


# --- citation-integrity rejections (mirrors validate_and_map_citations) ---

def test_item_with_no_markers_is_dropped():
    bad = _item("x", "no citation markers at all",
                [{"index": 1, "report_number": 1, "field": "extracted_data"},
                 {"index": 2, "report_number": 2, "field": "extracted_data"}], [1, 2])
    out = validate_items(_schema([bad]), BASE, CURR)
    assert out["items"] == [] and out["state"] == "insufficient_evidence"


def test_item_citing_undeclared_index_is_dropped():
    bad = _item("x", "claim [3]",
                [{"index": 1, "report_number": 1, "field": "extracted_data"},
                 {"index": 2, "report_number": 2, "field": "extracted_data"}], [1, 2])
    out = validate_items(_schema([bad]), BASE, CURR)
    assert out["items"] == []


def test_item_with_marker_not_confirmed_in_cited_is_dropped():
    bad = _item("x", "up [1] down [2]",
                [{"index": 1, "report_number": 1, "field": "extracted_data"},
                 {"index": 2, "report_number": 2, "field": "extracted_data"}], [1])  # [2] not confirmed
    out = validate_items(_schema([bad]), BASE, CURR)
    assert out["items"] == []


def test_item_with_duplicate_declared_index_is_dropped():
    bad = _item("x", "claim [1] [2]",
                [{"index": 1, "report_number": 1, "field": "extracted_data"},
                 {"index": 1, "report_number": 2, "field": "extracted_data"},
                 {"index": 2, "report_number": 2, "field": "extracted_data"}], [1, 2])
    out = validate_items(_schema([bad]), BASE, CURR)
    assert out["items"] == []


def test_item_with_invalid_field_is_dropped():
    bad = _item("x", "up [1] down [2]",
                [{"index": 1, "report_number": 1, "field": "made_up_field"},
                 {"index": 2, "report_number": 2, "field": "extracted_data"}], [1, 2])
    out = validate_items(_schema([bad]), BASE, CURR)
    assert out["items"] == []


def test_item_with_out_of_range_report_number_is_dropped():
    bad = _item("x", "up [1] other [2]",
                [{"index": 1, "report_number": 1, "field": "extracted_data"},
                 {"index": 2, "report_number": 5, "field": "extracted_data"}], [1, 2])
    out = validate_items(_schema([bad]), BASE, CURR)
    assert out["items"] == []


# --- partial via model-named limitation ---------------------------------

def test_eligible_item_plus_model_limitation_is_partial():
    lim = ChangeBriefNarrativeLimitationSchema(topic="segment margins", missing_side="baseline")
    out = validate_items(_schema([_both_sided()], [lim]), BASE, CURR)
    assert out["state"] == "partial"
    assert any("segment margins" in b and "baseline" in b for b in out["coverage_boundaries"])


# --- missing-evidence gate --------------------------------------------

def test_has_evidence_helper_detects_an_empty_side():
    assert _has_evidence(BASE) is True
    assert _has_evidence({"id": "x", "extracted_data": {}, "sentiment_analysis": {}, "scorecard": {}}) is False
    assert _has_evidence({"id": "x", "sentiment_analysis": {"sentiment": "Bearish"}}) is True


def test_no_eligible_items_and_a_missing_side_is_insufficient_evidence():
    empty_current = {"id": "rc", "extracted_data": {}, "sentiment_analysis": {}, "scorecard": {}}
    out = validate_items(_schema([]), BASE, empty_current)
    assert out["items"] == [] and out["state"] == "insufficient_evidence"


# --- prompt shape ----------------------------------------------------

def test_build_prompt_carries_grounding_rules_and_evidence_payload():
    system, user = build_prompt(build_evidence_payload([BASE, CURR]))
    assert "report_number 1" in system and "report_number 2" in system
    assert "BOTH sides" in system or "both sides" in system.lower()
    assert '"report_number": 1' in user and '"report_number": 2' in user
    assert "draft_report" not in user  # bounded payload, never the full draft


def test_build_prompt_states_evidence_is_data_not_instructions():
    """L-2: the report content is untrusted DATA (Document 70 R4 §18;
    Document 73 R1 §19) — the system prompt must say so explicitly, matching
    the filing-analysis _SYSTEM_COMMON convention."""
    system, _ = build_prompt(build_evidence_payload([BASE, CURR]))
    lower = system.lower()
    assert "data" in lower and "never as instructions" in lower


# --- deterministic generation (L-3) --------------------------------------

def test_generate_passes_low_deterministic_temperature(monkeypatch):
    """L-3: `chat_json`'s per-provider default is not low (0.3 for
    OpenAI-compatible, provider default otherwise). This surface must pass an
    explicit low temperature, matching M14's `filing_analysis.generate_output`
    (temperature=0.2). The global `chat_json` default is not modified."""
    import asyncio

    import agents.change_brief_narrative as cbn

    captured = {}

    async def _fake_chat_json(system, user, schema, *, model=None, temperature=None):
        captured["model"] = model
        captured["temperature"] = temperature
        return ChangeBriefNarrativeSchema(items=[])

    monkeypatch.setattr(cbn, "chat_json", _fake_chat_json)
    out = asyncio.run(cbn.generate_change_brief_narrative(BASE, CURR))
    assert captured["temperature"] == 0.2
    assert captured["model"] == cbn.DEFAULT_LIGHT_MODEL
    # envelope still assembled around the (stubbed) result
    assert out["prompt_version"] == cbn.PROMPT_VERSION
    assert out["state"] == "complete" and out["items"] == []


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
