# 41 — M9 Pre-Implementation Architecture Decision Pack

**Status:** 🟡 Draft — awaiting CTO and Backend & AI Design Reviewer 2 approval
**Type:** Architecture investigation (research-only, no code changed)
**Revision 3** — final correction pass before Backend & AI Design Reviewer 2 approval.
The core recommendation (Option C at the contract level, executed via Option B's
existing job infrastructure) remains accepted and unchanged from Revision 1/2. This
pass corrects: the `chat_json`/`chat_text` delegation relationship (§5, verified
against source — previously conflated), async grounding/report re-resolution (§13.2,
new — the explanation job independently re-authorizes its report set rather than
trusting the initiating request's in-memory result), and freezes BYOK/managed-AI
inheritance as settled architecture rather than an open question (§13.1, §19.1). This
revision does not itself constitute CTO or Reviewer 2 approval of the document as a
whole — see §20.
**Supersedes nothing; amends nothing.** Doc 17 §2/§6 and doc 28's reaffirmation remain
the roadmap record of *that* M9 was scoped; this document determines *how* it should
be built, which doc 17 explicitly did not settle (§2's one-line characterization —
"an LLM call inside `compare_reports`... no contract change needed" — was a roadmap-
sizing estimate, not an architecture review).

---

## 1. Executive Summary

M9's original characterization — "additive, one new LLM call" inside `POST
/reports/compare` — **cannot safely proceed as literally written**, for one concrete,
repository-verified reason: the frontend does not treat `/reports/compare` as a
mutation. It treats it as a **pure, deterministic, client-cached query**. The
integration layer's own comment states this explicitly:

> `web/features/comparison/application/useCompare.ts:5-10` — *"`POST /reports/compare`
> is a pure lookup (no LLM re-run, no side effects)... same selection always returns
> the same data, and TanStack Query's cache (keyed by the sorted id set) avoids
> re-fetching when toggling back and forth."*

Embedding an LLM call inside that endpoint would silently convert every cache-stale
refetch (`staleTime: 30_000`, plus any cache eviction, remount, or new tab) into a
**new billed LLM call for data that hasn't changed** — precisely the "accidental
billing multiplier on a frequently-called deterministic endpoint" this task's own
brief warns against, and a direct contradiction of the invariant the frontend was
built to rely on. This is not a hypothetical risk; it is a documented assumption
already encoded in shipped code.

A second, independent finding compounds this: **no request-handler-level LLM call
exists anywhere in this backend today.** Every LLM call runs inside the async
job/LangGraph pipeline (`_run_pipeline`, `_run_explanation`), which is also the only
place BYOK credentials are threaded onto the LLM context (`set_llm_context`, called
only from those two functions). A synchronous call inside `compare_reports` would,
without additional plumbing doc 17 never accounted for, silently use the
environment/managed provider instead of the caller's own key — a correctness gap
that "one new LLM call" does not describe.

**Conclusion:** the *capability* (AI explanation of comparison differences) is
approved and small. The *mechanism* doc 17 assumed (embed a synchronous call in the
existing endpoint, no contract change) is not architecturally sound against the
current repository. §10 recommends an alternative that keeps `/reports/compare`
exactly as-is and adds the explanation as a separate, additive capability built on
infrastructure that already exists and is already designed for exactly this kind of
reuse.

The rescore-deletion half of M9 is unaffected by any of this and remains ready to
implement independently (§17).

---

## 2. Current Repository State (evidence-backed findings)

- `POST /reports/compare` ([backend/server.py:1650-1673](../../backend/server.py#L1650)) does a single owner-scoped Mongo lookup of 2-4 existing report documents and returns them verbatim. **No LLM call, no computation, no side effect** beyond one `logger.warning` when a requested id is excluded.
- The frontend (`web/features/comparison/`) models this as a `useQuery` (TanStack Query), not a `useMutation` — cached by sorted report-id set, 30s stale time, with an explicit code comment asserting purity (quoted in §1).
- Every existing LLM-consuming feature (report generation, Learning) runs through the same generic async job machinery: `domain/models.py`'s `Job`/`JobKind`/`JobStatus`, `application/ports.py`'s `JobStore`/`EventBus` protocols (Redis-backed, `infrastructure/redis/`), and `application/jobs.py`'s feature-agnostic `JobLifecycle` (`start`/`mark_running`/`publish`/`complete`/`fail`/`cancel`/`is_past_deadline`/`reap_stale`). `JobKind` currently has exactly two members: `RESEARCH`, `LEARNING`.
- `agents/llm.py`'s `chat_text`/`chat_json` are the sole LLM entry points, with multi-provider dispatch, 4-attempt retry/backoff, per-attempt OTel spans, and `llm_calls_total`/`llm_tokens_total` metrics automatically attached. BYOK (`set_llm_context`) is invoked only from `_run_pipeline` and `_run_explanation` — nowhere else in the codebase.
- Reports are **immutable after creation**, with two narrow exceptions: claiming ownership on an anonymous cache-hit, and the rescore endpoint's scorecard overwrite (itself being deleted by M9.2). No other mutation path touches a report document post-creation.
- Learning already has a second AI-output Mongo collection (`db.explanations`, field name `explanation`) alongside `db.reports` — `application/ports.py`'s `ReportLikeRepository` docstring names this explicitly: *"`reports` and `explanations` share this shape... structurally identical: id, user_id, created_at, + feature payload"* — and [08_MongoDB_Data_Architecture.md §4.7](08_MongoDB_Data_Architecture.md) documents it as the established pattern for a second AI-output collection.
- Redis holds only **ephemeral, TTL-bound live-job state** (`_JOB_TTL_S = 24h` job hash, `_STREAM_TTL_S = 3600s` SSE reconnect grace window) — never a durable store. Mongo is the system of record for finished AI output. This matches the brief's "do not use Redis as a primary database" instruction and is the existing, un-debatable convention.
- No rate limiting currently applies to `/reports/compare` (confirmed: `auth.is_rate_limited` calls exist only for auth endpoints and the M8 financials-acquire endpoint).

---

## 3. Existing M9 Definition (quoted verbatim)

[17_M4_Backend_Capability_Roadmap_Reconciliation.md §2](17_M4_Backend_Capability_Roadmap_Reconciliation.md), Frontend↔Backend Parity Matrix, `comparison` row:

> "AI-generated comparison explanation (§1) — an LLM call inside `compare_reports`,
> new prompt, **no contract change needed** (`POST /reports/compare`'s response can
> add a field additively)"

§6, Milestone 9:

> "Scope: `POST /reports/compare`'s AI-generated explanation-of-differences
> (additive field, one new LLM call); delete `POST /reports/rescore`."

[28_Post_M6_Roadmap_Reconciliation.md:164](28_Post_M6_Roadmap_Reconciliation.md) reaffirms, unchanged, as of the most recent roadmap reconciliation: *"Still open, still small, still valid — just lower-priority... Not stale, simply not next."*

**No later document supersedes this.** A full-repository search for `M9`/`Milestone 9`/comparison-explanation contract language turned up no ADR, no Change Request, no contract-review document analogous to M8's `33_M8_Financials_API_Contract_Review.md`. Doc 17/28's one-paragraph characterization is the entire authoritative record — which is exactly why it is a *roadmap sizing note*, not an architecture decision, and exactly why this pack exists.

**No exact response field name is specified anywhere** in doc 17, doc 28, `docs/design/05_Screen_Inventory.md`, `docs/design/06_UX_Specifications.md`, or `web/features/comparison/integration/schemas.ts` (which has no placeholder for it today). This pack does not resolve that naming question — it is an implementation-contract decision, not an architecture question (§19.3).

---

## 4. `POST /reports/compare` Current Architecture

Direct answers to the ten required questions:

1. **Deterministic?** Yes — a pure Mongo lookup, same input always yields the same output (modulo report deletion).
2. **Performs LLM work today?** No.
3. **Side effects?** None beyond a diagnostic log line for excluded ids.
4. **Persists?** Nothing. Read-only.
5. **Returns?** `{"reports": [<report docs, minus events/source_documents>]}`, order preserved from the request, 404 if fewer than 2 are visible.
6. **Test assumptions encoded** ([backend_test_iter2.py:156-182](../../backend/tests/backend_test_iter2.py#L156), [test_reports_scoping.py:99-166](../../backend/tests/test_reports_scoping.py#L99)): 2-4 id bounds (422 outside), owner/sample visibility scoping (404 on cross-tenant), anonymous rejection. No test exercises or expects any AI/explanation behavior — none exists to break, but none exists to build on either.
7. **Frontend assumptions encoded:** purity and cacheability, as detailed in §1 — this is the load-bearing finding of this pack.
8. **Response contract frozen anywhere?** Not by a dedicated contract-review doc (unlike M8's Document 33). It is, however, covered by `backend/tests/contract/test_route_inventory.py`'s exact-route-set assertion (path/method only, not response shape) and by the frontend's own `compareResponseSchema` (Zod) — the de facto contract today is "whatever `compareResponseSchema` in `web/features/comparison/integration/schemas.ts` validates," which has no explanation field.
9. **Caching that currently exists:** client-side only (TanStack Query, 30s staleTime, sorted-id-set key). No server-side cache.
10. **Auth/authz/rate limiting:** `current_user` session dependency (login wall); EQ-3 owner-or-sample scoping at the query level; no rate limiting.

---

## 5. Existing AI Execution Architecture

**Job representation:** `domain/models.py`'s `Job` dataclass (`id`, `kind: JobKind`, `user_id`, `status`, `ticker`, `created_at`, `updated_at`, `deadline_at`, `error`) is feature-agnostic by construction. `JobKind` is a two-member enum (`RESEARCH`, `LEARNING`) — adding a member is additive, not a redesign.

**Initiation:** a request handler creates a job id, calls `container.job_lifecycle.start(job_id, kind, user_id, deadline_s=...)` (admission-controlled against one shared `MAX_ACTIVE_JOBS` budget across every kind — Learning does not get its own queue, per `application/jobs.py`'s own docstring), inserts a Mongo mirror doc, and schedules an `asyncio.create_task` tracked in `RUNNING_TASKS` for cancellation.

**State persistence:** dual — Redis (`JobStore`, 24h TTL hash) is the live/authoritative status during execution; Mongo (`db.jobs` / `db.explanation_jobs`) is a durable mirror updated at every transition, read by `GET /reports/{job_id}` for reconnect/restart resilience.

**Retries:** two independent layers — `chat_text`'s own 4-attempt provider-level retry/backoff (unrelated to job retries; there is no job-level retry, a failed job simply reaches `FAILED`).

**`chat_json` vs `chat_text` — verified against `agents/llm.py`, this revision (corrected — the recommended entry point for comparison explanation, §13, is `chat_json`, and every retry/observability claim below must describe what `chat_json` actually does, not `chat_text` in isolation):** `chat_json` is not a parallel or independent LLM entry point. It makes exactly **one** call to `chat_text` (`agents/llm.py:470`, `raw = await chat_text(system + guardrail, user_msg, model=model)`) and then post-processes the result — there is no second, `chat_json`-specific retry loop. Consequently, every behavior attributed to `chat_text` elsewhere in this pack (the 4-attempt retry loop, `NonRetryableLLMError`'s immediate-no-retry short-circuit, exponential-ish backoff capped at 30s, the per-attempt `llm.attempt` OTel span, `llm_calls_total`/`llm_tokens_total` metrics, provider dispatch, and BYOK context via `_active()`) applies to `chat_json` unchanged and automatically, purely by delegation — nothing needs to be re-implemented or re-verified for the JSON path.

What `chat_json` adds **on top**, strictly after `chat_text` has already returned a successful string, is JSON extraction/repair (stripping a wrapping code fence; three fallback parse strategies — direct `json.loads`, a regex-extracted `{...}`/`[...]`, and brace-wrapping bare `k: v` pairs; unwrapping a mistaken `{"properties": {...}}` schema-echo; unwrapping a bare array into a schema's single list field) and Pydantic schema validation (`schema.model_validate`). A failure at *this* layer — text that can't be parsed as JSON by any fallback, or that parses but fails schema validation — raises a plain `ValueError` (`agents/llm.py:483,505`) with no retry of any kind: it happens after `chat_text`'s own retry loop has already succeeded once, so a malformed/invalid *output shape* is architecturally distinct from a provider-level failure (network error, timeout, truncation) — the latter is retried up to 4 times entirely inside the single `chat_text` call `chat_json` makes; the former is never retried by the LLM layer itself. A caller wanting to retry a malformed-output case would need to invoke `chat_json` again itself — no such automatic second-layer retry exists today, and this pack does not propose adding one.

**Provider failures:** caught at the pipeline level, translated to a generic, redacted message (`JobLifecycle.fail(job_id, safe_message)` — its docstring explicitly forbids passing raw exception text, since "provider SDK exceptions can embed an API key"), full detail server-logged only via `logger.exception`.

**Cancellation:** `POST /reports/{job_id}/cancel` / `POST /learning/{id}/cancel` cancel the `RUNNING_TASKS` asyncio task; `JobLifecycle.cancel()` is idempotent (a no-op on an already-terminal job).

**Streaming:** `GET /reports/{job_id}/stream` / `GET /learning/{id}/stream` — generic SSE fan-out via `EventBus.subscribe(job_id)`, independent per subscriber (multiple tabs each see every event).

**Deadline enforcement:** checked at LangGraph node boundaries (`is_past_deadline`, per-kind `settings.job_deadline_s[kind]` dict entry — trivially extensible).

**Persisted AI results:** `db.reports` (research) / `db.explanations` (Learning) — structurally identical envelope (`id`, `user_id`, `created_at`, feature payload), by explicit design (`ReportLikeRepository` port docstring).

**Can this infrastructure support a comparison explanation without new infrastructure?** Yes. Every piece above is already generic over `kind`. Nothing about `JobLifecycle`, `JobStore`, `EventBus`, or the SSE/cancel/deadline machinery is Learning- or Research-specific. The only genuinely new things a third kind would need are: one `JobKind` member, one `job_deadline_s` entry, one background function (no LangGraph graph is required — a single `chat_json` call does not need a multi-node graph), and — this is the point §10 turns on — **new routes to create/read that job**, because the existing routes are named `/reports/*` and `/learning/*` for their respective kinds, and nothing in the current route surface lets a client create or poll a third kind of job. That need for new routes is exactly the "contract change" doc 17 assumed away.

---

## 6. Option A — Synchronous LLM inside `POST /reports/compare`

**Latency:** `chat_text`'s existing retry loop can take up to ~4×(120s timeout + backoff) in a worst-case provider outage — several minutes — inside a request that today returns in low tens of milliseconds. No existing precedent for a request handler blocking on this.

**Timeout risk:** every client-side timeout (browser fetch, any reverse proxy, TanStack Query's own retry/timeout config) is now in the critical path of what used to be an instant lookup.

**Provider failure impact:** would corrupt what is today an unconditionally-reliable endpoint — a provider outage would newly make comparison itself flaky, unless failure handling is built to always fall through to the deterministic data (extra logic, not free).

**Request lifecycle:** unchanged in shape (still one request/response), but its performance envelope becomes provider-dependent, which nothing else in this app's "query" endpoints does.

**Cost:** **disqualifying**, evidenced not asserted — §1's frontend-purity finding means every stale-cache refetch re-runs and re-bills the LLM call for identical input. `staleTime: 30_000` was tuned assuming zero cost per refetch; it would need re-tuning (a frontend change, out of scope for this backend-only milestone) merely to keep today's cost profile sane, and even then every remount/new-tab/cache-eviction still re-bills.
**Caching:** none exists today at this layer for anything AI-generated; would need to be invented as part of this change (defeating "no contract change needed").
**Determinism:** the deterministic lookup and the non-deterministic AI generation would share one response and one cache entry, so TanStack Query's cache (correctly memoizing the deterministic part) would incorrectly memoize the AI part too — different provider retries could return different phrasing for a cached vs. fresh explanation the user can't distinguish.
**Retry behavior:** `chat_text`'s retry loop, run inline, directly extends this request's latency on every attempt; no equivalent exists today for a synchronous endpoint.
**Observability:** would generate LLM traces/metrics under a request span that today has none, with no `jobs_active`/`pipeline_runs_total` equivalent — those metrics are job-shaped, and Option A isn't a job.
**Scalability:** ties up a request-handling coroutine (and, transitively, `chat_text`'s `asyncio.to_thread` worker) for the LLM's full duration on every cache-miss.
**Frontend contract implications:** breaks the documented purity/caching assumption outright; the frontend would need to change (`useQuery`→`useMutation` or equivalent) to stay correct, which contradicts both this task's "do not modify frontend code" boundary and doc 17's "no contract change" framing.
**Operational complexity:** low to build, high to operate — the failure modes above (timeout, cost, cache staleness) all become production incidents rather than design-time decisions.

**Verdict: not viable as scoped.** This is not rejected merely because it's synchronous (per the brief's own instruction not to reject on that basis alone) — it's rejected because it contradicts a concrete, already-shipped frontend invariant and creates an unbounded cost multiplier, both independently verifiable in the current repository.

---

## 7. Option B — Asynchronous explanation using existing job infrastructure

**Job lifecycle:** fully supported by the existing generic `JobLifecycle` — add `JobKind.COMPARISON_EXPLANATION`, call `job_lifecycle.start(...)` exactly as `_run_pipeline`/`_run_explanation` do. No new job *concept* needed.

**Persistence:** a durable Mongo artifact following the exact `reports`/`explanations` envelope pattern already established — see §12 for the frozen persistence-boundary decision (exact collection name deferred to implementation).

**Retries:** identical to today, inherited automatically. The recommended call (`chat_json`, §13) makes exactly one call to `chat_text` (§5), so the existing 4-attempt provider-level retry/backoff loop applies unchanged with zero additional retry logic — see §5's verified `chat_json`/`chat_text` relationship for the precise split between what's retried (provider-level failures, inside `chat_text`) and what isn't (malformed/invalid output shape, `chat_json`'s own `ValueError`, surfaced once with no retry).

**Cancellation:** mechanically available for free (`RUNNING_TASKS` + `JobLifecycle.cancel`), though whether cancellation is *meaningful* for a single `chat_json` call (vs. Learning/Research's multi-node graphs) is arguably over-scoped — a single LLM call is short enough that cancel may not be worth exposing. Flagged as an implementation-detail question, not decided here.

**Streaming:** the existing `EventBus`/SSE mechanism is generic over `job_id` and would work unmodified; whether a single LLM call benefits from token-level streaming (vs. a single "done" event) is a UX call, not an architecture constraint.

**Failure states:** directly reuses the existing, already-battle-tested `FAILED` status + redacted-message convention (`JobLifecycle.fail`).

**Duplicate requests / idempotency — corrected in Revision 2:** `MAX_ACTIVE_JOBS` is a *global admission budget*, not a deduplication mechanism, and does not by itself prevent two concurrent requests for the *same* explanation identity from each starting their own generation job — nothing in the existing job infrastructure enforces per-identity exclusivity today, because no existing job kind has ever needed it (Research/Learning jobs are inherently per-request, with no notion of "the same job as someone else's"). Comparison explanation is the first capability in this repository where two independent requests can legitimately resolve to *the same* underlying work, so this is a genuine new requirement, not something the existing infrastructure already provides. See §12 for the identity this must key on and §14 for the required lookup-before-create semantics.

**Cost:** solves Option A's billing-multiplier problem directly — generation only happens on explicit request, not on every cache refetch.

**UX implications:** the comparison screen would show deterministic data instantly (as it does today) and the explanation would load progressively/stream in afterward — this actually matches `docs/design/06_UX_Specifications.md`'s "AI explanation streams" language (§1 of the prior recon flagged this as contradicting doc 17's synchronous framing; Option B is precisely the mechanism that would make the UX spec's "streams" language true rather than false).

**Complexity:** the *execution* mechanism is nearly free (everything reused); the *contract* mechanism is not — this still needs at least one new route to create the explanation job and a way to retrieve/stream its result. That is unavoidably a contract change, contradicting doc 17's "no contract change needed" assumption, which is the central correction this pack makes.

**Verdict: architecturally sound, and the right execution mechanism** — but "asynchronous job infrastructure" alone doesn't answer whether the explanation is a field on `/reports/compare`'s response (impossible if async — a POST can't return a value that doesn't exist yet without either blocking (Option A) or the client polling a second time) or a wholly separate capability. That's Option C's question, and Option B is the implementation vehicle for it, not a competing choice — see §10.

---

## 8. Option C — Keep comparison deterministic, treat explanation as a separate capability

**API clarity:** `/reports/compare` keeps its current, tested, frontend-relied-upon contract exactly as-is — zero risk to existing behavior, zero risk to the 30s-staleTime caching assumption.

**Deterministic behavior:** fully preserved — this is the option that doesn't ask the deterministic endpoint to do double duty.

**Cacheability:** `/reports/compare` remains a `useQuery` with no changes needed; the explanation capability gets its **own** cache/identity, decoupled from comparison's.

**LLM cost:** generation happens once per explicit "explain this comparison" action (or once per unique explanation-generation identity, if the explanation itself is persisted and reused — see §12.2), never as a side effect of a cache-miss on unrelated deterministic data.

**Provider failures / retries:** isolated entirely to the explanation capability; a provider outage cannot make comparison itself unreliable.

**Persistence:** a durable MongoDB artifact, independently owned from `reports`, following the established `reports`/`explanations` envelope pattern exactly (§2, §5) — not a new pattern, a repetition of one that already shipped for Learning. Never stored solely in Redis, never embedded into `/reports/compare`'s response (§12's frozen persistence-boundary decision).

**Identity matching:** the explanation's identity is naturally tied to the comparison's inputs (see §12.2/§12.3) rather than to `/reports/compare`'s own (unrelated) cache lifecycle — no artifact is deleted or expired as inputs change; a changed input simply no longer matches the prior artifact's identity (§12.3).

**UX:** consistent with `06_UX_Specifications.md`'s SCR-07 language — comparative metrics/summaries load first (today's behavior, unchanged), "AI explanation streams" as a distinct, subsequent step. This matches the existing Learning UX pattern the product already ships (concept → grounded explanation, streamed).

**Scalability:** identical to Option B's (it's the same execution mechanism).

**Future model regeneration:** trivial — since the explanation is its own document/job, regenerating under a new prompt/model version is a new job with a new identity, not a mutation of a "frozen" comparison response.

**Observability:** gets its own `jobs_active`/`pipeline_runs_total`/`llm_calls_total` label values for free, exactly like Learning's `graph="learning"` labels today — comparison-explanation failures are distinguishable from comparison failures in every existing dashboard/metric without new instrumentation work.

**Architectural coupling:** the lowest of the three options — deterministic data and AI interpretation become two independently-versionable, independently-failable capabilities, matching the repository's own stated design principle (`agents/llm.py`'s module docstring: every AI feature "should keep depending on that one seam" — the seam is the LLM client, not the endpoint it's attached to).

**Verdict: this is the option that should be chosen at the contract level** — it is not "automatically superior" in the abstract, but it is the only one of the three that doesn't require either accepting Option A's cost/latency risk or awkwardly bolting async job status onto a `POST` response Zod schema currently modeled as complete-on-return.

---

## 9. Comparison Matrix

| Dimension | A — Synchronous | B — Async job (as a mechanism) | C — Separate capability (contract) |
|---|---|---|---|
| API semantics | Breaks documented purity | N/A alone (see below) | Preserves `/compare` exactly |
| Latency | Minutes worst-case, in critical path | Off critical path | Off critical path |
| Reliability | Comparison inherits LLM flakiness | Isolated | Isolated |
| Cost | Unbounded (refetch multiplier) | Bounded (explicit trigger) | Bounded (explicit trigger) |
| Caching | Broken (mixes deterministic + non-deterministic in one cache entry) | Needs its own identity | Own identity (§8) |
| Determinism | Compromised | N/A alone | Preserved for `/compare` |
| Failure isolation | None — explanation failure risks the request | Good (existing `FAILED` handling) | Good |
| Scalability | Ties up request coroutines under load | Reuses existing job budget | Reuses existing job budget |
| Observability | New, ad hoc | Existing metrics/spans, for free | Existing metrics/spans, for free |
| Implementation complexity | Low code, high hidden risk | Low (execution layer) | Low (execution) + needs new route(s) |
| Maintainability | Poor — couples two concerns permanently | Good | Best — matches Learning's proven shape |

(Option B has no row of its own in the "contract" dimensions because it is not a contract-level choice — it is the mechanism §10 recommends for implementing Option C.)

**B and C are not mutually exclusive alternatives being weighed against each other — they answer two different questions and both apply simultaneously:**

```text
Option A:  Rejected.
Option B:  Chosen as the execution mechanism (how the explanation job runs).
Option C:  Chosen as the API/capability boundary (what /reports/compare stays,
           and where AI generation lives instead).
```

---

## 10. Recommended Architecture

**Option C at the contract level, implemented using Option B's existing job infrastructure as its execution mechanism. Not a hedge — these are not competing choices; B answers "how does it run," C answers "what does the API look like," and the repository evidence in §1/§6/§8 rules out A cleanly enough that this is a single, explicit recommendation.** *(Accepted by Backend & AI Design Reviewer 2 in Revision 1 review; the corrections in this revision refine — not reopen — this recommendation.)*

**Frozen architectural boundary:** `POST /reports/compare` must remain deterministic and must never gain synchronous LLM execution, an `generate_explanation`-style request flag, or any other implicit AI-generation behavior. Comparison owns deterministic data; the separate explanation capability owns AI generation. This boundary is restated in §11 and §18 and applies to every future variant of this feature, not just the initial implementation — a later "just add a flag" shortcut is explicitly rejected by this pack, not merely unaddressed by it.

Why this is the right long-term architecture for AlphaScribe, not just the least-bad of three options:

1. It is the only option consistent with a concrete, shipped frontend invariant (`useCompare.ts`'s purity assumption) without requiring an out-of-scope frontend change.
2. It reuses 100% of the existing job/LLM infrastructure — `JobKind`, `JobLifecycle`, `JobStore`, `EventBus`, `chat_json`, retry/backoff, tracing, metrics — repeating a pattern (Learning) that has already shipped and is already proven, rather than inventing anything.
3. It matches the product's own stated UX intent (`06_UX_Specifications.md`'s "AI explanation streams") more faithfully than the roadmap doc's "additive field" framing does.
4. It keeps the two concerns — deterministic comparison, AI interpretation — independently failable, independently cacheable, and independently observable, which is exactly the coupling discipline `agents/llm.py`'s own module docstring already asks every AI feature in this codebase to follow.
5. It costs less to operate: no billing multiplier, no request-timeout risk on a previously-instant endpoint.

---

## 11. API Contract Implications (future, not implemented here)

- `POST /reports/compare` — **unchanged, and frozen unchanged.** No field added, no schema change, no behavior change, no synchronous LLM execution, no `generate_explanation`-style flag, no other implicit AI-generation trigger. This is an explicit architectural rejection (§10), not merely an absence of a proposal — any future design that reintroduces AI generation into this endpoint's request/response cycle would be a deviation from this pack and requires its own CTO review.
- A new, separate surface is needed to request/read a comparison explanation — shape (a new route under `/reports/compare/...`, or a `comparison_explanations` sibling to `/learning/*`) is an implementation decision for the eventual engineering task, not this pack. At minimum it needs: a way to initiate generation (comparison's report-id set as input), a way to read the result (by whatever identity is chosen, §12), and reuse of the existing SSE pattern if streaming is desired.
- This is, explicitly, **a contract change** — correcting doc 17's "no contract change needed" assumption, which this pack's evidence does not support.
- Versioning/back-compat: since nothing on `/reports/compare` changes, there is no back-compat concern for existing clients at all.

---

## 12. Data / Persistence Implications (conceptual)

### 12.1 Persistence boundary — frozen decision

Comparison explanations are durable AI artifacts and must be persisted in MongoDB as
an independently owned explanation artifact. They must not be stored solely in Redis,
and must not be embedded into the deterministic `/reports/compare` response. The
existing `reports`/`explanations` pattern (§2, §5) is the architectural precedent —
structurally identical envelope (`id`, `user_id`, `created_at`, feature payload), not
a new persistence pattern. The exact collection name, indexes, document schema, and
repository interface are an implementation-contract decision, not decided here (§19
deferred list). What is frozen is only:

```text
durable AI explanation → MongoDB system of record
Redis                  → ephemeral job/live state only (unchanged from every existing job)
```

### 12.2 Two distinct identities — do not conflate them

Revision 1 collapsed comparison identity and explanation-generation identity into one
concept. They are distinct, and the distinction is load-bearing for §14's dedup logic:

**Comparison identity** — the identity of the deterministic comparison itself:

```text
resolved report IDs (the set compare_reports actually returns, not the raw request —
today a requested id can be silently excluded for visibility reasons, §2)
```

No additional comparison configuration exists today. `CompareRequest` carries only
`report_ids` (2-4, `Field(min_length=2, max_length=4)`); there is no sort order,
metric-selection, or other parameter that affects what `compare_reports` returns. If
a future change to `/reports/compare` ever added configuration that changes its
output (out of scope for M9), comparison identity would need to incorporate it —
noted for completeness, not proposed here.

**Explanation generation identity** — the identity of a specific *generated
artifact*, which must be strictly narrower than comparison identity (every distinct
explanation identity implies one comparison identity, but not the reverse):

```text
comparison identity
  + prompt version
  + explanation/schema version
  + provider identity + model identity   (not model name alone — see below)
```

**Provider + model, not model alone:** this repository's LLM architecture is
explicitly multi-provider (`agents/llm.py`'s `PROVIDER_DEFAULTS` spans Gemini,
OpenAI, Anthropic, Groq, OpenRouter, DeepSeek, Mistral, and BYOK-custom endpoints).
Two different providers can expose models with the same or confusingly similar
names, and the same provider can serve materially different outputs across model
revisions. Collapsing identity to "model name" would let a cached explanation
generated by one provider silently stand in for a request meant for another. The
conceptual identity must therefore distinguish `provider + model` as a pair.

**Why "same comparison + different prompt/model/provider" legitimately produces a
new artifact:** each of those three variables can change the generated text without
changing the underlying facts being explained. A prompt-wording fix, a model
upgrade, or a provider switch (BYOK caller changes their configured provider) are
all *content-affecting* changes from the same deterministic input — reusing a stale
artifact across any of them would silently serve an explanation the current
configuration would not have produced, which is a correctness defect, not a caching
nicety.

The exact hashing/storage representation of either identity (a composite key, a
derived hash, a set of indexed fields) is an implementation detail, not decided here.

### 12.3 Prior artifacts and identity matching

A report deletion (`DELETE /reports/{report_id}`) already changes `compare_reports`'s
resolved set today. When that happens, a previously-generated explanation artifact
is not deleted, expired, or cleaned up as a result — it remains persisted exactly as
it was. What changes is that the *new* explanation-generation identity (§12.2),
computed from the newly-resolved report set, no longer matches the identity the
prior artifact was stored under — the prior artifact naturally becomes unmatched by
the new explanation identity, and so is no longer selected or reused for the new
comparison, with no explicit cleanup step required. The same applies to a prompt,
schema, or model/provider change: it naturally produces a new explanation-generation
identity (§12.2) that the prior artifact's identity doesn't match, rather than
requiring an explicit step to invalidate the old one.

---

## 13. AI Execution Implications

### 13.1 Model, provider, BYOK

- Model/provider: reuse `agents/llm.py`'s `chat_json` — a structured, schema-validated wrapper that delegates to `chat_text` for the underlying call (§5's verified relationship; not an alternative to `chat_text`, a layer on top of it), following the `FinancialsSchema`/`ToneSchema` precedent in `agents/schemas.py`, with `DEFAULT_LIGHT_MODEL` or `DEFAULT_HEAVY_MODEL` per existing tiering conventions — model choice is an implementation detail, not decided here.
- **BYOK — frozen architectural rule (§19.1), not an open product question.** `agents/llm.py` is built provider-agnostic with BYOK as a first-class path (per-request credentials via `_LLM_CTX`, not a special case bolted on): both `POST /reports/generate` (research) and Learning's explanation job already accept `llm_provider`/`llm_api_key`/`llm_base_url`/`llm_model` and call `set_llm_context`/`reset_llm_context` around their pipeline run, falling back to the managed/environment provider only when the caller supplies none. **Comparison explanation inherits this identical, existing BYOK/managed-AI provider-selection policy** — the new job's initiating request accepts the same fields and threads them through `set_llm_context`/`reset_llm_context`, exactly as `_run_pipeline`/`_run_explanation` do. No repository evidence was found that this capability cannot support that pattern (a single `chat_json` call is a strictly simpler case than either existing pipeline), so there is no basis for a silent managed-AI-only exception. Any deliberate deviation from this policy for this specific capability requires its own explicit CTO/product approval (§19.1) — the policy itself is not what's open. The plumbing (threading the fields through the new job's request) does not exist yet for anything outside `_run_pipeline`/`_run_explanation` and must be added as part of implementation — an engineering task, not an architectural one.
- Job kind: one new `JobKind` member.

### 13.2 Async grounding / report resolution

The explanation runs as an asynchronous job (§7) — it must not conceptually depend on
any in-memory state from the HTTP request that triggered it, because that request's
handler may have returned, and its local state gone out of scope, well before the job
actually executes (queued behind `MAX_ACTIVE_JOBS`, or simply scheduled later on the
event loop). The execution flow is:

```text
Explanation job
      ↓
resolve the authorized report set (re-run compare_reports's own EQ-3 owner-or-sample
scoping query against the job's report_ids — never trust them as pre-authorized)
      ↓
load the immutable report documents (safe to re-read independently of the
originating request — see below)
      ↓
construct bounded comparison context (structured extracted financials/sentiment/
scorecard per report, not full draft_report text, to keep prompt size and
hallucination risk bounded — mirrors financial_extractor_node's existing "only
what's in the text" grounding discipline)
      ↓
LLM generation (chat_json, §13.1)
      ↓
persist explanation artifact (§12.1)
```

**Why re-resolution, not reuse:** the job must never trust (a) raw client-supplied
report IDs without independently re-checking authorization, (b) an already-resolved
report set handed to it without that check having been redone, or (c) any in-memory
result object from the initiating HTTP request. It independently performs the exact
same ownership/sample-visibility check `compare_reports` performs today (§2, §4) —
re-running the check, not reusing its output — so the explanation job's authorization
is self-contained and correct even if it executes long after the request returns.

**Why this is safe and requires no new persistence:** reports are immutable after
creation (§2) — the only two mutations found anywhere in this repository are an
ownership claim on an anonymous cache-hit and rescore's scorecard overwrite (M9.2,
being deleted). For reports that still exist and remain visible to the caller,
re-reading by id returns the same immutable report content; however, report
deletion or a change in visibility between job initiation and job execution can
change the *resolved set* itself (§12.2's comparison identity) — so the job must
treat its own execution-time authorization/resolution result as authoritative, not
whatever the initiating request originally resolved. This is exactly what the
re-resolution step above already guarantees on every execution, mirroring precisely
what `compare_reports` itself does today. This pack does **not** introduce report
versioning, snapshots, or any change to the identity model to handle this — no
repository evidence suggests individual report *content* becomes mutable, so there
is no basis for a snapshot mechanism, and inventing one here would be exactly the
kind of speculative persistence architecture this pack's scope excludes (§18).

---

## 14. Failure and Degraded Modes (conceptual)

Per-scenario, for the recommended architecture (Option C/B):

- **Provider timeout / error:** job reaches `FAILED` via `JobLifecycle.fail(job_id, safe_message)` — the existing, already-redacted convention. `/reports/compare` is entirely unaffected (it's a separate capability).
- **Malformed model output:** `chat_json`'s existing parse-repair fallbacks (§5) handle the common cases (fenced code, a schema-echo envelope, a bare array/object); an unrecoverable case raises a plain `ValueError` with no retry (§5 — this happens after `chat_text`'s own retry loop already succeeded once, so it is not retried by the LLM layer). That `ValueError` propagates up to the job's own exception handling exactly like any other exception in `_run_pipeline`/`_run_explanation` today, reaching `FAILED` via `JobLifecycle.fail(job_id, safe_message)` — the raw `ValueError` text (which can include up to 400 characters of the model's actual output, per `agents/llm.py:483,505`) must be redacted/genericized before it reaches `safe_message`, following the exact existing convention that already governs every other exception on this path (§5, §15).
- **User disconnects:** SSE subscriber drops; `EventBus`'s existing per-subscriber-independent-iterator design means this has zero effect on the job itself (it keeps running/completing, exactly like Research/Learning today).
- **Request/job cancellation:** if cancellation is exposed (§7, §19.3 — an implementation detail, not an open architecture question), reuses `RUNNING_TASKS` + `JobLifecycle.cancel`'s existing idempotent behavior.
- **MongoDB failure:** identical failure surface to every existing job today — no new exposure.
- **Redis failure:** identical to today's job-store degraded behavior — no new exposure (and per the brief, no new Redis usage pattern is being proposed beyond the existing `JobStore`/`EventBus` shape).
- **Duplicate/concurrent generation requests — corrected in Revision 2:** `MAX_ACTIVE_JOBS` is a global admission budget, not an identity-scoped deduplication mechanism (§7) — two concurrent requests for the *same* explanation-generation identity (§12.2) can both be admitted under that budget and would, without an explicit dedup step, each start their own LLM generation. The architecture requires a lookup-before-create step against the explanation-generation identity, conceptually:

  ```text
  explanation generation identity
          ↓
   lookup existing artifact/job by that identity

   COMPLETED → reuse the existing explanation, no new generation
   RUNNING   → attach to / await the existing in-flight generation, no new generation
   FAILED    → permit a controlled retry per the eventual API contract, not an
               unbounded retry loop
   MISSING   → create the generation atomically
  ```

  This is an architectural requirement, not an implementation prescription: no distributed lock, no Redis-lock scheme, and no specific concurrency primitive is being specified here. The eventual implementation must provide atomicity appropriate to Mongo/job persistence (e.g. a conditional/idempotent write keyed on the explanation-generation identity — the exact mechanism is an implementation-contract decision, §19 deferred list). The frozen requirement is only that **the same explanation identity must not cause uncontrolled duplicate concurrent LLM generation.**

**First-class decision: does AI-explanation failure fail comparison?** **No.** The deterministic comparison result must never be corrupted, delayed, or blocked by explanation failure — comparison succeeds independently of explanation outcome, in every case: explanation failure, explanation still running, or explanation never requested. This is both the brief's explicit invariant and the natural consequence of Option C's separation. This differs from Learning's own precedent (where explanation *is* the entire deliverable, so a grounding failure fails the whole job) precisely because comparison has independent value the explanation doesn't gate.

---

## 15. Security Considerations

- **BYOK vs. managed:** inherits the existing policy (§13) — both are first-class, exactly as for Research and Learning today. Whichever the caller selects, credentials must never be persisted alongside the explanation document, matching the existing convention (BYOK keys live only in the per-request contextvar, never written to Mongo).
- **Credential isolation:** identical existing SSRF guard (`assert_public_url`) applies if a custom `base_url` is ever accepted for this capability, admin-gated exactly as `/reports/generate`'s custom-provider path is today.
- **Prompt injection:** the grounding input is the caller's *own* previously-generated report data (already access-controlled via EQ-3 ownership scoping) — no new untrusted-input surface beyond what report generation already accepts and defends against today.
- **Data exposure:** the explanation must never let a caller see report content they don't already have access to — trivially satisfied if generation only ever runs against `compare_reports`'s already-owner-scoped resolved set, never against raw request-supplied ids.
- **Logging:** no raw exception text, no API keys, in either logs reachable by the client or persisted documents — the existing `JobLifecycle.fail`/pipeline `except Exception` convention already enforces this; the new capability inherits it for free by reusing the same call.
- **Authorization:** identical `current_user` + EQ-3 owner-or-sample scoping as `compare_reports` itself.

---

## 16. Observability Requirements (minimum)

Comparison explanation reuses existing, generic job/LLM observability — no new
framework. This capability is a single `chat_json` call, not a LangGraph graph
(§5, §13.1), so nothing below presupposes a graph or LangGraph node boundaries; a
label value is added only where an existing metric's dimension genuinely fits:

- `jobs_active{kind="comparison_explanation"}` — the existing `kind`-scoped
  dimension already used by Research/Learning (`JobKind`) applies directly, with no
  graph assumption; extending it to a third `kind` value is exactly the extension
  Option B already requires (§5, §7).
- `llm_calls_total` / `llm_tokens_total` — already automatic inside `chat_text`, and
  therefore automatic for the recommended `chat_json` call too (§5 — `chat_json`
  delegates to `chat_text` for its one underlying call), labeled by provider/model/
  tier; no new label value needed, zero new code.
- Run-outcome visibility (completed/failed/cancelled) and deadline-exceeded
  visibility are reasonable to want, but the *existing* metrics for these
  (`pipeline_runs_total`, `deadline_exceeded_total`) are labeled `graph=...` — and,
  for deadline enforcement specifically, `node=...` — because they are tied to
  LangGraph's node-boundary deadline check (§5, §13.1: `is_past_deadline` is
  checked between `graph.astream()` node yields). Since this capability has no
  graph and no node boundaries, applying those labels verbatim (e.g.
  `graph="comparison_explanation"`) would misrepresent what's actually running.
  The exact metric name and label dimensions for this outcome/deadline visibility
  — a new `kind`-labeled counter, reuse of the job-status transitions
  `JobLifecycle` already records, or something else — is an engineering-task
  decision (§19.3), not fixed here.
- An OTel parent span for the job provides equivalent trace visibility without a
  graph; its exact name is likewise an engineering-task decision (§19.3), not
  fixed here — not necessarily `pipeline.comparison_explanation`, which would
  borrow the `pipeline.*` naming Research/Learning use specifically because those
  are LangGraph pipeline spans.

---

## 17. M9 Rescore Deletion Assessment

**Unaffected by everything above and ready for independent implementation.** Restating this session's full audit (unchanged from the prior recon pass): `POST /reports/rescore` ([backend/server.py:1622-1643](../../backend/server.py#L1622)) has zero frontend consumers (verified by full-repo search across `web/` and the frozen `frontend/`), zero backend consumers beyond its own dedicated tests, and its two dependencies — `require_admin` and `compute_scorecard` — are each used at multiple other call sites and must not be removed. The only living artifact requiring a change is `backend/tests/contract/test_route_inventory.py` (38→37 routes). **Ready.**

---

## 18. Scope Boundaries — what this pack does NOT include

- **No AI generation of any kind inside `POST /reports/compare`** — not a synchronous call, not a `generate_explanation` request flag, not any other implicit trigger. This endpoint's only job is the deterministic lookup it performs today (§10, §11).
- No general AI architecture redesign — `chat_text`/`chat_json`/the provider registry are reused verbatim.
- No new provider abstraction, no new retry system, no new job *framework* — `JobKind`/`JobLifecycle` are extended, not replaced.
- No new persistence architecture — the `reports`/`explanations` envelope pattern is repeated, not reinvented.
- No frontend changes of any kind (including `/reports/compare`'s own frontend integration, which needs zero changes under the recommended option).
- No Report View, Learning, or Financial Statement architecture changes.
- No unrelated API cleanup or security refactoring.
- No exact field names, route paths, or schemas are being decided here — those are engineering-task decisions (§19.3) once the contract-level choice (§10) and the genuinely open questions (§19.2) are ratified.

---

## 19. Decision Status

### 19.1 Frozen by this revision (no longer open)

The following are settled architecture, not pending questions — restated here so
Reviewer 2 and the CTO can freeze against a single list:

- `POST /reports/compare` remains deterministic, unchanged.
- No synchronous LLM call inside `POST /reports/compare`.
- No `generate_explanation` flag, or any other implicit AI-generation trigger, on `POST /reports/compare`.
- Comparison explanation is a separate capability (Option C, accepted by Reviewer 2).
- The existing async job infrastructure (`JobKind`/`JobLifecycle`/`JobStore`/`EventBus`) is reused as the execution mechanism (Option B), not replaced or redesigned.
- The explanation is a durable MongoDB artifact (§12.1).
- Redis remains ephemeral job/live state only, never the system of record for the explanation itself (§12.1).
- **Comparison explanation inherits the existing BYOK/managed-AI provider-selection policy used by the other AI capabilities** (§13.1) — both are first-class, exactly as for Research and Learning today; this is not a silent managed-AI-only exception. Any deliberate deviation from this policy for this specific capability requires its own explicit CTO/product approval — the inheritance itself is frozen, not the possibility of a future, explicitly-approved exception.
- Duplicate concurrent generation for the same explanation identity must be prevented through idempotent lookup-before-create semantics (§14) — the exact mechanism is deferred (§19.3), but the requirement itself is not.

### 19.2 Genuinely open (requires CTO / product approval)

Exactly one item remains — the real, unresolved product question:

1. **What does "explanation of differences" mean, precisely?** The only textual definition anywhere in the repository is `docs/design/05_Screen_Inventory.md`'s SCR-07: *"Copilot narrates the meaning of differences, grounded and sourced; never a buy/sell verdict."* This does not distinguish raw numerical deltas vs. semantic differences vs. materiality vs. causal/likely-cause analysis vs. broader financial interpretation. **Flagged as an unresolved product ambiguity — not invented or silently decided here, per this task's own instruction.**

### 19.3 Deferred to implementation (engineering decisions, not architecture uncertainty)

Legitimately undecided, and deliberately left undecided by this pack — none of these
block freezing the architecture above:

- Exact route path(s) for the new capability.
- Exact request/response schema and field names.
- Exact MongoDB collection name, indexes, and repository interface.
- Exact mechanism providing the idempotent lookup-before-create atomicity required by §14 (e.g. a conditional Mongo write) — the requirement is frozen, the mechanism is not.
- Exact SSE/streaming behavior and cancellation semantics (§7).
- Exact prompt content, output schema, and model tier.
- Exact observability metric name(s) and label dimensions for run-outcome and deadline-exceeded visibility, and the OTel parent span name (§16) — reuse existing Prometheus/OTel infrastructure, not graph-shaped labels for a capability with no graph.

---

## 20. Final Architecture Decision

```text
Architecture:
READY FOR REVIEWER 2 APPROVAL

Implementation:
NOT YET AUTHORIZED

Remaining product decision:
Meaning/semantics of "explanation of differences" (§19.2)

Rescore deletion:
READY FOR INDEPENDENT IMPLEMENTATION
```

The architecture in §19.1 is frozen — comparison stays deterministic and unchanged;
explanation is a separate, asynchronous capability on the existing job infrastructure
and existing AI provider/BYOK policy; persistence, identity, and idempotency are all
settled as described above. The single remaining item (§19.2) is a product-semantics
question, not an architecture question, and does not block Reviewer 2's architectural
sign-off — it blocks only the point at which an engineering task can pick an exact
prompt/output schema. Once §19.2 is resolved, implementation can proceed straight to
the engineering decisions in §19.3 with no remaining architectural ambiguity. Rescore
deletion (M9.2) may proceed independently at any time, on its own authorization,
without waiting on this decision.
