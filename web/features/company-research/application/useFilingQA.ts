import { useQuery } from "@tanstack/react-query";
import * as companyResearchApi from "../integration/api";
import type { FilingQAAnswer } from "../integration/schemas";

/**
 * Server-state ownership for one Filing Q&A answer (mirrors
 * `useFilingAnalysis` exactly — 03.14 row 2/3). Resolves to `null` until the
 * job completes; `useFilingQAJob` seeds this same cache key directly once
 * the stream's `final` event arrives.
 */
export function filingQAQueryKey(ticker: string, docId: string, id: string) {
  return ["company-research", "filing-qa", ticker, docId, id] as const;
}

async function fetchCompletedFilingQA(
  ticker: string,
  docId: string,
  id: string,
): Promise<FilingQAAnswer | null> {
  const res = await companyResearchApi.fetchFilingQA(ticker, docId, id);
  return res.answer ?? null;
}

export function useFilingQA(ticker: string, docId: string, id: string | null) {
  return useQuery({
    queryKey: filingQAQueryKey(ticker, docId, id ?? ""),
    queryFn: () => fetchCompletedFilingQA(ticker, docId, id as string),
    enabled: id != null,
    staleTime: 30_000,
  });
}
