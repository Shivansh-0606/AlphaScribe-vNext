"""M15 / C-4 — `period`-mode financial change-brief computation.

Pure, deterministic, dependency-free, LLM-free (Document 73 R1 §9; Document 70
R4 §8.2 / §11.2). Same house discipline as `agents/scoring.py`: stdlib + the
domain model only, no `chat_*` import, no I/O. The single place all of
Document 70 R4 §8.2's eligibility rules are encoded — nowhere else.

Metric identity is exact `Metric.provider_label` string equality only
(`Metric.canonical_metric` is `null` for every metric today — no canonical
vocabulary exists to map against, and none is invented here). A provider that
relabels a line item between periods is observed as one removed + one new
metric; Document 70 R4 §8.2 already documents and accepts this.
"""
from __future__ import annotations

from domain.financials import FinancialStatement

CATEGORY = "financial"
# No SCHEMA_VERSION here: the externally emitted `schema_version` is a single
# response-envelope version for both modes, sourced by server.py from the
# narrative module (agents/change_brief_narrative.SCHEMA_VERSION). A per-engine
# financial constant would be dead plumbing.


def _identity(stmt: FinancialStatement) -> dict:
    """The mode-specific `baseline`/`current` identity object for the response
    envelope (Document 70 R4 §11.1)."""
    return {
        "period_end": stmt.period_end,
        "period_type": stmt.period_type.value,
        "statement_type": stmt.statement_type.value,
        "fiscal_year": stmt.fiscal_year,
        "currency": stmt.currency,
    }


def _metric_map(stmt: FinancialStatement) -> dict[str, "object"]:
    # Last wins on a duplicate provider_label within one statement (a data
    # anomaly Document 70 R4 does not special-case); deterministic given the
    # stored metrics[] order, which is fixed for immutable financial rows.
    return {m.provider_label: m for m in stmt.metrics}


def compute_financial_change_brief(
    baseline: FinancialStatement, current: FinancialStatement
) -> dict:
    """Compare two already-resolved `FinancialStatement` rows and return the
    `changes` body's mode-specific fields: `baseline`, `current`, `items`,
    `state`, `coverage_boundaries`.

    Deterministic: the same two inputs always produce byte-identical output,
    including item order (sorted by `metric`, ascending, lexicographic).
    """
    baseline_id, current_id = _identity(baseline), _identity(current)
    empty = {
        "baseline": baseline_id,
        "current": current_id,
        "items": [],
        "state": "insufficient_evidence",
        "coverage_boundaries": [],
    }

    # Whole-comparison short-circuits (Document 70 R4 §14.1): a currency
    # mismatch is ungroundable (no FX capability exists), and an empty
    # metrics[] on either side leaves nothing to compare.
    if baseline.currency != current.currency:
        empty["coverage_boundaries"] = [
            f"currency mismatch: baseline {baseline.currency} vs current {current.currency}"
        ]
        return empty
    if not baseline.metrics or not current.metrics:
        empty["coverage_boundaries"] = ["one or both statements have no metrics"]
        return empty

    base_map = _metric_map(baseline)
    curr_map = _metric_map(current)

    items: list[dict] = []
    coverage_boundaries: list[str] = []

    for label in sorted(set(base_map) | set(curr_map)):
        b = base_map.get(label)
        c = curr_map.get(label)

        if b is not None and c is not None:
            if b.unit != c.unit:
                # Same label, different unit — not a computable delta
                # (Document 70 R4 §8.2). Excluded from items, recorded, → partial.
                coverage_boundaries.append(
                    f"unit mismatch for {label}: {b.unit.value} vs {c.unit.value}"
                )
                continue
            if b.value == c.value:
                continue  # identical — not emitted (Document 70 R4 §8.2)
            items.append(
                _item(
                    label, "changed", current.statement_type.value,
                    current.period_type.value, c.unit.value, current.currency,
                    before={"period_end": baseline.period_end, "value": b.value},
                    after={"period_end": current.period_end, "value": c.value},
                )
            )
        elif c is not None:  # present in current only
            items.append(
                _item(
                    label, "new", current.statement_type.value,
                    current.period_type.value, c.unit.value, current.currency,
                    before=None,
                    after={"period_end": current.period_end, "value": c.value},
                )
            )
        else:  # present in baseline only
            items.append(
                _item(
                    label, "removed", baseline.statement_type.value,
                    baseline.period_type.value, b.unit.value, baseline.currency,
                    before={"period_end": baseline.period_end, "value": b.value},
                    after=None,
                )
            )

    state = "partial" if coverage_boundaries else "complete"
    return {
        "baseline": baseline_id,
        "current": current_id,
        "items": items,
        "state": state,
        "coverage_boundaries": coverage_boundaries,
    }


