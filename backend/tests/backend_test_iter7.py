"""Iteration 7: Learning backend (03_Learning_Backend_Design.md) — Backend
Engineering M2 Phase L. Full explain -> stream -> status -> cancel lifecycle
against a running server + real Mongo, plus the response-shape/ownership
properties the design doc calls out as the most likely implementation
mistakes (F-1: "id", not "job_id"; EQ-3: owner-scoped reads).
"""
import json
import os
import time

import pytest
import requests

from conftest import login

# 06 §5.1 Ph0 / 05 T-1: needs a live server (+ Mongo, + LLM/network for the
# happy-path tests). Excluded from the hermetic CI job via `-m "not live"`.
pytestmark = pytest.mark.live

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    login(s, "iter7learning")
    return s


@pytest.fixture(scope="module")
def other_client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    login(s, "iter7learning-other")
    return s


@pytest.fixture(scope="module")
def ensure_aapl_filings(client):
    client.post(f"{API}/ingest/samples")


def _consume_stream(client, explanation_id, timeout=180):
    """Returns (seen_nodes, final_event or None)."""
    seen_nodes = set()
    final_event = None
    with client.get(f"{API}/learning/{explanation_id}/stream", stream=True, timeout=timeout) as r:
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


def test_explain_400_when_ticker_has_no_filings(client):
    r = client.post(f"{API}/learning/explain",
                     json={"ticker": "ZZZZ99", "concept": "operating leverage"})
    assert r.status_code == 400


def test_explain_requires_ticker_and_concept(client):
    r = client.post(f"{API}/learning/explain", json={"ticker": "", "concept": ""})
    assert r.status_code in (400, 422)


def test_explain_returns_id_not_job_id(client, ensure_aapl_filings):
    """02 F-1: the single most likely implementation mistake — the response
    key is "id", never "job_id" (unlike POST /reports/generate)."""
    r = client.post(f"{API}/learning/explain",
                     json={"ticker": "AAPL", "concept": "free cash flow"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert set(body.keys()) == {"id"}
    assert body["id"]


@pytest.fixture(scope="module")
def explanation_id(client, ensure_aapl_filings):
    r = client.post(f"{API}/learning/explain",
                     json={"ticker": "AAPL", "concept": "operating margin"})
    assert r.status_code == 200, r.text
    return r.json()["id"]


def test_stream_emits_retriever_and_explainer_and_final(client, explanation_id):
    """The node vocabulary is fixed by the UI (03 §1.2's table) — anything
    outside {pipeline, retriever, explainer, final} leaves the frontend
    stuck. No extractor/tone/fact_checker (03 §3.1 — those don't exist in
    this graph)."""
    seen_nodes, final_event = _consume_stream(client, explanation_id)
    for n in ("pipeline", "retriever"):
        assert n in seen_nodes, f"missing node event: {n}. Seen: {seen_nodes}"
    assert seen_nodes <= {"pipeline", "retriever", "explainer", "final"}, seen_nodes


def test_get_explanation_after_stream_completes(client, explanation_id):
    r = client.get(f"{API}/learning/{explanation_id}")
    assert r.status_code == 200
    j = r.json()
    assert j["id"] == explanation_id
    assert j["status"] in ("completed", "failed")
    if j["status"] == "completed":
        doc = j["explanation"]
        assert doc["id"] == explanation_id
        assert doc["ticker"] == "AAPL"
        assert doc["concept"] == "operating margin"
        assert isinstance(doc["source_documents"], list) and len(doc["source_documents"]) > 0
        assert "[" in doc["explanation"]  # at least one citation marker survived


def test_cancel_after_completion_is_idempotent_and_shape_matches_contract(client, explanation_id):
    """02 F-1 again: cancel's response is {"id","status"} — no "note" field
    (unlike POST /reports/{id}/cancel)."""
    r = client.post(f"{API}/learning/{explanation_id}/cancel")
    assert r.status_code == 200
    body = r.json()
    assert set(body.keys()) == {"id", "status"}
    assert body["id"] == explanation_id


def test_cancel_unknown_id_is_tolerated_not_a_500(client):
    r = client.post(f"{API}/learning/00000000-0000-0000-0000-000000000000/cancel")
    assert r.status_code == 404  # tolerated by the client (fire-and-forget, unread), not a crash


def test_cancel_stops_an_in_flight_job(client, ensure_aapl_filings):
    r = client.post(f"{API}/learning/explain",
                     json={"ticker": "AAPL", "concept": "deferred revenue recognition"})
    assert r.status_code == 200
    job_id = r.json()["id"]

    r = client.post(f"{API}/learning/{job_id}/cancel")
    assert r.status_code == 200
    assert r.json() == {"id": job_id, "status": "cancelled"}

    # A second cancel is idempotent — same shape, no error.
    r2 = client.post(f"{API}/learning/{job_id}/cancel")
    assert r2.status_code == 200
    assert r2.json()["status"] == "cancelled"

    deadline = time.time() + 15
    status = None
    while time.time() < deadline:
        r3 = client.get(f"{API}/learning/{job_id}")
        status = r3.json().get("status")
        if status == "cancelled":
            break
        time.sleep(1)
    assert status == "cancelled"


def test_learning_reads_are_scoped_to_the_owner(client, other_client, explanation_id):
    """EQ-3 (03 §7.3, §10): unlike GET /reports/{id}, Learning reads 404 for
    a caller who isn't the job's owner."""
    r = other_client.get(f"{API}/learning/{explanation_id}")
    assert r.status_code == 404

    r = other_client.get(f"{API}/learning/{explanation_id}/stream")
    assert r.status_code == 404

    r = other_client.post(f"{API}/learning/{explanation_id}/cancel")
    assert r.status_code == 404
