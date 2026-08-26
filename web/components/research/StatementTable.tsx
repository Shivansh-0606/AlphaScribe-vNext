import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/foundation/Table";
import { Text } from "@/components/foundation/Text";
import { cn } from "@/lib/utils";

export type StatementMetricUnit =
  "currency" | "currency_per_share" | "shares" | "ratio" | "percentage" | "count";

export interface StatementTableMetric {
  canonical_metric: string | null;
  provider_label: string;
  value: number;
  unit: StatementMetricUnit;
}

export interface StatementTablePeriod {
  period_end: string;
  fiscal_year: string;
  currency: string;
  metrics: StatementTableMetric[];
}

export interface StatementTableProps {
  periods: StatementTablePeriod[];
  className?: string;
}

// Fixed locale, not `undefined` (the runtime/OS default) — the same value
// must render identically regardless of which machine or browser locale is
// running this code, and `undefined` has been observed to resolve to
// non-Western grouping (e.g. lakh/crore) in some Node/ICU environments.
const LOCALE = "en-US";

function formatMetricValue(value: number, unit: StatementMetricUnit, currency: string): string {
  switch (unit) {
    case "currency":
      return new Intl.NumberFormat(LOCALE, {
        style: "currency",
        currency,
        notation: "compact",
        maximumFractionDigits: 2,
      }).format(value);
    case "currency_per_share":
      return new Intl.NumberFormat(LOCALE, {
        style: "currency",
        currency,
        maximumFractionDigits: 2,
      }).format(value);
    case "shares":
    case "count":
      return new Intl.NumberFormat(LOCALE, {
        notation: "compact",
        maximumFractionDigits: 2,
      }).format(value);
    case "percentage":
      // yfinance's margin/growth/yield fields (the label heuristic that
      // assigns this unit, agents/financials_provider.py::_infer_unit) are
      // fractional (0.35 => 35%) — never pre-scaled by the backend.
      return `${(value * 100).toFixed(1)}%`;
    case "ratio":
      return value.toFixed(2);
  }
}

/**
 * StatementTable (docs/design/09_Component_Inventory.md) — multi-period
 * Income/Balance/Cash Flow rendering, wired to real data for the first time
 * in M12 (Document 55 §3.2). Rows are the union of each period's
 * `canonical_metric ?? provider_label` in first-appearance order — periods
 * arrive `period_end` descending (Document 33 §6.2), so the most recent
 * period determines row order. A period missing a given row renders "Not
 * available" (Inventory's Partial Failure rule) rather than a blank cell:
 * different periods can carry different `provider_label` sets since the
 * canonical-metric mapping process doesn't exist yet (Document 32 §3) — not
 * this component's concern to reconcile beyond an honest per-cell gap.
 */
export function StatementTable({ periods, className }: StatementTableProps) {
  if (periods.length === 0) {
    return (
      <Text variant="small" className="text-muted-foreground">
        No periods to display.
      </Text>
    );
  }

  // `key` (canonical_metric, falling back to provider_label) identifies the
  // row across periods for matching purposes; `label` (always
  // provider_label) is what's actually shown — canonical_metric is an
  // internal snake_case slug, never user-facing text.
  const rowKeys: string[] = [];
  const rowLabel = new Map<string, string>();
  const seen = new Set<string>();
  for (const period of periods) {
    for (const metric of period.metrics) {
      const key = metric.canonical_metric ?? metric.provider_label;
      if (!seen.has(key)) {
        seen.add(key);
        rowKeys.push(key);
        rowLabel.set(key, metric.provider_label);
      }
    }
  }

  return (
    <div className={cn("overflow-x-auto", className)}>
      <Table>
        <TableHeader sticky>
          <TableRow>
            <TableHead scope="col">Line item</TableHead>
            {periods.map((period) => (
              <TableHead key={period.period_end} numeric scope="col">
                {period.fiscal_year}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rowKeys.map((key) => (
            <TableRow key={key}>
              <TableHead scope="row">{rowLabel.get(key)}</TableHead>
              {periods.map((period) => {
                const metric = period.metrics.find(
                  (m) => (m.canonical_metric ?? m.provider_label) === key,
                );
                return metric ? (
                  <TableCell key={period.period_end} numeric>
                    {formatMetricValue(metric.value, metric.unit, period.currency)}
                  </TableCell>
                ) : (
                  <TableCell key={period.period_end} numeric unavailable />
                );
              })}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
