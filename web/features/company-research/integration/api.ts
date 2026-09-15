import { apiFetch } from "@/lib/api/fetch-client";
import { openEventStream } from "@/lib/api/sse-client";
import { AppError } from "@/lib/errors/app-error";
import {
  cancelChangeBriefResponseSchema,
  cancelFilingAnalysisResponseSchema,
  cancelReportResponseSchema,
  changeBriefStatusResponseSchema,
  changeBriefStreamEventSchema,
  createChangeBriefRequestSchema,
  createChangeBriefResponseSchema,
  createFilingAnalysisRequestSchema,
  createFilingAnalysisResponseSchema,
  createFilingQARequestSchema,
  filingAnalysisStatusResponseSchema,
  filingAnalysisStreamEventSchema,
  filingContentResponseSchema,
  filingQAStatusResponseSchema,
  filingQAStreamEventSchema,
  filingsResponseSchema,
  financialsAcquireResponseSchema,
  financialsResponseSchema,
  generateReportRequestSchema,
  generateReportResponseSchema,
  ingestEdgarRequestSchema,
  ingestEdgarResultSchema,
  ingestSamplesResponseSchema,
  ingestTextRequestSchema,
  ingestResultSchema,
  reportsListResponseSchema,
  reportStatusResponseSchema,
  streamEventSchema,
  type ChangeBriefStreamEvent,
  type CreateChangeBriefRequestBody,
  type CreateFilingAnalysisRequestBody,
  type CreateFilingQARequestBody,
  type FilingAnalysisStreamEvent,
  type FilingQAStreamEvent,
  type GenerateReportRequestBody,
  type IngestEdgarRequestBody,
  type IngestTextRequestBody,
  type StreamEvent,
} from "./schemas";

/** Feature-scoped API access (02.2 AD-1) — the only place `company-research` touches `apiFetch`/`openEventStream`. */

export function ingestText(body: IngestTextRequestBody) {
  return apiFetch("/api/ingest/text", ingestResultSchema, {
    method: "POST",
    body: ingestTextRequestSchema.parse(body),
  });
}

export function ingestEdgar(body: IngestEdgarRequestBody) {
  return apiFetch("/api/ingest/edgar", ingestEdgarResultSchema, {
    method: "POST",
    body: ingestEdgarRequestSchema.parse(body),
  });
}

export function ingestSamples() {
  return apiFetch("/api/ingest/samples", ingestSamplesResponseSchema, { method: "POST" });
}

export function generateReport(body: GenerateReportRequestBody) {
  return apiFetch("/api/reports/generate", generateReportResponseSchema, {
    method: "POST",
    body: generateReportRequestSchema.parse(body),
  });
}

export function fetchReport(jobId: string) {
  return apiFetch(`/api/reports/${jobId}`, reportStatusResponseSchema);
}

export function cancelReport(jobId: string) {
  return apiFetch(`/api/reports/${jobId}/cancel`, cancelReportResponseSchema, { method: "POST" });
}

export function fetchFilings(ticker: string) {
  const params = new URLSearchParams({ ticker });
  return apiFetch(`/api/filings?${params.toString()}`, filingsResponseSchema);
}

/**
 * M13 — GET /companies/{ticker}/filings/{doc_id}/content (Document 59,
 * CTO-ratified 2026-08-27). Company-namespaced read of an already-ingested
 * filing's persisted text chunks. An unknown `(ticker, doc_id)` returns 404,
 * normalised to an `AppError` here like any other request.
 */
export function fetchFilingContent(ticker: string, docId: string) {
  return apiFetch(
    `/api/companies/${encodeURIComponent(ticker)}/filings/${encodeURIComponent(docId)}/content`,
    filingContentResponseSchema,
  );
}

function filingBasePath(ticker: string, docId: string): string {
  return `/api/companies/${encodeURIComponent(ticker)}/filings/${encodeURIComponent(docId)}`;
}

