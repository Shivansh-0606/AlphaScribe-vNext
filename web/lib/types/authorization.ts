/**
 * Authorization scaffolding (03.7) — types only. Exactly the frozen MVP
 * surface (03.7 AD-2): authenticated + valid AI access. No roles, tiers, or
 * RBAC — inventing more would breach scope (03.7 "no invented scope"). This
 * is UX-level reflection only; the backend is the enforcement authority
 * (03.7 AD-1) regardless of what this type reports.
 */
export type AiAccessStatus =
  | { state: "loading" }
  | { state: "not_configured" }
  | { state: "valid"; mode: "managed" | "byok" }
  | { state: "invalid"; reason: string };
