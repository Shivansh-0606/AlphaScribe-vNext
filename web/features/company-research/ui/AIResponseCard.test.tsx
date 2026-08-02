import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import type { ReportDoc } from "../integration/schemas";
import { AIResponseCard } from "./AIResponseCard";

const REPORT: ReportDoc = {
  id: "job-1",
  ticker: "AAPL",
  query: "q",
  created_at: "2026-01-01T00:00:00Z",
  draft_report: "Revenue grew 12% [1].",
  source_documents: [
    { doc_id: "d1", ticker: "AAPL", source: "10-Q FY24 Q3", chunk_idx: 0, text: "…", score: 0.9 },
  ],
  fact_check_status: true,
  validation_errors: [],
  retry_count: 0,
  scorecard: {
    faithfulness: 1,
    context_precision: 1,
    answer_relevance: 1,
    overall: 1,
    cited_sources: [1],
    n_claims: 1,
    n_supported: 1,
  },
};

describe("AIResponseCard", () => {
  it("renders a custom heading (used for Copilot follow-up answers)", () => {
    renderWithProviders(<AIResponseCard report={REPORT} heading="Follow-up answer" />);
    expect(screen.getByText("Follow-up answer")).toBeInTheDocument();
  });

  it("AI Action Toolbar: Copy places the brief text on the clipboard and confirms", async () => {
    const { user } = renderWithProviders(<AIResponseCard report={REPORT} />);
    // `renderWithProviders`' `userEvent.setup()` already provides a
    // jsdom-emulated `navigator.clipboard` — spy on the real thing rather
    // than pre-stubbing the property, which user-event's own setup clobbers.
    const writeText = vi.spyOn(navigator.clipboard, "writeText").mockResolvedValue(undefined);

    await user.click(screen.getByRole("button", { name: "Copy" }));

    expect(writeText).toHaveBeenCalledWith(REPORT.draft_report);
    expect(await screen.findByRole("button", { name: "Copied" })).toBeInTheDocument();
  });

  it("never renders without sources (Law 3)", () => {
    renderWithProviders(<AIResponseCard report={REPORT} />);
    expect(screen.getByRole("heading", { name: "Sources" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "[1] 10-Q FY24 Q3" })).toBeInTheDocument();
  });

  // Trust-First regression: `status: "completed"` only means the backend
  // pipeline didn't error — it does not mean the pipeline produced anything
  // worth reading. Confirmed live: a run can complete with an empty brief
  // when the LLM provider fails mid-run. A "completed" report must never
  // render as if it were a normal success just because the job didn't fail.
  describe("unusable completed reports (isUsableReport gate)", () => {
    it.each([
      ["empty draft_report / missing AI summary", { draft_report: "" }],
      ["whitespace-only draft_report", { draft_report: "   \n\t  " }],
      ["missing renderable sections (real brief, no sources)", { source_documents: [] }],
    ])("renders the honest failure state, not a normal brief: %s", (_label, overrides) => {
      renderWithProviders(<AIResponseCard report={{ ...REPORT, ...overrides }} />);

      expect(screen.getByRole("alert")).toHaveTextContent(
        /didn't produce a usable result|no trustworthy AI summary/,
      );
      expect(screen.queryByText("AI Research Brief")).not.toBeInTheDocument();
      expect(screen.queryByRole("heading", { name: "Sources" })).not.toBeInTheDocument();
      expect(screen.queryByRole("button", { name: "Copy" })).not.toBeInTheDocument();
    });

    it("never fabricates a Confidence Indicator for an unusable report", () => {
      renderWithProviders(<AIResponseCard report={{ ...REPORT, draft_report: "" }} />);
      expect(
        screen.queryByText(/Well-supported|Limited evidence|Not enough evidence/),
      ).not.toBeInTheDocument();
    });

    it("offers the caller's retry action when provided", async () => {
      const onRetry = vi.fn();
      const { user } = renderWithProviders(
        <AIResponseCard report={{ ...REPORT, draft_report: "" }} onRetry={onRetry} />,
      );
      await user.click(screen.getByRole("button", { name: "Retry" }));
      expect(onRetry).toHaveBeenCalledOnce();
    });

    it("shows no action when the caller doesn't provide onRetry, rather than a dead button", () => {
      renderWithProviders(<AIResponseCard report={{ ...REPORT, draft_report: "" }} />);
      expect(screen.queryByRole("button", { name: "Retry" })).not.toBeInTheDocument();
    });
  });
});
