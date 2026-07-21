"use client";

import { useSyncExternalStore } from "react";

const QUERY = "(prefers-reduced-motion: reduce)";

function subscribe(callback: () => void) {
  const mql = window.matchMedia(QUERY);
  mql.addEventListener("change", callback);
  return () => mql.removeEventListener("change", callback);
}

function getSnapshot() {
  return window.matchMedia(QUERY).matches;
}

function getServerSnapshot() {
  return false;
}

/**
 * The reduced-motion signal (04.5 AD-2 accessibility harness). Components
 * that use `lib/motion` don't need this directly — it's consumed there — but
 * it's exposed for the rare component that gates non-Motion-library behavior
 * (e.g. choosing not to auto-play something) on the same preference.
 */
export function useReducedMotion(): boolean {
  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot);
}
