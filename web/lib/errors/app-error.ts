/**
 * Typed error vocabulary (03.3 AD-3 "error normalization" / 03.11 AD-3).
 *
 * Transport/protocol/domain failures are normalized into this small, closed
 * set — never left as raw fetch/parse exceptions — so every failure maps
 * predictably to a frozen State (13_States.md) at the UI layer. This is
 * infrastructure only: nothing here calls a real endpoint.
 */

export type AppErrorKind =
  | "network" // Offline / request never reached the server -> State: Offline
  | "timeout" // Exceeded a reasonable wait -> State: Timeout
  | "auth_required" // Session missing/expired -> State: Authentication Required
  | "permission_denied" // Backend-authoritative denial -> State: Permission Denied
  | "validation" // Response failed Zod validation at the boundary -> State: Error
  | "server" // 5xx / unexpected backend failure -> State: Error
  | "unknown"; // Anything not otherwise classified -> State: Error

export class AppError extends Error {
  readonly kind: AppErrorKind;
  /** Present for HTTP-sourced failures; absent for network/validation failures. */
  readonly status?: number;
  readonly cause?: unknown;

  constructor(kind: AppErrorKind, message: string, options?: { status?: number; cause?: unknown }) {
    super(message);
    this.name = "AppError";
    this.kind = kind;
    this.status = options?.status;
    this.cause = options?.cause;
  }
}

/** Maps an HTTP status to the closed error vocabulary (03.3 AD-3). */
export function appErrorFromStatus(status: number, message?: string): AppError {
  if (status === 401)
    return new AppError("auth_required", message ?? "Authentication required.", { status });
  if (status === 403)
    return new AppError("permission_denied", message ?? "Permission denied.", { status });
  if (status >= 500) return new AppError("server", message ?? "Server error.", { status });
  return new AppError("unknown", message ?? `Request failed with status ${status}.`, { status });
}
