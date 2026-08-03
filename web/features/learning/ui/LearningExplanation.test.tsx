import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import type { ExplanationDoc } from "../integration/schemas";
import { LearningExplanation } from "./LearningExplanation";

const EXPLANATION: ExplanationDoc = {
  id: "e1",
  ticker: "MSFT",
  concept: "What is operating margin?",
  explanation: "Operating margin is operating income divided by revenue [1].",
  source_documents: [
    { doc_id: "d1", ticker: "MSFT", source: "10-Q FY24 Q4", chunk_idx: 0, text: "…", score: 0.9 },
  ],
  created_at: "2026-01-01T00:00:00Z",
};

describe("LearningExplanation", () => {
  it("renders the concept, grounded explanation, and sources (Law 3 — never without sources)", () => {
    renderWithProviders(<LearningExplanation explanation={EXPLANATION} />);
    expect(screen.getByText("What is operating margin?")).toBeInTheDocument();
    expect(screen.getByText(/operating income divided by revenue/)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Sources" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "[1] 10-Q FY24 Q4" })).toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<LearningExplanation explanation={EXPLANATION} />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
