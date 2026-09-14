import { useCallback, useEffect, useReducer, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { type AiAccessConfig, useAiAccessStore } from "@/lib/state/aiAccess";
import { AppError } from "@/lib/errors/app-error";
import * as companyResearchApi from "../integration/api";
import type { ChangeBriefStreamEvent, CreateChangeBriefRequestBody } from "../integration/schemas";
import { deriveChangeBriefStage, type ChangeBriefStage } from "../internal/streamStages";
import { changeBriefQueryKey } from "./useChangeBrief";

/**
 * Owns the streaming lifecycle for one Change Brief run (M15) — same shape
 * as `useFilingAnalysisJob` (03.14 row 11), scoped to one `ticker`. Unlike
 * Filing Analysis, `start()` takes the full mode-specific request body (the
 * comparison references), since there's no single fixed target — mirrors
 * `useResearchJob.start(query)` in that respect.
 */

interface ChangeBriefJobState {
  jobId: string | null;
  stage: ChangeBriefStage;
  events: ChangeBriefStreamEvent[];
  error: AppError | null;
}

const initialState: ChangeBriefJobState = { jobId: null, stage: "idle", events: [], error: null };

type Action =
  | { type: "started"; jobId: string }
  | { type: "event"; event: ChangeBriefStreamEvent }
  | { type: "error"; error: AppError }
  | { type: "cancelled" };

function reducer(state: ChangeBriefJobState, action: Action): ChangeBriefJobState {
  switch (action.type) {
    case "started":
      return { jobId: action.jobId, stage: "computing", events: [], error: null };
    case "event": {
      const stage = deriveChangeBriefStage(action.event);
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

function llmFields(config: AiAccessConfig): Partial<CreateChangeBriefRequestBody> {
  if (config.mode === "managed") return {};
  return {
    llm_provider: config.provider,
    llm_api_key: config.apiKey,
    llm_base_url: config.baseUrl || undefined,
    llm_model: config.model || undefined,
  };
}

export function useChangeBriefJob(ticker: string) {
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
      closeStreamRef.current = companyResearchApi.openChangeBriefStream(ticker, jobId, {
        onEvent: (event) => {
          if (event.node === "final" && event.changes) {
            queryClient.setQueryData(changeBriefQueryKey(ticker, jobId), event.changes);
          }
          dispatch({ type: "event", event });
        },
        onEnd: closeStream,
        onError: (error) => dispatch({ type: "error", error }),
      });
    },
    [closeStream, queryClient, ticker],
  );

  const startMutation = useMutation({
    mutationFn: (
      request: Omit<
        CreateChangeBriefRequestBody,
        "llm_provider" | "llm_api_key" | "llm_base_url" | "llm_model"
      >,
    ) => companyResearchApi.createChangeBrief(ticker, { ...request, ...llmFields(aiAccess) }),
    onSuccess: ({ id }) => {
      dispatch({ type: "started", jobId: id });
      attachStream(id);
    },
  });

  const cancel = useCallback(() => {
    if (!state.jobId) return;
    closeStream();
    dispatch({ type: "cancelled" });
    void companyResearchApi.cancelChangeBrief(ticker, state.jobId);
  }, [state.jobId, closeStream, ticker]);

  // Resubmits the exact same request (mirrors `useResearchJob.retry` —
  // failed/cancelled states offer Retry, never an edit-and-resubmit flow).
  // `startMutation.variables` is TanStack's own record of the last `mutate`
  // call, so no separate ref is needed to remember it.
  const retry = useCallback(() => {
    if (startMutation.variables) startMutation.mutate(startMutation.variables);
  }, [startMutation]);

  return {
    ...state,
    start: startMutation.mutate,
    retry,
    cancel,
    isStarting: startMutation.isPending,
    startError: startMutation.error as AppError | null,
  };
}
