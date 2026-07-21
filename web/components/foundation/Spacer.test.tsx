import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Spacer } from "./Spacer";

describe("Spacer", () => {
  it("defaults to a vertical space-4 gap and is hidden from assistive tech", () => {
    renderWithProviders(<Spacer data-testid="spacer" />);
    const el = screen.getByTestId("spacer");
    expect(el).toHaveClass("h-4");
    expect(el).toHaveAttribute("aria-hidden", "true");
  });

  it("switches to width on the horizontal axis", () => {
    renderWithProviders(<Spacer axis="horizontal" size={6} data-testid="spacer" />);
    expect(screen.getByTestId("spacer")).toHaveClass("w-8");
  });
});
