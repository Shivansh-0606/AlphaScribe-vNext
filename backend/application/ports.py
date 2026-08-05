"""The seam (06 §2.4/AD-2, ADR-004): `typing.Protocol` ports, structural
typing, zero runtime machinery. Adapters implement these by matching the
shape — no inheritance, no registration.

Seven protocols across six concerns — the two output repositories share one
shape, so `ReportLikeRepository` is generic over the document type rather
than duplicated. Each port exists because *this phase* changes its
implementation or blocks a test:

  - JobStore / EventBus / RateLimiter  — Redis is replacing their
    implementation this phase (ADR-001); each ships two adapters (memory,
    redis) implementing this exact Protocol.
  - LLMClient                          — every node depends on it (01 V-7);
    infrastructure/llm/registry.py implements it, collapsing the duplicated
    provider dispatch (01 D-3).
  - ChunkRepository / ReportLikeRepository — the Protocol is defined so
    Phase 3 has a target to implement against, per this phase's own scope
    note ("repository infrastructure... do not implement feature-specific
    repositories yet"). No Mongo adapter for these ships in this phase —
    only JobStore/EventBus/RateLimiter/LLMClient do.

No port is defined for a concern that is neither changing implementation nor
blocking a test this phase (06 §2.4's Anti-YAGNI check, restated).
"""
from __future__ import annotations

from typing import Any, AsyncIterator, Protocol, Type, TypeVar

from domain.events import TraceEvent
from domain.models import Job, JobStatus

T = TypeVar("T")


class JobStore(Protocol):
    """09 §6 — job hash + active-set. Two adapters ship this phase:
    infrastructure/redis/job_store.py (production) and an in-memory one
    (test double + the documented fallback, 09 RA-2)."""

    async def create(self, job: Job) -> None: ...
    async def get(self, job_id: str) -> Job | None: ...
    async def set_status(self, job_id: str, status: JobStatus, **fields: Any) -> None: ...
    async def active_count(self) -> int:
        """One shared budget across every job kind (03's design: research and
        Learning share MAX_ACTIVE_JOBS, not a per-kind cap) — deliberately
        not parameterized by kind."""
        ...

    async def reap(self) -> list[str]:
        """Prune active-set entries past MAX_JOB_LIFETIME (09 §6.2's
        self-healing ZSET); returns the job ids pruned — the restart-sweep
        (01 D-6) needs to know WHICH jobs to mark failed, not just a count."""
        ...


class EventBus(Protocol):
    """09 §4 — the AD-8 fix for 01 D-1. `subscribe()` MUST return an
    independent iterator per call: two concurrent subscribers to the same
    job_id must each see every event. This is a contract requirement on the
    port itself, not an implementation detail either adapter is free to
    violate (09 §4.1 — the binding ban on XREADGROUP exists precisely
    because it would violate this)."""

    async def publish(self, job_id: str, event: TraceEvent) -> None: ...
    def subscribe(self, job_id: str) -> AsyncIterator[TraceEvent]: ...
    async def history(self, job_id: str) -> list[TraceEvent]: ...


class RateLimiter(Protocol):
    """09 §7 — sliding-window, faithfully mirroring agents/auth.py's
    existing `_recent_hits` semantics (a fixed-window port would allow a
    boundary-burst regression, 09 RR-8)."""

    async def hit(self, key: str) -> bool:
        """Returns True if the call is ALLOWED (mirrors the sense of
        agents.auth.is_rate_limited being inverted — see the adapter)."""
        ...

    async def clear(self, key: str) -> None: ...


class LLMClient(Protocol):
    """Collapses agents/llm.py's `chat_text`/`chat_json` behind one seam so
    a node depends on a port, not a module (06 AD-7). The concrete adapter
    (infrastructure/llm/registry.py) wraps the existing, unmodified
    chat_text/chat_json — this port does not re-implement provider logic."""

    async def text(self, system: str, user: str, *, model: str) -> str: ...
    async def json(self, system: str, user: str, schema: Type[T], *, model: str) -> T: ...


class ChunkRepository(Protocol):
    """Defined, not implemented, this phase — see the module docstring."""

    async def chunks_for_ticker(self, ticker: str, limit: int = 2000) -> list[dict]: ...
    async def count_for_ticker(self, ticker: str) -> int: ...


class ReportLikeRepository(Protocol[T]):
    """Generic over the output document type — `reports` and `explanations`
    share this shape (08 §4.5/§4.7 are structurally identical: id, user_id,
    created_at, + feature payload). Defined, not implemented, this phase."""

    async def save(self, doc: T) -> None: ...
    async def get(self, doc_id: str, *, owner_id: str) -> T | None: ...
    async def delete(self, doc_id: str, *, owner_id: str) -> bool: ...
