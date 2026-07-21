import { X } from "@phosphor-icons/react/dist/ssr";
import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps, ReactElement } from "react";
import { cn } from "@/lib/utils";
import { IconButton } from "./IconButton";

/**
 * Chip (Family 05) — docs/experience_design/Components/05_Content_Data_Display.md.
 * No shadcn primitive maps to this token (Component Mapping: "wrapped token") —
 * built directly on native elements.
 *
 * `variant` drives both visuals and semantics:
 * - `filter` / `choice`: a real `<button>` (toggle vs single-select action).
 * - `removable` / `static`: a non-interactive `<span>` — only the trailing ✕
 *   (rendered via `IconButton`, itself focusable and labeled "Remove {x}")
 *   is ever a separate interactive target for `removable`.
 */
const chipVariants = cva(
  "inline-flex shrink-0 items-center gap-1.5 rounded-pill border border-border bg-surface font-sans text-foreground whitespace-nowrap transition-[background-color,border-color,color] duration-[var(--motion-duration-fast)] ease-standard",
  {
    variants: {
      variant: {
        filter: "cursor-pointer hover:bg-surface-hover",
        choice: "cursor-pointer hover:bg-surface-hover",
        removable: "",
        static: "",
      },
      size: {
        sm: "h-7 px-2 text-xs",
        md: "h-9 px-2.5 text-sm",
      },
    },
    defaultVariants: {
      variant: "static",
      size: "md",
    },
  },
);

// Selected must be a JS-level conditional class (via cn/tailwind-merge below),
// not a `data-[selected=true]:` CSS variant on top of the always-present
// `border-border`/`bg-surface` base — Tailwind v4 wraps variant selectors in
// `:where()` (zero added specificity), so that CSS rule ties with the
// unconditional base at equal specificity and loses to it on source order,
// silently never painting the selected cue. Found via real-browser computed-
// style inspection (border-color stayed identical before/after selecting) —
// the same class of leak Button.tsx documents, fixed the same way: let
// tailwind-merge fully drop the losing class instead of leaving both for CSS
// cascade order to referee.
const SELECTED_FILTER_CLASSNAME = "border-primary bg-accent text-accent-foreground";

export interface ChipProps
  extends
    Omit<ComponentProps<"button">, "children" | "onClick">,
    VariantProps<typeof chipVariants> {
  children: React.ReactNode;
  /** Rendered `aria-hidden` — the text label always carries the meaning. */
  icon?: ReactElement;
  /** Filter chips only — reflects as `aria-pressed`; carries a non-color cue via the variant's selected classes. */
  selected?: boolean;
  onClick?: () => void;
  /** Renders a labeled, separately-focusable ✕. Makes the chip a "removable" token regardless of `variant`. */
  onRemove?: () => void;
}

export function Chip({
  variant = "static",
  size = "md",
  children,
  icon,
  selected,
  onClick,
  onRemove,
  className,
  ...props
}: ChipProps) {
  const isInteractive = variant === "filter" || variant === "choice";
  const content = (
    <>
      {icon && (
        <span aria-hidden="true" className="inline-flex size-3.5 shrink-0">
          {icon}
        </span>
      )}
      {children}
    </>
  );

  const rootClassName = cn(
    chipVariants({ variant, size }),
    variant === "filter" && selected && SELECTED_FILTER_CLASSNAME,
    className,
  );

  if (isInteractive) {
    return (
      <button
        type="button"
        data-slot="foundation-chip"
        data-selected={variant === "filter" ? selected : undefined}
        aria-pressed={variant === "filter" ? selected : undefined}
        onClick={onClick}
        className={rootClassName}
        {...props}
      >
        {content}
        {onRemove && (
          <IconButton
            label={`Remove ${typeof children === "string" ? children : ""}`.trim()}
            icon={<X />}
            size="sm"
            variant="quiet"
            className="-mr-1 size-5"
            onClick={(event) => {
              event.stopPropagation();
              onRemove();
            }}
          />
        )}
      </button>
    );
  }

  return (
    <span data-slot="foundation-chip" className={rootClassName}>
      {content}
      {onRemove && (
        <IconButton
          label={`Remove ${typeof children === "string" ? children : ""}`.trim()}
          icon={<X />}
          size="sm"
          variant="quiet"
          className="-mr-1 size-5"
          onClick={onRemove}
        />
      )}
    </span>
  );
}
