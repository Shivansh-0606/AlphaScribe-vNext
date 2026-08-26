"""API/contract tests for GET /companies/{ticker}/financials (M12 —
Document 33 §1-§10, CTO-ratified Round 7; Document 55 §3.1, CTO-ratified;
M12 Implementation Authorization, 2026-08-24). Hermetic: TestClient drives
the real ASGI stack (real route, real FastAPI validation, real
domain_error_handler -> HTTP status mapping) with `server.container`
swapped to fake FinancialStatementRepository/AcquisitionStateRepository
instances implementing the port shape directly. Unlike
test_financials_acquire_endpoint.py (which fakes Mongo underneath the real
MongoAcquisitionStateRepository specifically to exercise AS-4 precedence),
`.get()` on both ports here is a plain read with no precedence logic to
preserve fidelity on, so a direct port fake is sufficient and simpler.

    python -m pytest backend/tests/unit/test_financials_get_endpoint.py -v
"""
import dataclasses
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from fastapi.testclient import TestClient  # noqa: E402

from domain.financials import (  # noqa: E402
    AcquisitionOutcome,
    FinancialStatement,
    Metric,
    MetricUnit,
    PeriodType,
    StatementType,
)
import server  # noqa: E402

USER = {"id": "get-financials-user", "email": "getfin@example.com"}


class _FakeStatementRepo:
    def __init__(self, statements):
        self._statements = statements

    async def get(self, ticker, period_type):
        return [s for s in self._statements if s.ticker == ticker and s.period_type == period_type]

    async def upsert(self, statement):
        raise NotImplementedError

    async def freshness(self, ticker, period_type):
        raise NotImplementedError


class _FakeAcquisitionStates:
    def __init__(self, states):
        self._states = states  # {(ticker, period_type, statement_type): AcquisitionOutcome}

    async def get(self, ticker, period_type, statement_type):
        return self._states.get((ticker, period_type, statement_type), AcquisitionOutcome.NOT_YET_ACQUIRED)

    async def write_terminal(self, *a, **kw):
        raise NotImplementedError


class _RaisingStatementRepo:
    async def get(self, ticker, period_type):
        raise ConnectionError("mongo unreachable")

    async def upsert(self, statement):
        raise NotImplementedError

    async def freshness(self, ticker, period_type):
        raise NotImplementedError


TICKER_COUNTER = iter(range(10_000))


def _unique_ticker() -> str:
    return f"G{next(TICKER_COUNTER)}"


def _swap_container(financial_statements=None, acquisition_states=None):
    kwargs = {}
    if financial_statements is not None:
        kwargs["financial_statements"] = financial_statements
    if acquisition_states is not None:
        kwargs["acquisition_states"] = acquisition_states
    return dataclasses.replace(server.container, **kwargs)


server.app.dependency_overrides[server.current_user] = lambda: USER
client = TestClient(server.app)


def _metric(**kw):
    defaults = dict(canonical_metric=None, provider_label="Total Revenue", value=100.0, unit=MetricUnit.CURRENCY)
    defaults.update(kw)
    return Metric(**defaults)


def _statement(ticker, period_type, statement_type, period_end, **kw):
    defaults = dict(
        ticker=ticker, period_type=period_type, period_end=period_end, fiscal_year=period_end[:4],
        statement_type=statement_type, currency="USD", source="yfinance",
        fetched_at="2026-08-10T09:00:00Z", metrics=[_metric()],
    )
    defaults.update(kw)
    return FinancialStatement(**defaults)


# --- validation / auth --------------------------------------------------------


def test_missing_period_type_returns_422():
    ticker = _unique_ticker()
    r = client.get(f"/api/companies/{ticker}/financials")
    assert r.status_code == 422


def test_invalid_period_type_returns_422():
    ticker = _unique_ticker()
    r = client.get(f"/api/companies/{ticker}/financials", params={"period_type": "yearly"})
    assert r.status_code == 422


def test_unauthenticated_request_returns_401():
    del server.app.dependency_overrides[server.current_user]
    try:
        ticker = _unique_ticker()
        r = client.get(f"/api/companies/{ticker}/financials", params={"period_type": "annual"})
        assert r.status_code == 401
    finally:
        server.app.dependency_overrides[server.current_user] = lambda: USER


# --- response shape + acquisition-state semantics -----------------------------


def test_unknown_ticker_returns_200_not_yet_acquired():
    # Document 33 §5 row 5 — unknown/unseen ticker is 200, not 404; acquisition
    # state comes from the canonical acquisition-state source (§4), never
    # inferred from FinancialStatement absence.
    ticker = _unique_ticker()
    original = server.container
    server.container = _swap_container(
        financial_statements=_FakeStatementRepo([]), acquisition_states=_FakeAcquisitionStates({})
    )
    try:
        r = client.get(f"/api/companies/{ticker}/financials", params={"period_type": "annual"})
    finally:
        server.container = original
    assert r.status_code == 200
    body = r.json()
    assert body["ticker"] == ticker
    assert body["period_type"] == "annual"
    for st in ("income", "balance_sheet", "cash_flow"):
        assert body["statements"][st] == {"acquisition_state": "not_yet_acquired", "periods": []}


