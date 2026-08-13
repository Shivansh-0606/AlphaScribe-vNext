"""AcquireFinancialsUseCase — the shared `acquire(identity)` application
capability Document 36 §6 defines: independently owned, application-layer,
invoked by future peer triggers (report/explain ingestion, the eventual
Financials acquisition-request endpoint, an operational command) — none of
which exist here yet. This is M8 Step 5 (Document 39 §18: "Build the
acquire(identity) use case") — this step builds the use case only, per its
own scope boundary; no trigger is wired to it.

HTTP-independent by construction (Document 36 §22's "application layer"
box) — no FastAPI import, no Mongo query, no yfinance call: everything
provider- and persistence-shaped is injected, mirroring
application/jobs.py::JobLifecycle's constructor-injection convention.

Concurrency: Document 36 §11 — "AS-4 is correctness, full stop... An
in-process per-identity lock remains optional, efficiency-only, and
provides zero correctness guarantee across multiple processes." No lock is
implemented here. Correctness comes entirely from AcquisitionStateRepository
.write_terminal()'s AS-4 conditional write (Phase 1, already built and
tested); this use case's only concurrency-relevant behavior is the
short-circuit read at the top of acquire(), which is a pure efficiency
optimization for the common sequential case — under a genuine race, two
concurrent calls may both call the provider and both attempt a terminal
write, which is safe (not merely tolerated) by AS-4 design, not despite it.
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Awaitable, Callable

from application.ports import AcquisitionStateRepository, FinancialStatementRepository
from agents.financials_provider import ProviderOutcome, ProviderOutcomeKind, fetch_and_classify
from domain.financials import AcquisitionOutcome, PeriodType, StatementType
from infrastructure.observability.metrics import acquisition_attempts_total, acquisition_duration_seconds
from infrastructure.observability.tracing import get_tracer

logger = logging.getLogger("alphascribe.financials")

ProviderCall = Callable[[str, PeriodType, StatementType], Awaitable[ProviderOutcome]]


class AcquisitionResultKind(str, Enum):
    ALREADY_TERMINAL = "already_terminal"  # no provider call — state was already available/confirmed_unavailable
    TRANSITIONED = "transitioned"  # provider called; a terminal write was attempted — check .state for the result
    RECOVERABLE_FAILURE = "recoverable_failure"  # transient/invalid provider result — AS-3, no write, state unchanged
    PERSISTENCE_FAILED = "persistence_failed"  # FinancialStatement upsert raised — no state transition attempted
    STATE_TRANSITION_FAILED = "state_transition_failed"  # AS-5 residual window — statement(s) may already be persisted
    UNEXPECTED_ERROR = "unexpected_error"  # defensive: the injected provider call itself raised


@dataclass
class AcquisitionResult:
    kind: AcquisitionResultKind
    state: AcquisitionOutcome  # the identity's actual current state after this call, ground truth
    detail: str | None = None  # observability only — never a provider/infra exception message verbatim to a caller


class AcquireFinancialsUseCase:
    def __init__(
        self,
        statement_repo: FinancialStatementRepository,
        acquisition_repo: AcquisitionStateRepository,
        *,
        provider: ProviderCall = fetch_and_classify,
    ) -> None:
        self._statements = statement_repo
        self._acquisitions = acquisition_repo
        self._provider = provider

    async def acquire(self, ticker: str, period_type: PeriodType, statement_type: StatementType) -> AcquisitionResult:
        ticker = ticker.upper()
        with get_tracer().start_as_current_span("financials.acquire") as span:
            span.set_attribute("ticker", ticker)
            span.set_attribute("period_type", period_type.value)
            span.set_attribute("statement_type", statement_type.value)
            start = time.monotonic()
            try:
                result = await self._acquire(ticker, period_type, statement_type)
                span.set_attribute("acquisition.result", result.kind.value)
                span.set_attribute("acquisition.state", result.state.value)
                return result
            finally:
                acquisition_duration_seconds.labels(statement_type=statement_type.value).observe(
                    time.monotonic() - start
                )

    async def _acquire(
        self, ticker: str, period_type: PeriodType, statement_type: StatementType
    ) -> AcquisitionResult:
        def _record(result: AcquisitionResult) -> AcquisitionResult:
            acquisition_attempts_total.labels(statement_type=statement_type.value, outcome=result.kind.value).inc()
            return result

        current = await self._acquisitions.get(ticker, period_type, statement_type)
        if current is not AcquisitionOutcome.NOT_YET_ACQUIRED:
            # Already terminal — Document 35 AS-3/AS-4: never re-acquire, never downgrade.
            logger.info(
                "acquisition skipped, already terminal ticker=%s period_type=%s statement_type=%s state=%s",
                ticker, period_type.value, statement_type.value, current.value,
            )
            return _record(AcquisitionResult(AcquisitionResultKind.ALREADY_TERMINAL, state=current))

        logger.info(
            "acquisition attempt started ticker=%s period_type=%s statement_type=%s",
            ticker, period_type.value, statement_type.value,
        )
        try:
            outcome = await self._provider(ticker, period_type, statement_type)
        except Exception as e:  # noqa: BLE001 — defensive: fetch_and_classify never raises by design (M8 Step 3)
            logger.exception(
                "unexpected exception from provider call ticker=%s period_type=%s statement_type=%s",
                ticker, period_type.value, statement_type.value,
            )
            return _record(
                AcquisitionResult(
                    AcquisitionResultKind.UNEXPECTED_ERROR, state=current, detail=f"{type(e).__name__}: {e}"
                )
            )

        logger.info(
            "provider outcome ticker=%s period_type=%s statement_type=%s kind=%s",
            ticker, period_type.value, statement_type.value, outcome.kind.value,
        )

        if outcome.kind in (ProviderOutcomeKind.TRANSIENT_FAILURE, ProviderOutcomeKind.INVALID_RESPONSE):
            # AS-3: no terminal write, prior state (NOT_YET_ACQUIRED here) preserved, safely retryable
            # by a future trigger.
            return _record(
                AcquisitionResult(AcquisitionResultKind.RECOVERABLE_FAILURE, state=current, detail=outcome.detail)
            )

        if outcome.kind is ProviderOutcomeKind.DEFINITIVE_UNAVAILABLE:
            return _record(await self._transition(ticker, period_type, statement_type, current,
                                                    AcquisitionOutcome.CONFIRMED_UNAVAILABLE))

        # SUCCESS or PARTIAL_SUCCESS — AS-5: persist FinancialStatement(s) first, only then transition.
        try:
            for statement in outcome.statements:
                await self._statements.upsert(statement)
        except Exception as e:  # noqa: BLE001 — Mongo/infra failure; state must NOT transition (AS-5)
            logger.error(
                "FinancialStatement persistence failed, acquisition state left unchanged "
                "ticker=%s period_type=%s statement_type=%s error=%s",
                ticker, period_type.value, statement_type.value, e,
            )
            return _record(
                AcquisitionResult(
                    AcquisitionResultKind.PERSISTENCE_FAILED, state=current, detail=f"{type(e).__name__}: {e}"
                )
            )

        return _record(await self._transition(ticker, period_type, statement_type, current,
                                                AcquisitionOutcome.AVAILABLE))

    async def _transition(
        self,
        ticker: str,
        period_type: PeriodType,
        statement_type: StatementType,
        previous: AcquisitionOutcome,
        target: AcquisitionOutcome,
    ) -> AcquisitionResult:
        try:
            new_state = await self._acquisitions.write_terminal(ticker, period_type, statement_type, target)
        except Exception as e:  # noqa: BLE001 — AS-5 residual window: FinancialStatement may already be persisted
            logger.error(
                "AcquisitionState transition failed ticker=%s period_type=%s statement_type=%s "
                "target=%s error=%s",
                ticker, period_type.value, statement_type.value, target.value, e,
            )
            return AcquisitionResult(
                AcquisitionResultKind.STATE_TRANSITION_FAILED, state=previous, detail=f"{type(e).__name__}: {e}"
            )
        logger.info(
            "acquisition state transitioned ticker=%s period_type=%s statement_type=%s state=%s",
            ticker, period_type.value, statement_type.value, new_state.value,
        )
        return AcquisitionResult(AcquisitionResultKind.TRANSITIONED, state=new_state)
