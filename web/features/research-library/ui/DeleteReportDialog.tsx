"use client";

import { useEffect, useRef } from "react";
import { toast } from "sonner";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/foundation/Dialog";
import { useDeleteReport } from "../application/useDeleteReport";
import type { ReportListItem } from "../integration/schemas";
import { REPORT_DELETE_COPY as copy } from "./copy";

/**
 * The confirm step for deleting one report (CR-SCOPE-004, brief §3.2/§3.8).
 * Rendered only while a delete is being considered, so mounting it is "open"
 * and unmounting it is "closed" — a fresh mutation per report, no stale error.
 *
 * Confirming → Deleting (button `loading`, dismissal blocked so the dialog
 * can't close into an ambiguous state) → Deleted (closes, toast) or Failed
 * (inline Banner INSIDE the dialog, which stays open and keeps focus; a toast
 * isn't reliable while a modal traps focus — same as `SettingsPanel`).
 *
 * Focus on close is set explicitly, because the dialog has no `DialogTrigger`
 * for Radix to return it to: Cancel/Esc return it to the row's menu trigger;
 * after a successful delete the row and its trigger are gone, so the caller
 * moves it to the list heading.
 */
export function DeleteReportDialog({
  report,
  returnFocusTo,
  onClose,
  onDeleted,
}: {
  report: ReportListItem;
  /** The row's menu trigger — where Cancel/Esc return focus. */
  returnFocusTo: HTMLElement | null;
  onClose: () => void;
  /** Called after a successful (or already-gone) delete, once the dialog has closed, to place focus. */
  onDeleted: () => void;
}) {
  const deleteReport = useDeleteReport();
  const removed = useRef(false);
  const confirmRef = useRef<HTMLButtonElement>(null);

  // The confirm button is disabled while the delete is pending, and a focused
  // element that gets disabled can lose focus (browser-dependent), which a
  // focus trap doesn't recover from. So once a failure has rendered, put focus
  // back on the retry action: it stays inside the dialog (§3.8).
  useEffect(() => {
    if (deleteReport.isError) confirmRef.current?.focus();
  }, [deleteReport.isError]);

  const confirm = () =>
    deleteReport.mutate(report.id, {
      onSuccess: (outcome) => {
        removed.current = true;
        onClose();
        if (outcome === "already_gone") toast.info(copy.alreadyGone);
        else toast.success(copy.deleted);
      },
    });

  return (
    <Dialog
      open
      onOpenChange={(open) => {
        if (!open && !deleteReport.isPending) onClose();
      }}
    >
      <DialogContent
        onCloseAutoFocus={(event) => {
          event.preventDefault();
          if (removed.current) onDeleted();
          else returnFocusTo?.focus();
        }}
      >
        <DialogHeader>
          <DialogTitle>{copy.dialogTitle}</DialogTitle>
          <DialogDescription>{copy.dialogBody(report)}</DialogDescription>
        </DialogHeader>
        {deleteReport.isError && <Banner tone="error">{copy.failure}</Banner>}
        <DialogFooter>
          <Button variant="secondary" onClick={onClose} disabled={deleteReport.isPending}>
            {copy.cancelButton}
          </Button>
          <Button
            ref={confirmRef}
            variant="destructive"
            onClick={confirm}
            loading={deleteReport.isPending}
          >
            {copy.confirmButton}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
