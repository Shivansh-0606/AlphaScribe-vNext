import { z } from "zod";

/**
 * Request/response shapes for the `company-research` feature's backend
 * contract (backend/server.py `/ingest/*`, `/reports/generate`,
 * `/reports/{id}/stream`, `/reports/{id}`, `/reports/{id}/cancel`). Field
 * names are verbatim from the Pydantic models/TypedDicts — this is the trust
 * boundary (03.3 AD-3); nothing beyond this module assumes a shape without
 * validating it first.
 */

// ---- Ingest --------------------------------------------------------------

export const ingestResultSchema = z.object({
  doc_id: z.string(),
  ticker: z.string(),
  company_name: z.string().nullable().optional(),
  source: z.string(),
  num_chunks: z.number(),
  char_count: z.number(),
});
export type IngestResult = z.infer<typeof ingestResultSchema>;

export const ingestTextRequestSchema = z.object({
  ticker: z.string().max(20),
  source: z.string().max(200),
  text: z.string().max(1_000_000),
  company_name: z.string().max(200).optional(),
});
export type IngestTextRequestBody = z.infer<typeof ingestTextRequestSchema>;

export const ingestEdgarRequestSchema = z.object({
  ticker: z.string().max(20),
  form_type: z.string().max(20).default("10-Q"),
});
export type IngestEdgarRequestBody = z.infer<typeof ingestEdgarRequestSchema>;

export const ingestEdgarResultSchema = ingestResultSchema.extend({
  url: z.string().nullable().optional(),
});

export const ingestSamplesResponseSchema = z.object({
  ingested: z.array(ingestResultSchema),
  total_samples: z.number(),
});

// ---- Report document -------------------------------------------------------

export const extractedFinancialsSchema = z.object({
  revenue: z.string().nullable().optional(),
  revenue_yoy: z.string().nullable().optional(),
  eps: z.string().nullable().optional(),
  net_income: z.string().nullable().optional(),
  guidance: z.string().nullable().optional(),
  operating_margin: z.string().nullable().optional(),
  free_cash_flow: z.string().nullable().optional(),
});
export type ExtractedFinancials = z.infer<typeof extractedFinancialsSchema>;

// All fields optional (not just the whole object) — confirmed live that the
// tone node can leave this as `{}` rather than absent when it fails
// (agents/nodes.py), same as `extracted_data`. A `.optional()` object schema
// alone does NOT tolerate that: Zod still validates present-but-empty `{}`
// against the inner required fields and fails the *entire* report parse.
export const toneAnalysisSchema = z.object({
  sentiment: z.string().optional(),
  confidence: z.number().optional(),
  summary: z.string().optional(),
  key_risks: z.array(z.string()).optional(),
  key_positives: z.array(z.string()).optional(),
});
export type ToneAnalysis = z.infer<typeof toneAnalysisSchema>;

export const sourceDocumentSchema = z.object({
  doc_id: z.string(),
  ticker: z.string(),
  source: z.string(),
  chunk_idx: z.number(),
  text: z.string(),
  score: z.number(),
});
export type SourceDocument = z.infer<typeof sourceDocumentSchema>;

export const scorecardSchema = z.object({
  faithfulness: z.number(),
  context_precision: z.number(),
  answer_relevance: z.number(),
  overall: z.number(),
  cited_sources: z.array(z.number()),
  n_claims: z.number(),
  n_supported: z.number(),
});
export type Scorecard = z.infer<typeof scorecardSchema>;

export const reportDocSchema = z.object({
  id: z.string(),
  ticker: z.string(),
  query: z.string(),
  created_at: z.string(),
  draft_report: z.string(),
  extracted_data: extractedFinancialsSchema.optional(),
  sentiment_analysis: toneAnalysisSchema.optional(),
  source_documents: z.array(sourceDocumentSchema),
  fact_check_status: z.boolean(),
  validation_errors: z.array(z.string()),
  retry_count: z.number(),
  scorecard: scorecardSchema,
  company_name: z.string().nullable().optional(),
  is_sample: z.boolean().optional(),
});
export type ReportDoc = z.infer<typeof reportDocSchema>;

// ---- Report generation -----------------------------------------------------

export const generateReportRequestSchema = z.object({
  ticker: z.string().max(20),
  query: z.string().max(2000),
  context_report_id: z.string().optional(),
  llm_provider: z.string().optional(),
  llm_api_key: z.string().optional(),
  llm_base_url: z.string().optional(),
  llm_model: z.string().optional(),
  no_cache: z.boolean().optional(),
});
export type GenerateReportRequestBody = z.infer<typeof generateReportRequestSchema>;

