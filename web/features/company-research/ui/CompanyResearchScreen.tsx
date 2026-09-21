"use client";

import { useState } from "react";
import { Banner } from "@/components/foundation/Banner";
import { Heading } from "@/components/foundation/Heading";
import { ResearchTemplate } from "@/components/layouts/ResearchTemplate";
import { useReportStatus } from "../application/useReport";
import { AIInsightsSection } from "./AIInsightsSection";
import { ChangeBriefSection } from "./ChangeBriefSection";
import { ExportSection } from "./ExportSection";
import { FilingsSection } from "./FilingsSection";
import { FinancialsSection } from "./FinancialsSection";
import { OverviewSection } from "./OverviewSection";
import { SectionNav, type SectionKey } from "./SectionNav";

/** SCR-06 Company Research — the feature's public screen composition. */
export function CompanyResearchScreen({ ticker, jobId }: { ticker?: string; jobId?: string }) {
  const [active, setActive] = useState<SectionKey>("overview");
  // Export's own hand-off (migrated-parity hardening pass, Sub-Slice 6
  // Finding A) needs to know the job actually *completed*, not just that a
  // `?job=` id is present — `jobId` alone is set the instant a run starts.
  // Distinct root cause from Sub-Slices 2/5 (which discard a fetched
  // `status`): Export never fetched status at all, so this is the first
  // status check in its path, not a widened one.
  const exportJobStatus = useReportStatus(jobId ?? null);

  if (!ticker) {
    return (
      <ResearchTemplate>
        <div className="flex flex-col gap-4">
          <Heading level="h1">Company Research</Heading>
          <Banner tone="info">
            Search for a company from Workspace Home to start researching it.
          </Banner>
        </div>
      </ResearchTemplate>
    );
  }

  const normalizedTicker = ticker.toUpperCase();

  return (
    <ResearchTemplate sectionNav={<SectionNav active={active} onSelect={setActive} />}>
      <div className="flex flex-col gap-6">
        <Heading level="h1">{normalizedTicker}</Heading>
        {active === "overview" && (
          <OverviewSection ticker={normalizedTicker} initialJobId={jobId ?? null} />
        )}
        {active === "financials" && (
          <FinancialsSection
            ticker={normalizedTicker}
            onGoToOverview={() => setActive("overview")}
          />
        )}
        {active === "filings" && <FilingsSection ticker={normalizedTicker} />}
        {active === "changes" && <ChangeBriefSection ticker={normalizedTicker} />}
        {active === "ai-insights" && (
          <AIInsightsSection
            ticker={normalizedTicker}
            onGoToOverview={() => setActive("overview")}
          />
        )}
        {active === "export" && (
          <ExportSection reportId={exportJobStatus.data === "completed" ? jobId : undefined} />
        )}
      </div>
    </ResearchTemplate>
  );
}
