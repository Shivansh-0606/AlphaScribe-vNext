import { Badge } from "@/components/foundation/Badge";

/**
 * Confidence Indicator (08_AI_Components.md) — the qualitative "honesty
 * instrument" (Law 8): confidence never exceeds evidence, and never as a
 * fabricated percentage. `confidenceLabel()` maps the backend's numeric
 * scorecard down to this vocabulary before it ever reaches this component —
 * this component only ever renders the label, never a raw score. Both live
 * here (shared `web/components/research/`, not a feature-internal module)
 * since every consumer of this component (`company-research`,
 * `research-library`) needs the identical mapping, not a per-feature copy.
 */
export type ConfidenceLabel = "Well-supported" | "Limited evidence" | "Not enough evidence";

export function confidenceLabel(overall: number): ConfidenceLabel {
  if (overall >= 0.8) return "Well-supported";
  if (overall >= 0.5) return "Limited evidence";
  return "Not enough evidence";
}

const VARIANT: Record<ConfidenceLabel, "verified" | "warning" | "bearish"> = {
  "Well-supported": "verified",
  "Limited evidence": "warning",
  "Not enough evidence": "bearish",
};

export function ConfidenceIndicator({ label }: { label: ConfidenceLabel }) {
  return <Badge variant={VARIANT[label]}>{label}</Badge>;
}
