# Legacy Frontend Removal Plan (`frontend/` → deletion)

| Field | Value |
| --- | --- |
| **Document Status** | 📝 **DRAFT — NOT APPROVED.** A plan only. Nothing in it has been executed. Six user rulings/directions are recorded (§1.4, §3, §4.1, §5); the plan stays unapproved until the user's final sign-off **and** until the F1 pre-deletion gate (§4.1) is recorded as done **and** the user has ruled on the legacy-only capabilities found 2026-10-02 (F6, §3 #12–#19, §4.1 item 5), each of which has **no recorded drop decision** (related records are cited per row). |
| **Date** | 2026-10-01 |
| **Author** | Docs generator 3 (for CTO 3; review via Docs Reviewer) |
| **Repo state when written** | `main` == `origin/main` == `5b5f5a8` |
| **Gate document** | [`Feature_Parity_Tracker.md`](Feature_Parity_Tracker.md) ("Source of Truth": "the single gate for the Legacy Frontend Removal Plan") |
| **Authority for the plan** | Tracker "Governing decision" (2026-07-22); **GRA-001** in [`change_requests/00_Change_Request_Register.md`](change_requests/00_Change_Request_Register.md) (CTO ruling 2026-07-21: `web/` is canonical, `frontend/` is non-canonical; its "Not yet executed" paragraph records that archiving/labeling `frontend/` and reconciling `CLAUDE.md` were deliberately left for explicit confirmation). This plan is the vehicle for the `frontend/` half of GRA-001; the `CLAUDE.md` half stays the user's (§5). |

**This document does not authorize anything.**
- It does not delete, move, or tag anything.
- It edits no other file. In particular it edits no `CLAUDE.md`; the `CLAUDE.md` lines it cites are listed in §2 for the **user** to change.
- Final approval and the deletion itself are the **user's** (§5).

Every claim below was checked against the repository on the date above, not taken from memory. How each was checked is in the Appendix.

---

## 1. Gate evidence

### 1.1 What the gate says

- Tracker, Governing decision: *"`frontend/` is not to be deleted until every row below reaches **Migrated** and passes validation. When this tracker reaches 100% and validation passes, a Legacy Frontend Removal Plan goes to the CTO for approval before any deletion."*
- Tracker, Next steps #17: *"Do not draft the Legacy Frontend Removal Plan until every row in §1–§5 reads Migrated and has been independently verified running end-to-end against the live backend — not just unit-tested in isolation."*

