import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Loader } from "./Loader";

describe("Loader", () => {
  it("announces a readable label via role=status, not aria-label alone", () => {
    renderWithProviders(<Loader label="Loading company summary" />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading company summary");
  });

  it("defaults to a generic label", () => {
    renderWithProviders(<Loader />);
    expect(screen.getByRole("status")).toHaveTextContent("Loading…");
  });

  it("fullView renders fixed and centered over the viewport", () => {
    renderWithProviders(<Loader fullView data-testid="loader" />);
    expect(screen.getByTestId("loader")).toHaveClass("fixed", "inset-0");
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<Loader label="Loading" />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
