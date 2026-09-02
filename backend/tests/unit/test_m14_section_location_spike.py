"""Offline unit tests for the pure helpers of the M14 section-20.1
section-location validation spike (`backend/scripts/m14_section_location_spike.py`).

Diagnostic-tool tests only: no network, no LLM, no MongoDB. They exercise the
deterministic realization of Document 65 OAQ-1(D) Alternative B -- normalization,
heading recognition, TOC discrimination, substantive-heading selection,
structural boundary detection, conservative missing-boundary behaviour, and
the "LLM only for genuinely ambiguous heuristic candidates" / "conservative on
disagreement" rules (with an injected fake classifier).

    python -m pytest backend/tests/unit/test_m14_section_location_spike.py
"""
import asyncio
import importlib.util
import os
import sys

_BACKEND = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

_SPEC = importlib.util.spec_from_file_location(
    "m14_section_location_spike",
    os.path.join(_BACKEND, "scripts", "m14_section_location_spike.py"),
)
spike = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(spike)


# --------------------------------------------------------------------------- #
# 1. HTML entity decoding
# --------------------------------------------------------------------------- #
def test_html_entity_decoding_named_and_numeric():
    assert spike.normalize_text("M&amp;A") == "M&A"
    assert "MANAGEMENT'S DISCUSSION" in spike.normalize_text("MANAGEMENT&#8217;S DISCUSSION")
    # &#160; (nbsp) decodes and then folds to a plain space
    assert spike.normalize_text("Risk&#160;Factors") == "Risk Factors"
    assert spike.normalize_text("&lt;IR&gt;") == "<IR>"


# --------------------------------------------------------------------------- #
# 2. Unicode punctuation normalization
# --------------------------------------------------------------------------- #
def test_unicode_punctuation_folding():
    assert spike.normalize_text("it’s") == "it's"
    assert spike.normalize_text("“MD&A”") == '"MD&A"'
    assert spike.normalize_text("a–b—c") == "a-b-c"
    assert spike.normalize_text("x\xa0y") == "x y"


# --------------------------------------------------------------------------- #
# 3. Whitespace normalization
# --------------------------------------------------------------------------- #
def test_whitespace_collapse_and_strip():
    assert spike.normalize_text("  a   \t  b  ") == "a b"
    assert spike.normalize_text("a\n\n\n\n\nb") == "a\n\nb"
    assert spike.normalize_text("a \n  \n b") == "a\n\nb"


# --------------------------------------------------------------------------- #
# 4. Inline RF heading detection (not line-anchored)
# --------------------------------------------------------------------------- #
def test_inline_risk_factors_heading_is_substantive():
    t = spike.normalize_text(
        "the consolidated financial statements included elsewhere in this "
        "Quarterly Report on Form 10-Q. ITEM 1A. RISK FACTORS Our operations "
        "and financial results are subject to various risks and uncertainties, "
        "including the factors discussed in Part I."
    )
    m = spike._heading_of_kind(t, "rf")
    assert m is not None
    assert not spike.is_toc_chunk(t)
    assert spike.is_substantive(t, m, "rf") is True


def test_risk_factors_tolerates_internal_space_artifact():
    # EDGAR HTML tag stripping can leave "RIS K FACTORS"
    t = spike.normalize_text("PART I Item 1A ITEM 1A. RIS K FACTORS Our operations "
                             "and financial results are subject to various risks.")
    m = spike._heading_of_kind(t, "rf")
    assert m is not None and spike.is_substantive(t, m, "rf") is True


# --------------------------------------------------------------------------- #
# 5. EDGAR MD&A heading detection (possessive)
# --------------------------------------------------------------------------- #
def test_edgar_possessive_mdna_heading_is_substantive():
    t = spike.normalize_text(
        "33 PART II Item 7 ITEM 7. MANAGEMENT&#8217;S DISCUSSION AND ANALYSIS OF "
        "FINANCIAL CONDITION AND RESULTS OF OPERATIONS The following "
        "Management&#8217;s Discussion and Analysis is intended to help the reader "
        "understand the results of operations and financial condition."
    )
    m = spike._heading_of_kind(t, "mda")
    assert m is not None
    assert not spike.is_toc_chunk(t)
    assert spike.is_substantive(t, m, "mda") is True


