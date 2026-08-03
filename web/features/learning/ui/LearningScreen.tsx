"use client";

import { useState } from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { FormField } from "@/components/foundation/FormField";
import { Heading } from "@/components/foundation/Heading";
import { Input } from "@/components/foundation/Input";
import { Loader } from "@/components/foundation/Loader";
import { ResearchTemplate } from "@/components/layouts/ResearchTemplate";
import { useAiAccessStatus } from "@/features/account-setup";
import { useExplanation } from "../application/useExplanation";
import { useExplanationJob } from "../application/useExplanationJob";
import { stageLabel } from "../internal/streamStages";
import { ConceptComposer } from "./ConceptComposer";
import { LearningExplanation } from "./LearningExplanation";

/**
 * SCR-08 Learning — the feature's public screen composition. Frozen entry
 * points: Company Research's "Explain This" (passes `?ticker=`, optionally
 * `?job=` as the grounding report) and global navigation with no context at
 * all — the latter hits the frozen Empty Behaviour ("missing company
 * context → prompt to choose an example", `06_UX_Specifications.md`).
 *
 * `requestExplanation`/the SSE stream this drives are a PROPOSED contract —
 * see `integration/schemas.ts`. Every state below (Loading/Empty/Error/AI
 * Thinking/AI Streaming) is real, live-verifiable UI; only the backend
 * behind it doesn't exist yet.
 */
export function LearningScreen({
  initialTicker,
  contextReportId,
}: {
  initialTicker?: string;
  contextReportId?: string;
}) {
  const router = useRouter();
  const [tickerInput, setTickerInput] = useState("");
  const aiAccess = useAiAccessStatus();
  const ticker = initialTicker?.toUpperCase();

  // Empty Behaviour: no company context yet — prompt to choose an example (06_UX_Specifications.md SCR-08).
  if (!ticker) {
    return (
      <ResearchTemplate>
        <div className="flex flex-col gap-4">
          <Heading level="h1">Learning</Heading>
          <Banner tone="info">
            Concept explanations are grounded in a real company&apos;s figures — choose an example
            company to get started, or open Learning from a Company Research report.
          </Banner>
          <form
            onSubmit={(event) => {
              event.preventDefault();
              if (!tickerInput.trim()) return;
              router.push(`/learning?ticker=${tickerInput.trim().toUpperCase()}` as Route);
            }}
            className="flex flex-col gap-3"
          >
            <FormField label="Example company ticker">
              <Input
                value={tickerInput}
                onChange={(event) => setTickerInput(event.target.value)}
                placeholder="e.g. MSFT"
                className="max-w-xs"
              />
            </FormField>
            <Button type="submit" disabled={!tickerInput.trim()} className="self-start">
              Continue
            </Button>
          </form>
        </div>
      </ResearchTemplate>
    );
  }

  return (
    <LearningWithTicker
      ticker={ticker}
      contextReportId={contextReportId}
      aiAccessValid={aiAccess.state === "valid"}
    />
  );
}

function LearningWithTicker({
  ticker,
  contextReportId,
  aiAccessValid,
}: {
  ticker: string;
  contextReportId?: string;
  aiAccessValid: boolean;
}) {
  const job = useExplanationJob(ticker, contextReportId);
  const explanation = useExplanation(job.jobId);
  const isRunning = job.stage === "thinking" || job.stage === "streaming";

  return (
    <ResearchTemplate>
      <div className="flex flex-col gap-6">
        <Heading level="h1">Learning — {ticker}</Heading>

        {!aiAccessValid && (
          <Banner
            tone="info"
            action={
              <Button variant="secondary" size="sm" asChild>
                <a href="/settings">Set up AI access</a>
              </Button>
            }
          >
            AI access isn&apos;t set up yet — set it up in Settings to ask for an explanation.
          </Banner>
        )}

        {aiAccessValid && (
          <>
            <ConceptComposer
              ticker={ticker}
              isRunning={isRunning}
              isStarting={job.isStarting}
              onAsk={job.start}
            />

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
                  : (job.error?.message ?? "The explanation failed.")}
              </Banner>
            )}

            {job.stage === "completed" && explanation.isPending && (
              <Loader label="Loading the explanation…" />
            )}
            {job.stage === "completed" && explanation.isError && (
              <Banner
                tone="error"
                action={
                  <Button variant="secondary" size="sm" onClick={() => explanation.refetch()}>
                    Retry
                  </Button>
                }
              >
                Couldn&apos;t load the explanation.
              </Banner>
            )}
            {job.stage === "completed" && explanation.data && (
              <LearningExplanation explanation={explanation.data} />
            )}
          </>
        )}
      </div>
    </ResearchTemplate>
  );
}
