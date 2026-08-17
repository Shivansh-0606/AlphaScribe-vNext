"""API/contract tests for POST/GET/cancel /reports/compare/explain (M9.1,
Document 43 §5-§13, frozen). Hermetic: TestClient drives the real ASGI stack
(real routes, real FastAPI validation, real domain_error_handler) with
`server.db` swapped to a fake motor-shaped DB — same technique
test_financials_acquire_endpoint.py already uses for a login-walled route.

    python -m pytest backend/tests/unit/test_comparison_explanation_endpoint.py -v
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from fastapi.testclient import TestClient  # noqa: E402
from pymongo.errors import DuplicateKeyError  # noqa: E402

import server  # noqa: E402

USER = {"id": "compare-explain-user", "email": "explain@example.com"}
OTHER_USER = {"id": "someone-else", "email": "other@example.com"}


# --- hermetic fake Mongo (same idiom as test_financials_acquire_endpoint.py,
# extended with insert_one/find + $in/$or/$set/$push support for this
# capability's own query shapes) ----------------------------------------------

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

    async def to_list(self, n):
        return self._docs[:n]


class _FakeCollection:
    def __init__(self, unique_keys=(), sparse_unique_keys=()):
        self._docs: list[dict] = []
        self._unique_keys = unique_keys
        self._sparse_unique_keys = sparse_unique_keys

    def find(self, filt, projection=None):
        return _FakeCursor([dict(d) for d in self._docs if _match(d, filt)])

    async def find_one(self, filt, projection=None):
        for d in self._docs:
            if _match(d, filt):
                return dict(d)
        return None

    async def insert_one(self, doc):
        for key in self._unique_keys:
            if any(d.get(key) == doc.get(key) for d in self._docs):
                raise DuplicateKeyError(f"E11000 duplicate key error collection: {key}")
        for key in self._sparse_unique_keys:
            if doc.get(key) is not None and any(d.get(key) == doc.get(key) for d in self._docs):
                raise DuplicateKeyError(f"E11000 duplicate key error collection: {key}")
        self._docs.append(dict(doc))

    async def update_one(self, filt, update, upsert=False):
        for d in self._docs:
            if _match(d, filt):
                if "$set" in update:
                    d.update(update["$set"])
                if "$push" in update:
                    for k, v in update["$push"].items():
                        d.setdefault(k, []).append(v)
                return
        if upsert:
            new_doc = {k: v for k, v in filt.items() if not isinstance(v, dict) and k != "$or"}
            new_doc.update(update.get("$set", {}))
            self._docs.append(new_doc)


class _FakeDB:
    def __init__(self):
        self.reports = _FakeCollection()
        self.comparison_explanation_jobs = _FakeCollection(sparse_unique_keys=("active_identity_key",))
        self.comparison_explanations = _FakeCollection(unique_keys=("identity_key",))


def _report(rid, *, user_id=USER["id"], is_sample=False, **fields):
    return {
        "id": rid, "ticker": rid.upper(), "user_id": user_id, "is_sample": is_sample,
        "extracted_data": {"revenue": "$1B"}, "sentiment_analysis": {}, "scorecard": {},
        **fields,
    }


server.app.dependency_overrides[server.current_user] = lambda: USER
client = TestClient(server.app)


def _swap_db(fake_db):
    original = server.db
    server.db = fake_db
    return original


def _stub_llm_never_called():
    """Some tests exercise a genuinely-new job creation, which schedules a
    real `asyncio.create_task(_run_comparison_explanation(...))` — TestClient
    keeps a persistent event-loop portal across calls, so that task can
    actually run in the background. Stubbing `_generate_sync` (same technique
    as test_llm_retry.py) guarantees no real network call happens even if it
    does, regardless of scheduling timing — the DB swap alone is not enough.
    Raises NonRetryableLLMError specifically so chat_text's retry loop fails
    fast with no real backoff sleep (test_llm_retry.py's own documented
    behavior), rather than a generic exception that would retry 4x."""
    import agents.llm as llm

    original = llm._generate_sync

    def _boom(*a, **k):
        raise llm.NonRetryableLLMError("real provider must never be called in a unit test")

    llm._generate_sync = _boom
    return original


def _restore_llm(original):
    import agents.llm as llm
    llm._generate_sync = original


def _cancel_scheduled_task(job_id):
    task = server.RUNNING_TASKS.pop(job_id, None)
    if task is not None:
        task.cancel()


# --- request validation ------------------------------------------------------

def test_report_ids_below_minimum_is_422():
    fake = _FakeDB()
    original = _swap_db(fake)
    try:
        r = client.post("/api/reports/compare/explain", json={"report_ids": ["only-one"]})
        assert r.status_code == 422
    finally:
        server.db = original


def test_report_ids_above_maximum_is_422():
    fake = _FakeDB()
    original = _swap_db(fake)
    try:
        r = client.post("/api/reports/compare/explain", json={"report_ids": ["a", "b", "c", "d", "e"]})
        assert r.status_code == 422
    finally:
        server.db = original


def test_missing_report_ids_field_is_422():
    fake = _FakeDB()
    original = _swap_db(fake)
    try:
        r = client.post("/api/reports/compare/explain", json={})
        assert r.status_code == 422
    finally:
        server.db = original


def test_unauthenticated_request_is_rejected():
    del server.app.dependency_overrides[server.current_user]
    try:
        r = client.post("/api/reports/compare/explain", json={"report_ids": ["a", "b"]})
        assert r.status_code in (401, 403)
    finally:
        server.app.dependency_overrides[server.current_user] = lambda: USER


def test_fewer_than_two_authorized_reports_is_404():
    fake = _FakeDB()
    asyncio.run(fake.reports.insert_one(_report("r1")))  # only 1 of 2 requested exists
    original = _swap_db(fake)
    try:
        r = client.post("/api/reports/compare/explain", json={"report_ids": ["r1", "r-does-not-exist"]})
        assert r.status_code == 404
        assert "fewer than 2" in r.json()["detail"]
    finally:
        server.db = original


def test_cross_tenant_report_is_excluded_not_leaked():
    """A report owned by someone else, not a sample, must not count toward
    authorization — mirrors compare_reports's own EQ-3 posture exactly."""
    fake = _FakeDB()
    asyncio.run(fake.reports.insert_one(_report("r1")))
    asyncio.run(fake.reports.insert_one(_report("r2", user_id=OTHER_USER["id"], is_sample=False)))
    original = _swap_db(fake)
    try:
        r = client.post("/api/reports/compare/explain", json={"report_ids": ["r1", "r2"]})
        assert r.status_code == 404
    finally:
        server.db = original


