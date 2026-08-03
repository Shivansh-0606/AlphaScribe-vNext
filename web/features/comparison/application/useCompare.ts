import { useQuery } from "@tanstack/react-query";
import * as comparisonApi from "../integration/api";

/**
 * SCR-07 Comparison — the side-by-side data for the selected set. `POST
 * /reports/compare` is a pure lookup (no LLM re-run, no side effects), so
 * modeling it as a query rather than a mutation is correct despite the verb —
 * same selection always returns the same data, and TanStack Query's cache
 * (keyed by the sorted id set) avoids re-fetching when toggling back and
 * forth between two already-seen selections.
 */
export function useCompare(reportIds: string[]) {
  const sorted = [...reportIds].sort();
  return useQuery({
    queryKey: ["comparison", "compare", sorted],
    queryFn: () => comparisonApi.compareReports(sorted),
    enabled: sorted.length >= 2,
    staleTime: 30_000,
  });
}
