# Learning Backend Design (SCR-08)

**Status:** Design · **Milestone:** Backend Engineering M1 · **Date:** 2026-08-03
**Implements:** the frozen frontend contract in
`web/features/learning/integration/schemas.ts` + `api.ts`
**Governs:** `docs/design/06_UX_Specifications.md` SCR-08
**No contract in this document is new.** Every field, path, node name, and
status string below is transcribed from the approved frontend contract. Where
the design has latitude, that is stated explicitly.

---

## 1. Contract Review (as approved — not modified)

### 1.1 `POST /api/learning/explain`

Request (`explainRequestSchema`, `schemas.ts:29-38`):

```jsonc
{
  "ticker":            "string, max 20",       // required
  "concept":           "string, max 500",      // required
  "context_report_id": "string?",              // set when entering from SCR-06 "Explain This"
  "llm_provider":      "string?",              // BYOK, same semantics as /reports/generate
  "llm_api_key":       "string?",
  "llm_base_url":      "string?",
  "llm_model":         "string?"
}
```

Response (`explainResponseSchema`, `schemas.ts:41-43`): **`{ "id": "<uuid>" }`**

> ⚠️ **`id`, not `job_id`.** This is the single most likely implementation
> mistake — `POST /reports/generate` returns `{job_id}`, and the frontend's
> `apiFetch` validates at the trust boundary, so a copied handler fails
> immediately with an `AppError("validation")`. Same for cancel (§1.4). See
> API Coverage Audit F-1.

There is **no `cached` field** in the approved response (F-2) and **no
`no_cache` field** in the request. v1 therefore does not implement caching.

### 1.2 `GET /api/learning/{id}/stream` (SSE)

Framing is inherited verbatim from the report stream, because
`web/lib/api/sse-client.ts` is shared and generic:

- unnamed `data: <json>\n\n` messages;
- `: keepalive\n\n` comments (native `EventSource` ignores comments — they
  never reach `onmessage`);
- a terminal named event `event: end\ndata: {}\n\n`, after which the client
  calls `source.close()`;
- `Content-Type: text/event-stream`, `Cache-Control: no-cache`,
  `X-Accel-Buffering: no`, `Connection: keep-alive`;
- credentialed (`withCredentials: true`) → the session cookie gates it, and
  CORS must keep `allow_credentials=True` with an explicit origin.

Event payload (`streamEventSchema`, `schemas.ts:79-85`):

```jsonc
{ "node": "string", "status": "string", "message": "string?", "explanation": ExplanationDoc? }
```

Note: **no `ts`** in the Learning event schema (F-3). Emitting one is harmless
(Zod strips unknown keys) and is recommended for log correlation, but the UI
cannot use it.

**Node vocabulary is fixed by the UI** (`internal/streamStages.ts:25-36`).
`deriveStage` recognizes exactly:

| `node` | `status` | UI stage | UI label |
|---|---|---|---|
| `pipeline` | `start` | `thinking` | "Finding relevant filings…" |
| `pipeline` | `ok` | `completed` | "Explanation ready." |
| `pipeline` | `warn` | `cancelled` | "Explanation cancelled." |
| `pipeline` | `error` | `failed` | "The explanation failed." |
| `retriever` | any | `thinking` | "Finding relevant filings…" |
| `explainer` | any | `streaming` | "Writing the explanation…" |
| `final` | any | `completed` | — |
| *anything else* | any | `thinking` | (stuck in thinking) |

> **Binding constraint:** any node name outside `{pipeline, retriever,
> explainer, final}` leaves the UI in the "AI Thinking" state forever. The
> graph's node names are part of the contract.

The `final` event carries the completed `explanation` document; the
application layer writes it straight into the react-query cache
(`useExplanationJob.ts:81-83`) so the UI renders without a second fetch.

### 1.3 `GET /api/learning/{id}` (status)

Response (`explanationStatusResponseSchema`, `schemas.ts:67-71`):

```jsonc
{ "status": "string", "id": "string", "explanation": ExplanationDoc? }
```

