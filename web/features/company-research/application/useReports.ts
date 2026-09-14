import { useQuery } from "@tanstack/react-query";
import * as companyResearchApi from "../integration/api";

/**
 * Server-state ownership for the ticker-scoped reports list — the candidate
 * pool for M15's report-mode picker (`ChangeBriefSection`). Always
 * ticker-scoped (unlike `comparison`'s optionally-filtered `useReports`,
 * which searches across tickers) since Change Brief compares two reports
 * for one company (Document 70 R4 §7).
 */
export function useReports(ticker: string) {
  return useQuery({
    queryKey: ["company-research", "reports", ticker],
    queryFn: () => companyResearchApi.fetchReportsForTicker(ticker),
    staleTime: 30_000,
  });
}
