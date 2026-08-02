import { apiFetch } from "@/lib/api/fetch-client";
import { reportStatusResponseSchema, reportsListResponseSchema } from "./schemas";

/** Feature-scoped API access (02.2 AD-1) — the only place `research-library` touches `apiFetch`. */
export function fetchReport(id: string) {
  return apiFetch(`/api/reports/${id}`, reportStatusResponseSchema);
}

export function fetchReports(params: { ticker?: string; limit?: number } = {}) {
  const query = new URLSearchParams();
  if (params.ticker) query.set("ticker", params.ticker);
  if (params.limit) query.set("limit", String(params.limit));
  const qs = query.toString();
  return apiFetch(`/api/reports${qs ? `?${qs}` : ""}`, reportsListResponseSchema);
}
