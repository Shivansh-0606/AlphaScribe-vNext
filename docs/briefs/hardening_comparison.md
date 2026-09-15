# Migrated-Parity Hardening Pass — Slice 2: Comparison — Implementation Brief

**Date:** 2026-09-16. **Author:** Docs. **For:** Frontend Engineer (via Docs
Reviewer). **Governing precedent:** [`docs/briefs/hardening_migrated-parity-pass.md`](hardening_migrated-parity-pass.md)
§4/§6 (sequencing + scope notes) and [`docs/governance/Feature_Parity_Tracker.md`](../governance/Feature_Parity_Tracker.md)
§4 (Comparison's existing row, Phase 7). This is Slice 2 of the initiative
Slice 1 (Workspace Home) started — same live-verify-and-promote treatment,
one track, live-verified end to end.

## 1. Goal

Re-verify Comparison (`web/features/comparison`) end-to-end against the real
running backend — the tracker's own **Migrated** bar — rather than carrying
forward Phase 7's one-time verification result from 2026-08-15.

## 2. Result: zero defects found. Recommend promoting Comparison to Migrated.

Exactly the three things scoped in the prior brief's §6 were exercised, plus
one entry point that scoping didn't call out but turned out to matter (§3.4).

## 3. What was exercised and confirmed real

**Method:** the already-running shared dev stack (started by another peer
session earlier; reattached to it rather than spawning a second instance
that would conflict on ports), one disposable test account
(`docs-hardening-comparison@example.com`), deleted via its own delete-account
step at the end — verified by the backend's own access log (`DELETE
/api/auth/me → 200 OK`) immediately followed by a redirect to Sign in, not
just a client-side redirect.

### 3.1 ComparisonPicker

- **Candidate list** (`GET /reports`, capped by `MAX_MEMBERS = 4`): a fresh
  account sees exactly one candidate — the seeded `Microsoft Corporation
  (Sample)` — matching this feature's own doc comment ("candidates come
  from existing saved reports... Comparison operates on already-generated
  reports, not raw ticker search").
- **Ticker filter** (debounced): typing `"ZZZZ"` correctly renders `No
  reports match "ZZZZ".` and — importantly — does **not** clear or refetch
  the already-selected comparison below it; the filter only narrows picker
  candidates, confirmed live, not just from reading the query-key code.
- **Chip selection / deselection**: toggling a chip on moves the selection
  count (`1/4` → `2/4`) and renders the table; toggling one back off
  correctly drops it, reverts to the "Select at least one more report to
  compare" copy, and updates the URL to the single remaining id (§3.3).

### 3.2 ComparisonTable — both gap-flagging mechanisms, in one real comparison

Generated one real, own report (MSFT, via Company Research's Overview,
against the real NVIDIA-hosted LLM configured in this environment — grounded
brief, real citations, real sentiment) specifically so the comparison would
have a genuinely different second member instead of two identical samples.
The resulting real two-report comparison exercised **both** documented
`ComparisonTable` behaviors at once, not just one:

- **Per-metric `unavailable` flagging**: the sample report has real values
  for 5 of 6 metrics and correctly shows "Not available" for the one it
  lacks (Free Cash Flow) — the *individual missing-metric* case.
- **The "Limited data" badge**: my own report's extraction returned no
  structured financials at all (the filing excerpts didn't disclose
  quarterly figures — an honest model limitation, not a bug), so every one
  of its 6 metric cells correctly reads "Not available" **and** the column
  header correctly carries the `Limited data` badge — the *zero-extracted-
  data member* case, `hasNoExtractedData()`'s own reason for existing.
- Sentiment rendered correctly for both (`Bullish` / `Neutral`), numeric
  columns right-aligned per the frozen spec, console clean throughout.

### 3.3 `?ids=` deep-link / reload persistence

- Selecting two chips produced `?ids=<id1>,<id2>` in the URL (URL-encoded
  comma), confirmed via `window.location.href`, not inferred.
- A full page reload (not client-side navigation — a real `navigate()` to
  the same URL, forcing `ComparisonScreen`'s `initialIds` prop to
  re-hydrate from scratch) restored the **exact same** two-report
  comparison, table and all.
- Removing one chip correctly rewrote the URL down to the single remaining
  id (`?ids=<id1>`), confirmed the same way.

### 3.4 Not in the original scope note, but real and worth recording: "Add to comparison"

Company Research's Overview screen has a real `Add to comparison` link
(`/compare?ids=<jobId>`) on a completed report, not mentioned in the prior
brief's §6 scope note or the tracker's Comparison row. Followed it live: it
correctly pre-selected that report's chip (`1/4 selected`) on arrival at
`/compare`. A real, working cross-feature entry point — recorded here since
whoever eventually corrects the Company Research tracker row (queued, not
part of this brief) should know this link exists and is Comparison's, not
Company Research's, to describe.

## 4. One infrastructure observation, precisely characterized — not a Comparison defect

While generating the own-report needed for §3.2, `/api/health` and every
other backend endpoint briefly stopped responding — confirmed independently
via a 5-second-timeout `curl` (exit 28, no response at all), not just a slow
page. This matches what earlier sessions today logged as a "blocked event
loop" requiring a restart. **This pass's own evidence is more specific and
less alarming than that:** waiting roughly another 10–15 seconds without
intervention, `/api/health` returned `200 OK` in 0.22s, and the backend's own
logs showed real activity throughout the gap — two `503`s from
`integrate.api.nvidia.com` that were retried and succeeded, plus (by
elapsed-time inference) the CPU-bound BM25/dense/cross-encoder retrieval
step, which the codebase confirms runs synchronously. **This pass did not
need a restart; it recovered on its own.** Recorded as a characterization
correction, not a contradiction — it's possible other sessions hit a longer
or genuinely stuck instance of the same underlying cause (a synchronous,
non-yielding step monopolizing the single-process event loop during report
generation) rather than a different bug. Not a Comparison defect either way
— `compare_reports` itself is a pure lookup with no LLM call and was never
implicated. Flagging for whoever eventually looks at Company Research's own
hardening slice (which will generate reports far more often) as a
worth-watching operational characteristic, not a p0.

## 5. Acceptance Criteria

- [x] `ComparisonPicker` live-verified: candidate list, ticker filter
      (including its empty state and non-interference with an active
      comparison), chip selection and deselection, the `MAX_MEMBERS` label.
- [x] `ComparisonTable` live-verified against a real two-report comparison
      exercising both the per-metric `unavailable` flag and the
      zero-data-member `Limited data` badge in the same pass.
- [x] `?ids=` deep-link and full-reload persistence live-verified, both add
      and remove directions.
- [x] Test account created and cleanly deleted; confirmed via the backend's
      own access log, not just the client-side redirect.
- [ ] Promote Comparison to Migrated in the tracker, carrying forward the
      "Add to comparison" entry point (§3.4) as a new, previously-undocumented
      detail on that row — a follow-up action for Engineer/Reviewer to make
      alongside sign-off on this brief, same division as Slice 1.

## 6. Open Questions / Risks

- **Who documents "Add to comparison" (§3.4) and where** — it's a
  Company-Research-originated link but Comparison-owned behavior. Simplest:
  add one sentence to Comparison's tracker row when it's promoted; no new
  row needed.
- **The event-loop-stall characterization (§4)** is this pass's own direct
  evidence, not a re-litigation of what earlier sessions saw. If it recurs
  for longer or without self-recovery during a future slice, that's worth
  escalating as its own investigation — not assumed resolved by this one
  data point.
- **Sequencing unchanged**: per the prior brief's §4, Research Library is
  next, then Company Research last (as its own multi-part effort, still
  pending the tracker-accuracy correction queued separately).
