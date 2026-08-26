import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import type { ReportDoc } from "../integration/schemas";
import { FinancialsSection } from "./FinancialsSection";

let searchParams = new URLSearchParams();
vi.mock("next/navigation", () => ({
  useSearchParams: () => searchParams,
}));

const fetchReport = vi.fn();
const acquireFinancials = vi.fn();
const fetchFinancialStatements = vi.fn();
vi.mock("../integration/api", () => ({
  fetchReport: (...args: unknown[]) => fetchReport(...args),
  acquireFinancials: (...args: unknown[]) => acquireFinancials(...args),
  fetchFinancialStatements: (...args: unknown[]) => fetchFinancialStatements(...args),
}));

function emptyGroup() {
  return { acquisition_state: "not_yet_acquired" as const, periods: [] };
}

function financialsResponse(
  overrides: {
    income?: unknown;
    balance_sheet?: unknown;
    cash_flow?: unknown;
  } = {},
) {
  return {
    ticker: "AAPL",
    period_type: "annual" as const,
    statements: {
      income: overrides.income ?? emptyGroup(),
      balance_sheet: overrides.balance_sheet ?? emptyGroup(),
      cash_flow: overrides.cash_flow ?? emptyGroup(),
    },
  };
}

const AVAILABLE_INCOME = {
  acquisition_state: "available" as const,
  periods: [
    {
      period_end: "2025-09-30",
      fiscal_year: "2025",
      currency: "USD",
      source: "yfinance",
      fetched_at: "2026-08-10T09:00:00Z",
      metrics: [
        {
          canonical_metric: "total_revenue",
          provider_label: "Total Revenue",
          value: 100,
          unit: "currency" as const,
        },
      ],
    },
  ],
};

const BASE_REPORT: ReportDoc = {
  id: "job-1",
  ticker: "AAPL",
  query: "q",
  created_at: "2026-01-01T00:00:00Z",
  draft_report: "…",
  source_documents: [],
  fact_check_status: true,
  validation_errors: [],
  retry_count: 0,
  scorecard: {
    faithfulness: 1,
    context_precision: 1,
    answer_relevance: 1,
    overall: 1,
    cited_sources: [],
    n_claims: 0,
    n_supported: 0,
  },
};

