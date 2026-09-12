"""Unit tests for `agents/filing_qa.py` — the M16 Filing Q&A (FQA v1) pure
module (Document 87 Revision 2 §7/§8/§9; Document 90 §5/§10/§11, as amended
for candidate selection by Documents 95/96; Document 94 Revision 1 §9/§10/§18).

Offline: no network, no LLM, no MongoDB. The one LLM call is replaced with an
injected `chat_fn`.

    python -m pytest backend/tests/unit/test_filing_qa.py -v
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents import filing_qa as fqa


def _chunks(n, start=0):
    return [{"chunk_idx": start + i, "text": f"chunk text {start + i}"} for i in range(n)]


async def _fake_chat_citing(system, user, schema, *, model=None, temperature=None):
    return schema(answer_text="A grounded factual claim [1].")


async def _fake_chat_empty(system, user, schema, *, model=None, temperature=None):
    return schema(answer_text="")


# --------------------------------------------------------------------------- #
# _select_positions / _select_by_positions  (Document 95/96-ratified formula)
# --------------------------------------------------------------------------- #
def _check_properties(n, k):
    positions = fqa._select_positions(n, k)
    assert len(positions) == k, f"N={n},K={k}: expected exactly K positions"
    assert len(set(positions)) == k, f"N={n},K={k}: duplicate positions"
    assert positions == sorted(positions), f"N={n},K={k}: not sorted/ascending"
    assert positions[0] == 0, f"N={n},K={k}: first position must be 0"
    assert positions[-1] == n - 1, f"N={n},K={k}: last position must be N-1"
    assert all(0 <= p < n for p in positions)
    # reproducibility — pure function of (n, k) alone
    assert fqa._select_positions(n, k) == positions
    return positions


def test_selection_properties_hold_for_the_documented_worked_examples():
    for n, k in [(7, 3), (8, 3), (10, 3), (11, 4), (13, 5), (9, 4)]:
        _check_properties(n, k)


def test_minimum_valid_k_equals_2_yields_exactly_first_and_last():
    positions = _check_properties(10, 2)
    assert positions == [0, 9]


def test_n_le_k_selects_every_chunk_not_k():
    universe = _chunks(5)
    selected = fqa._select_by_positions(universe, 8)  # K > N
    assert selected == universe  # every one of the N chunks, not K
    selected_eq = fqa._select_by_positions(universe, 5)  # K == N
    assert selected_eq == universe


def test_n_gt_k_selects_exactly_k_first_last_no_duplicates_sorted():
    universe = _chunks(37, start=100)
    selected = fqa._select_by_positions(universe, fqa.MAX_CANDIDATE_CHUNKS if fqa.MAX_CANDIDATE_CHUNKS < 37 else 5)
    k = fqa.MAX_CANDIDATE_CHUNKS if fqa.MAX_CANDIDATE_CHUNKS < 37 else 5
    assert len(selected) == k
    idxs = [c["chunk_idx"] for c in selected]
    assert len(set(idxs)) == k
    assert idxs == sorted(idxs)
    assert selected[0] == universe[0]
    assert selected[-1] == universe[-1]


def test_selection_is_independent_of_model_output():
    # a pure function of (N, K) alone — no chat_fn/candidates coupling exists
    # in _select_positions's signature at all; re-running with the same
    # (n, k) is the independence proof.
    a = fqa._select_positions(23, 6)
    b = fqa._select_positions(23, 6)
    assert a == b


# --------------------------------------------------------------------------- #
# _validate_candidate_cap  (K >= 2 hard invariant, Document 94 Revision 1 §7)
# --------------------------------------------------------------------------- #
def test_k_less_than_2_is_rejected():
    import pytest
    for bad_k in (0, 1, -1):
        try:
            fqa._validate_candidate_cap(bad_k)
        except ValueError:
            pass
        else:
            raise AssertionError(f"K={bad_k} must be rejected")


def test_k_equal_2_is_accepted():
    fqa._validate_candidate_cap(2)  # must not raise


def test_the_live_module_constant_already_satisfies_the_guard():
    # MAX_CANDIDATE_CHUNKS is validated unconditionally at import time
    # (module top level, not behind assert/debug-flag) — this just confirms
    # the deployed default is valid; a K<2 default would have raised on
    # `import agents.filing_qa` itself, before this test could even run.
    assert fqa.MAX_CANDIDATE_CHUNKS >= 2


# --------------------------------------------------------------------------- #
# resolve_and_validate  (deterministic citation validator)
# --------------------------------------------------------------------------- #
def test_valid_citation_produces_answered():
    cands = [{"n": 1, "chunk_idx": 10, "text": ""}, {"n": 2, "chunk_idx": 11, "text": ""}]
    out = fqa.resolve_and_validate("Revenue rose [1]. Margins held [2].", cands, "d1")
    assert out["state"] == "answered"
    assert out["sources"] == [{"index": 1, "doc_id": "d1", "chunk_start": 10, "chunk_end": 11}]
    assert out["cited_source_indices"] == [1]
    assert out["coverage_boundaries"] == []


def test_out_of_range_marker_is_dropped_but_answer_survives():
    out = fqa.resolve_and_validate("A [1]. B [9].", [{"n": 1, "chunk_idx": 5, "text": ""}], "d1")
    assert out["answer_text"].count("[") == 1  # [9] stripped
    assert out["state"] == "answered"
    assert any("no matching excerpt" in b for b in out["coverage_boundaries"])


def test_empty_answer_text_is_insufficient_evidence():
    out = fqa.resolve_and_validate("", [{"n": 1, "chunk_idx": 1, "text": ""}], "d1")
    assert out["state"] == "insufficient_evidence"
    assert out["sources"] == [] and out["cited_source_indices"] == []
    assert out["coverage_boundaries"]


def test_answer_without_any_marker_is_insufficient_evidence():
    out = fqa.resolve_and_validate("No citations here at all.", [{"n": 1, "chunk_idx": 1, "text": ""}], "d1")
    assert out["state"] == "insufficient_evidence"


def test_partial_coverage_does_not_force_insufficient_evidence():
    # Document 87 R2 §9.1 — the FQA-specific departure from the M14 3-state
    # precedent: a capped/partially-covered candidate set that still yields a
    # well-grounded answer is `answered`, WITH a coverage_boundaries entry,
    # never a downgrade.
    out = fqa.resolve_and_validate(
        "X [1].", [{"n": 1, "chunk_idx": 3, "text": ""}], "d1",
        extra_boundaries=["large filing: uses a retrieval-scoped subset of chunks relevant to the question"],
    )
    assert out["state"] == "answered"
    assert "large filing: uses a retrieval-scoped subset of chunks relevant to the question" in out["coverage_boundaries"]


def test_output_bound_violation_degrades_to_insufficient_evidence_not_truncation():
    out = fqa.resolve_and_validate(
        "This is a long grounded answer [1].", [{"n": 1, "chunk_idx": 1, "text": ""}], "d1",
        max_answer_chars=5,  # smaller than the cleaned text
    )
    assert out["state"] == "insufficient_evidence"
    assert out["sources"] == [] and out["cited_source_indices"] == []


def test_too_many_sources_degrades_to_insufficient_evidence():
    cands = [{"n": i, "chunk_idx": i * 10, "text": ""} for i in range(1, 4)]  # 3 disjoint chunks
    raw = " ".join(f"claim [{i}]." for i in range(1, 4))
    out = fqa.resolve_and_validate(raw, cands, "d1", max_sources=1)
    assert out["state"] == "insufficient_evidence"


def test_output_shape_is_exactly_the_contract_fields():
    out = fqa.resolve_and_validate("C [1].", [{"n": 1, "chunk_idx": 2, "text": ""}], "d1")
    assert set(out) == {"answer_text", "sources", "cited_source_indices", "state", "coverage_boundaries"}
    for s in out["sources"]:
        assert set(s) == {"index", "doc_id", "chunk_start", "chunk_end"}
        assert s["chunk_start"] <= s["chunk_end"] and s["doc_id"] == "d1"


# --------------------------------------------------------------------------- #
# build_candidates
# --------------------------------------------------------------------------- #
def test_small_filing_below_cap_uses_every_chunk():
    ch = _chunks(10)
    cands, b = asyncio.run(fqa.build_candidates(ch, "q", "d1"))
    assert [c["chunk_idx"] for c in cands] == list(range(10))
    assert b == []


def test_small_filing_over_cap_uses_the_d95_96_formula_with_first_last_coverage():
    n = fqa.MAX_CANDIDATE_CHUNKS + 20
    assert n <= fqa.WHOLE_FILING_CHUNK_THRESHOLD  # stays in the whole-filing branch
    ch = _chunks(n)
    cands, b = asyncio.run(fqa.build_candidates(ch, "q", "d1"))
    assert len(cands) == fqa.MAX_CANDIDATE_CHUNKS
    idxs = [c["chunk_idx"] for c in cands]
    assert idxs[0] == 0 and idxs[-1] == n - 1
    assert len(set(idxs)) == fqa.MAX_CANDIDATE_CHUNKS
    assert any("chunks" in x for x in b)


def test_large_filing_uses_retrieval_scoped_selection():
    n = fqa.WHOLE_FILING_CHUNK_THRESHOLD + 10
    ch = _chunks(n)

    async def _fake_retrieve(db, ticker, query, *, doc_id, top_k, candidate_k):
        return [{"chunk_idx": 3, "text": "x"}, {"chunk_idx": 4, "text": "y"}], {}

    import agents.retrieval as retrieval_mod
    orig = retrieval_mod.retrieve
    retrieval_mod.retrieve = _fake_retrieve
    try:
        cands, b = asyncio.run(fqa.build_candidates(ch, "q", "d1", db=object(), ticker="AAPL"))
    finally:
        retrieval_mod.retrieve = orig
    assert [c["chunk_idx"] for c in cands] == [3, 4]
    assert any("retrieval-scoped subset" in x for x in b)


def test_large_filing_empty_retrieval_falls_back_to_deterministic_sample():
    n = fqa.WHOLE_FILING_CHUNK_THRESHOLD + 10
    ch = _chunks(n)

    async def _fake_retrieve(db, ticker, query, *, doc_id, top_k, candidate_k):
        return [], {}

    import agents.retrieval as retrieval_mod
    orig = retrieval_mod.retrieve
    retrieval_mod.retrieve = _fake_retrieve
    try:
        cands, b = asyncio.run(fqa.build_candidates(ch, "q", "d1", db=object(), ticker="AAPL"))
    finally:
        retrieval_mod.retrieve = orig
    assert len(cands) == fqa.MAX_CANDIDATE_CHUNKS
    idxs = [c["chunk_idx"] for c in cands]
    assert idxs[0] == 0 and idxs[-1] == n - 1
    assert any("evenly-spaced sample" in x for x in b)


def test_no_db_or_ticker_degrades_large_filing_to_deterministic_sample():
    n = fqa.WHOLE_FILING_CHUNK_THRESHOLD + 10
    ch = _chunks(n)
    cands, b = asyncio.run(fqa.build_candidates(ch, "q", "d1"))  # db=None
    assert len(cands) == fqa.MAX_CANDIDATE_CHUNKS
    assert any("evenly-spaced sample" in x for x in b)


# --------------------------------------------------------------------------- #
# answer_question  (orchestration + generation-call invariant)
# --------------------------------------------------------------------------- #
def test_zero_content_filing_is_insufficient_evidence_with_zero_model_calls():
    calls = {"n": 0}

    async def _spy(*a, **k):
        calls["n"] += 1
        return fqa.AnswerSchema(answer_text="should never be called")

    res = asyncio.run(fqa.answer_question([], "d1", "What changed?", chat_fn=_spy))
    assert res["state"] == "insufficient_evidence"
    assert res["sources"] == [] and res["cited_source_indices"] == []
    assert "no usable persisted content" in res["coverage_boundaries"][0]
    assert calls["n"] == 0
    assert res["prompt_version"] == fqa.PROMPT_VERSION and res["schema_version"] == fqa.SCHEMA_VERSION


def test_normal_path_makes_exactly_one_generation_call():
    calls = {"n": 0}

    async def _spy(system, user, schema, *, model=None, temperature=None):
        calls["n"] += 1
        return schema(answer_text="A grounded claim [1].")

    ch = _chunks(5)
    res = asyncio.run(fqa.answer_question(ch, "d1", "What does the filing say?", chat_fn=_spy))
    assert calls["n"] == 1
    assert res["state"] == "answered"
    assert res["sources"] and res["cited_source_indices"]


def test_insufficient_evidence_path_still_makes_exactly_one_generation_call():
    calls = {"n": 0}

    async def _spy(system, user, schema, *, model=None, temperature=None):
        calls["n"] += 1
        return schema(answer_text="")  # model grounds nothing

    ch = _chunks(5)
    res = asyncio.run(fqa.answer_question(ch, "d1", "Unanswerable question", chat_fn=_spy))
    assert calls["n"] == 1
    assert res["state"] == "insufficient_evidence"


def test_citation_structure_error_is_caught_and_degrades_never_raises():
    real = fqa.resolve_and_validate

    def _boom(*a, **k):
        raise fqa.FilingQACitationStructureError("synthetic structural inconsistency")

    fqa.resolve_and_validate = _boom
    try:
        ch = _chunks(5)
        res = asyncio.run(fqa.answer_question(ch, "d1", "q", chat_fn=_fake_chat_citing))
    finally:
        fqa.resolve_and_validate = real

    assert res["state"] == "insufficient_evidence"
    assert any("structurally consistent" in b for b in res["coverage_boundaries"])


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
