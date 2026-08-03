import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { ComparisonPicker } from "./ComparisonPicker";

const fetchReports = vi.fn();
vi.mock("../integration/api", () => ({
  fetchReports: (...args: unknown[]) => fetchReports(...args),
}));

const REPORTS = [
  { id: "r1", ticker: "AAPL", query: "q1", created_at: "2026-01-01T00:00:00Z" },
  {
    id: "r2",
    ticker: "MSFT",
    query: "q2",
    created_at: "2026-01-02T00:00:00Z",
    company_name: "Microsoft Corporation",
    is_sample: true,
  },
];

const noop = () => {};

describe("ComparisonPicker", () => {
  beforeEach(() => {
    fetchReports.mockReset();
  });

  it("shows an empty state when there is nothing to compare yet", async () => {
    fetchReports.mockResolvedValueOnce({ reports: [] });
    renderWithProviders(<ComparisonPicker selectedIds={[]} onToggle={noop} />);
    expect(await screen.findByText(/No saved research yet/)).toBeInTheDocument();
  });

  it("surfaces a load failure with retry", async () => {
    fetchReports.mockRejectedValueOnce(new Error("network"));
    renderWithProviders(<ComparisonPicker selectedIds={[]} onToggle={noop} />);
    expect(await screen.findByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("renders each candidate as a toggle chip and reports selection state", async () => {
    fetchReports.mockResolvedValueOnce({ reports: REPORTS });
    renderWithProviders(<ComparisonPicker selectedIds={["r2"]} onToggle={noop} />);

    const aapl = await screen.findByRole("button", { name: "AAPL" });
    const msft = screen.getByRole("button", { name: "Microsoft Corporation (Sample)" });
    expect(aapl).toHaveAttribute("aria-pressed", "false");
    expect(msft).toHaveAttribute("aria-pressed", "true");
  });

  it("calls onToggle with the selected report on click", async () => {
    fetchReports.mockResolvedValueOnce({ reports: REPORTS });
    const onToggle = vi.fn();
    const { user } = renderWithProviders(<ComparisonPicker selectedIds={[]} onToggle={onToggle} />);

    await user.click(await screen.findByRole("button", { name: "AAPL" }));
    expect(onToggle).toHaveBeenCalledWith(REPORTS[0]);
  });

  // Backend caps `POST /reports/compare` at 4 (`report_ids`, max_length=4) —
  // the picker must not let the user select a 5th and hit a 422 later.
  it("disables unselected candidates once 4 are already selected", async () => {
    fetchReports.mockResolvedValueOnce({ reports: REPORTS });
    renderWithProviders(<ComparisonPicker selectedIds={["a", "b", "c", "d"]} onToggle={noop} />);
    expect(await screen.findByRole("button", { name: "AAPL" })).toBeDisabled();
  });

  it("has no detectable accessibility violations", async () => {
    fetchReports.mockResolvedValueOnce({ reports: REPORTS });
    const { container } = renderWithProviders(
      <ComparisonPicker selectedIds={[]} onToggle={noop} />,
    );
    await screen.findByRole("button", { name: "AAPL" });
    expect(await axe(container)).toHaveNoViolations();
  });
});
