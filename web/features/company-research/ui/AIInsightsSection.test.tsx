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
  const onGoToOverview = vi.fn();

  beforeEach(() => {
    useAiAccessStore.getState().clear();
    searchParams = new URLSearchParams();
    fetchReport.mockReset();
    onGoToOverview.mockReset();
  });

  it("prompts to run research first when there's no job yet", () => {
    renderWithProviders(<AIInsightsSection ticker="AAPL" onGoToOverview={onGoToOverview} />);
    expect(screen.getByText(/Run research on the Overview tab first/)).toBeInTheDocument();
  });

  it("shows a non-error message while the Overview run is still in progress", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValue({ status: "running", id: "job-1", events: [] });
    renderWithProviders(<AIInsightsSection ticker="AAPL" onGoToOverview={onGoToOverview} />);
    expect(await screen.findByText(/still running/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("renders the CopilotPanel once a completed report exists", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValue({ status: "completed", id: "job-1", report: REPORT });
    renderWithProviders(<AIInsightsSection ticker="AAPL" onGoToOverview={onGoToOverview} />);
    expect(await screen.findByText("About AAPL")).toBeInTheDocument();
  });

  // Migrated-parity hardening pass, Company Research Sub-Slice 5 Finding A —
  // a cancelled/failed job must show an honest error, not "still running"
  // forever (the same defect class as Financials Sub-Slice 2's Finding B).
  it("shows an honest error with a Go to Overview action when the job was cancelled", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValue({ status: "cancelled", id: "job-1" });
    renderWithProviders(<AIInsightsSection ticker="AAPL" onGoToOverview={onGoToOverview} />);
    expect(await screen.findByText(/was cancelled/)).toBeInTheDocument();
    expect(screen.queryByText(/still running/)).not.toBeInTheDocument();

    screen.getByRole("button", { name: "Go to Overview" }).click();
    expect(onGoToOverview).toHaveBeenCalledOnce();
  });

  it("shows an honest error with a Go to Overview action when the job failed", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValue({ status: "failed", id: "job-1" });
    renderWithProviders(<AIInsightsSection ticker="AAPL" onGoToOverview={onGoToOverview} />);
    expect(await screen.findByText(/failed — go to Overview/)).toBeInTheDocument();
    expect(screen.queryByText(/still running/)).not.toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValue({ status: "completed", id: "job-1", report: REPORT });
    const { container } = renderWithProviders(
      <AIInsightsSection ticker="AAPL" onGoToOverview={onGoToOverview} />,
    );
    await screen.findByText("About AAPL");

    expect(await axe(container)).toHaveNoViolations();
  });
});
