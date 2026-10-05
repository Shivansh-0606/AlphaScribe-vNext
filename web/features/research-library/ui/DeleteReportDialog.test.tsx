import { axe } from "jest-axe";
import { useState } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AppError } from "@/lib/errors/app-error";
import { renderWithProviders, screen, waitFor, within } from "@/tests/setup/render";
import type { ReportListItem } from "../integration/schemas";
import { REPORT_DELETE_COPY as copy } from "./copy";
import { DeleteReportDialog } from "./DeleteReportDialog";

const deleteReport = vi.fn();
vi.mock("../integration/api", () => ({
  deleteReport: (...args: unknown[]) => deleteReport(...args),
}));

const toastSuccess = vi.fn();
const toastInfo = vi.fn();
vi.mock("sonner", () => ({
  toast: {
    success: (...args: unknown[]) => toastSuccess(...args),
    info: (...args: unknown[]) => toastInfo(...args),
  },
}));

const REPORT: ReportListItem = {
  id: "r1",
  ticker: "AAPL",
  query: "Key risks?",
  created_at: "2026-01-01T00:00:00Z",
};

const onClose = vi.fn();
const onDeleted = vi.fn();

/** Stands in for the row's menu trigger: the element Cancel/Esc must return focus to. */
function Harness() {
  const [trigger, setTrigger] = useState<HTMLButtonElement | null>(null);
  const [open, setOpen] = useState(true);
  return (
    <>
      <button ref={setTrigger}>row menu trigger</button>
      {open && trigger && (
        <DeleteReportDialog
          report={REPORT}
          returnFocusTo={trigger}
          onClose={() => {
            setOpen(false);
            onClose();
          }}
          onDeleted={onDeleted}
        />
      )}
    </>
  );
}

const openDialog = () => screen.findByRole("dialog", { name: copy.dialogTitle });
const confirmButton = () => screen.getByRole("button", { name: copy.confirmButton });
const cancelButton = () => screen.getByRole("button", { name: copy.cancelButton });
const rowTrigger = () => screen.getByRole("button", { name: "row menu trigger" });

