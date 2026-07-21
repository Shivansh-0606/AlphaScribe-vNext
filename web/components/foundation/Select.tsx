"use client";

import type { ComponentProps } from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger as SelectTriggerPrimitive,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

/**
 * Select (Family 03) — docs/experience_design/Components/03_Selection_Controls.md.
 * Native-backed Radix Select (best a11y/mobile per the frozen preference).
 * Sub-components (`SelectContent`/`SelectItem`/etc.) are re-exported as
 * generated — already correctly token-bound (bg-popover, focus:bg-accent) —
 * only `SelectTrigger` is wrapped, to add the frozen `lg` size shadcn
 * doesn't ship (it only has `sm`/`default`).
 */
export interface SelectTriggerProps extends Omit<
  ComponentProps<typeof SelectTriggerPrimitive>,
  "size"
> {
  size?: "sm" | "md" | "lg";
}

const SIZE_TO_PRIMITIVE = { sm: "sm", md: "default", lg: "default" } as const;

export function SelectTrigger({ size = "md", className, ...props }: SelectTriggerProps) {
  return (
    <SelectTriggerPrimitive
      size={SIZE_TO_PRIMITIVE[size]}
      className={cn(size === "lg" && "h-11 text-base", "bg-input-bg", className)}
      {...props}
    />
  );
}

export {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectValue,
};
