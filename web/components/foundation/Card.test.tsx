import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Card, CardContent, CardHeader, CardTitle } from "./Card";

describe("Card", () => {
  it("renders flat at rest — no shadow, no leaked shadcn radius", () => {
    renderWithProviders(<Card data-testid="card">Content</Card>);
    const card = screen.getByTestId("card");
    expect(card).toHaveClass("shadow-none");
    expect(card).toHaveClass("rounded-md");
    expect(card.className).not.toContain("rounded-xl");
  });

  it("composes the actual focusable control via asChild for an interactive card", () => {
    renderWithProviders(
      <Card asChild variant="interactive">
        <a href="/companies/reliance">Reliance Industries</a>
      </Card>,
    );
    expect(screen.getByRole("link", { name: "Reliance Industries" })).toBeInTheDocument();
  });

  it("reflects the selected state via data-selected, not color alone", () => {
    renderWithProviders(
      <Card variant="selectable" selected data-testid="card">
        Option A
      </Card>,
    );
    expect(screen.getByTestId("card")).toHaveAttribute("data-selected", "true");
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <Card>
        <CardHeader>
          <CardTitle>Reliance Industries</CardTitle>
        </CardHeader>
        <CardContent>Summary text.</CardContent>
      </Card>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