`useExplanation` treats a missing `explanation` as `null` — "not finished yet"
— and does not branch on `status` values, so the status vocabulary is at the
backend's discretion. Recommended, matching reports: `queued` · `running` ·
`completed` · `failed` · `cancelled`.

`ExplanationDoc` (`schemas.ts:56-64`) — all fields **required** except
`company_name`:

```jsonc
{
  "id": "string", "ticker": "string", "concept": "string",
  "explanation": "string",                 // Markdown with [n] citation markers
  "source_documents": [SourceDocument],    // REQUIRED — Law 3 enforced by schema (F-5)
  "company_name": "string|null?",
  "created_at": "string"                   // ISO 8601
}
```

`SourceDocument` is **byte-identical** to the report one
(`doc_id, ticker, source, chunk_idx, text, score`) — i.e. exactly what
`agents/retrieval.py:retrieve()` already returns. No transformation needed.

### 1.4 `POST /api/learning/{id}/cancel`

Response (`cancelExplainResponseSchema`, `schemas.ts:74-77`):
**`{ "id": "string", "status": "string" }`** — again `id`, not `job_id`, and
**no `note` field** (reports has one).

Client behavior (`useExplanationJob.ts:107-112`): the UI closes the SSE stream,
dispatches `cancelled` locally, then fires the POST **fire-and-forget** —
`void learningApi.cancelExplanation(...)`. The response is never read and
errors are never surfaced. Implications:

- the endpoint **must be idempotent** and must tolerate being called after the
  stream is already closed, after the job finished, and for an unknown id;
- a non-2xx is invisible to the user, so cancel must not be the only path that
  stops server work.

---

## 2. Retrieval Pipeline

**Decision: reuse `agents/retrieval.py:retrieve()` unchanged.** It already
returns the exact `SourceDocument` shape the contract requires, already
degrades to BM25-only when models fail, and already caps at 2000 chunks
newest-first. No new retrieval code.

Two Learning-specific adaptations, both at the *call site*:

**R-1 · Query expansion.** A concept query is short ("free cash flow",
"operating leverage"). BM25 on 2–3 tokens against 900-char chunks is weak, and
the dense embedder's query prompt helps but does not fix recall. The retrieval
query is therefore composed rather than passed through:

```
retrieval_query = concept
                + " " + (company_name or ticker)
                + " " + (context_report.query if context_report_id else "")
```

The user-facing `concept` is stored verbatim in the document; only the
retrieval query is expanded. This is a call-site string concat — no change to
`retrieve()`.

**R-2 · `top_k = 6`, `candidate_k = 24` (default).** A learner explanation is
one prompt, not a five-node pipeline; 8 chunks × ~900 chars crowds out the
pedagogical instruction. 6 keeps the citation range small enough that `[n]`
markers stay meaningful.

**Empty-corpus behavior.** `retrieve()` returns `([], meta)` when the ticker
has no chunks. Because `source_documents` is a required non-empty-capable
array and Law 3 forbids ungrounded output, the explain job **fails fast**
rather than producing an unsourced explanation:

- emit `{"node":"pipeline","status":"error","message":"No filings ingested for
  {ticker}. Add a filing first."}` → UI shows the failure with retry, per
  SCR-08 Error Behaviour;
- do **not** fall back to a general-knowledge explanation. SCR-08's Interaction
  Rules require explanations "always tied back to the specific company".

This mirrors `POST /reports/generate`'s pre-flight `filing_chunks` count check
(`server.py:872-879`) — the same guard, but surfaced through the stream rather
than as a 400, because by then the job id has already been returned. **Both**
are implemented: a synchronous 400 on `POST /explain` when the ticker has zero
chunks (fails before a job exists, cheapest path), and the streamed error as a
backstop for a corpus that empties mid-run.

---

## 3. LangGraph Workflow

**Decision: a new two-node graph, not a variant of the report graph.**

```
START ──► retriever ──► explainer ──► END
```

New files:

