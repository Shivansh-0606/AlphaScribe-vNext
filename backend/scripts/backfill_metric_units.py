"""One-time backfill for the non-retroactive gap left by commit `cdc2914`
("fix(financials): match \"ratio\" as whole word, not substring") -- M15
Changes hardening-pass brief Finding B / Sub-Slice 2 Finding A follow-up.

`_infer_unit()` only runs at acquisition time and its result is written
permanently into `FinancialStatement.metrics[].unit`. Fixing the function
did nothing for already-stored documents. This script re-runs the (now
fixed) `_infer_unit()` over every stored `metrics[]` entry in the
`financial_statements` collection and rewrites `unit` in place wherever it
changes. Reclassification only -- `value` is already correct and is never
touched; no re-fetch from yfinance is needed.

Dry run by default (no writes) -- reports how many documents/tickers/metric
entries would be affected. `--execute` performs the writes.

    python backend/scripts/backfill_metric_units.py             # dry run
    python backend/scripts/backfill_metric_units.py --execute   # apply

Concurrency: this is a read-modify-write over a collection that
`MongoFinancialStatementRepository.upsert()` (agents/ingest.py's Financials
counterpart) can also write to concurrently -- e.g. a live re-acquisition of
one of these exact tickers while this script is mid-scan. A naive
`update_one({"_id": ...}, {"$set": {"metrics": metrics}})` would clobber a
concurrent upsert's fresh document with this script's stale in-memory copy
(a lost update). Guarded with a compare-and-swap: the update's filter also
requires `fetched_at` to still match what was read, so a document that
changed underneath the scan is left alone (matched_count == 0) rather than
overwritten -- and it needs no retry, since a fresh upsert already carries
the fix's correct classification.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.financials_provider import _infer_unit  # noqa: E402
from app.settings import load_settings  # noqa: E402
from infrastructure.mongo.client import create_mongo_client  # noqa: E402

_COLLECTION = "financial_statements"


async def backfill(db, execute: bool) -> dict:
    """Core migration logic, decoupled from Mongo client/settings wiring so
    it can run hermetically against a fake `db` in tests."""
    docs_seen = 0
    docs_changed = 0
    metrics_changed = 0
    docs_skipped_race = 0
    tickers_changed: set[str] = set()

    async for doc in db[_COLLECTION].find({}):
        docs_seen += 1
        metrics = doc.get("metrics", [])
        changed_labels = []
        for m in metrics:
            new_unit = _infer_unit(m["provider_label"]).value
            if m.get("unit") != new_unit:
                changed_labels.append(f"{m['provider_label']!r}: {m.get('unit')} -> {new_unit}")
                m["unit"] = new_unit
        if not changed_labels:
            continue

        verb = "UPDATING" if execute else "WOULD UPDATE"
        print(f"{verb} {doc['ticker']} {doc['period_type']} {doc['statement_type']} "
              f"{doc['period_end']} (fetched_at={doc.get('fetched_at')})")
        for line in changed_labels:
            print(f"    {line}")

        if not execute:
            docs_changed += 1
            metrics_changed += len(changed_labels)
            tickers_changed.add(doc["ticker"])
            continue

        result = await db[_COLLECTION].update_one(
            {"_id": doc["_id"], "fetched_at": doc.get("fetched_at")},
            {"$set": {"metrics": metrics}},
        )
        if result.matched_count == 0:
            print("    SKIPPED -- document changed since read (concurrent update); "
                  "already current, not overwritten")
            docs_skipped_race += 1
            continue
        docs_changed += 1
        metrics_changed += len(changed_labels)
        tickers_changed.add(doc["ticker"])

    return {
        "docs_seen": docs_seen,
        "docs_changed": docs_changed,
        "metrics_changed": metrics_changed,
        "docs_skipped_race": docs_skipped_race,
        "tickers_changed": tickers_changed,
    }


async def _run(execute: bool) -> None:
    settings = load_settings()
    client = create_mongo_client(settings.mongo_url)
    try:
        summary = await backfill(client[settings.db_name], execute)
    finally:
        client.close()

    race_note = (f", {summary['docs_skipped_race']} skipped due to a concurrent update"
                 if summary["docs_skipped_race"] else "")
    print()
    print(f"{'Applied' if execute else 'Dry run'}: {summary['docs_seen']} document(s) scanned, "
          f"{summary['docs_changed']} document(s) affected across {len(summary['tickers_changed'])} ticker(s) "
          f"{sorted(summary['tickers_changed'])}, {summary['metrics_changed']} metric entries reclassified"
          f"{race_note}.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--execute", action="store_true", help="apply the writes (default: dry run only)")
    args = parser.parse_args()
    asyncio.run(_run(args.execute))


if __name__ == "__main__":
    main()
