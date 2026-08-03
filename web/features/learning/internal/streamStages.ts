import type { StreamEvent } from "../integration/schemas";

/**
 * Derives the frozen "AI Thinking → AI Streaming" lifecycle
 * (`06_UX_Specifications.md` SCR-08) from the proposed `{node, status}`
 * event shape (`integration/schemas.ts`) — same derivation pattern as
 * `company-research/internal/streamStages.ts`, independently declared per
 * 02.2 AD-3.
 */
export type StreamStage = "idle" | "thinking" | "streaming" | "completed" | "failed" | "cancelled";

const STAGE_LABEL: Record<StreamStage, string> = {
  idle: "",
  thinking: "Finding relevant filings…",
  streaming: "Writing the explanation…",
  completed: "Explanation ready.",
  failed: "The explanation failed.",
  cancelled: "Explanation cancelled.",
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
  if (event.node === "retriever") return "thinking";
  if (event.node === "explainer") return "streaming";
  if (event.node === "final") return "completed";
  return "thinking";
}
