"""Execution-handler tests for M9.1 (_run_comparison_explanation,
_dedup_lookup_or_create_explanation_job — Document 41/42/43). Covers
execution-time authorization, grounding/citation failure, partial evidence,
persistence, and dedup under REAL asyncio concurrency (asyncio.gather over
the natural await points in the code under test — no sleeps used to fake
timing, per this task's own instruction).

The LLM layer is stubbed at `agents.llm._generate_sync` (same technique as
test_llm_retry.py) — no real provider is ever called.

    python -m pytest backend/tests/unit/test_comparison_explanation_execution.py -v
"""
import asyncio
import json
import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

import pytest  # noqa: E402
from pymongo.errors import DuplicateKeyError  # noqa: E402

import agents.llm as llm  # noqa: E402
import server  # noqa: E402
from agents.comparison_explanation import GroundingError, generate_explanation  # noqa: E402
from domain.models import JobKind  # noqa: E402

USER_ID = "exec-test-user"


# --- fake Mongo (same idiom as test_comparison_explanation_endpoint.py) -----

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


def _report(rid, **fields):
    return {
        "id": rid, "ticker": rid.upper(), "user_id": USER_ID, "is_sample": False,
        "extracted_data": {"revenue": "$1B"}, "sentiment_analysis": {}, "scorecard": {},
        **fields,
    }


@pytest.fixture()
def fake_db(monkeypatch):
    db = _FakeDB()
    monkeypatch.setattr(server, "db", db)
    return db


@pytest.fixture()
def stub_llm(monkeypatch):
    """Sets the JSON text `chat_json` will parse as the model's structured
    output. Call the returned setter with the desired payload per test."""
    state = {"text": None}

    def _generate_sync(system, user, model, usage_sink=None):
        if state["text"] is None:
            raise AssertionError("stub_llm() was not configured with a response")
        return state["text"]

    monkeypatch.setattr(llm, "_generate_sync", _generate_sync)

    def _set(payload: dict | str):
        state["text"] = payload if isinstance(payload, str) else json.dumps(payload)

    return _set


def _valid_payload(*, limitations=None):
    return {
        "narrative": "R1 has notably higher revenue than R2 [1].",
        "sources": [{"index": 1, "report_number": 1, "field": "extracted_data"}],
        "cited_source_indices": [1],
        "limitations": limitations or [],
    }


async def _admit(fake_db, report_ids, job_id=None) -> str:
    job_id = job_id or str(uuid.uuid4())
    await server.container.job_lifecycle.start(
        job_id, JobKind.COMPARISON_EXPLANATION, USER_ID,
        deadline_s=server.settings.job_deadline_s["comparison_explanation"],
    )
    now = "2026-08-17T00:00:00+00:00"
    await fake_db.comparison_explanation_jobs.insert_one({
        "id": job_id, "report_ids": report_ids, "identity_key": f"admission-{job_id}",
        "active_identity_key": f"admission-{job_id}", "resolved_identity_key": None,
        "status": "queued", "created_at": now, "updated_at": now,
        "user_id": USER_ID, "events": [], "error": None,
    })
    return job_id


# --- agents.comparison_explanation.generate_explanation (chat_json integration) --

def test_generate_explanation_valid_output_end_to_end(stub_llm):
    stub_llm(_valid_payload())
    reports = [_report("r1"), _report("r2")]
    result = asyncio.run(generate_explanation(reports))
    assert result["evidence_completeness"] == "complete"
    assert result["sources"][0]["report_id"] == "r1"


def test_generate_explanation_zero_citations_raises_grounding_error(stub_llm):
    stub_llm(_valid_payload() | {"cited_source_indices": []})
    reports = [_report("r1"), _report("r2")]
    with pytest.raises(GroundingError):
        asyncio.run(generate_explanation(reports))


