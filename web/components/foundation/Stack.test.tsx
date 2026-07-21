import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Stack } from "./Stack";

describe("Stack", () => {
  it("stacks vertically with the default space-4 gap", () => {
    renderWithProviders(<Stack data-testid="stack">content</Stack>);
    const el = screen.getByTestId("stack");
    expect(el).toHaveClass("flex-col", "gap-4");
  });

  it("accepts a custom gap step", () => {
    renderWithProviders(
      <Stack gap={2} data-testid="stack">
        content
      </Stack>,
    );
    expect(screen.getByTestId("stack")).toHaveClass("gap-2");
  });
});
