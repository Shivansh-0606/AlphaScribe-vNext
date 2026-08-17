"""Unit check for evaluation/core/behaviors.py (M10 Phase 3).

Pure, dependency-free — no DB, no network, no LLM anywhere in the module
under test or these tests.

    python backend/tests/unit/test_evaluation_core_behaviors.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pydantic import ValidationError

from evaluation.adapters.types import Citation, NormalizedOutput
from evaluation.core.behaviors import (
    evaluate_citation_required,
    evaluate_keyword_variant,
    evaluate_limitation_reference,
)
from evaluation.golden_dataset.models import ExpectedBehavior


def _behavior(**overrides) -> ExpectedBehavior:
    payload = {
        "behavior_id": "b1", "type": "presence", "description": "d",
        "match_rule": "keyword_variant", "variants": ["revenue grew", "revenue increased"],
    }
    payload.update(overrides)
    return ExpectedBehavior.model_validate(payload)


def _output(**overrides) -> NormalizedOutput:
    payload = dict(
        text="Revenue grew 5% year over year [1].",
        citations=[Citation(source_id="1", eligible=True, referenced=True, valid=True)],
        grounding_verdict="grounded",
        limitations_stated=[],
    )
    payload.update(overrides)
    return NormalizedOutput(**payload)


# ---------------------------------------------------------------------------
# keyword_variant
# ---------------------------------------------------------------------------

def test_keyword_variant_presence_matching_variant_passes():
    result = evaluate_keyword_variant(_behavior(type="presence"), _output())
    assert result.status == "PASS"


def test_keyword_variant_presence_no_matching_variant_fails():
    behavior = _behavior(type="presence", variants=["revenue declined"])
    result = evaluate_keyword_variant(behavior, _output())
    assert result.status == "FAIL"


def test_keyword_variant_forbidden_matching_variant_fails():
    behavior = _behavior(type="absence", variants=["revenue grew"])
    result = evaluate_keyword_variant(behavior, _output())
    assert result.status == "FAIL"


def test_keyword_variant_forbidden_no_matching_variant_passes():
    behavior = _behavior(type="absence", variants=["revenue declined"])
    result = evaluate_keyword_variant(behavior, _output())
    assert result.status == "PASS"


def test_keyword_variant_multiple_variants_any_match_passes():
    behavior = _behavior(type="presence", variants=["not present", "also not present", "revenue grew"])
    result = evaluate_keyword_variant(behavior, _output())
    assert result.status == "PASS"
    assert "revenue grew" in result.reason


def test_keyword_variant_case_insensitive_and_whitespace_tolerant():
    behavior = _behavior(type="presence", variants=["REVENUE   GREW"])
    output = _output(text="the report says revenue\ngrew steadily [1].")
    result = evaluate_keyword_variant(behavior, output)
    assert result.status == "PASS"


def test_keyword_variant_inconclusive_when_no_output_text():
    result = evaluate_keyword_variant(_behavior(), _output(text="", grounding_verdict="error"))
    assert result.status == "INCONCLUSIVE"
    assert "error" in result.reason


def test_keyword_variant_malformed_rule_rejected_by_schema():
    # Confirms the frozen Phase 1 invariant this evaluator relies on still
    # holds: an evaluator is never handed a keyword_variant with empty
    # variants — Pydantic rejects it before evaluate_keyword_variant ever runs.
    try:
        ExpectedBehavior.model_validate({
            "behavior_id": "b1", "type": "presence", "description": "d",
            "match_rule": "keyword_variant", "variants": [],
        })
    except ValidationError:
        pass
    else:
        raise AssertionError("expected ValidationError for empty variants")


# ---------------------------------------------------------------------------
# citation_required
# ---------------------------------------------------------------------------

def _citation_behavior(**overrides) -> ExpectedBehavior:
    payload = {
        "behavior_id": "b1", "type": "presence", "description": "d",
        "match_rule": "citation_required", "reference": "revenue_figure",
    }
    payload.update(overrides)
    return ExpectedBehavior.model_validate(payload)


def test_citation_required_present_passes():
    result = evaluate_citation_required(_citation_behavior(), _output())
    assert result.status == "PASS"


def test_citation_required_absent_fails():
    output = _output(citations=[Citation(source_id="1", eligible=True, referenced=False, valid=False)])
    result = evaluate_citation_required(_citation_behavior(), output)
    assert result.status == "FAIL"


def test_citation_required_forbidden_present_fails():
    # Document 45 §7 restricts citation_required to type='presence' only —
    # there is no way to construct type='absence' via model_validate. This
    # exercises the evaluator's defensive symmetric branch directly via
    # model_construct, which bypasses that schema constraint on purpose —
    # see evaluate_citation_required's own docstring for why this state
    # isn't reachable through the frozen, validated case-authoring path.
    behavior = ExpectedBehavior.model_construct(
        behavior_id="b1", type="absence", description="d",
        match_rule="citation_required", reference="revenue_figure", variants=None,
    )
    result = evaluate_citation_required(behavior, _output())  # a valid citation IS present
    assert result.status == "FAIL"


def test_citation_required_forbidden_absent_passes():
    behavior = ExpectedBehavior.model_construct(
        behavior_id="b1", type="absence", description="d",
        match_rule="citation_required", reference="revenue_figure", variants=None,
    )
    output = _output(citations=[Citation(source_id="1", eligible=True, referenced=False, valid=False)])
    result = evaluate_citation_required(behavior, output)
    assert result.status == "PASS"


def test_citation_required_inconclusive_when_no_output():
    result = evaluate_citation_required(_citation_behavior(), _output(text="", grounding_verdict="error"))
    assert result.status == "INCONCLUSIVE"


# ---------------------------------------------------------------------------
# limitation_reference
# ---------------------------------------------------------------------------

def _limitation_behavior(**overrides) -> ExpectedBehavior:
    payload = {
        "behavior_id": "b1", "type": "acknowledgment", "description": "d",
        "match_rule": "limitation_reference", "reference": "figure_not_disclosed",
    }
    payload.update(overrides)
    return ExpectedBehavior.model_validate(payload)


def test_limitation_reference_acknowledgment_present_passes():
    output = _output(limitations_stated=["revenue: not disclosed in the excerpt"])
    result = evaluate_limitation_reference(_limitation_behavior(), output, surface="research")
    assert result.status == "PASS"


def test_limitation_reference_acknowledgment_absent_fails():
    output = _output(limitations_stated=[])
    result = evaluate_limitation_reference(_limitation_behavior(), output, surface="research")
    assert result.status == "FAIL"


def test_limitation_reference_inconclusive_when_no_output():
    result = evaluate_limitation_reference(
        _limitation_behavior(), _output(text="", grounding_verdict="error"), surface="research",
    )
    assert result.status == "INCONCLUSIVE"


def test_limitation_reference_learning_surface_always_inconclusive():
    # Reported gap (evaluate_limitation_reference's own docstring): Learning's
    # adapter never populates limitations_stated at all — an empty list from
    # Learning means "cannot tell," not "nothing was acknowledged."
    output = _output(limitations_stated=[])  # what learning.py's adapter always returns
    result = evaluate_limitation_reference(_limitation_behavior(), output, surface="learning")
    assert result.status == "INCONCLUSIVE"
    assert "Learning" in result.reason


def test_limitation_reference_no_forbidden_type_value_exists():
    # Reported gap: Document 45 §7's BehaviorType enum (presence|absence|
    # acknowledgment) has no value meaning "forbidden acknowledgment" — this
    # rule's constraint table restricts it to type='acknowledgment' only, and
    # unlike citation_required there is no sibling type to reuse defensively.
    # Documented here as a test, not silently omitted: this exact combination
    # cannot be constructed at all, even via model_construct, without adding
    # a fourth type value to the frozen schema (out of Phase 3's scope).
    assert set(ExpectedBehavior.model_fields["type"].annotation.__args__) == {
        "presence", "absence", "acknowledgment",
    }


if __name__ == "__main__":
    test_keyword_variant_presence_matching_variant_passes()
    test_keyword_variant_presence_no_matching_variant_fails()
    test_keyword_variant_forbidden_matching_variant_fails()
    test_keyword_variant_forbidden_no_matching_variant_passes()
    test_keyword_variant_multiple_variants_any_match_passes()
    test_keyword_variant_case_insensitive_and_whitespace_tolerant()
    test_keyword_variant_inconclusive_when_no_output_text()
    test_keyword_variant_malformed_rule_rejected_by_schema()
    test_citation_required_present_passes()
    test_citation_required_absent_fails()
    test_citation_required_forbidden_present_fails()
    test_citation_required_forbidden_absent_passes()
    test_citation_required_inconclusive_when_no_output()
    test_limitation_reference_acknowledgment_present_passes()
    test_limitation_reference_acknowledgment_absent_fails()
    test_limitation_reference_inconclusive_when_no_output()
    test_limitation_reference_learning_surface_always_inconclusive()
    test_limitation_reference_no_forbidden_type_value_exists()
    print("ok: keyword_variant/citation_required/limitation_reference deterministic evaluators")
