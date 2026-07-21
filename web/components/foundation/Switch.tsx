"use client";

import { useId, type ComponentProps } from "react";
import { Switch as SwitchPrimitive } from "@/components/ui/switch";
import { Label as LabelPrimitive } from "@/components/ui/label";
import { cn } from "@/lib/utils";

/**
 * Switch (Family 03) — docs/experience_design/Components/03_Selection_Controls.md.
 * Immediate-effect setting toggle. `showStateLabel` renders the mandatory
 * textual On/Off cue (spec: "knob position AND a state label — never color
 * alone"); on by default since the spec treats it as required, not optional.
 */
export interface SwitchProps extends ComponentProps<typeof SwitchPrimitive> {
  label: string;
  showStateLabel?: boolean;
}

export function Switch({
  label,
  showStateLabel = true,
  id,
  checked,
  className,
  ...props
}: SwitchProps) {
  const generatedId = useId();
  const resolvedId = id ?? generatedId;

  return (
    <div className="flex items-center justify-between gap-3">
      <LabelPrimitive htmlFor={resolvedId} className="text-foreground text-sm font-normal">
        {label}
      </LabelPrimitive>
      <div className="flex items-center gap-2">
        {showStateLabel && (
          <span className="text-muted-foreground text-xs" aria-hidden="true">
            {checked ? "On" : "Off"}
          </span>
        )}
        <SwitchPrimitive id={resolvedId} checked={checked} className={cn(className)} {...props} />
      </div>
    </div>
  );
}
