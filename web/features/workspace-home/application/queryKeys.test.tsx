import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { reportKeys } from "@/lib/api/report-keys";
import { renderHook, waitFor } from "@/tests/setup/render";
import { useRecentReports } from "./useWorkspaceHome";

vi.mock("../integration/api", () => ({
  fetchRecentReports: vi.fn().mockResolvedValue({ reports: [] }),
}));

/** Adoption of the shared report-key factory (report-deletion brief §3.3): a delete only reaches what is filed under these keys. */
describe("workspace-home report query keys", () => {
  it("files Recent Research under the shared list key (reached by reportKeys.lists())", async () => {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    );
    renderHook(() => useRecentReports(5), { wrapper });

    await waitFor(() =>
      expect(client.getQueryState(reportKeys.list("workspace-home", "recent", 5))?.status).toBe(
        "success",
      ),
    );
  });
});
