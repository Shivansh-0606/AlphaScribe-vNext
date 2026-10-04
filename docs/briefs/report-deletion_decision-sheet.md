# Report Deletion — Decision Sheet for the 11 Open Questions

**Date:** 2026-10-03. **Author:** Docs (Docs generator 3), at the request of CTO 3. **For:** the user.
**Status:** 🗄 **SUPERSEDED by the 2026-10-05 decisions** (below). Kept as the historical record of the analysis. It was written on 2026-10-03 as a DRAFT for the user and is not itself a decision.

> **Superseded 2026-10-05.** The user approved CR-SCOPE-004 and adopted this sheet's "CTO-adjacent recommendation" for Q2–Q11 **except Q8** (the dialog wording stays for the user), as relayed by CTO 3. The decided answers are recorded in [`report-deletion_research-library.md`](report-deletion_research-library.md) ("Decisions recorded 2026-10-05" and §5) and in the CR's §13. The body of this sheet below is **unchanged** except for Q1 and the "Where things stand" paragraph, and its present-tense wording about open questions describes 2026-10-03.
**Companion documents:**
[`report-deletion_research-library.md`](report-deletion_research-library.md) (the implementation brief,
whose §5 held Q1–Q11 as open questions; as committed in `a4670c4` and since updated with the 2026-10-05
decisions) and the Change Request (approved 2026-10-05)
[`CR-SCOPE-004_Report_Deletion.md`](../governance/change_requests/CR-SCOPE-004_Report_Deletion.md).

**How to read this sheet.** For each question there are two clearly separated parts:
- **Facts and options** — what the repo says, with cites, and the realistic options with their
  trade-offs. These are the parts to check.
- **CTO-adjacent recommendation** — my view, **labelled as such, and not a fact and not a decision.**
  It is deliberately the *shortest* part of each entry. Where a question is really a product, copy or
  legal judgment I say so and make no recommendation. Nothing here changes any frozen document.

**Where things stand (as of 2026-10-05; the rest of the sheet describes 2026-10-03).** The user ruled on 2026-10-03 (relayed by CTO 3) that report deletion is to be treated as needing a governance Change Request, and **on 2026-10-05 approved CR-SCOPE-004** and adopted the recommendations below except Q8 (see the banner at the top). *As originally written on 2026-10-03:* the build stays blocked until the CR is raised and answered. Several answers below depend on how the CR is decided (Q2, Q3 above all), so the sheet
notes which questions are **independent of the CR** and could be settled now.

---

## Summary table

| Q | Question | Depends on the CR? | Short form of my recommendation (detail below) |
|---|---|:---:|---|
| Q1 | Is a Change Request required? | — | **Answered: yes; CR-SCOPE-004 approved 2026-10-05** |
| Q2 | Where does the control live? | Yes | Library list, via a per-row menu |
| Q3 | Hard delete or undo? | **Yes (this is CR Question B)** | Confirmed hard delete for launch; revisit undo later |
| Q4 | Per-item or bulk? | No | Per-item only |
| Q5 | How do other features' caches learn about a deletion? | No | A shared report-key factory under `lib/`; needs an architecture ruling |
| Q6 | Samples | No | Hide the control on samples |
| Q7 | How is a `404` treated? | No | "Already gone" with a neutral message and a list refresh |
| Q8 | Confirmation strength and copy | Partly | Plain confirm naming the report; **copy is yours to approve** |
| Q9 | Dependent artifacts | No | Verify Comparison's handling before the build; no extra dialog text unless it breaks |
| Q10 | Reports still running | No | Largely moot for the Library; no action |
| Q11 | Optimistic or confirmed update | No | Confirmed (wait for the `200`) |

---

## Q1 — Is a governance Change Request required?

**Facts.**
- The frozen SCR-09 and SCR-10 "Available Actions" and the `ListItem` definition contain no delete
  action (`docs/design/05_Screen_Inventory.md`; `09_Component_Inventory.md`). The full traceability is
  in CR-SCOPE-004 §3.
- `CLAUDE.md` describes a conflict with a frozen doc as "a stop-and-raise-a-CR situation, not a silent
  judgment call"; Documentation Governance says a frozen document changes only through the Change
  Request workflow; the frozen "# Uploads" pattern shows the same route for out-of-spec capabilities.

