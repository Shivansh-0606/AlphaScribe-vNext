/**
 * Safe sessionStorage read/write/remove for small, non-sensitive string
 * values (03.14 row 18 — "Persistent state... sessionStorage (non-sensitive
 * client)... within session"; row 1 — client UI state may persist to
 * sessionStorage). First concrete use: `OverviewSection`'s retry-after-
 * reload query. `sessionStorage` (never `localStorage`, per 03.14 row 18/19
 * and the explicit privacy call here) — scoped to the tab, gone when it
 * closes, matching "the lifetime required to support retry" rather than
 * persisting indefinitely like `localStorage` would.
 *
 * Every call is wrapped: sessionStorage can throw (private browsing, quota,
 * a sandboxed iframe) and a stored value can be anything by the time it's
 * read back (another tab, a stale schema) — neither may ever crash the
 * screen, so failures degrade to "as if nothing were stored" rather than
 * throwing (mirrors the legacy `frontend/src/lib/persist.js` precedent).
 */

export function readSessionValue(key: string): string | null {
  try {
    return sessionStorage.getItem(key);
  } catch {
    return null;
  }
}

export function writeSessionValue(key: string, value: string): void {
  try {
    sessionStorage.setItem(key, value);
  } catch {
    // Quota exceeded / storage disabled — retry-after-reload just won't work.
  }
}

export function removeSessionValue(key: string): void {
  try {
    sessionStorage.removeItem(key);
  } catch {
    // Nothing to clean up if storage was never writable.
  }
}