# --------------------------------------------------------------------------- #
# 6. Non-possessive MD&A detection (Indian annual-report convention)
# --------------------------------------------------------------------------- #
def test_non_possessive_mdna_heading_is_substantive():
    t = spike.normalize_text(
        "Reliance Industries Limited Integrated Annual Report 2025-26 6 7 "
        "Management Discussion and Analysis Financial Performance and Review "
        "Operating Environment Global economic expansion continued with IMF "
        "estimating global growth at 3.4 percent for CY25."
    )
    m = spike._heading_of_kind(t, "mda")
    assert m is not None
    assert spike.is_substantive(t, m, "mda") is True


# --------------------------------------------------------------------------- #
# 7. TOC rejection
# --------------------------------------------------------------------------- #
def test_toc_chunk_with_item_page_numbers_is_rejected():
    toc = spike.normalize_text(
        "Item 1A. Risk Factors 14 Item 1B. Unresolved Staff Comments 29 "
        "Item 1C. Cybersecurity 32 Item 2. Properties 33 Item 3. Legal Proceedings 34"
    )
    assert spike.is_toc_chunk(toc) is True


def test_toc_chunk_with_contents_page_leaders_is_rejected():
    toc = spike.normalize_text(
        "Corporate Overview 2 Reliance at a Glance 3 Stakeholder Value Creation 4 "
        "Chairman Statement 6 Financial Highlights 7 Business Overview 9 Retail 14 "
        "Digital Services 17 Media and Entertainment 21 Oil to Chemicals 24"
    )
    assert spike.is_toc_chunk(toc) is True


def test_real_section_start_chunk_is_not_toc():
    # MSFT chunk-192 shape: two Item tokens but dominated by MD&A prose
    real = spike.normalize_text(
        "chases and dividends. 32 PART II Item 6 ITEM 6. [R ESERVED] 33 PART II "
        "Item 7 ITEM 7. MANAGEMENT&#8217;S DISCUSSION AND ANALYSIS OF FINANCIAL "
        "CONDITION AND RESULTS OF OPERATIONS The following Management&#8217;s "
        "Discussion and Analysis of Financial Condition and Results of Operations "
        "is intended to help the reader understand the results of operations."
    )
    assert spike.is_toc_chunk(real) is False


# --------------------------------------------------------------------------- #
# 8. Substantive-heading selection: quoted / parenthetical cross-references rejected
# --------------------------------------------------------------------------- #
def test_forward_looking_cross_reference_is_not_substantive():
    t = spike.normalize_text(
        'We describe risks and uncertainties that could cause actual results to '
        'differ materially in "Risk Factors," "Management’s Discussion and '
        'Analysis of Financial Condition and Results of Operations," and '
        '"Quantitative and Qualitative Disclosures About Market Risk" '
        '(Part II, Item 7A of this Form 10-K). Readers are cautioned.'
    )
    m_rf = spike._heading_of_kind(t, "rf")
    m_mda = spike._heading_of_kind(t, "mda")
    # either no heading token matches at all (quote lookbehind blocks it), or it
    # matches but is judged non-substantive -- both are acceptable outcomes.
    assert (m_rf is None) or (spike.is_substantive(t, m_rf, "rf") is False)
    assert (m_mda is None) or (spike.is_substantive(t, m_mda, "mda") is False)


def test_of_this_form_10k_cross_reference_is_not_substantive():
    t = spike.normalize_text(
        'as described in Risk Factors (Part I, Item 1A of this Form 10-K), and in '
        'Management Discussion and Analysis of this Form 10-K, our results may vary.'
    )
    m = spike._heading_of_kind(t, "rf")
    assert (m is None) or (spike.is_substantive(t, m, "rf") is False)


