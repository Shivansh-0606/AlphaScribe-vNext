import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps, ElementType } from "react";
import { cn } from "@/lib/utils";

/**
 * Text — realizes the remaining frozen semantic type roles: `type.body`,
 * `type.body-strong`, `type.small`, `type.caption`, `type.label` (the
 * uppercase mono micro-label), `type.figure` (tabular mono for financial
 * values), `type.code` (03_Typography_System.md §Semantic Type Roles).
 *
 * `variant="label"` is the typographic micro-label treatment, distinct from
 * the FORM `Label` primitive (an accessible <label> element, Phase 2) — the
 * two share a name in casual language but are different concerns.
 */
const textVariants = cva("text-foreground", {
  variants: {
    variant: {
      body: "font-sans text-base leading-normal font-normal",
      "body-strong": "font-sans text-base leading-normal font-semibold",
      small: "font-sans text-sm leading-normal font-normal",
      caption: "font-sans text-xs leading-normal font-normal text-muted-foreground",
      label:
        "font-mono text-2xs leading-snug font-medium tracking-label text-muted-foreground uppercase",
      figure: "font-mono font-medium tabular-nums",
      code: "font-mono text-sm bg-code-bg rounded-sm px-1 py-0.5",
    },
  },
  defaultVariants: {
    variant: "body",
  },
});

export interface TextProps
  extends Omit<ComponentProps<"p">, "children">, VariantProps<typeof textVariants> {
  children: React.ReactNode;
  as?: ElementType;
}

const DEFAULT_ELEMENT: Record<NonNullable<TextProps["variant"]>, ElementType> = {
  body: "p",
  "body-strong": "p",
  small: "p",
  caption: "p",
  label: "span",
  figure: "span",
  code: "code",
};

export function Text({ variant = "body", as, className, children, ...props }: TextProps) {
  const Comp = as ?? DEFAULT_ELEMENT[variant ?? "body"];
  return (
    <Comp className={cn(textVariants({ variant }), className)} {...props}>
      {children}
    </Comp>
  );
}
