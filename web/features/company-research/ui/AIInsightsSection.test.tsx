import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { useAiAccessStore } from "@/lib/state/aiAccess";
import type { ReportDoc } from "../integration/schemas";
import { AIInsightsSection } from "./AIInsightsSection";

let searchParams = new URLSearchParams();
vi.mock("next/navigation", () => ({
  useSearchParams: () => searchParams,
}));

const fetchReport = vi.fn();
vi.mock("../integration/api", () => ({
  fetchReport: (...args: unknown[]) => fetchReport(...args),
  generateReport: vi.fn(),
  cancelReport: vi.fn(),
  openReportStream: vi.fn(),
}));

const REPORT: ReportDoc = {
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

describe("AIInsightsSection", () => {
  beforeEach(() => {
    useAiAccessStore.getState().clear();
    searchParams = new URLSearchParams();
    fetchReport.mockReset();
  });

  it("prompts to run research first when there's no job yet", () => {
    renderWithProviders(<AIInsightsSection ticker="AAPL" />);
    expect(screen.getByText(/Run research on the Overview tab first/)).toBeInTheDocument();
  });

  it("shows a non-error message while the Overview run is still in progress", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValueOnce({ status: "running", id: "job-1", events: [] });
    renderWithProviders(<AIInsightsSection ticker="AAPL" />);
    expect(await screen.findByText(/still running/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("renders the CopilotPanel once a completed report exists", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValueOnce({ status: "completed", id: "job-1", report: REPORT });
    renderWithProviders(<AIInsightsSection ticker="AAPL" />);
    expect(await screen.findByText("About AAPL")).toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValueOnce({ status: "completed", id: "job-1", report: REPORT });
    const { container } = renderWithProviders(<AIInsightsSection ticker="AAPL" />);
    await screen.findByText("About AAPL");

    expect(await axe(container)).toHaveNoViolations();
  });
});