def test_first_substantive_occurrence_is_selected_over_earlier_toc():
    chunks = [
        {"chunk_idx": 0, "text": "Item 1A. Risk Factors 14 Item 1B. Unresolved Staff Comments 29 "
                                 "Item 1C. Cybersecurity 32 Item 2. Properties 40"},
        {"chunk_idx": 1, "text": "some unrelated narrative about the business and its segments."},
        {"chunk_idx": 2, "text": "ITEM 1A. RISK FACTORS Our operations and financial results are "
                                 "subject to various risks and uncertainties, including those "
                                 "described below, that could adversely affect our business."},
        {"chunk_idx": 3, "text": "ITEM 1B. UNRESOLVED STAFF COMMENTS None."},
    ]
    res = asyncio.run(spike.locate_section(chunks, "rf", classify_fn=_never_call))
    assert res["predicted_present"] is True
    assert res["basis"] == "structural"
    assert res["start_chunk"] == 2
    assert 0 in res["toc_chunks"]


# --------------------------------------------------------------------------- #
# 9. Structural next-heading boundary detection
# --------------------------------------------------------------------------- #
def test_end_boundary_next_different_heading():
    chunks = [
        {"chunk_idx": 10, "text": "ITEM 2. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL "
                                  "CONDITION AND RESULTS OF OPERATIONS The following discussion "
                                  "and analysis should be read in conjunction with the financials."},
        {"chunk_idx": 11, "text": "Revenue increased due to higher deliveries and pricing."},
        {"chunk_idx": 12, "text": "Liquidity and capital resources remained strong in the period."},
        {"chunk_idx": 13, "text": "ITEM 3. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET "
                                  "RISK We transact business globally in multiple currencies."},
    ]
    res = asyncio.run(spike.locate_section(chunks, "mda", classify_fn=_never_call))
    assert res["predicted_present"] is True
    assert res["range"] == [10, 12]
    assert res["end_established"] is True
    assert res["boundary_rule"] == "next-different-heading"


def test_end_boundary_next_heading_inside_start_chunk():
    # TSLA 10-Q shape: whole RF disclosure + the next Item heading in one chunk
    chunks = [
        {"chunk_idx": 8, "text": "notes to the financial statements."},
        {"chunk_idx": 9, "text": "ITEM 1A. RISK FACTORS Our operations and financial results are "
                                 "subject to various risks and uncertainties, including the factors "
                                 "discussed in our Annual Report on Form 10-K, which could adversely "
                                 "affect our business. ITEM 2. UNREGISTERED SALES OF EQUITY "
                                 "SECURITIES AND USE OF PROCEEDS None."},
        {"chunk_idx": 10, "text": "signature page and exhibit index."},
    ]
    res = asyncio.run(spike.locate_section(chunks, "rf", classify_fn=_never_call))
    assert res["predicted_present"] is True
    assert res["range"] == [9, 9]
    assert res["end_established"] is True


def test_chunk_with_multiple_item_headings_but_real_prose_is_still_located():
    # TSLA 10-Q shape: Part II is short, so ITEM 1A + ITEM 2 (+more) can share one
    # chunk -- it is still the Risk Factors location, not a TOC.
    chunks = [
        {"chunk_idx": 200, "text": "notes to the consolidated financial statements."},
        {"chunk_idx": 201, "text": "to the consolidated financial statements included elsewhere in this "
                                   "Quarterly Report on Form 10-Q. ITEM 1A. RISK FACTORS Our operations "
                                   "and financial results are subject to various risks and uncertainties, "
                                   "including the factors discussed in Part I, Item 1A, Risk Factors in "
                                   "our Annual Report on Form 10-K, which could adversely affect our "
                                   "business. ITEM 2. UNREGISTERED SALES OF EQUITY SECURITIES AND USE "
                                   "OF PROCEEDS None. ITEM 5. OTHER INFORMATION None. ITEM 6. EXHIBITS"},
        {"chunk_idx": 202, "text": "exhibit index and signature page."},
    ]
    res = asyncio.run(spike.locate_section(chunks, "rf", classify_fn=_never_call))
    assert res["predicted_present"] is True
    assert res["basis"] == "structural"
    assert res["range"] == [201, 201]
    assert res["end_established"] is True


