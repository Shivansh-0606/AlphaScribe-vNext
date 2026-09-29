# Test IDs for E2E/QA (§7) — Constants File and Convention — Implementation Brief

**Date:** 2026-09-29. **Author:** Docs. **For:** Frontend Engineer (via Docs
Reviewer).

**Governing docs:**
- [`05.1_Testing_Architecture.md`](../frontend_architecture/05.1_Testing_Architecture.md)
  (✅ Approved (CTO)), AD-1/AD-3/AD-5;
- `CLAUDE.md`'s Test IDs convention note;
- the tracker's §7 row
  ([`Feature_Parity_Tracker.md`](../governance/Feature_Parity_Tracker.md)
  line 187: "No equivalent constants file in `web/` yet").

**Read this session:**
- legacy precedent: `frontend/src/constants/testIds/alphascribe.js`
  (+ `index.js`);
- current `web/`: `playwright.config.ts`, `tests/e2e/*.spec.ts`,
  `tests/README.md`, and every `data-testid` / `getByTestId` usage.

## 0. What exists today

**The legacy convention.** `frontend/` is frozen and used here as precedent
only.
- One registry file, re-exported from a barrel `index.js`, holding one
  `UPPER_SNAKE` object per screen or domain: `APP`, `NEW_REPORT`,
  `DASHBOARD`, `REPORT`, `COMPARE`, `AUTH`, `SETTINGS`, `INGEST`.
- Keys are camelCase. Values are kebab-case strings, usually prefixed by
  the screen (`"compare-run"`, `"auth-email"`).
- Dynamic IDs are functions: `sourceCard: (n) => \`source-card-${n}\``.
- Components apply them as `data-testid={REPORT.sourcesPanel}`, never as
  inline literals.
- Two comments record that old ID strings were deliberately kept through
  renames "so existing selectors keep working". That implies an external
  consumer at the time. The only trace of one in the repo today is the
  historical agent-run reports in `tests/reports/*.json`.

**`web/` today:**
- **No constants file exists.**
- **Product code has zero `data-testid` usages.** The only ones are on
  the internal component-preview fixture page
  (`app/test-fixtures/component-preview/page.tsx`, around 50 IDs such as
  `button-primary`). Foundation unit tests also set their own local IDs
  (`getByTestId("card")`).
- **A real Playwright E2E harness exists:** `tests/e2e/`, `npm run e2e`,
  an isolated port 4300. It holds three specs:
  - `auth.spec.ts` and `home.spec.ts` select entirely by **role/label/text**
    (`getByRole("button", { name: "Continue" })`, `getByLabel(/^Email/)`);
  - `component-fixtures.spec.ts` uses the fixture page's test IDs, for
    computed-style checks.
- **No E2E journey test exists yet for J-01…J-06.** `playwright.config.ts`'s
  own header says so: "a journey test only needs to be written... when a
  feature lands". All 15 migrated screens have only unit/component tests
  (Vitest + Testing Library) and live verification.

**What the frozen testing architecture says.** 05.1 does **not** mandate
test IDs. It points the other way:
- AD-1: component tests assert "accessibility (roles/names/keyboard)";
- AD-3: tests target "**public surfaces and boundaries**, not internals",
  so that "they assert contracts, not implementation";
- AD-5: accessibility is a merge gate.

Role/name-based selection tests the accessibility contract *and* the
behavior at once. A test ID tests neither. So **test IDs are the fallback,
not the default**, and the existing specs already follow that. `CLAUDE.md`
is compatible with this: it requires that test IDs, *when used*, come from
a constants file rather than inline literals. It does not require every
element to have one.

## 1. Goal

Establish `web/`'s test-ID convention and constants file, so that:
- the first E2E journey test, and any later one, has a sanctioned place to
  get a stable anchor where role/label selection genuinely can't provide
  one;
- no inline `data-testid` string literals accumulate in product code.

## 2. Scope

