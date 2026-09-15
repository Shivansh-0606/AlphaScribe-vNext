# Migrated-Parity Hardening Pass — Implementation Brief

**Date:** 2026-09-15. **Author:** Docs. **For:** Frontend Engineer (via Docs
Reviewer). **Governing precedent:** [`docs/governance/Feature_Parity_Tracker.md`](../governance/Feature_Parity_Tracker.md)
§"Migrated-parity hardening pass — Auth (2026-08-15)" and Next-steps item 16
— the only slice of this initiative that's actually completed. This brief
covers item 16's next slices: Workspace Home, Company Research (Overview/
Financials/Filings/Changes/AI Insights/Export), Research Library, and
Comparison.

**Slice 1 (Workspace Home) is done, live-verified, and included below in
full — not just scoped.** Slices 2–4 are triaged and sequenced but
intentionally left for their own future briefs, per the instruction not to
scope all four into one document.

## 1. Goal

Continue the Auth hardening pass's own unfinished list: re-verify each
remaining "In Progress" surface end-to-end against the real running
backend, sort what's genuinely broken from what's just never been
independently live-checked, and promote what passes to **Migrated** in the
tracker — the tracker's own bar, not a new one.

## 2. Correction to the premise, found before any verification could start

**The tracker is significantly stale for Company Research, and CTO's own
"five sections" framing is already one behind.** The tracker's last update
was 2026-08-15. Since then, four backend+frontend milestones landed
directly inside Company Research, none reflected in the tracker's Company
Research row or its "deliberately-scoped gap" notes:

