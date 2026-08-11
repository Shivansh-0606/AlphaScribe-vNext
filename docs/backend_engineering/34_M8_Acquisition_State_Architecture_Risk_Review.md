# M8 Acquisition-State Architecture Risk Review

**Status:** 🟡 **ARCHITECTURE INVESTIGATION — SEPARATE ARCHITECTURE
DECISION REQUIRED.** This is a read-only investigation and
decision-input artifact. It does **not** authorize implementation and
does **not** itself approve the acquisition-state architecture. No
backend, frontend, schema, migration, or dependency file was created or
modified to produce it.
**Date:** 2026-08-10
**Scope:** investigates whether an approved canonical acquisition-state
source exists for M8, and registers the architectural risks that would
otherwise surface mid-implementation. Does not reopen any decision
already made in Document 32 or Document 33.
**Does not modify:** `32_M8_Pre_Implementation_Decision_Pack.md`,
`33_M8_Financials_API_Contract_Review.md`, `30_ADR_Proposal_M8_Financial_Statements_Data_Model.md`,
any production code, any test, any schema, any migration.

> **Revision, Round 2 — CTO-directed governance correction (2026-08-10):**
> the CTO reviewed Round 1 and issued **🟡 APPROVED WITH CHANGES**. The
> investigation, the verified repository evidence, and the R1–R12 risk
> analysis are all accepted — specifically the findings that no approved
> canonical acquisition-state source exists, that R1 is a genuine
> implementation blocker, R3 a critical regression risk, R5 in need of
> explicit failure-semantics treatment, R10 a genuine Document 32 /
> Document 33 inconsistency, and R12 in need of an explicit
> failure/recovery invariant. What this revision corrects: Round 1's §7
> presented specific architectural choices (Mongo as the store,
> statement-type-level granularity, a particular repository/port and
> persistence model) in prescriptive language that read as an already-
> chosen solution. **None of those is approved.** §7 is restructured into
> Required Decisions / Recommended Direction / Out-of-Scope; the
> granularity question is restored to an open CTO decision with its
> alternative preserved; R5's transient-failure boundary and R12's
> terminal-state invariant are both restated as proposed rather than
> settled; the acquisition-state architecture is explicitly separated
> from acquisition *orchestration*; and a new §11 Decision Boundary makes
> the approved / not-yet-approved / out-of-scope split unambiguous. No
> risk severity was changed, no verified evidence was removed, and no
> decision in Document 32 or Document 33 was reopened.
>
> **Revision, Round 3 — CTO-directed final corrections
> (2026-08-10):** corrected R12 so the proposed terminal-state
> persistence invariant is treated as a new architecture requirement
> rather than being inferred from the existing `ingest.py` `None`-return
> behavior; aligned the M8 implementation gate with all seven required
> architecture decisions in §7.A; and clarified that the architecture
> investigation is 🟡 while M8 implementation remains 🔴 blocked until
> the separate acquisition-state architecture decision is approved.
>
> **Revision, Round 4 — CTO-directed precision correction
> (2026-08-10):** clarified that the proposed terminal-state invariant
> materially mitigates R12 and provides a persistence safeguard for R5,
> but does not by itself resolve provider-outcome classification, which
> remains a separate architecture decision.

---

## 1. Executive Summary

**ARCHITECTURE STATUS: 🟡 Separate architecture decision required.**

**IMPLEMENTATION STATUS: 🔴 M8 implementation is blocked until that
architecture decision is explicitly approved.**

These are two distinct statuses. The 🟡 describes the architecture
investigation — the gap is understood, bounded, and resolvable. It is
**not** permission to begin implementing M8, which remains 🔴 blocked
until the separate acquisition-state architecture decision is approved
(§9).

## 🟡 Requires Architecture Decision

**No approved canonical acquisition-state source exists anywhere in this
repository — not in code, not in a ratified schema, not as a designed
mechanism.** This was intentional at every prior review stage (ADR-029
§4/§8/§18, Document 32 §4, Document 33 §4) — the concept was decided,
the mechanism was explicitly deferred each time. That deferral is now
the single blocking dependency for M8 endpoint implementation.

This is not rated 🔴 **Blocked** in the sense of "no viable path exists."
The gap is narrow, well-scoped, and appears resolvable without new
infrastructure (§7.B sets out a recommended direction using only
patterns already present in this codebase — a recommendation, not a
selected architecture). It is rated 🟡 because a specific, boundable
architecture decision — not yet made — must be reviewed and approved
before implementation can safely begin. Until that decision is approved, **M8
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
an in-progress state is not itself a flaw — it means no crash can strand
the public state in an `in_progress` value, though on its own that
guarantees nothing about correct persistence semantics (R12).

