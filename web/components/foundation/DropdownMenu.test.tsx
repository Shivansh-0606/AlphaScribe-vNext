import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Button } from "./Button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "./DropdownMenu";

function ExampleMenu({ onDelete }: { onDelete?: () => void }) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button>Actions</Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent>
        <DropdownMenuItem>Rename</DropdownMenuItem>
        <DropdownMenuItem variant="destructive" onSelect={onDelete}>
          Delete
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

describe("DropdownMenu", () => {
  it("opens the menu from its trigger and lists actions", async () => {
    const { user } = renderWithProviders(<ExampleMenu />);
    await user.click(screen.getByRole("button", { name: "Actions" }));
    expect(await screen.findByRole("menuitem", { name: "Rename" })).toBeInTheDocument();
  });

  it("activating an item fires its handler", async () => {
    const onDelete = vi.fn();
    const { user } = renderWithProviders(<ExampleMenu onDelete={onDelete} />);
    await user.click(screen.getByRole("button", { name: "Actions" }));
    await user.click(await screen.findByRole("menuitem", { name: "Delete" }));
    expect(onDelete).toHaveBeenCalledOnce();
  });

  it("returns focus to the trigger when closed with Escape", async () => {
    const { user } = renderWithProviders(<ExampleMenu />);
    const trigger = screen.getByRole("button", { name: "Actions" });
    await user.click(trigger);
    await screen.findByRole("menuitem", { name: "Rename" });
    await user.keyboard("{Escape}");
    expect(trigger).toHaveFocus();
  });

  it("has no detectable accessibility violations while open", async () => {
    const { container, user } = renderWithProviders(<ExampleMenu />);
    await user.click(screen.getByRole("button", { name: "Actions" }));
    await screen.findByRole("menuitem", { name: "Rename" });
    expect(await axe(container)).toHaveNoViolations();
  });
});
