import type {
  ChangeBriefStreamEvent,
  FilingAnalysisStreamEvent,
  StreamEvent,
} from "../integration/schemas";

/**
 * Derives the canonical AI-surface lifecycle stage (03.15 AD — Thinking →
 * Streaming → Grounded → Completed, branching to Failed/Cancelled) from the
 * raw `{node, status}` primitives the backend actually emits. The backend
 * has no stage taxonomy of its own (confirmed against `agents/nodes.py` /
 * `server.py`) — this mapping is entirely a frontend concern (03.13 AD-2).
 */
export type StreamStage =
  "idle" | "thinking" | "streaming" | "grounded" | "completed" | "failed" | "cancelled";

const STAGE_LABEL: Record<StreamStage, string> = {
  idle: "",
  thinking: "Gathering filings and preparing to analyze…",
  streaming: "Drafting the research brief…",
  grounded: "Verifying claims against the source filings…",
  completed: "Analysis complete.",
  failed: "The analysis failed.",
  cancelled: "Analysis cancelled.",
};

export function stageLabel(stage: StreamStage): string {
  return STAGE_LABEL[stage];
}

export function deriveStage(event: StreamEvent): StreamStage {
  if (event.node === "pipeline") {
    if (event.status === "start") return "thinking";
    if (event.status === "ok") return "completed";
    if (event.status === "warn") return "cancelled";
    if (event.status === "error") return "failed";
  }
  if (event.node === "retriever" || event.node === "extractor" || event.node === "tone") {
    return "thinking";
  }
  if (event.node === "synthesizer") return "streaming";
  if (event.node === "fact_checker") return "grounded";
  // The final report snapshot (server.py:988-994) arrives right after the
  // "pipeline"/"ok" event that already set "completed" — must not regress.
  if (event.node === "final") return "completed";
  return "thinking";
}

/**
 * Filing Analysis (M14) has no synthesizer/fact_checker split — one atomic
 * "analyzing" phase (per-output progress arrives as `node: "analyzing"`
 * trace events, surfaced via `message`, not a distinct stage) between
 * `pipeline/start` and the terminal `pipeline/ok` + injected `final` event
 * (`_filing_analysis_stream_events`, server.py). "cancelled" is never
 * derived from a stream event here — same as `useResearchJob`/
 * `useExplanationJob`, cancellation is the caller's own optimistic local
 * action the moment the Stop control is clicked.
 */
export type FilingAnalysisStage = "idle" | "analyzing" | "completed" | "failed" | "cancelled";

const FILING_ANALYSIS_STAGE_LABEL: Record<FilingAnalysisStage, string> = {
  idle: "",
  analyzing: "Analyzing the filing…",
  completed: "Analysis complete.",
  failed: "The analysis failed.",
  cancelled: "Analysis cancelled.",
};

export function filingAnalysisStageLabel(stage: FilingAnalysisStage): string {
  return FILING_ANALYSIS_STAGE_LABEL[stage];
}

export function deriveFilingAnalysisStage(event: FilingAnalysisStreamEvent): FilingAnalysisStage {
  if (event.node === "pipeline") {
    if (event.status === "ok") return "completed";
    if (event.status === "error") return "failed";
    if (event.status === "warn") return "cancelled";
    return "analyzing";
  }
  if (event.node === "final") return "completed";
  return "analyzing";
}

/**
 * Change Brief (M15) has the same single-phase shape as Filing Analysis —
 * `pipeline/start` -> terminal `pipeline/ok` + injected `final` event
 * (`_change_brief_stream_events`, server.py), for both the `period` mode
 * (no LLM at all) and the `report` mode (one bounded call). "cancelled" is
 * never derived from a stream event here for the same reason as the other
 * job hooks — cancellation is the caller's own optimistic local action.
 */
export type ChangeBriefStage = "idle" | "computing" | "completed" | "failed" | "cancelled";

const CHANGE_BRIEF_STAGE_LABEL: Record<ChangeBriefStage, string> = {
  idle: "",
  computing: "Computing the change brief…",
  completed: "Change brief complete.",
  failed: "The change brief failed.",
  cancelled: "Change brief cancelled.",
};

export function changeBriefStageLabel(stage: ChangeBriefStage): string {
  return CHANGE_BRIEF_STAGE_LABEL[stage];
}

export function deriveChangeBriefStage(event: ChangeBriefStreamEvent): ChangeBriefStage {
  if (event.node === "pipeline") {
    if (event.status === "ok") return "completed";
    if (event.status === "error") return "failed";
    if (event.status === "warn") return "cancelled";
    return "computing";
  }
  if (event.node === "final") return "completed";
  return "computing";
}