**Status: answered, and the CR is approved.** The user's 2026-10-03 ruling (relayed by CTO 3) was that this is to be treated as needing a CR; **on 2026-10-05 CR-SCOPE-004 was approved** (relayed by CTO 3; Question A: yes; Question B: confirmed hard delete, no undo). *Original 2026-10-03 text:* the build stays blocked until the CR is raised and answered.

**What is left to decide here:** only *what the CR should ask* (CR-SCOPE-004 asks two things: Question A,
whether the frozen specs should gain a delete action, and Question B, confirm versus undo).

**CTO-adjacent recommendation.** None needed; the question is closed. *Original 2026-10-03 note, now moot:* if the CR were rejected or deferred, the Removal Plan's earlier "port before deletion of `frontend/`" ruling for #13 could not be carried out as written, and the user would need to re-rule it.

---

## Q2 — Where does the control live?

**Options.**
1. **On each Library list row** (SCR-09), as a visible secondary control.
2. **On each row, inside a per-row menu** (the foundation `DropdownMenu` has a destructive item variant).
3. **On Report View** (SCR-10) only.
4. **Both** a row control and one on Report View.

**Facts.**
- The frozen `ListItem` is "title, subtitle/date, primary action" and "Full item focusable"; SCR-09 says
  "Enter opens focused item". The row is today one `<button>`, and a nested button is invalid HTML
  (brief §3.4).
- Legacy put a trash icon on each history item that appears only on hover (the button at `AppLayout.jsx:191–198`,
  the classes `opacity-0 group-hover:opacity-100` on line 195; its handler and confirm are at lines 147–157). The frozen SCR-09 says "Keyboard behaviour: Lists and
  filters keyboard operable".
- SCR-10's frozen actions are Read / inspect sources / Export / return to the company; its wireframe's
  only primary action is "Export" (`07_Wireframes.md`).
- The Button rule is "Destructive only for irreversible actions" (`09_Component_Inventory.md`).

**Trade-offs.**
- Any option on the list needs the row restructured (see the facts above). A menu keeps the whole-row
  primary action intact and adds one small control; a visible secondary button adds a second
  always-visible destructive target to every row.
- A hover-only reveal like the legacy one would conflict with the frozen keyboard behaviour unless the
  control is also reachable by keyboard focus.
- A destructive action on the reading surface (Report View) would sit beside the export action and would
  need its own post-delete destination (the Library), which is an extra flow to specify.

**CTO-adjacent recommendation.** Option 2 (a per-row menu on the Library list only). It keeps the frozen
whole-row primary action, mirrors where legacy users found the control, avoids putting a destructive
action on a reading surface, and needs no new post-delete navigation. This is a design judgment for the
user, and it depends on the CR being approved.

---

## Q3 — Hard delete, or reversible delete with undo? (CR Question B)

**Options.**
- **(a) Confirmed hard delete** (backend as it is) behind the frozen Dialogs pattern.
- **(b) Soft delete with an undo prompt** (backend change).
- **(c) Soft delete with a recoverable "deleted" area** (backend change, plus a new surface the frozen IA
  does not define).

**Facts.**
- The backend is an irreversible hard delete of the `reports` and `jobs` documents
  (`server.py:1477–1493`); four backend tests cover it.
- Constitution line 258 allows "Explicit, confirmed user-initiated discard" as the exception to
  never losing work, and line 259's checklist asks "Is any destructive action explicit and confirmed?".
  Line 590 says "Undo: where feasible, prefer reversible actions and offer undo over hard confirmation
  dialogs." Line 440: "mistakes are easy to recover from; destructive actions are guarded." The frozen
  Dialogs pattern describes a confirm with a clear primary and a safe Cancel.
- Undo does not exist in the backend today: it would need a soft-delete flag, a restore route, a
  retention and purge rule, and changes so list, compare and `context_report_id` lookups skip
  soft-deleted reports.

**Trade-offs.**
- The phrase "where feasible" in line 590 is where the question turns: (a) is feasible now; (b) needs
  the backend work above; (c) adds scope beyond the frozen Research Library surfaces.
- A soft delete also changes what "delete" means to the user: the data is retained. Whether that is
  acceptable (for example for privacy expectations) is a product and legal question I have not assessed.

**CTO-adjacent recommendation.** (a) for the launch scope, with undo noted as a post-launch improvement:
it is the only option that needs no backend change, and the Constitution's own wording ("where
feasible") can be read as not requiring backend work to be built first. This is a product judgment for
the user and is exactly what CR Question B asks; I would not treat my reading as settled.

