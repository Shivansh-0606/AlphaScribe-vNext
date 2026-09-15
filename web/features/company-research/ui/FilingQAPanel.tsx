"use client";

import { useState } from "react";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { FormField } from "@/components/foundation/FormField";
import { Loader } from "@/components/foundation/Loader";
import { Text } from "@/components/foundation/Text";
import { Textarea } from "@/components/foundation/Textarea";
import {
  FilingAnalysisViewer,
  type FilingAnalysisOutputData,
  type FilingViewerChunk,
} from "@/components/research/FilingViewer";
import { useFilingQA } from "../application/useFilingQA";
import { useFilingQAJob } from "../application/useFilingQAJob";
import { filingQAStageLabel } from "../internal/streamStages";

/** Ask-a-question form, reused for the first question (idle) and for asking
 * a new one after a completed answer — each submission is a brand new job
 * with no memory of the last (Document 87 §1.2/§19 forbids simulating
 * conversational state the backend doesn't have). */
function QuestionForm({
  onSubmit,
  loading,
  error,
  label = "Ask a question about this filing",
  submitLabel = "Ask",
}: {
  onSubmit: (question: string) => void;
  loading: boolean;
  error?: string;
  label?: string;
  submitLabel?: string;
}) {
  const [question, setQuestion] = useState("");
  return (
    <form
      className="flex flex-col gap-3"
      onSubmit={(event) => {
        event.preventDefault();
        const trimmed = question.trim();
        if (!trimmed) return;
        onSubmit(trimmed);
        setQuestion("");
      }}
    >
      <FormField label={label}>
        {/* No client-side maxLength: the contract fixes no numeric ceiling for
         * question length (Document 87 §17.2/§20 OAQ-6) — it's undisclosed
         * operational config (`settings.fqa_max_question_chars`), and the
         * server's 422 is the only length gate (brief §2, explicit). */}
        <Textarea
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="e.g. What does the filing say about supply chain risk?"
        />
      </FormField>
      <Button type="submit" loading={loading} disabled={!question.trim()} className="self-start">
        {submitLabel}
      </Button>
      {error && <Banner tone="error">{error}</Banner>}
    </form>
  );
}

/**
 * M16 — owns the Filing Q&A job lifecycle for one filing and renders the
 * answer through the reused `FilingAnalysisViewer` via a one-entry adapter
 * (implementation brief §3): FQA has exactly one answer, so there's no
 * cross-output citation collision to renumber the way M14's four outputs
 * need. The adapter derives the viewer's `"partial"` state from a non-empty
 * `coverage_boundaries` — FQA's own wire `state` is only 2-valued
 * (`answered` / `insufficient_evidence`), but the partial-coverage
 * disclosure Document 87 §9.1 requires renders only through the viewer's
 * existing `"partial"` treatment, so collapsing every `answered` result
 * straight to `"complete"` would silently drop it.
 */
export function FilingQAPanel({
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
  const job = useFilingQAJob(ticker, docId);
  const answer = useFilingQA(ticker, docId, job.jobId);

  if (job.stage === "idle") {
    return (
      <QuestionForm onSubmit={job.start} loading={job.isStarting} error={job.startError?.message} />
    );
  }

  if (job.stage === "answering") {
    return (
      <div className="flex flex-col gap-3">
        <Loader label={filingQAStageLabel(job.stage)} />
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
          ? "Question was cancelled."
          : (job.error?.message ?? "Couldn't answer the question.")}
      </Banner>
    );
  }

  // job.stage === "completed" — the answer lives in the shared query cache (useFilingQA).
  if (answer.isPending) {
    return <Loader label="Loading the answer…" />;
  }
  if (answer.isError || !answer.data) {
    return (
      <Banner
        tone="error"
        action={
          <Button variant="secondary" size="sm" onClick={() => answer.refetch()}>
            Retry
          </Button>
        }
      >
        Couldn&apos;t load the answer.
      </Banner>
    );
  }

  const outputs: Record<string, FilingAnalysisOutputData> = {
    Answer: {
      narrative: answer.data.answer_text,
      sources: answer.data.sources,
      cited_source_indices: answer.data.cited_source_indices,
      state:
        answer.data.state === "insufficient_evidence"
          ? "insufficient_evidence"
          : answer.data.coverage_boundaries.length > 0
            ? "partial"
            : "complete",
      coverage_boundaries: answer.data.coverage_boundaries,
    },
  };

  return (
    <div className="flex flex-col gap-4">
      <Text variant="small" className="text-muted-foreground">
        Q: {answer.data.question}
      </Text>
      <FilingAnalysisViewer outputs={outputs} chunks={chunks} source={source} />
      <QuestionForm
        onSubmit={job.start}
        loading={job.isStarting}
        error={job.startError?.message}
        label="Ask another question"
        submitLabel="Ask"
      />
    </div>
  );
}
