"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useAuthStatus } from "../application/useAuth";

/**
 * Landing's (SCR-01) returning-user routing — the inverse of `AuthGate`: a
 * signed-in user visiting a public marketing page is routed onward rather
 * than shown marketing (06 SCR-01 Edge Cases). Renders nothing, so the
 * marketing page around it stays server-rendered and content-first (06:
 * "entry action available as soon as rendered") — only this child needs the
 * client-side identity check, and a loading/unauthenticated/error status
 * all render the page normally rather than gating it the way `AuthGate` does.
 */
export function ReturningUserRedirect() {
  const status = useAuthStatus();
  const router = useRouter();

  useEffect(() => {
    if (status.state === "authenticated") {
      router.replace("/workspace");
    }
  }, [status.state, router]);

  return null;
}
