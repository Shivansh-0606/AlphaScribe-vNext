import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Badge } from "./Badge";

describe("Badge", () => {
  it("renders its label as real text, never color-only", () => {
    renderWithProviders(<Badge variant="bearish">Bearish</Badge>);
    expect(screen.getByText("Bearish")).toBeInTheDocument();
  });

  it("defaults to the neutral variant", () => {
    renderWithProviders(<Badge>Draft</Badge>);
    expect(screen.getByText("Draft")).toHaveClass("bg-muted");
  });

  it("applies the requested variant's fill, cancelling the primitive default", () => {
    renderWithProviders(<Badge variant="bullish">Bullish</Badge>);
    const badge = screen.getByText("Bullish");
    expect(badge).toHaveClass("bg-bullish/15");
    expect(badge.classList.contains("bg-primary")).toBe(false);
  });

  it("has no detectable accessibility violations across variants", async () => {
    const { container } = renderWithProviders(
      <div>
        <Badge variant="neutral">Draft</Badge>
        <Badge variant="bullish">Bullish</Badge>
        <Badge variant="bearish">Bearish</Badge>
        <Badge variant="warning">Not comparable</Badge>
        <Badge variant="verified">Verified</Badge>
        <Badge variant="count" aria-label="3 unread">
          3
        </Badge>
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
