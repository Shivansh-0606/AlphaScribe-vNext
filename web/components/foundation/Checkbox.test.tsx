import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Checkbox } from "./Checkbox";

describe("Checkbox", () => {
  it("renders a native-semantics checkbox with a clickable label", async () => {
    const onCheckedChange = vi.fn();
    const { user } = renderWithProviders(
      <Checkbox label="Remember me" onCheckedChange={onCheckedChange} />,
    );
    await user.click(screen.getByText("Remember me"));
    expect(onCheckedChange).toHaveBeenCalledWith(true);
  });

  it("reflects the indeterminate state via aria-checked=mixed", () => {
    renderWithProviders(<Checkbox label="Select all" checked="indeterminate" />);
    expect(screen.getByRole("checkbox", { name: "Select all" })).toHaveAttribute(
      "aria-checked",
      "mixed",
    );
  });

  it("has no detectable accessibility violations across states", async () => {
    const { container } = renderWithProviders(
      <div>
        <Checkbox label="Unchecked" />
        <Checkbox label="Checked" checked />
        <Checkbox label="Indeterminate" checked="indeterminate" />
        <Checkbox label="Disabled" disabled />
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
