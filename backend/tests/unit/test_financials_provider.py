"""Unit tests for agents/financials_provider.py's outcome classification
(M8 Phase 1A). Hermetic: `_fetch_statement_sync` is monkeypatched so no real
yfinance/network call is ever made.

The one invariant every test here ultimately protects: a transient or
malformed provider result must never come out classified as
DEFINITIVE_UNAVAILABLE (Document 35 AS-3 — that would become an incorrect
terminal `confirmed_unavailable` write once a future orchestrator consumes
this classification).

    python backend/tests/unit/test_financials_provider.py
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import requests

import agents.financials_provider as fp
from domain.financials import MetricUnit, PeriodType, StatementType


def _run(ticker="AAPL", period_type=PeriodType.ANNUAL, statement_type=StatementType.INCOME):
    return asyncio.run(fp.fetch_and_classify(ticker, period_type, statement_type))


def _patch_fetch(monkeypatch_fn):
    fp._fetch_statement_sync = monkeypatch_fn


def _restore(original):
    fp._fetch_statement_sync = original


_ORIGINAL = fp._fetch_statement_sync


def test_success_full_period_coverage():
    df = pd.DataFrame(
        {pd.Timestamp("2025-09-30"): [391_035_000_000.0, 93_736_000_000.0]},
        index=["Total Revenue", "Net Income"],
    )
    _patch_fetch(lambda ticker, pt, st: (df, "USD"))
    try:
        outcome = _run()
        assert outcome.kind == fp.ProviderOutcomeKind.SUCCESS
        assert len(outcome.statements) == 1
        stmt = outcome.statements[0]
        assert stmt.ticker == "AAPL"
        assert stmt.period_end == "2025-09-30"
        assert stmt.fiscal_year == "2025"
        assert stmt.currency == "USD"
        assert {m.provider_label for m in stmt.metrics} == {"Total Revenue", "Net Income"}
        assert all(m.canonical_metric is None for m in stmt.metrics)
    finally:
        _restore(_ORIGINAL)


def test_definitive_unavailable_on_empty_dataframe():
    # The RELIANCE.NS .quarterly_cashflow precedent (Document 31 §9) — no
    # exception, a genuinely empty (0, 0) DataFrame.
    _patch_fetch(lambda ticker, pt, st: (pd.DataFrame(), "INR"))
    try:
        outcome = _run()
        assert outcome.kind == fp.ProviderOutcomeKind.DEFINITIVE_UNAVAILABLE
        assert outcome.statements == []
    finally:
        _restore(_ORIGINAL)


def test_transient_failure_on_timeout():
    def _raise(ticker, pt, st):
        raise requests.exceptions.Timeout("timed out after 25s")

    _patch_fetch(_raise)
    try:
        outcome = _run()
        assert outcome.kind == fp.ProviderOutcomeKind.TRANSIENT_FAILURE
        assert "timeout" in outcome.detail.lower()
    finally:
        _restore(_ORIGINAL)


def test_transient_failure_on_network_error():
    def _raise(ticker, pt, st):
        raise requests.exceptions.ConnectionError("no route to host")

    _patch_fetch(_raise)
    try:
        outcome = _run()
        assert outcome.kind == fp.ProviderOutcomeKind.TRANSIENT_FAILURE
    finally:
        _restore(_ORIGINAL)


def test_transient_failure_on_unexpected_exception():
    # An unclassified provider exception must default to TRANSIENT, never to
    # a terminal outcome (AS-3's conservative-default requirement).
    def _raise(ticker, pt, st):
        raise RuntimeError("yfinance internal parsing bug")

    _patch_fetch(_raise)
    try:
        outcome = _run()
        assert outcome.kind == fp.ProviderOutcomeKind.TRANSIENT_FAILURE
        assert "RuntimeError" in outcome.detail
    finally:
        _restore(_ORIGINAL)


def test_invalid_response_on_non_dataframe():
    _patch_fetch(lambda ticker, pt, st: ("not a dataframe", "USD"))
    try:
        outcome = _run()
        assert outcome.kind == fp.ProviderOutcomeKind.INVALID_RESPONSE
    finally:
        _restore(_ORIGINAL)


def test_invalid_response_on_missing_currency():
    df = pd.DataFrame({pd.Timestamp("2025-09-30"): [1.0]}, index=["Total Revenue"])
    _patch_fetch(lambda ticker, pt, st: (df, None))
    try:
        outcome = _run()
        assert outcome.kind == fp.ProviderOutcomeKind.INVALID_RESPONSE
    finally:
        _restore(_ORIGINAL)


def test_invalid_response_on_no_parseable_rows():
    df = pd.DataFrame({pd.Timestamp("2025-09-30"): [float("nan"), float("nan")]}, index=["A", "B"])
    _patch_fetch(lambda ticker, pt, st: (df, "USD"))
    try:
        outcome = _run()
        assert outcome.kind == fp.ProviderOutcomeKind.INVALID_RESPONSE
    finally:
        _restore(_ORIGINAL)


def test_partial_success_when_some_periods_have_no_usable_rows():
    df = pd.DataFrame(
        {
            pd.Timestamp("2025-09-30"): [391_035_000_000.0],
            pd.Timestamp("2024-09-30"): [float("nan")],
        },
        index=["Total Revenue"],
    )
    _patch_fetch(lambda ticker, pt, st: (df, "USD"))
    try:
        outcome = _run()
        assert outcome.kind == fp.ProviderOutcomeKind.PARTIAL_SUCCESS
        assert len(outcome.statements) == 1
        assert outcome.statements[0].period_end == "2025-09-30"
    finally:
        _restore(_ORIGINAL)


def test_unit_heuristic_recognizes_per_share_and_share_count_and_percentage():
    assert fp._infer_unit("Diluted EPS Per Share") == MetricUnit.CURRENCY_PER_SHARE
    assert fp._infer_unit("Ordinary Shares Number") == MetricUnit.SHARES
    assert fp._infer_unit("Gross Margin") == MetricUnit.PERCENTAGE
    assert fp._infer_unit("Total Revenue") == MetricUnit.CURRENCY


if __name__ == "__main__":
    test_success_full_period_coverage()
    test_definitive_unavailable_on_empty_dataframe()
    test_transient_failure_on_timeout()
    test_transient_failure_on_network_error()
    test_transient_failure_on_unexpected_exception()
    test_invalid_response_on_non_dataframe()
    test_invalid_response_on_missing_currency()
    test_invalid_response_on_no_parseable_rows()
    test_partial_success_when_some_periods_have_no_usable_rows()
    test_unit_heuristic_recognizes_per_share_and_share_count_and_percentage()
    print("ok: provider outcome classification — success/definitive-unavailable/transient/invalid/partial, "
          "unit heuristic")
