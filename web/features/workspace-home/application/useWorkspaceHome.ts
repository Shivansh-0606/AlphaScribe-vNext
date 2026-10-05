import { useQuery } from "@tanstack/react-query";
import { reportKeys } from "@/lib/api/report-keys";
import * as workspaceHomeApi from "../integration/api";

/** Search is available immediately and never blocked by anything else on the screen (SCR-04 UX spec). */
export function useCompanySearch(query: string, limit = 8) {
  const trimmed = query.trim();
  return useQuery({
    queryKey: ["workspace-home", "company-search", trimmed, limit],
    queryFn: () => workspaceHomeApi.searchCompanies(trimmed, limit),
    enabled: trimmed.length > 0,
    staleTime: 30_000,
  });
}

/**
 * Recent Research load failure is non-blocking (SCR-04 UX spec) — this query's
 * own `isError`/`refetch` drives an inline, retryable error scoped to that
 * region only; it never affects the search box above it.
 */
export function useRecentReports(limit = 10) {
  return useQuery({
    queryKey: reportKeys.list("workspace-home", "recent", limit),
    queryFn: () => workspaceHomeApi.fetchRecentReports(limit),
    staleTime: 30_000,
  });
}
