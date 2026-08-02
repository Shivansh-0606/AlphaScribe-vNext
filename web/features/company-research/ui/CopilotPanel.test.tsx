import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { useAiAccessStore } from "@/lib/state/aiAccess";
import type { ReportDoc } from "../integration/schemas";
import { CopilotPanel } from "./CopilotPanel";

const generateReport = vi.fn();
const fetchReport = vi.fn();
const cancelReport = vi.fn();
const openReportStream = vi.fn();

vi.mock("../integration/api", () => ({
  generateReport: (...args: unknown[]) => generateReport(...args),
  fetchReport: (...args: unknown[]) => fetchReport(...args),
  cancelReport: (...args: unknown[]) => cancelReport(...args),
  openReportStream: (...args: unknown[]) => openReportStream(...args),
}));

interface StreamHandlers {
  onEvent: (event: Record<string, unknown>) => void;
  onEnd: () => void;
  onError: (error: unknown) => void;
}

function lastStreamHandlers(): StreamHandlers {
  const call = openReportStream.mock.calls.at(-1) as [string, StreamHandlers] | undefined;
  if (!call) throw new Error("openReportStream was never called");
  return call[1];
}

const FOLLOWUP_REPORT: ReportDoc = {
  id: "job-2",
  ticker: "AAPL",
  query: "What drove the margin change?",
  created_at: "2026-01-01T00:00:00Z",
  draft_report: "Margin expanded due to cost discipline [1].",
  source_documents: [
    { doc_id: "d1", ticker: "AAPL", source: "10-Q FY24 Q3", chunk_idx: 0, text: "…", score: 0.9 },
  ],
  fact_check_status: true,
  validation_errors: [],
  retry_count: 0,
  scorecard: {
    faithfulness: 0.9,
    context_precision: 0.9,
    answer_relevance: 0.9,
    overall: 0.9,
    cited_sources: [1],
    n_claims: 1,
    n_supported: 1,
  },
};

describe("CopilotPanel", () => {
  beforeEach(() => {
    useAiAccessStore.getState().clear();
    generateReport.mockReset();
    fetchReport.mockReset();
    cancelReport.mockReset().mockResolvedValue({ job_id: "job-2", status: "cancelled" });
    openReportStream.mockReset().mockReturnValue(vi.fn());
  });

  it("routes to Settings instead of rendering a dead composer when AI access isn't set up", () => {
    useAiAccessStore.getState().setByokFields({});
    renderWithProviders(<CopilotPanel ticker="AAPL" contextReportId="job-1" />);
    expect(screen.getByRole("link", { name: "Set up AI access" })).toHaveAttribute(
      "href",
      "/settings",
    );
    expect(screen.queryByRole("button", { name: "Ask" })).not.toBeInTheDocument();
  });

  it("asks a follow-up with the given context_report_id and renders the answer", async () => {
    generateReport.mockResolvedValueOnce({ job_id: "job-2" });
    const { user } = renderWithProviders(<CopilotPanel ticker="AAPL" contextReportId="job-1" />);

    expect(screen.getByText("About AAPL")).toBeInTheDocument();
    await user.type(
      screen.getByLabelText(/Ask a follow-up question/),
      "What drove the margin change?",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(generateReport).toHaveBeenCalledWith(
      expect.objectContaining({ ticker: "AAPL", context_report_id: "job-1" }),
    );
    await waitFor(() => expect(openReportStream).toHaveBeenCalled());

    lastStreamHandlers().onEvent({ node: "final", status: "ok", report: FOLLOWUP_REPORT });
    lastStreamHandlers().onEnd();

    expect(await screen.findByText("Follow-up answer")).toBeInTheDocument();
    expect(screen.getByText(/Margin expanded due to cost discipline/)).toBeInTheDocument();
  });

  it("cancel stops the run and shows feedback immediately", async () => {
    generateReport.mockResolvedValueOnce({ job_id: "job-2" });
    const { user } = renderWithProviders(<CopilotPanel ticker="AAPL" contextReportId="job-1" />);
    await user.type(screen.getByLabelText(/Ask a follow-up question/), "Follow-up");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    await waitFor(() => expect(openReportStream).toHaveBeenCalled());

    await user.click(screen.getByRole("button", { name: "Stop generating" }));

    expect(cancelReport).toHaveBeenCalledWith("job-2");
    expect(await screen.findByText("Cancelled.")).toBeInTheDocument();
  });

  it("Trust-First regression: a completed-but-empty follow-up renders the honest failure state, and Retry re-asks", async () => {
    generateReport
      .mockResolvedValueOnce({ job_id: "job-2" })
      .mockResolvedValueOnce({ job_id: "job-3" });
    const { user } = renderWithProviders(<CopilotPanel ticker="AAPL" contextReportId="job-1" />);
    await user.type(screen.getByLabelText(/Ask a follow-up question/), "Follow-up");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    await waitFor(() => expect(openReportStream).toHaveBeenCalled());

    lastStreamHandlers().onEvent({
      node: "final",
      status: "ok",
      report: { ...FOLLOWUP_REPORT, draft_report: "", source_documents: [] },
    });
    lastStreamHandlers().onEnd();

    expect(await screen.findByRole("alert")).toHaveTextContent(/didn't produce a usable result/);
    expect(screen.queryByText("Follow-up answer")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Retry" }));
    await waitFor(() => expect(generateReport).toHaveBeenCalledTimes(2));
  });

  it("has no detectable accessibility violations in the composer state", async () => {
    const { container } = renderWithProviders(
      <CopilotPanel ticker="AAPL" contextReportId="job-1" />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
