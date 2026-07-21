"use client";

import type { Route } from "next";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { Loader } from "@/components/foundation/Loader";
import { AppError } from "@/lib/errors/app-error";
import { useIdentity } from "../application/useAuth";

/**
 * The login wall as a single routing boundary (02.3 AD-6 / 03.6 AD-4) — the
 * `(workspace)` route group layout wraps its children in exactly this one
 * gate; no feature re-checks auth itself.
 *
 * Engineering note (flagged, not silently assumed): the session cookie is
 * issued by the backend's own origin (localhost:8001, cross-origin from the
 * Next.js app on :3001 — see backend CORS config), so a Next.js Server
 * Component can never see it via `next/headers cookies()`. True SSR-level
 * redirect would need a same-origin proxy/rewrite, which no frozen doc
 * specifies. This gate therefore enforces the boundary client-side via the
 * identity query, which is the frozen 03.6 AD-5 server-state source either
 * way — the boundary is still centralized, just not pre-paint. Raise to CTO
 * if SSR-level enforcement is required.
 */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const identity = useIdentity();
  const router = useRouter();
  const pathname = usePathname();

  const authenticated = !identity.isPending && !identity.isError && !!identity.data;

  useEffect(() => {
    if (identity.isPending || authenticated) return;
    // The redirect decision itself never changes (any non-authenticated
    // result -> /login, fail-closed) — this only decides which honest
    // sentence Login shows for *why*. A connectivity/server failure reads
    // very differently to a user than "you're simply signed out"; collapsing
    // both into an identical experience would itself be a silent failure.
    const isConnectivityFailure =
      identity.error instanceof AppError && identity.error.kind !== "auth_required";
    const params = new URLSearchParams({ next: pathname });
    if (isConnectivityFailure) params.set("reason", "connection");
    router.replace(`/login?${params.toString()}` as Route);
  }, [identity.isPending, identity.error, authenticated, pathname, router]);

  if (authenticated) {
    return <>{children}</>;
  }

  // "loading" and "unauthenticated" (mid-redirect) render the same holding
  // state — never a flash of protected content (frozen States: Authentication Required).
  return <Loader fullView label="Checking your session…" />;
}
