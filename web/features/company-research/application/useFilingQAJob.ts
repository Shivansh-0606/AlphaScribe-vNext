import { useCallback, useEffect, useReducer, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { type AiAccessConfig, useAiAccessStore } from "@/lib/state/aiAccess";
import { AppError } from "@/lib/errors/app-error";
import * as companyResearchApi from "../integration/api";
import type { CreateFilingQARequestBody, FilingQAStreamEvent } from "../integration/schemas";
import { deriveFilingQAStage, type FilingQAStage } from "../internal/streamStages";
import { filingQAQueryKey } from "./useFilingQA";

/**
 * Owns the streaming lifecycle for one Filing Q&A run (M16) — same shape as
 * `useFilingAnalysisJob`, scoped to one `(ticker, docId)` filing. `start()`
 * takes exactly one argument, the question string — closer to
 * `useResearchJob.start(query)` than to `useFilingAnalysisJob.start()` (no
 * args, one fixed target) or `useChangeBriefJob.start(body)` (full request,
 * a mode + references to pick), since FQA has exactly one required,
 * user-authored input and nothing else to select.
 */

interface FilingQAJobState {
  jobId: string | null;
  stage: FilingQAStage;
  events: FilingQAStreamEvent[];
  error: AppError | null;
}

const initialState: FilingQAJobState = { jobId: null, stage: "idle", events: [], error: null };

type Action =
  | { type: "started"; jobId: string }
  | { type: "event"; event: FilingQAStreamEvent }
  | { type: "error"; error: AppError }
  | { type: "cancelled" };

function reducer(state: FilingQAJobState, action: Action): FilingQAJobState {
  switch (action.type) {
    case "started":
      return { jobId: action.jobId, stage: "answering", events: [], error: null };
    case "event": {
      const stage = deriveFilingQAStage(action.event);
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

function llmFields(config: AiAccessConfig): Partial<CreateFilingQARequestBody> {
  if (config.mode === "managed") return {};
  return {
    llm_provider: config.provider,
    llm_api_key: config.apiKey,
    llm_base_url: config.baseUrl || undefined,
    llm_model: config.model || undefined,
  };
}

export function useFilingQAJob(ticker: string, docId: string) {
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
      closeStreamRef.current = companyResearchApi.openFilingQAStream(ticker, docId, jobId, {
        onEvent: (event) => {
          if (event.node === "final" && event.answer) {
            queryClient.setQueryData(filingQAQueryKey(ticker, docId, jobId), event.answer);
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
    mutationFn: (question: string) =>
      companyResearchApi.createFilingQA(ticker, docId, { question, ...llmFields(aiAccess) }),
    onSuccess: ({ id }) => {
      dispatch({ type: "started", jobId: id });
      attachStream(id);
    },
  });

  const cancel = useCallback(() => {
    if (!state.jobId) return;
    closeStream();
    dispatch({ type: "cancelled" });
    void companyResearchApi.cancelFilingQA(ticker, docId, state.jobId);
  }, [state.jobId, closeStream, ticker, docId]);

  // Resubmits the same last question (mirrors `useChangeBriefJob.retry` —
  // `startMutation.variables` is TanStack's own record of the last `mutate`
  // call, so no separate ref is needed to remember it).
  const retry = useCallback(() => {
    if (startMutation.variables !== undefined) startMutation.mutate(startMutation.variables);
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