- `agents/learning_state.py` — `LearningState(TypedDict, total=False)`
- `agents/learning_graph.py` — `build_learning_graph(db)`
- `agents/learning_nodes.py` — `explainer_node`

`retriever_node` is **reused verbatim** from `agents/nodes.py`. It reads
`state["ticker"]` and `state["query"]`, so `LearningState` carries `query` (the
expanded retrieval string from R-1) alongside `concept` (the user's words, for
display and prompting). No fork, no parameterization, no change to `nodes.py`.

```python
class LearningState(TypedDict, total=False):
    ticker: str
    query: str                  # expanded retrieval query (R-1) — what retriever_node reads
    concept: str                # verbatim user input — what the prompt and doc use
    company_name: str
    prior_brief: str            # from context_report_id, capped
    prior_financials: dict      # from context_report_id's extracted_data
    source_documents: list[SourceDocument]
    explanation: str
    trace: Annotated[list[dict], add]
```

`explainer_node` emits its trace event with `node="explainer"` so the UI
transitions to `streaming` (F-4).

### 3.1 Why no extractor / tone / fact-checker

| Node | Included? | Reasoning |
|---|---|---|
| `extractor` | ❌ | The contract has no structured-financials field. When `context_report_id` is set, the *already-extracted* financials from that report are injected instead — a Mongo read, not an LLM call. |
| `tone` | ❌ | Sentiment is not part of an explanation. No contract field. |
| `fact_checker` | ❌ | **Decision, see §5.3.** The contract carries no `fact_check_status`, `validation_errors`, or `scorecard` field, and SCR-08's frozen Loading Behaviour is exactly two states — *AI Thinking → AI Streaming* — with no verification stage. A retry loop would double p50 latency for a learner-facing feature and produce a stage the UI has no vocabulary for. Grounding is enforced by prompt + deterministic citation validation instead. |

This keeps a Learning run at **one LLM call** vs. the report pipeline's 4–6,
which is the difference between a ~6s and a ~40s response for a feature whose
UX invites repeated follow-ups.

---

## 4. Prompt Orchestration

One call, `chat_text(system, user, model=DEFAULT_HEAVY_MODEL)`.

**Heavy, not light.** The report pipeline spends light-model calls on
extraction and tone because those are mechanical; the one thing it uses the
heavy model for is prose the user reads. An explanation is entirely prose the
user reads, and it is a single call with no retry loop — the cheapest place in
the product to spend the better model.

### 4.1 System prompt (derived from SCR-08, lines 249-260)

Each clause traces to a frozen requirement:

| Prompt clause | Source |
|---|---|
| explain to a learner, assume no finance background | "pitches explanations to a learner"; Persona P-02 |
| always ground in *this company's* actual figures from the excerpts | "tied to the company's figures"; Interaction Rules |
| cite inline as `[1]`, `[2]` using the excerpt numbers | "grounded and sourced"; Information Hierarchy → "source" |
| never state a number not present in the excerpts; say "not disclosed" | Law 3; mirrors `nodes.py:162-167` |
| end by inviting a specific follow-up question | "invites the next question rather than closing the topic" |
| under 400 words | learner-appropriate; report brief is capped at 500 |

### 4.2 User message assembly

```
# Concept to explain: {concept}
# Company: {company_name or ticker} ({ticker})

## Source excerpts (cite by number)
{_format_docs(docs, max_chars=6000)}

[if context_report_id]
## What this company's latest brief found (context for the explanation)
{prior_brief[:1200]}
### Figures already extracted from that brief
{prior_financials}
[/if]

Explain the concept, then show how it applies to {company} using the figures
above. Close with one follow-up question the reader could ask next.
```

`_format_docs` is reused from `agents/nodes.py:21` — unchanged, with a lower
`max_chars` (6000 vs 8000) to leave room for the pedagogical framing.

The `context_report_id` injection is the same shape as the synthesizer's
`prior_brief` block (`nodes.py:149-160`), including the 1200-char cap, for the
same reason: prior context must inform, not dominate.

