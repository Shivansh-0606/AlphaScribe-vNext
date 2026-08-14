import { useMutation } from "@tanstack/react-query";
import * as companyResearchApi from "../integration/api";

/**
 * Triggers `POST /financials/acquire` (mirrors the `useAuth.ts` mutation
 * pattern). No period-type selector exists anywhere in the frozen Financials
 * UX, so this always requests `annual` — the backend's `period_type` query
 * param has no default and no other value is reachable from this screen.
 *
 * `outcome` is one of the four frozen values (backend/domain/financials.py
 * `AcquisitionOutcome` + the endpoint's own "requested"/"mixed" rollup):
 * "requested" (acquisition kicked off — also what a repeat call while still
 * pending returns, so it doubles as "already in progress"), "available",
 * "confirmed_unavailable", or "mixed". A transport/HTTP failure (401/422/
 * 429/502) is a separate concern surfaced via `mutation.error`, not a fifth
 * outcome value.
 */
export function useFinancialsAcquisition(ticker: string) {
  return useMutation({
    mutationFn: () => companyResearchApi.acquireFinancials(ticker, "annual"),
  });
}
