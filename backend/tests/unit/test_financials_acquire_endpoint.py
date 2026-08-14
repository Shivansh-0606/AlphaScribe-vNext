"""API/contract tests for POST /companies/{ticker}/financials/acquire (M8
Step 7 — Document 33 Amendment §1-§17, frozen). Hermetic: TestClient drives
the real ASGI stack (real route, real FastAPI validation, real
domain_error_handler → HTTP status mapping) — the same technique
test_ingest_pdf_route.py already uses for a login-walled route — with
`server.container` swapped to real repository/orchestrator instances backed
by a fake motor-shaped collection (same fake as test_financials_persistence.py
and friends), so AcquisitionState precedence is read through the real
repository port, not reimplemented in the test.

    python -m pytest backend/tests/unit/test_financials_acquire_endpoint.py -v
"""
import asyncio
import dataclasses
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("DB_NAME", "alphascribe_unit_test")

from fastapi.testclient import TestClient  # noqa: E402
from pymongo.errors import DuplicateKeyError  # noqa: E402

from agents import auth  # noqa: E402
from domain.errors import InfrastructureError  # noqa: E402
from domain.financials import AcquisitionOutcome, PeriodType, StatementType  # noqa: E402
from infrastructure.mongo.acquisition_state import MongoAcquisitionStateRepository  # noqa: E402
import server  # noqa: E402

USER = {"id": "acquire-endpoint-user", "email": "acquire@example.com"}


# --- hermetic fake Mongo (same shape as test_financials_persistence.py) ----


def _match(doc, filt):
    for k, v in filt.items():
        if isinstance(v, dict) and "$ne" in v:
            if doc.get(k) == v["$ne"]:
                return False
        elif doc.get(k) != v:
            return False
    return True


class _FakeCollection:
    def __init__(self, unique_keys):
        self._docs: list[dict] = []
        self._unique_keys = unique_keys

    def find(self, filt, projection=None):
        raise NotImplementedError

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
        self._collections = {"acquisition_states": _FakeCollection(("ticker", "period_type", "statement_type"))}

    def __getitem__(self, name):
        return self._collections[name]


class _RecordingOrchestrator:
    """Records schedule() calls instead of doing real background work — the
    endpoint's own job is what's under test here, not Step 6's scheduling
    mechanics (already covered by test_financials_orchestration.py)."""

    def __init__(self):
        self.calls = []

    def schedule(self, ticker, *, period_types, statement_types, trigger):
        self.calls.append((ticker, tuple(period_types), tuple(statement_types), trigger))
        return []


class _RaisingAcquisitionStates:
    async def get(self, ticker, period_type, statement_type):
        raise ConnectionError("mongo unreachable")

    async def write_terminal(self, *a, **kw):
        raise ConnectionError("mongo unreachable")


TICKER_COUNTER = iter(range(10_000))


def _unique_ticker() -> str:
    return f"T{next(TICKER_COUNTER)}"


def _swap_container(acquisition_states=None, financials_orchestrator=None):
    kwargs = {}
    if acquisition_states is not None:
        kwargs["acquisition_states"] = acquisition_states
    if financials_orchestrator is not None:
        kwargs["financials_orchestrator"] = financials_orchestrator
    return dataclasses.replace(server.container, **kwargs)


server.app.dependency_overrides[server.current_user] = lambda: USER
client = TestClient(server.app)


# --- response shape + valid requests ----------------------------------------


def test_valid_annual_request_response_shape_is_exact():
    ticker = _unique_ticker()
    orchestrator = _RecordingOrchestrator()
    repo = MongoAcquisitionStateRepository(_FakeDB())
    original = server.container
    server.container = _swap_container(acquisition_states=repo, financials_orchestrator=orchestrator)
    try:
        r = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
        assert r.status_code == 200
        body = r.json()
        assert set(body.keys()) == {"ticker", "period_type", "outcome"}
        assert body["ticker"] == ticker
        assert body["period_type"] == "annual"
        assert body["outcome"] == "requested"
    finally:
        server.container = original


def test_valid_quarterly_request_accepted():
    ticker = _unique_ticker()
    orchestrator = _RecordingOrchestrator()
    repo = MongoAcquisitionStateRepository(_FakeDB())
    original = server.container
    server.container = _swap_container(acquisition_states=repo, financials_orchestrator=orchestrator)
    try:
        r = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "quarterly"})
        assert r.status_code == 200
        assert r.json()["period_type"] == "quarterly"
    finally:
        server.container = original


# --- outcome + precedence ----------------------------------------------------


