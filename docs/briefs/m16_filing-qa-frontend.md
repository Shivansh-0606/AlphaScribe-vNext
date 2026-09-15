# M16 — Filing Q&A Frontend Wiring — Implementation Brief

**Date:** 2026-09-15. **Author:** Docs. **For:** Frontend Engineer (via Docs
Reviewer). **Governing contract:** [`docs/backend_engineering/87`](../backend_engineering/87_M16_Filing_QA_API_Contract_Proposal.md)
Revision 2 (§3, §6, §8, §9, §14 — request/response shape, citation shape,
state vocabulary, SSE framing), reconciled against the ratified architecture
in [`90`](../backend_engineering/90_M16_Filing_QA_Architecture_Decision_Pack.md)
(as amended by [`95`](../backend_engineering/95_D90_Candidate_Selection_Architecture_Amendment_Decision.md)/[`96`](../backend_engineering/96_Document95_Candidate_Selection_Architecture_Amendment_Ratification_Record.md)),
and verified directly against the **already-implemented, already-closed**
backend (commits `9035e27`, `8844566`; closure record
[`98`](../backend_engineering/98_M16_FQA_Milestone_Closure_Record.md), review/acceptance
[`99`](../backend_engineering/99_M16_FQA_Implementation_Review_and_Engineering_Acceptance_Record.md))
— routes and trace-event node names below were read from
`backend/server.py` and `backend/agents/filing_qa.py` this session, not
assumed from the docs. Sections cited, not restated.

*(Note for whoever reads Document 87 directly: its own header banner still
reads "DRAFT / PENDING CTO REVIEW — NOT RATIFIED". Per Documents 88/89/92 and
Document 99 §3, that banner is never edited after the fact — ratification is
recorded in a separate, later document instead. Document 99 §3 confirms the
full chain, including 87, is 🟢 RATIFIED. This is the same "verify the doc's
own header, not the surrounding narrative" trap flagged in this project's
own memory — resolved here by cross-checking the implementation review, not
by trusting either banner alone.)*

## 1. Goal

While viewing one ingested filing in the Filings tab, let the user type one
natural-language question about *that filing* and get back one grounded,
cited answer — or an honest "the filing doesn't address this" result —
wiring the frontend to the M16 backend that already exists.

## 2. Scope

**In:**
- New hooks `useFilingQAJob` (job lifecycle: start/cancel/retry + SSE) and
  `useFilingQA` (GET the completed result), mirroring
  `useFilingAnalysisJob`/`useFilingAnalysis` exactly.
- `integration/api.ts` additions: `createFilingQA`, `fetchFilingQA`,
  `cancelFilingQA`, `openFilingQAStream` — same shape as the M14 quartet.
- `integration/schemas.ts` additions for the M16 request/response/stream
  shapes (§6.1–§6.3, §14).
- `internal/streamStages.ts` addition: `FilingQAStage` +
  `deriveFilingQAStage`, single-phase like `FilingAnalysisStage`.
- A new `FilingQAPanel` component and a third option ("Q&A") on
  `FilingViewSwitch` in `FilingsSection.tsx`, alongside Content/Analysis.
- Rendering the completed answer (and its citations) by **reusing
  `FilingAnalysisViewer` unmodified** via a one-entry adapter — see
  Approach. No new citation-rendering component (Document 87 §8's own
  expectation).
- BYOK fields threaded through `useAiAccessStore`, identical to M14/M15.

**Out:**
- Anything backend. M16's backend is implemented, tested (789 passed),
  reviewed (Document 99, `ACCEPT`), and closed (Document 98). This brief
  touches only `web/features/company-research/` and nothing under `backend/`.
- Question history, multi-turn follow-up, "ask again with the last answer as
  context", or any persisted Q&A thread. Forbidden by the contract itself —
  FQA is stateless with respect to conversational state and DRS remains
  blocked (§1.2, §19). Each submit is a fresh, independent job; the UI must
  not simulate a memory the backend doesn't have.
- A new top-level `SectionNav` tab. Q&A nests inside the existing Filings tab
  per-filing, matching where Filing Analysis already lives — it's the same
  `(ticker, doc_id)` scope.
- Any new shared component for rendering `[n]` markers / `sources[]`.
  `FilingAnalysisViewer` + `SourceReference` + `remarkCitations` are reused
  as-is.
- Client-side enforcement of a maximum question length. The contract fixes
  no numeric literal for it (§17.2, §20 OAQ-6) — it's undisclosed
  operational config. The server's 422 is the only length gate; don't invent
  a client-side ceiling the client can't actually know.
