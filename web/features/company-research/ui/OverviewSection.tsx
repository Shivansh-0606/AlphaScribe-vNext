"use client";

import { useEffect, useRef, useState } from "react";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Card, CardContent } from "@/components/foundation/Card";
import { FormField } from "@/components/foundation/FormField";
import { Link } from "@/components/foundation/Link";
import { Loader } from "@/components/foundation/Loader";
import { Text } from "@/components/foundation/Text";
import { Textarea } from "@/components/foundation/Textarea";
import { useFocusOnChange } from "@/lib/a11y/useFocusOnChange";
import type { AppError } from "@/lib/errors/app-error";
import { readSessionValue, removeSessionValue, writeSessionValue } from "@/lib/state/sessionValue";
import * as companyResearchApi from "../integration/api";
import type { IngestResult } from "../integration/schemas";
import { useReport } from "../application/useReport";
import { useResearchJob } from "../application/useResearchJob";
import { isUsableReport } from "../internal/reportUsability";
import { stageLabel } from "../internal/streamStages";
import { AIResponseCard } from "./AIResponseCard";

const NO_FILINGS_MARKER = "No filings ingested";

/** Namespaced sessionStorage key for a job's original query — read back so
 * Retry works after a reload/deep-link, since the backend doesn't expose
 * the original query for a non-completed job and this is otherwise only
 * ever held in this component's own local state. */
function retryQueryKey(jobId: string): string {
  return `company-research:retry-query:${jobId}`;
}

/**
 * SCR-06 Overview — the core of Phase 4A: ingest-on-demand, research
 * initiation, the AI Thinking/Streaming/Grounded/Completed lifecycle, and
 * the finished AI Response Card (draft report + citations + qualitative
 * Confidence Indicator). One component covers all of it since the states
 * are mutually exclusive views of the same run, not separate screens.
 */
