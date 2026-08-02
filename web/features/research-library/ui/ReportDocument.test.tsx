import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import type { ReportDoc } from "../integration/schemas";
import { ReportDocument } from "./ReportDocument";

const REPORT: ReportDoc = {
  id: "report-1",
  ticker: "AAPL",
  query: "Summarize the latest quarter",
  created_at: "2026-01-01T00:00:00Z",
  draft_report: "Revenue grew 12% [1].",
  source_documents: [
    { doc_id: "d1", ticker: "AAPL", source: "10-Q FY24 Q3", chunk_idx: 0, text: "…", score: 0.9 },
  ],
  scorecard: { overall: 1 },
};

const noop = () => {};

describe("ReportDocument", () => {
  it("shows a loader while pending", () => {
    renderWithProviders(
      <ReportDocument report={undefined} isLoading error={null} onRetry={noop} />,
    );
    expect(screen.getByText("Loading the report…")).toBeInTheDocument();
  });

  it("offers retry on a fetch error", async () => {
    const onRetry = vi.fn();
    const { user } = renderWithProviders(
      <ReportDocument
        report={null}
        isLoading={false}
        error={new Error("boom")}
        onRetry={onRetry}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  // Same Trust-First guarantee as `AIResponseCard` — a fetched report can
  // still be unusable (empty/unsourced); Report View must not render it as a
  // normal success just because the fetch itself succeeded.
  it("renders the honest failure state for an unusable report, not a normal document", () => {
    renderWithProviders(
      <ReportDocument
        report={{ ...REPORT, draft_report: "" }}
        isLoading={false}
        error={null}
        onRetry={noop}
      />,
    );
    expect(screen.getByRole("alert")).toHaveTextContent(
      /finished without producing a usable result/,
    );
    expect(screen.queryByRole("heading", { name: "Sources" })).not.toBeInTheDocument();
  });

  it("renders content, sources, and confidence for a usable report (never without sources — Law 3)", () => {
    renderWithProviders(
      <ReportDocument report={REPORT} isLoading={false} error={null} onRetry={noop} />,
    );
    expect(screen.getByRole("heading", { name: "AAPL" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Sources" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "[1] 10-Q FY24 Q3" })).toBeInTheDocument();
    expect(screen.getByText("Well-supported")).toBeInTheDocument();
  });

  it("Export downloads the report as markdown", async () => {
    const createObjectURL = vi.fn().mockReturnValue("blob:mock");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { ...URL, createObjectURL, revokeObjectURL });
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    const { user } = renderWithProviders(
      <ReportDocument report={REPORT} isLoading={false} error={null} onRetry={noop} />,
    );
    await user.click(screen.getByRole("button", { name: "Export" }));

    expect(createObjectURL).toHaveBeenCalledOnce();
    expect(clickSpy).toHaveBeenCalledOnce();
    expect(await screen.findByRole("button", { name: "Exported" })).toBeInTheDocument();

    clickSpy.mockRestore();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <ReportDocument report={REPORT} isLoading={false} error={null} onRetry={noop} />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