- A test-id constants file or a persisted-draft mechanism. Neither exists
  anywhere in `web/` yet (per `CLAUDE.md`); FQA isn't the milestone that
  should introduce either speculatively.

## 3. Approach

**Routes (verified live in `server.py`, matching Document 87 §3.1 exactly):**
```
POST   /api/companies/{ticker}/filings/{doc_id}/qa
GET    /api/companies/{ticker}/filings/{doc_id}/qa/{id}
GET    /api/companies/{ticker}/filings/{doc_id}/qa/{id}/stream
POST   /api/companies/{ticker}/filings/{doc_id}/qa/{id}/cancel
```
`filingBasePath(ticker, docId)` already exists in `api.ts` (used for
`/content` and `/analysis`) — append `/qa` the same way.

**Request/response field names that differ from M14 — don't copy-paste
blindly:**
- Create body requires `question: string` (M14's create body has no
  required field — BYOK only).
- Status response's completed payload key is **`answer`**, not `analysis`
  (§6.2): `{id, status, answer?}`.
- SSE `final` frame body is `{"node": "final", "status": "ok", "answer":
  {...}}` (§14 item 2) — same framing, different key.
- `state` is a **2-value** enum (`"answered" | "insufficient_evidence"`,
  §9), not M14's 3-value `"complete" | "partial" | "insufficient_evidence"`.

**Trace node names for the progress list** (read directly from
`backend/agents/filing_qa.py`, not inferred): `"retrieving"` → "Selecting
relevant filing excerpts", `"answering"` → "Generating answer",
`"validating"` → "Validating citations", framed inside the standard
`pipeline` start/ok/warn/error + `final` envelope
(`_filing_qa_stream_events`, same shape as M14/M15). `deriveFilingQAStage`
should be a one-phase mapping exactly like `deriveFilingAnalysisStage` /
`deriveChangeBriefStage` — pipeline `start`→`answering`,
`ok`/`final`→`completed`, `error`→`failed`, `warn`→`cancelled`. The existing
`event.message ?? \`${event.node}: ${event.status}\`` rendering in
`FilingAnalysisPanel` needs no per-node label map — the backend's own
`message` strings are already human-readable.

