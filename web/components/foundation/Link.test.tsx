import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Link } from "./Link";

describe("Link", () => {
  it("renders an internal path as a same-tab link with no target override", () => {
    renderWithProviders(<Link href="/research">Research</Link>);
    const link = screen.getByRole("link", { name: "Research" });
    expect(link).toHaveAttribute("href", "/research");
    expect(link).not.toHaveAttribute("target");
  });

  it("renders an external URL with target=_blank, rel=noopener noreferrer, and an accessible new-tab notice", () => {
    renderWithProviders(<Link href="https://sec.gov/filing">Filing</Link>);
    const link = screen.getByRole("link", { name: "Filing (opens in new tab)" });
    expect(link).toHaveAttribute("target", "_blank");
    expect(link).toHaveAttribute("rel", "noopener noreferrer");
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <div>
        <Link href="/internal">Internal</Link>
        <Link href="https://example.com">External</Link>
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
