"""M8 domain models — FinancialStatement persistence shape (Document 32 §2.B/D,
CTO APPROVED) and the AcquisitionState three-state model (Document 35 §2/§4,
CTO RATIFIED). Pydantic v2, matching agents/schemas.py's existing convention
for structured, wire-adjacent data (unlike domain/models.py's Job, which is a
plain dataclass because it never crosses the wire — these do, eventually, via
GET /financials).

`FinancialStatement data != Acquisition lifecycle state` (Document 32 §4) —
kept as two separate model families in this one file, not merged, mirroring
the separate-repository-boundary decision (Document 35 §9).

Pure — stdlib + pydantic only, no driver imports (06 AD-6).
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class PeriodType(str, Enum):
    ANNUAL = "annual"
    QUARTERLY = "quarterly"


class StatementType(str, Enum):
    INCOME = "income"
    BALANCE_SHEET = "balance_sheet"
    CASH_FLOW = "cash_flow"


class MetricUnit(str, Enum):
    """Document 32 §2.D — deliberately closed, not general-purpose."""

    CURRENCY = "currency"
    CURRENCY_PER_SHARE = "currency_per_share"
    SHARES = "shares"
    RATIO = "ratio"
    PERCENTAGE = "percentage"
    COUNT = "count"


class Metric(BaseModel):
    """One line item within a FinancialStatement's metrics[] (Document 32 §2.D).

    `canonical_metric` stays null for every metric in Phase 1 — the five-step
    canonical-vocabulary governance process (Document 32 §3) that would
    populate it doesn't exist yet; no mapping has been approved."""

    canonical_metric: str | None = None
    provider_label: str
    value: float
    unit: MetricUnit


class FinancialStatement(BaseModel):
    """Identity (Document 32 §2.B, ADR-029 §8): ticker + period_type +
    period_end + statement_type. Collection: financial_statements
    (CTO-approved name, Document 32 Summary Table item 2)."""

    ticker: str
    period_type: PeriodType
    period_end: str  # ISO-8601 date, e.g. "2025-09-30" — repo-wide convention
    fiscal_year: str  # calendar year of period_end, AlphaScribe-derived (§2.C)
    statement_type: StatementType
    currency: str  # ISO 4217, from .info.financialCurrency
    source: str = "yfinance"
    fetched_at: str  # ISO-8601 datetime
    metrics: list[Metric] = Field(default_factory=list)


class AcquisitionOutcome(str, Enum):
    """Document 35 §2/§4 — exactly three states, no fourth. Ordered by
    AS-4's monotonic evidence precedence: AVAILABLE > CONFIRMED_UNAVAILABLE >
    NOT_YET_ACQUIRED. `NOT_YET_ACQUIRED` is never persisted (AS-3 — a
    transient/non-definitive attempt writes nothing); it is the read-time
    default when no document exists for an identity."""

    NOT_YET_ACQUIRED = "not_yet_acquired"
    AVAILABLE = "available"
    CONFIRMED_UNAVAILABLE = "confirmed_unavailable"


_PRECEDENCE = {
    AcquisitionOutcome.AVAILABLE: 2,
    AcquisitionOutcome.CONFIRMED_UNAVAILABLE: 1,
    AcquisitionOutcome.NOT_YET_ACQUIRED: 0,
}


def outcome_precedence(outcome: AcquisitionOutcome) -> int:
    """AS-4's ordering as a comparable int — available > confirmed_unavailable
    > no terminal state. Used by the Mongo adapter's conditional write and by
    tests that assert the precedence rule directly."""
    return _PRECEDENCE[outcome]


class AcquisitionState(BaseModel):
    """Identity (Document 35 §6, ratified — period_end excluded): ticker +
    period_type + statement_type. Collection name (`acquisition_states`) is
    an implementation-time choice, not a CTO gate (Document 35 §13,
    Document 39 §7)."""

    ticker: str
    period_type: PeriodType
    statement_type: StatementType
    state: AcquisitionOutcome
    updated_at: str  # ISO-8601 datetime
