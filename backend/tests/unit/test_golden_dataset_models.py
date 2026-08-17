"""Unit check for evaluation/golden_dataset/models.py's ExpectedBehavior and
BenchmarkCase (M10 Phase 1, Document 45 §7).

Pure, dependency-free — no DB, no network, no LLM.

    python backend/tests/unit/test_golden_dataset_models.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pydantic import ValidationError

from evaluation.golden_dataset.models import BenchmarkCase, CitationExpectation, ExpectedBehavior


# ---------------------------------------------------------------------------
# ExpectedBehavior — keyword_variant
# ---------------------------------------------------------------------------

def test_keyword_variant_presence_is_valid():
    b = ExpectedBehavior(
        behavior_id="b1", type="presence", description="d",
        match_rule="keyword_variant", variants=["revenue grew", "revenue increased"],
    )
    assert b.match_rule == "keyword_variant"
    assert b.reference is None


def test_keyword_variant_absence_is_valid():
    b = ExpectedBehavior(
        behavior_id="b1", type="absence", description="d",
        match_rule="keyword_variant", variants=["you should buy"],
    )
    assert b.type == "absence"


def test_keyword_variant_rejects_empty_variants():
    try:
        ExpectedBehavior(behavior_id="b1", type="presence", description="d",
                          match_rule="keyword_variant", variants=[])
    except ValidationError as e:
        assert "non-empty 'variants'" in str(e)
    else:
        raise AssertionError("expected ValidationError for empty variants")


def test_keyword_variant_rejects_missing_variants():
    try:
        ExpectedBehavior(behavior_id="b1", type="presence", description="d",
                          match_rule="keyword_variant")
    except ValidationError as e:
        assert "non-empty 'variants'" in str(e)
    else:
        raise AssertionError("expected ValidationError for missing variants")


def test_keyword_variant_rejects_reference_set():
    try:
        ExpectedBehavior(behavior_id="b1", type="presence", description="d",
                          match_rule="keyword_variant", variants=["x"], reference="y")
    except ValidationError as e:
        assert "forbids 'reference'" in str(e)
    else:
        raise AssertionError("expected ValidationError for reference set on keyword_variant")


def test_keyword_variant_rejects_wrong_type():
    try:
        ExpectedBehavior(behavior_id="b1", type="acknowledgment", description="d",
                          match_rule="keyword_variant", variants=["x"])
    except ValidationError as e:
        assert "requires" in str(e) and "type in" in str(e)
    else:
        raise AssertionError("expected ValidationError for acknowledgment+keyword_variant")


# ---------------------------------------------------------------------------
# ExpectedBehavior — citation_required
# ---------------------------------------------------------------------------

def test_citation_required_is_valid():
    b = ExpectedBehavior(behavior_id="b1", type="presence", description="d",
                          match_rule="citation_required", reference="revenue_figure")
    assert b.variants is None


def test_citation_required_rejects_missing_reference():
    try:
        ExpectedBehavior(behavior_id="b1", type="presence", description="d",
                          match_rule="citation_required")
    except ValidationError as e:
        assert "non-empty 'reference'" in str(e)
    else:
        raise AssertionError("expected ValidationError for missing reference")


def test_citation_required_rejects_variants_set():
    try:
        ExpectedBehavior(behavior_id="b1", type="presence", description="d",
                          match_rule="citation_required", reference="r", variants=["x"])
    except ValidationError as e:
        assert "forbids 'variants'" in str(e)
    else:
        raise AssertionError("expected ValidationError for variants set on citation_required")


def test_citation_required_rejects_wrong_type():
    try:
        ExpectedBehavior(behavior_id="b1", type="absence", description="d",
                          match_rule="citation_required", reference="r")
    except ValidationError as e:
        assert "type in" in str(e)
    else:
        raise AssertionError("expected ValidationError for absence+citation_required")


# ---------------------------------------------------------------------------
# ExpectedBehavior — limitation_reference
# ---------------------------------------------------------------------------

def test_limitation_reference_is_valid():
    b = ExpectedBehavior(behavior_id="b1", type="acknowledgment", description="d",
                          match_rule="limitation_reference", reference="figure_not_disclosed")
    assert b.reference == "figure_not_disclosed"


def test_limitation_reference_rejects_missing_reference():
    try:
        ExpectedBehavior(behavior_id="b1", type="acknowledgment", description="d",
                          match_rule="limitation_reference")
    except ValidationError as e:
        assert "non-empty 'reference'" in str(e)
    else:
        raise AssertionError("expected ValidationError for missing reference")


def test_limitation_reference_rejects_variants_set():
    try:
        ExpectedBehavior(behavior_id="b1", type="acknowledgment", description="d",
                          match_rule="limitation_reference", reference="r", variants=["x"])
    except ValidationError as e:
        assert "forbids 'variants'" in str(e)
    else:
        raise AssertionError("expected ValidationError for variants set on limitation_reference")


def test_limitation_reference_rejects_wrong_type():
    try:
        ExpectedBehavior(behavior_id="b1", type="presence", description="d",
                          match_rule="limitation_reference", reference="r")
    except ValidationError as e:
        assert "type in" in str(e)
    else:
        raise AssertionError("expected ValidationError for presence+limitation_reference")


# ---------------------------------------------------------------------------
# BenchmarkCase
# ---------------------------------------------------------------------------

def _base_case(**overrides):
    payload = {
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
    payload.update(overrides)
    return payload


def test_valid_case_for_each_surface():
    research = BenchmarkCase.model_validate(_base_case())
    assert research.surface == "research"
    assert isinstance(research.citation_expectation, CitationExpectation)
    assert research.citation_expectation.min_valid_citations == 1

    learning = BenchmarkCase.model_validate(_base_case(
        surface="learning", context={"ticker": "MSFT", "concept": "operating margin"},
    ))
    assert learning.surface == "learning"

    comparison = BenchmarkCase.model_validate(_base_case(
        surface="comparison_explanation", context={"report_ids": ["r1", "r2"]},
    ))
    assert comparison.surface == "comparison_explanation"


def test_invalid_case_missing_required_field():
    payload = _base_case()
    del payload["citation_expectation"]
    try:
        BenchmarkCase.model_validate(payload)
    except ValidationError as e:
        assert "citation_expectation" in str(e)
    else:
        raise AssertionError("expected ValidationError for missing citation_expectation")


def test_unsupported_surface_rejected():
    try:
        BenchmarkCase.model_validate(_base_case(surface="unknown_surface"))
    except ValidationError as e:
        assert "surface" in str(e)
    else:
        raise AssertionError("expected ValidationError for unsupported surface")


def test_empty_expected_behaviors_rejected():
    try:
        BenchmarkCase.model_validate(_base_case(expected_behaviors=[]))
    except ValidationError as e:
        assert "expected_behaviors" in str(e)
    else:
        raise AssertionError("expected ValidationError for empty expected_behaviors")


def test_invalid_version_metadata_rejected():
    try:
        BenchmarkCase.model_validate(_base_case(dataset_version=0))
    except ValidationError as e:
        assert "dataset_version" in str(e)
    else:
        raise AssertionError("expected ValidationError for dataset_version=0")

    try:
        BenchmarkCase.model_validate(_base_case(case_version=-1))
    except ValidationError as e:
        assert "case_version" in str(e)
    else:
        raise AssertionError("expected ValidationError for negative case_version")


def test_context_missing_surface_required_key_rejected():
    try:
        BenchmarkCase.model_validate(_base_case(context={"ticker": "AAPL"}))  # missing 'query'
    except ValidationError as e:
        assert "requires non-empty context key" in str(e)
    else:
        raise AssertionError("expected ValidationError for missing 'query' on research surface")


def test_duplicate_behavior_id_rejected():
    payload = _base_case(expected_behaviors=[
        {"behavior_id": "dup", "type": "presence", "description": "d",
         "match_rule": "keyword_variant", "variants": ["x"]},
        {"behavior_id": "dup", "type": "absence", "description": "d2",
         "match_rule": "keyword_variant", "variants": ["y"]},
    ])
    try:
        BenchmarkCase.model_validate(payload)
    except ValidationError as e:
        assert "duplicate behavior_id" in str(e)
    else:
        raise AssertionError("expected ValidationError for duplicate behavior_id")


def test_limitation_reference_must_resolve_against_known_limitations():
    payload = _base_case(expected_behaviors=[
        {"behavior_id": "b1", "type": "acknowledgment", "description": "d",
         "match_rule": "limitation_reference", "reference": "gap_x"},
    ])
    # Missing known_limitations entirely -> reference can't resolve.
    try:
        BenchmarkCase.model_validate(payload)
    except ValidationError as e:
        assert "not present in known_limitations" in str(e)
    else:
        raise AssertionError("expected ValidationError for unresolved limitation reference")

    # Present -> valid.
    payload["known_limitations"] = ["gap_x"]
    case = BenchmarkCase.model_validate(payload)
    assert case.known_limitations == ["gap_x"]


if __name__ == "__main__":
    test_keyword_variant_presence_is_valid()
    test_keyword_variant_absence_is_valid()
    test_keyword_variant_rejects_empty_variants()
    test_keyword_variant_rejects_missing_variants()
    test_keyword_variant_rejects_reference_set()
    test_keyword_variant_rejects_wrong_type()
    test_citation_required_is_valid()
    test_citation_required_rejects_missing_reference()
    test_citation_required_rejects_variants_set()
    test_citation_required_rejects_wrong_type()
    test_limitation_reference_is_valid()
    test_limitation_reference_rejects_missing_reference()
    test_limitation_reference_rejects_variants_set()
    test_limitation_reference_rejects_wrong_type()
    test_valid_case_for_each_surface()
    test_invalid_case_missing_required_field()
    test_unsupported_surface_rejected()
    test_empty_expected_behaviors_rejected()
    test_invalid_version_metadata_rejected()
    test_context_missing_surface_required_key_rejected()
    test_duplicate_behavior_id_rejected()
    test_limitation_reference_must_resolve_against_known_limitations()
    print("ok: ExpectedBehavior cross-field invariants (keyword_variant/citation_required/"
          "limitation_reference); BenchmarkCase schema, surface/context, version, and "
          "behavior-integrity validation")
