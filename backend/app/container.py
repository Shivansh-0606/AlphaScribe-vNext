"""The composition root (06 §2.5/AD-3, ADR-004) — the ONLY place adapters are
constructed. Everything else depends on ports (application/ports.py); only
this module knows which concrete class implements which.

`JOB_BACKEND=memory|redis` (default `memory`, per 09 RR-10) selects the
JobStore/EventBus/RateLimiter adapters — the in-process ones are not a
fallback bolted on for tests; they are the documented production option for
`scripts/run.py`'s no-Docker developer path (09 RA-2), and here they are the
default so importing/using this container never requires a running Redis.

Nothing in server.py constructs this yet — see the Phase 1 report's
"Additive server.py integration" section for exactly what IS wired live this
phase (health/ready, /metrics, the DomainError handler, request-timing
middleware) versus what is built-and-tested-standalone, ready for Phase 3's
actual cutover (the container itself, ChunkRepository/ReportLikeRepository
adapters, and wiring server.py's routes to resolve dependencies through it).
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from application.jobs import JobLifecycle
from application.ports import EventBus, JobStore, RateLimiter
from app.settings import Settings
from infrastructure.mongo.client import create_mongo_client
from infrastructure.redis.event_bus import InMemoryEventBus, RedisEventBus
from infrastructure.redis.job_store import InMemoryJobStore, RedisJobStore
from infrastructure.redis.rate_limiter import InMemoryRateLimiter, RedisRateLimiter


@dataclass(frozen=True)
class Container:
    settings: Settings
    mongo_client: object  # AsyncIOMotorClient — typed loosely to avoid importing motor here twice
    jobs: JobStore
    events: EventBus
    limiter: RateLimiter
    job_lifecycle: JobLifecycle


def build_container(settings: Settings) -> Container:
    backend = os.environ.get("JOB_BACKEND", "memory").strip().lower()
    mongo_client = create_mongo_client(settings.mongo_url)

    if backend == "redis":
        import redis.asyncio as redis

        redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        jobs: JobStore = RedisJobStore(redis_client)
        events: EventBus = RedisEventBus(redis_client)
        limiter: RateLimiter = RedisRateLimiter(redis_client)
    elif backend == "memory":
        jobs = InMemoryJobStore()
        events = InMemoryEventBus()
        limiter = InMemoryRateLimiter()
    else:
        raise ValueError(f"Unknown JOB_BACKEND: {backend!r} (expected 'memory' or 'redis')")

    job_lifecycle = JobLifecycle(jobs, events, max_active_jobs=settings.max_active_jobs)

    return Container(
        settings=settings,
        mongo_client=mongo_client,
        jobs=jobs,
        events=events,
        limiter=limiter,
        job_lifecycle=job_lifecycle,
    )
