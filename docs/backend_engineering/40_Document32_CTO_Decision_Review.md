# Document 32 — CTO Decision Review

**Status:** 🔵 **REVIEW — NOT AN APPROVAL.** This document evaluates
Document 32 against the actual repository and the already-ratified/
approved M8 architecture chain (Documents 33's POST amendment, 34, 35,
36, 38) and Document 39's readiness assessment. It does not itself
approve, ratify, or modify Document 32, 35, or 38, does not create a
schema, collection, migration, or endpoint, and does not authorize
implementation.
**Date:** 2026-08-11
**Reviewed document:** [`32_M8_Pre_Implementation_Decision_Pack.md`](32_M8_Pre_Implementation_Decision_Pack.md)
(full text read directly for this review).

---

## 1. Objective

Determine whether Document 32's three still-open items — the
`financial_statements` collection name, the complete `FinancialStatement`
field set, and the decision pack as a whole — are ready for explicit CTO
approval: internally consistent, implementation-safe, and compatible with
everything ratified since Document 32 was written.

## 2. Item 1 — `financial_statements` Collection Name

**Finding: consistent, no issue found.** Document 32 §2.A recommends
`financial_statements`, matching this repository's existing collection-
naming convention exactly — plural, snake_case, no prefix
(`companies`, `filings`, `filing_chunks`, `reports`, `jobs`,
`explanations`, `explanation_jobs`, per `backend/infrastructure/mongo/indexes.py`).
No existing collection uses this name; no naming collision. Direct
inspection of `backend/infrastructure/mongo/indexes.py` confirms
`financial_statements` does not yet exist — this would be a genuinely new
collection, consistent with Document 32's own "no collection exists yet"
framing and Document 38 §7's "net-new collection, not a migration"
conclusion.

## 3. Item 2 — Complete `FinancialStatement` Field Set

**Finding: substantively sound; one confirmed textual inconsistency
requires correction before approval (see §5).**

The field-level decisions (§2.B-D) are well-evidenced and internally
consistent:
- `ticker`, `period_type`, `period_end`, `statement_type`, `currency`,
  `source`, `fetched_at` match existing repository conventions (ISO-8601
  date/datetime strings, never native BSON `Date` — matches `08` §4's
  universal convention, verified against existing collections).
- `fiscal_year` as an AlphaScribe-derived, not provider-observed,
  normalization is clearly specified and unambiguous.
- The per-metric `unit` enum (replacing document-level `scale`, which was
  correctly removed for lacking provider-guaranteed evidence) is a sound,
  evidence-driven correction from the original proposal.
- `period_duration`'s omission is justified by Document 31's spike
  evidence (no TTM-labeled columns observed), not by nothing having been
  checked.
- The five-step canonical-vocabulary governance process (observe →
  identify → validate → approve → promote) is a reasonable, low-risk
  process description — it does not invent a new department or approval
  bureaucracy, only names who owns an already-implied review
  responsibility. This is not blocking, but is worth a `00_README.md`
  cross-reference at some future point since no other numbered document
  formally charters "the Backend & AI architecture/data-governance review
  process" by that name — a minor documentation-findability note, not a
  substantive gap.

No field-set item found here contradicts Document 33's frozen `GET`/
`POST` contracts, Document 36's orchestration model, or Document 38's
MongoDB provider decision.

## 4. Item 3 — Internal Consistency and Implementation Safety of the Pack as a Whole

**Finding: NOT fully internally consistent as currently written — one
confirmed, material inconsistency exists between Document 32 §4 and the
now-ratified acquisition-state architecture (Document 35 §6).** Detailed
in §5.

