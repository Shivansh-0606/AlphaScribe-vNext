import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Textarea } from "./Textarea";

describe("Textarea", () => {
  it("renders as a native multi-line textbox", () => {
    renderWithProviders(<Textarea aria-label="Notes" />);
    expect(screen.getByRole("textbox", { name: "Notes" }).tagName).toBe("TEXTAREA");
  });

  it("shows a counter that warns near the limit without truncating", () => {
    renderWithProviders(
      <Textarea
        aria-label="Notes"
        maxLength={10}
        value="123456789"
        showCounter
        onChange={() => {}}
      />,
    );
    const counter = screen.getByText("9/10");
    expect(counter).toHaveClass("text-warning");
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<Textarea aria-label="Notes" />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
