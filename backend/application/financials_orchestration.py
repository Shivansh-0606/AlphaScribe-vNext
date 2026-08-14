"""FinancialsAcquisitionOrchestrator — M8 Step 6 (Document 39 §18: "Wire the
use case into Document 36's existing, ratified triggers"). The execution
boundary AROUND AcquireFinancialsUseCase (Step 5, frozen): schedules
background acquisition attempts for a ticker's relevant identities and
returns immediately, never blocking its caller.

Fire-and-forget mechanism matches this codebase's only existing precedent
for this exact pattern (server.py:360's
`asyncio.create_task(notify.send_otp_email(...))`) — a bare
`asyncio.create_task(coro)`, no wrapper, no result ever retrieved. That
precedent only works because the scheduled coroutine itself never raises;
`AcquireFinancialsUseCase.acquire()` already satisfies that same contract
(every failure path returns a typed `AcquisitionResult` — Step 5, frozen),
so this module adds no defensive exception handling of its own around it.

Reused, not duplicated, from Step 5: AS-4, AS-5, provider-outcome
classification, acquisition-state semantics, and Step 5's own per-identity
tracing/metrics/logging. This module's own observability is
orchestration-level only — "N identities were scheduled for this ticker,
by this trigger" — not a second copy of what Step 5 already records per
attempt.

Document 36 §5's trigger model: this module is invoked BY a trigger (§4.1
report/explain ingestion, wired into server.py's `ensure_company` this
step; §4.3 an operational command, `scripts/acquire_financials.py`) — it is
not itself a trigger, and it carries no user context into `acquire()`
(Document 36 §19 — acquisition is shared-corpus, trigger-agnostic).

Concurrency bound (added after live verification, see _MAX_CONCURRENT_
ACQUISITIONS below): each acquisition attempt's provider call runs via
asyncio.to_thread (agents/financials_provider.py), which draws from
Python's shared default thread-pool executor — the same pool every other
asyncio.to_thread caller in this process uses (existing EDGAR/yfinance
fetches, embeddings, etc.). Scheduling all 6 identities per ticker
unbounded, across several tickers in quick succession, was observed live
to exhaust that pool and stall unrelated requests. This is a local
thread-pool-pressure bound, unrelated to and not a substitute for
provider-side rate-limit/backoff policy (Document 36 §12/§25's still-open
Engineering Question, not decided here).
"""
from __future__ import annotations

import asyncio
import logging
from typing import Iterable

from application.financials import AcquireFinancialsUseCase, AcquisitionResult
from domain.financials import PeriodType, StatementType
from infrastructure.observability.metrics import acquisition_orchestration_scheduled_total
from infrastructure.observability.tracing import get_tracer

logger = logging.getLogger("alphascribe.financials")

_ALL_PERIOD_TYPES: tuple[PeriodType, ...] = tuple(PeriodType)
_ALL_STATEMENT_TYPES: tuple[StatementType, ...] = tuple(StatementType)

# ponytail: a fixed, process-wide cap — simplest thing that stops
# unbounded scheduling from starving other asyncio.to_thread callers
# (discovered empirically: an unthrottled run caused an unrelated endpoint
# to time out under the live test suite). Not a queue, not a scheduler, not
# a retry/backoff policy — a plain asyncio.Semaphore shared across every
# scheduled acquisition in the process. Raise if evidence shows 3 is overly
# conservative; lower if the default thread pool is shared with other
# latency-sensitive work under real load.
_MAX_CONCURRENT_ACQUISITIONS = 3
_acquisition_semaphore = asyncio.Semaphore(_MAX_CONCURRENT_ACQUISITIONS)


async def _bounded_acquire(
    use_case: AcquireFinancialsUseCase, ticker: str, period_type: PeriodType, statement_type: StatementType
) -> AcquisitionResult:
    async with _acquisition_semaphore:
        return await use_case.acquire(ticker, period_type, statement_type)


class FinancialsAcquisitionOrchestrator:
    """Constructor-injected with the Step 5 use case, mirroring
    application/jobs.py::JobLifecycle's dependency-injection convention."""

    def __init__(self, use_case: AcquireFinancialsUseCase) -> None:
        self._use_case = use_case

    def schedule(
        self,
        ticker: str,
        *,
        period_types: Iterable[PeriodType] = _ALL_PERIOD_TYPES,
        statement_types: Iterable[StatementType] = _ALL_STATEMENT_TYPES,
        trigger: str = "unspecified",
    ) -> list["asyncio.Task[AcquisitionResult]"]:
        """Schedules one background acquisition attempt per
        (period_type, statement_type) combination and returns immediately.
        Each already-terminal identity short-circuits cheaply inside
        acquire() itself (Step 5) — this method does not pre-filter.

        The returned list is for callers/tests that want to await
        completion explicitly; server.py's trigger wiring does not — it
        fires and moves on (Document 36 §9.3's non-durable execution
        model). `trigger` is an observability label only (e.g.
        "ensure_company", "operational") — never forwarded into
        acquire() itself (Document 36 §19: the use case carries no
        triggering context forward)."""
        ticker = ticker.upper()
        identities = [(pt, st) for pt in period_types for st in statement_types]

        with get_tracer().start_as_current_span("financials.orchestration.schedule") as span:
            span.set_attribute("ticker", ticker)
            span.set_attribute("trigger", trigger)
            span.set_attribute("acquisition.identity_count", len(identities))
            logger.info(
                "acquisition scheduled ticker=%s trigger=%s identity_count=%d",
                ticker, trigger, len(identities),
            )
            acquisition_orchestration_scheduled_total.labels(trigger=trigger).inc(len(identities))
            return [
                asyncio.create_task(_bounded_acquire(self._use_case, ticker, period_type, statement_type))
                for period_type, statement_type in identities
            ]
