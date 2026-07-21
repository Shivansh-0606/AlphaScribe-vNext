import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Button } from "./Button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "./Dialog";

function DemoDialog({ onConfirm = vi.fn() }: { onConfirm?: () => void }) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Delete report</Button>
      </DialogTrigger>
      <DialogContent showCloseButton>
        <DialogHeader>
          <DialogTitle>Delete this report?</DialogTitle>
          <DialogDescription>This cannot be undone.</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="quiet">Cancel</Button>
          </DialogClose>
          <Button variant="destructive" onClick={onConfirm}>
            Delete
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

describe("Dialog", () => {
  it("opens on trigger click, labeled by its title and described by its body", async () => {
    const { user } = renderWithProviders(<DemoDialog />);
    await user.click(screen.getByRole("button", { name: "Delete report" }));
    const dialog = await screen.findByRole("dialog", { name: "Delete this report?" });
    expect(dialog).toHaveAccessibleDescription("This cannot be undone.");
  });

  it("closes and returns focus to the trigger on Cancel", async () => {
    const { user } = renderWithProviders(<DemoDialog />);
    const trigger = screen.getByRole("button", { name: "Delete report" });
    await user.click(trigger);
    await user.click(await screen.findByRole("button", { name: "Cancel" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(trigger).toHaveFocus();
  });

  it("closes on Escape", async () => {
    const { user } = renderWithProviders(<DemoDialog />);
    await user.click(screen.getByRole("button", { name: "Delete report" }));
    await screen.findByRole("dialog");
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("has no detectable accessibility violations when open", async () => {
    const { container, user } = renderWithProviders(<DemoDialog />);
    await user.click(screen.getByRole("button", { name: "Delete report" }));
    await screen.findByRole("dialog");
    expect(await axe(container)).toHaveNoViolations();
  });
});
