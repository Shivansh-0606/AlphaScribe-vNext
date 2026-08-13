"""M8 Phase 1A — yfinance financial-statement fetch + provider-outcome
classification.

Deliberately a NEW module, not an addition to ingest.py, even though both
call yfinance (Document 30 §7 explicitly anticipates extending "the existing
`_fetch_yfinance_sync`-adjacent code path" — this is that extension, not a
second competing provider abstraction). The reason for the new file: every
existing ingest.py fetcher deliberately collapses failure to `None`
(`except ...: return None`) — Document 35 §2 names that exact pattern as the
anti-pattern acquisition-state persistence must not repeat. This module's
contract is the opposite: preserve enough information to classify the
failure, never silently collapse to `None`. Mixing that into a file whose
dominant, load-bearing convention is "swallow to None" would be easy to
accidentally erode; a dedicated module keeps the contract unambiguous.

Attribute selection (`.financials`/`.balance_sheet`/`.cashflow` and their
`quarterly_` counterparts, not the `_cash_flow` alias) is exactly what
Document 31 §2/§12 verified against the installed yfinance version.

Classification is intentionally separate from acquisition orchestration,
acquisition-state persistence, MongoDB, and the API layer — this module
returns a `ProviderOutcome`; nothing here writes to Mongo or decides what
`acquisition_state` value results (that mapping is Document 35 §5's outcome
table, applied by a future orchestration use case, not by this module).
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

import requests

from domain.financials import FinancialStatement, Metric, MetricUnit, PeriodType, StatementType

# Document 31 §2/§12 — the six attributes to call, per (period_type, statement_type).
# The `_cash_flow` spelling is a confirmed byte-identical alias; not called separately.
_ATTR_MAP: dict[tuple[PeriodType, StatementType], str] = {
    (PeriodType.ANNUAL, StatementType.INCOME): "financials",
    (PeriodType.QUARTERLY, StatementType.INCOME): "quarterly_financials",
    (PeriodType.ANNUAL, StatementType.BALANCE_SHEET): "balance_sheet",
    (PeriodType.QUARTERLY, StatementType.BALANCE_SHEET): "quarterly_balance_sheet",
    (PeriodType.ANNUAL, StatementType.CASH_FLOW): "cashflow",
    (PeriodType.QUARTERLY, StatementType.CASH_FLOW): "quarterly_cashflow",
}


class ProviderOutcomeKind(str, Enum):
    SUCCESS = "success"
    DEFINITIVE_UNAVAILABLE = "definitive_unavailable"
    TRANSIENT_FAILURE = "transient_failure"
    INVALID_RESPONSE = "invalid_response"
    PARTIAL_SUCCESS = "partial_success"


@dataclass
class ProviderOutcome:
    """The classification result. `statements` is populated only for
    SUCCESS/PARTIAL_SUCCESS (one FinancialStatement per usable period column
    — a single provider call can return several periods at once, Document
    30 §6.5). `detail` is for observability/logs only — never surfaced
    through a public API (this phase adds no API surface at all)."""

    kind: ProviderOutcomeKind
    statements: list[FinancialStatement] = field(default_factory=list)
    detail: str | None = None


def _infer_unit(provider_label: str) -> MetricUnit:
    """ponytail: label-text heuristic, not the Document 32 §3 five-step
    canonical-vocabulary governance process — that process (and the mapping
    table it produces) doesn't exist yet, so `unit` can't yet be derived from
    an approved canonical_metric mapping either. Upgrade path: once a
    provider_label -> canonical_metric mapping is approved and promoted, use
    the canonical concept's own known unit instead of this heuristic."""
    label = provider_label.lower()
    if "per share" in label:
        return MetricUnit.CURRENCY_PER_SHARE
    if "shares" in label or "share issued" in label:
        return MetricUnit.SHARES
    if "margin" in label or "growth" in label or "yield" in label or "%" in provider_label:
        return MetricUnit.PERCENTAGE
    if "ratio" in label:
        return MetricUnit.RATIO
    return MetricUnit.CURRENCY  # the observed default for statement line items (Document 31 §7)


def _fetch_statement_sync(ticker: str, period_type: PeriodType, statement_type: StatementType):
    """Blocking yfinance call — thread-wrapped by fetch_and_classify(). Raises
    on network/timeout/unexpected failure; never collapses to None (contrast
    with ingest.py's fetchers — see the module docstring)."""
    import yfinance as yf

    t = yf.Ticker(ticker.upper())
    df = getattr(t, _ATTR_MAP[(period_type, statement_type)])
    currency = None
    info = t.info
    if info:
        currency = info.get("financialCurrency") or info.get("currency")
    return df, currency


