import type { ReportListItem } from "../integration/schemas";

/**
 * TODO(user-copy): every string below is a `TBD-user` PLACEHOLDER, not
 * approved product copy (report-deletion brief Q8 / §3.7; Design Constitution
 * §15: the project does not invent product copy). The user supplies the final
 * wording, replacing these values in THIS file only — components render from
 * here and tests assert through these constants, so nothing else changes.
 * Placeholders may merge to `main`; approved copy is a release/deploy gate.
 *
 * Open copy question for the user (same decision as the dialog wording): does
 * the dialog say that comparisons or Learning requests that used the report
 * will lose that context? The placeholders below do not.
 */

/** Names the report the way the dialog and the menu trigger must: ticker, query and date. */
function describeReport(report: ReportListItem): string {
  return `${report.ticker} — ${report.query} (${new Date(report.created_at).toLocaleDateString()})`;
}

export const REPORT_DELETE_COPY = {
  /** Accessible name of each row's menu trigger — includes the report so rows are distinguishable. */
  menuTriggerLabel: (report: ReportListItem) => `TBD-user: actions for ${describeReport(report)}`,
  menuDeleteItem: "TBD-user: Delete report",
  dialogTitle: "TBD-user: Delete this report?",
  dialogBody: (report: ReportListItem) =>
    `TBD-user: Permanently delete ${describeReport(report)}. This cannot be undone.`,
  confirmButton: "TBD-user: Delete",
  cancelButton: "TBD-user: Cancel",
  deleted: "TBD-user: Report deleted.",
  alreadyGone: "TBD-user: This report was already deleted.",
  failure: "TBD-user: Couldn't delete this report. Try again.",
} as const;
