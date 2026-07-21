"use client";

import { useId, type ComponentProps } from "react";
import {
  RadioGroup as RadioGroupPrimitive,
  RadioGroupItem as RadioGroupItemPrimitive,
} from "@/components/ui/radio-group";
import { Label as LabelPrimitive } from "@/components/ui/label";
import { cn } from "@/lib/utils";

/**
 * Radio (Family 03) — docs/experience_design/Components/03_Selection_Controls.md.
 * Choose exactly one from a small set. A native `<fieldset>`/`<legend>` group
 * with Radix's roving-tabindex + arrow-key model (Tab enters/exits the
 * group, arrows move+select within it) — never reimplemented.
 */
export interface RadioGroupProps extends ComponentProps<typeof RadioGroupPrimitive> {
  /** The group's accessible name — rendered as a visible <legend>. */
  label: string;
}

export function RadioGroup({ label, className, children, ...props }: RadioGroupProps) {
  return (
    <fieldset className={cn("flex flex-col gap-2", className)}>
      <legend className="text-foreground mb-1 text-sm">{label}</legend>
      <RadioGroupPrimitive {...props}>{children}</RadioGroupPrimitive>
    </fieldset>
  );
}

export interface RadioGroupItemProps extends ComponentProps<typeof RadioGroupItemPrimitive> {
  label: string;
}

export function RadioGroupItem({ label, id, className, ...props }: RadioGroupItemProps) {
  const generatedId = useId();
  const resolvedId = id ?? generatedId;

  return (
    <div className="flex items-center gap-2">
      <RadioGroupItemPrimitive id={resolvedId} className={cn("size-4", className)} {...props} />
      <LabelPrimitive htmlFor={resolvedId} className="text-foreground text-sm font-normal">
        {label}
      </LabelPrimitive>
    </div>
  );
}
