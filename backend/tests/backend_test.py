"""AlphaScribe backend end-to-end pytest suite."""
import json
import os
import time

import pytest
import requests

from conftest import login

# 06 §5.1 Ph0 / 05 T-1: needs a live server (+ Mongo, + for some suites a
# live LLM/network). Excluded from the hermetic CI job via `-m "not live"`.
pytestmark = pytest.mark.live

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "http://localhost:8001").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    login(s, "backendtest")
    return s


# ---------- Health & seed ----------
def test_health(client):
    r = client.get(f"{API}/health")
    assert r.status_code == 200
    j = r.json()
    assert j["ok"] is True
    assert j["llm_key_configured"] is True


def test_ingest_samples(client):
    r = client.post(f"{API}/ingest/samples")
    assert r.status_code == 200
    j = r.json()
    assert "ingested" in j
    assert j["total_samples"] >= 4


def test_tickers(client):
    r = client.get(f"{API}/tickers")
    assert r.status_code == 200
    tks = r.json()["tickers"]
    for t in ("AAPL", "MSFT", "NVDA"):
        assert t in tks, f"missing {t} in {tks}"


def test_filings(client):
    r = client.get(f"{API}/filings")
    assert r.status_code == 200
    filings = r.json()["filings"]
    assert len(filings) >= 3
    for f in filings:
        assert "ticker" in f and "source" in f and "num_chunks" in f


# ---------- Ingest text ----------
def test_ingest_text_empty_400(client):
    r = client.post(f"{API}/ingest/text", json={"ticker": "TEST", "source": "TEST_src", "text": "  "})
    assert r.status_code == 400


def test_ingest_text_ok(client):
    payload = {"ticker": "TEST_TICK", "source": "TEST_source_1",
               "text": "Revenue was $10M in Q3 2024. Operating income grew 15%. Gross margin was 45%."}
    r = client.post(f"{API}/ingest/text", json=payload)
    assert r.status_code == 200
    j = r.json()
    assert j.get("ticker") == "TEST_TICK"
    assert j.get("num_chunks", 0) >= 1


# ---------- Ingest PDF (T-7, M7) ----------
# A hand-built minimal single-page PDF with a malformed xref (pypdf falls
# back to its own regex-based object-scan recovery, same as for a real-world
# PDF with a corrupt xref table) but a real, extractable text layer.
_PDF_WITH_TEXT = b"""%PDF-1.1
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R/MediaBox[0 0 300 144]>>endobj
4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj
5 0 obj<</Length 55>>stream
BT /F1 18 Tf 10 100 Td (Hello AlphaScribe Test PDF) Tj ET
endstream
endobj
trailer<</Size 6/Root 1 0 R>>
startxref
0
%%EOF"""


def test_ingest_pdf_ok(client):
    """Real endpoint behavior end-to-end: multipart upload -> pypdf
    extraction -> chunk+ingest into Mongo. Error paths (bad extension, empty
    file, unreadable/scanned PDF) are covered hermetically in
    tests/unit/test_ingest_pdf_route.py — this is the one live success case
    that needs a real DB."""
    r = client.post(
        f"{API}/ingest/pdf",
        files={"file": ("annual_report.pdf", _PDF_WITH_TEXT, "application/pdf")},
        data={"ticker": "TEST_PDF_TICK", "source": "Annual Report"},
        # The session's default Content-Type is application/json (see the
        # `client` fixture above); clearing it per-request lets `requests`
        # generate the real multipart/form-data boundary header instead.
        headers={"Content-Type": None},
    )
    assert r.status_code == 200, r.text
    j = r.json()
    assert j.get("ticker") == "TEST_PDF_TICK"
    assert j.get("num_chunks", 0) >= 1
    assert j.get("extracted_chars", 0) > 0
    assert "Hello AlphaScribe Test PDF" in j.get("text_preview", "")


# ---------- Reports ----------
def test_generate_no_data_400(client):
    r = client.post(f"{API}/reports/generate", json={"ticker": "ZZZZ_NONE", "query": "hi"})
    assert r.status_code == 400