def test_running_header_run_tolerates_multi_chunk_gaps():
    body = ("the company delivered resilient performance across its operating segments "
            "with revenue growth and stable margins driven by network expansion and "
            "improving customer mix over the course of the financial year " + "{i}")
    chunks = [{"chunk_idx": 0, "text": "cover"}]
    for i in range(1, 40):
        if i % 8 == 1:          # header reprinted every 8th chunk
            txt = "Management Discussion and Analysis - Business Overview " + body.format(i=i)
        else:
            txt = "ordinary segment narrative paragraph number " + str(i) + " with figures and commentary."
        chunks.append({"chunk_idx": i, "text": txt})
    chunks.append({"chunk_idx": 40, "text": "Corporate Governance Report and shareholder information section."})
    res = asyncio.run(spike.locate_section(chunks, "mda", classify_fn=_never_call))
    assert res["predicted_present"] is True
    assert res["start_chunk"] == 1
    assert res["end_established"] is True
    assert res["end_chunk"] >= 25          # spans the gapped running-header run
    assert res["boundary_rule"] == "running-header-run"


def test_end_boundary_running_header_run():
    chunks = [{"chunk_idx": 0, "text": "cover page"}]
    for i in range(1, 6):
        chunks.append({"chunk_idx": i, "text": "Management Discussion and Analysis - Business Overview "
                                               "segment performance narrative for period " + str(i) + "."})
    chunks.append({"chunk_idx": 6, "text": "Corporate Governance Report and shareholder information."})
    res = asyncio.run(spike.locate_section(chunks, "mda", classify_fn=_never_call))
    assert res["predicted_present"] is True
    assert res["start_chunk"] == 1
    assert res["end_chunk"] == 5
    assert res["boundary_rule"] == "running-header-run"


# --------------------------------------------------------------------------- #
# 10. Missing-boundary conservative behaviour
# --------------------------------------------------------------------------- #
def test_missing_boundary_collapses_to_single_chunk_partial():
    chunks = [
        {"chunk_idx": 0, "text": "intro"},
        {"chunk_idx": 1, "text": "ITEM 1A. RISK FACTORS Our operations and financial results are "
                                 "subject to various risks and uncertainties that could adversely "
                                 "affect our business and results of operations going forward."},
        {"chunk_idx": 2, "text": "more risk narrative continues here with additional detail."},
        {"chunk_idx": 3, "text": "and still more general narrative unrelated to any new section."},
    ]
    res = asyncio.run(spike.locate_section(chunks, "rf", classify_fn=_never_call))
    assert res["predicted_present"] is True
    assert res["start_chunk"] == 1
    assert res["end_established"] is False
    assert res["range"] == [1, 1]
    assert res["diagnostic_state"] == "located_partial_boundary"
    assert res["diagnostic_state_note"] == spike._DIAG_TAG


# --------------------------------------------------------------------------- #
# 11. Ambiguity-only LLM invocation
# --------------------------------------------------------------------------- #
class _Recorder:
    def __init__(self, label):
        self.label = label
        self.calls = 0

    async def __call__(self, _text):
        self.calls += 1
        return {"label": self.label, "error": None}


async def _never_call(_text):  # pragma: no cover - asserts it is never awaited
    raise AssertionError("LLM classifier must not be invoked when a substantive heading exists")


def test_llm_not_invoked_when_substantive_heading_found():
    rec = _Recorder("risk_factors")
    chunks = [
        {"chunk_idx": 0, "text": "cover"},
        {"chunk_idx": 1, "text": "ITEM 1A. RISK FACTORS Our operations and financial results are "
                                 "subject to various risks and uncertainties, including those "
                                 "described below, that could adversely affect our business."},
        {"chunk_idx": 2, "text": "ITEM 1B. UNRESOLVED STAFF COMMENTS None."},
    ]
    res = asyncio.run(spike.locate_section(chunks, "rf", classify_fn=rec))
    assert res["predicted_present"] is True and res["basis"] == "structural"
    assert rec.calls == 0


def test_llm_invoked_k3_only_when_heading_seen_but_not_substantive():
    rec = _Recorder("risk_factors")
    chunks = [
        {"chunk_idx": 0, "text": "Item 1A. Risk Factors 14 Item 1B. Unresolved Staff Comments 29 "
                                 "Item 1C. Cybersecurity 32 Item 2. Properties 40"},   # TOC
        {"chunk_idx": 1, "text": "our results depend on the risk factors, above."},  # non-substantive bare hit
        {"chunk_idx": 2, "text": "unrelated general narrative about products and services."},
    ]
    res = asyncio.run(spike.locate_section(chunks, "rf", classify_fn=rec))
    assert rec.calls == 3                       # exactly K=3 on the single candidate
    assert res["predicted_present"] is True
    assert res["basis"] == "llm-ambiguous-candidate"
    assert res["start_chunk"] == 1
    assert res["llm_calls"] and res["llm_calls"][0]["votes"] == ["risk_factors", "risk_factors", "risk_factors"]


