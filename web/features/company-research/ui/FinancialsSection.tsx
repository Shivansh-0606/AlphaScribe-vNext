"use client";

import { useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Card, CardContent } from "@/components/foundation/Card";
import { Loader } from "@/components/foundation/Loader";
import { Text } from "@/components/foundation/Text";
import { MetricStat } from "@/components/research/MetricStat";
import { useFinancialsAcquisition } from "../application/useFinancialsAcquisition";
import { useReport } from "../application/useReport";
import type { ExtractedFinancials } from "../integration/schemas";

/**
 * SCR-06 Financials. Progressive enhancement per CTO decision (Phase 4B):
 * the frozen `StatementTable` (multi-period Income/Balance/Cash Flow) has no
 * backend data source at all — only a single-period 7-field LLM snapshot
 * (`extracted_data` on a report) exists. This renders every field that
 * genuinely has a value as a `MetricStat`, and reserves the Statements
 * section with an honest placeholder rather than fabricating or omitting it.
 * No backend scope was added for this phase.
 */
const METRIC_FIELDS: { key: keyof ExtractedFinancials; label: string }[] = [
  { key: "revenue", label: "Revenue" },
  { key: "revenue_yoy", label: "Revenue YoY" },
  { key: "eps", label: "EPS" },
  { key: "net_income", label: "Net Income" },
  { key: "operating_margin", label: "Operating Margin" },
  { key: "free_cash_flow", label: "Free Cash Flow" },
];

/** Only a real leading sign already in the LLM-extracted string counts — never guessed. */
function directionFromValue(value: string): "up" | "down" | undefined {
  if (value.startsWith("+")) return "up";
  if (value.startsWith("-")) return "down";
  return undefined;
}

/**
 * Terminal outcomes that render with no action button at all — the ones
 * where the acquisition control (idle button or "Check status") unmounts,
 * which would otherwise drop keyboard focus to `<body>` with no indication
 * of what happened. `requested` keeps its "Check status" button in place
 * (same control, just relabeled), so focus is never lost there.
 */
const TERMINAL_OUTCOMES_WITHOUT_ACTION = new Set(["available", "confirmed_unavailable", "mixed"]);

/**
 * The Statements card's acquisition-status banner. `GET /companies/{ticker}/
 * financials` doesn't exist yet (out of scope for this integration), so a
 * successful acquisition still can't be rendered here — this only reports
 * what the backend now knows, never fabricates the statements themselves.
 */
function StatementsBanner({
  ticker,
  acquisition,
}: {
  ticker: string;
  acquisition: ReturnType<typeof useFinancialsAcquisition>;
}) {
  // Focus target for the terminal-without-action outcomes below. `tabIndex={-1}`
  // keeps it out of the normal Tab order — it's only ever reached
  // programmatically, right after the control it replaces disappears.
  const focusRef = useRef<HTMLDivElement>(null);
  const outcome = acquisition.isSuccess ? acquisition.data.outcome : undefined;

  useEffect(() => {
    // Keyed on `acquisition.data`'s identity (a fresh object per resolved
    // mutation) so this fires exactly once per new terminal result — never
    // on an unrelated re-render, which would yank focus from whatever the
    // user is doing next.
    if (outcome && TERMINAL_OUTCOMES_WITHOUT_ACTION.has(outcome)) {
      focusRef.current?.focus();
    }
  }, [outcome, acquisition.data]);

  const checkAction = (
    <Button
      variant="secondary"
      size="sm"
      loading={acquisition.isPending}
      onClick={() => acquisition.mutate()}
    >
      {acquisition.isSuccess ? "Check status" : "Check for financial statements"}
    </Button>
  );

  let content;
  if (acquisition.isError) {
    content = (
      <Banner tone="error" action={checkAction}>
        {acquisition.error.message}
      </Banner>
    );
  } else if (outcome === "requested") {
    content = (
      <Banner tone="info" action={checkAction}>
        Fetching financial statements for {ticker} in the background — check back shortly.
      </Banner>
    );
  } else if (outcome === "available") {
    content = (
      <Banner tone="success">
        Financial statements for {ticker} are now available on the backend. Display in this screen
        isn&apos;t built yet.
      </Banner>
    );
  } else if (outcome === "confirmed_unavailable") {
    content = (
      <Banner tone="info">The data provider has no financial statements for {ticker}.</Banner>
    );
  } else if (outcome === "mixed") {
    content = (
      <Banner tone="info">
        Some financial statements for {ticker} are available, others aren&apos;t — the provider
        couldn&apos;t supply all of them.
      </Banner>
    );
  } else {
    content = (
      <Banner tone="info" action={checkAction}>
        Multi-period Income Statement / Balance Sheet / Cash Flow Statement data isn&apos;t
        available yet — this section will show them once structured statement data is added to the
        backend.
      </Banner>
    );
  }

  return (
    <div ref={focusRef} tabIndex={-1}>
      {content}
    </div>
  );
}

export function FinancialsSection({ ticker }: { ticker: string }) {
  const jobId = useSearchParams().get("job");
  const report = useReport(jobId);
  const acquisition = useFinancialsAcquisition(ticker);

  if (!jobId) {
    return (
      <Banner tone="info">
        Run research on the Overview tab to see extracted financial metrics for {ticker}.
      </Banner>
    );
  }
  if (report.isPending) {
    return <Loader label="Loading financial metrics…" />;
  }
  if (report.isError) {
    return (
      <Banner
        tone="error"
        action={
          <Button variant="secondary" size="sm" onClick={() => report.refetch()}>
            Retry
          </Button>
        }
      >
        Couldn&apos;t load financial metrics.
      </Banner>
    );
  }
  // `report.data` is legitimately `null` — not an error — while the run on
  // Overview hasn't finished yet (`useReport` resolves null until a report exists).
  if (!report.data) {
    return (
      <Banner tone="info">
        Research is still running — financial metrics will appear here once it completes.
      </Banner>
    );
  }

  const data = report.data.extracted_data;
  const metrics = METRIC_FIELDS.map((f) => ({ ...f, value: data?.[f.key] })).filter(
    (f): f is { key: keyof ExtractedFinancials; label: string; value: string } => Boolean(f.value),
  );

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardContent className="flex flex-col gap-4">
          <Text variant="body-strong">Financial Metrics</Text>
          {metrics.length > 0 ? (
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
              {metrics.map((m) => (
                <MetricStat
                  key={m.key}
                  label={m.label}
                  value={m.value}
                  direction={directionFromValue(m.value)}
                />
              ))}
            </div>
          ) : (
            <Text variant="small" className="text-muted-foreground">
              No financial metrics were extracted for this report.
            </Text>
          )}
          {data?.guidance && (
            <div className="flex flex-col gap-1">
              <Text variant="label">Guidance</Text>
              <Text variant="small">{data.guidance}</Text>
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardContent className="flex flex-col gap-3">
          <Text variant="body-strong">Financial Statements</Text>
          <StatementsBanner ticker={ticker} acquisition={acquisition} />
        </CardContent>
      </Card>
    </div>
  );
}