def _item(
    metric: str, change_kind: str, statement_type: str, period_type: str,
    unit: str, currency: str, *, before: dict | None, after: dict | None,
) -> dict:
    absolute_delta = (
        after["value"] - before["value"] if before is not None and after is not None else None
    )
    percent_delta = (
        (after["value"] - before["value"]) / abs(before["value"])
        if before is not None and after is not None and before["value"] != 0
        else None
    )
    # Financial citations are self-evidencing and built directly from the two
    # resolved statement identities — no model, no grounding claim to validate
    # (Document 70 R4 §12). A `changed` item cites both sides (index 1 =
    # baseline, 2 = current); `new` cites current only; `removed` cites
    # baseline only (Document 70 R4 §11.2).
    sources: list[dict] = []
    if before is not None:
        sources.append({
            "index": len(sources) + 1, "statement_type": statement_type,
            "period_end": before["period_end"], "metric": metric,
        })
    if after is not None:
        sources.append({
            "index": len(sources) + 1, "statement_type": statement_type,
            "period_end": after["period_end"], "metric": metric,
        })
    return {
        "category": CATEGORY,
        "metric": metric,
        "statement_type": statement_type,
        "period_type": period_type,
        "change_kind": change_kind,
        "unit": unit,
        "currency": currency,
        "before": before,
        "after": after,
        "absolute_delta": absolute_delta,
        "percent_delta": percent_delta,
        "sources": sources,
        "cited_source_indices": [s["index"] for s in sources],
    }


if __name__ == "__main__":  # ponytail: one runnable check for the eligibility rule
    from domain.financials import Metric, MetricUnit, PeriodType, StatementType

    def _stmt(pe, metrics, currency="USD"):
        return FinancialStatement(
            ticker="T", period_type=PeriodType.QUARTERLY, period_end=pe,
            fiscal_year=pe[:4], statement_type=StatementType.INCOME,
            currency=currency, fetched_at="2026-01-01T00:00:00Z",
            metrics=[Metric(provider_label=l, value=v, unit=u) for l, v, u in metrics],
        )

    base = _stmt("2024-06-30", [
        ("Revenue", 100.0, MetricUnit.CURRENCY),
        ("Margin", 0.2, MetricUnit.RATIO),
        ("OldLine", 5.0, MetricUnit.CURRENCY),
        ("Same", 7.0, MetricUnit.CURRENCY),
    ])
    curr = _stmt("2024-09-30", [
        ("Revenue", 110.0, MetricUnit.CURRENCY),
        ("Margin", 20.0, MetricUnit.PERCENTAGE),   # unit mismatch → excluded, partial
        ("NewLine", 3.0, MetricUnit.CURRENCY),
        ("Same", 7.0, MetricUnit.CURRENCY),         # identical → not emitted
    ])
    out = compute_financial_change_brief(base, curr)
    kinds = {i["metric"]: i["change_kind"] for i in out["items"]}
    assert kinds == {"NewLine": "new", "OldLine": "removed", "Revenue": "changed"}, kinds
    assert out["state"] == "partial" and out["coverage_boundaries"], out
    rev = next(i for i in out["items"] if i["metric"] == "Revenue")
    assert rev["absolute_delta"] == 10.0 and abs(rev["percent_delta"] - 0.1) < 1e-9, rev
    assert rev["cited_source_indices"] == [1, 2]
    assert [i["metric"] for i in out["items"]] == sorted(i["metric"] for i in out["items"])
    # zero baseline → percent_delta null, item still returned
    z = compute_financial_change_brief(
        _stmt("2024-06-30", [("X", 0.0, MetricUnit.CURRENCY)]),
        _stmt("2024-09-30", [("X", 5.0, MetricUnit.CURRENCY)]),
    )
    assert z["items"][0]["percent_delta"] is None and z["items"][0]["absolute_delta"] == 5.0
    # currency mismatch → insufficient_evidence
    cm = compute_financial_change_brief(
        _stmt("2024-06-30", [("X", 1.0, MetricUnit.CURRENCY)], currency="USD"),
        _stmt("2024-09-30", [("X", 2.0, MetricUnit.CURRENCY)], currency="EUR"),
    )
    assert cm["state"] == "insufficient_evidence" and cm["items"] == []
    print("ok: change_brief_financial self-check passed")
