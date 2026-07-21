import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Grid } from "./Grid";

describe("Grid", () => {
  it("defaults to 12 columns via a CSS custom property", () => {
    renderWithProviders(<Grid data-testid="grid">content</Grid>);
    const el = screen.getByTestId("grid");
    expect(el.style.getPropertyValue("--grid-cols-base")).toBe("12");
    expect(el.className).toContain("grid-cols-[repeat(var(--grid-cols-base),minmax(0,1fr))]");
  });

  it("accepts a fixed column count", () => {
    renderWithProviders(
      <Grid cols={4} data-testid="grid">
        content
      </Grid>,
    );
    expect(screen.getByTestId("grid").style.getPropertyValue("--grid-cols-base")).toBe("4");
  });

  it("wires the 4/8/12 responsive band via per-breakpoint custom properties", () => {
    renderWithProviders(
      <Grid cols={{ base: 4, md: 8, lg: 12 }} data-testid="grid">
        content
      </Grid>,
    );
    const el = screen.getByTestId("grid");
    expect(el.style.getPropertyValue("--grid-cols-base")).toBe("4");
    expect(el.style.getPropertyValue("--grid-cols-md")).toBe("8");
    expect(el.style.getPropertyValue("--grid-cols-lg")).toBe("12");
    expect(el.className).toContain("md:grid-cols-[repeat(var(--grid-cols-md),minmax(0,1fr))]");
    expect(el.className).toContain("lg:grid-cols-[repeat(var(--grid-cols-lg),minmax(0,1fr))]");
  });
});
