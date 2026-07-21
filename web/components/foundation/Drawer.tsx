"use client";

import { X } from "@phosphor-icons/react/dist/ssr";
import { Dialog as DrawerPrimitive } from "radix-ui";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";
import { IconButton } from "./IconButton";

/**
 * Drawer (Family 06) — docs/experience_design/Components/06_Overlays.md.
 * Edge-anchored panel: the mobile nav (modal) or a contextual/AI-companion
 * surface (non-modal). Radix's Sheet IS its Dialog primitive under a
 * different name — composed directly here (same reason as `Dialog.tsx`):
 * the generated `components/ui/sheet.tsx` bakes its own `SheetOverlay` call
 * into `SheetContent` with no way to omit it for the non-modal case.
 *
 * Off-token values replaced (04.2 AD-3): scrim `bg-black/50` →
 * `bg-foreground opacity-scrim`; panel `bg-background` → `bg-surface` (the
 * spec's Token usage for Drawer, distinct from Dialog's `--popover`); no
 * `rounded-*` is added — the spec calls for sharp edges on an edge-anchored
 * panel, and the generated primitive already has none; layering/motion
 * `z-50`/raw durations → `--z-drawer`/`--motion-duration-slow`.
 *
 * `modal` on `DrawerContent` only toggles the rendered scrim — pass the
 * same `modal={false}` to the `Drawer` root too (Radix's own prop) to also
 * drop the focus trap for a genuinely non-modal companion (spec: "does not
 * trap focus, the user moves between content and companion freely").
 * **Not built:** the AI companion's own streaming/thinking states — that
 * behavior belongs to Family 08 (`CopilotPanel`), not forked here.
 */
export const Drawer = DrawerPrimitive.Root;
export const DrawerTrigger = DrawerPrimitive.Trigger;
export const DrawerClose = DrawerPrimitive.Close;

function DrawerOverlay({ className, ...props }: ComponentProps<typeof DrawerPrimitive.Overlay>) {
  return (
    <DrawerPrimitive.Overlay
      data-slot="foundation-drawer-overlay"
      className={cn(
        "bg-foreground opacity-scrim fixed inset-0 z-[var(--z-drawer)]",
        "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0",
        className,
      )}
      {...props}
    />
  );
}

const SIDE_CLASSNAME = {
  right:
    "inset-y-0 right-0 h-full w-3/4 border-l border-border data-[state=closed]:slide-out-to-right data-[state=open]:slide-in-from-right sm:max-w-sm",
  left: "inset-y-0 left-0 h-full w-3/4 border-r border-border data-[state=closed]:slide-out-to-left data-[state=open]:slide-in-from-left sm:max-w-sm",
  top: "inset-x-0 top-0 h-auto border-b border-border data-[state=closed]:slide-out-to-top data-[state=open]:slide-in-from-top",
  bottom:
    "inset-x-0 bottom-0 h-auto border-t border-border data-[state=closed]:slide-out-to-bottom data-[state=open]:slide-in-from-bottom",
} as const;

export interface DrawerContentProps extends ComponentProps<typeof DrawerPrimitive.Content> {
  side?: keyof typeof SIDE_CLASSNAME;
  /** Suppresses the scrim for a non-modal companion — see the file doc for pairing this with the `Drawer` root's own `modal` prop. */
  modal?: boolean;
  showCloseButton?: boolean;
}

export function DrawerContent({
  side = "right",
  modal = true,
  showCloseButton = true,
  className,
  children,
  ...props
}: DrawerContentProps) {
  return (
    <DrawerPrimitive.Portal>
      {modal && <DrawerOverlay />}
      <DrawerPrimitive.Content
        data-slot="foundation-drawer-content"
        className={cn(
          "bg-surface text-foreground ease-standard fixed z-[var(--z-drawer)] flex flex-col gap-4 shadow-lg transition",
          "data-[state=closed]:animate-out data-[state=open]:animate-in data-[state=closed]:duration-[var(--motion-duration-slow)] data-[state=open]:duration-[var(--motion-duration-slow)]",
          SIDE_CLASSNAME[side],
          className,
        )}
        {...props}
      >
        {children}
        {showCloseButton && (
          <DrawerPrimitive.Close asChild className="absolute top-4 right-4">
            <IconButton label="Close" icon={<X />} size="sm" variant="quiet" />
          </DrawerPrimitive.Close>
        )}
      </DrawerPrimitive.Content>
    </DrawerPrimitive.Portal>
  );
}

export function DrawerHeader({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      data-slot="foundation-drawer-header"
      className={cn("flex flex-col gap-1.5 p-4", className)}
      {...props}
    />
  );
}

export function DrawerFooter({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      data-slot="foundation-drawer-footer"
      className={cn("mt-auto flex flex-col gap-2 p-4", className)}
      {...props}
    />
  );
}

export function DrawerTitle({ className, ...props }: ComponentProps<typeof DrawerPrimitive.Title>) {
  return (
    <DrawerPrimitive.Title
      data-slot="foundation-drawer-title"
      className={cn("text-foreground font-sans font-semibold", className)}
      {...props}
    />
  );
}

export function DrawerDescription({
  className,
  ...props
}: ComponentProps<typeof DrawerPrimitive.Description>) {
  return (
    <DrawerPrimitive.Description
      data-slot="foundation-drawer-description"
      className={cn("text-muted-foreground font-sans text-sm", className)}
      {...props}
    />
  );
}
