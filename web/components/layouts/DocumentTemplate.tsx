import { WorkspaceTemplate } from "./WorkspaceTemplate";

/**
 * DocumentTemplate (09 Component Inventory Templates) — "WorkspaceTemplate +
 * linear document + source panel + export", used by SCR-10 (Report View).
 * The source panel and export action are composed inside `ReportDocument`
 * itself (research-library/ui), not reserved as separate layout slots here —
 * same precedent as `ResearchTemplate`'s AI companion region, but here the
 * feature that fills the slot already exists, so there's nothing to reserve
 * ahead of time.
 */
export function DocumentTemplate({ children }: { children: React.ReactNode }) {
  return <WorkspaceTemplate>{children}</WorkspaceTemplate>;
}
