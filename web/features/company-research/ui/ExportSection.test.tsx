import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { ExportSection } from "./ExportSection";

describe("ExportSection", () => {
  it("explains export happens via Report View, not a duplicate implementation here, when no report exists yet", () => {
    renderWithProviders(<ExportSection />);
    expect(screen.getByText(/Report View in Research Library/)).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Open Report View" })).not.toBeInTheDocument();
  });

  it("links directly to Report View once a report has been generated this run", () => {
    renderWithProviders(<ExportSection reportId="report-1" />);
    expect(screen.getByRole("link", { name: "Open Report View" })).toHaveAttribute(
      "href",
      "/reports/report-1",
    );
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<ExportSection />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
