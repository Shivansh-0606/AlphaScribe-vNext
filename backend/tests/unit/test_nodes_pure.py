"""Unit check for the pure helpers in agents/nodes.py: _extract_candidate_claims
(decides what the fact-checker verifies — 05 §3.2) and _format_docs (the
budget-aware source truncation every prompt depends on). No LLM, no DB.

    python backend/tests/unit/test_nodes_pure.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.nodes import _extract_candidate_claims, _format_docs


def test_claims_require_numeric_evidence():
    draft = "Revenue grew 12% year over year. The team is optimistic. EPS was $1.64."
    claims = _extract_candidate_claims(draft)
    assert claims == ["Revenue grew 12% year over year.", "EPS was $1.64."]


def test_purely_qualitative_draft_extracts_zero_claims():
    # ponytail (nodes.py:200-205): the documented blind spot — a qualitative
    # fabrication with no numbers extracts nothing and is trivially accepted.
    draft = "Management is confident about the outlook. Growth continues."
    assert _extract_candidate_claims(draft) == []


def test_claims_dedupe_case_insensitively():
    draft = "Revenue grew 12%. revenue grew 12%. Revenue grew 12%."
    claims = _extract_candidate_claims(draft)
    assert claims == ["Revenue grew 12%."]


def test_claims_capped_at_twelve():
    draft = " ".join(f"Metric {i} was {i}%." for i in range(20))
    claims = _extract_candidate_claims(draft)
    assert len(claims) == 12


def test_claims_recognize_bps_and_pp_and_dollar_units():
    draft = "Margin expanded 50bps. Share fell 3pp. Buyback totaled $2.5B."
    claims = _extract_candidate_claims(draft)
    assert len(claims) == 3


def test_format_docs_numbers_sequentially_and_joins_with_separator():
    docs = [
        {"source": "10-Q", "chunk_idx": 0, "text": "First excerpt."},
        {"source": "10-K", "chunk_idx": 1, "text": "Second excerpt."},
    ]
    out = _format_docs(docs)
    assert out == "[1] 10-Q (chunk 0)\nFirst excerpt.\n\n---\n\n[2] 10-K (chunk 1)\nSecond excerpt."


def test_format_docs_truncates_at_max_chars_without_splitting_a_block():
    # Each block is atomic: it is either included whole or dropped, never cut
    # mid-block (nodes.py:28-30) — a truncated citation would be worse than a
    # missing one.
    docs = [
        {"source": "A", "chunk_idx": 0, "text": "x" * 50},
        {"source": "B", "chunk_idx": 1, "text": "y" * 50},
        {"source": "C", "chunk_idx": 2, "text": "z" * 50},
    ]
    out = _format_docs(docs, max_chars=70)
    assert "[1]" in out and "[2]" not in out and "[3]" not in out


def test_format_docs_empty_list():
    assert _format_docs([]) == ""


if __name__ == "__main__":
    test_claims_require_numeric_evidence()
    test_purely_qualitative_draft_extracts_zero_claims()
    test_claims_dedupe_case_insensitively()
    test_claims_capped_at_twelve()
    test_claims_recognize_bps_and_pp_and_dollar_units()
    test_format_docs_numbers_sequentially_and_joins_with_separator()
    test_format_docs_truncates_at_max_chars_without_splitting_a_block()
    test_format_docs_empty_list()
    print("ok: _extract_candidate_claims numeric filter/dedupe/cap; _format_docs numbering + budget truncation")
