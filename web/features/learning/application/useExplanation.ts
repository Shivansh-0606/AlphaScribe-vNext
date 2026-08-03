import { useQuery } from "@tanstack/react-query";
import * as learningApi from "../integration/api";
import type { ExplanationDoc } from "../integration/schemas";

/** Resolves to `null` while the job hasn't completed yet — same convention as `company-research/application/useReport.ts`. */
export function explanationQueryKey(jobId: string) {
  return ["learning", "explanation", jobId] as const;
}

async function fetchCompletedExplanation(jobId: string): Promise<ExplanationDoc | null> {
  const res = await learningApi.fetchExplanation(jobId);
  return res.explanation ?? null;
}

export function useExplanation(jobId: string | null) {
  return useQuery({
    queryKey: explanationQueryKey(jobId ?? ""),
    queryFn: () => fetchCompletedExplanation(jobId as string),
    enabled: jobId != null,
    staleTime: 30_000,
  });
}
