"""MongoAcquisitionStateRepository — the adapter behind
application.ports.AcquisitionStateRepository (Document 35 §8/§9, Document 38,
both CTO ratified).

Collection: acquisition_states — an implementation-time naming choice
(Document 35 §13 / Document 39 §7 both explicitly defer this; not a CTO
gate). Identity: ticker + period_type + statement_type (Document 35 §6,
period_end excluded) — enforced by the I-27 unique index.

AS-4's monotonic evidence precedence (available > confirmed_unavailable > no
terminal state) is enforced here as a single-document conditional write, per
Document 35/38's explicit "no lock, no transaction — a losing concurrent
write is simply rejected or overwritten deterministically":

  - AVAILABLE is top precedence and sticky: always safe to set
    unconditionally (Document 35 AS-4 Case A/B/C).
  - CONFIRMED_UNAVAILABLE must never overwrite an existing AVAILABLE: the
    conditional update only matches documents whose state isn't already
    AVAILABLE. If a concurrent write already landed AVAILABLE first, the
    conditional update's upsert branch collides with the unique index and
    raises DuplicateKeyError — caught here and treated as the correct
    outcome (AVAILABLE wins), not an error.

No multi-document transaction is used or needed — this deployment's
standalone (non-replica-set) MongoDB topology doesn't support one anyway
(Document 38 §3), and AS-2/AS-4 only ever require single-document atomicity.
"""
from __future__ import annotations

from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from domain.financials import AcquisitionOutcome, PeriodType, StatementType

_COLLECTION = "acquisition_states"


class MongoAcquisitionStateRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._db = db

    def _identity(self, ticker: str, period_type: PeriodType, statement_type: StatementType) -> dict:
        return {"ticker": ticker.upper(), "period_type": period_type.value, "statement_type": statement_type.value}

    async def get(self, ticker: str, period_type: PeriodType, statement_type: StatementType) -> AcquisitionOutcome:
        doc = await self._db[_COLLECTION].find_one(self._identity(ticker, period_type, statement_type))
        if doc is None:
            return AcquisitionOutcome.NOT_YET_ACQUIRED
        return AcquisitionOutcome(doc["state"])

    async def write_terminal(
        self,
        ticker: str,
        period_type: PeriodType,
        statement_type: StatementType,
        outcome: AcquisitionOutcome,
    ) -> AcquisitionOutcome:
        if outcome is AcquisitionOutcome.NOT_YET_ACQUIRED:
            raise ValueError("write_terminal requires AVAILABLE or CONFIRMED_UNAVAILABLE, not NOT_YET_ACQUIRED (AS-3)")

        identity = self._identity(ticker, period_type, statement_type)
        now = datetime.now(timezone.utc).isoformat()

        if outcome is AcquisitionOutcome.AVAILABLE:
            await self._db[_COLLECTION].update_one(
                identity, {"$set": {**identity, "state": outcome.value, "updated_at": now}}, upsert=True
            )
            return AcquisitionOutcome.AVAILABLE

        # CONFIRMED_UNAVAILABLE — only write if the identity isn't already AVAILABLE.
        try:
            await self._db[_COLLECTION].update_one(
                {**identity, "state": {"$ne": AcquisitionOutcome.AVAILABLE.value}},
                {"$set": {**identity, "state": outcome.value, "updated_at": now}},
                upsert=True,
            )
        except DuplicateKeyError:
            # The identity already holds AVAILABLE under a different (unmatched) filter
            # clause — the unique index blocked the upsert's insert branch. Sticky-available
            # wins (Document 35 AS-4 Case A); this is the correct outcome, not a failure.
            pass

        return await self.get(ticker, period_type, statement_type)
