import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps, ElementType } from "react";
import { cn } from "@/lib/utils";

/**
 * Heading — realizes the frozen semantic type roles `type.h1`/`h2`/`h3`
 * (docs/experience_design/03_Typography_System.md §Semantic Type Roles).
 * Not a numbered Component Family — Typography is a token/foundation
 * concern, not an interactive control — but is a first-class reusable
 * primitive per the M2 brief.
 *
 * `level` sets the visual role (size/weight/leading); `as` sets the actual
 * HTML element when it must differ from the visual level (e.g. a visually
 * h2-sized heading that is semantically h1 on a given screen) — sequential
 * heading order (h1→h2→h3, no skips) is the caller's responsibility per
 * Typography System §Best Practices.
 */
const headingVariants = cva("font-sans text-foreground", {
  variants: {
    level: {
      h1: "text-3xl leading-snug font-semibold tracking-tight",
      h2: "text-2xl leading-snug font-semibold tracking-tight",
      h3: "text-xl leading-snug font-semibold",
    },
  },
  defaultVariants: {
    level: "h1",
  },
});

export interface HeadingProps
  extends Omit<ComponentProps<"h1">, "children">, VariantProps<typeof headingVariants> {
  children: React.ReactNode;
  as?: ElementType;
}

export function Heading({ level = "h1", as, className, children, ...props }: HeadingProps) {
  const Comp = as ?? level ?? "h1";
  return (
    <Comp className={cn(headingVariants({ level }), className)} {...props}>
      {children}
    </Comp>
  );
}
