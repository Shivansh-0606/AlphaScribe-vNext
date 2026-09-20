"use client";

import { useEffect, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Card, CardContent } from "@/components/foundation/Card";
import { Loader } from "@/components/foundation/Loader";
import { Text } from "@/components/foundation/Text";
import { MetricStat } from "@/components/research/MetricStat";
import { StatementTable } from "@/components/research/StatementTable";
import { useFinancialsAcquisition } from "../application/useFinancialsAcquisition";
import { useFinancialStatements } from "../application/useFinancialStatements";
import { useReport, useReportStatus } from "../application/useReport";
import type { ExtractedFinancials, FinancialStatementGroup } from "../integration/schemas";

/**
 * SCR-06 Financials. The "Financial Metrics" card renders the single-period
 * 7-field LLM snapshot (`extracted_data` on a report) as `MetricStat`s — every
 * field that genuinely has a value, nothing fabricated. The "Financial
 * Statements" card (below) is the M12 addition: multi-period Income/Balance/
 * Cash Flow data from `GET /companies/{ticker}/financials` (Document 33
 * §1-§10, CTO-ratified), rendered per statement type via `StatementTable`
 * once `acquisition_state` is `available` (Document 55 §3.2's acceptance
 * matrix) — genuinely independent of the report/job above: it renders
 * unconditionally, never gated on the Metrics card's own job state
 * (migrated-parity hardening pass, Company Research Sub-Slice 2 Finding C —
 * the two cards previously shared one early-return chain, so the Statements
 * card was unreachable until an Overview job for the same ticker existed
 * and succeeded, even though its own data source doesn't need one).
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

const STATEMENT_TITLES = {
  income: "Income Statement",
  balance_sheet: "Balance Sheet",
  cash_flow: "Cash Flow Statement",
} as const;

/**
 * Document 55 §3.2's acceptance matrix, as a pure function: `AVAILABLE` with
 * empty `periods[]` is treated the same as `NOT_YET_ACQUIRED` (that
 * combination shouldn't occur via the normal acquisition path but isn't
 * claimed impossible). Shared by the render branch below and the focus-
 * management effect, so "does this block still show the trigger button" is
 * decided in exactly one place.
 */
function statementDisplayState(
  group: FinancialStatementGroup,
): "table" | "unavailable" | "pending" {
  if (group.acquisition_state === "available" && group.periods.length > 0) return "table";
  if (group.acquisition_state === "confirmed_unavailable") return "unavailable";
  return "pending";
}

/** One statement type's card: table, "unavailable" banner, or "not yet" banner + trigger. */
function StatementBlock({
  title,
  group,
  ticker,
  triggerAction,
}: {
  title: string;
  group: FinancialStatementGroup;
  ticker: string;
  triggerAction: React.ReactElement;
}) {
  const state = statementDisplayState(group);
  let body: React.ReactNode;
  if (state === "table") {
    body = <StatementTable periods={group.periods} />;
  } else if (state === "unavailable") {
    body = (
      <Banner tone="info">
        The data provider has no {title.toLowerCase()} for {ticker}.
      </Banner>
    );
  } else {
    body = (
      <Banner tone="info" action={triggerAction}>
        {title} isn&apos;t available yet.
      </Banner>
    );
  }
  return (
    <div className="flex flex-col gap-2">
      <Text variant="label">{title}</Text>
      {body}
    </div>
  );
}

/**
 * The Statements card body: `GET /companies/{ticker}/financials` (Document
 * 33, CTO-ratified) drives each statement type's own state independently —
 * one card can show a real table while another still shows an idle banner.
 * The acquisition trigger (`POST .../acquire`) is shared across all three,
 * matching the backend's own per-(ticker, period_type) — not per-statement-
 * type — request shape (Document 33 Amendment §4).
 */
