import { useCallback, useEffect, useReducer, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { type AiAccessConfig, useAiAccessStore } from "@/lib/state/aiAccess";
import { AppError } from "@/lib/errors/app-error";
import * as learningApi from "../integration/api";
import type { ExplainRequestBody, StreamEvent } from "../integration/schemas";
import { deriveStage, type StreamStage } from "../internal/streamStages";
import { explanationQueryKey } from "./useExplanation";

/**
 * Owns the AI streaming lifecycle for one explanation run — mirrors
 * `company-research/application/useResearchJob.ts` exactly in shape
 * (independently implemented, per 02.2 AD-3), since Learning proposes the
 * identical start → SSE stream → fetch-final-doc contract.
 */

interface ExplanationJobState {
  jobId: string | null;
  stage: StreamStage;
  events: StreamEvent[];
  error: AppError | null;
}

const initialState: ExplanationJobState = { jobId: null, stage: "idle", events: [], error: null };

type Action =
  | { type: "started"; jobId: string }
  | { type: "event"; event: StreamEvent }
  | { type: "error"; error: AppError }
  | { type: "cancelled" };

function reducer(state: ExplanationJobState, action: Action): ExplanationJobState {
  switch (action.type) {
    case "started":
      return { jobId: action.jobId, stage: "thinking", events: [], error: null };
    case "event": {
      const stage = deriveStage(action.event);
      const error =
        (stage === "failed" || stage === "cancelled") && action.event.message
          ? new AppError("unknown", action.event.message)
          : state.error;
      return { ...state, stage, events: [...state.events, action.event], error };
    }
    case "error":
      return { ...state, stage: "failed", error: action.error };
    case "cancelled":
      return { ...state, stage: "cancelled" };
    default:
      return state;
  }
}

function llmFields(config: AiAccessConfig): Partial<ExplainRequestBody> {
  if (config.mode === "managed") return {};
  return {
    llm_provider: config.provider,
    llm_api_key: config.apiKey,
    llm_base_url: config.baseUrl || undefined,
    llm_model: config.model || undefined,
  };
}

export function useExplanationJob(ticker: string, contextReportId?: string) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const closeStreamRef = useRef<(() => void) | null>(null);
  const queryClient = useQueryClient();
  const aiAccess = useAiAccessStore();

  const closeStream = useCallback(() => {
    closeStreamRef.current?.();
    closeStreamRef.current = null;
  }, []);

  useEffect(() => closeStream, [closeStream]);

  const attachStream = useCallback(
    (jobId: string) => {
      closeStream();
      closeStreamRef.current = learningApi.openExplanationStream(jobId, {
        onEvent: (event) => {
          if (event.node === "final" && event.explanation) {
            queryClient.setQueryData(explanationQueryKey(jobId), event.explanation);
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
    mutationFn: (concept: string) =>
      learningApi.requestExplanation({
        ticker,
        concept,
        context_report_id: contextReportId,
        ...llmFields(aiAccess),
      }),
    onSuccess: ({ id }) => {
      dispatch({ type: "started", jobId: id });
      attachStream(id);
    },
  });

  const cancel = useCallback(() => {
    if (!state.jobId) return;
    closeStream();
    dispatch({ type: "cancelled" });
    void learningApi.cancelExplanation(state.jobId);
  }, [state.jobId, closeStream]);

  const retry = useCallback(
    (concept: string) => {
      startMutation.mutate(concept);
    },
    [startMutation],
  );

  return {
    ...state,
    start: startMutation.mutate,
    retry,
    cancel,
    isStarting: startMutation.isPending,
    startError: startMutation.error as AppError | null,
  };
}
