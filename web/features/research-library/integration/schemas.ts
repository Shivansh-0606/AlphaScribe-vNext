import { z } from "zod";

/**
 * `research-library`'s own contract for `GET /reports/{id}` (backend/server.py
 * `get_report`, ~line 1019). Report View only ever reads a single,
 * already-generated report by id — it never generates, streams, or cancels
 * one (that's `company-research`'s contract). Declared independently rather
 * than importing `company-research`'s `reportDocSchema` (02.2 AD-3 — each
 * feature validates its own trust boundary; features don't import each
 * other's internals), and deliberately narrower: SCR-10's frozen scope is
 * "report content, preserved reasoning, source references" only — no
 * financial-metrics/sentiment fields, which `ReportDocument` doesn't render.
 */

export const sourceDocumentSchema = z.object({
  doc_id: z.string(),
  ticker: z.string(),
  source: z.string(),
  chunk_idx: z.number(),
  text: z.string(),
  score: z.number(),
});

export const scorecardSchema = z.object({
  overall: z.number(),
});

export const reportDocSchema = z.object({
  id: z.string(),
  ticker: z.string(),
  query: z.string(),
  created_at: z.string(),
  draft_report: z.string(),
  source_documents: z.array(sourceDocumentSchema),
  scorecard: scorecardSchema,
  company_name: z.string().nullable().optional(),
});
export type ReportDoc = z.infer<typeof reportDocSchema>;

export const reportStatusResponseSchema = z.object({
  status: z.string(),
  id: z.string(),
  report: reportDocSchema.optional(),
});
export type ReportStatusResponse = z.infer<typeof reportStatusResponseSchema>;
