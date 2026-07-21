import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Flex } from "./Flex";

describe("Flex", () => {
  it("defaults to a row with no gap", () => {
    renderWithProviders(<Flex data-testid="flex">content</Flex>);
    const el = screen.getByTestId("flex");
    expect(el).toHaveClass("flex", "flex-row", "gap-0");
  });

  it("maps a gap step to the matching Tailwind gap utility", () => {
    renderWithProviders(
      <Flex gap={6} data-testid="flex">
        content
      </Flex>,
    );
    expect(screen.getByTestId("flex")).toHaveClass("gap-8");
  });

  it("applies direction, align, and justify", () => {
    renderWithProviders(
      <Flex direction="col" align="center" justify="between" data-testid="flex">
        content
      </Flex>,
    );
    expect(screen.getByTestId("flex")).toHaveClass("flex-col", "items-center", "justify-between");
  });

  it("renders as a different element via `as`", () => {
    renderWithProviders(
      <Flex as="section" data-testid="flex">
        content
      </Flex>,
    );
    expect(screen.getByTestId("flex").tagName).toBe("SECTION");
  });
});
