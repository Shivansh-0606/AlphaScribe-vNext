"use client";

import type { ComponentProps } from "react";
import { Textarea as TextareaPrimitive } from "@/components/ui/textarea";
import { cn } from "@/lib/utils";

/**
 * Textarea (Family 02) — docs/experience_design/Components/02_Text_Inputs.md.
 * Auto-grow uses the native CSS `field-sizing: content` (already in the
 * generated primitive) — no JS resize handler needed. `maxLength` + the
 * counter warn near the limit; never silently truncates (spec anti-pattern).
 */
export interface TextareaProps extends ComponentProps<"textarea"> {
  /** Shows a "used/max" counter; announced politely near the limit, not on every keystroke. */
  showCounter?: boolean;
}

export function Textarea({ className, showCounter, maxLength, value, ...props }: TextareaProps) {
  const length = typeof value === "string" ? value.length : 0;
  const nearLimit = !!maxLength && length >= maxLength * 0.9;

  return (
    <div className="flex flex-col gap-1">
      <TextareaPrimitive
        className={cn(
          "bg-input-bg placeholder:text-muted-foreground border-input text-foreground ease-standard focus-visible:border-ring aria-invalid:border-destructive disabled:opacity-disabled min-h-20 rounded-md border px-3 py-2 text-base transition-[border-color,box-shadow] duration-[var(--motion-duration-fast)] outline-none disabled:pointer-events-none",
          className,
        )}
        maxLength={maxLength}
        value={value}
        {...props}
      />
      {showCounter && maxLength && (
        <span
          aria-live="polite"
          className={cn(
            "text-muted-foreground self-end text-xs",
            nearLimit && "text-warning font-medium",
          )}
        >
          {length}/{maxLength}
        </span>
      )}
    </div>
  );
}