## 6. Risk Register

| ID | Risk | Severity | Existing Mitigation | Gap | Recommendation |
|----|------|----------|---------------------|-----|-----------------|
| R1 | No canonical acquisition-state source exists to answer any of the three states | **Critical** | None — deferred by design at every prior stage | The endpoint has nothing to read from for `acquisition_state` today | *Required decision (§7.A):* the acquisition-state architecture must be reviewed and approved before endpoint implementation begins. This document does not itself supply or approve it |
| R2 | State-lifecycle transitions (cold start, refresh) have no defined trigger mechanism | Medium | *Existing decision:* ADR-029 §8 explicitly scopes both out — direction only, not silently missing | Cold-start trigger is undesigned; refresh is deferred further still | *Required decision (§7.A.4)* covers only which state transitions are **valid** — the *representation* question. **Who triggers acquisition is orchestration (§7.C), a separate architectural concern**, and this review does not design it. Refresh remains deferred (R11) and does not block a correct v1 read-only GET endpoint |
| R3 | `FinancialStatement` absence gets used as a substitute for acquisition state during implementation | **Critical** | *Existing decision:* explicitly prohibited in Document 32 §4 and Document 33 §4/§5 | No enforcement mechanism (test, lint, or otherwise) stops an implementer from doing it anyway absent an approved alternative | *Required decision (§7.A.1):* do not begin implementation until the acquisition-state architecture is approved. *Recommendation (not a required decision):* once a source exists, a `test_route_inventory.py`-style regression guard could pin the invariant — offered as an option for the implementing decision to consider, not specified here |
| R4 | Cannot distinguish "never encountered" from "known, not yet acquired" tickers | Low | *Existing decision:* Document 33 §5 row 5 already decides both collapse into `not_yet_acquired` by design, matching the `GET /filings` precedent | None — this is a decided simplification, not an open risk | No action needed. Non-blocking |
| R5 | Three-state model has no distinct "transient failure" signal (timeout/network/rate-limit/exception/malformed response vs. provider-confirmed-empty) | Medium | *Existing decision:* `confirmed_unavailable`'s definition is already narrow — "explicitly returned nothing... not an exception, not a timeout" (Document 32 §4) | Nothing currently enforces that boundary in an implementation; the existing `ingest.py` precedent (§3) conflates every failure mode into one `None` signal, which is the wrong pattern to reuse here | *Required decision (§7.A.5):* a provider timeout, network failure, rate-limit, exception, or malformed/unusable response **must not** become `confirmed_unavailable` — only a definitive provider outcome may establish it. The **public** three-state vocabulary is unchanged and stays exactly as Document 33 froze it; **do not introduce a fourth public `acquisition_state`.** The architecture decision must separately determine whether *internal* acquisition history needs to distinguish "never attempted" from "attempted but inconclusive" (§7.A.7) — an internal-representation question, not an API-contract one |
| R6 | Two concurrent acquisition attempts for the same combination could race | Medium | None exists — no acquisition code at all yet | Duplicate concurrent provider calls possible once a trigger exists | *Required decision (§7.A.6):* the architecture must settle how duplicate attempts are prevented from corrupting state. *Recommendation:* an idempotent-upsert-plus-unique-key approach (R7) keeps persisted data correct without coordination; **do not automatically introduce a Redis or distributed lock** — RA-0/RA-1 argue against Redis as a coordination system-of-record, and a duplicate call is a bounded waste, not a correctness failure |
| R7 | Repeated acquisition could create duplicate `FinancialStatement` documents | Low | *Existing decision:* ADR-029 §8's unique compound index (`ticker+period_type+period_end+statement_type`) plus whole-document upsert already gives write idempotency for the persisted statement data — decided, sound, **preserved unchanged by this review** | The acquisition-state record itself (once designed) needs an equivalent idempotency guarantee — not yet designed, because the record doesn't exist | *Required decision (§7.A.6):* whatever acquisition-state representation is chosen must carry an equivalent idempotency guarantee at whatever key shape §7.A.3 resolves to. This review identifies idempotency as a decision requirement only — it does **not** specify an index, key, or schema |
| R8 | Partial statement-type availability (e.g. income available, cash flow confirmed-unavailable) might collapse into one company-wide state | Low | *Existing decision:* Document 33 §3.2 Example 2 already demonstrates exactly this scenario, grounded in real evidence (Document 31's RELIANCE.NS finding) | None identified — already correctly supported | No action needed. Non-blocking |
| R9 | A statement might be incorrectly demoted from `available` because one metric is missing | Low | *Existing decision:* ADR-029 §6.1's "preserve unknown rows" design (`canonical_metric: null`, `provider_label`/`value`/`unit` retained) already decouples per-metric mapping gaps from statement-level acquisition state | None identified | No action needed. Non-blocking |
| R10 | Acquisition-state granularity is described inconsistently — Document 32 §4 evaluates state "per `(ticker, period_type, period_end, statement_type)`" (period-level), while Document 33 §3.2 exposes exactly one `acquisition_state` per `statement_type` (aggregated across all periods) | **High** | None — neither document reconciles this | No aggregation rule exists for turning a period-level signal into the single field the frozen contract exposes, if period-level granularity is what's intended | *Required decision (§7.A.3) — must be resolved explicitly by the CTO, not chosen automatically.* Statement-type-level is this review's **recommended direction** (§7.B); period-level remains technically possible per Document 32's stated identity, and if selected requires a separate aggregation rule that this review does **not** invent. See §8 |
| R11 | Stale data has no refresh mechanism defined | Low | *Future/deferred concern:* ADR-029 §8/§18 item 4 already explicitly defers this as a known, tracked dependency | None beyond what's already tracked | Continue treating as out of M8 v1 scope — the GET endpoint never triggers a refresh itself (Document 33 §4), so this does not block implementation. Refresh belongs to acquisition *orchestration* (§7.C), not to the acquisition-state decision |
| R12 | An acquisition attempt could be interrupted (crash, timeout, restart) and leave a permanently stuck or ambiguous state | Medium | The public acquisition-state vocabulary deliberately contains **no client-visible `in_progress` state**. A crash therefore cannot leave the canonical *public* state permanently stuck in an `in_progress` state — there is no such state to strand. **This does not, by itself, guarantee correct persistence semantics** | Nothing yet governs *when* a terminal state may legitimately be written. The current repository has no canonical acquisition state at all (§4), so it offers no established persistence semantics to inherit — this requirement must be established by the architecture decision, not derived from existing behavior | **PROPOSED INVARIANT — REQUIRES ARCHITECTURE APPROVAL** (§7.A.5/§7.B): "Acquisition state should only be persisted as a terminal state after a definitive outcome. An interrupted or transient attempt must not leave the canonical state permanently representing successful acquisition or confirmed unavailability." This is a **new architecture requirement to be considered by the decision**, not an existing architectural decision and not an inference from any current code path. Note also that it is *not* the `JobStore.reap()`/restart-sweep pattern (§3), which exists only because `Job` has a genuine in-progress state the public model here deliberately avoids. **Two separate facts must not be conflated: (a) current repository behavior does not implement canonical acquisition state at all; (b) the future architecture must prevent transient or interrupted attempts from incorrectly persisting terminal states.** (a) is an observation about today; (b) is a requirement for tomorrow — neither establishes the other |

## 7. Architecture Decision Required

This section is a **decision checklist and a recommendation — not a
selected architecture.** Nothing in §7.B has been approved. The three
subsections below are deliberately kept distinct: what must be decided
(§7.A), what this review suggests as a starting position (§7.B), and
what is not part of this decision at all (§7.C).

### 7.A — Required decisions

The acquisition-state architecture decision must explicitly settle all
seven of the following. None is resolved by this document.

1. **Source of truth.** Where canonical acquisition state lives; whether
   it is persistent; and whether it is a store separate from
   `FinancialStatement` data. (Constraint carried forward, already
   decided elsewhere: it must not be inferred from `FinancialStatement`
   absence — Document 32 §4, Document 33 §4/§5.)
2. **State ownership.** Which architectural boundary owns acquisition
   state. It must remain distinct from `FinancialStatement` persistence
   semantics, per Document 32 §4's `FinancialStatement data ≠
   Acquisition lifecycle state` boundary. Whether that distinctness is
   expressed as a separate port, a separate adapter, or another
   structure is part of the decision, not presupposed here.
3. **State granularity.** Explicitly resolve the Document 32 vs.
   Document 33 mismatch (R10) by deciding whether acquisition state is
   (a) **period-level** or (b) **statement-type-level**. **This choice
   must not be made automatically.** If period-level is selected, the
   decision must also define how period-level state maps onto Document
   33's single statement-level `acquisition_state` field (§8).
4. **Lifecycle semantics.** Define the precise meaning of
   `not_yet_acquired`, `available`, and `confirmed_unavailable`, and
   which transitions between them are valid. No additional
   client-visible state may be introduced unless a separate
   API-contract decision is approved — Document 33's three-state public
   contract is frozen.
5. **Failure semantics.** Explicitly distinguish these provider
   outcomes: successful acquisition with data; provider-confirmed
   empty/unavailable result; timeout; network failure; provider rate
   limiting; provider exception; and malformed/unusable provider
   response. **Only a definitive provider outcome may establish
   `confirmed_unavailable`** — a transient failure must not. This
   changes nothing about Document 33's three-state public contract; it
   governs how a state is legitimately arrived at.
6. **Idempotency and concurrency.** Determine how duplicate acquisition
   attempts are prevented from corrupting state. ADR-029's existing
   `FinancialStatement` identity decision (`ticker + period_type +
   period_end + statement_type`) is preserved unchanged and is not
   reopened. Redis or distributed locks must **not** be introduced
   automatically — if the decision concludes coordination is genuinely
   required, that is itself a reviewable choice, not a default.
7. **Internal acquisition-attempt history.** Explicitly decide whether
   the *internal* architecture needs to distinguish: never attempted;
   attempted and inconclusive; successfully acquired; and definitively
   unavailable. This is an internal-representation question — it does
   not add a public state (§7.A.4/R5). If the distinction is deemed
   unnecessary for v1, the decision must document **why** rather than
   leaving it unaddressed.

### 7.B — Recommended architectural direction (pending CTO approval)

**Everything in this subsection is a recommendation only. None of it is
an approved or selected architecture.**

**Persistence candidate.** Mongo is the preferred *candidate* for the
acquisition-state store, because: Mongo is already the persistence
system for durable domain data in this codebase; `09` RA-0/RA-1
prohibit using Redis as a system of record; a durable acquisition-state
concept should not be inferred from `FinancialStatement` absence; and
the existing application architecture already uses repository ports
(`application/ports.py`), so a durable state concept has a conventional
home. **Mongo has not been selected.** This review deliberately does
not name a collection, define a schema, specify field names, or specify
indexes — idempotency is identified as a *decision requirement*
(§7.A.6), not designed here.

**Granularity.** Statement-type-level granularity is the current
recommended direction because it aligns with the frozen Document 33
response shape and the apparent provider call boundary. However, this
remains a CTO architecture decision. Period-level granularity remains
technically possible because Document 32 describes the acquisition-state
identity at `(ticker, period_type, period_end, statement_type)`. If
period-level is selected, a separate aggregation rule is required to
populate Document 33's statement-level `acquisition_state` — **this
review does not invent that rule** (§8).

**Terminal-state invariant (proposed, requires approval).** "Acquisition
state should only be persisted as a terminal state after a definitive
outcome. An interrupted/transient attempt must not leave the canonical
state permanently representing successful acquisition or confirmed
unavailability." If adopted, this invariant materially mitigates R12 and provides an
important persistence safeguard for R5; the provider-outcome
classification required by R5 remains a separate architecture
decision. It is proposed, not approved.

**Concurrency.** An idempotent-upsert-plus-unique-key approach appears
sufficient without any lock, since a rare duplicate attempt wastes one
extra provider call rather than corrupting state. Offered as a starting
position for §7.A.6, not as a settled mechanism.

### 7.C — Out of scope / separate decisions

**The canonical acquisition-state decision does not, by itself, design
the complete acquisition orchestration system.** These are two distinct
architectural concerns and must not be conflated:

| Acquisition-**state** architecture (§7.A) | Acquisition **orchestration** (separate) |
|---|---|
| How state is represented | Who triggers acquisition |
| Who owns it | How provider calls execute |
| How it is persisted | Worker/background execution |
| How it is read | Retry scheduling |
| | Refresh |
| | Provider routing |

Orchestration is a separate architectural concern unless an approved
decision explicitly requires it. **This document does not design
workers, queues, Redis jobs, schedulers, refresh pipelines, an
acquisition endpoint, or provider routing** — and the acquisition-state
decision in §7.A should not either. Cold-start triggering, in
particular, belongs to orchestration (R2), not to the state
representation question.

## 8. API Contract Compatibility

**Document 33 is frozen. The acquisition-state architecture must conform
to Document 33 — not the reverse.** Neither this review nor the
subsequent architecture decision may modify the API contract to
accommodate a persistence choice.

Compatibility therefore depends entirely on how §7.A.3 resolves:

- **If statement-type-level state is selected:** it maps **directly**
  onto the existing response shape — `statements.<type>.acquisition_state`
  is already exactly the right shape to receive a statement-type-level
  signal. No contract change, no aggregation logic, no additional
  architecture work.
- **If period-level state is selected:** an aggregation rule is required
  to collapse per-period state into the single statement-level field the
  frozen contract exposes. **That rule is not yet defined**, and this
  review deliberately does not invent it. Selecting period-level
  therefore **requires additional architecture work before
  implementation** — it is a viable option, but a more expensive one.

This asymmetry is precisely why R10 must be settled explicitly rather
than left implicit. Document 33 is not modified by this review in
either case.

## 9. Implementation Gate

M8 financials endpoint implementation may begin **only after all seven**
required architecture decisions in §7.A are explicitly approved — one
gate item per required decision:

1. **Canonical acquisition-state source of truth approved** (§7.A.1) —
   either because an already-approved architecture is found to supply it
   (none currently is, per §4) or because a new, minimal architecture
   decision is made and approved.
2. **State ownership approved** (§7.A.2) — the boundary that owns
   acquisition state, distinct from `FinancialStatement` persistence.
3. **State granularity approved** (§7.A.3), so the acquisition-state key
   shape and Document 33's response field are known to align (§8).
4. **Terminal/lifecycle semantics approved** (§7.A.4) — the meaning of
   each of the three states and which transitions are valid.
5. **Transient failure semantics approved** (§7.A.5) — in particular
   that a timeout, network failure, rate limit, exception, or malformed
   response cannot establish `confirmed_unavailable`.
6. **Idempotency and concurrency behavior approved** (§7.A.6).
7. **Internal acquisition-attempt history explicitly decided**
   (§7.A.7). Approval here may take either form: internal attempt
   history is designed and approved, **or** the CTO explicitly decides
   that no internal attempt history is required for v1. What is not
   acceptable is leaving this silently unresolved.

**This gate deliberately does not require approval of refresh, caching,
Redis, or a full worker/orchestration architecture** (§7.C). Those are
separate concerns and would only enter this gate if the
acquisition-state decision itself turned out to depend on one of them —
which, on the evidence in this review, it does not appear to.

Until all seven hold, implementation must not proceed, and an
implementer must not substitute `FinancialStatement` absence or any
other inferred signal for the missing source (R3).

## 10. CTO Recommendation

## 🟡 Separate architecture decision required

The API contract (Document 33) is sound and is not reopened by this
review. The data-model architecture (Document 32/ADR-029) is sound and
is not reopened either. What remains is a single, well-scoped gap this
review confirms has never been designed: the canonical acquisition-state
source itself. On the evidence gathered, resolving it appears not to
require a new class of infrastructure (no Redis, no queue, no worker
system) — §7.B sets out why, **as a recommendation pending approval, not
as a selected architecture.**

**The investigation has identified the missing architectural dependency,
but Document 34 does not itself approve the implementation of that
dependency.**

**The next artifact should be a focused M8 Acquisition-State
Architecture Decision. It must resolve the seven required decisions
identified in §7.A before M8 implementation begins.**

## 11. Decision Boundary

### Approved

- Document 32's architecture decisions remain approved and unchanged.
- Document 33's API contract remains approved and unchanged.
- The three public acquisition states (`not_yet_acquired`, `available`,
  `confirmed_unavailable`) remain approved.
- `FinancialStatement` absence must not determine acquisition state.
- `GET /companies/{ticker}/financials` remains read-only.

### Not yet approved

- The acquisition-state persistence mechanism.
- Mongo as the selected store (a recommendation only — §7.B).
- Statement-level vs. period-level granularity (§7.A.3/R10).
- Any acquisition-state repository or port.
- Internal acquisition-attempt history (§7.A.7).
- Any concrete state-transition implementation.

### Explicitly out of scope

- Acquisition worker architecture.
- Queue architecture.
- Redis coordination.
- Refresh scheduling.
- Provider routing.
- An acquisition endpoint.
- M8 implementation.

---

*Companion documents:
[`32_M8_Pre_Implementation_Decision_Pack.md`](32_M8_Pre_Implementation_Decision_Pack.md) §4 (acquisition-state semantics, unmodified) ·
[`33_M8_Financials_API_Contract_Review.md`](33_M8_Financials_API_Contract_Review.md) (API contract, unmodified) ·
[`30_ADR_Proposal_M8_Financial_Statements_Data_Model.md`](30_ADR_Proposal_M8_Financial_Statements_Data_Model.md) §4/§8/§18 (ratified architecture, unmodified) ·
[`09_Redis_Architecture.md`](09_Redis_Architecture.md) RA-0/RA-1 (cited, unmodified).*

*Document 34 is an architecture-risk investigation and decision-input
artifact. It does not authorize implementation and does not itself
approve the acquisition-state architecture.*

*It does not authorize schema changes, migrations, dependency changes,
provider integration, or endpoint implementation.*
