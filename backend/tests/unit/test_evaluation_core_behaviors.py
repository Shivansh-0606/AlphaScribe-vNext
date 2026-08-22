"""Unit check for evaluation/core/behaviors.py (M10 Phase 3).

Pure, dependency-free — no DB, no network, no LLM anywhere in the module
under test or these tests.

    python backend/tests/unit/test_evaluation_core_behaviors.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pydantic import ValidationError

from evaluation.adapters.types import Citation, NormalizedOutput
from evaluation.core.behaviors import (
    evaluate_behavior,
    evaluate_citation_required,
    evaluate_keyword_variant,
    evaluate_limitation_reference,
    evaluate_numeric_consistency,
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


# ---------------------------------------------------------------------------
# numeric_consistency (Document 47 §7.0/§7.1, Phase A) — Research/Learning only
# ---------------------------------------------------------------------------

def _numeric_behavior(**overrides) -> ExpectedBehavior:
    payload = {
        "behavior_id": "b1", "type": "presence", "description": "d",
        "match_rule": "numeric_consistency", "reference": "source_documents[0].revenue",
        "tolerance": 0.01,
    }
    payload.update(overrides)
    return ExpectedBehavior.model_validate(payload)


def _numeric_context(**overrides) -> dict:
    payload = {"ticker": "AAPL", "query": "q", "source_documents": [{"revenue": 95_000_000.0}]}
    payload.update(overrides)
    return payload


def _numeric_output(**overrides) -> NormalizedOutput:
    payload = dict(
        text="Revenue was $95.0M [1].",
        citations=[Citation(source_id="1", eligible=True, referenced=True, valid=True)],
        grounding_verdict="grounded",
        limitations_stated=[],
    )
    payload.update(overrides)
    return NormalizedOutput(**payload)


def test_numeric_consistency_correct_claim_passes():
    result = evaluate_numeric_consistency(
        _numeric_behavior(), _numeric_output(), surface="research", context=_numeric_context(),
    )
    assert result.status == "PASS"


def test_numeric_consistency_incorrect_claim_fails():
    output = _numeric_output(text="Revenue was $80.0M [1].")
    result = evaluate_numeric_consistency(
        _numeric_behavior(), output, surface="research", context=_numeric_context(),
    )
    assert result.status == "FAIL"


def test_numeric_consistency_contradictory_claim_fails():
    # Fixture says $120M; the claim tied to [1] explicitly states $95M —
    # a single, unambiguous, contradicted figure.
    context = _numeric_context(source_documents=[{"revenue": 120_000_000.0}])
    output = _numeric_output(text="Revenue declined to $95M [1].")
    result = evaluate_numeric_consistency(_numeric_behavior(), output, surface="research", context=context)
    assert result.status == "FAIL"
    assert "95000000" in result.reason or "95,000,000" in result.reason or "95000000.0" in result.reason


def test_numeric_consistency_unsupported_claim_no_fixture_value_is_inconclusive():
    # reference points at a key the fixture doesn't have -> can't construct
    # the check at all -> INCONCLUSIVE, never guessed.
    context = _numeric_context(source_documents=[{"other_field": 1.0}])
    result = evaluate_numeric_consistency(
        _numeric_behavior(), _numeric_output(), surface="research", context=context,
    )
    assert result.status == "INCONCLUSIVE"
    assert "does not resolve" in result.reason


def test_numeric_consistency_multiple_numeric_tokens_in_claim_is_inconclusive():
    # Document 47 Revision 4's own worked counter-example: sentence-scoping
    # alone still leaves two numbers in the same clause — must not guess.
    output = _numeric_output(text="Revenue declined to $95M [1], while another period reported $120M.")
    result = evaluate_numeric_consistency(
        _numeric_behavior(), output, surface="research", context=_numeric_context(),
    )
    assert result.status == "INCONCLUSIVE"
    assert "ambiguous" in result.reason


def test_numeric_consistency_missing_evidence_source_not_in_citations_is_inconclusive():
    output = _numeric_output(citations=[])  # source_id "1" never offered as evidence at all
    result = evaluate_numeric_consistency(
        _numeric_behavior(), output, surface="research", context=_numeric_context(),
    )
    assert result.status == "INCONCLUSIVE"
    assert "not present/eligible" in result.reason


def test_numeric_consistency_ineligible_source_is_inconclusive():
    output = _numeric_output(citations=[Citation(source_id="1", eligible=False, referenced=False, valid=False)])
    result = evaluate_numeric_consistency(
        _numeric_behavior(), output, surface="research", context=_numeric_context(),
    )
    assert result.status == "INCONCLUSIVE"


def test_numeric_consistency_zero_matching_sentences_is_inconclusive():
    output = _numeric_output(text="Revenue was strong this quarter.")  # no [1] marker at all
    result = evaluate_numeric_consistency(
        _numeric_behavior(), output, surface="research", context=_numeric_context(),
    )
    assert result.status == "INCONCLUSIVE"
    assert "no sentence" in result.reason


def test_numeric_consistency_multiple_matching_sentences_is_inconclusive():
    output = _numeric_output(text="Revenue was $95.0M [1]. Margin also cites [1] again.")
    result = evaluate_numeric_consistency(
        _numeric_behavior(), output, surface="research", context=_numeric_context(),
    )
    assert result.status == "INCONCLUSIVE"
    assert "2 sentences" in result.reason


def test_numeric_consistency_no_output_text_is_inconclusive():
    output = _numeric_output(text="", grounding_verdict="error")
    result = evaluate_numeric_consistency(
        _numeric_behavior(), output, surface="research", context=_numeric_context(),
    )
    assert result.status == "INCONCLUSIVE"


def test_numeric_consistency_no_numeric_value_in_claim_fails_not_inconclusive():
    # The check WAS constructible (fixture value resolved, exactly one claim
    # sentence selected) — the model just stated no matching figure. A
    # determinate FAIL, distinct from the construction-failure INCONCLUSIVE
    # cases above (Document 47 §7.1).
    output = _numeric_output(text="Revenue grew strongly this quarter [1].")
    result = evaluate_numeric_consistency(
        _numeric_behavior(), output, surface="research", context=_numeric_context(),
    )
    assert result.status == "FAIL"
    assert "no numeric value" in result.reason


def test_numeric_consistency_zero_expected_value_uses_exact_equality():
    context = _numeric_context(source_documents=[{"revenue": 0.0}])
    passing = evaluate_numeric_consistency(
        _numeric_behavior(), _numeric_output(text="Revenue was $0 [1]."),
        surface="research", context=context,
    )
    assert passing.status == "PASS"

    # Document 47 §7.1: at expected=0, relative tolerance is undefined —
    # any non-zero claim fails, even one that would pass a >0 relative check.
    failing = evaluate_numeric_consistency(
        _numeric_behavior(), _numeric_output(text="Revenue was $1 [1]."),
        surface="research", context=context,
    )
    assert failing.status == "FAIL"


def test_numeric_consistency_tolerance_boundary():
    # tolerance=0.01 (1%) of 95_000_000 = 950_000 either side.
    context = _numeric_context(source_documents=[{"revenue": 95_000_000.0}])
    just_inside = evaluate_numeric_consistency(
        _numeric_behavior(), _numeric_output(text="Revenue was $95.9M [1]."),
        surface="research", context=context,
    )
    assert just_inside.status == "PASS"

    just_outside = evaluate_numeric_consistency(
        _numeric_behavior(), _numeric_output(text="Revenue was $96.1M [1]."),
        surface="research", context=context,
    )
    assert just_outside.status == "FAIL"


def test_numeric_consistency_comparison_explanation_surface_is_inconclusive():
    # Defense in depth — BenchmarkCase construction already rejects this
    # combination (test_golden_dataset_models.py); the evaluator itself must
    # also never silently mis-evaluate it if ever reached directly.
    result = evaluate_numeric_consistency(
        _numeric_behavior(), _numeric_output(), surface="comparison_explanation", context=_numeric_context(),
    )
    assert result.status == "INCONCLUSIVE"
    assert "not supported for surface" in result.reason


def test_numeric_consistency_learning_surface_works_identically_to_research():
    context = _numeric_context(ticker=None, query=None, concept="operating margin")
    result = evaluate_numeric_consistency(
        _numeric_behavior(), _numeric_output(), surface="learning", context=context,
    )
    assert result.status == "PASS"


def test_numeric_consistency_repeated_evaluation_is_identical():
    # Document 47 Phase A's own determinism requirement — no LLM call, no
    # randomness anywhere in this evaluator; identical input must produce an
    # identical (equal, not merely equal-status) result every time.
    behavior, output, context = _numeric_behavior(), _numeric_output(), _numeric_context()
    first = evaluate_numeric_consistency(behavior, output, surface="research", context=context)
    second = evaluate_numeric_consistency(behavior, output, surface="research", context=context)
    assert first == second


def test_numeric_consistency_dispatches_through_evaluate_behavior():
    # Confirms the _EVALUATORS/evaluate_behavior wiring itself (not just the
    # standalone function) — the new `context` parameter reaches the right
    # evaluator, and the three existing rules still dispatch correctly with
    # the widened signature. M11 Phase C: evaluate_behavior is now async
    # (a real chat_json call may happen for model_judged_support) — wrapped
    # in asyncio.run() here; the deterministic rules' own results are
    # unaffected by that change.
    result = asyncio.run(evaluate_behavior(
        _numeric_behavior(), _numeric_output(), surface="research", context=_numeric_context(),
    ))
    assert result.status == "PASS"
    assert result.match_rule == "numeric_consistency"

    kw_result = asyncio.run(evaluate_behavior(_behavior(), _output(), surface="research", context={}))
    assert kw_result.status == "PASS"


# ---------------------------------------------------------------------------
# numeric_consistency — CTO-review regression tests: sign preservation
# ---------------------------------------------------------------------------

def _signed_numeric_behavior(**overrides) -> ExpectedBehavior:
    payload = {
        "behavior_id": "b1", "type": "presence", "description": "d",
        "match_rule": "numeric_consistency", "reference": "source_documents[0].revenue_yoy",
        "tolerance": 0.01,
    }
    payload.update(overrides)
    return ExpectedBehavior.model_validate(payload)


def _signed_numeric_context(expected_value) -> dict:
    return {"ticker": "AAPL", "query": "q", "source_documents": [{"revenue_yoy": expected_value}]}


def _signed_numeric_output(claim_token: str) -> NormalizedOutput:
    return NormalizedOutput(
        text=f"Revenue changed by {claim_token} [1].",
        citations=[Citation(source_id="1", eligible=True, referenced=True, valid=True)],
        grounding_verdict="grounded",
        limitations_stated=[],
    )


def test_numeric_consistency_sign_negative_expected_negative_claim_percent_passes():
    # 1. expected -5%, claim -5% -> PASS. Under the pre-fix regex/normalizer,
    # "-5%" lost its sign and normalized to +5.0, so this compared -5.0 vs
    # +5.0 and produced FAIL — this assertion would have failed pre-fix.
    result = evaluate_numeric_consistency(
        _signed_numeric_behavior(), _signed_numeric_output("-5%"),
        surface="research", context=_signed_numeric_context(-5.0),
    )
    assert result.status == "PASS"


def test_numeric_consistency_sign_negative_expected_positive_claim_percent_fails():
    # 2. expected -5%, claim +5% -> FAIL.
    result = evaluate_numeric_consistency(
        _signed_numeric_behavior(), _signed_numeric_output("+5%"),
        surface="research", context=_signed_numeric_context(-5.0),
    )
    assert result.status == "FAIL"


def test_numeric_consistency_sign_positive_expected_positive_claim_percent_passes():
    # 3. expected +5%, claim +5% -> PASS.
    result = evaluate_numeric_consistency(
        _signed_numeric_behavior(), _signed_numeric_output("+5%"),
        surface="research", context=_signed_numeric_context(5.0),
    )
    assert result.status == "PASS"


def test_numeric_consistency_sign_positive_expected_negative_claim_percent_fails():
    # 4. expected +5%, claim -5% -> FAIL. Under the pre-fix normalizer, "-5%"
    # also normalized to +5.0 (sign-blind), so this compared +5.0 vs +5.0 and
    # produced PASS — this assertion would have failed pre-fix.
    result = evaluate_numeric_consistency(
        _signed_numeric_behavior(), _signed_numeric_output("-5%"),
        surface="research", context=_signed_numeric_context(5.0),
    )
    assert result.status == "FAIL"


def test_numeric_consistency_sign_negative_expected_negative_claim_dollar_passes():
    # 5. expected -$95M, claim -$95M -> PASS. Pre-fix, the sign-blind claim
    # normalized to +95,000,000.0 vs the (unaffected, raw-float) expected
    # -95,000,000.0 -> FAIL — this assertion would have failed pre-fix.
    result = evaluate_numeric_consistency(
        _signed_numeric_behavior(), _signed_numeric_output("-$95M"),
        surface="research", context=_signed_numeric_context(-95_000_000.0),
    )
    assert result.status == "PASS"


def test_numeric_consistency_sign_negative_expected_positive_claim_dollar_fails():
    # 6. expected -$95M, claim +$95M -> FAIL.
    result = evaluate_numeric_consistency(
        _signed_numeric_behavior(), _signed_numeric_output("+$95M"),
        surface="research", context=_signed_numeric_context(-95_000_000.0),
    )
    assert result.status == "FAIL"


def test_normalize_numeric_token_preserves_sign_directly():
    # Supplements (does not replace) the evaluator-level tests above.
    from evaluation.core.behaviors import _normalize_numeric_token
    assert _normalize_numeric_token("-5%") == -5.0
    assert _normalize_numeric_token("+5%") == 5.0
    assert _normalize_numeric_token("-$95M") == -95_000_000.0
    assert _normalize_numeric_token("+$95M") == 95_000_000.0
    assert _normalize_numeric_token("-50bps") == -0.5
    assert _normalize_numeric_token("+2pp") == 2.0


# ---------------------------------------------------------------------------
# _select_single_claim_sentence — CTO-review regression tests: repeated
# citation-marker ambiguity within one sentence
# ---------------------------------------------------------------------------

def test_selector_A_one_sentence_one_marker_is_selected():
    output = _numeric_output(text="Revenue was $95.0M [1].")
    result = evaluate_numeric_consistency(_numeric_behavior(), output, surface="research", context=_numeric_context())
    assert result.status == "PASS"  # reached the comparison at all -> selection succeeded


def test_selector_B_one_sentence_repeated_marker_is_inconclusive():
    # The exact case the CTO review caught: one sentence, marker [1] twice.
    output = _numeric_output(text="Revenue was $95M [1], confirmed by the same filing [1].")
    result = evaluate_numeric_consistency(_numeric_behavior(), output, surface="research", context=_numeric_context())
    assert result.status == "INCONCLUSIVE"
    assert "appears 2 times" in result.reason


def test_selector_C_two_sentences_each_with_marker_is_inconclusive():
    output = _numeric_output(text="Revenue was $95.0M [1]. Margin also cites [1] again.")
    result = evaluate_numeric_consistency(_numeric_behavior(), output, surface="research", context=_numeric_context())
    assert result.status == "INCONCLUSIVE"
    assert "2 sentences" in result.reason


def test_selector_D_no_marker_is_inconclusive():
    output = _numeric_output(text="Revenue was strong this quarter.")
    result = evaluate_numeric_consistency(_numeric_behavior(), output, surface="research", context=_numeric_context())
    assert result.status == "INCONCLUSIVE"
    assert "no sentence" in result.reason


def test_selector_unrelated_marker_in_same_sentence_does_not_trigger_ambiguity():
    # "Do not change the existing behavior for unrelated citation markers."
    output = _numeric_output(text="Revenue was $95.0M [1][2].")
    result = evaluate_numeric_consistency(_numeric_behavior(), output, surface="research", context=_numeric_context())
    assert result.status == "PASS"


def test_select_single_claim_sentence_directly_counts_occurrences():
    from evaluation.core.behaviors import _select_single_claim_sentence
    sentence, reason = _select_single_claim_sentence(
        "Revenue was $95M [1], confirmed by the same filing [1].", "1",
    )
    assert sentence is None
    assert "appears 2 times" in reason

    sentence, reason = _select_single_claim_sentence("Revenue was $95M [1].", "1")
    assert sentence == "Revenue was $95M [1]."
    assert reason is None


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
    test_numeric_consistency_correct_claim_passes()
    test_numeric_consistency_incorrect_claim_fails()
    test_numeric_consistency_contradictory_claim_fails()
    test_numeric_consistency_unsupported_claim_no_fixture_value_is_inconclusive()
    test_numeric_consistency_multiple_numeric_tokens_in_claim_is_inconclusive()
    test_numeric_consistency_missing_evidence_source_not_in_citations_is_inconclusive()
    test_numeric_consistency_ineligible_source_is_inconclusive()
    test_numeric_consistency_zero_matching_sentences_is_inconclusive()
    test_numeric_consistency_multiple_matching_sentences_is_inconclusive()
    test_numeric_consistency_no_output_text_is_inconclusive()
    test_numeric_consistency_no_numeric_value_in_claim_fails_not_inconclusive()
    test_numeric_consistency_zero_expected_value_uses_exact_equality()
    test_numeric_consistency_tolerance_boundary()
    test_numeric_consistency_comparison_explanation_surface_is_inconclusive()
    test_numeric_consistency_learning_surface_works_identically_to_research()
    test_numeric_consistency_repeated_evaluation_is_identical()
    test_numeric_consistency_dispatches_through_evaluate_behavior()
    test_numeric_consistency_sign_negative_expected_negative_claim_percent_passes()
    test_numeric_consistency_sign_negative_expected_positive_claim_percent_fails()
    test_numeric_consistency_sign_positive_expected_positive_claim_percent_passes()
    test_numeric_consistency_sign_positive_expected_negative_claim_percent_fails()
    test_numeric_consistency_sign_negative_expected_negative_claim_dollar_passes()
    test_numeric_consistency_sign_negative_expected_positive_claim_dollar_fails()
    test_normalize_numeric_token_preserves_sign_directly()
    test_selector_A_one_sentence_one_marker_is_selected()
    test_selector_B_one_sentence_repeated_marker_is_inconclusive()
    test_selector_C_two_sentences_each_with_marker_is_inconclusive()
    test_selector_D_no_marker_is_inconclusive()
    test_selector_unrelated_marker_in_same_sentence_does_not_trigger_ambiguity()
    test_select_single_claim_sentence_directly_counts_occurrences()
    print("ok: keyword_variant/citation_required/limitation_reference/numeric_consistency deterministic "
          "evaluators, incl. CTO-review sign-preservation and repeated-marker-ambiguity fixes")
