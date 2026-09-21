"""Unit tests for scripts/backfill_metric_units.py's core migration logic.

Hermetic: a small fake motor-shaped collection (matching
test_financials_persistence.py's "fake motor double, no real server"
convention) simulates find({}) full-scan iteration and update_one's
_id+fetched_at compare-and-swap filter -- no real Mongo server.

    python backend/tests/unit/test_backfill_metric_units.py
"""
import asyncio
import copy
import os
import sys

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _BACKEND_DIR)
sys.path.insert(0, os.path.join(_BACKEND_DIR, "scripts"))

import backfill_metric_units as backfill_mod  # noqa: E402


class _UpdateResult:
    def __init__(self, matched_count: int) -> None:
        self.matched_count = matched_count


class _FakeCursor:
    def __init__(self, docs):
        self._docs = list(docs)

    def __aiter__(self):
        return self._gen()

    async def _gen(self):
        for d in self._docs:
            yield d


class _FakeCollection:
    """Only what backfill() calls: a full find({}) scan and an
    update_one(filter, {"$set": ...}) that matches iff every filter key
    equals the CURRENT stored value (the compare-and-swap semantics the
    race-condition fix depends on)."""

    def __init__(self, docs):
        self._docs = docs  # list[dict] -- the authoritative "stored" collection

    def find(self, _filt):
        # A real find() deserializes a fresh dict per document from wire
        # bytes -- mutating what it returns never touches the stored data.
        # Deep-copy here so the fake has the same isolation; without it,
        # backfill()'s local metrics-list mutation would leak into `_docs`
        # even in dry-run mode, which a real Mongo read would never do.
        return _FakeCursor([copy.deepcopy(d) for d in self._docs])

    async def update_one(self, filt, update):
        for d in self._docs:
            if all(d.get(k) == v for k, v in filt.items()):
                d.update(update.get("$set", {}))
                return _UpdateResult(matched_count=1)
        return _UpdateResult(matched_count=0)


class _FakeDB:
    def __init__(self, docs):
        self._collection = _FakeCollection(docs)

    def __getitem__(self, _name):
        return self._collection


def _doc(ticker, doc_id, provider_label, unit, fetched_at="2026-08-15T10:30:53+00:00"):
    return {
        "_id": doc_id,
        "ticker": ticker,
        "period_type": "annual",
        "statement_type": "income",
        "period_end": "2025-09-30",
        "fetched_at": fetched_at,
        "metrics": [{"provider_label": provider_label, "value": 1.0, "unit": unit}],
    }


def test_dry_run_reports_would_change_counts_without_writing():
    docs = [_doc("MSFT", "d1", "Net Income Continuous Operations", "ratio")]
    db = _FakeDB(docs)
    summary = asyncio.run(backfill_mod.backfill(db, execute=False))
    assert summary["docs_changed"] == 1 and summary["metrics_changed"] == 1
    assert summary["tickers_changed"] == {"MSFT"}
    assert docs[0]["metrics"][0]["unit"] == "ratio"  # dry run never mutates the stored doc


def test_execute_rewrites_unit_in_place_leaving_value_untouched():
    docs = [_doc("MSFT", "d1", "Selling General And Administration", "ratio")]
    db = _FakeDB(docs)
    summary = asyncio.run(backfill_mod.backfill(db, execute=True))
    assert summary["docs_changed"] == 1 and summary["docs_skipped_race"] == 0
    assert docs[0]["metrics"][0]["unit"] == "currency"
    assert docs[0]["metrics"][0]["value"] == 1.0


def test_correctly_classified_metric_is_left_alone():
    docs = [_doc("AAPL", "d1", "Total Revenue", "currency")]
    db = _FakeDB(docs)
    summary = asyncio.run(backfill_mod.backfill(db, execute=True))
    assert summary["docs_seen"] == 1 and summary["docs_changed"] == 0
    assert docs[0]["metrics"][0]["unit"] == "currency"


def test_concurrent_update_during_scan_is_not_clobbered():
    # The race Backend Reviewer flagged: a concurrent re-acquisition (e.g.
    # agents/financials_provider.py-driven upsert) changes fetched_at AFTER
    # this script reads the document but BEFORE it writes back. The CAS
    # filter must then miss (matched_count == 0) and the stale in-memory
    # copy must never overwrite the fresh document.
    docs = [_doc("MSFT", "d1", "Net Income Continuous Operations", "ratio",
                  fetched_at="2026-08-15T10:30:53+00:00")]
    db = _FakeDB(docs)
    real_update_one = db._collection.update_one

    async def _update_one_after_concurrent_write(filt, update):
        # By now backfill() has already built `filt` from its (stale) read,
        # keyed on the OLD fetched_at. Simulate the concurrent upsert landing
        # right before this write reaches the "server": bump fetched_at and
        # install a fresh, already-correctly-classified metrics array on the
        # authoritative stored document.
        docs[0]["fetched_at"] = "2026-09-21T00:00:00+00:00"
        docs[0]["metrics"] = [{"provider_label": "Net Income Continuous Operations",
                                "value": 2.0, "unit": "currency"}]
        return await real_update_one(filt, update)

    db._collection.update_one = _update_one_after_concurrent_write
    summary = asyncio.run(backfill_mod.backfill(db, execute=True))

    assert summary["docs_skipped_race"] == 1 and summary["docs_changed"] == 0
    # the concurrent writer's fresh value survives untouched
    assert docs[0]["metrics"][0]["value"] == 2.0
    assert docs[0]["fetched_at"] == "2026-09-21T00:00:00+00:00"


if __name__ == "__main__":
    test_dry_run_reports_would_change_counts_without_writing()
    test_execute_rewrites_unit_in_place_leaving_value_untouched()
    test_correctly_classified_metric_is_left_alone()
    test_concurrent_update_during_scan_is_not_clobbered()
    print("ok: backfill_metric_units dry-run/execute/no-op/concurrent-update-CAS-guard")
