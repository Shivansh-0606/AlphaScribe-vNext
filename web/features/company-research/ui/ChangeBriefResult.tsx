"use client";

import ReactMarkdown from "react-markdown";
import { Badge } from "@/components/foundation/Badge";
import { Card, CardContent } from "@/components/foundation/Card";
import { Text } from "@/components/foundation/Text";
import { formatMetricValue, type StatementMetricUnit } from "@/components/research/StatementTable";
import { SourceReference } from "@/components/research/SourceReference";
import remarkCitations from "@/lib/markdown/citations";
import { useReport } from "../application/useReport";
import type { ChangeBriefPayload, ReportDoc } from "../integration/schemas";

const STATE_BADGE: Record<
  ChangeBriefPayload["state"],
  { label: string; variant: "warning" | "neutral" } | null
> = {
  complete: null,
  partial: { label: "Partial", variant: "warning" },
  insufficient_evidence: { label: "Insufficient evidence", variant: "neutral" },
};

const CHANGE_KIND_LABEL = { changed: "Changed", new: "New", removed: "Removed" } as const;

function reportLabel(identity: {
  report_id: string | null;
  ticker: string | null;
  company_name: string | null;
}): string {
  return identity.company_name ?? identity.ticker ?? identity.report_id ?? "Unknown report";
}

function periodLabel(identity: { period_end: string; period_type: string }): string {
  return `${identity.period_end} (${identity.period_type})`;
}

function narrativeSourceExcerpt(field: string, report: ReportDoc | null | undefined): string {
  if (!report) return "Source report is still loading.";
  if (field === "extracted_data") return JSON.stringify(report.extracted_data ?? {}, null, 2);
  if (field === "sentiment_analysis")
    return JSON.stringify(report.sentiment_analysis ?? {}, null, 2);
  if (field === "scorecard") return JSON.stringify(report.scorecard ?? {}, null, 2);
  return report.draft_report;
}

/**
 * Renders one completed Change Brief (M15, Document 70 R4). Presentational
 * only — the caller (`ChangeBriefSection`) owns the job lifecycle and the
 * idle/computing/failed/cancelled states; this renders a loaded result,
 * honestly, including the `insufficient_evidence`/`partial` states §11/§14
 * require. `comparison_type` fully narrows `baseline`/`current`/`items`
 * (the discriminated union), so the two render branches below are exhaustive
 * over the two shipped modes, not a guess at future ones.
 *
 * Citation numbering: each item's `sources[].index` is only unique *within*
 * that item (mirrors M14's per-output scoping — Document 70 R4 doesn't
 * promise cross-item uniqueness either), so — same fix as
 * `FilingAnalysisViewer` — every item's citations are renumbered to a
 * page-wide-unique index before rendering, reusing `SourceReference`/
 * `remarkCitations` unmodified.
 */
export function ChangeBriefResult({ payload }: { payload: ChangeBriefPayload }) {
  const isReportMode = payload.comparison_type === "report";
  const baselineReportId = isReportMode ? payload.baseline.report_id : null;
  const currentReportId = isReportMode ? payload.current.report_id : null;
  const baselineReport = useReport(baselineReportId);
  const currentReport = useReport(currentReportId);

  const badge = STATE_BADGE[payload.state];
  const baselineLabel = isReportMode
    ? reportLabel(payload.baseline)
    : periodLabel(payload.baseline);
  const currentLabel = isReportMode ? reportLabel(payload.current) : periodLabel(payload.current);

  let offset = 0;
  function renumber<T extends { index: number }>(sources: T[]): (T & { globalIndex: number })[] {
    const localOffset = offset;
    offset += sources.length;
    return sources.map((s, i) => ({ ...s, globalIndex: localOffset + i + 1 }));
  }

  return (
    <div className="flex flex-col gap-4" data-slot="change-brief-result">
      <div className="flex flex-wrap items-center gap-2">
        <Text variant="body-strong">
          {baselineLabel} → {currentLabel}
        </Text>
        {badge && <Badge variant={badge.variant}>{badge.label}</Badge>}
      </div>

      {payload.coverage_boundaries.length > 0 && (
        <Text variant="small" className="text-muted-foreground">
          {payload.coverage_boundaries.join(" · ")}
        </Text>
      )}

      {payload.items.length === 0 ? (
        <Text variant="small" className="text-muted-foreground" data-slot="change-brief-empty">
          {payload.state === "insufficient_evidence"
            ? "Not enough grounded evidence to report what changed."
            : "Nothing substantive changed between these two."}
        </Text>
      ) : (
        <div className="flex flex-col gap-3">
          {isReportMode
            ? payload.items.map((item, i) => {
                const renumbered = renumber(item.sources);
                const globalByLocal = new Map(renumbered.map((s) => [s.index, s.globalIndex]));
                const explanation = item.explanation.replace(/\[(\d+)\]/g, (match, n: string) => {
                  const g = globalByLocal.get(Number(n));
                  return g ? `[${g}]` : match;
                });
                return (
                  <Card key={i}>
                    <CardContent className="flex flex-col gap-2">
                      <Text variant="body-strong">{item.summary}</Text>
                      <div className="[&_a]:text-primary text-foreground font-sans text-sm leading-normal [&_p]:my-2">
                        <ReactMarkdown remarkPlugins={[remarkCitations]}>
                          {explanation}
                        </ReactMarkdown>
                      </div>
                      <ol className="flex flex-col gap-1">
                        {renumbered.map((s) => {
                          const side = s.report_id === baselineReportId ? "Baseline" : "Current";
                          const report =
                            s.report_id === baselineReportId
                              ? baselineReport.data
                              : currentReport.data;
                          return (
                            <SourceReference
                              key={`${i}-${s.index}`}
                              index={s.globalIndex}
                              source={`${side} report — ${s.field.replace(/_/g, " ")}`}
                              excerpt={narrativeSourceExcerpt(s.field, report)}
                            />
                          );
                        })}
                      </ol>
                    </CardContent>
                  </Card>
                );
              })
            : payload.items.map((item, i) => {
                const renumbered = renumber(item.sources);
                const unit = item.unit as StatementMetricUnit;
                return (
                  <Card key={i}>
                    <CardContent className="flex flex-col gap-2">
                      <div className="flex items-center justify-between gap-2">
                        <Text variant="body-strong">{item.metric}</Text>
                        <Badge variant="neutral">{CHANGE_KIND_LABEL[item.change_kind]}</Badge>
                      </div>
                      <Text variant="small">
                        {item.before
                          ? formatMetricValue(item.before.value, unit, item.currency)
                          : "—"}
                        {" → "}
                        {item.after
                          ? formatMetricValue(item.after.value, unit, item.currency)
                          : "—"}
                        {item.percent_delta != null &&
                          ` (${(item.percent_delta * 100).toFixed(1)}%)`}
                      </Text>
                      <ol className="flex flex-col gap-1">
                        {renumbered.map((s) => (
                          <SourceReference
                            key={`${i}-${s.index}`}
                            index={s.globalIndex}
                            source={`${s.statement_type} — ${s.period_end}`}
                            excerpt={`${s.statement_type} statement, period ending ${s.period_end}: ${s.metric}`}
                          />
                        ))}
                      </ol>
                    </CardContent>
                  </Card>
                );
              })}
        </div>
      )}
    </div>
  );
}
