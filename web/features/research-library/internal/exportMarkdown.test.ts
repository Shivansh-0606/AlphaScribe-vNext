import { describe, expect, it } from "vitest";
import type { ReportDoc } from "../integration/schemas";
import { buildExportMarkdown } from "./exportMarkdown";

const REPORT: ReportDoc = {
  id: "report-1",
  ticker: "AAPL",
  query: "Summarize the latest quarter",
  created_at: "2026-01-01T00:00:00Z",
  draft_report: "Revenue grew 12% [1].",
  source_documents: [
    {
      doc_id: "d1",
      ticker: "AAPL",
      source: "10-Q FY24 Q3",
      chunk_idx: 0,
      text: "Full text.",
      score: 0.9,
    },
  ],
  scorecard: { overall: 1 },
  company_name: "Apple Inc.",
};

describe("buildExportMarkdown", () => {
  it("preserves both the reasoning (draft_report) and the sources (J-06)", () => {
    const markdown = buildExportMarkdown(REPORT);
    expect(markdown).toContain("Revenue grew 12% [1].");
    expect(markdown).toContain("10-Q FY24 Q3");
    expect(markdown).toContain("Full text.");
    expect(markdown).toContain("Apple Inc.");
  });
});
