"use client";

import { useRouter } from "next/navigation";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Heading } from "@/components/foundation/Heading";
import { Skeleton, SkeletonGroup } from "@/components/foundation/Skeleton";
import { Text } from "@/components/foundation/Text";
import { useRecentReports } from "../application/useWorkspaceHome";

/**
 * SCR-04 Workspace Home — Recent Research. Per the frozen UX spec: loads
 * progressively, and a load failure is non-blocking and scoped to this
 * region only (Search above stays usable regardless — see CompanySearch,
 * which has no dependency on this component's state).
 */
export function RecentResearch() {
  const router = useRouter();
  const recent = useRecentReports();

  if (recent.isPending) {
    return (
      <SkeletonGroup label="Loading recent research" className="flex flex-col gap-3">
        <Heading level="h2">Recent Research</Heading>
        <Skeleton className="h-14 w-full" />
        <Skeleton className="h-14 w-full" />
        <Skeleton className="h-14 w-full" />
      </SkeletonGroup>
    );
  }

  if (recent.isError) {
    return (
      <div className="flex flex-col gap-3">
        <Heading level="h2">Recent Research</Heading>
        <Banner
          tone="error"
          action={
            <Button variant="secondary" size="sm" onClick={() => recent.refetch()}>
              Retry
            </Button>
          }
        >
          Couldn&apos;t load your recent research. Search above still works.
        </Banner>
      </div>
    );
  }

  // Curated public samples aren't the user's own activity — only their own reports belong here.
  const reports = (recent.data?.reports ?? []).filter((report) => !report.is_sample);

  if (reports.length === 0) {
    return (
      <div className="flex flex-col gap-3">
        <Heading level="h2">Recent Research</Heading>
        <Text variant="small" className="text-muted-foreground">
          No research yet — search a company above to get started.
        </Text>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3">
      <Heading level="h2">Recent Research ({reports.length})</Heading>
      <ul className="flex flex-col gap-1">
        {reports.map((report) => (
          <li key={report.id}>
            <button
              type="button"
              onClick={() => router.push(`/research?ticker=${encodeURIComponent(report.ticker)}`)}
              className="hover:bg-surface-hover flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-left"
            >
              <span className="text-foreground shrink-0 font-mono text-sm">{report.ticker}</span>
              <span className="text-muted-foreground min-w-0 flex-1 truncate text-sm">
                {report.query}
              </span>
              <span className="text-muted-foreground shrink-0 text-xs">
                {new Date(report.created_at).toLocaleDateString()}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
