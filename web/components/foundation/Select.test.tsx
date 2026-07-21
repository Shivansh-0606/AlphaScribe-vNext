import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./Select";

function ExampleSelect({ onValueChange }: { onValueChange?: (v: string) => void }) {
  return (
    <Select onValueChange={onValueChange}>
      <SelectTrigger aria-label="Reporting period">
        <SelectValue placeholder="Select a period" />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="annual">Annual</SelectItem>
        <SelectItem value="quarterly">Quarterly</SelectItem>
      </SelectContent>
    </Select>
  );
}

describe("Select", () => {
  it("renders a labeled trigger showing the placeholder before selection", () => {
    renderWithProviders(<ExampleSelect />);
    expect(screen.getByRole("combobox", { name: "Reporting period" })).toHaveTextContent(
      "Select a period",
    );
  });

  it("opens the listbox and selects an option via keyboard", async () => {
    const onValueChange = vi.fn();
    const { user } = renderWithProviders(<ExampleSelect onValueChange={onValueChange} />);
    const trigger = screen.getByRole("combobox", { name: "Reporting period" });
    await user.click(trigger);
    const option = await screen.findByRole("option", { name: "Quarterly" });
    await user.click(option);
    expect(onValueChange).toHaveBeenCalledWith("quarterly");
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<ExampleSelect />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
