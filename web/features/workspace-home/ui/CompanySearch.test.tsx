import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { CompanySearch } from "./CompanySearch";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
}));

const searchCompanies = vi.fn();
vi.mock("../integration/api", () => ({
  searchCompanies: (...args: unknown[]) => searchCompanies(...args),
  fetchRecentReports: vi.fn(),
}));

describe("CompanySearch", () => {
  beforeEach(() => {
    push.mockClear();
    searchCompanies.mockReset();
  });

  it("focuses the search box on arrival (SCR-04: search is the primary focus)", () => {
    renderWithProviders(<CompanySearch />);
    expect(screen.getByRole("combobox", { name: "Search a company" })).toHaveFocus();
  });

  it("debounces typing, then shows real suggestions from the backend", async () => {
    searchCompanies.mockResolvedValueOnce({
      results: [{ ticker: "AAPL", name: "Apple Inc.", has_filings: true }],
    });
    const { user } = renderWithProviders(<CompanySearch />);
    await user.type(screen.getByRole("combobox"), "app");

    await waitFor(() => expect(searchCompanies).toHaveBeenCalledWith("app", 8));
    expect(await screen.findByText("Apple Inc.")).toBeInTheDocument();
  });

  it("navigates to /research?ticker=... when a suggestion is selected", async () => {
    searchCompanies.mockResolvedValueOnce({
      results: [{ ticker: "AAPL", name: "Apple Inc.", has_filings: true }],
    });
    const { user } = renderWithProviders(<CompanySearch />);
    await user.type(screen.getByRole("combobox"), "app");
    const option = await screen.findByText("Apple Inc.");
    await user.click(option);

    expect(push).toHaveBeenCalledWith("/research?ticker=AAPL");
  });

  it("routes in on Enter even with no suggestion highlighted (search never hard-validates)", async () => {
    searchCompanies.mockResolvedValueOnce({ results: [] });
    const { user } = renderWithProviders(<CompanySearch />);
    const input = screen.getByRole("combobox");
    await user.type(input, "msft");
    await waitFor(() => expect(searchCompanies).toHaveBeenCalled());
    await user.keyboard("{Enter}");

    expect(push).toHaveBeenCalledWith("/research?ticker=MSFT");
  });

  it("shows a non-blocking message if the search backend is unreachable", async () => {
    searchCompanies.mockRejectedValueOnce(new Error("network"));
    const { user } = renderWithProviders(<CompanySearch />);
    await user.type(screen.getByRole("combobox"), "app");

    expect(
      await screen.findByText("Search is temporarily unavailable — try again in a moment."),
    ).toBeInTheDocument();
  });
});