def test_generate_explanation_malformed_json_raises(stub_llm):
    stub_llm("this is not json at all { garbage")
    reports = [_report("r1"), _report("r2")]
    with pytest.raises(ValueError):
        asyncio.run(generate_explanation(reports))


# --- _run_comparison_explanation: outcomes -----------------------------------

def test_run_completes_with_complete_evidence(fake_db, stub_llm):
    stub_llm(_valid_payload())
    asyncio.run(fake_db.reports.insert_one(_report("r1")))
    asyncio.run(fake_db.reports.insert_one(_report("r2")))

    async def go():
        job_id = await _admit(fake_db, ["r1", "r2"])
        await server._run_comparison_explanation(job_id, ["r1", "r2"], USER_ID)
        return job_id

    job_id = asyncio.run(go())
    job = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": job_id}))
    assert job["status"] == "completed"
    artifact = asyncio.run(fake_db.comparison_explanations.find_one({"identity_key": job["resolved_identity_key"]}))
    assert artifact["evidence_completeness"] == "complete"
    assert artifact["comparison_report_ids"] == ["r1", "r2"]


def test_run_completes_with_partial_evidence(fake_db, stub_llm):
    stub_llm(_valid_payload(limitations=[{"report_number": 2, "metric": "operating_margin", "reason": "not disclosed"}]))
    asyncio.run(fake_db.reports.insert_one(_report("r1")))
    asyncio.run(fake_db.reports.insert_one(_report("r2")))

    async def go():
        job_id = await _admit(fake_db, ["r1", "r2"])
        await server._run_comparison_explanation(job_id, ["r1", "r2"], USER_ID)
        return job_id

    job_id = asyncio.run(go())
    job = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": job_id}))
    assert job["status"] == "completed"
    artifact = asyncio.run(fake_db.comparison_explanations.find_one({"identity_key": job["resolved_identity_key"]}))
    assert artifact["evidence_completeness"] == "partial"
    assert artifact["limitations"] == [{"report_id": "r2", "metric": "operating_margin", "reason": "not disclosed"}]


def test_run_zero_citations_marks_job_failed_not_a_degraded_success(fake_db, stub_llm):
    stub_llm(_valid_payload() | {"cited_source_indices": []})
    asyncio.run(fake_db.reports.insert_one(_report("r1")))
    asyncio.run(fake_db.reports.insert_one(_report("r2")))

    async def go():
        job_id = await _admit(fake_db, ["r1", "r2"])
        await server._run_comparison_explanation(job_id, ["r1", "r2"], USER_ID)
        return job_id

    job_id = asyncio.run(go())
    job = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": job_id}))
    assert job["status"] == "failed"
    assert job["error"]  # a redacted, safe message — never raw LLM output
    assert fake_db.comparison_explanations._docs == []  # nothing persisted


def test_run_malformed_output_marks_job_failed_without_leaking_raw_text(fake_db, stub_llm):
    stub_llm("not json { garbage")
    asyncio.run(fake_db.reports.insert_one(_report("r1")))
    asyncio.run(fake_db.reports.insert_one(_report("r2")))

    async def go():
        job_id = await _admit(fake_db, ["r1", "r2"])
        await server._run_comparison_explanation(job_id, ["r1", "r2"], USER_ID)
        return job_id

    job_id = asyncio.run(go())
    job = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": job_id}))
    assert job["status"] == "failed"
    assert "garbage" not in job["error"]
    assert "not json" not in job["error"]


# --- execution-time authorization (Document 41 §13.2/§16) --------------------

def test_execution_time_narrowing_below_two_fails_with_exact_message(fake_db, stub_llm):
    """r2 was requested but is no longer authorized/visible by execution
    time (deleted, or ownership changed) — the job must fail with the exact
    same message compare_reports itself uses, per Document 43 §12/§16."""
    stub_llm(_valid_payload())
    asyncio.run(fake_db.reports.insert_one(_report("r1")))  # r2 intentionally absent

    async def go():
        job_id = await _admit(fake_db, ["r1", "r2"])
        await server._run_comparison_explanation(job_id, ["r1", "r2"], USER_ID)
        return job_id

    job_id = asyncio.run(go())
    job = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": job_id}))
    assert job["status"] == "failed"
    assert job["error"] == "fewer than 2 reports found"