# --------------------------------------------------------------------------- #
# 12. Conservative LLM disagreement -- never locate, never expand
# --------------------------------------------------------------------------- #
class _Cycler:
    def __init__(self, labels):
        self.labels = labels
        self.i = 0

    async def __call__(self, _text):
        lab = self.labels[self.i % len(self.labels)]
        self.i += 1
        return {"label": lab, "error": None}


def test_llm_disagreement_resolves_conservatively():
    cyc = _Cycler(["risk_factors", "mda", "other"])
    chunks = [
        {"chunk_idx": 0, "text": "Item 1A. Risk Factors 14 Item 1B. Unresolved Staff Comments 29 "
                                 "Item 1C. Cybersecurity 32 Item 2. Properties 40"},
        {"chunk_idx": 1, "text": "our exposure to the risk factors, noted."},
        {"chunk_idx": 2, "text": "general narrative."},
    ]
    res = asyncio.run(spike.locate_section(chunks, "rf", classify_fn=cyc))
    assert res["predicted_present"] is False
    assert res["range"] is None
    assert res["diagnostic_state"] == "not_located"


def test_llm_wrong_majority_resolves_conservatively():
    rec = _Recorder("other")     # strict majority, but NOT the wanted section
    chunks = [
        {"chunk_idx": 0, "text": "Item 1A. Risk Factors 14 Item 1B. Unresolved Staff Comments 29 "
                                 "Item 1C. Cybersecurity 32 Item 2. Properties 40"},
        {"chunk_idx": 1, "text": "our exposure to the risk factors, noted."},
    ]
    res = asyncio.run(spike.locate_section(chunks, "rf", classify_fn=rec))
    assert res["predicted_present"] is False
    assert res["range"] is None


# --------------------------------------------------------------------------- #
# 13. classify_kv majority-vote arithmetic
# --------------------------------------------------------------------------- #
def test_classify_kv_majority_and_disagreement():
    two_one = asyncio.run(spike.classify_kv("x", classify_fn=_Cycler(["mda", "mda", "other"]), k=3))
    assert two_one["strict_majority"] is True and two_one["majority"] == "mda"
    split = asyncio.run(spike.classify_kv("x", classify_fn=_Cycler(["rf", "mda", "other"]), k=3))
    assert split["strict_majority"] is False and split["majority"] is None


# --------------------------------------------------------------------------- #
# 14. Ground-truth table is evaluation-only and clearly marked
# --------------------------------------------------------------------------- #
def test_ground_truth_present_and_not_referenced_by_locator():
    import inspect
    assert set(spike.GROUND_TRUTH) == {"EDGAR_10Q", "EDGAR_10K", "BSE_ANNUAL", "PLAINTEXT"}
    # the prediction pipeline must not REFERENCE the name (co_names catches an
    # actual load; comments/docstrings mentioning it are fine).
    for fn in (spike.locate_section, spike.locate_all, spike.locate_section.__wrapped__ if hasattr(spike.locate_section, "__wrapped__") else spike._end_boundary,
               spike.is_substantive, spike.is_toc_chunk, spike.normalize_text,
               spike._heading_of_kind, spike._prose_follows, spike.classify_kv):
        assert "GROUND_TRUTH" not in fn.__code__.co_names, (
            f"{fn.__name__} must not consult the evaluation ground-truth table"
        )
    # only the evaluate_* layer references it
    assert "GROUND_TRUTH" not in spike.evaluate_section.__code__.co_names  # takes gt as an arg
    src = inspect.getsource(spike)
    assert "HUMAN-ESTABLISHED EVALUATION GROUND TRUTH -- NOT PRODUCTION LOGIC -- NOT CONTRACT ARTIFACT" in src
