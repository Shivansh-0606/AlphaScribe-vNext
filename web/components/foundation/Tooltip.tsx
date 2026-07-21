"use client";

import { Tooltip as TooltipPrimitive } from "radix-ui";
import type { ComponentProps, ReactElement, ReactNode } from "react";
import { cn } from "@/lib/utils";

/**
 * Tooltip (Family 06) — docs/experience_design/Components/06_Overlays.md.
 * `TooltipProvider` is mounted once at the app root (`providers/AppProviders.tsx`)
 * — never re-added per instance.
 *
 * Composes Root/Trigger/Content into one component (like `FormField` wires
 * label/control/help) so callers never hand-assemble the three pieces. The
 * generated `components/ui/tooltip.tsx` uses an inverted `bg-foreground`
 * bubble with no shadow and a raw `z-50` — overridden here to the frozen
 * `--popover` surface + `--shadow-md` + `--z-overlay` the spec actually
 * calls for (Token usage: "--popover(-foreground)", same class of fix as
 * Button's variant cancellation, just for a different property set).
 *
 * `children` must accept a ref (a native element or another Radix
 * trigger) — `asChild` composes it directly as the trigger, so hover/focus
 * land on the real control, never a wrapping `<button>`. Supplementary only
 * (spec: never the only place essential info lives) — pair with, never
 * replace, `IconButton`'s own mandatory `label`.
 *
 * `forceMount` on `Portal`/`Content`, with `data-[state=closed]:opacity-0
 * pointer-events-none` doing the actual hide-at-rest: without it, opening
 * via **keyboard focus** (never hover) reproducibly self-closed on the very
 * next tick, 100% of the time — confirmed by tracing Radix's own source:
 * `TooltipContent` subscribes to a `document`-level `"tooltip.open"` event
 * (its cross-instance "only one tooltip open at a time" mechanism) in a
 * mount effect, and on the *synchronous* focus path that mount effect and
 * the dispatch from opening race in the same commit, so Content catches its
 * own just-fired open event and immediately closes itself. The *delayed*
 * hover path (a real `setTimeout`) never raced this way — confirmed via a
 * 6-run stress test each way (0/6 opened on focus, 6/6 opened on hover)
 * before this fix, 6/6 after. `forceMount` sidesteps the race entirely by
 * mounting Content once, up front, rather than exactly when it needs to
 * become visible — the same effect-timing class of bug as `Chip`'s
 * `data-[selected]` fix, just triggered by different code. Not a jsdom-only
 * concern: reproduced against a full `next build && next start`.
 */
export interface TooltipProps {
  content: ReactNode;
  children: ReactElement;
  side?: ComponentProps<typeof TooltipPrimitive.Content>["side"];
  /** `definition` allows a slightly wider bubble for a learner-term explanation; still never a paragraph panel. */
  variant?: "text" | "definition";
}

export function Tooltip({ content, children, side = "top", variant = "text" }: TooltipProps) {
  return (
    <TooltipPrimitive.Root>
      <TooltipPrimitive.Trigger asChild>{children}</TooltipPrimitive.Trigger>
      <TooltipPrimitive.Portal forceMount>
        <TooltipPrimitive.Content
          forceMount
          data-slot="foundation-tooltip-content"
          side={side}
          sideOffset={6}
          className={cn(
            "border-border bg-popover text-popover-foreground z-[var(--z-overlay)] rounded-md border px-3 py-1.5 font-sans text-xs shadow-md",
            "data-[state=closed]:pointer-events-none data-[state=closed]:opacity-0",
            "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95",
            "data-[state=delayed-open]:animate-in data-[state=delayed-open]:fade-in-0 data-[state=delayed-open]:zoom-in-95",
            "data-[state=instant-open]:animate-in data-[state=instant-open]:fade-in-0 data-[state=instant-open]:zoom-in-95",
            variant === "definition" ? "max-w-xs" : "max-w-56",
          )}
        >
          {content}
          <TooltipPrimitive.Arrow className="fill-popover" />
        </TooltipPrimitive.Content>
      </TooltipPrimitive.Portal>
    </TooltipPrimitive.Root>
  );
}
