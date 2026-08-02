import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import type { ReportListItem } from "../integration/schemas";
import { LibraryList } from "./LibraryList";

const REPORTS: ReportListItem[] = [
  { id: "r1", ticker: "AAPL", query: "Key risks?", created_at: "2026-01-01T00:00:00Z" },
  {
    id: "r2",
    ticker: "MSFT",
    query: "Is it a good time to invest",
    created_at: "2026-01-02T00:00:00Z",
    is_sample: true,
  },
];

const noop = () => {};

describe("LibraryList", () => {
  it("shows a loading skeleton while pending", () => {
    renderWithProviders(
      <LibraryList
        reports={undefined}
        isLoading
        isError={false}
        onRetry={noop}
        filter=""
        onFilterChange={noop}
        onSelect={noop}
      />,
    );
    expect(screen.getByText("Loading research library")).toBeInTheDocument();
  });

  it("offers retry on a load error", async () => {
    const onRetry = vi.fn();
    const { user } = renderWithProviders(
      <LibraryList
        reports={undefined}
        isLoading={false}
        isError
        onRetry={onRetry}
        filter=""
        onFilterChange={noop}
        onSelect={noop}
      />,
    );
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("shows the Empty state when there is no saved research and no filter is active", () => {
    renderWithProviders(
      <LibraryList
        reports={[]}
        isLoading={false}
        isError={false}
        onRetry={noop}
        filter=""
        onFilterChange={noop}
        onSelect={noop}
      />,
    );
    expect(screen.getByText(/No saved research yet/)).toBeInTheDocument();
  });

  it("shows the No Results state (distinct from Empty) when a filter matches nothing", () => {
    renderWithProviders(
      <LibraryList
        reports={[]}
        isLoading={false}
        isError={false}
        onRetry={noop}
        filter="ZZZZ"
        onFilterChange={noop}
        onSelect={noop}
      />,
    );
    expect(screen.getByText('No reports match "ZZZZ".')).toBeInTheDocument();
    expect(screen.queryByText(/No saved research yet/)).not.toBeInTheDocument();
  });

  it("renders each report and tags samples distinctly from the user's own reports", () => {
    renderWithProviders(
      <LibraryList
        reports={REPORTS}
        isLoading={false}
        isError={false}
        onRetry={noop}
        filter=""
        onFilterChange={noop}
        onSelect={noop}
      />,
    );
    expect(screen.getByText("AAPL")).toBeInTheDocument();
    expect(screen.getByText("MSFT")).toBeInTheDocument();
    expect(screen.getByText("Sample")).toBeInTheDocument();
  });

  it("opens the selected report", async () => {
    const onSelect = vi.fn();
    const { user } = renderWithProviders(
      <LibraryList
        reports={REPORTS}
        isLoading={false}
        isError={false}
        onRetry={noop}
        filter=""
        onFilterChange={noop}
        onSelect={onSelect}
      />,
    );
    await user.click(screen.getByRole("button", { name: /AAPL.*Key risks/ }));
    expect(onSelect).toHaveBeenCalledWith(REPORTS[0]);
  });

  it("reports each keystroke to the caller (debouncing is the screen's concern, not this component's)", async () => {
    const onFilterChange = vi.fn();
    const { user } = renderWithProviders(
      <LibraryList
        reports={REPORTS}
        isLoading={false}
        isError={false}
        onRetry={noop}
        filter=""
        onFilterChange={onFilterChange}
        onSelect={noop}
      />,
    );
    // Controlled input with no state in this test — each keystroke's event
    // reflects just that character, since `value` never advances between them.
    await user.type(screen.getByLabelText("Filter by ticker"), "MS");
    expect(onFilterChange).toHaveBeenCalledWith("M");
    expect(onFilterChange).toHaveBeenCalledWith("S");
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(
      <LibraryList
        reports={REPORTS}
        isLoading={false}
        isError={false}
        onRetry={noop}
        filter=""
        onFilterChange={noop}
        onSelect={noop}
      />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
