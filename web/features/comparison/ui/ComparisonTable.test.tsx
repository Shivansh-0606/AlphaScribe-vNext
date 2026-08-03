import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import type { ComparisonReport } from "../integration/schemas";
import { ComparisonTable } from "./ComparisonTable";

const FULL_DATA: ComparisonReport = {
  id: "r1",
  ticker: "MSFT",
  query: "q",
  created_at: "2026-01-01T00:00:00Z",
  company_name: "Microsoft Corporation",
  extracted_data: {
    revenue: "$64.7B",
    revenue_yoy: "+15%",
    eps: "$2.95",
    net_income: "$22.0B",
    operating_margin: "43.1%",
    free_cash_flow: null,
    guidance: null,
  },
  sentiment_analysis: { sentiment: "Bullish", summary: "s" },
  scorecard: { overall: 0.9 },
};

const NO_DATA: ComparisonReport = {
  id: "r2",
  ticker: "ZZZZ",
  query: "q",
  created_at: "2026-01-02T00:00:00Z",
  extracted_data: {},
  is_sample: true,
};

const noop = () => {};

describe("ComparisonTable", () => {
  it("shows a loader while pending", () => {
    renderWithProviders(
      <ComparisonTable reports={undefined} isLoading isError={false} onRetry={noop} />,
    );
    expect(screen.getByText("Loading comparison…")).toBeInTheDocument();
  });

  it("offers retry on a load error", async () => {
    const onRetry = vi.fn();
    const { user } = renderWithProviders(
      <ComparisonTable reports={undefined} isLoading={false} isError onRetry={onRetry} />,
    );
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("renders metrics side by side for each member", () => {
    renderWithProviders(
      <ComparisonTable
        reports={[FULL_DATA, NO_DATA]}
        isLoading={false}
        isError={false}
        onRetry={noop}
      />,
    );
    expect(screen.getByText("Microsoft Corporation")).toBeInTheDocument();
    expect(screen.getByText("$64.7B")).toBeInTheDocument();
    expect(screen.getByText("Bullish")).toBeInTheDocument();
  });

  // Frozen usage rule: "flags gaps rather than hiding them" — a member with
  // no extracted data still gets a column, just marked, never omitted.
  it("flags a member with no comparable data instead of hiding its column", () => {
    renderWithProviders(
      <ComparisonTable
        reports={[FULL_DATA, NO_DATA]}
        isLoading={false}
        isError={false}
        onRetry={noop}
      />,
    );
    expect(screen.getByText("Limited data")).toBeInTheDocument();
    expect(screen.getByText("ZZZZ")).toBeInTheDocument();
  });

  it("marks curated samples distinctly", () => {
    renderWithProviders(
      <ComparisonTable
        reports={[FULL_DATA, NO_DATA]}
        isLoading={false}
        isError={false}
        onRetry={noop}
      />,
    );
    expect(screen.getByText("Sample")).toBeInTheDocument();
  });

  it("shows explicit unavailable text for a missing individual metric, never a blank cell", () => {
    renderWithProviders(
      <ComparisonTable reports={[FULL_DATA]} isLoading={false} isError={false} onRetry={noop} />,
    );
    // Free Cash Flow is null on FULL_DATA.
    expect(screen.getAllByText("Not available").length).toBeGreaterThan(0);
  });

  it("renders nothing for an empty selection rather than an empty table shell", () => {
    const { container } = renderWithProviders(
      <ComparisonTable reports={[]} isLoading={false} isError={false} onRetry={noop} />,
    );
    expect(container.querySelector("table")).not.toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <ComparisonTable
        reports={[FULL_DATA, NO_DATA]}
        isLoading={false}
        isError={false}
        onRetry={noop}
      />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
