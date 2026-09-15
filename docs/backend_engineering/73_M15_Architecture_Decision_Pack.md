# 73 — M15 Architecture Decision Pack — C-4 "What Changed Since Last Review"

**Status:** 🟠 **M15 ARCHITECTURE DECISION PACK — DRAFT / PENDING CTO
REVIEW (REVISION R1).** This document determines *how* the CTO-ratified M15 = C-4 API
contract ([Document 70, Revision R4](70_M15_What_Changed_API_Contract_Proposal.md),
ratified by [Document 72](72_Document70_R4_CTO_Ratification_Record.md))
should be architecturally realized. It does **not** build it, and it does
**not** redefine the contract. **It is not ratified. It does not authorize
implementation, commit, or push** — each is a separate, subsequent CTO act
(§27).

**Type:** Architecture design artifact (documentation only — no source
code, test, schema, migration, index, route, LangGraph node, MongoDB
collection, Redis usage, or provider change created or modified to produce
it).

**Governance chain:** Document 67 (recommendation, 🟢 ratified) → Document
68 (selection, 🟢 ratified via Document 69) → Document 69 (selection
ratification, 🟢 ratified) → Document 70 R1→R4 (API contract, 🟢 ratified
via Document 72) → Document 71 (a blocked ratification review of Document
70, historical — superseded by Document 72's successful ratification, not
modified here) → Document 72 (Document 70 R4 ratification, 🟢 ratified) →
**this document (73) — architecture proposal, not yet ratified.**

**Date:** 2026-09-06.

**Revision R1 (2026-09-06) — targeted architecture correction following
CTO review, pre-ratification.** CTO review result: **NOT YET APPROVED FOR
RATIFICATION — AH-2's DEPLOYMENT INVARIANT AND AH-1's OUTPUT BOUND REQUIRE
EXPLICIT STATEMENT.** This revision: (1) makes AH-2's process-locality an
explicit, stated **deployment invariant** rather than a deferred
operational concern — a completed result is retrievable only from the
backend process that computed it, a process restart can legitimately
discard it, and a `GET` (or SSE `final` frame) routed to a different
process cannot retrieve it; M15's supported execution model is therefore
explicitly single-backend-process for the `POST → completion → GET`
lifecycle, with horizontal multi-instance support for this lifecycle
explicitly out of scope and left to a future, separate architecture
decision (§12, §15, §21, §25); (2) clarifies that the existing
`RedisEventBus` SSE transport being cross-process-capable for raw
trace-event delivery does **not** lift this invariant, because the SSE
`final` frame's payload is still constructed from the same process-local
result buffer (§12.2); (3) states that `report`-mode's generated item list
is bounded in principle — by the same fixed 2-report evidence payload
`report`-mode's evidence retrieval already bounds, and by the single
`chat_json` call's own output-token budget — without fixing a new hard
numeric cap, which remains an implementation-level decision (§10, §11); (4)
adds explicit architecture-level test requirements for the deployment
invariant (same-process GET, expiration, post-restart unavailability,
unsupported cross-instance behavior, and SSE under the same invariant)
(§22); (5) reframes §25's contract-impact conclusion to distinguish
Document 70's internal coherence from the fact that AH-2's chosen mechanism
introduces a deployment invariant that must be stated to realize `POST →
GET` correctly — without proposing any change to Document 70. **No scope
change beyond corrections 1–5. No new infrastructure (Redis, MongoDB,
sticky sessions, or otherwise) is introduced. No API-contract field is
added or altered — Document 70 is not reopened. Status unchanged: 🟠 DRAFT
/ PENDING CTO REVIEW. NOT RATIFIED. Does not authorize implementation,
commit, or push.**

