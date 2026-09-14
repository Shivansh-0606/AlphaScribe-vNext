import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, within } from "@/tests/setup/render";
import type { ChangeBriefPayload } from "../integration/schemas";
import { ChangeBriefResult } from "./ChangeBriefResult";

const fetchReport = vi.fn();
vi.mock("../integration/api", () => ({
  fetchReport: (...args: unknown[]) => fetchReport(...args),
}));

function narrativePayload(overrides: Partial<ChangeBriefPayload> = {}): ChangeBriefPayload {
  return {
    ticker: "AAPL",
    comparison_type: "report",
    baseline: { report_id: "rb", ticker: "AAPL", company_name: "Apple Inc." },
    current: { report_id: "rc", ticker: "AAPL", company_name: "Apple Inc." },
    created_at: "2026-01-01T00:00:00Z",
    prompt_version: "v1",
    schema_version: "v1",
    items: [
      {
        category: "narrative",
        summary: "Guidance cut",
        explanation: "Guidance was raised [1] but is now lowered [2].",
        sources: [
          { index: 1, report_id: "rb", field: "extracted_data" },
          { index: 2, report_id: "rc", field: "extracted_data" },
        ],
        cited_source_indices: [1, 2],
      },
    ],
    state: "complete",
    coverage_boundaries: [],
    ...overrides,
  } as ChangeBriefPayload;
}

function periodPayload(overrides: Partial<ChangeBriefPayload> = {}): ChangeBriefPayload {
  return {
    ticker: "AAPL",
    comparison_type: "period",
    baseline: {
      period_end: "2024-06-30",
      period_type: "quarterly",
      statement_type: "income",
      fiscal_year: "2024",
      currency: "USD",
    },
    current: {
      period_end: "2024-09-30",
      period_type: "quarterly",
      statement_type: "income",
      fiscal_year: "2024",
      currency: "USD",
    },
    created_at: "2026-01-01T00:00:00Z",
    prompt_version: null,
    schema_version: "v1",
    items: [
      {
        category: "financial",
        metric: "Revenue",
        statement_type: "income",
        period_type: "quarterly",
        change_kind: "changed",
        unit: "currency",
        currency: "USD",
        before: { period_end: "2024-06-30", value: 100_000_000 },
        after: { period_end: "2024-09-30", value: 110_000_000 },
        absolute_delta: 10_000_000,
        percent_delta: 0.1,
        sources: [
          { index: 1, statement_type: "income", period_end: "2024-06-30", metric: "Revenue" },
          { index: 2, statement_type: "income", period_end: "2024-09-30", metric: "Revenue" },
        ],
        cited_source_indices: [1, 2],
      },
    ],
    state: "complete",
    coverage_boundaries: [],
    ...overrides,
  } as ChangeBriefPayload;
}

describe("ChangeBriefResult", () => {
  beforeEach(() => {
    fetchReport.mockReset().mockResolvedValue({ status: "completed", id: "x", report: undefined });
  });

  it("renders report-mode narrative items, grounded and cited", async () => {
    renderWithProviders(<ChangeBriefResult payload={narrativePayload()} />);
    expect(screen.getByText("Guidance cut")).toBeInTheDocument();
    expect(screen.getByText(/Guidance was raised/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /\[1\]/ })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /\[2\]/ })).toBeInTheDocument();
  });

  it("renders period-mode financial items with formatted before/after values", () => {
    renderWithProviders(<ChangeBriefResult payload={periodPayload()} />);
    expect(screen.getByText("Revenue")).toBeInTheDocument();
    expect(screen.getByText("Changed")).toBeInTheDocument();
    expect(screen.getByText(/\$100M/)).toBeInTheDocument();
    expect(screen.getByText(/\$110M/)).toBeInTheDocument();
    expect(screen.getByText(/10\.0%/)).toBeInTheDocument();
  });

  it("labels new/removed metrics distinctly from changed ones", () => {
    renderWithProviders(
      <ChangeBriefResult
        payload={periodPayload({
          items: [
            {
              category: "financial",
              metric: "NewLine",
              statement_type: "income",
              period_type: "quarterly",
              change_kind: "new",
              unit: "currency",
              currency: "USD",
              before: null,
              after: { period_end: "2024-09-30", value: 5_000_000 },
              absolute_delta: null,
              percent_delta: null,
              sources: [
                { index: 1, statement_type: "income", period_end: "2024-09-30", metric: "NewLine" },
              ],
              cited_source_indices: [1],
            },
          ],
        })}
      />,
    );
    expect(screen.getByText("New")).toBeInTheDocument();
    // No baseline value for a "new" item — an honest "—" placeholder, never fabricated.
    expect(
      screen.getByText((_, el) => el?.tagName === "P" && el.textContent === "— → $5M"),
    ).toBeInTheDocument();
  });

  it("shows an honest insufficient-evidence empty state, never a fabricated item", () => {
    renderWithProviders(
      <ChangeBriefResult
        payload={narrativePayload({ items: [], state: "insufficient_evidence" })}
      />,
    );
    expect(
      screen.getByText("Not enough grounded evidence to report what changed."),
    ).toBeInTheDocument();
  });

  it("surfaces a partial state's coverage boundaries", () => {
    renderWithProviders(
      <ChangeBriefResult
        payload={periodPayload({
          state: "partial",
          coverage_boundaries: ["unit mismatch for Margin: ratio vs percentage"],
        })}
      />,
    );
    expect(screen.getByText("Partial")).toBeInTheDocument();
    expect(screen.getByText(/unit mismatch for Margin/)).toBeInTheDocument();
  });

  it("renumbers per-item-local source indices to page-wide-unique ids across multiple items", () => {
    renderWithProviders(
      <ChangeBriefResult
        payload={periodPayload({
          items: [
            {
              category: "financial",
              metric: "Revenue",
              statement_type: "income",
              period_type: "quarterly",
              change_kind: "changed",
              unit: "currency",
              currency: "USD",
              before: { period_end: "2024-06-30", value: 100 },
              after: { period_end: "2024-09-30", value: 110 },
              absolute_delta: 10,
              percent_delta: 0.1,
              sources: [
                { index: 1, statement_type: "income", period_end: "2024-06-30", metric: "Revenue" },
              ],
              cited_source_indices: [1],
            },
            {
              category: "financial",
              metric: "NetIncome",
              statement_type: "income",
              period_type: "quarterly",
              change_kind: "changed",
              unit: "currency",
              currency: "USD",
              before: { period_end: "2024-06-30", value: 20 },
              after: { period_end: "2024-09-30", value: 25 },
              absolute_delta: 5,
              percent_delta: 0.25,
              sources: [
                {
                  index: 1,
                  statement_type: "income",
                  period_end: "2024-06-30",
                  metric: "NetIncome",
                },
              ],
              cited_source_indices: [1],
            },
          ],
        })}
      />,
    );
    // Both items cite their own local [1] — must not collide into duplicate DOM ids.
    expect(document.getElementById("source-1")).toBeInTheDocument();
    expect(document.getElementById("source-2")).toBeInTheDocument();
  });

  it("labels each citation with which side of the comparison it came from", () => {
    renderWithProviders(<ChangeBriefResult payload={narrativePayload()} />);
    expect(within(screen.getByRole("list")).getByText(/Baseline report/)).toBeInTheDocument();
    expect(within(screen.getByRole("list")).getByText(/Current report/)).toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<ChangeBriefResult payload={narrativePayload()} />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
