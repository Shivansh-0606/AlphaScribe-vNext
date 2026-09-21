# Migrated-Parity Hardening Pass — Company Research Sub-Slice 3: Filings — Implementation Brief

**Date:** 2026-09-19. **Author:** Docs. **For:** Backend/Frontend Engineer
(via Docs Reviewer). **Governing precedent:** [`docs/briefs/hardening_company-research-financials.md`](hardening_company-research-financials.md)
(Sub-Slice 2) and CTO's six-sub-slice breakdown. This brief covers the
Content/Analysis/Q&A three-way switch (`FilingsSection.tsx`,
`FilingAnalysisPanel.tsx`/M14, `FilingQAPanel.tsx`/M16) and, because live
verification surfaced it directly, the backend generation paths those two
panels depend on (`agents/filing_analysis.py`, `agents/filing_qa.py`).

## 1. Goal

Re-verify Filings' Content/Analysis/Q&A switch end-to-end against the real
running backend and a real reachable LLM, on real filings of meaningfully
different sizes — not just a single small happy-path case.

## 2. Result: the headline finding is more significant than any prior sub-slice's. Both Filing Analysis (M14) and Filing Q&A (M16) are live-confirmed to reliably fail — deterministically, not flakily — on a large, real 10-K, both via the exact same unhandled failure class. This is a deliberate architectural boundary, not sloppy code, but this pass makes its real cost concrete for the first time.

Two independently-acquired filings were used specifically to bracket this:
`MSFT`'s 10-K (215 chunks, 200,000 chars — the largest ingested filing
available) and its 10-Q (4 chunks, 2,500 chars — a small excerpt). All
three views work correctly, honestly, and per-spec on the small filing.
Two of the three (Analysis, Q&A) are **reliably broken** on the large one.

## 3. Finding A (headline): `NonRetryableLLMError` from output-truncation is uncaught in both `filing_analysis.py` and `filing_qa.py`, crashing the whole job — reproduced 3/3 times on one real large filing

