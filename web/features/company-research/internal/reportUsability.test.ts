import { describe, expect, it } from "vitest";
import type { ReportDoc } from "../integration/schemas";
import { isUsableReport } from "./reportUsability";

const BASE: ReportDoc = {
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

describe("isUsableReport", () => {
  it("is usable with real brief text and at least one source", () => {
    expect(isUsableReport(BASE)).toBe(true);
  });

  it("is not usable with an empty draft_report", () => {
    expect(isUsableReport({ ...BASE, draft_report: "" })).toBe(false);
  });

  it("is not usable with a whitespace-only draft_report", () => {
    expect(isUsableReport({ ...BASE, draft_report: "   \n\t  " })).toBe(false);
  });

  it("is not usable with real brief text but zero sources (Law 3 — never unsourced)", () => {
    expect(isUsableReport({ ...BASE, source_documents: [] })).toBe(false);
  });
});
