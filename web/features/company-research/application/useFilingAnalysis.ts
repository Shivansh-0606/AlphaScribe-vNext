import { useQuery } from "@tanstack/react-query";
import * as companyResearchApi from "../integration/api";
import type { FilingAnalysisPayload } from "../integration/schemas";

/**
 * Server-state ownership for one Filing Analysis result (mirrors `useReport`
 * exactly — 03.14 row 2/3). Resolves to `null` until the job completes;
 * `useFilingAnalysisJob` seeds this same cache key directly once the
 * stream's `final` event arrives, so this hook picks it up reactively.
 */
export function filingAnalysisQueryKey(ticker: string, docId: string, id: string) {
  return ["company-research", "filing-analysis", ticker, docId, id] as const;
}

async function fetchCompletedFilingAnalysis(
  ticker: string,
  docId: string,
  id: string,
): Promise<FilingAnalysisPayload | null> {
  const res = await companyResearchApi.fetchFilingAnalysis(ticker, docId, id);
  return res.analysis ?? null;
}

export function useFilingAnalysis(ticker: string, docId: string, id: string | null) {
  return useQuery({
    queryKey: filingAnalysisQueryKey(ticker, docId, id ?? ""),
    queryFn: () => fetchCompletedFilingAnalysis(ticker, docId, id as string),
    enabled: id != null,
    staleTime: 30_000,
  });
}
