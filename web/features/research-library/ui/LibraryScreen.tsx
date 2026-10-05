"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { Route } from "next";
import { Heading } from "@/components/foundation/Heading";
import { useDebouncedValue } from "@/lib/hooks/useDebouncedValue";
import { useReports } from "../application/useReports";
import type { ReportListItem } from "../integration/schemas";
import { DeleteReportDialog } from "./DeleteReportDialog";
import { LibraryList } from "./LibraryList";

/**
 * SCR-09 Research Library — the feature's public screen composition.
 * `WorkspaceTemplate` is already applied once at `(workspace)/layout.tsx`
 * (this screen's only route) — not re-applied here, same as Workspace
 * Home's page composition.
 *
 * Frozen scope: "Research Reports" only (`GET /reports`, already real).
 * "Research Sessions"/"Saved Exports"/"Research History" are also named in
 * the frozen IA (`05_Screen_Inventory.md`) but have no backend data source
 * of their own (no session concept beyond a report, no persisted-export
 * record, no distinct history feed) — deferred, not silently dropped, same
 * as Financials/Filings' progressive-enhancement precedent from Phase 4B.
 *
 * Deleting a report (CR-SCOPE-004) is composed here: the list reports which
 * row asked, this screen shows the confirm dialog, and after a successful
 * delete focus moves to the heading — the deleted row and its menu trigger no
 * longer exist to hold it.
 */
export function LibraryScreen() {
  const router = useRouter();
  const [filter, setFilter] = useState("");
  const debouncedFilter = useDebouncedValue(filter);
  const reports = useReports(debouncedFilter);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const [deleting, setDeleting] = useState<{
    report: ReportListItem;
    trigger: HTMLElement | null;
  } | null>(null);

  return (
    <div className="flex flex-col gap-6">
      <Heading level="h1" ref={headingRef} tabIndex={-1}>
        Research Library
      </Heading>
      <LibraryList
        reports={reports.data?.reports}
        isLoading={reports.isPending}
        isError={reports.isError}
        onRetry={() => reports.refetch()}
        filter={filter}
        onFilterChange={setFilter}
        onSelect={(report) => router.push(`/reports/${report.id}` as Route)}
        onDeleteRequest={(report, trigger) => setDeleting({ report, trigger })}
      />
      {deleting && (
        <DeleteReportDialog
          key={deleting.report.id}
          report={deleting.report}
          returnFocusTo={deleting.trigger}
          onClose={() => setDeleting(null)}
          onDeleted={() => headingRef.current?.focus()}
        />
      )}
    </div>
  );
}
