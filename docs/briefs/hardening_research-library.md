# Migrated-Parity Hardening Pass — Slice 3: Research Library — Implementation Brief

**Date:** 2026-09-18. **Author:** Docs. **For:** Frontend Engineer (via Docs
Reviewer). **Governing precedent:** [`docs/briefs/hardening_migrated-parity-pass.md`](hardening_migrated-parity-pass.md)
§4/§6 (sequencing + scope notes) and [`docs/governance/Feature_Parity_Tracker.md`](../governance/Feature_Parity_Tracker.md)
§5 (Research Library's existing row, Phases 5–6). Slice 3 of the initiative
— same live-verify-and-promote treatment Slices 1 (Workspace Home) and 2
(Comparison) got.

## 1. Goal

Re-verify Research Library (`web/features/research-library` — `LibraryList`
at `/library`, `ReportDocument` at `/reports/[id]`) end-to-end against the
real running backend, independently of Phases 5–6's original verification,
per the tracker's own **Migrated** bar.

## 2. Result: zero defects found. Recommend promoting Research Library to Migrated.

One honest gap carried over (§4) — a known, already-accepted limitation,
not a new one — plus one state this pass could not safely force live (§5),
same disciplined-honesty pattern as the prior two slices.

## 3. What was exercised and confirmed real

**Method:** the shared dev stack (fresh restart this session), one
disposable test account (`docs-hardening-library@example.com`), deleted at
the end via its own delete-account step — confirmed by the backend's own
access log (`DELETE /api/auth/me → 200 OK`), not just the client redirect.
One real report was generated first (MSFT, via Company Research's Overview,
against the real configured LLM — retrieval, extraction, and synthesis all
completed for real, including one transient NVIDIA `503` that retried and
succeeded) specifically so `LibraryList`/`ReportDocument` would have a
genuinely-owned, non-sample report to render, not just the seeded sample.

### 3.1 LibraryList — three of its four frozen states confirmed live

- **Loaded**: with the fresh own report plus the seeded sample both present,
  the list correctly renders both rows — the sample tagged with a `Sample`
  badge, the own report not — sorted newest-first (`created_at desc`,
  confirmed by row order matching creation order).
- **No Results**: filtering by a ticker matching nothing (`"ZZZZ"`) renders
  the exact `No reports match "ZZZZ".` copy, distinct from the empty-library
  copy.
- **Filter round-trip**: clearing the filter afterward correctly restored
  both rows — no stale state left over from the filtered query.
- **Empty** (zero-report account, no filter): **not reachable live**, same
  as this tracker row's own Phase 6 note already states — the seeded sample
  is visible to every account (`is_sample: True` matches for any caller,
  confirmed directly against `backend/server.py`'s `list_reports` query:
  `{"$or": [{"user_id": user["id"]}, {"is_sample": True}]}`), so a fresh
  account never actually sees zero rows. Re-confirmed this pass, not a new
  finding — the code path is simple and was already correctly noted as
  untestable-live in this exact tracker row.
- **Loading**: not independently screenshotted — the transition from
  pending to loaded happened correctly and quickly every time this pass hit
  it, which is itself evidence the `isLoading` guard is wired correctly, but
  the skeleton itself wasn't caught on camera. Low risk: `isLoading` is a
  single boolean gating a `SkeletonGroup` with no logic beyond that.

### 3.2 ReportDocument — real render, real error path, real export

- **A genuinely-owned, freshly-generated report** rendered correctly at
  `/reports/{id}`: correct heading (`MICROSOFT CORP`), correct qualitative
  `Limited evidence` confidence label (never a raw number), the query text,
  the full markdown brief with inline `[n]` citations, and all 8
  `SourceReference` entries — clicked through from `LibraryList`, not typed
  directly, so the full row-click → route → fetch chain was exercised, not
  just the destination page in isolation.
- **Nonexistent / inaccessible report id**: `/reports/00000000-...` renders
  the exact non-disclosure copy ("may not exist, or you may not have access
  to it") with a working Retry button — confirmed distinct from the
  Trust-First unusable-content banner (different copy, different trigger).
- **Export**: clicking it produced no console errors and correctly toggled
  the button label `Export` → `Exported` (reverting after 2s, per the
  component's own `setTimeout`) — the `Blob`/anchor download path executed
  without throwing. Whether the browser's own save-dialog / download
  actually completed isn't independently confirmable from this sandboxed
  preview session (out of the app's own control either way); the
  app-controlled half of this feature — building the correct markdown blob
  and triggering the anchor click — ran cleanly.

## 4. One already-accepted gap, re-confirmed, not new

This pass re-confirms the Phase 6 note already on this tracker row:
`LibraryList` deliberately includes curated samples (unlike Workspace
Home's Recent Research, which excludes them), and because the seeded MSFT
sample is visible to every account, a genuinely-empty account's `Empty`
state is real, unit-tested, and correctly coded — but not reachable in this
or any live environment where that sample exists. Nothing new here; this
pass just independently walked into the same wall the tracker already
documents, which is itself a small piece of confirming evidence that the
existing note is accurate.

## 5. One state this pass did not force, and why

The Trust-First **unusable-report** banner (`isUsable` = non-empty
`draft_report` **and** non-empty `source_documents`, both required) was
**not** independently reproduced live this pass. Reaching it needs a report
that completes with a genuinely empty or unsourced brief — historically
observed (per this tracker's Phase 4A/4B notes) only when the underlying
LLM pipeline errors mid-run against an unreachable or misbehaving provider.
Forcing that on demand isn't reliable without deliberately sabotaging the
run, which risks producing a misleading one-off rather than real signal.
Not treated as a live-verification gap the way an untested happy path would
be: `ReportDocument`'s `isUsable` check is a simpler, single-component
version of the identical guarantee `company-research`'s `AIResponseCard`
already enforces via `isUsableReport()` — a mechanism the tracker's own §3
row already records as live-proven twice, including against a real
degraded run. Recorded here for completeness, not as an open defect.

## 6. Acceptance Criteria

- [x] `LibraryList` live-verified: Loaded (own report + sample, correctly
      badged and sorted), No Results, and the filter clear/restore
      round-trip. Empty re-confirmed as environmentally unreachable (not new).
- [x] `ReportDocument` live-verified: a freshly-generated own report
      (reached via a real row click, not a typed URL), the nonexistent/
      inaccessible-report error banner, and a working Export button.
- [x] Test account created and cleanly deleted; deletion confirmed via the
      backend's own access log.
- [ ] Promote Research Library to Migrated in the tracker — a follow-up
      action for Engineer/Reviewer alongside sign-off on this brief, same
      division as Slices 1 and 2.

## 7. Open Questions / Risks

- **The unusable-report banner (§5)** remains unverified live in this
  specific component, by design of this pass's own risk tolerance, not by
  oversight. If a future pass or incident produces a real degraded report
  under this account's normal use, worth a quick opportunistic screenshot
  rather than engineering one deliberately.
- **Sequencing unchanged**: per the original brief's §4, Company Research is
  next and last, as its own multi-part effort — its tracker-staleness
  correction is now done (2026-09-18, documentation-only, `2e7122e`), so
  nothing else blocks that slice from being scoped whenever it's picked up.
