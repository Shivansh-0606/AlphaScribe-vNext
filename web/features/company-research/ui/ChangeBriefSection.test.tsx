import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import type { AppError } from "@/lib/errors/app-error";
import { ChangeBriefSection } from "./ChangeBriefSection";

const fetchReportsForTicker = vi.fn();
const fetchFinancialStatements = vi.fn();
const createChangeBrief = vi.fn();
const fetchChangeBrief = vi.fn();
const cancelChangeBrief = vi.fn();
const openChangeBriefStream = vi.fn();
const fetchReport = vi.fn();

vi.mock("../integration/api", () => ({
  fetchReportsForTicker: (...args: unknown[]) => fetchReportsForTicker(...args),
  fetchFinancialStatements: (...args: unknown[]) => fetchFinancialStatements(...args),
  createChangeBrief: (...args: unknown[]) => createChangeBrief(...args),
  fetchChangeBrief: (...args: unknown[]) => fetchChangeBrief(...args),
  cancelChangeBrief: (...args: unknown[]) => cancelChangeBrief(...args),
  openChangeBriefStream: (...args: unknown[]) => openChangeBriefStream(...args),
  fetchReport: (...args: unknown[]) => fetchReport(...args),
}));

interface StreamHandlers {
  onEvent: (event: Record<string, unknown>) => void;
  onEnd: () => void;
  onError: (error: AppError) => void;
}

function lastStreamHandlers(): StreamHandlers {
  const call = openChangeBriefStream.mock.calls.at(-1) as
    [string, string, StreamHandlers] | undefined;
  if (!call) throw new Error("openChangeBriefStream was never called");
  return call[2];
}

const REPORTS = {
  reports: [
    { id: "rb", ticker: "AAPL", query: "Q2 check-in", created_at: "2026-01-01T00:00:00Z" },
    { id: "rc", ticker: "AAPL", query: "Q3 check-in", created_at: "2026-04-01T00:00:00Z" },
  ],
};

const CHANGES_PAYLOAD = {
  ticker: "AAPL",
  comparison_type: "report",
  baseline: { report_id: "rb", ticker: "AAPL", company_name: "Apple Inc." },
  current: { report_id: "rc", ticker: "AAPL", company_name: "Apple Inc." },
  created_at: "2026-01-01T00:00:00Z",
  prompt_version: "v1",
  schema_version: "v1",
  items: [
    {
      category: "narrative",
      summary: "Guidance cut",
      explanation: "Guidance was raised [1] but is now lowered [2].",
      sources: [
        { index: 1, report_id: "rb", field: "extracted_data" },
        { index: 2, report_id: "rc", field: "extracted_data" },
      ],
      cited_source_indices: [1, 2],
    },
  ],
  state: "complete",
  coverage_boundaries: [],
};

