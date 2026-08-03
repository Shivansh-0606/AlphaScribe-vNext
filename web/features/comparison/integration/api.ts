import { apiFetch } from "@/lib/api/fetch-client";
import { compareResponseSchema, reportsListResponseSchema } from "./schemas";

/** Feature-scoped API access (02.2 AD-1) — the only place `comparison` touches `apiFetch`. */
export function fetchReports(params: { ticker?: string; limit?: number } = {}) {
  const query = new URLSearchParams();
  if (params.ticker) query.set("ticker", params.ticker);
  if (params.limit) query.set("limit", String(params.limit));
  const qs = query.toString();
  return apiFetch(`/api/reports${qs ? `?${qs}` : ""}`, reportsListResponseSchema);
}

/** `POST /reports/compare` (backend/server.py `compare_reports`) — a pure lookup of 2-4 existing reports, no LLM re-run. */
export function compareReports(reportIds: string[]) {
  return apiFetch("/api/reports/compare", compareResponseSchema, {
    method: "POST",
    body: { report_ids: reportIds },
  });
}