**Rendering — the actual reuse trick.** `FilingAnalysisSourceAnchor`
(`{index, doc_id, chunk_start, chunk_end}`) in
`web/components/research/FilingViewer.tsx` is byte-identical to Document
87's frozen locator shape (§8) — it's the same shape by design (Document 87
§0/§21 cites Document 64 as its direct reuse basis for exactly this). FQA
has only **one** answer, so there's no cross-output citation-index collision
to renumber (the reason `FilingAnalysisViewer` renumbers markers in the
first place doesn't apply here — one output, no collision). `FilingQAPanel`
should build a single-entry record and hand it to the existing viewer
unmodified:

```ts
const outputs = {
  Answer: {
    narrative: answer.answer_text,
    sources: answer.sources,
    cited_source_indices: answer.cited_source_indices,
    state:
      answer.state === "insufficient_evidence"
        ? "insufficient_evidence"
        : answer.coverage_boundaries.length > 0
          ? "partial"
          : "complete",
    coverage_boundaries: answer.coverage_boundaries,
  },
};
return <FilingAnalysisViewer outputs={outputs} chunks={chunks} source={source} />;
```
**This mapping is load-bearing, not cosmetic — get it exactly right.** FQA's
`state` is a 2-value enum (§9), but the viewer's disclosure text ("Partial
coverage: …") only renders when `output.state === "partial"`
(`FilingViewer.tsx` — the check is strict; a `"complete"` output's
`coverage_boundaries` are never shown, full stop). Collapsing every
`"answered"` result straight to `"complete"` would silently hide the exact
disclosure Document 87 §9.1 requires: "Partial coverage… is still
`answered`, with the gaps disclosed in `coverage_boundaries` — there is no
separate `partial` state." The contract's disclosure requirement is met on
the frontend only by deriving `"partial"` from a non-empty
`coverage_boundaries` at the adapter, the way shown above — not by assuming
the viewer already does this for `"complete"` outputs (it doesn't). Still a
one-line adapter, no viewer changes.

**Schemas — reuse, don't redeclare, where the shape is actually identical:**
- Source anchor: reuse `filingAnalysisSourceSchema` verbatim (same 4 fields).
- Create response `{id, status, reused}`: reuse
  `createFilingAnalysisResponseSchema` verbatim.
- Cancel response `{id, status}`: reuse `cancelFilingAnalysisResponseSchema`
  verbatim.
- New, because the shape genuinely differs: `filingQAStateSchema` (2-value
  enum), `filingQAAnswerSchema` (adds `question`, no `narrative`/multi-output
  wrapper), `createFilingQARequestSchema` (adds required `question`),
  `filingQAStatusResponseSchema` (`answer` key), `filingQAStreamEventSchema`
  (`answer` key in the `final` frame). **Don't copy-paste
  `filingAnalysisPayloadSchema`'s field list for this one** — the actual
  `answer_payload` dict built in `server.py` (~3028–3039) is `{ticker,
  doc_id, question, answer_text, sources, cited_source_indices, state,
  coverage_boundaries, created_at, prompt_version, schema_version}`. It has
  no `company_name` and no `source` (both present on `FilingAnalysisPayload`)
  — build `filingQAAnswerSchema` from this list, not from the M14 one.

**Job hook shape.** `start()` takes exactly one argument, the question
string — closer to `useResearchJob.start(query)` than to
`useFilingAnalysisJob.start()` (no args) or `useChangeBriefJob.start(body)`
(full request object), since FQA has exactly one required, user-authored
input and no mode/reference selection. `retry()` should resubmit the same
last question, mirroring `useChangeBriefJob`'s `startMutation.variables`
pattern (not `useFilingAnalysisJob`'s no-arg retry, which has nothing to
resubmit).

## 4. Acceptance Criteria

- [ ] From the Filings tab, with a filing open, a "Q&A" view (alongside
      Content/Analysis) lets the user type a question and submit it.
- [ ] While running, the panel shows live progress from the `retrieving` /
      `answering` / `validating` trace events and a Stop control that calls
      `cancel`.
- [ ] On completion, the answer renders with inline `[n]` citations linking
      to real excerpts from the filing's own chunks, via the reused
      `FilingAnalysisViewer` — no new rendering component.
- [ ] An `insufficient_evidence` result (including the zero-content-filing
      case, §9.3) renders honestly — not as an error, not silently upgraded.
- [ ] An `answered` result with non-empty `coverage_boundaries` visibly
      discloses them (via the adapter's `"partial"` derivation and the
      viewer's existing partial-coverage badge/text) — never rendered
      identically to a fully-covered answer.
- [ ] A 422 (empty/too-long/missing question) shows as an inline form error
      without ever creating a job.
- [ ] Cancel and Retry (same question) both work; switching filings
      (`key={docId}`, matching `FilingAnalysisPanel`'s existing convention)
      resets to idle.
- [ ] No question history, thread, or "previous answer" is shown once a new
      question is asked — each submission is visibly a fresh, independent
      result.
- [ ] BYOK fields (managed vs custom provider) behave identically to the
      Analysis and Change Brief panels on the same screen.
- [ ] Hook/component tests exist mirroring the existing
      `FilingAnalysisPanel.test.tsx` coverage, adjusted for the contract's
      2-value `state` enum (not M14's 3-value one — the third render state,
      `"partial"`, is derived at the adapter, not present on the wire) and
      the single-answer (not multi-output) body.

## 5. Open Questions / Risks

- **UI copy** ("Q&A" vs "Ask a question" as the switch label, button text,
  empty-state copy) is a product/UX call, not fixed by the contract —
  Engineer or Reviewer can pick; doesn't block starting the build.
- ~~**Reusing `FilingAnalysisViewer`'s `state` prop type.**~~ Resolved —
  originally flagged this as "the viewer allows `partial`, a value FQA will
  never produce." That was wrong: FQA's own disclosure requirement (§9.1)
  can only surface through the viewer's existing `"partial"` treatment, so
  the adapter does emit it (§3). No follow-up needed; the prop type is used
  as designed, not merely tolerated.
- ~~**Sequencing with M15.**~~ Resolved — M15's Change Brief frontend work
  (touching the same `integration/api.ts` / `integration/schemas.ts` /
  `internal/streamStages.ts` files) landed as commit `8224be8` before this
  brief reached Engineer. Build on top of current `main`; no coordination
  needed.
- **Zero-byte stray files** noted in Documents 98 §8.2 / 99 §11
  (`backend/whole-filing`, `backend/None`, etc.) are pre-existing backend
  working-tree hygiene debris, unrelated to and out of scope for this
  brief — flagged only so the Engineer doesn't mistake them for something
  this work touches.
