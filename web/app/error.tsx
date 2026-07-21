"use client";

import { useEffect } from "react";

/**
 * Route-segment error boundary (03.11 AD-1 "Template boundary" / AD-2
 * unexpected-failure path). Scopes an unhandled error to this segment; the
 * root layout (header, skip link) keeps rendering above it, so navigation
 * stays available (03.11 AD-1, Design §20 Law 13 — never a dead end).
 */
export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Observability seam (03.11 AD-8 / 05.3) — wired to a real sink in a
    // later milestone; logging here keeps the failure visible in the interim.
    console.error(error);
  }, [error]);

  return (
    <div role="alert" aria-live="assertive" className="max-w-2xl">
      <h1 className="text-foreground text-2xl font-semibold tracking-tight">
        Something went wrong
      </h1>
      <p className="text-muted-foreground mt-3 text-base leading-relaxed">
        This section hit an unexpected error. Your place and any in-progress work are preserved —
        you can try again.
      </p>
      <button
        type="button"
        onClick={reset}
        className="border-border bg-surface text-foreground hover:bg-surface-hover mt-6 rounded-md border px-4 py-2 text-sm font-medium"
      >
        Try again
      </button>
    </div>
  );
}
