import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { reportKeys } from "@/lib/api/report-keys";
import { AppError } from "@/lib/errors/app-error";
import { act, renderHook, waitFor } from "@/tests/setup/render";
import { useDeleteReport } from "./useDeleteReport";

const deleteReport = vi.fn();
vi.mock("../integration/api", () => ({
  deleteReport: (...args: unknown[]) => deleteReport(...args),
}));

const LISTS = [
  reportKeys.list("research-library", ""),
  reportKeys.list("company-research", "MSFT"),
  reportKeys.list("comparison", ""),
  reportKeys.list("workspace-home", "recent", 10),
];
const COMPARE = reportKeys.compare(["r1", "r2"]);
const R1_ENTRIES = [
  reportKeys.detail("r1", "research-library"),
  reportKeys.detail("r1", "company-research"),
  reportKeys.status("r1", "company-research"),
];
const R2_DETAIL = reportKeys.detail("r2", "research-library");

describe("useDeleteReport", () => {
  let client: QueryClient;
  let wrapper: (props: { children: ReactNode }) => ReactNode;

  const invalidated = (key: readonly unknown[]) => client.getQueryState(key)?.isInvalidated;
  const present = (key: readonly unknown[]) => client.getQueryState(key) !== undefined;

  beforeEach(() => {
    deleteReport.mockReset();
    client = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
    for (const key of [...LISTS, COMPARE, ...R1_ENTRIES, R2_DETAIL]) client.setQueryData(key, {});
    wrapper = ({ children }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
  });
  afterEach(() => client.clear());

  it("on a delete: invalidates every feature's list AND cached compares, and removes only that report's detail/status entries", async () => {
    deleteReport.mockResolvedValueOnce({ deleted: "r1" });
    const { result } = renderHook(() => useDeleteReport(), { wrapper });

    await act(async () => {
      await expect(result.current.mutateAsync("r1")).resolves.toBe("deleted");
    });

    expect(deleteReport).toHaveBeenCalledWith("r1");
    for (const key of LISTS) expect(invalidated(key)).toBe(true);
    expect(invalidated(COMPARE)).toBe(true);
    for (const key of R1_ENTRIES) expect(present(key)).toBe(false);
    expect(present(R2_DETAIL)).toBe(true);
    expect(invalidated(R2_DETAIL)).toBe(false);
  });

  it("refetches lists that are on screen, so they update without a manual reload", async () => {
    const fetchList = vi.fn().mockResolvedValue({ reports: [] });
    deleteReport.mockResolvedValueOnce({ deleted: "r1" });
    const { result } = renderHook(
      () => ({
        list: useQuery({ queryKey: reportKeys.list("comparison", "live"), queryFn: fetchList }),
        remove: useDeleteReport(),
      }),
      { wrapper },
    );
    await waitFor(() => expect(fetchList).toHaveBeenCalledTimes(1));

    await act(async () => {
      await result.current.remove.mutateAsync("r1");
    });

    expect(fetchList).toHaveBeenCalledTimes(2);
  });

  it("is confirmed, not optimistic: nothing is removed or invalidated until the backend answers", async () => {
    let resolveDelete: (value: { deleted: string }) => void = () => {};
    deleteReport.mockReturnValueOnce(
      new Promise((resolve) => {
        resolveDelete = resolve;
      }),
    );
    const { result } = renderHook(() => useDeleteReport(), { wrapper });

    act(() => {
      result.current.mutate("r1");
    });
    await waitFor(() => expect(result.current.isPending).toBe(true));
    for (const key of R1_ENTRIES) expect(present(key)).toBe(true);
    for (const key of LISTS) expect(invalidated(key)).toBe(false);

    await act(async () => {
      resolveDelete({ deleted: "r1" });
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    for (const key of R1_ENTRIES) expect(present(key)).toBe(false);
  });

  it("treats a 404 as 'already gone' (Q7): resolves, and converges the caches exactly like a delete", async () => {
    deleteReport.mockRejectedValueOnce(
      new AppError("unknown", "report not found", { status: 404 }),
    );
    const { result } = renderHook(() => useDeleteReport(), { wrapper });

    await act(async () => {
      await expect(result.current.mutateAsync("r1")).resolves.toBe("already_gone");
    });

    for (const key of LISTS) expect(invalidated(key)).toBe(true);
    expect(invalidated(COMPARE)).toBe(true);
    for (const key of R1_ENTRIES) expect(present(key)).toBe(false);
  });

  it.each([
    ["network", new AppError("network", "Unable to reach the server.")],
    ["server (5xx)", new AppError("server", "Server error.", { status: 500 })],
    [
      "auth_required (401) — surfaced, not swallowed",
      new AppError("auth_required", "Authentication required.", { status: 401 }),
    ],
  ])(
    "on a %s failure: rejects to the caller and leaves every cache exactly as it was",
    async (_label, error) => {
      deleteReport.mockRejectedValueOnce(error);
      const { result } = renderHook(() => useDeleteReport(), { wrapper });

      await act(async () => {
        await expect(result.current.mutateAsync("r1")).rejects.toBe(error);
      });

      for (const key of [...LISTS, COMPARE]) expect(invalidated(key)).toBe(false);
      for (const key of R1_ENTRIES) expect(present(key)).toBe(true);
    },
  );

  it("on a validation failure (response wasn't {deleted: string}): rejects AND refreshes the lists, since the delete may have happened", async () => {
    const error = new AppError("validation", "Response failed validation at the trust boundary.");
    deleteReport.mockRejectedValueOnce(error);
    const { result } = renderHook(() => useDeleteReport(), { wrapper });

    await act(async () => {
      await expect(result.current.mutateAsync("r1")).rejects.toBe(error);
    });

    for (const key of LISTS) expect(invalidated(key)).toBe(true);
    for (const key of R1_ENTRIES) expect(present(key)).toBe(true);
  });
});
