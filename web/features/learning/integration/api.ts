import { apiFetch } from "@/lib/api/fetch-client";
import { openEventStream } from "@/lib/api/sse-client";
import { AppError } from "@/lib/errors/app-error";
import {
  cancelExplainResponseSchema,
  explainRequestSchema,
  explainResponseSchema,
  explanationStatusResponseSchema,
  streamEventSchema,
  type ExplainRequestBody,
  type StreamEvent,
} from "./schemas";

/**
 * Feature-scoped API access (02.2 AD-1). Every path here is a PROPOSED
 * contract, not a live endpoint — see `schemas.ts`'s header comment. Calls
 * 404 until the Backend & AI phase implements them.
 */

export function requestExplanation(body: ExplainRequestBody) {
  return apiFetch("/api/learning/explain", explainResponseSchema, {
    method: "POST",
    body: explainRequestSchema.parse(body),
  });
}

export function fetchExplanation(id: string) {
  return apiFetch(`/api/learning/${id}`, explanationStatusResponseSchema);
}

export function cancelExplanation(id: string) {
  return apiFetch(`/api/learning/${id}/cancel`, cancelExplainResponseSchema, { method: "POST" });
}

/** Mirrors `openReportStream` (`company-research/integration/api.ts`) — same integration-layer streaming boundary (03.13 AD-2). */
export function openExplanationStream(
  id: string,
  handlers: {
    onEvent: (event: StreamEvent) => void;
    onEnd: () => void;
    onError: (error: AppError) => void;
  },
): () => void {
  return openEventStream(`/api/learning/${id}/stream`, {
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
