"""Unit tests for `agents/filing_sections.py` — the M14 analysis-time
section-location realization (Document 65 OAQ-1(D) Alternative B) that cleared
the §20.1 validation gate.

Offline: no network, no LLM, no MongoDB (the LLM ambiguity path is exercised
with an injected fake classifier).

    python -m pytest backend/tests/unit/test_filing_sections.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents import filing_sections as fs


# --- normalization ------------------------------------------------------- #
def test_normalize_decodes_entities_and_folds_punctuation():
    assert fs.normalize_text("M&amp;A") == "M&A"
    assert "MANAGEMENT'S DISCUSSION" in fs.normalize_text("MANAGEMENT&#8217;S DISCUSSION")
    assert fs.normalize_text("Risk&#160;Factors") == "Risk Factors"          # nbsp -> space
    assert fs.normalize_text("“it’s”") == '"it\'s"'
    assert fs.normalize_text("a\n\n\n\n\nb  ") == "a\n\nb"


# --- heading detection -------------------------------------------------- #
def test_inline_risk_factors_heading_is_substantive():
    t = fs.normalize_text("... in this Quarterly Report on Form 10-Q. ITEM 1A. RISK FACTORS "
                          "Our operations and financial results are subject to various risks "
                          "and uncertainties, including the factors discussed in Part I.")
    m = fs._heading_of_kind(t, "rf")
    assert m and fs.is_substantive(t, m, "rf") is True and fs.is_toc_chunk(t) is False


def test_edgar_possessive_and_non_possessive_mdna_headings():
    poss = fs.normalize_text("33 PART II Item 7 ITEM 7. MANAGEMENT&#8217;S DISCUSSION AND ANALYSIS OF "
                             "FINANCIAL CONDITION AND RESULTS OF OPERATIONS The following Management&#8217;s "
                             "Discussion and Analysis is intended to help the reader understand results.")
    non_poss = fs.normalize_text("Integrated Annual Report 2025-26 6 7 Management Discussion and Analysis "
                                 "Financial Performance and Review Operating Environment global economic "
                                 "expansion continued with growth estimated at three point four percent.")
    for t in (poss, non_poss):
        m = fs._heading_of_kind(t, "mda")
        assert m and fs.is_substantive(t, m, "mda") is True


def test_ris_k_factors_tag_strip_artifact_is_tolerated():
    t = fs.normalize_text("PART I Item 1A ITEM 1A. RIS K FACTORS Our operations and financial "
                          "results are subject to various risks that could adversely affect the business.")
    m = fs._heading_of_kind(t, "rf")
    assert m and fs.is_substantive(t, m, "rf") is True


# --- TOC discrimination ---------------------------------------------------- #
def test_contents_page_lines_are_toc():
    assert fs.is_toc_chunk(fs.normalize_text(
        "Item 1A. Risk Factors 14 Item 1B. Unresolved Staff Comments 29 "
        "Item 1C. Cybersecurity 32 Item 2. Properties 33 Item 3. Legal Proceedings 34")) is True
    assert fs.is_toc_chunk(fs.normalize_text(
        "Corporate Overview 2 Reliance at a Glance 3 Value Creation 4 Chairman Statement 6 "
        "Financial Highlights 7 Business Overview 9 Retail 14 Digital Services 17 Media 21")) is True


def test_real_mdna_start_chunk_with_two_item_tokens_is_not_toc():
    assert fs.is_toc_chunk(fs.normalize_text(
        "chases and dividends. 32 PART II Item 6 ITEM 6. [R ESERVED] 33 PART II Item 7 ITEM 7. "
        "MANAGEMENT&#8217;S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS "
        "The following Management&#8217;s Discussion and Analysis is intended to help the reader "
        "understand the results of operations and financial condition of the company.")) is False


def test_quoted_and_parenthetical_cross_reference_is_not_substantive():
    t = fs.normalize_text('We describe risks in "Risk Factors," "Management’s Discussion and Analysis of '
                          'Financial Condition and Results of Operations," and elsewhere '
                          '(Part II, Item 7A of this Form 10-K). Readers are cautioned.')
    for kind in ("rf", "mda"):
        m = fs._heading_of_kind(t, kind)
        assert (m is None) or (fs.is_substantive(t, m, kind) is False)


# --- section location + boundary ---------------------------------------- #
_FAKE_ERR = "LLM must not be called when a substantive heading exists"


async def _boom(_text):  # pragma: no cover
    raise AssertionError(_FAKE_ERR)


def test_first_substantive_occurrence_selected_over_earlier_toc_and_bounded():
    chunks = [
        {"chunk_idx": 0, "text": "Item 1A. Risk Factors 14 Item 1B. Unresolved Staff Comments 29 "
                                 "Item 1C. Cybersecurity 32 Item 2. Properties 40"},
        {"chunk_idx": 1, "text": "unrelated business narrative about segments and products."},
        {"chunk_idx": 2, "text": "ITEM 1A. RISK FACTORS Our operations and financial results are subject "
                                 "to various risks and uncertainties, including those described below, that "
                                 "could adversely affect our business and results of operations."},
        {"chunk_idx": 3, "text": "more risk narrative describing competitive and regulatory pressures."},
        {"chunk_idx": 4, "text": "ITEM 1B. UNRESOLVED STAFF COMMENTS None."},
    ]
    res = asyncio.run(fs.locate_section(chunks, "rf", classify_fn=_boom))
    assert res["predicted_present"] and res["basis"] == "structural"
    assert res["range"] == [2, 3] and res["end_established"] is True
    assert res["boundary_rule"] == "next-different-heading"
    assert 0 in res["toc_chunks"]


def test_missing_end_boundary_collapses_to_single_chunk_partial():
    chunks = [
        {"chunk_idx": 0, "text": "intro"},
        {"chunk_idx": 1, "text": "ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND "
                                 "RESULTS OF OPERATIONS the following discussion and analysis should be read "
                                 "together with the financial statements and covers results for the period."},
        {"chunk_idx": 2, "text": "revenue increased on higher demand and pricing across segments."},
        {"chunk_idx": 3, "text": "general narrative with no further section heading of any kind."},
    ]
    res = asyncio.run(fs.locate_section(chunks, "mda", classify_fn=_boom))
    assert res["predicted_present"] and res["start_chunk"] == 1
    assert res["end_established"] is False and res["range"] == [1, 1]
    assert res["diagnostic_state"] == "located_partial_boundary"


def test_heading_absent_returns_not_located_no_range():
    chunks = [{"chunk_idx": i, "text": "narrative memo paragraph with no regulatory section headings " + str(i)}
              for i in range(3)]
    res = asyncio.run(fs.locate_section(chunks, "rf", classify_fn=_boom))
    assert res["predicted_present"] is False and res["range"] is None
    assert res["basis"] == "heading-absent"


# --- LLM ambiguity path ------------------------------------------------- #
class _Fixed:
    def __init__(self, label):
        self.label, self.calls = label, 0

    async def __call__(self, _t):
        self.calls += 1
        return {"label": self.label, "error": None}


class _Cycle:
    def __init__(self, labels):
        self.labels, self.i = labels, 0

    async def __call__(self, _t):
        lab = self.labels[self.i % len(self.labels)]
        self.i += 1
        return {"label": lab, "error": None}


def test_llm_invoked_k3_only_for_ambiguous_heading_candidate():
    rec = _Fixed("risk_factors")
    chunks = [
        {"chunk_idx": 0, "text": "Item 1A. Risk Factors 14 Item 1B. Unresolved Staff Comments 29 "
                                 "Item 1C. Cybersecurity 32 Item 2. Properties 40"},              # TOC
        {"chunk_idx": 1, "text": "our exposure to the risk factors, noted."},                    # non-substantive bare hit
        {"chunk_idx": 2, "text": "unrelated general narrative."},
    ]
    res = asyncio.run(fs.locate_section(chunks, "rf", classify_fn=rec))
    assert rec.calls == 3 and res["predicted_present"] and res["basis"] == "llm-ambiguous-candidate"
    assert res["start_chunk"] == 1


def test_llm_disagreement_and_wrong_majority_resolve_conservatively():
    chunks = [
        {"chunk_idx": 0, "text": "Item 1A. Risk Factors 14 Item 1B. Unresolved Staff Comments 29 "
                                 "Item 1C. Cybersecurity 32 Item 2. Properties 40"},
        {"chunk_idx": 1, "text": "our exposure to the risk factors, noted."},
    ]
    split = asyncio.run(fs.locate_section(chunks, "rf", classify_fn=_Cycle(["risk_factors", "mda", "other"])))
    assert split["predicted_present"] is False and split["range"] is None
    wrong = asyncio.run(fs.locate_section(chunks, "rf", classify_fn=_Fixed("other")))
    assert wrong["predicted_present"] is False and wrong["range"] is None


def test_classify_kv_majority_arithmetic():
    two_one = asyncio.run(fs.classify_kv("x", classify_fn=_Cycle(["mda", "mda", "other"]), k=3))
    assert two_one["strict_majority"] and two_one["majority"] == "mda"
    tie = asyncio.run(fs.classify_kv("x", classify_fn=_Cycle(["rf", "mda", "other"]), k=3))
    assert tie["strict_majority"] is False and tie["majority"] is None
