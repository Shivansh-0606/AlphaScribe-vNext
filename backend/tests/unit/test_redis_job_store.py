"""Port-conformance suite for JobStore (09 §11): InMemoryJobStore for real,
RedisJobStore against fakeredis. The self-healing-ZSET test is the one that
matters most — it's the property that makes RR-6 ("an INCR-style counter
leaks a slot forever on a crash") structurally impossible instead of merely
avoided by convention.

    python backend/tests/unit/test_redis_job_store.py
"""
import asyncio
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import fakeredis.aioredis as fakeredis_async

from domain.models import Job, JobKind, JobStatus
from infrastructure.redis.job_store import InMemoryJobStore, RedisJobStore

ADAPTERS = {
    "memory": lambda: InMemoryJobStore(),
    "redis (fakeredis)": lambda: RedisJobStore(fakeredis_async.FakeRedis(decode_responses=True)),
}


def _job(job_id="j1", **overrides):
    defaults = dict(id=job_id, kind=JobKind.RESEARCH, user_id="u1", status=JobStatus.QUEUED)
    defaults.update(overrides)
    return Job(**defaults)


def test_create_and_get_roundtrip():
    for label, make in ADAPTERS.items():
        async def run(make=make):
            store = make()
            job = _job(ticker="AAPL")
            await store.create(job)
            got = await store.get(job.id)
            assert got is not None, label
            assert got.id == job.id and got.kind == JobKind.RESEARCH and got.ticker == "AAPL", label
            assert got.status == JobStatus.QUEUED, label

        asyncio.run(run())


def test_get_unknown_job_returns_none():
    for label, make in ADAPTERS.items():
        assert asyncio.run(make().get("nope")) is None, label


def test_active_count_reflects_queued_and_running_only():
    for label, make in ADAPTERS.items():
        async def run(make=make):
            store = make()
            await store.create(_job("a"))
            await store.create(_job("b"))
            assert await store.active_count() == 2, label
            await store.set_status("a", JobStatus.COMPLETED)
            assert await store.active_count() == 1, label

        asyncio.run(run())


def test_set_status_updates_fields_and_terminal_removes_from_active():
    for label, make in ADAPTERS.items():
        async def run(make=make):
            store = make()
            await store.create(_job("a"))
            await store.set_status("a", JobStatus.FAILED, error="boom")
            got = await store.get("a")
            assert got.status == JobStatus.FAILED, label
            assert got.error == "boom", label
            assert await store.active_count() == 0, label

        asyncio.run(run())


def test_reap_is_self_healing_not_a_leaking_counter():
    """09 RR-6 — the core property. A "crashed" job (created long ago,
    never transitioned to terminal) must free its slot on reap(), unlike an
    INCR counter which would leak it forever."""
    for label, make in ADAPTERS.items():
        async def run(make=make):
            store = make()
            stale = _job("stale", created_at=time.time() - 1000)  # older than any real max_lifetime
            await store.create(stale)
            fresh = _job("fresh")
            await store.create(fresh)
            assert await store.active_count() == 2, label

            reaped = await store.reap(max_lifetime_s=600.0)
            assert reaped == ["stale"], f"[{label}] expected exactly ['stale'] reaped, got {reaped}"
            assert await store.active_count() == 1, label
            # The fresh job is untouched — reap() prunes by score, not by
            # wiping everything.
            assert await store.get("fresh") is not None, label

        asyncio.run(run())


def test_reap_never_removes_the_job_hash_itself_only_the_active_flag():
    # Reaping frees the concurrency slot; it must NOT delete the job's own
    # record — the restart-sweep (01 D-6) still needs to read its status to
    # mark it "failed" for the client, not make it vanish.
    for label, make in ADAPTERS.items():
        async def run(make=make):
            store = make()
            await store.create(_job("stale", created_at=time.time() - 1000))
            await store.reap(max_lifetime_s=600.0)
            assert await store.get("stale") is not None, label

        asyncio.run(run())


if __name__ == "__main__":
    test_create_and_get_roundtrip()
    test_get_unknown_job_returns_none()
    test_active_count_reflects_queued_and_running_only()
    test_set_status_updates_fields_and_terminal_removes_from_active()
    test_reap_is_self_healing_not_a_leaking_counter()
    test_reap_never_removes_the_job_hash_itself_only_the_active_flag()
    print("ok: JobStore port conformance (memory + redis/fakeredis) — create/get, active-count, "
          "terminal removal, self-healing reap")
