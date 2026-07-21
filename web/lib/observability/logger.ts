/**
 * Tool-agnostic observability seam (05.3 — privacy-safe diagnostics only,
 * never PII/credentials/research bodies). A thin wrapper, not a vendor SDK:
 * swapping in a real sink (Sentry/Datadog/etc.) later means changing this
 * one file, not every call site (§4.12 stable interface).
 */

type LogFields = Record<string, unknown>;

function emit(level: "debug" | "info" | "warn" | "error", message: string, fields?: LogFields) {
  console[level](`[${level}] ${message}`, fields ?? "");
}

export const logger = {
  debug: (message: string, fields?: LogFields) => emit("debug", message, fields),
  info: (message: string, fields?: LogFields) => emit("info", message, fields),
  warn: (message: string, fields?: LogFields) => emit("warn", message, fields),
  error: (message: string, fields?: LogFields) => emit("error", message, fields),
};