describe("ChangeBriefSection", () => {
  beforeEach(() => {
    fetchReportsForTicker.mockReset().mockResolvedValue(REPORTS);
    fetchFinancialStatements.mockReset();
    createChangeBrief.mockReset();
    fetchChangeBrief.mockReset();
    cancelChangeBrief.mockReset().mockResolvedValue({ id: "job-1", status: "cancelled" });
    openChangeBriefStream.mockReset().mockReturnValue(vi.fn());
    fetchReport.mockReset().mockResolvedValue({ status: "completed", id: "x", report: undefined });
  });

  it("defaults to report mode and offers the Compare action once two reports load", async () => {
    renderWithProviders(<ChangeBriefSection ticker="AAPL" />);
    expect(await screen.findByText("Baseline report (earlier)")).toBeInTheDocument();
    expect(screen.getAllByRole("combobox")).toHaveLength(2);
    expect(screen.getByRole("button", { name: "Compare" })).toBeDisabled();
  });

  it("shows an empty-state hint when fewer than two reports exist, never a broken picker", async () => {
    fetchReportsForTicker.mockReset().mockResolvedValue({ reports: [] });
    renderWithProviders(<ChangeBriefSection ticker="AAPL" />);
    expect(await screen.findByText(/Generate at least two research reports/)).toBeInTheDocument();
  });

  it("switching to period mode shows the financial-period pickers instead", async () => {
    fetchFinancialStatements.mockResolvedValue({
      ticker: "AAPL",
      period_type: "annual",
      statements: {
        income: {
          acquisition_state: "available",
          periods: [
            {
              period_end: "2023-09-30",
              fiscal_year: "2023",
              currency: "USD",
              source: "s",
              fetched_at: "t",
              metrics: [],
            },
            {
              period_end: "2024-09-30",
              fiscal_year: "2024",
              currency: "USD",
              source: "s",
              fetched_at: "t",
              metrics: [],
            },
          ],
        },
        balance_sheet: { acquisition_state: "not_yet_acquired", periods: [] },
        cash_flow: { acquisition_state: "not_yet_acquired", periods: [] },
      },
    });
    const { user } = renderWithProviders(<ChangeBriefSection ticker="AAPL" />);
    await user.click(screen.getByRole("button", { name: "Compare Financial Periods" }));
    expect(await screen.findByText("Baseline period (earlier)")).toBeInTheDocument();
    expect(screen.getByText("Current period (later)")).toBeInTheDocument();

    const periodCombos = screen.getAllByRole("combobox");
    await user.click(periodCombos[2]); // period type, statement, then baseline period select
    expect(await screen.findByRole("option", { name: /2023-09-30/ })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: /2024-09-30/ })).toBeInTheDocument();
  });

  it("runs the report-mode compute → completed lifecycle end to end", async () => {
    createChangeBrief.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const { user } = renderWithProviders(<ChangeBriefSection ticker="AAPL" />);
    await screen.findByText("Baseline report (earlier)");

    const combos = screen.getAllByRole("combobox");
    await user.click(combos[0]);
    await user.click(await screen.findByRole("option", { name: /Q2 check-in/ }));
    await user.click(combos[1]);
    await user.click(await screen.findByRole("option", { name: /Q3 check-in/ }));

    expect(screen.getByRole("button", { name: "Compare" })).toBeEnabled();
    await user.click(screen.getByRole("button", { name: "Compare" }));

    expect(createChangeBrief).toHaveBeenCalledWith("AAPL", {
      comparison_type: "report",
      baseline_report_id: "rb",
      current_report_id: "rc",
    });

    await waitFor(() => expect(openChangeBriefStream).toHaveBeenCalled());
    expect(screen.getByText("Computing the change brief…")).toBeInTheDocument();

    const handlers = lastStreamHandlers();
    handlers.onEvent({ node: "pipeline", status: "start", message: "Computing change brief" });
    handlers.onEvent({ node: "pipeline", status: "ok" });
    handlers.onEvent({ node: "final", status: "ok", changes: CHANGES_PAYLOAD });
    handlers.onEnd();

    expect(await screen.findByText("Guidance cut")).toBeInTheDocument();
  });

  it("disables Compare when the same report is picked for both sides", async () => {
    const { user } = renderWithProviders(<ChangeBriefSection ticker="AAPL" />);
    await screen.findByText("Baseline report (earlier)");
    const combos = screen.getAllByRole("combobox");
    await user.click(combos[0]);
    await user.click(await screen.findByRole("option", { name: /Q2 check-in/ }));
    await user.click(combos[1]);
    await user.click(await screen.findByRole("option", { name: /Q2 check-in/ }));

    expect(screen.getByRole("button", { name: "Compare" })).toBeDisabled();
    expect(screen.getByText(/must be two different reports/)).toBeInTheDocument();
  });

  it("surfaces a failed run honestly, with retry", async () => {
    createChangeBrief.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const { user } = renderWithProviders(<ChangeBriefSection ticker="AAPL" />);
    await screen.findByText("Baseline report (earlier)");
    const combos = screen.getAllByRole("combobox");
    await user.click(combos[0]);
    await user.click(await screen.findByRole("option", { name: /Q2 check-in/ }));
    await user.click(combos[1]);
    await user.click(await screen.findByRole("option", { name: /Q3 check-in/ }));
    await user.click(screen.getByRole("button", { name: "Compare" }));
    await waitFor(() => expect(openChangeBriefStream).toHaveBeenCalled());

    lastStreamHandlers().onEvent({
      node: "pipeline",
      status: "error",
      message: "Change brief failed. See server logs for details.",
    });

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Change brief failed. See server logs for details.",
    );
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("cancelling stops the run and reports it honestly, without waiting on the server", async () => {
    createChangeBrief.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const closeStream = vi.fn();
    openChangeBriefStream.mockReturnValue(closeStream);
    const { user } = renderWithProviders(<ChangeBriefSection ticker="AAPL" />);
    await screen.findByText("Baseline report (earlier)");
    const combos = screen.getAllByRole("combobox");
    await user.click(combos[0]);
    await user.click(await screen.findByRole("option", { name: /Q2 check-in/ }));
    await user.click(combos[1]);
    await user.click(await screen.findByRole("option", { name: /Q3 check-in/ }));
    await user.click(screen.getByRole("button", { name: "Compare" }));
    await waitFor(() => expect(openChangeBriefStream).toHaveBeenCalled());

    await user.click(screen.getByRole("button", { name: "Stop" }));

    expect(closeStream).toHaveBeenCalled();
    expect(cancelChangeBrief).toHaveBeenCalledWith("AAPL", "job-1");
    expect(await screen.findByText("Change brief was cancelled.")).toBeInTheDocument();
  });

  it("has no detectable accessibility violations in the idle state", async () => {
    const { container } = renderWithProviders(<ChangeBriefSection ticker="AAPL" />);
    await screen.findByText("Baseline report (earlier)");
    expect(await axe(container)).toHaveNoViolations();
  });
});
