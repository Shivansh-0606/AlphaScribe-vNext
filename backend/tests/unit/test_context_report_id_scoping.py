"""Regression test for the cross-tenant `context_report_id` disclosure fix
(Learning hardening-pass brief §8, SECURITY): `POST /reports/generate`'s
follow-up path and `POST /learning/explain` both looked up
`context_report_id` with no owner predicate, so any authenticated user could
supply another tenant's report id and have that report's `draft_report`/
`extracted_data` injected into their own job.

Hermetic: `TestClient` drives the real ASGI stack (real routes, real FastAPI
validation) with `server.db` swapped for a fake and the async pipeline
runners (`_run_pipeline`/`_run_explanation`) replaced with a synchronous
function that captures the `prior_brief`/`prior_financials` they were called
with, before returning an already-built no-op coroutine for
`asyncio.create_task` to schedule -- same "fake db + swapped route
dependency" idiom as test_change_brief_endpoint.py. The capture must happen
synchronously at the call site (not inside the coroutine body), since a
TestClient request doesn't guarantee a newly scheduled task gets a chance to
run before the response returns.

    python -m pytest backend/tests/unit/test_context_report_id_scoping.py -v
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from fastapi.testclient import TestClient  # noqa: E402

import server  # noqa: E402

OWNER = {"id": "ctx-owner", "email": "owner@example.com"}
OTHER = {"id": "ctx-other", "email": "other@example.com"}
FOREIGN_BRIEF = "OWNER-ONLY BRIEF CONTENT -- must never reach another tenant's prompt"


def _match(doc, filt):
    for k, v in filt.items():
        if k == "$or":
            if not any(_match(doc, sub) for sub in v):
                return False
            continue
        if doc.get(k) != v:
            return False
    return True


class _FakeReports:
    def __init__(self, docs):
        self._docs = docs

    async def find_one(self, filt, projection=None):
        for d in self._docs:
            if _match(d, filt):
                return dict(d)
        return None


class _FakeCountCollection:
    async def count_documents(self, _filt):
        return 1  # pretend the ticker always has ingested filings


class _FakeCompanies:
    async def find_one(self, _filt, _projection=None):
        return None


class _FakeInsertOnly:
    async def insert_one(self, _doc):
        return None


class _FakeDB:
    def __init__(self, reports):
        self.reports = _FakeReports(reports)
        self.filing_chunks = _FakeCountCollection()
        self.companies = _FakeCompanies()
        self.jobs = _FakeInsertOnly()
        self.explanation_jobs = _FakeInsertOnly()


def _report(rid, *, user_id, is_sample=False, draft_report=FOREIGN_BRIEF):
    return {
        "id": rid, "user_id": user_id, "is_sample": is_sample,
        "draft_report": draft_report,
        "extracted_data": {"revenue": "$1B"},
        "query": "prior question",
    }


client = TestClient(server.app)


def _swap_db(fake):
    original = server.db
    server.db = fake
    return original


def _swap_user(user):
    # Deliberately per-test, not a module-level override: other hermetic
    # test files (e.g. test_change_brief_endpoint.py) also set
    # server.app.dependency_overrides[server.current_user] at their own
    # module scope with no teardown, and whichever file's import runs last
    # during pytest's collection wins for the rest of the worker process.
    # These tests assert on exact user["id"] identity against fake report
    # ownership, so they must pin (and restore) their own override around
    # each call rather than assume a module-level one survives untouched.
    original = server.app.dependency_overrides.get(server.current_user)
    server.app.dependency_overrides[server.current_user] = lambda: user
    return original


def _restore_user(original):
    if original is None:
        server.app.dependency_overrides.pop(server.current_user, None)
    else:
        server.app.dependency_overrides[server.current_user] = original


def _capture_runner(attr):
    captured = {}

    async def _noop():
        return None

    def _capture(*_args, **kwargs):
        captured["prior_brief"] = kwargs.get("prior_brief")
        captured["prior_financials"] = kwargs.get("prior_financials")
        return _noop()

    original = getattr(server, attr)
    setattr(server, attr, _capture)
    return original, captured


def _restore(attr, original):
    setattr(server, attr, original)


def _kill(job_id):
    """Cancel the task AND release the shared job-lifecycle budget slot
    (research + Learning share one MAX_ACTIVE_JOBS pool) -- otherwise these
    tests would silently exhaust it for whatever else shares this worker
    process."""
    t = server.RUNNING_TASKS.pop(job_id, None)
    if t is not None:
        t.cancel()
    asyncio.run(server.container.job_lifecycle.cancel(job_id))


# --------------------------------------------------------------------------- #
# POST /reports/generate follow-up path
# --------------------------------------------------------------------------- #
def test_reports_generate_ignores_a_cross_tenant_context_report_id():
    orig_user = _swap_user(OWNER)
    orig_db = _swap_db(_FakeDB(reports=[_report("foreign", user_id=OTHER["id"])]))
    orig_runner, captured = _capture_runner("_run_pipeline")
    try:
        r = client.post("/api/reports/generate", json={
            "ticker": "AAPL", "query": "Summarize the latest quarter",
            "context_report_id": "foreign",
        })
        assert r.status_code == 200, r.text
        _kill(r.json()["job_id"])
        assert captured["prior_brief"] == ""  # falls through like a nonexistent id
    finally:
        server.db = orig_db
        _restore("_run_pipeline", orig_runner)
        _restore_user(orig_user)


def test_reports_generate_still_works_for_the_callers_own_report():
    orig_user = _swap_user(OWNER)
    orig_db = _swap_db(_FakeDB(reports=[_report("mine", user_id=OWNER["id"])]))
    orig_runner, captured = _capture_runner("_run_pipeline")
    try:
        r = client.post("/api/reports/generate", json={
            "ticker": "AAPL", "query": "Summarize the latest quarter",
            "context_report_id": "mine",
        })
        assert r.status_code == 200, r.text
        _kill(r.json()["job_id"])
        assert captured["prior_brief"] == FOREIGN_BRIEF  # the caller's own content, not blocked
    finally:
        server.db = orig_db
        _restore("_run_pipeline", orig_runner)
        _restore_user(orig_user)


def test_reports_generate_still_works_for_a_public_sample_report():
    orig_user = _swap_user(OWNER)
    orig_db = _swap_db(_FakeDB(reports=[_report("sample", user_id=None, is_sample=True)]))
    orig_runner, captured = _capture_runner("_run_pipeline")
    try:
        r = client.post("/api/reports/generate", json={
            "ticker": "AAPL", "query": "Summarize the latest quarter",
            "context_report_id": "sample",
        })
        assert r.status_code == 200, r.text
        _kill(r.json()["job_id"])
        assert captured["prior_brief"] == FOREIGN_BRIEF
    finally:
        server.db = orig_db
        _restore("_run_pipeline", orig_runner)
        _restore_user(orig_user)


# --------------------------------------------------------------------------- #
# POST /learning/explain
# --------------------------------------------------------------------------- #
def test_learning_explain_ignores_a_cross_tenant_context_report_id():
    orig_user = _swap_user(OWNER)
    orig_db = _swap_db(_FakeDB(reports=[_report("foreign", user_id=OTHER["id"])]))
    orig_runner, captured = _capture_runner("_run_explanation")
    try:
        r = client.post("/api/learning/explain", json={
            "ticker": "AAPL", "concept": "operating margin",
            "context_report_id": "foreign",
        })
        assert r.status_code == 200, r.text
        _kill(r.json()["id"])
        assert captured["prior_brief"] == "" and captured["prior_financials"] == {}
    finally:
        server.db = orig_db
        _restore("_run_explanation", orig_runner)
        _restore_user(orig_user)


def test_learning_explain_still_works_for_the_callers_own_report():
    orig_user = _swap_user(OWNER)
    orig_db = _swap_db(_FakeDB(reports=[_report("mine", user_id=OWNER["id"])]))
    orig_runner, captured = _capture_runner("_run_explanation")
    try:
        r = client.post("/api/learning/explain", json={
            "ticker": "AAPL", "concept": "operating margin",
            "context_report_id": "mine",
        })
        assert r.status_code == 200, r.text
        _kill(r.json()["id"])
        assert captured["prior_brief"] == FOREIGN_BRIEF
        assert captured["prior_financials"] == {"revenue": "$1B"}
    finally:
        server.db = orig_db
        _restore("_run_explanation", orig_runner)
        _restore_user(orig_user)


if __name__ == "__main__":
    test_reports_generate_ignores_a_cross_tenant_context_report_id()
    test_reports_generate_still_works_for_the_callers_own_report()
    test_reports_generate_still_works_for_a_public_sample_report()
    test_learning_explain_ignores_a_cross_tenant_context_report_id()
    test_learning_explain_still_works_for_the_callers_own_report()
    print("ok: context_report_id lookups are owner-or-sample scoped on both "
          "POST /reports/generate and POST /learning/explain")
