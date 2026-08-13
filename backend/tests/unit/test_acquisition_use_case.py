"""Unit tests for application/financials.py::AcquireFinancialsUseCase (M8
Step 5 — Document 39 §18: "Build the acquire(identity) use case"). Hermetic:
repositories are the real Mongo adapters backed by a fake motor-shaped
collection (same fake as test_financials_persistence.py, duplicated locally
— no shared test-utils module exists yet for this), so AS-4's precedence
logic is exercised for real on repeated/back-to-back calls, not reimplemented
in a second test double. The provider is a plain injected async callable —
no yfinance/network call is ever made.

A note on the "same-identity" test group below: the fake collection's
find_one/update_one methods contain no internal `await` (no real I/O), so an
asyncio.gather() of multiple acquire() calls does not actually interleave —
the first scheduled task runs to completion before the next one starts. Those
tests are named and documented accordingly (same-identity *repeated*
invocation, not a genuine race) — the real interleaving/DuplicateKeyError
race guarantee is covered at the repository level in
test_financials_persistence.py's AS-4 tests, unchanged by this file.

    python backend/tests/unit/test_acquisition_use_case.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pymongo.errors import DuplicateKeyError

from agents.financials_provider import ProviderOutcome, ProviderOutcomeKind
from application.financials import AcquireFinancialsUseCase, AcquisitionResultKind
from domain.financials import AcquisitionOutcome, FinancialStatement, Metric, MetricUnit, PeriodType, StatementType
from infrastructure.mongo.acquisition_state import MongoAcquisitionStateRepository
from infrastructure.mongo.financial_statements import MongoFinancialStatementRepository


# --- hermetic fake Mongo (duplicated from test_financials_persistence.py) --


def _match(doc, filt):
    for k, v in filt.items():
        if isinstance(v, dict) and "$ne" in v:
            if doc.get(k) == v["$ne"]:
                return False
        elif doc.get(k) != v:
            return False
    return True


class _FakeCursor:
    def __init__(self, docs):
        self._docs = list(docs)

    def sort(self, key, direction):
        self._docs.sort(key=lambda d: d[key], reverse=(direction == -1))
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        for d in self._docs:
            yield d


class _FakeCollection:
    def __init__(self, unique_keys):
        self._docs: list[dict] = []
        self._unique_keys = unique_keys

    def find(self, filt, projection=None):
        return _FakeCursor([d for d in self._docs if _match(d, filt)])

    async def find_one(self, filt):
        for d in self._docs:
            if _match(d, filt):
                return d
        return None

    async def update_one(self, filt, update, upsert=False):
        for d in self._docs:
            if _match(d, filt):
                d.update(update.get("$set", {}))
                return
        if not upsert:
            return
        new_doc = {k: v for k, v in filt.items() if not isinstance(v, dict)}
        new_doc.update(update.get("$set", {}))
        key = tuple(new_doc.get(k) for k in self._unique_keys)
        if any(tuple(d.get(k) for k in self._unique_keys) == key for d in self._docs):
            raise DuplicateKeyError("E11000 duplicate key error collection")
        self._docs.append(new_doc)


class _FakeDB:
    def __init__(self):
        self._collections = {
            "financial_statements": _FakeCollection(("ticker", "period_type", "period_end", "statement_type")),
            "acquisition_states": _FakeCollection(("ticker", "period_type", "statement_type")),
        }

    def __getitem__(self, name):
        return self._collections[name]


class _FailingStatementRepo(MongoFinancialStatementRepository):
    async def upsert(self, statement):
        raise RuntimeError("mongo write failed")


class _FailingAcquisitionRepo(MongoAcquisitionStateRepository):
    async def write_terminal(self, *a, **kw):
        raise RuntimeError("mongo write failed")


# --- fixtures ---------------------------------------------------------------


def _use_case(db=None, statement_repo=None, acquisition_repo=None, provider=None):
    db = db if db is not None else _FakeDB()
    statement_repo = statement_repo or MongoFinancialStatementRepository(db)
    acquisition_repo = acquisition_repo or MongoAcquisitionStateRepository(db)
    kwargs = {}
    if provider is not None:
        kwargs["provider"] = provider
    return AcquireFinancialsUseCase(statement_repo, acquisition_repo, **kwargs), statement_repo, acquisition_repo, db


def _success_outcome():
    stmt = FinancialStatement(
        ticker="AAPL", period_type=PeriodType.ANNUAL, period_end="2025-09-30", fiscal_year="2025",
        statement_type=StatementType.INCOME, currency="USD", fetched_at="2026-08-13T00:00:00+00:00",
        metrics=[Metric(provider_label="Total Revenue", value=391_035_000_000.0, unit=MetricUnit.CURRENCY)],
    )
    return ProviderOutcome(ProviderOutcomeKind.SUCCESS, statements=[stmt])


def _provider_returning(outcome):
    async def _fn(ticker, period_type, statement_type):
        return outcome

    return _fn


def _counting_provider(outcome):
    calls = []

    async def _fn(ticker, period_type, statement_type):
        calls.append((ticker, period_type, statement_type))
        return outcome

    _fn.calls = calls
    return _fn


IDENTITY = ("AAPL", PeriodType.ANNUAL, StatementType.INCOME)


def _run(uc, identity=IDENTITY):
    return asyncio.run(uc.acquire(*identity))


async def _gather(*coros):
    # asyncio.gather() must be called from inside a running loop (3.10+) —
    # this wrapper lets callers pass already-created coroutine objects to
    # asyncio.run() without hitting "no current event loop".
    return await asyncio.gather(*coros)


# --- 1-4: not_yet_acquired -> each provider outcome -------------------------


def test_not_yet_acquired_success_transitions_to_available():
    uc, stmt_repo, acq_repo, _ = _use_case(provider=_provider_returning(_success_outcome()))
    result = _run(uc)
    assert result.kind == AcquisitionResultKind.TRANSITIONED
    assert result.state == AcquisitionOutcome.AVAILABLE


def test_not_yet_acquired_definitive_unavailable_transitions():
    uc, _, _, _ = _use_case(provider=_provider_returning(ProviderOutcome(ProviderOutcomeKind.DEFINITIVE_UNAVAILABLE)))
    result = _run(uc)
    assert result.kind == AcquisitionResultKind.TRANSITIONED
    assert result.state == AcquisitionOutcome.CONFIRMED_UNAVAILABLE


def test_not_yet_acquired_transient_failure_is_recoverable_and_unchanged():
    outcome = ProviderOutcome(ProviderOutcomeKind.TRANSIENT_FAILURE, detail="timeout")
    uc, _, _, _ = _use_case(provider=_provider_returning(outcome))
    result = _run(uc)
    assert result.kind == AcquisitionResultKind.RECOVERABLE_FAILURE
    assert result.state == AcquisitionOutcome.NOT_YET_ACQUIRED


def test_invalid_provider_response_is_recoverable_not_definitive():
    outcome = ProviderOutcome(ProviderOutcomeKind.INVALID_RESPONSE, detail="missing currency")
    uc, _, _, _ = _use_case(provider=_provider_returning(outcome))
    result = _run(uc)
    assert result.kind == AcquisitionResultKind.RECOVERABLE_FAILURE
    assert result.state == AcquisitionOutcome.NOT_YET_ACQUIRED


# --- 5-6: already-terminal short-circuit ------------------------------------


def test_already_available_skips_provider_call():
    db = _FakeDB()
    acq_repo = MongoAcquisitionStateRepository(db)
    asyncio.run(acq_repo.write_terminal(*IDENTITY, AcquisitionOutcome.AVAILABLE))
    provider = _counting_provider(_success_outcome())
    uc, _, _, _ = _use_case(db=db, provider=provider)

    result = _run(uc)
    assert result.kind == AcquisitionResultKind.ALREADY_TERMINAL
    assert result.state == AcquisitionOutcome.AVAILABLE
    assert provider.calls == []  # no unnecessary reacquisition


def test_already_confirmed_unavailable_skips_provider_call():
    db = _FakeDB()
    acq_repo = MongoAcquisitionStateRepository(db)
    asyncio.run(acq_repo.write_terminal(*IDENTITY, AcquisitionOutcome.CONFIRMED_UNAVAILABLE))
    provider = _counting_provider(_success_outcome())
    uc, _, _, _ = _use_case(db=db, provider=provider)

    result = _run(uc)
    assert result.kind == AcquisitionResultKind.ALREADY_TERMINAL
    assert result.state == AcquisitionOutcome.CONFIRMED_UNAVAILABLE
    assert provider.calls == []


# --- 7-9: persistence / state-transition failure -----------------------------


def test_successful_financial_statement_persistence():
    uc, stmt_repo, _, _ = _use_case(provider=_provider_returning(_success_outcome()))
    _run(uc)
    got = asyncio.run(stmt_repo.get("AAPL", PeriodType.ANNUAL))
    assert len(got) == 1
    assert got[0].metrics[0].provider_label == "Total Revenue"


def test_financial_statement_persistence_failure_leaves_state_unchanged():
    db = _FakeDB()
    uc, stmt_repo, acq_repo, _ = _use_case(
        db=db, statement_repo=_FailingStatementRepo(db), provider=_provider_returning(_success_outcome())
    )
    result = _run(uc)
    assert result.kind == AcquisitionResultKind.PERSISTENCE_FAILED
    assert result.state == AcquisitionOutcome.NOT_YET_ACQUIRED
    assert asyncio.run(acq_repo.get(*IDENTITY)) == AcquisitionOutcome.NOT_YET_ACQUIRED


def test_acquisition_state_transition_failure_leaves_statement_persisted_but_state_unchanged():
    # The AS-5 residual crash window (Document 35 §4/AS-5, Document 36 §20
    # scenario 7): FinancialStatement succeeds, the subsequent state write
    # fails — safe (never a false `available`), but non-converged.
    db = _FakeDB()
    uc, stmt_repo, _, _ = _use_case(
        db=db, acquisition_repo=_FailingAcquisitionRepo(db), provider=_provider_returning(_success_outcome())
    )
    result = _run(uc)
    assert result.kind == AcquisitionResultKind.STATE_TRANSITION_FAILED
    assert result.state == AcquisitionOutcome.NOT_YET_ACQUIRED
    assert len(asyncio.run(stmt_repo.get("AAPL", PeriodType.ANNUAL))) == 1  # persisted despite the failed transition


# --- 10: unexpected exception ------------------------------------------------


def test_unexpected_provider_exception_is_observable_not_fatal():
    async def _raise(ticker, period_type, statement_type):
        raise RuntimeError("provider contract violated")

    uc, _, _, _ = _use_case(provider=_raise)
    result = _run(uc)
    assert result.kind == AcquisitionResultKind.UNEXPECTED_ERROR
    assert result.state == AcquisitionOutcome.NOT_YET_ACQUIRED
    assert "RuntimeError" in result.detail


# --- idempotency --------------------------------------------------------------


def test_idempotent_repeated_request_after_available_does_not_recall_provider():
    provider = _counting_provider(_success_outcome())
    uc, _, _, _ = _use_case(provider=provider)
    first = _run(uc)
    second = _run(uc)
    assert first.kind == AcquisitionResultKind.TRANSITIONED
    assert second.kind == AcquisitionResultKind.ALREADY_TERMINAL
    assert len(provider.calls) == 1


def test_idempotent_repeated_request_after_confirmed_unavailable():
    provider = _counting_provider(ProviderOutcome(ProviderOutcomeKind.DEFINITIVE_UNAVAILABLE))
    uc, _, _, _ = _use_case(provider=provider)
    first = _run(uc)
    second = _run(uc)
    assert first.state == second.state == AcquisitionOutcome.CONFIRMED_UNAVAILABLE
    assert len(provider.calls) == 1


# --- same-identity repeated acquisitions (scheduled via asyncio.gather —
# see the module docstring: the fake collection has no internal await, so
# these run back-to-back, not genuinely interleaved; the real
# interleaving/DuplicateKeyError race guarantee is repository-level, in
# test_financials_persistence.py) ---------------------------------------------


def test_same_identity_repeated_acquisitions_produce_one_statement_and_available():
    db = _FakeDB()
    provider = _provider_returning(_success_outcome())
    uc1, stmt_repo, acq_repo, _ = _use_case(db=db, provider=provider)
    uc2, _, _, _ = _use_case(db=db, provider=provider)

    results = asyncio.run(_gather(uc1.acquire(*IDENTITY), uc2.acquire(*IDENTITY)))

    assert asyncio.run(acq_repo.get(*IDENTITY)) == AcquisitionOutcome.AVAILABLE
    assert len(asyncio.run(stmt_repo.get("AAPL", PeriodType.ANNUAL))) == 1  # not 2 — upsert-by-identity, no duplicate
    assert all(r.state == AcquisitionOutcome.AVAILABLE for r in results)


def test_same_identity_sequential_acquisitions_with_conflicting_outcomes_sticky_available_wins():
    # Document 35 AS-4: available is sticky regardless of write order. This
    # proves the use case's delegation to write_terminal() preserves that
    # guarantee end-to-end — the precedence rule itself is repository-level
    # (test_financials_persistence.py's AS-4 tests), unchanged here.
    db = _FakeDB()
    success_uc, _, acq_repo, _ = _use_case(db=db, provider=_provider_returning(_success_outcome()))
    unavailable_uc, _, _, _ = _use_case(
        db=db, provider=_provider_returning(ProviderOutcome(ProviderOutcomeKind.DEFINITIVE_UNAVAILABLE))
    )

    asyncio.run(_gather(success_uc.acquire(*IDENTITY), unavailable_uc.acquire(*IDENTITY)))

    assert asyncio.run(acq_repo.get(*IDENTITY)) == AcquisitionOutcome.AVAILABLE


def test_same_identity_five_repeated_acquisitions_converge_to_one_statement_and_available():
    db = _FakeDB()
    provider = _provider_returning(_success_outcome())
    use_cases = [_use_case(db=db, provider=provider)[0] for _ in range(5)]

    asyncio.run(_gather(*(uc.acquire(*IDENTITY) for uc in use_cases)))

    _, stmt_repo, acq_repo, _ = _use_case(db=db)
    assert asyncio.run(acq_repo.get(*IDENTITY)) == AcquisitionOutcome.AVAILABLE
    assert len(asyncio.run(stmt_repo.get("AAPL", PeriodType.ANNUAL))) == 1


# --- recovery ------------------------------------------------------------------


def test_recovery_after_transient_failure_a_later_call_succeeds():
    db = _FakeDB()
    transient = ProviderOutcome(ProviderOutcomeKind.TRANSIENT_FAILURE, detail="timeout")
    uc_fail, _, acq_repo, _ = _use_case(db=db, provider=_provider_returning(transient))
    first = _run(uc_fail)
    assert first.kind == AcquisitionResultKind.RECOVERABLE_FAILURE
    assert asyncio.run(acq_repo.get(*IDENTITY)) == AcquisitionOutcome.NOT_YET_ACQUIRED

    uc_retry, _, _, _ = _use_case(db=db, provider=_provider_returning(_success_outcome()))
    second = _run(uc_retry)
    assert second.kind == AcquisitionResultKind.TRANSITIONED
    assert second.state == AcquisitionOutcome.AVAILABLE


def test_recovery_after_persistence_failure_a_later_call_succeeds():
    db = _FakeDB()
    uc_fail, _, acq_repo, _ = _use_case(
        db=db, statement_repo=_FailingStatementRepo(db), provider=_provider_returning(_success_outcome())
    )
    first = _run(uc_fail)
    assert first.kind == AcquisitionResultKind.PERSISTENCE_FAILED
    assert asyncio.run(acq_repo.get(*IDENTITY)) == AcquisitionOutcome.NOT_YET_ACQUIRED

    uc_retry, stmt_repo, _, _ = _use_case(db=db, provider=_provider_returning(_success_outcome()))
    second = _run(uc_retry)
    assert second.kind == AcquisitionResultKind.TRANSITIONED
    assert second.state == AcquisitionOutcome.AVAILABLE
    assert len(asyncio.run(stmt_repo.get("AAPL", PeriodType.ANNUAL))) == 1


if __name__ == "__main__":
    test_not_yet_acquired_success_transitions_to_available()
    test_not_yet_acquired_definitive_unavailable_transitions()
    test_not_yet_acquired_transient_failure_is_recoverable_and_unchanged()
    test_invalid_provider_response_is_recoverable_not_definitive()
    test_already_available_skips_provider_call()
    test_already_confirmed_unavailable_skips_provider_call()
    test_successful_financial_statement_persistence()
    test_financial_statement_persistence_failure_leaves_state_unchanged()
    test_acquisition_state_transition_failure_leaves_statement_persisted_but_state_unchanged()
    test_unexpected_provider_exception_is_observable_not_fatal()
    test_idempotent_repeated_request_after_available_does_not_recall_provider()
    test_idempotent_repeated_request_after_confirmed_unavailable()
    test_same_identity_repeated_acquisitions_produce_one_statement_and_available()
    test_same_identity_sequential_acquisitions_with_conflicting_outcomes_sticky_available_wins()
    test_same_identity_five_repeated_acquisitions_converge_to_one_statement_and_available()
    test_recovery_after_transient_failure_a_later_call_succeeds()
    test_recovery_after_persistence_failure_a_later_call_succeeds()
    print("ok: AcquireFinancialsUseCase (M8 Step 5) — 10 outcome scenarios, idempotency, same-identity repeated "
          "invocation (AS-4 through the use case), recovery")
