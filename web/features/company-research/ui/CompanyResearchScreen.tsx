"use client";

import { useState } from "react";
import { Banner } from "@/components/foundation/Banner";
import { Heading } from "@/components/foundation/Heading";
import { ResearchTemplate } from "@/components/layouts/ResearchTemplate";
import { AIInsightsSection } from "./AIInsightsSection";
import { ExportSection } from "./ExportSection";
import { FilingsSection } from "./FilingsSection";
import { FinancialsSection } from "./FinancialsSection";
import { OverviewSection } from "./OverviewSection";
import { SectionNav, type SectionKey } from "./SectionNav";

/** SCR-06 Company Research — the feature's public screen composition. */
export function CompanyResearchScreen({ ticker, jobId }: { ticker?: string; jobId?: string }) {
  const [active, setActive] = useState<SectionKey>("overview");

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
        {active === "financials" && <FinancialsSection ticker={normalizedTicker} />}
        {active === "filings" && <FilingsSection ticker={normalizedTicker} />}
        {active === "ai-insights" && <AIInsightsSection ticker={normalizedTicker} />}
        {active === "export" && <ExportSection reportId={jobId} />}
      </div>
    </ResearchTemplate>
  );
}
