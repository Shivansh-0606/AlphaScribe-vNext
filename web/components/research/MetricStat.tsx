import { Text } from "@/components/foundation/Text";
import { cn } from "@/lib/utils";

/**
 * MetricStat (09 Component Inventory / 09_Research_Components.md — "Financial
 * Metric Card"): label · value (`type.figure`) · direction · meaning. First
 * real usage of the Research Components family (`components/research/`,
 * previously a README placeholder).
 *
 * `direction` is optional and only ever set from a real leading +/- sign
 * already present in the source value (see `FinancialsSection.tsx`) — never
 * inferred/guessed, so a metric with no reliable sign just omits the
 * indicator rather than showing a fabricated one. Direction is always paired
 * with the glyph + a screen-reader-only word, never color alone (Constitution §17).
 */
export interface MetricStatProps {
  label: string;
  value: string;
  direction?: "up" | "down";
  meaning?: string;
  className?: string;
}

export function MetricStat({ label, value, direction, meaning, className }: MetricStatProps) {
  return (
    <div data-slot="research-metric-stat" className={cn("flex flex-col gap-1", className)}>
      <Text variant="label">{label}</Text>
      <div className="flex items-baseline gap-1.5">
        <Text variant="figure" className="text-lg">
          {value}
        </Text>
        {direction && (
          <span
            className={cn(
              "text-sm font-medium",
              direction === "up" ? "text-bullish" : "text-bearish",
            )}
          >
            <span aria-hidden="true">{direction === "up" ? "▲" : "▼"}</span>
            <span className="sr-only">{direction === "up" ? " increase" : " decrease"}</span>
          </span>
        )}
      </div>
      {meaning && <Text variant="caption">{meaning}</Text>}
    </div>
  );
}