export function OverviewSection({
  ticker,
  initialJobId,
}: {
  ticker: string;
  initialJobId: string | null;
}) {
  const router = useRouter();
  const job = useResearchJob(ticker);
  const { resume } = job;
  const report = useReport(job.jobId);
  // Seeded from sessionStorage when this mount IS a deep link (reload/shared
  // URL) — the only way Retry can know what to resubmit, since the backend's
  // `GET /reports/{job_id}` doesn't expose the original query for a
  // non-completed job. A fresh visit (`initialJobId` null) has nothing to read.
  const [query, setQuery] = useState(() =>
    initialJobId ? (readSessionValue(retryQueryKey(initialJobId)) ?? "") : "",
  );
  const [pastedText, setPastedText] = useState("");
  const resumedRef = useRef(false);
  // Captured once, at mount, via the lazy initializer — NOT the live
  // `initialJobId` prop. The effect below keeps the URL in sync by writing
  // `?job=` back after `start()`, which flows back down as a new
  // `initialJobId` prop; depending on that live prop here would misread our
  // own URL sync as a fresh deep link and `resume()` a job that's already
  // streaming, duplicating the event history mid-run.
  const [deepLinkJobId] = useState(initialJobId);

  // Resume from a `?job=` deep link once (Law 6 — never lose completed/in-progress work on reload).
  useEffect(() => {
    if (deepLinkJobId && !resumedRef.current) {
      resumedRef.current = true;
      resume(deepLinkJobId);
    }
  }, [deepLinkJobId, resume]);

  // Keep the URL in sync with the active job so a reload can resume it.
  // This component only ever renders under `/research` — the base path is
  // fixed, not user input, so the cast mirrors GlobalNav's own known-route casts.
  useEffect(() => {
    if (!job.jobId) return;
    const params = new URLSearchParams({ ticker, job: job.jobId });
    router.replace(`/research?${params.toString()}` as Route);
  }, [job.jobId, router, ticker]);

  // Persist the query the moment a job (fresh start or retry) gets an id —
  // the only record of it that survives a reload. `query` can't actually
  // change again while a job is in flight (the composer that edits it isn't
  // rendered once we leave "idle"), so this fires once per new job, not on
  // every render.
  useEffect(() => {
    if (job.jobId) writeSessionValue(retryQueryKey(job.jobId), query);
  }, [job.jobId, query]);

  // Clean up once the job produced a genuinely usable report — Retry is no
  // longer offered past this point, so there's nothing left to resubmit for.
  // Failed/cancelled jobs deliberately keep their persisted query (Retry
  // still needs it) until the tab itself closes (sessionStorage's own bound).
  useEffect(() => {
    if (job.jobId && report.data && isUsableReport(report.data)) {
      removeSessionValue(retryQueryKey(job.jobId));
    }
  }, [job.jobId, report.data]);

  const ingestText = useMutation<IngestResult, AppError, string>({
    mutationFn: (text) =>
      companyResearchApi.ingestText({ ticker, source: "Pasted document", text }),
  });
  const ingestEdgar = useMutation<IngestResult, AppError, void>({
    mutationFn: () => companyResearchApi.ingestEdgar({ ticker, form_type: "10-Q" }),
  });
  const ingestSamples = useMutation<
    { ingested: IngestResult[]; total_samples: number },
    AppError,
    void
  >({
    mutationFn: companyResearchApi.ingestSamples,
  });

  const retryAfterIngest = () => {
    if (query.trim()) job.retry(query);
  };

  const handleStart = (event: React.FormEvent) => {
    event.preventDefault();
    if (!query.trim()) return;
    job.start(query);
  };

  const needsIngest = job.startError?.message.includes(NO_FILINGS_MARKER) ?? false;
  const ingestError = ingestEdgar.error ?? ingestText.error ?? ingestSamples.error;

  // Enter submits (Shift+Enter still inserts a newline, native textarea
  // behavior); guards the exact condition the button's own disabled state
  // uses, `job.isStarting` included — the button is only visibly disabled by
  // its `loading` prop during that window, so a keyboard Enter needs its own
  // check to avoid a double submit before `job.stage` leaves "idle".
  const handleComposerKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    if (!query.trim() || job.isStarting) return;
    job.start(query);
  };

  // Moves focus to the arriving response/status region once a run leaves
  // "thinking/streaming/grounded" (08_AI_Components.md Prompt Composer:
  // "submit moves attention to the arriving response region considerately")
  // — never during the run itself, only on the actual terminal transition.
  const focusKey =
    job.stage === "failed" || job.stage === "cancelled"
      ? job.stage
      : report.data
        ? `completed:${report.data.id}`
        : report.isError
          ? "completed:error"
          : null;
  const focusRef = useFocusOnChange(focusKey);

  // --- Idle: query form (+ inline ingest empty-state if the ticker has no filings) ---
  if (job.stage === "idle") {
    return (
      <div className="flex flex-col gap-4">
        <form onSubmit={handleStart} className="flex flex-col gap-3">
          <FormField label="What do you want to know?" required>
            <Textarea
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={handleComposerKeyDown}
              placeholder="e.g. Summarize the latest quarterly results and key risks."
              maxLength={2000}
              showCounter
            />
          </FormField>
          <Button
            type="submit"
            loading={job.isStarting}
            disabled={!query.trim()}
            className="self-start"
          >
            Start research
          </Button>
        </form>

        {job.startError && !needsIngest && <Banner tone="error">{job.startError.message}</Banner>}

        {needsIngest && (
          <Card>
            <CardContent className="flex flex-col gap-4">
              <Text variant="body-strong">No filings for {ticker} yet</Text>
              <Text variant="small" className="text-muted-foreground">
                Ingest a filing first — research picks it up automatically once it&apos;s in.
              </Text>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  loading={ingestSamples.isPending}
                  onClick={() => ingestSamples.mutate(undefined, { onSuccess: retryAfterIngest })}
                >
                  Load sample filings
                </Button>
                <Button
                  variant="secondary"
                  size="sm"
                  loading={ingestEdgar.isPending}
                  onClick={() => ingestEdgar.mutate(undefined, { onSuccess: retryAfterIngest })}
                >
                  Fetch latest 10-Q from EDGAR
                </Button>
              </div>
              <FormField label="Or paste filing text">
                <Textarea
                  value={pastedText}
                  onChange={(event) => setPastedText(event.target.value)}
                  maxLength={1_000_000}
                />
              </FormField>
              <Button
                variant="secondary"
                size="sm"
                disabled={!pastedText.trim()}
                loading={ingestText.isPending}
                className="self-start"
                onClick={() => ingestText.mutate(pastedText, { onSuccess: retryAfterIngest })}
              >
                Ingest pasted text
              </Button>
              {ingestError && <Banner tone="error">{ingestError.message}</Banner>}
            </CardContent>
          </Card>
        )}
      </div>
    );
  }

  // --- Thinking / Streaming / Grounded: visible, bounded progress (never a frozen void) ---
  if (job.stage === "thinking" || job.stage === "streaming" || job.stage === "grounded") {
    return (
      <div className="flex flex-col gap-4">
        <Loader label={stageLabel(job.stage)} />
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
          Stop generating
        </Button>
      </div>
    );
  }

  // --- Failed / Cancelled: retain the produced trace, offer retry (Law 6) ---
  if (job.stage === "failed" || job.stage === "cancelled") {
    return (
      <div ref={focusRef} tabIndex={-1} className="flex flex-col gap-4">
        <Banner
          tone={job.stage === "cancelled" ? "warning" : "error"}
          action={
            <Button variant="secondary" size="sm" onClick={retryAfterIngest}>
              Retry
            </Button>
          }
        >
          {job.stage === "cancelled"
            ? "Analysis was cancelled."
            : (job.error?.message ?? "The analysis failed.")}
        </Banner>
        {job.events.length > 0 && (
          <ul className="flex flex-col gap-1">
            {job.events.map((event, i) => (
              <li key={i}>
                <Text variant="caption">{event.message ?? `${event.node}: ${event.status}`}</Text>
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  }

  // --- Completed: the report lives in the shared query cache (useReport), not here ---
  if (report.isPending) {
    return <Loader label="Loading the finished report…" />;
  }
  if (report.isError || !report.data) {
    return (
      <div ref={focusRef} tabIndex={-1}>
        <Banner
          tone="error"
          action={
            <Button variant="secondary" size="sm" onClick={() => report.refetch()}>
              Retry
            </Button>
          }
        >
          Couldn&apos;t load the finished report.
        </Banner>
      </div>
    );
  }

  return (
    <div ref={focusRef} tabIndex={-1} className="flex flex-col gap-4">
      <AIResponseCard report={report.data} onRetry={retryAfterIngest} />
      <div className="flex flex-wrap gap-4">
        {/* Frozen entry point (05_Screen_Inventory.md SCR-06/SCR-08): "Company
            Research (SCR-06, 'Explain This')" into Learning, grounded in this
            report. Phase 8 scope: Learning itself is built; the backend
            capability it calls is a proposed contract, not live yet. */}
        <Link
          href={`/learning?ticker=${ticker}&job=${report.data.id}` as Route}
          className="self-start"
        >
          Explain a concept from this report
        </Link>
        {/* Frozen action (05_Screen_Inventory.md SCR-06 "Available Actions":
            "add to comparison") — reuses Comparison's own existing `?ids=`
            deep-link contract (`app/(workspace)/compare/page.tsx`) verbatim;
            no new comparison state or data model here. */}
        <Link href={`/compare?ids=${report.data.id}` as Route} className="self-start">
          Add to comparison
        </Link>
      </div>
    </div>
  );
}
