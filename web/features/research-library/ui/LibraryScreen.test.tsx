import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AppError } from "@/lib/errors/app-error";
import { renderWithProviders, screen, waitFor, within } from "@/tests/setup/render";
import type { ReportListItem } from "../integration/schemas";
import { REPORT_DELETE_COPY as copy } from "./copy";
import { LibraryScreen } from "./LibraryScreen";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
}));

// The filter's debounce is real-timer wall-clock behaviour that isn't under
// test here; identity keeps the filter tests deterministic.
vi.mock("@/lib/hooks/useDebouncedValue", () => ({
  useDebouncedValue: (value: string) => value,
}));

const fetchReports = vi.fn();
const deleteReport = vi.fn();
vi.mock("../integration/api", () => ({
  fetchReports: (...args: unknown[]) => fetchReports(...args),
  deleteReport: (...args: unknown[]) => deleteReport(...args),
}));

const toastSuccess = vi.fn();
const toastInfo = vi.fn();
vi.mock("sonner", () => ({
  toast: {
    success: (...args: unknown[]) => toastSuccess(...args),
    info: (...args: unknown[]) => toastInfo(...args),
  },
}));

const R1: ReportListItem = {
  id: "r1",
  ticker: "AAPL",
  query: "Key risks?",
  created_at: "2026-01-01T00:00:00Z",
};
const R2: ReportListItem = {
  id: "r2",
  ticker: "MSFT",
  query: "Margins",
  created_at: "2026-01-02T00:00:00Z",
};
const SAMPLE: ReportListItem = {
  id: "s1",
  ticker: "NVDA",
  query: "Sample brief",
  created_at: "2026-01-03T00:00:00Z",
  is_sample: true,
};

/** The fake backend: what `GET /reports` returns now, and what a delete removes. */
let db: ReportListItem[];

// `hidden: true`: while the confirm dialog is open it is modal, so everything behind it —
// the list rows included — is aria-hidden. These checks are about the row existing, not its a11y.
const rowFor = (report: ReportListItem) =>
  screen.queryByRole("button", { name: new RegExp(`^${report.ticker}`), hidden: true });
const triggerFor = (report: ReportListItem) =>
  screen.getByRole("button", { name: copy.menuTriggerLabel(report) });
const heading = () => screen.getByRole("heading", { name: "Research Library" });

async function chooseDelete(
  user: ReturnType<typeof renderWithProviders>["user"],
  report: ReportListItem,
) {
  await user.click(await screen.findByRole("button", { name: copy.menuTriggerLabel(report) }));
  await user.click(await screen.findByRole("menuitem", { name: copy.menuDeleteItem }));
  return screen.findByRole("dialog", { name: copy.dialogTitle });
}

