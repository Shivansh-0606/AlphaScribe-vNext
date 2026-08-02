import type { ReportDoc } from "../integration/schemas";

/**
 * Export (09_Component_Inventory.md `ReportDocument` — "Export preserves
 * reasoning and sources", J-06). No backend export endpoint exists (export
 * is a frontend concern — the report is already fetched); a client-side
 * markdown download via the native Blob/anchor APIs satisfies the
 * requirement with no new dependency (`jsPDF`, etc. would be scope beyond
 * what J-06 actually asks for: preserve reasoning + sources, not produce a
 * specific file format).
 */
export function buildExportMarkdown(report: ReportDoc): string {
  const sources = report.source_documents
    .map((source, i) => `${i + 1}. ${source.source}\n\n   > ${source.text}`)
    .join("\n\n");

  return [
    `# ${report.company_name ?? report.ticker} — ${report.query}`,
    "",
    report.draft_report,
    "",
    "## Sources",
    "",
    sources,
  ].join("\n");
}

export function downloadReportExport(report: ReportDoc): void {
  const blob = new Blob([buildExportMarkdown(report)], { type: "text/markdown" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${report.ticker}-report-${report.id}.md`;
  anchor.click();
  URL.revokeObjectURL(url);
}
