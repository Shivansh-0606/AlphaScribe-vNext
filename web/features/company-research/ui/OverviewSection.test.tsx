import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { AppError } from "@/lib/errors/app-error";
import type { ReportDoc } from "../integration/schemas";
import { OverviewSection } from "./OverviewSection";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

const generateReport = vi.fn();
const fetchReport = vi.fn();
const cancelReport = vi.fn();
const ingestText = vi.fn();
const ingestEdgar = vi.fn();
const ingestSamples = vi.fn();
const openReportStream = vi.fn();

vi.mock("../integration/api", () => ({
  generateReport: (...args: unknown[]) => generateReport(...args),
  fetchReport: (...args: unknown[]) => fetchReport(...args),
  cancelReport: (...args: unknown[]) => cancelReport(...args),
  ingestText: (...args: unknown[]) => ingestText(...args),
  ingestEdgar: (...args: unknown[]) => ingestEdgar(...args),
  ingestSamples: (...args: unknown[]) => ingestSamples(...args),
  openReportStream: (...args: unknown[]) => openReportStream(...args),
}));

interface StreamHandlers {
  onEvent: (event: Record<string, unknown>) => void;
  onEnd: () => void;
  onError: (error: AppError) => void;
}

function lastStreamHandlers(): StreamHandlers {
  const call = openReportStream.mock.calls.at(-1) as [string, StreamHandlers] | undefined;
  if (!call) throw new Error("openReportStream was never called");
  return call[1];
}

const REPORT: ReportDoc = {
  id: "job-1",
  ticker: "AAPL",
  query: "Summarize the latest quarter",
  created_at: "2026-01-01T00:00:00Z",
  draft_report: "Revenue grew 12% year over year [1].",
  extracted_data: {
    revenue: "$100B",
    revenue_yoy: null,
    eps: null,
    net_income: null,
    guidance: null,
    operating_margin: null,
    free_cash_flow: null,
  },
  sentiment_analysis: {
    sentiment: "Bullish",
    confidence: 0.8,
    summary: "Strong quarter overall.",
    key_risks: [],
    key_positives: [],
  },
  source_documents: [
    { doc_id: "d1", ticker: "AAPL", source: "10-Q FY24 Q3", chunk_idx: 0, text: "…", score: 0.9 },
  ],
  fact_check_status: true,
  validation_errors: [],
  retry_count: 0,
  scorecard: {
    faithfulness: 0.9,
    context_precision: 0.85,
    answer_relevance: 0.88,
    overall: 0.87,
    cited_sources: [1],
    n_claims: 1,
    n_supported: 1,
  },
  company_name: "Apple Inc.",
};

async function startResearch(user: ReturnType<typeof renderWithProviders>["user"]) {
  await user.type(
    screen.getByLabelText(/What do you want to know/),
    "Summarize the latest quarter",
  );
  await user.click(screen.getByRole("button", { name: "Start research" }));
}

