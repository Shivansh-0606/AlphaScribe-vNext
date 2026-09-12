"""AH-2 deployment-invariant tests for the M16 Filing Q&A job-result buffer
(Document 90 §7-§9; Document 94 Revision 1 §11). The completed result lives
ONLY in the process that computed it: restart loss is accepted, cross-process
GET is unsupported, and the SSE `final` frame is built from the same
process-local buffer as GET.

These assert the buffer mechanism's *behaviour*, not merely its happy path —
so a future change cannot silently regress into an accidentally-working
cross-instance assumption. Direct structural peer of
test_change_brief_result_buffer.py.

    python -m pytest backend/tests/unit/test_filing_qa_result_buffer.py -v
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

import server  # noqa: E402

USER = "fqa-buf-user"
OTHER = "fqa-buf-other"


def _payload(state="answered"):
    return {"ticker": "AAPL", "doc_id": "d1", "question": "q", "answer_text": "a [1].",
            "sources": [{"index": 1, "doc_id": "d1", "chunk_start": 0, "chunk_end": 0}],
            "cited_source_indices": [1], "state": state, "coverage_boundaries": []}


def _reset_buffer():
    server._FILING_QA_RESULTS.clear()


# --- same-process baseline -------------------------------------------------
def test_same_process_completed_result_is_retrievable():
    _reset_buffer()
    server._store_filing_qa_result("j1", USER, _payload())
    assert server._get_filing_qa_result("j1", USER) == _payload()


def test_owner_scoping_on_the_buffer():
    _reset_buffer()
    server._store_filing_qa_result("j2", USER, _payload())
    assert server._get_filing_qa_result("j2", OTHER) is None  # non-disclosure


# --- TTL expiration ---------------------------------------------------
def test_expired_result_is_treated_as_absent_not_a_stale_hit(monkeypatch):
    _reset_buffer()
    clock = {"now": 1_000.0}
    monkeypatch.setattr(server, "_fa_now", lambda: clock["now"])
    server._store_filing_qa_result("j3", USER, _payload())
    assert server._get_filing_qa_result("j3", USER) == _payload()
    clock["now"] += server.settings.max_job_lifetime_s + 1
    assert server._get_filing_qa_result("j3", USER) is None
    assert "j3" not in server._FILING_QA_RESULTS  # evicted on read


# --- bounded size ---------------------------------------------------
def test_buffer_is_bounded_by_a_fixed_entry_ceiling():
    _reset_buffer()
    for i in range(server._FQA_MAX_ENTRIES + 25):
        server._store_filing_qa_result(f"k{i:04d}", USER, _payload())
    assert len(server._FILING_QA_RESULTS) <= server._FQA_MAX_ENTRIES
    # oldest-first eviction: the very first ids are gone, the newest remain
    assert "k0000" not in server._FILING_QA_RESULTS
    assert f"k{server._FQA_MAX_ENTRIES + 24:04d}" in server._FILING_QA_RESULTS


# --- restart / cross-process unavailability -------------------------------
def test_result_does_not_survive_a_simulated_restart():
    """A restarted process is a fresh module-level dict — a job id known to the
    previous buffer is simply not found."""
    _reset_buffer()
    server._store_filing_qa_result("j-restart", USER, _payload())
    previous_buffer = server._FILING_QA_RESULTS
    server._FILING_QA_RESULTS = {}  # the "restarted process"
    try:
        assert server._get_filing_qa_result("j-restart", USER) is None
    finally:
        server._FILING_QA_RESULTS = previous_buffer
        _reset_buffer()


def test_cross_instance_result_is_not_retrievable():
    """Two independent buffers = two backend processes. A job completed in one
    is never visible from the other — there is no cross-process lookup path."""
    _reset_buffer()
    process_a = server._FILING_QA_RESULTS
    process_b: dict = {}

    server._FILING_QA_RESULTS = process_a
    server._store_filing_qa_result("j-xproc", USER, _payload())

    server._FILING_QA_RESULTS = process_b
    try:
        assert server._get_filing_qa_result("j-xproc", USER) is None
    finally:
        server._FILING_QA_RESULTS = process_a
        _reset_buffer()


# --- cancellation / failure pop the buffer --------------------------------
def test_cancellation_pops_the_buffer_entry():
    _reset_buffer()
    server._store_filing_qa_result("j-cancel", USER, _payload())
    server._FILING_QA_RESULTS.pop("j-cancel", None)  # mirrors cancel_filing_qa's own pop
    assert server._get_filing_qa_result("j-cancel", USER) is None


# --- SSE final frame under the same invariant --------------------------
def test_sse_final_frame_is_built_from_the_process_local_buffer():
    _reset_buffer()
    server._store_filing_qa_result("j-sse", USER, _payload("insufficient_evidence"))

    class _Events:
        def subscribe(self, job_id):
            async def _gen():
                yield {"node": "pipeline", "status": "start"}
                yield {"node": "pipeline", "status": "ok"}
            return _gen()

    orig_events = server.container.events
    object.__setattr__(server.container, "events", _Events())
    try:
        frames = asyncio.run(_drain(server._filing_qa_stream_events("j-sse", USER)))
    finally:
        object.__setattr__(server.container, "events", orig_events)
        _reset_buffer()

    final = [f for f in frames if f.get("node") == "final"]
    assert len(final) == 1
    assert final[0]["answer"] == _payload("insufficient_evidence")


def test_sse_emits_no_final_frame_when_the_buffer_has_no_result():
    """Simulates a stream consumed from a process whose buffer never held this
    job (cross-instance / post-restart) — trace frames still flow, but the
    stream never fabricates a `final` frame it cannot construct."""
    _reset_buffer()

    class _Events:
        def subscribe(self, job_id):
            async def _gen():
                yield {"node": "pipeline", "status": "ok"}
            return _gen()

    orig_events = server.container.events
    object.__setattr__(server.container, "events", _Events())
    try:
        frames = asyncio.run(_drain(server._filing_qa_stream_events("j-none", USER)))
    finally:
        object.__setattr__(server.container, "events", orig_events)

    assert not [f for f in frames if f.get("node") == "final"]


def test_sse_never_emits_final_on_failed_or_cancelled():
    # the frozen SSE convention: a job that reaches failed/cancelled emits no
    # final frame — only the preceding trace frames, then the terminal event.
    _reset_buffer()

    class _Events:
        def subscribe(self, job_id):
            async def _gen():
                yield {"node": "pipeline", "status": "start"}
                yield {"node": "pipeline", "status": "error", "message": "boom"}
            return _gen()

    orig_events = server.container.events
    object.__setattr__(server.container, "events", _Events())
    try:
        frames = asyncio.run(_drain(server._filing_qa_stream_events("j-failed", USER)))
    finally:
        object.__setattr__(server.container, "events", orig_events)

    assert not [f for f in frames if f.get("node") == "final"]


async def _drain(agen):
    return [ev async for ev in agen]


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
