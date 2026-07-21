import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Avatar } from "./Avatar";

describe("Avatar", () => {
  it("uses the real name as the accessible name, not 'avatar'", () => {
    renderWithProviders(<Avatar name="Priya Sharma" />);
    expect(screen.getByRole("img", { name: "Priya Sharma" })).toBeInTheDocument();
  });

  it("derives initials from the first and last name", () => {
    renderWithProviders(<Avatar name="Priya Sharma" />);
    expect(screen.getByText("PS")).toBeInTheDocument();
  });

  it("gives the status dot a textual accessible name, not color alone", () => {
    renderWithProviders(<Avatar name="Priya Sharma" statusLabel="Online" />);
    expect(screen.getByRole("img", { name: "Online" })).toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <div>
        <Avatar name="Priya Sharma" size="sm" />
        <Avatar name="Amit Verma" size="md" statusLabel="Online" />
        <Avatar name="Reliance Industries" size="lg" />
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
