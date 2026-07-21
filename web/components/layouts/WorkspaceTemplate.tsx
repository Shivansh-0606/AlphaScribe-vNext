import { Footer } from "./Footer";
import { GlobalNav } from "./GlobalNav";

/**
 * WorkspaceTemplate (09 Component Inventory Templates) — global header (root
 * shell) + global navigation + content + footer. ResearchTemplate/DocumentTemplate
 * (this template plus section nav / AI companion / source panel) are deferred
 * until Company Research, Comparison, Learning, and Report Viewer are built.
 */
export function WorkspaceTemplate({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-full flex-1 flex-col">
      <div className="mx-auto flex w-full max-w-6xl flex-1 gap-6 px-4 py-6 sm:px-6 lg:px-8">
        <GlobalNav />
        <div className="min-w-0 flex-1">{children}</div>
      </div>
      <Footer />
    </div>
  );
}
