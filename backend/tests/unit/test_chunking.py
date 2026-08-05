"""Unit check for agents/retrieval.py's chunk_text — the function that
determines every chunk boundary in the retrieval corpus (05 §3.2). Pure,
no I/O, no models.

    python backend/tests/unit/test_chunking.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.retrieval import chunk_text


def test_empty_and_whitespace_only():
    assert chunk_text("") == []
    assert chunk_text("   \n\n  \r\n  ") == []


def test_paragraphs_merge_when_they_fit_in_one_chunk():
    text = "First paragraph.\n\nSecond paragraph."
    chunks = chunk_text(text, chunk_size=900, overlap=0)
    assert chunks == ["First paragraph.\n\nSecond paragraph."]


def test_paragraph_split_and_overlap_stitching():
    text = "AAAAAAAAAA\n\nBBBBBBBBBB"
    chunks = chunk_text(text, chunk_size=15, overlap=3)
    # Base chunks are ["AAAAAAAAAA", "BBBBBBBBBB"]; overlap prepends the last
    # 3 chars of chunk[i-1] onto chunk[i], so nothing at a boundary is dropped.
    assert chunks == ["AAAAAAAAAA", "AAA BBBBBBBBBB"]


def test_overlap_zero_disables_stitching():
    text = "AAAAAAAAAA\n\nBBBBBBBBBB"
    chunks = chunk_text(text, chunk_size=15, overlap=0)
    assert chunks == ["AAAAAAAAAA", "BBBBBBBBBB"]


def test_single_chunk_never_gets_stitched_even_with_overlap():
    # len(chunks) == 1 -> the overlap branch (retrieval.py:132) is skipped.
    chunks = chunk_text("just one short paragraph", chunk_size=900, overlap=120)
    assert chunks == ["just one short paragraph"]


def test_oversized_paragraph_splits_on_sentence_boundaries():
    text = "One. Two. Three. Four."
    chunks = chunk_text(text, chunk_size=10, overlap=0)
    assert chunks == ["One. Two.", "Three.", "Four."]


def test_crlf_and_excess_blank_lines_are_normalized():
    text = "para one\r\n\r\n\r\n\r\npara two"
    # \r\n -> \n, then 3+ newlines collapse to exactly 2 (a paragraph break),
    # so this is still exactly two paragraphs, not one merged with stray blanks.
    chunks = chunk_text(text, chunk_size=900, overlap=0)
    assert chunks == ["para one\n\npara two"]


if __name__ == "__main__":
    test_empty_and_whitespace_only()
    test_paragraphs_merge_when_they_fit_in_one_chunk()
    test_paragraph_split_and_overlap_stitching()
    test_overlap_zero_disables_stitching()
    test_single_chunk_never_gets_stitched_even_with_overlap()
    test_oversized_paragraph_splits_on_sentence_boundaries()
    test_crlf_and_excess_blank_lines_are_normalized()
    print("ok: chunk_text — paragraph packing, sentence-split overflow, overlap stitching, normalization")
