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
vi.mock("../integration/api", () => ({
  fetchReport: (...args: unknown[]) => fetchReport(...args),
  acquireFinancials: (...args: unknown[]) => acquireFinancials(...args),
}));

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
    // The Statements placeholder is always present — never fabricated content (CTO decision).
    expect(screen.getByText(/Multi-period Income Statement/)).toBeInTheDocument();
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

  describe("Financial Statements acquisition", () => {
    async function renderReady() {
      searchParams = new URLSearchParams({ job: "job-1" });
      fetchReport.mockResolvedValueOnce({
        status: "completed",
        id: "job-1",
        report: { ...BASE_REPORT, extracted_data: {} },
      });
      const utils = renderWithProviders(<FinancialsSection ticker="AAPL" />);
      await screen.findByText(/No financial metrics were extracted/);
      return utils;
    }

    it("idle: shows the honest placeholder with a check action", async () => {
      await renderReady();
      expect(screen.getByText(/isn't available yet/)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: "Check for financial statements" })).toBeEnabled();
    });

    it("acquiring: disables the control and shows a loading state while the request is in flight", async () => {
      let resolveAcquire: (v: unknown) => void = () => {};
      acquireFinancials.mockReturnValueOnce(new Promise((res) => (resolveAcquire = res)));
      const { user } = await renderReady();

      await user.click(screen.getByRole("button", { name: "Check for financial statements" }));
      const button = screen.getByRole("button", { name: "Check for financial statements" });
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute("aria-busy", "true");

      resolveAcquire({ ticker: "AAPL", period_type: "annual", outcome: "requested" });
      await screen.findByText(/Fetching financial statements/);
    });

    it("requested: reports acquisition in progress and allows re-checking status", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "requested",
      });
      const { user } = await renderReady();
      await user.click(screen.getByRole("button", { name: "Check for financial statements" }));

      expect(await screen.findByText(/Fetching financial statements for AAPL/)).toBeInTheDocument();
      const recheck = screen.getByRole("button", { name: "Check status" });
      expect(recheck).toBeEnabled();

      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "available",
      });
      await user.click(recheck);
      expect(await screen.findByText(/are now available on the backend/)).toBeInTheDocument();
    });

    it("available: reports success without fabricating statement data, and moves focus onto the banner", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "available",
      });
      const { user } = await renderReady();
      await user.click(screen.getByRole("button", { name: "Check for financial statements" }));

      const banner = await screen.findByText(/are now available on the backend/);
      expect(banner.closest('[role="status"]')).toBeInTheDocument();
      // The acquisition button unmounts on this outcome — focus must land
      // somewhere intentional (the banner's focusable wrapper), never body.
      expect(banner.closest('[tabindex="-1"]')).toHaveFocus();
    });

    it("confirmed_unavailable: reports the terminal negative outcome, not an error, and moves focus onto the banner", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "confirmed_unavailable",
      });
      const { user } = await renderReady();
      await user.click(screen.getByRole("button", { name: "Check for financial statements" }));

      const banner = await screen.findByText(/has no financial statements for AAPL/);
      expect(banner.closest('[role="status"]')).toBeInTheDocument();
      expect(banner.closest('[tabindex="-1"]')).toHaveFocus();
    });

    it("mixed: reports partial availability and moves focus onto the banner", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "mixed",
      });
      const { user } = await renderReady();
      await user.click(screen.getByRole("button", { name: "Check for financial statements" }));

      const banner = await screen.findByText(/couldn't supply all of them/);
      expect(banner.closest('[tabindex="-1"]')).toHaveFocus();
    });

    it("requested: keeps focus on the persisting action button rather than redirecting it", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "requested",
      });
      const { user } = await renderReady();
      await user.click(screen.getByRole("button", { name: "Check for financial statements" }));

      const recheck = await screen.findByRole("button", { name: "Check status" });
      // Same control the user just activated (relabeled) — never yanked
      // away, since it never disappears for this outcome.
      expect(recheck).toHaveFocus();
    });

    it("error/retry: does not steal focus from the persisting Retry button", async () => {
      acquireFinancials.mockRejectedValueOnce(new Error("Too many acquisition requests"));
      const { user } = await renderReady();
      await user.click(screen.getByRole("button", { name: "Check for financial statements" }));

      const retry = await screen.findByRole("button", { name: "Check for financial statements" });
      expect(retry).toHaveFocus();
    });

    it("failure: surfaces the transport error and lets the user retry", async () => {
      acquireFinancials.mockRejectedValueOnce(new Error("Too many acquisition requests"));
      const { user } = await renderReady();
      await user.click(screen.getByRole("button", { name: "Check for financial statements" }));

      const errorBanner = await screen.findByRole("alert");
      expect(errorBanner).toHaveTextContent("Too many acquisition requests");

      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "requested",
      });
      await user.click(screen.getByRole("button", { name: "Check for financial statements" }));
      expect(await screen.findByText(/Fetching financial statements/)).toBeInTheDocument();
    });

    it("requests the annual period — no period selector exists in this UX", async () => {
      acquireFinancials.mockResolvedValueOnce({
        ticker: "AAPL",
        period_type: "annual",
        outcome: "requested",
      });
      const { user } = await renderReady();
      await user.click(screen.getByRole("button", { name: "Check for financial statements" }));

      await screen.findByText(/Fetching financial statements/);
      expect(acquireFinancials).toHaveBeenCalledWith("AAPL", "annual");
    });
  });
});