/**
 * M14 — POST .../analysis (Document 64, CTO-ratified 2026-08-31). Creates an
 * async Filing Analysis job for one filing; body is the BYOK field set,
 * verbatim, always sent (the backend's own field is optional, but an empty
 * object round-trips through it identically).
 */
export function createFilingAnalysis(
  ticker: string,
  docId: string,
  body: CreateFilingAnalysisRequestBody = {},
) {
  return apiFetch(`${filingBasePath(ticker, docId)}/analysis`, createFilingAnalysisResponseSchema, {
    method: "POST",
    body: createFilingAnalysisRequestSchema.parse(body),
  });
}

export function fetchFilingAnalysis(ticker: string, docId: string, id: string) {
  return apiFetch(
    `${filingBasePath(ticker, docId)}/analysis/${encodeURIComponent(id)}`,
    filingAnalysisStatusResponseSchema,
  );
}

export function cancelFilingAnalysis(ticker: string, docId: string, id: string) {
  return apiFetch(
    `${filingBasePath(ticker, docId)}/analysis/${encodeURIComponent(id)}/cancel`,
    cancelFilingAnalysisResponseSchema,
    { method: "POST" },
  );
}

/** Mirrors `openReportStream` — same integration-layer streaming boundary (03.13 AD-2). */
export function openFilingAnalysisStream(
  ticker: string,
  docId: string,
  id: string,
  handlers: {
    onEvent: (event: FilingAnalysisStreamEvent) => void;
    onEnd: () => void;
    onError: (error: AppError) => void;
  },
): () => void {
  return openEventStream(
    `${filingBasePath(ticker, docId)}/analysis/${encodeURIComponent(id)}/stream`,
    {
      onMessage: (raw) => {
        const parsed = filingAnalysisStreamEventSchema.safeParse(raw);
        if (!parsed.success) {
          handlers.onError(
            new AppError("validation", "Received a malformed stream event.", {
              cause: parsed.error,
            }),
          );
          return;
        }
        handlers.onEvent(parsed.data);
      },
      onEnd: handlers.onEnd,
      onError: handlers.onError,
    },
  );
}

/**
 * M16 — POST .../qa (Document 87 R2, implemented `9035e27`). Creates an
 * async Filing Q&A job for one question about one filing; `question` is the
 * one required field (server-side 422 on empty/missing/too-long).
 */
export function createFilingQA(ticker: string, docId: string, body: CreateFilingQARequestBody) {
  return apiFetch(`${filingBasePath(ticker, docId)}/qa`, createFilingAnalysisResponseSchema, {
    method: "POST",
    body: createFilingQARequestSchema.parse(body),
  });
}

export function fetchFilingQA(ticker: string, docId: string, id: string) {
  return apiFetch(
    `${filingBasePath(ticker, docId)}/qa/${encodeURIComponent(id)}`,
    filingQAStatusResponseSchema,
  );
}

export function cancelFilingQA(ticker: string, docId: string, id: string) {
  return apiFetch(
    `${filingBasePath(ticker, docId)}/qa/${encodeURIComponent(id)}/cancel`,
    cancelFilingAnalysisResponseSchema,
    { method: "POST" },
  );
}

/** Mirrors `openFilingAnalysisStream` — same integration-layer streaming boundary (03.13 AD-2). */
export function openFilingQAStream(
  ticker: string,
  docId: string,
  id: string,
  handlers: {
    onEvent: (event: FilingQAStreamEvent) => void;
    onEnd: () => void;
    onError: (error: AppError) => void;
  },
): () => void {
  return openEventStream(`${filingBasePath(ticker, docId)}/qa/${encodeURIComponent(id)}/stream`, {
    onMessage: (raw) => {
      const parsed = filingQAStreamEventSchema.safeParse(raw);
      if (!parsed.success) {
        handlers.onError(
          new AppError("validation", "Received a malformed stream event.", { cause: parsed.error }),
        );
        return;
      }
      handlers.onEvent(parsed.data);
    },
    onEnd: handlers.onEnd,
    onError: handlers.onError,
  });
}

