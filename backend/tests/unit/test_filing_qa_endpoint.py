"""API / contract tests for the four M16 Filing Q&A routes (Document 87
Revision 2 §3/§9-§14; Document 94 Revision 1 §9-§12/§18). Hermetic:
TestClient drives the real ASGI stack (real routes, real FastAPI validation,
real domain_error_handler -> HTTP status mapping) with `server.db` swapped to
a fake motor-shaped DB -- same idiom as test_filing_analysis_endpoint.py.

The completed-answer contract is exercised by driving `_run_filing_qa`
directly with `answer_question` monkeypatched (no real LLM), since the async
job task cannot be awaited through the sync TestClient.

    python -m pytest backend/tests/unit/test_filing_qa_endpoint.py -v
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

USER = {"id": "fqa-user", "email": "fqa@example.com"}
OTHER = {"id": "fqa-other", "email": "other@example.com"}


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
PATH = "/api/companies/{t}/filings/{d}/qa"


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
    server._FILING_QA_RESULTS.pop(job_id, None)


def _stub_runner():
    """Replace the real job runner with a no-op so route-behaviour tests see a
    deterministic 'queued' job (TestClient's persistent loop can otherwise run
    the real task between calls)."""
    orig = server._run_filing_qa

    async def _noop(*_a, **_k):
        return None

    server._run_filing_qa = _noop
    return orig


def _restore_runner(orig):
    server._run_filing_qa = orig


# ======================================================================= #
# request / validation / auth
# ======================================================================= #
def test_post_valid_returns_queued_and_never_reused():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk(chunk_idx=i) for i in range(3)])
    orig_db, orig_llm = _swap_db(fake), _stub_llm()
    try:
        r = client.post(PATH.format(t="aapl", d="d1"), json={"question": "What are the risks?"})
        assert r.status_code == 200, r.text
        body = r.json()
        assert set(body) == {"id", "status", "reused"}
        assert body["status"] == "queued" and body["reused"] is False
        _kill(body["id"])
    finally:
        server.db = orig_db
        _restore_llm(orig_llm)


def test_missing_question_is_422():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)
    try:
        r = client.post(PATH.format(t="AAPL", d="d1"), json={})
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig_db


def test_bare_post_with_no_body_is_422():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)
    try:
        r = client.post(PATH.format(t="AAPL", d="d1"))
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig_db


def test_whitespace_only_question_is_422():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)
    try:
        r = client.post(PATH.format(t="AAPL", d="d1"), json={"question": "   "})
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig_db


def test_question_over_max_length_is_422():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)
    try:
        too_long = "x" * (server.settings.fqa_max_question_chars + 1)
        r = client.post(PATH.format(t="AAPL", d="d1"), json={"question": too_long})
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig_db


def test_question_is_trimmed_before_processing():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db, orig_run = _swap_db(fake), _stub_runner()
    seen = {}

    async def _capture(job_id, ticker, doc_id, question, user_id, **kw):
        seen["question"] = question

    server._run_filing_qa = _capture
    try:
        r = client.post(PATH.format(t="AAPL", d="d1"), json={"question": "  What changed?  "})
        assert r.status_code == 200
        _kill(r.json()["id"])
    finally:
        server.db = orig_db
        _restore_runner(orig_run)
    assert seen["question"] == "What changed?"


def test_empty_ticker_is_422():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)
    try:
        r = client.post("/api/companies/%20%20/filings/d1/qa", json={"question": "q"})
        assert r.status_code == 422
        assert r.json()["type"] == "validation_error"
    finally:
        server.db = orig_db


def test_unknown_ticker_doc_id_is_404():
    fake = _FakeDB(filings=[], filing_chunks=[])
    orig_db = _swap_db(fake)
    try:
        r = client.post(PATH.format(t="AAPL", d="nope"), json={"question": "q"})
        assert r.status_code == 404 and r.json()["type"] == "not_found"
    finally:
        server.db = orig_db


def test_doc_id_under_a_different_ticker_is_404_non_disclosure():
    fake = _FakeDB(filings=[_filing(doc_id="d1", ticker="AAPL")], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)
    try:
        r = client.post(PATH.format(t="MSFT", d="d1"), json={"question": "q"})
        assert r.status_code == 404
    finally:
        server.db = orig_db


def test_unauthenticated_is_rejected():
    del server.app.dependency_overrides[server.current_user]
    try:
        r = client.post(PATH.format(t="AAPL", d="d1"), json={"question": "q"})
        assert r.status_code == 401
    finally:
        server.app.dependency_overrides[server.current_user] = lambda: USER


def test_custom_provider_from_non_admin_is_403():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)
    try:
        r = client.post(PATH.format(t="AAPL", d="d1"), json={"question": "q", "llm_provider": "custom"})
        assert r.status_code == 403
    finally:
        server.db = orig_db


def test_unsafe_custom_base_url_is_400_with_no_type_field():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db, orig_admin = _swap_db(fake), server.require_admin
    server.require_admin = lambda user, **kw: None  # bypass the (separately tested) 403 gate
    # The local dev .env sets LLM_ALLOW_PRIVATE_BASE_URL=true as a deliberate
    # self-hosting escape hatch (agents/llm.py::assert_public_url's own
    # docstring) — suspend it so this test exercises the real SSRF guard.
    had_escape = os.environ.pop("LLM_ALLOW_PRIVATE_BASE_URL", None)
    try:
        r = client.post(
            PATH.format(t="AAPL", d="d1"),
            json={"question": "q", "llm_provider": "custom", "llm_base_url": "http://127.0.0.1:9999"},
        )
        assert r.status_code == 400
        assert "type" not in r.json()  # established M14/M15 deviation, reproduced exactly
    finally:
        server.db = orig_db
        server.require_admin = orig_admin
        if had_escape is not None:
            os.environ["LLM_ALLOW_PRIVATE_BASE_URL"] = had_escape


# ======================================================================= #
# GET / cancel — status + owner scoping
# ======================================================================= #
def test_get_unknown_id_is_404():
    r = client.get(PATH.format(t="AAPL", d="d1") + "/does-not-exist")
    assert r.status_code == 404


def test_get_queued_job_returns_status_without_answer():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db, orig_run = _swap_db(fake), _stub_runner()
    try:
        jid = client.post(PATH.format(t="AAPL", d="d1"), json={"question": "q"}).json()["id"]
        r = client.get(PATH.format(t="AAPL", d="d1") + f"/{jid}")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == jid and body["status"] == "queued"
        assert "answer" not in body
        _kill(jid)
    finally:
        server.db = orig_db
        _restore_runner(orig_run)


def test_cancel_by_non_owner_is_404_and_by_owner_cancels():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db, orig_run = _swap_db(fake), _stub_runner()
    try:
        jid = client.post(PATH.format(t="AAPL", d="d1"), json={"question": "q"}).json()["id"]

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


def test_cancel_on_terminal_job_is_idempotent():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db, orig_run = _swap_db(fake), _stub_runner()
    try:
        jid = client.post(PATH.format(t="AAPL", d="d1"), json={"question": "q"}).json()["id"]
        client.post(PATH.format(t="AAPL", d="d1") + f"/{jid}/cancel")
        r2 = client.post(PATH.format(t="AAPL", d="d1") + f"/{jid}/cancel")
        assert r2.status_code == 200 and r2.json()["status"] == "cancelled"
        _kill(jid)
    finally:
        server.db = orig_db
        _restore_runner(orig_run)


# ======================================================================= #
# completed-answer contract  (drive _run_filing_qa directly)
# ======================================================================= #
def _canned_answered():
    return {
        "answer_text": "Revenue grew [1].",
        "sources": [{"index": 1, "doc_id": "d1", "chunk_start": 0, "chunk_end": 1}],
        "cited_source_indices": [1],
        "state": "answered",
        "coverage_boundaries": [],
        "prompt_version": "v1",
        "schema_version": "v1",
    }


def _canned_insufficient():
    return {
        "answer_text": "The filing does not address this question.",
        "sources": [],
        "cited_source_indices": [],
        "state": "insufficient_evidence",
        "coverage_boundaries": ["no substantive grounded claim survived validation"],
        "prompt_version": "v1",
        "schema_version": "v1",
    }


def test_completed_answered_payload_conforms_to_document_87():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk(chunk_idx=i, text=f"c{i}") for i in range(3)])
    orig_db = _swap_db(fake)

    async def _fake_answer(chunks, doc_id, question, **kw):
        assert doc_id == "d1" and question == "What grew?"
        return _canned_answered()

    orig_answer = server.answer_question
    server.answer_question = _fake_answer
    try:
        jid = "fqa-complete-1"
        asyncio.run(server.container.job_lifecycle.start(
            jid, JobKind.FILING_QA, USER["id"], ticker="AAPL", deadline_s=120))
        asyncio.run(server._run_filing_qa(jid, "AAPL", "d1", "What grew?", USER["id"]))

        r = client.get(PATH.format(t="AAPL", d="d1") + f"/{jid}")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == jid and body["status"] == "completed"
        a = body["answer"]
        assert set(a) == {
            "ticker", "doc_id", "question", "answer_text", "sources",
            "cited_source_indices", "state", "coverage_boundaries",
            "created_at", "prompt_version", "schema_version",
        }
        assert a["ticker"] == "AAPL" and a["doc_id"] == "d1" and a["question"] == "What grew?"
        assert a["state"] == "answered" and a["sources"] and a["cited_source_indices"]
        assert "_id" not in a and "embedding" not in str(a)

        # owner scoping on GET
        server.app.dependency_overrides[server.current_user] = lambda: OTHER
        r_other = client.get(PATH.format(t="AAPL", d="d1") + f"/{jid}")
        server.app.dependency_overrides[server.current_user] = lambda: USER
        assert r_other.status_code == 404
    finally:
        server.answer_question = orig_answer
        server.db = orig_db
        server._FILING_QA_RESULTS.pop("fqa-complete-1", None)


def test_completed_insufficient_evidence_payload():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    orig_db = _swap_db(fake)

    async def _fake_answer(chunks, doc_id, question, **kw):
        return _canned_insufficient()

    orig_answer = server.answer_question
    server.answer_question = _fake_answer
    try:
        jid = "fqa-insuff-1"
        asyncio.run(server.container.job_lifecycle.start(
            jid, JobKind.FILING_QA, USER["id"], ticker="AAPL", deadline_s=120))
        asyncio.run(server._run_filing_qa(jid, "AAPL", "d1", "Unanswerable?", USER["id"]))

        a = client.get(PATH.format(t="AAPL", d="d1") + f"/{jid}").json()["answer"]
        assert a["state"] == "insufficient_evidence"
        assert a["sources"] == [] and a["cited_source_indices"] == []
    finally:
        server.answer_question = orig_answer
        server.db = orig_db
        server._FILING_QA_RESULTS.pop("fqa-insuff-1", None)


def test_zero_content_filing_completes_never_404_never_502():
    fake = _FakeDB(filings=[_filing(num_chunks=0)], filing_chunks=[])
    orig_db = _swap_db(fake)
    try:
        jid = "fqa-zero-1"
        asyncio.run(server.container.job_lifecycle.start(
            jid, JobKind.FILING_QA, USER["id"], ticker="AAPL", deadline_s=120))
        asyncio.run(server._run_filing_qa(jid, "AAPL", "d1", "Anything?", USER["id"]))

        r = client.get(PATH.format(t="AAPL", d="d1") + f"/{jid}")
        assert r.status_code == 200
        a = r.json()["answer"]
        assert a["state"] == "insufficient_evidence"
        assert a["sources"] == [] and a["cited_source_indices"] == []
    finally:
        server.db = orig_db
        server._FILING_QA_RESULTS.pop("fqa-zero-1", None)


def test_m14_and_m15_route_families_are_unaffected_by_the_fqa_addition():
    # regression guard named by Document 94 Revision 1 §18: adding FQA must
    # not disturb the pre-existing route surface.
    schema = server.app.openapi()
    paths = set(schema["paths"])
    assert "/api/companies/{ticker}/filings/{doc_id}/analysis" in paths
    assert "/api/companies/{ticker}/changes" in paths
    assert "/api/companies/{ticker}/filings/{doc_id}/qa" in paths


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
