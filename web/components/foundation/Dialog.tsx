"use client";

import { X } from "@phosphor-icons/react/dist/ssr";
import { Dialog as DialogPrimitive } from "radix-ui";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";
import { IconButton } from "./IconButton";

/**
 * Dialog (Family 06) — docs/experience_design/Components/06_Overlays.md.
 * Composes the raw `radix-ui` Dialog primitive directly rather than the
 * generated `components/ui/dialog.tsx` — that generated `DialogContent`
 * bakes its own `DialogOverlay` call directly into its JSX with no way to
 * pass a differently-styled one in, so there's no way to fix the scrim
 * token from outside (the same reason `Checkbox`/`Progress` bypass their
 * generated primitives).
 *
 * Off-token values replaced with the frozen ones (04.2 AD-3 "tokens or
 * nothing"): scrim `bg-black/50` → `bg-foreground opacity-scrim`; panel
 * `rounded-lg`/`bg-background` → `rounded-md`/`bg-popover` (a raised
 * floating surface, not the page canvas); layering/motion `z-50`/
 * `duration-200` → `--z-modal`/`--motion-duration-slow` (`shadow-lg`
 * already matches `--shadow-lg` by coincidence of naming, left as-is). The
 * close control uses `IconButton` (mandatory `label`, Phosphor `X`) instead
 * of the generated file's raw `lucide-react` icon-in-a-div.
 *
 * Compose the actions row inside `DialogFooter` with the foundation
 * `Button` (a primary + a `quiet`/`secondary` Cancel) — there is no
 * built-in `showCloseButton` shortcut here (unlike the generated primitive)
 * specifically so a raw, non-token-bound button can never leak in.
 */
export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogClose = DialogPrimitive.Close;

function DialogOverlay({ className, ...props }: ComponentProps<typeof DialogPrimitive.Overlay>) {
  return (
    <DialogPrimitive.Overlay
      data-slot="foundation-dialog-overlay"
      className={cn(
        "bg-foreground opacity-scrim fixed inset-0 z-[var(--z-modal)]",
        "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:animate-in data-[state=open]:fade-in-0",
        className,
      )}
      {...props}
    />
  );
}

export interface DialogContentProps extends ComponentProps<typeof DialogPrimitive.Content> {
  /** Off by default — compose the close affordance explicitly via `DialogClose` + `IconButton`, or opt into the default top-right one here. */
  showCloseButton?: boolean;
}

export function DialogContent({
  className,
  children,
  showCloseButton = false,
  ...props
}: DialogContentProps) {
  return (
    <DialogPrimitive.Portal>
      <DialogOverlay />
      <DialogPrimitive.Content
        data-slot="foundation-dialog-content"
        className={cn(
          "border-border bg-popover text-popover-foreground fixed top-1/2 left-1/2 z-[var(--z-modal)] grid w-full max-w-[calc(100%-2rem)] -translate-x-1/2 -translate-y-1/2 gap-4 rounded-md border p-6 shadow-lg duration-[var(--motion-duration-slow)] outline-none",
          "data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[state=open]:animate-in data-[state=open]:fade-in-0 data-[state=open]:zoom-in-95",
          "sm:max-w-lg",
          className,
        )}
        {...props}
      >
        {children}
        {showCloseButton && (
          <DialogPrimitive.Close asChild className="absolute top-4 right-4">
            <IconButton label="Close" icon={<X />} size="sm" variant="quiet" />
          </DialogPrimitive.Close>
        )}
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}

export function DialogHeader({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      data-slot="foundation-dialog-header"
      className={cn("flex flex-col gap-2 text-center sm:text-left", className)}
      {...props}
    />
  );
}

export function DialogFooter({ className, ...props }: ComponentProps<"div">) {
  return (
    <div
      data-slot="foundation-dialog-footer"
      className={cn("flex flex-col-reverse gap-2 sm:flex-row sm:justify-end", className)}
      {...props}
    />
  );
}

export function DialogTitle({ className, ...props }: ComponentProps<typeof DialogPrimitive.Title>) {
  return (
    <DialogPrimitive.Title
      data-slot="foundation-dialog-title"
      className={cn("text-foreground font-sans text-lg leading-none font-semibold", className)}
      {...props}
    />
  );
}

export function DialogDescription({
  className,
  ...props
}: ComponentProps<typeof DialogPrimitive.Description>) {
  return (
    <DialogPrimitive.Description
      data-slot="foundation-dialog-description"
      className={cn("text-muted-foreground font-sans text-sm", className)}
      {...props}
    />
  );
}
