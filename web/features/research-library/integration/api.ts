import { apiFetch } from "@/lib/api/fetch-client";
import { reportStatusResponseSchema } from "./schemas";

/** Feature-scoped API access (02.2 AD-1) — the only place `research-library` touches `apiFetch`. */
export function fetchReport(id: string) {
  return apiFetch(`/api/reports/${id}`, reportStatusResponseSchema);
}
