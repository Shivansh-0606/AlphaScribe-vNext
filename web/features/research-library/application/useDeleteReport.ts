import { useMutation, useQueryClient } from "@tanstack/react-query";
import { reportKeys } from "@/lib/api/report-keys";
import { AppError } from "@/lib/errors/app-error";
import * as researchLibraryApi from "../integration/api";

/** `already_gone`: the backend answered 404 (deleted elsewhere, not the caller's, a sample, or never saved). */
export type DeleteReportOutcome = "deleted" | "already_gone";

/**
 * Deletes one saved report (CR-SCOPE-004, report-deletion brief §3.2/§3.3).
 * Confirmed, never optimistic (Q11, 03.2): nothing leaves a cache until the
 * backend answers, and the mutation stays pending until the affected lists
 * have refetched.
 *
 * On `deleted` and on `already_gone` (Q7: a 404 is "the report isn't there",
 * so the UI should converge, not error): lists and cached compares are
 * invalidated by their shared prefix, and this report's per-report entries
 * are removed — it no longer exists, so invalidating them would refetch a 404.
 *
 * Any other failure leaves every cache untouched and rejects to the caller,
 * so the list stays exactly as it was. The one exception is `validation`
 * (the response wasn't `{"deleted": string}`): the delete may have happened,
 * so the lists are refreshed to find out.
 */
export function useDeleteReport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string): Promise<DeleteReportOutcome> => {
      try {
        await researchLibraryApi.deleteReport(id);
        return "deleted";
      } catch (error) {
        if (error instanceof AppError && error.status === 404) return "already_gone";
        throw error;
      }
    },
    onSuccess: (_outcome, id) => {
      queryClient.removeQueries({ queryKey: reportKeys.detailsFor(id) });
      queryClient.removeQueries({ queryKey: reportKeys.statusFor(id) });
      return Promise.all([
        queryClient.invalidateQueries({ queryKey: reportKeys.lists() }),
        queryClient.invalidateQueries({ queryKey: reportKeys.compares() }),
      ]);
    },
    onError: (error) => {
      if (error instanceof AppError && error.kind === "validation") {
        void queryClient.invalidateQueries({ queryKey: reportKeys.lists() });
      }
    },
  });
}
