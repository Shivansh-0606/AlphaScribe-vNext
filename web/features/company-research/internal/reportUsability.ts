import type { ReportDoc } from "../integration/schemas";

/**
 * The single, centralized answer to "is this completed report safe to show
 * as a normal AI Research Brief?" (Trust-First: `job.stage === "completed"`
 * only means the backend pipeline finished without erroring — it does NOT
 * mean the pipeline produced anything worth reading. Confirmed live: a run
 * can reach `status: "completed"` with `draft_report: ""` when the
 * extractor/synthesizer nodes fail against an unreachable LLM provider but
 * the pipeline framework itself doesn't treat that as a hard failure.
 *
 * A report is usable when it has real brief text AND at least one source —
 * an unsourced "brief" would violate the same Law 3 guarantee
 * (`AIResponseCard`'s own "never rendered without sources" rule) an empty
 * brief would. Every caller of `AIResponseCard` gets this check for free
 * rather than re-implementing it, per 03.14's "derive, don't duplicate"
 * placement guide — this is a `report` predicate, not job-lifecycle state
 * (`streamStages.ts`), so it belongs in its own file.
 */
export function isUsableReport(report: ReportDoc): boolean {
  return report.draft_report.trim().length > 0 && report.source_documents.length > 0;
}
