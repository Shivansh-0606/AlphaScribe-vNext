import { Banner } from "@/components/foundation/Banner";
import { Heading } from "@/components/foundation/Heading";

/**
 * Shared shell for global-nav destinations whose feature is Not Started yet
 * (Feature Parity Tracker). Keeps the destination reachable per the frozen
 * Navigation Structure (no dead links) without inventing its content.
 */
export function ComingSoon({ title, note }: { title: string; note: string }) {
  return (
    <div className="flex flex-col gap-6">
      <Heading level="h1">{title}</Heading>
      <Banner tone="info">{note}</Banner>
    </div>
  );
}