function FinancialStatements({ ticker }: { ticker: string }) {
  const financials = useFinancialStatements(ticker, "annual");
  const acquisition = useFinancialsAcquisition(ticker);
  // Focus target for when every statement type turns terminal and the
  // trigger button this card previously had focus on unmounts — `tabIndex=
  // -1` keeps it out of the normal Tab order, reached only programmatically.
  const focusRef = useRef<HTMLDivElement>(null);
  const justMutatedRef = useRef(false);

  useEffect(() => {
    if (acquisition.isSuccess) {
      justMutatedRef.current = true;
      financials.refetch();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [acquisition.data]);

  useEffect(() => {
    if (!justMutatedRef.current || !financials.data) return;
    justMutatedRef.current = false;
    const stillPending = Object.values(financials.data.statements).some(
      (g) => statementDisplayState(g) === "pending",
    );
    if (!stillPending) {
      focusRef.current?.focus();
    }
  }, [financials.data]);

  if (financials.isPending) {
    return <Loader label="Loading financial statements…" />;
  }

  if (financials.isError) {
    return (
      <Banner
        tone="error"
        action={
          <Button variant="secondary" size="sm" onClick={() => financials.refetch()}>
            Retry
          </Button>
        }
      >
        Couldn&apos;t load financial statements.
      </Banner>
    );
  }

  const triggerAction = (
    <Button
      variant="secondary"
      size="sm"
      loading={acquisition.isPending}
      onClick={() => acquisition.mutate()}
    >
      {acquisition.isSuccess ? "Check status" : "Check for financial statements"}
    </Button>
  );

  const { statements } = financials.data;

  return (
    <div ref={focusRef} tabIndex={-1} className="flex flex-col gap-4">
      {acquisition.isError && <Banner tone="error">{acquisition.error.message}</Banner>}
      {(Object.keys(STATEMENT_TITLES) as (keyof typeof STATEMENT_TITLES)[]).map((key) => (
        <StatementBlock
          key={key}
          title={STATEMENT_TITLES[key]}
          group={statements[key]}
          ticker={ticker}
          triggerAction={triggerAction}
        />
      ))}
    </div>
  );
}

/**
 * The single-period "Financial Metrics" card's own gating — split out so it
 * no longer gates the independent Statements card below it (Finding C).
 * Distinguishes a job that's genuinely still running from one that reached
 * a terminal `failed`/`cancelled` status (Finding B): `useReport` alone
 * can't tell the two apart, since both currently present as `report.data
 * === null` — `GET /reports/{id}`'s own `status` field (via
 * `useReportStatus`) is what actually carries that distinction, and it was
 * being discarded before this fix.
 */
function FinancialMetricsCard({
  ticker,
  jobId,
  onGoToOverview,
}: {
  ticker: string;
  jobId: string | null;
  onGoToOverview: () => void;
}) {
  const report = useReport(jobId);
  const status = useReportStatus(jobId);

  if (!jobId) {
    return (
      <Banner tone="info">
        Run research on the Overview tab to see extracted financial metrics for {ticker}.
      </Banner>
    );
  }
  if (report.isPending || status.isPending) {
    return <Loader label="Loading financial metrics…" />;
  }
  if (report.isError || status.isError) {
    return (
      <Banner
        tone="error"
        action={
          <Button
            variant="secondary"
            size="sm"
            onClick={() => {
              report.refetch();
              status.refetch();
            }}
          >
            Retry
          </Button>
        }
      >
        Couldn&apos;t load financial metrics.
      </Banner>
    );
  }
  // A terminal non-success status is not "still running" — the honest state
  // Overview's own job hook already shows a Retry for; Financials has no
  // live job/stream of its own to retry inline, so it hands off there
  // rather than faking a retry it can't actually perform.
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
        Research is still running — financial metrics will appear here once it completes.
      </Banner>
    );
  }

  const data = report.data.extracted_data;
  const metrics = METRIC_FIELDS.map((f) => ({ ...f, value: data?.[f.key] })).filter(
    (f): f is { key: keyof ExtractedFinancials; label: string; value: string } => Boolean(f.value),
  );

  return (
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
  );
}

export function FinancialsSection({
  ticker,
  onGoToOverview,
}: {
  ticker: string;
  onGoToOverview: () => void;
}) {
  const jobId = useSearchParams().get("job");

  return (
    <div className="flex flex-col gap-6">
      <FinancialMetricsCard ticker={ticker} jobId={jobId} onGoToOverview={onGoToOverview} />

      <Card>
        <CardContent className="flex flex-col gap-3">
          <Text variant="body-strong">Financial Statements</Text>
          <FinancialStatements ticker={ticker} />
        </CardContent>
      </Card>
    </div>
  );
}
