import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { reportKeys } from "@/lib/api/report-keys";
import { renderHook, waitFor } from "@/tests/setup/render";
import { reportQueryKey, useReport } from "./useReport";
import { useReports } from "./useReports";

vi.mock("../integration/api", () => ({
  fetchReports: vi.fn().mockResolvedValue({ reports: [] }),
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
describe("research-library report query keys", () => {
  it("files the report list under the shared list key (reached by reportKeys.lists())", async () => {
    const { client, wrapper } = setup();
    renderHook(() => useReports(" MSFT "), { wrapper });

    await waitFor(() =>
      expect(client.getQueryState(reportKeys.list("research-library", "MSFT"))?.status).toBe(
        "success",
      ),
    );
  });

  it("files a single report under the shared detail key (reached by reportKeys.detailsFor(id))", async () => {
    const { client, wrapper } = setup();
    renderHook(() => useReport("r1"), { wrapper });

    expect(reportQueryKey("r1")).toEqual(reportKeys.detail("r1", "research-library"));
    await waitFor(() =>
      expect(client.getQueryState(reportKeys.detail("r1", "research-library"))?.status).toBe(
        "success",
      ),
    );
  });
});
