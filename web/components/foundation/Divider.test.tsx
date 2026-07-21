import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Divider } from "./Divider";

describe("Divider", () => {
  it("renders a decorative horizontal separator by default", () => {
    renderWithProviders(<Divider data-testid="divider" />);
    const el = screen.getByTestId("divider");
    expect(el).toHaveAttribute("data-orientation", "horizontal");
    // Decorative separators are role="none" per the ARIA spec, not "separator".
    expect(el).not.toHaveAttribute("role", "separator");
  });

  it("supports the vertical orientation", () => {
    renderWithProviders(<Divider orientation="vertical" data-testid="divider" />);
    expect(screen.getByTestId("divider")).toHaveAttribute("data-orientation", "vertical");
  });
});
