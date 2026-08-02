import { clientEnv } from "@/lib/config/env";
import { AppError } from "@/lib/errors/app-error";

/**
 * The integration layer's server-sent-events counterpart to `fetch-client.ts`
 * (03.3 AD-1/AD-3, 03.13 AD-2 "integration layer owns the streaming
 * boundary"). Generic on purpose — it only frames transport, leaving
 * JSON-parsing and Zod validation of each event to the feature that owns the
 * contract (see `company-research/integration/api.ts`).
 *
 * Backend framing (`GET /reports/{id}/stream`, `backend/server.py`): default
 * `data:` messages, a `: keepalive` comment every 120s (ignored by
 * `EventSource` natively — comments never fire `onmessage`), and a terminal
 * named `event: end` once the stream is done. Native `EventSource` is used
 * rather than a hand-rolled `fetch` reader since the endpoint is a GET and
 * `withCredentials` covers the same session-cookie boundary `apiFetch` uses
 * via `credentials: "include"`.
 */

interface SseHandlers {
  onMessage: (raw: unknown) => void;
  onEnd: () => void;
  onError: (error: AppError) => void;
}

/** Opens the stream and returns a disposer to close it early (e.g. on unmount or cancel). */
export function openEventStream(path: string, handlers: SseHandlers): () => void {
  const source = new EventSource(`${clientEnv.NEXT_PUBLIC_API_BASE_URL}${path}`, {
    withCredentials: true,
  });

  source.onmessage = (event) => {
    try {
      handlers.onMessage(JSON.parse(event.data));
    } catch (cause) {
      handlers.onError(new AppError("validation", "Received a malformed stream event.", { cause }));
    }
  };

  source.addEventListener("end", () => {
    handlers.onEnd();
    source.close();
  });

  // Closing in the "end" handler above sets readyState to CLOSED first, so a
  // graceful end never also reports as a network error here.
  source.onerror = () => {
    handlers.onError(new AppError("network", "The connection to the server was lost."));
  };

  return () => source.close();
}
