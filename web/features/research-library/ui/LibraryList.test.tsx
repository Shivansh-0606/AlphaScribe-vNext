import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import type { ReportListItem } from "../integration/schemas";
import { REPORT_DELETE_COPY as copy } from "./copy";
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
        onDeleteRequest={noop}
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
        onDeleteRequest={noop}
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
        onDeleteRequest={noop}
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
        onDeleteRequest={noop}
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
        onDeleteRequest={noop}
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
        onDeleteRequest={noop}
      />,
    );
    // Anchored: the row's menu trigger (a sibling button) also names this report.
    await user.click(screen.getByRole("button", { name: /^AAPL.*Key risks/ }));
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
        onDeleteRequest={noop}
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
        onDeleteRequest={noop}
      />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });

  describe("per-row actions menu (CR-SCOPE-004)", () => {
    function renderList() {
      const onDeleteRequest = vi.fn();
      return {
        onDeleteRequest,
        ...renderWithProviders(
          <LibraryList
            reports={REPORTS}
            isLoading={false}
            isError={false}
            onRetry={noop}
            filter=""
            onFilterChange={noop}
            onSelect={noop}
            onDeleteRequest={onDeleteRequest}
          />,
        ),
      };
    }
    const triggerFor = (report: ReportListItem) =>
      screen.getByRole("button", { name: copy.menuTriggerLabel(report) });

    it("offers a menu on the user's own report, with an accessible name that names that report", () => {
      renderList();
      expect(triggerFor(REPORTS[0])).toBeInTheDocument();
    });

    it("offers no menu on a public sample — the backend would 404, so the control is hidden (Q6)", () => {
      renderList();
      expect(
        screen.queryByRole("button", { name: copy.menuTriggerLabel(REPORTS[1]) }),
      ).not.toBeInTheDocument();
      // Menu triggers are the only buttons that report an expanded state: exactly one, the own report's.
      expect(screen.getAllByRole("button", { expanded: false })).toHaveLength(1);
    });

    it("keeps the row's open button and the menu as siblings — never nested interactive elements", () => {
      renderList();
      expect(screen.getByRole("button", { name: /^AAPL/ })).not.toContainElement(
        triggerFor(REPORTS[0]),
      );
    });

    it("choosing Delete hands the report and that row's own trigger up", async () => {
      const { user, onDeleteRequest } = renderList();
      await user.click(triggerFor(REPORTS[0]));
      await user.click(await screen.findByRole("menuitem", { name: copy.menuDeleteItem }));
      expect(onDeleteRequest).toHaveBeenCalledOnce();
      expect(onDeleteRequest).toHaveBeenCalledWith(REPORTS[0], triggerFor(REPORTS[0]));
    });

    it("is operable from the keyboard alone", async () => {
      const { user, onDeleteRequest } = renderList();
      triggerFor(REPORTS[0]).focus();
      await user.keyboard("{Enter}");
      await screen.findByRole("menuitem", { name: copy.menuDeleteItem });
      await user.keyboard("{Enter}");
      expect(onDeleteRequest).toHaveBeenCalledOnce();
    });

    it("has no detectable accessibility violations with the menu open", async () => {
      const { user, baseElement } = renderList();
      await user.click(triggerFor(REPORTS[0]));
      await screen.findByRole("menuitem", { name: copy.menuDeleteItem });
      // baseElement, so the portaled menu itself is checked. Only axe's page-level
      // `region` rule is off: a test page has no landmarks for portaled content to sit in.
      expect(
        await axe(baseElement, { rules: { region: { enabled: false } } }),
      ).toHaveNoViolations();
    });
  });
});
