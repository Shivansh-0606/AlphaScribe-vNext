import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Popover, PopoverContent, PopoverTrigger } from "./Popover";

describe("Popover", () => {
  it("opens the panel when the trigger is clicked", async () => {
    const { user } = renderWithProviders(
      <Popover>
        <PopoverTrigger>Filters</PopoverTrigger>
        <PopoverContent>Filter options</PopoverContent>
      </Popover>,
    );
    await user.click(screen.getByRole("button", { name: "Filters" }));
    expect(await screen.findByText("Filter options")).toBeInTheDocument();
  });

  it("has no detectable accessibility violations when open", async () => {
    const { container } = renderWithProviders(
      <Popover defaultOpen>
        <PopoverTrigger>Filters</PopoverTrigger>
        <PopoverContent>Filter options</PopoverContent>
      </Popover>,
    );
    await screen.findByText("Filter options");
    expect(await axe(container)).toHaveNoViolations();
  });
});
