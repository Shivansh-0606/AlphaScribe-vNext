import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import Home from "./page";

describe("Home", () => {
  it("renders exactly one heading naming the product", () => {
    renderWithProviders(<Home />);
    const headings = screen.getAllByRole("heading");
    expect(headings).toHaveLength(1);
    expect(headings[0]).toHaveTextContent("AlphaScribe");
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<Home />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
