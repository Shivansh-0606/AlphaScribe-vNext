# Change Request — CR-SCOPE-004: Report Deletion in Research Library

| Field | Value |
|-------|-------|
| **CR ID** | CR-SCOPE-004 |
| **Title** | Report deletion (a delete action with confirmation on Research Reports) |
| **Status** | 📝 **DRAFT — not submitted, not approved.** Prepared for the user to approve and submit. Nothing in this file is a decision. |
| **Raised By** | Not yet raised. Drafted by Docs (Docs generator 3) at the request of CTO 3, following the user's ruling of 2026-10-03 (relayed by CTO 3) that report deletion is to be treated as needing a governance Change Request. |
| **Raised On** | — (drafted 2026-10-03; not submitted) |
| **Type** | Scope addition (adds a user action to frozen screens and components) |
| **Affects** | Screen Inventory (SCR-09, SCR-10) · UX Specifications (SCR-09, SCR-10) · Wireframes (SCR-09, SCR-10) · Component Inventory (`ListItem`, `LibraryList`, `ReportDocument`) · possibly Interaction Patterns · Experience Design Family 09 and Component Mapping. Full list in §3. |
| **Decision** | ☐ Approve ☐ Reject ☐ Defer — **not decided.** To be completed by the CTO / user. |

> Raised because the user ruled (2026-10-02, relayed by CTO 3) that report deletion is to be ported
> before `frontend/` is deleted ([Legacy Frontend Removal Plan](../Legacy_Frontend_Removal_Plan.md)
> §3 #13), and the frozen screen specifications **do not include a delete action**. Per
> [Documentation Governance](../Documentation_Governance.md), a frozen or approved document "changes only through
> this workflow" (the Change Request Process), and `CLAUDE.md` calls a conflict with a frozen doc "a
> stop-and-raise-a-CR situation, not a silent judgment call". Until this CR is approved, **the frozen
> baseline remains authoritative and report deletion is not built.** The implementation brief
> ([`docs/briefs/report-deletion_research-library.md`](../../briefs/report-deletion_research-library.md))
> is committed but marked "DRAFT — NOT READY TO BUILD" for this reason.
>
> **This draft deliberately makes no recommendation** (§12). It sets out the question, the evidence,
> the options and their consequences; the answer is the CTO's and the user's.

---

## 1. Feature Description (the proposed change, stated as questions)

**Proposed change.** Add a **delete action, with an explicit confirmation**, for a user's own
**Research Reports**, so that a signed-in user can permanently remove a saved report they no longer
want. Today the Research Library lets the user browse, filter and open reports, and nothing else.

The CR asks the decision-maker to answer **two questions**:

- **Question A — scope.** Should the frozen screen specifications **gain** a report-delete action at
  all? If yes: on **SCR-09 Research Library** (per list item), on **SCR-10 Report View**, or both; and
  does `ListItem` / `LibraryList` / `ReportDocument` gain a destructive action?
- **Question B — reversibility.** If yes, should the action be an **explicit, confirmed, irreversible
  delete** (the Dialogs pattern; Constitution lines 258–259), or a **reversible delete with undo**
  (Constitution line 590: "where feasible, prefer reversible actions and offer undo over hard
  confirmation dialogs")? The current backend is an **irreversible hard delete** (§6), so undo is a
  backend change, not only a design choice.

**Outcome options** (none is selected here):

| Option | Meaning | Main consequence |
|---|---|---|
| **Approve — confirmed delete** | Add a delete action with a confirmation dialog; backend unchanged | Frozen docs in §3 are amended; the existing brief can proceed after its other open questions are answered |
| **Approve — reversible delete (undo)** | Add a delete action with undo | As above, plus a backend change (soft delete / restore / retention) |
| **Reject** | No report deletion in the product | Reports can be removed only by deleting the whole account (§4). The Removal Plan's #13 ruling "port before deletion of `frontend/`" cannot be carried out, and the user would need to re-rule it |
| **Defer** | Revisit after launch, as the user did for upload ingest and company refresh | Report deletion is absent from the product after `frontend/` is deleted until rebuilt; the legacy code stays recoverable through the rollback tag |

## 2. Why It Was Flagged

1. **Legacy parity sweep.** The Removal Plan's diff of the legacy client against `web/` found that the
   legacy app let users delete a report (`frontend/src/components/AppLayout.jsx:147–157`: a delete
   button with a confirm on each history item; `frontend/src/lib/api.js:39`) and `web/` has no caller
   of `DELETE /reports/{id}` (the only `DELETE` in `web/features` is account deletion).
2. **The frozen baseline omits it.** Nothing in the frozen design set defines a report-delete action
   (§3). The omission may be deliberate (durable research is "a promised value (J-06)") or simply a gap;
   the baseline does not say.
3. **The backend offers it and a Backend Engineering audit recommended wiring it.**
   [`02_API_Coverage_Audit.md`](../../backend_engineering/02_API_Coverage_Audit.md) §4.4
   ("⚪ Unconsumed, but *behaviorally required*") says `research-library` "offers no delete action"
   and "Recommend wiring rather than deprecating — deletion is the one report operation with no
   alternative path." That is an **audit recommendation, not a ratified decision**.
4. **Two frozen principles pull in different directions** on how to do it (§1 Question B and §10).

## 3. Current Traceability Against Frozen Baseline

All documents below are 🧊 Frozen unless marked otherwise. **None of them mentions report deletion.**
Line numbers were read in the files on 2026-10-03.

| Baseline document | What it says | Verdict |
|-------------------|--------------|---------|
| **Screen Inventory** `05_Screen_Inventory.md` — SCR-09 | Available Actions: "Browse/filter sessions, reports, saved exports, history; open a report; **Resume Session**; open a saved export." Required States: Loading, Empty, No Results, Error | ❌ No delete action |
| **Screen Inventory** — SCR-10 | Available Actions: "Read the report; inspect sources; export; return to subject company." Required States: Loading, Error, Success (export), Timeout | ❌ No delete action |
| **UX Specifications** `06_UX_Specifications.md` — SCR-09 | Primary Tasks: "Browse/filter ...; open; **Resume Session**." Interaction Rules: "Resume Session restores prior reasoning and sources; nothing is lost on return (J-06)." | ❌ No delete task |
| **Wireframes** `07_Wireframes.md` — SCR-09 / SCR-10 | SCR-09 Primary: "Resume Session; Open report/export"; Secondary: "Filter; open history item". SCR-10 Primary: "Export"; Secondary: "Inspect source; return to company" | ❌ No delete control drawn |
| **Component Inventory** `09_Component_Inventory.md` — `ListItem` | "Properties: title, subtitle/date, primary action"; dependencies `Label, Button, Badge` | ❌ No secondary or destructive item action |
| **Component Inventory** — `LibraryList` | `items, filters`; states Default, Empty, No Results, Loading, Error | ❌ |
| **Component Inventory** — `ReportDocument` | "Properties: conclusion, reasoning, content, sources, export action" | ❌ |
| **Component Inventory** — `Button` | "Variants: Primary, Secondary, Quiet/Text, **Destructive**"; "Destructive only for irreversible actions" | ✅ A destructive variant exists and its usage rule matches an irreversible delete |
| **Interaction Patterns** `10_Interaction_Patterns.md` — "# Dialogs" | "Request a focused decision inline (e.g. confirm a discard) ... a clear primary and cancel; dismissible ... Cancel is always safe and non-destructive." | ✅ A confirmation pattern exists |
| **Interaction Patterns** — "# Downloads" | Export "is retained as a Saved Export" | ⚠ Silent on what deleting a report does to its exports (Saved Exports are not yet built) |
| **Design Constitution** `00_Design_Constitution.md` lines 160–161, 252–259 | "Preserve user progress. No action — including navigation and errors — may lose the user's work (Journeys: J-06)"; "No interaction discards in-progress or saved research" (253); "Exceptions: Explicit, confirmed user-initiated discard" (258); "Is any destructive action explicit and confirmed?" (259) | ⚠ Supports a confirmed, user-initiated discard as an exception |
| **Design Constitution** lines 440, 586–590 | "Forgiving: mistakes are easy to recover from; destructive actions are guarded" (440); "Undo: where feasible, prefer reversible actions and offer undo over hard confirmation dialogs" (590) | ⚠ **Tension with a confirm-only, irreversible delete** (§1 Question B) |
| **User Journeys** `02_User_Journeys.md` — J-06 | "Capturing and Returning to Research"; a search of the journeys found no report-deletion step | ❌ |
| **Information Architecture / Navigation** `03_…`, `04_…` | Research Library holds Research Sessions · Reports · Saved Exports · History; Navigation line 77: "Moving does not discard the user's research state." | ❌ No deletion |
| **Experience Design** `Components/00_Component_System.md` line 67; `Components/09_Research_Components.md` lines 387–388; `engineering_handoff/12_Component_Mapping.md` line 133 | Line 67: "No component action discards in-progress or saved work without explicit, confirmed intent (Law 6; §7.4)." | ⚠ Same confirmed-intent principle |
| **Frontend Architecture** `01_Frontend_Architecture_Constitution.md` lines 372–373 (Law 6); `03.12_Offline_Synchronization_Philosophy.md` lines 53–54 | "must not discard in-progress research across navigation, error, or timeout"; no sync decision "may discard the user's completed or in-progress research" | ⚠ Written about unintended loss; silent on a deliberate delete |
| **Backend** (not frozen design) `server.py:1477–1493` | Owner-scoped hard delete; samples undeletable (404) | See §6 |

**Frozen documents that would need a MAJOR/MINOR amendment if Question A is answered "yes"** (to be
enumerated precisely at the Impact Analysis step; this draft **edits none of them**):
`05_Screen_Inventory.md` (SCR-09, and SCR-10 if chosen), `06_UX_Specifications.md` (same screens),
`07_Wireframes.md` (same screens), `09_Component_Inventory.md` (`ListItem`, `LibraryList`, and
`ReportDocument` if chosen), and, if the answer to Question B is "undo",
`10_Interaction_Patterns.md` and `13_States.md`. Experience Design Family 09 and
`12_Component_Mapping.md` follow from the frozen set. The Design Constitution is **not** expected to
change; Question B asks how to read its lines 258 and 590 together.

## 4. User Value

- **Facts.** The legacy app offered it; the backend offers it and has tests for it; the only way to
  remove a saved report in the current `web/` app is to **delete the entire account**, which cascades
  to all of the user's reports (`server.py:466–486`).
- **Not assessed here.** How many users want to delete single reports, and why (tidying, privacy,
  mistakes), is not evidenced in the repo. No product metric is recorded.

## 5. Business Value

Not assessed. The repo records no metric or commitment tied to report deletion. Any argument from
retention or trust would be an inference and is left to the decision-maker.

## 6. Engineering Complexity

- **Confirmed (irreversible) delete:** the backend route already exists and is tested
  (`DELETE /api/reports/{id}`: owner-scoped hard delete of the `reports` and `jobs` documents; `404` for
  missing, not-yours and sample reports; no cascade to other collections). No backend change. Frontend
  work is scoped in the implementation brief: an integration function, a mutation hook, a confirmation
  `Dialog`, restructuring the list row, and cache invalidation across **four features that each cache
  report lists under separate keys**.
- **Reversible delete (undo):** needs backend work that does not exist today (a soft-delete flag, a
  restore route, a retention/purge rule, and changes so that list, compare and context lookups skip
  soft-deleted reports). Its size is **not estimated here**.
- **Either way:** cross-feature cache invalidation is itself an architecture question (brief §5 Q5).

## 7. UX Impact

- Adds a destructive control to a surface whose frozen actions are all non-destructive (open, resume,
  filter, export).
- The current list row is a single button (the whole row is the focus target, as `ListItem` specifies:
  "Full item focusable"), so a delete control means **restructuring the row** (a nested button is not
  valid). That changes the frozen `ListItem` shape.
- Public samples cannot be deleted by anyone (backend `404`), so the control would need to be absent or
  explained on those rows.
- If SCR-10 is chosen as a home, a destructive action would sit on a reading surface whose frozen
  primary action is Export.

## 8. AI Impact

None directly. Indirect: a Learning ("Explain This") or follow-up request that names a deleted report
gets no injected context (the lookups are owner-or-sample scoped, commit `94b01ba`); it does not error.

## 9. Dependencies

- The implementation brief and its decision sheet:
  [`docs/briefs/report-deletion_research-library.md`](../../briefs/report-deletion_research-library.md),
  [`docs/briefs/report-deletion_decision-sheet.md`](../../briefs/report-deletion_decision-sheet.md) (DRAFT).
- Saved Exports, Research Sessions and History (frozen IA, not yet built) would interact with deletion
  once they exist.
- The Removal Plan §3 #13 and §4.1 item 5, which are blocked on this CR.

## 10. Risks

- **Irreversible loss versus the durability promise.** Research durability is "a promised value (J-06)";
  an explicit, confirmed discard is the Constitution's stated exception (258), but a hard delete cannot
  be recovered, and line 590 prefers undo where feasible.
- **Scope drift** toward bulk delete, trash or recovery, or retention features, none of which the
  frozen IA defines. This CR is bounded to a single-report delete unless the decision-maker widens it.
- **Stale views.** If invalidation misses one of the four features' caches, a deleted report would
  remain visible there until it refetches.
- **Dependent artifacts.** Comparisons that reference the report, and Learning requests that used it as
  context, are not cascaded; how Comparison treats a missing id was **not verified**.
- **Reports still running.** The Library lists completed reports only (`GET /reports` reads the
  `reports` collection), so a running job is not offered; whether a delete of a running job's id is
  possible by other means was not traced.

## 11. Recommended Release

**Not specified by this draft.** The options are in §1: approve for the launch scope, approve with
undo (later or sooner), reject, or defer past launch.

## 12. CTO Recommendation

**None given in this draft.** The Documentation Governance workflow ends in approval by the required
approver. This file does **not** recommend an outcome for either Question A or Question B, because the
choice between "confirmed, irreversible delete", "reversible delete" and "no delete" turns on a product
judgment about durability versus user control that is the CTO's and the user's to make. A
non-binding analysis of each open implementation question, labelled as such, is in
[`docs/briefs/report-deletion_decision-sheet.md`](../../briefs/report-deletion_decision-sheet.md).

**For the decision-maker:**

| Step (Documentation Governance, Change Request Process) | Status |
|---|---|
| 1. Proposed Change | Drafted (§1) |
| 2. Impact Analysis | Partly drafted (§3, §6–§10); to be completed |
| 3. Affected Documents | Provisional list in §3 |
| 4. Review | Not started |
| 5. Approval | **Not decided** (☐ Approve ☐ Reject ☐ Defer, above) |
| 6–9. Implementation, verification, revision history, re-freeze | Not started; only after approval |

*Draft Change Request, prepared for the [Documentation Governance](../Documentation_Governance.md)
process. It has not been entered in the [Change Request Register](00_Change_Request_Register.md); doing
so, and submitting it, is the user's step. The frozen baseline remains authoritative until this CR is
explicitly approved.*
