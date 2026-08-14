import { apiFetch } from "@/lib/api/fetch-client";
import { openEventStream } from "@/lib/api/sse-client";
import { AppError } from "@/lib/errors/app-error";
import {
  cancelReportResponseSchema,
  filingsResponseSchema,
  financialsAcquireResponseSchema,
  generateReportRequestSchema,
  generateReportResponseSchema,
  ingestEdgarRequestSchema,
  ingestEdgarResultSchema,
  ingestSamplesResponseSchema,
  ingestTextRequestSchema,
  ingestResultSchema,
  reportStatusResponseSchema,
  streamEventSchema,
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

/** `period_type` is a required query param on this route, not a body field (Document 33 Amendment, frozen). */
export function acquireFinancials(ticker: string, periodType: "annual" | "quarterly") {
  const params = new URLSearchParams({ period_type: periodType });
  return apiFetch(
    `/api/companies/${encodeURIComponent(ticker)}/financials/acquire?${params.toString()}`,
    financialsAcquireResponseSchema,
    { method: "POST" },
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
