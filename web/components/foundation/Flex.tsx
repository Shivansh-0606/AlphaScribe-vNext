import type { ComponentProps, ElementType } from "react";
import { cn } from "@/lib/utils";

/**
 * Generic layout primitives (M2 Phase 3) — engineering conveniences over the
 * frozen `--space-N` scale (docs/experience_design/04_Spacing_System.md),
 * not a numbered design Family. Tailwind's own scale already contains every
 * `--space-N` px value verbatim (no separate CSS custom properties exist for
 * it — see 04_Spacing_System's rationale, same reasoning as the grid
 * breakpoints in styles/tokens.css), so this map is the single place that
 * translates a spacing *step* to the Tailwind *gap* utility that realizes
 * it; `Grid`/`Stack` import it rather than re-deriving it.
 */
export const GAP_CLASS = {
  0: "gap-0",
  1: "gap-1", // 4px
  2: "gap-2", // 8px
  3: "gap-3", // 12px
  4: "gap-4", // 16px — default component gap
  5: "gap-6", // 24px — group separation
  6: "gap-8", // 32px — section spacing
  7: "gap-10", // 40px
  8: "gap-12", // 48px
  9: "gap-16", // 64px
  10: "gap-24", // 96px
} as const;

export type SpaceStep = keyof typeof GAP_CLASS;

export interface FlexProps extends ComponentProps<"div"> {
  direction?: "row" | "col" | "row-reverse" | "col-reverse";
  gap?: SpaceStep;
  align?: "start" | "center" | "end" | "stretch" | "baseline";
  justify?: "start" | "center" | "end" | "between" | "around" | "evenly";
  wrap?: boolean;
  as?: ElementType;
}

const DIRECTION_CLASS: Record<NonNullable<FlexProps["direction"]>, string> = {
  row: "flex-row",
  col: "flex-col",
  "row-reverse": "flex-row-reverse",
  "col-reverse": "flex-col-reverse",
};

const ALIGN_CLASS: Record<NonNullable<FlexProps["align"]>, string> = {
  start: "items-start",
  center: "items-center",
  end: "items-end",
  stretch: "items-stretch",
  baseline: "items-baseline",
};

const JUSTIFY_CLASS: Record<NonNullable<FlexProps["justify"]>, string> = {
  start: "justify-start",
  center: "justify-center",
  end: "justify-end",
  between: "justify-between",
  around: "justify-around",
  evenly: "justify-evenly",
};

export function Flex({
  direction = "row",
  gap = 0,
  align,
  justify,
  wrap = false,
  as: Comp = "div",
  className,
  ...props
}: FlexProps) {
  return (
    <Comp
      data-slot="foundation-flex"
      className={cn(
        "flex",
        DIRECTION_CLASS[direction],
        GAP_CLASS[gap],
        align && ALIGN_CLASS[align],
        justify && JUSTIFY_CLASS[justify],
        wrap && "flex-wrap",
        className,
      )}
      {...props}
    />
  );
}
