"use client";

import { useState } from "react";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Chip } from "@/components/foundation/Chip";
import { FormField } from "@/components/foundation/FormField";
import { Input } from "@/components/foundation/Input";
import { Skeleton, SkeletonGroup } from "@/components/foundation/Skeleton";
import { Text } from "@/components/foundation/Text";
import { useDebouncedValue } from "@/lib/hooks/useDebouncedValue";
import { useReports } from "../application/useReports";
import type { ReportListItem } from "../integration/schemas";

const MAX_MEMBERS = 4;

/**
 * SCR-07's "company chips" (05_Screen_Inventory.md's "Add/remove a
 * company"). Candidates come from existing saved reports (`GET /reports`,
 * same as Research Library) — Comparison operates on already-generated
 * reports, not raw ticker search, per the backend's `POST /reports/compare`
 * contract (`report_ids`, not tickers).
 */
export function ComparisonPicker({
  selectedIds,
  onToggle,
}: {
  selectedIds: string[];
  onToggle: (report: ReportListItem) => void;
}) {
  const [filter, setFilter] = useState("");
  const debouncedFilter = useDebouncedValue(filter);
  const reports = useReports(debouncedFilter);
  const selected = new Set(selectedIds);
  const atMax = selectedIds.length >= MAX_MEMBERS;

  return (
    <div className="flex flex-col gap-3">
      <FormField label="Filter by ticker">
        <Input
          value={filter}
          onChange={(event) => setFilter(event.target.value)}
          placeholder="e.g. MSFT"
          className="max-w-xs"
        />
      </FormField>

      {reports.isPending && (
        <SkeletonGroup label="Loading candidate reports" className="flex flex-wrap gap-2">
          <Skeleton className="h-9 w-32" />
          <Skeleton className="h-9 w-32" />
          <Skeleton className="h-9 w-32" />
        </SkeletonGroup>
      )}

      {!reports.isPending && reports.isError && (
        <Banner
          tone="error"
          action={
            <Button variant="secondary" size="sm" onClick={() => reports.refetch()}>
              Retry
            </Button>
          }
        >
          Couldn&apos;t load reports to compare.
        </Banner>
      )}

      {!reports.isPending && !reports.isError && reports.data?.reports.length === 0 && (
        <Text variant="small" className="text-muted-foreground">
          {filter.trim()
            ? `No reports match "${filter}".`
            : "No saved research yet — generate a report in Company Research first."}
        </Text>
      )}

      {!reports.isPending &&
        !reports.isError &&
        reports.data &&
        reports.data.reports.length > 0 && (
          <div className="flex flex-col gap-2">
            <div className="flex flex-wrap gap-2">
              {reports.data.reports.map((report) => {
                const isSelected = selected.has(report.id);
                return (
                  <Chip
                    key={report.id}
                    variant="filter"
                    selected={isSelected}
                    disabled={!isSelected && atMax}
                    className={!isSelected && atMax ? "opacity-disabled" : undefined}
                    onClick={() => onToggle(report)}
                  >
                    {report.company_name ?? report.ticker}
                    {report.is_sample ? " (Sample)" : ""}
                  </Chip>
                );
              })}
            </div>
            <Text variant="caption" className="text-muted-foreground">
              {selectedIds.length}/{MAX_MEMBERS} selected — pick at least 2 to compare.
            </Text>
          </div>
        )}
    </div>
  );
}