export const generateReportResponseSchema = z.object({
  job_id: z.string(),
  cached: z.boolean().optional(),
});
export type GenerateReportResponse = z.infer<typeof generateReportResponseSchema>;

export const cancelReportResponseSchema = z.object({
  job_id: z.string(),
  status: z.string(),
  note: z.string().optional(),
});

/**
 * `GET /reports/{id}` returns one of three shapes depending on job state
 * (completed/in-flight/in-flight-after-restart) — modeled loosely rather
 * than as a strict discriminated union since only `status` is common to all
 * three (server.py:1009-1027).
 */
export const reportStatusResponseSchema = z.object({
  status: z.string(),
  id: z.string(),
  report: reportDocSchema.optional(),
  events: z.array(z.record(z.string(), z.unknown())).optional(),
});
export type ReportStatusResponse = z.infer<typeof reportStatusResponseSchema>;

// ---- Filings (metadata only — see `backend/agents/ingest.py`: only text
// chunks + this metadata are persisted, never structured/numeric data or
// the reconstructed full document) -----------------------------------------

export const filingSchema = z.object({
  doc_id: z.string(),
  ticker: z.string(),
  company_name: z.string().nullable().optional(),
  source: z.string(),
  num_chunks: z.number(),
  char_count: z.number(),
  created_at: z.string(),
});
export type Filing = z.infer<typeof filingSchema>;

export const filingsResponseSchema = z.object({
  filings: z.array(filingSchema),
});

// ---- Financials acquisition (backend/server.py POST
// /companies/{ticker}/financials/acquire — Document 33 Amendment, frozen
// wire contract; backend/domain/financials.py AcquisitionOutcome) ----------

export const financialsAcquireResponseSchema = z.object({
  ticker: z.string(),
  period_type: z.enum(["annual", "quarterly"]),
  outcome: z.enum(["requested", "available", "confirmed_unavailable", "mixed"]),
});
export type FinancialsAcquireResponse = z.infer<typeof financialsAcquireResponseSchema>;

// ---- Financials read (backend/server.py GET /companies/{ticker}/financials
// — Document 33 §1-§10, CTO-ratified Round 7; backend/domain/financials.py
// FinancialStatement/Metric/AcquisitionOutcome) -----------------------------

export const financialMetricSchema = z.object({
  canonical_metric: z.string().nullable(),
  provider_label: z.string(),
  value: z.number(),
  unit: z.enum(["currency", "currency_per_share", "shares", "ratio", "percentage", "count"]),
});
export type FinancialMetric = z.infer<typeof financialMetricSchema>;

// periods[] arrives period_end descending (most recent first) — Document 33
// §6.2, a backend contract guarantee, not re-sorted client-side.
export const financialPeriodSchema = z.object({
  period_end: z.string(),
  fiscal_year: z.string(),
  currency: z.string(),
  source: z.string(),
  fetched_at: z.string(),
  metrics: z.array(financialMetricSchema),
});
export type FinancialPeriod = z.infer<typeof financialPeriodSchema>;

export const financialStatementGroupSchema = z.object({
  acquisition_state: z.enum(["not_yet_acquired", "available", "confirmed_unavailable"]),
  periods: z.array(financialPeriodSchema),
});
export type FinancialStatementGroup = z.infer<typeof financialStatementGroupSchema>;

export const financialsResponseSchema = z.object({
  ticker: z.string(),
  period_type: z.enum(["annual", "quarterly"]),
  statements: z.object({
    income: financialStatementGroupSchema,
    balance_sheet: financialStatementGroupSchema,
    cash_flow: financialStatementGroupSchema,
  }),
});
export type FinancialsResponse = z.infer<typeof financialsResponseSchema>;

// ---- SSE stream events -----------------------------------------------------

/**
 * Both event families the stream emits (pipeline wrapper events and
 * per-node trace events, server.py:970-1006 / agents/nodes.py `_event`) share
 * `node`/`status`/`message`/`ts`; everything else is family-specific extra
 * data, kept optional rather than split into a discriminated union since the
 * UI only ever branches on `node`+`status`.
 */
export const streamEventSchema = z.object({
  node: z.string(),
  status: z.string(),
  message: z.string().optional(),
  ts: z.string().optional(),
  report: reportDocSchema.optional(),
  count: z.number().optional(),
  stages: z.array(z.string()).optional(),
  total_chunks: z.number().optional(),
  flagged: z.number().optional(),
  total: z.number().optional(),
  fact_check_status: z.boolean().optional(),
  retry_count: z.number().optional(),
});
export type StreamEvent = z.infer<typeof streamEventSchema>;
