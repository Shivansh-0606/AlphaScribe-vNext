"""Unit check for agents/learning_nodes.py's pure citation post-processor
(03_Learning_Backend_Design.md §5.2 — the Law 3 enforcement that replaces
Learning's fact-checker). No LLM, no DB.

    python backend/tests/unit/test_learning_nodes.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.learning_nodes import _build_user_message, _postprocess_citations


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


if __name__ == "__main__":
    test_valid_citations_are_kept_and_recorded_in_order()
    test_out_of_range_citation_is_stripped_not_left_dangling()
    test_zero_citation_marker_is_out_of_range()
    test_no_citations_at_all_yields_empty_cited_list()
    test_duplicate_citations_recorded_once_in_first_appearance_order()
    test_empty_docs_means_every_citation_is_out_of_range()
    test_user_message_includes_prior_context_only_when_present()
    test_user_message_caps_prior_brief_at_1200_chars()
    print("ok: citation post-processor strips out-of-range markers, records first-seen order; "
          "user message assembly includes/omits prior-context block correctly")