describe("DeleteReportDialog", () => {
  beforeEach(() => {
    deleteReport.mockReset();
    toastSuccess.mockClear();
    toastInfo.mockClear();
    onClose.mockClear();
    onDeleted.mockClear();
  });

  describe("Confirming", () => {
    it("names the report and states the consequence (through the copy constants), and moves focus into the dialog", async () => {
      renderWithProviders(<Harness />);
      const dialog = await openDialog();

      expect(within(dialog).getByText(copy.dialogBody(REPORT))).toBeInTheDocument();
      expect(within(dialog).getByRole("button", { name: copy.confirmButton })).toBeInTheDocument();
      expect(within(dialog).getByRole("button", { name: copy.cancelButton })).toBeInTheDocument();
      expect(dialog.contains(document.activeElement)).toBe(true);
      expect(deleteReport).not.toHaveBeenCalled();
    });

    it("Cancel closes without deleting and returns focus to the row's menu trigger", async () => {
      const { user } = renderWithProviders(<Harness />);
      await openDialog();

      await user.click(cancelButton());

      expect(onClose).toHaveBeenCalledOnce();
      expect(deleteReport).not.toHaveBeenCalled();
      await waitFor(() => expect(rowTrigger()).toHaveFocus());
    });

    it("Escape is the same safe exit as Cancel", async () => {
      const { user } = renderWithProviders(<Harness />);
      await openDialog();

      await user.keyboard("{Escape}");

      expect(onClose).toHaveBeenCalledOnce();
      expect(deleteReport).not.toHaveBeenCalled();
      await waitFor(() => expect(rowTrigger()).toHaveFocus());
    });
  });

  describe("Deleting", () => {
    it("shows the pending state, disables Cancel, and can't be dismissed into an ambiguous state", async () => {
      let resolveDelete: (value: { deleted: string }) => void = () => {};
      deleteReport.mockReturnValueOnce(
        new Promise((resolve) => {
          resolveDelete = resolve;
        }),
      );
      const { user } = renderWithProviders(<Harness />);
      await openDialog();

      const confirm = confirmButton();
      await user.click(confirm);

      await waitFor(() => expect(confirm).toHaveAttribute("aria-busy", "true"));
      expect(cancelButton()).toBeDisabled();
      await user.keyboard("{Escape}");
      expect(onClose).not.toHaveBeenCalled();
      expect(screen.getByRole("dialog")).toBeInTheDocument();

      resolveDelete({ deleted: "r1" });
      await waitFor(() => expect(onClose).toHaveBeenCalledOnce());
    });
  });

  describe("Deleted", () => {
    it("deletes that report, closes, confirms with a toast, and hands focus placement to the caller", async () => {
      deleteReport.mockResolvedValueOnce({ deleted: "r1" });
      const { user } = renderWithProviders(<Harness />);
      await openDialog();

      await user.click(confirmButton());

      await waitFor(() => expect(onClose).toHaveBeenCalledOnce());
      expect(deleteReport).toHaveBeenCalledWith("r1");
      expect(toastSuccess).toHaveBeenCalledWith(copy.deleted);
      expect(toastInfo).not.toHaveBeenCalled();
      await waitFor(() => expect(onDeleted).toHaveBeenCalledOnce());
      // The row (and its trigger) are gone in real use — focus is NOT pulled back to the trigger.
      expect(rowTrigger()).not.toHaveFocus();
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    });

    it("treats a 404 as 'already gone' (Q7): closes with the neutral message, not an error", async () => {
      deleteReport.mockRejectedValueOnce(
        new AppError("unknown", "report not found", { status: 404 }),
      );
      const { user } = renderWithProviders(<Harness />);
      await openDialog();

      await user.click(confirmButton());

      await waitFor(() => expect(onClose).toHaveBeenCalledOnce());
      expect(toastInfo).toHaveBeenCalledWith(copy.alreadyGone);
      expect(toastSuccess).not.toHaveBeenCalled();
      await waitFor(() => expect(onDeleted).toHaveBeenCalledOnce());
      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });
  });

  describe("Failed", () => {
    it.each([
      ["network", new AppError("network", "Unable to reach the server.")],
      ["server (5xx)", new AppError("server", "Server error.", { status: 500 })],
      [
        "auth_required (401)",
        new AppError("auth_required", "Authentication required.", { status: 401 }),
      ],
      [
        "validation",
        new AppError("validation", "Response failed validation at the trust boundary."),
      ],
    ])(
      "on a %s failure: the error shows inline INSIDE the dialog, which stays open, keeps focus, and tells the caller nothing happened",
      async (_label, error) => {
        deleteReport.mockRejectedValueOnce(error);
        const { user } = renderWithProviders(<Harness />);
        const dialog = await openDialog();

        await user.click(confirmButton());

        const alert = await within(dialog).findByRole("alert");
        expect(alert).toHaveTextContent(copy.failure);
        expect(onClose).not.toHaveBeenCalled();
        expect(onDeleted).not.toHaveBeenCalled();
        expect(toastSuccess).not.toHaveBeenCalled();
        expect(toastInfo).not.toHaveBeenCalled();
        expect(screen.getByRole("dialog")).toBeInTheDocument();
        await waitFor(() => expect(dialog.contains(document.activeElement)).toBe(true));
      },
    );

    it("lets the user retry after a failure, and then succeeds", async () => {
      deleteReport
        .mockRejectedValueOnce(new AppError("server", "Server error.", { status: 500 }))
        .mockResolvedValueOnce({ deleted: "r1" });
      const { user } = renderWithProviders(<Harness />);
      const dialog = await openDialog();

      await user.click(confirmButton());
      await within(dialog).findByRole("alert");
      await user.click(confirmButton());

      await waitFor(() => expect(onClose).toHaveBeenCalledOnce());
      expect(deleteReport).toHaveBeenCalledTimes(2);
      expect(toastSuccess).toHaveBeenCalledWith(copy.deleted);
    });
  });

  it("has no detectable accessibility violations", async () => {
    renderWithProviders(<Harness />);
    await openDialog();
    expect(await axe(document.body)).toHaveNoViolations();
  });
});
