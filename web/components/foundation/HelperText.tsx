import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * HelperText — the frozen help-text treatment (02_Text_Inputs.md): `type.caption`,
 * `--muted-foreground`. Standalone so it can attach to a field (via
 * FormField) or stand alone beside any control.
 */
export function HelperText({ className, ...props }: ComponentProps<"p">) {
  return <p className={cn("text-muted-foreground text-xs", className)} {...props} />;
}
