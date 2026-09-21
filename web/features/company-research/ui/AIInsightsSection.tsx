"use client";

import { useSearchParams } from "next/navigation";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Loader } from "@/components/foundation/Loader";
import { useReport, useReportStatus } from "../application/useReport";
import { CopilotPanel } from "./CopilotPanel";

/**
 * SCR-06 AI Insights — the Copilot follow-up surface. Needs a completed
 * report to build on (`context_report_id`), so it's gated behind the same
 * `?job=` URL state Overview writes, same pattern as Financials/Filings.
 *
 * Distinguishes a terminal `failed`/`cancelled` job from one genuinely still
 * running via `useReportStatus` (migrated-parity hardening pass, Company
 * Research Sub-Slice 5 Finding A — `useReport` alone can't tell the two
 * apart, since both currently present as `report.data === null`; same root
 * cause and same fix shape as Sub-Slice 2's Financials Finding B).
 */
export function AIInsightsSection({
  ticker,
  onGoToOverview,
}: {
  ticker: string;
  onGoToOverview: () => void;
}) {
  const jobId = useSearchParams().get("job");
  const report = useReport(jobId);
  const status = useReportStatus(jobId);

  if (!jobId) {
    return (
      <Banner tone="info">
        Run research on the Overview tab first — AI Insights lets you ask follow-up questions once
        you have a research brief for {ticker}.
      </Banner>
    );
  }
  if (report.isPending || status.isPending) {
    return <Loader label="Loading…" />;
  }
  if (report.isError || status.isError) {
    return <Banner tone="error">Couldn&apos;t load the research brief.</Banner>;
  }
  // A terminal non-success status is not "still running" — Overview's own
  // job hook already shows a Retry for it; AI Insights has no live job/stream
  // of its own to retry inline, so it hands off there rather than faking a
  // retry it can't actually perform.
  if (status.data === "failed" || status.data === "cancelled") {
    return (
      <Banner
        tone="error"
        action={
          <Button variant="secondary" size="sm" onClick={onGoToOverview}>
            Go to Overview
          </Button>
        }
      >
        Research {status.data === "cancelled" ? "was cancelled" : "failed"} — go to Overview to see
        what happened and retry.
      </Banner>
    );
  }
  // `report.data` is legitimately `null` — not an error — while a genuinely
  // still-running job hasn't produced a report yet.
  if (!report.data) {
    return (
      <Banner tone="info">
        Research is still running — AI Insights will be available once it completes.
      </Banner>
    );
  }

  return <CopilotPanel ticker={ticker} contextReportId={report.data.id} />;
}
