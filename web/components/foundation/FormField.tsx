import { cloneElement, isValidElement, useId, type ReactElement } from "react";
import { Label as LabelPrimitive } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import { HelperText } from "./HelperText";
import { ValidationMessage } from "./ValidationMessage";

/**
 * FormField (Family 02/03 — label + control + help/error). Per
 * 02_Text_Inputs.md: "All three components live inside a FormField wrapper
 * in forms" — the label is always present, help/error occupies reserved
 * height so validation never shifts layout, and the control receives its
 * id/aria-describedby/aria-invalid automatically via cloneElement (the
 * caller doesn't wire these by hand — one less place to get it wrong).
 *
 * `children` must be a single control that accepts `id`, `aria-describedby`,
 * and `aria-invalid` (Input, Textarea, Select trigger, etc.).
 */
export interface FormFieldProps {
  label: string;
  helpText?: string;
  error?: string;
  required?: boolean;
  children: ReactElement<{
    id?: string;
    "aria-describedby"?: string;
    "aria-invalid"?: boolean;
  }>;
  className?: string;
}

export function FormField({
  label,
  helpText,
  error,
  required,
  children,
  className,
}: FormFieldProps) {
  const id = useId();
  const helpId = `${id}-help`;
  const errorId = `${id}-error`;
  // Error takes priority over help text and only one ever renders below —
  // aria-describedby must reference only the id that actually exists in the
  // DOM, not both (a dangling reference is silently skipped by assistive
  // tech, which would mask this being wrong rather than surface it).
  const describedBy = error ? errorId : helpText ? helpId : undefined;

  const control = isValidElement(children)
    ? cloneElement(children, {
        id,
        "aria-describedby": describedBy,
        "aria-invalid": !!error,
      })
    : children;

  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <LabelPrimitive htmlFor={id} className="text-foreground text-sm">
        {label}
        {required && (
          <span aria-hidden="true" className="text-destructive">
            *
          </span>
        )}
      </LabelPrimitive>
      {control}
      {/* Reserved-height region: help/error never shifts layout when it appears (spec §Anatomy). */}
      <div className="min-h-4">
        {error ? (
          <ValidationMessage id={errorId}>{error}</ValidationMessage>
        ) : helpText ? (
          <HelperText id={helpId}>{helpText}</HelperText>
        ) : null}
      </div>
    </div>
  );
}
