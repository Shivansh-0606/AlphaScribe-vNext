import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";
import { Badge as BadgePrimitive } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

/**
 * Badge (Family 05) — docs/experience_design/Components/05_Content_Data_Display.md.
 * Meaning-bearing status/category token — text always carries the meaning,
 * never color alone (§17), so `children` (the label) is required.
 *
 * Wraps the generated `components/ui/badge.tsx` but replaces its variant
 * vocabulary entirely — every variant below sets its own explicit `bg-*`
 * class to cancel the primitive's default fill (the same leak documented in
 * Button.tsx).
 */
const badgeVariants = cva(
  "inline-flex w-fit shrink-0 items-center gap-1 rounded-sm px-1.5 py-0.5 font-sans text-xs font-medium whitespace-nowrap",
  {
    variants: {
      variant: {
        neutral: "bg-muted text-muted-foreground",
        bullish: "bg-bullish/15 text-bullish",
        bearish: "bg-bearish/15 text-bearish",
        warning: "bg-warning/15 text-warning",
        verified: "bg-accent text-accent-foreground",
        count: "rounded-pill bg-primary text-primary-foreground justify-center px-1.5",
      },
    },
    defaultVariants: {
      variant: "neutral",
    },
  },
);

export interface BadgeProps
  extends Omit<ComponentProps<"span">, "children">, VariantProps<typeof badgeVariants> {
  children: React.ReactNode;
}

export function Badge({ variant = "neutral", className, children, ...props }: BadgeProps) {
  return (
    <BadgePrimitive
      data-slot="foundation-badge"
      className={cn(badgeVariants({ variant }), className)}
      {...props}
    >
      {children}
    </BadgePrimitive>
  );
}