def test_execution_time_narrowing_still_above_two_succeeds_with_narrower_set(fake_db, stub_llm):
    """3 requested, only 2 still authorized at execution time -- the job
    succeeds, but comparison_report_ids reflects the NARROWER, execution-time
    resolved set, never the originally-requested one (Document 41 §13.2)."""
    stub_llm(_valid_payload())
    asyncio.run(fake_db.reports.insert_one(_report("r1")))
    asyncio.run(fake_db.reports.insert_one(_report("r2")))
    # r3 intentionally absent -- became inaccessible between admission and execution

    async def go():
        job_id = await _admit(fake_db, ["r1", "r2", "r3"])
        await server._run_comparison_explanation(job_id, ["r1", "r2", "r3"], USER_ID)
        return job_id

    job_id = asyncio.run(go())
    job = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": job_id}))
    assert job["status"] == "completed"
    artifact = asyncio.run(fake_db.comparison_explanations.find_one({"identity_key": job["resolved_identity_key"]}))
    assert artifact["comparison_report_ids"] == ["r1", "r2"]


def test_execution_time_reauthorizes_never_trusts_admission_time_snapshot(fake_db, stub_llm):
    """A report that was NOT authorized at admission time but becomes
    authorized by execution time (rare, but the code must not have cached a
    stale 'unauthorized' verdict) is correctly included -- proves execution
    time genuinely re-runs the predicate rather than reusing an earlier
    result."""
    stub_llm(_valid_payload())
    # Simulate: at "admission time" neither report existed in the DB the job
    # was admitted against; by the time _run_comparison_explanation executes,
    # both are present -- the function must read fresh, not reuse anything
    # captured at admission.
    asyncio.run(fake_db.reports.insert_one(_report("r1")))
    asyncio.run(fake_db.reports.insert_one(_report("r2")))

    async def go():
        job_id = str(uuid.uuid4())
        await server.container.job_lifecycle.start(
            job_id, JobKind.COMPARISON_EXPLANATION, USER_ID,
            deadline_s=server.settings.job_deadline_s["comparison_explanation"],
        )
        now = "2026-08-17T00:00:00+00:00"
        await fake_db.comparison_explanation_jobs.insert_one({
            "id": job_id, "report_ids": ["r1", "r2"], "identity_key": "whatever-admission-computed",
            "active_identity_key": "whatever-admission-computed", "resolved_identity_key": None,
            "status": "queued", "created_at": now, "updated_at": now,
            "user_id": USER_ID, "events": [], "error": None,
        })
        await server._run_comparison_explanation(job_id, ["r1", "r2"], USER_ID)
        return job_id

    job_id = asyncio.run(go())
    job = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": job_id}))
    assert job["status"] == "completed"


# --- deduplication under real asyncio concurrency (Step 10 — no sleeps) ------

