import type { ComponentProps, ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * Skeleton (Family 07) — docs/experience_design/Components/07_Feedback_Status.md.
 * The generated `components/ui/skeleton.tsx` is already token-bound
 * (`bg-accent`, `rounded-md`) and its `animate-pulse` already honors the
 * global reduced-motion override (globals.css) — re-exported as a shape
 * primitive, matching real content dimensions exactly (no layout shift on
 * swap, per spec). Always decorative (`aria-hidden`): placeholders are never
 * read as real data — wrap a group in `SkeletonGroup` for the one real
 * "loading" status a screen reader should hear.
 */
export function Skeleton({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      data-slot="foundation-skeleton"
      aria-hidden="true"
      className={cn("bg-accent animate-pulse rounded-md", className)}
      {...props}
    />
  );
}

export interface SkeletonTextProps extends ComponentProps<"div"> {
  /** Number of placeholder lines. The last line renders shorter (the common "ragged end" convention). */
  lines?: number;
}

export function SkeletonText({ lines = 3, className, ...props }: SkeletonTextProps) {
  return (
    <div
      data-slot="foundation-skeleton-text"
      className={cn("flex flex-col gap-2", className)}
      {...props}
    >
      {Array.from({ length: lines }, (_, i) => (
        <Skeleton
          key={i}
          className={cn("h-4", i === lines - 1 && lines > 1 ? "w-2/3" : "w-full")}
        />
      ))}
    </div>
  );
}

export interface SkeletonGroupProps extends ComponentProps<"div"> {
  children: ReactNode;
  /** The one accessible "loading" status for the whole region (spec: a single status, not per-shape). */
  label?: string;
}

export function SkeletonGroup({
  children,
  label = "Loading",
  className,
  ...props
}: SkeletonGroupProps) {
  return (
    <div data-slot="foundation-skeleton-group" role="status" className={className} {...props}>
      <span className="sr-only">{label}</span>
      {children}
    </div>
  );
}
