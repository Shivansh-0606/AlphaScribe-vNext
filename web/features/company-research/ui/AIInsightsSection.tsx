"use client";

import { useSearchParams } from "next/navigation";
import { Banner } from "@/components/foundation/Banner";
import { Loader } from "@/components/foundation/Loader";
import { useReport } from "../application/useReport";
import { CopilotPanel } from "./CopilotPanel";

/**
 * SCR-06 AI Insights — the Copilot follow-up surface. Needs a completed
 * report to build on (`context_report_id`), so it's gated behind the same
 * `?job=` URL state Overview writes, same pattern as Financials/Filings.
 */
export function AIInsightsSection({ ticker }: { ticker: string }) {
  const jobId = useSearchParams().get("job");
  const report = useReport(jobId);

  if (!jobId) {
    return (
      <Banner tone="info">
        Run research on the Overview tab first — AI Insights lets you ask follow-up questions once
        you have a research brief for {ticker}.
      </Banner>
    );
  }
  if (report.isPending) {
    return <Loader label="Loading…" />;
  }
  if (report.isError) {
    return <Banner tone="error">Couldn&apos;t load the research brief.</Banner>;
  }
  // Legitimately null while the Overview run hasn't finished yet — not an error.
  if (!report.data) {
    return (
      <Banner tone="info">
        Research is still running — AI Insights will be available once it completes.
      </Banner>
    );
  }

  return <CopilotPanel ticker={ticker} contextReportId={report.data.id} />;
}
