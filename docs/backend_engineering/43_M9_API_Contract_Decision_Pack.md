# 43 — M9 API / Contract Decision Pack

**Status:** 🟢 APPROVED / FROZEN — CTO RATIFIED
**Type:** Contract-design artifact. CTO-approved and frozen — see §25 for exactly what this approval does and does not authorize on its own.
**Depends on (frozen, unmodified):** [41_M9_Pre_Implementation_Architecture_Decision_Pack.md](41_M9_Pre_Implementation_Architecture_Decision_Pack.md) 🟢 APPROVED/FROZEN, [42_M9_Product_Decision_Explanation_Semantics.md](42_M9_Product_Decision_Explanation_Semantics.md) 🟢 APPROVED/FROZEN.

---

## 1. Purpose

Documents 41 and 42 answered *what architecture* (separate capability, existing job infrastructure, existing LLM abstraction) and *what it means* (Level 2 semantic interpretation, grounded, cited, non-recommending). Neither froze the wire contract. This document defines the exact request/response shapes, route(s), identity/deduplication behavior at the API boundary, failure semantics, and citation representation needed to hand this capability to an implementation task with no remaining contract ambiguity — while leaving genuinely implementation-level choices (Mongo collection/index names, repository interfaces, prompt wording, exact model/provider selection, background-task code, frontend code) to that later work, per Documents 41 §18/§19.3 and 42's own scope boundary.

This document does not reopen, alter, or add to any decision Document 41 or 42 already froze. Where this pack repeats a frozen fact, it cites the exact section rather than re-deriving it.

---

## 2. Authoritative Inputs

Verified directly against the current, unmodified text of both frozen documents (not assumed):

**From Document 41** (§10, §11, §12.1–12.3, §13.1–13.2, §14, §19.1): `/reports/compare` stays deterministic and unchanged; no synchronous LLM execution or `generate_explanation` flag on it; comparison explanation is a separate, additive capability; the existing async job infrastructure (`JobKind`/`JobLifecycle`/`JobStore`/`EventBus`) is reused, extended by exactly one new `JobKind` member (already frozen as necessary, §5/§13.1 — this pack does not re-derive that decision, only names the member, §14 below); `chat_json`/`chat_text` are reused verbatim; BYOK/managed-AI inherits the existing policy; MongoDB is the durable artifact store, Redis stays ephemeral job/live state only; comparison identity (resolved report IDs) is distinct from explanation-generation identity (comparison identity + prompt version + schema version + provider + model); same-identity concurrent generation must be deduplicated via lookup-before-create (COMPLETED/RUNNING/FAILED/MISSING); explanation failure must never fail comparison; execution-time authorization/resolution is authoritative, not initiation-time; no report snapshots or versioning.

**From Document 42** (§1–§11): explanation semantic level = Level 2 (Semantic Interpretation), grounded in resolved comparison data; every material claim needs a reachable source; zero grounded citations = failed generation (not a degraded success); sourced causality permitted, unsupported causality prohibited; recommendations absolutely prohibited; no separate materiality-ranking feature; partial data → partial explanation with explicitly named evidence boundaries (Option C), never inferred/estimated/interpolated; reuses the existing `AI Response Card`/`Citation Card`/state-family UX pattern; no remaining product-semantic decisions.

---

## 3. Existing API Patterns (inspected, cited)

Every design choice below reuses one of these, cited by file:line. No new API style is introduced.

