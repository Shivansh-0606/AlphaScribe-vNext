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

/**
 * Lightweight companion to `useReport` — exposes just the job's own
 * terminal `status` (`GET /reports/{id}`'s `status` field, which
 * `fetchCompletedReport` above discards after extracting `report`). Kept as
 * a fully separate query (own key, own fetch) rather than widening
 * `useReport`'s cached shape: `useResearchJob` already seeds
 * `reportQueryKey` directly with a bare `ReportDoc` on the SSE `final`
 * event, so changing what's cached under that key would ripple into that
 * seeding code and every other `useReport` consumer for a need only one
 * caller (`FinancialsSection`, distinguishing a failed job from a
 * genuinely still-running one) actually has.
 */
export function reportStatusQueryKey(jobId: string) {
  return ["company-research", "report-status", jobId] as const;
}

export function useReportStatus(jobId: string | null) {
  return useQuery({
    queryKey: reportStatusQueryKey(jobId ?? ""),
    queryFn: () => companyResearchApi.fetchReport(jobId as string).then((res) => res.status),
    enabled: jobId != null,
    staleTime: 30_000,
  });
}