def test_sample_report_is_visible_cross_tenant():
    fake = _FakeDB()
    asyncio.run(fake.reports.insert_one(_report("r1")))
    asyncio.run(fake.reports.insert_one(_report("r2", user_id=OTHER_USER["id"], is_sample=True)))
    original_db = _swap_db(fake)
    original_llm = _stub_llm_never_called()
    try:
        r = client.post("/api/reports/compare/explain", json={"report_ids": ["r1", "r2"]})
        assert r.status_code == 200
    finally:
        _cancel_scheduled_task(r.json().get("id"))
        server.db = original_db
        _restore_llm(original_llm)


# --- response shape -----------------------------------------------------------

def test_post_response_shape_is_exact():
    fake = _FakeDB()
    asyncio.run(fake.reports.insert_one(_report("r1")))
    asyncio.run(fake.reports.insert_one(_report("r2")))
    original_db = _swap_db(fake)
    original_llm = _stub_llm_never_called()
    try:
        r = client.post("/api/reports/compare/explain", json={"report_ids": ["r1", "r2"]})
        assert r.status_code == 200
        body = r.json()
        assert set(body.keys()) == {"id", "status", "reused"}
        assert isinstance(body["id"], str) and body["id"]
        assert body["status"] == "queued"
        assert body["reused"] is False
    finally:
        _cancel_scheduled_task(r.json().get("id"))
        server.db = original_db
        _restore_llm(original_llm)


def test_get_unknown_job_id_is_404():
    fake = _FakeDB()
    original = _swap_db(fake)
    try:
        r = client.get("/api/reports/compare/explain/does-not-exist")
        assert r.status_code == 404
    finally:
        server.db = original