**In scope:**
1. **`web/lib/constants/testIds.ts`.** This is the path `CLAUDE.md`
   names. `lib/` is the shared layer, so features may import it without
   crossing feature boundaries.
   - Follow the legacy *shape*, typed: one `UPPER_SNAKE` object per IA
     domain, matching the `web/features/` modules (e.g. `WORKSPACE_HOME`,
     `COMPANY_RESEARCH`, `COMPARISON`, `RESEARCH_LIBRARY`, `LEARNING`,
     `ACCOUNT_SETUP`), plus `APP` for shell/layout.
   - Each object is `as const`, with camelCase keys, kebab-case values
     prefixed by the domain (`"company-research-source-card-3"`), and
     functions for dynamic IDs.
   - Initial contents: see §5 OQ-2.
2. **The selector-priority rule**, written as a short header comment in
   the file (no separate doc). It restates 05.1 and the practice the
   existing specs already follow:
   1. `getByRole` with an accessible name;
   2. `getByLabel`;
   3. `getByText`, for static, non-copy-volatile text only;
   4. `getByTestId`, **only** where 1–3 cannot uniquely identify the
      element. Typical cases: a specific row in a repeated list (a source
      card by index, a report row by id), a non-interactive region with no
      landmark or heading, or an element whose visible text is
      LLM-generated or data-driven and so unstable.

   When a test ID is used, its value comes from `testIds.ts`, applied as
   `data-testid={COMPANY_RESEARCH.sourceCard(n)}`. There are **no inline
   literals in product code**.
3. **One trivial unit test** (`testIds.test.ts`) asserting that every
   static value across all objects is unique. Duplicate IDs are the one
   mechanical failure this file can have.

**Out of scope:**
- **Legacy ID string compatibility.** Nothing in `web/` or its E2E suite
  consumes the legacy strings, and the legacy reports in `tests/reports/`
  are historical. Reuse the legacy *structure*, not its values.
- **The component-preview fixture page and foundation unit tests.** Their
  local IDs are test-fixture scaffolding, not product anchors, so they
  stay as they are.
- **A lint rule** banning inline `data-testid` literals (§5 OQ-3).
- **The retroactive sweep** (§5 OQ-1) — pending CTO-2's decision.

## 3. Approach

- There is **no barrel re-export**. The legacy `index.js` barrel only
  existed to allow split files later. One file, imported as
  `@/lib/constants/testIds`, is enough until it's genuinely too big to
  read.
- Where a test ID lands on a `foundation/` wrapper, pass it through as a
  normal prop. Foundation components already forward `data-testid`: the
  fixture page relies on this, e.g. `<Button data-testid=...>`. No wrapper
  changes should be needed. Confirm this per component as IDs are
  applied.
- Unit/component tests (Vitest + Testing Library) follow the same
  priority rule. Where one does need `getByTestId` on product code, it
  imports the same constant rather than repeating the string.

## 4. Acceptance Criteria

- [ ] `web/lib/constants/testIds.ts` exists, with the header comment
      stating the §2 selector-priority rule and the naming convention.
      Contents follow §5 OQ-2's decision.
- [ ] Every product `data-testid` introduced under this brief references
      a constant. `grep` shows no `data-testid="..."` string literals
      outside `app/test-fixtures/` and co-located `*.test.tsx`.
- [ ] `testIds.test.ts` asserts uniqueness of all static values.
- [ ] The full `web/` test suite, `tsc`, and lint are green. `npm run e2e`
      is unaffected.
- [ ] `CLAUDE.md`'s Test IDs note becomes stale once this lands: it says
      no equivalent exists. A replacement paragraph is proposed in §6.
      Applying it is **the user's own decision**. `CLAUDE.md` is
      project-level instruction configuration, and no AI session edits it
      on another session's request. It should be applied only once the
      file actually exists, so that it never describes something that
      isn't there yet.
- [ ] Tracker §7 "Test IDs for E2E/QA" row → **Migrated** (CTO-2
      decision, §5). The row note must record:
      - convention + scaffold + uniqueness test established;
      - IDs are applied on demand, per the role → label → text → testId
        priority rule, with no retroactive sweep, by decision;
      - the J-02 research-journey E2E is the first expected consumer,
        tracked as a follow-up, not a blocker.
      The §7 rollup row changes Not Started 3 → 2 and Migrated 5 → 6.
      Update both prose and table in the same diff.

