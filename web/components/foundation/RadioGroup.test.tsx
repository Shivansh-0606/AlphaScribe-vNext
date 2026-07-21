import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { RadioGroup, RadioGroupItem } from "./RadioGroup";

describe("RadioGroup", () => {
  it("groups options under a visible legend naming the group", () => {
    renderWithProviders(
      <RadioGroup label="AI access mode" defaultValue="managed">
        <RadioGroupItem value="managed" label="Managed" />
        <RadioGroupItem value="byok" label="Bring your own key" />
      </RadioGroup>,
    );
    expect(screen.getByRole("group", { name: "AI access mode" })).toBeInTheDocument();
  });

  it("arrow keys move focus within the group (native Radix roving-tabindex model)", async () => {
    // Full arrow-key-selects behavior (Radix's documented roving-focus model)
    // is verified against a real browser in
    // tests/e2e/component-fixtures.spec.ts — jsdom's Pointer/Focus Events
    // fidelity isn't reliable enough here to assert selection, only focus
    // movement (05.1 AD-3 — test at the right boundary).
    const { user } = renderWithProviders(
      <RadioGroup label="AI access mode" defaultValue="managed">
        <RadioGroupItem value="managed" label="Managed" />
        <RadioGroupItem value="byok" label="Bring your own key" />
      </RadioGroup>,
    );
    await user.click(screen.getByRole("radio", { name: "Managed" }));
    await user.keyboard("{ArrowDown}");
    expect(screen.getByRole("radio", { name: "Bring your own key" })).toHaveFocus();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <RadioGroup label="AI access mode" defaultValue="managed">
        <RadioGroupItem value="managed" label="Managed" />
        <RadioGroupItem value="byok" label="Bring your own key" />
      </RadioGroup>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
