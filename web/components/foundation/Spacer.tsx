import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";
import type { SpaceStep } from "./Flex";

const VERTICAL_CLASS: Record<SpaceStep, string> = {
  0: "h-0",
  1: "h-1",
  2: "h-2",
  3: "h-3",
  4: "h-4",
  5: "h-6",
  6: "h-8",
  7: "h-10",
  8: "h-12",
  9: "h-16",
  10: "h-24",
};

const HORIZONTAL_CLASS: Record<SpaceStep, string> = {
  0: "w-0",
  1: "w-1",
  2: "w-2",
  3: "w-3",
  4: "w-4",
  5: "w-6",
  6: "w-8",
  7: "w-10",
  8: "w-12",
  9: "w-16",
  10: "w-24",
};

/**
 * Spacer — an explicit rhythm gap on one axis, over the `--space-N` scale.
 * Prefer `gap` on `Flex`/`Stack`/`Grid` where possible (04_Spacing_System.md
 * "prefer gap over margins"); this is for the rarer case of a single
 * one-off gap between two elements that aren't already in a gapped container.
 */
export interface SpacerProps extends Omit<ComponentProps<"div">, "children"> {
  size?: SpaceStep;
  axis?: "vertical" | "horizontal";
}

export function Spacer({ size = 4, axis = "vertical", className, ...props }: SpacerProps) {
  return (
    <div
      data-slot="foundation-spacer"
      aria-hidden="true"
      className={cn(
        "shrink-0",
        axis === "vertical" ? VERTICAL_CLASS[size] : HORIZONTAL_CLASS[size],
        className,
      )}
      {...props}
    />
  );
}
