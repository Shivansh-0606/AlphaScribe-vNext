"use client";

import { useState } from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { Heading } from "@/components/foundation/Heading";
import { Text } from "@/components/foundation/Text";
import { ResearchTemplate } from "@/components/layouts/ResearchTemplate";
import { useCompare } from "../application/useCompare";
import type { ReportListItem } from "../integration/schemas";
import { ComparisonPicker } from "./ComparisonPicker";
import { ComparisonTable } from "./ComparisonTable";

/**
 * SCR-07 Comparison — the feature's public screen composition.
 * `?ids=` is the deep-link/persistence mechanism (Law 6 — never lose
 * in-progress work on reload), mirroring `OverviewSection`'s `?job=` sync:
 * kept in the URL so a selection survives a reload and matches the frozen
 * entry point "Research Library (SCR-09), a saved comparison" — a comparison
 * is just a URL, nothing is persisted server-side (no such backend concept
 * exists; `POST /reports/compare` is a stateless lookup).
 *
 * AI Company Comparison (the frozen "explanation of differences") has no
 * backend support — `compare_reports` is a pure lookup, no LLM call — so
 * it's an honest deferral here, not a fabricated panel, same precedent as
 * AI Insights' deferred `Regenerate`/`Feedback` (Phase 4C) and Financials'
 * deferred `StatementTable` (Phase 4B).
 */
export function ComparisonScreen({ initialIds }: { initialIds: string[] }) {
  const router = useRouter();
  const [selected, setSelected] = useState<ReportListItem[]>(
    initialIds.map((id) => ({ id, ticker: "", query: "", created_at: "" })),
  );
  const selectedIds = selected.map((r) => r.id);
  const compare = useCompare(selectedIds);

  const syncUrl = (ids: string[]) => {
    const params = new URLSearchParams();
    if (ids.length > 0) params.set("ids", ids.join(","));
    const qs = params.toString();
    router.replace((qs ? `/compare?${qs}` : "/compare") as Route);
  };

  const handleToggle = (report: ReportListItem) => {
    const isSelected = selectedIds.includes(report.id);
    const next = isSelected
      ? selected.filter((r) => r.id !== report.id)
      : selected.length >= 4
        ? selected
        : [...selected, report];
    setSelected(next);
    syncUrl(next.map((r) => r.id));
  };

  return (
    <ResearchTemplate>
      <div className="flex flex-col gap-6">
        <Heading level="h1">Comparison</Heading>
        <ComparisonPicker selectedIds={selectedIds} onToggle={handleToggle} />

        {selectedIds.length === 0 && (
          <Text variant="small" className="text-muted-foreground">
            Select 2–4 reports above to compare them side by side.
          </Text>
        )}
        {selectedIds.length === 1 && (
          <Text variant="small" className="text-muted-foreground">
            Select at least one more report to compare.
          </Text>
        )}
        {selectedIds.length >= 2 && (
          <ComparisonTable
            reports={compare.data?.reports}
            isLoading={compare.isPending}
            isError={compare.isError}
            onRetry={() => compare.refetch()}
          />
        )}
      </div>
    </ResearchTemplate>
  );
}