@pytest.fixture(scope="module")
def job_id(client):
    r = client.post(f"{API}/reports/generate",
                    json={"ticker": "AAPL", "query": "Summarize the latest quarter"})
    assert r.status_code == 200, r.text
    jid = r.json()["job_id"]
    assert jid
    return jid


def test_sse_stream(client, job_id):
    """Consume SSE stream and verify pipeline node events."""
    seen_nodes = set()
    got_final = False
    with client.get(f"{API}/reports/{job_id}/stream", stream=True, timeout=180) as r:
        assert r.status_code == 200
        start = time.time()
        for raw in r.iter_lines(decode_unicode=True):
            if time.time() - start > 180:
                break
            if not raw:
                continue
            if raw.startswith("event: end"):
                break
            if raw.startswith("data:"):
                payload = raw[5:].strip()
                if not payload or payload == "{}":
                    continue
                try:
                    ev = json.loads(payload)
                except Exception:
                    continue
                node = ev.get("node")
                if node:
                    seen_nodes.add(node)
                if node == "final":
                    got_final = True
                if ev.get("node") == "pipeline" and ev.get("status") in ("ok", "error"):
                    # let stream close naturally
                    pass
    # required nodes
    for n in ("pipeline", "retriever", "extractor", "tone", "synthesizer", "fact_checker"):
        assert n in seen_nodes, f"missing node event: {n}. Seen: {seen_nodes}"
    assert got_final, f"no final event; seen={seen_nodes}"


def _wait_for_job_completion(client, job_id, timeout=1800):
    """Polls GET /reports/{id} — a plain request, not a stream, so there's no
    per-read timeout to fight — until the job reaches `completed`. Mirrors
    the existing `_generate_and_wait` convention in test_reports_scoping.py
    (which bounds at 300s under a normal-latency LLM provider). T-11/T-14
    below assume `job_id` has already finished by the time they run; that's
    normally true because test_sse_stream above already drained the stream
    to completion, but on a slow local-LLM fallback (see backend/.env) that
    drain can itself time out mid-pipeline while the job keeps running
    server-side regardless. Waiting here — bounded generously rather than
    assumed — is what makes T-11/T-14 an honest live check instead of a
    flaky one in that environment, without touching test_sse_stream itself
    or skipping any assertion."""
    start = time.time()
    while time.time() - start < timeout:
        r = client.get(f"{API}/reports/{job_id}")
        status = r.json().get("status")
        if status == "completed":
            return
        assert status not in ("failed", "cancelled"), f"job {job_id} ended as {status}: {r.text}"
        time.sleep(5)
    raise TimeoutError(f"job {job_id} did not reach 'completed' within {timeout}s (last status={status!r})")


def _consume_report_stream(client, job_id, timeout=20):
    """Returns the ordered list of decoded `data:` events (not a set) plus
    elapsed wall-clock time — used by both the T-11 and T-14 checks below."""
    events = []
    start = time.time()
    with client.get(f"{API}/reports/{job_id}/stream", stream=True, timeout=timeout) as r:
        assert r.status_code == 200
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
                events.append(json.loads(payload))
    return events, time.time() - start


def test_reconnect_to_a_finished_job_replays_history_promptly(client, job_id):
    """T-11: streaming a job that already completed (job_id is completed by
    this point — test_sse_stream/test_get_report already ran) must replay the
    stored history and terminate, not hang waiting for events that will never
    come since the pipeline is already done."""
    _wait_for_job_completion(client, job_id)
    events, elapsed = _consume_report_stream(client, job_id)
    assert elapsed < 15, f"reconnect to an already-finished job took {elapsed:.1f}s — looks hung"
    assert events, "reconnecting to a finished job replayed no history at all"
    assert events[0].get("node") == "pipeline" and events[0].get("status") == "start"
    assert any(e.get("node") == "final" for e in events), (
        f"finished-job reconnect must still deliver the final report snapshot; seen={events}"
    )


