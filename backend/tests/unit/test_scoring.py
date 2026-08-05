"""Unit check for agents/scoring.py's RAGAS-lite metrics (compute_scorecard).

Pure, dependency-free (06 C-7) — no DB, no network, no LLM. Was flagged in
05 §3.2 as the highest-value untested function in the codebase: every quality
claim about a report rests on it, and it had zero direct tests.

    python backend/tests/unit/test_scoring.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.scoring import compute_scorecard


def test_faithfulness_from_verified_claims():
    report = {
        "draft_report": "Revenue was $10B [1].",
        "source_documents": [{"chunk_idx": 0}],
        "query": "revenue",
        "verified_claims": [{"supported": True}, {"supported": False}],
        "fact_check_status": False,
    }
    card = compute_scorecard(report)
    assert card["faithfulness"] == 0.5
    assert card["n_claims"] == 2
    assert card["n_supported"] == 1


def test_faithfulness_trivial_accept_when_no_numeric_claims():
    # No verified_claims at all, but the fact-checker trivially passed
    # (nodes.py:238-246) -> credited as fully faithful, per scoring.py:37-39.
    report = {"draft_report": "All good, no numbers here.", "source_documents": [],
              "query": "", "verified_claims": [], "fact_check_status": True}
    assert compute_scorecard(report)["faithfulness"] == 1.0


def test_faithfulness_zero_when_fact_check_failed_with_no_claims():
    report = {"draft_report": "", "source_documents": [], "query": "",
              "verified_claims": [], "fact_check_status": False}
    assert compute_scorecard(report)["faithfulness"] == 0.0


def test_context_precision_counts_distinct_valid_citations():
    docs = [{}, {}, {}]  # 3 source docs, indices 1..3 are valid
    draft = "Claim [1]. Another [2]. Repeat [1] again. Out of range [9]."
    card = compute_scorecard({"draft_report": draft, "source_documents": docs,
                               "query": "", "verified_claims": [], "fact_check_status": True})
    # [1] and [2] are distinct valid cites out of 3 docs; [9] is out of range and ignored.
    assert card["cited_sources"] == [1, 2]
    assert card["context_precision"] == round(2 / 3, 3)


def test_context_precision_zero_with_no_source_docs():
    card = compute_scorecard({"draft_report": "text [1]", "source_documents": [],
                               "query": "", "verified_claims": [], "fact_check_status": True})
    assert card["context_precision"] == 0.0


def test_answer_relevance_token_overlap():
    report = {
        "draft_report": "The operating margin expanded due to cost discipline.",
        "source_documents": [], "verified_claims": [], "fact_check_status": True,
        "query": "What is the operating margin trend?",
    }
    card = compute_scorecard(report)
    # query tokens (stop-words removed): operating, margin, trend
    # draft contains "operating" and "margin" -> 2/3
    assert round(card["answer_relevance"], 3) == round(2 / 3, 3)


def test_answer_relevance_zero_when_query_or_draft_empty():
    card = compute_scorecard({"draft_report": "", "source_documents": [],
                               "verified_claims": [], "fact_check_status": True, "query": "anything"})
    assert card["answer_relevance"] == 0.0


def test_overall_is_the_simple_average():
    report = {
        "draft_report": "x [1]", "source_documents": [{}],
        "verified_claims": [{"supported": True}], "fact_check_status": True,
        "query": "x",
    }
    card = compute_scorecard(report)
    expected = round((card["faithfulness"] + card["context_precision"] + card["answer_relevance"]) / 3.0, 3)
    assert card["overall"] == expected


def test_missing_fields_default_gracefully():
    # compute_scorecard is called on old report docs that may lack keys.
    assert compute_scorecard({}) == compute_scorecard({
        "draft_report": None, "source_documents": None, "query": None,
        "verified_claims": None, "fact_check_status": None,
    })


if __name__ == "__main__":
    test_faithfulness_from_verified_claims()
    test_faithfulness_trivial_accept_when_no_numeric_claims()
    test_faithfulness_zero_when_fact_check_failed_with_no_claims()
    test_context_precision_counts_distinct_valid_citations()
    test_context_precision_zero_with_no_source_docs()
    test_answer_relevance_token_overlap()
    test_answer_relevance_zero_when_query_or_draft_empty()
    test_overall_is_the_simple_average()
    test_missing_fields_default_gracefully()
    print("ok: compute_scorecard — faithfulness, context precision, answer relevance, overall, defaults")