**Reading of the gate:**
- §1–§5 is 15 Migrated + 1 Not Started (`/docs`, deliberately never built). **Ruled exempt by the user, 2026-10-01 (G1, §1.4).**
- §7 has 2 Not Started + 3 In Progress. "Every row below" (Governing decision) versus "§1–§5" (#17) was ambiguous. **Ruled by the user, 2026-10-01 (G2, §1.4): §7 is not part of the gate.**
- With both rulings, the gate as the user has read it (every §1–§5 row Migrated, `/docs` exempt) is met on paper, subject to the thin-verification flags in §1.3, which remain open. **F6 (found 2026-10-02) qualifies this:** several legacy-only capabilities are carried inside rows that read Migrated, with no recorded drop decision (§3 #12–#19; related records are cited per row). The tracker statuses are not changed by this plan; the user rules on those items before deletion.

### 1.2 Per-row status and verification record (§1–§6)

"Evidence" is the tracker row's own record plus git history. Dates are those recorded in the tracker or brief headers; commits are from `git log`.

| § | Row | Status | Live-verification record | Evidence |
|---|---|---|---|---|
| 1 | `/` Landing | Migrated | Signed-out render and signed-in redirect verified live 2026-09-28 (disposable account, deleted) | Brief `docs/briefs/landing_scr-01.md` (`db2f216`); build `7ef23dc`; promotion `3871891` |
| 1 | `/docs` | **Not Started — by decision** | n/a | Milestone 3 freeze closeout, 2026-08-03: not in `05_Screen_Inventory.md`; "will not be built" (see §3 row 1) |
| 2 | `/login` | Migrated | Auth hardening pass 2026-08-15: full login / change-password / sign-out / sign-out-everywhere / forgot / reset / delete cycle | Tracker prose only (see flag F3) |
| 2 | `/signup` | Migrated | Phase-time only: real signup, session, redirect to `/setup`, confirmed via network tab (before the 2026-08-03 freeze) | Tracker row (see flag F2) |
| 2 | `/forgot-password` | Migrated | 2026-08-15 pass (as `/login`) | Tracker prose only |
| 2 | `/settings` | Migrated | 2026-08-15 pass | Tracker prose only |
| 2 | Auth session/guard | Migrated | Phase-time + 2026-08-15: `AuthGate` never let an unauthenticated request through, never falsely bounced an authenticated one | Tracker prose only |
| 2 | AI Access Setup | Migrated | Phase-time only: a real invalid Gemini key (backend made a real Google call; got a real `400`; UI showed it inline); Managed → `/workspace` | Tracker row (see flags F1, F2) |
| 3 | `/dashboard` (Workspace Home) | Migrated | Hardening 2026-09-15, zero defects | `docs/briefs/hardening_migrated-parity-pass.md`; promotion `f96b69b` |
| 3 | `/app` NewReport; `/ingest`; `/reports/:id` brief; SSE streaming; citation rendering + AI Insights | Migrated (5 rows, one promotion) | Six sub-slices 2026-09-19 → 2026-09-21: Overview, Financials, Filings (09-19), Changes (09-20), AI Insights, Export (09-21). Real defects found and fixed (e.g. Financials `_infer_unit`; the `useReport`-discards-`status` pair; commit `4214b905`) | Briefs `docs/briefs/hardening_company-research-{overview,financials,filings,changes,ai-insights,export}.md`; promotion `55db76f` (committed 2026-09-23) |
| 4 | `/compare` | Migrated | Hardening 2026-09-16, zero defects; own + sample MSFT comparison | `docs/briefs/hardening_comparison.md`; promotion `2ca6689` |
| 5 | Research Library | Migrated | Hardening 2026-09-18, zero defects | `docs/briefs/hardening_research-library.md`; promotion `8962906` |
| 6 | `learning/` (N/A for parity) | Migrated | Re-verified live 2026-09-26: `context_report_id` path 4/4 (incl. 2/2 on the exact failing trigger); cross-tenant canary | `docs/briefs/hardening_learning.md` §11; promotion `fcb2010`; fixes `6d65aec`, `94b01ba`, `d937e68`, `5b5f5a8` |

Row-by-row recount of the tracker (done for this plan): §1 = 1 Migrated + 1 Not Started; §2 = 6 Migrated; §3 = 6 Migrated; §4 = 1; §5 = 1. That is 15 Migrated + 1 Not Started = 16, matching the Rollup.

### 1.3 Rows whose verification is thin

These are flags, not verdicts. Each says what is missing and the cheapest way to close it.

- **F1 — BYOK happy path was never live-verified. STATUS: OPEN, not closed. The user will verify it with their own key before deletion; recorded as a user-owned pre-deletion gate in §4.1 (user direction 2026-10-01, relayed by CTO 3).**
  - The AI Access Setup row records only an *invalid*-key rejection and the Managed path. No tracker row or hardening brief records a BYOK run with a *valid* key (generation using the user's own key). A search of the ten hardening briefs for `BYOK` / "own key" / "valid key" found nothing.
  - Every hardening-pass verification used Managed AI (the NVIDIA-hosted provider).
  - BYOK is legacy parity (`LlmSettings.jsx`, `llmSettings.jsx`).
  - *To close:* one live BYOK generation with a real key. **The user must do this**: entering API keys is not something an AI session may do. Use a throwaway key if possible.
- **F2 — Signup and AI Access Setup were verified at build time only.** Both were promoted to Migrated in their own phases, before the hardening pass existed. Neither was re-verified under it. The 2026-08-15 pass covered login, forgot/reset, settings, and the guard, not signup or the setup page. #17 asks for "independently verified" rows. *To close:* a short live re-verification of `/signup` → `/setup`, in the same style as the 2026-08-15 pass.
- **F3 — The Auth slice's evidence is prose-only and bundled.**
  - The 2026-08-15 verification has no standalone brief and no review-gate record. Its tracker text arrived in commit `d80e105` ("M9 comparison explanation + M10 evaluation framework"), a large unrelated commit.
  - Mitigating: the code it verified has not changed since. `git log --since=2026-08-14` over `web/features/account-setup` and the auth route folders shows only `7ef23dc` (Landing's `ReturningUserRedirect`), and `backend/agents/auth.py` has no commits since.
  - *To close:* optional. Either accept it on that basis, or re-run the cycle and record it as a brief.
- **F4 — A Company Research audit is still open.** The tracker's own note: a *broader* cross-surface job/report-status-gating audit is "requested but not yet run" beyond the two instances found and fixed (`4214b905`). It is documented as "not a blocker" to the Migrated promotion; it is carried here for completeness.
- **F5 — Stale tracker notes. CORRECTED 2026-10-01 in the tracker (commit `8f9246d`; see the tracker's §7 rows "Watchlist store", "Client persistence" and "API client"). The text below is the original finding, kept for the record.** Not a verification gap, but they would mislead anyone using the tracker as the deletion record: the §7 "API client" row says ingest, report generation/streaming and comparison "still have zero calls from `web/`", which the Migrated features contradict; the Watchlist and `usePersistedState` rows say `web/lib/state/` is "a README placeholder only", yet `aiAccess.ts` and `sessionValue.ts` exist there. These should be reconciled before the tracker is archived as the evidence record.
- **F6 — Legacy-only capabilities carried inside Migrated rows (found 2026-10-02). STATUS: OPEN, for the user.** A complete diff of legacy `frontend/src/lib/api.js` (28 exports; Appendix B) against `web/` found **three user-facing capabilities with no `web/` caller and no recorded DROP decision**: PDF/audio upload ingest, report deletion, and the company refresh (`POST /companies/ensure`). A wider sweep of the legacy pages and components (Appendix C) found further legacy-only behaviours (§3 #15–#19). **Related records exist for several of these and are cited per row in §3, as records and not as recommendations**: a frozen "Uploads" interaction pattern, a Backend Engineering API-coverage audit, and frozen experience-design documents that mention a serif PDF export. None of them is a decision to drop or to port. The backend routes for the three main items still exist. No tracker Status changes because of this: the Ingest and Research Library rows stay Migrated, and these are carry-overs for the user to rule on. But deleting `frontend/` would remove the only UI for each. The first draft of this plan missed them because it diffed route files and components, not `api.js`, and an earlier draft of this flag also said "no recorded decision" without citing the related records. *To close:* the user rules row by row (§3 #12–#19), either dropping the item (and citing the ruling) or requiring a port first. **The §7 API client row's promotion to Migrated is held** until then (CTO 3, 2026-10-02).

### 1.4 Gate decisions (rulings recorded)

> **Provenance:** the rulings below were made by **the user in chat on 2026-10-01** and were **relayed to this document by CTO 3**, who asked for them to be recorded as the user's rulings. They are recorded here as relayed; this document's author did not see the chat. They are not an approval of the plan (§5).

- **G1 — `/docs`. RULED 2026-10-01 (user): `/docs` is explicitly EXEMPT from the "every row Migrated" gate.** Basis: the 2026-08-03 closeout decision that it "will not be built" (tracker §1 row: "by decision, not by oversight"). The literal gate ("every row ... Migrated") is therefore read as excluding it, on the record.
- **G2 — Is §7 in the gate? RULED 2026-10-01 (user): no. The gate is §1–§5 only** (this matches Next steps #17). §7's 2 Not Started and 3 In Progress rows (Watchlist store, `usePersistedState`, API client, App shell, `jest-axe`) are not removal blockers and **stay tracked separately in the tracker**.

---

## 2. Inventory: `frontend/` and everything that depends on it

### 2.1 `frontend/` itself

- **43 tracked files:** 8 root config (`.gitignore`, `components.json`, `craco.config.js`, `jsconfig.json`, `package-lock.json`, `package.json`, `postcss.config.js`, `tailwind.config.js`) + `public/index.html` + 34 under `src/`. No `src/components/ui/` (CRA app has none).
- **Local-only, untracked, gitignored files on this machine:** `frontend/.env` (`REACT_APP_BACKEND_URL`, `WDS_SOCKET_PORT`, `ENABLE_HEALTH_CHECK`) and `frontend/.env.local`. They would **survive `git rm`** and need a manual step (§4). There is no `frontend/node_modules` here.
- Stack: Create React App via `craco`, React 19, `react-router-dom` 7, `react-scripts` 5.0.1; `package.json` scripts are `start` / `build` / `test` (all `craco`).

### 2.2 Runtime, CI and tooling dependents: none found

| Place | Result |
|---|---|
| `scripts/run.py` | Does not use `frontend/`. Only the words "frontend" in a docstring/port label (lines 4, 9, 336). It installs and starts `web/`. |
| `.claude/launch.json` | No reference; its two configs are `alphascribe-web-dev` (`npm --prefix web run dev`) and `alphascribe-full` (`python scripts/run.py`). |
| `.github/workflows/` | One workflow, `backend-ci.yml`. No `frontend/` step. (There is also **no CI for `web/`**; a pre-existing gap, unrelated to removal.) |
| Root manifests | No root `package.json`. |
| `web/` and `backend/` imports | Nothing imports from `frontend/`. The only mentions are 4 *comments* (see 2.4). |

### 2.3 Backend test env coupling (a trap, not a dependency)

- Thirteen backend test modules read `REACT_APP_BACKEND_URL`, a CRA-named variable that `frontend/.env` sets locally. Most default to `http://localhost:8001`. **`backend_test_iter3.py`–`backend_test_iter6.py` use `os.environ["REACT_APP_BACKEND_URL"]` with no default**, so they raise `KeyError` unless the variable is set in the shell.
- Those four also call `load_dotenv("/app/frontend/.env")`: an absolute `/app/...` path (a hosted-platform layout), which does **not** point at this repo's `frontend/`. Deleting `frontend/` therefore changes nothing for that line.
- **Do not rename the variable or edit these files**: `CLAUDE.md` says the `backend_test_iter*.py` suites are additive and to be kept, and `pytest.ini`'s `addopts` must not change. Record the variable name as a known legacy name; just make sure it is exported in the shell where the live suites are run.

### 2.4 In-repo references that would dangle (text only)

**Config / ignore:**
- `.gitignore` lines 85–87 (`android-sdk/frontend/...`, `frontend/node_modules/.cache/...` ×2) and line 102 (`frontend/.env.local`).
- `.hermes.md` lines 15, 29, 37: an agent-profile file whose own text says it is read-only and changes need approval. Its "compare source files under backend/ and frontend/" rule would point at a missing directory. **User's call.**

**Code comments in `web/` (4):**
- `web/README.md:4` ("frozen legacy `frontend/` (CRA) app");
- `web/lib/constants/testIds.ts:19`;
- `web/lib/markdown/citations.ts:6` ("Ported from `frontend/src/lib/remarkCitations.js`");
- `web/lib/state/sessionValue.ts:15`.

All four read correctly if they point at a git tag (§4 step 1) rather than a path; editing them is an optional follow-up.

**`CLAUDE.md` — listed for the user; this plan edits none:**

| Lines | Content |
|---|---|
| 32–38 | "The legacy Create React App (`frontend/`, craco, React Router) is a **frozen, read-only reference implementation** ... It stays in the repo until `docs/governance/Feature_Parity_Tracker.md` reaches 100% migrated and a CTO-approved Legacy Frontend Removal Plan authorizes deleting it — do not delete `frontend/` on your own initiative." (**The authorization clause: this is the sentence the user's approval satisfies.**) |
| 50–51 | "...reverses the old CRA-era 'no shadcn' rule, which only applied to the retired `frontend/` app." |
| 60–64 | Test IDs bullet: names `frontend/src/constants/testIds/alphascribe.js` and says `web/` has no equivalent. Already stale since `aadfa1e`; replacement text is proposed in `docs/briefs/test-ids_convention.md` §6. |
| 65–67 | Client persistence bullet: "the CRA-era `usePersistedState` ... and watchlist store ... have no `web/` port yet — re-establish ... when the first feature ..." |

**Docs (18 files under `docs/` match the string `frontend/`, not counting this plan itself; 13 of them refer to the directory, 5 are false matches):**
- **False matches (no action):** `frontend_architecture/{02,02.1,03.3}` and `backend_engineering/{36,39}`, which use the phrases "frontend/backend" or "frontend/UX".
- **Governance and history records (leave unedited):** `Feature_Parity_Tracker.md` (38 mentions; becomes the archived gate record), `Final_Governance_Verification_2026-07-21.md` (3; lines 88 and 96 record GRA-001's execution as open), and `backend_engineering/{12,29,41,54,58,62}`. Of these, `12_M2_Implementation_Charter.md:163` is the only one that states a rule ("Deleting `frontend/` (legacy CRA) | Gated on `Feature_Parity_Tracker.md` + a CTO-approved Legacy Frontend Removal Plan"), and that rule is exactly what this plan satisfies.
- **Briefs from this pass (history):** `test-ids_convention.md`, `landing_scr-01.md`.
- **Local-only planning history (leave unedited):** `docs/planning/09-Auth-and-Accounts-Plan.md`, a dated log of the legacy auth build (its checklist cites e.g. `frontend/src/lib/api.js`). **The whole `docs/planning/` directory is gitignored** (`.gitignore` line 122 is the comment "Local product/planning docs — keep private" and line 123 is the `docs/planning/` pattern; `git ls-files docs/planning` is empty), so the file exists on this machine only, is not in any clone, and is untouched by removing `frontend/` from git. An earlier draft of this plan missed it because `git grep` searches tracked files only; the count above comes from a filesystem search.
- **Living, worth a closing note from their owners:** `docs/Documentation_Index.md:109` ("`frontend/` (Create React App) is non-canonical; repository-structure cleanup (archiving/labeling) is ...") and the Change Request Register's GRA-001 section (lines 89–95, "**Not yet executed:**"). A closing note on each is the normal governed route.

### 2.5 Things the repo cannot tell us (user to confirm)

- **Any deployment or hosting config outside the repo that builds `frontend/`.** There are hints of an earlier hosted-platform life (`/app/frontend/.env` paths in tests, `.emergent/` in `.gitignore`, `tests/reports/iteration_*.json`, a root `test_result.md`), but nothing in the repo builds `frontend/`.
- **Whether the legacy app was ever reachable at a URL users hold.** The two apps use different routes: legacy `/app`, `/dashboard`, `/ingest`, `/account` (redirects to `/settings`), `/docs`, and a catch-all `*` → `/`. `web/` has `/research`, `/workspace`, `/library`, `/settings`, `/reports/[id]`, `/compare`, `/learning`, `/setup`, and **no redirects and no `not-found` page**. In this repo only `web/` is ever served (`scripts/run.py`), so nothing breaks locally; this matters only if legacy URLs were published somewhere.

---

## 3. Parity gaps: legacy-only items with no `web/` equivalent

"Dropped" below means *a decision exists in the repo that I can cite*. Where none exists I say **OPEN** and give a recommendation, **not** a decision: I have not invented one.

| # | Legacy item | `web/` today | Verdict | Basis |
|---|---|---|---|---|
| 1 | `/docs` page (`Docs.jsx`: install / API reference / troubleshooting) | none | **Intentionally dropped; exempt from the gate (G1, user ruling 2026-10-01)** | Milestone 3 freeze closeout 2026-08-03, tracker §1 row: not in `05_Screen_Inventory.md`; "will not be built". Its content survives only in the git tag (§4). `README-RUN.md` covers installation; that it also covers the API-reference/troubleshooting material is **not verified**. |
| 2 | Watchlist store (`watchlist.js`, `useSyncExternalStore`) | none | **Intentionally deferred (post-MVP)** | `docs/design/03_Information_Architecture.md` lines 256, 345 ("post-MVP"; "deferred to a later release"); `02.2_Feature_Organization.md:94`; tracker §3 Dashboard row (stats strip / Watchlist / Quick Actions "none of those appear in the frozen SCR-04 wireframe"). Gap: the §7 row still reads Not Started with a stale note (F5, since corrected). Any watchlist a user built in the legacy app lives in that browser's `localStorage` and is **orphaned**, never migrated. |
| 3 | `usePersistedState` (`persist.js`) | `web/lib/state/sessionValue.ts` (+ test) covers the single current use (the Overview retry query) | **Intentionally dropped, no port. SUPERSEDED by `web/lib/state/sessionValue.ts` (user ruling 2026-10-01)** | Ruled by the user 2026-10-01 (relayed by CTO 3). Supporting evidence: the general hook is not ported and no `web/` feature needs it today (CLAUDE.md: "re-establish ... when the first feature ... needs it"). The tracker's §7 row still reads Not Started with a stale note (F5, since corrected); under G2 it is tracked separately. |
| 4 | Legacy test-ID strings (`alphascribe.js`) | `web/lib/constants/testIds.ts` (empty scaffold, `aadfa1e`) | **Intentionally dropped** | `docs/briefs/test-ids_convention.md` §2 (out of scope) and CTO-2's 2026-09-29 decision: nothing in `web/` consumes the legacy values. The legacy *structure* was reused; the strings were not. |
| 5 | `remarkCitations.selfcheck.mjs` (legacy self-check script) | `web/lib/markdown/citations.ts` is used by 4+ surfaces; unit tests added in `web/lib/markdown/citations.test.tsx` | **DONE 2026-10-02: ported as a Vitest suite, commit `03279e7`** | At first draft no `web` test file referenced the shared citation plugin and the legacy self-check would disappear on deletion. Closed by `03279e7`: 10 tests (marker linking, adjacent and multi-digit markers, real links untouched, no double-wrapping, emphasis, inline and fenced code left alone, non-numeric brackets ignored); the plugin itself is unmodified (`citations.ts` has no commit after its original `f912773`); Frontend Reviewer 2 PASS per CTO 3. |
| 6 | `AmbientBackground.jsx` (legacy ambient visual) | none | **Intentionally dropped, not ported (user ruling 2026-10-01)** | Ruled by the user on 2026-10-01 (relayed by CTO 3, same provenance as §1.4): cosmetic; `web/` has its own single light theme (`web/styles/tokens.css`). |
| 7 | `/account` → `/settings` redirect; `*` → `/` catch-all | none; no `not-found` page. `web/` has no `redirects()` and no middleware; stray URLs get Next.js's built-in default 404 (HTTP 404, unbranded, no link back) | **Intentionally dropped, covered by Next.js's default 404 (HTTP 404 for unknown routes) (user ruling 2026-10-01, relayed by CTO 3, same provenance as §1.4)** | `/account` was already a retired legacy alias (legacy `App.js`: "`/account` was the old settings route") and has no `web/` consumer. Legacy's silent catch-all bounce to `/` is not ported: an honest 404 is preferable. **Follow-up, not a removal blocker:** a branded `app/not-found.tsx` (the default page is unbranded with no way back; roughly 20–30 lines plus a test). **Contingent on §2.5, which stays OPEN:** *the user did not confirm whether any legacy URLs were ever published.* If they were, add `redirects()` entries in `web/next.config.ts` for `/account → /settings`, `/dashboard → /workspace` and `/app → /research` (about 6 lines each way, a small port). Investigation basis: legacy `frontend/src/App.js` routes; live probe of the `web/` dev server (`/account`, an unknown path, `/app`, `/dashboard`, `/ingest`, `/docs` all 404; `/workspace` and `/reports/<id>` 200). |
| 8 | §7 **API client** (In Progress) | `fetch-client.ts`, `query-client.ts`, plus per-feature API modules | **Not a removal blocker (G2); reconcile the row separately** | Row note was stale (F5, since corrected in the tracker; status left unchanged). **Promotion to Migrated held pending the F6 rulings** (CTO 3, 2026-10-02). Every Migrated feature already calls the backend through it, so this looks like a labelling gap, not a functional one. **Not verified by me**, so this is not a claim it is complete. |
| 9 | §7 **App shell / nav layout** (In Progress) | `PublicTemplate`, `WorkspaceTemplate`, `ResearchTemplate`, `DocumentTemplate`, `SetupTemplate` | **Not a removal blocker (G2); reconcile the row separately** | Same shape as #8. Its legacy-only `AmbientBackground` component is row #6, ruled intentionally dropped (user, 2026-10-01). |
| 10 | §7 **`jest-axe` testing** (In Progress) | Foundation + Company Research covered; not workspace-home / account-setup / route-level | **Not a legacy-removal item** | The legacy app has no equivalent ("none" in the tracker row). Extending coverage is forward work. Not relevant to the gate: G2 (user ruling 2026-10-01) puts §7 out of scope. |
| 11 | Accepted deferrals inside Migrated rows | n/a | **Carried, not gaps** | Per tracker decisions: AI Insights deferred actions (no backend support); Research Library Sessions / Saved Exports / History (no backend data source); Comparison "explanation of differences" (no LLM-backed endpoint); Landing's labels-only trust copy, plain-text footer, and the **open investment-advice-disclaimer compliance item** (PRD §7, a legal matter and not a removal blocker). |
| 12 | **PDF and audio upload ingest** (`POST /ingest/pdf`, `POST /ingest/audio`) | none. `web/`'s ingest covers EDGAR, pasted text and samples only (`web/features/company-research/integration/api.ts`) | **OPEN — no recorded DROP decision; related records below; decide explicitly** | Legacy: `frontend/src/lib/api.js:56–78`; UI in `Ingest.jsx` (calls at lines 112 and 140). Backend routes exist (`backend/server.py:538` audio, `:618` pdf). **Related records (reported as records, not recommendations):** (a) `docs/design/10_Interaction_Patterns.md` "# Uploads" (🧊 Frozen, v0.1.1, line 157): "Not an MVP interaction — flagged. No approved journey or IA element requires uploading files ... This pattern is intentionally **not defined** for MVP to avoid inventing scope. If a future capability requires uploads, it enters via a governance Change Request." (b) `docs/backend_engineering/02_API_Coverage_Audit.md` lines 85–96 (Backend Engineering M1 audit, 2026-08-03): both routes are "functional and tested" and "awaiting a UI, not rotting"; `05_Screen_Inventory.md` defines no Ingest screen, so this is "a product scope question, not a backend gap". (c) The tracker's Ingest row says "Paste-text/EDGAR-fetch/load-samples are wired; audio/PDF multipart upload is not (out of 4A scope)." and later in the same row that "audio/PDF upload remains correctly listed as not built." Both are statements of status, and the row was promoted to Migrated on 2026-09-21 without revisiting it. None of these is a decision to drop or to port; the user decides. Tracker statuses unchanged. |
| 13 | **Report deletion** (`DELETE /reports/{id}`) | none. The only `DELETE` in `web/features` is account deletion (`account-setup/integration/api.ts:75`) | **OPEN — no recorded DROP decision; related records below; decide explicitly** | Legacy: `api.js:39`; UI `AppLayout.jsx:147–157` (a delete button with a confirm on every history item). Backend route exists (`server.py:1477`). **Related records (records, not recommendations):** (a) `docs/backend_engineering/02_API_Coverage_Audit.md` §4.4 (lines 196–204; audit, 2026-08-03) classifies it "⚪ Unconsumed, but *behaviorally required*": `research-library` "offers no delete action", and the audit says "Recommend wiring rather than deprecating — deletion is the one report operation with no alternative path." That is an audit recommendation, not a ratified decision. (b) `docs/backend_engineering/16_M2_Company_Research_Findings_Report.md` lines 84 and 190 mark the frontend wiring "Out of scope" for that backend-only milestone, i.e. deferred, not dropped. The Research Library row and `hardening_research-library.md` do not mention deletion, and the frozen screen inventory is silent. Tracker statuses unchanged. |
| 14 | **Company ensure / refresh** (`POST /companies/ensure`) | none | **OPEN — no recorded DROP decision; related records below; decide explicitly** | Legacy: `api.js:54`. **Two distinct legacy uses:** (i) `ReportView.jsx:42–66` is the true **refresh** path: `ensureCompany(ticker, true)` behind a confirm, labelled "Fetch the latest SEC filing" (line 44), adding a new filing for a company that already has some; (ii) `NewReport.jsx:150–166` is the **first-time** path: `ensureCompany(selected.ticker)` with no refresh, when the picked company has no ingested filings (add-company-on-select). Backend route exists (`server.py:722`). **Related records (records, not recommendations):** `docs/backend_engineering/02_API_Coverage_Audit.md` §4.1 (lines 150–165) classifies it "🟡 Partial": "no `web/` module calls it"; a user who picks a company with no ingested filings "hits `POST /reports/generate`'s 400 ... rather than the ensure-then-generate flow the legacy app used"; "a genuine integration gap, not an orphaned endpoint". `docs/backend_engineering/17_M4_Backend_Capability_Roadmap_Reconciliation.md:123`: "⚪ Missing (documented, not contract-breaking)", "zero frontend consumer". The tracker's Ingest row records that `web/` instead treats an empty corpus as an empty state inside Overview, triggered off the backend's `400`. It may also be superseded by the M12/M13 acquisition flows; not verified. |
| 15 | **Global activity bar + global job store** (in-flight analyses shown on every page with the pipeline stage, a link back, and Stop; analyses keep streaming across navigation) | none found (no `useJobs`/status-bar code in `web/`); `web/` resumes a run via `?job=` per the tracker | **OPEN — no recorded position on this feature; a related principle is cited** | Legacy: `AppLayout.jsx:255–292` (`ActivityBar`), `jobs.jsx`. **Related record (a principle, not a position on a status bar):** `docs/design/00_Design_Constitution.md` lines 160–161 (🧊 Frozen, v1.1): "Preserve user progress. No action — including navigation and errors — may lose the user's work (Journeys: J-06)." Searched the design, experience_design, frontend_architecture and backend_engineering docs for "activity bar", "status bar", "global job", "in-flight" and "background job": the only hits are backend uses of "in-flight". Behaviour of `web/` when navigating away from a running analysis was not tested for this plan. |
| 16 | **Keyboard shortcuts**: Cmd/Ctrl+K and `/` focus the ticker search | none found (no `metaKey`/`ctrlKey` handler in `web/`) | **OPEN — no recorded position found** | Legacy: `NewReport.jsx:114–129`. Searched the design, experience_design, frontend_architecture and backend_engineering docs for "shortcut", "command palette" and Cmd/Ctrl+K: no relevant hit. Related only in a general sense: the frozen Navigation pattern requires "full keyboard operability" (`docs/design/10_Interaction_Patterns.md` line 55), and the frozen wireframes' shared frame has a `[Global Search]` header slot (`docs/design/07_Wireframes.md`); neither defines a shortcut. |
| 17 | **Compare extras**: quality/confidence bar chart, quality filter, report search | `ComparisonTable` + ticker filter + `?ids=` only; no chart code in `web/features/comparison` | **OPEN — no recorded position found on these three; the frozen pattern is cited** | Legacy: `Compare.jsx:25–40` (chart), `:69,125,158` (quality filter), `:70,124` (search). **Related record:** `docs/design/10_Interaction_Patterns.md` "# Comparison" (lines 165–171, 🧊 Frozen): "like-for-like by default; non-comparable data flagged; AI explains differences; the set can be preserved", with table navigation. It specifies no chart, quality filter or search. The tracker's Comparison row records only the deferred AI "explanation of differences". |
| 18 | **Report-page extras**: PDF export (print window), copy report link, "run a fresh analysis, bypass cache" | Markdown export is covered (Export row; `exportMarkdown.ts`); copy-brief-text exists (`AIResponseCard.tsx:148`); no PDF, no copy-link, no fresh re-run UI (`no_cache` appears only in `schemas.ts:123`) | **OPEN — no recorded DROP decision for PDF; related frozen records below; no recorded position found on copy-link or fresh re-run** | Legacy: `ReportView.jsx:100–136` (PDF), `:138–145` (copy link), `:147–161` (fresh analysis). **Related records on PDF (records, not recommendations):** frozen `docs/experience_design/Components/09_Research_Components.md` lines 387–388 (🧊 Frozen): "Per Inventory: **Report view** (+ export/serif PDF template — the codebase's `ReportView.jsx` serif export)." and frozen `docs/experience_design/engineering_handoff/12_Component_Mapping.md` line 133: Report Viewer → "Report view (+serif PDF export)". So frozen experience-design documents do mention a serif PDF export. The frozen `docs/design/` files 05, 06, 07 and 09 contain no "PDF", and `docs/design/10_Interaction_Patterns.md` "# Downloads" specifies an artifact "preserving reasoning and sources" with no format. The code comment at `web/features/research-library/internal/exportMarkdown.ts:3–11` (jsPDF-style output is "scope beyond what J-06 actually asks for") is additional context, not a governance decision. Copy-link and fresh re-run: searched the design docs for share / copy link / re-run / regenerate and found nothing relevant. |
| 19 | **Other UI items**: Settings profile rows "Member since" and "Credits"; New Report query presets | `web/` Settings shows email only (`SettingsPanel.tsx:96`); no presets found in the company-research UI beyond `CopilotPanel` (not verified further) | **OPEN — no recorded position found; the frozen Settings entry is cited** | Legacy: `Settings.jsx:109–111`; `NewReport.jsx:44–78,131`. **Related record:** `docs/design/05_Screen_Inventory.md` SCR-11 (line 333, 🧊 Frozen) lists "Information Displayed: Account information; current AI access model and status.", without enumerating individual profile rows. Presets: searched `docs/design/` files 05, 06, 10 and 13 for starter / preset / suggested / example prompt and found nothing. |

---

## 4. Deletion sequence, rollback, verification

Each step says **who** does it. Nothing here is to be run until §5's approvals exist.

### 4.1 Before deletion (blocking)

1. Rulings on G1, G2, #3, #6 and #7 are **recorded** (§1.4, §3; user, 2026-10-01). **Still OPEN:** the §2.5 contingency (were legacy URLs ever published? unconfirmed), which decides whether the §3 #7 `redirects()` entries are needed.
2. **PRE-DELETION GATE (F1), owned by the user. Status: NOT DONE.** The user will live-verify the BYOK happy path, i.e. one real generation using their own valid API key, **before deletion**. No AI session types or handles a real key. This plan **stays unapproved until the user records this as done** here (name/date/result below). Until then F1 is OPEN, not closed.
   - Recorded by the user: _not yet done_ (date: ___; result: ___)
   Also close or accept in writing the other thin-verification flags F2–F4. The "port first" item (§3 #5) is **done** (`03279e7`, 2026-10-02).
3. Confirm §2.5 items (no external deployment of `frontend/`; no published legacy URLs).
4. **Back up the local-only files** `frontend/.env` and `frontend/.env.local` if their values matter. Nothing in the repo reads them.
5. **USER RULINGS ON LEGACY-ONLY CAPABILITIES (F6): NOT DONE.** Before deletion the user rules explicitly, row by row, on §3 #12–#19: drop (citing the ruling) or port first through the brief pipeline. #12–#14 are user-facing capabilities with working backend routes; #15–#19 are other UI behaviours. The user may rule on these individually or together. Until recorded they are OPEN and the plan stays unapproved. Appendices B and C carry the evidence.
   - Recorded by the user: _not yet done_ (date: ___; rulings: ___)

### 4.2 Sequence

1. **Tag the final state (the rollback anchor).** An annotated tag at the current `origin/main` commit, e.g. `legacy-frontend-final`, then push the tag. *Pushing is the user's call.* This is a convenience pointer only; see 4.3 for why the history itself already guarantees recovery.
2. **Branch:** `chore/remove-legacy-frontend` from that commit. Do not work on `main` directly.
3. **Remove tracked files:** `git rm -r frontend`. This removes the 43 tracked files.
4. **Remove the untracked leftovers manually.** `git rm` leaves the gitignored `frontend/.env`, `frontend/.env.local`, and any local `node_modules` behind, so the directory still exists. Delete it by hand after step 4.1's backup.
5. **Tidy ignore entries.** Remove `.gitignore` lines 85–87 and 102 (they would be dead).
6. **Leave alone, by decision:** the `REACT_APP_BACKEND_URL` env name and `/app/frontend/.env` paths in backend tests (§2.3); the frozen/historical docs (§2.4); `.hermes.md` (user's call).
7. **Doc/comment follow-ups (separate small changes):** a closing note in `Documentation_Index.md` and the Change Request Register; update the four `web/` comments to cite the tag; a closing "Legacy frontend removed, see tag" note in the tracker header. **`CLAUDE.md` is edited by the user alone** (§2.4's table; including the Test IDs replacement text already proposed in `test-ids_convention.md` §6).
8. Run §4.4 verification, then merge by the project's normal review path.

### 4.3 Rollback

- **Primary: Git history.** Removal is an ordinary commit; no history rewrite is proposed. Recovery is `git revert <removal-commit>`, or `git checkout legacy-frontend-final -- frontend`. **Do not** use `git filter-repo` / BFG or force-push at any point in this plan; those are the only operations that could make removal irreversible.
- **Tag:** gives a stable human-readable name for the pre-removal state.
- **Not recoverable from git:** the local-only `frontend/.env*` files and any legacy `localStorage` data (§3 #2). Hence the 4.1 backup.
- **Revert trigger:** any §4.4 failure, or a published-URL discovery (§2.5).

### 4.4 Verification after deletion

On the removal branch, with the stack started the normal way:

1. `git ls-files frontend` prints nothing; `git grep -n "frontend/" -- . ':!docs'` shows only the intentionally retained items from §4.2 step 6, and no *import* of a deleted path.
2. `python scripts/run.py` starts MongoDB, backend (`8001`) and web (`3001`) with no error, and the backend `/api/health` returns `ok`.
3. `web/`: `npm run verify` (it chains `typecheck`, `lint`, `format:check` and `test`) and `npm run build` all green. The suite size at write time was 385 tests (per the Landing commit `7ef23dc`); treat the *count* as indicative, and the *green* as the requirement.
4. `npm run e2e` (Playwright; it builds and serves on its own isolated port 4300) passes.
5. Backend hermetic tests pass. Backend live suites (which need the stack and, for `iter3`–`iter6`, `REACT_APP_BACKEND_URL` exported) pass as they did before removal.
6. A short live smoke of the three entry states against the running stack: signed-out Landing; signup → setup → workspace; a Company Research run; Learning "Explain This". This guards against the only realistic breakage (an undiscovered dependency), not against the removal of dead code.
7. `.github` CI is unaffected (`backend-ci.yml` never touched `frontend/`); confirm by reading the next run, not by assumption.

---

## 5. Open decisions and sign-off

**Recorded rulings (user, 2026-10-01, relayed by CTO 3):**
- **G1** `/docs` is exempt from the gate. **G2** §7 is not part of the gate (§1–§5 only). **§3 #3** `usePersistedState` is superseded by `sessionValue.ts` (intentionally dropped, no port).
- **§3 #6** `AmbientBackground` is intentionally dropped, not ported (cosmetic; `web/` has its own single light theme).
- **§3 #7** the `/account` redirect and `*` catch-all are intentionally dropped, covered by Next.js's default 404; a branded `not-found.tsx` is a follow-up, not a blocker; the user did not confirm whether legacy URLs were published, so the §2.5 contingency stays open.
- **F1** is to be live-verified by the user with their own key **before deletion**; it is a user-owned gate in §4.1 and remains OPEN until recorded as done.
- (All relayed by CTO 3 from the user's chat of 2026-10-01; the user directed CTO 3's recommendations be followed on the last two.)

**Still OPEN:**
- **F6 legacy-only capabilities (§3 #12–#19; Appendices B and C): the user's rulings are needed before deletion. NOT DONE.** The §7 API client row's promotion is held until then.
- **F1 pre-deletion gate (§4.1): user-owned, NOT DONE.** The plan cannot be approved until it is recorded as done.
- **§2.5 contingency (legacy URLs):** whether any legacy URL was ever published is **unconfirmed by the user**. §3 #7 is ruled (dropped, covered by the default 404), but its redirect contingency stays open and visible here.
- F2/F3/F4 (close or accept in writing); whether `.hermes.md` changes (user).
- Housekeeping: §3 #5 (the citation self-check port) is **done**, `03279e7`; §3 #8/#9 row reconciliation (tracked separately under G2).

**Sign-off (to be completed by the people named; none has signed):**

| Role | What they sign | Name / date |
|---|---|---|
| CTO | That this plan may go to the user (the G1/G2/#3/#6/#7 rulings are the user's and are recorded above) | _unsigned_ |
| **User** | **Final approval of the plan, and approval to delete.** Under `CLAUDE.md` lines 32–38 and the tracker's own text, deleting `frontend/` is not for an AI session to authorize or initiate. | _unsigned_ |
| **User** | **Executes (or explicitly instructs the execution of) the deletion**, and pushes the tag and merge. | _unsigned_ |
| **User, alone** | **Every `CLAUDE.md` edit**, including those in §2.4. No other session edits it. | _unsigned_ |

---

## Appendix — how each claim was verified

- Doc-reference count: a filesystem `grep -rl "frontend/" docs` (19 files, which is 18 plus this plan), cross-checked against `git grep` (17 tracked files); the difference is this plan and the gitignored `docs/planning/09-Auth-and-Accounts-Plan.md`. A filesystem search of non-doc source files for the same string found only items already listed in §2.2–§2.4, plus the historical test-agent output `tests/reports/iteration_5.json`.
- Tracker status, rows and quotes: read from `docs/governance/Feature_Parity_Tracker.md`; the §1–§7 statuses were recounted row by row with a script, not read from the Rollup.
- Commits and dates: `git log` over the tracker, and over `web/features/account-setup`, the auth route folders and `backend/agents/auth.py`; hardening-brief dates from each brief's header.
- `frontend/` contents: `git ls-files frontend` (43) and a listing of tracked and gitignored files; `git check-ignore -v` for the `.env*` files (values not reproduced).
- Dependents: `git grep` across the whole tree excluding `frontend/`, `docs/` and `tests/reports/`, for `frontend/`, `craco`, `react-scripts`, `REACT_APP`, and `:3000`; direct reads of `scripts/run.py`, `.claude/launch.json`, `.github/workflows/backend-ci.yml`, `.hermes.md`, `.gitignore`.
- `web/` routes: `find web/app -name page.tsx`; no `redirects()` in `next.config.*`; no `not-found.tsx`.
- Legacy routes: `frontend/src/App.js`.
- Citation-plugin test gap: at first draft, a search for `*.test.*` files naming `remarkCitations` or `markdown/citations` in `web/` found none. Closed 2026-10-02 by `03279e7` (`web/lib/markdown/citations.test.tsx`, 10 tests; confirmed by counting the `it(` blocks and checking that `citations.ts` was not changed).
- Deliberately **not** verified: external hosting, whether any legacy URLs are published, and whether `README-RUN.md` covers the legacy Docs content. (The citation-plugin question that used to be listed here is closed by `03279e7`.)

## Appendix B — Legacy `api.js` endpoint coverage (complete: all 28 exports)

Source: `frontend/src/lib/api.js` read in full (2026-10-02). "Covered" means a `web/` call site was found (file named). "OPEN" means no `web/` caller and no recorded drop decision; the row number points to §3.

| # | Legacy export | Endpoint | Status | Where / why |
|---|---|---|---|---|
| 1 | `registerUser` | `POST /auth/register` | Covered | `web/features/account-setup/integration/api.ts` |
| 2 | `loginUser` | `POST /auth/login` | Covered | same |
| 3 | `logoutUser` | `POST /auth/logout` | Covered | same |
| 4 | `getMe` | `GET /auth/me` | Covered | same |
| 5 | `changePassword` | `POST /auth/password` | Covered | same |
| 6 | `logoutAllSessions` | `POST /auth/logout-all` | Covered | same |
| 7 | `deleteAccount` | `DELETE /auth/me` | Covered | same (`api.ts:75`) |
| 8 | `forgotPassword` | `POST /auth/forgot-password` | Covered | same |
| 9 | `resetPassword` | `POST /auth/reset-password` | Covered | same |
| 10 | `listTickers` | `GET /tickers` | **OPEN** (likely superseded, **not verified**) | Legacy use: `NewReport.jsx:92,209` (which tickers have filings). `web/` has no caller; its company picker uses `GET /companies/search`. No recorded drop decision. |
| 11 | `listCompanies` | `GET /companies` | **OPEN** (likely superseded, **not verified**) | Legacy use: `AppLayout.jsx:31`, `Dashboard.jsx:49` (ticker to company-name map). `web/` has no caller. No recorded drop decision. |
| 12 | `listFilings` | `GET /filings` | Covered | `web/features/company-research/integration/api.ts` |
| 13 | `listReports` | `GET /reports` | Covered | `company-research`, `comparison`, `research-library`, `workspace-home` integration modules |
| 14 | `deleteReport` | `DELETE /reports/{id}` | **OPEN, §3 #13** | no `web/` caller |
| 15 | `trendingCompanies` | `GET /companies/trending` | Not a capability | Defined in `api.js:40` but **no legacy page calls it** (searched `frontend/src`), so nothing user-facing is lost |
| 16 | `getReport` | `GET /reports/{id}` | Covered | `company-research`, `research-library` integration modules |
| 17 | `generateReport` | `POST /reports/generate` | Covered | `company-research/integration/api.ts` |
| 18 | `cancelReport` | `POST /reports/{id}/cancel` | Covered | same |
| 19 | `compareReports` | `POST /reports/compare` | Covered | `web/features/comparison/integration/api.ts` |
| 20 | `ingestText` | `POST /ingest/text` | Covered | `company-research/integration/api.ts` |
| 21 | `ingestEdgar` | `POST /ingest/edgar` | Covered | same |
| 22 | `ingestSamples` | `POST /ingest/samples` | Covered | same |
| 23 | `searchCompanies` | `GET /companies/search` | Covered | `web/features/workspace-home/integration/api.ts` |
| 24 | `ensureCompany` | `POST /companies/ensure` | **OPEN, §3 #14** | no `web/` caller |
| 25 | `ingestAudio` | `POST /ingest/audio` | **OPEN, §3 #12** | no `web/` caller |
| 26 | `ingestPdf` | `POST /ingest/pdf` | **OPEN, §3 #12** | no `web/` caller |
| 27 | `health` | `GET /health` | Not a capability | Defined in `api.js:79`; the only legacy mention is the endpoint documented on the `/docs` page (`Docs.jsx:171`), which is exempt (G1) |
| 28 | `streamJob` | `GET /reports/{id}/stream` (SSE) | Covered | `web/lib/api/sse-client.ts` (`openEventStream`), used by `company-research` and `learning` |

Totals over the 28 exports: **22** covered or not-a-capability (rows 1–9, 12, 13, 15–23, 27, 28) and **6** OPEN (rows 10, 11, 14, 24, 25, 26). Those six are **four distinct items**: report deletion (§3 #13), company refresh (§3 #14), PDF/audio upload (§3 #12, two exports), and two list calls that are likely superseded but unverified (`/tickers`, `/companies`; they have no §3 row of their own because they only fed legacy lookups). No OPEN endpoint has a recorded drop decision; related records for the four user-facing ones are cited in §3 #12–#14.

## Appendix C — Other legacy surfaces (beyond `api.js`)

Method: read in full: `api.js`, `AppLayout.jsx` lines 24–292, `ReportView.jsx` lines 36–166, `NewReport.jsx` lines 84–143, `Settings.jsx` lines 1–125, `jobs.jsx` lines 1–60. Searched the whole of `frontend/src` for storage keys, keyboard handlers, downloads and clipboard use. **Not read (explicitly unverified):** `lib/auth.jsx`, `AppLayout.jsx` lines 1–23 and from line 293 to the end. **Surveyed by targeted search only, not read line by line:** `Dashboard.jsx`, `Compare.jsx`, `Ingest.jsx`, `Login`/`Signup`/`ForgotPassword`/`Landing`/`Docs`, and the components `CompanyCombobox`, `LlmSettings`, `PipelineLog`, `ResearchBrief`, `Scorecard`, `ToneGauge`, `FinancialsTable`. Rows marked "Covered by tracker row; not code-compared" rest on the tracker's own row text or on file names, **not on a comparison of legacy and `web/` code by this plan**. This table is therefore strong evidence for the gaps it lists, **not proof that no other gap exists**.

| # | Legacy surface (file:line) | `web/` equivalent | Status |
|---|---|---|---|
| C1 | Sidebar report history with score badge (`AppLayout.jsx:135–209`) | Research Library (`/library`) | Covered by tracker row; not code-compared |
| C2 | Per-item report delete in that history (`AppLayout.jsx:147–157`) | none | **OPEN, §3 #13** |
| C3 | Sidebar Watchlist (`AppLayout.jsx:84–133`, `watchlist.js`, `localStorage`) | none | Dropped by recorded decision: deferred post-MVP (§3 #2) |
| C4 | Global `ActivityBar` + `jobs.jsx` global job store | none found | **OPEN, §3 #15** |
| C5 | Cmd/Ctrl+K and `/` shortcuts (`NewReport.jsx:114–129`) | none found | **OPEN, §3 #16** |
| C6 | Markdown download (`ReportView.jsx:68–98`) | Export (`research-library/internal/exportMarkdown.ts`) | Covered (both sides read: `ReportView.jsx:68–98`, `exportMarkdown.ts:1–30`) |
| C7 | PDF export via print window (`ReportView.jsx:100–136`) | none | **OPEN, §3 #18** (related frozen records cited there) |
| C8 | Copy report link (`ReportView.jsx:138–145`) | copy brief text only (`AIResponseCard.tsx:148`) | **OPEN, §3 #18** |
| C9 | Fresh analysis bypassing cache (`ReportView.jsx:147–161`) | none (`no_cache` only in `schemas.ts:123`) | **OPEN, §3 #18** |
| C10 | Follow-up question building on a report (`ReportView.jsx:163`) | AI Insights / Copilot via `context_report_id` | Covered by tracker row; not code-compared |
| C11 | Refresh latest filing (`ReportView.jsx:42–66`) | none | **OPEN, §3 #14** |
| C12 | Dashboard stats strip, Watchlist, Quick Actions, Coverage tags | none | Dropped by recorded decision: tracker §3 Dashboard row ("none of those appear in the frozen SCR-04 wireframe") |
| C13 | Dashboard first-run onboarding banner (`Dashboard.jsx:14,40–44`, `localStorage`) | `/setup` once after signup (tracker AI Access Setup row) | Covered by tracker row; not code-compared (a different mechanism: the banner itself is not ported; this is the author's reading of the tracker row) |
| C14 | Compare quality/confidence chart, quality filter, search (`Compare.jsx:25–40,69–70,124–125,158`) | `ComparisonTable` + ticker filter + `?ids=` | **OPEN, §3 #17** |
| C15 | Compare selection persisted across navigation (`usePersistedState`) | URL `?ids=` sync (tracker Comparison row) | Covered by tracker row; not code-compared (a different mechanism) |
| C16 | PDF / audio ingest tabs (`Ingest.jsx:112,140`) | none | **OPEN, §3 #12** |
| C17 | Ingest form-state persistence (`usePersistedState`, `ingest:*` keys) | none (ingest is an empty state inside Overview) | Covered by the user's `usePersistedState` ruling (§3 #3: superseded, no port); not code-compared |
| C18 | Settings profile rows: Member since, Credits (`Settings.jsx:109–111`) | email only (`SettingsPanel.tsx:96`) | **OPEN, §3 #19** |
| C19 | New Report query presets (`NewReport.jsx:44–78,131`) | none found beyond `CopilotPanel` | **OPEN, §3 #19** (not verified further) |
| C20 | BYOK key store (`llmSettings.jsx`, `localStorage`) | `web/lib/state/aiAccess.ts` | Covered by tracker row; not code-compared. Keys saved by the legacy app are **not migrated**, so a user who used BYOK there re-enters the key. |
| C21 | Ticker combobox with keyboard navigation (`CompanyCombobox.jsx`) | `CompanySearch` (`workspace-home`) | Covered by tracker row; not code-compared |
| C22 | Report brief, scorecard, tone gauge, financials table, pipeline log | Company Research / Report View rows | Covered by tracker row; not code-compared |
| C23 | `/account` redirect, catch-all route | Next.js default 404 | Dropped by user ruling (§3 #7) |
| C24 | `AmbientBackground` | none | Dropped by user ruling (§3 #6) |
| C25 | `/docs` page | none | Exempt by user ruling (G1) |