## 5. Open Questions — decided by CTO-2, 2026-09-29

- **OQ-1: scope.** CTO-2 framed the choice as:
  - **(a)** a full retroactive `data-testid` sweep of all 15 migrated
    screens; or
  - **(b)** the file and convention now, applied going forward, with
    opportunistic retrofits.

  The §0 findings sharpen this. 05.1 and the existing E2E specs are
  role/label-first, and most interactive elements on the migrated screens
  are already uniquely addressable by role and name. Those are the
  foundation components, which carry accessible names because a11y is a
  merge gate. So option (a) would mostly add IDs no test needs, which is
  exactly the "brittle internal-coupled" pattern 05.1 AD-3 warns against,
  at real diff cost across every feature.

  **Docs recommends (b)**, sharpened to a concrete trigger: IDs are added
  when an E2E journey test (or component test) actually needs an anchor
  that §2's priority rule can't provide, in the same change as that test.
  "Opportunistic" then has a definite meaning rather than "whenever".
  **Decision: (b), with that trigger.** No retroactive sweep.
- **OQ-2: initial contents of the file.** Under (b), there is today no
  test that needs a product test ID, so an honest file starts nearly
  empty. Options:
  - **(i)** Ship the file with the convention header, the typed empty
    domain objects, and the uniqueness test. It is populated by the
    first journey test that needs it.
  - **(ii)** Pre-seed one root anchor per migrated screen (15 IDs,
    applied on each screen's root). This is cheap, but largely redundant
    with `getByRole("heading", { level: 1 })`, and it adds IDs before any
    consumer exists.
  - **(iii)** Don't create the file at all until the first journey test.
    But then the §7 row stays Not Started, and the convention stays
    undocumented in code.

  **Docs recommends (i).** It establishes the convention and the
  sanctioned home now, which is what the tracker row and `CLAUDE.md` ask
  for, without inventing anchors nobody uses. The obvious first consumer
  is a J-02 (company research) E2E journey, the trust-critical path
  05.1 AD-2 says to test first. It is flagged here as the natural
  follow-up, and is not scoped by this brief.
  **Decision: (i).** The file ships with the convention header, empty
  typed per-domain objects, and the uniqueness test. The J-02 research
  journey E2E is recorded as the natural first real consumer: a follow-up,
  not a blocker.
- **OQ-3: enforcing "no inline literals".** An ESLint rule (e.g.
  `no-restricted-syntax` on a `data-testid` JSX attribute with a string
  literal value) would enforce it mechanically. Docs recommends **not
  now**: with zero product IDs today, code review plus §4's grep check is
  enough. Add the rule if literals start appearing.
  **Decision: not now.**
- **Tracker status after this lands:** if OQ-1 is (b) and OQ-2 is (i), the
  row could reasonably move to **Migrated**, with the note "convention and
  file established; IDs applied on demand per the priority rule". That
  matches the precedent of promoting rows with documented, accepted
  deferrals. The alternative is to hold it at In Progress until a first
  real consumer exists. This is CTO-2's call.
  **Decision: Migrated**, with an "applied on demand" note. The narrower
  deliverable (convention + scaffold + test) is complete in itself.
  Holding the row open for an E2E test nothing is scheduling doesn't
  serve anyone.

## 6. Proposed `CLAUDE.md` replacement (for the user to apply after this lands)

This replaces the current "**Test IDs**" bullet under Conventions:

> - **Test IDs**: `web/lib/constants/testIds.ts` holds one `as const`
>   object per `web/features/` domain (plus `APP`), with camelCase keys,
>   kebab-case domain-prefixed values, and functions for dynamic IDs
>   (the legacy `frontend/src/constants/testIds/alphascribe.js` shape).
>   Tests select by role → label → text first (05.1); a `data-testid` is
>   the fallback, added in the same change as the test that needs it,
>   never proactively, and always from this file, never as an inline
>   literal. The objects start empty by design.
