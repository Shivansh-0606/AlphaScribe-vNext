import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import type { AppError } from "@/lib/errors/app-error";
import { FilingAnalysisPanel } from "./FilingAnalysisPanel";

const createFilingAnalysis = vi.fn();
const fetchFilingAnalysis = vi.fn();
const cancelFilingAnalysis = vi.fn();
const openFilingAnalysisStream = vi.fn();

vi.mock("../integration/api", () => ({
  createFilingAnalysis: (...args: unknown[]) => createFilingAnalysis(...args),
  fetchFilingAnalysis: (...args: unknown[]) => fetchFilingAnalysis(...args),
  cancelFilingAnalysis: (...args: unknown[]) => cancelFilingAnalysis(...args),
  openFilingAnalysisStream: (...args: unknown[]) => openFilingAnalysisStream(...args),
}));

interface StreamHandlers {
  onEvent: (event: Record<string, unknown>) => void;
  onEnd: () => void;
  onError: (error: AppError) => void;
}

function lastStreamHandlers(): StreamHandlers {
  const call = openFilingAnalysisStream.mock.calls.at(-1) as
    [string, string, string, StreamHandlers] | undefined;
  if (!call) throw new Error("openFilingAnalysisStream was never called");
  return call[3];
}

const CHUNKS = [{ chunk_idx: 0, text: "Revenue for the period was $10B." }];

const ANALYSIS = {
  doc_id: "d1",
  ticker: "AAPL",
  company_name: "Apple Inc.",
  source: "10-Q FY24 Q3",
  created_at: "2026-01-01T00:00:00Z",
  prompt_version: "v1",
  schema_version: "v1",
  outputs: {
    "Filing Summary": {
      narrative: "Revenue was $10B [1].",
      sources: [{ index: 1, doc_id: "d1", chunk_start: 0, chunk_end: 0 }],
      cited_source_indices: [1],
      state: "complete",
      coverage_boundaries: [],
    },
  },
};

describe("FilingAnalysisPanel", () => {
  beforeEach(() => {
    createFilingAnalysis.mockReset();
    fetchFilingAnalysis.mockReset();
    cancelFilingAnalysis.mockReset().mockResolvedValue({ id: "job-1", status: "cancelled" });
    openFilingAnalysisStream.mockReset().mockReturnValue(vi.fn());
  });

  it("starts idle, offering an explicit Analyze action (never auto-runs a paid LLM job)", () => {
    renderWithProviders(
      <FilingAnalysisPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    expect(screen.getByRole("button", { name: "Analyze this filing" })).toBeInTheDocument();
    expect(createFilingAnalysis).not.toHaveBeenCalled();
  });

  it("runs the analyzing → completed lifecycle and renders the grounded result", async () => {
    createFilingAnalysis.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const { user } = renderWithProviders(
      <FilingAnalysisPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    await user.click(screen.getByRole("button", { name: "Analyze this filing" }));
    expect(createFilingAnalysis).toHaveBeenCalledWith("AAPL", "d1", {});

    await waitFor(() =>
      expect(openFilingAnalysisStream).toHaveBeenCalledWith(
        "AAPL",
        "d1",
        "job-1",
        expect.anything(),
      ),
    );
    expect(screen.getByText("Analyzing the filing…")).toBeInTheDocument();

    const handlers = lastStreamHandlers();
    handlers.onEvent({ node: "pipeline", status: "start", message: "Analysing filing" });
    handlers.onEvent({ node: "analyzing", status: "ok", message: "Filing Summary" });
    expect(await screen.findByText("Filing Summary")).toBeInTheDocument();

    handlers.onEvent({ node: "pipeline", status: "ok" });
    handlers.onEvent({ node: "final", status: "ok", analysis: ANALYSIS });
    handlers.onEnd();

    const region = await screen.findByRole("region", { name: "Filing Summary" });
    expect(region).toHaveTextContent("Revenue was $10B");
  });

  it("surfaces a failed run honestly, with retry", async () => {
    createFilingAnalysis.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const { user } = renderWithProviders(
      <FilingAnalysisPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    await user.click(screen.getByRole("button", { name: "Analyze this filing" }));
    await waitFor(() => expect(openFilingAnalysisStream).toHaveBeenCalled());

    lastStreamHandlers().onEvent({
      node: "pipeline",
      status: "error",
      message: "Filing analysis failed. See server logs for details.",
    });

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Filing analysis failed. See server logs for details.",
    );
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("cancelling stops the run and reports it honestly, without waiting on the server", async () => {
    createFilingAnalysis.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const closeStream = vi.fn();
    openFilingAnalysisStream.mockReturnValue(closeStream);
    const { user } = renderWithProviders(
      <FilingAnalysisPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    await user.click(screen.getByRole("button", { name: "Analyze this filing" }));
    await waitFor(() => expect(openFilingAnalysisStream).toHaveBeenCalled());

    await user.click(screen.getByRole("button", { name: "Stop analyzing" }));

    expect(closeStream).toHaveBeenCalled();
    expect(cancelFilingAnalysis).toHaveBeenCalledWith("AAPL", "d1", "job-1");
    expect(await screen.findByText("Filing analysis was cancelled.")).toBeInTheDocument();
  });

  it("has no detectable accessibility violations in the idle state", async () => {
    const { container } = renderWithProviders(
      <FilingAnalysisPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