---

## Q4 — Per-item or bulk?

**Options.** Per-item only; or add multi-select with a bulk action.

**Facts and trade-offs.**
- Legacy was per-item only (`AppLayout.jsx:147–157`). The backend route deletes one report per call
  (`DELETE /reports/{id}`); a bulk action would be many calls or a new route.
- A bulk action needs a selection mode and a larger-blast-radius confirmation, neither of which is in
  the frozen `LibraryList` (`items, filters`).

**CTO-adjacent recommendation.** Per-item only, for parity and the smallest change. Revisit if users ask.

---

## Q5 — How do the other features' caches learn about a deletion?

**Facts.**
- Four features cache report lists under keys with no shared prefix:
  `["research-library","reports",ticker]`, `["company-research","reports",ticker]`,
  `["comparison","reports",ticker]`, `["workspace-home","recent-reports",limit]`, plus per-report keys.
- Rules: `03.5_Caching_Strategy.md` AD-3 ("invalidate or update the specific server-state entries
  they affect ... using the semantic query-key hierarchy ... not broad cache-clearing");
  `02.2_Feature_Organization.md` AD-2 (a feature "communicates only through its public interface")
  and AD-3 ("Shared modules hold cross-cutting, feature-agnostic concerns").
- The repo already crosses features through a public surface: `company-research` and `learning` import
  from `@/features/account-setup`.

**Options and trade-offs.**
1. **A shared report-key factory under `lib/`** that all four features adopt, so one invalidation by the
   shared prefix refreshes them all. Fits AD-3 and `03.5` AD-3's "semantic hierarchy". Cost: it retrofits
   the key construction of four features.
2. **Predicate invalidation** on the shared query client, matching keys by position or name. No retrofit,
   but it relies on a naming convention nobody enforces, so a new list key could be silently missed.
3. **A feature's `index.ts` exporting an invalidation helper**, such as `research-library` exporting one
   that others import. Fits AD-2 and has precedent, but `research-library` would then have to know the
   other features' keys (inverting the dependency), or each feature would export its own and something
   would have to call all four.
4. **Rely on staleness.** The Library list uses `staleTime: 30_000`; a deleted report could remain
   visible in another feature's list for at least that long. This does not meet the acceptance criterion
   ("without a manual reload").

**CTO-adjacent recommendation.** Option 1. It is the structurally honest fix and avoids a hidden naming
dependency. It is also the one most likely to need an architecture ruling, since it touches four
features, so the user may prefer option 2 as a documented stopgap. A judgment for the user.

---

## Q6 — Samples

**Facts.** The backend answers `404` for public samples (`user_id=None`; `test_cannot_delete_sample`), the
list already carries `is_sample`, and the Library shows samples to every account with a "Sample" badge
(`LibraryList.tsx`). Legacy did not hide the control on samples.

**Options.** Hide the control on sample rows; show it disabled with an explanation; show it and let the
`404` surface.

**Trade-offs.** Hiding matches the contract and avoids a control that can never work; a disabled control
is discoverable but needs an explanatory sentence (a copy decision); surfacing the `404` offers the user
an action that is guaranteed to fail.

**CTO-adjacent recommendation.** Hide it.

---

## Q7 — How should a `404` from the delete be treated?

**Facts.** The route returns the same `404 "report not found"` for a missing report, a report owned by
someone else, and a sample (`server.py:1485–1487`), so the UI cannot tell them apart. `apiFetch` surfaces
it as `AppError` with `kind: "unknown"` and `status: 404`. With Q6 hiding the control on samples, the
remaining causes are "already deleted (for example in another tab)", "not yours", and "not saved yet".

**Options.** (a) Treat it as a failure ("couldn't delete"). (b) Treat it as "already gone": a neutral
message and a list refresh. (c) Show different messages by guessing the cause (not possible from the
response).

**Trade-offs.** (a) leaves the user stuck on something that cannot succeed and keeps showing a row that
is gone; (b) makes the UI converge on the server's state, at the cost of a message that is slightly less
specific.

**CTO-adjacent recommendation.** (b): refresh the list either way, with a neutral message. The wording is
a copy decision for the user.

---

## Q8 — Confirmation strength, and the dialog's wording

**Facts.**
- The frozen Dialogs pattern: "a clear primary and cancel; dismissible ... Cancel is always safe".
- The existing precedent, account deletion, asks the user to type their email, which is proportionate to
  deleting the account and all research (`SettingsPanel.tsx`, "Danger zone").
- Legacy used a plain `window.confirm("Delete this report for <name>?")` (`AppLayout.jsx:149`).
- Copy rules: Constitution §15 (plain, neutral, no hype, no coined terms).

**Options.** A plain confirm dialog naming the report; or typed confirmation as for account deletion.

**Trade-offs.** Typed confirmation guards against slips but adds friction that the "Forgiving" principle
(line 440) and the single-report scale do not obviously call for; a plain confirm is faster and matches
the frozen pattern and legacy.

**CTO-adjacent recommendation.** A plain confirm dialog that names the report (ticker, query, date).
**I am not proposing the wording:** product copy has to come from you, within §15, and I will not
invent it. Whether the dialog should also mention that comparisons or Learning requests referencing the
report will lose that context is part of the same copy decision (see Q9).

---

## Q9 — Dependent artifacts

**Facts.**
- The route does not cascade (`server.py:1477–1493`).
- **Learning / follow-up requests** that name a deleted report get no injected context, and do not error
  (owner-or-sample scoped lookups, `94b01ba`).
- **Comparison:** the backend's `POST /reports/compare` silently drops ids it cannot find ("a typo'd/
  deleted id looks identical here") and answers `404 "fewer than 2 reports found"` if fewer than two
  remain (`server.py:1819–1842`). So a comparison URL (`?ids=`) that includes a deleted report either
  loads with one fewer member or shows an error state. **How `web/`'s Comparison screen presents that
  has not been checked.** (This sharpens the brief, which listed Comparison's handling as unverified;
  the backend half is now verified.)
- **Saved Exports and Research Sessions** do not exist yet in `web/` and so cannot be affected today.
- **Account deletion** already cascades to all of a user's reports (`server.py:466–486`).

**Options.** Do nothing beyond the dialog; add a sentence to the dialog; make the backend cascade or
protect dependants (not implied by anything above).

**CTO-adjacent recommendation.** Before the build, check how the Comparison screen handles a missing id
(a short check against the running stack). If it degrades gracefully, no extra dialog text is needed.
If it does not, that becomes a small defect to fix alongside, not a reason to change the delete itself.

---

## Q10 — Reports that are still running

**This narrows the brief's Q10.** The brief asks whether the UI should offer Cancel, or nothing, for a
running report. For the Library the situation does not arise (see the facts below), so what remains of
the question is only whether any such offer is wanted elsewhere.

**Facts.** `GET /reports` reads the `reports` collection, which the pipeline fills on its completion path
(`server.py:1149`), so the Library list does not contain running reports. A delete of a running job's id
would find no `reports` document and answer `404`. I did not trace whether another path can create a
`reports` document earlier.

**Options.** Do nothing (a running job is not in the list); or offer Cancel in the surface that shows a
running job (Company Research already has it).

**CTO-adjacent recommendation.** Do nothing for the Library: the situation cannot arise from this list.
Cancelling a running report is a separate, existing action.

---

## Q11 — Optimistic or confirmed update?

**Facts.** `03.2_Server_State_Strategy.md` (line 94): optimism is "conservative — never for
trust-critical/AI/financial data". The delete is irreversible (Q3).

**Options.** (a) Wait for the `200` (the dialog shows the pending state, then the row disappears).
(b) Remove the row immediately and restore it if the call fails.

**Trade-offs.** (a) is slower by one round trip and never shows a false result; (b) feels instant but
a failed delete after the row had already disappeared would show the user a false result, and the row
would reappear after the user believed it was gone, with an irreversible action behind it.

**CTO-adjacent recommendation.** (a), for an irreversible action. The loading state it needs is already
part of the brief's four states.

---

## Which answers could be settled before the CR is decided

**Independent of the CR (can be settled now):** Q4, Q5, Q6, Q7, Q9, Q10, Q11, and the structure (not the
content) of Q8.
**Depend on the CR:** Q2, Q3, and the content of Q8. If the CR is **rejected or deferred**, none of the
questions needs an answer for now, and the Removal Plan's #13 would have to be re-ruled.

*Prepared as a non-binding analysis. The recommendations above are the author's and are separate from the
facts and cites; none is a ruling, and no frozen document has been edited.*
