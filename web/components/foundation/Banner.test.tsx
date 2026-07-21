import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Banner } from "./Banner";

describe("Banner", () => {
  it("uses role=status for info/success (polite)", () => {
    renderWithProviders(<Banner tone="info">{"You're viewing cached data."}</Banner>);
    expect(screen.getByRole("status")).toHaveTextContent("You're viewing cached data.");
  });

  it("uses role=alert for warning/error (assertive)", () => {
    renderWithProviders(<Banner tone="error">Failed to load filings.</Banner>);
    expect(screen.getByRole("alert")).toHaveTextContent("Failed to load filings.");
  });

  it("renders an optional title above the message", () => {
    renderWithProviders(
      <Banner tone="warning" title="Partial data">
        Some figures are unavailable.
      </Banner>,
    );
    expect(screen.getByText("Partial data")).toBeInTheDocument();
  });

  it("gives the dismiss control its own accessible name", async () => {
    const onDismiss = vi.fn();
    const { user } = renderWithProviders(
      <Banner tone="info" onDismiss={onDismiss}>
        Message
      </Banner>,
    );
    await user.click(screen.getByRole("button", { name: "Dismiss" }));
    expect(onDismiss).toHaveBeenCalled();
  });

  it("has no detectable accessibility violations across tones", async () => {
    const { container } = renderWithProviders(
      <div>
        <Banner tone="info">Info</Banner>
        <Banner tone="success">Success</Banner>
        <Banner tone="warning">Warning</Banner>
        <Banner tone="error">Error</Banner>
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
