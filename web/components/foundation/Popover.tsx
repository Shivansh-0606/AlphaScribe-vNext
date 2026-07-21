"use client";

import type { ComponentProps } from "react";
import {
  Popover,
  PopoverAnchor,
  PopoverContent as PopoverContentPrimitive,
  PopoverDescription,
  PopoverHeader,
  PopoverTitle,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";

/**
 * Popover (Family 06) — docs/experience_design/Components/06_Overlays.md.
 * Root/Trigger/Anchor/Header/Title/Description re-exported as generated —
 * already correctly token-bound (`bg-popover`, `shadow-md`, `border`).
 * Only `PopoverContent` is wrapped, to swap the raw `z-50` for the frozen
 * `--z-overlay` token (04.2 AD-3 "tokens or nothing") — everything else
 * about the generated primitive already matches the spec.
 */
export function PopoverContent({
  className,
  ...props
}: ComponentProps<typeof PopoverContentPrimitive>) {
  return (
    <PopoverContentPrimitive
      data-slot="foundation-popover-content"
      className={cn("z-[var(--z-overlay)]", className)}
      {...props}
    />
  );
}

export { Popover, PopoverAnchor, PopoverDescription, PopoverHeader, PopoverTitle, PopoverTrigger };
