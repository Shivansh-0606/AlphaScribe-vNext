# 70 — M15 API Contract Proposal — C-4 "What Changed Since Last Review"

**Status:** 🟡 **M15 API CONTRACT PROPOSAL — CTO-REVIEWED, APPROVED FOR
RATIFICATION, NOT YET RATIFIED (REVISION R4).** This is **not** the ratified M15 API contract. It proposes externally observable
request/response, citation, error, state, and persistence semantics for
**M15 = C-4** — formally selected by
[68_M15_Formal_Milestone_Selection_Record.md](68_M15_Formal_Milestone_Selection_Record.md)
and ratified by
[69_Document68_CTO_Ratification_Record.md](69_Document68_CTO_Ratification_Record.md).
Nothing in this document **ratifies** itself, decides M15 architecture,
authorizes implementation, authorizes a commit, or authorizes a push — each
is a separate, subsequent CTO act (§24).

**Type:** API / contract proposal artifact (research / design / governance
only — no source code, test, schema / migration / index, endpoint, route,
LangGraph node, retrieval / RAG change, MongoDB collection, Redis usage,
provider selection, or frontend file created or modified to produce it).

**Depends on (CTO-ratified, unmodified — read, not altered):**
[67_Post_M14_Backend_AI_Roadmap_Reconciliation.md](67_Post_M14_Backend_AI_Roadmap_Reconciliation.md)
(the roadmap recommendation that identified C-4 as the preferred next
Backend & AI direction, and its OD-2…OD-7 register),
[68_M15_Formal_Milestone_Selection_Record.md](68_M15_Formal_Milestone_Selection_Record.md)
(the formal selection **M15 = C-4**, its §5 candidate dispositions, and its
§6 open-design-question register), and
[69_Document68_CTO_Ratification_Record.md](69_Document68_CTO_Ratification_Record.md)
(the CTO ratification of that selection — "the next legitimate governance
gate is the M15 API Contract Proposal — not implementation").

**Structural precedent (cited, unmodified):**
[64_M14_Filing_Analysis_API_Contract.md](64_M14_Filing_Analysis_API_Contract.md)
(the most recent ratified API contract — its section skeleton, its §5.1
contract-vs-architecture boundary rule, its §6.1 mechanism-naming-exclusion
reasoning, and its flat-cited-narrative response shape are reused here),
[43_M9_API_Contract_Decision_Pack.md](43_M9_API_Contract_Decision_Pack.md)
and
[42_M9_Product_Decision_Explanation_Semantics.md](42_M9_Product_Decision_Explanation_Semantics.md)
(the grounded / cited / non-recommending AI-output semantics pattern, and the
job / status / SSE / cancel route family), and
[59_M13_Filing_Content_Read_API_Contract.md](59_M13_Filing_Content_Read_API_Contract.md)
(the `(ticker, doc_id)` filing-identity and non-disclosure-404 pattern, reused
here in generalized form for report and period identity).

**Roadmap position:** Document 67 recommended C-4 (CTO-ratified 2026-09-03);
Document 68 formally selected M15 = C-4 (CTO-ratified via Document 69,
2026-09-04). This document is the next authorized governance activity after
Document 69 — "the M15 API Contract Proposal." Through Revision R4, this
proposal has been **CTO-reviewed and approved for ratification**; the
separate act of **ratifying** this contract has not yet been performed
(§2, §24).

**Date:** 2026-09-04.

**Revision R1 (2026-09-05) — CTO-directed correction pass, pre-ratification.**
CTO review result: **NOT YET APPROVED FOR RATIFICATION — INTERNAL
INCONSISTENCIES REQUIRE CORRECTION BEFORE RATIFICATION CAN BE CONSIDERED.**
This revision: (1) resolves the two-dimension / comparison-type
contradiction — `report` and `period` are now explicit, **mutually
exclusive comparison modes**; a single request evaluates exactly one and
never both (§8, §9); (2) rewrites `complete`/`partial`/`insufficient_evidence`
per mode, replacing the invalid "both dimensions were evaluated" framing
(§13, §14); (3) adds a precise, mechanical financial change-item
qualification rule — metric identity, absolute/percentage delta, zero
baseline, negative values, missing/newly-appearing line items, stable
ordering — with **no invented materiality threshold** (§8.2); (4) fixes the
financial vs. narrative source shapes to be distinct and internally
consistent, removing the prior contradiction between the §11.1 example and
its own prose (§11.2, §11.3); (5) corrects the prior false claim that
`agents/comparison_explanation.py` is reused "as-is" for `report` mode —
producing `items[]` from that engine's single-narrative output is an
explicitly acknowledged **additive transformation** whose mechanism is left
to the architecture phase, not designed here (§8.3, §22.1 AH-1); (6) grounds
financial `before`/`after` value semantics in the actual `Metric` /
`FinancialStatement` domain model — metric identity via `provider_label`,
raw (non-normalized) values, `unit`, `currency`, zero-denominator behavior
(§8.2); (7) adds explicit reference-consistency rules — report/ticker
scoping, independent per-id authorization, and period directional ordering
(§9.4); (8) fully specifies the externally observable create / status /
stream / cancel contract without hedging on architecture adoption (§10.3);
(9) softens §16's persistence language so the contract states only the
required externally observable constraint (no durable per-user history),
without selecting or ratifying a specific retention mechanism (§16, §22.1
AH-2); (10) reconciles §23 against every revised section. **No scope change
beyond what corrections 1–10 require. No architecture decision. No
implementation / commit / push authorization. Status unchanged: 🟡
PROPOSED — CTO DECISION REQUIRED. NOT RATIFIED.**

**Revision R2 (2026-09-05) — CTO re-review correction pass, pre-ratification.**
CTO re-review result: **STILL NOT APPROVED FOR RATIFICATION — REMAINING
UNDEFINED TERMS AND GAPS REQUIRE CORRECTION.** This revision: (11) defines a
precise, non-numeric **narrative-item eligibility rule** (§8.3) — substantive
semantic difference, a discrete expressible claim, grounded on both sides —
replacing the undefined "materially unremarkable" / "material narrative
difference" / "worth reporting" language in §8.3, §13, and §14.2; (12)
requires every narrative item to cite **at least one source from each of
the baseline and current reports** (§8.3, §11.3, §12, §23) — the §11.3
example now shows two sources, one per side; (13) rewrites narrative
`partial` semantics (§14.2) as an externally observable evidence-coverage
gap (a topic/metric evidenced on only one side), no longer naming the
comparison engine's `limitations[]` field as the contract's semantic
authority; (14) changes `prompt_version` to `string | null` (§11.1) —
`report` mode returns the applicable version, `period` mode always returns
`null` (not a placeholder string); `schema_version` stays populated for
both modes; (15) removes the "(if adopted)" conditional `JobKind` wording
from §23, stating instead the externally observable requirement (existing
`JobStatus` lifecycle and shared admission budget) without prescribing a
specific `JobKind` identifier; (16) precisely specifies the SSE `final`
frame's wire shape (§10.3) — an unnamed `data:` frame with `node == "final"`
in its body, not a distinct SSE event type — sufficient for a client/test to
distinguish it from a normal trace frame and the terminal `event: end`
frame; (17) verifies and states the **actual** repository precedent for the
create endpoint's HTTP `200` status (§10.3) — confirmed by inspecting every
existing async-job creation route's decorator for a `status_code=` override
(none found) — rather than asserting it unverified; (18) makes explicit that
`report` mode infers no chronology from report metadata — only
`baseline_report_id`/`current_report_id` field position establishes
direction (§9.4). **No scope change beyond what corrections 11–18 require.
No architecture decision. No implementation / commit / push authorization.
Status unchanged: 🟡 PROPOSED — CTO DECISION REQUIRED. NOT RATIFIED.**

**Revision R3 (2026-09-05) — CTO-directed narrow correction pass, pre-ratification.**
CTO re-review result: **STILL NOT APPROVED FOR RATIFICATION — RESIDUAL
IMPRECISION IN CITATION WORDING REQUIRES CORRECTION.** This revision: (19)
rewrites §5's global citation wording — no longer claiming every item is
"cited to the two references' own persisted content" — to state precisely
that a `period`-mode `changed` item cites both statement sides, a `new`
item cites `current` only, a `removed` item cites `baseline` only, and a
`report`-mode narrative item continues to require at least one source from
**each** side (unweakened); (20) makes §7's parallel description
mode-neutral to match §5 and §11.2, so it no longer implies every financial
`new`/`removed` item needs both-sided evidence; (21) corrects §12's "reused
unmodified" claim — the indexed **citation convention** (`sources[]` +
`cited_source_indices`, no new syntax or mechanism) is what's reused
unmodified; the financial source-reference shape
`{index, statement_type, period_end, metric}` is **newly defined** (financial
evidence has no prior shape to reuse, since its persisted identity differs
from a report's), while the narrative shape `{index, report_id, field}`
does reuse the existing report-citation mapping unmodified — both shapes
are kept, neither removed; (22) rewrites §19's deadline requirement so it
states only that a dedicated **C-4 job deadline configuration** must exist,
without requiring a specific `JobKind` identifier or internal mapping,
consistent with §23's existing architecture-freedom stance. **No scope
change beyond what corrections 19–22 require. No architecture decision. No
implementation / commit / push authorization. Status unchanged: 🟡
PROPOSED — CTO DECISION REQUIRED. NOT RATIFIED.**

**Revision R4 (2026-09-05) — CTO-directed narrow consistency correction, pre-ratification.**
CTO re-review result: **STILL NOT APPROVED FOR RATIFICATION — RESIDUAL
MIXED-MODE ORDERING WORDING REQUIRES CORRECTION.** This revision: (23)
rewrites the `items[]` inline comment in §11.1's top-level response example
— the prior parenthetical listing `§11.2 ("financial") or §11.3
("narrative")` in that order could be misread as sequencing (financial
items followed by narrative items in one response) — to state explicitly
that every item belongs to the single category matching the request's
`comparison_type`, and the two categories never appear together in one
response. No other wording in §11.2, §11.3, §11.4, or elsewhere was found
to imply combined- or mixed-mode ordering. **No scope change beyond this
wording clarification. No architecture decision. No implementation /
commit / push authorization. Status unchanged: 🟡 PROPOSED — CTO DECISION
REQUIRED. NOT RATIFIED.**

---

## 0. What This Document Is and Is Not

**Is:** a **proposed** M15 API contract for C-4 — the capability's identity
and auth model, the semantic shape of its comparison-reference input, the
bounded definition of "changed" it commits to, its response shape, its
citation / provenance requirement, its no-change and insufficient-evidence
semantics, its error taxonomy, its state / persistence semantics, its
determinism expectations, and a register of what remains genuinely open for
CTO decision or a later architecture phase. Structured after Document 64,
which is itself structured after Documents 59 and 43.

**Is not:**

- a ratified contract — ratification is a separate, subsequent CTO act (§2,
  §24);
- an **architecture decision** — it does not choose a persistence mechanism,
  a MongoDB collection / index / schema, LangGraph topology, retrieval / RAG
  strategy, worker topology, caching layer, or model / provider selection.
  Where a question is architecture-owned, it is filed in §22 as an **Open
  Contract Decision** or handed to a future M15 Architecture Decision Pack,
  never silently resolved;
- Durable Research Sessions, a "last visit" pointer, general news/market
  monitoring, alerts/watchlists, sentiment or analyst-consensus monitoring,
  unrestricted Filing Q&A, C-2, C-3, or C-5 (§20);
- a reopening of M14, Document 67, Document 68, or Document 69, or an
  amendment to any of them.

---

## 1. Document Identity

| Field | Value |
|---|---|
| Document number | 70 |
| Title | M15 API Contract Proposal — C-4 "What Changed Since Last Review" |
| Milestone | M15 = C-4 (Document 68 §4; Document 69 §2) |
| Governance stage | API Contract Proposal — Revision R4, CTO-reviewed, approved for ratification, **not yet ratified** |
| Predecessor gate | Document 69 — Document 68 CTO Ratification Record (🟢 CTO-RATIFIED, 2026-09-04) |
| Successor gate (not created here) | CTO ratification of this contract, then a separate M15 Architecture Decision Pack |
| Files created by this task | this document only |
| Files modified by this task | none |

---

## 2. Status / Authority

🟡 **PROPOSED — CTO DECISION REQUIRED. NOT RATIFIED.**

**Governance ladder (each a distinct CTO act; none confers the next):**

```text
Document 67 — roadmap recommendation           🟢 CTO-RATIFIED (2026-09-03)
Document 68 — M15 = C-4 formally selected       🟢 CTO-RATIFIED via Doc 69 (2026-09-04)
Document 69 — Document 68 ratification record   🟢 CTO-RATIFIED (2026-09-04)
Document 70 (THIS) — M15 API contract proposal  🟡 CTO-reviewed, approved for ratification — not yet ratified
  ↓
M15 contract ratification                       NOT YET PERFORMED
  ↓
M15 Architecture Decision Pack                   NOT CREATED
  ↓
M15 implementation authorization                 NOT AUTHORIZED
  ↓
Implementation / commit / push                   NOT AUTHORIZED
```

This document performs exactly one act: **drafting a contract proposal for
CTO review.** It does not perform, and does not imply, any later stage.

---

## 3. Governance Preconditions (verified this session, read-only)

| Fact | Source | Verified state |
|---|---|---|
| M14 — Filing Analysis | `git log`; Document 66 | **COMPLETE / PUBLISHED** (`be4949b`); `HEAD = origin/main = be4949b` |
| Document 67 | its §14 | **CTO-RATIFIED (2026-09-03)** — recommends C-4 as preferred next Backend & AI direction; does not itself select M15 |
| Document 68 | its §1, §Status | **M15 = C-4 — FORMALLY SELECTED**; contract / architecture / implementation / commit / push all **NOT** authorized by the selection itself |
| Document 69 | its §2, §8 | **Document 68 — CTO RATIFIED (2026-09-04)**; explicitly names "the M15 API Contract Proposal" as the next legitimate gate; explicitly authorizes no contract, architecture, code, schema, or git mutation |
| C-4 open design questions | Document 68 §6; Document 67 §10 (OD-2…OD-7) | **OPEN**, restated unresolved by Document 69 §7 — this document is where they are owed a resolution or an explicit, bounded deferral |
| Candidate dispositions (C-2, C-3, Filing Q&A, DRS, C-5) | Document 68 §5; Document 69 §6 | Unchanged, restated in §20 below |
| M15 contract / architecture / implementation | Document 69 §8 | **NONE proposed or ratified** before this document. This document is the M15 API **contract proposal** — **CTO-reviewed, approved for ratification, not yet ratified** (as of Revision R4). |

No governance state above is changed by this document. It is cited, not
re-decided.

---

## 4. Existing API / Backend Convention Dependency (inspected this session, cited — not modified)

Every proposal choice in §8–§19 is derived from, and constrained by, this
table. **No file below is modified by this document.**

| Component | File / location | Verified finding |
|---|---|---|
| Async job / stream infra | `backend/domain/models.py` (`JobKind`, `JobStatus`); `backend/infrastructure/streaming/sse.py`; Document 43 §3; Document 64 §2 | `JobKind ∈ {RESEARCH, LEARNING, COMPARISON_EXPLANATION, FILING_ANALYSIS}`; `JobStatus ∈ {QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED}`; one shared `MAX_ACTIVE_JOBS` admission budget; one shared `sse_response()` helper (unnamed `data:` frames, `: keepalive`, terminal `event: end`). **Every existing LLM-generating surface (Research, Learning, Comparison-Explanation, Filing Analysis) is an async job with a create/status/stream/cancel route family — none is a synchronous call.** |
| Comparison / explanation engine | `backend/agents/comparison_explanation.py` | Pure, hermetic module that already does "explain the meaningful differences between 2–4 already-generated `reports`": `build_evidence_payload`, `build_prompt`, `compute_identity_key`, `compute_evidence_fingerprint`, `validate_and_map_citations`, `generate_explanation`. One `chat_json` call, deterministic post-hoc citation validation (model never trusted with a real `report_id` — only a 1-based `report_number` it maps server-side). **The closest existing engine to "compare two things and explain what changed."** |
| Comparison-explanation request/response shape | `backend/server.py:1834` (`ExplainRequest.report_ids: list[str] = Field(min_length=2, max_length=4)`); `backend/agents/schemas.py:61-73` (`ComparisonExplanationSchema`) | Wire field is `report_ids` (a flat, **unordered**, 2–4 member list — no "before/after" directionality). Response: `{narrative, sources[], cited_source_indices, limitations[]}`. |
| Report ownership / resolution | `backend/server.py:1848` (`_resolve_authorized_reports`); `backend/tests/test_reports_scoping.py` | `{"id": {"$in": report_ids}, "$or": [{"user_id": user_id}, {"is_sample": True}]}` — a report is authorized if owned by the caller **or** flagged `is_sample: True` (public sample data). One authorized id missing from the resolved set → **404** (`test_compare_one_valid_one_invalid_returns_404`). Reports **are** owner-scoped, unlike the shared filing/company corpus. |
| Financial statement identity | `backend/domain/financials.py:57-65` | `FinancialStatement` identity = `ticker + period_type + period_end + statement_type`. `PeriodType ∈ {annual, quarterly}`; `StatementType ∈ {income, balance_sheet, cash_flow}`; `period_end` is an ISO-8601 date string. |
| Financials read endpoint | `backend/server.py:875-931` (`GET /companies/{ticker}/financials`) | Groups by `statement_type`; sorts `periods` by `period_end` descending; response `{"ticker","period_type","statements": {<type>: {"acquisition_state","periods":[...]}}}`. Purely a read adapter — thin, **synchronous**, no LLM. |
| Filing identity | Document 59 §3.1 (CTO-RESOLVED); Document 64 §2 | A filing is addressed by `(ticker, doc_id)` together; `doc_id` under the wrong `ticker` → 404, non-disclosure. |
| Filing analysis output shape | Document 64 §8.2; `backend/agents/filing_analysis.py` | Each output = `{narrative, sources[], cited_source_indices, state, coverage_boundaries}`; `state ∈ {complete, partial, insufficient_evidence}`; a single output's grounding failure never fails the whole request. |
| LLM access boundary | `backend/agents/llm.py`; `CLAUDE.md` | **All** LLM access is `chat_text` / `chat_json` only — multi-provider, per-request key + base_url via a `contextvar`. |
| Error envelope + taxonomy (closed, 9 kinds) | `backend/domain/errors.py:19-119`; `backend/app/api/errors.py:32-38` | `{"detail": <msg>, "type": <code>}`. `NotFoundError`(404,`not_found`), `ValidationError`(422,`validation_error`), `ConflictError`(409,`conflict`), `AuthorizationError`(403,`forbidden`), `RateLimitedError`(429,`rate_limited`), `DeadlineExceededError`(504,`deadline_exceeded`), `InfrastructureError`(502,`infrastructure_error`), `LLMProviderError`(502,`llm_provider_error`, subclass of `InfrastructureError`), `StreamingError`(500,`streaming_error`). Module docstring: *"there are nine concrete error kinds today... split it when a kind needs its own logic, not before (YAGNI)."* |
| Auth | `backend/server.py` — `Depends(current_user)` on every tool route | One dependency, identical everywhere. Corpus collections (`companies`, `filings`, `filing_chunks`) have **no `user_id`** — shared by design. Job records **are** owner-scoped. `reports` **are** owner-scoped (see above). |
| M14's on-demand persistence precedent | `backend/server.py:2289-2326` (`_FILING_ANALYSIS_RESULTS`); Document 65 §OAQ-5; Document 67 §2.3 | M14 shipped with **no new MongoDB collection** — a `ponytail:`-marked, in-process, TTL-bounded (256-entry, oldest-first eviction), single-instance result buffer, explicitly because the OAQ-5 durable two-collection design was gated on a separate `08_MongoDB_Data_Architecture.md` + ADR chain that was never separately run. This is the concrete, most recent precedent for "on-demand, no forced new persistence." |
| Route-inventory contract | `backend/tests/contract/test_route_inventory.py:143` | Exact-set guard, `assert len(APPROVED_ROUTES) == 47`. Additive-only; each new route is one explicit entry, added as part of a separately authorized implementation — not this proposal. |
| Job-kind deadline convention | `backend/app/settings.py:63,123-128` | Each `JobKind` has its own `job_deadline_<kind>_s` setting exposed via a `job_deadline_s` dict property. |
| Observability | `backend/infrastructure/observability/` | Every route emits `alphascribe_http_requests_total{method,path,status}` + `alphascribe_http_request_duration_seconds{method,path}`; per-endpoint OTel spans; `llm_calls_total`/`llm_tokens_total` automatic via `chat_*`; M14 additionally emits an outcome-labeled completion counter. |

---

## 5. M15 Scope — Bounded Change Brief  *(contract item 3)*

**In scope for this proposal:**

1. A backend capability that, given a ticker and **exactly one of two
   mutually exclusive comparison modes** (§8, §9) — a `report` mode
   (report-to-report narrative comparison) or a `period` mode (financial
   period-to-period comparison) — each identified by an explicit,
   caller-named pair of comparison references of that mode's kind, produces
   a **bounded list of change items belonging to that single mode** (§11).
   A single request never mixes modes and never evaluates both (§8, §9.2).
2. An authenticated HTTP surface for requesting that comparison and
   retrieving its result, additive to the existing route inventory,
   `current_user` gated, using the existing `{detail, type}` error envelope
   (§10, §15).
3. A **contract-level citation / provenance requirement** — every change
   item is grounded and cited to the persisted evidence that actually
   supports it (§12): a `period`-mode `changed` item cites both the
   `baseline` and `current` statement sides; a `period`-mode `new` item
   cites the `current` side only (no `baseline`-side evidence exists to
   cite — the metric doesn't exist there); a `period`-mode `removed` item
   cites the `baseline` side only, symmetrically; a `report`-mode narrative
   item always cites **at least one source from each of** `baseline` and
   `current` (§8.3, §12) — this both-sides requirement is unchanged.
4. Honest **no-change**, **partial**, and **insufficient-evidence** semantics,
   defined per mode (§13, §14).
5. Reuse of the existing async-job family (`JobStatus` lifecycle, shared
   admission budget) for both modes — without prescribing a specific
   `JobKind` identifier (§23) — and reuse of `agents/comparison_explanation.py`
   as the grounding
   and citation-validation engine for `report` mode, additively extended to
   produce a list of discrete narrative items (§8.3, §11.3) — the
   transformation's mechanics are an architecture-phase concern, not fixed
   here.

**Bounded by construction — M15 is one company, exactly one comparison mode
per request, two explicitly named comparison points of that mode's kind, a
fixed and closed set of per-mode change semantics, fully cited.** Anything
requiring implicit history, multiple companies, mixed-mode or combined-mode
requests, new ingestion, new retrieval infrastructure, or new durable
persistence is either excluded (§20) or deferred to a future architecture
phase (§22) — never assumed in by this proposal.

### 5.1 Contract-vs-architecture boundary — what this proposal fixes, and what it does not

This proposal fixes only *externally observable* behaviour, following
Document 64 §5.1's rule verbatim:

- the capability boundary and exclusions (§5, §20);
- the comparison-reference input shape as *observable behaviour* (§9) —
  what the caller must supply, in what shape, and what happens when it is
  missing or invalid;
- the bounded definition of "changed" (§8) and the fixed, closed set of
  comparison modes and change categories (§8.1);
- the response shape (§11), including per-item citation requirements (§12);
- no-change, partial, and insufficient-evidence semantics (§13, §14);
- validation, status codes, and the error envelope (§15);
- the client-observable determinism / reproducibility guarantees (§17);
- the security / access-control posture (§18);
- the observability signals that must exist (§19, in outline).

It does **not** fix, and a future M15 Architecture Decision Pack remains the
sole authority for: the persistence mechanism if any (§16 proposes
**none**, subject to that phase's own evaluation); retrieval / RAG strategy;
LangGraph topology, if any is used at all; caching and Redis usage; provider
/ model / tier selection beyond BYOK passthrough; and the internal
implementation of the deterministic financial-delta computation. Where this
proposal recommends a mechanism (e.g. "no new collection," §16), that
recommendation is a **bounded, evidence-based default for the contract
stage**, not a foreclosure — exactly as Document 64 §6.1 treats
mechanism-naming exclusions: a later architecture phase may select a
durable mechanism only through the normal schema-change / ADR governance,
never by reading this document as pre-authorizing it.

---

## 6. Problem Statement  *(contract item 4, part 1)*

| Capability | State today | Evidence |
|---|---|---|
| Compare 2–4 already-known reports and narrate differences | **Exists** (M9.1) | `agents/comparison_explanation.py`; `POST /reports/compare/explain` |
| Read one company's financial statements, multiple periods | **Exists** (M12) | `GET /companies/{ticker}/financials`; `financial_statements.periods[]` |
| Deterministic period-over-period **numeric delta** computation | **Missing** | No module analogous to `agents/scoring.py` exists for financial deltas; `financials.py` defines identity and storage only |
| A single, bounded "change brief" naming what differs between two explicit reference points, categorized and cited | **Missing** | No route, no schema, no engine; Document 68 §4: *"a grounded change brief for a single company against a prior reference point... is hereby formally selected"* |
| Any notion of "since a user's last visit" | **Does not exist and must not be introduced** | Document 68 §6 OD-2; Document 69 §7 — explicitly excluded |

**What a user cannot do today:** ask "what changed for this company between
two specific points I name" and get back a short, categorized, cited answer.
The pieces this needs already exist (`reports`, `financial_statements`, the
M9.1 diff engine); nothing bridges them into a bounded change-brief primitive.

---

## 7. Capability Definition  *(contract item 5)*

**C-4, precisely stated:** given a ticker and **exactly one comparison
mode** — `report` or `period` — identified by two explicit, caller-named
comparison references of that mode's kind for that ticker (§9), C-4 returns
a **closed list of change items belonging to that one mode** (§11) — each
briefly explained and grounded/cited to whichever side(s) of the comparison
actually evidence it (§5, §12) — describing what differs between them. A
single request produces items of
exactly one category (`"financial"` for `period` mode, `"narrative"` for
`report` mode); it never mixes the two. Nothing more.

**C-4 is:**

- a **two-point diff and narrate** capability, directional (`baseline` →
  `current`), always over caller-named, already-persisted platform state;
- exactly one of two independent modes per request, each bounded to one
  data source: `report` mode over prior `reports` (via the existing
  comparison-explanation engine, additively extended — §8.3) or `period`
  mode over `financial_statements` (via a new, deterministic numeric-delta
  step — §8.2). A client that wants both a narrative and a financial change
  brief issues two separate requests, one per mode;
- always fully cited, honestly empty when nothing qualifying differs (§13),
  and honestly partial/insufficient when evidence is thin (§14), each
  defined per mode.

**C-4 is NOT:**

- a monitor, an alert, a watchlist, or anything that runs without an
  explicit request;
- a chat, a Q&A surface, or anything conversational;
- aware of "the user's last visit," a session, or any implicit history;
- a general market-news or sentiment feed;
- a capability that evaluates both modes in a single request or merges
  their results — each request is single-mode by construction (§8, §9);
- a new analytical primitive beyond "diff two known points and cite the
  differences" — its value is a bounded, retention-oriented convenience over
  data the platform already holds (Document 67 R-C4-4), not a new kind of
  analysis.

---

## 8. Definition of "Changed"  *(contract item 7 — resolves Document 68 §6 "meaning and breadth of 'changed'")*

**"Changed" is bounded to exactly two mutually exclusive comparison modes,
selected by the request's `comparison_type` (§9.2). A single request always
evaluates exactly one mode and returns items of exactly one category — never
both, never a merged result.** No third mode is included in this proposal.

### 8.1 The two modes

| `comparison_type` | Change category | Source | Engine |
|---|---|---|---|
| `"period"` | `"financial"` | `financial_statements`, matched by `(ticker, period_type, statement_type)`, comparing the `baseline_period_end` and `current_period_end` rows | **New**, deterministic, dependency-free numeric delta over matching line items — same house discipline as `agents/scoring.py` (stdlib-only, no LLM for the arithmetic itself). Qualification rule: §8.2. |
| `"report"` | `"narrative"` | Two `reports` documents (`extracted_data`, `sentiment_analysis`, `scorecard` — the same bounded evidence payload `comparison_explanation.py::build_evidence_payload` already extracts) | **Existing engine, additively extended.** `agents/comparison_explanation.py` grounds and validates citations exactly as today; producing a list of discrete narrative items from its single-narrative output is a required additive extension (§8.3, §11.3) — not an as-is reuse. |

A `period`-mode request returns only `"financial"` items; a `report`-mode
request returns only `"narrative"` items. §11's `items[]` is therefore
always category-homogeneous within one response.

### 8.2 Financial change-item qualification and value semantics (`period` mode)

This section defines precisely what makes a financial difference eligible to
appear as an item, and precisely what its `before`/`after`/delta fields
mean — a mechanical, deterministic rule, not a materiality judgment.

**Metric identity.** A line item is identified by `Metric.provider_label`
(`backend/domain/financials.py:51`) — the raw label the data provider
assigned. **`Metric.canonical_metric` is `null` for every metric today**
(`financials.py:46-48`: it "stays null for every metric in Phase 1 — the
five-step canonical-vocabulary governance process... doesn't exist yet; no
mapping has been approved"). This contract therefore matches metrics **only
by exact `provider_label` string equality** between the `baseline` and
`current` statement rows — no fuzzy matching, no synonym resolution, no
canonical-key lookup, because none exists. **Known limitation, not silently
smoothed over:** if a provider relabels the same underlying line item
between two periods, this contract observes that as a removed metric plus a
newly-appearing metric, not a renamed one — no data in the repository today
would let it conclude otherwise.

**Raw value, no separate normalization.** `Metric.value`
(`financials.py:52`) is a single `float` with no separate scaling/magnitude
field (no "reported in millions" multiplier exists in the domain model) —
this contract computes deltas directly on `value` as stored, with no unit
conversion or normalization layer, because none exists to invent.

**Units.** `Metric.unit` (`MetricUnit ∈ {currency, currency_per_share,
shares, ratio, percentage, count}`, `financials.py:32-40`) is carried
through to the response unchanged (§11.2's `unit` field). A `provider_label`
present in both periods with a **different `unit`** between `baseline` and
`current` is a data anomaly, not a computable delta — such a metric is
excluded from `items[]` and named in `coverage_boundaries` (§14.1, triggers
`partial`).

**Currency.** `FinancialStatement.currency` (ISO 4217, `financials.py:66`)
is per-statement, not per-metric. If the resolved `baseline` and `current`
statements carry **different `currency` values**, this contract does not
perform currency conversion — no FX-conversion capability exists anywhere in
the repository, and inventing one here would be unsupported. A currency
mismatch between the two resolved statements makes the entire comparison
ungroundable: **`insufficient_evidence`** (§14.1), not a best-effort
mixed-currency delta.

**Absolute delta** = `after.value - before.value`, computed only when both
sides are non-null.

**Percentage delta** = `(after.value - before.value) / abs(before.value)`
when `before.value != 0`. **When `before.value == 0` (zero baseline), or
when `before`/`after` is `null` (a `"new"`/`"removed"` metric, below),
`percent_delta` is `null`** — never a fabricated infinite/undefined number.
The item still qualifies and is still returned; only the percentage field is
absent.

**Negative values.** Deltas are computed on signed values as stored — no
absolute-value normalization. A metric moving between positive and negative
(or vice versa) is a valid, eligible change with no special-cased
arithmetic.

**Eligibility rule (mechanical, no magnitude threshold):**

| Case | Eligible? | Item shape |
|---|---|---|
| Metric present in both periods, `value` differs | **Yes** | `change_kind: "changed"`, both `before`/`after` populated |
| Metric present in both periods, `value` identical | **No** | not emitted |
| Metric present in `current`, absent from `baseline` | **Yes** | `change_kind: "new"`, `before: null` |
| Metric present in `baseline`, absent from `current` | **Yes** | `change_kind: "removed"`, `after: null` |
| Metric absent from both periods | n/a | never considered |
| Same `provider_label` present in both periods with **different `unit`** | **Not computed as a delta** | excluded from `items[]`, recorded in `coverage_boundaries` (§14.1, `partial`) |

**No minimum-magnitude materiality threshold is imposed.** Any nonzero
delta, or any appearing/disappearing metric, qualifies. This proposal does
**not** invent a "materially different" cutoff (e.g. "only deltas over 5%")
because no existing repository convention grounds a specific number — see
Open Contract Decision **OCD-6** (§22) for whether a future filter threshold
should be added. **`significance` (a per-item qualitative label, OCD-2) is a
separate question from eligibility** — eligibility (this section) decides
*whether an item appears at all*; `significance`, if ever added, would only
label an already-eligible item, never gate its appearance.

Item ordering is defined in §11.4.

### 8.3 Narrative change-item qualification (`report` mode)

**Eligibility rule (externally observable, no numeric threshold).** A
`report`-mode narrative difference is eligible to become an item only if it
satisfies **all three** of the following:

1. **Substantive semantic difference.** The claim describes something a
   reader's understanding of the company would change because of — a
   difference in business facts, financial condition, outlook, risk, or
   management commentary between `baseline` and `current`. A difference
   that is purely **wording, phrasing, emphasis, or ordering** of the same
   underlying fact (restated but not changed) is **not** eligible and must
   not be emitted as an item.
2. **Discrete, expressible claim.** The difference can be stated as one
   bounded, specific claim (e.g. "guidance was revised downward," "a new
   litigation risk was disclosed") — not a vague or diffuse impression that
   cannot be pinned to a specific claim.
3. **Grounded in report evidence on both sides, not inferred.** The claim
   is directly supported by content actually present in the `reports`
   evidence payload (§4 `build_evidence_payload` — `extracted_data`,
   `sentiment_analysis`, `scorecard`) from **both** `baseline` and `current`
   (§11.3, §12) — never a claim extrapolated, guessed, or inferred beyond
   what that evidence states.

**This is not a numerical materiality threshold** — no percentage, score, or
magnitude cutoff is imposed or implied. It is a categorical eligibility test
applied to each candidate difference: wording-only/noise differences and
unsupported/inferred claims are excluded by definition; a difference that
passes all three criteria is eligible regardless of how significant it
seems (a separate, optional labeling question — OCD-2, §22).

`report` mode reuses `agents/comparison_explanation.py`'s existing grounding
and citation-validation logic (`validate_and_map_citations`) **without
modification** to *how a claim is grounded*: **zero grounded citations for a
narrative claim is a failed generation for that claim**, never a fabricated
one (Document 42 §7's grounding law, reused verbatim) — criterion 3 above is
that same grounding law applied per candidate difference, with the
both-sides requirement of §12 added.

**`items: [] + state: "complete"` means: the comparison was successfully
grounded, and applying the eligibility rule above, no eligible narrative
difference was found** — not that grounding failed (§13, §14.2).

**What is genuinely new, and not yet built:** the engine's existing output
(`ComparisonExplanationSchema`, §4) is **one narrative block** with a
parallel `sources[]`/`cited_source_indices` and a `limitations[]` list — not
a list of independently structured, individually cited items, and not
structured around the per-item eligibility rule above. Producing `report`
mode's contractually-required `items[]` (§11.3) — each item satisfying the
eligibility rule and the both-sides citation requirement (§12) — from that
single narrative requires an **additive transformation or schema
extension** to the engine's output; the two are not currently the same
output model, and this proposal does not claim otherwise. **This contract
fixes the required external shape and eligibility criteria of that
transformation's output (§11.3) and does not fix, invent, or presume its
mechanism** (whether the model is prompted to emit a list directly via an
extended schema, or the single narrative is deterministically decomposed
post-generation, is an architecture-phase decision — §22.1 AH-1).

### 8.4 Explicitly excluded from "changed" in this proposal

(bounded, not a silent gap — see §20 for the full exclusion list):

- risk-disclosure or MD&A diffing **across two different filings'** M14
  analyses — no existing engine diffs two `filing_analysis` results against
  each other (M14's own "Important Changes" output is explicitly
  filing-local, INV-IC, Document 64 §8.1); building one is out of scope for
  this proposal and is recorded as an Open Contract Decision (§22, OCD-1);
- anything sourced outside `reports` and `financial_statements` — no news,
  no external market data, no analyst consensus, no sentiment monitoring;
- management-commentary diffing as an independent primitive — to the extent
  management commentary is reflected in a report's `extracted_data` /
  `sentiment_analysis`, it is already covered by `report` mode; no separate
  MD&A-specific diff is added;
- **a combined or merged mode that evaluates both `report` and `period`
  comparisons in a single request** — not defined by this contract; a
  client needing both issues two separate requests (§7, §9).

This keeps C-4's "changed" bounded to what two already-hardened data sources
can support today, per Document 68 §6 item B and the task's explicit
instruction not to broaden C-4 into a general monitoring platform.

---

## 9. Comparison / Reference Semantics  *(contract item 6 — resolves Document 68 §6 OD-2)*

**Resolution: the caller must always name both comparison points explicitly.
There is no default, no "most recent," and no implicit "since last visit"
for either point.** This directly satisfies Document 68 §6 / Document 69 §7's
explicit prohibition on redefining "last review" as "the user's last visit,"
and it applies symmetrically to *both* the reference (prior) point and the
current point — not only the reference point — so that neither side of the
comparison can be read as a stored, per-user pointer.

### 9.1 The four candidate semantics from Document 68 §6, evaluated

| Candidate | Evidence | Disposition |
|---|---|---|
| (1) Explicitly supplied prior artifact (`report_id`) | **Strong** — `agents/comparison_explanation.py` already compares named `report_id`s; `report_ids` is an established wire convention (`ExplainRequest`) | **Adopted**, as one of two comparison kinds (§9.2) |
| (2) Explicitly supplied reporting period (`period_end`) | **Medium** — `financial_statements.periods[]` identity already includes `period_end`; no existing diff *engine*, but the data and identity scheme are hardened (M8/M12) | **Adopted**, as the second comparison kind (§9.2), with a new deterministic delta step |
| (3) Explicitly selected comparison point (a general "the caller always names it" principle) | **Strong** — this is not a distinct third mechanism; it is the *governing principle* that (1) and (2) both implement | **Adopted as the governing principle**, not a separate kind |
| (4) Durable user/session history ("since last visit") | **Contra-indicated** — Document 68 §6, Document 69 §7, and Document 67 R-C4-3 all identify this as the DRS-adjacency risk | **Rejected.** Not implemented in any form, explicit or implicit. |

### 9.2 Proposed request shape

`comparison_type` is a single, request-level discriminator — it selects
which pair of fields is required, not a per-side choice. Both comparison
points are always of the kind that `comparison_type` names and are always
explicitly supplied; supplying fields belonging to the other kind alongside
it is a validation error (§10.2, §15).

```jsonc
// POST /api/companies/{ticker}/changes
{
  "comparison_type": "report",          // "report" | "period" — required
  // comparison_type == "report":
  "baseline_report_id": "<report id>",  // required
  "current_report_id": "<report id>",   // required
  // comparison_type == "period":
  "period_type": "annual",              // "annual" | "quarterly" — required
  "statement_type": "income",           // "income" | "balance_sheet" | "cash_flow" — required
  "baseline_period_end": "2024-06-30",  // ISO-8601 date — required
  "current_period_end": "2024-09-30",   // ISO-8601 date — required

  "llm_provider": null, "llm_api_key": null,
  "llm_base_url": null, "llm_model": null   // BYOK, reused verbatim
}
```

**Why two named fields (`baseline_*`/`current_*`) instead of reusing
`ExplainRequest.report_ids` as-is:** M9.1's `report_ids` list is symmetric
and unordered (2–4 reports, no directionality). C-4 is inherently
directional — "what changed **from** the baseline **to** the current
state" — so a flat list would either impose an undocumented ordering
convention or lose directionality entirely. Named `baseline`/`current`
fields make the direction part of the wire contract, not an implicit
convention (§21 records this as a deliberate, evidence-justified divergence,
not an incompatibility).

**"Current" is never implicit.** The `current_report_id` /
`current_period_end` must be supplied by the caller exactly like the
baseline. This is a deliberately more conservative position than "current
defaults to the newest report/period" — even though "newest" is a
deterministic, non-personalized, company-level fact rather than a
per-user "last visit," requiring it explicitly removes any ambiguity about
whether C-4 tracks *anything* implicit, and keeps the contract maximally
defensible against DRS-adjacency review. Whether to later relax this (allow
`current_report_id`/`current_period_end` to default to "the most recent
existing one for this ticker") is recorded as an Open Contract Decision
(§22, OCD-3) — it is evidence-compatible, but not adopted by default here.

### 9.3 What §9 does not define

- how `baseline`/`current` values are chosen by the *frontend* — that is a
  frontend implementation concern, not part of this backend contract;
- whether a third `comparison_type` (e.g. filing-to-filing) is ever added —
  excluded from this proposal (§8, §20), recorded as OCD-1;
- the deterministic delta algorithm's internals — the *existence and
  determinism* of the computation is contractual (§8, §17); its
  implementation is not.

### 9.4 Reference consistency requirements

**`report` mode:**

- `baseline_report_id` and `current_report_id` must each independently
  resolve to a `reports` document whose own `ticker` field matches the path
  `ticker` — a `report_id` that resolves under a *different* ticker is
  treated identically to a nonexistent id (404 `not_found`, non-disclosure,
  §15). Cross-ticker comparison is not supported by this contract.
- Each of `baseline_report_id` and `current_report_id` is checked for
  authorization **independently** (owned by the caller, or `is_sample:
  True`) — matching the existing `_resolve_authorized_reports` one-id-at-a-
  time disposition (`test_compare_one_valid_one_invalid_returns_404`, §4). A
  request where one id is authorized and the other is not returns 404, not
  a partial result.
- `baseline_report_id == current_report_id` is a degenerate self-comparison.
  This contract treats it as a validation error (422 `validation_error`),
  matching the `period`-mode directionality rule below, rather than a valid
  (necessarily empty) comparison.
- **No chronology is inferred from report metadata.** `report` mode does
  not read, compare, or order by any report timestamp or other metadata
  field (e.g. `created_at`) to decide which side is "prior" — doing so
  would reintroduce an implicit ordering this contract deliberately avoids
  (§9). **Field position alone** — `baseline_report_id` versus
  `current_report_id` — establishes directional semantics; the caller is
  solely responsible for choosing which `report_id` plays which role. This
  preserves the decision not to invent a chronology rule the repository's
  `reports` model does not itself support to any degree of grounding.

**`period` mode:**

- `baseline_period_end` **must be strictly earlier than** `current_period_end`
  (ISO-8601 date string comparison). Equal values are already rejected
  (§10.2); `baseline_period_end > current_period_end` is **also** a
  validation error (422 `validation_error`) — this contract enforces
  directional ordering explicitly rather than leaving it ambiguous, because
  the `before`/`after` and `change_kind: "new"/"removed"` semantics (§8.2,
  §11.2) are only meaningful if `baseline` genuinely precedes `current`.
- Both `(ticker, period_type, statement_type, baseline_period_end)` and
  `(ticker, period_type, statement_type, current_period_end)` must each
  resolve to an existing `financial_statements` row — checked
  independently; either missing → 404 `not_found` (§15).

---

## 10. Request Contract  *(contract item 8)*

### 10.1 Endpoint family

Following the repo-wide, uncontested convention that every LLM-generating
surface (Research, Learning, Comparison-Explanation, Filing Analysis) is an
**async job + status + SSE + cancel** family (§4), never a synchronous call —
and because `report` mode's narrative comparison is itself one
`chat_json`-backed call through the existing comparison-explanation engine —
this proposal specifies the same four-route family for **both modes**,
company-scoped like M12–M14:

```
POST   /api/companies/{ticker}/changes
GET    /api/companies/{ticker}/changes/{id}
GET    /api/companies/{ticker}/changes/{id}/stream
POST   /api/companies/{ticker}/changes/{id}/cancel
```

This is a **contract-level decision**, not an architecture decision: the
choice between "synchronous call" and "async job with polling/SSE" is
externally observable to a client and is therefore properly fixed here,
exactly as Document 64 §9 fixed M14's route family at the contract stage
while leaving the *internal* orchestration (LangGraph topology, node
structure) to the architecture phase.

### 10.2 Request

| Input | Type | Required | Notes |
|---|---|---|---|
| `ticker` | `str` (path) | required | Normalized `.strip().upper()`, matching every existing company-scoped route. Empty after normalization → 422 `validation_error`. |
| `comparison_type` | `"report" \| "period"` | required | Discriminates the two branches in §9.2. Any other value → 422 `validation_error`. |
| `baseline_report_id`, `current_report_id` | `str` | required iff `comparison_type == "report"` | Must each **independently** resolve to a `reports` document owned by the caller (or `is_sample: True`) whose own `ticker` matches the path `ticker` (§9.4, §18). `baseline_report_id == current_report_id` → 422 `validation_error`. |
| `period_type`, `statement_type`, `baseline_period_end`, `current_period_end` | `str` | required iff `comparison_type == "period"` | Must each **independently** resolve to an existing `financial_statements` row for `(ticker, period_type, statement_type, period_end)`. `baseline_period_end` must be **strictly earlier than** `current_period_end` — equal or reversed → 422 `validation_error` (§9.4). |
| BYOK fields | `str \| None` | optional | Reused **verbatim** from every prior contract (Document 43 §3, §6; Document 64 §7). `llm_api_key` never persisted. Custom provider / `llm_base_url` → existing `require_admin` + `assert_public_url` SSRF guard applies unchanged. |
| *(no output-selection parameter)* | — | n/a | The response always contains every change item the comparison finds — no client-selectable filter, mirroring M14 CQ-2's fixed-output-set precedent. |

A bare `POST {}` (no body) is **not** accepted — unlike M14's
`FilingAnalysisRequest`, C-4 has no meaningful default because
`comparison_type` and its dependent fields are the entire point of the
request. Missing `comparison_type` → 422 `validation_error`.

### 10.3 Per-route response contract (firmly decided; internal orchestration unspecified)

This subsection fixes the **externally observable** behavior of all four
routes unconditionally — it does not use "if the architecture phase
adopts..." language, because the wire contract, unlike the mechanism that
fulfills it, is a contract-stage decision. Internal orchestration
(LangGraph topology, worker/process model, or any other implementation
mechanism) remains unspecified and is not implied by anything below.

**`POST /api/companies/{ticker}/changes`** (create) — `200` (verified
repository precedent, not merely assumed): every existing async-job
creation endpoint's route decorator declares no `status_code=` override —
`POST /reports/generate` (`server.py:1243`), `POST /learning/explain`
(`server.py:1611`), `POST /reports/compare/explain` (`server.py:2143`), and
`POST /companies/{ticker}/filings/{doc_id}/analysis` (`server.py:2435`) all
fall through to FastAPI's default of `200` on a `POST` route with no
override — confirmed by grepping every `status_code=` occurrence in
`server.py`: none appears on any of these four decorators. No existing
async-job creation endpoint in this codebase uses `201`/`202`. C-4's create
route follows this uncontested, repo-wide precedent rather than introducing
a different status code:

```jsonc
{"id": "<job id>", "status": "queued", "reused": false}
```

`reused` is **always `false`** — §16/§17 require no identity-based result
reuse, so every request performs fresh work. This is a firm, externally
observable contract commitment.

**`GET /api/companies/{ticker}/changes/{id}`** (status/result):

- while `status ∈ {"queued", "running"}`: `{"id": "...", "status": "..."}` —
  the `changes` key is **omitted entirely** (not present, not `null`),
  matching the M14 precedent (§4);
- while `status == "completed"`: `{"id": "...", "status": "completed",
  "changes": {...}}` — the mode-specific shape from §11.2/§11.3;
- while `status ∈ {"failed", "cancelled"}`: `{"id": "...", "status": "..."}`
  — no `changes` key;
- an unknown or foreign-owned job id → 404 `not_found` (§15, §18).

**`GET /api/companies/{ticker}/changes/{id}/stream`** (SSE) — reuses the
existing `sse_response()` framing verbatim (§4). Three distinguishable
frame kinds appear on the wire, matching `infrastructure/streaming/sse.py`
exactly:

1. **Normal trace frames** — an unnamed SSE frame, `data: <json>\n\n` (no
   `event:` field), whose decoded JSON body is a `TraceEvent`
   (`{node, status, message?, ts?}`) with `node` set to any pipeline stage
   name **other than** `"final"` (e.g. `"pipeline"`, or a mode-specific
   stage). Identical framing to every existing stream.
2. **The completed `final` payload** — following the exact M14 precedent
   (`server.py:2500-2509`), this is **not** a distinct SSE event type; it is
   one more unnamed `data: <json>\n\n` frame whose decoded JSON body is
   `{"node": "final", "status": "ok", "changes": {...}}`, where `changes` is
   the completed, mode-specific object from §11. A client/test distinguishes
   it from a normal trace frame **solely by `node == "final"`** in the
   decoded body — the SSE-level framing is identical to case 1. This frame
   is emitted exactly once, immediately after the terminal processing trace
   frame, only when the job reaches `"completed"`.
3. **The terminal frame** — the named SSE event `event: end\ndata:
   {}\n\n`, identical to every existing stream, marking the end of the
   stream regardless of outcome.

A job that reaches `"failed"`/`"cancelled"` emits **no** `final` frame —
only whatever normal trace frames preceded the failure/cancellation,
followed directly by the terminal frame (case 3). `: keepalive\n\n` comment
lines (never a `data:` frame, never fire a client's `onmessage`) may appear
at any point before the terminal frame, exactly as in every existing
stream. **No new SSE event type is introduced** — `final` is a `node` value
inside the existing `data:` framing, not a new wire-level mechanism.

**`POST /api/companies/{ticker}/changes/{id}/cancel`**:

- a `queued`/`running` job transitions to `"cancelled"` → `200
  {"id": "...", "status": "cancelled"}`;
- a job already in a terminal state (`completed`/`failed`/`cancelled`) is
  **idempotent** — `200` with its current, unchanged `status`, never an
  error;
- an unknown or foreign-owned job id → 404 `not_found` (§15, §18).

---

## 11. Response Contract  *(contract item 9)*

The shape of the `changes` object returned by a completed job (§10.3)
depends on the request's `comparison_type` (§8, §9). The two shapes are
**not interchangeable**, are never mixed within one response, and a client
discriminates on the `comparison_type` field echoed back in the response.

### 11.1 Common envelope fields (both modes)

```jsonc
{
  "ticker": "AAPL",
  "comparison_type": "period",           // echoes the request — "report" | "period"
  "baseline": {"...": "..."},            // mode-specific identity — §11.2/§11.3
  "current":  {"...": "..."},
  "created_at": "2026-09-05T12:00:00Z",
  "prompt_version": null,
  "schema_version": "v1",
  "items": [ /* every item belongs to the ONE category matching "comparison_type" above: §11.2 ("financial") when comparison_type == "period", §11.3 ("narrative") when comparison_type == "report" — the two categories never appear together in one response */ ],
  "state": "complete",                   // §14
  "coverage_boundaries": []              // §14
}
```

`prompt_version: string | null`. **`report` mode** returns the version
string of the LLM prompt its generation step used (e.g. `"v1"`). **`period`
mode always returns `null`** — it performs no LLM call and has no prompt to
version (§8.2); `null` is the correct, honest value, not a placeholder
string. `schema_version` is a plain string, populated for **both** modes —
it versions the response schema itself, not a generation prompt.

### 11.2 `period`-mode item shape (`category: "financial"`)

```jsonc
{
  "category": "financial",
  "metric": "TotalRevenue",              // Metric.provider_label — exact-match identity key (§8.2)
  "statement_type": "income",
  "period_type": "quarterly",
  "change_kind": "changed",              // "changed" | "new" | "removed" — §8.2
  "unit": "currency",                    // Metric.unit, carried through unchanged
  "currency": "USD",                     // FinancialStatement.currency (ISO 4217)
  "before": {"period_end": "2024-06-30", "value": 123456.0},   // null when change_kind == "new"
  "after":  {"period_end": "2024-09-30", "value": 118234.0},   // null when change_kind == "removed"
  "absolute_delta": -5222.0,             // after.value - before.value; null if either side is null
  "percent_delta": -0.0423,              // (after-before)/abs(before); null when before is null or before.value == 0 (§8.2)
  "sources": [
    {"index": 1, "statement_type": "income", "period_end": "2024-06-30", "metric": "TotalRevenue"},
    {"index": 2, "statement_type": "income", "period_end": "2024-09-30", "metric": "TotalRevenue"}
  ],
  "cited_source_indices": [1, 2]
}
```

The **financial source shape** — exactly `{index, statement_type,
period_end, metric}` — is distinct from, and never mixed with, the
**narrative source shape** (§11.3, exactly `{index, report_id, field}`). No
model is involved in producing a financial citation (§12); it is present in
every financial item unconditionally — `cited_source_indices` therefore
always equals every index present (a `"new"`/`"removed"` item cites only
the one side that exists). There is no partial-citation case for a
financial item, unlike a narrative one.

### 11.3 `report`-mode item shape (`category: "narrative"`)

```jsonc
{
  "category": "narrative",
  "summary": "Guidance for the next quarter was revised downward.",
  "explanation": "The current report lowers forward guidance [2] relative to the guidance stated in the baseline report [1].",
  "sources": [
    {"index": 1, "report_id": "<baseline report id>", "field": "extracted_data.guidance"},
    {"index": 2, "report_id": "<current report id>", "field": "extracted_data.guidance"}
  ],
  "cited_source_indices": [1, 2]
}
```

The **narrative source shape** — exactly `{index, report_id, field}` —
reuses the existing model-facing `report_number` → real-`report_id` mapping
(`comparison_explanation.py`, §4): the model is never trusted with a real
`report_id`. **Every narrative item's `sources[]` must include at least one
entry whose `report_id == baseline_report_id` and at least one entry whose
`report_id == current_report_id`** (§8.3 criterion 3, §12) — a claim about
what *changed* is inherently a claim about both states, so evidence from
only one side does not qualify a candidate difference as an item (§8.3).
**Producing this `items[]` list from the underlying engine's
single-narrative output is the additive transformation §8.3 requires** —
its mechanism is not fixed here (§22.1 AH-1). A candidate difference that
cannot be grounded on both sides is an evidence-coverage gap, surfaced at
the top level via `coverage_boundaries` (§14.2), not as a per-item field.

### 11.4 Ordering

- **`period` mode**: items are ordered by `metric` (`provider_label`),
  ascending, lexicographic — deterministic and reproducible run-to-run
  (§8.2, §17). (Ordering across `statement_type` values does not arise: one
  `period`-mode request names exactly one `statement_type`, §9.2.)
- **`report` mode**: items follow the order the underlying generation step
  emits them — not reordered by the server, exactly as every existing
  narrative surface (Comparison-Explanation, Filing Analysis) already
  treats model output order as authorial, not something to normalize.

---

## 12. Citation / Evidence Contract  *(contract item 10)*

AlphaScribe's established **citation convention** — inline `[n]` markers in
narrative text, a parallel indexed `sources` list, and a `cited_source_indices`
subset of indices actually referenced — is reused as the **sole governing
citation mechanism** for every change item, in both modes. **No new citation
syntax, no new citation mechanism, and no parallel evidence representation
is introduced.**

This does **not** mean every source-reference *shape* is unmodified —
financial-statement evidence and report evidence have different persisted
identities (§4), so two source-reference shapes exist under this one
convention, neither replacing nor duplicating the other:

- **Report evidence** reuses the existing report-citation mapping
  **unmodified** — `{index, report_id, field}` — the same
  `report_number` → real-`report_id` mapping `agents/comparison_explanation.py`
  already uses (§11.3).
- **Financial-statement evidence** has no equivalent existing shape to
  reuse — a `financial_statements` row is identified by
  `(ticker, period_type, statement_type, period_end)` (§4), not by a
  `report_id` — so this contract **newly defines** the financial
  source-reference shape `{index, statement_type, period_end, metric}`
  (§11.2) for it. This is an additive shape under the same governing
  convention, not a departure from it: it still populates the same
  `sources[]` + `cited_source_indices` fields, and no third shape or syntax
  exists.

- **Narrative items** (`report` mode) ground exactly as
  `agents/comparison_explanation.py` already does: `validate_and_map_citations`
  rejects duplicate, undeclared, or unconfirmed citation indices. **Every
  narrative item must additionally cite at least one source from each of
  the baseline and current reports** (§8.3 criterion 3, §11.3) — a
  single-sided citation does not qualify a candidate difference as an item.
  **Zero grounded citations across the whole comparison is a failed
  generation**, not a degraded success (Document 42 §7's grounding law,
  reused verbatim) — it surfaces as `insufficient_evidence` (§14.2), never a
  fabricated narrative.
- **Financial items** (`period` mode) are self-evidencing: the citation *is*
  the matched `(statement_type, period_end, metric)` rows the deterministic
  delta was computed from (§11.2). No model is involved in producing a
  financial item's citation, so there is no "grounding failure" mode for it
  distinct from "the underlying data doesn't exist" (§14.1).
- `SourceReference`-style rendering on the frontend (a design concern, not
  defined here) is expected to reuse the identical `{label, target}`
  component the M9.1/M14 citation shape already targets — no new component
  is required by this contract.

---

## 13. No-Change Behavior  *(contract item 11)*

**Deterministic and unambiguous, defined per mode: "nothing qualifying was
found" is a positive, complete result, never an error and never
`insufficient_evidence`.**

**`period` mode:** if every metric matched between `baseline_period_end` and
`current_period_end` for the requested `(ticker, period_type,
statement_type)` has an identical value, and no `"new"`/`"removed"` metric
exists either (§8.2's eligibility rule finds zero eligible metrics), the
response is:

```jsonc
{"id": "...", "status": "completed",
 "changes": {"...": "...", "comparison_type": "period",
             "items": [], "state": "complete", "coverage_boundaries": []}}
```

This means: *both periods resolved, every matched metric was compared, and
none differed.*

**`report` mode:** if the additive narrative transformation (§8.3) grounds
the comparison but, applying the eligibility rule (§8.3), determines that no
candidate difference between `baseline` and `current` is eligible to become
an item, the response is likewise:

```jsonc
{"id": "...", "status": "completed",
 "changes": {"...": "...", "comparison_type": "report",
             "items": [], "state": "complete", "coverage_boundaries": []}}
```

This means: *both reports resolved, the comparison was grounded, and no
narrative difference satisfying the eligibility rule (§8.3) was identified.*

**In both modes**, `items: []` with `state: "complete"` is categorically
distinct from `insufficient_evidence` (§14): `items: []` + `complete` says
"we compared them and found nothing that qualifies as an item under the
applicable rule (§8.2/§8.3)"; `insufficient_evidence` says "we could not
ground a comparison at all." A client can rely on `state == "complete"` to
distinguish "we looked and found nothing eligible" from "we couldn't look,"
regardless of mode.

No fourth `state` value is introduced for this case — the state vocabulary
stays closed at the three values M9.1/M14 already use (§14), keeping this
proposal additive rather than divergent.

---

## 14. Partial / Insufficient-Evidence Behavior  *(contract item 12 — resolves Document 68 §6 "state semantics")*

**Resolution: reuse the existing `complete` / `partial` /
`insufficient_evidence` vocabulary verbatim. No new state value. Each
value's meaning is defined per mode below — never in terms of "both
dimensions," since a single request always evaluates exactly one mode
(§8).**

### 14.1 `period` mode

| `state` | Meaning | Trigger |
|---|---|---|
| `complete` | Both periods resolved; every matched metric was compared (including the "nothing differed" case, §13) | `baseline_period_end` and `current_period_end` both resolve to an existing `financial_statements` row with the same `currency`; no unresolvable unit conflicts prevent evaluation of every matched metric |
| `partial` | Both periods resolved and share a `currency`, but one or more **specific metrics** could not be compared (a `provider_label` unit mismatch, §8.2), while others were | `coverage_boundaries` names the excluded metric(s) and the reason (e.g. `"unit mismatch for TotalRevenue: currency vs. ratio"`) |
| `insufficient_evidence` | Both periods resolve (not a 404 case), but nothing can be compared at all | Either statement row has an empty `metrics: []` list, or `baseline`'s and `current`'s `currency` differ (§8.2) — no delta can be computed for anything |

### 14.2 `report` mode

| `state` | Meaning | Trigger |
|---|---|---|
| `complete` | Both reports resolved; the narrative comparison was grounded (including the "nothing eligible" case, §13) | `baseline_report_id`/`current_report_id` both resolve and are authorized; every candidate difference considered was either grounded on both sides and found eligible (§8.3, §12) or found not eligible — none was left unresolved by an evidence gap |
| `partial` | Both reports resolved and the comparison is grounded overall (at least one eligible, both-sides-cited item was produced, or the "nothing eligible" determination itself succeeded, §13), but for one or more **specific candidate differences**, evidence exists on only one side — the other side is simply silent on that topic, so whether it is a genuine change or merely an omission cannot be confirmed (§8.3 criterion 3, §12) | `coverage_boundaries` names the specific topic/metric and which side (`baseline` or `current`) lacks corroborating evidence — an externally observable evidence-coverage gap; how the engine detects it internally (whether via `limitations[]` or otherwise) is not part of this contract |
| `insufficient_evidence` | Both reports resolve (not a 404 case), but the comparison cannot be grounded at all | e.g. one or both reports have empty `extracted_data`; **no candidate difference can be grounded on both sides** — reusing Document 42 §7's grounding law verbatim (§8.3, §12) |

**In both modes, a missing/nonexistent/unauthorized `baseline`/`current`
reference is not `insufficient_evidence` — it is a 404 validation failure
(§15).** `insufficient_evidence` applies only when both references are
valid, resolved, and authorized, but the resulting comparison has too
little grounded content to report anything. This keeps "the identifiers
were wrong" and "the identifiers were right but the data was thin"
contractually distinct in both modes.

---

## 15. Error Taxonomy  *(contract item 13)*

**Zero new error classes.** Every C-4 failure mode maps onto the existing
nine-class `domain/errors.py` taxonomy (§4), following the same discipline
Documents 59, 43, and 64 all state explicitly ("split it when a kind needs
its own logic, not before").

| Situation | HTTP | `type` |
|---|---|---|
| Unauthenticated | 401 | — (no body change; existing auth middleware) |
| Empty `ticker` after normalization | 422 | `validation_error` |
| Missing/invalid `comparison_type` | 422 | `validation_error` |
| Missing required field for the chosen `comparison_type` | 422 | `validation_error` |
| `baseline_period_end >= current_period_end` (equal **or** reversed, §9.4) | 422 | `validation_error` |
| `baseline_report_id == current_report_id` (§9.4) | 422 | `validation_error` |
| `baseline_report_id`/`current_report_id` not found, not owned by caller and not `is_sample`, **or resolves under a different ticker than the path `ticker`** (§9.4) | 404 | `not_found` (non-disclosure — identical in all three cases, checked independently per id) |
| `(ticker, period_type, statement_type, period_end)` has no `financial_statements` row for either `baseline_period_end` or `current_period_end` | 404 | `not_found` |
| Unknown `ticker` (no company/financials/reports at all) | 404 | `not_found` |
| Job admission budget exceeded | 429 | `rate_limited` |
| Custom LLM provider by non-admin | 403 | `forbidden` |
| Provider call failure | 502 | `llm_provider_error` |
| Malformed structured model output | 502 | `llm_provider_error` |
| Processing deadline exceeded | 504 | `deadline_exceeded` |
| Cancel on unknown/foreign job id | 404 | `not_found` (non-disclosure, matching M9.1/M14) |
| Cancel on a terminal job | 200 | idempotent, same as M14/M9.1 |
| Database / infra failure | 502 | `infrastructure_error` |

**No distinct "unsupported comparison" code.** An invalid `comparison_type`
enum value is a `validation_error` (422), not a new taxonomy member — this
satisfies the task's requirement to "distinguish... unsupported comparison"
by routing it to the existing validation-error class rather than inventing
one. **No distinct "missing source" vs. "unavailable source" split** —
both collapse to `not_found` (404), matching the non-disclosure discipline
already governing `report_id` and `(ticker, doc_id)` lookups throughout the
codebase. **A `period`-mode currency mismatch between the resolved
`baseline`/`current` statements is not an error** — both references
resolved validly; the comparison itself cannot be grounded, which is the
`insufficient_evidence` *state* (§14.1), returned as a `200` with that
state, not an HTTP error.

---

## 16. State / Persistence Semantics  *(contract item 14 — resolves Document 68 §6 OD-5)*

**Resolution, bounded recommendation: C-4 is stateless / on-demand. No new
MongoDB collection, index, schema, or migration is required or proposed by
this contract.**

- C-4 **requires caller-supplied comparison state** on every request — both
  `baseline` and `current` are always explicit (§9). There is no
  server-held "current comparison state" for any user.
- C-4 **references existing persisted artifacts only** —
  `reports` and `financial_statements` — read-only. No new write path is
  introduced to either collection.
- C-4 **is not Durable Research Sessions.** No per-user history, no "last
  visited" pointer, no watchlist, no new collection tracking what a user has
  looked at (Document 68 §6; Document 69 §7 — restated as firm, not
  reopened by this proposal).
- **This contract does not require, select, or ratify any particular
  retention mechanism** for holding a completed job's result between the
  completing `POST` and a client's `GET` (§10.3). It states only the
  externally observable constraint: whatever bounded, best-effort mechanism
  the architecture phase selects, it must not become a durable,
  cross-request, per-user comparison-history store (which would reopen the
  DRS question this proposal forecloses, above). The architecture phase
  remains free to evaluate the M14 precedent (`server.py:2289-2326` — an
  in-process, TTL-bounded result buffer) among other on-demand mechanisms
  satisfying that constraint; naming it here as a precedent is not a
  selection, and this document does not ratify it as the M15 mechanism
  (§22.1 AH-2).
- **If a future architecture phase concludes a durable store (e.g. to cache
  expensive change-briefs across requests) is warranted, that is a new
  decision** requiring the normal `08_MongoDB_Data_Architecture.md` + ADR
  governance chain — exactly as Document 64 §6.1 treats mechanism-naming
  exclusions. This contract does not pre-authorize it, and does not forbid
  the architecture phase from proposing it through proper governance.

This resolves Document 68 §6's "Persistence" open item with a bounded,
evidence-grounded default, without foreclosing further architecture-phase
evaluation.

---

## 17. Idempotency / Determinism Expectations  *(contract item 15 — resolves Document 68 §6 "orchestration"/determinism cross-cutting concern)*

- **`period`-mode computation is fully deterministic.** The same
  `(baseline_period_end, current_period_end, statement_type, period_type)`
  input always produces the same eligible items, in the same order, with the
  same citations — pure computation, no LLM involvement (§8.2, §11.2).
- **`report`-mode generation is not guaranteed bit-identical across runs.**
  Consistent with Document 64 §12's stance for M14: absent a persisted,
  identity-keyed result to reuse, "run-to-run textual variation is expected
  and acceptable." Because §16 requires no identity-based result reuse,
  **every request recomputes fresh for both modes**, and the create-response's
  `reused` field (§10.3) is **always `false`** — a firm contract commitment,
  not conditional on any architecture choice — exactly matching the M14
  fallback-C precedent (§4).
- If a later architecture phase adopts persistence and identity-based reuse
  (a mechanism choice this contract does not make, §16), the identity key is
  expected to follow `compute_identity_key`'s existing formula
  (`comparison_explanation.py:95`): a hash of the sorted comparison
  references, `prompt_version`, `schema_version`, provider, and model — not
  a new scheme.
- **The response schema is stable regardless of run-to-run text variation** —
  field names, types, and the closed `category`/`state`/`change_kind` enums
  never change between requests, even when `report`-mode narrative text or
  item count varies.
- **`period`-mode item ordering is deterministic** (§11.4); **`report`-mode
  item ordering is whatever the generation step emits**, not normalized,
  matching every existing narrative surface's convention.

---

## 18. Security / Authorization Expectations  *(contract item 16)*

- `current_user` — reused verbatim. No new auth model, no new dependency.
- **Company/financials corpus** (`companies`, `financial_statements`): no
  ownership scoping, shared by every tenant, exactly as M12–M14 (`08` RI-5).
- **`reports`**: owner-scoped. `baseline_report_id`/`current_report_id` must
  resolve under `{"id": {"$in": [...]}, "$or": [{"user_id": user_id},
  {"is_sample": True}]}` (§4) — identical to the existing
  `_resolve_authorized_reports` logic. A foreign, non-sample report id is
  indistinguishable from a nonexistent one (404 non-disclosure, §15).
- **Job records**: owner-scoped exactly like every other `JobKind` — `GET`
  and `cancel` by a non-owner → 404, non-disclosure.
- **BYOK fields**: inherit the existing SSRF-guard policy verbatim
  (`require_admin` + `assert_public_url` for a custom provider / base URL).
- **Prompt-injection note** (handoff item, not resolved here): report
  `extracted_data`/`sentiment_analysis` content is untrusted data fed to the
  model, not instructions — the same posture Document 64 §15 records for
  filing text.

---

## 19. Performance / Operational Contractual Requirements  *(contract item 17)*

Evidence supports only the following as contractual (not tuning values,
which stay operational):

- **A dedicated C-4 job deadline configuration must exist**, following the
  repository's existing job-deadline configuration convention
  (`app/settings.py`'s per-job-kind `job_deadline_<kind>_s` pattern, exposed
  via the `job_deadline_s` dict property, §4) — the externally observable
  requirement is that C-4 has its own deadline value, distinct from every
  other job kind's. This contract does **not** require a particular
  `JobKind` identifier or a specific internal mapping between C-4 and that
  configuration — which `JobKind` (if any new one at all) C-4 uses, and how
  it is wired to its deadline setting, remains an architecture-phase
  decision (§23). The specific numeric deadline value is likewise an
  operational/tuning decision, not fixed by this contract.
- **Observability signals**: the same automatic per-route metrics
  (`alphascribe_http_requests_total`, `alphascribe_http_request_duration_seconds`),
  OTel spans, and automatic `llm_calls_total`/`llm_tokens_total` every route
  already gets, plus an outcome-labeled completion counter mirroring M14's
  `.labels(outcome=...)` pattern for `completed_complete` /
  `completed_partial` / `completed_insufficient_evidence`, applied
  identically regardless of `comparison_type`. **No fourth "no_change"
  outcome label is added** — a no-change result is `completed_complete` with
  `items: []` in either mode, keeping the outcome vocabulary closed at the
  three values M14 already established (§13, §14).
- No SLA, throughput, or concurrency figure is specified — no evidence in
  the repository grounds a specific number for this new capability, and
  inventing one would be exactly the kind of unsupported figure the task
  instructs against.

---

## 20. Explicit Exclusions  *(contract item 18)*

M15 / C-4 **does NOT include, and this contract does NOT define:**

- **User "last visit" history, or any per-user comparison-history state.**
  Both comparison points are always explicit (§9).
- **Durable Research Sessions** — remains BLOCKED (Document 68 §5; Document
  69 §6). Not introduced directly or indirectly through C-4.
- **General-purpose news or market monitoring.**
- **Alerts, notifications, watchlists, or scheduling** of any kind.
- **Sentiment monitoring or analyst-consensus monitoring** as standalone
  capabilities (distinct from the bounded, already-captured sentiment fields
  a `reports` document may already carry, which `report` mode's narrative
  comparison may reflect — §8).
- **A combined or merged comparison mode evaluating both `report` and
  `period` inputs in a single request.** Not defined by this contract; each
  request is single-mode by construction (§8, §9) — a client needing both
  issues two separate requests.
- **Unrestricted / conversational Filing Q&A.** Remains separately scoped
  (Document 68 §5).
- **C-2 (Structured Filing-Section Extraction) as a separate milestone.**
  Not selected, not rejected, not folded into M15 (Document 68 §5; Document
  69 §6).
- **C-3 (Financial Visualization).** Frontend track, untouched.
- **C-5 (Governance hygiene).** Untouched, unrelated.
- **Any change to Documents 64–69 or to the M14 implementation.**
- **Filing-analysis-to-filing-analysis (risk/MD&A) diffing across two
  filings** — no existing engine supports it; excluded from this proposal
  and recorded as an Open Contract Decision (§22, OCD-1), not silently
  smuggled in under "narrative" or "financial."
- **New MongoDB collection / index / schema / migration; Redis usage; a new
  caching layer** — none is authorized by this contract, and none is
  pre-approved (§16; mirrors Document 64 §6.1's mechanism-naming-exclusion
  reasoning applied to C-4).
- **New retrieval / RAG infrastructure, LangGraph topology change, or a new
  LLM provider dependency** — this proposal assumes none of these and
  authorizes none.
- **Frontend implementation** — out of backend-contract scope entirely.

---

## 21. Compatibility with Existing Contracts  *(contract item 19)*

- **Does not modify** Document 43 (M9 API Contract), Document 59 (M13
  contract), or Document 64 (M14 contract) — purely additive.
- **Reuses `agents/comparison_explanation.py` as the grounding /
  citation-validation engine for `report` mode**, not a fork. §8.3
  establishes that producing `report` mode's `items[]` list requires an
  **additive transformation or schema extension** beyond the engine's
  current single-narrative output — the engine's existing output model and
  C-4's required `items[]` shape are not currently identical, and this
  document does not claim otherwise. That transformation is a compatible,
  additive change to an already-general module; its specific mechanism is
  an architecture-phase decision (§8.3, §22.1 AH-1), not designed here.
- **Deliberately diverges from `ExplainRequest.report_ids`'s flat-list
  shape** in favor of named `baseline_report_id`/`current_report_id` fields
  (§9.2) — justified by C-4's inherent directionality, which M9.1's
  symmetric N-way comparison does not have. This is a new, additive request
  shape, not a breaking change to the existing one.
- **New route family is additive** to the 47-route inventory guard
  (`test_route_inventory.py:143`) — a future implementation updates that
  guard by exactly the four new routes in §10.1, mirroring every prior
  milestone's discipline.
- **Error envelope, citation shape, job/SSE conventions, and the
  `{complete, partial, insufficient_evidence}` state vocabulary are reused
  with zero divergence** from Documents 43 and 64.

---

## 22. Open Contract Decisions

Genuinely unresolved items this proposal could not ground in existing
evidence, listed for explicit CTO decision rather than silently assumed:

| # | Question | Why unresolved | Bounded recommendation |
|---|---|---|---|
| **OCD-1** | Should a third `comparison_type` (filing-to-filing, for risk/MD&A diffing) be added to M15 v1? | No existing engine diffs two M14 filing analyses against each other; INV-IC (Document 64 §8.1) keeps "Important Changes" filing-local by design | **No, for v1.** Revisit as a future, separately scoped extension once real usage shows the two adopted modes (§8) are insufficient. |
| **OCD-2** | Should a `significance`/materiality **label** field be added to each change item? | Equity-research value would favor it, but no existing module computes or scores materiality, and inventing an unbounded scale here would be an unsupported figure | **Omit from v1.** `summary`/`explanation` already carry qualitative weight in prose; add a bounded enum only if a future review shows client need. **Distinct from OCD-6** — this labels an already-eligible item, it does not gate whether the item appears. |
| **OCD-3** | Should `current_report_id`/`current_period_end` ever be allowed to default to "most recent for this ticker" rather than always being explicit? | Evidence-compatible (a deterministic, non-personalized fact, distinct from "last visit") but not adopted here for maximal defensibility (§9.2) | **Keep explicit-only for v1.** Relax only with an explicit, separate CTO decision if usage friction demonstrates a need. |
| **OCD-4** | What is the numeric value of the C-4 job deadline setting? | Operational tuning, not evidenced by any existing figure in the repository | **Not a contract question.** Set at implementation time following the `job_deadline_<kind>_s` convention (§19). |
| **OCD-5** | Should a §20.1-style evidence/validation gate apply to C-4's change-detection quality before it ships? | Document 68 §6 "Validation" item leaves this open; M14's §20.1 gate is a strong precedent for this class of capability, but designing an equivalent gate is beyond a contract proposal | **Yes in principle** (consistent with the M14 precedent); the gate's specific design is deferred to the architecture / validation phase, not fixed here. |
| **OCD-6** | Should a minimum-magnitude filter threshold (e.g. a minimum absolute or percentage delta) gate which mechanically-eligible `period`-mode items are actually returned? | §8.2 imposes no magnitude threshold — every nonzero delta and every appearing/disappearing metric qualifies; no existing repository convention grounds a specific cutoff number | **No threshold for v1** — return every mechanically eligible item (§8.2). **Distinct from OCD-2** — this is about *whether an item appears at all*, not how an appearing item is labeled. Revisit only if real usage shows the unfiltered list is unwieldy. |

None of these blocks contract ratification on its own — each is a bounded,
explicitly flagged gap, not a silent assumption.

### 22.1 Architecture Handoff Items (not CTO contract decisions)

Distinct from the Open Contract Decisions above (which need explicit CTO
resolution), the following are already decided at the contract level — their
*externally observable* requirement is fixed — but their *mechanism* is
properly an architecture-phase concern, not designed here:

| # | Item | What the contract already fixes | What remains open |
|---|---|---|---|
| **AH-1** | `report`-mode narrative `items[]` transformation (§8.3, §11.3) | The required external shape and rule: a list of discrete items, each satisfying the eligibility criteria of §8.3 and cited on both sides (§12) | Whether produced by an extended model-output schema or a deterministic post-generation decomposition of the engine's existing single narrative — including how an internal representation such as `limitations[]` is used, if at all, to detect the evidence-coverage gaps §14.2 describes |
| **AH-2** | Job-result retention between `POST` and `GET` (§16) | No durable, cross-request, per-user comparison-history store is introduced | Which bounded, on-demand mechanism (e.g. the M14 in-process buffer, or another) — evaluated and selected by the architecture phase |

---

## 23. Acceptance Criteria  *(contract item 21)*

A future implementation satisfies this contract when, at minimum:

**Mode exclusivity (§8, §9):**

- `POST /api/companies/{ticker}/changes` rejects a missing/invalid
  `comparison_type` with 422 `validation_error` (§10.2, §15);
- a request missing any field required by its declared `comparison_type`,
  or supplying fields belonging to the *other* mode, is rejected with 422
  `validation_error`;
- a `period`-mode response never contains a `"narrative"` item and a
  `report`-mode response never contains a `"financial"` item — every
  response's `items[]` is category-homogeneous with the request's mode
  (§8.1, §11).

**Reference validation (§9.4, §15):**

- `baseline_report_id == current_report_id` → 422 `validation_error`;
- a `report_id` resolving under a ticker other than the path `ticker` → 404
  `not_found`, indistinguishable from a nonexistent id;
- a `report_id` owned by another user and not `is_sample` → 404 `not_found`,
  indistinguishable from a nonexistent id, checked independently per id;
- `baseline_period_end >= current_period_end` → 422 `validation_error`;
- an unresolvable `(ticker, period_type, statement_type, period_end)` for
  either side → 404 `not_found`.

**Financial qualification and value semantics (§8.2, §11.2):**

- two identical values for the same `provider_label` across both periods
  never produce an item;
- a metric present only in `current` produces a `change_kind: "new"` item
  with `before: null`; present only in `baseline` produces `"removed"` with
  `after: null`;
- `percent_delta` is `null` whenever `before` is `null` or `before.value ==
  0` — never a fabricated infinite/undefined number;
- a `provider_label` present in both periods with different `unit` values
  is excluded from `items[]` and named in `coverage_boundaries`, triggering
  `partial` (§14.1);
- `baseline`/`current` statements with different `currency` values produce
  `insufficient_evidence` (§14.1), not a mixed-currency computed delta;
- financial items are ordered by `metric`, ascending, lexicographic,
  identically across repeated identical requests (§11.4, §17).

**Source shape consistency (§11.2, §11.3):**

- every `"financial"` item's `sources[]` entries are shaped exactly
  `{index, statement_type, period_end, metric}` — never `report_id` or
  `field`;
- every `"narrative"` item's `sources[]` entries are shaped exactly
  `{index, report_id, field}` — never `statement_type` or `period_end`;
- the two source shapes are never mixed within one item or one response.

**Narrative eligibility and citation completeness (§8.3, §12):**

- an emitted narrative item satisfies all three eligibility criteria of
  §8.3 — no item represents a wording-only/noise difference, a vague or
  non-discrete impression, or a claim inferred beyond the report evidence;
- every narrative item's `sources[]` includes at least one entry with
  `report_id == baseline_report_id` and at least one with
  `report_id == current_report_id` — never a single-sided citation;
- a candidate difference with zero grounded citations, or with grounded
  citations from only one side, never appears verbatim as an item — the
  overall `report`-mode result degrades to `insufficient_evidence` (§14.2)
  if no candidate is groundable on both sides, or `partial` (§14.2) if some
  are and some are not, never a fabricated or single-sided claim.

**No-change and state semantics (§13, §14):**

- a `period`-mode comparison where every matched metric is unchanged returns
  `items: [], state: "complete"`;
- a `report`-mode comparison the engine grounds but for which no candidate
  difference satisfies the eligibility rule (§8.3) returns
  `items: [], state: "complete"`;
- both of the above are distinguishable in tests from a response with
  `state: "insufficient_evidence"`;
- only `complete`/`partial`/`insufficient_evidence` are used as `state`
  values — no fourth value, in either mode.

**Error taxonomy (§15):**

- no error response uses a `type` value outside the nine classes in
  `domain/errors.py` — grep-verifiable, zero new exception classes.

**API/route mechanics (§10.3):**

- the create response is exactly `{id, status: "queued", reused: false}`,
  with HTTP `200` — `reused` is `false` on every request, with no exception;
- `prompt_version` is `null` for every `period`-mode response and a
  non-null version string for every `report`-mode response; `schema_version`
  is a non-null string in both modes;
- `GET .../{id}` omits the `changes` key entirely while
  `status ∈ {"queued","running","failed","cancelled"}`, and includes it only
  when `status == "completed"`;
- the SSE stream's completed payload is carried by an unnamed `data:
  <json>\n\n` frame whose body has `node == "final"` (never a distinct SSE
  `event:` type), emitted immediately before the terminal `event: end`
  frame for a completed job; a `failed`/`cancelled` job emits no such frame
  before its terminal `event: end`;
- `cancel` on a terminal job is idempotent (200, unchanged status, no
  error); on a queued/running job it transitions to `cancelled`.

**Infrastructure reuse (§4, §18, §19):**

- the route-inventory guard (`test_route_inventory.py`) is updated by
  exactly the four routes in §10.1, no more, no fewer;
- C-4's jobs participate in the existing `JobStatus` lifecycle and the
  shared `MAX_ACTIVE_JOBS` admission budget, unchanged — whether this is
  realized via a new `JobKind` enum member or another mechanism is an
  architecture-phase decision, not fixed by this contract;
- job records and `reports` references are ownership-checked per §18/§9.4,
  with tests for both the "missing" and "foreign-owned" 404 cases;
- BYOK / SSRF policy is exercised identically to every existing contract
  (custom provider + non-admin → 403; custom `llm_base_url` → SSRF guard).

---

## 24. Non-Authorization / Downstream Governance Gate  *(contract item 22)*

**This document does not ratify itself.** It is a proposal, submitted for
CTO review. It does not authorize:

- M15 API contract ratification (a separate, subsequent CTO act);
- an M15 Architecture Decision Pack, or any architecture decision;
- production code, tests, or route-inventory changes;
- any MongoDB collection, index, schema, or migration;
- any Redis, LangGraph, or retrieval/RAG change;
- any frontend implementation;
- implementation authorization, commit, push, merge, deployment, or release.

**The next legitimate governance gate, if the CTO accepts this proposal, is
this document's own ratification** — a distinct act from drafting it —
followed by a separate M15 Architecture Decision Pack (mirroring
Document 64 → Document 65), then a separate implementation-authorization
decision, then implementation, then commit, then push — each a distinct CTO
act, none collapsed.

---

## 25. Repository / Working-Tree State and Provenance

Recorded by read-only inspection this session. **This is a point-in-time
snapshot observed during the creation of this proposal on 2026-09-04**, not
a claim about repository state at any later reading time. **No `git`
mutation was performed** — no `add`/stage, no `commit`, no `push`, no
`amend`, no `rebase`, no `merge`, no `reset`, no `stash`, no `clean`.

- `HEAD = origin/main = be4949b` (M14 implementation commit), unchanged.
- Document number 70 was verified free before creation (highest existing
  Backend & AI governance document was 69).
- **Revision R1 (2026-09-05)** corrects the ten internal inconsistencies
  identified in CTO review (header revision note) by editing this document
  in place. It creates no new file, modifies no other document, and
  performs no `git` mutation.
- **Revision R2 (2026-09-05)** corrects the eight further re-review
  findings (header revision note) by editing this document in place. It
  creates no new file, modifies no other document, and performs no `git`
  mutation.
- **Revision R3 (2026-09-05)** corrects the four further citation- and
  JobKind-wording findings (header revision note) by editing this document
  in place. It creates no new file, modifies no other document, and
  performs no `git` mutation.
- **Revision R4 (2026-09-05)** corrects one residual mixed-mode ordering
  wording finding (header revision note) by editing this document in
  place. It creates no new file, modifies no other document, and performs
  no `git` mutation.
- Documents 64–69 were read, not modified. Their ratified content is cited,
  not amended, above.
- No source code, test, schema, index, migration, route, handler, LangGraph
  node, prompt, retrieval/RAG code, MongoDB collection, Redis component,
  provider, configuration, infrastructure, or frontend file was created or
  modified. `.gitignore` was not modified.
- Known pre-existing, unrelated working-tree items were not staged,
  modified, renamed, or deleted:
  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/   (untracked, M11 evidence)
  ?? docs/backend_engineering/67_Post_M14_Backend_AI_Roadmap_Reconciliation.md
  ?? docs/backend_engineering/68_M15_Formal_Milestone_Selection_Record.md
  ?? docs/backend_engineering/69_Document68_CTO_Ratification_Record.md
  ```
- This document adds one further untracked file — itself
  (`docs/backend_engineering/70_M15_What_Changed_API_Contract_Proposal.md`).
  It is untracked and not yet version-controlled. Staging or committing it
  is a separate, subsequently CTO-authorized step.

---

**🟡 M15 API CONTRACT PROPOSAL — CTO-REVIEWED, APPROVED FOR RATIFICATION,
NOT YET RATIFIED (REVISION R4). THIS DOCUMENT PROPOSES, BUT DOES NOT RATIFY, EXTERNALLY OBSERVABLE
REQUEST/RESPONSE, CITATION, ERROR, STATE, AND PERSISTENCE SEMANTICS FOR
M15 = C-4 — "WHAT CHANGED SINCE LAST REVIEW." BOTH COMPARISON POINTS
(BASELINE AND CURRENT) ARE ALWAYS EXPLICIT, CALLER-SUPPLIED IDENTIFIERS,
WITH DIRECTION ESTABLISHED BY FIELD POSITION ALONE, NEVER INFERRED
CHRONOLOGY — "LAST REVIEW" IS NOT DEFINED AS "LAST USER VISIT," AND NO
USER/SESSION HISTORY, DURABLE RESEARCH SESSION, WATCHLIST, OR ALERT
MECHANISM IS INTRODUCED IN ANY FORM. "CHANGED" IS BOUNDED TO EXACTLY TWO
MUTUALLY EXCLUSIVE COMPARISON MODES — A `period` MODE (FINANCIAL-STATEMENT
DELTAS, A MECHANICAL ELIGIBILITY RULE WITH NO MAGNITUDE THRESHOLD) AND A
`report` MODE (NARRATIVE DIFFERENCES, A NON-NUMERIC ELIGIBILITY RULE
REQUIRING A SUBSTANTIVE, DISCRETE, BOTH-SIDES-GROUNDED CLAIM) — AND A
SINGLE REQUEST ALWAYS EVALUATES EXACTLY ONE MODE, NEVER BOTH. EVERY ITEM IS
CITED TO THE EVIDENCE THAT ACTUALLY SUPPORTS IT, NOT UNIFORMLY TO "BOTH
REFERENCES": A `period`-MODE `changed` ITEM CITES BOTH SIDES, A `new` ITEM
CITES `current` ONLY, A `removed` ITEM CITES `baseline` ONLY, WHILE A
`report`-MODE NARRATIVE ITEM STILL REQUIRES AT LEAST ONE SOURCE FROM **EACH**
SIDE, UNWEAKENED. `report` MODE REUSES THE EXISTING
`agents/comparison_explanation.py` ENGINE FOR GROUNDING AND CITATION
VALIDATION, ADDITIVELY EXTENDED TO PRODUCE A LIST OF DISCRETE,
BOTH-SIDES-CITED ITEMS — A TRANSFORMATION THIS DOCUMENT REQUIRES BUT DOES
NOT DESIGN. `partial` STATE IS DEFINED AS AN EXTERNALLY OBSERVABLE
EVIDENCE-COVERAGE GAP, NOT AS THE COMPARISON ENGINE'S INTERNAL
`limitations[]` FIELD. `prompt_version` IS `string | null` — NULL FOR
`period` MODE, POPULATED FOR `report` MODE. THE CREATE ENDPOINT'S HTTP
`200` IS STATED AS A VERIFIED, GREP-CONFIRMED REPOSITORY PRECEDENT, NOT AN
ASSUMPTION. THE SSE `final` PAYLOAD IS PRECISELY SPECIFIED AS AN UNNAMED
`data:` FRAME CARRYING `node == "final"`, NOT A NEW SSE EVENT TYPE. THE
GOVERNING CITATION CONVENTION (`sources[]` + `cited_source_indices`, NO NEW
SYNTAX) IS REUSED UNMODIFIED, WHILE THE FINANCIAL SOURCE-REFERENCE SHAPE
IS NEWLY DEFINED FOR EVIDENCE WITH NO PRIOR SHAPE TO REUSE — THE NARRATIVE
SHAPE REUSES THE EXISTING REPORT-CITATION MAPPING UNMODIFIED; NEITHER SHAPE
REPLACES THE OTHER. C-4'S DEDICATED JOB DEADLINE CONFIGURATION IS REQUIRED
WITHOUT PRESCRIBING A SPECIFIC `JobKind` IDENTIFIER OR INTERNAL MAPPING.
THE EXISTING CITATION, ERROR, AND JOB-LIFECYCLE CONVENTIONS ARE REUSED WITH
ZERO NEW ERROR CLASSES AND ZERO NEW CITATION SYNTAX. NO PARTICULAR
PERSISTENCE MECHANISM IS SELECTED
OR RATIFIED; THE CONTRACT REQUIRES ONLY THAT NO DURABLE, CROSS-REQUEST,
PER-USER COMPARISON-HISTORY STORE IS INTRODUCED. NO NEW MONGODB
COLLECTION, INDEX, SCHEMA, OR MIGRATION IS AUTHORIZED. THIS DOCUMENT IS
ARCHITECTURE-NEUTRAL: NO PERSISTENCE MECHANISM, RETRIEVAL STRATEGY,
LANGGRAPH TOPOLOGY, WORKER ARCHITECTURE, OR PROVIDER SELECTION IS DECIDED.
SIX OPEN CONTRACT DECISIONS (§22) AND TWO ARCHITECTURE HANDOFF ITEMS
(§22.1) REMAIN. THIS PROPOSAL DOES NOT RATIFY ITSELF, DOES NOT AUTHORIZE
AN M15 ARCHITECTURE DECISION PACK, DOES NOT AUTHORIZE IMPLEMENTATION, AND
DOES NOT AUTHORIZE ANY COMMIT OR PUSH. NO PRODUCTION CODE, TEST, SCHEMA,
OR INFRASTRUCTURE FILE WAS CREATED OR MODIFIED. NO M14 CONTRACT WAS
CHANGED. NO GIT MUTATION WAS PERFORMED — NO STAGE, NO COMMIT, NO PUSH, NO
MERGE, NO REBASE, NO RESET, NO AMEND. THE NEXT LEGITIMATE GOVERNANCE GATE
IS THIS PROPOSAL'S OWN CTO RATIFICATION.**
