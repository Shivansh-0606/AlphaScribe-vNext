# AlphaScribe vNext — Feature Parity Tracker (frontend/ → web/)

| Field | Value |
|-------|-------|
| **Document Status** | 🟡 Living tracker (updated as `web/` implementation progresses) |
| **Version** | 1.0.0 |
| **Owner** | Engineering |
| **Approved By** | CTO directive, 2026-07-22 (see decision below) |
| **Last Updated** | 2026-07-22 (Milestone 3, Phase 2: Workspace Home) |
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

**Current overall status: 0 of 15 user-facing routes migrated. Auth (login/signup/forgot-password/settings) and the authenticated app shell are In Progress as of Milestone 3 Phase 1; the remaining research/comparison/learning/library workflows are still Not Started/Scaffolded.**

---

## 1. Public / marketing routes

| Route (`frontend/`) | Source file | `web/` equivalent | Status | Notes |
|---|---|---|---|---|
| `/` — Landing | `frontend/src/pages/Landing.jsx` | `web/app/(public)/page.tsx` | **In Progress** | Moved into the `(public)` route group under `PublicTemplate`; now has the value-prop copy plus "Get started"/"Sign in" CTAs to the real signup/login routes (SCR-01 primary/secondary actions). Still missing the wireframe's trust-positioning copy and footer legal content — not a full port of `Landing.jsx`. |
| `/docs` — Docs | `frontend/src/pages/Docs.jsx` | none | **Not Started** | No route, no content. |

## 2. Auth / account-setup routes (maps to `web/features/account-setup`)

