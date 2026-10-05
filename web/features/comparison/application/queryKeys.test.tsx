import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { reportKeys } from "@/lib/api/report-keys";
import { renderHook, waitFor } from "@/tests/setup/render";
import { useCompare } from "./useCompare";
import { useReports } from "./useReports";

vi.mock("../integration/api", () => ({
  fetchReports: vi.fn().mockResolvedValue({ reports: [] }),
  compareReports: vi.fn().mockResolvedValue({ reports: [] }),
}));

function setup() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  const wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
  return { client, wrapper };
}

/** Adoption of the shared report-key factory (report-deletion brief §3.3): a delete only reaches what is filed under these keys. */
describe("comparison report query keys", () => {
  it("files the picker's report list under the shared list key (reached by reportKeys.lists())", async () => {
    const { client, wrapper } = setup();
    renderHook(() => useReports(" MSFT "), { wrapper });

    await waitFor(() =>
      expect(client.getQueryState(reportKeys.list("comparison", "MSFT"))?.status).toBe("success"),
    );
  });

  it("files a cached compare under the shared compare key, order-insensitively (reached by reportKeys.compares())", async () => {
    const { client, wrapper } = setup();
    renderHook(() => useCompare(["b", "a"]), { wrapper });

    await waitFor(() =>
      expect(client.getQueryState(reportKeys.compare(["a", "b"]))?.status).toBe("success"),
    );
  });
});
