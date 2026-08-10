# M8 Acquisition-State Architecture Risk Review

**Status:** 🟡 **ARCHITECTURE INVESTIGATION — NOT AN IMPLEMENTATION
AUTHORIZATION.** This is a read-only investigation and risk-register
artifact. No backend, frontend, schema, migration, or dependency file
was created or modified to produce it.
**Date:** 2026-08-10
**Scope:** investigates whether an approved canonical acquisition-state
source exists for M8, and registers the architectural risks that would
otherwise surface mid-implementation. Does not reopen any decision
already made in Document 32 or Document 33.
**Does not modify:** `32_M8_Pre_Implementation_Decision_Pack.md`,
`33_M8_Financials_API_Contract_Review.md`, `30_ADR_Proposal_M8_Financial_Statements_Data_Model.md`,
any production code, any test, any schema, any migration.

---

## 1. Executive Summary

## 🟡 Requires Architecture Decision

**No approved canonical acquisition-state source exists anywhere in this
repository — not in code, not in a ratified schema, not as a designed
mechanism.** This was intentional at every prior review stage (ADR-029
§4/§8/§18, Document 32 §4, Document 33 §4) — the concept was decided,
the mechanism was explicitly deferred each time. That deferral is now
the single blocking dependency for M8 endpoint implementation.

This is not rated 🔴 **Blocked** in the sense of "no viable path exists."
The gap is narrow, well-scoped, and does not require new infrastructure
(§7 proposes a minimum decision using only patterns already present in
this codebase). It is rated 🟡 because a specific, boundable architecture
decision — not yet made — must be reviewed and approved before
implementation can safely begin. Until that decision is approved, **M8
endpoint implementation cannot proceed** without an implementer either
inventing the mechanism ad hoc (explicitly prohibited by Document 32 §4
and Document 33's own implementation gate) or silently collapsing
acquisition state back onto `FinancialStatement` absence (the exact
regression Document 33 Round 3 already corrected once).

One additional finding not previously surfaced: **Document 32 §4 and
Document 33 §3.2 describe acquisition-state granularity at two different
grains** (period-level vs. statement-type-level) — see R10, §6 and §8.
This must be resolved as part of the same architecture decision, not
separately.

## 2. Authoritative Decisions

Summarized only where relevant to this investigation — nothing below
reopens either document.

**From Document 32 §4 (Data Availability / Acquisition State Semantics):**
- Three states: `not_yet_acquired`, `available`, `confirmed_unavailable`.
- `FinancialStatement data ≠ Acquisition lifecycle state` — architecturally
  separate concepts, decided as a boundary, not a schema.
- Evaluated "per `(ticker, period_type, period_end, statement_type)`
  combination — the same identity ADR-029 §8 already fixed for the
  statement document itself" (period-level wording — see R10).
- Storage mechanism explicitly **not** designed: "a field on a (possibly
  minimal) placeholder document, a separate small tracking structure, or
  something else is an implementation-time modeling choice."
- Explicitly rejected: inferring state from `FinancialStatement` absence
  alone.

**From Document 33 (API Contract, approved):**
- `acquisition_state` appears once per `statement_type` inside the
  response envelope (`statements.<type>.acquisition_state`), not once
  per period (§3.2).
- The endpoint is read-only — must not synchronously call yfinance, must
  not trigger acquisition itself (§4).
- The implementation gate (added in the prior governance-correction
  round): endpoint implementation must not begin by inventing an
  acquisition-state mechanism; either an already-approved architecture or
  a separately approved architecture decision must supply the canonical
  source first.

**From ADR-029 §8/§18:**
- Statement-document identity/unique index:
  `{ ticker, period_type, period_end, statement_type }` — decided, not
  reopened here.
- Cold-start acquisition path and refresh mechanism both explicitly
  **not designed** — direction only (serve-then-refresh-async for
  existing data; "controlled initial acquisition path" for cold start).
- No Redis caching proposed for this domain (RA-0/RA-1 cited directly).

