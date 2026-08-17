import { useEffect, useRef } from "react";

/**
 * Returns a ref for a `tabIndex={-1}` focus target, and moves focus there
 * whenever `key` changes to a non-null value — the "move attention to the
 * arriving response region" pattern (08_AI_Components.md Prompt Composer:
 * "submit moves attention to the arriving response region considerately").
 * The foundation-layer focus-management utility named but not built by
 * 04.5 AD-2; first extracted here from the pattern `FinancialsSection`
 * already shipped inline, now shared by `OverviewSection`/`CopilotPanel`.
 *
 * Never fires while `key` stays the same or null — an in-progress run's own
 * intermediate updates (Thinking → Streaming → Grounded) and unrelated
 * re-renders can't steal focus from wherever the user currently is; only an
 * actual transition to a new terminal key does.
 */
export function useFocusOnChange(key: string | null) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (key) ref.current?.focus();
  }, [key]);
  return ref;
}
