import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Progress } from "./Progress";

describe("Progress", () => {
  it("exposes a determinate value via aria-valuenow", () => {
    renderWithProviders(<Progress label="Export progress" value={40} />);
    const bar = screen.getByRole("progressbar", { name: "Export progress" });
    expect(bar).toHaveAttribute("aria-valuenow", "40");
  });

  it("omits aria-valuenow when indeterminate", () => {
    renderWithProviders(<Progress label="Loading filings" />);
    const bar = screen.getByRole("progressbar", { name: "Loading filings" });
    expect(bar).not.toHaveAttribute("aria-valuenow");
  });

  it("has no detectable accessibility violations for determinate and indeterminate", async () => {
    const { container } = renderWithProviders(
      <div>
        <Progress label="Export progress" value={40} />
        <Progress label="Loading filings" />
        <Progress label="AI analysis" value={70} tone="brand" />
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