/** `GET /reports?ticker=` — the candidate list for M15's report-mode picker (Document 70 R4 §7). */
export function fetchReportsForTicker(ticker: string) {
  const params = new URLSearchParams({ ticker });
  return apiFetch(`/api/reports?${params.toString()}`, reportsListResponseSchema);
}

function changesBasePath(ticker: string): string {
  return `/api/companies/${encodeURIComponent(ticker)}/changes`;
}

/**
 * M15 — POST .../changes (Document 70 R4, implemented `f8c0664`). Creates an
 * async change-brief job in exactly one mode (`comparison_type`); the
 * request-shape validation rules (§9.4/§10.2/§15) are enforced server-side —
 * this layer only forwards the discriminated body verbatim.
 */
export function createChangeBrief(ticker: string, body: CreateChangeBriefRequestBody) {
  return apiFetch(changesBasePath(ticker), createChangeBriefResponseSchema, {
    method: "POST",
    body: createChangeBriefRequestSchema.parse(body),
  });
}

export function fetchChangeBrief(ticker: string, id: string) {
  return apiFetch(
    `${changesBasePath(ticker)}/${encodeURIComponent(id)}`,
    changeBriefStatusResponseSchema,
  );
}

export function cancelChangeBrief(ticker: string, id: string) {
  return apiFetch(
    `${changesBasePath(ticker)}/${encodeURIComponent(id)}/cancel`,
    cancelChangeBriefResponseSchema,
    { method: "POST" },
  );
}

/** Mirrors `openFilingAnalysisStream` — same integration-layer streaming boundary (03.13 AD-2). */
export function openChangeBriefStream(
  ticker: string,
  id: string,
  handlers: {
    onEvent: (event: ChangeBriefStreamEvent) => void;
    onEnd: () => void;
    onError: (error: AppError) => void;
  },
): () => void {
  return openEventStream(`${changesBasePath(ticker)}/${encodeURIComponent(id)}/stream`, {
    onMessage: (raw) => {
      const parsed = changeBriefStreamEventSchema.safeParse(raw);
      if (!parsed.success) {
        handlers.onError(
          new AppError("validation", "Received a malformed stream event.", { cause: parsed.error }),
        );
        return;
      }
      handlers.onEvent(parsed.data);
    },
    onEnd: handlers.onEnd,
    onError: handlers.onError,
  });
}

/** `period_type` is a required query param on this route, not a body field (Document 33 Amendment, frozen). */
export function acquireFinancials(ticker: string, periodType: "annual" | "quarterly") {
  const params = new URLSearchParams({ period_type: periodType });
  return apiFetch(
    `/api/companies/${encodeURIComponent(ticker)}/financials/acquire?${params.toString()}`,
    financialsAcquireResponseSchema,
    { method: "POST" },
  );
}

/** `period_type` is a required query param on this route too (Document 33 §6.1, frozen). */
export function fetchFinancialStatements(ticker: string, periodType: "annual" | "quarterly") {
  const params = new URLSearchParams({ period_type: periodType });
  return apiFetch(
    `/api/companies/${encodeURIComponent(ticker)}/financials?${params.toString()}`,
    financialsResponseSchema,
  );
}

/**
 * Opens the SSE trace stream for a running job (03.13 AD-2 — integration
 * layer owns the streaming boundary: validating arriving events before the
 * application layer ever sees them). Returns a disposer to close early.
 */
export function openReportStream(
  jobId: string,
  handlers: {
    onEvent: (event: StreamEvent) => void;
    onEnd: () => void;
    onError: (error: AppError) => void;
  },
): () => void {
  return openEventStream(`/api/reports/${jobId}/stream`, {
    onMessage: (raw) => {
      const parsed = streamEventSchema.safeParse(raw);
      if (!parsed.success) {
        handlers.onError(
          new AppError("validation", "Received a malformed stream event.", { cause: parsed.error }),
        );
        return;
      }
      handlers.onEvent(parsed.data);
    },
    onEnd: handlers.onEnd,
    onError: handlers.onError,
  });
}