def test_get_returns_completed_explanation_with_exact_field_set():
    fake = _FakeDB()
    now = "2026-08-17T00:00:00+00:00"
    asyncio.run(fake.comparison_explanation_jobs.insert_one({
        "id": "job-1", "report_ids": ["r1", "r2"], "identity_key": "k1",
        "active_identity_key": None, "resolved_identity_key": "k1",
        "status": "completed", "created_at": now, "updated_at": now,
        "completed_at": now, "user_id": USER["id"], "events": [], "error": None,
    }))
    asyncio.run(fake.comparison_explanations.insert_one({
        "id": "job-1", "identity_key": "k1", "comparison_report_ids": ["r1", "r2"],
        "narrative": "R1 has higher revenue [1].",
        "sources": [{"index": 1, "report_id": "r1", "field": "extracted_data"}],
        "cited_source_indices": [1], "limitations": [], "evidence_completeness": "complete",
        "evidence_fingerprint": "fp1", "generated_at": now,
    }))
    original = _swap_db(fake)
    try:
        r = client.get("/api/reports/compare/explain/job-1")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "completed"
        assert body["id"] == "job-1"
        explanation = body["explanation"]
        assert set(explanation.keys()) == {
            "id", "comparison_report_ids", "narrative", "sources",
            "cited_source_indices", "limitations", "evidence_completeness", "generated_at",
        }
        assert "identity_key" not in explanation
        assert "evidence_fingerprint" not in explanation
        assert explanation["id"] == "job-1"
    finally:
        server.db = original


def test_get_echoes_the_requested_job_id_even_if_artifact_was_authored_by_another_job():
    """Document 43 §9's justified id coupling: the wire-contract `id` is
    "which job did you ask about," not whatever id happened to win the
    persistence race for the shared identity_key."""
    fake = _FakeDB()
    now = "2026-08-17T00:00:00+00:00"
    asyncio.run(fake.comparison_explanation_jobs.insert_one({
        "id": "job-B", "report_ids": ["r1", "r2"], "identity_key": "k1",
        "active_identity_key": None, "resolved_identity_key": "k1",
        "status": "completed", "created_at": now, "updated_at": now,
        "user_id": USER["id"], "events": [], "error": None,
    }))
    asyncio.run(fake.comparison_explanations.insert_one({
        "id": "job-A",  # a DIFFERENT job authored/won this artifact
        "identity_key": "k1", "comparison_report_ids": ["r1", "r2"],
        "narrative": "X [1].", "sources": [{"index": 1, "report_id": "r1", "field": "report"}],
        "cited_source_indices": [1], "limitations": [], "evidence_completeness": "complete",
        "evidence_fingerprint": "fp1", "generated_at": now,
    }))
    original = _swap_db(fake)
    try:
        r = client.get("/api/reports/compare/explain/job-B")
        assert r.json()["explanation"]["id"] == "job-B"
    finally:
        server.db = original


def test_get_non_completed_job_has_no_explanation_field():
    fake = _FakeDB()
    now = "2026-08-17T00:00:00+00:00"
    asyncio.run(fake.comparison_explanation_jobs.insert_one({
        "id": "job-2", "report_ids": ["r1", "r2"], "identity_key": "k2",
        "active_identity_key": "k2", "resolved_identity_key": None,
        "status": "running", "created_at": now, "updated_at": now,
        "user_id": USER["id"], "events": [], "error": None,
    }))
    original = _swap_db(fake)
    try:
        r = client.get("/api/reports/compare/explain/job-2")
        body = r.json()
        assert body["status"] == "running"
        assert "explanation" not in body
    finally:
        server.db = original


# --- cancellation --------------------------------------------------------------

def test_cancel_queued_job_transitions_to_cancelled():
    fake = _FakeDB()
    now = "2026-08-17T00:00:00+00:00"
    asyncio.run(fake.comparison_explanation_jobs.insert_one({
        "id": "job-3", "report_ids": ["r1", "r2"], "identity_key": "k3",
        "active_identity_key": "k3", "resolved_identity_key": None,
        "status": "queued", "created_at": now, "updated_at": now,
        "user_id": USER["id"], "events": [], "error": None,
    }))
    original = _swap_db(fake)
    try:
        r = client.post("/api/reports/compare/explain/job-3/cancel")
        assert r.status_code == 200
        assert r.json() == {"id": "job-3", "status": "cancelled"}
    finally:
        server.db = original


