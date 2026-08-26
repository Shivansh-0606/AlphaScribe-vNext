import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { StatementTable, type StatementTablePeriod } from "./StatementTable";

const REVENUE = {
  canonical_metric: "total_revenue",
  provider_label: "Total Revenue",
  value: 416_161_000_000,
  unit: "currency" as const,
};
const EPS = {
  canonical_metric: null,
  provider_label: "Diluted EPS",
  value: 6.11,
  unit: "currency_per_share" as const,
};
const MARGIN = {
  canonical_metric: null,
  provider_label: "Operating Margin",
  value: 0.302,
  unit: "percentage" as const,
};
const SHARES = {
  canonical_metric: null,
  provider_label: "Shares Outstanding",
  value: 14_773_260_000,
  unit: "shares" as const,
};
const RATIO = {
  canonical_metric: null,
  provider_label: "Current Ratio",
  value: 1.83,
  unit: "ratio" as const,
};

function period(overrides: Partial<StatementTablePeriod>): StatementTablePeriod {
  return {
    period_end: "2025-09-30",
    fiscal_year: "2025",
    currency: "USD",
    metrics: [REVENUE],
    ...overrides,
  };
}

describe("StatementTable", () => {
  it("shows an honest empty state for zero periods, never a fabricated table", () => {
    renderWithProviders(<StatementTable periods={[]} />);
    expect(screen.getByText("No periods to display.")).toBeInTheDocument();
    expect(screen.queryByRole("table")).not.toBeInTheDocument();
  });

  it("renders one column per period, headed by fiscal year", () => {
    renderWithProviders(
      <StatementTable
        periods={[
          period({ period_end: "2025-09-30", fiscal_year: "2025" }),
          period({ period_end: "2024-09-30", fiscal_year: "2024" }),
        ]}
      />,
    );
    expect(screen.getByRole("columnheader", { name: "2025" })).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "2024" })).toBeInTheDocument();
  });

  it("formats each unit distinctly: currency (compact), per-share, percentage, shares, ratio", () => {
    renderWithProviders(
      <StatementTable periods={[period({ metrics: [REVENUE, EPS, MARGIN, SHARES, RATIO] })]} />,
    );
    expect(screen.getByText("$416.16B")).toBeInTheDocument();
    expect(screen.getByText("$6.11")).toBeInTheDocument();
    expect(screen.getByText("30.2%")).toBeInTheDocument();
    expect(screen.getByText("14.77B")).toBeInTheDocument();
    expect(screen.getByText("1.83")).toBeInTheDocument();
  });

  it("row order follows the most recent period's first-appearance order", () => {
    renderWithProviders(
      <StatementTable
        periods={[
          period({ period_end: "2025-09-30", fiscal_year: "2025", metrics: [REVENUE, EPS] }),
          period({ period_end: "2024-09-30", fiscal_year: "2024", metrics: [EPS, REVENUE] }),
        ]}
      />,
    );
    const rowHeaders = screen.getAllByRole("rowheader").map((el) => el.textContent);
    expect(rowHeaders).toEqual(["Total Revenue", "Diluted EPS"]);
  });

  it("a period missing a row shows an explicit 'Not available' cell, never a blank one", () => {
    renderWithProviders(
      <StatementTable
        periods={[
          period({ period_end: "2025-09-30", fiscal_year: "2025", metrics: [REVENUE, EPS] }),
          period({ period_end: "2024-09-30", fiscal_year: "2024", metrics: [REVENUE] }),
        ]}
      />,
    );
    expect(screen.getByText("Not available")).toBeInTheDocument();
  });

  it("uses scope=row on line-item headers for accessible row navigation", () => {
    renderWithProviders(<StatementTable periods={[period({})]} />);
    const rowHeader = screen.getByRole("rowheader", { name: "Total Revenue" });
    expect(rowHeader.tagName).toBe("TH");
    expect(rowHeader).toHaveAttribute("scope", "row");
  });
});