| Tracker claim (2026-08-15, still standing) | Current reality (verified this pass) |
|---|---|
| "`StatementTable`... has no backend data source" — Financials Statements is an honest placeholder | **False as of `b4e90a0` (2026-08-26, M12).** `GET /companies/{ticker}/financials` is real; `FinancialsSection.tsx` renders real multi-period `StatementTable` output via `useFinancialStatements` — confirmed by reading the component, not just the commit log. |
| "`FilingViewer`'s content-reading pane... reserves... an honest 'not available yet' placeholder" | **False as of M13/M14/M16** (`244ca5c`, `7c2e3b8`, `b6d4e68`). Filings now has real content reading, a Content/Analysis/Q&A three-way switch, and per-filing grounded Q&A. |
| "Company Research's five `SectionNav` destinations" (tracker text, and CTO's scope message today) | **Six**, confirmed live this pass: Overview, Financials, Filings, **Changes** (M15, added between Filings and AI Insights), AI Insights, Export — `SectionNav.tsx`'s own doc comment names this explicitly. |

**Why this matters for sequencing, not just accuracy:** Company Research is
not the same size or risk profile the tracker's own text implies. It has
absorbed four milestones' worth of new backend-integrated surface since the
tracker was last touched. Treating it as "one more In Progress row, same as
the others" would understate the verification effort it actually needs.
This is the basis for putting it last, below (§4).

**Recommendation, not yet acted on:** before Company Research's own
hardening slice starts, someone should do a short, dedicated
tracker-accuracy pass (re-read the current §3 row against the code, correct
the stale placeholder language, add the M12/M13/M14/M15/M16 rows) — a
documentation correction, not a verification pass, and cheap relative to
getting Company Research's eventual hardening slice wrong by starting from
a wrong mental model of what already exists.

## 3. Scope

**In (this brief):**
- Full live-verification of **Workspace Home** (§5) — done.
- A triage + sequencing recommendation for all four remaining tracks (§4).
- Scope notes for slices 2–4, thin enough to hand off without re-deriving
  them, thick enough that whoever picks up slice 2 doesn't start blind.

**Out:**
- Full live-verification of Comparison, Research Library, or Company
  Research — each gets its own brief when its turn comes (§4).
- Any code change. This is a verification-and-documentation pass; the one
  thing resembling a "finding" below (§5.4) is a testing-methodology note,
  not a defect, and nothing here requires an Engineer fix.
- Rewriting the Feature Parity Tracker itself — recommended above (§2) but
  not performed here; that's a distinct, small follow-up task.
- Learning (§6 of the tracker) — explicitly N/A-for-parity, not part of
  this initiative.

## 4. Triage and sequencing across all four tracks

| Track | Code drift since 2026-08-15 | Apparent risk | Recommended order |
|---|---|---|---|
| **Workspace Home** | One test-stability fix only (`e5b5fdb`, debounce race in tests — no product code changed) | Low — smallest surface, two real backend endpoints already exercised repeatedly elsewhere in the tracker's own history | **1st — done this pass (§5). Zero defects. Recommend promoting to Migrated.** |
| **Comparison** | **Zero commits** since 2026-08-15 | Low — unchanged code, was live-verified once already (Phase 7), backend endpoint (`POST /reports/compare`) is a pure lookup, no LLM re-run | **2nd** — smallest of the three remaining, most likely to replicate Auth's "zero defects" outcome quickly |
| **Research Library** | **Zero commits** since 2026-08-15 | Low-moderate — unchanged code, was live-verified once already (Phases 5–6), but has more states to re-check (Loading/Empty/No Results/Error across two screens) than Comparison | **3rd** |
| **Company Research** | **Four milestones' worth** of new backend-integrated surface (M12 financials, M13 filing content, M14 filing analysis, M15 change brief, M16 filing Q&A) | High — by far the largest surface, the most drifted from the tracker's own description of it, and the only one where "what currently exists" itself needed correcting before triage could even start (§2) | **4th, as its own multi-part initiative** — recommend the tracker-accuracy correction (§2) happens first, then break its six sections into their own verification passes rather than one sitting |

This ordering optimizes for the same thing the Auth slice did: bank a fast,
clean win first, build confidence in the live-verification process itself,
and save the largest, highest-uncertainty surface for when it can get a
dedicated pass rather than being squeezed into a shared one.

## 5. Slice 1 — Workspace Home: live-verification results

**Method, mirroring the Auth pass exactly:** full local stack
(`.venv`/`.mongo`/Next.js dev server via `python scripts/run.py`), one
disposable test account (`docs-hardening-pass@example.com`), deleted via its
own delete-account step at the end — no manual cleanup needed, no residue
left in the database.

**Result: zero defects found in Workspace Home itself.**

### 5.1 What was exercised and confirmed real

- **Landing → Signup → Onboarding (Managed AI) → Workspace Home**: every
  step hit the real backend (`POST /api/auth/register`, real redirect to
  `/setup`, Managed AI → Continue → real redirect to `/workspace`) — no
  surprises, matches the tracker's existing Auth-row claims exactly.
- **Company search** (`GET /api/companies/search`, debounced): typed
  `"Micro"` → real 200, eight real SEC-registered results incl. `MSFT`
  correctly flagged `has_filings: true` and ranked first; typed `"Tesla"` →
  selecting the suggestion reliably navigates to `/research?ticker=TSLA`.
  Confirmed twice, independently.
- **Recent Research empty state**: a fresh account with zero owned reports
  correctly shows "No research yet — search a company above to get
  started." — matches the frozen SCR-04 empty-state spec.
- **Auth session/guard pattern**, re-exercised as a side effect of this
  pass: `AuthGate` correctly held through the full
  signup → search → navigate → settings → delete-account → login-fails
  cycle.

### 5.2 Not exercised — one honest gap, low risk

**Recent Research's *Loaded* state** (a populated list, not the empty one)
was not directly observed this pass. Reaching it requires a report the test
account actually owns, which means running a real report-generation job to
completion — that pipeline belongs to Company Research, not Workspace Home,
and forcing one just to see a list re-render wasn't a good use of this
slice's scope. Low risk: the same `GET /reports` endpoint Workspace Home's
Recent Research calls is already exercised in its *Loaded* form elsewhere in
the tracker's own verified history (Research Library's list screen, Phase
6). Recommend closing this specific sub-case out opportunistically during
whichever future pass runs a real report end-to-end, rather than forcing it
here.

### 5.3 One real, pre-existing, non-blocking accessibility gap

The `CompanySearch` suggestion list items are plain `generic` elements
inside the results `dialog`/`listbox`, not exposed with `role="option"` —
found by reading the accessibility tree directly (`find`/`read_page`), not
inferred. Not a new regression: the tracker's own §7 accessibility row
already states `jest-axe` coverage has not been extended to
workspace-home/account-setup screens yet, only to Company Research (Phase
4D) and the shared foundation layer. This is that known gap made concrete,
not a surprise. Recommend folding it into whatever future pass finally
extends `jest-axe` past Company Research — not urgent enough to block
promoting this row to Migrated on its own.

### 5.4 Testing-methodology note, not a product defect

