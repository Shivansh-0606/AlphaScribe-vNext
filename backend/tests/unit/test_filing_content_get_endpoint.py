"""API/contract tests for GET /companies/{ticker}/filings/{doc_id}/content
(M13 — Document 59 CTO-RATIFIED / FROZEN, Document 60 CTO-RATIFIED / FROZEN,
2026-08-27; M13 Implementation Authorization, 2026-08-27).

Hermetic: TestClient drives the real ASGI stack (real route, real FastAPI
validation, real domain_error_handler -> HTTP status mapping) with
`server.db` swapped to a fake motor-shaped DB — the same technique
test_comparison_explanation_endpoint.py / test_financials_acquire_endpoint.py
already use for a login-walled `db`-backed route.

The fake cursor's `.sort()` is a deliberate NO-OP: Document 59 §6 /
Document 60 §3.2 require the handler to re-order chunks by `chunk_idx` in
Python so incidental Mongo ordering is never trusted, and a no-op fake sort
proves the handler does not lean on the driver call (it also records that
`.sort("chunk_idx", 1)` WAS issued, for literal contract compliance).

    python -m pytest backend/tests/unit/test_filing_content_get_endpoint.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from fastapi.testclient import TestClient  # noqa: E402

import server  # noqa: E402

USER = {"id": "filing-content-user", "email": "fc@example.com"}


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
        self._docs = docs
        self._projection = projection
        self.sort_calls = []

    def sort(self, key, direction=1):
        # Deliberate no-op — see module docstring.
        self.sort_calls.append((key, direction))
        return self

    async def to_list(self, length=None):
        out = [_project(d, self._projection) for d in self._docs]
        return out if length is None else out[:length]


class _FakeCollection:
    def __init__(self, docs=None):
        self._docs = [dict(d) for d in (docs or [])]
        self.last_cursor = None

    def find(self, filt, projection=None):
        cur = _FakeCursor([d for d in self._docs if _match(d, filt)], projection)
        self.last_cursor = cur
        return cur

    async def find_one(self, filt, projection=None):
        for d in self._docs:
            if _match(d, filt):
                return _project(d, projection)
        return None


class _RaisingCollection:
    def find(self, *a, **kw):
        raise ConnectionError("mongo unreachable")

    async def find_one(self, *a, **kw):
        raise ConnectionError("mongo unreachable")


class _FakeDB:
    def __init__(self, filings=None, filing_chunks=None):
        self.filings = _FakeCollection(filings)
        self.filing_chunks = _FakeCollection(filing_chunks)


def _filing(doc_id="d1", ticker="AAPL", **kw):
    row = {
        "doc_id": doc_id,
        "ticker": ticker,
        "company_name": "Apple Inc.",
        "source": "10-Q 0000320193-24-000081 filed 2024-08-02",
        "num_chunks": 3,
        "char_count": 45000,
        "created_at": "2026-08-02T14:11:03.221+00:00",
    }
    row.update(kw)
    return row


def _chunk(doc_id="d1", chunk_idx=0, text="chunk text", *, with_embedding=True, ticker="AAPL"):
    row = {
        "doc_id": doc_id,
        "ticker": ticker,
        "source": "10-Q 0000320193-24-000081 filed 2024-08-02",
        "chunk_idx": chunk_idx,
        "text": text,
        "created_at": "2026-08-02T14:11:03.221+00:00",
    }
    if with_embedding:
        row["embedding"] = [0.1] * 384
    return row


server.app.dependency_overrides[server.current_user] = lambda: USER
client = TestClient(server.app)

PATH = "/api/companies/{ticker}/filings/{doc_id}/content"


def _get(ticker="AAPL", doc_id="d1"):
    return client.get(PATH.format(ticker=ticker, doc_id=doc_id))


def _with_db(fake_db):
    original = server.db
    server.db = fake_db
    return original


# --- happy path -------------------------------------------------------------


def test_authenticated_successful_read_returns_the_frozen_envelope():
    fake = _FakeDB(
        filings=[_filing()],
        filing_chunks=[
            _chunk(chunk_idx=0, text="alpha"),
            _chunk(chunk_idx=1, text="bravo"),
            _chunk(chunk_idx=2, text="charlie"),
        ],
    )
    original = _with_db(fake)
    try:
        r = _get()
    finally:
        server.db = original
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {
        "doc_id", "ticker", "company_name", "source",
        "created_at", "num_chunks", "char_count", "content",
    }
    assert body["doc_id"] == "d1"
    assert body["ticker"] == "AAPL"
    assert body["company_name"] == "Apple Inc."
    assert body["source"] == "10-Q 0000320193-24-000081 filed 2024-08-02"
    assert body["num_chunks"] == 3
    assert body["char_count"] == 45000
    assert body["content"] == {
        "chunks": [
            {"chunk_idx": 0, "text": "alpha"},
            {"chunk_idx": 1, "text": "bravo"},
            {"chunk_idx": 2, "text": "charlie"},
        ]
    }
    # No `partial` / flag fields — the ratified envelope has none.
    assert "partial" not in body and "content_available" not in body


def test_company_name_null_is_passed_through():
    fake = _FakeDB(filings=[_filing(company_name=None)], filing_chunks=[_chunk()])
    original = _with_db(fake)
    try:
        r = _get()
    finally:
        server.db = original
    assert r.status_code == 200
    assert r.json()["company_name"] is None


# --- OD-6: unknown filing -> 404 ------------------------------------------------


def test_unknown_doc_id_returns_404():
    fake = _FakeDB(filings=[], filing_chunks=[])
    original = _with_db(fake)
    try:
        r = _get(doc_id="does-not-exist")
    finally:
        server.db = original
    assert r.status_code == 404
    assert r.json()["type"] == "not_found"


def test_doc_id_under_a_different_ticker_returns_404():
    # "does not exist for the requested company" (Document 59 §3.1 / OD-6).
    fake = _FakeDB(filings=[_filing(doc_id="d1", ticker="MSFT")], filing_chunks=[_chunk(doc_id="d1")])
    original = _with_db(fake)
    try:
        r = _get(ticker="AAPL", doc_id="d1")
    finally:
        server.db = original
    assert r.status_code == 404
    assert r.json()["type"] == "not_found"


# --- OD-7: known filing, zero chunks -> 200 + empty collection ---------------


def test_known_filing_with_no_chunks_returns_200_and_empty_collection():
    fake = _FakeDB(filings=[_filing(num_chunks=0)], filing_chunks=[])
    original = _with_db(fake)
    try:
        r = _get()
    finally:
        server.db = original
    assert r.status_code == 200
    body = r.json()
    assert body["doc_id"] == "d1"
    assert body["content"] == {"chunks": []}
    # distinct from the 404 case: metadata envelope is present, status is 200.


# --- ordering (Document 59 §6) ----------------------------------------------


def test_chunks_returned_in_ascending_chunk_idx_order_from_out_of_order_input():
    fake = _FakeDB(
        filings=[_filing()],
        filing_chunks=[
            _chunk(chunk_idx=2, text="c2"),
            _chunk(chunk_idx=0, text="c0"),
            _chunk(chunk_idx=1, text="c1"),
        ],
    )
    original = _with_db(fake)
    try:
        r = _get()
    finally:
        server.db = original
    idxs = [c["chunk_idx"] for c in r.json()["content"]["chunks"]]
    assert idxs == [0, 1, 2]


def test_ordering_does_not_depend_on_incidental_mongo_ordering():
    # The fake cursor's .sort() is a no-op; input is reverse-ordered. If the
    # handler leaned on the driver sort, this would come back reversed.
    fake = _FakeDB(
        filings=[_filing(num_chunks=4)],
        filing_chunks=[_chunk(chunk_idx=i, text=f"c{i}") for i in (3, 1, 2, 0)],
    )
    original = _with_db(fake)
    try:
        r = _get()
    finally:
        server.db = original
    idxs = [c["chunk_idx"] for c in r.json()["content"]["chunks"]]
    assert idxs == [0, 1, 2, 3]
    # ...and the handler still issued the ratified explicit sort on the query.
    assert fake.filing_chunks.last_cursor.sort_calls == [("chunk_idx", 1)]


# --- persisted representation preserved (Document 59 §5.1 / OD-2) --------------


def test_persisted_chunk_representation_is_preserved_and_stripped_to_idx_text():
    fake = _FakeDB(
        filings=[_filing(num_chunks=1)],
        filing_chunks=[_chunk(chunk_idx=0, text="  verbatim  text with\nnewlines  ", with_embedding=True)],
    )
    original = _with_db(fake)
    try:
        r = _get()
    finally:
        server.db = original
    chunks = r.json()["content"]["chunks"]
    assert len(chunks) == 1
    # exactly the persisted representation: chunk_idx + text, nothing else.
    assert set(chunks[0].keys()) == {"chunk_idx", "text"}
    # text is byte-identical to what was persisted — no trim/transform.
    assert chunks[0]["text"] == "  verbatim  text with\nnewlines  "
    # embedding / _id / ticker / source / created_at never surface.
    assert "embedding" not in chunks[0]


# --- OD-8 (delegated): malformed/gapped chunks --------------------------------


def test_malformed_chunk_is_omitted_not_fatal_and_envelope_unchanged():
    fake = _FakeDB(
        filings=[_filing(num_chunks=4)],
        filing_chunks=[
            _chunk(chunk_idx=0, text="good0"),
            {"doc_id": "d1", "text": "missing chunk_idx"},           # no chunk_idx
            {"doc_id": "d1", "chunk_idx": 2},                        # no text
            _chunk(chunk_idx=3, text="good3"),
        ],
    )
    original = _with_db(fake)
    try:
        r = _get()
    finally:
        server.db = original
    assert r.status_code == 200
    body = r.json()
    assert body["content"] == {"chunks": [{"chunk_idx": 0, "text": "good0"}, {"chunk_idx": 3, "text": "good3"}]}
    # contract unchanged: no `partial` flag added.
    assert "partial" not in body


# --- error handling ----------------------------------------------------------


def test_synchronous_infrastructure_failure_returns_502_and_no_internal_detail():
    fake = _FakeDB()
    fake.filings = _RaisingCollection()
    original = _with_db(fake)
    try:
        r = _get()
    finally:
        server.db = original
    assert r.status_code == 502
    assert "mongo unreachable" not in r.text.lower()


def test_malformed_filing_row_missing_required_field_returns_502_no_leaked_detail():
    # Document 59 §8 (last row) / §9 — delegated to the implementation phase:
    # an EXISTING filings row (so this is not the OD-6 404 path) that cannot be
    # assembled into the §5.1 envelope because a required response field is
    # absent must map to the established safe 502, never an unhandled 500
    # leaking the raw KeyError. Here `source` is dropped from an otherwise
    # normal row; the handler's `filing["source"]` raises KeyError inside the
    # try, is not a DomainError, and falls through to InfrastructureError.
    bad = _filing()
    del bad["source"]  # a required §5.1 envelope field
    fake = _FakeDB(filings=[bad], filing_chunks=[_chunk(chunk_idx=0, text="present")])
    original = _with_db(fake)
    try:
        r = _get()
    finally:
        server.db = original
    assert r.status_code == 502
    body = r.json()
    # established error envelope (backend/app/api/errors.py: {detail, type}).
    assert body["type"] == "infrastructure_error"
    assert body["detail"] == "Failed to read filing content. See server logs for details."
    # no raw exception / implementation detail leaked to the client.
    assert "keyerror" not in r.text.lower()
    assert "'source'" not in r.text
    assert "traceback" not in r.text.lower()


def test_empty_ticker_after_normalisation_returns_422():
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    original = _with_db(fake)
    try:
        r = client.get("/api/companies/%20/filings/d1/content")
    finally:
        server.db = original
    assert r.status_code == 422


def test_unauthenticated_request_returns_401():
    del server.app.dependency_overrides[server.current_user]
    fake = _FakeDB(filings=[_filing()], filing_chunks=[_chunk()])
    original = _with_db(fake)
    try:
        r = _get()
        assert r.status_code == 401
    finally:
        server.db = original
        server.app.dependency_overrides[server.current_user] = lambda: USER


if __name__ == "__main__":
    test_authenticated_successful_read_returns_the_frozen_envelope()
    test_company_name_null_is_passed_through()
    test_unknown_doc_id_returns_404()
    test_doc_id_under_a_different_ticker_returns_404()
    test_known_filing_with_no_chunks_returns_200_and_empty_collection()
    test_chunks_returned_in_ascending_chunk_idx_order_from_out_of_order_input()
    test_ordering_does_not_depend_on_incidental_mongo_ordering()
    test_persisted_chunk_representation_is_preserved_and_stripped_to_idx_text()
    test_malformed_chunk_is_omitted_not_fatal_and_envelope_unchanged()
    test_synchronous_infrastructure_failure_returns_502_and_no_internal_detail()
    test_malformed_filing_row_missing_required_field_returns_502_no_leaked_detail()
    test_empty_ticker_after_normalisation_returns_422()
    test_unauthenticated_request_returns_401()
    print("ok: GET /companies/{ticker}/filings/{doc_id}/content — frozen envelope, "
          "OD-6 404, OD-7 200+empty, chunk_idx ordering (Python re-sort), persisted "
          "representation preserved, OD-8 malformed-chunk omission, 401/422/502")