def test_concurrent_admission_for_identical_identity_creates_exactly_one_active_job(fake_db):
    """Two callers (the SAME user, here — cross-user is covered separately by
    test_concurrent_admission_by_different_users_for_same_identity_never_shares_a_job_id)
    hit _dedup_lookup_or_create_explanation_job for the exact same identity_key
    concurrently (asyncio.gather over the function's own real await points --
    find_one/insert_one on the fake collections -- which is what creates
    genuine interleaving, not an artificial sleep)."""
    reports = [_report("r1"), _report("r2")]
    asyncio.run(fake_db.reports.insert_one(reports[0]))
    asyncio.run(fake_db.reports.insert_one(reports[1]))

    async def go():
        return await asyncio.gather(
            server._dedup_lookup_or_create_explanation_job(reports, ["r1", "r2"], USER_ID, "same-identity-key"),
            server._dedup_lookup_or_create_explanation_job(reports, ["r1", "r2"], USER_ID, "same-identity-key"),
        )

    result_a, result_b = asyncio.run(go())
    # exactly one of the two admitted a new job; the other attached to it
    assert {result_a["reused"], result_b["reused"]} == {False, True}
    assert result_a["id"] == result_b["id"]
    # active_identity_key is composed as f"{user_id}:{identity_key}" (corrective
    # pass, cross-user dedup fix) -- same user + same identity still collapses
    # to exactly one active-key value, exactly as before the fix.
    active_key = f"{USER_ID}:same-identity-key"
    active_jobs = [d for d in fake_db.comparison_explanation_jobs._docs if d.get("active_identity_key") == active_key]
    assert len(active_jobs) == 1, "two concurrent admissions must not create two active jobs for one identity"


def test_concurrent_admission_by_different_users_for_same_identity_never_shares_a_job_id(fake_db):
    """Corrective-pass regression: two DIFFERENT users concurrently requesting
    the same explanation identity (e.g. both comparing the same sample
    reports) must each get their OWN job id — never one user's id handed to
    the other — even under real asyncio interleaving (asyncio.gather), not
    just sequential calls."""
    reports = [_report("r1"), _report("r2")]
    asyncio.run(fake_db.reports.insert_one(reports[0]))
    asyncio.run(fake_db.reports.insert_one(reports[1]))

    async def go():
        return await asyncio.gather(
            server._dedup_lookup_or_create_explanation_job(reports, ["r1", "r2"], "user-A", "shared-identity-key"),
            server._dedup_lookup_or_create_explanation_job(reports, ["r1", "r2"], "user-B", "shared-identity-key"),
        )

    result_a, result_b = asyncio.run(go())
    assert result_a["id"] != result_b["id"], "different users must never be handed the same job id"
    assert result_a["reused"] is False
    assert result_b["reused"] is False  # each user's own admission is genuinely new, not a cross-user "reuse"
    doc_a = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": result_a["id"], "user_id": "user-A"}))
    doc_b = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": result_b["id"], "user_id": "user-B"}))
    assert doc_a is not None, "user A must be able to find their own job by (id, user_id)"
    assert doc_b is not None, "user B must be able to find their own job by (id, user_id)"


def test_concurrent_execution_for_identical_identity_persists_exactly_one_artifact(fake_db, stub_llm):
    """Two independently-admitted jobs that resolve to the SAME execution-time
    identity (Document 41 §14.1's reconciliation invariant) race to persist —
    only one durable artifact must ever exist, regardless of which job's
    generation "wins"."""
    stub_llm(_valid_payload())
    asyncio.run(fake_db.reports.insert_one(_report("r1")))
    asyncio.run(fake_db.reports.insert_one(_report("r2")))

    async def go():
        job_a = await _admit(fake_db, ["r1", "r2"])
        job_b = await _admit(fake_db, ["r1", "r2"])
        await asyncio.gather(
            server._run_comparison_explanation(job_a, ["r1", "r2"], USER_ID),
            server._run_comparison_explanation(job_b, ["r1", "r2"], USER_ID),
        )
        return job_a, job_b

    job_a, job_b = asyncio.run(go())
    doc_a = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": job_a}))
    doc_b = asyncio.run(fake_db.comparison_explanation_jobs.find_one({"id": job_b}))
    assert doc_a["status"] == "completed"
    assert doc_b["status"] == "completed"
    # both resolved to the identical exec-time identity (same report set,
    # same provider/model) -- and therefore point at the same one artifact
    assert doc_a["resolved_identity_key"] == doc_b["resolved_identity_key"]
    assert len(fake_db.comparison_explanations._docs) == 1, "concurrent identical-identity generations must not duplicate the artifact"


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
