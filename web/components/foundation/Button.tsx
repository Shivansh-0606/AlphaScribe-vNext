import { CircleNotch } from "@phosphor-icons/react/dist/ssr";
import { cva, type VariantProps } from "class-variance-authority";
import { Slot } from "radix-ui";
import type { ComponentProps } from "react";
import { Button as ButtonPrimitive } from "@/components/ui/button";
import { cn } from "@/lib/utils";

/**
 * Button (Family 01) — docs/experience_design/Components/01_Buttons.md.
 *
 * Exactly the four frozen variants (no more): Primary, Secondary, Quiet,
 * Destructive. `hero` swaps Primary's fill to the brand gradient for the
 * single most important action in a context — never a fifth variant, and
 * never combined with a non-primary variant (enforced by the type).
 *
 * Wraps the generated `components/ui/button.tsx` (Radix Slot/asChild +
 * native <button> semantics) but does NOT use its variant/size vocabulary —
 * this component's own cva below is the only source of visual variants, per
 * the frozen spec.
 */
const buttonVariants = cva(
  // Focus ring is NOT set here — the global `:focus-visible` rule
  // (app/globals.css) already applies the frozen ring to every interactive
  // element identically; a per-component ring would duplicate/diverge from it.
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-md font-medium whitespace-nowrap outline-none transition-[background-color,border-color,color,opacity] duration-[var(--motion-duration-fast)] ease-standard disabled:pointer-events-none disabled:opacity-disabled",
  {
    variants: {
      variant: {
        primary: "bg-primary text-primary-foreground hover:bg-primary/90",
        secondary:
          "border border-border bg-secondary text-secondary-foreground hover:bg-surface-hover",
        // bg-transparent is required, not decorative: the underlying
        // ButtonPrimitive (components/ui/button.tsx) always applies its own
        // default variant (bg-primary) internally; every other variant here
        // happens to cancel it via its own explicit bg-* class, but "quiet"
        // has no fill by design — without this, shadcn's bg-primary leaks
        // through untouched (confirmed via computed-style browser check).
        quiet: "bg-transparent text-foreground hover:bg-surface-hover",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
      },
      size: {
        sm: "h-7 px-2 text-sm",
        md: "h-9 px-3 text-sm",
        lg: "h-11 px-4 text-base",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

export interface ButtonProps
  extends Omit<ComponentProps<"button">, "children">, VariantProps<typeof buttonVariants> {
  children: React.ReactNode;
  /** Swaps Primary's fill to the brand gradient — the ONE hero action in a context (§7.1). No-op on other variants. */
  hero?: boolean;
  /** Keeps the button's width, sets aria-busy, replaces the leading position with a spinner. */
  loading?: boolean;
  asChild?: boolean;
}

export function Button({
  variant = "primary",
  size = "md",
  hero = false,
  loading = false,
  disabled,
  className,
  children,
  asChild = false,
  ...props
}: ButtonProps) {
  const Comp = asChild ? Slot.Root : ButtonPrimitive;

  return (
    <Comp
      data-slot="foundation-button"
      aria-busy={loading || undefined}
      aria-disabled={disabled || loading || undefined}
      disabled={disabled || loading}
      className={cn(
        buttonVariants({ variant, size }),
        hero &&
          variant === "primary" &&
          "text-primary-foreground bg-[linear-gradient(135deg,hsl(var(--brand-from)),hsl(var(--brand-to)))] hover:opacity-90",
        className,
      )}
      {...props}
    >
      {loading && (
        <CircleNotch className="size-4 shrink-0 animate-spin" weight="bold" aria-hidden="true" />
      )}
      {children}
    </Comp>
  );
}
