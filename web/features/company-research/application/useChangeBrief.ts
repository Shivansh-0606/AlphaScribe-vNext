import { useQuery } from "@tanstack/react-query";
import * as companyResearchApi from "../integration/api";
import type { ChangeBriefPayload } from "../integration/schemas";

/**
 * Server-state ownership for one Change Brief result (mirrors
 * `useFilingAnalysis`/`useReport` exactly — 03.14 row 2/3). Resolves to
 * `null` until the job completes; `useChangeBriefJob` seeds this same cache
 * key directly once the stream's `final` event arrives.
 */
export function changeBriefQueryKey(ticker: string, id: string) {
  return ["company-research", "change-brief", ticker, id] as const;
}

async function fetchCompletedChangeBrief(
  ticker: string,
  id: string,
): Promise<ChangeBriefPayload | null> {
  const res = await companyResearchApi.fetchChangeBrief(ticker, id);
  return res.changes ?? null;
}

export function useChangeBrief(ticker: string, id: string | null) {
  return useQuery({
    queryKey: changeBriefQueryKey(ticker, id ?? ""),
    queryFn: () => fetchCompletedChangeBrief(ticker, id as string),
    enabled: id != null,
    staleTime: 30_000,
  });
}
