"""Iteration 8: M16 Filing Q&A (FQA v1) — Documents 87 Revision 2 / 90 / 94
Revision 1 (candidate selection as amended by Documents 95/96). Full
create -> stream -> status -> cancel lifecycle against a running server +
real Mongo (+ real LLM for the happy-path test), plus the response-shape,
ownership, and not-found properties the contract calls out.
"""
import json
import os
import time

import pytest
import requests

from conftest import login

# 06 §5.1 Ph0 / 05 T-1: needs a live server (+ Mongo, + LLM/network for the
# happy-path test). Excluded from the hermetic CI job via `-m "not live"`.
pytestmark = pytest.mark.live

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    login(s, "iter8fqa")
    return s


@pytest.fixture(scope="module")
def other_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    login(s, "iter8fqa-other")
    return s


@pytest.fixture(scope="module")
def aapl_filing(client):
    """An ingested AAPL filing's (ticker, doc_id) — seeds sample data if none
    exists yet, then reads it back through the established GET /filings
    listing route (no direct DB access from the test)."""
    client.post(f"{API}/ingest/samples")
    r = client.get(f"{API}/filings", params={"ticker": "AAPL"})
    assert r.status_code == 200, r.text
    rows = r.json()["filings"]
    assert rows, "expected at least one ingested AAPL filing"
    return "AAPL", rows[0]["doc_id"]


def _poll_until_terminal(client, ticker, doc_id, job_id, timeout=150):
    deadline = time.time() + timeout
    while time.time() < deadline:
        r = client.get(f"{API}/companies/{ticker}/filings/{doc_id}/qa/{job_id}")
        assert r.status_code == 200, r.text
        body = r.json()
        if body["status"] in ("completed", "failed", "cancelled"):
            return body
        time.sleep(2)
    raise AssertionError(f"job {job_id} did not reach a terminal state within {timeout}s")


def _consume_stream(client, ticker, doc_id, job_id, timeout=150):
    """Returns (seen_nodes, final_event or None)."""
    seen_nodes = set()
    final_event = None
    url = f"{API}/companies/{ticker}/filings/{doc_id}/qa/{job_id}/stream"
    with client.get(url, stream=True, timeout=timeout) as r:
        assert r.status_code == 200
        start = time.time()
        for raw in r.iter_lines(decode_unicode=True):
            if time.time() - start > timeout:
                break
            if not raw:
                continue
            if raw.startswith("event: end"):
                break
            if raw.startswith("data:"):
                payload = raw[5:].strip()
                if not payload or payload == "{}":
                    continue
                ev = json.loads(payload)
                node = ev.get("node")
                if node:
                    seen_nodes.add(node)
                if node == "final":
                    final_event = ev
    return seen_nodes, final_event


# ======================================================================= #
# request validation / not-found
# ======================================================================= #
def test_missing_question_is_422(client, aapl_filing):
    ticker, doc_id = aapl_filing
    r = client.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa", json={})
    assert r.status_code == 422 and r.json()["type"] == "validation_error"


def test_unknown_doc_id_is_404(client):
    r = client.post(f"{API}/companies/AAPL/filings/does-not-exist/qa", json={"question": "q"})
    assert r.status_code == 404 and r.json()["type"] == "not_found"


def test_unauthenticated_is_401(aapl_filing):
    ticker, doc_id = aapl_filing
    r = requests.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa", json={"question": "q"})
    assert r.status_code == 401


# ======================================================================= #
# create -> status lifecycle
# ======================================================================= #
def test_create_returns_queued_and_never_reused(client, aapl_filing):
    ticker, doc_id = aapl_filing
    r = client.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa",
                    json={"question": "What form is this filing and what period does it cover?"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body) == {"id", "status", "reused"}
    assert body["status"] == "queued" and body["reused"] is False


def test_full_lifecycle_reaches_a_completed_answer(client, aapl_filing):
    ticker, doc_id = aapl_filing
    r = client.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa",
                    json={"question": "What form is this filing and what period does it cover?"})
    assert r.status_code == 200, r.text
    job_id = r.json()["id"]

    body = _poll_until_terminal(client, ticker, doc_id, job_id)
    assert body["status"] == "completed", body

    a = body["answer"]
    assert set(a) == {
        "ticker", "doc_id", "question", "answer_text", "sources",
        "cited_source_indices", "state", "coverage_boundaries",
        "created_at", "prompt_version", "schema_version",
    }
    assert a["ticker"] == ticker and a["doc_id"] == doc_id
    assert a["state"] in ("answered", "insufficient_evidence")
    if a["state"] == "answered":
        assert a["sources"] and a["cited_source_indices"]
        for s in a["sources"]:
            assert set(s) == {"index", "doc_id", "chunk_start", "chunk_end"}
            assert s["doc_id"] == doc_id  # every locator resolves to the identified filing
    else:
        assert a["sources"] == [] and a["cited_source_indices"] == []


def test_stream_emits_a_final_frame_matching_the_get_result(client, aapl_filing):
    ticker, doc_id = aapl_filing
    r = client.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa",
                    json={"question": "Summarize one key point from this filing."})
    assert r.status_code == 200, r.text
    job_id = r.json()["id"]

    seen_nodes, final_event = _consume_stream(client, ticker, doc_id, job_id)
    assert "pipeline" in seen_nodes
    assert final_event is not None, f"no final frame seen; nodes observed: {seen_nodes}"
    assert final_event["status"] == "ok"
    assert final_event["answer"]["state"] in ("answered", "insufficient_evidence")


# ======================================================================= #
# cancellation / ownership
# ======================================================================= #
def test_cancel_is_idempotent_and_owner_scoped(client, other_client, aapl_filing):
    ticker, doc_id = aapl_filing
    r = client.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa",
                    json={"question": "Another independent question for cancellation."})
    job_id = r.json()["id"]

    r_other = other_client.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa/{job_id}/cancel")
    assert r_other.status_code == 404  # non-disclosure — not this owner's job

    r_cancel = client.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa/{job_id}/cancel")
    assert r_cancel.status_code == 200
    assert r_cancel.json()["id"] == job_id

    r_cancel_again = client.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa/{job_id}/cancel")
    assert r_cancel_again.status_code == 200  # idempotent on a terminal job


def test_get_by_non_owner_is_404(client, other_client, aapl_filing):
    ticker, doc_id = aapl_filing
    r = client.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa",
                    json={"question": "Owner-scoping check question."})
    job_id = r.json()["id"]
    r_other = other_client.get(f"{API}/companies/{ticker}/filings/{doc_id}/qa/{job_id}")
    assert r_other.status_code == 404
    client.post(f"{API}/companies/{ticker}/filings/{doc_id}/qa/{job_id}/cancel")


# ======================================================================= #
# regression — existing M14/M15 route families are unaffected
# ======================================================================= #
def test_existing_filing_analysis_route_still_reachable(client, aapl_filing):
    ticker, doc_id = aapl_filing
    r = client.post(f"{API}/companies/{ticker}/filings/{doc_id}/analysis", json={})
    assert r.status_code == 200, r.text
    job_id = r.json()["id"]
    client.post(f"{API}/companies/{ticker}/filings/{doc_id}/analysis/{job_id}/cancel")
