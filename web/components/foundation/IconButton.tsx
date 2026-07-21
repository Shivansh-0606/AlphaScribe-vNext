import { CircleNotch } from "@phosphor-icons/react/dist/ssr";
import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps, ReactElement } from "react";
import { Button as ButtonPrimitive } from "@/components/ui/button";
import { cn } from "@/lib/utils";

/**
 * Icon Button (Family 01) — docs/experience_design/Components/01_Buttons.md.
 *
 * A Button whose label is visually an icon but semantically still a name:
 * `label` is MANDATORY and always becomes the `aria-label` — there is no way
 * to render this component without an accessible name (Inventory: "icon-only
 * buttons carry a label"; §17).
 */
const iconButtonVariants = cva(
  "inline-flex shrink-0 items-center justify-center rounded-md outline-none transition-[background-color,border-color,color,opacity] duration-[var(--motion-duration-fast)] ease-standard disabled:pointer-events-none disabled:opacity-disabled",
  {
    variants: {
      variant: {
        // bg-transparent required — see the identical note in Button.tsx.
        quiet: "bg-transparent text-foreground hover:bg-surface-hover",
        secondary:
          "border border-border bg-secondary text-secondary-foreground hover:bg-surface-hover",
        primary: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
      },
      size: {
        sm: "size-7", // 28px
        md: "size-9", // 36px
        lg: "size-11", // 44px
      },
    },
    defaultVariants: {
      variant: "quiet",
      size: "md",
    },
  },
);

const ICON_SIZE: Record<NonNullable<IconButtonProps["size"]>, string> = {
  sm: "size-4", // 16px
  md: "size-5", // 20px
  lg: "size-6", // 24px
};

export interface IconButtonProps
  extends Omit<ComponentProps<"button">, "children">, VariantProps<typeof iconButtonVariants> {
  /** The accessible name — MANDATORY, becomes aria-label. Name the outcome, not the icon. */
  label: string;
  /** The Phosphor glyph. Rendered aria-hidden — `label` carries the name, never the icon. */
  icon: ReactElement;
  loading?: boolean;
  /** For toggle icon buttons (e.g. watchlist add/remove) — reflects as aria-pressed. */
  pressed?: boolean;
}

export function IconButton({
  variant = "quiet",
  size = "md",
  label,
  icon,
  loading = false,
  pressed,
  disabled,
  className,
  ...props
}: IconButtonProps) {
  return (
    <ButtonPrimitive
      type="button"
      aria-label={label}
      aria-pressed={pressed}
      aria-busy={loading || undefined}
      aria-disabled={disabled || loading || undefined}
      disabled={disabled || loading}
      className={cn(iconButtonVariants({ variant, size }), className)}
      {...props}
    >
      {loading ? (
        <CircleNotch
          className={cn(ICON_SIZE[size ?? "md"], "animate-spin")}
          weight="bold"
          aria-hidden="true"
        />
      ) : (
        <span aria-hidden="true" className={cn(ICON_SIZE[size ?? "md"], "inline-flex")}>
          {icon}
        </span>
      )}
    </ButtonPrimitive>
  );
}
