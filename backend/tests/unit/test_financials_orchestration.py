"""Unit tests for application/financials_orchestration.py::
FinancialsAcquisitionOrchestrator (M8 Step 6 — Document 39 §18: "Wire the
use case into Document 36's existing, ratified triggers"). Hermetic: the
injected "use case" is a plain recording/raising double, not a real
AcquireFinancialsUseCase — these tests verify the orchestrator's own job
(scheduling, identity construction, not swallowing failures), not Step 5's
business rules, which are already covered by test_acquisition_use_case.py
and unchanged here.

`schedule()` calls `asyncio.create_task()` internally, which requires a
running event loop — true in its real call site (an async route handler,
e.g. server.py's `ensure_company`) and reproduced here by running each test
body as a coroutine via asyncio.run(), rather than calling `.schedule()`
from plain sync test functions.

    python backend/tests/unit/test_financials_orchestration.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from application.financials import AcquisitionResult, AcquisitionResultKind
from application.financials_orchestration import FinancialsAcquisitionOrchestrator
from domain.financials import AcquisitionOutcome, PeriodType, StatementType


class _RecordingUseCase:
    """Records every acquire() call — proves the orchestrator delegates
    with the correct identity and does not itself decide any outcome."""

    def __init__(self):
        self.calls: list[tuple[str, PeriodType, StatementType]] = []

    async def acquire(self, ticker, period_type, statement_type):
        self.calls.append((ticker, period_type, statement_type))
        return AcquisitionResult(AcquisitionResultKind.ALREADY_TERMINAL, state=AcquisitionOutcome.AVAILABLE)


class _RaisingUseCase:
    async def acquire(self, ticker, period_type, statement_type):
        raise RuntimeError("use case exploded")


class _ConcurrencyTrackingUseCase:
    """A deliberate, real await point (asyncio.sleep) — not "faking"
    concurrency (contrast with the Step 5 use-case tests, where a bare
    asyncio.gather over instantly-resolving fakes never truly interleaves).
    Here a genuine overlap window is the only way to observe whether the
    module's concurrency bound (_MAX_CONCURRENT_ACQUISITIONS) actually caps
    in-flight calls — this is what that primitive exists to be tested
    against, not an attempt to dress up sequential calls as concurrent."""

    def __init__(self, delay: float = 0.05):
        self._delay = delay
        self.in_flight = 0
        self.max_in_flight = 0

    async def acquire(self, ticker, period_type, statement_type):
        self.in_flight += 1
        self.max_in_flight = max(self.max_in_flight, self.in_flight)
        await asyncio.sleep(self._delay)
        self.in_flight -= 1
        return AcquisitionResult(AcquisitionResultKind.ALREADY_TERMINAL, state=AcquisitionOutcome.AVAILABLE)


def test_schedule_defaults_to_all_six_identities():
    use_case = _RecordingUseCase()
    orchestrator = FinancialsAcquisitionOrchestrator(use_case)

    async def _body():
        tasks = orchestrator.schedule("aapl")
        assert len(tasks) == 6
        await asyncio.gather(*tasks)

    asyncio.run(_body())
    identities = set(use_case.calls)
    assert identities == {("AAPL", pt, st) for pt in PeriodType for st in StatementType}


def test_schedule_ticker_is_normalized_uppercase():
    use_case = _RecordingUseCase()
    orchestrator = FinancialsAcquisitionOrchestrator(use_case)

    async def _body():
        tasks = orchestrator.schedule("aapl", statement_types=[StatementType.INCOME],
                                       period_types=[PeriodType.ANNUAL])
        await asyncio.gather(*tasks)

    asyncio.run(_body())
    assert use_case.calls == [("AAPL", PeriodType.ANNUAL, StatementType.INCOME)]


def test_schedule_respects_a_narrowed_subset():
    use_case = _RecordingUseCase()
    orchestrator = FinancialsAcquisitionOrchestrator(use_case)

    async def _body():
        tasks = orchestrator.schedule(
            "AAPL", period_types=[PeriodType.QUARTERLY], statement_types=[StatementType.CASH_FLOW]
        )
        assert len(tasks) == 1
        await asyncio.gather(*tasks)

    asyncio.run(_body())
    assert use_case.calls == [("AAPL", PeriodType.QUARTERLY, StatementType.CASH_FLOW)]


def test_schedule_does_not_duplicate_business_logic():
    # The orchestrator never inspects or branches on the use case's result —
    # it only schedules the call and returns the Task. Proven here by using
    # a use case double that always returns ALREADY_TERMINAL/AVAILABLE
    # regardless of identity, and confirming the orchestrator does nothing
    # beyond scheduling (no state written, no classification performed —
    # there is nothing in this module capable of doing either).
    use_case = _RecordingUseCase()
    orchestrator = FinancialsAcquisitionOrchestrator(use_case)

    async def _body():
        tasks = orchestrator.schedule("AAPL", period_types=[PeriodType.ANNUAL], statement_types=[StatementType.INCOME])
        return await asyncio.gather(*tasks)

    results = asyncio.run(_body())
    assert results == [AcquisitionResult(AcquisitionResultKind.ALREADY_TERMINAL, state=AcquisitionOutcome.AVAILABLE)]


def test_schedule_returns_immediately_without_awaiting_the_use_case():
    # schedule() itself must never block on acquire() completing — it's a
    # synchronous method that only calls asyncio.create_task().
    use_case = _RecordingUseCase()
    orchestrator = FinancialsAcquisitionOrchestrator(use_case)
    calls_immediately_after_schedule = []

    async def _body():
        tasks = orchestrator.schedule(
            "AAPL", period_types=[PeriodType.ANNUAL], statement_types=[StatementType.INCOME]
        )
        # Nothing has run yet — schedule() returned before the event loop
        # ever got a chance to execute the scheduled coroutine.
        calls_immediately_after_schedule.append(len(use_case.calls))
        await asyncio.gather(*tasks)

    asyncio.run(_body())
    assert calls_immediately_after_schedule == [0]
    assert len(use_case.calls) == 1


def test_unexpected_use_case_failure_is_not_silently_swallowed():
    # AcquireFinancialsUseCase never raises (Step 5, frozen) — but this
    # module must not hide a violation of that contract either: the
    # exception must remain retrievable on the Task, not swallowed.
    orchestrator = FinancialsAcquisitionOrchestrator(_RaisingUseCase())

    async def _body():
        tasks = orchestrator.schedule(
            "AAPL", period_types=[PeriodType.ANNUAL], statement_types=[StatementType.INCOME]
        )
        return await asyncio.gather(*tasks, return_exceptions=True)

    results = asyncio.run(_body())
    assert len(results) == 1
    assert isinstance(results[0], RuntimeError)


def test_concurrent_acquisitions_are_bounded():
    # Discovered live (not hypothetical): scheduling identities fully
    # unbounded exhausted the shared asyncio.to_thread default executor and
    # starved unrelated requests under real load. This asserts the fix —
    # module-level _MAX_CONCURRENT_ACQUISITIONS is actually enforced across
    # every task this orchestrator schedules, from two separate calls (two
    # tickers), not just within a single schedule() call.
    from application.financials_orchestration import _MAX_CONCURRENT_ACQUISITIONS

    use_case = _ConcurrencyTrackingUseCase(delay=0.05)
    orchestrator = FinancialsAcquisitionOrchestrator(use_case)

    async def _body():
        tasks = orchestrator.schedule("AAPL") + orchestrator.schedule("MSFT")
        await asyncio.gather(*tasks)

    asyncio.run(_body())
    assert use_case.max_in_flight <= _MAX_CONCURRENT_ACQUISITIONS
    assert use_case.max_in_flight > 1  # sanity: overlap genuinely occurred, this isn't accidentally serial


if __name__ == "__main__":
    test_schedule_defaults_to_all_six_identities()
    test_schedule_ticker_is_normalized_uppercase()
    test_schedule_respects_a_narrowed_subset()
    test_schedule_does_not_duplicate_business_logic()
    test_schedule_returns_immediately_without_awaiting_the_use_case()
    test_unexpected_use_case_failure_is_not_silently_swallowed()
    test_concurrent_acquisitions_are_bounded()
    print("ok: FinancialsAcquisitionOrchestrator — identity construction, ticker normalization, subset scheduling, "
          "no duplicated business logic, fire-and-forget non-blocking, failures not swallowed, concurrency bounded")
