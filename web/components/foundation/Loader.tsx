import { CircleNotch } from "@phosphor-icons/react/dist/ssr";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * Loader (Family 07) — docs/experience_design/Components/07_Feedback_Status.md.
 * No shadcn primitive maps to this token (Component Mapping: "wrapped ·
 * Motion"). Covers the spec's **Region** / **Full-view** variants —
 * **Inline** (in a button/field) is already the existing `CircleNotch` spinner Button.tsx
 * and IconButton.tsx render for their own `loading` prop; this isn't a
 * refactor of that, just the standalone region/full-view case those two
 * don't cover.
 */
export interface LoaderProps extends ComponentProps<"div"> {
  /** Always visible text, not just an aria-label — busy semantics pair with a readable label (spec). */
  label?: string;
  size?: "sm" | "md";
  /** Rare — the initial-boot-only case: fixed, centered over the full viewport. */
  fullView?: boolean;
}

const ICON_SIZE: Record<NonNullable<LoaderProps["size"]>, string> = {
  sm: "size-4",
  md: "size-6",
};

export function Loader({
  label = "Loading…",
  size = "md",
  fullView = false,
  className,
  ...props
}: LoaderProps) {
  return (
    <div
      data-slot="foundation-loader"
      role="status"
      className={cn(
        "text-muted-foreground flex flex-col items-center justify-center gap-2",
        fullView && "bg-background/80 fixed inset-0 z-[var(--z-overlay)]",
        className,
      )}
      {...props}
    >
      <CircleNotch
        className={cn(ICON_SIZE[size], "animate-spin")}
        weight="bold"
        aria-hidden="true"
      />
      <span className="font-sans text-xs">{label}</span>
    </div>
  );
}
