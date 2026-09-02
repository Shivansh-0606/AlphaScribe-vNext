"""Unit tests for `agents/filing_analysis.py` — the M14 four-output grounded
filing analysis (Document 64 §8/§9/§11; Document 65 §9/§10/OAQ-9).

Offline: no network, no LLM, no MongoDB. The one LLM call per output is
replaced with an injected `chat_fn`; section location runs deterministically
(heuristic) with a conservative fake classifier.

    python -m pytest backend/tests/unit/test_filing_analysis.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents import filing_analysis as fa


def _chunks(texts, start=0):
    return [{"chunk_idx": start + i, "text": t} for i, t in enumerate(texts)]


async def _classify_other(_text):
    return {"label": "other", "error": None}


async def _fake_chat(system, user, schema, *, model=None, temperature=None):
    """Echo a narrative that cites excerpt [1] iff excerpt [1] is present."""
    return schema(narrative="A grounded factual claim [1]." if "[1] (chunk" in user else "")


# --------------------------------------------------------------------------- #
# resolve_and_validate  (OAQ-9 deterministic validator)
# --------------------------------------------------------------------------- #
def test_contiguous_cited_chunks_coalesce_into_one_range_noncontiguous_split():
    cands = [{"n": 1, "chunk_idx": 10, "text": ""},
             {"n": 2, "chunk_idx": 11, "text": ""},
             {"n": 3, "chunk_idx": 20, "text": ""}]
    out = fa.resolve_and_validate("Revenue rose [1]. Margins held [2]. Guidance raised [3].", cands, "d1")
    assert out["sources"] == [
        {"index": 1, "doc_id": "d1", "chunk_start": 10, "chunk_end": 11},
        {"index": 2, "doc_id": "d1", "chunk_start": 20, "chunk_end": 20},
    ]
    assert out["cited_source_indices"] == [1, 2]
    assert out["state"] == "complete" and out["coverage_boundaries"] == []
    # markers rewritten to source indices; both present, no orphans
    import re
    used = sorted({int(m) for m in re.findall(r"\[(\d+)\]", out["narrative"])})
    assert used == [1, 2] and set(used) <= {s["index"] for s in out["sources"]}


def test_out_of_range_marker_is_dropped_and_state_is_partial():
    out = fa.resolve_and_validate("A [1]. B [9].", [{"n": 1, "chunk_idx": 5, "text": ""}], "d1")
    assert out["narrative"].count("[") == 1                      # [9] stripped
    assert out["state"] == "partial"
    assert any("no matching excerpt" in b for b in out["coverage_boundaries"])


def test_empty_narrative_is_insufficient_evidence():
    out = fa.resolve_and_validate("", [{"n": 1, "chunk_idx": 1, "text": ""}], "d1")
    assert out["state"] == "insufficient_evidence"
    assert out["narrative"] == "" and out["sources"] == [] and out["cited_source_indices"] == []
    assert out["coverage_boundaries"]                             # machine-readable reason present


def test_narrative_without_any_marker_is_insufficient_evidence():
    out = fa.resolve_and_validate("Ungrounded prose with no citation markers at all.",
                                  [{"n": 1, "chunk_idx": 1, "text": ""}], "d1")
    assert out["state"] == "insufficient_evidence" and out["narrative"] == ""


def test_extra_boundaries_force_partial():
    out = fa.resolve_and_validate("X [1].", [{"n": 1, "chunk_idx": 3, "text": ""}], "d1",
                                  extra_boundaries=["located section exceeds the per-output budget"])
    assert out["state"] == "partial"
    assert "located section exceeds the per-output budget" in out["coverage_boundaries"]


def test_output_shape_is_exactly_the_flat_cited_narrative():
    out = fa.resolve_and_validate("C [1].", [{"n": 1, "chunk_idx": 2, "text": ""}], "d1")
    assert set(out) == {"narrative", "sources", "cited_source_indices", "state", "coverage_boundaries"}
    for s in out["sources"]:
        assert set(s) == {"index", "doc_id", "chunk_start", "chunk_end"}
        assert s["chunk_start"] <= s["chunk_end"] and s["doc_id"] == "d1"


# --------------------------------------------------------------------------- #
# build_candidates  (OAQ-1(D) + OAQ-3 + OAQ-10)
# --------------------------------------------------------------------------- #
def test_small_filing_filing_summary_uses_the_whole_filing():
    ch = _chunks([f"para {i}" for i in range(10)])
    cands, b = asyncio.run(fa.build_candidates(ch, "filing_summary", {}, doc_id="d1"))
    assert [c["chunk_idx"] for c in cands] == list(range(10)) and b == []


def test_large_filing_filing_summary_falls_back_to_a_sampled_subset():
    ch = _chunks([f"para {i}" for i in range(fa.WHOLE_FILING_CHUNK_THRESHOLD + 40)])
    cands, b = asyncio.run(fa.build_candidates(ch, "filing_summary", {}, doc_id="d1"))  # db=None -> deterministic spread
    assert 0 < len(cands) <= fa.MAX_CANDIDATE_CHUNKS
    assert any("retrieval-scoped / sampled subset" in x for x in b)


def test_unlocated_section_yields_no_candidates_and_a_boundary():
    ch = _chunks(["ordinary narrative with no section heading"] * 5)
    cands, b = asyncio.run(fa.build_candidates(ch, "risk_factors",
                                               {"risk_factors": {"predicted_present": False}}, doc_id="d1"))
    assert cands == [] and any("no Risk Factors Digest section heading located" in x for x in b)


def test_located_bounded_section_candidates_are_exactly_the_range():
    ch = _chunks([f"c{i}" for i in range(20)])
    sections = {"mda": {"predicted_present": True, "range": [5, 9], "end_established": True}}
    cands, b = asyncio.run(fa.build_candidates(ch, "mda", sections, doc_id="d1"))
    assert [c["chunk_idx"] for c in cands] == [5, 6, 7, 8, 9] and b == []


def test_partial_boundary_section_adds_a_coverage_boundary():
    ch = _chunks([f"c{i}" for i in range(20)])
    sections = {"mda": {"predicted_present": True, "range": [5, 5], "end_established": False}}
    cands, b = asyncio.run(fa.build_candidates(ch, "mda", sections, doc_id="d1"))
    assert [c["chunk_idx"] for c in cands] == [5]
    assert any("end boundary could not be structurally established" in x for x in b)


def test_important_changes_is_a_filing_local_cue_scan_only():
    ch = _chunks(["ordinary text", "We have revised our guidance for the period.", "more text"])
    cands, b = asyncio.run(fa.build_candidates(ch, "important_changes", {}, doc_id="d1"))
    assert [c["chunk_idx"] for c in cands] == [1] and b == []
    ch2 = _chunks(["no change language", "just plain narrative about the business"])
    c2, b2 = asyncio.run(fa.build_candidates(ch2, "important_changes", {}, doc_id="d1"))
    assert c2 == [] and any("INV-IC" in x for x in b2)


# --------------------------------------------------------------------------- #
# analyze_filing  (orchestration)
# --------------------------------------------------------------------------- #
def test_analyze_filing_always_returns_exactly_the_four_outputs():
    ch = _chunks([
        "in this Quarterly Report on Form 10-Q. ITEM 1A. RISK FACTORS Our operations and financial "
        "results are subject to various risks and uncertainties that could adversely affect our business. "
        "ITEM 2. UNREGISTERED SALES None.",
        "ITEM 2. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS "
        "the following discussion should be read together with the financial statements for the period.",
        "We reclassified certain prior period balances to conform to current presentation.",
        "ITEM 3. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK foreign currency risk.",
    ])
    res = asyncio.run(fa.analyze_filing(ch, "d1", chat_fn=_fake_chat, section_classify_fn=_classify_other))
    assert set(res["outputs"]) == {"Filing Summary", "Risk Factors Digest", "MD&A Digest", "Important Changes"}
    for o in res["outputs"].values():
        assert set(o) == {"narrative", "sources", "cited_source_indices", "state", "coverage_boundaries"}
        assert o["state"] in ("complete", "partial", "insufficient_evidence")
        for s in o["sources"]:
            assert s["doc_id"] == "d1" and s["chunk_start"] <= s["chunk_end"]
    assert res["prompt_version"] == fa.PROMPT_VERSION and res["schema_version"] == fa.SCHEMA_VERSION


def test_analyze_empty_filing_is_all_insufficient_evidence():
    res = asyncio.run(fa.analyze_filing([], "d1", chat_fn=_fake_chat))
    assert set(res["outputs"]) == {"Filing Summary", "Risk Factors Digest", "MD&A Digest", "Important Changes"}
    assert all(o["state"] == "insufficient_evidence" and o["narrative"] == ""
               for o in res["outputs"].values())


def test_analyze_filing_is_structurally_filing_local_inv_ic():
    # analyze_filing receives ONLY this filing's chunks; the Important Changes
    # candidate set is a cue scan over exactly those chunks -- no other doc_id
    # is reachable. (INV-IC, Document 64 §8.1.)
    ch = _chunks(["plain narrative, no change language, no headings"])
    res = asyncio.run(fa.analyze_filing(ch, "solo-doc", chat_fn=_fake_chat, section_classify_fn=_classify_other))
    ic = res["outputs"]["Important Changes"]
    assert ic["state"] == "insufficient_evidence"
    assert any("INV-IC" in b for b in ic["coverage_boundaries"])


# --------------------------------------------------------------------------- #
# M-2  candidate truncation is honest (never silent `complete`)
# --------------------------------------------------------------------------- #
def test_m2_61_to_120_chunk_filing_summary_flags_the_dropped_tail_and_is_partial():
    # 90 chunks: still "whole filing" (<= threshold) so the old code implied
    # full coverage, but _number caps at MAX_CANDIDATE_CHUNKS and dropped 30
    # chunks with no boundary and a `complete` state.
    ch = _chunks([f"para {i}" for i in range(90)])
    cands, b = asyncio.run(fa.build_candidates(ch, "filing_summary", {}, doc_id="d1"))
    assert len(cands) == fa.MAX_CANDIDATE_CHUNKS
    assert any("60 of 90 candidate chunks" in x and "30 further chunk(s)" in x for x in b)
    # the boundary forces the output off `complete`
    out = fa.resolve_and_validate("Overview claim [1].", cands, "d1", extra_boundaries=b)
    assert out["state"] == "partial"


def test_m2_small_filing_at_or_below_cap_has_no_truncation_boundary():
    ch = _chunks([f"para {i}" for i in range(fa.MAX_CANDIDATE_CHUNKS)])
    cands, b = asyncio.run(fa.build_candidates(ch, "filing_summary", {}, doc_id="d1"))
    assert len(cands) == fa.MAX_CANDIDATE_CHUNKS and b == []


def test_m2_important_changes_over_cap_flags_omitted_change_language():
    ch = _chunks([f"We have revised item {i} effective this quarter." for i in range(65)])
    cands, b = asyncio.run(fa.build_candidates(ch, "important_changes", {}, doc_id="d1"))
    assert len(cands) == fa.MAX_CANDIDATE_CHUNKS
    assert any("60 of 65 candidate chunks" in x and "5 further chunk(s)" in x for x in b)
    out = fa.resolve_and_validate("A change [1].", cands, "d1", extra_boundaries=b)
    assert out["state"] == "partial"


# --------------------------------------------------------------------------- #
# M-3  one output's grounding failure does not sink the other three
# --------------------------------------------------------------------------- #
_M3_CHUNKS = [
    "ITEM 1A. RISK FACTORS various risks and uncertainties could adversely affect the "
    "business, operations, and financial results of the company in future periods.",
    "ITEM 2. MANAGEMENT'S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF "
    "OPERATIONS the following discussion should be read together with the financial "
    "statements for the period presented in this report.",
    "We reclassified certain prior period balances to conform to the current presentation.",
    "ITEM 3. QUANTITATIVE AND QUALITATIVE DISCLOSURES ABOUT MARKET RISK foreign currency risk.",
]


def test_m3_grounding_error_in_one_output_isolates_to_insufficient_evidence():
    real = fa.resolve_and_validate
    calls = {"n": 0}

    def _boom_on_second(narr, cands, doc_id, **kw):
        calls["n"] += 1
        if calls["n"] == 2:  # OUTPUT_KINDS[1] == "risk_factors"
            raise fa.FilingAnalysisGroundingError("synthetic structural inconsistency")
        return real(narr, cands, doc_id, **kw)

    fa.resolve_and_validate = _boom_on_second
    try:
        res = asyncio.run(fa.analyze_filing(_chunks(_M3_CHUNKS), "d1",
                                            chat_fn=_fake_chat, section_classify_fn=_classify_other))
    finally:
        fa.resolve_and_validate = real

    assert set(res["outputs"]) == {"Filing Summary", "Risk Factors Digest", "MD&A Digest", "Important Changes"}
    bad = res["outputs"]["Risk Factors Digest"]
    assert bad["state"] == "insufficient_evidence"
    assert bad["narrative"] == "" and bad["sources"] == [] and bad["cited_source_indices"] == []
    assert any("structurally consistent" in x and "synthetic structural inconsistency" in x
               for x in bad["coverage_boundaries"])
    # the siblings still produced normally
    assert res["outputs"]["Filing Summary"]["state"] in ("complete", "partial")


def test_m3_a_non_grounding_exception_still_fails_the_job_loudly():
    real = fa.resolve_and_validate

    def _unexpected(*_a, **_k):
        raise RuntimeError("not a grounding error")

    fa.resolve_and_validate = _unexpected
    try:
        try:
            asyncio.run(fa.analyze_filing(_chunks(_M3_CHUNKS), "d1",
                                          chat_fn=_fake_chat, section_classify_fn=_classify_other))
        except RuntimeError as e:
            assert "not a grounding error" in str(e)
        else:
            raise AssertionError("a non-grounding exception must propagate, not be swallowed")
    finally:
        fa.resolve_and_validate = real
