import { CheckCircle, Info, WarningCircle, X, XCircle } from "@phosphor-icons/react/dist/ssr";
import type { ComponentProps, ReactElement, ReactNode } from "react";
import { cn } from "@/lib/utils";
import { IconButton } from "./IconButton";

/**
 * Banner (Family 07) — docs/experience_design/Components/07_Feedback_Status.md,
 * the **inline banner** variant of Notification (Component Mapping:
 * "region banner / list" — no shadcn primitive). Persistent status for a
 * region (Offline, Partial Failure, permission notice) — not a transient
 * outcome (that's `sonner`'s `toast()`, see the foundation README).
 *
 * **Not built:** the notification-list-item variant — it composes a
 * `ListItem` primitive (Inventory) that doesn't exist yet; deferred until
 * that primitive lands rather than forked here.
 *
 * Tone is a plain per-tone lookup (like `Button`'s `variant`), not a
 * `data-[attr]:` CSS conditional — avoids the specificity-tie class of bug
 * documented for `Chip` in the README, since only one tone's classes are
 * ever in the DOM at a time.
 */
const BANNER_TONE = {
  info: { icon: Info, className: "border-border bg-muted" },
  success: { icon: CheckCircle, className: "border-bullish/30 bg-bullish/10" },
  warning: { icon: WarningCircle, className: "border-warning/30 bg-warning/10" },
  error: { icon: XCircle, className: "border-bearish/30 bg-bearish/10" },
} as const;

export interface BannerProps extends Omit<ComponentProps<"div">, "title"> {
  tone: keyof typeof BANNER_TONE;
  /** Optional bold lead-in above the message. */
  title?: string;
  children: ReactNode;
  /** e.g. a `Button` — a labeled, keyboard-reachable action. */
  action?: ReactElement;
  /** Renders a labeled "Dismiss" control. Omit for a condition that clears itself (e.g. Offline). */
  onDismiss?: () => void;
}

export function Banner({
  tone,
  title,
  children,
  action,
  onDismiss,
  className,
  ...props
}: BannerProps) {
  const { icon: Icon, className: toneClassName } = BANNER_TONE[tone];
  // warning/error are assertive (interrupt); info/success are polite — matches
  // the spec's "role=status/alert per severity".
  const role = tone === "warning" || tone === "error" ? "alert" : "status";

  return (
    <div
      data-slot="foundation-banner"
      role={role}
      className={cn(
        "text-foreground flex items-start gap-3 rounded-md border p-4",
        toneClassName,
        className,
      )}
      {...props}
    >
      <Icon className="mt-0.5 size-5 shrink-0" weight="bold" aria-hidden="true" />
      <div className="flex flex-1 flex-col gap-1">
        {title && <p className="font-sans text-sm font-semibold">{title}</p>}
        <p className="font-sans text-sm">{children}</p>
      </div>
      {action}
      {onDismiss && (
        <IconButton label="Dismiss" icon={<X />} size="sm" variant="quiet" onClick={onDismiss} />
      )}
    </div>
  );
}
