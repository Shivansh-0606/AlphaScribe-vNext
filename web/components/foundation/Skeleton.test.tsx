import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Skeleton, SkeletonGroup, SkeletonText } from "./Skeleton";

describe("Skeleton", () => {
  it("is hidden from assistive tech — never read as real data", () => {
    renderWithProviders(<Skeleton data-testid="skeleton" />);
    expect(screen.getByTestId("skeleton")).toHaveAttribute("aria-hidden", "true");
  });

  it("SkeletonText renders the requested number of lines, the last one shorter", () => {
    const { container } = renderWithProviders(<SkeletonText lines={3} />);
    const lines = container.querySelectorAll('[data-slot="foundation-skeleton"]');
    expect(lines).toHaveLength(3);
    expect(lines[2]).toHaveClass("w-2/3");
    expect(lines[0]).toHaveClass("w-full");
  });

  it("SkeletonGroup announces a single loading status for the whole region", () => {
    renderWithProviders(
      <SkeletonGroup label="Loading company summary">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-full" />
      </SkeletonGroup>,
    );
    expect(screen.getByRole("status")).toHaveTextContent("Loading company summary");
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <SkeletonGroup label="Loading">
        <SkeletonText lines={2} />
      </SkeletonGroup>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
