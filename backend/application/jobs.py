"""JobLifecycle — the shared job lifecycle use case (M2 Phase 1 "Background
Infrastructure" scope; 06 §2.3, ADR-001/011). Backed by the JobStore and
EventBus ports only — no LangGraph, no research/Learning-specific logic
("do not implement Learning jobs yet"; the actual `_run_pipeline`/JOBS-dict
cutover for the live report pipeline is Migration Phase 4, 06 §7, and is not
done in this phase — see this class's module-level docstring note below).

Every method here is feature-agnostic: `start()` takes a `kind` (research |
learning) and enforces ONE shared MAX_ACTIVE_JOBS budget across both (03's
design — Learning does not get its own queue). This is the seam Phase 4
(existing report pipeline) and Phase L (Learning) both build their actual
`_run_pipeline`-equivalents on top of, once each is ready to move off its
current bespoke state.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone

from application.ports import EventBus, JobStore
from domain.errors import NotFoundError, RateLimitedError
from domain.events import TraceEvent
from domain.models import Job, JobKind, JobStatus


def _now_ts() -> str:
    return datetime.now(timezone.utc).isoformat()


class JobLifecycle:
    def __init__(self, store: JobStore, events: EventBus, *, max_active_jobs: int) -> None:
        self._store = store
        self._events = events
        self._max_active_jobs = max_active_jobs

    async def start(
        self, job_id: str, kind: JobKind, user_id: str, *, ticker: str | None = None,
        deadline_s: float | None = None,
    ) -> Job:
        """Admission control + job creation + the opening `pipeline/start`
        trace event, in one call — the three things every kind of job
        needs done in the same order (07 §4.2's envelope: `pipeline/start`
        is always event #1)."""
        if await self._store.active_count() >= self._max_active_jobs:
            raise RateLimitedError(
                "Too many analyses in progress. Retry in a moment.", code="too_many_jobs"
            )
        deadline_at = time.time() + deadline_s if deadline_s is not None else None
        job = Job(id=job_id, kind=kind, user_id=user_id, ticker=ticker, deadline_at=deadline_at)
        await self._store.create(job)
        await self._events.publish(job_id, {
            "node": "pipeline", "status": "start",
            "message": f"Starting AlphaScribe pipeline for {ticker}" if ticker else "Starting",
            "ts": _now_ts(),
        })
        return job

    async def mark_running(self, job_id: str) -> None:
        await self._store.set_status(job_id, JobStatus.RUNNING)

    async def publish(self, job_id: str, event: TraceEvent) -> None:
        """The per-node trace events between start and the terminal one —
        callers (the LangGraph run loop, once Phase 4 wires it here) call
        this once per node completion, exactly mirroring the existing
        `push()` in server.py's `_run_pipeline` (server.py:698-705), minus
        the direct Mongo `$push` this replaces (08 DA-3 — Redis Streams own
        replay; see infrastructure/redis/event_bus.py)."""
        await self._events.publish(job_id, event)

    async def complete(self, job_id: str) -> None:
        await self._store.set_status(job_id, JobStatus.COMPLETED)
        await self._events.publish(job_id, {"node": "pipeline", "status": "ok", "ts": _now_ts()})

    async def fail(self, job_id: str, safe_message: str) -> None:
        """`safe_message` — never the raw exception. Provider SDK exceptions
        can embed an API key (10 T-13); the caller is responsible for
        already having redacted/genericized the message before it reaches
        here, exactly as server.py's existing except-block does today
        (server.py:779-795) — this method does not re-derive that logic,
        only persists and publishes what it's given."""
        await self._store.set_status(job_id, JobStatus.FAILED, error=safe_message)
        await self._events.publish(job_id, {
            "node": "pipeline", "status": "error",
            "message": f"Pipeline failed: {safe_message}", "ts": _now_ts(),
        })

    async def cancel(self, job_id: str) -> Job:
        """Idempotent (10 §5's Learning cancel contract — fire-and-forget,
        never read by the client): cancelling an already-terminal job is a
        no-op that still returns the job, not an error."""
        job = await self._store.get(job_id)
        if job is None:
            raise NotFoundError(f"job not found: {job_id}")
        if job.is_terminal():
            return job
        await self._store.set_status(job_id, JobStatus.CANCELLED)
        await self._events.publish(job_id, {
            "node": "pipeline", "status": "warn",
            "message": "Analysis cancelled by user", "ts": _now_ts(),
        })
        job.status = JobStatus.CANCELLED
        return job

    async def get(self, job_id: str) -> Job | None:
        return await self._store.get(job_id)

    async def is_past_deadline(self, job_id: str) -> bool:
        """07 §5.4 — checked at node boundaries by the graph run loop (once
        Phase 4 wires it there); exposed here so that call site has one
        thing to ask rather than re-deriving `time.time() > deadline_at`
        itself."""
        job = await self._store.get(job_id)
        return job is not None and job.is_past_deadline()

    async def reap_stale(self, *, max_lifetime_s: float) -> list[str]:
        """09 §6.2's self-healing sweep: frees the concurrency slot of any
        job whose active-set entry has outlived MAX_JOB_LIFETIME, and marks
        each one failed (rather than merely freeing the slot silently) so a
        client polling GET /reports/{id} sees a terminal status instead of
        an indefinite "running". Returns the ids reaped, for caller logging.

        This is NOT the full 01 D-6 restart sweep (which additionally needs
        Mongo's durable job records — a repository this phase deliberately
        does not build, "do not implement feature-specific repositories").
        It is the JobStore-only half: freeing concurrency slots the active
        job it's tracking has genuinely exceeded its lifetime for, which
        works standalone today and composes with the Mongo-backed sweep once
        Phase 3/4 builds it."""
        stale_ids = await self._store.reap(max_lifetime_s=max_lifetime_s)
        for job_id in stale_ids:
            job = await self._store.get(job_id)
            if job is not None and not job.is_terminal():
                await self.fail(job_id, "Job exceeded its maximum lifetime.")
        return stale_ids