def _run_with_states(ticker, states: dict):
    db = _FakeDB()
    repo = MongoAcquisitionStateRepository(db)
    for st, outcome in states.items():
        asyncio.run(repo.write_terminal(ticker, PeriodType.ANNUAL, st, outcome))
    orchestrator = _RecordingOrchestrator()
    original = server.container
    server.container = _swap_container(acquisition_states=repo, financials_orchestrator=orchestrator)
    try:
        r = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
    finally:
        server.container = original
    return r, orchestrator


def test_outcome_requested_when_nothing_acquired():
    ticker = _unique_ticker()
    r, orch = _run_with_states(ticker, {})
    assert r.json()["outcome"] == "requested"
    assert len(orch.calls) == 1
    _, period_types, statement_types, trigger = orch.calls[0]
    assert set(statement_types) == set(StatementType)  # all three, none acquired yet
    assert trigger == "acquire_endpoint"


def test_outcome_available_when_all_available():
    ticker = _unique_ticker()
    r, orch = _run_with_states(ticker, {st: AcquisitionOutcome.AVAILABLE for st in StatementType})
    assert r.json()["outcome"] == "available"
    assert orch.calls == []  # nothing re-scheduled


def test_outcome_confirmed_unavailable_when_all_confirmed_unavailable():
    ticker = _unique_ticker()
    r, orch = _run_with_states(ticker, {st: AcquisitionOutcome.CONFIRMED_UNAVAILABLE for st in StatementType})
    assert r.json()["outcome"] == "confirmed_unavailable"
    assert orch.calls == []


def test_outcome_mixed_when_available_and_confirmed_unavailable_combine():
    ticker = _unique_ticker()
    r, orch = _run_with_states(ticker, {
        StatementType.INCOME: AcquisitionOutcome.AVAILABLE,
        StatementType.BALANCE_SHEET: AcquisitionOutcome.CONFIRMED_UNAVAILABLE,
        StatementType.CASH_FLOW: AcquisitionOutcome.AVAILABLE,
    })
    assert r.json()["outcome"] == "mixed"
    assert orch.calls == []


def test_precedence_any_not_yet_acquired_wins_over_terminal_states():
    # Document 33 Amendment §6 rule 1: requested takes precedence over
    # every other case, and only the not_yet_acquired identity is scheduled.
    ticker = _unique_ticker()
    r, orch = _run_with_states(ticker, {
        StatementType.INCOME: AcquisitionOutcome.AVAILABLE,
        StatementType.CASH_FLOW: AcquisitionOutcome.CONFIRMED_UNAVAILABLE,
        # balance_sheet omitted -> not_yet_acquired
    })
    assert r.json()["outcome"] == "requested"
    assert len(orch.calls) == 1
    _, _, statement_types, _ = orch.calls[0]
    assert set(statement_types) == {StatementType.BALANCE_SHEET}  # only the not-yet one


# --- error tests --------------------------------------------------------------


def test_missing_period_type_returns_422():
    ticker = _unique_ticker()
    r = client.post(f"/api/companies/{ticker}/financials/acquire")
    assert r.status_code == 422


def test_invalid_period_type_returns_422():
    ticker = _unique_ticker()
    r = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "yearly"})
    assert r.status_code == 422


def test_empty_ticker_returns_422():
    # Not reachable via TestClient (an empty path segment doesn't route to
    # {ticker}) — the ValidationError path is exercised directly instead.
    async def _body():
        try:
            await server.acquire_financials("   ", PeriodType.ANNUAL, user=USER)
        except Exception as e:
            return e
        return None

    from domain.errors import ValidationError

    exc = asyncio.run(_body())
    assert isinstance(exc, ValidationError)
    assert exc.status_code == 422


def test_unauthenticated_request_returns_401():
    del server.app.dependency_overrides[server.current_user]
    try:
        ticker = _unique_ticker()
        r = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
        assert r.status_code == 401
    finally:
        server.app.dependency_overrides[server.current_user] = lambda: USER


def test_rate_limited_request_returns_429():
    ticker = _unique_ticker()
    orchestrator = _RecordingOrchestrator()
    repo = MongoAcquisitionStateRepository(_FakeDB())
    original = server.container
    server.container = _swap_container(acquisition_states=repo, financials_orchestrator=orchestrator)
    key = f"acquire:{USER['id']}:{ticker}:annual"
    try:
        for _ in range(auth._RATE_LIMIT_MAX):
            r = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
            assert r.status_code == 200
        r = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
        assert r.status_code == 429
    finally:
        server.container = original
        auth.clear_hits(key)


