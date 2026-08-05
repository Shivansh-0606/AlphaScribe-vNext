"""Unit check for application/jobs.py's JobLifecycle — end-to-end against
the real in-memory JobStore + EventBus adapters (not mocks): this proves the
use case actually composes correctly with its two ports, which is the whole
point of building them as Protocols (06 AD-2/ADR-004).

    python backend/tests/unit/test_job_lifecycle.py
"""
import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from application.jobs import JobLifecycle
from domain.errors import NotFoundError, RateLimitedError
from domain.models import JobKind, JobStatus
from infrastructure.redis.event_bus import InMemoryEventBus
from infrastructure.redis.job_store import InMemoryJobStore


def _lifecycle(max_active_jobs=8):
    return JobLifecycle(InMemoryJobStore(), InMemoryEventBus(), max_active_jobs=max_active_jobs)


def test_start_creates_the_job_and_emits_pipeline_start():
    async def run():
        lc = _lifecycle()
        job = await lc.start("j1", JobKind.RESEARCH, "u1", ticker="AAPL")
        assert job.status == JobStatus.QUEUED
        got = await lc.get("j1")
        assert got.ticker == "AAPL"
        history = await lc._events.history("j1")
        assert history[0]["node"] == "pipeline" and history[0]["status"] == "start"

    asyncio.run(run())


def test_start_enforces_the_shared_concurrency_budget():
    """03's design: research and Learning share ONE MAX_ACTIVE_JOBS budget,
    not a per-kind cap — this test starts one of each kind against a
    budget of 2 to prove the cap is shared, not per-kind."""
    async def run():
        lc = _lifecycle(max_active_jobs=2)
        await lc.start("j1", JobKind.RESEARCH, "u1")
        await lc.start("j2", JobKind.LEARNING, "u1")
        try:
            await lc.start("j3", JobKind.RESEARCH, "u1")
        except RateLimitedError as e:
            assert e.code == "too_many_jobs"
            assert e.status_code == 429
        else:
            raise AssertionError("expected RateLimitedError once the shared budget is exhausted")

    asyncio.run(run())


def test_complete_transitions_status_and_emits_terminal_ok():
    async def run():
        lc = _lifecycle()
        await lc.start("j1", JobKind.RESEARCH, "u1")
        await lc.mark_running("j1")
        assert (await lc.get("j1")).status == JobStatus.RUNNING
        await lc.complete("j1")
        job = await lc.get("j1")
        assert job.status == JobStatus.COMPLETED
        history = await lc._events.history("j1")
        assert history[-1] == {"node": "pipeline", "status": "ok", "ts": history[-1]["ts"]}

    asyncio.run(run())


def test_fail_never_leaks_the_raw_message_shape_and_persists_it():
    async def run():
        lc = _lifecycle()
        await lc.start("j1", JobKind.RESEARCH, "u1")
        await lc.fail("j1", "Analysis failed. See server logs for details.")
        job = await lc.get("j1")
        assert job.status == JobStatus.FAILED
        assert job.error == "Analysis failed. See server logs for details."

    asyncio.run(run())


def test_cancel_is_idempotent_on_an_already_terminal_job():
    """10 §5 — Learning's cancel is fire-and-forget and never read; the
    endpoint must tolerate a second cancel after the job already finished."""
    async def run():
        lc = _lifecycle()
        await lc.start("j1", JobKind.RESEARCH, "u1")
        await lc.complete("j1")
        job = await lc.cancel("j1")  # must not raise, must not flip COMPLETED -> CANCELLED
        assert job.status == JobStatus.COMPLETED

    asyncio.run(run())


def test_cancel_an_active_job_transitions_and_emits_warn():
    async def run():
        lc = _lifecycle()
        await lc.start("j1", JobKind.RESEARCH, "u1")
        job = await lc.cancel("j1")
        assert job.status == JobStatus.CANCELLED
        history = await lc._events.history("j1")
        assert history[-1]["status"] == "warn"

    asyncio.run(run())


def test_cancel_unknown_job_raises_not_found():
    async def run():
        lc = _lifecycle()
        try:
            await lc.cancel("nope")
        except NotFoundError as e:
            assert e.status_code == 404
        else:
            raise AssertionError("expected NotFoundError")

    asyncio.run(run())


def test_is_past_deadline_reflects_the_deadline_set_at_start():
    async def run():
        lc = _lifecycle()
        await lc.start("j1", JobKind.LEARNING, "u1", deadline_s=0.05)
        assert await lc.is_past_deadline("j1") is False
        await asyncio.sleep(0.1)
        assert await lc.is_past_deadline("j1") is True

    asyncio.run(run())


def test_reap_stale_frees_the_slot_and_marks_the_job_failed():
    """09 §6.2's self-healing sweep, as JobLifecycle exposes it — a "crashed"
    job (active-set entry older than max_lifetime) is both freed AND marked
    failed, not silently forgotten."""
    async def run():
        lc = _lifecycle(max_active_jobs=1)
        job = await lc.start("stale", JobKind.RESEARCH, "u1")
        # Directly age the store's bookkeeping to simulate a crash long ago —
        # the public API has no "pretend time passed" hook, by design.
        lc._store._jobs["stale"].created_at = time.time() - 1000
        lc._store._active["stale"] = time.time() - 1000

        reaped = await lc.reap_stale(max_lifetime_s=600.0)
        assert reaped == ["stale"]
        job = await lc.get("stale")
        assert job.status == JobStatus.FAILED
        # The concurrency slot is free again.
        await lc.start("new", JobKind.RESEARCH, "u1")  # must not raise RateLimitedError

    asyncio.run(run())


if __name__ == "__main__":
    test_start_creates_the_job_and_emits_pipeline_start()
    test_start_enforces_the_shared_concurrency_budget()
    test_complete_transitions_status_and_emits_terminal_ok()
    test_fail_never_leaks_the_raw_message_shape_and_persists_it()
    test_cancel_is_idempotent_on_an_already_terminal_job()
    test_cancel_an_active_job_transitions_and_emits_warn()
    test_cancel_unknown_job_raises_not_found()
    test_is_past_deadline_reflects_the_deadline_set_at_start()
    test_reap_stale_frees_the_slot_and_marks_the_job_failed()
    print("ok: JobLifecycle end-to-end against real in-memory JobStore+EventBus — start/admission, "
          "status transitions, cancel idempotency, deadline check, self-healing reap")
