import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "radix-ui";
import type { ComponentProps } from "react";
import {
  Card as CardPrimitive,
  CardAction,
  CardContent as CardContentPrimitive,
  CardDescription,
  CardFooter as CardFooterPrimitive,
  CardHeader as CardHeaderPrimitive,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

/**
 * Card (Family 05) — docs/experience_design/Components/05_Content_Data_Display.md.
 * Direction C: flat on the canvas at rest, elevation appears only on
 * interaction — the generated primitive's own `rounded-xl`/`shadow-sm`/`py-6`
 * are cancelled below (`rounded-md`/`shadow-none`/`py-4`, the frozen radius +
 * comfortable padding) the same way Button.tsx cancels shadcn's default fill.
 *
 * `interactive`/`selectable` don't grant focusability themselves — compose
 * with `asChild` (Radix Slot) to make the actual anchor/RadioGroupItem/etc.
 * the DOM node, so there's exactly one focusable control per card (§Accessibility).
 */
const cardVariants = cva("rounded-md bg-surface py-4 text-foreground shadow-none", {
  variants: {
    variant: {
      static: "",
      interactive:
        "cursor-pointer transition-[box-shadow,transform] duration-[var(--motion-duration-base)] ease-motion-out outline-none hover:-translate-y-px hover:shadow-sm focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
      selectable:
        "cursor-pointer transition-[box-shadow,border-color] duration-[var(--motion-duration-base)] ease-motion-out outline-none hover:shadow-sm focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 data-[selected=true]:border-primary data-[selected=true]:ring-1 data-[selected=true]:ring-primary",
    },
  },
  defaultVariants: {
    variant: "static",
  },
});

export interface CardProps extends ComponentProps<"div">, VariantProps<typeof cardVariants> {
  /** `selectable` variant only — the non-color selected cue (border + ring). */
  selected?: boolean;
  /** Compose the actual focusable element (a Link, a RadioGroupItem, …) as the card root. */
  asChild?: boolean;
}

export function Card({
  variant = "static",
  selected,
  asChild = false,
  className,
  ...props
}: CardProps) {
  const Comp = asChild ? Slot.Root : CardPrimitive;
  return (
    <Comp
      data-slot="foundation-card"
      data-selected={variant === "selectable" ? selected : undefined}
      className={cn(cardVariants({ variant }), className)}
      {...props}
    />
  );
}

// Header/Content/Footer default to `--space-4` (comfortable) padding instead
// of the generated primitive's `px-6` — pass `className="px-3"` for dense grids.
export function CardHeader({ className, ...props }: ComponentProps<"div">) {
  return <CardHeaderPrimitive className={cn("px-4", className)} {...props} />;
}

export function CardContent({ className, ...props }: ComponentProps<"div">) {
  return <CardContentPrimitive className={cn("px-4", className)} {...props} />;
}

export function CardFooter({ className, ...props }: ComponentProps<"div">) {
  return <CardFooterPrimitive className={cn("px-4", className)} {...props} />;
}

export { CardAction, CardDescription, CardTitle };