One delete-account attempt appeared to hang — the confirm button's `DELETE
/api/auth/me` request never reached the backend (confirmed via the
backend's own access log, not just the browser's network panel). Before
treating this as a regression against Auth's already-`Migrated` row, it was
run down: a raw `fetch()` DELETE from the browser console resolved in 66ms
with a normal `422` (missing body — expected, since the endpoint requires
the confirmation email), and `SettingsPanel.tsx`/`fetch-client.ts`'s actual
request-construction code reads correctly on inspection. A second, patient
attempt (waiting for the Settings route's dev-mode compile — logged at 10.8s
for that route alone — to fully settle before clicking) succeeded cleanly:
`200 OK`, followed by a real subsequent login attempt correctly failing with
`401`. **Conclusion: not a reproducible defect** — one dev-mode
compile/hydration race, not a broken delete flow. Recorded here only as an
operational note for whoever runs slices 2–4: this session observed
individual routes taking as long as **37 seconds** to Fast-Refresh-recompile
on first visit in this sandboxed dev environment. Wait for a route's own
compile-log line before treating a slow or unresponsive first interaction
as a bug.

### 5.5 Recommendation

**Promote Workspace Home to Migrated** in the tracker, with §5.2 and §5.3
carried over as its row's own notes — exactly the pattern the Auth row
already uses for its own accepted, non-blocking gaps (rate-limiting,
"Remember me" duration, multi-device isolation).

## 6. Slices 2–4 — scope notes for whoever picks them up next

Not executed this pass; recorded so the next brief doesn't re-derive them.

- **Comparison** (`web/features/comparison`): re-verify `ComparisonPicker`
  (chip selection, capped at 4, `GET /reports`), `ComparisonTable`
  (`unavailable` gap-flagging for missing metrics/zero-data members), and
  `?ids=` deep-link/reload persistence — the same three things Phase 7's
  one-time live pass already checked once. A hardening pass re-confirms
  independently rather than carrying that result forward, per the tracker's
  own **Migrated** bar.
- **Research Library** (`web/features/research-library`): re-verify
  `ReportDocument` (`/reports/[id]`, the Trust-First unusable-report gate,
  client-side markdown export) and `LibraryList` (`/library`, all four
  states — Loading/Empty/No Results/Error, including the tracker's own
  already-flagged product note that a genuinely empty account may be
  unreachable live while the MSFT sample exists).
- **Company Research**: do not start this as a normal-sized slice. First,
  correct the tracker itself (§2) so the six current sections' actual state
  is accurately described; then scope it as multiple sub-slices (at minimum:
  Overview+streaming, Financials, Filings' three-way switch, Changes,
  AI Insights, Export) rather than one end-to-end pass — each has absorbed
  enough independent milestone work to warrant its own live check.

## 7. Acceptance Criteria

- [x] Workspace Home live-verified end-to-end against the real backend;
      zero defects found; test account created and cleanly deleted.
- [x] Company Research's actual current shape (six sections, M12–M16
      capabilities) confirmed directly against the code and the tracker's
      staleness relative to it documented with specifics, not just asserted.
- [x] All four remaining tracks triaged (drift since 2026-08-15, apparent
      risk) and sequenced with a stated rationale.
- [ ] Tracker itself updated to promote Workspace Home to Migrated and
      record its two accepted notes (§5.2, §5.3) — a follow-up action, not
      performed by this brief (Docs proposes; the tracker edit is the
      Engineer/Reviewer's to make alongside the code review, same division
      as every other milestone in this repo).
- [ ] Slices 2–4 each get their own brief when their turn comes, per the
      sequencing in §4 — not scoped further here by design.

## 8. Open Questions / Risks

- **Who updates the tracker file itself?** This brief recommends promoting
  Workspace Home to Migrated and documents exactly what to write, but per
  this repo's own convention (Docs writes briefs, doesn't edit governance
  trackers directly), the actual tracker edit should happen alongside
  Frontend Engineer/Reviewer's sign-off on this slice, not before it.
- **The tracker-accuracy correction for Company Research (§2)** is a real
  piece of work someone needs to pick up before that track's hardening
  slice starts. It's small (a documentation correction, not new
  verification) but it isn't nothing, and it isn't automatically part of
  the Comparison/Research Library slices ahead of it in the queue — flagging
  so it doesn't get silently dropped between slices 3 and 4.
- **Dev-mode compile latency** (§5.4) is specific to this sandboxed
  environment's Next.js dev server, not necessarily every environment this
  pass might run in later. Worth re-confirming whether it recurs before
  assuming every future slice needs the same generous waits.
- **Live-testing an LLM-backed flow** (Company Research's Overview/Changes/
  AI Insights/Filing Q&A) will need a reachable LLM provider in whatever
  environment runs that slice — this pass deliberately avoided forcing a
  real generation job for the one small thing it would have proven (§5.2)
  precisely because that dependency doesn't yet exist confirmed-reachable
  here. Whoever scopes Company Research's slice should confirm LLM
  reachability first, not discover it mid-pass.
