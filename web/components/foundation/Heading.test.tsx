import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Heading } from "./Heading";

describe("Heading", () => {
  it("defaults to an h1", () => {
    renderWithProviders(<Heading>Page title</Heading>);
    expect(screen.getByRole("heading", { level: 1, name: "Page title" })).toBeInTheDocument();
  });

  it("renders the matching element for each level", () => {
    const { rerender } = renderWithProviders(<Heading level="h2">Section</Heading>);
    expect(screen.getByRole("heading", { level: 2 })).toBeInTheDocument();
    rerender(<Heading level="h3">Subsection</Heading>);
    expect(screen.getByRole("heading", { level: 3 })).toBeInTheDocument();
  });

  it("allows visual level to differ from semantic element via `as`", () => {
    renderWithProviders(
      <Heading level="h2" as="h1">
        Visually h2, semantically h1
      </Heading>,
    );
    expect(screen.getByRole("heading", { level: 1 })).toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<Heading>Page title</Heading>);
    expect(await axe(container)).toHaveNoViolations();
  });
});