Everything else in the pack is internally consistent: the
`FinancialStatement` vs. acquisition-lifecycle-state boundary Document 32
§4 establishes ("`FinancialStatement data ≠ Acquisition lifecycle
state`") is exactly the boundary Document 35 AS-0/AS-1 build on and is
correctly honored throughout the downstream chain. The three-state model
(`not_yet_acquired` / `available` / `confirmed_unavailable`) matches
Document 33's frozen outcome enumeration exactly, with no fourth state
invented anywhere.

## 5. Dependency on Document 35 — Confirmed Inconsistency Requiring Amendment

This is the substantive finding of this review, verified by direct
reading of both documents, not inferred:

**Document 32 §4 states, as a "Recommended" position:**
> "a minimal three-state acquisition status, evaluated per `(ticker,
> period_type, period_end, statement_type)` combination — the same
> identity ADR-029 §8 already fixed for the statement document itself"

This is a **four-field, period-level** granularity for the
*acquisition-state* identity — one acquisition-state record per
`period_end`, matching the `FinancialStatement` document's own identity.

**Document 35 §6 ("R10 — Granularity Decision") explicitly rejects
exactly this option**, after a full comparative evaluation against
company-level and statement-type-level alternatives:
> "**Period-level is rejected** — not because it is impossible, but
> because it requires inventing an aggregation rule this document has no
> evidence to define, and it doesn't correspond to any real,
> independently-executable provider operation."

Document 35 adopts a **three-field, statement-type-level** identity
instead — `(ticker, period_type, statement_type)`, explicitly *without*
`period_end` — and states plainly that this is a deliberate correction of
Document 32's own wording:

> "This resolves R10 definitively: **the granularity mismatch Document
> 34 flagged between Document 32 §4's wording and Document 33's response
> shape** is closed by choosing the grain Document 33 already assumes."

This is not a novel finding of this review — it is Document 34's R10
risk (classified **High** severity, "must be resolved explicitly by
CTO"), which Document 35 §6 already closed. The problem is that
**Document 32's own text was never amended to reflect that closure.**
Document 32 §4, its "Interaction with other decided architecture"
subsection, Summary Table item 10, and the corresponding "Implementation
Blockers Remaining" bullet all still describe the superseded period-level
recommendation as if it were current.

**Confirmed downstream impact:** Document 36 (ratified orchestration
architecture) does not reference `period_end` anywhere and is unaffected.
Document 38 (ratified MongoDB provider decision) consistently uses the
three-field `(ticker, period_type, statement_type)` identity throughout,
correctly following Document 35 §6 rather than Document 32 §4. **Only
Document 32's own text is stale** — every other document in the chain
already reflects the correct, current architecture.

**Why this matters for approval, not just as a note:** Document 32 is
about to receive explicit CTO approval per this governance sequence.
Approving it with §4's superseded language intact would formally ratify
text that contradicts binding, already-ratified architecture (Document
35 §6) — the exact "stale text presented as current" problem this entire
governance sequence has repeatedly had to catch and correct in Documents
33, 38, and 39. A reader consulting Document 32 alone, without
cross-referencing Document 35, would be misled about the acquisition-
state identity's actual shape.

**This does not require new architecture or a new decision** — Document
35 §6 already made the real decision, with full reasoning. It requires
only that Document 32's own record be brought into agreement with it.

## 6. Compatibility Checks

| Dependency | Result |
|---|---|
| Document 33 approved `POST .../acquire` contract | ✅ Compatible. The three-state model and statement-type framing Document 32 established is exactly what Document 33's outcome enumeration (`not_yet_acquired`/`available`/`confirmed_unavailable`/`mixed`) already assumes. |
| Document 36 orchestration architecture | ✅ Compatible. No reference to `period_end` or period-level granularity anywhere in Document 36 — unaffected by the §5 finding. |
| Document 38 MongoDB canonical provider | ✅ Compatible, and itself already correctly uses the statement-type-level identity Document 35 §6 adopted — reinforces that §5's finding is isolated to Document 32's own text. |
| Existing MongoDB architecture (`08`) | ✅ Compatible. Collection-naming convention, ISO-8601 date-string convention, and the `m0006` migration-number recommendation are all still accurate — `08` §11's migration table (verified directly) still lists only `m0001`-`m0005`; `m0006` remains unclaimed. |
| Existing Company Research implementation | ✅ No conflict. `FinancialsSection.tsx` currently renders an unrelated single-period LLM-extracted snapshot; Document 32 doesn't touch frontend and nothing it proposes collides with existing frontend behavior. |
| Existing financial-data implementation (`backend/agents/ingest.py`) | ✅ No conflict. The three existing fetchers (`fetch_edgar_latest`, `fetch_yfinance`, `fetch_bse_annual_report`) implement none of Document 32's proposed persistence yet — this remains genuinely new work, as Document 32 itself states. |

## 7. Required Amendments

**Amendment 1 (required before approval):** Update Document 32 §4's
"Recommended" acquisition-status identity from `(ticker, period_type,
period_end, statement_type)` to `(ticker, period_type, statement_type)`,
citing Document 35 §6's resolution of Document 34's R10. Correspondingly
update:
- The "Interaction with other decided architecture" subsection in §4
  (cold-start / freshness discussion currently assumes the period-level
  framing).
- Summary Table item 10 ("Data-availability/acquisition state") to note
  the granularity was subsequently fixed by Document 35 §6, not left for
  future implementation.
- The "Implementation Blockers Remaining" bullet for acquisition-state
  semantics, which currently says only "the implementation mechanism is
  intentionally unspecified" — it is no longer fully unspecified;
  Document 35 §6 fixed the identity granularity specifically.

This is a textual synchronization, not a new architectural decision —
Document 35 §6 already made and justified the actual decision.

No other amendments are required. Items 2 and 3 (collection name, field
set) are sound as written.

## 8. Verdict

### APPROVE WITH REQUIRED AMENDMENTS

Document 32's substantive decisions — collection name, field set,
currency/unit model, restatement policy, migration numbering, BSE/NSE v1
strategy, canonical-vocabulary governance, and the `FinancialStatement`-
vs-acquisition-state boundary — are evidence-based, internally sound, and
compatible with every document ratified since Document 32 was written.
The one required amendment (§7) is a narrow textual correction bringing
Document 32 §4's already-superseded acquisition-status granularity
language into agreement with Document 35 §6's later, explicit resolution
of the same question — not a reopening of any decision, not a new design
question, and not something this review resolves itself (per this task's
explicit instruction not to modify Document 32).

---

*Companion documents: [`32_M8_Pre_Implementation_Decision_Pack.md`](32_M8_Pre_Implementation_Decision_Pack.md)
(reviewed, unmodified) · [`34_M8_Acquisition_State_Architecture_Risk_Review.md`](34_M8_Acquisition_State_Architecture_Risk_Review.md)
(R10, unmodified) · [`35_M8_Acquisition_State_Architecture_Decision.md`](35_M8_Acquisition_State_Architecture_Decision.md)
§6 (unmodified) · [`36_M8_Acquisition_Orchestration_Architecture.md`](36_M8_Acquisition_Orchestration_Architecture.md)
(unmodified) · [`38_M8_Canonical_Acquisition_State_Provider_Decision.md`](38_M8_Canonical_Acquisition_State_Provider_Decision.md)
(unmodified) · [`39_M8_Implementation_Readiness_Assessment.md`](39_M8_Implementation_Readiness_Assessment.md)
(unmodified) · `backend/infrastructure/mongo/indexes.py`,
`docs/backend_engineering/08_MongoDB_Data_Architecture.md` §11
(repository evidence cited above, unmodified).*

*This is a review artifact. It does not itself approve Document 32, does
not create a schema, collection, migration, or endpoint, and does not
authorize implementation.*