### 4.3 Provider / BYOK routing

Identical to `_run_pipeline` (`server.py:685-690`): if `llm_provider` or
`llm_api_key` is present, `set_llm_context(...)` before the run and
`reset_llm_context(tok)` in `finally`. The same admin gate and SSRF guard apply
to `llm_base_url` — **this is not optional.** `POST /api/learning/explain`
accepts a client-supplied `llm_base_url` (`schemas.ts:36`), which makes it a
new server-side-fetch surface. It must replicate `server.py:846-870` verbatim:

- `custom` provider or any `llm_base_url` → `auth.is_admin(user)` or **403**;
- `llm_base_url` → `assert_public_url(...)` or **400**.

Omitting this would open an SSRF hole that the report path closed.

---

## 5. Citation Generation & Source Attribution

### 5.1 Convention

`[n]` is a **1-based index into `source_documents` as returned in the same
document** — identical to reports, so `web/lib/markdown/citations.ts` renders
Learning explanations with no frontend change. `_format_docs` already numbers
excerpts `[1]…[k]` in the prompt in the same order, so the mapping is
positional and requires no id bookkeeping.

### 5.2 Deterministic post-processing (replaces the fact-checker)

Before persisting, `explanation` passes through a pure function
(stdlib `re` only, in the spirit of `agents/scoring.py`):

1. **Strip out-of-range markers.** Any `[n]` where `n < 1` or `n > len(docs)`
   is removed. An LLM inventing `[9]` against 6 sources produces a dangling
   citation the UI would render as a broken link.
2. **Record which sources were actually cited.** Reuse
   `scoring._CITATION_RE`; the cited set is stored on the persisted document
   for later quality analysis (not exposed in the API response — no contract
   field).
3. **Reject an uncited explanation.** If the text contains **zero** valid
   markers, the job fails with `{"node":"pipeline","status":"error"}` rather
   than persisting ungrounded output. This is the enforcement of Law 3 that
   the absence of a fact-checker would otherwise leave to the prompt alone.

Cost: ~20 lines, zero LLM calls, deterministic, unit-testable without a
network.

### 5.3 Engineering note — the grounding trade-off

The report pipeline verifies **numeric** claims only, and a purely qualitative
fabrication is trivially accepted at faithfulness 1.0 — a limitation already
recorded in-code (`nodes.py:200-205`, `ponytail:`). A learner explanation is
*mostly* qualitative, which is precisely the class the existing fact-checker
cannot catch. Adding the existing fact-checker to Learning would therefore add
latency and a contract-less UI stage while catching very little.

The defense that actually fits this content type is §5.2's citation validation
plus the prompt's "never state a number not in the excerpts". If a stronger
guarantee is later required, the upgrade path is an entailment check over
declarative sentences — the same upgrade path already recorded for the report
fact-checker, and it should be taken for both features at once or neither.

---

## 6. Streaming Architecture

### 6.1 Fix the fan-out defect rather than inherit it

The report stream's single `asyncio.Queue` per job (Architecture Review **D-1**)
splits events between concurrent readers. Learning's stream is a copy of that
code, so copying it ships the defect twice.

**Design: per-connection subscriber queues.**

```python
# agents/jobs.py (new, shared by reports and learning)
job["subscribers"]: list[asyncio.Queue]

def subscribe(job) -> asyncio.Queue:
    q = asyncio.Queue()
    job["subscribers"].append(q)
    return q

async def push(job, ev):                     # replaces server.py:698-705
    job["events"].append(ev)
    for q in job["subscribers"]:
        await q.put(ev)                      # every subscriber gets every event
    await db.<jobs_coll>.update_one({"id": job["id"]},
        {"$push": {"events": ev}, "$set": {"updated_at": ev["ts"]}})
```

The SSE generator then replays `job["events"]` **and subscribes atomically**
(subscribe first, snapshot second, dedupe by index) — which also deletes the
fragile `to_skip` counter at `server.py:989-996`. On disconnect, `finally:
job["subscribers"].remove(q)`.

