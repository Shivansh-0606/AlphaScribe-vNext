"use client";

import { useEffect } from "react";

/**
 * Root error boundary (03.11 AD-1 "Root boundary catches anything unhandled;
 * app never white-screens"). Only fires if the root layout itself throws, so
 * it must render its own <html>/<body> — nothing above it, including the
 * Tailwind stylesheet from the failed root layout's <head>, can be relied on.
 * Inline styles (not tokens/Tailwind classes) are the documented, correct
 * pattern here — a deliberate, narrowly-scoped exception to "tokens or
 * nothing" (04.2 AD-3), not a lapse in it. Values are the frozen
 * --border/--surface hex equivalents, hardcoded only because this boundary
 * cannot assume its stylesheet loaded.
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <html lang="en">
      <body style={{ fontFamily: "system-ui, sans-serif", padding: "3rem 1.5rem" }}>
        <div role="alert" aria-live="assertive" style={{ maxWidth: "36rem" }}>
          <h1 style={{ fontSize: "1.5rem", fontWeight: 600 }}>AlphaScribe hit a problem</h1>
          <p style={{ marginTop: "0.75rem", lineHeight: 1.6 }}>
            The application failed to load. Reloading usually resolves this.
          </p>
          <button
            type="button"
            onClick={reset}
            style={{
              marginTop: "1.5rem",
              padding: "0.5rem 1rem",
              border: "1px solid #DBD5CC",
              borderRadius: "4px",
              background: "#F6F3EF",
              cursor: "pointer",
            }}
          >
            Try again
          </button>
        </div>
      </body>
    </html>
  );
}
