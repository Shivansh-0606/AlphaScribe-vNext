/**
 * Shared query-key factory for report server state (CTO architecture ruling
 * 2026-10-05, report-deletion brief §3.3 / Q5). Entity keys only: no fetching
 * and no feature imports (02.2 AD-2/AD-3) — `feature` is a plain string so a
 * new feature never needs an edit here.
 *
 * Every key shares the `"reports"` root, and the report id comes BEFORE the
 * feature name in per-report keys, so one prefix by id (`detailsFor` /
 * `statusFor`) reaches every feature's entry for that report, and one list or
 * compare prefix (`lists` / `compares`) reaches every feature's cached lists
 * and compares. That is what lets a delete refresh them all without any
 * feature importing another.
 */
const ROOT = "reports" as const;

export const reportKeys = {
  list: (feature: string, ...params: Array<string | number>) =>
    [ROOT, "list", feature, ...params] as const,
  lists: () => [ROOT, "list"] as const,

  detail: (id: string, feature: string) => [ROOT, "detail", id, feature] as const,
  detailsFor: (id: string) => [ROOT, "detail", id] as const,

  status: (id: string, feature: string) => [ROOT, "status", id, feature] as const,
  statusFor: (id: string) => [ROOT, "status", id] as const,

  /** Sorted here too, so a differently ordered selection of the same ids is one cache entry. */
  compare: (ids: readonly string[]) => [ROOT, "compare", ...[...ids].sort()] as const,
  compares: () => [ROOT, "compare"] as const,
};
