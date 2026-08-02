"use client";

import { useState } from "react";
import Link from "next/link";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Chip } from "@/components/foundation/Chip";
import { FormField } from "@/components/foundation/FormField";
import { Loader } from "@/components/foundation/Loader";
import { Textarea } from "@/components/foundation/Textarea";
import { useAiAccessStatus } from "@/features/account-setup";
import { useReport } from "../application/useReport";
import { useResearchJob } from "../application/useResearchJob";
import { stageLabel } from "../internal/streamStages";
import { AIResponseCard } from "./AIResponseCard";

/**
 * Prompt Composer + AI Response turn (08_AI_Components.md — `CopilotPanel`,
 * Company variant). One follow-up at a time: the frozen `AI Chat Bubble`
 * persisted multi-turn thread is deferred — each submission reruns the full
 * pipeline (retriever→…→fact_checker) via `context_report_id`, seeded with
 * the prior brief, not a lightweight incremental chat completion. This
 * ships the Prompt Composer → AI Response Card exchange the frozen spec
 * requires, without inventing persisted session state the backend has no
 * concept of. `AI Suggestions` (grounded next-question chips) are also
 * deferred — they'd need a backend call to generate grounded suggestions,
 * which doesn't exist; hardcoded generic suggestions would violate the
 * spec's own anti-pattern ("context-free suggestions").
 */
export function CopilotPanel({
  ticker,
  contextReportId,
}: {
  ticker: string;
  contextReportId: string;
}) {
  const aiAccess = useAiAccessStatus();
  const job = useResearchJob(ticker, contextReportId);
  const report = useReport(job.jobId);
  const [query, setQuery] = useState("");

  const isRunning =
    job.stage === "thinking" || job.stage === "streaming" || job.stage === "grounded";

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!query.trim() || isRunning) return;
    job.start(query);
  };

  const retry = () => {
    if (query.trim()) job.retry(query);
  };

  // Disabled/Permission Denied (08_AI_Components.md, Prompt Composer states)
  // — explain and route to AI setup, never a dead field.
  if (aiAccess.state !== "valid") {
    return (
      <Banner
        tone="info"
        action={
          <Button variant="secondary" size="sm" asChild>
            <Link href="/settings">Set up AI access</Link>
          </Button>
        }
      >
        AI access isn&apos;t set up yet — set it up in Settings to ask follow-up questions.
      </Banner>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <Chip className="self-start">About {ticker}</Chip>
        <FormField label="Ask a follow-up question" required>
          <Textarea
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="e.g. What drove the margin change this quarter?"
            maxLength={2000}
            showCounter
            disabled={isRunning}
          />
        </FormField>
        <Button
          type="submit"
          loading={job.isStarting}
          disabled={!query.trim() || isRunning}
          className="self-start"
        >
          Ask
        </Button>
      </form>

      {job.startError && <Banner tone="error">{job.startError.message}</Banner>}

      {isRunning && (
        <div className="flex flex-col gap-4">
          <Loader label={stageLabel(job.stage)} />
          <Button variant="secondary" size="sm" className="self-start" onClick={job.cancel}>
            Stop generating
          </Button>
        </div>
      )}

      {(job.stage === "failed" || job.stage === "cancelled") && (
        <Banner tone={job.stage === "cancelled" ? "warning" : "error"}>
          {job.stage === "cancelled"
            ? "Cancelled."
            : (job.error?.message ?? "The follow-up failed.")}
        </Banner>
      )}

      {job.stage === "completed" && report.data && (
        <AIResponseCard report={report.data} heading="Follow-up answer" onRetry={retry} />
      )}
    </div>
  );
}
