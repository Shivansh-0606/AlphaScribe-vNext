import { useQuery } from "@tanstack/react-query";
import * as companyResearchApi from "../integration/api";

export function useFilings(ticker: string) {
  return useQuery({
    queryKey: ["company-research", "filings", ticker],
    queryFn: () => companyResearchApi.fetchFilings(ticker),
    staleTime: 30_000,
  });
}
