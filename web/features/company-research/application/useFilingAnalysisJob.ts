import { useCallback, useEffect, useReducer, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { type AiAccessConfig, useAiAccessStore } from "@/lib/state/aiAccess";
import { AppError } from "@/lib/errors/app-error";
import * as companyResearchApi from "../integration/api";
import type {
  CreateFilingAnalysisRequestBody,
  FilingAnalysisStreamEvent,
} from "../integration/schemas";
import { deriveFilingAnalysisStage, type FilingAnalysisStage } from "../internal/streamStages";
import { filingAnalysisQueryKey } from "./useFilingAnalysis";

/**
 * Owns the AI streaming lifecycle for one Filing Analysis run (M14) — same
 * shape as `useResearchJob`/`useExplanationJob` (03.14 row 11), scoped to
 * one `(ticker, docId)` filing. No output-selection parameter to pass
 * (CQ-2): `start()` takes no argument, unlike the query/concept-driven jobs.
 */

interface FilingAnalysisJobState {
  jobId: string | null;
  stage: FilingAnalysisStage;
  events: FilingAnalysisStreamEvent[];
  error: AppError | null;
}

const initialState: FilingAnalysisJobState = {
  jobId: null,
  stage: "idle",
  events: [],
  error: null,
};

type Action =
  | { type: "started"; jobId: string }
  | { type: "event"; event: FilingAnalysisStreamEvent }
  | { type: "error"; error: AppError }
  | { type: "cancelled" };

function reducer(state: FilingAnalysisJobState, action: Action): FilingAnalysisJobState {
  switch (action.type) {
    case "started":
      return { jobId: action.jobId, stage: "analyzing", events: [], error: null };
    case "event": {
      const stage = deriveFilingAnalysisStage(action.event);
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

function llmFields(config: AiAccessConfig): CreateFilingAnalysisRequestBody {
  if (config.mode === "managed") return {};
  return {
    llm_provider: config.provider,
    llm_api_key: config.apiKey,
    llm_base_url: config.baseUrl || undefined,
    llm_model: config.model || undefined,
  };
}

export function useFilingAnalysisJob(ticker: string, docId: string) {
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
      closeStreamRef.current = companyResearchApi.openFilingAnalysisStream(ticker, docId, jobId, {
        onEvent: (event) => {
          if (event.node === "final" && event.analysis) {
            queryClient.setQueryData(filingAnalysisQueryKey(ticker, docId, jobId), event.analysis);
          }
          dispatch({ type: "event", event });
        },
        onEnd: closeStream,
        onError: (error) => dispatch({ type: "error", error }),
      });
    },
    [closeStream, docId, queryClient, ticker],
  );

  const startMutation = useMutation({
    mutationFn: () => companyResearchApi.createFilingAnalysis(ticker, docId, llmFields(aiAccess)),
    onSuccess: ({ id }) => {
      dispatch({ type: "started", jobId: id });
      attachStream(id);
    },
  });

  const cancel = useCallback(() => {
    if (!state.jobId) return;
    closeStream();
    dispatch({ type: "cancelled" });
    void companyResearchApi.cancelFilingAnalysis(ticker, docId, state.jobId);
  }, [state.jobId, closeStream, ticker, docId]);

  const retry = useCallback(() => {
    startMutation.mutate();
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