describe("LibraryScreen — deleting a report", () => {
  beforeEach(() => {
    db = [R1, R2, SAMPLE];
    fetchReports.mockReset().mockImplementation(async (params: { ticker?: string } = {}) => ({
      reports: db.filter((report) => !params.ticker || report.ticker === params.ticker),
    }));
    deleteReport.mockReset().mockImplementation(async (id: string) => {
      db = db.filter((report) => report.id !== id);
      return { deleted: id };
    });
    toastSuccess.mockClear();
    toastInfo.mockClear();
  });

  it("menu → confirm → the row is gone, a toast confirms, the other rows stay, and focus lands on the list heading", async () => {
    const { user } = renderWithProviders(<LibraryScreen />);
    await screen.findByRole("button", { name: /^AAPL/ });

    const dialog = await chooseDelete(user, R1);
    expect(dialog.contains(document.activeElement)).toBe(true);
    await user.click(within(dialog).getByRole("button", { name: copy.confirmButton }));

    await waitFor(() => expect(rowFor(R1)).not.toBeInTheDocument());
    expect(deleteReport).toHaveBeenCalledWith("r1");
    expect(rowFor(R2)).toBeInTheDocument();
    expect(rowFor(SAMPLE)).toBeInTheDocument();
    expect(toastSuccess).toHaveBeenCalledWith(copy.deleted);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    await waitFor(() => expect(heading()).toHaveFocus());
  });

  it("waits for the backend (Q11): the row stays put while the delete is pending, and goes only once it resolves", async () => {
    let resolveDelete: (value: { deleted: string }) => void = () => {};
    deleteReport.mockReset().mockImplementationOnce(
      (id: string) =>
        new Promise((resolve) => {
          resolveDelete = () => {
            db = db.filter((report) => report.id !== id);
            resolve({ deleted: id });
          };
        }),
    );
    const { user } = renderWithProviders(<LibraryScreen />);
    await screen.findByRole("button", { name: /^AAPL/ });
    const dialog = await chooseDelete(user, R1);

    await user.click(within(dialog).getByRole("button", { name: copy.confirmButton }));
    await waitFor(() => expect(deleteReport).toHaveBeenCalledOnce());
    expect(rowFor(R1)).toBeInTheDocument();

    resolveDelete({ deleted: "r1" });
    await waitFor(() => expect(rowFor(R1)).not.toBeInTheDocument());
  });

  it("Cancel leaves the list untouched and returns focus to that row's OWN menu trigger", async () => {
    const { user } = renderWithProviders(<LibraryScreen />);
    await screen.findByRole("button", { name: /^MSFT/ });
    const dialog = await chooseDelete(user, R2);

    await user.click(within(dialog).getByRole("button", { name: copy.cancelButton }));

    await waitFor(() => expect(triggerFor(R2)).toHaveFocus());
    expect(triggerFor(R1)).not.toHaveFocus();
    expect(deleteReport).not.toHaveBeenCalled();
    expect(fetchReports).toHaveBeenCalledTimes(1);
    expect(rowFor(R2)).toBeInTheDocument();
  });

  it("deleting the last remaining report shows the Empty state", async () => {
    db = [R1];
    const { user } = renderWithProviders(<LibraryScreen />);
    await screen.findByRole("button", { name: /^AAPL/ });
    const dialog = await chooseDelete(user, R1);

    await user.click(within(dialog).getByRole("button", { name: copy.confirmButton }));

    expect(await screen.findByText(/No saved research yet/)).toBeInTheDocument();
    expect(screen.queryByText(/No reports match/)).not.toBeInTheDocument();
  });

  it("deleting the last match while a ticker filter is active shows No Results, not Empty", async () => {
    const { user } = renderWithProviders(<LibraryScreen />);
    await screen.findByRole("button", { name: /^AAPL/ });
    await user.type(screen.getByLabelText("Filter by ticker"), "AAPL");
    await waitFor(() => expect(screen.queryByRole("button", { name: /^MSFT/ })).toBeNull());
    const dialog = await chooseDelete(user, R1);

    await user.click(within(dialog).getByRole("button", { name: copy.confirmButton }));

    expect(await screen.findByText('No reports match "AAPL".')).toBeInTheDocument();
    expect(screen.queryByText(/No saved research yet/)).not.toBeInTheDocument();
  });

  it("a failed delete keeps the dialog open with the error inline, and the list unchanged — no refetch", async () => {
    deleteReport
      .mockReset()
      .mockRejectedValueOnce(new AppError("server", "Server error.", { status: 500 }));
    const { user } = renderWithProviders(<LibraryScreen />);
    await screen.findByRole("button", { name: /^AAPL/ });
    const dialog = await chooseDelete(user, R1);

    await user.click(within(dialog).getByRole("button", { name: copy.confirmButton }));

    expect(await within(dialog).findByRole("alert")).toHaveTextContent(copy.failure);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(rowFor(R1)).toBeInTheDocument();
    expect(fetchReports).toHaveBeenCalledTimes(1);
    expect(toastSuccess).not.toHaveBeenCalled();

    await user.click(within(dialog).getByRole("button", { name: copy.cancelButton }));
    await waitFor(() => expect(triggerFor(R1)).toHaveFocus());
    expect(rowFor(R1)).toBeInTheDocument();
    expect(fetchReports).toHaveBeenCalledTimes(1);
  });

  it("a 404 is 'already gone' (Q7): a neutral message, and the list refreshes so the UI converges", async () => {
    deleteReport.mockReset().mockImplementationOnce(async () => {
      db = db.filter((report) => report.id !== "r1"); // removed elsewhere (another tab)
      throw new AppError("unknown", "report not found", { status: 404 });
    });
    const { user } = renderWithProviders(<LibraryScreen />);
    await screen.findByRole("button", { name: /^AAPL/ });
    const dialog = await chooseDelete(user, R1);

    await user.click(within(dialog).getByRole("button", { name: copy.confirmButton }));

    await waitFor(() => expect(rowFor(R1)).not.toBeInTheDocument());
    expect(toastInfo).toHaveBeenCalledWith(copy.alreadyGone);
    expect(toastSuccess).not.toHaveBeenCalled();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
    expect(fetchReports).toHaveBeenCalledTimes(2);
  });

  it("never offers a delete control on a public sample — only the user's own reports have a menu", async () => {
    renderWithProviders(<LibraryScreen />);
    await screen.findByRole("button", { name: /^NVDA/ });

    expect(
      screen.queryByRole("button", { name: copy.menuTriggerLabel(SAMPLE) }),
    ).not.toBeInTheDocument();
    expect(screen.getAllByRole("button", { expanded: false })).toHaveLength(2); // R1 and R2 only
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<LibraryScreen />);
    await screen.findByRole("button", { name: /^AAPL/ });
    expect(await axe(container)).toHaveNoViolations();
  });
});
