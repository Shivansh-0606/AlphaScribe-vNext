# Report Deletion in Research Library (SCR-09 / SCR-10) — Implementation Brief

**Date:** 2026-10-02. **Author:** Docs. **For:** Frontend Engineer (via Docs Reviewer).
**Status:** 📝 **DRAFT, NOT READY TO BUILD.** §0.2 records a conflict with frozen
screen specs, and §5 Q1 (does this need a governance Change Request?) must be
answered before anyone builds from this brief.

**Origin:** the user ruled on 2026-10-02 (relayed by CTO 3) that report deletion is
to be **ported before `frontend/` is deleted** (Removal Plan
[`docs/governance/Legacy_Frontend_Removal_Plan.md`](../governance/Legacy_Frontend_Removal_Plan.md)
§3 #13; recorded evidence:
[`docs/backend_engineering/02_API_Coverage_Audit.md`](../backend_engineering/02_API_Coverage_Audit.md) §4.4).

**Governing docs (all 🧊 Frozen unless noted):**
[`05_Screen_Inventory.md`](../design/05_Screen_Inventory.md) SCR-09/SCR-10,
[`06_UX_Specifications.md`](../design/06_UX_Specifications.md) SCR-09,
[`09_Component_Inventory.md`](../design/09_Component_Inventory.md) (`ListItem`, `LibraryList`, `Button`),
[`10_Interaction_Patterns.md`](../design/10_Interaction_Patterns.md) ("# Dialogs"),
[`13_States.md`](../design/13_States.md),
[`00_Design_Constitution.md`](../design/00_Design_Constitution.md) (lines 160–161, 254–259, 440, 586–590),
[`frontend_architecture/03.5_Caching_Strategy.md`](../frontend_architecture/03.5_Caching_Strategy.md) AD-3 and
[`03.2_Server_State_Strategy.md`](../frontend_architecture/03.2_Server_State_Strategy.md) AD-4 (✅ Approved).
Test IDs: [`test-ids_convention.md`](test-ids_convention.md).

**Read this session:** `backend/server.py` lines 1477–1493 (the route) and the
scoping tests; `web/features/research-library/` (`integration/`, `application/`,
`ui/LibraryList.tsx`, `ui/LibraryScreen.tsx`, `index.ts`); the other features'
report-list query keys; `web/features/account-setup/ui/SettingsPanel.tsx`
(the existing destructive-confirmation precedent); `web/lib/api/fetch-client.ts`
and `web/lib/errors/app-error.ts`; the legacy implementation
(`frontend/src/components/AppLayout.jsx` lines 147–157, `frontend/src/lib/api.js` line 39).

## 0. What exists today

### 0.1 Backend contract (verified in code, `backend/server.py:1477–1493`)

`DELETE /api/reports/{report_id}` (requires a session; unauthenticated callers get
`401` from `current_user`):
- **Owner-scoped:** `db.reports.delete_one({"id": report_id, "user_id": user["id"]})`.
  The route's own comment says deletion "can't lean on the report id being an
  unguessable UUID" because it is destructive and irreversible.
- **Hard delete:** it removes the `reports` document and then the matching `jobs`
  document (`db.jobs.delete_one`), and evicts any in-process task handle. There is
  no soft-delete flag and no undo in the contract.
- **`404 {"detail": "report not found"}`** when the report does not exist, belongs
  to someone else, **or is a public sample**. Samples have `user_id=None`, so no
  caller's id ever matches; the route makes them effectively read-only. A foreign
  id is indistinguishable from a missing one.
- **Success:** `200 {"deleted": "<report_id>"}`.
- **No cascade to dependents.** The route touches no explanation, comparison or
  other collection. Since `94b01ba`, the `context_report_id` lookups are
  scoped to **owner-or-sample** (`{user_id: caller}` or `{is_sample: true}`), so a
  Learning or follow-up request that names a report the caller has since deleted
  gets no injected context (a no-op) rather than an error.
- **Running reports (not verified):** the pipeline inserts the `reports` document
  on its completion path (`server.py:1149`). A report whose job is still running may
  therefore have no `reports` document yet; if so the route would answer `404`. I
  did not trace this end to end.