def test_cancel_already_completed_job_is_a_noop():
    fake = _FakeDB()
    now = "2026-08-17T00:00:00+00:00"
    asyncio.run(fake.comparison_explanation_jobs.insert_one({
        "id": "job-4", "report_ids": ["r1", "r2"], "identity_key": "k4",
        "active_identity_key": None, "resolved_identity_key": "k4",
        "status": "completed", "created_at": now, "updated_at": now,
        "user_id": USER["id"], "events": [], "error": None,
    }))
    original = _swap_db(fake)
    try:
        r = client.post("/api/reports/compare/explain/job-4/cancel")
        assert r.status_code == 200
        assert r.json() == {"id": "job-4", "status": "completed"}
    finally:
        server.db = original


def test_cancel_unknown_job_is_404():
    fake = _FakeDB()
    original = _swap_db(fake)
    try:
        r = client.post("/api/reports/compare/explain/does-not-exist/cancel")
        assert r.status_code == 404
    finally:
        server.db = original


def test_cancel_someone_elses_job_is_404_not_403():
    """Mirrors cancel_explanation's existing non-disclosure posture — a
    non-owner gets 404, never a 403 that would confirm the job exists."""
    fake = _FakeDB()
    now = "2026-08-17T00:00:00+00:00"
    asyncio.run(fake.comparison_explanation_jobs.insert_one({
        "id": "job-5", "report_ids": ["r1", "r2"], "identity_key": "k5",
        "active_identity_key": "k5", "resolved_identity_key": None,
        "status": "queued", "created_at": now, "updated_at": now,
        "user_id": OTHER_USER["id"], "events": [], "error": None,
    }))
    original = _swap_db(fake)
    try:
        r = client.post("/api/reports/compare/explain/job-5/cancel")
        assert r.status_code == 404
    finally:
        server.db = original


# --- cross-user deduplication (corrective pass) --------------------------------

def test_cross_user_dedup_never_exposes_another_users_job_id():
    """User A and User B are both independently authorized (shared sample
    reports) and request the identical comparison. Dedup may reuse the shared
    underlying artifact, but the job id each caller gets back must belong to
    THEM — User B must be able to GET the id POST handed back, and must never
    be able to reach User A's actual job id."""
    fake = _FakeDB()
    asyncio.run(fake.reports.insert_one(_report("r1", user_id=USER["id"], is_sample=True)))
    asyncio.run(fake.reports.insert_one(_report("r2", user_id=USER["id"], is_sample=True)))
    original_db = _swap_db(fake)
    original_llm = _stub_llm_never_called()
    try:
        # User A creates the job.
        r_a = client.post("/api/reports/compare/explain", json={"report_ids": ["r1", "r2"]})
        assert r_a.status_code == 200
        job_id_a = r_a.json()["id"]
        _cancel_scheduled_task(job_id_a)

        # Deterministically complete User A's job + the shared artifact
        # (avoids depending on a real/racy background task for this
        # ownership-focused test — the generation path itself is already
        # covered by test_comparison_explanation_execution.py).
        job_doc_a = asyncio.run(fake.comparison_explanation_jobs.find_one({"id": job_id_a}))
        identity_key = job_doc_a["identity_key"]
        now = "2026-08-17T00:00:00+00:00"
        asyncio.run(fake.comparison_explanations.insert_one({
            "id": job_id_a, "identity_key": identity_key,
            "comparison_report_ids": ["r1", "r2"], "narrative": "X differs from Y [1].",
            "sources": [{"index": 1, "report_id": "r1", "field": "report"}],
            "cited_source_indices": [1], "limitations": [], "evidence_completeness": "complete",
            "evidence_fingerprint": "fp", "generated_at": now,
        }))
        asyncio.run(fake.comparison_explanation_jobs.update_one(
            {"id": job_id_a},
            {"$set": {"status": "completed", "resolved_identity_key": identity_key, "active_identity_key": None}},
        ))

        # User B requests the identical comparison.
        server.app.dependency_overrides[server.current_user] = lambda: OTHER_USER
        try:
            r_b = client.post("/api/reports/compare/explain", json={"report_ids": ["r1", "r2"]})
        finally:
            server.app.dependency_overrides[server.current_user] = lambda: USER
        assert r_b.status_code == 200
        body_b = r_b.json()
        assert body_b["reused"] is True
        job_id_b = body_b["id"]
        assert job_id_b != job_id_a, "dedup must never hand back another user's job id"

        # User B can GET the id they were actually given.
        server.app.dependency_overrides[server.current_user] = lambda: OTHER_USER
        try:
            r_get = client.get(f"/api/reports/compare/explain/{job_id_b}")
        finally:
            server.app.dependency_overrides[server.current_user] = lambda: USER
        assert r_get.status_code == 200
        body_get = r_get.json()
        assert body_get["status"] == "completed"
        assert body_get["explanation"]["narrative"] == "X differs from Y [1]."  # the shared artifact, reused correctly

        # User B can never reach User A's actual job id, via GET or stream —
        # tenant isolation is preserved even though the artifact is shared.
        server.app.dependency_overrides[server.current_user] = lambda: OTHER_USER
        try:
            r_leak_get = client.get(f"/api/reports/compare/explain/{job_id_a}")
            r_leak_stream = client.get(f"/api/reports/compare/explain/{job_id_a}/stream")
        finally:
            server.app.dependency_overrides[server.current_user] = lambda: USER
        assert r_leak_get.status_code == 404
        assert r_leak_stream.status_code == 404
    finally:
        server.db = original_db
        _restore_llm(original_llm)


