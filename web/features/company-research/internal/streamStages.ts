import type { StreamEvent } from "../integration/schemas";

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