**Observed live:** running Filing Analysis against MSFT's 10-K failed
**twice in a row**, byte-identical stack trace both times:
```
backend/agents/filing_analysis.py:457, in analyze_filing
    raw = await generate_output(candidates, kind, model=heavy_model, chat_fn=chat_fn)
...
agents.llm.NonRetryableLLMError: LLM output was truncated by the max_tokens
cap (LLM_MAX_OUTPUT_TOKENS). Raise it in backend/.env and retry.
```
Running Filing Q&A against the **same** 10-K (a fresh question, a fresh
job) failed on its **first** attempt, with the **identical exception class**
from a **different** call site:
```
backend/agents/filing_qa.py:431, in answer_question
    raw = await generate_answer(candidates, question, model=heavy_model, chat_fn=chat_fn)
```
Both jobs correctly surfaced only the generic, redacted
`"Pipeline failed: {Filing analysis|Filing Q&A} failed. See server logs
for details."` to the user (no raw internal text leaked, unlike the
Overview sub-slice's finding on this same underlying error) — but both
lost **all** their work. Filing Analysis had already produced two of its
four outputs (confirmed via the SSE trace: `Filing Summary`, `Risk Factors
Digest` both logged as reached) before output 3's generation call truncated
and killed the entire job — a real cost, not a one-off, since a retry
starts completely over from output 1.

**Root cause, precisely isolated in both files:** each module catches
exactly one narrow, *post-generation* error class and nothing else:
- `filing_analysis.py:462` — `except FilingAnalysisGroundingError`, with its
  own comment stating the boundary explicitly: *"M-3: a structurally
  inconsistent citation result is contained to THIS output... Only this
  defined grounding failure is caught — any other exception still
  propagates and fails the job loudly."*
- `filing_qa.py:439` — `except FilingQACitationStructureError`, the same
  shape: a citation-*structure* validation failure is contained; a raw
  generation failure is not.

`NonRetryableLLMError` is raised **before** either of those validators ever
runs — there is nothing to catch it in either file, by design, and the
exception propagates uncaught to `server.py`'s `_run_filing_analysis` /
`_run_filing_qa`, which log it and mark the whole job `failed`.

**This is not the same kind of finding as Sub-Slice 2's Findings A/B/C.**
Those were unintentional (a substring bug, a missing status check). This
one is a **known, load-bearing design boundary**, and for Filing Q&A it is
**contract-mandated, not just a code choice**: Document 87 (M16's ratified
API contract) §17.1 explicitly states *"Structured-output repair that
requires an additional model completion is an additional model completion
and is not permitted by this contract as drafted... [it] requires an
explicit contract amendment, not a silent implementation choice."* Adding a
retry-on-truncation path to Filing Q&A the way Overview's graph-level
`fact_check_router` already does for Research would mean amending Document
87, not just patching code.

**What this pass adds that wasn't known before:** not that this boundary
exists (it's documented, on purpose, in both places) — but that it is
**live-reproducible, deterministically, on real ingested content of a size
this product will routinely encounter** (a standard company 10-K, not an
edge case). A design choice with a previously-theoretical cost now has a
concrete, measured one: two consecutive full-job failures on one real
filing, discarding genuine partial progress each time.

## 4. What worked correctly, confirmed live

- **Content view**: renders the full persisted text of both a large (215
  chunks) and small (4 chunks) real filing correctly, `Read content`/`Hide
  content` toggle working, chunk/char counts accurate.
- **Filing Analysis, on a filing small enough not to trigger Finding A**:
  completed cleanly, and — valuably — exercised **all three** of the
  frozen per-output states in one real run: `Filing Summary` (`complete`,
  real citations), `Risk Factors Digest` (`partial`, with a real,
  honest `coverage_boundaries` disclosure — "section start located but its
  end boundary could not be structurally established"), and `MD&A
  Digest`/`Important Changes` (`insufficient_evidence`, correctly honest
  that a 4-chunk excerpt has no MD&A section to find). This is exactly the
  M14 citation/state contract working as designed — the underlying
  per-output logic is sound; Finding A is specifically about the
  *generation* step upstream of it.
- **Filing Q&A, on the same small filing**: two independent questions, each
  a fresh job with no memory of the other (confirmed — the second answer
  never referenced the first question's content), both correctly cited to
  real chunk ranges, `SourceReference` popovers present and correctly
  labeled.
- **Filing Q&A, on the large filing, for retrieval/candidate-selection
  itself** (as distinct from the generation call that then failed): the
  "Selecting relevant filing excerpts" stage completed and progressed to
  "Generating answer" before hitting Finding A — i.e., the M16 candidate-
  curation algorithm (the N>K position-selection formula from Document 95)
  itself handled the 215-chunk filing fine; the failure is specifically in
  the single generation call afterward, not in retrieval.

## 5. Finding B (minor, ingestion-side, not this section's own code): raw XBRL taxonomy metadata appears as filing "content"

**Observed live**, scrolling through the large 10-K's Content view: a
meaningful stretch of the persisted, displayed text is raw inline-XBRL
taxonomy declarations —
`http://fasb.org/us-gaap/2025#DerivativeAssets`,
`http://fasb.org/us-gaap/2025#ShortTermInvestments`, and similar namespace
URIs, dozens in a row — not human-readable filing prose. Confirmed this
isn't a `FilingViewer` rendering defect: the component renders chunk text
verbatim with no transformation, and `grep`ping `agents/ingest.py` for any
XBRL-aware extraction/stripping found none. This is an ingestion-side
content-extraction quality gap, not a defect in the Filings section's own
code, and not flagged with a `ponytail:` marker the way this repo usually
records an accepted, known-ceiling shortcut — recorded here because it's
directly visible through the Content view this sub-slice is reviewing, not
because it belongs to this brief's own fix surface.

## 6. Acceptance Criteria

- [x] Content view live-verified on both a large and a small real filing.
- [x] Filing Analysis's three per-output states (complete/partial/
      insufficient_evidence) all live-verified in one real run.
- [x] Filing Q&A's stateless-per-question behavior and citation rendering
      live-verified across two independent questions.
- [x] Finding A reproduced 3/3 (2× Filing Analysis, 1× Filing Q&A) on one
      real large filing, root-caused to an exact, named, and in Filing
      Q&A's case contract-documented, design boundary in both modules.
- [x] Finding B observed and attributed to ingestion, not this section.
- [ ] Finding A is a design/scope question, not a straightforward bug fix —
      see §8. Not applied here.

## 7. Open Questions / Risks

- **Finding A's actual resolution path needs a decision, not just a
  patch.** Candidate directions, none chosen here: (a) widen Filing
  Analysis's per-output containment (§3's `filing_analysis.py:462`) to also
  catch `NonRetryableLLMError` and degrade *that one output* to
  `insufficient_evidence` rather than failing the whole job — this doesn't
  touch any ratified contract, since Document 64 (M14) doesn't have Document
  87's §17.1 one-generation restriction; (b) for Filing Q&A specifically,
  since Document 87 §17.1 explicitly requires a **contract amendment**
  before any repair/retry completion can be added, this is a CTO-level
  decision, not something Engineer can just fix; (c) reduce the candidate
  window / lower the operational output-length ceiling so truncation
  becomes less likely in practice, without touching the generation-retry
  question at all. This brief surfaces the evidence; it doesn't pick (a),
  (b), or (c).
- **How common is a 215-chunk-scale filing in practice?** Not established
  here — this pass used the largest filing already present in the shared
  dev corpus, not a deliberately worst-case one. Worth Backend confirming
  whether this is a realistic median large-cap 10-K size or an outlier
  before weighting how urgent Finding A is.
- **Finding B (XBRL noise)**: worth its own small, separate investigation
  (which ingestion path produced this filing, whether it's specific to how
  this one 10-K was ingested or systemic) — not scoped or sized here.
- **Sequencing**: per CTO's breakdown, Changes (M15) is next.
