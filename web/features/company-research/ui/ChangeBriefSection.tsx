"use client";

import { useState } from "react";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { FormField } from "@/components/foundation/FormField";
import { Loader } from "@/components/foundation/Loader";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/foundation/Select";
import { Text } from "@/components/foundation/Text";
import { cn } from "@/lib/utils";
import { useChangeBrief } from "../application/useChangeBrief";
import { useChangeBriefJob } from "../application/useChangeBriefJob";
import { useFinancialStatements } from "../application/useFinancialStatements";
import { useReports } from "../application/useReports";
import type { CreateChangeBriefRequestBody } from "../integration/schemas";
import { changeBriefStageLabel } from "../internal/streamStages";
import { ChangeBriefResult } from "./ChangeBriefResult";

type ComparisonMode = "report" | "period";
type StatementType = "income" | "balance_sheet" | "cash_flow";
type PeriodType = "annual" | "quarterly";

const STATEMENT_LABEL: Record<StatementType, string> = {
  income: "Income Statement",
  balance_sheet: "Balance Sheet",
  cash_flow: "Cash Flow Statement",
};

/** Same `aria-current` toggle-button convention as `FilingViewSwitch`/`SectionNav`. */
function ModeSwitch({
  mode,
  onChange,
}: {
  mode: ComparisonMode;
  onChange: (m: ComparisonMode) => void;
}) {
  const options: { key: ComparisonMode; label: string }[] = [
    { key: "report", label: "Compare Reports" },
    { key: "period", label: "Compare Financial Periods" },
  ];
  return (
    <div role="group" aria-label="Comparison mode" className="flex flex-row gap-1">
      {options.map((option) => (
        <button
          key={option.key}
          type="button"
          aria-current={mode === option.key ? "true" : undefined}
          onClick={() => onChange(option.key)}
          className={cn(
            "rounded-md px-3 py-1 text-sm font-medium transition-colors",
            mode === option.key
              ? "bg-surface-hover text-foreground"
              : "text-muted-foreground hover:bg-surface-hover",
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

/**
 * SCR-06 "What Changed Since Last Review" (M15, Document 70 R4) — no frozen
 * Component Inventory entry exists for this surface (unlike M14's
 * `FilingViewer`), so the picker/result layout below is this feature's own
 * design, following the established job-lifecycle + a11y conventions rather
 * than a spec. Two independent, mutually exclusive comparison modes: two of
 * the ticker's own generated reports, or two financial-statement periods for
 * one statement type — never both at once (Document 70 R4 §7/§9.4).
 */
export function ChangeBriefSection({ ticker }: { ticker: string }) {
  const [mode, setMode] = useState<ComparisonMode>("report");

  const reports = useReports(ticker);
  const [baselineReportId, setBaselineReportId] = useState("");
  const [currentReportId, setCurrentReportId] = useState("");

  const [periodType, setPeriodType] = useState<PeriodType>("annual");
  const [statementType, setStatementType] = useState<StatementType>("income");
  const financials = useFinancialStatements(ticker, periodType, mode === "period");
  const [baselinePeriodEnd, setBaselinePeriodEnd] = useState("");
  const [currentPeriodEnd, setCurrentPeriodEnd] = useState("");

  const job = useChangeBriefJob(ticker);
  const changes = useChangeBrief(ticker, job.jobId);

  const periods = financials.data?.statements[statementType].periods ?? [];

  const canCompareReports =
    baselineReportId !== "" && currentReportId !== "" && baselineReportId !== currentReportId;
  // period_end is ISO-8601 YYYY-MM-DD, so lexicographic comparison is chronological
  // (mirrors the backend's own strictly-increasing check, Document 70 R4 §10.2/§15,
  // checked here too so the user gets instant feedback instead of a round-trip 422).
  const canComparePeriods =
    baselinePeriodEnd !== "" && currentPeriodEnd !== "" && baselinePeriodEnd < currentPeriodEnd;

  function handleCompare() {
    const request: CreateChangeBriefRequestBody =
      mode === "report"
        ? {
            comparison_type: "report",
            baseline_report_id: baselineReportId,
            current_report_id: currentReportId,
          }
        : {
            comparison_type: "period",
            period_type: periodType,
            statement_type: statementType,
            baseline_period_end: baselinePeriodEnd,
            current_period_end: currentPeriodEnd,
          };
    job.start(request);
  }

  if (job.stage === "idle") {
    return (
      <div className="flex flex-col gap-4">
        <ModeSwitch mode={mode} onChange={setMode} />

        {mode === "report" ? (
          <div className="flex flex-col gap-3">
            {reports.isPending && <Loader label="Loading reports…" />}
            {reports.isError && (
              <Banner
                tone="error"
                action={
                  <Button variant="secondary" size="sm" onClick={() => reports.refetch()}>
                    Retry
                  </Button>
                }
              >
                Couldn&apos;t load reports for {ticker}.
              </Banner>
            )}
            {reports.data && reports.data.reports.length < 2 && (
              <Banner tone="info">
                Generate at least two research reports for {ticker} on the Overview tab before
                comparing.
              </Banner>
            )}
            {reports.data && reports.data.reports.length >= 2 && (
              <>
                <FormField label="Baseline report (earlier)">
                  <Select value={baselineReportId} onValueChange={setBaselineReportId}>
                    <SelectTrigger aria-label="Baseline report (earlier)">
                      <SelectValue placeholder="Choose a report" />
                    </SelectTrigger>
                    <SelectContent>
                      {reports.data.reports.map((r) => (
                        <SelectItem key={r.id} value={r.id}>
                          {new Date(r.created_at).toLocaleDateString()} — {r.query}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </FormField>
                <FormField label="Current report (later)">
                  <Select value={currentReportId} onValueChange={setCurrentReportId}>
                    <SelectTrigger aria-label="Current report (later)">
                      <SelectValue placeholder="Choose a report" />
                    </SelectTrigger>
                    <SelectContent>
                      {reports.data.reports.map((r) => (
                        <SelectItem key={r.id} value={r.id}>
                          {new Date(r.created_at).toLocaleDateString()} — {r.query}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </FormField>
                {baselineReportId !== "" && baselineReportId === currentReportId && (
                  <Text variant="small" className="text-muted-foreground">
                    Baseline and current must be two different reports.
                  </Text>
                )}
              </>
            )}
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            <FormField label="Period type">
              <Select value={periodType} onValueChange={(v) => setPeriodType(v as PeriodType)}>
                <SelectTrigger aria-label="Period type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="annual">Annual</SelectItem>
                  <SelectItem value="quarterly">Quarterly</SelectItem>
                </SelectContent>
              </Select>
            </FormField>
            <FormField label="Statement">
              <Select
                value={statementType}
                onValueChange={(v) => setStatementType(v as StatementType)}
              >
                <SelectTrigger aria-label="Statement">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {(Object.keys(STATEMENT_LABEL) as StatementType[]).map((key) => (
                    <SelectItem key={key} value={key}>
                      {STATEMENT_LABEL[key]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </FormField>

            {financials.isPending && <Loader label="Loading financial periods…" />}
            {financials.isError && (
              <Banner
                tone="error"
                action={
                  <Button variant="secondary" size="sm" onClick={() => financials.refetch()}>
                    Retry
                  </Button>
                }
              >
                Couldn&apos;t load financial periods for {ticker}.
              </Banner>
            )}
            {financials.data && periods.length < 2 && (
              <Banner tone="info">
                {STATEMENT_LABEL[statementType]} has fewer than two available periods for {ticker} —
                check the Financials tab to acquire more.
              </Banner>
            )}
            {financials.data && periods.length >= 2 && (
              <>
                <FormField label="Baseline period (earlier)">
                  <Select value={baselinePeriodEnd} onValueChange={setBaselinePeriodEnd}>
                    <SelectTrigger aria-label="Baseline period (earlier)">
                      <SelectValue placeholder="Choose a period" />
                    </SelectTrigger>
                    <SelectContent>
                      {periods.map((p) => (
                        <SelectItem key={p.period_end} value={p.period_end}>
                          {p.period_end} (FY{p.fiscal_year})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </FormField>
                <FormField label="Current period (later)">
                  <Select value={currentPeriodEnd} onValueChange={setCurrentPeriodEnd}>
                    <SelectTrigger aria-label="Current period (later)">
                      <SelectValue placeholder="Choose a period" />
                    </SelectTrigger>
                    <SelectContent>
                      {periods.map((p) => (
                        <SelectItem key={p.period_end} value={p.period_end}>
                          {p.period_end} (FY{p.fiscal_year})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </FormField>
                {baselinePeriodEnd !== "" && currentPeriodEnd !== "" && !canComparePeriods && (
                  <Text variant="small" className="text-muted-foreground">
                    Baseline period must be strictly earlier than the current period.
                  </Text>
                )}
              </>
            )}
          </div>
        )}

        <Button
          loading={job.isStarting}
          disabled={mode === "report" ? !canCompareReports : !canComparePeriods}
          onClick={handleCompare}
          className="self-start"
        >
          Compare
        </Button>
        {job.startError && <Banner tone="error">{job.startError.message}</Banner>}
      </div>
    );
  }

  if (job.stage === "computing") {
    return (
      <div className="flex flex-col gap-3">
        <Loader label={changeBriefStageLabel(job.stage)} />
        <Button variant="secondary" size="sm" className="self-start" onClick={job.cancel}>
          Stop
        </Button>
      </div>
    );
  }

  if (job.stage === "failed" || job.stage === "cancelled") {
    return (
      <Banner
        tone={job.stage === "cancelled" ? "warning" : "error"}
        action={
          <Button variant="secondary" size="sm" onClick={job.retry}>
            Retry
          </Button>
        }
      >
        {job.stage === "cancelled"
          ? "Change brief was cancelled."
          : (job.error?.message ?? "Change brief failed.")}
      </Banner>
    );
  }

  // job.stage === "completed" — the result lives in the shared query cache (useChangeBrief).
  if (changes.isPending) {
    return <Loader label="Loading the finished change brief…" />;
  }
  if (changes.isError || !changes.data) {
    return (
      <Banner
        tone="error"
        action={
          <Button variant="secondary" size="sm" onClick={() => changes.refetch()}>
            Retry
          </Button>
        }
      >
        Couldn&apos;t load the change brief.
      </Banner>
    );
  }
  return <ChangeBriefResult payload={changes.data} />;
}