describe("FinancialsSection", () => {
  beforeEach(() => {
    searchParams = new URLSearchParams();
    fetchReport.mockReset();
    acquireFinancials.mockReset();
    fetchFinancialStatements.mockReset();
    fetchFinancialStatements.mockResolvedValue(financialsResponse());
  });

  it("shows an empty state prompting Overview when there's no job yet", () => {
    renderWithProviders(<FinancialsSection ticker="AAPL" />);
    expect(screen.getByText(/Run research on the Overview tab/)).toBeInTheDocument();
  });

  it("renders MetricStat cards only for fields that actually have a value, plus guidance separately", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValueOnce({
      status: "completed",
      id: "job-1",
      report: {
        ...BASE_REPORT,
        extracted_data: {
          revenue: "$100B",
          revenue_yoy: "+8.2%",
          eps: null,
          net_income: null,
          guidance: "Raised FY25 outlook.",
          operating_margin: null,
          free_cash_flow: null,
        },
      },
    });
    renderWithProviders(<FinancialsSection ticker="AAPL" />);

    expect(await screen.findByText("$100B")).toBeInTheDocument();
    expect(screen.getByText("+8.2%")).toBeInTheDocument();
    expect(screen.getByText("Raised FY25 outlook.")).toBeInTheDocument();
    expect(screen.queryByText("EPS")).not.toBeInTheDocument();
    // The Statements card is always present, driven by its own query — never
    // fabricated from the report (M12: GET /companies/{ticker}/financials).
    expect(await screen.findByText("Income Statement")).toBeInTheDocument();
  });

  it("shows a no-metrics message when extracted_data is empty, not a blank grid", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValueOnce({
      status: "completed",
      id: "job-1",
      report: { ...BASE_REPORT, extracted_data: {} },
    });
    renderWithProviders(<FinancialsSection ticker="AAPL" />);
    expect(
      await screen.findByText("No financial metrics were extracted for this report."),
    ).toBeInTheDocument();
  });

  it("surfaces a load failure with retry", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockRejectedValueOnce(new Error("network"));
    renderWithProviders(<FinancialsSection ticker="AAPL" />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't load financial metrics.");
  });

  it("regression: a still-running job (no report yet) is not treated as a load failure", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    // In-flight jobs resolve to {status, id, events} — no `report` field — which is
    // legitimate, not an error (server.py:1009-1027).
    fetchReport.mockResolvedValueOnce({ status: "running", id: "job-1", events: [] });
    renderWithProviders(<FinancialsSection ticker="AAPL" />);
    expect(await screen.findByText(/Research is still running/)).toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("has no detectable accessibility violations with metrics rendered", async () => {
    searchParams = new URLSearchParams({ job: "job-1" });
    fetchReport.mockResolvedValueOnce({
      status: "completed",
      id: "job-1",
      report: { ...BASE_REPORT, extracted_data: { revenue: "$100B", eps: "$1.23" } },
    });
    const { container } = renderWithProviders(<FinancialsSection ticker="AAPL" />);
    await screen.findByText("$100B");

    expect(await axe(container)).toHaveNoViolations();
  });

  describe("Financial Statements (M12 — GET /companies/{ticker}/financials)", () => {
    async function renderReady() {
      searchParams = new URLSearchParams({ job: "job-1" });
      fetchReport.mockResolvedValueOnce({
        status: "completed",
        id: "job-1",
        report: { ...BASE_REPORT, extracted_data: {} },
      });
      const utils = renderWithProviders(<FinancialsSection ticker="AAPL" />);
      await screen.findByText(/No financial metrics were extracted/);
      await screen.findByText("Income Statement");
      return utils;
    }

    it("loading: shows a loader while financial statements are being fetched", async () => {
      let resolveFinancials: (v: unknown) => void = () => {};
      fetchFinancialStatements.mockReset();
      fetchFinancialStatements.mockReturnValueOnce(new Promise((res) => (resolveFinancials = res)));
      searchParams = new URLSearchParams({ job: "job-1" });
      fetchReport.mockResolvedValueOnce({
        status: "completed",
        id: "job-1",
        report: { ...BASE_REPORT, extracted_data: {} },
      });
      renderWithProviders(<FinancialsSection ticker="AAPL" />);

      expect(await screen.findByText(/Loading financial statements/)).toBeInTheDocument();
      resolveFinancials(financialsResponse());
      await screen.findByText("Income Statement");
    });

    it("error: surfaces a load failure with retry, independent of the metrics card", async () => {
      fetchFinancialStatements.mockReset();
      fetchFinancialStatements.mockRejectedValueOnce(new Error("network"));
      searchParams = new URLSearchParams({ job: "job-1" });
      fetchReport.mockResolvedValueOnce({
        status: "completed",
        id: "job-1",
        report: { ...BASE_REPORT, extracted_data: {} },
      });
      renderWithProviders(<FinancialsSection ticker="AAPL" />);

      expect(await screen.findByRole("alert")).toHaveTextContent(
        "Couldn't load financial statements.",
      );
      // The unrelated metrics card above still rendered fine.
      expect(
        screen.getByText("No financial metrics were extracted for this report."),
      ).toBeInTheDocument();
    });

    it("idle: each statement type shows its own honest placeholder with a check action", async () => {
      await renderReady();
      expect(screen.getByText("Income Statement isn't available yet.")).toBeInTheDocument();
      expect(screen.getByText("Balance Sheet isn't available yet.")).toBeInTheDocument();
      expect(screen.getByText("Cash Flow Statement isn't available yet.")).toBeInTheDocument();
      const buttons = screen.getAllByRole("button", { name: "Check for financial statements" });
      expect(buttons).toHaveLength(3);
      buttons.forEach((b) => expect(b).toBeEnabled());
    });

    it("acquiring: disables every trigger and shows a loading state while the request is in flight", async () => {
      let resolveAcquire: (v: unknown) => void = () => {};
      acquireFinancials.mockReturnValueOnce(new Promise((res) => (resolveAcquire = res)));
      const { user } = await renderReady();

      await user.click(
        screen.getAllByRole("button", { name: "Check for financial statements" })[0],
      );
      for (const button of screen.getAllByRole("button", {
        name: "Check for financial statements",
      })) {
        expect(button).toBeDisabled();
        expect(button).toHaveAttribute("aria-busy", "true");
      }

      resolveAcquire({ ticker: "AAPL", period_type: "annual", outcome: "requested" });
      await screen.findAllByRole("button", { name: "Check status" });
    });

    it("requested: relabels the trigger to Check status and keeps focus on it (no data yet, so no block goes terminal)", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "requested",
      });
      const { user } = await renderReady();
      const [firstButton] = screen.getAllByRole("button", {
        name: "Check for financial statements",
      });
      await user.click(firstButton);

      const recheckButtons = await screen.findAllByRole("button", { name: "Check status" });
      expect(recheckButtons).toHaveLength(3);
      // Same control the user just activated (relabeled) — still not_yet_acquired
      // after refetch (default mock), so nothing goes terminal and focus stays put.
      expect(firstButton).toHaveFocus();
    });

    it("available: renders the real StatementTable for that statement type and moves focus once every type is terminal", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "requested",
      });
      const { user } = await renderReady();
      // Queued AFTER renderReady()'s initial (default, all not_yet_acquired)
      // fetch, so this becomes the response to the refetch the mutation
      // triggers — not the initial mount fetch.
      fetchFinancialStatements.mockResolvedValueOnce(
        financialsResponse({
          income: AVAILABLE_INCOME,
          balance_sheet: { acquisition_state: "confirmed_unavailable", periods: [] },
          cash_flow: { acquisition_state: "confirmed_unavailable", periods: [] },
        }),
      );
      await user.click(
        screen.getAllByRole("button", { name: "Check for financial statements" })[0],
      );

      expect(await screen.findByText("Total Revenue")).toBeInTheDocument();
      expect(screen.getByRole("table")).toBeInTheDocument();
      // Every type is now terminal (available-with-data or confirmed_unavailable)
      // — no trigger button remains anywhere in the card, so focus must land
      // somewhere intentional (the card's focusable wrapper), never <body>.
      expect(screen.queryByRole("button", { name: /Check/ })).not.toBeInTheDocument();
      expect(screen.getByRole("table").closest('[tabindex="-1"]')).toHaveFocus();
    });

    it("confirmed_unavailable: reports the terminal negative outcome per statement type, not an error", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "confirmed_unavailable",
      });
      const { user } = await renderReady();
      fetchFinancialStatements.mockResolvedValueOnce(
        financialsResponse({
          income: { acquisition_state: "confirmed_unavailable", periods: [] },
          balance_sheet: { acquisition_state: "confirmed_unavailable", periods: [] },
          cash_flow: { acquisition_state: "confirmed_unavailable", periods: [] },
        }),
      );
      await user.click(
        screen.getAllByRole("button", { name: "Check for financial statements" })[0],
      );

      expect(
        await screen.findByText("The data provider has no income statement for AAPL."),
      ).toBeInTheDocument();
      expect(
        screen.getByText("The data provider has no balance sheet for AAPL."),
      ).toBeInTheDocument();
      expect(
        screen.getByText("The data provider has no cash flow statement for AAPL."),
      ).toBeInTheDocument();
      expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    });

    it("mixed: each statement type renders its own true state independently, with no combined 'mixed' message", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "mixed",
      });
      const { user } = await renderReady();
      fetchFinancialStatements.mockResolvedValueOnce(
        financialsResponse({
          income: AVAILABLE_INCOME,
          balance_sheet: emptyGroup(),
          cash_flow: { acquisition_state: "confirmed_unavailable", periods: [] },
        }),
      );
      await user.click(
        screen.getAllByRole("button", { name: "Check for financial statements" })[0],
      );

      expect(await screen.findByRole("table")).toBeInTheDocument();
      expect(screen.getByText("Balance Sheet isn't available yet.")).toBeInTheDocument();
      expect(
        screen.getByText("The data provider has no cash flow statement for AAPL."),
      ).toBeInTheDocument();
      // Balance Sheet is still not_yet_acquired, so its trigger persists.
      expect(screen.getByRole("button", { name: "Check status" })).toBeInTheDocument();
    });

    it("acquisition error: surfaces the transport error without discarding the statements already shown", async () => {
      acquireFinancials.mockRejectedValueOnce(new Error("Too many acquisition requests"));
      const { user } = await renderReady();
      await user.click(
        screen.getAllByRole("button", { name: "Check for financial statements" })[0],
      );

      const errorBanner = await screen.findByRole("alert");
      expect(errorBanner).toHaveTextContent("Too many acquisition requests");
      // The idle placeholders are still there — the error didn't blank the card.
      expect(screen.getByText("Income Statement isn't available yet.")).toBeInTheDocument();
    });

    it("requests the annual period for both the read query and the acquisition trigger", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "requested",
      });
      const { user } = await renderReady();
      expect(fetchFinancialStatements).toHaveBeenCalledWith("AAPL", "annual");

      await user.click(
        screen.getAllByRole("button", { name: "Check for financial statements" })[0],
      );
      expect(acquireFinancials).toHaveBeenCalledWith("AAPL", "annual");
    });
  });
});