This is ~30 LOC in one shared module and fixes reports at the same time.

> **Recommendation:** land `agents/jobs.py` as the first commit of the Learning
> build, migrate `_run_pipeline` onto it in the same change, then build
> Learning on top. Building Learning first and refactoring later means writing
> the defect deliberately.

### 6.2 Token-level streaming — explicitly out of scope

The UI's `streaming` stage is derived from a **node-level** event
(`node: "explainer"`), and the completed text arrives in one `final` event. The
approved contract has no token-delta event type. `agents/llm.py` has no
streaming interface. v1 emits: `pipeline/start` → `retriever/ok` →
`explainer/start` → `explainer/ok` → `final` → `pipeline/ok` → `event: end`.

This satisfies SCR-08's frozen Loading Behaviour exactly. Token streaming would
require a contract change and is not proposed.

### 6.3 Keepalive

Same 120s `asyncio.wait_for` timeout → `: keepalive\n\n`. A single-LLM-call job
rarely needs it, but a cold fastembed load (~30-40s per
`server.py:1182-1196`) plus a slow provider can approach it.

---

## 7. Job Lifecycle & Persistence

### 7.1 ⚠️ Engineering Question EQ-1 — Redis

> **The Milestone brief specifies a "Redis job lifecycle." Redis does not exist
> anywhere in this system**, and adopting it conflicts with approved
> governance. Raising rather than silently implementing, per the milestone's
> own instruction.
>
> **Evidence:**
> - Redis appears in **zero** source files, **zero** governance documents, and
>   is absent from `backend/requirements.txt`. The only two mentions in the
>   entire repository are *hypothetical upgrade paths* in comments:
>   `agents/auth.py:45-46` ("move to Mongo/Redis if it ever scales to multiple
>   instances") and `docs/planning/03-Technical-Architecture.md:59` ("move to
>   Redis pub/sub to scale horizontally").
> - `CLAUDE.md` § Dependencies: *"Keep both dependency manifests lean… Before
>   adding a dependency, confirm nothing already installed (or the stdlib /
>   platform) does the job."*
> - A job lifecycle **already exists and is in production use**: in-process
>   registry + `asyncio.Queue` + a Mongo `jobs` collection mirror that already
>   survives client reconnects (`server.py:52-53`, `:694-705`, `:1027-1031`).
> - Redis's actual value is **multi-instance** deployment. The runtime is
>   single-process by design (`scripts/run.py` starts one uvicorn); there is no
>   deployment configuration, no container orchestration, and no CI in the
>   repository. Redis would add an operational dependency to `run.py`'s
>   bootstrap (which already provisions a portable MongoDB) to solve a problem
>   this deployment does not yet have.
>
> **Recommendation: implement the Mongo-mirrored lifecycle (§7.2) for v1.** It
> is the pattern reports already uses, needs zero new dependencies, and its
> upgrade path to Redis is already documented in the Technical Architecture.
>
> **If Redis is nonetheless required**, §7.4 specifies exactly what changes —
> the design below is deliberately structured so the swap touches one module.
>
> **This question does not block the build.** Everything else in this document
> is implementable today.

### 7.2 Recommended lifecycle (Mongo-mirrored, dependency-free)

Two new collections, mirroring `jobs` / `reports`:

| Collection | Document |
|---|---|
| `explanation_jobs` | `{id, user_id, ticker, concept, context_report_id, status, created_at, updated_at, completed_at, events[]}` |
| `explanations` | `ExplanationDoc` + `{user_id, cited_sources[], retrieval_meta, events[]}` |

Extra persisted fields (`user_id`, `cited_sources`, `retrieval_meta`) are
**stripped from the API response**, which returns exactly the approved
`ExplanationDoc` keys. Persisting more than the contract exposes is how
`reports` already works (`events`, `user_id`, `verified_claims` are all
persisted; list responses project them out at `server.py:1050`).

State machine:

```
queued ──► running ──┬──► completed      (explanation persisted, final event sent)
                     ├──► failed         (pipeline/error event, nothing persisted to `explanations`)
                     └──► cancelled      (pipeline/warn event)
```

Terminal states are absorbing. `_reap_jobs()` and `MAX_ACTIVE_JOBS` are
**shared with reports** through `agents/jobs.py` — a shared concurrency budget,
so Learning cannot starve report generation and vice versa. Add
`completed_at` while touching this code (Architecture Review D-8).

**Restart recovery (fixes D-6 for both features):** on startup, sweep
`explanation_jobs` and `jobs` for `status ∈ {queued, running}` and mark them
`failed` with a "server restarted" message. Without this, an in-flight job
after a restart reports `running` forever with no producer.

### 7.3 Endpoint handlers

```
POST /api/learning/explain
  ├─ current_user (401 if absent)                      # login wall, same as every tool route
  ├─ validate: ticker non-empty, concept non-empty (400)
  ├─ custom provider / llm_base_url → is_admin (403), assert_public_url (400)   # §4.3
  ├─ filing_chunks count for ticker == 0 → 400          # §2
  ├─ shared concurrency cap exceeded → 429
  ├─ resolve company_name (companies collection), prior brief (if context_report_id, scoped to caller)
  ├─ insert explanation_jobs doc (status=queued)
  ├─ create asyncio.Task(_run_explanation(...))
  └─ 200 {"id": job_id}                                 # NOT job_id — F-1

GET /api/learning/{id}/stream
  ├─ current_user; job exists (404); job.user_id == caller (404)
  ├─ subscribe() → replay job["events"] → drain subscriber queue    # §6.1
  └─ on sentinel: emit {"node":"final", "status":"ok", "explanation": <doc>} then `event: end`

GET /api/learning/{id}
  ├─ current_user; scoped lookup in `explanations` → {"status":"completed","id","explanation"}
  ├─ else `explanation_jobs` → {"status": <status>, "id"}
  └─ else 404

POST /api/learning/{id}/cancel
  ├─ current_user; unknown id → 404
  ├─ already terminal → 200 {"id", "status": <existing>}   # idempotent, no `note` field (F-1)
  └─ else task.cancel(); status=cancelled; 200 {"id","status":"cancelled"}
```

**Ownership scoping.** Learning reads are scoped to `user_id`. This
deliberately diverges from `GET /reports/{id}`, which is unscoped by an
accepted-risk decision recorded at `server.py:1059-1064`. Scoping a *new*
surface costs one query predicate; inheriting the looser posture would extend
an accepted risk to code that never had to carry it. Raised as **EQ-3**
(Architecture Review §7) — if the ruling is to match reports exactly, remove
the predicate.

### 7.4 Redis variant (only if EQ-1 is decided in Redis's favor)

Contained to `agents/jobs.py`:

| Concern | Mongo (recommended) | Redis |
|---|---|---|
| Job record | `explanation_jobs` doc | `HSET learn:job:{id}` + `EXPIRE` |
| Event log / replay | `$push` to `events[]` | `XADD learn:events:{id}` (Stream), replay via `XRANGE` |
| Live fan-out | in-process subscriber queues (§6.1) | `XREAD BLOCK` per connection — fan-out for free, multi-instance |
| Cancellation | `task.cancel()` (same process) | `PUBLISH learn:cancel:{id}`; every instance subscribes and cancels if it owns the task |
| Concurrency cap | `len(JOBS)` scan | `INCR/DECR learn:active` |
| Final document | `explanations` collection | still Mongo — Redis is not the system of record |

Additional cost: one dependency (`redis>=5` with asyncio support), a Redis
server in `scripts/run.py`'s bootstrap alongside the portable MongoDB, a new
failure mode (Redis down → all jobs unstartable, where today Mongo-down is
already fatal so no *new* class of outage), and an operational surface with no
current deployment target. **A Redis Stream is the right answer the day a
second backend instance exists. It is not required for any behavior in the
approved contract.**

---

## 8. Failure Recovery

SCR-08 Error Behaviour (frozen): *"AI failure offers retry; prior explanation
retained."*

| Failure | Backend behavior | UI result |
|---|---|---|
| No chunks for ticker | 400 on `POST /explain` (pre-flight) | `startError` surfaces; retry available |
| Retrieval throws | `retriever_node` already catches and returns `[]` + an error trace (`nodes.py:44-50`) → §2's empty-corpus path → `pipeline/error` | `failed` stage + retry |
| LLM transient error | `chat_text` retries ×4 with backoff (existing, `llm.py:310-325`); exhaustion → `pipeline/error` | `failed` + retry |
| LLM non-retryable (bad key, truncation) | `NonRetryableLLMError` raised immediately, no backoff | `failed` + retry |
| Zero valid citations (§5.2) | `pipeline/error`, nothing persisted | `failed` + retry |
| Provider error text | **Never echoed.** `logger.exception` + a fixed user-facing string, exactly as `server.py:779-795` — provider SDK exceptions can embed the API key | safe message |
| Client disconnects mid-run | Job continues; events keep landing in `job["events"]` + Mongo; subscriber queue removed in `finally` | reconnect replays from `job["events"]` |
| Server restart mid-run | Startup sweep marks `running` → `failed` (§7.2) | `failed` + retry, not a permanent spinner |
| Cancel after completion | Idempotent 200 with the existing status | no-op (response unread anyway) |

**"Prior explanation retained" is client-side.** `useExplanationJob`'s reducer
never clears `events`/data on error, and the completed doc lives in the
react-query cache under `["learning","explanation",jobId]`. The backend
requirement is only **not to clobber**: a failed run must not overwrite or
delete a previously persisted `explanations` document. Since retry issues a
**new job id** (`retry` → `startMutation.mutate` → a fresh `POST`), each run
writes a distinct document and this holds naturally. No resume, no
idempotency-key handling, no server-side retry state.

---

## 9. Build Order

| # | Change | Why first |
|---|---|---|
| 1 | `agents/jobs.py` — shared lifecycle + per-connection SSE fan-out (§6.1); migrate `_run_pipeline` onto it | Fixes D-1 once instead of shipping it twice; gives Learning a home for §7.2 |
| 2 | Startup sweep for orphaned `running` jobs (D-6); `completed_at` (D-8) | Same module, same commit window |
| 3 | `learning_state.py`, `learning_graph.py`, `learning_nodes.py` + citation post-processor (§5.2) | Pure logic, unit-testable with no network — the first thing in this backend that can have real unit tests |
| 4 | Four route handlers (§7.3) incl. the admin/SSRF gate (§4.3) | — |
| 5 | Contract test: assert every Learning response validates against the frozen Zod shapes (F-6) | The `id`-vs-`job_id` class of bug (F-1) is exactly what this catches |

---

## 10. Open Questions

| ID | Question | Status |
|---|---|---|
| **EQ-1** | Redis vs. Mongo-mirrored job lifecycle (§7.1) | **Raised — decision needed.** Does not block; Mongo variant is the recommended default and is fully specified. |
| **EQ-3** | Scope Learning reads to the owner (recommended), or match reports' accepted-risk unscoped posture? (§7.3) | **Raised.** Default taken: scoped. One-line reversal if ruled otherwise. |
| EQ-4 | Should `explanations` be listable/browsable (a "learning history")? No approved screen, no contract, no route. | Not implemented. Out of scope until a screen exists. |
| EQ-5 | Should Learning cache on `(ticker, concept, context_report_id)` the way reports caches on `(ticker, query)`? | **Not in v1** — the approved response has no `cached` field (F-2), and a cache hit would return a job id whose stream has already terminated, which the current stream design cannot replay cleanly. Revisit with the contract owner if cost becomes a driver. |

---

*Cross-references: `01_Backend_Architecture_Review.md` (D-1, D-6, D-8, EQ-1,
EQ-3), `02_API_Coverage_Audit.md` (F-1…F-6), `05_Testing_Audit.md` (§3, §4).*
