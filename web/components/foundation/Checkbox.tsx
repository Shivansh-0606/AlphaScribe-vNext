"use client";

import { Check, Minus } from "@phosphor-icons/react/dist/ssr";
import { Checkbox as CheckboxPrimitive } from "radix-ui";
import { useId, type ComponentProps } from "react";
import { Label as LabelPrimitive } from "@/components/ui/label";
import { cn } from "@/lib/utils";

/**
 * Checkbox (Family 03) — docs/experience_design/Components/03_Selection_Controls.md.
 * `checked` accepts Radix's `boolean | "indeterminate"` directly — no manual
 * ref/DOM hack needed for the indeterminate state.
 *
 * Composes the raw `radix-ui` primitive directly rather than the generated
 * `components/ui/checkbox.tsx` — that generated file only styles
 * `data-[state=checked]` (no rule for `data-[state=indeterminate]`) and
 * hardcodes a checkmark glyph for both states. The spec requires "distinct
 * glyphs (✓ vs –); both carry the non-color cue" — found via real-browser
 * computed-style verification (indeterminate rendered with no fill at all,
 * same as unchecked), fixed here rather than hand-editing the generated
 * primitive.
 */
export interface CheckboxProps extends Omit<ComponentProps<typeof CheckboxPrimitive.Root>, "size"> {
  label: string;
  size?: "sm" | "md";
}

const BOX_SIZE: Record<NonNullable<CheckboxProps["size"]>, string> = {
  sm: "size-4", // 16px
  md: "size-5", // 20px
};

const GLYPH_SIZE: Record<NonNullable<CheckboxProps["size"]>, string> = {
  sm: "size-3",
  md: "size-3.5",
};

export function Checkbox({ label, size = "md", id, checked, className, ...props }: CheckboxProps) {
  const generatedId = useId();
  const resolvedId = id ?? generatedId;

  return (
    <div className="flex items-center gap-2">
      <CheckboxPrimitive.Root
        id={resolvedId}
        checked={checked}
        className={cn(
          BOX_SIZE[size],
          "border-input focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 shrink-0 rounded-sm border shadow-xs transition-shadow outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50",
          "data-[state=checked]:border-primary data-[state=checked]:bg-primary data-[state=checked]:text-primary-foreground",
          "data-[state=indeterminate]:border-primary data-[state=indeterminate]:bg-primary data-[state=indeterminate]:text-primary-foreground",
          className,
        )}
        {...props}
      >
        <CheckboxPrimitive.Indicator className="grid place-content-center text-current transition-none">
          {checked === "indeterminate" ? (
            <Minus className={GLYPH_SIZE[size]} weight="bold" />
          ) : (
            <Check className={GLYPH_SIZE[size]} weight="bold" />
          )}
        </CheckboxPrimitive.Indicator>
      </CheckboxPrimitive.Root>
      <LabelPrimitive htmlFor={resolvedId} className="text-foreground text-sm font-normal">
        {label}
      </LabelPrimitive>
    </div>
  );
}
