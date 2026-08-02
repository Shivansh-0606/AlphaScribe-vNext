import { useQuery } from "@tanstack/react-query";
import * as researchLibraryApi from "../integration/api";
import type { ReportDoc } from "../integration/schemas";

/** Server-state ownership for a single saved report (03.14 row 2/3). */
export function reportQueryKey(id: string) {
  return ["research-library", "report", id] as const;
}

async function fetchSavedReport(id: string): Promise<ReportDoc | null> {
  const res = await researchLibraryApi.fetchReport(id);
  return res.report ?? null;
}

export function useReport(id: string) {
  return useQuery({
    queryKey: reportQueryKey(id),
    queryFn: () => fetchSavedReport(id),
    staleTime: 30_000,
  });
}