def test_cross_user_dedup_still_creates_a_new_job_reference_not_a_ghost_share():
    """Sanity check on the fix's shape: User B's own job document exists and
    is owned by User B (not a copy of User A's doc / not user_id-less)."""
    fake = _FakeDB()
    asyncio.run(fake.reports.insert_one(_report("r1", user_id=USER["id"], is_sample=True)))
    asyncio.run(fake.reports.insert_one(_report("r2", user_id=USER["id"], is_sample=True)))
    original_db = _swap_db(fake)
    original_llm = _stub_llm_never_called()
    try:
        r_a = client.post("/api/reports/compare/explain", json={"report_ids": ["r1", "r2"]})
        job_id_a = r_a.json()["id"]
        _cancel_scheduled_task(job_id_a)
        job_doc_a = asyncio.run(fake.comparison_explanation_jobs.find_one({"id": job_id_a}))
        identity_key = job_doc_a["identity_key"]
        now = "2026-08-17T00:00:00+00:00"
        asyncio.run(fake.comparison_explanations.insert_one({
            "id": job_id_a, "identity_key": identity_key,
            "comparison_report_ids": ["r1", "r2"], "narrative": "X [1].",
            "sources": [{"index": 1, "report_id": "r1", "field": "report"}],
            "cited_source_indices": [1], "limitations": [], "evidence_completeness": "complete",
            "evidence_fingerprint": "fp", "generated_at": now,
        }))
        asyncio.run(fake.comparison_explanation_jobs.update_one(
            {"id": job_id_a},
            {"$set": {"status": "completed", "resolved_identity_key": identity_key, "active_identity_key": None}},
        ))

        server.app.dependency_overrides[server.current_user] = lambda: OTHER_USER
        try:
            r_b = client.post("/api/reports/compare/explain", json={"report_ids": ["r1", "r2"]})
        finally:
            server.app.dependency_overrides[server.current_user] = lambda: USER
        job_id_b = r_b.json()["id"]

        job_doc_b = asyncio.run(fake.comparison_explanation_jobs.find_one({"id": job_id_b}))
        assert job_doc_b is not None
        assert job_doc_b["user_id"] == OTHER_USER["id"]
        assert job_doc_b["resolved_identity_key"] == identity_key
    finally:
        server.db = original_db
        _restore_llm(original_llm)


# --- deterministic-comparison isolation ----------------------------------------

def test_compare_endpoint_untouched_by_explain_capability():
    """POST /reports/compare's own behavior/shape must be identical to before
    M9.1 — no generate_explanation flag, no new fields, no AI generation."""
    fake = _FakeDB()
    asyncio.run(fake.reports.insert_one(_report("r1")))
    asyncio.run(fake.reports.insert_one(_report("r2")))
    original = _swap_db(fake)
    try:
        r = client.post("/api/reports/compare", json={"report_ids": ["r1", "r2"]})
        assert r.status_code == 200
        body = r.json()
        assert set(body.keys()) == {"reports"}
        assert len(body["reports"]) == 2
        # explicitly reject any smuggled explanation-generation trigger
        r2 = client.post("/api/reports/compare", json={"report_ids": ["r1", "r2"], "generate_explanation": True})
        assert r2.status_code == 200
        assert set(r2.json().keys()) == {"reports"}  # extra field silently ignored, no AI behavior added
    finally:
        server.db = original


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
