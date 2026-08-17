"""Unit checks for agents/comparison_explanation.py's pure grounding logic
(M9.1, Document 43 §9-§10). No DB, no network — the same hermetic style as
test_scoring.py/test_llm_json_repair.py.

    python -m pytest backend/tests/unit/test_comparison_explanation_pure.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest  # noqa: E402

from agents.comparison_explanation import (  # noqa: E402
    GroundingError,
    build_evidence_payload,
    compute_evidence_fingerprint,
    compute_identity_key,
    validate_and_map_citations,
)
from agents.schemas import (  # noqa: E402
    ComparisonExplanationSchema,
    ComparisonLimitationSchema,
    ComparisonSourceSchema,
)


def _reports(*ids: str) -> list[dict]:
    return [
        {"id": rid, "ticker": rid.upper(), "extracted_data": {"revenue": "$1B"},
         "sentiment_analysis": {"sentiment": "Bullish"}, "scorecard": {"overall": 0.8}}
        for rid in ids
    ]


# --- build_evidence_payload --------------------------------------------------

def test_evidence_payload_is_bounded_and_numbered():
    reports = _reports("r1", "r2")
    reports[1]["draft_report"] = "should never appear in the payload"
    payload = build_evidence_payload(reports)
    assert [p["report_number"] for p in payload] == [1, 2]
    assert "draft_report" not in payload[1]
    assert payload[0]["extracted_data"] == {"revenue": "$1B"}


def test_evidence_payload_defaults_missing_fields_to_empty_dict():
    payload = build_evidence_payload([{"id": "r1", "ticker": "R1"}])
    assert payload[0]["extracted_data"] == {}
    assert payload[0]["sentiment_analysis"] == {}
    assert payload[0]["scorecard"] == {}


# --- compute_identity_key ----------------------------------------------------

def test_identity_key_is_order_independent_in_report_ids():
    a = compute_identity_key(["r1", "r2"], provider="gemini", model="gemini-2.0-flash")
    b = compute_identity_key(["r2", "r1"], provider="gemini", model="gemini-2.0-flash")
    assert a == b


def test_identity_key_differs_by_provider_and_model():
    base = compute_identity_key(["r1", "r2"], provider="gemini", model="m1")
    diff_provider = compute_identity_key(["r1", "r2"], provider="openai", model="m1")
    diff_model = compute_identity_key(["r1", "r2"], provider="gemini", model="m2")
    assert base != diff_provider
    assert base != diff_model


def test_identity_key_differs_by_report_set():
    a = compute_identity_key(["r1", "r2"], provider="gemini", model="m1")
    b = compute_identity_key(["r1", "r3"], provider="gemini", model="m1")
    assert a != b


# --- compute_evidence_fingerprint --------------------------------------------

def test_evidence_fingerprint_is_order_independent():
    reports = _reports("r1", "r2")
    a = compute_evidence_fingerprint(reports)
    b = compute_evidence_fingerprint(list(reversed(reports)))
    assert a == b


def test_evidence_fingerprint_changes_when_a_field_becomes_available():
    before = [{"id": "r1", "extracted_data": {}, "sentiment_analysis": {}, "scorecard": {}}]
    after = [{"id": "r1", "extracted_data": {"revenue": "$1B"}, "sentiment_analysis": {}, "scorecard": {}}]
    assert compute_evidence_fingerprint(before) != compute_evidence_fingerprint(after)


def test_evidence_fingerprint_stable_for_identical_presence():
    reports = _reports("r1", "r2")
    assert compute_evidence_fingerprint(reports) == compute_evidence_fingerprint(reports)


# --- validate_and_map_citations ----------------------------------------------

def _schema(narrative, sources, cited, limitations=None) -> ComparisonExplanationSchema:
    return ComparisonExplanationSchema(
        narrative=narrative,
        sources=[ComparisonSourceSchema(**s) for s in sources],
        cited_source_indices=cited,
        limitations=[ComparisonLimitationSchema(**l) for l in (limitations or [])],
    )


def test_valid_citation_maps_report_number_to_real_report_id():
    reports = _reports("real-report-id-1", "real-report-id-2")
    result = _schema(
        "R1 has higher revenue than R2 [1].",
        [{"index": 1, "report_number": 1, "field": "extracted_data"}],
        [1],
    )
    out = validate_and_map_citations(result, reports)
    assert out["sources"][0]["report_id"] == "real-report-id-1"
    assert out["evidence_completeness"] == "complete"
    assert out["limitations"] == []


def test_zero_cited_source_indices_is_a_grounding_error():
    """A narrative WITH a marker (so the "no markers at all" check doesn't fire
    first) but an empty cited_source_indices list — distinct failure mode."""
    reports = _reports("r1", "r2")
    result = _schema(
        "R1 differs from R2 [1].",
        [{"index": 1, "report_number": 1, "field": "extracted_data"}],
        [],
    )
    with pytest.raises(GroundingError, match="zero grounded"):
        validate_and_map_citations(result, reports)


def test_narrative_with_no_citation_markers_is_a_grounding_error():
    reports = _reports("r1", "r2")
    result = _schema(
        "R1 differs from R2 with no citation at all.",
        [{"index": 1, "report_number": 1, "field": "extracted_data"}],
        [1],
    )
    with pytest.raises(GroundingError, match="no \\[n\\] citation markers"):
        validate_and_map_citations(result, reports)


def test_used_marker_not_confirmed_in_cited_source_indices_is_a_grounding_error():
    """Document 43 §10's invariant: used ⊆ cited, not just used ⊆ declared.
    [2] is declared in sources (so it passes the weaker used<=declared check)
    but is never listed in cited_source_indices — this must still fail."""
    reports = _reports("r1", "r2")
    result = _schema(
        "Revenue improved [1], while margins weakened [2].",
        [{"index": 1, "report_number": 1, "field": "extracted_data"},
         {"index": 2, "report_number": 2, "field": "extracted_data"}],
        [1],  # [2] used in narrative but NOT in cited_source_indices
    )
    with pytest.raises(GroundingError, match="not confirmed in cited_source_indices"):
        validate_and_map_citations(result, reports)


def test_marker_referencing_an_undeclared_source_is_a_grounding_error():
    reports = _reports("r1", "r2")
    result = _schema(
        "R1 differs from R2 [2].",  # [2] never declared in sources
        [{"index": 1, "report_number": 1, "field": "extracted_data"}],
        [1],
    )
    with pytest.raises(GroundingError, match="not declared in sources"):
        validate_and_map_citations(result, reports)


def test_report_number_out_of_range_is_a_grounding_error():
    reports = _reports("r1", "r2")  # only 2 reports -> valid report_number is 1 or 2
    result = _schema(
        "R1 differs from R2 [1].",
        [{"index": 1, "report_number": 5, "field": "extracted_data"}],
        [1],
    )
    with pytest.raises(GroundingError, match="out of range"):
        validate_and_map_citations(result, reports)


def test_invalid_source_field_is_a_grounding_error():
    reports = _reports("r1", "r2")
    result = _schema(
        "R1 differs from R2 [1].",
        [{"index": 1, "report_number": 1, "field": "made_up_field"}],
        [1],
    )
    with pytest.raises(GroundingError, match="invalid field"):
        validate_and_map_citations(result, reports)


def test_duplicate_citation_indices_is_a_grounding_error():
    reports = _reports("r1", "r2")
    result = _schema(
        "R1 differs from R2 [1].",
        [{"index": 1, "report_number": 1, "field": "extracted_data"},
         {"index": 1, "report_number": 2, "field": "extracted_data"}],
        [1],
    )
    with pytest.raises(GroundingError, match="duplicate citation indices"):
        validate_and_map_citations(result, reports)


def test_limitation_produces_a_partial_result_never_a_fabricated_value():
    reports = _reports("r1", "r2")
    result = _schema(
        "R1's revenue is higher than R2's [1].",
        [{"index": 1, "report_number": 1, "field": "extracted_data"}],
        [1],
        limitations=[{"report_number": 2, "metric": "operating_margin",
                      "reason": "not disclosed this period"}],
    )
    out = validate_and_map_citations(result, reports)
    assert out["evidence_completeness"] == "partial"
    assert out["limitations"] == [
        {"report_id": "r2", "metric": "operating_margin", "reason": "not disclosed this period"}
    ]


def test_limitation_report_number_out_of_range_is_a_grounding_error():
    reports = _reports("r1", "r2")
    result = _schema(
        "R1 differs from R2 [1].",
        [{"index": 1, "report_number": 1, "field": "extracted_data"}],
        [1],
        limitations=[{"report_number": 9, "metric": "x", "reason": "y"}],
    )
    with pytest.raises(GroundingError, match="out of range"):
        validate_and_map_citations(result, reports)


def test_limitation_without_a_report_number_is_allowed():
    reports = _reports("r1", "r2")
    result = _schema(
        "R1 differs from R2 [1].",
        [{"index": 1, "report_number": 1, "field": "extracted_data"}],
        [1],
        limitations=[{"report_number": None, "metric": "x", "reason": "not attributable to one report"}],
    )
    out = validate_and_map_citations(result, reports)
    assert out["limitations"][0]["report_id"] is None


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
