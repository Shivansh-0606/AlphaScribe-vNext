"""Unit check for agents/retrieval.py's _minmax normalization and the hybrid
fusion inside retrieve(), including the BM25-only degradation branch flagged
as untested in 05 §3.2 ("the dense_norm is None branch is a documented
production path and is untested").

No real Mongo, no fastembed model load: the DB is a minimal fake cursor, and
embed_query/rerank_pairs are monkeypatched to None so the test is deterministic
regardless of whether fastembed models happen to be cached in this environment.

    python backend/tests/unit/test_retrieval_fusion.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import agents.retrieval as retrieval
from agents.retrieval import _minmax, retrieve


def test_minmax_empty():
    assert _minmax([]) == []


def test_minmax_all_equal_maps_to_half():
    # hi - lo < 1e-9 -> every score maps to 0.5 (retrieval.py:74-75), avoiding
    # a division by (near) zero.
    assert _minmax([3.0, 3.0, 3.0]) == [0.5, 0.5, 0.5]


def test_minmax_normal_range():
    assert _minmax([0.0, 5.0, 10.0]) == [0.0, 0.5, 1.0]


class _FakeCursor:
    def __init__(self, rows):
        self._rows = rows

    def sort(self, *a, **k):
        return self

    async def to_list(self, n):
        return self._rows[:n]


class _FakeChunks:
    def __init__(self, rows):
        self._rows = rows

    def find(self, *a, **k):
        return _FakeCursor(self._rows)


class _FakeDB:
    def __init__(self, rows):
        self.filing_chunks = _FakeChunks(rows)


def _rows():
    return [
        {"ticker": "AAPL", "chunk_idx": 0, "created_at": "2024-01-03",
         "text": "Apple reported strong revenue growth this quarter."},
        {"ticker": "AAPL", "chunk_idx": 1, "created_at": "2024-01-02",
         "text": "Weather was pleasant in Cupertino this spring."},
        {"ticker": "AAPL", "chunk_idx": 2, "created_at": "2024-01-01",
         "text": "Revenue increased by 12% to $50B this year, driven by growth."},
    ]


def test_retrieve_empty_corpus_returns_empty_with_meta():
    db = _FakeDB([])
    docs, meta = asyncio.run(retrieve(db, "aapl", "revenue"))
    assert docs == []
    assert meta == {"total_chunks": 0, "bm25": True, "dense": False, "reranker": False}


def test_retrieve_bm25_only_degradation_branch():
    """embed_query/rerank_pairs unavailable -> pure BM25 + numeric-heuristic
    fusion (retrieval.py:203-204), the branch 05 §3.2 flagged as untested."""
    real_embed_query = retrieval.embed_query
    real_rerank_pairs = retrieval.rerank_pairs
    retrieval.embed_query = lambda text: None
    retrieval.rerank_pairs = lambda query, texts: None
    try:
        db = _FakeDB(_rows())
        docs, meta = asyncio.run(retrieve(db, "AAPL", "revenue growth", top_k=3))
    finally:
        retrieval.embed_query = real_embed_query
        retrieval.rerank_pairs = real_rerank_pairs

    assert meta == {"total_chunks": 3, "bm25": True, "dense": False, "reranker": False}
    assert len(docs) == 3

    # No vector ever leaves retrieve() (retrieval.py:195), regardless of stage.
    assert all("embedding" not in d for d in docs)
    # Descending score order.
    scores = [d["score"] for d in docs]
    assert scores == sorted(scores, reverse=True)
    # The two revenue-relevant chunks (idx 0 and 2) must outrank the
    # unrelated weather chunk (idx 1) under BM25 alone.
    ranked_idxs = [d["chunk_idx"] for d in docs]
    assert ranked_idxs.index(1) > ranked_idxs.index(0)
    assert ranked_idxs.index(1) > ranked_idxs.index(2)
    # idx 2 carries two numeric hits ("12%", "$50B") and still gets its 5%
    # heuristic boost added (score > raw BM25 alone would give it) even
    # though BM25's own length normalization keeps idx 0 ranked first here.
    idx2_doc = next(d for d in docs if d["chunk_idx"] == 2)
    assert idx2_doc["score"] > idx2_doc["_bm25"] * 0.95


def test_retrieve_ticker_is_uppercased_for_the_query():
    seen = {}

    class _RecordingChunks(_FakeChunks):
        def find(self, filt, *a, **k):
            seen["ticker"] = filt["ticker"]
            return _FakeCursor(self._rows)

    db = _FakeDB([])
    db.filing_chunks = _RecordingChunks([])
    asyncio.run(retrieve(db, "aapl", "x"))
    assert seen["ticker"] == "AAPL"


if __name__ == "__main__":
    test_minmax_empty()
    test_minmax_all_equal_maps_to_half()
    test_minmax_normal_range()
    test_retrieve_empty_corpus_returns_empty_with_meta()
    test_retrieve_bm25_only_degradation_branch()
    test_retrieve_ticker_is_uppercased_for_the_query()
    print("ok: _minmax edge cases; retrieve() BM25-only degradation branch; empty corpus; ticker normalization")