def test_reconnect_replay_has_the_graphs_required_event_order(client, job_id):
    """T-14: the existing live SSE test only ever checked the *set* of node
    events (test_sse_stream above). This asserts the actual sequence agents/
    graph.py wires: START -> retriever -> (extractor || tone) -> synthesizer
    -> fact_checker -> pipeline/ok -> final. extractor/tone run in parallel
    (both edges come out of retriever, both feed synthesizer) so their
    relative order to each other isn't fixed — only their position relative
    to retriever/synthesizer is. `.index()` (first occurrence) keeps this
    correct even if fact_checker's conditional router retried synthesizer."""
    _wait_for_job_completion(client, job_id)
    events, _ = _consume_report_stream(client, job_id)
    nodes = [e["node"] for e in events]
    for required in ("pipeline", "retriever", "extractor", "tone", "synthesizer", "fact_checker", "final"):
        assert required in nodes, f"missing node event: {required}. seen={nodes}"

    assert nodes[0] == "pipeline" and events[0]["status"] == "start"
    assert nodes.index("retriever") < nodes.index("extractor")
    assert nodes.index("retriever") < nodes.index("tone")
    assert nodes.index("extractor") < nodes.index("synthesizer")
    assert nodes.index("tone") < nodes.index("synthesizer")
    assert nodes.index("synthesizer") < nodes.index("fact_checker")

    pipeline_events = [e for e in events if e["node"] == "pipeline"]
    assert pipeline_events[0]["status"] == "start"
    assert pipeline_events[-1]["status"] in ("ok", "error")  # terminal pipeline event is always last
    assert nodes.index("final") == len(nodes) - 1  # `final` is injected right after the terminal pipeline/ok


def test_cancel_mid_stream_emits_the_pipeline_warn_event(client):
    """T-13: must inspect the actual SSE event stream, not just GET /status
    after the fact. Starts a fresh job (job_id above must stay completed for
    the tests around it), cancels once the stream proves the pipeline is
    genuinely in flight (a `retriever` event observed), then asserts the
    cancellation's own `pipeline`/`warn` event (application/jobs.py's
    JobLifecycle.cancel — "Analysis cancelled by user") actually arrives on
    the stream the client is reading, not merely that GET /status flips."""
    r = client.post(f"{API}/reports/generate",
                     json={"ticker": "AAPL", "query": "Summarize competitive risks"})
    assert r.status_code == 200, r.text
    cancel_job_id = r.json()["job_id"]

    saw_warn_event = False
    cancelled = False
    events = []
    with client.get(f"{API}/reports/{cancel_job_id}/stream", stream=True, timeout=60) as r:
        assert r.status_code == 200
        start = time.time()
        for raw in r.iter_lines(decode_unicode=True):
            if time.time() - start > 60:
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
                events.append(ev)
                if not cancelled and ev.get("node") == "retriever":
                    cr = client.post(f"{API}/reports/{cancel_job_id}/cancel")
                    assert cr.status_code == 200, cr.text
                    assert cr.json()["status"] == "cancelled"
                    cancelled = True
                if ev.get("node") == "pipeline" and ev.get("status") == "warn":
                    saw_warn_event = True

    assert cancelled, f"stream ended before a retriever event arrived to cancel against; seen={events}"
    assert saw_warn_event, f"no pipeline/warn cancellation event observed in the SSE stream; seen={events}"


def test_get_report(client, job_id):
    r = client.get(f"{API}/reports/{job_id}")
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "completed"
    rep = j["report"]
    assert rep["draft_report"] and len(rep["draft_report"]) > 50
    assert isinstance(rep["extracted_data"], dict)
    sa = rep["sentiment_analysis"]
    assert isinstance(sa, dict)
    for k in ("sentiment", "confidence", "key_risks", "key_positives"):
        assert k in sa, f"missing sentiment key: {k}"
    assert isinstance(rep["source_documents"], list) and len(rep["source_documents"]) > 0
    assert "score" in rep["source_documents"][0]
    assert isinstance(rep["fact_check_status"], bool)
    assert isinstance(rep["verified_claims"], list)
    assert isinstance(rep["retry_count"], int)


def test_list_reports_contains_job(client, job_id):
    r = client.get(f"{API}/reports")
    assert r.status_code == 200
    ids = [x["id"] for x in r.json()["reports"]]
    assert job_id in ids
