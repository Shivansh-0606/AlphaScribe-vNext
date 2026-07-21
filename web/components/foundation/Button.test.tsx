import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Button } from "./Button";

describe("Button", () => {
  it("renders as a native button with the label as its accessible name", () => {
    renderWithProviders(<Button>Export report</Button>);
    expect(screen.getByRole("button", { name: "Export report" })).toBeInTheDocument();
  });

  it("fires onClick when activated", async () => {
    const onClick = vi.fn();
    const { user } = renderWithProviders(<Button onClick={onClick}>Save</Button>);
    await user.click(screen.getByRole("button", { name: "Save" }));
    expect(onClick).toHaveBeenCalledOnce();
  });

  it("keeps the label and sets aria-busy while loading, without becoming activatable", async () => {
    const onClick = vi.fn();
    const { user } = renderWithProviders(
      <Button loading onClick={onClick}>
        Save
      </Button>,
    );
    const button = screen.getByRole("button", { name: "Save" });
    expect(button).toHaveAttribute("aria-busy", "true");
    expect(button).toBeDisabled();
    await user.click(button);
    expect(onClick).not.toHaveBeenCalled();
  });

  it("marks disabled buttons as unavailable to assistive tech", () => {
    renderWithProviders(<Button disabled>Delete</Button>);
    const button = screen.getByRole("button", { name: "Delete" });
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute("aria-disabled", "true");
  });

  it("quiet variant has no fill class (jsdom can't compute real CSS — see tests/e2e/component-fixtures.spec.ts for the actual rendered-background regression check)", () => {
    renderWithProviders(<Button variant="quiet">Quiet</Button>);
    const button = screen.getByRole("button", { name: "Quiet" });
    expect(button.className).toContain("bg-transparent");
  });

  it("has no detectable accessibility violations across variants", async () => {
    const { container } = renderWithProviders(
      <div>
        <Button variant="primary">Primary</Button>
        <Button variant="secondary">Secondary</Button>
        <Button variant="quiet">Quiet</Button>
        <Button variant="destructive">Destructive</Button>
        <Button loading>Loading</Button>
        <Button disabled>Disabled</Button>
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