describe("OverviewSection", () => {
  beforeEach(() => {
    replace.mockClear();
    generateReport.mockReset();
    fetchReport.mockReset();
    cancelReport.mockReset().mockResolvedValue({ job_id: "job-1", status: "cancelled" });
    ingestText.mockReset();
    ingestEdgar.mockReset();
    ingestSamples.mockReset();
    openReportStream.mockReset().mockReturnValue(vi.fn());
  });

  it("shows inline ingest actions when the ticker has no filings, and auto-retries after ingesting samples", async () => {
    generateReport
      .mockRejectedValueOnce(
        new AppError(
          "unknown",
          "No filings ingested for AAPL. Ingest a filing first (POST /api/ingest/samples for demo data).",
          { status: 400 },
        ),
      )
      .mockResolvedValueOnce({ job_id: "job-1" });
    ingestSamples.mockResolvedValueOnce({ ingested: [], total_samples: 1 });

    const { user } = renderWithProviders(<OverviewSection ticker="AAPL" initialJobId={null} />);
    await startResearch(user);

    expect(await screen.findByText(/No filings for AAPL yet/)).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Load sample filings" }));

    await waitFor(() => expect(generateReport).toHaveBeenCalledTimes(2));
  });

  it("renders the thinking → streaming → grounded → completed lifecycle with a qualitative confidence label, never a raw number", async () => {
    generateReport.mockResolvedValueOnce({ job_id: "job-1" });
    const { user } = renderWithProviders(<OverviewSection ticker="AAPL" initialJobId={null} />);
    await startResearch(user);

    await waitFor(() => expect(openReportStream).toHaveBeenCalled());
    const handlers = lastStreamHandlers();

    handlers.onEvent({ node: "pipeline", status: "start", message: "Starting analysis" });
    expect(await screen.findByText(/Gathering filings/)).toBeInTheDocument();

    handlers.onEvent({ node: "synthesizer", status: "ok", message: "Draft ready" });
    expect(await screen.findByText(/Drafting the research brief/)).toBeInTheDocument();

    handlers.onEvent({ node: "fact_checker", status: "ok", message: "Claims verified" });
    expect(await screen.findByText(/Verifying claims/)).toBeInTheDocument();

    handlers.onEvent({ node: "pipeline", status: "ok", message: "Pipeline complete" });
    handlers.onEvent({ node: "final", status: "ok", report: REPORT });
    handlers.onEnd();

    expect(await screen.findByText("Well-supported")).toBeInTheDocument();
    expect(screen.queryByText("0.87")).not.toBeInTheDocument();
    expect(screen.queryByText(/87%/)).not.toBeInTheDocument();
  });

  it("renders citation markers as clickable anchors into the source list", async () => {
    generateReport.mockResolvedValueOnce({ job_id: "job-1" });
    const { user } = renderWithProviders(<OverviewSection ticker="AAPL" initialJobId={null} />);
    await startResearch(user);
    await waitFor(() => expect(openReportStream).toHaveBeenCalled());

    lastStreamHandlers().onEvent({ node: "final", status: "ok", report: REPORT });
    lastStreamHandlers().onEnd();

    const citationLink = await screen.findByRole("link", { name: "[1]" });
    expect(citationLink).toHaveAttribute("href", "#source-1");
  });

  it("cancel stops the stream and calls the cancel endpoint", async () => {
    generateReport.mockResolvedValueOnce({ job_id: "job-1" });
    const disposeStream = vi.fn();
    openReportStream.mockReturnValueOnce(disposeStream);
    const { user } = renderWithProviders(<OverviewSection ticker="AAPL" initialJobId={null} />);
    await startResearch(user);
    await waitFor(() => expect(openReportStream).toHaveBeenCalled());

    await user.click(screen.getByRole("button", { name: "Stop generating" }));

    expect(disposeStream).toHaveBeenCalled();
    expect(cancelReport).toHaveBeenCalledWith("job-1");
    // Regression: the UI must reflect cancellation immediately (never trap
    // the user waiting on the fire-and-forget cancel request) — it's the
    // only way this hook learns the run stopped, since we just closed our
    // own stream above.
    expect(await screen.findByText("Analysis was cancelled.")).toBeInTheDocument();
  });

  it("regression: closes the stream on unmount (e.g. switching SectionNav tabs mid-run)", async () => {
    generateReport.mockResolvedValueOnce({ job_id: "job-1" });
    const disposeStream = vi.fn();
    openReportStream.mockReturnValueOnce(disposeStream);
    const { user, unmount } = renderWithProviders(
      <OverviewSection ticker="AAPL" initialJobId={null} />,
    );
    await startResearch(user);
    await waitFor(() => expect(openReportStream).toHaveBeenCalled());

    unmount();

    expect(disposeStream).toHaveBeenCalled();
  });

  it("offers retry after a failed run and re-submits the same query", async () => {
    generateReport
      .mockResolvedValueOnce({ job_id: "job-1" })
      .mockResolvedValueOnce({ job_id: "job-2" });
    const { user } = renderWithProviders(<OverviewSection ticker="AAPL" initialJobId={null} />);
    await startResearch(user);
    await waitFor(() => expect(openReportStream).toHaveBeenCalled());

    lastStreamHandlers().onEvent({ node: "pipeline", status: "error", message: "Pipeline failed" });

    expect(await screen.findByRole("alert")).toHaveTextContent("Pipeline failed");
    await user.click(screen.getByRole("button", { name: "Retry" }));

    await waitFor(() => expect(generateReport).toHaveBeenCalledTimes(2));
  });

  it("a cached hit renders directly from the persisted report without opening a stream", async () => {
    generateReport.mockResolvedValueOnce({ job_id: "job-1", cached: true });
    fetchReport.mockResolvedValueOnce({ status: "completed", id: "job-1", report: REPORT });
    const { user } = renderWithProviders(<OverviewSection ticker="AAPL" initialJobId={null} />);
    await startResearch(user);

    expect(await screen.findByText("Well-supported")).toBeInTheDocument();
    expect(openReportStream).not.toHaveBeenCalled();
  });

  it("Trust-First regression: a completed-but-empty report renders the honest failure state, not a normal success brief, and Retry re-submits", async () => {
    generateReport
      .mockResolvedValueOnce({ job_id: "job-1" })
      .mockResolvedValueOnce({ job_id: "job-2" });
    const { user } = renderWithProviders(<OverviewSection ticker="AAPL" initialJobId={null} />);
    await startResearch(user);
    await waitFor(() => expect(openReportStream).toHaveBeenCalled());

    // Mirrors what was actually observed live: the pipeline reaches
    // "completed" (pipeline:ok, no error) but produced no usable content.
    lastStreamHandlers().onEvent({ node: "pipeline", status: "ok", message: "Pipeline complete" });
    lastStreamHandlers().onEvent({
      node: "final",
      status: "ok",
      report: { ...REPORT, draft_report: "", source_documents: [] },
    });
    lastStreamHandlers().onEnd();

    expect(await screen.findByRole("alert")).toHaveTextContent(/didn't produce a usable result/);
    expect(screen.queryByText("Well-supported")).not.toBeInTheDocument();
    expect(screen.queryByText("AI Research Brief")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Retry" }));
    await waitFor(() => expect(generateReport).toHaveBeenCalledTimes(2));
  });

  it("has no detectable accessibility violations in the idle (query form) state", async () => {
    const { container } = renderWithProviders(
      <OverviewSection ticker="AAPL" initialJobId={null} />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  it("has no detectable accessibility violations in the completed (AI Response Card) state", async () => {
    generateReport.mockResolvedValueOnce({ job_id: "job-1", cached: true });
    fetchReport.mockResolvedValueOnce({ status: "completed", id: "job-1", report: REPORT });
    const { user, container } = renderWithProviders(
      <OverviewSection ticker="AAPL" initialJobId={null} />,
    );
    await startResearch(user);
    await screen.findByText("Well-supported");

    expect(await axe(container)).toHaveNoViolations();
  });
});
