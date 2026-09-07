"""API / contract tests for the four M15 C-4 routes under
/api/companies/{ticker}/changes (Document 70 R4 §10-§15, frozen; Document 73
R1 §16). Hermetic: TestClient drives the real ASGI stack (real routes, real
FastAPI validation, real domain_error_handler -> HTTP status mapping) with
`server.db` and `server.container.financial_statements.get` swapped for fakes
-- same idiom as test_filing_analysis_endpoint.py / test_comparison_explanation_endpoint.py.

The completed-brief contract is exercised by driving `_run_change_brief`
directly (period mode: real deterministic engine; report mode:
`generate_change_brief_narrative` monkeypatched, no real LLM), since the
async job task cannot be awaited through the sync TestClient.

    python -m pytest backend/tests/unit/test_change_brief_endpoint.py -v
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from fastapi.testclient import TestClient  # noqa: E402

import server  # noqa: E402
from domain.financials import FinancialStatement, Metric, MetricUnit, PeriodType, StatementType  # noqa: E402
from domain.models import JobKind  # noqa: E402

USER = {"id": "cb-user", "email": "cb@example.com"}
OTHER = {"id": "cb-other", "email": "other@example.com"}
PATH = "/api/companies/{t}/changes"


# --- hermetic fake Mongo (reports: find + $in/$or + equality) ----------------
def _match(doc, filt):
    for k, v in filt.items():
        if k == "$or":
            if not any(_match(doc, sub) for sub in v):
                return False
            continue
        if isinstance(v, dict):
            if "$in" in v:
                if doc.get(k) not in v["$in"]:
                    return False
                continue
            raise NotImplementedError(v)
        if doc.get(k) != v:
            return False
    return True


class _FakeCursor:
    def __init__(self, docs):
        self._docs = docs

    async def to_list(self, n=None):
        return self._docs if n is None else self._docs[:n]


class _FakeCollection:
    def __init__(self, docs=None):
        self._docs = [dict(d) for d in (docs or [])]

    def find(self, filt, projection=None):
        return _FakeCursor([dict(d) for d in self._docs if _match(d, filt)])


class _FakeDB:
    def __init__(self, reports=None):
        self.reports = _FakeCollection(reports)


def _report(rid, *, ticker="AAPL", user_id=USER["id"], is_sample=False, **fields):
    return {
        "id": rid, "ticker": ticker, "user_id": user_id, "is_sample": is_sample,
        "company_name": "Apple Inc.",
        "extracted_data": {"guidance": f"guidance-{rid}"},
        "sentiment_analysis": {"sentiment": "Neutral"}, "scorecard": {"overall": 0.7},
        **fields,
    }


def _stmt(period_end, metrics, *, ticker="AAPL", currency="USD",
          statement_type=StatementType.INCOME, period_type=PeriodType.QUARTERLY):
    return FinancialStatement(
        ticker=ticker, period_type=period_type, period_end=period_end,
        fiscal_year=period_end[:4], statement_type=statement_type, currency=currency,
        fetched_at="2026-01-01T00:00:00Z",
        metrics=[Metric(provider_label=label, value=value, unit=unit) for label, value, unit in metrics],
    )


server.app.dependency_overrides[server.current_user] = lambda: USER
client = TestClient(server.app)


def _swap_db(fake):
    original = server.db
    server.db = fake
    return original


def _swap_financials(rows):
    repo = server.container.financial_statements
    orig = repo.get

    async def _get(ticker, period_type):
        return list(rows)

    repo.get = _get
    return orig


def _restore_financials(orig):
    server.container.financial_statements.get = orig


def _stub_runner():
    orig = server._run_change_brief

    async def _noop(*_a, **_k):
        return None

    server._run_change_brief = _noop
    return orig


def _restore_runner(orig):
    server._run_change_brief = orig


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
    server._CHANGE_BRIEF_RESULTS.pop(job_id, None)


# ======================================================================= #
# request validation / mode exclusivity  (Document 70 R4 §10.2 / §15)
# ======================================================================= #
def test_missing_comparison_type_is_422_validation_error():
    orig = _swap_db(_FakeDB())
    try:
        r = client.post(PATH.format(t="AAPL"), json={})
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig


def test_bare_post_no_body_is_422():
    orig = _swap_db(_FakeDB())
    try:
        r = client.post(PATH.format(t="AAPL"))
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig


def test_invalid_comparison_type_is_422():
    orig = _swap_db(_FakeDB())
    try:
        r = client.post(PATH.format(t="AAPL"), json={"comparison_type": "both"})
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig


def test_report_mode_missing_current_report_id_is_422():
    orig = _swap_db(_FakeDB())
    try:
        r = client.post(PATH.format(t="AAPL"),
                        json={"comparison_type": "report", "baseline_report_id": "r1"})
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig


def test_report_mode_with_period_field_is_422_wrong_mode_field():
    orig = _swap_db(_FakeDB())
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "report", "baseline_report_id": "r1",
            "current_report_id": "r2", "period_type": "annual",
        })
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig


def test_report_mode_self_comparison_is_422():
    orig = _swap_db(_FakeDB())
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "report", "baseline_report_id": "r1", "current_report_id": "r1",
        })
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig


def test_period_mode_reversed_period_order_is_422():
    orig = _swap_db(_FakeDB())
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "period", "period_type": "quarterly", "statement_type": "income",
            "baseline_period_end": "2024-09-30", "current_period_end": "2024-06-30",
        })
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig


def test_period_mode_equal_period_ends_is_422():
    orig = _swap_db(_FakeDB())
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "period", "period_type": "quarterly", "statement_type": "income",
            "baseline_period_end": "2024-06-30", "current_period_end": "2024-06-30",
        })
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig


def test_period_mode_malformed_date_is_422_not_404():
    """L-4: a malformed period_end must be rejected at validation (422), never
    passed to reference resolution where it would degrade to a 404 for a
    nonexistent row (Document 70 R4 §10.2 / §15). Financials are stubbed to a
    valid row so a leak-through would produce 404, not 422."""
    orig_db = _swap_db(_FakeDB())
    orig_fin = _swap_financials([_stmt("2024-06-30", [("Revenue", 1.0, MetricUnit.CURRENCY)])])
    try:
        for bad in ("not-a-date", "2024-13-01", "2024-06-31", "06/30/2024", "20240630", ""):
            r = client.post(PATH.format(t="AAPL"), json={
                "comparison_type": "period", "period_type": "quarterly", "statement_type": "income",
                "baseline_period_end": bad, "current_period_end": "2024-09-30",
            })
            assert r.status_code == 422 and r.json()["type"] == "validation_error", (bad, r.status_code)
        # a malformed *current* is caught too
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "period", "period_type": "quarterly", "statement_type": "income",
            "baseline_period_end": "2024-06-30", "current_period_end": "2024-99-99",
        })
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig_db
        _restore_financials(orig_fin)


def test_period_mode_valid_canonical_dates_still_pass_validation():
    """L-4 regression guard: well-formed YYYY-MM-DD annual/quarterly requests
    are unaffected — a valid-but-nonexistent period is still a 404, not a 422."""
    orig_db = _swap_db(_FakeDB())
    orig_fin = _swap_financials([_stmt("2023-12-31", [("Revenue", 1.0, MetricUnit.CURRENCY)],
                                       period_type=PeriodType.ANNUAL)])
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "period", "period_type": "annual", "statement_type": "income",
            "baseline_period_end": "2022-12-31", "current_period_end": "2023-12-31",  # 2022 row absent
        })
        assert r.status_code == 404 and r.json()["type"] == "not_found"  # validation passed; resolution 404'd
    finally:
        server.db = orig_db
        _restore_financials(orig_fin)


def test_empty_ticker_is_422():
    orig = _swap_db(_FakeDB())
    try:
        r = client.post("/api/companies/%20%20/changes", json={"comparison_type": "report",
                        "baseline_report_id": "r1", "current_report_id": "r2"})
        assert r.status_code == 422 and r.json()["type"] == "validation_error"
    finally:
        server.db = orig


def test_unauthenticated_is_rejected():
    del server.app.dependency_overrides[server.current_user]
    try:
        r = client.post(PATH.format(t="AAPL"), json={"comparison_type": "report",
                        "baseline_report_id": "r1", "current_report_id": "r2"})
        assert r.status_code == 401
    finally:
        server.app.dependency_overrides[server.current_user] = lambda: USER


# ======================================================================= #
# reference resolution -> 404 non-disclosure  (Document 70 R4 §9.4 / §15)
# ======================================================================= #
def test_report_mode_unknown_report_id_is_404():
    orig = _swap_db(_FakeDB(reports=[_report("r1")]))
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "report", "baseline_report_id": "r1", "current_report_id": "missing",
        })
        assert r.status_code == 404 and r.json()["type"] == "not_found"
    finally:
        server.db = orig


def test_report_mode_cross_ticker_report_is_404_non_disclosure():
    orig = _swap_db(_FakeDB(reports=[_report("r1", ticker="AAPL"), _report("r2", ticker="MSFT")]))
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "report", "baseline_report_id": "r1", "current_report_id": "r2",
        })
        assert r.status_code == 404
    finally:
        server.db = orig


def test_report_mode_foreign_owned_non_sample_report_is_404():
    orig = _swap_db(_FakeDB(reports=[
        _report("r1"), _report("r2", user_id=OTHER["id"], is_sample=False),
    ]))
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "report", "baseline_report_id": "r1", "current_report_id": "r2",
        })
        assert r.status_code == 404
    finally:
        server.db = orig


def test_report_mode_sample_report_is_visible_cross_tenant():
    orig_db = _swap_db(_FakeDB(reports=[
        _report("r1"), _report("r2", user_id=OTHER["id"], is_sample=True),
    ]))
    orig_run = _stub_runner()
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "report", "baseline_report_id": "r1", "current_report_id": "r2",
        })
        assert r.status_code == 200
        _kill(r.json()["id"])
    finally:
        server.db = orig_db
        _restore_runner(orig_run)


def test_period_mode_missing_statement_row_is_404():
    orig_db = _swap_db(_FakeDB())
    orig_fin = _swap_financials([_stmt("2024-06-30", [("Revenue", 1.0, MetricUnit.CURRENCY)])])
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "period", "period_type": "quarterly", "statement_type": "income",
            "baseline_period_end": "2024-06-30", "current_period_end": "2024-09-30",  # current absent
        })
        assert r.status_code == 404 and r.json()["type"] == "not_found"
    finally:
        server.db = orig_db
        _restore_financials(orig_fin)


# ======================================================================= #
# create response shape + BYOK gate  (Document 70 R4 §10.3 / §18)
# ======================================================================= #
def test_create_returns_queued_and_never_reused():
    orig_db = _swap_db(_FakeDB(reports=[_report("r1"), _report("r2")]))
    orig_run = _stub_runner()
    try:
        r = client.post(PATH.format(t="aapl"), json={
            "comparison_type": "report", "baseline_report_id": "r1", "current_report_id": "r2",
        })
        assert r.status_code == 200, r.text
        body = r.json()
        assert set(body) == {"id", "status", "reused"}
        assert body["status"] == "queued" and body["reused"] is False
        _kill(body["id"])
    finally:
        server.db = orig_db
        _restore_runner(orig_run)


def test_custom_provider_from_non_admin_is_403():
    orig_db = _swap_db(_FakeDB(reports=[_report("r1"), _report("r2")]))
    try:
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "report", "baseline_report_id": "r1",
            "current_report_id": "r2", "llm_provider": "custom",
        })
        assert r.status_code == 403
    finally:
        server.db = orig_db


def test_custom_base_url_private_address_is_ssrf_blocked():
    orig_db = _swap_db(_FakeDB(reports=[_report("r1"), _report("r2")]))
    try:
        # non-admin + base_url -> require_admin fires first (403); the SSRF
        # guard itself is covered by test_ssrf_guard.py at the unit level.
        r = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "report", "baseline_report_id": "r1",
            "current_report_id": "r2", "llm_base_url": "http://169.254.169.254/",
        })
        assert r.status_code in (400, 403)
    finally:
        server.db = orig_db


# ======================================================================= #
# GET / cancel — status + owner scoping  (Document 70 R4 §10.3 / §18)
# ======================================================================= #
def test_get_unknown_id_is_404():
    r = client.get(PATH.format(t="AAPL") + "/does-not-exist")
    assert r.status_code == 404


def test_get_queued_job_omits_changes_key():
    orig_db = _swap_db(_FakeDB(reports=[_report("r1"), _report("r2")]))
    orig_run = _stub_runner()
    try:
        jid = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "report", "baseline_report_id": "r1", "current_report_id": "r2",
        }).json()["id"]
        r = client.get(PATH.format(t="AAPL") + f"/{jid}")
        assert r.status_code == 200
        body = r.json()
        assert body == {"id": jid, "status": "queued"}
        assert "changes" not in body
        _kill(jid)
    finally:
        server.db = orig_db
        _restore_runner(orig_run)


def test_cancel_by_non_owner_is_404_and_by_owner_cancels():
    orig_db = _swap_db(_FakeDB(reports=[_report("r1"), _report("r2")]))
    orig_run = _stub_runner()
    try:
        jid = client.post(PATH.format(t="AAPL"), json={
            "comparison_type": "report", "baseline_report_id": "r1", "current_report_id": "r2",
        }).json()["id"]

        server.app.dependency_overrides[server.current_user] = lambda: OTHER
        r_other = client.post(PATH.format(t="AAPL") + f"/{jid}/cancel")
        server.app.dependency_overrides[server.current_user] = lambda: USER
        assert r_other.status_code == 404

        r = client.post(PATH.format(t="AAPL") + f"/{jid}/cancel")
        assert r.status_code == 200 and r.json() == {"id": jid, "status": "cancelled"}
        _kill(jid)
    finally:
        server.db = orig_db
        _restore_runner(orig_run)


def test_stream_by_non_owner_is_404_non_disclosure():
    """T-1: GET /api/companies/{ticker}/changes/{id}/stream exercises the
    route handler's owner guard (`job.user_id != user["id"]` -> 404) BEFORE
    any streaming response is constructed — a non-owner cannot even tell the
    job exists. Mirrors the cancel/get non-owner 404 pattern; the live-stream
    happy path stays a `live` test, as the filing-analysis suite does."""
    async def _seed():
        await server.container.job_lifecycle.start(
            "cb-stream-owned", JobKind.CHANGE_BRIEF, USER["id"], ticker="AAPL", deadline_s=60)

    asyncio.run(_seed())
    try:
        # unknown id -> 404
        r_unknown = client.get(PATH.format(t="AAPL") + "/no-such-job/stream")
        assert r_unknown.status_code == 404

        # existing job, non-owner -> 404 (non-disclosure), not 200/403
        server.app.dependency_overrides[server.current_user] = lambda: OTHER
        r_other = client.get(PATH.format(t="AAPL") + "/cb-stream-owned/stream")
        server.app.dependency_overrides[server.current_user] = lambda: USER
        assert r_other.status_code == 404
        assert "text/event-stream" not in r_other.headers.get("content-type", "")
    finally:
        _kill("cb-stream-owned")


def test_cancel_terminal_job_is_idempotent():
    async def _seed():
        await server.container.job_lifecycle.start(
            "cb-term", JobKind.CHANGE_BRIEF, USER["id"], ticker="AAPL", deadline_s=60)
        await server.container.job_lifecycle.complete("cb-term")

    asyncio.run(_seed())
    try:
        r = client.post(PATH.format(t="AAPL") + "/cb-term/cancel")
        assert r.status_code == 200 and r.json() == {"id": "cb-term", "status": "completed"}
    finally:
        _kill("cb-term")


# ======================================================================= #
# completed `period`-mode contract  (drive _run_change_brief directly)
# ======================================================================= #
def _run_period(jid, baseline, current):
    asyncio.run(server.container.job_lifecycle.start(
        jid, JobKind.CHANGE_BRIEF, USER["id"], ticker="AAPL", deadline_s=60))
    asyncio.run(server._run_change_brief(jid, "AAPL", USER["id"], "period", baseline, current))


def test_period_completed_payload_conforms_to_document_70():
    jid = "cb-period-1"
    _run_period(
        jid,
        _stmt("2024-06-30", [("Revenue", 100.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("Revenue", 118.0, MetricUnit.CURRENCY)]),
    )
    try:
        r = client.get(PATH.format(t="AAPL") + f"/{jid}")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == jid and body["status"] == "completed"
        ch = body["changes"]
        assert set(ch) == {"ticker", "comparison_type", "baseline", "current", "created_at",
                           "prompt_version", "schema_version", "items", "state", "coverage_boundaries"}
        assert ch["comparison_type"] == "period"
        assert ch["prompt_version"] is None       # period mode makes no LLM call
        assert ch["schema_version"] == "v1"
        (item,) = ch["items"]
        assert item["category"] == "financial" and item["change_kind"] == "changed"
        assert item["absolute_delta"] == 18.0
        # financial source shape only — never report_id / field
        for s in item["sources"]:
            assert set(s) == {"index", "statement_type", "period_end", "metric"}
        assert ch["state"] == "complete"

        # owner scoping on GET
        server.app.dependency_overrides[server.current_user] = lambda: OTHER
        r_other = client.get(PATH.format(t="AAPL") + f"/{jid}")
        server.app.dependency_overrides[server.current_user] = lambda: USER
        assert r_other.status_code == 404
    finally:
        _kill(jid)


def test_period_no_change_is_complete_with_empty_items():
    jid = "cb-period-nochange"
    _run_period(
        jid,
        _stmt("2024-06-30", [("Revenue", 100.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("Revenue", 100.0, MetricUnit.CURRENCY)]),
    )
    try:
        ch = client.get(PATH.format(t="AAPL") + f"/{jid}").json()["changes"]
        assert ch["items"] == [] and ch["state"] == "complete"
    finally:
        _kill(jid)


def test_period_currency_mismatch_is_insufficient_evidence_200():
    jid = "cb-period-cur"
    _run_period(
        jid,
        _stmt("2024-06-30", [("Revenue", 100.0, MetricUnit.CURRENCY)], currency="USD"),
        _stmt("2024-09-30", [("Revenue", 90.0, MetricUnit.CURRENCY)], currency="EUR"),
    )
    try:
        body = client.get(PATH.format(t="AAPL") + f"/{jid}").json()
        assert body["status"] == "completed"
        assert body["changes"]["state"] == "insufficient_evidence" and body["changes"]["items"] == []
    finally:
        _kill(jid)


def test_period_output_is_bit_identical_across_repeated_runs():
    args = (
        _stmt("2024-06-30", [("Revenue", 100.0, MetricUnit.CURRENCY),
                             ("EPS", 1.0, MetricUnit.CURRENCY_PER_SHARE)]),
        _stmt("2024-09-30", [("Revenue", 118.0, MetricUnit.CURRENCY),
                             ("EPS", 1.2, MetricUnit.CURRENCY_PER_SHARE)]),
    )
    _run_period("cb-det-a", *args)
    _run_period("cb-det-b", *args)
    try:
        a = client.get(PATH.format(t="AAPL") + "/cb-det-a").json()["changes"]
        b = client.get(PATH.format(t="AAPL") + "/cb-det-b").json()["changes"]
        a.pop("created_at"); b.pop("created_at")
        assert a == b
    finally:
        _kill("cb-det-a"); _kill("cb-det-b")


# ======================================================================= #
# completed `report`-mode contract  (monkeypatch generate_change_brief_narrative)
# ======================================================================= #
def _run_report(jid, fake_generate):
    orig = server.generate_change_brief_narrative
    server.generate_change_brief_narrative = fake_generate
    try:
        asyncio.run(server.container.job_lifecycle.start(
            jid, JobKind.CHANGE_BRIEF, USER["id"], ticker="AAPL", deadline_s=60))
        asyncio.run(server._run_change_brief(
            jid, "AAPL", USER["id"], "report", {"id": "rb"}, {"id": "rc"}))
    finally:
        server.generate_change_brief_narrative = orig


def test_report_completed_payload_conforms_to_document_70():
    async def _fake(baseline, current):
        return {
            "baseline": {"report_id": "rb", "ticker": "AAPL", "company_name": "Apple Inc."},
            "current": {"report_id": "rc", "ticker": "AAPL", "company_name": "Apple Inc."},
            "prompt_version": "v1",
            "items": [{
                "category": "narrative",
                "summary": "Guidance was revised downward.",
                "explanation": "Guidance moved from up [1] to down [2].",
                "sources": [{"index": 1, "report_id": "rb", "field": "extracted_data"},
                            {"index": 2, "report_id": "rc", "field": "extracted_data"}],
                "cited_source_indices": [1, 2],
            }],
            "state": "complete",
            "coverage_boundaries": [],
        }

    jid = "cb-report-1"
    _run_report(jid, _fake)
    try:
        ch = client.get(PATH.format(t="AAPL") + f"/{jid}").json()["changes"]
        assert ch["comparison_type"] == "report"
        assert ch["prompt_version"] == "v1" and ch["schema_version"] == "v1"
        (item,) = ch["items"]
        assert item["category"] == "narrative"
        for s in item["sources"]:
            assert set(s) == {"index", "report_id", "field"}  # narrative shape only
        assert ch["state"] == "complete"
    finally:
        _kill(jid)


def test_report_insufficient_evidence_maps_to_completed_200():
    async def _fake(baseline, current):
        return {
            "baseline": {"report_id": "rb"}, "current": {"report_id": "rc"},
            "prompt_version": "v1", "items": [], "state": "insufficient_evidence",
            "coverage_boundaries": [],
        }

    jid = "cb-report-insuff"
    _run_report(jid, _fake)
    try:
        body = client.get(PATH.format(t="AAPL") + f"/{jid}").json()
        assert body["status"] == "completed"
        assert body["changes"]["state"] == "insufficient_evidence"
    finally:
        _kill(jid)


def test_report_provider_failure_marks_job_failed_not_a_fabricated_result():
    async def _boom(baseline, current):
        from domain.errors import LLMProviderError
        raise LLMProviderError("provider exploded")

    jid = "cb-report-fail"
    _run_report(jid, _boom)
    try:
        body = client.get(PATH.format(t="AAPL") + f"/{jid}").json()
        assert body["status"] == "failed"
        assert "changes" not in body
    finally:
        _kill(jid)


# ======================================================================= #
# M14 regression — the filing-analysis route family is unaffected
# ======================================================================= #
def test_m14_filing_analysis_routes_still_present_and_distinct():
    paths = set(server.app.openapi()["paths"])
    assert "/api/companies/{ticker}/filings/{doc_id}/analysis" in paths
    assert "/api/companies/{ticker}/changes" in paths
    assert server._FILING_ANALYSIS_RESULTS is not server._CHANGE_BRIEF_RESULTS


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
