import { useCallback, useEffect, useReducer, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { type AiAccessConfig, useAiAccessStore } from "@/lib/state/aiAccess";
import { AppError } from "@/lib/errors/app-error";
import * as companyResearchApi from "../integration/api";
import type { GenerateReportRequestBody, StreamEvent } from "../integration/schemas";
import { deriveStage, type StreamStage } from "../internal/streamStages";
import { reportQueryKey } from "./useReport";

/**
 * Owns the AI streaming lifecycle for one research run (03.14 row 11 —
 * "streamed server state (Application) + integration boundary; UI renders").
 * Report *content* is not held here — it's seeded into the `useReport`
 * query cache as soon as it's known, so this hook only tracks `jobId`,
 * lifecycle `stage`, the raw trace `events` (the pipeline log), and any
 * transport-level error. Each caller (Overview, `CopilotPanel`) owns its own
 * instance/run, so this is hook-local `useReducer` state, not a Zustand
 * store (03.14 placement guide).
 */

interface ResearchJobState {
  jobId: string | null;
  stage: StreamStage;
  events: StreamEvent[];
  error: AppError | null;
}

const initialState: ResearchJobState = { jobId: null, stage: "idle", events: [], error: null };

type Action =
  | { type: "started"; jobId: string }
  | { type: "event"; event: StreamEvent }
  | { type: "error"; error: AppError }
  | { type: "cancelled" };

function reducer(state: ResearchJobState, action: Action): ResearchJobState {
  switch (action.type) {
    case "started":
      return { jobId: action.jobId, stage: "thinking", events: [], error: null };
    case "event": {
      const stage = deriveStage(action.event);
      // Surface the pipeline's own (already-redacted, server.py:790-795)
      // error/cancel message instead of a generic fallback — it's real
      // information, not a raw exception.
      const error =
        (stage === "failed" || stage === "cancelled") && action.event.message
          ? new AppError("unknown", action.event.message)
          : state.error;
      return { ...state, stage, events: [...state.events, action.event], error };
    }
    case "error":
      // Retain jobId/events (Law 6 — never lose produced work); only the
      // terminal stage and error change.
      return { ...state, stage: "failed", error: action.error };
    case "cancelled":
      // Optimistic — the user's intent is unambiguous the moment they click
      // Stop. We also just closed our own stream (cancel() below), so
      // there's no other way this hook would ever learn the run stopped;
      // waiting on the fire-and-forget cancel request would leave the UI
      // stuck showing "Stop generating" with no feedback (never trap the user).
      return { ...state, stage: "cancelled" };
    default:
      return state;
  }
}

function llmFields(config: AiAccessConfig): Partial<GenerateReportRequestBody> {
  if (config.mode === "managed") return {};
  return {
    llm_provider: config.provider,
    llm_api_key: config.apiKey,
    llm_base_url: config.baseUrl || undefined,
    llm_model: config.model || undefined,
  };
}

/**
 * @param contextReportId — when set, every `start()`/`retry()` call in this
 * instance is a follow-up building on that prior report (`CopilotPanel`,
 * Phase 4C), not a fresh Overview run.
 */
export function useResearchJob(ticker: string, contextReportId?: string) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const closeStreamRef = useRef<(() => void) | null>(null);
  const queryClient = useQueryClient();
  const aiAccess = useAiAccessStore();

  const closeStream = useCallback(() => {
    closeStreamRef.current?.();
    closeStreamRef.current = null;
  }, []);

  // Without this, switching away mid-run (e.g. to another SectionNav tab)
  // unmounts this hook but leaves the EventSource open indefinitely — the
  // stream has no other owner to close it.
  useEffect(() => closeStream, [closeStream]);

  const attachStream = useCallback(
    (jobId: string) => {
      closeStream();
      closeStreamRef.current = companyResearchApi.openReportStream(jobId, {
        onEvent: (event) => {
          // Seed the report cache before signaling "completed" so a
          // consumer reading both never observes the stage flip first.
          if (event.node === "final" && event.report) {
            queryClient.setQueryData(reportQueryKey(jobId), event.report);
          }
          dispatch({ type: "event", event });
        },
        onEnd: closeStream,
        onError: (error) => dispatch({ type: "error", error }),
      });
    },
    [closeStream, queryClient],
  );

  const startMutation = useMutation({
    mutationFn: (query: string) =>
      companyResearchApi.generateReport({
        ticker,
        query,
        context_report_id: contextReportId,
        ...llmFields(aiAccess),
      }),
    onSuccess: ({ job_id, cached }) => {
      dispatch({ type: "started", jobId: job_id });
      if (cached) {
        // Cached hit: no SSE stream will ever emit for this job_id
        // (server.py:881-907) — the report is already in `db.reports`.
        companyResearchApi
          .fetchReport(job_id)
          .then((res) => {
            if (res.report) queryClient.setQueryData(reportQueryKey(job_id), res.report);
            dispatch({ type: "event", event: { node: "final", status: "ok" } });
          })
          .catch((error: AppError) => dispatch({ type: "error", error }));
        return;
      }
      attachStream(job_id);
    },
  });

  /** Resumes an in-progress or already-finished job from a `?job=` deep link (Law 6). */
  const resume = useCallback(
    (jobId: string) => {
      dispatch({ type: "started", jobId });
      companyResearchApi
        .fetchReport(jobId)
        .then((res) => {
          if (res.status === "completed" && res.report) {
            queryClient.setQueryData(reportQueryKey(jobId), res.report);
            dispatch({ type: "event", event: { node: "final", status: "ok" } });
            return;
          }
          // Still running (or the process restarted but the job persisted) —
          // reopen the stream; the backend replays full event history.
          attachStream(jobId);
        })
        .catch((error: AppError) => dispatch({ type: "error", error }));
    },
    [attachStream, queryClient],
  );

  const cancel = useCallback(() => {
    if (!state.jobId) return;
    closeStream();
    dispatch({ type: "cancelled" });
    void companyResearchApi.cancelReport(state.jobId);
  }, [state.jobId, closeStream]);

  const retry = useCallback(
    (query: string) => {
      startMutation.mutate(query);
    },
    [startMutation],
  );

  return {
    ...state,
    start: startMutation.mutate,
    resume,
    retry,
    cancel,
    isStarting: startMutation.isPending,
    startError: startMutation.error as AppError | null,
  };
}
