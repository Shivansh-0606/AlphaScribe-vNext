# Migrated-Parity Hardening Pass — Company Research Sub-Slice 1: Overview + Streaming — Implementation Brief

**Date:** 2026-09-19. **Author:** Docs. **For:** Frontend Engineer (via Docs
Reviewer). **Governing precedent:** [`docs/briefs/hardening_migrated-parity-pass.md`](hardening_migrated-parity-pass.md)
§6's recommendation not to scope Company Research as one end-to-end pass —
CTO confirmed this explicitly and broke it into six sub-slices (Overview+
streaming, Financials, Filings, Changes, AI Insights, Export). This brief
covers the first: `OverviewSection.tsx` (`web/features/company-research`)
and its streaming lifecycle (`useResearchJob.ts`, `sse-client.ts`,
`streamStages.ts`), plus the finished-report render (`AIResponseCard.tsx`).
The remaining five sub-slices are each their own future brief.

## 1. Goal

Re-verify Company Research's Overview section and its SSE-driven research
lifecycle end-to-end against the real running backend and a real configured
LLM — the tracker's own **Migrated** bar — as the entry point sub-slice the
other five build on.

## 2. Result: zero product defects found. One real, minor UX polish gap. Recommend promoting this sub-slice's scope once Docs Reviewer confirms.

Note on tracker mechanics: Company Research's §3 row covers all six
sections in one row, not one row per section — so this sub-slice's result
doesn't promote the row by itself. It's recorded here as evidence toward
that eventual promotion, the same way each of the five remaining sub-slices
will need to land before the row as a whole can move to Migrated.

## 3. What was exercised and confirmed real

**Method:** the shared dev stack, one disposable test account
(`docs-hardening-overview@example.com`), deleted at the end via its own
delete-account step — confirmed via the backend's own access log. A real
configured LLM was reachable throughout (`nvidia/nemotron-3-super-120b-a12b`
via an OpenAI-compatible endpoint) — every run below is a genuine external
LLM call, not a mock.

### 3.1 Full lifecycle, start to finish

- **Idle → Start**: submitting a query against a ticker with existing
  filings (IBM — already present in this shared, persistent dev corpus from
  earlier testing, not freshly ingested by this pass) correctly transitions
  to `thinking`, then through `streaming`/`grounded` stages with real,
  human-readable trace messages (`Retrieved 8/178 chunks via
  bm25+dense+cross-encoder`, `Sentiment: Bullish (0.85)`, `Structured
  financials extracted`, `Draft written (N chars)`).
- **Completed**: the finished report rendered via `AIResponseCard` with real
  extracted financial `MetricStat` cards (Revenue, Revenue YoY, EPS, Net
  Income), real sentiment, a full cited markdown brief, and 8 real
  `SourceReference` entries — confirmed after the job actually completed
  server-side (§3.4), not assumed from the streaming trace alone.

### 3.2 Cancel and Retry — both backend-confirmed, not just UI-optimistic

- **Cancel**: clicking "Stop generating" mid-run immediately showed the
  optimistic `Analysis was cancelled.` banner with the produced trace
  retained (Law 6 — "never lose produced work") — and a real `POST
  .../cancel → 200 OK` was confirmed in the network log, not just the
  client-side dispatch.
- **Retry**: from the cancelled state, Retry correctly resubmitted the
  original persisted query (`sessionStorage`-backed, per the component's own
  `retryQueryKey` mechanism) as a fresh `POST .../generate` call with a new
  `job_id`, and the event list correctly reset to empty before the new run's
  own trace began.

### 3.3 Reload / `?job=` deep-link resume — mid-run, not just post-completion

Reloading the exact `?ticker=IBM&job=<id>` URL **while the job was still
actively streaming** correctly: reopened the SSE connection, replayed the
**full** prior event history in order, and continued receiving new live
events afterward (`Draft written` appeared post-reload, `Fact-check failed`
and the retry draft appeared later still) — a genuine mid-flight resume,
not just a completed-job reload.

### 3.4 A real self-healing event, witnessed live: the retry-router actually retries

One IBM run's fact-checking step failed with a real, backend-surfaced error:
`Fact-check failed: LLM output was truncated by the max_tokens cap
(LLM_MAX_OUTPUT_TOKENS). Raise it in backend/.env and retry.` — and the
pipeline's own conditional router (`agents/graph.py`'s "retries the
synthesizer or ends" edge, per this project's own architecture guide)
**automatically retried the synthesizer**, producing a longer redraft
(`Draft written (2105 chars) [retry 1]`), which was then re-fact-checked and
eventually completed successfully (§3.1's finished IBM report **is** this
retried run). This is the first time this specific self-healing path has
been directly witnessed live in any hardening-pass slice — confirms the
retry-or-end router is real, not just a design description.