| Pattern | Where it already exists | What it establishes |
|---|---|---|
| Job-creation route returns `{"id": ...}` | [`POST /learning/explain`, server.py:1521](../../backend/server.py#L1521) | Minimal creation response; client polls/streams by `id` |
| Unified status+result GET (one endpoint, not two) | [`GET /learning/{id}`, server.py:1563-1579](../../backend/server.py#L1563) | `{"status": ..., "id": ..., "explanation"?: doc}` — result appears only once `status == "completed"` |
| Cancel route, ownership-scoped, idempotent-on-terminal | [`POST /learning/{id}/cancel`, server.py:1524-1536](../../backend/server.py#L1524) | `job is None or job.user_id != user["id"]` → 404 (not 403 — avoids confirming existence to a non-owner); terminal job → no-op, still 200 |
| SSE transport, fully generic | [`infrastructure/streaming/sse.py`](../../backend/infrastructure/streaming/sse.py) | `sse_response(events, stream_name=...)`; unnamed `data: {json}` frames, `: keepalive` comment, terminal `event: end\ndata: {}` — proven against `tests/contract/test_sse_event_shape.py` |
| `TraceEvent` shape | [`domain/events.py:20-24`](../../backend/domain/events.py#L20) | `{node: str, status: str, message?: str, ts?: str}` — the one event shape every stream already emits |
| `final` event convention on stream completion | [`_learning_stream_events`, server.py:1539-1552](../../backend/server.py#L1539) | `{"node": "final", "status": "ok", "explanation": doc}` injected right after the terminal `pipeline/ok` event — this is what `useExplanationJob.ts` already writes into its query cache |
| Request schema: BYOK fields on every AI-generating request | [`GenerateRequest`/`ExplainRequest`, server.py:150-170](../../backend/server.py#L150) | `llm_provider`/`llm_api_key`/`llm_base_url`/`llm_model`, all `Optional[str] = None` |
| Custom-provider admin-gate + SSRF guard | [server.py:1452-1466](../../backend/server.py#L1452) (identical at `/reports/generate`) | `if req.llm_provider == "custom" or req.llm_base_url: require_admin(user)`, then `assert_public_url` |
| Cache-hit / reuse response shape | [`generate_report`'s cache path, server.py:1130-1151](../../backend/server.py#L1130) | `{"job_id": cached["id"], "cached": True}` vs. `{"job_id": job_id}` — the exact existing precedent for "return an existing thing instead of creating a new one," reused for M9.1's dedup response (§7, §15) |
| Inline `[n]` citation markers + indexed source list + cited-index list | [`_postprocess_citations`, `learning_nodes.py:20-28,89-100`](../../backend/agents/learning_nodes.py#L20); mirrored in [`web/features/learning/integration/schemas.ts:45-65`](../../web/features/learning/integration/schemas.ts#L45) | Text carries `[n]` markers; a parallel indexed list carries what each `n` points to; a separate `cited_sources`/`cited_source_indices` list is the *actually-referenced* subset — Law 3 enforcement checks this list is non-empty, not the narrative text |
| Error envelope | [`domain_error_handler`, `app/api/errors.py:32-38`](../../backend/app/api/errors.py#L32) | `{"detail": <message>, "type": <exc.code>}`, status from `DomainError.status_code`; plain `HTTPException` (e.g. 400/422 validation) uses FastAPI's default `{"detail": ...}` with no `type` |
| Full existing `DomainError` taxonomy | [`domain/errors.py:19-117`](../../backend/domain/errors.py#L19) | `NotFoundError`(404), `ValidationError`(422), `ConflictError`(409), `AuthorizationError`(403), `RateLimitedError`(429), `DeadlineExceededError`(504), `InfrastructureError`(502), `LLMProviderError`(502, subclass) — a complete taxonomy already covering every failure category this capability needs |
| `JobStatus` enum (reused verbatim, no new states) | [`domain/models.py:25-30`](../../backend/domain/models.py#L25) | `QUEUED · RUNNING · COMPLETED · FAILED · CANCELLED` |
| `JobKind` enum (extended by exactly one member) | [`domain/models.py:20-22`](../../backend/domain/models.py#L20) | `RESEARCH · LEARNING` today |
| Shared admission control across every job kind | [`application/jobs.py:36-56`](../../backend/application/jobs.py#L36); Document 41 §5 | One `MAX_ACTIVE_JOBS` budget, not per-kind — applies to the new kind automatically, no new rate limiter needed |
| Owner-or-sample visibility scoping | [`compare_reports`, server.py:1656-1673](../../backend/server.py#L1656) | The exact query predicate the explanation job must re-run at execution time (Document 41 §13.2) |
| `AI Response Card`/`Citation Card`/`Confidence Indicator` component family | [`docs/experience_design/Components/08_AI_Components.md`](../experience_design/Components/08_AI_Components.md) 🧊 Frozen | The UX shell every AI surface in the product already uses — Document 42 §10 requires reuse, not redesign |

No frontend consumer exists yet for this capability (unlike Learning, which was built frontend-first against a proposed contract per its own schemas.ts docstring) — there is nothing to avoid breaking, only a pattern to match.

---

## 4. Capability Boundary

Restated from Document 41 §10/§18, unchanged: `POST /reports/compare` performs the deterministic lookup it does today and nothing else. The new capability is a fully separate route family that happens to consume the same `report_ids` shape as `CompareRequest`. Nothing in this pack adds a field, a query parameter, or a behavior to the existing `/reports/compare` route.

---

## 5. Route Decision

Two plausible shapes were evaluated — not chosen by default:

| | **Nested under `/reports/compare/...`** | **New top-level `/comparisons/...` family** |
|---|---|---|
| Precedent | `POST /companies/{ticker}/financials/acquire` (M8, most recently CTO-approved nesting-an-action-under-an-existing-resource pattern in this repo) | `POST /learning/explain` (Learning's own top-level domain family) |
| Visually ties to the data it explains | Yes — same `compare` path segment | No — reads as an unrelated new resource |
| Implies a new resource collection that doesn't otherwise exist | No | Yes — there is no `GET /comparisons`, no comparisons collection; only this one sub-capability would exist under it |
| Path depth | 4 segments at most (`/reports/compare/explain/{id}/stream`) — same depth as the M8 precedent | 3 segments (`/comparisons/explain/{id}/stream`) |
| Consistency with "separate capability, tied to compare's data" (Document 41 §8, §10) | Directly expressed in the URL | Requires the reader to already know the relationship |

**Recommendation: nest under `/reports/compare/`.** It matches the most recently established convention in this exact codebase (M8's action-under-resource nesting) rather than reaching for Learning's older top-level-domain shape, which was appropriate when Learning was its own first-class IA domain — comparison explanation is explicitly *not* that; it is data-dependent on `/reports/compare`'s own output (Document 41 §12.2's comparison identity = the same resolved report IDs). Nesting keeps the routes' names honest about that dependency without implying a resource collection that doesn't exist.

**Frozen route set (4 new routes, mirroring Learning's own 4-route shape exactly):**

```text
POST   /api/reports/compare/explain
GET    /api/reports/compare/explain/{id}
GET    /api/reports/compare/explain/{id}/stream
POST   /api/reports/compare/explain/{id}/cancel
```

---

## 6. Request Contract

**`POST /api/reports/compare/explain`**

- **Authentication:** `current_user` session dependency — identical to every other route.
- **Authorization:** owner-or-sample scoping, re-run against `report_ids` (Document 41 §4, §13.2) — a fast, non-authoritative check at this layer (see §16); the authoritative check happens at execution time.
- **Request body** (mirrors `CompareRequest` + the existing BYOK field set verbatim — no new field shape invented):

| Field | Type | Required | Notes |
|---|---|---|---|
| `report_ids` | `list[str]` | **required** | `min_length=2, max_length=4` — identical constraint to `CompareRequest` (server.py:1646-1647); this is the comparison identity input (Document 41 §12.2) |
| `llm_provider` | `str \| None` | optional | Mirrors `GenerateRequest`/`ExplainRequest` |
| `llm_api_key` | `str \| None` | optional | Never persisted (Document 41 §15, unchanged) |
| `llm_base_url` | `str \| None` | optional | Same admin-gate + SSRF guard as `/reports/generate`/`/learning/explain` applies unchanged if set |
| `llm_model` | `str \| None` | optional | Mirrors existing fields |

No report content is sent in the body — only `report_ids`. The job resolves the actual report documents itself, server-side, at execution time (Document 41 §13.2's re-resolution flow) — this is why no report body is transmitted through this API: identity, not content, crosses the wire.

---

## 7. Initial Response Contract

**`POST /api/reports/compare/explain` → 200**

| Field | Type | Required | Nullability |
|---|---|---|---|
| `id` | `str` | required | never null |
| `status` | `str` (enum: `"queued" \| "running" \| "completed" \| "failed" \| "cancelled"`) | required | never null — the existing `JobStatus` enum values verbatim, no new value |
| `reused` | `bool` | required | never null |

`reused: true` whenever `id`/`status` correspond to a pre-existing job or artifact for the same explanation-generation identity (Document 41 §12.2, §14) rather than a freshly created job — reusing the exact existing precedent of `generate_report`'s `{"job_id": cached["id"], "cached": True}` shape (§3), generalized to the four-state dedup outcome (§15). The client's next step is identical either way: poll `GET .../{id}` or open `GET .../{id}/stream` — this endpoint does not require the client to branch on `reused`.

---

## 8. Job Status Contract

**`GET /api/reports/compare/explain/{id}` → 200** (one endpoint serves both "status" and "final result," exactly matching `GET /learning/{id}`'s existing merged shape — not two separate endpoints):

| Field | Type | Required | Nullability |
|---|---|---|---|
| `id` | `str` | required | never null |
| `status` | `str` (same enum as §7) | required | never null |
| `explanation` | `ExplanationResult` (§9) | optional | present **only** when `status == "completed"`; absent (not null) otherwise — matches `GET /learning/{id}`'s existing `.optional()` Zod shape |

**404** (`NotFoundError`) if `id` doesn't exist or doesn't belong to the caller — identical ownership-scoping convention to `GET /learning/{id}`/`cancel_explanation` (§3).

---

## 9. Final Explanation Contract

The smallest structure that can still enforce Document 42's citation/grounding standard mechanically — deliberately reusing Learning's existing flat-narrative-plus-indexed-sources shape (§3) rather than inventing a heavier structured "claims" tree. A structured per-claim breakdown was considered and rejected as over-engineering: Learning's existing `_postprocess_citations` already proves that a flat text with `[n]` markers, a parallel indexed source list, and a separate "actually cited" index list is sufficient to mechanically verify Law 3 (non-empty citation set) without parsing claim-level structure.

**`ExplanationResult`:**

| Field | Type | Required | Nullability | Notes |
|---|---|---|---|---|
| `id` | `str` | required | never null | same value as the job `id` — justified below, not a silent assumption |
| `comparison_report_ids` | `list[str]` | required | never null, may be a subset of the requested `report_ids` | the execution-time authoritative resolved set (Document 41 §13.2) — **not** an echo of the request |
| `narrative` | `str` | required | never null, may be empty only if `cited_source_indices` is also empty **and** `status` is not `"completed"` (i.e. never for a completed result — see §11) | plain-language Level 2 interpretation; inline `[n]` markers, same convention as `draft_report`/Learning's `explanation` |
| `sources` | `list[ExplanationSource]` (§10) | required | never null; non-empty for any `"completed"` result | indexed source list the narrative's `[n]` markers reference |
| `cited_source_indices` | `list[int]` | required | never null; **must be non-empty** for `status == "completed"` (Document 42 §7, Law 3 — enforced identically to Learning's `cited_sources`) | 1-based indices into `sources`, in order of first appearance |
| `limitations` | `list[ExplanationLimitation]` (§11) | required | never null; may be empty | empty list = full coverage; non-empty = Document 42 §11's Option C boundaries |
| `evidence_completeness` | `str` (enum: `"complete" \| "partial"`) | required | never null | `"partial"` iff `limitations` is non-empty — explicit, not left for the client to derive, per the instruction not to collapse states |
| `generated_at` | `str` (ISO-8601) | required | never null | matches every existing `created_at`/`completed_at` convention |

**Job ID vs. explanation artifact ID — verified against the repository, not silently retained.** `ExplanationResult.id` deliberately equals the job `id`, and this is not an accidental coupling of two different domain concepts: it is the exact, already-established pattern both existing AI-generating capabilities in this repository use. `_run_pipeline` persists `report_doc = {"id": job_id, ...}` (`server.py:949`); `_run_explanation` persists `explanation_doc = {"id": job_id, ...}` (`server.py:1383`); both `db.reports`/`db.explanations` documents are looked up by that same `job_id` value (`get_report`, `get_explanation`, §3). The `Job` (Redis-resident, ephemeral, §3) and the durable Mongo artifact are architecturally distinct records — this pack does not conflate them — but they intentionally *share one identifier* across this entire codebase, letting a single opaque `id` address "the execution" while it's running and "the result" once it's done, with no lookup translation at any API boundary. Diverging from that here (introducing a separate `explanation_id` distinct from the job `id`) would be the actual novelty — inventing a second identifier scheme this repository has never used, for no behavioral benefit, since nothing in §14/§15 requires the client-visible `id` to differ from the job that produced it. **Kept as-is, justified by repository precedent rather than silently retained.**

This is unrelated to, and must not be confused with, the *canonical explanation identity* (§14.1) — that is an internal, never-exposed lookup key used to find *which* `id` (if any) already exists for a given set of inputs. The `id` field here is the address of one specific job/artifact record; the canonical identity is what the server uses to decide which record's `id` to return.

---

## 10. Citation Contract

**Citation identifier:** a 1-based integer index into `ExplanationResult.sources`, referenced inline in `narrative` as `[n]` — the exact existing marker convention (§3), not a new citation syntax.

**`ExplanationSource`:**

| Field | Type | Required | Notes |
|---|---|---|---|
| `index` | `int` | required | 1-based; matches the `[n]` marker it backs |
| `report_id` | `str` | required | one of `comparison_report_ids` — the compared report this claim is grounded in |
| `field` | `str` (enum: `"extracted_data" \| "sentiment_analysis" \| "scorecard" \| "report"`) | required | which part of that report's own already-grounded data the claim draws on; `"report"` is used when the attribution is whole-report-level rather than one specific field |

**Relationship between claim and citation:** every `[n]` marker in `narrative` must have a corresponding entry in `sources` at that index, and every index actually used by the narrative must appear in `cited_source_indices` — this is a mechanically checkable invariant (marker set ⊆ `sources` indices ⊆ verifiable-report-membership), not a prose convention to trust.

**What this contract mechanically enforces, precisely stated — a three-tier hierarchy, not a weakening of Document 42's rule:**

```text
Document 42 (semantic/product requirement, frozen, unmodified by this pack):
    every factual/material claim must be grounded and cited — the standard
    a generation is judged against, full stop.

Document 43 (this pack — wire representation, mechanically checkable):
    citation indices must be structurally valid (every [n] marker resolves to
    a sources[] entry; every used index appears in cited_source_indices, §10);
    a completed result must contain at least one grounded citation
    (cited_source_indices non-empty, §9, §11) — the coarsest invariant the
    wire schema can prove without a per-claim structure.

Implementation (deferred, §22 — not decided here):
    prompt design + structured-output validation + post-processing must
    enforce the stronger, Document-42-level claim-by-claim requirement as far
    as technically achievable — this is where the gap between "non-empty
    citations" and "every claim cited" is meant to be closed, not at the
    wire-schema layer.
```

**A schema-valid response with floating, uncited factual claims is still an invalid generation from the product perspective** — passing this contract's structural checks (non-empty `cited_source_indices`, valid index references) is necessary but not sufficient proof of Document 42 §3/§7 compliance. This pack does not weaken Document 42's rule; it states plainly that the wire schema alone cannot fully prove it, and assigns the remainder to the implementation layer rather than pretending a heavier schema would close the gap for free. A per-sentence structural checker was considered and rejected as over-engineering (it would require the heavier per-claim structure explicitly rejected above, for marginal mechanical gain over prompt+validation+post-processing already doing that work); this is a deliberate boundary choice, not an oversight.

**Behavior when evidence is unavailable:** there is no "citation with an empty/null target." A gap is never represented as a citation — it is represented as an `ExplanationLimitation` entry (§11), a structurally distinct concept. This is deliberate: conflating "cited but unavailable" with "no citation possible" would blur exactly the boundary Document 42 §11 requires to stay explicit.

**Reuse, not a new system:** the existing `Citation Card`/`SourceReference` component (§3; `docs/design/09_Component_Inventory.md`: "source label, target") already supports `{label, target}` — for this capability, `target` resolves to the cited report (e.g. its existing Report View), which the client already has full access to and which already carries its *own* deeper citation chain back to the original filing excerpt (established by Company Research, SCR-06) — this pack does not need to chain that deeper, per-filing citation through the comparison-explanation API at all; citing "which compared report, which part of it" is the correct grounding depth for a capability whose own grounding input (Document 41 §13.2) is the compared reports' *extracted* data, not raw filing text.

---

## 11. Partial Evidence Contract

Three states, kept explicitly distinct per Document 42 §11 and the brief's own instruction not to collapse them:

| State | `status` (job) | `explanation` present? | `evidence_completeness` | `limitations` |
|---|---|---|---|---|
| **Complete** | `"completed"` | yes | `"complete"` | `[]` |
| **Partial** | `"completed"` | yes | `"partial"` | non-empty |
| **Zero-evidence failure** | `"failed"` | no (field absent) | n/a | n/a |

**`ExplanationLimitation`:**

| Field | Type | Required | Nullability | Notes |
|---|---|---|---|---|
| `report_id` | `str \| None` | required | nullable | the specific member the gap applies to; `null` only in the rare case a gap isn't attributable to one specific member |
| `metric` | `str` | required | never null | free-text label (e.g. `"operating margin"`) — not a closed enum, since compared metrics vary by report shape, matching how `extracted_data`'s own fields are already named as plain strings, not an enum, elsewhere in this codebase |
| `reason` | `str` | required | never null | short, plain-language (e.g. `"not available for this reporting period"`) — never raw provider/internal detail, per the existing redaction convention (§3, Document 41 §15) |

**Zero-evidence failure is not an HTTP error.** Exactly like Learning's existing precedent ("the route layer treats an empty `explanation` + empty `cited_sources` as a failed job, not a success with no sources" — `_run_explanation`'s docstring, §3): the `POST` call itself always succeeds; a job that cannot ground *any* claim reaches `status: "failed"` with no `explanation` field, discovered via `GET .../{id}` or the terminal SSE event — not a 4xx/5xx on the creation call, and not a 200 with an empty/placeholder explanation object.

---

## 12. Failure Contract

| Scenario | Mechanism | HTTP status | Envelope |
|---|---|---|---|
| Not authenticated | existing session dependency | 401 | existing auth envelope, unchanged |
| Caller doesn't own / can't see the job (`GET`/`cancel`) | `NotFoundError` | 404 | `{"detail": ..., "type": "not_found"}` |
| `report_ids` fails length/shape validation | Pydantic `RequestValidationError` (existing app-wide handler, server.py:1683-1691) | 422 | existing redacted-validation-error shape |
| Fewer than 2 of the requested reports are visible/exist *at request time* | `ValidationError` or existing 404-style response — mirrors `compare_reports`'s own "fewer than 2 reports found" (server.py:1671-1672) | 404 | `{"detail": "fewer than 2 reports found"}` — reused verbatim, same message, same status |
| Admission budget exceeded (`MAX_ACTIVE_JOBS`) | `RateLimitedError` (existing, `JobLifecycle.start`) | 429 | `{"detail": ..., "type": "too_many_jobs"}` — unchanged, applies automatically (§3) |
| Duplicate/already-running generation for the same identity | **not a failure** — §7/§15's `reused: true` response | 200 | n/a |
| Custom-provider request from a non-admin | `require_admin`'s existing 403 | 403 | existing shape, unchanged |
| Provider failure during generation | `LLMProviderError` inside the job → `JobLifecycle.fail(job_id, safe_message)` | n/a (surfaces as job `status: "failed"`, not an HTTP error on a still-open request) | job's `status` field only — no raw provider text ever reaches the client (Document 41 §14, §15, unchanged) |
| Malformed/unvalidatable model output | `chat_json`'s `ValueError` (Document 41 §5) → same `JobLifecycle.fail` path | n/a | same as above |
| Job deadline exceeded | `DeadlineExceededError`/`TimeoutError` → `JobLifecycle.fail` | n/a | job `status: "failed"`, generic message — mirrors `_run_pipeline`'s existing LG-11 handling |
| Zero grounded citations | see §11 | n/a | job `status: "failed"`, no `explanation` field |
| Client cancels | see §13 | n/a | job `status: "cancelled"` |
| Internal infrastructure failure (Mongo/Redis) | `InfrastructureError` | 502 | existing shape, unchanged |

**Invariant, restated and enforced by this table:** nothing in this contract can cause `/reports/compare` itself to fail, slow down, or change shape — every failure mode above belongs to the separate explanation job's own `status` field or, for pre-job request-level failures, to the new `POST` endpoint's own response — never to `/reports/compare`.

---

## 13. Cancellation Contract

**`POST /api/reports/compare/explain/{id}/cancel`** — mirrors `POST /learning/{id}/cancel` (§3) exactly, no new semantics invented:

- **Who may cancel:** the job's owner only — `job is None or job.user_id != user["id"]` → 404 (not 403, matching the existing precedent's non-disclosure choice).
- **Already completed / already failed / already cancelled:** no-op — `JobLifecycle.cancel()` is already idempotent on a terminal job (Document 41 §5); returns the job's current terminal `status` unchanged, still 200.
- **Running:** the tracked `asyncio.Task` is cancelled and `JobLifecycle.cancel()` marks the job `"cancelled"`, publishing the existing warn event — identical to every other cancellable job today.
- **Guarantee, stated honestly (per this task's own instruction not to overstate it):** cancellation guarantees the result will not be published or persisted, and that the job reaches a terminal state promptly. It does **not** guarantee the in-flight provider HTTP call terminates early — `chat_text`'s blocking SDK call runs inside `asyncio.to_thread`, and Python cannot forcibly interrupt a running OS thread; `task.cancel()` stops the *awaiting* coroutine at its next `await`, not the thread already executing the provider request. This is an existing, unchanged limitation of `chat_text`'s architecture (Document 41 §5) — this capability does not need a stronger guarantee than Research/Learning already have, and this pack does not invent one.

**Response:**

| Field | Type | Required |
|---|---|---|
| `id` | `str` | required |
| `status` | `str` (same enum as §7) | required |

---

## 14. Identity Contract

Restated verbatim from Document 41 §12.2 (not modified, not re-derived):

```text
comparison identity     = resolved report IDs
explanation identity    = comparison identity + prompt version + schema version
                           + provider identity + model identity
```

**Client-visible identity:** the `report_ids` array in the `POST` request body. The client never computes, sees, or submits a hash — it interacts purely through the opaque `id` string the API returns (§7), identical to how `job_id` works for Research and Learning today. This is unchanged by the corrections below — the client's role in identity is exactly as thin as it was.

### 14.1 Identity coherence — the four-stage pipeline (corrected)

Document 41 §12.2 freezes `comparison identity = resolved report IDs` as a single conceptual line, but three genuinely different points in this capability's lifecycle can each produce a different resolved set for the *same* request. Left undifferentiated, "resolved report IDs" is ambiguous about *which* resolution is canonical. It is exactly one pipeline, in this order, and only the last stage is ever durable:

```text
requested report IDs
        ↓                (submitted in the POST body, §6 — never itself the identity)
admission-time authorized/resolved IDs
        ↓                (the POST-time fast-fail check, §16 — a UX convenience, never authoritative,
                          never persisted, never used to key an artifact)
execution-time authorized/resolved IDs
        ↓                (the job's own re-run of compare_reports's owner-or-sample check, §16 —
                          AUTHORITATIVE; this is Document 41 §12.2's "comparison identity", precisely)
canonical durable explanation identity
                         (execution-time resolved IDs + prompt version + schema version + provider
                          identity + model identity — Document 41 §12.2's "explanation identity",
                          precisely; the only identity ever used to key a durable artifact or a
                          dedup lookup)
```

**The durable explanation artifact is canonically associated with the execution-time resolved report set — never the requested set, and never any admission-time intermediate.** This resolves what was previously left implicit: "resolved report IDs" in Document 41 §12.2 means the execution-time stage of this pipeline, exclusively.

**Required invariant (frozen by this pack, not an implementation suggestion):**

> If execution-time resolution changes the effective report set relative to what was requested or admitted, the job must reconcile that change without allowing two durable explanation artifacts to simultaneously claim the same canonical explanation identity.

Concretely: a job admitted against a nominal set of report IDs may, at execution time, discover a narrower authorized set (§16 — a report became inaccessible between request and execution). The canonical explanation identity that job's *artifact* is ultimately keyed under must reflect that narrower, execution-time set — not the originally requested one. Because a second, independent request could concurrently resolve to that *same* narrower execution-time identity, the reconciliation this invariant requires is exactly the same lookup-before-create discipline §15 already establishes, applied at the point execution-time resolution is known, not only at admission time. **The exact mechanism that enforces this** — a conditional write, a lock, a transaction, a redo-the-lookup-post-resolution step, or something else — **is explicitly not decided here** (§22); the invariant is frozen, the mechanism is not.

**The client does not compute, see, or participate in canonical identity at any stage.** It submits `report_ids` (stage 1) and receives an opaque `id` (§7) — every later stage of this pipeline is entirely server-side and invisible to the client, including when reconciliation (above) causes the client's request to resolve to a job/artifact it did not itself trigger (§15).

### 14.2 Internal persistence identity

The composite key of stage 4 above (execution-time resolved IDs + prompt/schema/provider/model versions), used server-side for the lookup-before-create dedup check (§15) and for the reconciliation invariant (§14.1). Its exact representation (a derived hash, a set of indexed Mongo fields, a lock, a transaction, or something else) is explicitly out of scope for this pack (§22) — Document 41 §12.2 already states the hashing/storage representation is an implementation detail, and this pack does not narrow that further than necessary to define the client-observable behavior in §15.

**`JobKind`:** Document 41 §5/§13.1 already froze that exactly one new member is required. This pack names it: `JobKind.COMPARISON_EXPLANATION` — the same identifier Document 41 itself used as its own illustrative example (§7). No second new `JobKind` is introduced.

---

## 15. Deduplication Semantics

The observable behavior at the API boundary — not the internal Mongo mechanism (explicitly out of scope, §22). Identity match (§14) is a *necessary* condition for reuse in every case below; for a **complete** result it is also *sufficient*, for a **partial** result it is not (frozen rule, §15.1).

| Internal state for this explanation identity | `POST` response | Client-observable behavior |
|---|---|---|
| **COMPLETED**, `evidence_completeness: "complete"` | `{"id": <existing id>, "status": "completed", "reused": true}` | `GET .../{id}` immediately returns the existing `ExplanationResult` — no new generation. Always reusable on identity match alone. |
| **COMPLETED**, `evidence_completeness: "partial"` | `{"id": <existing id>, "status": "completed", "reused": true}` **if** the evidence state that produced it is still materially equivalent; otherwise treated as **MISSING** (fresh generation) | See §15.1 — reuse is conditional, not automatic, even though identity matches |
| **RUNNING** job exists | `{"id": <existing id>, "status": "running" \| "queued", "reused": true}` | Client polls/streams the *same* `id` as whoever initiated it; no second generation is started |
| **FAILED** prior attempt exists | `{"id": <new id>, "status": "queued", "reused": false}` | Treated identically to **MISSING** — a fresh attempt is created automatically. Resolves Document 41 §14's explicitly deferred "controlled retry" question: no existing convention in this repository blocks retrying a prior generation failure (`generate_report`'s own cache-hit logic only ever matches a *completed* report, §3 — a failed report generation is never blocked from a fresh attempt), so this pack extends that same convention rather than inventing a new one. "Controlled" is satisfied by the existing, unchanged `MAX_ACTIVE_JOBS` system-wide admission ceiling (§3) — no new per-identity retry limiter is introduced. |
| **MISSING** — no prior job/artifact | `{"id": <new id>, "status": "queued", "reused": false}` | Standard creation path |

**Where the client receives the same response shape for different internal cases (as the brief requires this to be stated explicitly):** COMPLETED (complete or reusable-partial) and RUNNING all return `reused: true` with the *same field shape* — the client cannot distinguish "an already-finished explanation," "someone else's still-running one," or "a reused partial result" from the `POST` response alone; it must call `GET .../{id}` (or stream) to learn which, exactly as it would for a freshly created job. This is intentional, not an oversight: the client's next action (poll/stream by `id`) is identical in every case, so no additional signal is needed at this layer.

### 15.1 Partial-result reuse — frozen rule (not left open)

A **complete** explanation (§11, `evidence_completeness: "complete"`) is reusable for the same explanation identity unconditionally — identity match alone is sufficient, per the table above.

A **partial** explanation (`evidence_completeness: "partial"`) may be persisted and returned on a subsequent identity match, but **must not be assumed to remain valid forever merely because the report-ID identity is unchanged.** It is reusable only while the evidence state that produced it remains materially equivalent. If newly available evidence would change that evidence state (for example: a report that was itself still generating, or lacked a specific field, at the time the partial explanation was produced, has since completed or gained that field), the system must permit a fresh generation rather than permanently returning the stale partial artifact.

This is a frozen **behavioral requirement**, not a vague open question — but the exact mechanism that determines "materially equivalent evidence state" (a version/hash of the resolved reports' relevant fields, a freshness timestamp comparison, or something else) is explicitly **not** decided here (§22, implementation detail) — mirroring exactly how Document 41 §12.2 already treats the broader identity's hashing/storage representation as an implementation concern separate from the frozen requirement that it exist and be checked.

### 15.2 POST-time lookup vs. execution-time canonical identity

The dedup table above performs its lookup at `POST` time, but §14.1 defines the canonical explanation identity in terms of *execution-time* resolved report IDs. This is not a contradiction, and the relationship between the two is frozen here rather than left implicit:

Admission-time resolution (§16) is sufficient for the *initial* deduplication lookup (§15's table) because it uses the exact same authorization/resolution predicate that is rerun at execution time (§14.1, §16) — not an approximation of it. However, the admission-time result is provisional: it does not become the canonical durable explanation identity merely because it was used to perform that initial lookup. Execution-time resolution remains authoritative, exactly as §14.1 and §16 already establish. If execution-time resolution differs from what admission-time resolution found, the implementation must reconcile the job against the canonical execution-time identity (§14.1) before publishing or persisting the final artifact — the initial lookup's outcome is a starting point for admission and an early opportunity to attach to existing work, not a commitment that survives a divergent execution-time result.

This preserves every invariant already frozen elsewhere in this pack: `POST` performs a fast admission-time authorization/resolution check (§16) and may use its result for the initial dedup lookup (§15); execution-time resolution remains authoritative (§13.2/§16); the durable artifact's identity is based on execution-time resolved IDs, not admission-time ones (§14.1); concurrent requests must not produce two durable artifacts claiming the same canonical explanation identity, whether or not their admission-time lookups agreed (§14.1's reconciliation invariant, unchanged). The exact mechanism for this reconciliation — a re-check immediately before publish, a conditional write keyed on the execution-time identity, or something else — remains implementation detail (§22), not decided here.

---

## 16. Authorization / Execution-Time Resolution

Restated and made contract-explicit from Document 41 §13.2:

- **At `POST` time:** the `report_ids`/owner-or-sample check (§6) is a fast-fail convenience — cheap, matches the existing "no filings ingested" 400-style precedent (§3) — **not** the authoritative check.
- **At execution time:** the job independently re-runs the exact same owner-or-sample query `compare_reports` itself uses (Document 41 §13.2) against the `report_ids` it was given, never trusting the `POST`-time result. If the resolved, authorized set has changed by execution time (a report was deleted, or visibility changed):
  - The job does **not** silently use stale or now-unauthorized content — it uses only what execution-time resolution actually authorizes.
  - No snapshot is introduced (Document 41 §13.2, unchanged) — `comparison_report_ids` in the final `ExplanationResult` (§9) reflects the *execution-time* resolved set, which may be a strict subset of the originally requested `report_ids`.
  - If the resolved set narrows below 2 reports, the job fails using the exact same message/status `compare_reports` itself already uses for this case ("fewer than 2 reports found," §12) — not a distinguishable "you lost access" message, which would create a cross-tenant existence oracle. This mirrors `compare_reports`'s own existing comment that a visibility exclusion is "not necessarily cross-tenant... looks identical" to a nonexistent id (server.py:1663-1670, §3) — the same non-disclosure posture, applied to the new capability.

---

## 17. SSE / Streaming Contract

**Decision: both** status polling (`GET .../{id}`) and SSE (`GET .../{id}/stream`) are offered, exactly mirroring how Research and Learning already offer both simultaneously — not an either/or choice introduced for this capability.

**Why SSE is warranted, not merely available:** Document 42 §10 requires this capability to present through the existing `AI Thinking → AI Streaming → Complete` state family, and the Constitution's AI Experience Philosophy (§9, cited in Document 42) already establishes "AI should stream naturally" as a product-wide expectation, not a Research/Learning-specific one. Reusing `sse_response()` (§3) costs zero new code — it is fully generic over `EventBus.subscribe(job_id)`, and a new `JobKind` value participates in that machinery automatically (Document 41 §5).

**Frozen event shapes (reusing the existing `TraceEvent`/`final` conventions verbatim, §3):**

- Progress events: `{"node": str, "status": str, "message"?: str, "ts"?: str}` — the same shape every existing pipeline already emits.
- Terminal completion: a `final` event carrying the full result, exactly mirroring Learning's own convention (server.py:1552) —
  `{"node": "final", "status": "ok", "explanation": <ExplanationResult, §9>}`.
- Terminal SSE framing: unchanged, `event: end\ndata: {}\n\n` (§3) — no modification to `infrastructure/streaming/sse.py`.
- Keepalive: unchanged, `: keepalive\n\n` comment (§3).

No new SSE mechanism, framing rule, or event field is introduced — every shape above is a direct instantiation of an existing, generic convention.

---

## 18. Frontend Consumption Contract

Documentation only — no frontend code is designed or implemented here (out of scope, §22). What a future frontend implementation will need to consume, mapped to the already-frozen, already-shipped component family (Document 42 §10, `08_AI_Components.md`):

- `POST .../explain` → `id`. Render the `Thinking State` component (§3) immediately.
- Either poll `GET .../{id}` or open `GET .../{id}/stream` — both are valid per §17; which one a given surface uses is a frontend implementation choice, not frozen here.
- While `status` is `"queued"`/`"running"`: `Thinking State` → `Streaming Response` component, exactly as every other AI surface already renders (§3).
- On `status: "completed"`: render an `AI Response Card` variant (§3) with `explanation.narrative`, resolving each `[n]` marker against `explanation.sources` through the existing `Citation Card`/`SourceReference` component (target = the cited `report_id`'s existing Report View, §10); if `evidence_completeness == "partial"`, render `explanation.limitations` using the existing `Evidence Card` "Partial (some unavailable, flagged)" state (§3, §11) — not a new UI state.
- On `status: "failed"`: render the existing `Insufficient-evidence` state already defined for `AI Response Card` (§3, Document 42 §10) — "say so honestly, offer what is possible," not a bespoke error UI.
- On `status: "cancelled"`: mirrors whatever existing pattern Research/Learning already use for a cancelled job (out of scope to re-specify — no new behavior needed here).

---

## 19. Security

- **Authentication:** `current_user`, unchanged (§6).
- **Authorization/report visibility:** owner-or-sample scoping, re-verified at execution time as authoritative (§16) — a caller can never obtain explanation content grounded in a report they cannot access, because the job itself cannot resolve such a report in the first place.
- **BYOK/Managed AI policy:** inherits the existing policy verbatim (Document 41 §13.1, §19.1) — the same fields, the same `set_llm_context`/`reset_llm_context` threading, the same custom-provider admin-gate + SSRF guard (§6, §3). No new credential-handling path.
- **Rate limiting:** the existing shared `MAX_ACTIVE_JOBS` admission control applies automatically to the new `JobKind` (§3, §14) — no new rate limiter is introduced. Whether a *stricter*, capability-specific limit is warranted is noted as a genuinely open question (§23) — not decided here, since no existing convention in this repository has a per-capability-kind limiter to reuse.
- **Sensitive data / provider internals:** never exposed — every failure path (§12) surfaces only a redacted, generic message, matching the existing convention exhaustively (Document 41 §5, §15).
- **Source/citation access:** a citation's `target` (§10) only ever resolves to a report the caller already has access to, by construction — the explanation cannot cite a report outside its own `comparison_report_ids`, which is itself execution-time-authorized (§16).

---

## 20. Observability

Required observable events/attributes — **no metric names are frozen here** (per the brief's own instruction and Document 41 §16's existing deferral); this section states *what* must be observable, not the Prometheus/OTel implementation:

- **Request received:** the new `POST` endpoint's own request, distinguishable from `/reports/compare`'s existing requests by route (automatic, standard HTTP access logging — no new instrumentation needed).
- **Job admission:** already automatic via the existing `jobs_active`/`MAX_ACTIVE_JOBS` instrumentation once `JobKind.COMPARISON_EXPLANATION` exists (§3, §14) — no new code.
- **Execution start / completion / failure:** an outcome signal distinguishing `completed (complete)` / `completed (partial)` / `failed`, at minimum labeled by the new job kind — exact metric name/shape deferred to implementation (Document 41 §16 already establishes this deferral pattern; this pack extends it, doesn't reopen it).
- **LLM invocation:** already fully automatic via `chat_json`→`chat_text` (Document 41 §5) — `llm_calls_total`/`llm_tokens_total` require zero new code.
- **Latency:** job duration, mirroring the existing `pipeline_duration_seconds` pattern's *intent* — exact metric deferred (Document 41 §16).
- **Partial evidence:** whether a completed result had `evidence_completeness == "partial"` should be observable (at minimum loggable), so a systemic grounding-data problem is visible in aggregate — exact mechanism deferred.
- **Cancellation:** already automatic via the existing `JobLifecycle.cancel()` event publication (§3) — no new code.

---

## 21. API Compatibility

Explicit, unambiguous statement, restated from Document 41 §11/§19.1 and unmodified by this pack:

- `POST /reports/compare` remains **completely unchanged** — no field added, removed, or retyped; no new query parameter; no new status code; no behavior change of any kind.
- No existing response field, anywhere in the API, is modified by this pack.
- No synchronous AI work is added to any existing route.
- The new capability (§5–§17) is 100% additive — 4 new routes, zero modified routes.
- **Route count arithmetic** (for the eventual `test_route_inventory.py` update, not performed here — tests are explicitly out of scope, §22 below), stated precisely so no intermediate number is mistaken for current or already-approved:
  - **38** — the current approved route count, today, unmodified by anything in this pack.
  - **37** — the expected count *after* `/reports/rescore` is independently removed (Document 41 §17), which is its own already-ready, separately-authorized piece of work, not contingent on this pack.
  - **41** — the expected count once both `/reports/rescore` is removed and the four M9.1 routes are live in `test_route_inventory.py`. This pack's contract-level approval (§25) ratifies the route *shape*, not the route *count* by itself — 41 becomes the actual approved-route-inventory number only once the route-inventory contract test itself is updated to reflect it (a step this pack does not perform, §22), independent of and not automatically implied by this document's own approval status.

---

## 22. Out of Scope

This pack does **not** decide, and none of the following is frozen by it:

- Exact MongoDB collection name, indexes, or repository interface (Document 41 §12.1, §19.3 already deferred this).
- Prompt wording or structure.
- Exact model selection or model tier.
- Exact provider defaults (beyond the existing BYOK field pass-through, §6).
- `chat_text`'s retry-loop internals (unchanged, reused verbatim per Document 41 §5).
- SSE implementation code (the framing/event *shapes* are frozen, §17; the code that emits them is not written here).
- Frontend implementation of any kind (§18 documents the contract to consume, not the component code).
- Background-task/job-runner implementation code.
- `/reports/rescore` deletion (Document 41 §17, unaffected — a wholly separate, already-ready piece of work).
- The internal identity-hashing/persistence mechanism (§14.2).
- The exact mechanism that enforces §14.1's canonical-identity reconciliation invariant (a conditional write, a lock, a transaction, a redo-the-lookup step, or something else) — the invariant is frozen, the mechanism is implementation detail, not a contract ambiguity.
- The exact mechanism that determines "materially equivalent evidence state" for partial-result reuse (§15.1) — a version/hash of the resolved reports' relevant fields, a freshness comparison, or something else. The *behavioral rule* (partial results are conditionally, not unconditionally, reusable) is frozen; this is purely how that condition gets checked.

---

## 23. Open Decisions

Only genuinely unresolved, CTO/product-level questions — everything resolvable from Documents 41/42 or existing repository convention has been resolved above, not left open; implementation-level mechanisms with a frozen behavioral requirement above them are listed in §22, not here, per this task's own instruction not to disguise a mechanism choice as a contract ambiguity.

1. **Whether comparison-explanation warrants a rate limit stricter than the existing shared `MAX_ACTIVE_JOBS` budget** (§19). No existing per-capability-kind limiter exists to reuse as precedent; this is a product/ops judgment call, not a contract necessity.

Previously listed here, now resolved and moved to frozen decisions above (not open, and not disguised as an implementation detail): whether a `"partial"` result counts as a dedup hit (§15.1 — conditionally, not unconditionally reusable) and the explanation-identity coherence question (§14.1).

---

## 24. Acceptance Criteria

A testable checklist for the eventual implementation to satisfy — not itself an implementation:

- [ ] Route inventory gains exactly 4 routes (§5); zero existing routes change.
- [ ] `POST /reports/compare`'s response shape, status codes, and behavior are byte-for-byte unchanged before and after this capability ships.
- [ ] No code path allows a synchronous LLM call to execute inside the `compare_reports` request handler.
- [ ] `POST .../explain` is idempotent per explanation identity per §15's table — two concurrent requests for the same identity never both trigger independent generation.
- [ ] A completed `ExplanationResult` never has an empty `cited_source_indices` (§9, §11) — such a case is always `status: "failed"` instead.
- [ ] A `"partial"` result always has a non-empty `limitations` list, and a `"complete"` result always has an empty one (§11) — the two are never ambiguous.
- [ ] No failure path anywhere in this capability returns raw provider exception text, an API key fragment, or an internal stack trace to the client (§12, §19).
- [ ] Cancellation is owner-scoped and idempotent on an already-terminal job (§13).
- [ ] BYOK fields, when supplied, thread through `set_llm_context`/`reset_llm_context` exactly as `_run_pipeline`/`_run_explanation` already do (§6, §19) — no separate credential path.
- [ ] Every citation index referenced by a `[n]` marker in `narrative` exists in `sources`, and every index in `sources` that's actually referenced appears in `cited_source_indices` (§10).
- [ ] `comparison_report_ids` in a completed result reflects execution-time authorization, which may be a strict subset of the requested `report_ids` (§16).
- [ ] No two durable explanation artifacts simultaneously claim the same canonical explanation identity (execution-time resolved report IDs + prompt/schema/provider/model versions), even when execution-time resolution narrows the effective report set relative to what was requested or admitted (§14.1).
- [ ] A `"partial"` result is never returned as a dedup hit once the evidence state that produced it is no longer materially equivalent to the current one — a fresh generation is triggered instead (§15.1).
- [ ] A `"complete"` result is always returned as a dedup hit on identity match alone, with no additional condition (§15.1).

---

## 25. Governance / Approval Record

```text
Document 43 status:
🟢 APPROVED / FROZEN — CTO RATIFIED

This document is CTO-approved and frozen. It authorizes implementation of
M9.1 against the contract defined herein, subject to the normal engineering
implementation and reviewer gates. Contract approval, engineering
implementation review, and final merge approval remain three distinct gates —
this ratification satisfies only the first; it does not itself constitute
engineering sign-off or a merge approval.

Document 41 (Architecture):        🟢 APPROVED / FROZEN — unmodified by this pack
Document 42 (Product Semantics):   🟢 APPROVED / FROZEN — unmodified by this pack
Document 43 (this pack):           🟢 APPROVED / FROZEN — CTO ratified.

Sequencing note, stated precisely so this record stays accurate: M9.1
implementation was carried out under a separate, earlier CTO directive that
explicitly authorized building against this document while it was still
🔴 PROPOSED ("M9.1 IMPLEMENTATION IS AUTHORIZED"). This document's own
contract-level approval is ratified now — it is not, and does not claim to
be, something that preceded or retroactively authorized that earlier
implementation work.

What this ratification covers: §5's recommended route shape, §14.1's identity
coherence invariant, §15.1's partial-result reuse rule, §10's citation-
enforcement hierarchy, and §9's job/artifact ID coupling are all ratified as
part of this approval. §23's one remaining item (a stricter-than-global rate
limit) is a product/ops judgment call, not a contract blocker, and remains
open at engineering discretion.

Required next step:
Engineering implementation review (Backend & AI Reviewer 2) and final merge
approval — the two gates this contract-level ratification does not itself
satisfy. /reports/rescore deletion (Document 41 §17) remains independently
authorized and separate from M9.1, unaffected by this pack's approval status.
```
