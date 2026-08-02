import { useQuery } from "@tanstack/react-query";
import * as researchLibraryApi from "../integration/api";

/** SCR-09 Research Library — the report list, optionally filtered by ticker (`LibraryList`'s "filters"). */
export function useReports(ticker: string) {
  const trimmed = ticker.trim();
  return useQuery({
    queryKey: ["research-library", "reports", trimmed],
    queryFn: () => researchLibraryApi.fetchReports(trimmed ? { ticker: trimmed } : {}),
    staleTime: 30_000,
  });
}
