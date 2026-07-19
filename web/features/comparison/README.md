# Feature: `comparison`

**Frozen IA domain:** Comparison — DERIVED domain; references company subjects via the shared `company` contract, never company-research internals (02.2 AD-4).

Bounded context (02.2 AD-1). Communicates only through its public surface
(`index.ts`); internals are private (02.7 AD-2).

## Internal layers (02.1 AD-2)

- `ui/` — feature-specific presentation (composes design-system components).
- `application/` — behavior: use-cases, feature-scoped client state (Zustand), data hooks (TanStack Query), forms (RHF+Zod).
- `integration/` — feature-scoped API-contract access + Zod validation (if any).
- `internal/` — private helpers/types; never imported across the feature boundary.