def test_available_statement_returns_populated_periods_in_envelope_shape():
    ticker = _unique_ticker()
    stmt = _statement(ticker, PeriodType.ANNUAL, StatementType.INCOME, "2025-09-30")
    original = server.container
    server.container = _swap_container(
        financial_statements=_FakeStatementRepo([stmt]),
        acquisition_states=_FakeAcquisitionStates(
            {(ticker, PeriodType.ANNUAL, StatementType.INCOME): AcquisitionOutcome.AVAILABLE}
        ),
    )
    try:
        r = client.get(f"/api/companies/{ticker}/financials", params={"period_type": "annual"})
    finally:
        server.container = original
    assert r.status_code == 200
    income = r.json()["statements"]["income"]
    assert income["acquisition_state"] == "available"
    assert len(income["periods"]) == 1
    period = income["periods"][0]
    assert set(period.keys()) == {"period_end", "fiscal_year", "currency", "source", "fetched_at", "metrics"}
    assert period["period_end"] == "2025-09-30"
    assert period["metrics"] == [
        {"canonical_metric": None, "provider_label": "Total Revenue", "value": 100.0, "unit": "currency"}
    ]


def test_confirmed_unavailable_statement_has_empty_periods():
    ticker = _unique_ticker()
    original = server.container
    server.container = _swap_container(
        financial_statements=_FakeStatementRepo([]),
        acquisition_states=_FakeAcquisitionStates(
            {(ticker, PeriodType.QUARTERLY, StatementType.CASH_FLOW): AcquisitionOutcome.CONFIRMED_UNAVAILABLE}
        ),
    )
    try:
        r = client.get(f"/api/companies/{ticker}/financials", params={"period_type": "quarterly"})
    finally:
        server.container = original
    cash_flow = r.json()["statements"]["cash_flow"]
    assert cash_flow == {"acquisition_state": "confirmed_unavailable", "periods": []}


# --- ordering (Document 33 §6.2, Round 6/7) -----------------------------------


def test_periods_ordered_by_period_end_descending():
    ticker = _unique_ticker()
    statements = [
        _statement(ticker, PeriodType.ANNUAL, StatementType.INCOME, "2023-09-30"),
        _statement(ticker, PeriodType.ANNUAL, StatementType.INCOME, "2025-09-30"),
        _statement(ticker, PeriodType.ANNUAL, StatementType.INCOME, "2024-09-30"),
    ]
    original = server.container
    server.container = _swap_container(
        financial_statements=_FakeStatementRepo(statements),
        acquisition_states=_FakeAcquisitionStates(
            {(ticker, PeriodType.ANNUAL, StatementType.INCOME): AcquisitionOutcome.AVAILABLE}
        ),
    )
    try:
        r = client.get(f"/api/companies/{ticker}/financials", params={"period_type": "annual"})
    finally:
        server.container = original
    period_ends = [p["period_end"] for p in r.json()["statements"]["income"]["periods"]]
    assert period_ends == ["2025-09-30", "2024-09-30", "2023-09-30"]


def test_ordering_applies_identically_to_quarterly():
    ticker = _unique_ticker()
    statements = [
        _statement(ticker, PeriodType.QUARTERLY, StatementType.BALANCE_SHEET, "2026-03-31"),
        _statement(ticker, PeriodType.QUARTERLY, StatementType.BALANCE_SHEET, "2026-06-30"),
    ]
    original = server.container
    server.container = _swap_container(
        financial_statements=_FakeStatementRepo(statements),
        acquisition_states=_FakeAcquisitionStates(
            {(ticker, PeriodType.QUARTERLY, StatementType.BALANCE_SHEET): AcquisitionOutcome.AVAILABLE}
        ),
    )
    try:
        r = client.get(f"/api/companies/{ticker}/financials", params={"period_type": "quarterly"})
    finally:
        server.container = original
    period_ends = [p["period_end"] for p in r.json()["statements"]["balance_sheet"]["periods"]]
    assert period_ends == ["2026-06-30", "2026-03-31"]


# --- period_type isolation (Document 55 §3.5) ---------------------------------


def test_annual_and_quarterly_never_mixed():
    ticker = _unique_ticker()
    statements = [
        _statement(ticker, PeriodType.ANNUAL, StatementType.INCOME, "2025-09-30"),
        _statement(ticker, PeriodType.QUARTERLY, StatementType.INCOME, "2026-06-30"),
    ]
    original = server.container
    server.container = _swap_container(
        financial_statements=_FakeStatementRepo(statements),
        acquisition_states=_FakeAcquisitionStates({
            (ticker, PeriodType.ANNUAL, StatementType.INCOME): AcquisitionOutcome.AVAILABLE,
            (ticker, PeriodType.QUARTERLY, StatementType.INCOME): AcquisitionOutcome.AVAILABLE,
        }),
    )
    try:
        r = client.get(f"/api/companies/{ticker}/financials", params={"period_type": "annual"})
    finally:
        server.container = original
    periods = r.json()["statements"]["income"]["periods"]
    assert len(periods) == 1
    assert periods[0]["period_end"] == "2025-09-30"


# --- error handling ------------------------------------------------------------


def test_synchronous_infrastructure_failure_returns_502_and_no_internal_detail():
    ticker = _unique_ticker()
    original = server.container
    server.container = _swap_container(financial_statements=_RaisingStatementRepo())
    try:
        r = client.get(f"/api/companies/{ticker}/financials", params={"period_type": "annual"})
        assert r.status_code == 502
        assert "mongo unreachable" not in r.text.lower()
    finally:
        server.container = original


if __name__ == "__main__":
    test_missing_period_type_returns_422()
    test_invalid_period_type_returns_422()
    test_unauthenticated_request_returns_401()
    test_unknown_ticker_returns_200_not_yet_acquired()
    test_available_statement_returns_populated_periods_in_envelope_shape()
    test_confirmed_unavailable_statement_has_empty_periods()
    test_periods_ordered_by_period_end_descending()
    test_ordering_applies_identically_to_quarterly()
    test_annual_and_quarterly_never_mixed()
    test_synchronous_infrastructure_failure_returns_502_and_no_internal_detail()
    print("ok: GET /financials -- response envelope shape, 3-state acquisition_state, "
          "period_end-descending ordering (annual+quarterly), period_type isolation, 401/422/502")
