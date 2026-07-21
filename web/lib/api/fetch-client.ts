import type { z } from "zod";
import { clientEnv } from "@/lib/config/env";
import { AppError, appErrorFromStatus } from "@/lib/errors/app-error";

/**
 * The integration layer's single typed request path (03.3 AD-1/AD-3). No
 * component, feature UI, or store may call `fetch` directly — everything
 * routes through here so the trust boundary (validation, error
 * normalization) is enforced in one place. No endpoints are defined yet
 * (Phase 5 scope: infrastructure only, no backend integration).
 */

interface ApiFetchOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
}

/**
 * Issues a request against the backend contract and validates the response
 * with the given Zod schema (03.3 AD-3 — untrusted until validated; 03.3 AD-4
 * fail fast on invalid data). Failures are normalized to `AppError`.
 */
export async function apiFetch<Schema extends z.ZodType>(
  path: string,
  schema: Schema,
  options: ApiFetchOptions = {},
): Promise<z.infer<Schema>> {
  const { body, headers, ...rest } = options;

  let response: Response;
  try {
    response = await fetch(`${clientEnv.NEXT_PUBLIC_API_BASE_URL}${path}`, {
      ...rest,
      // Session context travels as a backend-managed cookie, never a
      // JS-accessible token (03.6 AD-3).
      credentials: "include",
      headers: {
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (cause) {
    throw new AppError("network", "Unable to reach the server.", { cause });
  }

  if (!response.ok) {
    let message: string | undefined;
    try {
      const errorBody = (await response.json()) as { message?: string };
      message = errorBody.message;
    } catch {
      // Non-JSON error body — fall back to the status-derived message.
    }
    throw appErrorFromStatus(response.status, message);
  }

  const json = await response.json();
  const parsed = schema.safeParse(json);
  if (!parsed.success) {
    throw new AppError("validation", "Response failed validation at the trust boundary.", {
      cause: parsed.error,
    });
  }

  return parsed.data;
}
