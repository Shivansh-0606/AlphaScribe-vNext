import { apiFetch } from "@/lib/api/fetch-client";
import { companySearchResponseSchema, reportsResponseSchema } from "./schemas";

/** Feature-scoped API access (02.2 AD-1) — the only place `workspace-home` touches `apiFetch`. */

export function searchCompanies(query: string, limit = 8) {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  return apiFetch(`/api/companies/search?${params.toString()}`, companySearchResponseSchema);
}

export function fetchRecentReports(limit = 10) {
  const params = new URLSearchParams({ limit: String(limit) });
  return apiFetch(`/api/reports?${params.toString()}`, reportsResponseSchema);
}
