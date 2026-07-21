import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Input } from "./Input";

describe("Input", () => {
  it("renders as a native text input", () => {
    renderWithProviders(<Input aria-label="Company name" />);
    expect(screen.getByRole("textbox", { name: "Company name" })).toBeInTheDocument();
  });

  it("password type starts masked, and the mandatory reveal toggle switches it to text", async () => {
    const { user } = renderWithProviders(<Input type="password" aria-label="Password" />);
    const input = screen.getByLabelText("Password");
    expect(input).toHaveAttribute("type", "password");

    const toggle = screen.getByRole("button", { name: "Show password" });
    await user.click(toggle);
    expect(input).toHaveAttribute("type", "text");
    expect(screen.getByRole("button", { name: "Hide password" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  it("has no detectable accessibility violations across configurations", async () => {
    const { container } = renderWithProviders(
      <div>
        <Input aria-label="Text" />
        <Input type="password" aria-label="Password" />
        <Input aria-label="Disabled" disabled />
        <Input aria-label="Invalid" aria-invalid />
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
