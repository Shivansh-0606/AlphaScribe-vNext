import { WorkspaceTemplate } from "./WorkspaceTemplate";

/**
 * ResearchTemplate (09 Component Inventory Templates) — "WorkspaceTemplate +
 * SectionNav + embedded AI side panel", used by SCR-06/07/08 (Company
 * Research, Comparison, Learning). Wraps `WorkspaceTemplate` rather than
 * re-rendering GlobalNav/Footer itself — this is why Company Research moved
 * to its own `(research)` route group instead of nesting under
 * `(workspace)`, which already applies `WorkspaceTemplate` once.
 *
 * The AI companion region is a persistent layout concern here (02.4 AD-5 —
 * reflows, never overlaps) but has no content yet: Company Research's
 * Copilot experience is Phase 4C. Reserving the slot now means later phases
 * fill it without another layout change.
 */
export function ResearchTemplate({
  sectionNav,
  children,
}: {
  sectionNav?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <WorkspaceTemplate>
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        {sectionNav ? <div className="lg:w-48 lg:shrink-0">{sectionNav}</div> : null}
        <div className="min-w-0 flex-1">{children}</div>
      </div>
    </WorkspaceTemplate>
  );
}
