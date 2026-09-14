import { useQuery } from "@tanstack/react-query";
import * as companyResearchApi from "../integration/api";

export function financialStatementsQueryKey(ticker: string, periodType: "annual" | "quarterly") {
  return ["company-research", "financials", ticker, periodType] as const;
}

/**
 * Server-state ownership for `GET /companies/{ticker}/financials` (Document
 * 33 §1-§10, CTO-ratified Round 7). Keyed on (ticker, periodType) together,
 * never `ticker` alone (Document 55 §3.5's period_type invariant) — annual
 * and quarterly must never share a cache entry or fall back into each other.
 * `enabled` (default `true`, `FinancialsSection`'s existing eager-fetch
 * behavior unchanged) lets a caller that only sometimes needs this data —
 * `ChangeBriefSection`'s period-mode picker — skip the request entirely
 * rather than fetching it on every mount regardless of which mode is active.
 */
export function useFinancialStatements(
  ticker: string,
  periodType: "annual" | "quarterly",
  enabled = true,
) {
  return useQuery({
    queryKey: financialStatementsQueryKey(ticker, periodType),
    queryFn: () => companyResearchApi.fetchFinancialStatements(ticker, periodType),
    enabled,
    staleTime: 30_000,
  });
}
