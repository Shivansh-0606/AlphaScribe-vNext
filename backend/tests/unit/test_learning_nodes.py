"""Unit check for agents/learning_nodes.py's pure citation post-processor
(03_Learning_Backend_Design.md §5.2 — the Law 3 enforcement that replaces
Learning's fact-checker), the CJK-bracket citation-marker normalizer (Learning
hardening-pass brief Finding A), and `explainer_node` itself with `chat_text`
monkeypatched. No real LLM call, no DB.

    python backend/tests/unit/test_learning_nodes.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import agents.learning_nodes as learning_nodes  # noqa: E402
from agents.learning_nodes import (  # noqa: E402
    _build_user_message, _normalize_citation_markers, _postprocess_citations, explainer_node,
)


def test_valid_citations_are_kept_and_recorded_in_order():
    text = "Revenue grew [1]. Margins held [2]. As noted [1] again."
    cleaned, cited = _postprocess_citations(text, num_docs=2)
    assert cleaned == text
    assert cited == [1, 2]


def test_out_of_range_citation_is_stripped_not_left_dangling():
    text = "Revenue grew [1]. Also [9] which does not exist."
    cleaned, cited = _postprocess_citations(text, num_docs=3)
    assert "[9]" not in cleaned
    assert "[1]" in cleaned
    assert cited == [1]


def test_zero_citation_marker_is_out_of_range():
    # 1-based indexing — [0] must never validate even with docs present.
    text = "A claim with [0] in it."
    cleaned, cited = _postprocess_citations(text, num_docs=5)
    assert "[0]" not in cleaned
    assert cited == []


def test_no_citations_at_all_yields_empty_cited_list():
    text = "A purely qualitative explanation with no markers."
    cleaned, cited = _postprocess_citations(text, num_docs=4)
    assert cleaned == text
    assert cited == []


def test_duplicate_citations_recorded_once_in_first_appearance_order():
    text = "[3] then [1] then [3] again then [1] once more."
    _, cited = _postprocess_citations(text, num_docs=3)
    assert cited == [3, 1]


def test_empty_docs_means_every_citation_is_out_of_range():
    text = "Claims a source [1] that cannot exist."
    cleaned, cited = _postprocess_citations(text, num_docs=0)
    assert "[1]" not in cleaned
    assert cited == []


def test_user_message_includes_prior_context_only_when_present():
    state = {"concept": "operating leverage", "ticker": "ACME", "company_name": "Acme Corp"}
    msg = _build_user_message(state, docs=[])
    assert "operating leverage" in msg
    assert "Acme Corp (ACME)" in msg
    assert "latest brief found" not in msg


def test_user_message_caps_prior_brief_at_1200_chars():
    state = {
        "concept": "free cash flow", "ticker": "ACME",
        "prior_brief": "x" * 5000, "prior_financials": {"revenue": "$1B"},
    }
    msg = _build_user_message(state, docs=[])
    assert "latest brief found" in msg
    # Only the first 1200 chars of the (5000-char) prior brief should appear.
    assert "x" * 1200 in msg
    assert "x" * 1201 not in msg


# --------------------------------------------------------------------------- #
# _normalize_citation_markers (Learning hardening-pass brief Finding A)
# --------------------------------------------------------------------------- #
def test_normalize_converts_confirmed_lenticular_brackets_to_ascii():
    # The exact character pair Docs generator 2 captured live on both the
    # no-context and context_report_id repros: 【n】 (U+3010/U+3011).
    assert _normalize_citation_markers("Revenue grew【1】.") == "Revenue grew[1]."


def test_normalize_converts_defensive_tortoise_shell_brackets_to_ascii():
    assert _normalize_citation_markers("See〔2〕.") == "See[2]."


def test_normalize_converts_fullwidth_square_brackets_via_nfkc():
    assert _normalize_citation_markers("See［3］.") == "See[3]."


def test_normalize_does_not_turn_fullwidth_parens_into_citation_brackets():
    # A deliberate boundary, not an oversight: fullwidth/ASCII parens are
    # NFKC-normalized (fullwidth -> ASCII) but never mapped to square
    # brackets. Parens were never the citation format the prompt asks for --
    # treating "(4.2%)" as citation marker "4" would be a false positive on
    # ordinary parenthetical figures, not a fix.
    normalized = _normalize_citation_markers("Margin was down (（4.2）%).")
    assert normalized == "Margin was down ((4.2)%)."
    _, cited = _postprocess_citations(normalized, num_docs=5)
    assert cited == []


def test_normalized_lenticular_citations_pass_the_postprocessor_gate():
    text = "Revenue grew【1】. Margin held【2】."
    cleaned, cited = _postprocess_citations(_normalize_citation_markers(text), num_docs=2)
    assert cleaned == "Revenue grew[1]. Margin held[2]."
    assert cited == [1, 2]


# --------------------------------------------------------------------------- #
# explainer_node end-to-end (chat_text monkeypatched) -- the two live repros
# --------------------------------------------------------------------------- #
def test_explainer_node_grounds_no_context_explanation_with_lenticular_citations():
    # Equivalent of the brief's run A/C: a starter-chip concept question, no
    # context_report_id, real content the model correctly grounds but marks
    # with 【n】 instead of [n].
    async def _lenticular_response(*_a, **_k):
        return (
            "Operating margin measures how much profit a company keeps from each "
            "dollar of revenue after operating expenses【1】. For NVIDIA, "
            "this figure reflects strong cost discipline relative to revenue "
            "growth【2】.\n\nWhat might cause operating margin to compress "
            "in a future quarter?"
        )

    original = learning_nodes.chat_text
    learning_nodes.chat_text = _lenticular_response
    try:
        state = {
            "concept": "operating margin", "ticker": "NVDA",
            "source_documents": [
                {"source": "10-Q FY25 Q1", "chunk_idx": 1, "text": "..."},
                {"source": "10-Q FY25 Q1", "chunk_idx": 2, "text": "..."},
            ],
        }
        result = asyncio.run(explainer_node(state))
    finally:
        learning_nodes.chat_text = original

    assert result["cited_sources"] == [1, 2]
    assert "[1]" in result["explanation"] and "[2]" in result["explanation"]
    assert "【" not in result["explanation"]  # no raw CJK bracket left in persisted text
    assert result["trace"][0]["status"] == "ok"


def test_explainer_node_grounds_context_report_id_explanation_with_lenticular_citations():
    # Equivalent of the brief's run F/G: a context_report_id ("Explain This")
    # follow-up question, same lenticular-bracket failure mode, 2/2 in the
    # live sample.
    async def _lenticular_response(*_a, **_k):
        return (
            "NVIDIA's Data Center segment revenue is growing quickly because "
            "demand for AI infrastructure is outpacing available "
            "supply【1】, which the company describes as Blackwell demand "
            "exceeding production capacity【2】.\n\nHow might supply "
            "constraints affect pricing power next quarter?"
        )

    original = learning_nodes.chat_text
    learning_nodes.chat_text = _lenticular_response
    try:
        state = {
            "concept": "Data Center segment revenue", "ticker": "NVDA",
            "context_report_id": "bb355bde-976e-483f-8866-8db9c1c64985",
            "prior_brief": "NVIDIA Data Center revenue rose sharply this quarter...",
            "source_documents": [
                {"source": "10-Q FY25 Q1", "chunk_idx": 1, "text": "..."},
                {"source": "10-Q FY25 Q1", "chunk_idx": 2, "text": "..."},
            ],
        }
        result = asyncio.run(explainer_node(state))
    finally:
        learning_nodes.chat_text = original

    assert result["cited_sources"] == [1, 2]
    assert "【" not in result["explanation"]
    assert result["trace"][0]["status"] == "ok"


if __name__ == "__main__":
    test_valid_citations_are_kept_and_recorded_in_order()
    test_out_of_range_citation_is_stripped_not_left_dangling()
    test_zero_citation_marker_is_out_of_range()
    test_no_citations_at_all_yields_empty_cited_list()
    test_duplicate_citations_recorded_once_in_first_appearance_order()
    test_empty_docs_means_every_citation_is_out_of_range()
    test_user_message_includes_prior_context_only_when_present()
    test_user_message_caps_prior_brief_at_1200_chars()
    test_normalize_converts_confirmed_lenticular_brackets_to_ascii()
    test_normalize_converts_defensive_tortoise_shell_brackets_to_ascii()
    test_normalize_converts_fullwidth_square_brackets_via_nfkc()
    test_normalize_does_not_turn_fullwidth_parens_into_citation_brackets()
    test_normalized_lenticular_citations_pass_the_postprocessor_gate()
    test_explainer_node_grounds_no_context_explanation_with_lenticular_citations()
    test_explainer_node_grounds_context_report_id_explanation_with_lenticular_citations()
    print("ok: citation post-processor + CJK-bracket normalization + explainer_node end-to-end "
          "(both live repro shapes) all pass")
