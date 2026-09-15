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

/**
 * Keyed on the query text rather than `mockResolvedValueOnce` — the real
 * `useDebouncedValue` (250ms, real timers) cancels its timer on every
 * keystroke, but that cancellation races real wall-clock time against
 * whatever else is on the event loop. Under a loaded test run an
 * intermediate value ("a", "ap") can legitimately fire before the next
 * keystroke cancels it, calling `searchCompanies` more than once before
 * settling on "app". A single-use mock breaks under that extra call; this
 * mock instead answers correctly for every call, exactly as the real
 * backend would (only "app" matches Apple Inc., any other prefix has no
 * results yet).
 */
function mockAppleSearchOnSettledQuery() {
  searchCompanies.mockImplementation((query: string) =>
    Promise.resolve(
      query === "app"
        ? { results: [{ ticker: "AAPL", name: "Apple Inc.", has_filings: true }] }
        : { results: [] },
    ),
  );
}

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
    mockAppleSearchOnSettledQuery();
    const { user } = renderWithProviders(<CompanySearch />);
    await user.type(screen.getByRole("combobox"), "app");

    await waitFor(() => expect(searchCompanies).toHaveBeenCalledWith("app", 8));
    expect(await screen.findByText("Apple Inc.")).toBeInTheDocument();
  });

  it("navigates to /research?ticker=... when a suggestion is selected", async () => {
    mockAppleSearchOnSettledQuery();
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
