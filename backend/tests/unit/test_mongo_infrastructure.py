"""Unit check for infrastructure/mongo/{client,indexes}.py.

Hermetic: a fake motor-shaped db records create_index() calls instead of
hitting a real server, so this runs with no Mongo available. The real thing
was additionally verified against this repo's actual live dev database
during Phase 1 (docs/backend_engineering/14 Test Report) — 25/25 indexes
applied, idempotent on a second run, and `explain()` confirmed IXSCAN
(not COLLSCAN) on both hot-path queries against 128 real users / 2,364 real
filing_chunks documents. That real-data proof isn't repeatable in hermetic
CI (08 §5.5 — indexes are created from application startup, not a fixture);
what IS repeatable and belongs here is the *shape* of what ensure_indexes
asks for: exactly the 25 rows in 08 §5.1, idempotently.

    python backend/tests/unit/test_mongo_infrastructure.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pymongo.errors import OperationFailure

from infrastructure.mongo.client import ping
from infrastructure.mongo.indexes import ensure_indexes


class _FakeCollection:
    def __init__(self, name, calls, conflict_names):
        self._name = name
        self._calls = calls
        self._conflict_names = conflict_names

    async def create_index(self, keys, **kwargs):
        self._calls.append((self._name, keys, kwargs))
        name = kwargs.get("name")
        if name in self._conflict_names:
            raise OperationFailure("Index already exists with a different name", code=85)
        return name


class _FakeDB:
    """Records every create_index() call; `conflict_names` simulates the
    real pre-existing-index-under-a-different-name case found in Phase 1."""

    def __init__(self, conflict_names=frozenset()):
        self.calls = []
        self._conflict_names = conflict_names

    def __getitem__(self, name):
        return _FakeCollection(name, self.calls, self._conflict_names)

    async def command(self, name):
        if name == "ping":
            return {"ok": 1.0}
        raise NotImplementedError(name)


def test_ping_returns_true_on_success():
    assert asyncio.run(ping(_FakeDB())) is True


def test_ping_raises_infrastructure_error_on_failure():
    from domain.errors import InfrastructureError

    class _BrokenDB(_FakeDB):
        async def command(self, name):
            raise ConnectionError("no route to host")

    try:
        asyncio.run(ping(_BrokenDB()))
    except InfrastructureError as e:
        assert e.code == "mongo_unreachable"
    else:
        raise AssertionError("expected InfrastructureError")


def test_ensure_indexes_creates_exactly_the_25_row_set():
    db = _FakeDB()
    created = asyncio.run(ensure_indexes(db))

    names = [n for coll in created.values() for n in coll]
    ids = {n.split("_", 1)[0] for n in names}
    expected_ids = {f"I-{i}" for i in range(1, 26)}
    assert ids == expected_ids, f"missing or extra rows: {expected_ids ^ ids}"
    assert sum(len(v) for v in created.values()) == 25


def test_ensure_indexes_is_idempotent_across_two_runs():
    db = _FakeDB()
    first = asyncio.run(ensure_indexes(db))
    second = asyncio.run(ensure_indexes(db))
    assert first == second


def test_ensure_indexes_tolerates_a_pre_existing_differently_named_index():
    # Exactly the real conflict found in Phase 1: I-1/I-3/I-4/I-6/I-7 already
    # exist under pymongo's auto-generated names from agents/auth.py's
    # original ensure_indexes().
    db = _FakeDB(conflict_names={"I-1_email_unique", "I-3_token_hash_unique"})
    created = asyncio.run(ensure_indexes(db))
    names = [n for coll in created.values() for n in coll]
    conflict_hits = [n for n in names if "pre-existing under a different name" in n]
    assert len(conflict_hits) == 2
    # Still reports all 25 rows as satisfied, not as failures.
    assert sum(len(v) for v in created.values()) == 25


def test_ensure_indexes_reraises_unrelated_operation_failures():
    class _FailingDB(_FakeDB):
        def __getitem__(self, name):
            class _AlwaysFails:
                async def create_index(self, keys, **kwargs):
                    raise OperationFailure("disk full", code=999)
            return _AlwaysFails()

    try:
        asyncio.run(ensure_indexes(_FailingDB()))
    except OperationFailure as e:
        assert e.code == 999
    else:
        raise AssertionError("a non-85 OperationFailure must propagate, not be swallowed")


if __name__ == "__main__":
    test_ping_returns_true_on_success()
    test_ping_raises_infrastructure_error_on_failure()
    test_ensure_indexes_creates_exactly_the_25_row_set()
    test_ensure_indexes_is_idempotent_across_two_runs()
    test_ensure_indexes_tolerates_a_pre_existing_differently_named_index()
    test_ensure_indexes_reraises_unrelated_operation_failures()
    print("ok: Mongo ping + ensure_indexes — 25/25 rows, idempotent, tolerates pre-existing conflicts, "
          "re-raises real failures")
