"""Unit tests for the M8 Phase 1B Mongo adapters
(infrastructure/mongo/financial_statements.py, .../acquisition_state.py).

Hermetic: a small fake motor-shaped collection simulates unique-index
enforcement (DuplicateKeyError) and update_one's filter/upsert semantics
(including the `$ne` operator the acquisition-state adapter's conditional
write depends on) — matching test_mongo_infrastructure.py's existing
"fake motor double, no real server" convention. No mongomock dependency is
added (none exists in requirements.txt); this fake only implements the exact
operations the two adapters use.

    python backend/tests/unit/test_financials_persistence.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pymongo.errors import DuplicateKeyError

from domain.financials import AcquisitionOutcome, FinancialStatement, Metric, MetricUnit, PeriodType, StatementType
from infrastructure.mongo.acquisition_state import MongoAcquisitionStateRepository
from infrastructure.mongo.financial_statements import MongoFinancialStatementRepository


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
    """Simulates exactly what the two M8 adapters call: find, find_one,
    update_one(upsert=True) with unique-key enforcement on the insert
    branch — mirroring what a real unique compound index does."""

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


def _statement(period_end="2025-09-30", fetched_at="2026-08-13T00:00:00+00:00") -> FinancialStatement:
    return FinancialStatement(
        ticker="AAPL",
        period_type=PeriodType.ANNUAL,
        period_end=period_end,
        fiscal_year=period_end[:4],
        statement_type=StatementType.INCOME,
        currency="USD",
        fetched_at=fetched_at,
        metrics=[Metric(provider_label="Total Revenue", value=391_035_000_000.0, unit=MetricUnit.CURRENCY)],
    )


# --- FinancialStatementRepository -----------------------------------------


def test_financial_statement_write_and_read_back():
    repo = MongoFinancialStatementRepository(_FakeDB())
    asyncio.run(repo.upsert(_statement()))
    got = asyncio.run(repo.get("AAPL", PeriodType.ANNUAL))
    assert len(got) == 1
    assert got[0].period_end == "2025-09-30"
    assert got[0].metrics[0].provider_label == "Total Revenue"


def test_financial_statement_identity_uniqueness_upsert_in_place():
    # Restatement policy (ADR-029 §6.4): latest-value-wins, same identity
    # overwrites, never duplicates.
    repo = MongoFinancialStatementRepository(_FakeDB())
    asyncio.run(repo.upsert(_statement(fetched_at="2026-08-01T00:00:00+00:00")))
    revised = _statement(fetched_at="2026-08-13T00:00:00+00:00")
    revised.metrics[0].value = 400_000_000_000.0
    asyncio.run(repo.upsert(revised))

    got = asyncio.run(repo.get("AAPL", PeriodType.ANNUAL))
    assert len(got) == 1  # not 2 — same identity, overwritten
    assert got[0].metrics[0].value == 400_000_000_000.0
    assert got[0].fetched_at == "2026-08-13T00:00:00+00:00"


def test_financial_statement_upsert_normalizes_ticker_case():
    # CTO hardening fix: upsert() must normalize ticker identically to
    # get()'s ticker.upper() — otherwise a lowercase/mixed-case ticker
    # persists under an identity get() can never look up.
    repo = MongoFinancialStatementRepository(_FakeDB())
    stmt = _statement()
    stmt.ticker = "aapl"
    asyncio.run(repo.upsert(stmt))

    got = asyncio.run(repo.get("AAPL", PeriodType.ANNUAL))
    assert len(got) == 1
    assert got[0].ticker == "AAPL"


def test_financial_statement_freshness_none_then_latest():
    repo = MongoFinancialStatementRepository(_FakeDB())
    assert asyncio.run(repo.freshness("AAPL", PeriodType.ANNUAL)) is None

    asyncio.run(repo.upsert(_statement(period_end="2024-09-30", fetched_at="2026-08-01T00:00:00+00:00")))
    asyncio.run(repo.upsert(_statement(period_end="2025-09-30", fetched_at="2026-08-13T00:00:00+00:00")))
    assert asyncio.run(repo.freshness("AAPL", PeriodType.ANNUAL)) == "2026-08-13T00:00:00+00:00"


# --- AcquisitionStateRepository -------------------------------------------


def test_acquisition_state_defaults_to_not_yet_acquired():
    repo = MongoAcquisitionStateRepository(_FakeDB())
    state = asyncio.run(repo.get("AAPL", PeriodType.ANNUAL, StatementType.INCOME))
    assert state == AcquisitionOutcome.NOT_YET_ACQUIRED


def test_write_terminal_rejects_not_yet_acquired():
    repo = MongoAcquisitionStateRepository(_FakeDB())
    try:
        asyncio.run(
            repo.write_terminal("AAPL", PeriodType.ANNUAL, StatementType.INCOME, AcquisitionOutcome.NOT_YET_ACQUIRED)
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_write_terminal_available_persists_and_is_idempotent():
    repo = MongoAcquisitionStateRepository(_FakeDB())
    result1 = asyncio.run(
        repo.write_terminal("AAPL", PeriodType.ANNUAL, StatementType.INCOME, AcquisitionOutcome.AVAILABLE)
    )
    result2 = asyncio.run(
        repo.write_terminal("AAPL", PeriodType.ANNUAL, StatementType.INCOME, AcquisitionOutcome.AVAILABLE)
    )
    assert result1 == result2 == AcquisitionOutcome.AVAILABLE
    assert asyncio.run(repo.get("AAPL", PeriodType.ANNUAL, StatementType.INCOME)) == AcquisitionOutcome.AVAILABLE


def test_write_terminal_confirmed_unavailable_from_no_state():
    repo = MongoAcquisitionStateRepository(_FakeDB())
    result = asyncio.run(
        repo.write_terminal("AAPL", PeriodType.ANNUAL, StatementType.INCOME, AcquisitionOutcome.CONFIRMED_UNAVAILABLE)
    )
    assert result == AcquisitionOutcome.CONFIRMED_UNAVAILABLE


def test_as4_available_is_sticky_against_later_confirmed_unavailable():
    # Document 35 AS-4 Case A: available + later confirmed_unavailable -> available.
    repo = MongoAcquisitionStateRepository(_FakeDB())
    asyncio.run(repo.write_terminal("AAPL", PeriodType.ANNUAL, StatementType.INCOME, AcquisitionOutcome.AVAILABLE))
    result = asyncio.run(
        repo.write_terminal("AAPL", PeriodType.ANNUAL, StatementType.INCOME, AcquisitionOutcome.CONFIRMED_UNAVAILABLE)
    )
    assert result == AcquisitionOutcome.AVAILABLE
    assert asyncio.run(repo.get("AAPL", PeriodType.ANNUAL, StatementType.INCOME)) == AcquisitionOutcome.AVAILABLE


def test_as4_confirmed_unavailable_upgrades_to_available():
    # Document 35 AS-4 Case B: confirmed_unavailable + later available -> available.
    repo = MongoAcquisitionStateRepository(_FakeDB())
    asyncio.run(
        repo.write_terminal("AAPL", PeriodType.ANNUAL, StatementType.INCOME, AcquisitionOutcome.CONFIRMED_UNAVAILABLE)
    )
    result = asyncio.run(
        repo.write_terminal("AAPL", PeriodType.ANNUAL, StatementType.INCOME, AcquisitionOutcome.AVAILABLE)
    )
    assert result == AcquisitionOutcome.AVAILABLE


def test_acquisition_state_identity_is_independent_per_statement_type():
    repo = MongoAcquisitionStateRepository(_FakeDB())
    asyncio.run(repo.write_terminal("AAPL", PeriodType.ANNUAL, StatementType.INCOME, AcquisitionOutcome.AVAILABLE))
    asyncio.run(
        repo.write_terminal(
            "AAPL", PeriodType.ANNUAL, StatementType.CASH_FLOW, AcquisitionOutcome.CONFIRMED_UNAVAILABLE
        )
    )
    assert asyncio.run(repo.get("AAPL", PeriodType.ANNUAL, StatementType.INCOME)) == AcquisitionOutcome.AVAILABLE
    assert (
        asyncio.run(repo.get("AAPL", PeriodType.ANNUAL, StatementType.CASH_FLOW))
        == AcquisitionOutcome.CONFIRMED_UNAVAILABLE
    )
    assert asyncio.run(repo.get("AAPL", PeriodType.ANNUAL, StatementType.BALANCE_SHEET)) == (
        AcquisitionOutcome.NOT_YET_ACQUIRED
    )


if __name__ == "__main__":
    test_financial_statement_write_and_read_back()
    test_financial_statement_identity_uniqueness_upsert_in_place()
    test_financial_statement_upsert_normalizes_ticker_case()
    test_financial_statement_freshness_none_then_latest()
    test_acquisition_state_defaults_to_not_yet_acquired()
    test_write_terminal_rejects_not_yet_acquired()
    test_write_terminal_available_persists_and_is_idempotent()
    test_write_terminal_confirmed_unavailable_from_no_state()
    test_as4_available_is_sticky_against_later_confirmed_unavailable()
    test_as4_confirmed_unavailable_upgrades_to_available()
    test_acquisition_state_identity_is_independent_per_statement_type()
    print("ok: FinancialStatement upsert/uniqueness/freshness; AcquisitionState AS-4 precedence, idempotency, "
          "per-statement-type independence")
