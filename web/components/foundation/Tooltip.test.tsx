import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Tooltip } from "./Tooltip";

describe("Tooltip", () => {
  it("reveals its content when the trigger receives keyboard focus", async () => {
    const { user } = renderWithProviders(
      <Tooltip content="Net income after tax">
        <button type="button">P/E ratio</button>
      </Tooltip>,
    );
    await user.tab();
    expect(await screen.findByRole("tooltip")).toHaveTextContent("Net income after tax");
  });

  it("composes the child as the real trigger via asChild, not a wrapper element", () => {
    renderWithProviders(
      <Tooltip content="Hint">
        <button type="button">Trigger</button>
      </Tooltip>,
    );
    expect(screen.getByRole("button", { name: "Trigger" })).toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <Tooltip content="Net income after tax">
        <button type="button">P/E ratio</button>
      </Tooltip>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
