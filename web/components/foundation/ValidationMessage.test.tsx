import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { ValidationMessage } from "./ValidationMessage";

describe("ValidationMessage", () => {
  it("renders as an alert so it's announced when it appears", () => {
    renderWithProviders(<ValidationMessage>Select at least one option.</ValidationMessage>);
    expect(screen.getByRole("alert")).toHaveTextContent("Select at least one option.");
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<ValidationMessage>Error text</ValidationMessage>);
    expect(await axe(container)).toHaveNoViolations();
  });
});
