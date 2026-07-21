"use client";

import { Progress as ProgressPrimitive } from "radix-ui";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * Progress (Family 07) — docs/experience_design/Components/07_Feedback_Status.md.
 * Composes the raw `radix-ui` Progress primitive directly rather than the
 * generated `components/ui/progress.tsx` — that generated file bakes the
 * determinate `translateX` math and a hardcoded `bg-primary` fill directly
 * into its own JSX with no way to opt into an indeterminate sweep or a
 * `tone`-selected fill, the same reason `Checkbox.tsx` bypasses its generated
 * primitive.
 *
 * `value` omitted → indeterminate (unknown duration): a fixed-width segment
 * sweeps continuously rather than sitting frozen. `label` is mandatory — a
 * progress bar is never the only signal for a wait (spec's a11y rule) and
 * needs an accessible name either way (Radix sets `aria-valuenow` for
 * determinate; indeterminate has none, so `label` carries the busy meaning).
 */
export interface ProgressProps extends Omit<
  ComponentProps<typeof ProgressPrimitive.Root>,
  "value" | "children"
> {
  /** Omit for indeterminate (unknown duration); 0–100 for determinate. */
  value?: number;
  /** Mandatory accessible name — also the visible context a caller should pair nearby (spec: never bare). */
  label: string;
  /** `brand` is the sanctioned signal gradient for AI/primary flows; `neutral` otherwise. */
  tone?: "neutral" | "brand";
}

const TONE_FILL_CLASSNAME = {
  neutral: "bg-muted-foreground",
  brand: "bg-[linear-gradient(90deg,hsl(var(--brand-from)),hsl(var(--brand-to)))]",
} as const;

export function Progress({ value, label, tone = "neutral", className, ...props }: ProgressProps) {
  const indeterminate = value === undefined;

  return (
    <ProgressPrimitive.Root
      data-slot="foundation-progress"
      value={indeterminate ? null : value}
      aria-label={label}
      className={cn("rounded-pill bg-muted relative h-2 w-full overflow-hidden", className)}
      {...props}
    >
      <ProgressPrimitive.Indicator
        data-slot="foundation-progress-indicator"
        className={cn(
          "rounded-pill h-full",
          TONE_FILL_CLASSNAME[tone],
          indeterminate
            ? "w-1/3 animate-[progress-indeterminate_1.5s_ease-in-out_infinite]"
            : "ease-standard transition-[width] duration-[var(--motion-duration-base)]",
        )}
        style={indeterminate ? undefined : { width: `${value}%` }}
      />
    </ProgressPrimitive.Root>
  );
}