- **Backend tests that already exist** (so no backend work is implied):
  `backend_test_iter5.py::test_delete_nonexistent_returns_404`,
  `::test_delete_report_and_verify_removal`, and `test_reports_scoping.py::test_other_user_cannot_delete_my_report`,
  `::test_cannot_delete_sample`.

### 0.2 ⚠ CONFLICT WITH FROZEN DOCS (raised, not decided)

The frozen screen specs do **not** list deletion anywhere:
- **SCR-09 Research Library**, Available Actions: "Browse/filter sessions, reports,
  saved exports, history; open a report; **Resume Session**; open a saved export."
- **SCR-10 Report View**, Available Actions: "Read the report; inspect sources;
  export; return to subject company."
- **`ListItem`** (09): "Properties: title, subtitle/date, primary action." Dependencies
  `Label, Button, Badge`. No secondary or destructive item action is defined.
- The same documents ground the screen in a durability promise: Constitution lines
  160–161 ("Preserve user progress. No action ... may lose the user's work") and
  `06_UX_Specifications.md` SCR-09 ("Resume Session restores prior reasoning and
  sources; nothing is lost on return (J-06)"). A delete control is a deliberate,
  user-initiated exception, which the Constitution allows only as an "Explicit,
  confirmed user-initiated discard" (line 258).

`CLAUDE.md` says an implementation need that conflicts with a frozen doc "is a
stop-and-raise-a-CR situation, not a silent judgment call", and the frozen
"# Uploads" pattern shows the repo's precedent for out-of-spec capabilities: "it
enters via a governance Change Request." **This brief therefore does not decide
whether the user's ruling suffices or a CR is required; that is §5 Q1, and it
blocks the build.**

**Related frozen records (records, not decisions; none of them mentions report deletion).** They concern discarding "in-progress or saved" work in general, and whether a user-requested deletion of a saved report falls under them is part of §5 Q1:
- `docs/frontend_architecture/01_Frontend_Architecture_Constitution.md` lines 372–373 (Law 6): "the frontend must not discard in-progress research across navigation, error, or timeout, and must support Resume Session."
- `docs/frontend_architecture/03.12_Offline_Synchronization_Philosophy.md` lines 53–54: "No synchronization decision — reconnect, retry, conflict resolution, or cache expiry — may discard the user's completed or in-progress research (Law 6)."
- `docs/experience_design/Components/00_Component_System.md` line 67 (🧊 Frozen): "No component action discards in-progress or saved work without explicit, confirmed intent (Law 6; §7.4)."
- `docs/design/00_Design_Constitution.md` line 253 (§7.4): "No interaction discards in-progress or saved research." The "Exceptions" line cited above (258) belongs to the same principle; and line 440 ("Forgiving"): "mistakes are easy to recover from; destructive actions are guarded."
- `docs/design/04_Navigation_Structure.md` line 77: "Moving does not discard the user's research state."
- `docs/design/13_States.md` line 52: "Never lose work — no state discards in-progress research (J-06)."

A second, smaller tension, also not decided here: Constitution line 590 says "Undo:
where feasible, prefer reversible actions and offer undo over hard confirmation
dialogs", while the backend contract is an irreversible hard delete (§0.1) and the
frozen Button rule is "Destructive only for irreversible actions" (09). The
confirmation-dialog route this brief describes follows the Dialogs pattern and
lines 258–259 ("Is any destructive action explicit and confirmed?"); an undo
route would need a backend change (§5 Q3).

### 0.3 What `web/` has today

- **No delete anywhere in `research-library`.** `integration/api.ts` has only
  `fetchReport` and `fetchReports`; the only `DELETE` call in `web/features` is account
  deletion (`account-setup/integration/api.ts:75`).
- **`LibraryList.tsx`** renders each report as one `<button>` row (title = ticker +
  query, a "Sample" `Badge` when `is_sample`, and the date) whose only action is
  `onSelect`. Samples are shown to every account. `ReportListItem` already carries
  `is_sample` (`integration/schemas.ts`).
- **Report lists are cached independently by four features**, under keys with no
  shared prefix: `["research-library","reports",ticker]` (`research-library/application/useReports.ts`),
  `["company-research","reports",ticker]`, `["comparison","reports",ticker]`, and
  `["workspace-home","recent-reports",limit]`. Per-report entries also exist
  (`reportQueryKey(id)` in `research-library` and in `company-research`).
  A feature "communicates only through its public interface; internals are private"
  (`frontend_architecture/02.2_Feature_Organization.md` AD-2, line 47 ff.), which is the
  problem §5 Q5 raises.
- **Destructive-confirmation precedent:** `SettingsPanel.tsx` ("Danger zone", lines
  198–247) uses the foundation `Dialog` (`Dialog`, `DialogTrigger`, `DialogContent`,
  `DialogHeader`, `DialogTitle`, `DialogDescription`, `DialogFooter`), a
  `variant="destructive"` `Button`, a `loading` state, and an **inline** `Banner` for
  failures *inside* the dialog (its comment: a toast's reliability while a Radix modal
  is open is not guaranteed).
- **Error shape:** a `404` from `apiFetch` surfaces as `AppError` with
  `kind: "unknown"` and `status: 404`, with the backend's `detail` as the message
  (`web/lib/errors/app-error.ts`).
- **Legacy behaviour (for reference only):** `AppLayout.jsx:147–157` showed a
  hover-revealed trash icon on each history item, a `window.confirm("Delete this
  report for <name>?")`, a success toast, and a list refresh. It did not hide the
  control on samples.

## 1. Goal

Give a signed-in user a way to permanently delete one of their own research reports
from the Research Library, with an explicit confirmation, honest handling of every
outcome, and a list that no longer shows the deleted report anywhere in the app,
**subject to the §0.2 conflict being resolved first**.

## 2. Scope

**In scope, once §5 Q1 is answered.** The shapes below follow from the backend contract
(§0.1) and existing `web/` patterns; every genuine design choice is an open question
in §5, not a decision.

1. **Integration (`research-library/integration/`).** `deleteReport(id)` in `api.ts`,
   through `apiFetch` with `method: "DELETE"` and a response schema for
   `{"deleted": string}` added to `schemas.ts` (Zod at the trust boundary, as
   `deleteAccount` does).
2. **Application (`research-library/application/`).** A mutation hook
   (`useDeleteReport`), explicit and typed (`03.2` AD-4), that calls the integration
   function and, on success, invalidates the affected cache entries (§3.3).
3. **UI (`research-library/ui/`).** *Default shape, subject to §5 Q2, Q3 and Q8:* a
   confirmation step using the foundation `Dialog` pattern from `SettingsPanel.tsx`: a
   clear destructive primary action, a Cancel that is always safe, focus trapped and
   returned on close (frozen "# Dialogs"). Where the control lives is §5 Q2.
4. **States.** The four states of the action (§3.2), plus the list states the screen
   already has (Loading, Empty, No Results, Error), which must keep working
   after the last report is removed.
5. **Samples (subject to §5 Q6).** The backend answers `404` for samples, so by default the
   control would not be offered on a row with `is_sample` (the data already carries the flag). This is
   an implication of the contract, recorded here so it is not forgotten; §5 Q6 asks
   whether anything else is wanted.
6. **Tests and Test IDs** (§3.5).

**Out of scope:** bulk deletion; undo or soft delete (needs a backend change, §5 Q3);
Saved Exports, Research Sessions and History (no data source today, per
`LibraryScreen.tsx`); account deletion (unchanged); any backend change.

## 3. Approach

### 3.1 Layering and boundaries
Keep to `ui/ → application/ → integration/` (`research-library/README.md`). Nothing
is exported through `index.ts` unless another module needs it. Use `@/components/foundation/*`
wrappers only, never `components/ui` directly (CLAUDE.md). Toasts use `sonner` directly.
No raw hex; use the existing tokens.

### 3.2 The four states of the action

*Default shape unless the §5 answers say otherwise (notably Q3, Q7, Q8 and Q11).*

| State | What the user sees | Notes |
|---|---|---|
| **Confirming** (default) | Dialog naming the report (ticker and query or date) and stating the consequence in plain words, destructive primary, Cancel | Wording is a copy decision, not made here (§5 Q8). Constitution §15 applies: plain, neutral, no hype. |
| **Deleting** (loading) | The destructive button shows `loading`; the dialog cannot be dismissed into an ambiguous state | Pending state per `13_States.md`. |
| **Deleted** (success) | Dialog closes; the row is gone; a brief, non-blocking confirmation (frozen: "Confirm that an action completed ... the confirmation does not block") | A `sonner` toast is the existing pattern. If the list is now empty, the existing Empty state shows. |
| **Failed** (error) | Failure shown **inside the dialog** as an inline `Banner` (the `SettingsPanel.tsx` precedent), the dialog stays open, the list is unchanged, and the user can retry or cancel | See the error table below. |

| Outcome | Source | Suggested handling (open to review) |
|---|---|---|
| `network` / `server` (`5xx`) | `AppError` kinds | Inline error, retry, nothing removed. |
| `auth_required` (`401`) | session expired | Defer to the app's existing signed-out handling; do not swallow it. |
| `404` (`kind: "unknown"`, `status: 404`) | already deleted, not the user's, a sample, or not yet saved | §5 Q7 asks how to treat it; the list should in any case be refreshed so the UI converges. |
| `validation` | response did not match `{"deleted": string}` | Inline error; refresh the list. |

### 3.3 Cache invalidation
`03.5` AD-3: mutations "invalidate or update the specific server-state entries they
affect ... using the semantic query-key hierarchy ... not broad cache-clearing."
After a successful delete, **every** place that lists or reads that report must stop
showing it: the four list keys and the two per-report keys in §0.3. The three keys
owned by other features are the boundary problem in §5 Q5. Optimism: `03.2` (line 94)
says optimism is "conservative — never for trust-critical/AI/financial data"; whether
deletion may be optimistic is §5 Q11.

### 3.4 Structural note for `LibraryList.tsx`
Each row is currently **one `<button>`** that is also the whole-row focus target (frozen
`ListItem`: "Full item focusable; labeled with subject and date"; SCR-09: "Enter opens
focused item"). A delete control cannot be a button nested inside that button (invalid
HTML, broken keyboard and accessibility semantics). Adding one means restructuring the
row, for example a row container with two sibling controls. That changes the frozen
`ListItem` shape, which is part of the §0.2 conflict, and is mentioned so the
Engineer does not discover it mid-build.

### 3.5 Test IDs
Follow `test-ids_convention.md`: select by role and accessible name first, and use a
`data-testid` only where that cannot identify the element, and only from
`web/lib/constants/testIds.ts`, in the same change as the test that needs it. A
per-row delete control is a plausible case, since two reports can share a ticker and
a query. If one is needed, add it under `RESEARCH_LIBRARY` as a function of the report
id (the file's documented convention for dynamic IDs).

### 3.6 Edge cases to cover (behaviour is partly open: see §5)
- Deleting the last remaining report → the Empty state.
- Deleting while a ticker filter is active → the filtered list updates and a
  now-empty filter shows No Results, not Empty.
- A report deleted in another tab, or already gone → the `404` path.
- A deleted report's deep links: `/reports/<id>` (Report View's own error state),
  Comparison's `?ids=`, Overview's `?job=`. Whether Comparison handles a missing id
  gracefully was **not verified**.
- Keyboard: open the dialog, Cancel and confirm without a pointer; focus returns to
  a sensible element (the next row, or the list when it empties).

## 4. Acceptance Criteria

- [ ] **Gate:** §5 Q1 is answered in writing (CR required or not), and any frozen-doc
      amendment it requires has landed, **before the build starts.**
- [ ] A signed-in user can delete one of their own reports from the Research Library
      (**where the control lives: subject to Q2**), through a confirmation dialog that
      follows the frozen Dialogs pattern (primary + Cancel, focus trapped and returned,
      dismissible, Cancel safe) (**dialog form and copy: subject to Q3 and Q8**).
- [ ] All four action states are implemented and tested: Confirming, Deleting,
      Deleted, Failed (default shape: error inline in the dialog, dialog stays open,
      list unchanged; **subject to Q7 and Q8**).
- [ ] After a successful delete the report is absent from the Research Library,
      Workspace Home's recent reports, the Comparison picker and Company Research's
      report list **without a manual reload**, using targeted invalidation (§3.3), and
      its per-report cache entries are gone (**mechanism subject to Q5; optimistic or
      confirmed update subject to Q11**).
- [ ] Public samples (`is_sample`) never show a delete control (**default; subject to Q6**).
- [ ] `404`, network, server, auth-required and validation outcomes are each handled
      as in §3.2 (as amended by the §5 answers) and each has a test.
- [ ] The existing list states (Loading, Empty, No Results, Error) still behave as
      before; the Empty and No Results cases after a delete are tested.
- [ ] No nested interactive elements (**the row restructuring depends on Q1 and Q2**): the row keeps a valid structure and full keyboard
      operability; the delete control has an accessible name that identifies the
      report; `jest-axe` is clean on the changed components.
- [ ] No inline `data-testid` string literals; any test ID comes from `testIds.ts`.
- [ ] `npm run verify` and `npm run build` are green; no backend change.
- [ ] **Live-verified against the running stack** (two accounts): delete own report
      → gone everywhere; attempt on a sample is not offered (subject to Q6); deleting a report the
      other account owns is not possible from the UI (backend `404`); the deleted
      report's `/reports/<id>` shows the existing error state.
- [ ] Removal Plan §3 #13 and §4.1 item 5 updated to record the port as done, with the
      commit hash (a docs follow-up, not part of the build).

## 5. Open Questions — not decided here

- **Q1 (blocking): is a governance Change Request required?** Deletion is absent from
  the frozen SCR-09/SCR-10 Available Actions and the `ListItem` definition (§0.2). The
  user ruled "port before deleting `frontend/`", but that ruling does not say whether
  it amends the frozen specs. Options for the CTO and user: (a) treat the ruling as
  sufficient authority and record a deviation note; (b) raise a CR to amend SCR-09
  (and `ListItem`/`LibraryList`) first, as the frozen "Uploads" text and CLAUDE.md
  describe. Docs does not choose.
- **Q2: where does the control live?** The Library row, Report View (SCR-10), both, or
  inside a per-row overflow menu (the foundation `DropdownMenu` has a destructive
  item variant). Legacy put it on the history list. SCR-10's frozen actions are also
  silent on deletion.
- **Q3: hard delete or undo?** The backend contract is an irreversible hard delete.
  Constitution line 590 prefers undo over hard confirmation "where feasible"; undo
  would need a backend change (soft delete, a grace period, a restore route). Is the
  confirmation-dialog route acceptable as-is?
- **Q4: per-item or bulk?** Legacy was per-item only. Bulk is out of scope here
  unless the user wants it.
- **Q5: how do the other features' caches learn about a deletion?** Their list keys
  share no prefix, and features may not import each other's internals. Candidate
  mechanisms: a small shared key helper under `lib/`; a predicate-based invalidation
  through `lib/api/query-client`; a shared key convention; or **a feature's `index.ts`
  public surface** (for example `research-library` exporting an invalidation helper that
  other features import from `@/features/research-library`). That last route is not
  foreign to the repo: `company-research` (`ui/CopilotPanel.tsx`) and `learning`
  (`ui/LearningScreen.tsx`) already import from `@/features/account-setup`. Each has trade-offs against
  `02.2` AD-2 and `03.5` AD-3, and this may itself need an architecture ruling.
- **Q6: samples.** The brief assumes the control is hidden on `is_sample` rows
  because the backend returns `404`. Confirm, or specify something else (e.g. a
  disabled control with an explanation).
- **Q7: how should a `404` be treated?** As a failure ("couldn't delete"), or as
  "already gone" with a neutral message plus a refresh? The backend gives the same
  answer for missing, not-yours and sample.
- **Q8: confirmation strength and copy.** A plain confirm dialog, or typed
  confirmation as `SettingsPanel.tsx` uses for account deletion? What the dialog says
  (including whether to mention that comparisons or Learning requests that referenced
  the report will lose that context) is a copy decision.
- **Q9: dependent artifacts.** The route does not cascade. Saved Exports and
  Sessions do not exist yet; comparisons and Learning requests may reference the
  report. Is anything beyond a dialog sentence required?
- **Q10: reports that are still running.** Per §0.1 the route may return `404` for a
  report whose job has not completed. Should the UI offer cancel instead, or nothing?
  (Not verified in code; needs a quick backend check by whoever builds this.)
- **Q11: optimistic or confirmed update?** `03.2` says optimism is never for
  trust-critical data. Is a deletion that fails after the row has disappeared
  acceptable, or must the UI wait for the `200`?
