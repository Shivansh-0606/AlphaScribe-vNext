"use client";

import { Banner } from "@/components/foundation/Banner";
import { Link } from "@/components/foundation/Link";

/**
 * SCR-06 Export — CTO-resolved (Phase 4D): the frozen Component Inventory
 * ties the actual export mechanism ("Export preserves reasoning and
 * sources", J-06) to `ReportDocument` on Report View (SCR-10), owned by
 * `research-library`, not `company-research`. Building a second export
 * implementation here would duplicate that architecture rather than extend
 * it — this stays an honest hand-off, not the feature itself.
 *
 * Phase 5: Report View now exists, so once a report has actually been
 * generated this run (`reportId` set, mirroring the `?job=` query param
 * `OverviewSection` keeps in sync), this links there directly instead of
 * only describing where export lives.
 */
export function ExportSection({ reportId }: { reportId?: string }) {
  if (reportId) {
    return (
      <Banner tone="info" action={<Link href={`/reports/${reportId}`}>Open Report View</Link>}>
        Export happens from the Report View, which preserves the full reasoning and sources behind
        this report.
      </Banner>
    );
  }

  return (
    <Banner tone="info">
      Export isn&apos;t built here — it happens from the Report View in Research Library, which
      preserves the full reasoning and sources behind a saved report. Generate a report first, then
      this tab will link there directly.
    </Banner>
  );
}