def _parse_periods(
    df, *, ticker: str, period_type: PeriodType, statement_type: StatementType, currency: str
) -> tuple[list[FinancialStatement], int]:
    """One column (period_end) -> one FinancialStatement, if it has at least
    one numeric row. Returns (statements, dropped_period_count) — a dropped
    period is a column where every row was NaN/unparseable, which is what
    makes PARTIAL_SUCCESS distinguishable from SUCCESS."""
    import pandas as pd

    now = datetime.now(timezone.utc).isoformat()
    statements: list[FinancialStatement] = []
    dropped = 0

    for column in df.columns:
        period_end_ts = pd.Timestamp(column)
        metrics: list[Metric] = []
        for label, raw_value in df[column].items():
            if raw_value is None or (isinstance(raw_value, float) and pd.isna(raw_value)):
                continue
            try:
                value = float(raw_value)
            except (TypeError, ValueError):
                continue
            metrics.append(
                Metric(
                    canonical_metric=None,  # Document 32 §3 — no approved mappings exist yet
                    provider_label=str(label),
                    value=value,
                    unit=_infer_unit(str(label)),
                )
            )
        if not metrics:
            dropped += 1
            continue
        statements.append(
            FinancialStatement(
                ticker=ticker.upper(),
                period_type=period_type,
                period_end=period_end_ts.date().isoformat(),
                fiscal_year=str(period_end_ts.year),
                statement_type=statement_type,
                currency=currency,
                fetched_at=now,
                metrics=metrics,
            )
        )
    return statements, dropped


async def fetch_and_classify(
    ticker: str, period_type: PeriodType, statement_type: StatementType
) -> ProviderOutcome:
    """The classification layer. Maps every named scenario (Phase 1A's
    REQUIRED OUTCOME MODEL) onto exactly one ProviderOutcomeKind:
      - timeout / network failure / unexpected exception -> TRANSIENT_FAILURE
        (AS-3: must never become a terminal confirmed_unavailable write)
      - empty DataFrame (Document 31 §9 — checked via .empty, not an
        exception) -> DEFINITIVE_UNAVAILABLE
      - non-DataFrame / no parseable rows / no usable currency ->
        INVALID_RESPONSE (cannot safely interpret per the FinancialStatement
        model)
      - every period usable -> SUCCESS; some but not all -> PARTIAL_SUCCESS
        (Document 35 §5: both map to `available` at the acquisition-state
        layer — no new state is introduced here or by that mapping)
    """
    try:
        df, currency = await asyncio.to_thread(_fetch_statement_sync, ticker, period_type, statement_type)
    except requests.exceptions.Timeout as e:
        return ProviderOutcome(ProviderOutcomeKind.TRANSIENT_FAILURE, detail=f"timeout: {e}")
    except requests.exceptions.RequestException as e:
        return ProviderOutcome(ProviderOutcomeKind.TRANSIENT_FAILURE, detail=f"network error: {e}")
    except Exception as e:  # noqa: BLE001 — unclassified provider exception; safe default per AS-3
        return ProviderOutcome(
            ProviderOutcomeKind.TRANSIENT_FAILURE,
            detail=f"unexpected provider exception: {type(e).__name__}: {e}",
        )

    import pandas as pd

    if not isinstance(df, pd.DataFrame):
        return ProviderOutcome(
            ProviderOutcomeKind.INVALID_RESPONSE, detail=f"unexpected response type: {type(df).__name__}"
        )
    if df.empty:
        return ProviderOutcome(ProviderOutcomeKind.DEFINITIVE_UNAVAILABLE)
    if not currency:
        return ProviderOutcome(
            ProviderOutcomeKind.INVALID_RESPONSE, detail="response missing a usable currency (.info)"
        )

    statements, dropped = _parse_periods(
        df, ticker=ticker, period_type=period_type, statement_type=statement_type, currency=currency
    )
    if not statements:
        return ProviderOutcome(
            ProviderOutcomeKind.INVALID_RESPONSE,
            detail="non-empty response but no period column had a parseable numeric row",
        )

    kind = ProviderOutcomeKind.PARTIAL_SUCCESS if dropped else ProviderOutcomeKind.SUCCESS
    return ProviderOutcome(kind, statements=statements)
