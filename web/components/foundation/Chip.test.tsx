import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Chip } from "./Chip";

describe("Chip", () => {
  it("renders a filter chip as a toggle button reflecting aria-pressed", async () => {
    const onClick = vi.fn();
    const { user } = renderWithProviders(
      <Chip variant="filter" selected onClick={onClick}>
        Technology
      </Chip>,
    );
    const chip = screen.getByRole("button", { name: "Technology" });
    expect(chip).toHaveAttribute("aria-pressed", "true");
    await user.click(chip);
    expect(onClick).toHaveBeenCalled();
  });

  it("renders a static chip as non-interactive", () => {
    renderWithProviders(<Chip variant="static">12 results</Chip>);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(screen.getByText("12 results")).toBeInTheDocument();
  });

  it("gives the remove control its own accessible name, separate from the chip", async () => {
    const onRemove = vi.fn();
    const { user } = renderWithProviders(
      <Chip variant="removable" onRemove={onRemove}>
        Reliance Industries
      </Chip>,
    );
    const removeButton = screen.getByRole("button", { name: "Remove Reliance Industries" });
    await user.click(removeButton);
    expect(onRemove).toHaveBeenCalled();
  });

  it("has no detectable accessibility violations across variants", async () => {
    const { container } = renderWithProviders(
      <div>
        <Chip variant="filter">Filter</Chip>
        <Chip variant="choice">Choice</Chip>
        <Chip variant="removable" onRemove={() => {}}>
          Removable
        </Chip>
        <Chip variant="static">Static</Chip>
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
