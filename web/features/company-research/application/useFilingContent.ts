import { useQuery } from "@tanstack/react-query";
import * as companyResearchApi from "../integration/api";

export function filingContentQueryKey(ticker: string, docId: string) {
  return ["company-research", "filing-content", ticker, docId] as const;
}

/**
 * Server-state ownership for `GET /companies/{ticker}/filings/{doc_id}/content`
 * (M13 — Document 59, CTO-ratified 2026-08-27). Keyed on `(ticker, docId)`
 * together — the endpoint is company-namespaced and a `doc_id` is only
 * meaningful within its ticker. Disabled until a `docId` is selected so the
 * list view issues no request. `staleTime` matches `useFilings` — a filing's
 * persisted text is immutable once ingested (an out-of-band re-ingest gets a
 * fresh `doc_id`), so a short stale window is ample.
 */
export function useFilingContent(ticker: string, docId: string | null) {
  return useQuery({
    queryKey: filingContentQueryKey(ticker, docId ?? ""),
    queryFn: () => companyResearchApi.fetchFilingContent(ticker, docId as string),
    enabled: docId !== null && docId !== "",
    staleTime: 30_000,
  });
}
