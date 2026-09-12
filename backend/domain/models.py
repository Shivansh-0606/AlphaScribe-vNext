"""Shared domain entities for M2 Phase 1's infrastructure — deliberately
minimal. Feature-shaped entities (Report, Explanation, SourceDocument) are
NOT here: they belong to the research/Learning features themselves (out of
this phase's scope — "do not implement feature-specific repositories").

`Job` is the one entity every future capability needs regardless of feature:
both the existing report pipeline and the future Learning pipeline are "a job
with a status, a kind, and a deadline" (07 §5.4, 09 §6, ADR-011). Kept as a
plain dataclass, not a Pydantic model — nothing here crosses the wire
directly (transport DTOs are a Phase 6 concern, 06 AD-11/ADR-006); this is
pure in-process domain state.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum


class JobKind(str, Enum):
    RESEARCH = "research"
    LEARNING = "learning"
    COMPARISON_EXPLANATION = "comparison_explanation"
    FILING_ANALYSIS = "filing_analysis"  # M14 — additive (Document 65 OAQ-4 / §11; Document 66 §5 C-c)
    CHANGE_BRIEF = "change_brief"  # M15 — additive (Document 73 R1 §16; Document 75 §15; Document 76)
    FILING_QA = "filing_qa"  # M16 — additive (Document 90 §7; Document 94 Revision 1 §5.2)


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL_STATUSES = frozenset({JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED})


@dataclass
class Job:
    """In-memory/Redis-resident job state (09 §6.1 — mirrors the job HASH
    shape exactly, field for field). Mongo remains the system of record for
    the *output* of a job (a report/explanation document); this dataclass
    never is one — see the module docstring.

    All timestamps are wall-clock epoch seconds (`time.time()`), not
    `time.monotonic()` — this state is written by one process and may be
    read (and reaped, 09 §6.2's self-healing ZSET) by another after a
    restart, or scored in a Redis ZSET that outlives the process entirely.
    monotonic time resets on restart and is meaningless across processes, so
    it would silently break the ZSET's "how long has this been active"
    scoring the moment two workers or a restart were involved. (The
    *separate*, in-process "has this job's LangGraph run exceeded its
    07 §5.4 deadline" check IS appropriately monotonic — that lives in the
    graph's own execution state once Phase 3/4 builds it, not here.)"""

    id: str
    kind: JobKind
    user_id: str
    status: JobStatus = JobStatus.QUEUED
    ticker: str | None = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    deadline_at: float | None = None
    error: str | None = None

    def is_terminal(self) -> bool:
        return self.status in TERMINAL_STATUSES

    def is_past_deadline(self, *, now: float | None = None) -> bool:
        if self.deadline_at is None:
            return False
        return (now if now is not None else time.time()) > self.deadline_at
