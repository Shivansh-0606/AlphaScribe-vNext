# AlphaScribe vNext — Feature Parity Tracker (frontend/ → web/)

| Field | Value |
|-------|-------|
| **Document Status** | 🟡 Living tracker (updated as `web/` implementation progresses) |
| **Version** | 1.0.0 |
| **Owner** | Engineering |
| **Approved By** | CTO directive, 2026-07-22 (see decision below) |
| **Last Updated** | 2026-07-22 |
| **Source of Truth** | Yes — this is the single gate for the Legacy Frontend Removal Plan |

---

## Governing decision (effective 2026-07-22)

- `web/` (Next.js 15) is the only active development frontend. All new feature work happens there.
- `frontend/` (CRA) is now a **legacy reference implementation** — read-only. No new features. Only critical bug fixes, and only if absolutely necessary.
- `frontend/` is **not** to be deleted until every row below reaches **Migrated** and passes validation.
- When this tracker reaches 100% and validation passes, a **Legacy Frontend Removal Plan** goes to the CTO for approval before any deletion. Until then, Repository Modernization Phase 3 (removing `frontend/`) stays paused.

## How to read this tracker

**Status values:**
- **Not Started** — no corresponding code exists in `web/` yet, not even scaffolding.
- **Scaffolded** — the frozen IA-domain folder/README/typed contract exists in `web/features/` or `web/lib/`, but no working UI or logic.
- **In Progress** — partial implementation exists in `web/`.
- **Migrated** — full functional parity in `web/`, verified working end-to-end.

**Current overall status: 0 of 13 user-facing routes migrated. Infrastructure-only groundwork exists for some.**

---

## 1. Public / marketing routes

| Route (`frontend/`) | Source file | `web/` equivalent | Status | Notes |
|---|---|---|---|---|
| `/` — Landing | `frontend/src/pages/Landing.jsx` | `web/app/page.tsx` | **In Progress** (rough draft only) | `web/app/page.tsx` currently renders a one-paragraph placeholder ("AlphaScribe is an AI-native Equity Research Workspace…") with no nav, no CTA, no marketing content. Not a real port of `Landing.jsx`. |
| `/docs` — Docs | `frontend/src/pages/Docs.jsx` | none | **Not Started** | No route, no content. |

## 2. Auth / account-setup routes (maps to `web/features/account-setup`)

| Route (`frontend/`) | Source file | `web/` equivalent | Status | Notes |
|---|---|---|---|---|
| `/login` — Login | `frontend/src/pages/Login.jsx` | `web/features/account-setup/` | **Scaffolded** | Feature folder + `index.ts` + README exist; `ui/`, `application/`, `integration/`, `internal/` are all empty (`.gitkeep` only). No login page, no form, no session call. |
| `/signup` — Signup | `frontend/src/pages/Signup.jsx` | `web/features/account-setup/` | **Scaffolded** | Same as above — no signup flow implemented. |
| `/forgot-password` — ForgotPassword | `frontend/src/pages/ForgotPassword.jsx` | `web/features/account-setup/` | **Scaffolded** | Same — no reset-password flow implemented. |
| `/settings` — Settings (account + LLM key mgmt) | `frontend/src/pages/Settings.jsx`, `frontend/src/components/LlmSettings.jsx` | `web/features/account-setup/` | **Scaffolded** | BYOK key management UI not present; `web/lib/types/auth.ts` and `authorization.ts` define typed contracts only, no implementation. |
| Auth session/guard pattern | `frontend/src/lib/auth.jsx` (`AuthProvider`, `RequireAuth`) | — | **Not Started** | No route-guard/middleware equivalent exists in `web/app/` yet (no Next.js middleware, no protected-route wrapper). |

## 3. Core research workflow (maps to `web/features/company-research` + `workspace-home`)

| Route (`frontend/`) | Source file | `web/` equivalent | Status | Notes |
|---|---|---|---|---|
| `/dashboard` — Dashboard (entry point, company search, recent research) | `frontend/src/pages/Dashboard.jsx`, `frontend/src/components/CompanyCombobox.jsx` | `web/features/workspace-home/` | **Scaffolded** | Folder/README/`index.ts` exist; `ui/application/integration/internal` empty. |
| `/app` — NewReport (report-generation workflow) | `frontend/src/pages/NewReport.jsx` | `web/features/company-research/` | **Scaffolded** | Folder exists, no logic. |
| `/ingest` — Ingest (SEC EDGAR fetch, paste, audio upload) | `frontend/src/pages/Ingest.jsx` | `web/features/company-research/` | **Not Started** | No ingest UI or API wiring anywhere in `web/`; `web/lib/api/fetch-client.ts` has zero endpoints defined (confirmed in its own doc comment: "Phase 5 scope: infrastructure only, no backend integration"). |
| `/reports/:id` — ReportView (brief, citations, scorecard, tone gauge, financials table) | `frontend/src/pages/ReportView.jsx`, `frontend/src/components/{ResearchBrief,Scorecard,ToneGauge,FinancialsTable,PipelineLog}.jsx` | `web/features/company-research/` | **Not Started** | None of these five presentational components have a `web/` counterpart; `web/components/research/` is a README placeholder only. |
| Live pipeline streaming (SSE progress log) | `frontend/src/components/PipelineLog.jsx`, `frontend/src/lib/jobs.jsx` | — | **Not Started** | No SSE client, no job-state store in `web/lib/state/` (placeholder README only). |
| Citation-aware markdown rendering | `frontend/src/lib/remarkCitations.js` | — | **Not Started** | No markdown rendering pipeline in `web/` yet (no `react-markdown` dependency installed). |

