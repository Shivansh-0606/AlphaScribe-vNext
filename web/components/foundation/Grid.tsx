import type { ComponentProps, CSSProperties } from "react";
import { cn } from "@/lib/utils";
import { GAP_CLASS, type SpaceStep } from "./Flex";

/**
 * Grid — CSS grid over the frozen 12/8/4 column system
 * (docs/experience_design/05_Grid_System.md). `cols` accepts a single number
 * or a per-breakpoint object matching the doc's mobile/tablet/desktop bands;
 * expressed via inline custom properties + Tailwind's arbitrary-value
 * `grid-cols-[var(--x)]` syntax (same pattern tokens.css documents for
 * z-index) rather than template-interpolated class names, which Tailwind's
 * static scanner can't see.
 */
export interface GridProps extends ComponentProps<"div"> {
  cols?: number | { base?: number; md?: number; lg?: number };
  gap?: SpaceStep;
}

export function Grid({ cols = 12, gap = 4, className, style, ...props }: GridProps) {
  const responsive = typeof cols === "object";
  const vars: CSSProperties = responsive
    ? ({
        "--grid-cols-base": String(cols.base ?? 4),
        "--grid-cols-md": String(cols.md ?? cols.base ?? 8),
        "--grid-cols-lg": String(cols.lg ?? cols.md ?? cols.base ?? 12),
      } as CSSProperties)
    : ({ "--grid-cols-base": String(cols) } as CSSProperties);

  return (
    <div
      data-slot="foundation-grid"
      style={{ ...vars, ...style }}
      className={cn(
        "grid grid-cols-[repeat(var(--grid-cols-base),minmax(0,1fr))]",
        responsive && "md:grid-cols-[repeat(var(--grid-cols-md),minmax(0,1fr))]",
        responsive && "lg:grid-cols-[repeat(var(--grid-cols-lg),minmax(0,1fr))]",
        GAP_CLASS[gap],
        className,
      )}
      {...props}
    />
  );
}
