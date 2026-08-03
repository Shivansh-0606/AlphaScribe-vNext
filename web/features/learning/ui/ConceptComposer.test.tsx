import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { ConceptComposer } from "./ConceptComposer";

describe("ConceptComposer", () => {
  it("shows the company context chip", () => {
    renderWithProviders(
      <ConceptComposer ticker="MSFT" isRunning={false} isStarting={false} onAsk={() => {}} />,
    );
    expect(screen.getByText("About MSFT")).toBeInTheDocument();
  });

  it("asks with the typed concept", async () => {
    const onAsk = vi.fn();
    const { user } = renderWithProviders(
      <ConceptComposer ticker="MSFT" isRunning={false} isStarting={false} onAsk={onAsk} />,
    );
    await user.type(screen.getByLabelText(/What concept do you want explained/), "What is EPS?");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    expect(onAsk).toHaveBeenCalledWith("What is EPS?");
  });

  // Empty Behaviour: "No concept chosen → prompt with a starting point" (06_UX_Specifications.md).
  it("offers starter concepts that ask immediately on click", async () => {
    const onAsk = vi.fn();
    const { user } = renderWithProviders(
      <ConceptComposer ticker="MSFT" isRunning={false} isStarting={false} onAsk={onAsk} />,
    );
    await user.click(screen.getByRole("button", { name: "What does YoY mean?" }));
    expect(onAsk).toHaveBeenCalledWith("What does YoY mean?");
  });

  it("disables the field and hides starters while a run is in progress", () => {
    renderWithProviders(
      <ConceptComposer ticker="MSFT" isRunning isStarting={false} onAsk={() => {}} />,
    );
    expect(screen.getByLabelText(/What concept do you want explained/)).toBeDisabled();
    expect(screen.queryByRole("button", { name: "What does YoY mean?" })).not.toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <ConceptComposer ticker="MSFT" isRunning={false} isStarting={false} onAsk={() => {}} />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
