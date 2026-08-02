import { useQuery } from "@tanstack/react-query";
import * as companyResearchApi from "../integration/api";
import type { ReportDoc } from "../integration/schemas";

/**
 * Server-state ownership for a single report (03.14 row 2/3 — TanStack
 * Query owns it, the client holds no independent copy; row 11 — the
 * *streaming lifecycle* is a separate concern owned by `useResearchJob`).
 * Resolves to `null` while the job hasn't completed yet. Used for `cached:
 * true` generate responses and for resuming from a `?job=` deep link on
 * reload (Law 6 — never lose completed work); `useResearchJob` seeds this
 * same cache key directly once the stream's `final` event arrives, so this
 * hook picks it up reactively without a redundant fetch.
 */
export function reportQueryKey(jobId: string) {
  return ["company-research", "report", jobId] as const;
}

async function fetchCompletedReport(jobId: string): Promise<ReportDoc | null> {
  const res = await companyResearchApi.fetchReport(jobId);
  return res.report ?? null;
}

export function useReport(jobId: string | null) {
  return useQuery({
    queryKey: reportQueryKey(jobId ?? ""),
    queryFn: () => fetchCompletedReport(jobId as string),
    enabled: jobId != null,
    staleTime: 30_000,
  });
}
