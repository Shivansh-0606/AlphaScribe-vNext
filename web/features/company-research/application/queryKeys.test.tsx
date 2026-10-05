import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { reportKeys } from "@/lib/api/report-keys";
import { renderHook, waitFor } from "@/tests/setup/render";
import { reportQueryKey, reportStatusQueryKey, useReport, useReportStatus } from "./useReport";
import { useReports } from "./useReports";

vi.mock("../integration/api", () => ({
  fetchReportsForTicker: vi.fn().mockResolvedValue({ reports: [] }),
  fetchReport: vi.fn().mockResolvedValue({ status: "completed", id: "r1" }),
}));

function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { client, wrapper };
}

/** Adoption of the shared report-key factory (report-deletion brief §3.3): a delete only reaches what is filed under these keys. */
describe("company-research report query keys", () => {
  it("files the ticker-scoped report list under the shared list key (reached by reportKeys.lists())", async () => {
    const { client, wrapper } = setup();
    renderHook(() => useReports("MSFT"), { wrapper });

    await waitFor(() =>
      expect(client.getQueryState(reportKeys.list("company-research", "MSFT"))?.status).toBe(
        "success",
      ),
    );
  });

  it("files a report under the shared detail key, keeping the exported reportQueryKey name for its other callers", async () => {
    const { client, wrapper } = setup();
    renderHook(() => useReport("r1"), { wrapper });

    expect(reportQueryKey("r1")).toEqual(reportKeys.detail("r1", "company-research"));
    await waitFor(() =>
      expect(client.getQueryState(reportKeys.detail("r1", "company-research"))?.status).toBe(
        "success",
      ),
    );
  });

  it("files a job's status under the shared status key, keeping the exported reportStatusQueryKey name", async () => {
    const { client, wrapper } = setup();
    renderHook(() => useReportStatus("r1"), { wrapper });

    expect(reportStatusQueryKey("r1")).toEqual(reportKeys.status("r1", "company-research"));
    await waitFor(() =>
      expect(client.getQueryState(reportKeys.status("r1", "company-research"))?.status).toBe(
        "success",
      ),
    );
  });
});
