"""MongoFinancialStatementRepository — the adapter behind
application.ports.FinancialStatementRepository (ADR-029 §5/§8, ratified).

Collection: financial_statements (CTO-approved name, Document 32 Summary
Table item 2). Identity: ticker + period_type + period_end + statement_type
(ADR-029 §8) — enforced by the I-26 unique index (infrastructure/mongo/
indexes.py), not by this adapter; upsert() relies on that index for
uniqueness, matching the existing companies/filings upsert pattern.

Restatement policy (ADR-029 §6.4, decided): latest-provider-value-wins,
whole-document upsert, no historical versioning — a plain upsert on the
identity key is sufficient, no conditional/compare-and-swap logic needed
here (contrast with acquisition_state.py, where AS-4's precedence rule does
require one).
"""
from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from domain.financials import FinancialStatement, PeriodType

_COLLECTION = "financial_statements"


class MongoFinancialStatementRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._db = db

    async def get(self, ticker: str, period_type: PeriodType) -> list[FinancialStatement]:
        cursor = self._db[_COLLECTION].find({"ticker": ticker.upper(), "period_type": period_type.value})
        return [FinancialStatement.model_validate(doc) async for doc in cursor]

    async def upsert(self, statement: FinancialStatement) -> None:
        doc = statement.model_dump(mode="json")
        doc["ticker"] = doc["ticker"].upper()  # normalize consistently with get() (CTO hardening fix)
        identity = {
            "ticker": doc["ticker"],
            "period_type": doc["period_type"],
            "period_end": doc["period_end"],
            "statement_type": doc["statement_type"],
        }
        await self._db[_COLLECTION].update_one(identity, {"$set": doc}, upsert=True)

    async def freshness(self, ticker: str, period_type: PeriodType) -> str | None:
        cursor = (
            self._db[_COLLECTION]
            .find({"ticker": ticker.upper(), "period_type": period_type.value}, {"fetched_at": 1})
            .sort("fetched_at", -1)
            .limit(1)
        )
        docs = [d async for d in cursor]
        return docs[0]["fetched_at"] if docs else None
