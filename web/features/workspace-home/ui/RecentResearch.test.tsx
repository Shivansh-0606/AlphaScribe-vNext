import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { RecentResearch } from "./RecentResearch";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

const fetchRecentReports = vi.fn();
vi.mock("../integration/api", () => ({
  searchCompanies: vi.fn(),
  fetchRecentReports: (...args: unknown[]) => fetchRecentReports(...args),
}));

describe("RecentResearch", () => {
  beforeEach(() => {
    push.mockClear();
    fetchRecentReports.mockReset();
  });

  it("shows a scoped loading skeleton while the reports load", async () => {
    fetchRecentReports.mockReturnValueOnce(new Promise(() => {}));
    renderWithProviders(<RecentResearch />);
    // `status` is name-from-author only per ARIA (not name-from-content), so the
    // live region's accessible name is "" — the label is announced as its content instead.
    expect(screen.getByRole("status")).toHaveTextContent("Loading recent research");
  });

  it("shows the empty state guiding a first search when there is no research yet", async () => {
    fetchRecentReports.mockResolvedValueOnce({ reports: [] });
    renderWithProviders(<RecentResearch />);
    expect(
      await screen.findByText("No research yet — search a company above to get started."),
    ).toBeInTheDocument();
  });

  it("excludes curated public samples — recent research is the user's own work", async () => {
    fetchRecentReports.mockResolvedValueOnce({
      reports: [
        {
          id: "r1",
          ticker: "AAPL",
          query: "How's margin trending?",
          created_at: "2026-01-01",
          is_sample: true,
        },
      ],
    });
    renderWithProviders(<RecentResearch />);
    expect(
      await screen.findByText("No research yet — search a company above to get started."),
    ).toBeInTheDocument();
  });

  it("lists the user's own reports with a count, and navigates on click", async () => {
    fetchRecentReports.mockResolvedValueOnce({
      reports: [
        {
          id: "r1",
          ticker: "AAPL",
          query: "How's margin trending?",
          created_at: "2026-01-01T00:00:00Z",
          is_sample: false,
        },
      ],
    });
    const { user } = renderWithProviders(<RecentResearch />);
    expect(await screen.findByText("Recent Research (1)")).toBeInTheDocument();
    await user.click(screen.getByText("How's margin trending?"));
    expect(push).toHaveBeenCalledWith("/research?ticker=AAPL");
  });

  it("shows a non-blocking, retryable error scoped to this region on load failure", async () => {
    fetchRecentReports.mockRejectedValueOnce(new Error("network"));
    const { user } = renderWithProviders(<RecentResearch />);

    const banner = await screen.findByRole("alert");
    expect(banner).toHaveTextContent(
      "Couldn't load your recent research. Search above still works.",
    );

    fetchRecentReports.mockResolvedValueOnce({ reports: [] });
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(
      await screen.findByText("No research yet — search a company above to get started."),
    ).toBeInTheDocument();
  });
});