def test_synchronous_infrastructure_failure_returns_502_and_no_internal_detail():
    ticker = _unique_ticker()
    original = server.container
    server.container = _swap_container(acquisition_states=_RaisingAcquisitionStates())
    try:
        r = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
        assert r.status_code == 502
        assert "mongo unreachable" not in r.text.lower()  # raw exception text never leaked
    finally:
        server.container = original


# --- authorization (no ownership dimension, per the frozen contract) --------


def test_two_different_authenticated_users_both_get_served_same_ticker():
    ticker = _unique_ticker()
    orchestrator = _RecordingOrchestrator()
    repo = MongoAcquisitionStateRepository(_FakeDB())
    original = server.container
    server.container = _swap_container(acquisition_states=repo, financials_orchestrator=orchestrator)
    try:
        server.app.dependency_overrides[server.current_user] = lambda: {"id": "user-a"}
        r1 = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
        server.app.dependency_overrides[server.current_user] = lambda: {"id": "user-b"}
        r2 = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
        assert r1.status_code == 200
        assert r2.status_code == 200  # no cross-tenant rejection — shared corpus, no ownership dimension
    finally:
        server.container = original
        server.app.dependency_overrides[server.current_user] = lambda: USER
        auth.clear_hits(f"acquire:user-a:{ticker}:annual")
        auth.clear_hits(f"acquire:user-b:{ticker}:annual")


# --- idempotency / repeat request -------------------------------------------


def test_repeat_request_after_available_does_not_reschedule():
    # Document 33 Amendment §10: "no new attempt is scheduled" once
    # available — the endpoint must not introduce a second idempotency
    # model beyond what Step 5/6 already guarantee. Same repo/orchestrator
    # across both calls, so a wrongly-reissued schedule() would show up.
    ticker = _unique_ticker()
    db = _FakeDB()
    repo = MongoAcquisitionStateRepository(db)
    for st in StatementType:
        asyncio.run(repo.write_terminal(ticker, PeriodType.ANNUAL, st, AcquisitionOutcome.AVAILABLE))
    orchestrator = _RecordingOrchestrator()

    original = server.container
    server.container = _swap_container(acquisition_states=repo, financials_orchestrator=orchestrator)
    try:
        r1 = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
        r2 = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
    finally:
        server.container = original
        auth.clear_hits(f"acquire:{USER['id']}:{ticker}:annual")

    assert r1.json()["outcome"] == "available"
    assert r2.json()["outcome"] == "available"
    assert orchestrator.calls == []


def test_repeat_request_after_confirmed_unavailable_does_not_reschedule():
    ticker = _unique_ticker()
    db = _FakeDB()
    repo = MongoAcquisitionStateRepository(db)
    for st in StatementType:
        asyncio.run(repo.write_terminal(ticker, PeriodType.ANNUAL, st, AcquisitionOutcome.CONFIRMED_UNAVAILABLE))
    orchestrator = _RecordingOrchestrator()

    original = server.container
    server.container = _swap_container(acquisition_states=repo, financials_orchestrator=orchestrator)
    try:
        r1 = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
        r2 = client.post(f"/api/companies/{ticker}/financials/acquire", params={"period_type": "annual"})
    finally:
        server.container = original
        auth.clear_hits(f"acquire:{USER['id']}:{ticker}:annual")

    assert r1.json()["outcome"] == "confirmed_unavailable"
    assert r2.json()["outcome"] == "confirmed_unavailable"
    assert orchestrator.calls == []


if __name__ == "__main__":
    test_valid_annual_request_response_shape_is_exact()
    test_valid_quarterly_request_accepted()
    test_outcome_requested_when_nothing_acquired()
    test_outcome_available_when_all_available()
    test_outcome_confirmed_unavailable_when_all_confirmed_unavailable()
    test_outcome_mixed_when_available_and_confirmed_unavailable_combine()
    test_precedence_any_not_yet_acquired_wins_over_terminal_states()
    test_missing_period_type_returns_422()
    test_invalid_period_type_returns_422()
    test_empty_ticker_returns_422()
    test_unauthenticated_request_returns_401()
    test_rate_limited_request_returns_429()
    test_synchronous_infrastructure_failure_returns_502_and_no_internal_detail()
    test_two_different_authenticated_users_both_get_served_same_ticker()
    test_repeat_request_after_available_does_not_reschedule()
    test_repeat_request_after_confirmed_unavailable_does_not_reschedule()
    print("ok: POST /financials/acquire — response shape, all 4 outcomes + precedence, "
          "401/422/429/502, no ownership dimension, idempotent repeat requests")
