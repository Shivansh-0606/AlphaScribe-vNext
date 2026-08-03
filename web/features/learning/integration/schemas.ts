import { z } from "zod";

/**
 * FRONTEND/BACKEND CONTRACT — NOT YET IMPLEMENTED SERVER-SIDE.
 *
 * Per CTO direction (Milestone 3 Phase 8), Learning is a cross-functional
 * feature: Frontend Engineering builds the complete UI/integration layer
 * against this proposed contract now; a separate Backend & AI phase
 * implements the actual grounded-explanation service (retrieval, prompting,
 * source generation) behind these exact shapes. Until that phase lands,
 * every call in `integration/api.ts` will 404 against the real backend —
 * that is expected, not a bug (see `Feature_Parity_Tracker.md` Phase 8 for
 * how this was live-verified: the honest "backend unavailable" path, not the
 * happy path, since the happy path has nothing to call yet).
 *
 * Modeled deliberately on the already-implemented `/reports/generate` +
 * `/reports/{id}/stream` + `/reports/{id}` lifecycle
 * (`company-research/integration/schemas.ts`) — same start → SSE stream →
 * fetch-final-doc flow, same `{node, status, message}` event shape — because
 * the frozen UX spec (`06_UX_Specifications.md` SCR-08) requires the
 * identical "AI Thinking → AI Streaming" loading behavior, and handing the
 * backend team a pattern they've already built once is far easier to
 * implement against than a bespoke one. Two node names are proposed below
 * (`retriever`, `explainer`) as the minimal shape; the backend team may
 * rename/restructure as long as the `pipeline`-wrapper + `final` convention
 * (used identically by the real report pipeline) is preserved.
 */

export const explainRequestSchema = z.object({
  ticker: z.string().max(20),
  concept: z.string().max(500),
  /** Set when entering from Company Research's "Explain This" (SCR-06) — grounds the explanation in that report's actual figures, not just the ticker generally. */
  context_report_id: z.string().optional(),
  llm_provider: z.string().optional(),
  llm_api_key: z.string().optional(),
  llm_base_url: z.string().optional(),
  llm_model: z.string().optional(),
});
export type ExplainRequestBody = z.infer<typeof explainRequestSchema>;

export const explainResponseSchema = z.object({
  id: z.string(),
});

export const sourceDocumentSchema = z.object({
  doc_id: z.string(),
  ticker: z.string(),
  source: z.string(),
  chunk_idx: z.number(),
  text: z.string(),
  score: z.number(),
});
export type SourceDocument = z.infer<typeof sourceDocumentSchema>;

/** `explanation` uses the same `[n]` citation-marker convention as a report's `draft_report` (`@/lib/markdown/citations`) — Law 3 (never ungrounded) applies here exactly as it does to a research brief. */
export const explanationDocSchema = z.object({
  id: z.string(),
  ticker: z.string(),
  concept: z.string(),
  explanation: z.string(),
  source_documents: z.array(sourceDocumentSchema),
  company_name: z.string().nullable().optional(),
  created_at: z.string(),
});
export type ExplanationDoc = z.infer<typeof explanationDocSchema>;

export const explanationStatusResponseSchema = z.object({
  status: z.string(),
  id: z.string(),
  explanation: explanationDocSchema.optional(),
});
export type ExplanationStatusResponse = z.infer<typeof explanationStatusResponseSchema>;

export const cancelExplainResponseSchema = z.object({
  id: z.string(),
  status: z.string(),
});

export const streamEventSchema = z.object({
  node: z.string(),
  status: z.string(),
  message: z.string().optional(),
  explanation: explanationDocSchema.optional(),
});
export type StreamEvent = z.infer<typeof streamEventSchema>;
