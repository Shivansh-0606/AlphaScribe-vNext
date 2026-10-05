import { useQuery } from "@tanstack/react-query";
import { reportKeys } from "@/lib/api/report-keys";
import * as comparisonApi from "../integration/api";

/** SCR-07 Comparison — the picker's candidate list, optionally filtered by ticker. */
export function useReports(ticker: string) {
  const trimmed = ticker.trim();
  return useQuery({
    queryKey: reportKeys.list("comparison", trimmed),
    queryFn: () => comparisonApi.fetchReports(trimmed ? { ticker: trimmed } : {}),
    staleTime: 30_000,
  });
}
