"use client";

import { Badge } from "@/components/foundation/Badge";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { FormField } from "@/components/foundation/FormField";
import { Input } from "@/components/foundation/Input";
import { Skeleton, SkeletonGroup } from "@/components/foundation/Skeleton";
import { Text } from "@/components/foundation/Text";
import type { ReportListItem } from "../integration/schemas";

/**
 * LibraryList (09_Component_Inventory.md) — SCR-09's frozen component:
 * `items, filters` properties; `ListItem`(Report variant)/`Input`(filter)
 * dependencies; states `Default, Empty, No Results, Loading, Error`.
 *
 * Curated public samples ARE included here (unlike `workspace-home`'s
 * "Recent Research", which deliberately excludes them as "not the user's
 * own activity") — Research Library is a browse surface for every report
 * this account can reach, not an activity feed, and the frozen spec doesn't
 * say otherwise. Tagged with a Badge so it's never ambiguous which is which.
 */
export function LibraryList({
  reports,
  isLoading,
  isError,
  onRetry,
  filter,
  onFilterChange,
  onSelect,
}: {
  reports: ReportListItem[] | undefined;
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  filter: string;
  onFilterChange: (value: string) => void;
  onSelect: (report: ReportListItem) => void;
}) {
  return (
    <div className="flex flex-col gap-4">
      <FormField label="Filter by ticker">
        <Input
          value={filter}
          onChange={(event) => onFilterChange(event.target.value)}
          placeholder="e.g. MSFT"
          className="max-w-xs"
        />
      </FormField>

      {isLoading && (
        <SkeletonGroup label="Loading research library" className="flex flex-col gap-2">
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
        </SkeletonGroup>
      )}

      {!isLoading && isError && (
        <Banner
          tone="error"
          action={
            <Button variant="secondary" size="sm" onClick={onRetry}>
              Retry
            </Button>
          }
        >
          Couldn&apos;t load the research library.
        </Banner>
      )}

      {!isLoading && !isError && reports && reports.length === 0 && filter.trim() === "" && (
        <Text variant="small" className="text-muted-foreground">
          No saved research yet — reports you generate in Company Research will show up here.
        </Text>
      )}

      {!isLoading && !isError && reports && reports.length === 0 && filter.trim() !== "" && (
        <Text variant="small" className="text-muted-foreground">
          No reports match &quot;{filter}&quot;.
        </Text>
      )}

      {!isLoading && !isError && reports && reports.length > 0 && (
        <ul className="flex flex-col gap-1">
          {reports.map((report) => (
            <li key={report.id}>
              <button
                type="button"
                onClick={() => onSelect(report)}
                className="hover:bg-surface-hover flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-left"
              >
                <span className="text-foreground shrink-0 font-mono text-sm">{report.ticker}</span>
                <span className="text-muted-foreground min-w-0 flex-1 truncate text-sm">
                  {report.query}
                </span>
                {report.is_sample && <Badge variant="neutral">Sample</Badge>}
                <span className="text-muted-foreground shrink-0 text-xs">
                  {new Date(report.created_at).toLocaleDateString()}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
