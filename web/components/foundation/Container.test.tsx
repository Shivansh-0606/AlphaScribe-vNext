import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Container } from "./Container";

describe("Container", () => {
  it("centers content within the max-content width", () => {
    renderWithProviders(<Container data-testid="container">content</Container>);
    expect(screen.getByTestId("container")).toHaveClass("mx-auto", "max-w-[1400px]");
  });

  it("constrains to the reading measure when reading=true", () => {
    renderWithProviders(
      <Container reading data-testid="container">
        content
      </Container>,
    );
    expect(screen.getByTestId("container")).toHaveClass("max-w-[72ch]");
  });
});