## 4. Comparison workflow (maps to `web/features/comparison`)

| Route (`frontend/`) | Source file | `web/` equivalent | Status | Notes |
|---|---|---|---|---|
| `/compare` — Compare (side-by-side reports, follow-up Q&A) | `frontend/src/pages/Compare.jsx` | `web/features/comparison/` | **Scaffolded** | Folder exists, no logic. |

## 5. Research history / library (maps to `web/features/research-library`)

| Route (`frontend/`) | Source file | `web/` equivalent | Status | Notes |
|---|---|---|---|---|
| Report history / resume session / saved exports (currently folded into Dashboard in `frontend/`, no dedicated route) | `frontend/src/pages/Dashboard.jsx` (partial) | `web/features/research-library/` | **Scaffolded** | This is a new, dedicated IA domain in the frozen `web/` architecture with no direct 1:1 legacy route — treat as a restructure, not a straight port. Folder exists, no logic. |

## 6. Net-new domain with no legacy equivalent

| `web/` IA domain | Status | Notes |
|---|---|---|
| `web/features/learning/` | **Scaffolded** (N/A for parity) | "Learner-level explanation" domain — does not exist in `frontend/` at all. Not a parity blocker; new scope, track separately from legacy migration. |

## 7. Shared/cross-cutting infrastructure

| Concern | `frontend/` | `web/` | Status | Notes |
|---|---|---|---|---|
| Watchlist store | `frontend/src/lib/watchlist.js` (`useSyncExternalStore`) | `web/lib/state/` | **Not Started** | `web/lib/state/` is a README placeholder only. |
| Client persistence (`usePersistedState`) | `frontend/src/lib/persist.js` | `web/lib/state/` | **Not Started** | Same placeholder. |
| Test IDs for E2E/QA | `frontend/src/constants/testIds/alphascribe.js` | — | **Not Started** | No equivalent constants file in `web/` yet. |
| API client | `frontend/src/lib/api.js` | `web/lib/api/fetch-client.ts`, `query-client.ts` | **In Progress** (infra only) | Typed fetch wrapper + TanStack Query client exist and are architecturally sound, but carry zero actual endpoint calls. |
| Toasts | `sonner` via `App.js` `<Toaster>` | `sonner` (installed dependency) | **In Progress** (infra only) | Same library, but no `<Toaster>` wired into `web/app/layout.tsx` yet — unverified. |
| App shell / nav layout | `frontend/src/components/AppLayout.jsx`, `AmbientBackground.jsx` | `web/components/layouts/` | **Scaffolded** | README placeholder only, no layout component built. |
| Error boundaries | ad hoc in `frontend/` | `web/app/error.tsx`, `web/app/global-error.tsx` | **Migrated** (framework-level) | Next.js App Router error boundaries exist and are wired at the framework level — this is genuinely ahead of `frontend/`'s equivalent. |
| Design tokens / theming | `frontend/src/index.css` (warm-light editorial-fintech theme) | `web/styles/tokens.css` | **Migrated** | Token set ported and verified rendering correctly (confirmed visually during Phase 2 verification — homepage renders the correct cream/ink-navy/emerald palette). |
| Foundation component library | `frontend/src/components/*` (ad hoc, page-specific) | `web/components/foundation/` (30+ generic components: Button, Input, Table, Dialog, etc.) | **Migrated** (foundation layer only) | This is a genuine, tested upgrade over `frontend/`'s page-specific components — but it's the generic layer, not the domain-specific ones (`ResearchBrief`, `Scorecard`, `ToneGauge`, `FinancialsTable`, `PipelineLog`, `CompanyCombobox`) listed in §3, which remain **Not Started**. |

---

## Rollup

| Category | Not Started | Scaffolded | In Progress | Migrated | Total |
|---|---|---|---|---|---|
| User-facing routes (§1–§5) | 6 | 7 | 1 | 0 | 14 |
| Cross-cutting infra (§7) | 3 | 1 | 2 | 2 | 8 |

**No user-facing route has reached Migrated.** The two fully-Migrated infra items (error boundaries, design tokens) and the foundation component library are real, verified progress — but they are groundwork, not features a user can actually complete a workflow with.

## Next steps

1. Prioritize `web/features/account-setup` (login/signup/forgot-password) — every other authenticated route depends on it per the frozen IA (`account-setup` is "precondition for all other features").
2. Wire `web/lib/api/fetch-client.ts` to real backend endpoints as each feature is built — it's currently a correct but unused shell.
3. Re-check this tracker after each feature lands; update its row from Scaffolded/Not Started to In Progress/Migrated with a one-line verification note (what was tested, not just "done").
4. Do not draft the Legacy Frontend Removal Plan until every row in §1–§5 reads Migrated and has been independently verified running end-to-end against the live backend — not just unit-tested in isolation.
