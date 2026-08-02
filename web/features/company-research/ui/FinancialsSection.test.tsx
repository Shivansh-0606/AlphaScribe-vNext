import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import type { ReportDoc } from "../integration/schemas";
import { FinancialsSection } from "./FinancialsSection";

let searchParams = new URLSearchParams();
vi.mock("next/navigation", () => ({
  useSearchParams: () => searchParams,
}));

const fetchReport = vi.fn();
vi.mock("../integration/api", () => ({
  fetchReport: (...args: unknown[]) => fetchReport(...args),
}));

const BASE_REPORT: ReportDoc = {
  id: "job-1",
  ticker: "AAPL",
  query: "q",
  created_at: "2026-01-01T00:00:00Z",
  draft_report: "…",
  source_documents: [],
  fact_check_status: true,
  validation_errors: [],
  retry_count: 0,
  scorecard: {
    faithfulness: 1,
    context_precision: 1,
    answer_relevance: 1,
    overall: 1,
    cited_sources: [],
    n_claims: 0,
    n_supported: 0,
  },
};

describe("FinancialsSection", () => {
  beforeEach(() => {
    searchParams = new URLSearchParams();
    fetchReport.mockReset();
  });

  it("shows an empty state prompting Overview when there's no job yet", () => {
    renderWithProviders(<FinancialsSection ticker="AAPL" />);
    expect(screen.getByText(/Run research on the Overview tab/)).toBeInTheDocument();
  });

  it("renders MetricStat cards only for fields that actually have a value, plus guidance separately", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValueOnce({
      status: "completed",
      id: "job-1",
      report: {
        ...BASE_REPORT,
        extracted_data: {
          revenue: "$100B",
          revenue_yoy: "+8.2%",
          eps: null,
          net_income: null,
          guidance: "Raised FY25 outlook.",
          operating_margin: null,
          free_cash_flow: null,
        },
      },
    });
    renderWithProviders(<FinancialsSection ticker="AAPL" />);

    expect(await screen.findByText("$100B")).toBeInTheDocument();
    expect(screen.getByText("+8.2%")).toBeInTheDocument();
    expect(screen.getByText("Raised FY25 outlook.")).toBeInTheDocument();
    expect(screen.queryByText("EPS")).not.toBeInTheDocument();
    // The Statements placeholder is always present — never fabricated content (CTO decision).
    expect(screen.getByText(/Multi-period Income Statement/)).toBeInTheDocument();
  });

  it("shows a no-metrics message when extracted_data is empty, not a blank grid", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValueOnce({
      status: "completed",
      id: "job-1",
      report: { ...BASE_REPORT, extracted_data: {} },
    });
    renderWithProviders(<FinancialsSection ticker="AAPL" />);
    expect(
      await screen.findByText("No financial metrics were extracted for this report."),
    ).toBeInTheDocument();
  });

  it("surfaces a load failure with retry", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockRejectedValueOnce(new Error("network"));
    renderWithProviders(<FinancialsSection ticker="AAPL" />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't load financial metrics.");
  });

  it("regression: a still-running job (no report yet) is not treated as a load failure", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    // In-flight jobs resolve to {status, id, events} — no `report` field — which is
    // legitimate, not an error (server.py:1009-1027).
    fetchReport.mockResolvedValueOnce({ status: "running", id: "job-1", events: [] });
    renderWithProviders(<FinancialsSection ticker="AAPL" />);
    expect(await screen.findByText(/Research is still running/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("has no detectable accessibility violations with metrics rendered", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValueOnce({
      status: "completed",
      id: "job-1",
      report: { ...BASE_REPORT, extracted_data: { revenue: "$100B", eps: "$1.23" } },
    });
    const { container } = renderWithProviders(<FinancialsSection ticker="AAPL" />);
    await screen.findByText("$100B");

    expect(await axe(container)).toHaveNoViolations();
  });
});
