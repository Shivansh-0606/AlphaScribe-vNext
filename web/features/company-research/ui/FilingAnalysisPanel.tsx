"use client";

import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Loader } from "@/components/foundation/Loader";
import { Text } from "@/components/foundation/Text";
import { FilingAnalysisViewer, type FilingViewerChunk } from "@/components/research/FilingViewer";
import { useFilingAnalysis } from "../application/useFilingAnalysis";
import { useFilingAnalysisJob } from "../application/useFilingAnalysisJob";
import { filingAnalysisStageLabel } from "../internal/streamStages";

/**
 * M14 — owns the Filing Analysis job lifecycle for one filing and renders
 * the frozen `FilingViewer` "Filing analysis" variant once a result exists
 * (mirrors `OverviewSection`'s ownership of `useResearchJob` +
 * `AIResponseCard`). The caller (`FilingsSection`) mounts this with
 * `key={docId}` so switching filings starts from a clean idle state rather
 * than carrying over a previous filing's job.
 */
export function FilingAnalysisPanel({
  ticker,
  docId,
  source,
  chunks,
}: {
  ticker: string;
  docId: string;
  source: string;
  chunks: FilingViewerChunk[];
}) {
  const job = useFilingAnalysisJob(ticker, docId);
  const analysis = useFilingAnalysis(ticker, docId, job.jobId);

  if (job.stage === "idle") {
    return (
      <div className="flex flex-col gap-3">
        <Text variant="small" className="text-muted-foreground">
          Generate a grounded Filing Summary, Risk Factors Digest, MD&amp;A Digest, and Important
          Changes digest for this filing — every claim cited back to its own text.
        </Text>
        <Button
          variant="secondary"
          size="sm"
          className="self-start"
          loading={job.isStarting}
          onClick={() => job.start()}
        >
          Analyze this filing
        </Button>
        {job.startError && <Banner tone="error">{job.startError.message}</Banner>}
      </div>
    );
  }

  if (job.stage === "analyzing") {
    return (
      <div className="flex flex-col gap-3">
        <Loader label={filingAnalysisStageLabel(job.stage)} />
        {job.events.length > 0 && (
          <ul className="flex flex-col gap-1">
            {job.events.map((event, i) => (
              <li key={i}>
                <Text variant="caption">{event.message ?? `${event.node}: ${event.status}`}</Text>
              </li>
            ))}
          </ul>
        )}
        <Button variant="secondary" size="sm" className="self-start" onClick={job.cancel}>
          Stop analyzing
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
          ? "Filing analysis was cancelled."
          : (job.error?.message ?? "Filing analysis failed.")}
      </Banner>
    );
  }

  // job.stage === "completed" — the result lives in the shared query cache (useFilingAnalysis).
  if (analysis.isPending) {
    return <Loader label="Loading the finished analysis…" />;
  }
  if (analysis.isError || !analysis.data) {
    return (
      <Banner
        tone="error"
        action={
          <Button variant="secondary" size="sm" onClick={() => analysis.refetch()}>
            Retry
          </Button>
        }
      >
        Couldn&apos;t load this filing&apos;s analysis.
      </Banner>
    );
  }

  return <FilingAnalysisViewer outputs={analysis.data.outputs} chunks={chunks} source={source} />;
}
