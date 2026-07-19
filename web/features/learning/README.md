# Feature: `learning`

**Frozen IA domain:** Learning — overlays company/filings with learner-level explanation via shared company/source contracts.

Bounded context (02.2 AD-1). Communicates only through its public surface
(`index.ts`); internals are private (02.7 AD-2).

## Internal layers (02.1 AD-2)

- `ui/` — feature-specific presentation (composes design-system components).
- `application/` — behavior: use-cases, feature-scoped client state (Zustand), data hooks (TanStack Query), forms (RHF+Zod).
- `integration/` — feature-scoped API-contract access + Zod validation (if any).
- `internal/` — private helpers/types; never imported across the feature boundary.
