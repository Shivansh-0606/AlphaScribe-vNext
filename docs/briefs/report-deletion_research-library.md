# Report Deletion in Research Library (SCR-09) — Implementation Brief

**Date:** 2026-10-02 (drafted); updated 2026-10-05. **Author:** Docs. **For:** Frontend Engineer (via Docs Reviewer).
**Status:** ✅ **Ready to build** (reviewed and passed by Docs Reviewer 2 on 2026-10-05). Q8 and all user-visible copy stay `TBD-user` placeholders until the user signs off. The blocking question, whether a
governance Change Request was needed, is answered: [`CR-SCOPE-004`](../governance/change_requests/CR-SCOPE-004_Report_Deletion.md) was **approved on 2026-10-05** (decided by the
user, as relayed by CTO 3; see the CR's §13). The Q1–Q11 answers are recorded in §5. **One thing is still
open on the user's side: the confirmation dialog's wording (Q8).** All user-visible copy in this feature is
a placeholder marked `TBD-user`, and **the build must not ship final copy without the user's sign-off.**

**Origin:** the user ruled on 2026-10-02 (relayed by CTO 3) that report deletion is
to be **ported before `frontend/` is deleted** (Removal Plan
[`docs/governance/Legacy_Frontend_Removal_Plan.md`](../governance/Legacy_Frontend_Removal_Plan.md)
§3 #13; recorded evidence:
[`docs/backend_engineering/02_API_Coverage_Audit.md`](../backend_engineering/02_API_Coverage_Audit.md) §4.4).
On 2026-10-03 the user ruled that it is to be treated as needing a Change Request; on 2026-10-05 the CR
was approved (confirmed hard delete, no undo). The frozen Screen Inventory, UX Specifications, Wireframes
and Component Inventory were amended under it (each 0.1.1 → 1.0.0, MAJOR, re-freeze pending approver confirmation).

**Governing docs (all 🧊 Frozen unless noted):**
[`05_Screen_Inventory.md`](../design/05_Screen_Inventory.md) SCR-09 (v1.0.0, amended by CR-SCOPE-004; re-freeze pending),
[`06_UX_Specifications.md`](../design/06_UX_Specifications.md) SCR-09 (v1.0.0),
[`07_Wireframes.md`](../design/07_Wireframes.md) SCR-09 (v1.0.0),
[`09_Component_Inventory.md`](../design/09_Component_Inventory.md) (v1.0.0: `ListItem`, `LibraryList`; and `Button`),
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

## Decisions recorded 2026-10-05

Attributed to the user, **relayed by CTO 3** (not verified first-hand by the author of this brief). Verbatim as
relayed: *"Approve CR-SCOPE-004 and go with your recommendations"*. "Go with your recommendations" was
relayed as adopting the "CTO-adjacent recommendation" for each of Q2–Q11 in
[`report-deletion_decision-sheet.md`](report-deletion_decision-sheet.md), **except Q8** (wording stays with
the user). The decided shape is in §5; the table is the short form.

| Q | Decided shape |
|---|---|
| Q1 | CR required: **raised and APPROVED** 2026-10-05 (Question A: yes; Question B: confirmed hard delete, no undo; undo is a later enhancement through its own CR) |
| Q2 | A **per-row menu on the Library list** (SCR-09). **Not** on Report View (SCR-10). See the scope note below |
| Q3 | **Confirmed hard delete** for launch; no undo |
| Q4 | **Per-item only** |
| Q5 | A **shared report-key factory** at `web/lib/api/report-keys.ts` that the four features adopt: **CTO architecture ruling 2026-10-05**, details in §3.3 (including a `compare(ids)`/`compares()` key for the comparison feature's cached compares; confirmed by CTO 3 2026-10-05, subject to Docs Reviewer check; the factory stays entity-key-only: no fetching, no feature imports) |
| Q6 | The control is **hidden** on sample (`is_sample`) rows |
| Q7 | A `404` is treated as **"already gone"**: a neutral message and a list refresh |
| Q8 | A plain confirm dialog naming the report; **its wording is `TBD-user` placeholder copy** (one constants file, §3.7) until the user signs off |
| Q9 | **The Frontend Engineer checks Comparison with a deleted id before the build's PR** (§3.6); no extra dialog text unless it breaks |
| Q10 | **No action**: the Library lists completed reports only |
| Q11 | **Confirmed update**: wait for the `200` |

**Scope note (confirmed by CTO 3, 2026-10-05).** The relayed answer to the CR's Question A names SCR-09, SCR-10 and
`ListItem`, while the adopted Q2 places the control on the Library list only. **CTO 3 confirmed Library-list-only**:
the frozen amendments match (SCR-10 and `ReportDocument` were not amended), and **Report View deletion would need a
later Change Request.**

**Placeholder-copy rule.** Every user-visible string this feature adds (dialog title, body and button labels,
the success confirmation, the "already gone" message, the failure message) is written as a clearly marked
`TBD-user` placeholder, in code and in tests. Q8 names the dialog wording explicitly; the same rule is applied
by analogy to the other strings, because the project does not invent product copy (Constitution §15), and
that extension was **confirmed by CTO 3 on 2026-10-05** as conservative and consistent with Constitution §15.
The mechanics are in §3.7.

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
- **Running reports (aligned with the decided Q10):** the pipeline inserts the `reports` document
  on its completion path (`server.py:1149`), and `GET /reports` reads only that collection, so the Library
  list never contains a running report and this control cannot be offered for one. (A delete aimed at a
  running job's id by other means would find no `reports` document and answer `404`; no UI path produces that.)
- **Backend tests that already exist** (so no backend work is implied):
  `backend_test_iter5.py::test_delete_nonexistent_returns_404`,
  `::test_delete_report_and_verify_removal`, and `test_reports_scoping.py::test_other_user_cannot_delete_my_report`,
  `::test_cannot_delete_sample`.

### 0.2 Conflict with the frozen docs: RESOLVED by CR-SCOPE-004 (approved 2026-10-05)

*The text below records the conflict as it stood before the CR; it is kept for the trail. Resolution is at the end of this subsection.*

Before the CR, the frozen screen specs did **not** list deletion anywhere:
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
enters via a governance Change Request." **That is the route taken:** the user ruled on 2026-10-03 that this is to be treated as needing a CR, and [`CR-SCOPE-004`](../governance/change_requests/CR-SCOPE-004_Report_Deletion.md) was approved on 2026-10-05. SCR-09's Available Actions, the SCR-09 UX and wireframe entries, and `ListItem`/`LibraryList` were amended accordingly (each document now 1.0.0, citing the CR; re-freeze pending approver confirmation).

**Related frozen records (records, not decisions; none of them mentions report deletion).** They concern discarding "in-progress or saved" work in general; whether a user-requested deletion of a saved report falls under them was part of Q1, which the CR approval resolved:
- `docs/frontend_architecture/01_Frontend_Architecture_Constitution.md` lines 372–373 (Law 6): "the frontend must not discard in-progress research across navigation, error, or timeout, and must support Resume Session."
- `docs/frontend_architecture/03.12_Offline_Synchronization_Philosophy.md` lines 53–54: "No synchronization decision — reconnect, retry, conflict resolution, or cache expiry — may discard the user's completed or in-progress research (Law 6)."
- `docs/experience_design/Components/00_Component_System.md` line 67 (🧊 Frozen): "No component action discards in-progress or saved work without explicit, confirmed intent (Law 6; §7.4)."
- `docs/design/00_Design_Constitution.md` line 253 (§7.4): "No interaction discards in-progress or saved research." The "Exceptions" line cited above (258) belongs to the same principle; and line 440 ("Forgiving"): "mistakes are easy to recover from; destructive actions are guarded."
- `docs/design/04_Navigation_Structure.md` line 77: "Moving does not discard the user's research state."
- `docs/design/13_States.md` line 52: "Never lose work — no state discards in-progress research (J-06)."

A second, smaller tension, **resolved by the CR's Question B (confirmed hard delete, no undo for launch; undo is a later CR)**: Constitution line 590 says "Undo:
where feasible, prefer reversible actions and offer undo over hard confirmation
dialogs", while the backend contract is an irreversible hard delete (§0.1) and the
frozen Button rule is "Destructive only for irreversible actions" (09). The
confirmation-dialog route this brief describes follows the Dialogs pattern and
lines 258–259 ("Is any destructive action explicit and confirmed?"); an undo
route would have needed a backend change (§5 Q3).

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
  `["workspace-home","recent-reports",limit]`; comparison also caches `["comparison","compare",sortedIds]` (`useCompare.ts`, `staleTime` 30 s). Per-report entries also exist
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
as authorised by [`CR-SCOPE-004`](../governance/change_requests/CR-SCOPE-004_Report_Deletion.md) (approved 2026-10-05).

## 2. Scope

**In scope.** The shapes below follow from the backend contract (§0.1), existing `web/`
patterns, and the decisions in §5.

1. **Integration (`research-library/integration/`).** `deleteReport(id)` in `api.ts`,
   through `apiFetch` with `method: "DELETE"` and a response schema for
   `{"deleted": string}` added to `schemas.ts` (Zod at the trust boundary, as
   `deleteAccount` does).
2. **Application (`research-library/application/`).** A mutation hook
   (`useDeleteReport`), explicit and typed (`03.2` AD-4), that calls the integration
   function and, on success, invalidates the affected cache entries (§3.3).
3. **UI (`research-library/ui/`).** A **per-row action menu** on the Library list (Q2; the
   foundation `DropdownMenu` has a destructive item variant, and the frozen Experience Design
   component system defines a dropdown "action menu", `Components/03_Selection_Controls.md` line 222),
   opening a confirmation step that uses the foundation `Dialog` pattern from `SettingsPanel.tsx`: a
   clear destructive primary action, a Cancel that is always safe, focus trapped and
   returned on close (frozen "# Dialogs"). **Dialog wording is `TBD-user` placeholder copy (Q8).**
4. **States.** The four states of the action (§3.2), plus the list states the screen
   already has (Loading, Empty, No Results, Error), which must keep working
   after the last report is removed.
5. **Samples (Q6).** The backend answers `404` for samples, so the control is **not offered** on a
   row with `is_sample` (the data already carries the flag).
6. **Tests and Test IDs** (§3.5).

**Out of scope:** bulk deletion (Q4); undo or soft delete (a later enhancement through its own CR, Q3);
a delete action on Report View (Q2; see the scope note above);
Saved Exports, Research Sessions and History (no data source today, per
`LibraryScreen.tsx`); account deletion (unchanged); any backend change.

## 3. Approach

### 3.1 Layering and boundaries
Keep to `ui/ → application/ → integration/` (`research-library/README.md`). Nothing
is exported through `index.ts` unless another module needs it. Use `@/components/foundation/*`
wrappers only, never `components/ui` directly (CLAUDE.md). Toasts use `sonner` directly.
No raw hex; use the existing tokens.

### 3.2 The four states of the action

*The decided shape (§5). Every user-visible string below is a `TBD-user` placeholder.*

| State | What the user sees | Notes |
|---|---|---|
| **Confirming** (default) | Dialog naming the report (ticker and query or date) and stating the consequence in plain words, destructive primary, Cancel | Wording is `TBD-user` placeholder copy until the user signs off (Q8). Constitution §15 applies: plain, neutral, no hype. |
| **Deleting** (loading) | The destructive button shows `loading`; the dialog cannot be dismissed into an ambiguous state | Pending state per `13_States.md`. |
| **Deleted** (success) | Dialog closes; the row is gone; a brief, non-blocking confirmation (frozen: "Confirm that an action completed ... the confirmation does not block") | A `sonner` toast is the existing pattern. If the list is now empty, the existing Empty state shows. |
| **Failed** (error) | Failure shown **inside the dialog** as an inline `Banner` (the `SettingsPanel.tsx` precedent), the dialog stays open, the list is unchanged, and the user can retry or cancel | See the error table below. |

| Outcome | Source | Handling (decided) |
|---|---|---|
| `network` / `server` (`5xx`) | `AppError` kinds | Inline error, retry, nothing removed. |
| `auth_required` (`401`) | session expired | Defer to the app's existing signed-out handling; do not swallow it. |
| `404` (`kind: "unknown"`, `status: 404`) | already deleted, not the user's, a sample, or not yet saved | Treated as "already gone" (Q7): a neutral message (`TBD-user` placeholder) and a list refresh so the UI converges. |
| `validation` | response did not match `{"deleted": string}` | Inline error; refresh the list. |

### 3.3 Cache invalidation: CTO ARCHITECTURE RULING 2026-10-05 (Q5)

`03.5` AD-3: mutations "invalidate or update the specific server-state entries they
affect ... using the semantic query-key hierarchy ... not broad cache-clearing."
After a successful delete, **every** place that lists or reads that report must stop
showing it: the four list keys and the per-report keys in §0.3. Optimism: `03.2` (line 94)
says optimism is "conservative — never for trust-critical/AI/financial data"; the
update is **confirmed**, not optimistic (Q11).

**Ruling.** Adopt the decision sheet's Q5 recommendation (a shared report-key factory) as a **CTO architecture
ruling dated 2026-10-05**. The specifics below are the simplest choice that fits the frozen architecture docs
(`02.2_Feature_Organization.md` AD-2 and AD-3: shared modules hold cross-cutting, feature-agnostic concerns and
depend on no feature; features talk through public surfaces), and are **confirmed by CTO 3 2026-10-05, subject to Docs Reviewer check**. Constraint: the `reportKeys` factory stays entity-key-only (no fetching, no feature imports); the Docs Reviewer is to check that this fits 02.2 AD-2/AD-3:

- **Module:** a new `web/lib/api/report-keys.ts` (the shared server-state layer, beside `fetch-client.ts` and
  `query-client.ts`). It exports one object, `reportKeys`:
  - `reportKeys.list(feature, ...params)` → `["reports", "list", feature, ...params]`
  - `reportKeys.lists()` → `["reports", "list"]` (the prefix that matches every feature's list)
  - `reportKeys.detail(id, feature)` → `["reports", "detail", id, feature]` and
    `reportKeys.status(id, feature)` → `["reports", "status", id, feature]`
  - `reportKeys.detailsFor(id)` → `["reports", "detail", id]` and `reportKeys.statusFor(id)` →
    `["reports", "status", id]` (prefixes). The report id comes **before** the feature name so one prefix by id
    matches every feature's entry for that report.
  - `reportKeys.compare(ids)` → `["reports", "compare", ...sortedIds]` and `reportKeys.compares()` →
    `["reports", "compare"]` (the prefix). *Added by CTO 3, 2026-10-05:* the comparison feature's
    `useCompare.ts` caches full report documents for a selection (`["comparison","compare",sorted]`, `staleTime` 30 s),
    so a deleted report could otherwise still show in a cached compare.
- **Who edits what** (all by the Frontend Engineer in the build PR; no feature imports another feature):
  1. the new file plus a small unit test of the prefix relationships;
  2. a key-construction edit in **seven files**, each importing only from `@/lib/api/report-keys`:
     `research-library/application/useReports.ts` (list) and `useReport.ts` (`reportQueryKey` → `detail`);
     `company-research/application/useReports.ts` (list) and `useReport.ts` (`reportQueryKey` → `detail`,
     `reportStatusQueryKey` → `status`); `comparison/application/useReports.ts` (list) and `comparison/application/useCompare.ts` (`["comparison","compare",sorted]` → `compare(sorted)`);
     `workspace-home/application/useWorkspaceHome.ts` (the `recent-reports` list → `list("workspace-home", "recent", limit)`).
     The exported function names `reportQueryKey` and `reportStatusQueryKey` stay, so their other callers
     (for example `company-research/application/useResearchJob.ts`'s `setQueryData`) are untouched;
  3. any existing test that asserts an old key array is updated in the same change;
  4. the delete mutation (`research-library/application/useDeleteReport.ts`) is the only new consumer.
- **`removeQueries` versus `invalidateQueries`:** on success, **list keys are invalidated**
  (`queryClient.invalidateQueries({ queryKey: reportKeys.lists() })`, which refetches the active ones), and the
  **cached compares are invalidated** (`queryClient.invalidateQueries({ queryKey: reportKeys.compares() })`), and the
  **per-report entries are removed**, not invalidated, because the report no longer exists
  (`queryClient.removeQueries({ queryKey: reportKeys.detailsFor(id) })` and
  `queryClient.removeQueries({ queryKey: reportKeys.statusFor(id) })`).
- **Not chosen:** predicate-based invalidation (it relies on a naming convention nobody enforces); a feature exporting
  an invalidation helper that others import (it inverts the dependency, or needs four helpers and a caller); relying
  on `staleTime` (it would leave the report visible elsewhere, which fails the no-manual-reload criterion).

### 3.4 Structural note for `LibraryList.tsx`
Each row is currently **one `<button>`** that is also the whole-row focus target (frozen
`ListItem`: "Full item focusable; labeled with subject and date"; SCR-09: "Enter opens
focused item"). A delete control cannot be a button nested inside that button (invalid
HTML, broken keyboard and accessibility semantics). Adding one means restructuring the
row, for example a row container with two sibling controls (the whole-row primary action plus
the per-row menu). `ListItem` now allows an optional secondary action (09 v1.0.0, CR-SCOPE-004), so this
is within the amended spec. It is mentioned so the Engineer does not discover it mid-build.

### 3.5 Test IDs
Follow `test-ids_convention.md`: select by role and accessible name first, and use a
`data-testid` only where that cannot identify the element, and only from
`web/lib/constants/testIds.ts`, in the same change as the test that needs it. A
per-row delete control is a plausible case, since two reports can share a ticker and
a query. `RESEARCH_LIBRARY` in `testIds.ts` is **currently empty by design**: IDs are
added **on demand**, in the same change as the test that needs one. If one is needed here, add it as a
function of the report id (the file's documented convention for dynamic IDs).

### 3.6 Edge cases to cover
- Deleting the last remaining report → the Empty state.
- Deleting while a ticker filter is active → the filtered list updates and a
  now-empty filter shows No Results, not Empty.
- A report deleted in another tab, or already gone → the `404` path.
- A deleted report's deep links: `/reports/<id>` (Report View's own error state),
  Comparison's `?ids=`, Overview's `?job=`. The backend's `POST /reports/compare` silently drops ids it
  cannot find and answers `404 "fewer than 2 reports found"` if fewer than two remain
  (`server.py:1819–1842`). **The Frontend Engineer checks this before the build's PR** (Q9): load Comparison with
  `?ids=` containing a deleted id against the running stack. **"Breaks" means Comparison renders a crash or an
  unhandled error for a deleted id**; a silently shorter set is acceptable (it is what the backend does), and a
  *handled* error state for "fewer than 2 remain" is acceptable. The finding goes in the engineer's report and here:
  **Q9 finding: _not yet recorded_.**
- Keyboard: open the menu, choose Delete, Cancel and confirm without a pointer; the focus rules are in §3.8.

### 3.7 Copy mechanics (placeholder strings, Q8)

- **One file:** every user-visible string this feature adds lives in a single constants file,
  `web/features/research-library/ui/copy.ts` (for example one exported `REPORT_DELETE_COPY` object: menu trigger
  and item labels, dialog title and body, confirm and cancel labels, success confirmation, "already gone" message,
  failure message). The file carries a **`TODO(user-copy)`** marker so the whole set is greppable.
- **Each value is visibly a placeholder** (prefixed `TBD-user`), so nobody mistakes it for approved copy.
- **No other file contains those strings.** Components render from the constants, and **tests assert through the
  constants, never through string literals**, so replacing the copy later changes one file.
- **Merge versus deploy:** placeholder strings **may merge to `main`**. A **release/deploy gate item** requires the
  user-approved final copy to replace them **before any deploy**.

### 3.8 Focus and accessible names (menu → dialog → list)

- The menu trigger has an **accessible name that includes the report** (for example its ticker and query or date,
  from the placeholder copy), so each row's trigger is distinguishable to a screen reader.
- **A one-item menu (Delete only) is acceptable for launch.**
- After the actions menu closes on choosing Delete, **focus moves into the confirm Dialog**.
- **Cancel** returns focus to that row's menu trigger.
- **On success**, focus moves to the list heading ("Research Library"), because the row and its trigger are gone.
- **On failure**, focus stays in the dialog and the inline error is announced.
- These behaviours are asserted in tests (the focus rules are testable with Testing Library and `jest-axe`).

## 4. Acceptance Criteria

- [x] **Gate: approval given by the user in chat 2026-10-05, relayed by CTO 3 (CR-SCOPE-004 §13)**, and the
      frozen-doc amendments it authorised are written (05, 06, 07 and 09, each now 1.0.0, re-freeze pending
      approver confirmation). The build starts after Docs Reviewer has checked this brief and those amendments.
- [ ] A signed-in user can delete one of their own reports from the Research Library
      through a **per-row menu on the Library list** (Q2), opening a confirmation dialog that
      follows the frozen Dialogs pattern (primary + Cancel, focus trapped and returned,
      dismissible, Cancel safe). **Dialog copy is `TBD-user` placeholder text and no final copy ships
      without the user's sign-off (Q8).**
- [ ] All four action states are implemented and tested: Confirming, Deleting,
      Deleted, Failed (error inline in the dialog, dialog stays open, list unchanged;
      a `404` shows the neutral "already gone" message and refreshes the list, Q7).
- [ ] After a successful delete the report is absent from the Research Library,
      Workspace Home's recent reports, the Comparison picker and Company Research's
      report list **without a manual reload**, using targeted invalidation (§3.3), and
      its per-report cache entries are gone, via the shared report-key factory (Q5), and the UI
      waits for the `200` before removing the row (Q11).
- [ ] A cached Comparison result (`reportKeys.compare(ids)`) that contains the deleted id no longer shows it after the delete (test: seed a compare cache entry, delete, assert it is invalidated).
- [ ] Public samples (`is_sample`) never show a delete control (Q6).
- [ ] `404`, network, server, auth-required and validation outcomes are each handled
      as in §3.2 (as amended by the §5 answers) and each has a test.
- [ ] The existing list states (Loading, Empty, No Results, Error) still behave as
      before; the Empty and No Results cases after a delete are tested.
- [ ] No nested interactive elements: the row keeps a valid structure and full keyboard
      operability; the delete control has an accessible name that identifies the
      report; `jest-axe` is clean on the changed components.
- [ ] No inline `data-testid` string literals; any test ID comes from `testIds.ts`, added on demand
      with the test that needs it (`RESEARCH_LIBRARY` is empty today).
- [ ] The Comparison check from Q9 is done by the Frontend Engineer before the build's PR (§3.6), and its
      finding is recorded in the engineer's report and in §3.6.
- [ ] Every user-visible string comes from `ui/copy.ts` (§3.7), tests assert through those constants, and the
      `TODO(user-copy)` marker is present.
- [ ] Focus and accessible-name behaviour is implemented and tested as in §3.8.
- [ ] **Release/deploy gate (not a merge gate):** the user-approved final copy replaces the `TBD-user`
      placeholders before any deploy.
- [ ] `npm run verify` and `npm run build` are green; no backend change.
- [ ] **Live-verified against the running stack** (two accounts): delete own report
      → gone everywhere; attempt on a sample is not offered; deleting a report the
      other account owns is not possible from the UI (backend `404`); the deleted
      report's `/reports/<id>` shows the existing error state.
- [ ] Removal Plan §3 #13 and §4.1 item 5 updated to record the port as done, with the
      commit hash (a docs follow-up, not part of the build).

## 5. Questions Q1–Q11 and their answers (2026-10-05)

Decisions attributed to the user, **relayed by CTO 3**; each adopts the decision sheet's "CTO-adjacent
recommendation" ([`report-deletion_decision-sheet.md`](report-deletion_decision-sheet.md)) except Q8.

- **Q1: is a governance Change Request required?** **Decided: yes. CR-SCOPE-004 was raised and approved on
  2026-10-05** (Question A: yes; Question B: confirmed hard delete, no undo).
- **Q2: where does the control live?** **Decided:** a per-row menu on the Library list (SCR-09). Not on Report
  View. *Needs CTO confirmation:* the relayed CR answer also names SCR-10 (see the scope note near the top).
- **Q3: hard delete or undo?** **Decided:** confirmed hard delete for launch; undo is a later enhancement
  through its own CR (it needs backend work: a soft-delete flag, a restore route, a retention rule).
- **Q4: per-item or bulk?** **Decided:** per-item only.
- **Q5: how do the other features' caches learn about a deletion?** **Decided, as a CTO architecture ruling
  dated 2026-10-05:** a shared report-key factory at `web/lib/api/report-keys.ts` that all four features adopt, so one
  invalidation by the shared prefix refreshes them all. The module path, exports (including `compare`/`compares`), who edits what (seven files), and
  `invalidateQueries` (list and compare keys) versus `removeQueries` (per-report entries) are in §3.3, **confirmed by CTO 3 2026-10-05, subject to Docs Reviewer check** (entity-key-only factory).
- **Q6: samples.** **Decided:** hide the control on `is_sample` rows.
- **Q7: how should a `404` be treated?** **Decided:** as "already gone": a neutral message plus a list
  refresh. The message text is a `TBD-user` placeholder.
- **Q8: confirmation strength and copy.** **Decided:** a plain confirm dialog that names the report (ticker,
  query, date). **Exception, kept for the user:** the dialog's wording. It is `TBD-user` placeholder copy, and
  the build must not ship final copy without the user's sign-off; all such strings live in `ui/copy.ts` (§3.7), and
  final copy is a release/deploy gate. (Whether the dialog should mention that
  comparisons or Learning requests that used the report will lose that context is part of the same copy
  decision.)
- **Q9: dependent artifacts.** **Decided:** the Frontend Engineer checks how Comparison handles a deleted id
  before the build's PR ("breaks" = a crash or unhandled error; a silently shorter set is acceptable); add no
  dialog text unless it breaks. The finding is recorded in §3.6. (Backend half already verified: `POST /reports/compare` drops missing ids
  silently and errors only if fewer than two remain; the `web/` half is the check.)
- **Q10: reports that are still running.** **Decided:** no action. `GET /reports` reads completed reports only, so
  this list cannot offer a running report. Cancelling a running report remains the existing, separate action.
- **Q11: optimistic or confirmed update?** **Decided:** confirmed. The UI waits for the `200` and then removes
  the row.
