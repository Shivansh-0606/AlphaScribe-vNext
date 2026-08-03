import { z } from "zod";

/**
 * `comparison`'s own contract for `GET /reports` and `POST /reports/compare`
 * (backend/server.py `list_reports` ~line 1040, `compare_reports` ~line
 * 1135). Declared independently rather than importing `research-library`'s
 * or `company-research`'s schemas for the same backend shapes (02.2 AD-3 —
 * each feature validates its own trust boundary; features don't import each
 * other's internals) — the list-row shape below is intentionally identical
 * to `research-library`'s `reportListItemSchema`, and the financials/
 * sentiment shapes mirror `company-research`'s, by the nature of both
 * hitting the same backend fields, not by sharing code.
 */

export const reportListItemSchema = z.object({
  id: z.string(),
  ticker: z.string(),
  query: z.string(),
  created_at: z.string(),
  company_name: z.string().nullable().optional(),
  is_sample: z.boolean().optional(),
});
export type ReportListItem = z.infer<typeof reportListItemSchema>;

export const reportsListResponseSchema = z.object({
  reports: z.array(reportListItemSchema),
});

/** Fixed 7-key shape (`agents/schemas.py` `FinancialsSchema`) — same key set for every report, `null` when not found; `{}` only when retrieval returned zero docs. */
export const extractedFinancialsSchema = z.object({
  revenue: z.string().nullable().optional(),
  revenue_yoy: z.string().nullable().optional(),
  eps: z.string().nullable().optional(),
  net_income: z.string().nullable().optional(),
  operating_margin: z.string().nullable().optional(),
  free_cash_flow: z.string().nullable().optional(),
  guidance: z.string().nullable().optional(),
});
export type ExtractedFinancials = z.infer<typeof extractedFinancialsSchema>;

export const sentimentAnalysisSchema = z.object({
  sentiment: z.string().optional(),
  summary: z.string().optional(),
});

export const comparisonReportSchema = z.object({
  id: z.string(),
  ticker: z.string(),
  query: z.string(),
  created_at: z.string(),
  company_name: z.string().nullable().optional(),
  is_sample: z.boolean().optional(),
  extracted_data: extractedFinancialsSchema.optional(),
  sentiment_analysis: sentimentAnalysisSchema.optional(),
  scorecard: z.object({ overall: z.number() }).optional(),
});
export type ComparisonReport = z.infer<typeof comparisonReportSchema>;

export const compareResponseSchema = z.object({
  reports: z.array(comparisonReportSchema),
});
