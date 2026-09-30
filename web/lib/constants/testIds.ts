/**
 * Test IDs for E2E/QA (§7, `docs/briefs/test-ids_convention.md`). One
 * `as const` object per `web/features/` domain, plus `APP` for shell/layout,
 * living in `lib/` so any feature can import it without crossing another
 * feature's boundary.
 *
 * Selector priority (05.1_Testing_Architecture.md AD-1/AD-3 — test the
 * accessibility contract, not internals):
 *   1. `getByRole` with an accessible name
 *   2. `getByLabel`
 *   3. `getByText`, for static, non-copy-volatile text only
 *   4. `getByTestId` — only where 1-3 can't uniquely identify the element
 *      (a row in a repeated list, a landmark-less region, LLM-generated or
 *      data-driven text).
 *
 * When a test ID is used, its value comes from here — `data-testid={
 * COMPANY_RESEARCH.sourceCard(n)}` — never an inline string literal.
 *
 * Convention (the legacy `frontend/src/constants/testIds/alphascribe.js`
 * shape, typed): camelCase keys; kebab-case values prefixed by the domain
 * (`"company-research-source-card-3"`); functions for dynamic IDs.
 *
 * The objects below start empty by design (brief §5 OQ-1/OQ-2) — no
 * retroactive sweep. An ID is added only in the same change as the test
 * that actually needs one, once role/label/text selection can't provide a
 * stable anchor.
 */

export const APP = {} as const;

export const WORKSPACE_HOME = {} as const;

export const COMPANY_RESEARCH = {} as const;

export const COMPARISON = {} as const;

export const RESEARCH_LIBRARY = {} as const;

export const LEARNING = {} as const;

export const ACCOUNT_SETUP = {} as const;
