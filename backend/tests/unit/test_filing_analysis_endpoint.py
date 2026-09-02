"""API / contract tests for the four M14 Filing Analysis routes
(Document 64 §9-§11, frozen; Document 65 §13). Hermetic: TestClient drives the
real ASGI stack (real routes, real FastAPI validation, real
domain_error_handler -> HTTP status mapping) with `server.db` swapped to a
fake motor-shaped DB -- same idiom as test_filing_content_get_endpoint.py /
test_comparison_explanation_endpoint.py.

The completed-analysis contract is exercised by driving `_run_filing_analysis`
directly with `analyze_filing` monkeypatched (no real LLM), since the async
job task cannot be awaited through the sync TestClient.

    python -m pytest backend/tests/unit/test_filing_analysis_endpoint.py -v
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from fastapi.testclient import TestClient  # noqa: E402

import server  # noqa: E402
from domain.models import JobKind  # noqa: E402

USER = {"id": "fa-user", "email": "fa@example.com"}
OTHER = {"id": "fa-other", "email": "other@example.com"}


# --- hermetic fake Mongo (find/find_one + exclusion projection + no-op sort) --
def _match(doc, filt):
    return all(doc.get(k) == v for k, v in filt.items())


def _project(doc, projection):
    row = dict(doc)
    for k, v in (projection or {}).items():
        if v == 0:
            row.pop(k, None)
    return row


class _FakeCursor:
    def __init__(self, docs, projection=None):
        self._docs, self._projection = docs, projection

    def sort(self, *_a, **_k):
        return self

    async def to_list(self, length=None):
        out = [_project(d, self._projection) for d in self._docs]
        return out if length is None else out[:length]


class _FakeCollection:
    def __init__(self, docs=None):
        self._docs = [dict(d) for d in (docs or [])]

    def find(self, filt, projection=None):
        return _FakeCursor([d for d in self._docs if _match(d, filt)], projection)

    async def find_one(self, filt, projection=None):
        for d in self._docs:
            if _match(d, filt):
                return _project(d, projection)
        return None


class _FakeDB:
    def __init__(self, filings=None, filing_chunks=None):
        self.filings = _FakeCollection(filings)
        self.filing_chunks = _FakeCollection(filing_chunks)


def _filing(doc_id="d1", ticker="AAPL", **kw):
    row = {
        "doc_id": doc_id, "ticker": ticker, "company_name": "Apple Inc.",
        "source": "10-Q 0000320193-24-000081 filed 2024-08-02",
        "num_chunks": 3, "char_count": 45000,
        "created_at": "2026-08-02T14:11:03.221+00:00",
    }
    row.update(kw)
    return row


def _chunk(doc_id="d1", chunk_idx=0, text="chunk text", ticker="AAPL"):
    return {"doc_id": doc_id, "ticker": ticker, "chunk_idx": chunk_idx, "text": text,
            "created_at": "2026-08-02T14:11:03.221+00:00", "embedding": [0.1] * 384}


server.app.dependency_overrides[server.current_user] = lambda: USER
client = TestClient(server.app)
PATH = "/api/companies/{t}/filings/{d}/analysis"


def _swap_db(fake):
    original = server.db
    server.db = fake
    return original


def _stub_llm():
    import agents.llm as llm
    orig = llm._generate_sync

    def _boom(*a, **k):
        raise llm.NonRetryableLLMError("real provider must never be called in a unit test")

    llm._generate_sync = _boom
    return orig


def _restore_llm(orig):
    import agents.llm as llm
    llm._generate_sync = orig


def _kill(job_id):
    t = server.RUNNING_TASKS.pop(job_id, None)
    if t is not None:
        t.cancel()
    server._FILING_ANALYSIS_RESULTS.pop(job_id, None)


def _stub_runner():
    """Replace the real job runner with a no-op so route-behaviour tests see a
    deterministic 'queued' job (TestClient's persistent loop can otherwise run
    the real task between calls)."""
    orig = server._run_filing_analysis

    async def _noop(*_a, **_k):
        return None

    server._run_filing_analysis = _noop
    return orig


def _restore_runner(orig):
    server._run_filing_analysis = orig


# ======================================================================= #
# request / validation / auth
# ======================================================================= #
def test_post_valid_returns_queued_and_never_reused():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk(chunk_idx=i) for i in range(3)])
    orig_db, orig_llm = _swap_db(fake), _stub_llm()
    try:
        r = client.post(PATH.format(t="aapl", d="d1"), json={})
        assert r.status_code == 200, r.text
        body = r.json()
        assert set(body) == {"id", "status", "reused"}
        assert body["status"] == "queued" and body["reused"] is False
        _kill(body["id"])
    finally:
        server.db = orig_db
        _restore_llm(orig_llm)


def test_post_with_no_body_is_accepted():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db, orig_llm = _swap_db(fake), _stub_llm()
    try:
        r = client.post(PATH.format(t="AAPL", d="d1"))
        assert r.status_code == 200, r.text
        _kill(r.json()["id"])
    finally:
        server.db = orig_db
        _restore_llm(orig_llm)


def test_empty_ticker_is_422():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)
    try:
        r = client.post("/api/companies/%20%20/filings/d1/analysis", json={})
        assert r.status_code == 422
        assert r.json()["type"] == "validation_error"
    finally:
        server.db = orig_db


def test_unknown_ticker_doc_id_is_404():
    fake = _FakeDB(filings=[], filing_chunks=[])
    orig_db = _swap_db(fake)
    try:
        r = client.post(PATH.format(t="AAPL", d="nope"), json={})
        assert r.status_code == 404 and r.json()["type"] == "not_found"
    finally:
        server.db = orig_db


def test_doc_id_under_a_different_ticker_is_404_non_disclosure():
    fake = _FakeDB(filings=[_filing(doc_id="d1", ticker="AAPL")], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)
    try:
        r = client.post(PATH.format(t="MSFT", d="d1"), json={})
        assert r.status_code == 404
    finally:
        server.db = orig_db


def test_unauthenticated_is_rejected():
    del server.app.dependency_overrides[server.current_user]
    try:
        r = client.post(PATH.format(t="AAPL", d="d1"), json={})
        assert r.status_code == 401
    finally:
        server.app.dependency_overrides[server.current_user] = lambda: USER


def test_custom_provider_from_non_admin_is_403():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)
    try:
        r = client.post(PATH.format(t="AAPL", d="d1"), json={"llm_provider": "custom"})
        assert r.status_code == 403
    finally:
        server.db = orig_db


# ======================================================================= #
# GET / cancel — status + owner scoping
# ======================================================================= #
def test_get_unknown_id_is_404():
    r = client.get(PATH.format(t="AAPL", d="d1") + "/does-not-exist")
    assert r.status_code == 404


def test_get_queued_job_returns_status_without_analysis():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db, orig_run = _swap_db(fake), _stub_runner()
    try:
        jid = client.post(PATH.format(t="AAPL", d="d1"), json={}).json()["id"]
        r = client.get(PATH.format(t="AAPL", d="d1") + f"/{jid}")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == jid and body["status"] == "queued"
        assert "analysis" not in body
        _kill(jid)
    finally:
        server.db = orig_db
        _restore_runner(orig_run)


def test_cancel_by_non_owner_is_404_and_by_owner_cancels():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db, orig_run = _swap_db(fake), _stub_runner()
    try:
        jid = client.post(PATH.format(t="AAPL", d="d1"), json={}).json()["id"]

        server.app.dependency_overrides[server.current_user] = lambda: OTHER
        r_other = client.post(PATH.format(t="AAPL", d="d1") + f"/{jid}/cancel")
        server.app.dependency_overrides[server.current_user] = lambda: USER
        assert r_other.status_code == 404

        r = client.post(PATH.format(t="AAPL", d="d1") + f"/{jid}/cancel")
        assert r.status_code == 200 and r.json() == {"id": jid, "status": "cancelled"}
        _kill(jid)
    finally:
        server.db = orig_db
        _restore_runner(orig_run)


# ======================================================================= #
# completed-analysis contract  (drive _run_filing_analysis directly)
# ======================================================================= #
def _canned_result():
    def out(state, cites):
        srcs = [{"index": i + 1, "doc_id": "d1", "chunk_start": c, "chunk_end": c} for i, c in enumerate(cites)]
        return {
            "narrative": " ".join(f"claim [{i+1}]." for i in range(len(cites))) if cites else "",
            "sources": srcs,
            "cited_source_indices": [s["index"] for s in srcs],
            "state": state,
            "coverage_boundaries": [] if state == "complete" else ["boundary reason"],
        }
    return {
        "outputs": {
            "Filing Summary": out("complete", [0, 1]),
            "Risk Factors Digest": out("partial", [2]),
            "MD&A Digest": out("insufficient_evidence", []),
            "Important Changes": out("complete", [3]),
        },
        "prompt_version": "v1",
        "schema_version": "v1",
    }


def test_completed_analysis_payload_conforms_to_document_64():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk(chunk_idx=i, text=f"c{i}") for i in range(4)])
    orig_db = _swap_db(fake)

    async def _fake_analyze(chunks, doc_id, **kw):
        assert doc_id == "d1" and [c["chunk_idx"] for c in chunks] == [0, 1, 2, 3]
        return _canned_result()

    orig_analyze = server.analyze_filing
    server.analyze_filing = _fake_analyze
    try:
        jid = "fa-complete-1"
        asyncio.run(server.container.job_lifecycle.start(
            jid, JobKind.FILING_ANALYSIS, USER["id"], ticker="AAPL", deadline_s=180))
        asyncio.run(server._run_filing_analysis(jid, "AAPL", "d1", USER["id"]))

        r = client.get(PATH.format(t="AAPL", d="d1") + f"/{jid}")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == jid and body["status"] == "completed"
        a = body["analysis"]
        # metadata echoed verbatim; no _id / embedding anywhere
        assert a["doc_id"] == "d1" and a["ticker"] == "AAPL" and a["company_name"] == "Apple Inc."
        assert a["source"].startswith("10-Q ") and a["prompt_version"] == "v1"
        # Document 59 §5.2 / Document 64 §9.3 -- never echo internal fields
        assert "_id" not in a and "embedding" not in str(a)
        for o in a["outputs"].values():
            for s in o["sources"]:
                assert "_id" not in s and "embedding" not in s
        # exactly the four outputs, each a flat cited narrative + state
        assert set(a["outputs"]) == {"Filing Summary", "Risk Factors Digest", "MD&A Digest", "Important Changes"}
        for o in a["outputs"].values():
            assert set(o) == {"narrative", "sources", "cited_source_indices", "state", "coverage_boundaries"}
            assert o["state"] in ("complete", "partial", "insufficient_evidence")
            for s in o["sources"]:
                assert set(s) == {"index", "doc_id", "chunk_start", "chunk_end"}
        # insufficient_evidence output carries no claims / citations
        mda = a["outputs"]["MD&A Digest"]
        assert mda["narrative"] == "" and mda["sources"] == [] and mda["cited_source_indices"] == []

        # owner scoping on GET
        server.app.dependency_overrides[server.current_user] = lambda: OTHER
        r_other = client.get(PATH.format(t="AAPL", d="d1") + f"/{jid}")
        server.app.dependency_overrides[server.current_user] = lambda: USER
        assert r_other.status_code == 404
    finally:
        server.analyze_filing = orig_analyze
        server.db = orig_db
        server._FILING_ANALYSIS_RESULTS.pop("fa-complete-1", None)


def test_empty_filing_completes_all_insufficient_evidence():
    fake = _FakeDB(filings=[_filing(num_chunks=0)], filing_chunks=[])
    orig_db = _swap_db(fake)
    try:
        jid = "fa-empty-1"
        asyncio.run(server.container.job_lifecycle.start(
            jid, JobKind.FILING_ANALYSIS, USER["id"], ticker="AAPL", deadline_s=180))
        asyncio.run(server._run_filing_analysis(jid, "AAPL", "d1", USER["id"]))
        a = client.get(PATH.format(t="AAPL", d="d1") + f"/{jid}").json()["analysis"]
        assert all(o["state"] == "insufficient_evidence" for o in a["outputs"].values())
    finally:
        server.db = orig_db
        server._FILING_ANALYSIS_RESULTS.pop("fa-empty-1", None)


def test_m1_shared_helper_orders_chunks_and_omits_malformed_in_the_m14_path():
    # bounded-revision M-1: _run_filing_analysis loads chunks through the same
    # _load_ordered_filing_chunks helper as M13 get_filing_content -> a row
    # with a non-int chunk_idx or non-str text is dropped, and the result is
    # chunk_idx-ascending, before analyze_filing ever sees it.
    fake = _FakeDB(
        filings=[_filing(num_chunks=3)],
        filing_chunks=[
            _chunk(chunk_idx=1, text="one"),
            {"doc_id": "d1", "ticker": "AAPL", "text": "no chunk_idx"},
            {"doc_id": "d1", "ticker": "AAPL", "chunk_idx": 2},        # no text
            _chunk(chunk_idx=0, text="zero"),
        ],
    )
    orig_db = _swap_db(fake)
    seen = {}

    async def _capture(chunks, doc_id, **kw):
        seen["chunks"] = chunks
        return _canned_result()

    orig_analyze = server.analyze_filing
    server.analyze_filing = _capture
    try:
        jid = "fa-m1-malformed"
        asyncio.run(server.container.job_lifecycle.start(
            jid, JobKind.FILING_ANALYSIS, USER["id"], ticker="AAPL", deadline_s=180))
        asyncio.run(server._run_filing_analysis(jid, "AAPL", "d1", USER["id"]))
    finally:
        server.analyze_filing = orig_analyze
        server.db = orig_db
        server._FILING_ANALYSIS_RESULTS.pop("fa-m1-malformed", None)

    assert [c["chunk_idx"] for c in seen["chunks"]] == [0, 1]
    assert all(set(c) == {"chunk_idx", "text"} for c in seen["chunks"])
