import { WarningCircle } from "@phosphor-icons/react/dist/ssr";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * ValidationMessage — the frozen error-text treatment (02_Text_Inputs.md):
 * `type.caption`, `--destructive`, with icon (never color alone). `role="alert"`
 * so screen readers announce it as it appears. Standalone so it can attach to
 * a field (via FormField) or a control group (Checkbox/Radio group-level
 * errors, 03_Selection_Controls.md).
 */
export function ValidationMessage({ className, children, ...props }: ComponentProps<"p">) {
  return (
    <p
      role="alert"
      className={cn("text-destructive flex items-center gap-1 text-xs", className)}
      {...props}
    >
      <WarningCircle aria-hidden="true" className="size-3.5 shrink-0" />
      {children}
    </p>
  );
}
