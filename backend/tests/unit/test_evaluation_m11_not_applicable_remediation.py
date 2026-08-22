"""M11 NOT_APPLICABLE remediation (Document 47 Rev 6 §7.3.1) — the relevance-
first applicability rule added to `evaluation/core/judge.py`'s `_SYSTEM_PROMPT`
and to `agents/schemas.py`'s `JudgeVerdictSchema.verdict` description.

v3-na2 supersedes v3-na1: the live v3-na1 validation found that its bare
"property" wording let the model treat modality (Case 06, disclosure
uncertainty) and tense (Case 07, relevant silence) as if they were property
differences, incorrectly returning NOT_APPLICABLE. v3-na2's applicability
rule explicitly names tense, modality, and polarity as differences that do
NOT make evidence inapplicable, mirroring Document 47 Rev 6 §7.3.1's own
exclusion list rather than leaving the model to infer it.

Hermetic throughout — no live provider, no network. `_generate_sync` is
stubbed exactly as `test_llm_json_repair.py` / the Phase C suite already do,
driving the REAL prompt construction, REAL `chat_json` parsing, and REAL
`JudgeVerdictSchema` validation for each of the nine canonical M11 v2
held-out cases. This proves the plumbing (prompt content reaches the model,
the model's structured response round-trips correctly for every verdict
type, channel separation still holds) is wired correctly for each boundary
— it does NOT prove the live model actually returns these verdicts for
these inputs. That is a live-evaluation question, explicitly out of scope
here and not authorized by this task.

    python -m pytest backend/tests/unit/test_evaluation_m11_not_applicable_remediation.py -v
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import agents.llm as llm  # noqa: E402
from agents.schemas import JudgeVerdictSchema  # noqa: E402
from evaluation.core.judge import JUDGE_PROMPT_VERSION, _SYSTEM_PROMPT, invoke_judge  # noqa: E402


def _invoke_judge_with_mocked_verdict(claim: str, evidence: str, verdict: str, rationale: str):
    """Drives the REAL invoke_judge -> chat_json -> _SYSTEM_PROMPT/_build_user_message
    path, stubbing only the network call, exactly like _chat_json_with_raw in
    test_llm_json_repair.py."""
    real = llm._generate_sync
    captured = {}

    def _generate_sync(system, user, model, *, usage_sink=None, temperature=None):
        captured["system"] = system
        captured["user"] = user
        return f'{{"verdict": "{verdict}", "rationale": "{rationale}"}}'

    llm._generate_sync = _generate_sync
    try:
        result = asyncio.run(invoke_judge(claim, evidence))
        return result, captured
    finally:
        llm._generate_sync = real


# ---------------------------------------------------------------------------
# TEST 8 — prompt ordering + v3 exclusion (structural, not semantic)
# ---------------------------------------------------------------------------

def test_applicability_rule_precedes_contradicted_rule():
    applicability_marker = "first decide"
    contradicted_marker = "CONTRADICTED requires EVIDENCE to state a fact"
    i = _SYSTEM_PROMPT.index(applicability_marker)
    j = _SYSTEM_PROMPT.index(contradicted_marker)
    assert i < j, "the applicability rule must appear before the CONTRADICTED rule"


def test_rejected_v3_time_and_scope_axes_not_reintroduced():
    # The rejected v3 four-test block's TIME/SCOPE-specific markers must be
    # absent — this remediation is deliberately narrower than v3.
    v3_markers = [
        "(3) TIME:", "(4) SCOPE:", "applicable only if ALL four",
        "Verdict selection order", "structurally incapable of bearing",
        "evidentiary question CLAIM expresses",
    ]
    for marker in v3_markers:
        assert marker not in _SYSTEM_PROMPT, f"rejected v3 marker reintroduced: {marker!r}"


def test_applicability_rule_names_entity_and_quantity():
    # v3-na2's applicability test is entity + underlying quantity/business
    # fact — not the bare "property" noun v3-na1 used with no stated bound.
    assert "entity" in _SYSTEM_PROMPT.lower()
    assert "underlying quantity or business fact" in _SYSTEM_PROMPT


def test_applicability_rule_explicitly_excludes_tense_modality_polarity():
    # The v3-na1 regression (Case 06: modality; Case 07: tense) is addressed
    # by naming these axes explicitly as NOT determining applicability —
    # unlike test_applicability_rule_names_entity_and_property_only's old
    # v3-na1-era assertion, these words are now expected to be PRESENT,
    # paired with exclusion language.
    prompt = _SYSTEM_PROMPT
    for axis in ("tense", "modality", "polarity"):
        assert axis in prompt, f"v3-na2 must name {axis!r} explicitly"
    assert "still applicable" in prompt
    assert "None of those differences make EVIDENCE inapplicable" in prompt


def test_applicability_rule_gives_concrete_tense_modality_polarity_examples():
    # Matches Document 47 Rev 6 §7.3.1's own worked examples closely enough
    # to be recognizable as the same exclusion, not a vaguer restatement.
    assert "current-period figure offered against a future expectation" in _SYSTEM_PROMPT
    assert "statement about whether a disclosure exists" in _SYSTEM_PROMPT
    assert "increase versus a decrease" in _SYSTEM_PROMPT


def test_contradicted_rule_text_unchanged():
    # The approved v2 CONTRADICTED remediation must survive verbatim.
    v2_text = (
        "CONTRADICTED requires EVIDENCE to state a fact or substantive position "
        "that is itself incompatible with CLAIM. Evidence that merely fails to "
        "confirm CLAIM is not contradiction. In particular, absence of "
        "information, guidance, disclosure, or a stated position about CLAIM's "
        "subject does not by itself contradict CLAIM; when otherwise relevant, "
        "such evidence is UNSUPPORTED. A substantive statement that negates or "
        "opposes CLAIM's actual proposition can be CONTRADICTED, even if the "
        "statement uses words such as 'not' or 'no.'"
    )
    assert v2_text in _SYSTEM_PROMPT


def test_prompt_version_is_v3_na5():
    # v3-na5 adds the granularity/component-aggregate clause (M11 Phase H
    # remediation, Document 47 §7.3.1 Revision 6) — a distinct persisted
    # identity from "v3", "v3-na1", "v3-na2", "v3-na3", and "v3-na4", each of
    # which has genuinely different prompt content.
    assert JUDGE_PROMPT_VERSION == "v3-na5"


def test_applicability_rule_covers_modality_denial():
    # v3-na3's live run showed the modality clause (added in v3-na2) lacked
    # its own affirmative denial, unlike entity and tense/level-change —
    # Case 06 (disclosure-existence uncertainty) regressed to NOT_APPLICABLE.
    # This is the matching denial clause v3-na4 adds, mirroring Document 47
    # Rev 6 §7.3.1 item 1's own already-ratified sentence.
    prompt = _SYSTEM_PROMPT
    assert "a statement of fact and an expectation, plan, or statement about whether a disclosure exists about that same fact" in prompt
    assert "are the same underlying quantity or business fact, not different ones" in prompt


def test_modality_denial_clause_sits_inside_the_existing_modality_exclusion():
    # Must extend the EXISTING modality parenthetical, not stand alone as a
    # new axis or a new sentence — same structural requirement already
    # enforced for the level/change clause.
    prompt = _SYSTEM_PROMPT
    modality_clause_start = prompt.index("in modality (e.g. a statement of fact")
    denial_idx = prompt.index("a statement of fact and an expectation, plan, or statement about whether a disclosure exists about that same fact")
    polarity_idx = prompt.index("or in polarity (e.g. an")
    assert modality_clause_start < denial_idx < polarity_idx, (
        "modality denial clause must sit inside the modality parenthetical, "
        "before the polarity clause — not as a standalone axis"
    )


def test_v3na3_level_change_wording_unchanged_by_v3na4():
    # v3-na4 must not touch the clause that fixed Case 07.
    prompt = _SYSTEM_PROMPT
    assert "reported level and a claim about that same quantity's change" in prompt
    assert "a level and its own change are the same underlying quantity, not different ones" in prompt


def test_polarity_wording_byte_identical_to_v3na3():
    prompt = _SYSTEM_PROMPT
    assert "or in polarity (e.g. an increase versus a decrease)" in prompt


def test_applicability_rule_covers_level_versus_change():
    # Document 47 Rev 6 §7.3.1 groups "level versus change" with "period"
    # under one tense/aspect axis; v3-na2 stated only the period half. This
    # is the specific clause v3-na3 adds to close that gap.
    prompt = _SYSTEM_PROMPT
    assert "reported level and a claim about that same quantity's change" in prompt
    assert "a level and its own change are the same underlying quantity, not different ones" in prompt


def test_level_change_clause_sits_inside_the_existing_tense_exclusion():
    # Must extend the EXISTING tense/time-period parenthetical, not stand
    # alone as a new axis or a new sentence.
    prompt = _SYSTEM_PROMPT
    tense_clause_start = prompt.index("when it differs from CLAIM in tense or time period")
    level_change_idx = prompt.index("reported level and a claim about that same quantity's change")
    modality_idx = prompt.index("in modality (e.g. a statement of fact")
    assert tense_clause_start < level_change_idx < modality_idx, (
        "level/change clause must sit inside the tense/time-period parenthetical, "
        "before the modality clause — not as a standalone axis"
    )


def test_applicability_rule_does_not_generalize_to_related_metric_equivalence():
    # Guard against the overcorrection risk: this must remain scoped to a
    # quantity and its OWN change over time, never "related metrics are the
    # same property" — that tier is Document 47 Rev 6's own open boundary
    # (MORE EVIDENCE REQUIRED) and must not be silently resolved here.
    prompt = _SYSTEM_PROMPT.lower()
    for forbidden in ("related metric", "related metrics are", "same property as gross margin",
                      "gross margin", "ebitda", "free cash flow", "headcount", "customer count",
                      "same topic"):
        assert forbidden not in prompt, f"overcorrection into related-metric equivalence: {forbidden!r}"


def test_schema_not_applicable_description_updated():
    desc = JudgeVerdictSchema.model_fields["verdict"].description
    assert "different entity" in desc
    assert "underlying quantity or business fact" in desc
    assert "tense, modality, or polarity" in desc
    assert "level versus that same quantity's change" in desc
    assert "fails to confirm the claim is UNSUPPORTED, not NOT_APPLICABLE" in desc
    # v3's rejected four-test taxonomy must not reappear in the schema either.
    assert "entity, property, time, or scope applicability" not in desc


def test_schema_does_not_generalize_to_related_metric_equivalence():
    desc = JudgeVerdictSchema.model_fields["verdict"].description.lower()
    for forbidden in ("related metric", "gross margin", "ebitda", "free cash flow",
                      "headcount", "customer count", "same topic"):
        assert forbidden not in desc, f"overcorrection into related-metric equivalence: {forbidden!r}"


def test_schema_covers_modality_denial():
    desc = JudgeVerdictSchema.model_fields["verdict"].description
    assert "disclosure-existence statement about that same fact" in desc


def test_schema_enum_and_other_fields_unchanged():
    fields = JudgeVerdictSchema.model_fields
    assert set(fields) == {"verdict", "rationale"}
    assert fields["verdict"].annotation.__args__ == (
        "SUPPORTED", "CONTRADICTED", "UNSUPPORTED", "NOT_APPLICABLE",
    )


# ---------------------------------------------------------------------------
# TESTS 1-7 (+ 08/09) — plumbing/regression for each canonical boundary
# ---------------------------------------------------------------------------

_CASES = [
    # (name, claim, evidence, expected_verdict)  — the nine M11 v2 held-out cases
    ("case01_genuine_contradiction",
     "The company expects revenue growth next quarter.",
     "The company expects revenue to decline next quarter.",
     "CONTRADICTED"),
    ("case02_alt_wording_contradiction",
     "Revenue will increase next quarter.",
     "Revenue will decrease next quarter.",
     "CONTRADICTED"),
    ("case03_substantive_negated_belief",
     "Management expects revenue to grow next quarter.",
     "Management does not expect revenue to grow next quarter.",
     "CONTRADICTED"),
    ("case04_explicit_category_absence",
     "The company expects revenue growth next quarter.",
     "The company provides no guidance regarding revenue for next quarter.",
     "UNSUPPORTED"),
    ("case05_absence_inside_disclosure",
     "The company expects revenue growth next quarter.",
     "The company's revenue guidance for next quarter does not include a specific figure.",
     "UNSUPPORTED"),
    ("case06_disclosure_uncertainty",
     "The company expects revenue growth next quarter.",
     "The company has not determined whether it will provide revenue guidance for next quarter.",
     "UNSUPPORTED"),
    ("case07_relevant_silence",
     "The company expects revenue growth next quarter.",
     "The company's revenue this quarter was $50 million.",
     "UNSUPPORTED"),
    ("case08_different_entity",
     "Company X expects revenue growth next quarter.",
     "Company Y's revenue increased this quarter.",
     "NOT_APPLICABLE"),
    ("case09_unrelated_disclosure",
     "The company expects revenue growth next quarter.",
     "The company's primary business is manufacturing consumer electronics.",
     "NOT_APPLICABLE"),
]


def test_all_nine_boundary_cases_round_trip_through_the_real_pipeline():
    for name, claim, evidence, expected in _CASES:
        result, captured = _invoke_judge_with_mocked_verdict(
            claim, evidence, expected, "mocked rationale for " + name,
        )
        assert isinstance(result, JudgeVerdictSchema), name
        assert result.verdict == expected, name
        # Channel separation: claim/evidence reach the user message, not the
        # system prompt (Document 47 §10.1), for every one of the nine cases.
        assert claim in captured["user"], name
        assert evidence in captured["user"], name
        assert claim not in captured["system"], name
        assert evidence not in captured["system"], name


def test_case08_different_entity_not_applicable_round_trips():
    result, _ = _invoke_judge_with_mocked_verdict(
        "Company X expects revenue growth next quarter.",
        "Company Y's revenue increased this quarter.",
        "NOT_APPLICABLE", "different entity",
    )
    assert result.verdict == "NOT_APPLICABLE"


def test_case09_unrelated_disclosure_not_applicable_round_trips():
    result, _ = _invoke_judge_with_mocked_verdict(
        "The company expects revenue growth next quarter.",
        "The company's primary business is manufacturing consumer electronics.",
        "NOT_APPLICABLE", "unrelated business subject",
    )
    assert result.verdict == "NOT_APPLICABLE"


def test_case04_explicit_absence_still_maps_to_unsupported_not_not_applicable():
    # Direct regression guard for the v3 failure mode: relevant absence must
    # remain reachable as UNSUPPORTED, never silently forced to NOT_APPLICABLE
    # by anything in the plumbing (the model's own choice is out of scope —
    # this only proves the harness doesn't rewrite it either way).
    result, _ = _invoke_judge_with_mocked_verdict(
        "The company expects revenue growth next quarter.",
        "The company provides no guidance regarding revenue for next quarter.",
        "UNSUPPORTED", "explicit absence",
    )
    assert result.verdict == "UNSUPPORTED"


def test_case01_genuine_contradiction_still_reachable():
    result, _ = _invoke_judge_with_mocked_verdict(
        "The company expects revenue growth next quarter.",
        "The company expects revenue to decline next quarter.",
        "CONTRADICTED", "genuine contradiction",
    )
    assert result.verdict == "CONTRADICTED"


# ---------------------------------------------------------------------------
# v3-na2 regression guards — Case 06 (modality) and Case 07 (tense), the two
# boundaries the v3-na1 live run broke. These prove the harness's plumbing
# does not force either verdict either way; whether the LIVE model now
# respects the new wording is a separate, unauthorized-here live question.
# ---------------------------------------------------------------------------

def test_case06_disclosure_uncertainty_still_reachable_as_unsupported():
    result, _ = _invoke_judge_with_mocked_verdict(
        "The company expects revenue growth next quarter.",
        "The company has not determined whether it will provide revenue guidance for next quarter.",
        "UNSUPPORTED", "disclosure-existence uncertainty, same underlying quantity",
    )
    assert result.verdict == "UNSUPPORTED"


def test_case07_relevant_silence_still_reachable_as_unsupported():
    result, _ = _invoke_judge_with_mocked_verdict(
        "The company expects revenue growth next quarter.",
        "The company's revenue this quarter was $50 million.",
        "UNSUPPORTED", "current-period figure, same underlying quantity",
    )
    assert result.verdict == "UNSUPPORTED"


def test_same_quantity_different_tense_period_remains_reachable_as_unsupported():
    # Same underlying quantity (revenue), differing only in tense/time period
    # (current-period actual vs. future expectation) — must remain reachable
    # as UNSUPPORTED, not forced toward NOT_APPLICABLE by the plumbing.
    result, _ = _invoke_judge_with_mocked_verdict(
        "The company expects revenue growth next quarter.",
        "The company's revenue last quarter was $45 million.",
        "UNSUPPORTED", "historical figure offered against a forward expectation",
    )
    assert result.verdict == "UNSUPPORTED"


def test_same_quantity_different_modality_remains_reachable_as_unsupported():
    # Same underlying quantity, differing only in modality (a statement about
    # whether disclosure/guidance exists vs. a substantive expectation).
    result, _ = _invoke_judge_with_mocked_verdict(
        "The company expects revenue growth next quarter.",
        "The company has not decided whether it will issue revenue guidance for next quarter.",
        "UNSUPPORTED", "disclosure-existence modality, same underlying quantity",
    )
    assert result.verdict == "UNSUPPORTED"


def test_same_quantity_different_polarity_remains_reachable_as_contradicted():
    # Same underlying quantity, opposite polarity (increase vs. decrease) —
    # this is CONTRADICTED, not NOT_APPLICABLE, per Rev 6's contradiction rule.
    result, _ = _invoke_judge_with_mocked_verdict(
        "Revenue will increase next quarter.",
        "Revenue will decrease next quarter.",
        "CONTRADICTED", "opposite polarity on the same underlying quantity",
    )
    assert result.verdict == "CONTRADICTED"


def test_level_versus_change_remains_reachable_as_unsupported():
    # v3-na3's specific target: Case 07's exact live-observed failure shape
    # ("expected revenue growth" — change — vs. "revenue was $50 million" —
    # level) must remain reachable as UNSUPPORTED through the real pipeline,
    # not forced toward NOT_APPLICABLE by anything in the plumbing. This does
    # not prove the live model complies — only that the harness doesn't.
    result, _ = _invoke_judge_with_mocked_verdict(
        "The company expects revenue growth next quarter.",
        "The company's revenue this quarter was $50 million.",
        "UNSUPPORTED", "same quantity (revenue), level vs. its own expected change",
    )
    assert result.verdict == "UNSUPPORTED"


if __name__ == "__main__":
    test_applicability_rule_precedes_contradicted_rule()
    test_rejected_v3_time_and_scope_axes_not_reintroduced()
    test_applicability_rule_names_entity_and_quantity()
    test_applicability_rule_explicitly_excludes_tense_modality_polarity()
    test_applicability_rule_gives_concrete_tense_modality_polarity_examples()
    test_contradicted_rule_text_unchanged()
    test_prompt_version_is_v3_na5()
    test_applicability_rule_covers_level_versus_change()
    test_level_change_clause_sits_inside_the_existing_tense_exclusion()
    test_applicability_rule_covers_modality_denial()
    test_modality_denial_clause_sits_inside_the_existing_modality_exclusion()
    test_v3na3_level_change_wording_unchanged_by_v3na4()
    test_polarity_wording_byte_identical_to_v3na3()
    test_applicability_rule_does_not_generalize_to_related_metric_equivalence()
    test_schema_not_applicable_description_updated()
    test_schema_does_not_generalize_to_related_metric_equivalence()
    test_schema_covers_modality_denial()
    test_schema_enum_and_other_fields_unchanged()
    test_all_nine_boundary_cases_round_trip_through_the_real_pipeline()
    test_case08_different_entity_not_applicable_round_trips()
    test_case09_unrelated_disclosure_not_applicable_round_trips()
    test_case04_explicit_absence_still_maps_to_unsupported_not_not_applicable()
    test_case01_genuine_contradiction_still_reachable()
    test_case06_disclosure_uncertainty_still_reachable_as_unsupported()
    test_case07_relevant_silence_still_reachable_as_unsupported()
    test_same_quantity_different_tense_period_remains_reachable_as_unsupported()
    test_same_quantity_different_modality_remains_reachable_as_unsupported()
    test_same_quantity_different_polarity_remains_reachable_as_contradicted()
    test_level_versus_change_remains_reachable_as_unsupported()
    print("all M11 NOT_APPLICABLE remediation tests passed")