**Structural precedent (cited, unmodified):**
[65_M14_Filing_Analysis_Architecture_Decision_Pack.md](65_M14_Filing_Analysis_Architecture_Decision_Pack.md)
(the most recent Architecture Decision Pack — its section skeleton, its
open-question decision format, and its persistence-fallback-chain reasoning
are reused here), and the M9.1/M14 implementations themselves
(`agents/comparison_explanation.py`, `agents/filing_analysis.py`,
`server.py`'s async-job route families) as the concrete, shipped precedent
this pack builds on rather than reinvents.

---

## 0. What This Document Is and Is Not

**Is:** an architecture proposal for C-4 — the end-to-end request flow, the
`period` and `report` comparison engines, resolutions for Document 70's
AH-1 and AH-2 architecture-handoff items, the LLM/orchestration/persistence
boundary, the API/job execution model, validation/error/security/
observability/performance architecture, and a testing strategy. Structured
after Document 65.

**Is not:** a redefinition of the API contract (Document 70 R4 is treated
as frozen input, §5); an implementation; a commit or push authorization; a
MongoDB schema/collection/index/migration; a Redis realization; a LangGraph
change; a frontend implementation; a resolution of Document 70's six Open
Contract Decisions (they remain contract-level, owed to a future CTO
decision, not an architecture one — §24); a reopening of Documents 67–72; a
promotion of C-2; an introduction of Durable Research Sessions, Filing Q&A,
or general research-history semantics.

---

## 1. Metadata and Provenance

| Field | Value |
|---|---|
| Document number | 73 |
| Title | M15 Architecture Decision Pack — C-4 "What Changed Since Last Review" |
| Milestone | M15 = C-4 (Document 68 §4; Document 72 §5) |
| Governance stage | Architecture proposal — first draft, pre-CTO-review |
| Predecessor gate | Document 72 — Document 70 R4 CTO Ratification Record (🟢 CTO-RATIFIED, 2026-09-06) |
| Successor gate (not created here) | Architecture ratification, then a separate implementation-authorization decision |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Governance Status

🟠 **M15 ARCHITECTURE DECISION PACK — DRAFT / PENDING CTO REVIEW.**

```text
Doc 70 R4 (API contract)         🟢 CTO-RATIFIED (Document 72)
  ↓
Doc 73 (THIS) — architecture     🟠 PROPOSAL — pending CTO review
  ↓
Architecture ratification        NOT YET PERFORMED
  ↓
Implementation authorization     NOT AUTHORIZED
  ↓
Implementation / commit / push   NOT AUTHORIZED
```

This document performs exactly one act: **drafting an architecture
proposal for CTO review.** It does not perform, and does not imply, any
later stage.

---

## 3. Executive Architecture Summary

C-4 is realized as a **fifth async-job-backed AI/data surface**, structurally
identical in shape to the four that already exist (Research, Learning,
Comparison-Explanation, Filing Analysis): one new `JobKind` enum member,
one new route family under `/api/companies/{ticker}/changes` (already
fixed by Document 70 §10.1), and one top-level orchestration function that
branches on `comparison_type` into two independent, domain-specific
engines:

- **`period` mode** is **pure, deterministic, LLM-free** computation over
  two existing `financial_statements` rows — a new dependency-free module
  in the tradition of `agents/scoring.py`.
- **`report` mode** is **one bounded LLM call** over two existing `reports`
  documents, reusing `agents/comparison_explanation.py`'s evidence
  extraction and citation-validation machinery, with a **new, structured,
  list-shaped output schema** (this pack's resolution of AH-1) rather than
  a text-decomposition heuristic.

**No new persistence, no new caching layer, no LangGraph involvement, and
no new job protocol are introduced.** Job-result retention (AH-2) reuses
the M14 in-process, TTL-bounded buffer pattern rather than a new durable
collection — **this carries an explicit deployment invariant**: a
completed result is retrievable only from the one backend process that ran
the job, and horizontal multi-instance deployment for the `POST → GET`
lifecycle is explicitly outside M15's supported execution model (§12.1).
The two comparison engines share only the outer orchestration shell (job
lifecycle, route handlers, response envelope, error mapping) —
their domain logic stays separate, mirroring the existing
`scoring.py`-vs-`comparison_explanation.py` separation already established
in this codebase.

---

## 4. Scope and Non-Goals

**In scope:** the architecture needed to realize Document 70 R4's `period`
and `report` modes, including AH-1, AH-2, orchestration, LLM boundary,
persistence, job execution, validation, error handling, security,
observability, performance, and testing strategy.

**Explicit non-goals** (this pack must not, and does not):

- implement C-4;
- prescribe concrete code structure beyond what architecture requires
  (module names are proposed as architecture-level decisions, not fully
  specified implementations);
- create database schemas or migrations;
- define production deployment;
- authorize implementation, commit, or push;
- resolve unrelated M14 limitations;
- promote C-2 (Structured Filing-Section Extraction);
- introduce Durable Research Sessions;
- broaden C-4 into Filing Q&A;
- broaden C-4 into a general research-history feature.

---

## 5. Authoritative Contract Constraints (Document 70, Revision R4 — frozen input)

This pack treats the following as **fixed and non-negotiable** — inspected
directly from Document 70 R4 this session, not modified:

- **Exactly two mutually exclusive modes** — `period` (financial) and
  `report` (narrative); a single request evaluates exactly one; no
  combined mode; no third, filing-to-filing mode in v1 (OCD-1, still
  open — not architecture's to resolve).
- **Comparison points are explicit, caller-supplied `baseline`/`current`
  identifiers** — no implicit "last user visit," no session history, no
  Durable Research Sessions, in any form.
- **Financial metric identity** is `Metric.provider_label`, exact-match
  only; `Metric.canonical_metric` is `null` for every metric today; no
  canonical-vocabulary mapping is invented.
- **Financial eligibility**: any nonzero delta or appearing/disappearing
  metric qualifies — no magnitude threshold (OCD-6, still open).
- **Financial citation shape**: `{index, statement_type, period_end,
  metric}`.
- **Narrative eligibility**: substantive semantic difference, a discrete
  expressible claim, grounded in report evidence on **both** sides — no
  materiality threshold.
- **Narrative citation shape**: `{index, report_id, field}`, and **every
  narrative item must cite at least one source from each of** `baseline`
  and `current`.
- **The two citation shapes are distinct and must not be merged.**
- **State vocabulary**: `complete` / `partial` / `insufficient_evidence`,
  defined per mode (§13, §14 of Document 70).
- **No new MongoDB collection, index, schema, or migration is required or
  proposed by the contract**; no particular retention mechanism is
  selected by the contract (AH-2).
- **Route family** (already fixed at the contract level, §10.1):
  `POST/GET/GET-stream/POST-cancel` under
  `/api/companies/{ticker}/changes`; create response always `200
  {id, status: "queued", reused: false}`; SSE `final` is a `node ==
  "final"` value inside a normal `data:` frame, not a new event type.
- **Error taxonomy**: zero new error classes — the existing nine-class
  `domain/errors.py` taxonomy only.
- **`prompt_version: string | null`** — `null` for `period` mode, a real
  version string for `report` mode.
- **BYOK/SSRF boundaries** reused verbatim.
- **AH-1 and AH-2** are explicitly handed to this architecture phase — this
  pack's job is to resolve them (§11, §12).

Nothing below overrides any of the above. Where this pack proposes a
mechanism, it is chosen to satisfy these constraints, never to relax them.

---

## 6. Existing-System Dependencies / Reuse

| Component | File / location | Reused for C-4 |
|---|---|---|
| Async job lifecycle | `backend/application/jobs.py` (`JobLifecycle`: `start/mark_running/publish/complete/fail/cancel/get/is_past_deadline/reap_stale`) | Reused unmodified — C-4 becomes a fifth caller. |
| Job admission control | `backend/application/ports.py` (`JobStore.active_count()`); `InMemoryJobStore` / `RedisJobStore` (`backend/infrastructure/redis/job_store.py`) | Reused unmodified — one shared `MAX_ACTIVE_JOBS` budget across every kind, "deliberately not parameterized by kind." |
| `JobKind` enum | `backend/domain/models.py:20-24` | Extended by exactly one new member (§16), matching the M9.1/M14 precedent of a one-line additive change. |
| Event bus / SSE | `backend/infrastructure/redis/event_bus.py` (`InMemoryEventBus` / `RedisEventBus`, Redis Streams `XADD`/`XREAD`, never `XREADGROUP`); `backend/infrastructure/streaming/sse.py` (`sse_response()`) | Reused unmodified — no new streaming mechanism. |
| Comparison / citation engine | `backend/agents/comparison_explanation.py` (`build_evidence_payload`, `build_prompt`, `compute_identity_key`, `validate_and_map_citations`, `generate_explanation`) | `build_evidence_payload` reused unmodified for `report` mode; citation-validation *logic* reused, extended per-item (§11). |
| LLM access | `backend/agents/llm.py` (`chat_text`/`chat_json` only) | Reused unmodified — no direct provider SDK calls. |
| Deterministic, dependency-free computation precedent | `backend/agents/scoring.py` | Style precedent for the new `period`-mode financial-delta module (§10) — stdlib-only, no LLM. |
| Financial domain model | `backend/domain/financials.py` (`Metric`, `FinancialStatement`, `PeriodType`, `StatementType`) | Read-only reuse — no schema change. |
| Error taxonomy | `backend/domain/errors.py` (9 classes); `backend/app/api/errors.py` (`domain_error_handler`) | Reused unmodified — zero new classes (§18). |
| Observability | `backend/infrastructure/observability/{tracing,metrics,logging}.py` | Reused conventions: `pipeline.<capability>` root span, `<capability>_runs_total{outcome}` counter pattern, correlation-id logging (§20). |
| Job-result retention precedent | `backend/server.py:2289-2326` (`_FILING_ANALYSIS_RESULTS`, in-process TTL buffer) | Adopted as the AH-2 resolution (§12) — not a new mechanism. |
| Evaluation framework | `backend/evaluation/golden_dataset/`, `backend/evaluation/adapters/comparison_explanation.py`, `backend/evaluation/self_consistency/` | Reused pattern for a new `change_brief` surface/adapter (§22). |
| LangGraph pipeline | `backend/agents/graph.py` (frozen per `07_LangGraph_Architecture.md` 🔒 v1.0) | **Not touched.** Neither `comparison_explanation.py` nor `filing_analysis.py` import `agents.graph`; C-4 follows the same out-of-graph precedent (§14). |

No file in this table is modified by this document.

---

## 7. Context and Architectural Problem

Document 70 R4 fixes *what* C-4 must do; it explicitly hands two questions
to this phase:

- **AH-1**: `report` mode requires a list of discrete, independently
  cited narrative items, each grounded on both sides — but the only
  existing engine that could produce a narrative comparison
  (`comparison_explanation.py`) emits **one** narrative block with **one**
  shared citation list. Producing the contractually-required shape from
  that engine's current output is not a trivial reuse; it requires either
  a schema extension or a decomposition step.
- **AH-2**: a completed job's result must be retrievable via `GET` after
  `POST` completes, but the contract explicitly declines to select a
  retention mechanism, only constraining that it must not become a
  durable, cross-request, per-user comparison-history store.

Beyond these two named items, this phase must also decide the LLM
boundary, orchestration style, job execution model, and the usual
validation/error/security/observability/performance/testing architecture —
all while introducing the least new surface area the contract allows,
consistent with every prior milestone's discipline in this repository.

---

## 8. End-to-End Architecture

```text
Client
  │  POST /api/companies/{ticker}/changes  {comparison_type, ...}
  ▼
[1] Request validation           FastAPI + Pydantic discriminated request model
  │  (comparison_type-conditional required fields; §10.2 rules)
  ▼
[2] Admission control            JobLifecycle.start(kind=CHANGE_BRIEF, ...)
  │  (shared MAX_ACTIVE_JOBS budget — no new gate)
  ▼
[3] 200 {id, status: "queued", reused: false}   ← synchronous return to caller
  │
  ▼  (background asyncio task)
[4] Input / reference resolution
  │    period:  resolve two financial_statements rows (ticker, period_type,
  │             statement_type, period_end) — independent existence checks
  │    report:  resolve two reports rows (id, ticker, ownership) —
  │             independent per-id authorization + ticker match (§9.4)
  ▼
[5] Data retrieval                (already-persisted data only — no acquisition trigger)
  ▼
[6] Comparison (mode-specific, §10/§11)
  │    period:  pure deterministic delta computation — no LLM
  │    report:  one chat_json call against a structured list schema
  ▼
[7] Evidence / citation construction
  │    period:  self-evidencing, built alongside the delta computation
  │    report:  per-item citation validation, both-sides check (§11)
  ▼
[8] Validation / state determination
  │    → complete | partial | insufficient_evidence   (§14.1 / §14.2 mapping)
  ▼
[9] Response assembly             shared envelope: {ticker, comparison_type,
  │                                baseline, current, created_at, prompt_version,
  │                                schema_version, items[], state, coverage_boundaries}
  ▼
[10] JobLifecycle.complete()  + in-process result buffer store (AH-2, §12)
  │
  ▼
GET .../{id}  or  GET .../{id}/stream  →  client retrieves the completed result
```

Steps 1–3 and 9–10 are **shared** across both modes (the orchestration
shell, §13). Steps 4–8 branch into two independent, domain-specific
engines (§10, §11) that never call into each other and share no comparison
logic — only the surrounding shell and the citation-validation *style*
(not code) are common.

---

## 9. `period` Financial Architecture

**New module (proposed name):** `backend/agents/change_brief_financial.py`
— pure, dependency-free, stdlib-only, in the tradition of
`agents/scoring.py`. No `chat_*` import, no I/O.

- **Reference resolution**: given `(ticker, period_type, statement_type,
  baseline_period_end, current_period_end)`, resolve the two
  `financial_statements` rows via the **existing** financial-statements
  read port (the same repository call `server.py`'s
  `GET /companies/{ticker}/financials` already uses) — no new port, no new
  query shape. Each side resolved and existence-checked **independently**
  (missing → 404, per Document 70 §9.4/§15).
- **Financial data retrieval**: two `FinancialStatement` documents, each
  already carrying `metrics: list[Metric]` and `currency`.
- **Metric alignment**: build two `dict[provider_label, Metric]` maps, one
  per side. Alignment is by exact `provider_label` string equality only —
  no fuzzy matching, no canonical mapping (§5).
- **Change computation**: the pure function implements Document 70 §8.2's
  eligibility table exactly — `changed`/`new`/`removed` classification,
  `absolute_delta`, `percent_delta` (null on zero/absent baseline), a
  same-label-different-`unit` exclusion feeding `coverage_boundaries`, and
  a whole-comparison `currency` mismatch short-circuiting to
  `insufficient_evidence`. This function is the single place all of
  Document 70 §8.2's rules are encoded — nowhere else.
- **Evidence generation / citation construction**: not a separate step —
  each computed item's `sources[]` (`{index, statement_type, period_end,
  metric}`) is built by the same function from the two resolved
  `FinancialStatement` identities, since the citation *is* the computation
  input, not a separate grounding claim to validate.
- **Citation "validation"**: there is no runtime LLM-trust boundary to
  guard here — "validation" for this path means the pure function's own
  invariants (asserted by unit tests, §22), not a request-time grounding
  check. No `validate_and_map_citations`-style step applies to `period`
  mode, and none should be added — that machinery exists to guard against
  a model's untrustworthy citation claims, and no model is involved.
- **Missing-data behavior**: an existing `financial_statements` row with
  `metrics: []` → `insufficient_evidence`; a resolved-but-`currency`-
  mismatched pair → `insufficient_evidence`; a resolved pair where some
  metrics have unit conflicts → `partial`, others still returned.
- **Provider-label limitations**: Document 70 §8.2 already fully documents
  and accepts this limitation (a relabeled line item reads as one removed
  + one new metric). **This architecture does not attempt to solve it** —
  doing so would require a canonical-metric-mapping system the contract
  explicitly declines to invent (§5). No governance issue is raised here;
  Document 70 already anticipated and accepted this exactly.

**Decision record — financial engine shape:**

1. **Decision**: implement `period`-mode comparison as one pure,
   synchronous function with no external dependencies.
2. **Context/problem**: the contract requires a mechanical, deterministic
   delta computation with no LLM and no invented ontology.
3. **Options considered**: (a) a pure stdlib function (à la
   `agents/scoring.py`); (b) a small class-based "comparison engine" with
   pluggable strategies; (c) delegating to a generic diff library.
4. **Chosen approach**: (a).
5. **Why**: the computation is a bounded, well-specified set operation over
   two flat metric maps — no polymorphism, no extensibility requirement
   exists today, and a pure function is trivially unit-testable and
   trivially proven deterministic.
6. **Tradeoffs**: none material — a class or library would add indirection
   with no corresponding capability gain.
7. **Consequences**: the module has zero runtime dependencies beyond the
   domain model it reads; it can be fully covered by unit tests with no
   fixtures beyond in-memory `FinancialStatement` objects.
8. **What remains unresolved**: OCD-2 (significance label) and OCD-6
   (magnitude filter) are contract-level questions this function's
   interface should not preclude adding later, but does not implement now.

---

## 10. `report` Narrative Architecture

**New module (proposed name):** `backend/agents/change_brief_narrative.py`.

- **Report identity / retrieval**: reuse the **query pattern** (not the
  exact function) of `_resolve_authorized_reports`
  (`{"id": {"$in": [...]}, "$or": [{"user_id": user_id}, {"is_sample":
  True}]}`), **extended with a `"ticker": ticker` filter clause** — the
  existing helper is ticker-agnostic (M9.1's compare/explain is a general
  N-report comparison), while Document 70 §9.4 requires C-4's report
  references to belong to the path ticker. This is a small, compatible
  extension of an existing query shape, not a new resolution mechanism.
  Both `baseline_report_id` and `current_report_id` are checked
  independently — one authorized, one not → 404 (§9.4), matching the
  existing `test_compare_one_valid_one_invalid_returns_404` precedent.
- **Relevant narrative evidence selection**: `build_evidence_payload`
  (`comparison_explanation.py`), reused **unmodified**, called with
  exactly `[baseline_report, current_report]` — the function already
  supports 2–4 reports, so a 2-report call requires no signature change.
- **Baseline/current grounding — AH-1 resolution**: see §11.
- **Change extraction**: the one `chat_json` call (§11) produces the list
  of candidate claims directly — there is no separate "extraction" step
  distinct from generation, matching the existing one-call-per-surface
  precedent (M9.1, M14).
- **Evidence construction**: each item's `sources[]` (`{index, report_id,
  field}`) is built by mapping the model's declared 1-based
  `report_number` (1 = baseline, 2 = current, matching the evidence
  payload's own ordering) to the real `report_id` — the model is never
  trusted with a real id, exactly as `comparison_explanation.py` already
  does.
- **Citation validation**: per item, reuse `validate_and_map_citations`'s
  core rejection logic (duplicate/undeclared/unconfirmed indices), **plus
  a new both-sides check**: an item is dropped (not emitted) unless its
  cited set includes at least one index mapping to `report_number == 1`
  and at least one mapping to `report_number == 2`. A dropped item never
  surfaces — it either reduces the returned list (if other items remain
  eligible) or, if it empties the list entirely with zero eligible items
  found at all, contributes to the `insufficient_evidence` determination
  (§14.2).
- **Missing/insufficient evidence behavior**: matches Document 70 §14.2
  exactly (see §5).
- **Output-list bound (not literally unbounded)**: the number of items a
  single `report`-mode response can contain is bounded **in principle** by
  two existing, already-established constraints — (a) the same fixed
  2-report `build_evidence_payload` bound this path already inherits from
  `comparison_explanation.py` (a finite, structured evidence input, not an
  open-ended one), and (b) the single `chat_json` call's own output-token
  budget, which mechanically caps how many discrete items the model can
  emit in one response. Neither of these is a new architectural mechanism;
  both already exist today. This pack does **not** fix a new, separate
  hard numeric cap on item count — doing so is an implementation-level
  decision (e.g., a defensive `max_items` truncation if operational
  experience ever shows the natural bounds above are insufficient), not an
  architecture decision, and no existing part of this codebase's
  architecture establishes such a cap for any comparable list-shaped LLM
  output today. No new Document 70 field is introduced to carry such a
  cap.

**AH-1 decision record — narrative `items[]` transformation mechanism:**

1. **Decision**: extend the model-output schema to emit a **list** of
   discrete claim objects directly, rather than decomposing a single
   generated narrative after the fact.
2. **Context/problem**: `comparison_explanation.py`'s existing
   `ComparisonExplanationSchema` returns one narrative string with one
   shared `sources[]`/`cited_source_indices` pair and a `limitations[]`
   list. Document 70 requires a list of items, each independently
   satisfying the eligibility rule (§8.3) and each carrying its **own**
   both-sides citation set — information a single shared citation list
   cannot represent.
3. **Options considered**:
   (a) **Structured schema extension** — add a new Pydantic schema (e.g.
   `ChangeBriefNarrativeSchema{items: list[ChangeBriefNarrativeItemSchema
   {summary, explanation, cited_source_indices: list[int]}]}`) and a new
   prompt instructing the model to emit discrete, both-sides-grounded
   claims meeting the §8.3 eligibility criteria directly, validated via
   `chat_json` exactly like every existing structured-output call in this
   codebase.
   (b) **Deterministic post-generation decomposition** — call
   `generate_explanation` unmodified, then heuristically split the
   returned narrative (by sentence or paragraph) into "items," inferring
   each item's citations from which `[n]` markers fall within its span.
   (c) **Two-pass**: generate the narrative as today, then a second LLM
   call to restructure it into items.
4. **Chosen approach**: (a).
5. **Why**: this codebase's own established convention — for every
   existing structured-output surface (`ComparisonExplanationSchema`,
   `FilingAnalysisSchema`'s per-output narrative) — is to ask the model for
   exactly the shape needed and validate it deterministically afterward,
   never to infer structure from free text after the fact. Option (b) is
   fragile: sentence/paragraph boundaries do not reliably align with
   "one discrete claim," and inferring per-item citation ownership from
   marker position in decomposed text is exactly the kind of brittle
   text-heuristic this codebase avoids elsewhere. Option (c) doubles LLM
   cost and latency for a problem a single well-specified schema already
   solves. Option (a) also directly gives per-item citations for free
   (the model states which indices support each item), which (b) cannot
   do reliably.
6. **Tradeoffs**: option (a) requires a new prompt (adapted from, not
   identical to, `comparison_explanation.py`'s existing one) and a new
   schema — marginally more new surface area than "reuse as-is," but this
   surface area is exactly what Document 70 §8.3/§21 already anticipated
   and required ("an additive transformation or schema extension").
7. **Consequences**: `change_brief_narrative.py` depends on
   `comparison_explanation.py` only for `build_evidence_payload` (data
   shaping) — it does not call `generate_explanation` or reuse
   `ComparisonExplanationSchema`, since those are shaped for the single-
   narrative case. The per-item citation-validation logic is a genuinely
   new function, though it reuses `validate_and_map_citations`'s
   duplicate/undeclared-rejection logic as a building block rather than
   reimplementing it.
8. **What remains unresolved**: the exact prompt wording and the model
   tier (`DEFAULT_LIGHT_MODEL` vs. a heavier tier) are implementation
   details, not architecture decisions, and are left to implementation
   time; OCD-5 (whether a §20.1-style validation gate applies) remains a
   separate, contract-level open question this pack does not resolve.

**Evidence-coverage-gap detection (`partial` state, §14.2).** The new
schema retains a `limitations: list[{topic, missing_side}]`-shaped field
(analogous to, but not identical to, `ComparisonLimitationSchema`) as
**one input signal**, not the sole authority: the architecturally
authoritative signal for `partial` is the **combination** of (a) at least
one item successfully validated as eligible and both-sides-cited, and (b)
at least one candidate topic the model names in `limitations` that could
not be corroborated on both sides. This keeps the contract's own framing
intact — Document 70 §14.2/§22.1 AH-1 explicitly requires the *externally
observable* evidence-coverage condition to be the authority, with
`limitations[]`-style data as an internal detail the architecture is free
to use or not.

---

## 11. AH-1 Decision (restated for clarity)

**AH-1 — RESOLVED (architecture level; does not amend Document 70).**
`report`-mode `items[]` is produced by a **structured schema extension** —
a new prompt and a new Pydantic output schema requesting discrete,
both-sides-grounded claims directly from the model — not by deterministic
decomposition of the existing single-narrative output. Full reasoning:
§10's decision record. This resolves the mechanism Document 70 §22.1
explicitly left open; it does not change any externally observable
contract behavior. The resulting item list is bounded in principle, not
literally unbounded — by the fixed evidence-payload size and the model's
own output-token budget (§10) — with no new hard numeric cap fixed by this
pack.

---

## 12. AH-2 Decision (job-result retention)

1. **Decision**: adopt the **M14 in-process, TTL-bounded, best-effort
   result buffer** pattern (`server.py:2289-2326`'s
   `_FILING_ANALYSIS_RESULTS` precedent) for C-4's job-result retention. No
   new MongoDB collection is proposed.
2. **Context/problem**: a completed job's result must be retrievable via a
   later `GET`, but Document 70 §16/AH-2 declines to select a mechanism,
   requiring only that whatever is chosen not become a durable,
   cross-request, per-user comparison-history store.
3. **Options considered**:
   (a) the M14 in-process TTL-bounded dict (fixed entry ceiling,
   oldest-first eviction, not surviving a restart, not shared across
   instances);
   (b) the M9.1 pattern — durable storage of the full result in a Mongo
   collection (`comparison_explanation_jobs`), retrievable indefinitely by
   job id + owner check;
   (c) a Redis-backed result cache (new key pattern on the existing Redis
   infrastructure, TTL-bounded).
4. **Chosen approach**: (a).
5. **Why**: (a) requires **zero new schema, collection, index, or
   migration governance** — fully avoiding any MongoDB realization
   question, which this task is not authorized to trigger. (b), even
   though it reuses an *existing* collection's pattern, would require a
   **new** collection for C-4's own result shape, which is exactly the
   kind of change Document 70 §16 states is "a new decision requiring the
   normal `08_MongoDB_Data_Architecture.md` + ADR governance chain" — not
   something this architecture pack can pre-approve for itself. (c) adds a
   new Redis usage (a cache) where Document 65's own OAQ-6 precedent
   already reasoned that new AI-artifact capabilities should add no new
   caching layer, and no operational evidence exists that C-4 needs one.
   (a) is also the most recent, most directly analogous precedent — a
   fifth async-job surface behaving exactly like the fourth.
6. **Tradeoffs**: (a) does not survive a process restart and does not work
   across multiple backend instances — a known, explicit ceiling, not a
   silent gap.
7. **Consequences**: a `_CHANGE_BRIEF_RESULTS: dict[str, tuple[str, dict,
   float]]` module-level buffer (mirroring `_FILING_ANALYSIS_RESULTS`'s
   shape exactly: `job_id -> (user_id, changes_payload, expires_at)`),
   bounded by the same style of fixed entry ceiling and TTL, marked with a
   `ponytail:`-style comment naming the ceiling and the upgrade path (the
   Document 70 AH-2-referenced durable-store option, gated on separate
   schema governance) — exactly matching the existing marker convention
   at `server.py:2289-2296`.
8. **What remains unresolved**: if a future multi-instance deployment or
   measured operational need requires durable or cross-instance result
   retention, that is a **new, separate architecture decision** requiring
   the normal schema-change governance — not decided, and not
   pre-authorized, here.

### 12.1 Deployment invariant this decision requires (explicit, non-negotiable)

The mechanism chosen above is **process-local, bounded, TTL-limited,
transient job-result retention** — not a database, and not a cache in the
shared, cross-process sense. Stated precisely, so implementation and
testing cannot accidentally assume otherwise:

- A completed job's result is held only in the memory of the **one backend
  process** that ran the job. It is retrievable via `GET` — or delivered
  via the SSE `final` frame, §12.2 below — **only from that same
  process**, only while the entry remains in its bounded buffer (before
  eviction) and before its TTL expires.
- **A process restart legitimately and unrecoverably discards the
  result.** This is not a defect to remediate later — it is the accepted,
  intended behavior of the chosen mechanism, identical to the M14
  precedent already running in production (`be4949b`).
- **A `GET` request routed to a different backend process than the one
  that ran the job cannot retrieve the result.** The buffer is an
  in-process Python dict, not a shared or replicated store; no
  cross-process lookup path exists for it, regardless of which `JobStore`/
  `EventBus` backend (`memory` or `redis`) is configured for job
  *status* (§16) — job status and job *result payload* are retained by two
  different mechanisms with two different scopes (§12.2).
- **Therefore: M15's supported deployment model is single-backend-process
  for the `POST → job completion → GET` lifecycle.** This pack does
  **not** introduce process affinity, sticky sessions, a shared cache, or
  any other cross-instance mechanism to satisfy horizontal scaling — doing
  so would be a new infrastructure decision this pack is not authorized to
  make. Instead, this pack **explicitly declares horizontal multi-instance
  deployment of the backend, for the purposes of C-4's `POST → GET`
  lifecycle, outside M15's supported execution model** — the same boundary
  M14 already operates under today in production, now stated as an
  explicit architectural invariant rather than left implicit.
- **Multi-instance or shared-result retention is NOT solved by this
  pack.** If it is ever required, it is a **separate, future architecture
  decision** (§24 AAQ-3), gated on the same `08_MongoDB_Data_Architecture.md`
  + ADR governance chain (or an equivalent design) that this section's
  "Why" already declines to trigger here.

### 12.2 SSE implications (same invariant — not a separate mechanism)

The existing `EventBus` used for SSE trace-event delivery has two
backends: `InMemoryEventBus` (an `asyncio.Queue` per subscriber — always
process-local) and `RedisEventBus` (Redis Streams, `XADD`/`XREAD` with
independent per-subscriber cursors — **cross-process-capable** for raw
trace-event delivery when `JOB_BACKEND=redis` is configured). Read alone,
this could suggest SSE trace-event delivery is exempt from §12.1's
invariant.

**It is not exempt, because the invariant does not live in the event
transport — it lives in the result payload.** The SSE stream's synthetic
`final` frame — the frame that carries the completed `changes` payload
(Document 70 §10.3) — is not read from the event stream itself; it is
constructed at emission time by looking up the **same process-local result
buffer** §12.1 describes (mirroring the existing
`_filing_analysis_stream_events` → `_get_filing_analysis_result` call,
`server.py:2500-2509`). So even when `JOB_BACKEND=redis` makes raw
trace-event delivery cross-process-capable, **the completed result
payload — whether delivered via `GET` or via the SSE `final` frame —
remains available only from the one backend process that ran the job.**
No new streaming mechanism is introduced to change this; this section
states the existing dependency precisely so implementation and testing do
not assume cross-instance job-result availability by mistake.

---

## 13. Comparison / Orchestration Architecture

**Decision record:**

1. **Decision**: share the orchestration shell (route handlers, job
   lifecycle calls, response-envelope assembly, error-taxonomy mapping)
   across both modes; keep the two comparison engines (§9, §10) fully
   separate, with no shared comparison or citation-validation code between
   them.
2. **Context/problem**: the task asks whether financial and narrative
   comparison should share orchestration, validation infrastructure,
   evidence/citation infrastructure, or use fully separate logic.
3. **Options considered**: (a) one shared "comparison engine" abstraction
   with a `period`/`report` strategy interface; (b) shared orchestration
   shell only, separate domain engines; (c) fully separate route handlers
   and job kinds per mode (two `JobKind` members instead of one).
4. **Chosen approach**: (b).
5. **Why**: the orchestration concerns (job admission, status transitions,
   SSE framing, response envelope shape, error mapping) are **identical**
   across modes and already fully generic in the existing `JobLifecycle`
   infrastructure — sharing them is exactly what every prior milestone
   does, not a new abstraction. The domain logic (deterministic arithmetic
   vs. LLM-grounded claim generation) has no meaningful overlap — a shared
   "comparison engine" interface (option a) would be an abstraction with
   exactly one implementation for years, refactored the first time a third
   mode is ever considered (which OCD-1 explicitly defers). Option (c)
   would duplicate the entire route family and double the `JobKind`/
   settings surface for no behavioral gain, since Document 70 already
   unifies both modes under one route family.
6. **Tradeoffs**: the single top-level orchestration function
   (`_run_change_brief`) contains an early `if comparison_type ==
   "period": ... else: ...` branch — a visible seam, but an honest one,
   matching `_run_filing_analysis`'s own internal structure (outcome
   classification branches by output kind already).
7. **Consequences**: one `JobKind.CHANGE_BRIEF` member (§16) serves both
   modes; `comparison_type` is carried through the job's stored
   metadata/result, not encoded as a second `JobKind`.
8. **What remains unresolved**: none — this is a settled architecture
   choice with no deferred sub-question.

---

## 14. LLM Boundary

- **`period` mode: no LLM, ever.** The financial-delta computation is
  100% deterministic arithmetic over already-persisted structured data
  (§9). Using an LLM here would violate Document 70 §8.2's own "mechanical
  rule, not a materiality judgment" framing and this task's explicit
  instruction not to reach for an LLM for deterministic computation.
- **`report` mode: exactly one `chat_json` call per request.**
  Deterministic preprocessing (`build_evidence_payload`) ends, and model
  reasoning begins, at the point where *semantic* claim identification is
  required — the same boundary `comparison_explanation.py` and
  `filing_analysis.py` already draw.
  - **Determinism**: not guaranteed bit-identical across runs (Document 70
    §17) — no persisted identity-keyed reuse is adopted (§12), so this is
    an accepted, contract-sanctioned property, not a defect.
  - **Structured outputs**: `chat_json` against the new Pydantic schema
    (§10) — the existing, sole mechanism for structured LLM output in this
    codebase; no new invocation path.
  - **Validation**: per-item citation validation (§10) runs on every
    response, deterministically, regardless of what the model returned.
  - **Retry/failure behavior**: reuse `agents/llm.py`'s existing
    `chat_json` retry/repair behavior unmodified — no new retry policy.
    A provider failure or unrepairable malformed output maps to the
    existing `LLMProviderError` → job `failed` → 502 path (§18).
  - **Token/cost considerations**: the evidence payload is bounded to
    exactly 2 reports (narrower than M9.1's 2–4), so per-request cost is
    at most what a 2-report M9.1 comparison already costs today — no new
    cost-control mechanism is needed.
  - **Evidence grounding**: the entire point of the per-item both-sides
    validation (§10) — a claim's grounding is judged by deterministic
    index-mapping checks against the evidence payload, never by trusting
    the model's own assertion that it is grounded.

---

## 15. Persistence / State Architecture

**C-4 requires no new durable persistence.** It reads two existing,
already-persisted collections (`reports`, `financial_statements`) —
read-only, no new write path to either. The only retained state is
**process-local, bounded, TTL-limited, transient job-result retention**
(AH-2, §12) — not a database, and not framed here as "a cache" or "not a
cache" as a matter of semantics; what matters architecturally is its
behavior, stated precisely in §12.1: retrievable only from the process
that computed it, discarded on that process's restart, and not reachable
by a `GET` (or SSE `final` frame) landing on a different process.

- **No user research history** is introduced — nothing tracks what a user
  has previously compared.
- **No last-visit state** — every comparison point is explicit,
  caller-supplied on every request (§5).
- **No Durable Research Sessions** — no session concept exists for C-4 at
  all.
- **No durable C-4 comparison state** — the AH-2 buffer does not persist
  across a process restart and is not queryable except by its own job id,
  from the process that holds it.

**This is a stated architectural deployment constraint, not merely a
future operational concern**: M15's supported execution model for the
`POST → completion → GET` lifecycle is single-backend-process (§12.1) as a
direct, present-tense consequence of the AH-2 mechanism this pack selects
— it is true today, for the architecture this pack proposes, not only in
some future multi-instance scenario. **If durable or cross-instance
retention were genuinely required** — to lift that constraint — the
required governance is exactly what Document 70 §16 already names:
`08_MongoDB_Data_Architecture.md` + the ADR chain, as a **separate,
subsequent** architecture decision (§24 AAQ-3), not folded into this one.

---

## 16. API / Job Execution Architecture

The async-job execution model is **already fixed at the contract level**
(Document 70 §10.1, §10.3) — this section addresses only how the
architecture plugs into the **existing** job infrastructure, inventing no
new protocol:

- **New `JobKind` member** (`backend/domain/models.py`): one additive
  enum line, `CHANGE_BRIEF = "change_brief"`, matching the exact pattern
  of the `FILING_ANALYSIS` addition before it (a one-line, additive
  change with no restructuring of the enum).
- **New settings entry** (`backend/app/settings.py`): one additive
  `job_deadline_change_brief_s: float = Field(default=<TBD>, ...)` field,
  mirroring `job_deadline_filing_analysis_s` exactly, added to the
  `job_deadline_s` dict property. The default numeric value is
  operational tuning (Document 70 OCD-4) — not fixed by this pack.
- **Route handlers** (`backend/server.py`): four new handlers under
  `/api/companies/{ticker}/changes`, following the exact structural
  pattern of `create_filing_analysis` / `get_filing_analysis` /
  `stream_filing_analysis` / `cancel_filing_analysis` — `JobLifecycle`
  calls for admission/status/cancel, `sse_response()` for the stream, and
  the AH-2 result buffer (§12) for the completed-result payload.
- **Admission control**: the existing shared `MAX_ACTIVE_JOBS` budget
  applies automatically — no new gate, no per-kind override (matching
  `JobStore.active_count()`'s explicit "not parameterized by kind"
  design).
- **Ownership enforcement**: at the route-handler layer, exactly as every
  existing job kind does (`job.user_id != user["id"]` → 404) — not at the
  `JobStore`/`JobLifecycle` layer, which enforces no ownership today for
  any kind. C-4 does not change this pattern.

**Decision record — synchronous vs. asynchronous execution:**

1. **Decision**: confirm and reuse the existing asynchronous job model;
   do not introduce a synchronous execution path for either mode.
2. **Context/problem**: `period` mode is fast and fully deterministic —
   it could technically execute synchronously within a single HTTP
   request/response cycle.
3. **Options considered**: (a) both modes async (uniform with the rest of
   the platform); (b) `period` mode synchronous (thin read-adapter style,
   like `GET /companies/{ticker}/financials`), `report` mode async.
4. **Chosen approach**: (a).
5. **Why**: Document 70 §10.1 already fixes the route family as async for
   **both** modes at the contract level — this is not an open
   architecture question. Uniformity also avoids a client needing to
   branch its own polling/streaming logic by `comparison_type`, and avoids
   maintaining two response-shape conventions (job envelope vs. direct
   body) for what the client experiences as one capability.
6. **Tradeoffs**: `period`-mode requests pay a small, likely-negligible
   round-trip latency overhead (job creation + at least one poll or
   stream connection) they wouldn't pay as a synchronous call.
7. **Consequences**: none beyond the above — this follows directly from
   the already-ratified contract.
8. **What remains unresolved**: none — this is fixed by Document 70, not
   an open architecture question.

---

## 17. Validation and Quality Architecture

Two categories are kept explicitly distinct, per the task's requirement:

**Contract validation** (per-request, deterministic, runs on every call,
shapes the response):
- **Request shape**: a new discriminated Pydantic request model
  (`comparison_type`-conditional required fields), validated by FastAPI at
  the route boundary — mirroring the existing pattern of Pydantic models
  with conditional field requirements already used elsewhere in
  `server.py`.
- **Comparison references**: existence + ownership + ticker-match checks
  (§9, §10) — 404 on any failure, per Document 70 §15.
- **Financial outputs**: correctness is validated by construction (the
  pure function's own tested invariants, §22) — there is no separate
  request-time "is this delta plausible" check, since the computation is
  arithmetic, not a claim to distrust.
- **Narrative outputs**: per-item citation validation (§10) — duplicate/
  undeclared-index rejection plus the both-sides requirement. An item
  failing validation is dropped, never surfaced malformed.
- **Evidence completeness**: `coverage_boundaries` construction from
  validation/alignment failures (unit mismatches, uncorroborated topics).
- **Malformed/partial provider data**: matches the existing repository-
  wide convention (`CLAUDE.md`: "External data sources are best-effort...
  must return `None` and fall back, never crash a request") — an empty
  `metrics: []` list or an absent field degrades to `insufficient_evidence`
  /`partial`, never a 500.
- **Model outputs**: malformed JSON is rejected at the `chat_json`/Pydantic
  parsing layer before reaching application logic at all.

**Model-quality evaluation** (offline, not per-request, informs whether the
system is good enough to ship — never gates an individual request):
- The golden-dataset framework (§22) and, if OCD-5 is later resolved
  affirmatively, the self-consistency framework — both operate on fixed,
  held-out cases, entirely separate from the live request path.

This mirrors the existing separation already present in the codebase
(`evaluation/core/case_evaluator.py` vs. the live `server.py` request path)
— C-4 introduces no new separation principle, only a new instance of the
existing one.

---

## 18. Error / Partial-Result Architecture

Every scenario below maps onto **already-ratified** Document 70 behavior
(§5, §15) — this section is an internal implementation-to-contract mapping,
introducing no new externally observable semantics:

| Scenario | Architectural handling | Contract-level result |
|---|---|---|
| Missing baseline (report or period) | Independent existence check fails | 404 `not_found` |
| Missing current (report or period) | Independent existence check fails | 404 `not_found` |
| Missing metric (present in only one period) | `change_kind: "new"`/`"removed"` classification | Not an error — a valid item |
| Insufficient narrative evidence | Zero candidate items groundable on both sides | `insufficient_evidence` state, 200 |
| Malformed/empty provider data | Empty `metrics: []`, or unit/currency mismatch | `insufficient_evidence` / `partial`, 200 |
| Retrieval failure (DB error) | Unhandled DB exception | 502 `infrastructure_error` |
| Validation failure (request shape) | Pydantic/FastAPI rejection | 422 `validation_error` |
| Validation failure (self-comparison, reversed period order) | Explicit check in the request model | 422 `validation_error` |
| Model / provider failure | `LLMProviderError` from `chat_json` | Job `failed`, 502 `llm_provider_error` |
| Malformed model output (unrepairable) | Same `chat_json` failure path | Job `failed`, 502 `llm_provider_error` |
| Timeout | `JobLifecycle.is_past_deadline()` check | Job `failed`, 504 `deadline_exceeded` |
| Client cancellation | `JobLifecycle.cancel()` | Job `cancelled`, idempotent 200 |

No row above introduces a class, code, or state beyond what Document 70
already enumerates.

---

## 19. Security Architecture

- **SSRF protection**: reuse `require_admin` + `assert_public_url` for any
  custom `llm_provider`/`llm_base_url`, unmodified — the identical guard
  every existing BYOK-accepting route already applies.
- **BYOK handling**: reuse the existing per-request `contextvar` threading
  (`set_llm_context`/`reset_llm_context`) around the single `chat_json`
  call in `report` mode; `period` mode makes no LLM call and therefore
  never touches BYOK context at all.
- **External-provider boundary**: all LLM access through `agents/llm.py`
  only — the new `change_brief_narrative.py` module makes no direct
  provider SDK call.
- **Untrusted content**: `reports.extracted_data`/`sentiment_analysis`
  content fed to the model is untrusted **data**, not instructions — the
  same posture Document 70 §18 and Document 64 §15 already establish for
  report/filing text. No new sanitization is invented; the existing
  prompt-construction convention (data interpolated into a fixed system
  prompt, never treated as executable instruction) is reused.
- **Ownership / non-disclosure**: job records and report references are
  owner-scoped exactly as every existing surface enforces (§16, §10) — a
  foreign or nonexistent reference is indistinguishable (404), preserving
  the existing non-disclosure discipline.

---

## 20. Observability

- **Tracing**: one root span per run, `pipeline.change_brief`, following
  the exact out-of-graph convention M9.1/M14 already use (a single
  `pipeline.<capability>` span, no LangGraph node instrumentation since
  there is no graph). Child spans per logical step:
  `resolve_references`, and either `compute_financial_delta` (period) or
  `generate_narrative` + `validate_citations` (report).
- **Metrics**: a new counter, **`change_brief_runs_total{outcome,
  comparison_type}`**, following the exact naming/label precedent of
  `comparison_explanation_runs_total`/`filing_analysis_runs_total`
  (`outcome ∈ {completed_complete, completed_partial,
  completed_insufficient_evidence, failed, failed_deadline_exceeded,
  cancelled}`), with `comparison_type` added as an extra label dimension
  — a deliberate, justified deviation from the exact precedent shape,
  since C-4 (unlike its predecessors) has two modes worth distinguishing
  in aggregate metrics. All other metrics (`alphascribe_http_requests_total`,
  per-route duration histograms, `llm_calls_total`/`llm_tokens_total` for
  `report` mode) are inherited automatically — no new instrumentation
  required for them.
- **Structured logging**: correlation-id propagation is inherited
  automatically via the existing middleware/filter — no new logging code.
- **What must never be logged**: BYOK API keys, raw provider responses on
  failure (the existing `LLMProviderError` safe-message substitution
  already prevents this), and raw report/filing text beyond what existing
  routes already log (i.e., nothing new is introduced that isn't already
  covered by the existing discipline).

---

## 21. Performance / Scalability

- **Retrieval cost**: at most two document reads per request (either two
  `financial_statements` rows or two `reports` rows) — bounded, and of the
  same order of magnitude as existing single-digit-read endpoints.
- **Model invocation cost**: at most one `chat_json` call per request
  (`report` mode only), over a 2-report evidence payload — narrower than
  M9.1's existing 2–4-report bound, so no worse than an already-accepted
  cost profile.
- **Repeated retrieval / caching**: **no new caching layer is introduced.**
  No repeated-access pattern has been identified that a cache would
  address, and Document 65's own OAQ-6 precedent already reasoned that new
  AI-artifact capabilities should add no new Redis caching. If a specific,
  measured latency or cost problem is later identified, that is a
  separate, future architecture decision — not pre-empted here.
- **Horizontal scaling (deployment constraint, not a performance tuning
  item)**: the AH-2 mechanism (§12.1) fixes M15's supported execution
  model for the `POST → completion → GET` lifecycle as
  single-backend-process. This is **not** a scalability optimization to
  revisit later for latency reasons — it is a present, architectural
  limit on how C-4 may be deployed at all, distinct from every other
  bullet in this section (which are genuine cost/latency tuning
  questions). Running the backend behind a load balancer that may route a
  `GET`/stream request to a different process than the one that completed
  the job is **not supported** by this architecture; scaling C-4
  horizontally in that sense requires the separate, future decision named
  in §12.1/§15/§24 AAQ-3.
- **Concurrency**: bounded by the existing, shared `MAX_ACTIVE_JOBS`
  admission budget — no new concurrency control is introduced or needed.
- **Large documents**: not a new concern for C-4 — it reads structured
  `reports`/`financial_statements` documents, not raw filing chunks; their
  size is already bounded by the existing report-generation and financials
  pipelines.
- **Timeout boundary**: one new `job_deadline_change_brief_s` setting
  (§16); its numeric value is operational tuning (Document 70 OCD-4), not
  fixed here.
- **Worker utilization**: identical to every existing job kind — one
  `asyncio` background task per job, no new worker pool.

**No Redis caching or persistence is introduced simply because Redis
exists in the stack.** Every stateful component this pack proposes (the
AH-2 result buffer) is justified in §12 by direct reference to an existing,
shipped precedent and an explicit non-durability ceiling — not by
convenience.

---

## 22. Testing / Evaluation Architecture

**No tests are implemented by this task** — this section defines strategy
only, for a future, separately authorized implementation phase.

- **Unit tests (pure-function, hermetic style)**, following
  `test_comparison_explanation_pure.py`'s pattern: for
  `change_brief_financial.py`'s eligibility rule — `changed`/`new`/
  `removed` classification, `percent_delta` null-on-zero/absent-baseline,
  unit-mismatch exclusion, currency-mismatch short-circuit, and financial
  item ordering — using in-memory `FinancialStatement`/`Metric` fixtures,
  no DB, no network.
- **Integration/contract tests (hermetic fake-Mongo + real ASGI style)**,
  following `test_comparison_explanation_endpoint.py`/
  `test_filing_analysis_endpoint.py`'s pattern: for the full
  `/api/companies/{ticker}/changes` route family — request validation for
  both modes, independent per-id ownership/ticker checks, the create/
  status/stream/cancel lifecycle, and the complete/partial/
  insufficient_evidence state transitions.
- **Deterministic financial fixtures**: small, hand-authored
  `FinancialStatement` pairs covering every §9 case explicitly (a matched
  metric that changed, a new metric, a removed metric, a unit mismatch, a
  currency mismatch, a zero baseline).
- **Narrative evaluation corpus**: new golden-dataset cases (proposed
  naming: `change_brief_narrative_<tickers>.json`), reusing the **existing**
  case schema (`case_id, surface, dataset_version, context.report_ids` /
  `fixture_reports, expected_behaviors, citation_expectation`) verbatim,
  with a new `surface` value (`"change_brief"`) and one new adapter module
  (proposed: `evaluation/adapters/change_brief.py`), mirroring
  `evaluation/adapters/comparison_explanation.py`'s structure exactly:
  wraps the real production function (`change_brief_narrative`'s
  generation entry point), never re-implements grounding/citation logic,
  supports the same LIVE/FIXTURE modes.
- **Citation/evidence validation tests**: explicit assertions that an item
  citing only one side is dropped and never surfaces in a response.
- **Failure-path tests**: one test per row of §18's table.
- **Reproducibility expectations**: `period`-mode output asserted
  bit-identical across repeated identical requests; `report`-mode narrative
  text explicitly **not** asserted bit-identical (Document 70 §17) — only
  the response **schema** is asserted stable.
- **Self-consistency framework reuse**: `backend/evaluation/self_consistency/`
  is confirmed generic and reusable (it operates on arbitrary `(claim,
  evidence)` pairs via `evaluation/core/judge.py`, with no
  filing-analysis-specific coupling) — it **may** be pointed at C-4
  narrative cases without modification, if a future, separate CTO decision
  resolves OCD-5 affirmatively. This pack does not trigger that decision.
- **Deployment-invariant tests (§12.1, §12.2)** — required additions
  covering the AH-2 mechanism's stated behavior, not merely its happy
  path:
  - **Same-process completed-result `GET`**: a job created and completed
    within one test process's buffer is retrievable via `GET` from that
    same process — the baseline case every other test below is contrasted
    against.
  - **Result expiration**: a completed result past its TTL is no longer
    returned by `GET` (the entry is treated as absent, not as a stale
    hit) — asserted with a controllable/injectable clock or TTL, not a
    real-time sleep.
  - **Process-local result unavailable after restart**: simulated by
    constructing a fresh buffer instance (representing a restarted
    process) and asserting a `GET` for a job id known to the *previous*
    buffer instance is not found — proving the mechanism does not
    accidentally survive a restart.
  - **Unsupported/cross-instance behavior**: simulated by constructing two
    independent buffer instances (representing two backend processes) and
    asserting a job completed in one is not retrievable via the other —
    proving the architecture's single-process invariant (§12.1) actually
    holds, so implementation cannot silently regress into an
    accidentally-working cross-instance assumption.
  - **SSE / job lifecycle under the same supported execution model**: the
    SSE stream test suite asserts the `final` frame is emitted only when
    the stream is consumed from the **same process** that ran the job
    (§12.2) — and, symmetrically, that a stream consumed from a different
    process (simulated as above) still delivers ordinary trace frames if
    `JOB_BACKEND=redis` is exercised, but never fabricates a `final` frame
    it cannot construct from its own process-local buffer.

---

## 23. Alternatives and Tradeoffs (consolidated)

| Area | Alternative rejected | Why |
|---|---|---|
| Financial engine | Class-based pluggable comparison strategy | No extensibility requirement exists; adds indirection with no gain (§9). |
| Narrative `items[]` (AH-1) | Deterministic text decomposition of one narrative | Fragile sentence/paragraph heuristics; cannot reliably attribute per-item citations (§10, §11). |
| Narrative `items[]` (AH-1) | Two-pass LLM (generate then restructure) | Doubles cost/latency for a problem one schema already solves (§10, §11). |
| Job-result retention (AH-2) | Durable Mongo collection (M9.1-style) | Requires new schema governance this task cannot authorize (§12). |
| Job-result retention (AH-2) | New Redis-backed cache | New Redis usage with no measured need; contradicts Document 65's own OAQ-6 precedent (§12). |
| Orchestration | Shared generic "comparison engine" abstraction | Premature abstraction for two domains with no logic overlap (§13). |
| Orchestration | Two separate `JobKind` members (one per mode) | Duplicates route family and settings surface Document 70 already unifies (§13). |
| Execution model | Synchronous `period`-mode path | Contract already fixes both modes as async (§16). |
| Orchestration engine | LangGraph | No multi-step agentic reasoning exists to justify it; contradicts the existing out-of-graph precedent for single-call surfaces (§14). |
| Performance | New caching layer | No measured need; Redis exists for job/event infrastructure, not general caching (§21). |

---

## 24. Open Architectural Decisions

None of the following blocks architecture ratification on its own — each
is a bounded, explicitly flagged item for a future decision:

| # | Item | Status |
|---|---|---|
| **AAQ-1** | Exact numeric value of `job_deadline_change_brief_s` | Operational tuning at implementation time (Document 70 OCD-4). |
| **AAQ-2** | Exact prompt wording and model tier for `report`-mode generation | Implementation detail, not fixed by this pack (§10). |
| **AAQ-3** | If/when M15 must support horizontal multi-instance deployment for the `POST → GET` lifecycle, what mechanism lifts the §12.1 single-process invariant | Not needed today — this pack explicitly scopes multi-instance support for this lifecycle out of M15 (§12.1, §15, §21); would require a separate architecture decision plus schema/infrastructure governance if it ever arises. |
| **AAQ-4** | Whether OCD-5's §20.1-style validation gate is adopted for C-4 | Contract-level decision, not architecture's to make; self-consistency framework is ready to reuse if adopted (§22). |

**Contract-level Open Contract Decisions (OCD-1 through OCD-6) and the
formerly-open AH-1/AH-2 are not re-listed here as unresolved** — OCD-1
through OCD-6 remain explicitly contract-level and untouched by this pack
(§5); AH-1 and AH-2 are resolved by this pack (§11, §12).

---

## 25. Contract-Impact Assessment

**Document 70's contract is internally coherent, and this pack proposes no
change to it — but the AH-2 mechanism this pack selects introduces a
deployment invariant that must be stated explicitly for `POST → GET` to be
realized correctly.** These are two separate findings, kept distinct:

- **Contract coherence**: Document 70 R4 is fully sufficient to guide this
  architecture. The financial path's mechanical rule (§8.2) required no
  architectural interpretation beyond direct implementation. AH-1's
  resolution (§11) satisfies Document 70 §8.3/§11.3/§12's requirements
  exactly (a list of items, each eligibility-checked, each both-sides
  cited) without requiring any contract change. AH-2's resolution (§12)
  satisfies Document 70 §16's constraint (no durable per-user history)
  without requiring any contract change. The one implementation-level
  nuance worth recording — that C-4's report resolution needs a
  `ticker`-match clause the existing `_resolve_authorized_reports` query
  pattern doesn't itself include — is a **compatible extension of an
  existing query shape**, not a contract gap; Document 70 §9.4 already
  specifies the required behavior precisely (§10).
- **Deployment invariant, not a contract gap**: Document 70 §16/AH-2
  deliberately declines to select a retention mechanism, requiring only
  that whatever is chosen not become a durable, cross-request, per-user
  history store. This pack's chosen mechanism satisfies that constraint,
  but — as a property of *this specific mechanism*, not of the contract —
  it is only correctly realized under a single-backend-process deployment
  for the `POST → completion → GET` lifecycle (§12.1). That invariant is
  an architecture-level fact this pack must state precisely so it is not
  silently violated by a future deployment change; it does not indicate
  anything insufficient or contradictory in Document 70 itself, and no
  change to Document 70 is being proposed.

**No STOP condition under the contract-change rule is triggered.** This
pack does not modify, does not propose modifying, and finds no need to
modify Document 70. Nothing in this document reopens Document 70.

---

## 26. Implementation Boundary

This pack defines architecture only. A future, separately authorized
implementation would need to:

- add one `JobKind` member and one settings entry (§16);
- add two new pure/LLM-backed modules (`change_brief_financial.py`,
  `change_brief_narrative.py`) and their schemas (§9, §10);
- add four route handlers and update the route-inventory guard by exactly
  those four entries;
- add the AH-2 result buffer (§12);
- add the observability counter and spans (§20);
- add the tests and golden-dataset cases described in §22.

**None of the above is created, modified, or authorized by this document.**

---

## 27. Authorization Status

🟠 **DRAFT / PENDING CTO REVIEW. NOT RATIFIED.** This document does not
authorize:

- implementation of any kind;
- any source code, test, or configuration file;
- any MongoDB collection, index, schema, or migration;
- any Redis realization beyond what already exists;
- any LangGraph change;
- any frontend implementation;
- commit, push, merge, deployment, or release.

---

## 28. Next Governance Gate

**The next legitimate governance action is CTO review and ratification of
this Architecture Decision Pack** — a distinct act from drafting it —
followed by a separate implementation-authorization decision, then
implementation, then commit, then push, each a distinct CTO act, none
collapsed:

```text
Doc 73 (this pack)          🟠 PROPOSED — pending CTO review
  ↓
Architecture ratification    NOT YET PERFORMED
  ↓
Implementation authorization NOT AUTHORIZED
  ↓
Implementation / commit / push  NOT AUTHORIZED
```

---

**🟠 M15 ARCHITECTURE DECISION PACK — DRAFT / PENDING CTO REVIEW (REVISION
R1). THIS DOCUMENT PROPOSES, BUT DOES NOT RATIFY, AN ARCHITECTURE FOR THE
CTO-RATIFIED M15 = C-4 API CONTRACT (DOCUMENT 70, REVISION R4, RATIFIED BY
DOCUMENT 72). AH-1 IS RESOLVED: `report`-MODE `items[]` IS PRODUCED BY A
STRUCTURED MODEL-OUTPUT SCHEMA EXTENSION, NOT TEXT DECOMPOSITION, AND IS
BOUNDED IN PRINCIPLE BY THE EXISTING EVIDENCE-PAYLOAD SIZE AND THE MODEL'S
OWN OUTPUT-TOKEN BUDGET — NO NEW HARD NUMERIC CAP IS FIXED. AH-2 IS
RESOLVED: JOB-RESULT RETENTION REUSES THE M14 IN-PROCESS, TTL-BOUNDED
BUFFER PATTERN — NO NEW MONGODB COLLECTION — BUT THIS MECHANISM CARRIES AN
EXPLICIT DEPLOYMENT INVARIANT: A COMPLETED RESULT IS RETRIEVABLE, VIA
EITHER `GET` OR THE SSE `final` FRAME, ONLY FROM THE ONE BACKEND PROCESS
THAT RAN THE JOB; A PROCESS RESTART CAN LEGITIMATELY DISCARD IT; AND A
REQUEST ROUTED TO A DIFFERENT PROCESS CANNOT RETRIEVE IT — EVEN WHEN THE
UNDERLYING `RedisEventBus` MAKES RAW TRACE-EVENT DELIVERY CROSS-PROCESS-
CAPABLE. HORIZONTAL MULTI-INSTANCE DEPLOYMENT FOR THE `POST → GET`
LIFECYCLE IS THEREFORE EXPLICITLY OUTSIDE M15'S SUPPORTED EXECUTION MODEL
AND IS NOT SOLVED BY THIS PACK. NO NEW REDIS USAGE, NO STICKY SESSIONS, AND
NO OTHER NEW INFRASTRUCTURE ARE INTRODUCED TO WORK AROUND THIS. NO LANGGRAPH
INVOLVEMENT. NO LLM INVOLVEMENT IN `period` MODE. THE TWO MODE-SPECIFIC
CITATION SHAPES REMAIN DISTINCT. THE BOTH-SIDES NARRATIVE GROUNDING
REQUIREMENT IS ARCHITECTURALLY ENFORCEABLE AND ENFORCED PER ITEM. DOCUMENT
70'S CONTRACT IS INTERNALLY COHERENT AND IS NOT MODIFIED, NOT REOPENED, AND
NOT PROPOSED FOR CHANGE — THE DEPLOYMENT INVARIANT ABOVE IS A PROPERTY OF
THIS PACK'S CHOSEN MECHANISM, NOT A CONTRACT DEFICIENCY. ALL SIX OPEN
CONTRACT DECISIONS (OCD-1 THROUGH OCD-6) REMAIN CONTRACT-LEVEL AND
UNRESOLVED BY THIS PACK. THIS DOCUMENT DOES NOT AUTHORIZE IMPLEMENTATION,
PRODUCTION CODE, TESTS, MONGODB SCHEMA/COLLECTION/INDEX/MIGRATION, REDIS
REALIZATION, LANGGRAPH CHANGES, FRONTEND IMPLEMENTATION, COMMIT, OR PUSH.
NO SOURCE, TEST, SCHEMA, OR INFRASTRUCTURE FILE WAS CREATED OR MODIFIED.
DOCUMENTS 67–72 WERE NOT MODIFIED. NO STAGE. NO COMMIT. NO PUSH. NO MERGE /
REBASE / RESET / AMEND. THE NEXT LEGITIMATE GOVERNANCE ACTION IS CTO REVIEW
AND RATIFICATION OF THIS ARCHITECTURE DECISION PACK — NOT IMPLEMENTATION.**