| Route (`frontend/`) | Source file | `web/` equivalent | Status | Notes |
|---|---|---|---|---|
| `/login` — Login | `frontend/src/pages/Login.jsx` | `web/app/(public)/login/`, `web/features/account-setup/ui/LoginForm.tsx` | **In Progress** | RHF+Zod form wired to real `POST /api/auth/login`; success redirects to `/workspace` (or a validated `?next=`). Verified: typecheck/lint/format clean, component tests cover empty-submit validation and the success→redirect path (`LoginForm.test.tsx`). Not yet verified against a live backend process end-to-end. |
| `/signup` — Signup | `frontend/src/pages/Signup.jsx` | `web/app/(public)/signup/`, `web/features/account-setup/ui/SignupForm.tsx` | **In Progress** | Same pattern, wired to `POST /api/auth/register`. Verified via typecheck/lint/tests only, not against a live backend. |
| `/forgot-password` — ForgotPassword | `frontend/src/pages/ForgotPassword.jsx` | `web/app/(public)/forgot-password/`, `web/features/account-setup/ui/ForgotPasswordForm.tsx` | **In Progress** | Two-step flow (request OTP → verify OTP + new password) wired to `/api/auth/forgot-password` + `/api/auth/reset-password`. Verified via typecheck/lint/tests only. |
| `/settings` — Settings (account + LLM key mgmt) | `frontend/src/pages/Settings.jsx`, `frontend/src/components/LlmSettings.jsx` | `web/app/(workspace)/settings/`, `web/features/account-setup/ui/SettingsPanel.tsx` | **In Progress** | Change password, sign out, sign out everywhere, and delete-account (confirm dialog) built and wired to their endpoints. BYOK/LLM key management is **not** built here — deliberately out of scope (it's an authorization/AI-access concern, 03.7, not account authentication) and remains its own gap. |
| Auth session/guard pattern | `frontend/src/lib/auth.jsx` (`AuthProvider`, `RequireAuth`) | `web/features/account-setup/ui/AuthGate.tsx` | **In Progress** | The login wall is enforced once, at the `(workspace)` route group's layout (`AuthGate` wrapping `WorkspaceTemplate`), per 02.3 AD-6/03.6 AD-4 — not scattered per-component checks. **Engineering note for review:** the session cookie is issued by the backend's own origin (cross-origin from the Next.js app — see `backend/server.py` CORS config), so a Next.js Server Component can never read it via `next/headers`; this enforces client-side via the identity query rather than as an SSR redirect. Flag if true SSR-level enforcement is required — it would need a same-origin proxy/rewrite not specified in any frozen doc. |

## 3. Core research workflow (maps to `web/features/company-research` + `workspace-home`)

| Route (`frontend/`) | Source file | `web/` equivalent | Status | Notes |
|---|---|---|---|---|
| `/dashboard` — Dashboard (entry point, company search, recent research) | `frontend/src/pages/Dashboard.jsx`, `frontend/src/components/CompanyCombobox.jsx` | `web/app/(workspace)/workspace/`, `web/features/workspace-home/` | **In Progress** | **Correction to the Phase 1 note previously here:** the claim "needs a backend search endpoint that doesn't exist yet" was wrong — `GET /api/companies/search` and `GET /api/reports` already exist and work (confirmed by reading `backend/server.py` directly before starting Phase 2). Company search (debounced, wired to the real endpoint) and Recent Research (wired to `GET /reports`, curated `is_sample` entries excluded) are now real, with Loading/Empty/Error(non-blocking, retryable)/Loaded states per the frozen SCR-04 UX spec. Deliberately NOT ported from `Dashboard.jsx`: the stats strip, Watchlist, Quick Actions rail, and Coverage tags — none of those appear in the frozen SCR-04 wireframe/UX spec, so building them would be inventing product behavior beyond the approved docs. Selecting a company or a past report routes to `/research?ticker=`, which is still the Phase-1 stub (Company Research itself is a later phase) — an honest hand-off, not a dead end. Verified: typecheck/lint/format clean, 10 new component tests (search debounce+select+Enter-submit+error, recent-research loading/empty/sample-filtering/error-retry/navigate). Not yet verified against a live backend process (none was running during this phase; the mocked tests assert against the exact response shape read from `backend/server.py`, not a guess). |
| `/app` — NewReport (report-generation workflow) | `frontend/src/pages/NewReport.jsx` | `web/features/company-research/` | **Scaffolded** | Folder exists, no logic. `web/app/(workspace)/research/` now renders a labeled stub for the global-nav "Research" destination (same nav-reachability rationale as Compare) — not the feature itself. |
| `/ingest` — Ingest (SEC EDGAR fetch, paste, audio upload) | `frontend/src/pages/Ingest.jsx` | `web/features/company-research/` | **Not Started** | No ingest UI or API wiring anywhere in `web/`; `web/lib/api/fetch-client.ts` has zero endpoints defined (confirmed in its own doc comment: "Phase 5 scope: infrastructure only, no backend integration"). |
| `/reports/:id` — ReportView (brief, citations, scorecard, tone gauge, financials table) | `frontend/src/pages/ReportView.jsx`, `frontend/src/components/{ResearchBrief,Scorecard,ToneGauge,FinancialsTable,PipelineLog}.jsx` | `web/features/company-research/` | **Not Started** | None of these five presentational components have a `web/` counterpart; `web/components/research/` is a README placeholder only. |
| Live pipeline streaming (SSE progress log) | `frontend/src/components/PipelineLog.jsx`, `frontend/src/lib/jobs.jsx` | — | **Not Started** | No SSE client, no job-state store in `web/lib/state/` (placeholder README only). |
| Citation-aware markdown rendering | `frontend/src/lib/remarkCitations.js` | — | **Not Started** | No markdown rendering pipeline in `web/` yet (no `react-markdown` dependency installed). |

## 4. Comparison workflow (maps to `web/features/comparison`)

| Route (`frontend/`) | Source file | `web/` equivalent | Status | Notes |
|---|---|---|---|---|
| `/compare` — Compare (side-by-side reports, follow-up Q&A) | `frontend/src/pages/Compare.jsx` | `web/features/comparison/` | **Scaffolded** | Folder exists, no logic. `web/app/(workspace)/compare/` now renders a labeled "not built yet" stub so the global-nav destination isn't a dead link — status unchanged since it isn't the feature. |

## 5. Research history / library (maps to `web/features/research-library`)

| Route (`frontend/`) | Source file | `web/` equivalent | Status | Notes |
|---|---|---|---|---|
| Report history / resume session / saved exports (currently folded into Dashboard in `frontend/`, no dedicated route) | `frontend/src/pages/Dashboard.jsx` (partial) | `web/features/research-library/` | **Scaffolded** | This is a new, dedicated IA domain in the frozen `web/` architecture with no direct 1:1 legacy route — treat as a restructure, not a straight port. Folder exists, no logic. `web/app/(workspace)/library/` now renders a labeled stub (same nav-reachability rationale as Compare). |

## 6. Net-new domain with no legacy equivalent

| `web/` IA domain | Status | Notes |
|---|---|---|
| `web/features/learning/` | **Scaffolded** (N/A for parity) | "Learner-level explanation" domain — does not exist in `frontend/` at all. Not a parity blocker; new scope, track separately from legacy migration. `web/app/(workspace)/learning/` now renders a labeled stub (same nav-reachability rationale as Compare/Research Library). |

## 7. Shared/cross-cutting infrastructure

| Concern | `frontend/` | `web/` | Status | Notes |
|---|---|---|---|---|
| Watchlist store | `frontend/src/lib/watchlist.js` (`useSyncExternalStore`) | `web/lib/state/` | **Not Started** | `web/lib/state/` is a README placeholder only. |
| Client persistence (`usePersistedState`) | `frontend/src/lib/persist.js` | `web/lib/state/` | **Not Started** | Same placeholder. |
| Test IDs for E2E/QA | `frontend/src/constants/testIds/alphascribe.js` | — | **Not Started** | No equivalent constants file in `web/` yet. |
| API client | `frontend/src/lib/api.js` | `web/lib/api/fetch-client.ts`, `query-client.ts` | **In Progress** | Wired so far: the nine `/api/auth/*` endpoints (`account-setup/integration/api.ts`) and `GET /api/companies/search` + `GET /api/reports` (`workspace-home/integration/api.ts`), each with a matching Zod schema. Ingest, report generation/streaming, and comparison endpoints still have zero calls from `web/`. |
| Toasts | `sonner` via `App.js` `<Toaster>` | `sonner` (installed dependency) | **Migrated** | Confirmed: `<Toaster>` is mounted in `web/providers/AppProviders.tsx` and is exercised by real call sites now (account-setup mutations call `toast.success`/`toast.error` on real success/failure paths). |
| App shell / nav layout | `frontend/src/components/AppLayout.jsx`, `AmbientBackground.jsx` | `web/components/layouts/` (`PublicTemplate`, `WorkspaceTemplate`, `GlobalNav`, `Footer`) | **In Progress** | Built and composing real routes: `PublicTemplate` (Landing + auth pages) and `WorkspaceTemplate` (global nav + footer, gated by `AuthGate`) per the frozen 02.4 template hierarchy. `ResearchTemplate`/`DocumentTemplate` (section nav, AI companion, source panel) are not built — deferred to the phase that builds Company Research/Comparison/Learning/Report Viewer. |
| Error boundaries | ad hoc in `frontend/` | `web/app/error.tsx`, `web/app/global-error.tsx` | **Migrated** (framework-level) | Next.js App Router error boundaries exist and are wired at the framework level — this is genuinely ahead of `frontend/`'s equivalent. |
| Design tokens / theming | `frontend/src/index.css` (warm-light editorial-fintech theme) | `web/styles/tokens.css` | **Migrated** | Token set ported and verified rendering correctly (confirmed visually during Phase 2 verification — homepage renders the correct cream/ink-navy/emerald palette). |
| Foundation component library | `frontend/src/components/*` (ad hoc, page-specific) | `web/components/foundation/` (30+ generic components: Button, Input, Table, Dialog, etc.) | **Migrated** (foundation layer only) | This is a genuine, tested upgrade over `frontend/`'s page-specific components — but it's the generic layer, not the domain-specific ones (`ResearchBrief`, `Scorecard`, `ToneGauge`, `FinancialsTable`, `PipelineLog`, `CompanyCombobox`) listed in §3, which remain **Not Started**. |

---

## Rollup

| Category | Not Started | Scaffolded | In Progress | Migrated | Total |
|---|---|---|---|---|---|
| User-facing routes (§1–§5) | 5 | 3 | 7 | 0 | 15 |
| Cross-cutting infra (§7) | 3 | 0 | 2 | 4 | 9 |

*(The row/total counts above have also been corrected against the actual table rows — the prior version undercounted both sections by one row each.)*

**No user-facing route has reached Migrated.** Auth (login, signup, forgot-password, settings-account, the auth-gate pattern) and Workspace Home moved from Scaffolded/Not-Started to **In Progress** across Milestone 3 Phase 1–2, verified by `npm run verify` (typecheck + lint + format + 177 passing vitest tests). Toasts moved to **Migrated**. Everything else in §3–§5 (real ingest, report view, comparison, research library content) is still Scaffolded/Not Started — those still need Company Research (Phase 4) before they have anywhere real to land.

## Next steps

1. ~~Prioritize `web/features/account-setup`~~ — done for login/signup/forgot-password/settings-account in Phase 1. Remaining: BYOK/AI-access setup (a 03.7 authorization concern, separate from authentication).
2. ~~Build `web/features/workspace-home` for real~~ — done in Phase 2: company search and recent research are real, wired to already-existing backend endpoints (`GET /companies/search`, `GET /reports`) — the earlier belief that no search endpoint existed was a Phase-1 mistake, corrected above. Both destinations still hand off to the `/research` stub since Company Research itself isn't built.
3. Build Company Research (Overview/Financials/Filings/AI Insights/Export, SSE pipeline log, citation markdown, `ResearchTemplate` layout) — the next natural phase, since it's what `/research?ticker=` and every "recent research" item are already waiting to hand off to.
4. Wire `web/lib/api/fetch-client.ts` to each remaining domain's endpoints as its feature is built (ingest, report generation/streaming, comparison) — **check `backend/server.py` directly first**, the way Phase 2 should have from the start, rather than assuming an endpoint doesn't exist.
5. Re-check this tracker after each feature lands; update its row from Scaffolded/Not Started to In Progress/Migrated with a one-line verification note (what was tested, not just "done").
6. Do not draft the Legacy Frontend Removal Plan until every row in §1–§5 reads Migrated and has been independently verified running end-to-end against the live backend — not just unit-tested in isolation.
