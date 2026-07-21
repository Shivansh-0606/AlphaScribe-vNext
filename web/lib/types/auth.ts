/**
 * Authentication scaffolding (03.6) — types only. Auth status is
 * backend-authoritative, derived server state (03.6 AD-5), never a
 * client-held flag; it is read via a TanStack Query identity query owned by
 * the `account-setup` feature once that feature is built (03.6 AD-4 — the
 * login wall is a routing boundary, not a per-component check). No endpoint
 * exists yet — this shape is the contract other modules type against.
 */
export type AuthStatus =
  { state: "loading" } | { state: "unauthenticated" } | { state: "authenticated"; userId: string };
