# Migrated-Parity Hardening Pass — Company Research Sub-Slice 6: Export — Implementation Brief

**Date:** 2026-09-21. **Author:** Docs. **For:** Frontend Engineer (via Docs
Reviewer). **Governing precedent:** [`docs/briefs/hardening_company-research-ai-insights.md`](hardening_company-research-ai-insights.md)
(Sub-Slice 5) and CTO's six-sub-slice breakdown of Company Research. This
brief covers `ExportSection.tsx` — by design an honest hand-off, not a
second export implementation: the actual export mechanism (a client-side
Markdown download preserving reasoning + sources) lives on Report View,
owned by `research-library` (`ReportDocument.tsx` /
`internal/exportMarkdown.ts`). This is the last of the six Company Research
sub-slices.

## 1. Goal

Re-verify Export end-to-end: does the "Open Report View" hand-off only
appear once a report has actually been generated, and does the underlying
export mechanism (Report View's own Export button) actually work? Also, per
CTO's specific ask after Sub-Slice 5's finding: does Export's own gating on
Overview job status share that same blind spot, or is it a confirmed-safe
surface?

## 2. Result: not the same blind spot as Sub-Slices 2/5 — a related but distinct one. Export doesn't discard a fetched job's status; it never fetches status at all. It treats "a job id exists in the URL" as "a report is ready," so the hand-off appears the instant ANY Overview run starts, not once it completes — pointing users at a link that 404s-in-spirit until the run finishes. The actual export mechanism itself, once a report is genuinely complete, works correctly.

## 3. Finding A (headline, CTO's specific ask): the "Open Report View" hand-off is shown from the moment a job starts, not once it completes — clicking it early leads to a dead end

**Observed live:** started a real Overview job for MSFT
(`2492db9d-dcd9-4885-a2a6-dfaa4d1cc3b2`) and, while it was still mid-run
("Gathering filings and preparing to analyze…" — no report exists yet),
switched to the Export tab. It immediately showed **"Export happens from
the Report View, which preserves the full reasoning and sources behind this
report"** with a live **"Open Report View"** link to `/reports/{jobId}` —
worded and presented identically to how it looks once the report is
actually done. Following that link while the job was still running landed
on Report View's own error state: **"Couldn't load this report — it may
not exist, or you may not have access to it,"** with a Retry button — a
dead end, and a misleading one in a different direction than Sub-Slices
2/5's finding (there, a done/failed job was called "still running"; here,
an in-progress job is called "may not exist"). Once the same job genuinely
completed, re-opening the identical link worked correctly and rendered the
full report.

**Root cause, and how it differs from Sub-Slices 2/5's finding:**
`ExportSection` does not call `useReport` or `useReportStatus` at all — it
has no data-fetching of its own. `CompanyResearchScreen.tsx` passes it
`reportId={jobId}`, where `jobId` is the raw `?job=` URL parameter
`OverviewSection` writes the moment a run starts (confirmed against that
component) — **not** a value derived from a completed report. `ExportSection`
then treats any truthy `reportId` as "ready": `if (reportId) return <...Open
Report View link.../>`. So this is not the `useReport`-discards-`status`
pattern Financials (Sub-Slice 2) and AI Insights (Sub-Slice 5) hit — there is
no fetch to discard a status from. It's one layer further upstream: the
component conflates "a job id is present" with "a report exists," with
nothing in between checking whether that job actually finished. The
practical symptom rhymes with the other two findings (a UI element presents
readiness that isn't real) but the code shape and the fix shape are both
different — adopting `useReportStatus` doesn't apply here since there's no
existing fetch to swap; the fix has to add a status check where today there
is none.

**Confirmed at the test level too:** `ExportSection.test.tsx`'s second case
is titled *"links directly to Report View once a report has been generated
this run"* but passes a bare string (`reportId="report-1"`) with no
completed-report fixture behind it — the test's own name describes the
intended behavior (gate on generation) while its body only ever checks that
a truthy id produces the link, the same gap as the implementation.

## 4. What worked correctly, confirmed live

- **The actual export mechanism, once a report is genuinely complete**:
  re-opened Report View for the same job after it finished — rendered
  correctly (title, confidence badge, full markdown body with citations,
  sources list). Clicking **Export** flipped the button to "Exported" with
  no errors; read `internal/exportMarkdown.ts` to confirm the mechanism —
  a client-side `Blob`/anchor download of a Markdown file assembling
  `draft_report` + a numbered source list, no backend call, no new
  dependency. This satisfies the stated requirement (preserve reasoning +
  sources) without duplicating an export implementation, exactly as the
  module's own doc comment describes.
- **The "no report yet" gate**: confirmed live before starting any research
  — Export correctly shows the generic "Export isn't built here... Generate
  a report first" copy with no link, when `jobId` is genuinely absent.
- **This is a different bug shape than Sub-Slices 2/5's, not a third
  instance of the identical one** — worth stating explicitly since it was
  the specific thing asked to check: Export does not reuse the
  status-discarding `useReport` pattern at all; it has its own, narrower
  gap (no status awareness whatsoever, rather than status fetched-then-
  discarded).

## 5. Acceptance Criteria

- [x] Verified whether Export shares Sub-Slices 2/5's exact `useReport`
      blind spot — confirmed it does not; documented the distinct but
      related gap it does have instead.
- [x] Finding A reproduced live (mid-run and post-completion), root-caused
      to `CompanyResearchScreen` passing the raw `?job=` param as
      `reportId`, corroborated by the test suite's matching gap.
- [x] The actual export/download mechanism live-verified working correctly
      on a genuinely completed report.
- [x] The "no report yet" gate confirmed live.
- [ ] Finding A's fix (gate the hand-off on the job's actual terminal status,
      not just its presence) is not applied here.

## 6. Open Questions / Risks

- **Fix shape, not decided here**: the cleanest fix is likely for
  `CompanyResearchScreen` (which already knows `jobId`) to also know whether
  that job completed successfully — e.g. via the same `useReportStatus`
  pattern Financials uses — and pass `ExportSection` a `reportId` only once
  status is `completed`, otherwise `undefined` (falling back to today's
  honest "generate a report first" copy, which already handles the absent
  case correctly). This keeps `ExportSection` itself simple and stateless.
  Not applied here.
- **This closes the six-sub-slice Company Research hardening-pass
  sequence** (Overview → Financials → Filings → Changes → AI Insights →
  Export). Three sub-slices (Financials, AI Insights, Export) now each carry
  their own flavor of "UI presents a state before/regardless of the actual
  backend job's real status" — Financials and AI Insights share one exact
  code shape (`useReport` discarding `status`), Export has an adjacent but
  distinct one (no status check at all). Per CTO-2's direction, a
  proper grep audit across all Company Research surfaces that gate on job/
  report state (not just the ones this hardening pass happened to touch) is
  the right next step, rather than continuing to find these one sub-slice
  at a time.
