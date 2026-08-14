"""The composition root (06 §2.5/AD-3, ADR-004) — the ONLY place adapters are
constructed. Everything else depends on ports (application/ports.py); only
this module knows which concrete class implements which.

`JOB_BACKEND=memory|redis` (default `memory`, per 09 RR-10) selects the
JobStore/EventBus/RateLimiter adapters — the in-process ones are not a
fallback bolted on for tests; they are the documented production option for
`scripts/run.py`'s no-Docker developer path (09 RA-2), and here they are the
default so importing/using this container never requires a running Redis.

`server.py:90` constructs this at import time (`container = build_container(settings)`)
and uses `container.job_lifecycle` on every job admission, publish, and
terminal transition in both the research and Learning pipelines — this has
been live since the M2 Phase 4/L cutover, not merely built-and-tested-standalone
(a stale claim this docstring carried past that cutover; corrected in M6 —
see `docs/backend_engineering/26_M6_Observability_Architecture_Review.md`
A3). `ChunkRepository`/`ReportLikeRepository` adapters and routing
server.py's routes through this container for their data access remain
future Phase 3 work — that part of the original claim still holds.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from application.financials import AcquireFinancialsUseCase
from application.financials_orchestration import FinancialsAcquisitionOrchestrator
from application.jobs import JobLifecycle
from application.ports import AcquisitionStateRepository, EventBus, JobStore, RateLimiter
from app.settings import Settings
from infrastructure.mongo.acquisition_state import MongoAcquisitionStateRepository
from infrastructure.mongo.client import create_mongo_client
from infrastructure.mongo.financial_statements import MongoFinancialStatementRepository
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
    financials_orchestrator: FinancialsAcquisitionOrchestrator
    # M8 Step 7 — exposed separately from AcquireFinancialsUseCase (which
    # holds its own instance privately) so the POST /financials/acquire
    # endpoint can read current AcquisitionState through the same
    # repository port Step 5 uses, without reaching into the use case's
    # internals or duplicating its business logic.
    acquisition_states: AcquisitionStateRepository
    job_backend: str = "memory"
    # M6 A2 — exposed only under JOB_BACKEND=redis, so /health/ready can
    # verify the configured execution backend (26 A2) without the
    # JobStore/EventBus/RateLimiter ports needing a generic, transport-leaking
    # `ping()` method of their own.
    redis_client: object | None = None  # redis.asyncio.Redis, typed loosely for the same reason as mongo_client


def build_container(settings: Settings) -> Container:
    backend = os.environ.get("JOB_BACKEND", "memory").strip().lower()
    mongo_client = create_mongo_client(settings.mongo_url)
    redis_client = None

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

    # M8 Step 6 — the container's first Mongo-backed repository pair,
    # extending the existing composition-root pattern (not a new one).
    db = mongo_client[settings.db_name]
    acquisition_states = MongoAcquisitionStateRepository(db)
    acquire_financials = AcquireFinancialsUseCase(
        MongoFinancialStatementRepository(db), acquisition_states
    )
    financials_orchestrator = FinancialsAcquisitionOrchestrator(acquire_financials)

    return Container(
        settings=settings,
        mongo_client=mongo_client,
        jobs=jobs,
        events=events,
        limiter=limiter,
        job_lifecycle=job_lifecycle,
        financials_orchestrator=financials_orchestrator,
        acquisition_states=acquisition_states,
        job_backend=backend,
        redis_client=redis_client,
    )
