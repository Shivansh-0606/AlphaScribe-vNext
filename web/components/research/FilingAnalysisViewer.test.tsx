import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen, within } from "@/tests/setup/render";
import { FilingAnalysisViewer, type FilingAnalysisOutputData } from "./FilingViewer";

const CHUNKS = [
  { chunk_idx: 0, text: "The company reports total revenue of $10B for the period." },
  { chunk_idx: 1, text: "A new supply-chain concentration risk factor was added this quarter." },
];

function output(overrides: Partial<FilingAnalysisOutputData> = {}): FilingAnalysisOutputData {
  return {
    narrative: "Revenue was $10B [1].",
    sources: [{ index: 1, doc_id: "d1", chunk_start: 0, chunk_end: 0 }],
    cited_source_indices: [1],
    state: "complete",
    coverage_boundaries: [],
    ...overrides,
  };
}

describe("FilingAnalysisViewer (Filing analysis variant)", () => {
  it("renders each output as a labelled, navigable section anchored to the filing", () => {
    renderWithProviders(
      <FilingAnalysisViewer
        source="10-Q FY24 Q3"
        chunks={CHUNKS}
        outputs={{ "Filing Summary": output() }}
      />,
    );
    const region = screen.getByRole("region", { name: "Filing Summary" });
    expect(within(region).getByText(/Revenue was \$10B/)).toBeInTheDocument();
    // Analysis always anchored to the filing (Component Inventory usage rule) — a source anchor is present.
    expect(within(region).getByRole("button", { name: /\[1\]/ })).toBeInTheDocument();
  });

  it("shows an honest insufficient-evidence state, never a fabricated narrative", () => {
    renderWithProviders(
      <FilingAnalysisViewer
        source="10-Q FY24 Q3"
        chunks={CHUNKS}
        outputs={{
          "Important Changes": output({
            narrative: "",
            sources: [],
            cited_source_indices: [],
            state: "insufficient_evidence",
            coverage_boundaries: ["no material change language found in this filing"],
          }),
        }}
      />,
    );
    expect(screen.getByText(/Not enough grounded evidence/)).toBeInTheDocument();
    expect(screen.getByText(/no material change language found/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /\[1\]/ })).not.toBeInTheDocument();
  });

  it("surfaces a partial state's coverage boundaries alongside its grounded narrative", () => {
    renderWithProviders(
      <FilingAnalysisViewer
        source="10-Q FY24 Q3"
        chunks={CHUNKS}
        outputs={{
          "MD&A Digest": output({
            state: "partial",
            coverage_boundaries: [
              "MD&A section exceeds the per-output budget; only the first portion is covered",
            ],
          }),
        }}
      />,
    );
    expect(screen.getByText("Partial")).toBeInTheDocument();
    expect(screen.getByText(/exceeds the per-output budget/)).toBeInTheDocument();
    expect(screen.getByText(/Revenue was \$10B/)).toBeInTheDocument();
  });

  it("resolves a source anchor's chunk range into a readable excerpt from the filing's own content", async () => {
    const { user } = renderWithProviders(
      <FilingAnalysisViewer
        source="10-Q FY24 Q3"
        chunks={CHUNKS}
        outputs={{
          "Risk Factors Digest": output({
            narrative: "A new concentration risk was disclosed [1].",
            sources: [{ index: 1, doc_id: "d1", chunk_start: 1, chunk_end: 1 }],
          }),
        }}
      />,
    );
    await user.click(screen.getByRole("button", { name: /\[1\]/ }));
    expect(await screen.findByText(/supply-chain concentration risk/)).toBeInTheDocument();
  });

  it("renumbers per-output-local source indices to page-wide-unique ids across multiple outputs", () => {
    renderWithProviders(
      <FilingAnalysisViewer
        source="10-Q FY24 Q3"
        chunks={CHUNKS}
        outputs={{
          "Filing Summary": output({
            narrative: "Revenue was $10B [1].",
            sources: [{ index: 1, doc_id: "d1", chunk_start: 0, chunk_end: 0 }],
          }),
          "Risk Factors Digest": output({
            narrative: "A new concentration risk was disclosed [1].",
            sources: [{ index: 1, doc_id: "d1", chunk_start: 1, chunk_end: 1 }],
          }),
        }}
      />,
    );
    // Both outputs cite their own local [1] — must not collide into duplicate DOM ids.
    expect(document.getElementById("source-1")).toBeInTheDocument();
    expect(document.getElementById("source-2")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "[1] 10-Q FY24 Q3 (chunks 0–0)" }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "[2] 10-Q FY24 Q3 (chunks 1–1)" }),
    ).toBeInTheDocument();
  });

  it("shows an honest empty state when no outputs are given, never fabricated text", () => {
    renderWithProviders(
      <FilingAnalysisViewer source="10-Q FY24 Q3" chunks={CHUNKS} outputs={{}} />,
    );
    expect(screen.getByText("No analysis is available for this filing.")).toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <FilingAnalysisViewer
        source="10-Q FY24 Q3"
        chunks={CHUNKS}
        outputs={{
          "Filing Summary": output(),
          "Important Changes": output({
            narrative: "",
            sources: [],
            cited_source_indices: [],
            state: "insufficient_evidence",
            coverage_boundaries: ["no material change language found in this filing"],
          }),
        }}
      />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