## 3. Existing Repository Evidence

Inspected directly, not inferred from documentation:

- **`grep -ri acquisition backend/`** → **zero matches** in any Python
  source file. The word appears only in `docs/`.
- **`grep -ri "FinancialStatement\|financial_statement" backend/`** →
  **zero matches** anywhere except `requirements.txt`/`server.py`/
  `agents/ingest.py`/tests matching on the unrelated substring
  `yfinance` (false positive from the grep pattern) — there is no
  `FinancialStatement` model, repository, or collection anywhere in the
  codebase yet.
- **`backend/domain/models.py`** — the only lifecycle/state-machine
  entity in the codebase today is `Job`/`JobStatus`
  (`queued|running|completed|failed|cancelled`), explicitly scoped as
  "the one entity every future capability needs" for **request-scoped,
  Redis-resident, TTL'd** work (research/Learning pipeline jobs). Its
  `JobStore` port (`application/ports.py`) ships a `reap()`/restart-sweep
  mechanism (`infrastructure/redis/job_store.py`) specifically because
  `Job` has a genuine **in-progress** state that can be orphaned by a
  crash — see R12.
- **`backend/application/ports.py`** — seven `Protocol`s exist
  (`JobStore`, `EventBus`, `RateLimiter`, `LLMClient`, `ChunkRepository`,
  `ReportLikeRepository`). No `FinancialStatementRepository` and no
  acquisition-state-shaped port exists yet — confirms ADR-029 §5's
  proposed repository has not been created (correctly — it isn't
  authorized).
- **`backend/agents/ingest.py`** — the one existing precedent for
  provider-failure handling: `fetch_bse_annual_report` and the yfinance
  fallback path both **return `None` on any failure** (timeout, 403,
  anti-bot block, empty payload, unexpected shape) with no distinction
  between "provider explicitly said no data" and "we couldn't reach the
  provider." This single-signal pattern is the opposite of what
  Document 32 §4's three-state model requires — it is not a reusable
  precedent for acquisition state, it is evidence of exactly the
  ambiguity the three-state model exists to avoid (see R5).
- **`backend/server.py:1034` (`db.reports.find_one(...).sort(created_at,-1)`)**
  — the only existing "is externally-derived data still usable"
  precedent, a plain Mongo query, no Redis, no status field — supports
  ADR-029 §8's citation of it as the freshness-comparison precedent.
- **No background job runner, worker, scheduler, or queue exists** —
  confirmed absent: no Celery, no cron entry, no `worker.py`, no
  scheduled-task infrastructure anywhere in `backend/`. The only
  "background-ish" execution today is `asyncio.to_thread` wrapping
  synchronous yfinance/PDF calls inline within a request (`agents/ingest.py`).
- **`docs/backend_engineering/09_Redis_Architecture.md` RA-0/RA-1**
  (directly inspected): "Redis is never the system of record" / "every
  key has a TTL or a bounded size" — binding invariants that rule out
  Redis as a persistent acquisition-state store, and rule out an
  unbounded distributed lock.
- **`backend/tests/contract/test_route_inventory.py`** — confirms the
  frozen-route-set contract-test pattern already exists in this
  codebase (relevant to R3's recommendation: an analogous safeguard
  could exist for acquisition-state once implemented, though none is
  proposed here).

## 4. Canonical Acquisition-State Source

**NO APPROVED CANONICAL ACQUISITION-STATE SOURCE EXISTS.**

This is confirmed by direct repository inspection (§3), not merely by
absence of documentation — there is no collection, no port, no adapter,
no placeholder, and no in-code reference to the concept anywhere in
`backend/`. Every prior document that touches this topic (ADR-029 §4/§8,
Document 32 §4, Document 33 §4) explicitly defers the mechanism rather
than silently assuming one. This review does not soften that conclusion
or propose working around it by inference from `FinancialStatement`
absence — both documents already forbid that, and this review agrees.

## 5. State Lifecycle Analysis

