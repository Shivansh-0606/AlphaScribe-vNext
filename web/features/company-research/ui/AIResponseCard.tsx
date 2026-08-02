"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Card, CardContent } from "@/components/foundation/Card";
import { Heading } from "@/components/foundation/Heading";
import { Text } from "@/components/foundation/Text";
import { ConfidenceIndicator } from "@/components/research/ConfidenceIndicator";
import { SourceReference } from "@/components/research/SourceReference";
import remarkCitations from "@/lib/markdown/citations";
import type { ReportDoc } from "../integration/schemas";
import { isUsableReport } from "../internal/reportUsability";
import { confidenceLabel } from "@/components/research/ConfidenceIndicator";

/**
 * AI Response Card (08_AI_Components.md) — the grounded AI answer surface,
 * shared by Overview's initial brief (Phase 4A) and Copilot follow-up
 * answers (Phase 4C): both render the exact same `ReportDoc` shape, so this
 * is one component, not two. Never rendered without sources (Law 3) — the
 * citation markers in `draft_report` and the source list below are the same
 * traceability mechanism either way.
 *
 * Feature-internal, not `web/components/research/` — its only two consumers
 * (`OverviewSection`, `CopilotPanel`) are both inside `company-research`,
 * and it depends on this feature's own `remarkCitations`/`confidenceLabel`
 * internals, which a genuinely shared cross-feature component couldn't.
 *
 * `isUsableReport()` is checked here, centrally, rather than by each
 * caller — a backend `status: "completed"` only means the pipeline didn't
 * error; it does NOT mean the pipeline produced anything worth reading
 * (Trust-First: confirmed live, a run can complete with an empty brief when
 * the LLM provider fails mid-run). Every current and future caller of this
 * component gets that honesty for free instead of re-deriving it.
 */
export function AIResponseCard({
  report,
  heading = "AI Research Brief",
  onRetry,
}: {
  report: ReportDoc;
  heading?: string;
  /** Wired by the caller (it owns the job/query, this component doesn't) — shown only in the unusable-report state. */
  onRetry?: () => void;
}) {
  if (!isUsableReport(report)) {
    return (
      <Banner
        tone="error"
        action={
          onRetry ? (
            <Button variant="secondary" size="sm" onClick={onRetry}>
              Retry
            </Button>
          ) : undefined
        }
      >
        The research pipeline finished, but didn&apos;t produce a usable result — there&apos;s no
        trustworthy AI summary to show, since the brief has no content or no sources to ground it
        in. This can happen when the underlying AI provider is unavailable or errors mid-run.
      </Banner>
    );
  }

  const confidence = confidenceLabel(report.scorecard.overall);

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardContent className="flex flex-col gap-4">
          <div className="flex items-center justify-between gap-2">
            <Text variant="body-strong">{heading}</Text>
            <ConfidenceIndicator label={confidence} />
          </div>
          <div className="[&_a]:text-primary text-foreground font-sans text-base leading-normal [&_h1]:font-sans [&_h2]:font-sans [&_h3]:font-sans [&_li]:my-1 [&_p]:my-3 [&_ul]:my-3 [&_ul]:list-disc [&_ul]:pl-5">
            <ReactMarkdown remarkPlugins={[remarkCitations]}>{report.draft_report}</ReactMarkdown>
          </div>
          {/* AI Action Toolbar (08_AI_Components.md) — Copy only. Add to
              report/session, Regenerate, and Feedback all need backend
              support (a saved-report/session endpoint, a feedback endpoint)
              that doesn't exist — deferred, not silently invented. */}
          {report.draft_report && (
            <div className="flex justify-end">
              <CopyButton text={report.draft_report} />
            </div>
          )}
        </CardContent>
      </Card>

      {/* `sentiment_analysis` can be `{}` (tone node failed) — check for real
          content, not just object presence. */}
      {report.sentiment_analysis?.sentiment && (
        <Card>
          <CardContent className="flex flex-col gap-2">
            <Text variant="body-strong">Sentiment: {report.sentiment_analysis.sentiment}</Text>
            <Text variant="small" className="text-muted-foreground">
              {report.sentiment_analysis.summary}
            </Text>
          </CardContent>
        </Card>
      )}

      {(() => {
        // `extracted_data` can also be `{}` — truthy but nothing to show.
        const metrics = Object.entries(report.extracted_data ?? {}).filter(([, value]) => value);
        return (
          metrics.length > 0 && (
            <Card>
              <CardContent className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                {metrics.map(([key, value]) => (
                  <div key={key} className="flex flex-col gap-1">
                    <Text variant="label">{key.replace(/_/g, " ")}</Text>
                    <Text variant="figure">{value}</Text>
                  </div>
                ))}
              </CardContent>
            </Card>
          )
        );
      })()}

      <div className="flex flex-col gap-2">
        <Heading level="h3">Sources</Heading>
        <ol className="flex flex-col gap-2">
          {report.source_documents.map((source, i) => (
            <SourceReference
              key={`${source.doc_id}-${source.chunk_idx}`}
              index={i + 1}
              source={source.source}
              excerpt={source.text}
            />
          ))}
        </ol>
      </div>
    </div>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);

  return (
    <Button
      variant="quiet"
      size="sm"
      onClick={() => {
        void navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }}
    >
      {copied ? "Copied" : "Copy"}
    </Button>
  );
}
