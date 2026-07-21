import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { FormField } from "./FormField";
import { Input } from "./Input";

describe("FormField", () => {
  it("associates the label with the control via a shared id", () => {
    renderWithProviders(
      <FormField label="Email">
        <Input type="email" />
      </FormField>,
    );
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
  });

  it("wires help text via aria-describedby when no error is present", () => {
    renderWithProviders(
      <FormField label="Email" helpText="We'll never share this.">
        <Input type="email" />
      </FormField>,
    );
    const input = screen.getByLabelText("Email");
    const describedBy = input.getAttribute("aria-describedby");
    expect(describedBy).toBeTruthy();
    expect(document.getElementById(describedBy!)).toHaveTextContent("We'll never share this.");
  });

  it("wires the error message via aria-describedby and sets aria-invalid, preferring error over help text", () => {
    renderWithProviders(
      <FormField label="Email" helpText="An example." error="Enter a valid email.">
        <Input type="email" />
      </FormField>,
    );
    const input = screen.getByLabelText("Email");
    expect(input).toHaveAttribute("aria-invalid", "true");
    const describedBy = input.getAttribute("aria-describedby");
    expect(document.getElementById(describedBy!)).toHaveTextContent("Enter a valid email.");
    expect(screen.queryByText("An example.")).not.toBeInTheDocument();
  });

  it("reserves space for help/error even when neither is present (no layout shift)", () => {
    renderWithProviders(
      <FormField label="Email">
        <Input type="email" />
      </FormField>,
    );
    // The reserved region exists structurally even with nothing to show.
    const label = screen.getByText("Email");
    const container = label.parentElement!;
    expect(container.querySelector(".min-h-4")).not.toBeNull();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <FormField label="Email" error="Enter a valid email." required>
        <Input type="email" />
      </FormField>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
