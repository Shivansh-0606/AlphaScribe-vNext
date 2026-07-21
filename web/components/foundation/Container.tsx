import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * Container — the page-edge margin + max-width wrapper from
 * docs/experience_design/05_Grid_System.md (`--grid-max-content` ≈
 * 1280–1440px, margins growing `--space-4`→`--space-8` by context).
 * `reading` swaps the max-width to `--reading-max` (72ch) for long-form
 * research text, per that doc's "reading measure protected" principle.
 */
export interface ContainerProps extends ComponentProps<"div"> {
  reading?: boolean;
}

export function Container({ reading = false, className, ...props }: ContainerProps) {
  return (
    <div
      data-slot="foundation-container"
      className={cn(
        "mx-auto w-full px-4 md:px-6 lg:px-8",
        reading ? "max-w-[72ch]" : "max-w-[1400px]",
        className,
      )}
      {...props}
    />
  );
}