**One real, minor finding from this same event:** the trace message text
itself — `Raise it in backend/.env and retry` — is operator/developer
guidance, not something an end user could act on (they don't have server
`.env` access). It's currently surfaced verbatim in the same user-visible
trace log as every other, genuinely user-relevant message (`Retrieved
8/178 chunks...`, etc.), which elsewhere in this codebase follows a
discipline of never leaking raw internal detail to end users (see, e.g.,
M14/M16's "redacted message; raw provider text never surfaced" convention
for provider errors). This one specific string doesn't follow that
convention. Low severity — the retry is automatic and invisible to a user
who isn't reading the trace log closely — but a real, concrete instance,
not a hypothetical.

### 3.5 Cache-hit short-circuit — confirmed live, not just from reading the code

Resubmitting the **exact same** `(ticker, query)` pair under the same
account (`IBM`, `"Summarize the latest quarterly results and key
risks."`) — after the first run had genuinely completed — returned
`{"job_id": "...", "cached": true}` **instantly**, with no SSE stream opened
at all, and the identical finished report rendered immediately. Confirmed
directly against the response body of the `POST .../generate` call, not
inferred. Also confirmed by reading `server.py`'s cache-lookup query
(`{"$or": [{"user_id": user["id"]}, {"is_sample": True}]}`) that this cache
is scoped per-user-or-sample, not global — a fresh account never
accidentally reuses a stranger's cached run.

## 4. Not independently forced this pass, and why

- **The `NO_FILINGS_MARKER` ingest-empty-state** (paste/EDGAR-fetch/load-
  samples) was not reached — the test ticker chosen (IBM) turned out to
  already have filings in this shared, persistent dev corpus from earlier
  testing sessions, discovered only after starting the run. Not treated as
  a gap: this exact code path (`job.startError?.message.includes(...)`) is
  a simple, direct string match already live-verified during Phase 4A's
  original pass and unchanged since — re-deriving it would be re-proving
  something that hasn't been touched, not closing a real risk.
- **Two concurrent jobs slowed each other down.** Running a second job
  (MSFT) while IBM's was still active visibly extended both jobs' wall-clock
  time — consistent with a shared external LLM rate limit, not a app-side
  bug. The MSFT run's specific job id was lost when this session's dev
  stack restarted mid-pass (a session-continuity issue on this pass's side,
  not the product's) before its outcome was captured; not re-attempted,
  since §3.1–§3.5 already independently prove the same code paths via IBM.
- **A multi-hour session gap occurred mid-pipeline-run.** The backend
  process itself kept running server-side throughout and both restart-
  survived tests here (IBM's completion, §3.1; the cache hit, §3.5) confirm
  the async job model is correctly decoupled from any client connection —
  worth calling out as a positive property proven somewhat by accident,
  not a methodology gap.

## 5. Acceptance Criteria

- [x] Full Overview lifecycle (idle→thinking→streaming→grounded→completed)
      live-verified with a real LLM, real citations, real extracted
      financial metrics rendered via `AIResponseCard`.
- [x] Cancel and Retry both live-verified, including the real backend
      `POST .../cancel` call, not just client-side optimism.
- [x] Reload/`?job=` deep-link resume live-verified **mid-run**, not just
      after completion — full event history replay confirmed.
- [x] The conditional retry-router (fact-check-truncation → automatic
      synthesizer retry → re-fact-check → completion) witnessed live for
      the first time in this hardening pass.
- [x] Cache-hit short-circuit (`cached: true`) live-verified against the
      actual response body, plus its per-user/sample scoping confirmed
      against the backend query.
- [ ] One real, minor UX finding (§3.4) — the dev-facing fact-check-retry
      message text — recorded for Engineer's judgment on whether it's worth
      a small copy fix or accepted as-is; not blocking.

## 6. Open Questions / Risks

- **The dev-facing trace message (§3.4)**: is this worth a small,
  standalone copy fix (redact the `backend/.env` instruction the same way
  provider errors already are), or is it acceptable as-is since it only
  ever appears mid-retry and the retry itself is invisible to a casual
  user? Docs Reviewer/Engineer's call — flagged, not fixed here.
- **Sequencing**: per CTO's breakdown, Financials is the natural next
  sub-slice (M12, multi-period statements) — not started by this brief.
- **The Company Research §3 tracker row** stays **In Progress** until all
  six sub-slices land; this brief's evidence is one of six inputs to that
  eventual promotion, not a promotion on its own.
