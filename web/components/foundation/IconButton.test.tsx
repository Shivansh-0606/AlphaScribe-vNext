import { Star } from "@phosphor-icons/react/dist/ssr";
import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { IconButton } from "./IconButton";

describe("IconButton", () => {
  it("requires and exposes an accessible name via the mandatory label prop", () => {
    renderWithProviders(<IconButton label="Add to watchlist" icon={<Star />} />);
    expect(screen.getByRole("button", { name: "Add to watchlist" })).toBeInTheDocument();
  });

  it("hides the glyph from assistive tech (the name comes from the label, not the icon)", () => {
    renderWithProviders(<IconButton label="Close" icon={<Star data-testid="glyph" />} />);
    const glyph = screen.getByTestId("glyph");
    expect(glyph.closest("[aria-hidden='true']")).not.toBeNull();
  });

  it("reflects toggle state via aria-pressed", () => {
    const { rerender } = renderWithProviders(
      <IconButton label="Add to watchlist" icon={<Star />} pressed={false} />,
    );
    expect(screen.getByRole("button")).toHaveAttribute("aria-pressed", "false");
    rerender(<IconButton label="Remove from watchlist" icon={<Star />} pressed={true} />);
    expect(screen.getByRole("button", { name: "Remove from watchlist" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  it("fires onClick when activated and not while loading", async () => {
    const onClick = vi.fn();
    const { user, rerender } = renderWithProviders(
      <IconButton label="Send" icon={<Star />} onClick={onClick} />,
    );
    await user.click(screen.getByRole("button", { name: "Send" }));
    expect(onClick).toHaveBeenCalledOnce();

    rerender(<IconButton label="Send" icon={<Star />} onClick={onClick} loading />);
    const button = screen.getByRole("button", { name: "Send" });
    expect(button).toHaveAttribute("aria-busy", "true");
    expect(button).toBeDisabled();
  });

  it("quiet variant has no fill class (jsdom can't compute real CSS — see tests/e2e/component-fixtures.spec.ts for the actual rendered-background regression check)", () => {
    renderWithProviders(<IconButton label="Quiet" icon={<Star />} variant="quiet" />);
    expect(screen.getByRole("button", { name: "Quiet" }).className).toContain("bg-transparent");
  });

  it("has no detectable accessibility violations across variants", async () => {
    const { container } = renderWithProviders(
      <div>
        <IconButton label="Quiet" icon={<Star />} variant="quiet" />
        <IconButton label="Secondary" icon={<Star />} variant="secondary" />
        <IconButton label="Primary" icon={<Star />} variant="primary" />
        <IconButton label="Destructive" icon={<Star />} variant="destructive" />
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
