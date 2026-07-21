import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Switch } from "./Switch";

describe("Switch", () => {
  it("renders the frozen role and reflects checked state", () => {
    renderWithProviders(<Switch label="Email notifications" checked onCheckedChange={() => {}} />);
    expect(screen.getByRole("switch", { name: "Email notifications" })).toBeChecked();
  });

  it("shows a textual On/Off state label by default (never color alone)", () => {
    const { rerender } = renderWithProviders(
      <Switch label="Email notifications" checked={false} onCheckedChange={() => {}} />,
    );
    expect(screen.getByText("Off")).toBeInTheDocument();
    rerender(<Switch label="Email notifications" checked onCheckedChange={() => {}} />);
    expect(screen.getByText("On")).toBeInTheDocument();
  });

  it("fires onCheckedChange when toggled", async () => {
    const onCheckedChange = vi.fn();
    const { user } = renderWithProviders(
      <Switch label="Email notifications" checked={false} onCheckedChange={onCheckedChange} />,
    );
    await user.click(screen.getByRole("switch"));
    expect(onCheckedChange).toHaveBeenCalledWith(true);
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <div>
        <Switch label="On" checked onCheckedChange={() => {}} />
        <Switch label="Off" checked={false} onCheckedChange={() => {}} />
        <Switch label="Disabled" disabled />
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
