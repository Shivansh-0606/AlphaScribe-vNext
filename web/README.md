# AlphaScribe vNext — Frontend

The Next.js 15 frontend for AlphaScribe, an AI-native equity research workspace, and the
active replacement for the frozen legacy `frontend/` (CRA) app. The foundation layer
(design tokens, component library — see
[`components/foundation/README.md`](components/foundation/README.md#milestone-2-status))
is complete, and product features are built on top of it in `features/`: account setup,
workspace home, company research (including financial statements), comparison, and Learning
(concept explanations) all live here today. See
[Architecture References](#architecture-references) for what governs what gets built next,
and [`docs/governance/Feature_Parity_Tracker.md`](../docs/governance/Feature_Parity_Tracker.md)
for migration status against the legacy app.

## Stack

Next.js 15 (App Router) · React 19 · TypeScript · Tailwind CSS v4 · shadcn/ui · Motion ·
Zustand · TanStack Query · React Hook Form · Zod. The stack is fixed — see
[Dependency Guidelines](../docs/frontend_architecture/05.5_Dependency_Guidelines.md); changing
it requires a Change Request.

## Setup

1. **Prerequisites:** Node.js ≥ 20.11 (see `engines` in `package.json`), npm.
2. **Install:**
   ```bash
   npm install
   ```
   This also wires Git hooks (`prepare` runs `scripts/setup-husky.mjs`, which points
   `core.hooksPath` at `web/.husky` since this app lives in a subdirectory of the repo).
3. **Environment:** copy `.env.example` to `.env.local` and adjust if needed. See
   [Environment Setup](#environment-setup) below.
4. **Run:**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3001](http://localhost:3001).

## Environment Setup

Configuration is typed and validated at `lib/config/env.ts` (05.4 Environment Configuration
Strategy) — it fails fast with a clear error if required config is missing or malformed, rather
than surfacing a confusing runtime error later.

- **Public/secret boundary is absolute:** only `NEXT_PUBLIC_*` variables are client-safe: they
  end up in the browser bundle. Secrets are server-only and are never given a `NEXT_PUBLIC_`
  prefix. There are no secrets in this app yet — the backend owns authentication.
- **BYOK AI keys are never configuration.** They are user-provided at runtime and handled per the
  Authentication Architecture (03.6) — never env vars, never client storage.
- The key set is identical across environments (local/staging/production); only values differ.

## Folder Structure

```
app/                    Next.js App Router — route composition only, no business logic
components/
  ui/                     shadcn/ui primitives (generated) — never imported outside foundation/
  foundation/              AlphaScribe wrappers of primitives (Button, Input, …)
  ai/                      AI-specific presentational components
  research/                Research-domain presentational components
  layouts/                 Shared layout templates
features/                one module per frozen Information Architecture domain:
  account-setup/ workspace-home/ company-research/ comparison/ learning/ research-library/
    ui/ application/ integration/ internal/    — internals; never imported across features
    index.ts                                    — the ONLY sanctioned public entry point
lib/                     foundation/shared — depends on nothing feature-specific
  api/                     integration layer: fetch wrapper, error normalization, query client
  state/                   shared (cross-feature) Zustand stores
  validation/              shared Zod schemas
  tokens/                  typed accessors for design tokens where TS needs them
  hooks/                   shared foundation hooks
  a11y/                    accessibility harness (focus mgmt, live regions, reduced-motion)
  motion/                  motion vocabulary bound to frozen motion tokens
  observability/           logging seam
  errors/                  typed error vocabulary
  utils/                   pure helpers (e.g. `cn`)
  config/                  typed env + app-wide constants
  types/                   shared cross-cutting types/contracts
providers/               global React providers, composed once at the root layout
styles/                  global CSS + the design-token layer (`tokens.css`)
tests/
  setup/                   Vitest setup, jest-dom/jest-axe wiring, provider-aware render helper
  e2e/                     Playwright journey + accessibility tests
public/assets/           exported icons/illustrations/logo (Design-owned, read-only)
```

Every directory carries its own `README.md` stating its responsibility and citing the governing
architecture doc — read the local README before adding to a directory you haven't touched before.
Full rationale: [02.1 Project Structure](../docs/frontend_architecture/02.1_Project_Structure.md).

**Module boundaries (enforced by convention, not yet by CI tooling — see 02.7):**

- Import a feature only through its `index.ts` public surface, never its internals.
- Dependencies point inward: Presentation → Feature → Application → Integration → Foundation.
- Never import `components/ui` (raw shadcn) outside `components/foundation`.

## Coding Standards

Full rationale: [05.8 Engineering Conventions](../docs/frontend_architecture/05.8_Engineering_Conventions.md).

- **Naming matches the frozen product vocabulary and design component names 1:1** — no synonyms.
- **Strong typing at boundaries:** no implicit `any` where data crosses a module/trust boundary;
  Zod schemas are the shape source of truth for anything crossing the API boundary.
- **Tokens or nothing:** every visual value references a token (`styles/tokens.css`) — a raw hex/
  px/ms value in component code is a defect (04.2 AD-3).
- **Absolute imports** (`@/…`) for cross-module references; relative imports stay within a module.
- A change updates its documentation in the same change.

## Development Workflow

- `npm run dev` — start the dev server.
- Before committing, `lint-staged` (via the pre-commit hook) runs ESLint + Prettier on staged
  files automatically.
- Before opening a PR, run `npm run verify` (typecheck + lint + format check + unit/component
  tests) locally — it's the same gate CI will apply.
- A change touching the design system (tokens, a new component variant) or an approved
  architectural decision follows the CR path — see
  [05.7 Frontend Governance](../docs/frontend_architecture/05.7_Frontend_Governance.md).

## Running Tests

| Command                           | What it runs                                                            |
| --------------------------------- | ----------------------------------------------------------------------- |
| `npm run test`                    | Unit + component tests (Vitest + React Testing Library), once           |
| `npm run test:watch`              | Same, in watch mode                                                     |
| `npm run test:coverage`           | Same, with a coverage report (v8 provider)                              |
| `npm run e2e:install`             | One-time: installs Playwright's browser binaries                        |
| `npm run e2e`                     | End-to-end/journey tests (Playwright) — builds and serves the app first |
| `npm run typecheck`               | `tsc --noEmit`                                                          |
| `npm run lint` / `lint:fix`       | ESLint                                                                  |
| `npm run format` / `format:check` | Prettier                                                                |
| `npm run verify`                  | typecheck + lint + format check + unit tests — the full local gate      |

**Test levels** (05.1 Testing Architecture): unit tests for pure logic, component tests for
behavior/states/accessibility, integration tests for a feature's cross-layer flow, E2E for the
approved user journeys once they exist. Accessibility is not a separate afterthought — component
tests use `jest-axe` and the E2E suite runs `@axe-core/playwright`; both are expected to report
zero violations before a change merges (04.5 AD-5 — accessibility is a merge gate, not optional).

## Architecture References

This app implements the frozen Frontend Architecture — it does not redecide it. Start here:

- [Frontend Architecture Constitution](../docs/frontend_architecture/01_Frontend_Architecture_Constitution.md) — governing principles
- [02 Application Architecture](../docs/frontend_architecture/02_Application_Architecture.md) — layers & boundaries
- [03 Data & State Architecture](../docs/frontend_architecture/03_Data_and_State_Architecture.md) — state ownership
- [04 Experience Infrastructure](../docs/frontend_architecture/04_Experience_Infrastructure.md) — tokens, theme, a11y, motion
- [05 Engineering Readiness](../docs/frontend_architecture/05_Engineering_Readiness.md) — testing, conventions, governance
- [Design Tokens](../docs/experience_design/10_Design_Tokens.md) — the canonical token catalogue (`styles/tokens.css` implements this)

If an implementation need conflicts with any frozen document, that is a **stop-and-raise-a-CR**
situation (05.7 Frontend Governance) — not a judgment call to make silently in code.

## Contribution Guide

1. Read the architecture doc(s) relevant to what you're changing before writing code — this
   department implements frozen decisions; it does not make new ones.
2. Keep changes small and cohesive (one reason to change per PR where practical).
3. `npm run verify` must pass locally before opening a PR.
4. A PR touching the design system, an architectural boundary, or product scope needs the CR path,
   not just code review.
5. Update the relevant `README.md` (this file, or the local directory README) in the same change
   if you alter a directory's responsibility.