| Transition | Architecturally decided? | Mechanism specified? |
|---|---|---|
| `not_yet_acquired` → `available` | Yes, conceptually (Document 32 §4) | No — cold-start acquisition path is explicitly not designed (ADR-029 §8) |
| `not_yet_acquired` → `confirmed_unavailable` | Yes, conceptually — "a fetch was attempted and the provider explicitly returned nothing" (Document 32 §4, RELIANCE.NS precedent) | No — same undesigned trigger as above |
| `available` → refreshed `available` | Direction only ("serve-then-refresh-async") | No — mechanism and staleness threshold both explicitly open (ADR-029 §18 item 4) |
| any state → an **in-progress/attempting** state | **Not modeled at all** — the three-state vocabulary has no transitional state | N/A — see R12 |

The model is architecturally coherent as a *vocabulary* (three
non-overlapping, well-defined terminal-or-initial states), but it has
**zero transition triggers defined**. A state can be described; nothing
in the approved architecture can currently produce one. The absence of
an in-progress state is not itself a flaw — see R12's finding that this
is a favorable crash-safety property, provided the eventual source
writes state only on a definitive outcome.

## 6. Risk Register

| ID | Risk | Severity | Existing Mitigation | Gap | Recommendation |
|----|------|----------|---------------------|-----|-----------------|
| R1 | No canonical acquisition-state source exists to answer any of the three states | **Critical** | None — deferred by design at every prior stage | The endpoint has nothing to read from for `acquisition_state` today | Approve the minimum architecture decision (§7) before endpoint implementation begins |
| R2 | State-lifecycle transitions (cold start, refresh) have no defined trigger mechanism | Medium | ADR-029 §8 explicitly scopes both out — direction only, not silently missing | Cold-start trigger is undesigned; refresh is intentionally deferred further | Cold-start trigger must be part of §7's decision (minimum: a non-request-blocking initial-acquisition path); refresh may remain deferred — it doesn't block a correct v1 GET endpoint |
| R3 | `FinancialStatement` absence gets used as a substitute for acquisition state during implementation | **Critical** | Explicitly prohibited in Document 32 §4 and Document 33 §4/§5 | No enforcement mechanism (test, lint, or otherwise) stops an implementer from doing it anyway absent an approved alternative | Do not begin implementation until §7 is approved; consider a `test_route_inventory.py`-style regression guard once a source exists |
| R4 | Cannot distinguish "never encountered" from "known, not yet acquired" tickers | Low | Document 33 §5 row 5 already decides both collapse into `not_yet_acquired` by design, matching the `GET /filings` precedent | None — this is a decided simplification, not an open risk | No action needed |
| R5 | Three-state model has no distinct "transient failure" signal (timeout/network/rate-limit vs. provider-confirmed-empty) | Medium | `confirmed_unavailable`'s definition is already narrow — "explicitly returned nothing... not an exception, not a timeout" (Document 32 §4) | Nothing currently enforces that boundary in an implementation; existing `ingest.py` precedent (§3) conflates all failure modes into one `None` signal, which is the wrong pattern to reuse here | §7's failure-semantics rule must state explicitly: only a definitive provider outcome may write a terminal state; do not add a fourth client-visible state (would reopen Document 33) |
| R6 | Two concurrent acquisition attempts for the same combination could race | Medium | None exists — no acquisition code at all yet | Duplicate concurrent yfinance calls possible once a trigger exists | Rely on Mongo idempotent upsert + unique index (R7) to keep data correct; do not add a Redis lock — RA-0/RA-1 argue against Redis as a coordination system-of-record, and duplicate calls are a tolerable, bounded cost at current scale, not a correctness risk |
| R7 | Repeated acquisition could create duplicate `FinancialStatement` documents | Low | ADR-029 §8's unique compound index (`ticker+period_type+period_end+statement_type`) plus whole-document upsert already gives write idempotency for the persisted data — decided, sound | The acquisition-state record itself (once designed) needs the equivalent unique-index + upsert guarantee — not yet designed, because the record doesn't exist | Apply the identical index+upsert pattern to whatever acquisition-state record §7 defines |
| R8 | Partial statement-type availability (e.g. income available, cash flow confirmed-unavailable) might collapse into one company-wide state | Low | Document 33 §3.2 Example 2 already demonstrates exactly this scenario, grounded in real evidence (Document 31's RELIANCE.NS finding) | None identified — already correctly supported | No action needed |
| R9 | A statement might be incorrectly demoted from `available` because one metric is missing | Low | ADR-029 §6.1's "preserve unknown rows" design (`canonical_metric: null`, `provider_label`/`value`/`unit` retained) already decouples per-metric mapping gaps from statement-level acquisition state | None identified | No action needed |
| R10 | Acquisition-state granularity is described inconsistently — Document 32 §4 evaluates state "per `(ticker, period_type, period_end, statement_type)`" (period-level), while Document 33 §3.2 exposes exactly one `acquisition_state` per `statement_type` (aggregated across all periods) | **High** | None — neither document reconciles this | No aggregation rule exists for turning a period-level signal into the single field the frozen contract exposes, if period-level granularity is what's intended | Resolve explicitly in §7. This review recommends **statement-type-level** granularity — it matches the real provider call boundary (one `.financials`-style call returns all periods atomically) and requires no aggregation logic or contract change. See §8. |
| R11 | Stale data has no refresh mechanism defined | Low | ADR-029 §8/§18 item 4 already explicitly defers this as a known, tracked future dependency | None beyond what's already tracked | Continue treating as out of M8 v1 scope — the GET endpoint never triggers a refresh itself (Document 33 §4), so this does not block implementation |
| R12 | An acquisition attempt could be interrupted (crash, timeout, restart) and leave a permanently stuck or ambiguous state | Medium | The three-state model has **no in-progress state** — by shape, this is crash-safe *if* the eventual source writes state only on a definitive terminal outcome, never a separate "attempting" flag. This mirrors how `ingest.py`'s existing best-effort `None`-return already tolerates failures without persisting a bad state (§3) | This "write only on terminal outcome" invariant is implied by the model's shape but not yet a documented requirement anywhere | Make it an explicit requirement in §7 — the cheapest possible failure-recovery guarantee, and notably *not* the `JobStore.reap()`/restart-sweep pattern (§3), which exists only because `Job` has a genuine in-progress state that this model deliberately avoids |

## 7. Architecture Decision Required

The minimum decision needed answers exactly these questions — it does
not design the acquisition pipeline, a background worker, or any
implementation code:

1. **Source of truth:** a small, purpose-built persistent store —
   Mongo, matching every other non-ephemeral concept in this codebase.
   Not Redis (RA-0/RA-1 bar it as system of record for anything other
   than in-flight, TTL'd data). Not inferred from `FinancialStatement`
   absence (already prohibited).
2. **State ownership:** a boundary distinct from
   `FinancialStatementRepository` (ADR-029 §5) — e.g. a sibling
   `Protocol`-shaped port, matching the existing structural-typing
   convention in `application/ports.py` — keeping Document 32 §4's
   `FinancialStatement data ≠ Acquisition lifecycle state` separation
   architectural, not just conceptual.
3. **State granularity:** resolve R10 explicitly. This review recommends
   statement-type-level (matching the real provider call boundary and
   Document 33's existing response shape) over period-level, as the
   smaller model that needs no aggregation rule.
4. **Lifecycle semantics:** v1 needs only
   `not_yet_acquired → {available, confirmed_unavailable}`, triggered by
   a still-undesigned but now-scoped cold-start acquisition path.
   Refresh/staleness transitions remain deferred, per ADR-029 §18 item 4
   — unchanged by this review.
5. **Persistence boundary:** Mongo, shared-corpus, no `user_id` — same
   ownership model as `companies`/`filings`/`financial_statements`
   (`08` RI-5). No new trust boundary.
6. **Failure semantics:** only an unambiguous provider outcome may write
   a terminal state (success-with-data → `available`;
   success-with-explicit-empty-result → `confirmed_unavailable`). A
   transient failure (timeout, network error, rate limit, exception)
   must never write `confirmed_unavailable` and should leave the
   combination at `not_yet_acquired` (or write nothing at all) so it
   stays safely retryable — this is what makes R5 and R12 non-issues by
   construction.
7. **Concurrency/idempotency:** reuse the same mechanism ADR-029 §8
   already decided for `FinancialStatement` itself — a unique compound
   index (at whatever granularity #3 resolves to) plus an idempotent
   upsert. No distributed lock, no Redis lock, no queue is required for
   v1 — a rare duplicate concurrent acquisition attempt wastes one extra
   yfinance call at worst; it cannot corrupt persisted state.

Nothing above specifies a field name, a collection name, a class, or any
code. It is a decision checklist, not a design document.

## 8. API Contract Compatibility

**Compatible, with one dependency.** If the granularity question (R10)
is resolved as statement-type-level per this review's recommendation,
the identified/proposed acquisition-state architecture requires **no
change** to Document 33 — the existing `statements.<type>.acquisition_state`
field is already exactly the right shape to receive a statement-type-level
signal.

**The one incompatibility risk:** if a future decision instead resolves
R10 as period-level (matching Document 32 §4's literal wording), Document
33's response contract would need an aggregation rule (e.g., "report the
most conservative state across periods") that neither document currently
defines. This review does not resolve that case and does not modify
Document 33 to address it — it is flagged here as the reason R10 must be
settled explicitly as part of §7, not left implicit.

## 9. Implementation Gate

M8 financials endpoint implementation may begin only when **all** of the
following are true:

1. A canonical acquisition-state source architecture (§7's seven
   questions) has been reviewed and approved — either because an
   already-approved architecture is found to supply it (none currently
   is, per §4) or because a new, minimal architecture decision is made
   and approved.
2. That architecture includes, at minimum, a defined cold-start
   acquisition trigger — without it, every ticker/statement combination
   remains permanently `not_yet_acquired` and the endpoint has nothing
   real to report, even though its read-only contract would technically
   still be satisfiable.
3. The granularity question (R10) is explicitly resolved, so the
   acquisition-state source's key shape and Document 33's response
   field are known to align (§8).

Until all three hold, implementation must not proceed, and an
implementer must not substitute `FinancialStatement` absence or any
other inferred signal for the missing source (R3).

## 10. CTO Recommendation

## 🟡 Separate architecture decision required

The API contract (Document 33) is sound and is not reopened by this
review. The data-model architecture (Document 32/ADR-029) is sound and
is not reopened either. What remains is a single, well-scoped gap this
review confirms has never been designed: the canonical acquisition-state
source itself. §7 shows this does not require new infrastructure class
(no Redis, no queue, no worker system) — it requires the same pattern
this codebase already uses for `FinancialStatement` (a small Mongo
collection, a `Protocol` port, a unique-index upsert). M8 implementation
remains correctly gated until that decision is reviewed and approved;
it is not blocked by a deeper or unresolvable architectural conflict.

---

*Companion documents:
[`32_M8_Pre_Implementation_Decision_Pack.md`](32_M8_Pre_Implementation_Decision_Pack.md) §4 (acquisition-state semantics, unmodified) ·
[`33_M8_Financials_API_Contract_Review.md`](33_M8_Financials_API_Contract_Review.md) (API contract, unmodified) ·
[`30_ADR_Proposal_M8_Financial_Statements_Data_Model.md`](30_ADR_Proposal_M8_Financial_Statements_Data_Model.md) §4/§8/§18 (ratified architecture, unmodified) ·
[`09_Redis_Architecture.md`](09_Redis_Architecture.md) RA-0/RA-1 (cited, unmodified).*

*This is an architecture-review artifact. It does not authorize schema
changes, migrations, dependency changes, provider integration, or
endpoint implementation.*
