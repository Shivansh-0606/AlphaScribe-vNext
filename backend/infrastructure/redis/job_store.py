"""JobStore — job hash + self-healing active-set (09 §6).

Two adapters implementing application.ports.JobStore: InMemoryJobStore (test
double + documented fallback, 09 RA-2) and RedisJobStore (production).

09 §6.2's central point, ported faithfully to both adapters: the active set
is a SCORED set (member=job_id, score=start time), never a plain counter.
An INCR-style counter leaks a slot permanently on every crash — after enough
crashes the system refuses all work with a 429 that only a manual reset
clears. A scored set prunes stale entries by time (reap()), so a crashed
worker's slot recovers on its own instead of leaking forever.
"""
from __future__ import annotations

import time
from typing import Any

import redis.asyncio as redis

from domain.models import TERMINAL_STATUSES, Job, JobKind, JobStatus
from infrastructure.observability.metrics import track_redis_errors

_JOB_TTL_S = 24 * 3600  # 09 §3 — job hash TTL, refreshed on write


class InMemoryJobStore:
    """The documented fallback (09 RA-2). A plain dict for job state; a
    dict[job_id, start_time] standing in for the Redis ZSET, with the same
    score-based (not count-based) semantics."""

    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._active: dict[str, float] = {}

    async def create(self, job: Job) -> None:
        self._jobs[job.id] = job
        if job.status not in TERMINAL_STATUSES:
            self._active[job.id] = job.created_at

    async def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    async def set_status(self, job_id: str, status: JobStatus, **fields: Any) -> None:
        job = self._jobs.get(job_id)
        if job is None:
            return
        job.status = status
        job.updated_at = time.time()
        for k, v in fields.items():
            setattr(job, k, v)
        if status in TERMINAL_STATUSES:
            self._active.pop(job_id, None)
        else:
            self._active.setdefault(job_id, job.created_at)

    async def active_count(self) -> int:
        return len(self._active)

    async def reap(self, *, max_lifetime_s: float = 600.0) -> list[str]:
        """Returns the job ids pruned (not just a count) — the restart-sweep
        (01 D-6) needs to know WHICH jobs to mark failed and notify, not
        merely how many."""
        cutoff = time.time() - max_lifetime_s
        stale = [jid for jid, started in self._active.items() if started < cutoff]
        for jid in stale:
            self._active.pop(jid, None)
        return stale


class RedisJobStore:
    """09 §6 — a HASH per job (`as:v1:job:{id}`) for state, and one shared
    ZSET (`as:v1:jobs:active`) for admission control across every job kind."""

    def __init__(self, client: redis.Redis, *, namespace: str = "as:v1") -> None:
        self._r = client
        self._ns = namespace

    def _job_key(self, job_id: str) -> str:
        return f"{self._ns}:job:{job_id}"

    @property
    def _active_key(self) -> str:
        return f"{self._ns}:jobs:active"

    async def create(self, job: Job) -> None:
        async with track_redis_errors("job_store.create"):
            key = self._job_key(job.id)
            mapping = {
                "id": job.id,
                "kind": job.kind.value,
                "user_id": job.user_id,
                "status": job.status.value,
                "ticker": job.ticker or "",
                "created_at": str(job.created_at),
                "updated_at": str(job.updated_at),
                "deadline_at": str(job.deadline_at) if job.deadline_at is not None else "",
                "error": job.error or "",
            }
            await self._r.hset(key, mapping=mapping)
            await self._r.expire(key, _JOB_TTL_S)
            if job.status not in TERMINAL_STATUSES:
                await self._r.zadd(self._active_key, {job.id: job.created_at})

    async def get(self, job_id: str) -> Job | None:
        data = await self._r.hgetall(self._job_key(job_id))
        if not data:
            return None
        return Job(
            id=data["id"],
            kind=JobKind(data["kind"]),
            user_id=data["user_id"],
            status=JobStatus(data["status"]),
            ticker=data["ticker"] or None,
            created_at=float(data["created_at"]),
            updated_at=float(data["updated_at"]),
            deadline_at=float(data["deadline_at"]) if data.get("deadline_at") else None,
            error=data["error"] or None,
        )

    async def set_status(self, job_id: str, status: JobStatus, **fields: Any) -> None:
        key = self._job_key(job_id)
        mapping = {"status": status.value, "updated_at": str(time.time())}
        for k, v in fields.items():
            mapping[k] = "" if v is None else str(v)
        await self._r.hset(key, mapping=mapping)
        await self._r.expire(key, _JOB_TTL_S)
        if status in TERMINAL_STATUSES:
            await self._r.zrem(self._active_key, job_id)

    async def active_count(self) -> int:
        return await self._r.zcard(self._active_key)

    async def reap(self, *, max_lifetime_s: float = 600.0) -> list[str]:
        """Returns the job ids pruned — see InMemoryJobStore.reap()'s
        docstring. ZREMRANGEBYSCORE alone only returns a count, so this is
        ZRANGEBYSCORE (read the ids) then ZREMRANGEBYSCORE (remove them) —
        two round-trips instead of one, in exchange for actually knowing
        which jobs the restart-sweep needs to mark failed."""
        cutoff = time.time() - max_lifetime_s
        stale = await self._r.zrangebyscore(self._active_key, "-inf", cutoff)
        if stale:
            await self._r.zremrangebyscore(self._active_key, "-inf", cutoff)
        return stale
