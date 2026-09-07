"""Unit checks for agents/change_brief_financial.py's pure `period`-mode
delta computation (M15 / C-4, Document 70 R4 §8.2 / §11.2 / §14.1; Document
73 R1 §9). No DB, no network, no LLM — hermetic, same style as
test_comparison_explanation_pure.py / test_scoring.py.

    python -m pytest backend/tests/unit/test_change_brief_financial_pure.py -v
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.change_brief_financial import compute_financial_change_brief  # noqa: E402
from domain.financials import (  # noqa: E402
    FinancialStatement,
    Metric,
    MetricUnit,
    PeriodType,
    StatementType,
)


def _stmt(period_end, metrics, *, currency="USD", statement_type=StatementType.INCOME,
          period_type=PeriodType.QUARTERLY):
    return FinancialStatement(
        ticker="AAPL", period_type=period_type, period_end=period_end,
        fiscal_year=period_end[:4], statement_type=statement_type, currency=currency,
        fetched_at="2026-01-01T00:00:00Z",
        metrics=[Metric(provider_label=label, value=value, unit=unit) for label, value, unit in metrics],
    )


# --- changed / new / removed classification -------------------------------

def test_matched_metric_that_changed_is_a_changed_item_with_both_sides():
    out = compute_financial_change_brief(
        _stmt("2024-06-30", [("Revenue", 100.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("Revenue", 118.0, MetricUnit.CURRENCY)]),
    )
    assert out["state"] == "complete" and out["coverage_boundaries"] == []
    (item,) = out["items"]
    assert item["change_kind"] == "changed"
    assert item["before"] == {"period_end": "2024-06-30", "value": 100.0}
    assert item["after"] == {"period_end": "2024-09-30", "value": 118.0}
    assert item["absolute_delta"] == 18.0
    assert abs(item["percent_delta"] - 0.18) < 1e-9
    assert item["category"] == "financial" and item["unit"] == "currency" and item["currency"] == "USD"
    assert item["cited_source_indices"] == [1, 2]
    assert [s["period_end"] for s in item["sources"]] == ["2024-06-30", "2024-09-30"]
    assert all(set(s) == {"index", "statement_type", "period_end", "metric"} for s in item["sources"])


def test_identical_value_is_never_emitted():
    out = compute_financial_change_brief(
        _stmt("2024-06-30", [("Revenue", 100.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("Revenue", 100.0, MetricUnit.CURRENCY)]),
    )
    assert out["items"] == [] and out["state"] == "complete"  # no-change: positive, complete


def test_metric_only_in_current_is_new_with_null_before_and_cites_current_only():
    out = compute_financial_change_brief(
        _stmt("2024-06-30", [("Revenue", 100.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("Revenue", 100.0, MetricUnit.CURRENCY),
                             ("DeferredRev", 9.0, MetricUnit.CURRENCY)]),
    )
    (item,) = out["items"]
    assert item["metric"] == "DeferredRev" and item["change_kind"] == "new"
    assert item["before"] is None and item["after"] == {"period_end": "2024-09-30", "value": 9.0}
    assert item["absolute_delta"] is None and item["percent_delta"] is None
    assert item["cited_source_indices"] == [1]
    assert item["sources"] == [{"index": 1, "statement_type": "income",
                                "period_end": "2024-09-30", "metric": "DeferredRev"}]


def test_metric_only_in_baseline_is_removed_with_null_after_and_cites_baseline_only():
    out = compute_financial_change_brief(
        _stmt("2024-06-30", [("Revenue", 100.0, MetricUnit.CURRENCY),
                             ("LegacyLine", 4.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("Revenue", 100.0, MetricUnit.CURRENCY)]),
    )
    (item,) = out["items"]
    assert item["metric"] == "LegacyLine" and item["change_kind"] == "removed"
    assert item["after"] is None and item["before"] == {"period_end": "2024-06-30", "value": 4.0}
    assert item["cited_source_indices"] == [1]
    assert item["sources"][0]["period_end"] == "2024-06-30"


# --- percent_delta edge cases --------------------------------------------

def test_zero_baseline_yields_null_percent_delta_but_item_still_returned():
    out = compute_financial_change_brief(
        _stmt("2024-06-30", [("R&D", 0.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("R&D", 12.0, MetricUnit.CURRENCY)]),
    )
    (item,) = out["items"]
    assert item["change_kind"] == "changed"
    assert item["absolute_delta"] == 12.0
    assert item["percent_delta"] is None  # never a fabricated infinity


def test_sign_flip_is_a_valid_change_with_signed_arithmetic():
    out = compute_financial_change_brief(
        _stmt("2024-06-30", [("NetIncome", 10.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("NetIncome", -4.0, MetricUnit.CURRENCY)]),
    )
    (item,) = out["items"]
    assert item["absolute_delta"] == -14.0
    assert abs(item["percent_delta"] - (-1.4)) < 1e-9


# --- unit / currency anomalies -----------------------------------------

def test_same_label_different_unit_is_excluded_and_triggers_partial():
    out = compute_financial_change_brief(
        _stmt("2024-06-30", [("Margin", 0.31, MetricUnit.RATIO),
                             ("Revenue", 100.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("Margin", 33.0, MetricUnit.PERCENTAGE),
                             ("Revenue", 110.0, MetricUnit.CURRENCY)]),
    )
    assert out["state"] == "partial"
    assert [i["metric"] for i in out["items"]] == ["Revenue"]  # Margin excluded
    assert any("Margin" in b and "unit mismatch" in b for b in out["coverage_boundaries"])


def test_currency_mismatch_is_insufficient_evidence_not_a_mixed_delta():
    out = compute_financial_change_brief(
        _stmt("2024-06-30", [("Revenue", 100.0, MetricUnit.CURRENCY)], currency="USD"),
        _stmt("2024-09-30", [("Revenue", 90.0, MetricUnit.CURRENCY)], currency="EUR"),
    )
    assert out["state"] == "insufficient_evidence" and out["items"] == []
    assert any("currency mismatch" in b for b in out["coverage_boundaries"])


def test_empty_metrics_on_a_side_is_insufficient_evidence():
    out = compute_financial_change_brief(
        _stmt("2024-06-30", []),
        _stmt("2024-09-30", [("Revenue", 90.0, MetricUnit.CURRENCY)]),
    )
    assert out["state"] == "insufficient_evidence" and out["items"] == []


# --- ordering + determinism -------------------------------------------

def test_items_are_ordered_by_metric_ascending_and_deterministic():
    base = _stmt("2024-06-30", [("Zeta", 1.0, MetricUnit.CURRENCY),
                                ("Alpha", 1.0, MetricUnit.CURRENCY),
                                ("Mu", 1.0, MetricUnit.CURRENCY)])
    curr = _stmt("2024-09-30", [("Zeta", 2.0, MetricUnit.CURRENCY),
                                ("Alpha", 2.0, MetricUnit.CURRENCY),
                                ("Mu", 2.0, MetricUnit.CURRENCY)])
    out1 = compute_financial_change_brief(base, curr)
    out2 = compute_financial_change_brief(base, curr)
    assert [i["metric"] for i in out1["items"]] == ["Alpha", "Mu", "Zeta"]
    assert out1 == out2  # byte-identical across repeated identical requests


def test_no_magnitude_threshold_every_nonzero_delta_qualifies():
    out = compute_financial_change_brief(
        _stmt("2024-06-30", [("Revenue", 1_000_000.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("Revenue", 1_000_000.01, MetricUnit.CURRENCY)]),
    )
    assert len(out["items"]) == 1 and out["items"][0]["change_kind"] == "changed"


if __name__ == "__main__":
    import subprocess
    raise SystemExit(subprocess.call([sys.executable, "-m", "pytest", __file__, "-v"]))
