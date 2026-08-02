import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { SourceReference } from "./SourceReference";

describe("SourceReference", () => {
  it("names the target descriptively — never bare 'source'/'click here' (Law 3)", () => {
    renderWithProviders(
      <ol>
        <SourceReference index={1} source="10-Q FY24 Q3" excerpt="Revenue grew 12%." />
      </ol>,
    );
    expect(screen.getByRole("button", { name: "[1] 10-Q FY24 Q3" })).toBeInTheDocument();
  });

  it("sets the id anchor the inline [n] citation markers target", () => {
    renderWithProviders(
      <ol>
        <SourceReference index={2} source="10-K FY24" excerpt="…" />
      </ol>,
    );
    expect(document.getElementById("source-2")).toBeInTheDocument();
  });

  it("opens a Source Preview with the cited excerpt on click, without navigating away", async () => {
    const { user } = renderWithProviders(
      <ol>
        <SourceReference
          index={1}
          source="10-Q FY24 Q3"
          excerpt="Revenue grew 12% year over year."
        />
      </ol>,
    );
    await user.click(screen.getByRole("button", { name: "[1] 10-Q FY24 Q3" }));
    expect(await screen.findByText("Revenue grew 12% year over year.")).toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <ol>
        <SourceReference index={1} source="10-Q FY24 Q3" excerpt="Revenue grew 12%." />
      </ol>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
