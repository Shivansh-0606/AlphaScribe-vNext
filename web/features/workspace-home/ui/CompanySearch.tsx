"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { SearchField, type SearchFieldSuggestion } from "@/components/foundation/SearchField";
import { useDebouncedValue } from "@/lib/hooks/useDebouncedValue";
import { useCompanySearch } from "../application/useWorkspaceHome";

/**
 * SCR-04 Workspace Home — primary focus, available immediately (SCR-04 UX
 * spec: "search is available immediately", never blocked by Recent Research).
 * Selecting a result routes into `/research?ticker=` — Company Research
 * itself is a later phase (Feature Parity Tracker), so this is the honest
 * hand-off point today, not a dead end.
 */
export function CompanySearch() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebouncedValue(query, 250);
  const search = useCompanySearch(debouncedQuery);

  const suggestions: SearchFieldSuggestion[] = (search.data?.results ?? []).map((company) => ({
    id: company.ticker,
    label: company.name,
    description: company.ticker,
  }));

  const goToCompany = (ticker: string) => {
    router.push(`/research?ticker=${encodeURIComponent(ticker.toUpperCase())}`);
  };

  return (
    <SearchField
      label="Search a company"
      placeholder="Search a company — e.g. Apple, Microsoft, Tesla…"
      size="lg"
      autoFocus
      value={query}
      onValueChange={setQuery}
      suggestions={suggestions}
      loading={search.isFetching}
      emptyMessage={
        search.isError
          ? "Search is temporarily unavailable — try again in a moment."
          : "No matches — try a different term."
      }
      onSelect={(suggestion) => goToCompany(suggestion.id)}
      // Search tolerates partial input; no hard validation (SCR-04 UX spec) — Enter
      // with no suggestion highlighted still routes in on whatever was typed.
      onSubmit={(value) => {
        if (value.trim()) goToCompany(value.trim());
      }}
    />
  );
}
