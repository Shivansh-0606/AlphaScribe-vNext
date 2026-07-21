/**
 * Route-segment loading UI (Next.js file convention — an automatic Suspense
 * boundary around the segment). Realizes the frozen Loading state (13
 * States): scoped, not focus-stealing, not conveyed by motion alone.
 */
export default function Loading() {
  return (
    <div role="status" aria-live="polite" className="text-muted-foreground text-sm">
      Loading…
    </div>
  );
}
