# LangGraph Architecture

**Status:** 🔒 **FROZEN** — `v1.0`, ratified 2026-08-03 · amendments only (§13)
**Milestone:** Backend Engineering M1 (post-audit) · **Date:** 2026-08-03
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main` · commit `7404b67`
**Depends on:** [`06_Clean_Architecture_Migration_Plan.md`](06_Clean_Architecture_Migration_Plan.md) (AD-7, AD-12, AD-13),
[`03_Learning_Backend_Design.md`](03_Learning_Backend_Design.md) (frozen node vocabulary)
**Referenced by:** [`08`](08_MongoDB_Data_Architecture.md) §5.3, §12.3 · [`09`](09_Redis_Architecture.md) §5, §6.2, §12

### Document control

| Version | Date | Change |
|---|---|---|
| **v1.0** | **2026-08-03** | **FROZEN.** Final consistency pass: cross-references, ID uniqueness, inter-document contradictions, ratification/register sync, diagram fidelity, and API-contract invariance all verified. |
| v1.0-rc1 | 2026-08-03 | Added §5 (execution limits, retry budgets, timeouts); added §4.4 execution-timeline diagram; fixed cross-references; freeze-ready |
| v0.9 | 2026-08-03 | Initial proposal |

> **ID prefixing.** IDs defined here use `G-`, `N-`, `LG-`, `LR-`, `EB-`.
> References to IDs owned by another document are prefixed with that
> document's number — e.g. `06 AD-7`, `01 D-1`, `02 F-1`.

---

## 0. Scope & Binding Constraints

Governs the **agent orchestration layer**: graph topology, state, node
contracts, execution budgets, streaming, cancellation, and instrumentation.
Prompts are owned by [`03`](03_Learning_Backend_Design.md) §4 and
`agents/nodes.py`; persistence by [`08`](08_MongoDB_Data_Architecture.md).

| # | Constraint | Source |
|---|---|---|
| G-1 | **Node names are part of the API contract.** The UI derives its loading state from `event.node`; an unrecognized name leaves it stuck in "AI Thinking". Research: `pipeline`, `retriever`, `extractor`, `tone`, `synthesizer`, `fact_checker`, `final`. Learning: `pipeline`, `retriever`, `explainer`, `final`. | `web/features/*/internal/streamStages.ts` |
| G-2 | **Trace event shape is frozen:** `{node, status, message, ts, …extra}`, `status ∈ {start, ok, warn, error}`. | `agents/nodes.py:11-18`; `*/integration/schemas.ts` |
| G-3 | **Research retry is capped at ≤2 re-syntheses**; the UI displays `retry_count`. | `nodes.py:304-310`; `reportDocSchema.retry_count` |
| G-4 | **No token-level streaming.** No delta event type exists in either approved contract. | [`03`](03_Learning_Backend_Design.md) §6.2 |
| G-5 | **Nodes never raise past their own boundary.** Every node catches and returns a degraded state + an `error` trace event — load-bearing for the best-effort-sources rule (`06` C-8). | `nodes.py:43-50, 92-96, 124-128, 191-195, 264-271` |

---

## 1. Baseline

One graph, compiled at import (`server.py:77` — removed by Migration Phase 1),
five nodes, one conditional edge.

```
START ──► retriever ──┬──► extractor ──┐
                      └──► tone ───────┴──► synthesizer ──► fact_checker ──┬─► accept ──► END
                                              ▲                            ├─► retry ────┘
                                              └────────────────────────────┘  (retry_count < 2)
                                                                           └─► give_up ─► END
```

- **State:** `AgentState` TypedDict, `total=False`, one reducer —
  `trace: Annotated[list[dict], add]` (`state.py:58`).
- **Fan-in:** `extractor` and `tone` both edge into `synthesizer`; LangGraph
  joins them. Their trace events interleave nondeterministically — tolerated by
  the UI, and the reason per-node timing cannot be derived by differencing
  timestamps ([`04`](04_Observability_Audit.md) O-8).
- **Execution:** `graph.astream(initial, {"recursion_limit": 25})`; each yielded
  `{node_name: node_return}` merges into `final_state` and its `trace` entries
  are pushed to the event transport.
- **Injection:** `partial(retriever_node, db=db)` — the `01 B-2` violation.

The topology is sound and does not change. What changes: how nodes receive
dependencies, how many graphs exist, what bounds execution, and what is
observable.

---

## 2. Target Architecture

### 2.1 Two graphs, one node library

```
                         agents/nodes/                      (shared, port-injected)
    ┌────────────────────────────────────────────────────────────────────────┐
    │ retriever   extractor   tone   synthesizer   fact_checker   explainer  │
    └────┬─────────────┬──────────┬─────────┬───────────┬─────────────┬──────┘
         │             │          │         │           │             │
    ┌────┴─────────────┴──────────┴─────────┴───────────┴───┐   ┌─────┴──────────┐
    │ agents/graphs/research.py                             │   │ graphs/        │
    │   build_research_graph(container) -> CompiledGraph    │   │ learning.py    │
    │   START→retriever→(extractor ‖ tone)→synthesizer      │   │  START→        │
    │        →fact_checker→{accept | retry | give_up}       │   │  retriever→    │
    │   ≤6 LLM calls                                        │   │  explainer→END │
    └───────────────────────────────────────────────────────┘   │  exactly 1 call│
                                                                └────────────────┘
         Both compiled once in app/container.py (06 AD-3, LG-10).
```

`retriever` is **shared verbatim**. It reads `state["ticker"]` and
`state["query"]`; the Learning use case places its expanded retrieval query
([`03`](03_Learning_Backend_Design.md) §2 R-1) in `query` and keeps the user's
words in `concept`. No fork, no flag, no parameterization.

### 2.2 Node dependency injection (`06 AD-7`)

```python
# before (01 B-2):  partial(retriever_node, db=db)        ← motor handle on the domain path
# after:
g.add_node("retriever", traced(partial(retriever_node, chunks=c.chunks)))   # ChunkRepository
g.add_node("explainer", traced(partial(explainer_node, llm=c.llm)))         # LLMClient
```

Every node becomes `async def node(state, *, <ports>) -> dict`. A node is then
unit-testable with a 10-line fake and zero infrastructure — the first time that
is true in this codebase.

### 2.3 State design

```python
# agents/state.py
class AgentState(TypedDict, total=False):
    ticker: str; query: str; prior_brief: str
    source_documents: list[SourceDocument]
    extracted_data: ExtractedFinancials          # written only by `extractor`
    sentiment_analysis: ToneAnalysis             # written only by `tone`
    draft_report: str
    fact_check_status: bool; validation_errors: list[str]
    verified_claims: list[dict]; retry_count: int
    deadline_at: float                           # ✅ monotonic deadline — §5.4
    trace: Annotated[list[dict], add]

# agents/learning_state.py
class LearningState(TypedDict, total=False):
    ticker: str
    query: str            # expanded retrieval query — what `retriever` reads
    concept: str          # verbatim user input — what `explainer` prompts with
    company_name: str; prior_brief: str; prior_financials: dict
    source_documents: list[SourceDocument]
    explanation: str
    deadline_at: float                           # ✅ §5.4
    trace: Annotated[list[dict], add]
```

**Reducer policy — the one rule that keeps fan-in correct.** `add` on `trace`
only; every other key is last-writer-wins. Safe today because no two
concurrently-executing nodes write the same key. **Any new parallel branch must
either write a disjoint key set or declare an explicit reducer.** LangGraph does
not enforce this; §8 does (state-merge test), and it is restated as a module
docstring in `state.py`.

**Separate state classes, not a union.** A shared `total=False` state would let
a Learning node read `fact_check_status` and typecheck — the coupling that made
`_run_pipeline` un-reusable (`01 V-1`).

---

## 3. Node Contract

| # | Rule | Why |
|---|---|---|
| **N-1** | Returns a partial state dict; never mutates the input state. | LangGraph merge semantics; keeps nodes referentially transparent. |
| **N-2** | **Never raises** (G-5). Catches its own failures, returns a degraded value + an `error` trace event. | A raising node aborts `astream`, which the UI reads as a hard failure rather than a degraded-but-usable result. |
| **N-3** | Emits ≥1 trace event carrying its own contract-bound `node` name (G-1). | The UI stage machine is driven entirely by these. |
| **N-4** | Depends only on ports (`06 AD-7`). No `motor`, no provider SDK, no `os.environ`. | Testability + the `06 AD-5` dependency rule. |
| **N-5** | Tolerates missing upstream state — `state.get(...)` with a default. | Already the de-facto behavior; formalized. |
| **N-6** | ✅ **Checks the deadline before starting expensive work** (§5.4). | Bounds worst-case job duration without a hard kill mid-write. |

### 3.1 Node catalog

| Node | Graph | Ports | LLM calls | Degraded return (N-2) |
|---|---|---|---|---|
| `retriever` | both | `ChunkRepository` | 0 | `[]` + `error` event |
| `extractor` | research | `LLMClient` (light) | 1 | `{}` + `error` event |
| `tone` | research | `LLMClient` (light) | 1 | `{}` + `error` event |
| `synthesizer` | research | `LLMClient` (heavy) | 1 (×≤3 total, G-3) | `""` → fact_checker flags "No draft" |
| `fact_checker` | research | `LLMClient` (heavy) | 0 or 1 (×≤3) | `fact_check_status=False`, `retry_count+1` |
| `explainer` | learning | `LLMClient` (heavy) | 1 | `""` → use case fails the job |

**Research worst case: 6 LLM calls. Learning: exactly 1.** That ratio is the
justification for LG-1 (a separate two-node graph rather than a parameterized
research graph).

---

## 4. Streaming Architecture

### 4.1 Event flow

```
 node returns {..., "trace": [TraceEvent]}
        │
        ▼
 graph.astream(state)  yields {node_name: partial_state}
        │
        ▼
 application/{research,learning}.py  _run() loop
        │  ├─ merge partial into final_state
        │  └─ for ev in partial["trace"]: await events.publish(job_id, ev)
        ▼
 EventBus port (06 AD-8)  — in-process fan-out (Ph 4) → Redis Streams (Ph 7, 09 §4)
        │
        ├──► subscriber A ──► SSE generator ──► `data: {...}\n\n`
        └──► subscriber B ──► SSE generator ──► `data: {...}\n\n`   ← 01 D-1 fixed
                                                     │
                                                     └─ terminal → `event: end\ndata: {}\n\n`
```

**`astream` mode:** default (`updates` semantics — one `{node: partial}` per
node completion). Not `values` (re-emits the whole state per step, including the
full `source_documents` array on every tick) and not `messages` (no chat-message
model here).

### 4.2 Event envelope (frozen — G-1/G-2)

| # | Event | Emitted by | Learning equivalent |
|---|---|---|---|
| 1 | `{node:"pipeline", status:"start"}` | use case, before `astream` | same |
| 2… | per-node `{node:"<name>", status:"ok"\|"warn"\|"error"}` | nodes | `retriever`, `explainer` |
| n-2 | `{node:"final", status:"ok", report:…}` | use case, after persistence | `{…, explanation:…}` |
| n-1 | `{node:"pipeline", status:"ok"}` | use case | same |
| n | `event: end` (SSE frame, not a trace event) | SSE generator | same |

Failure replaces n-2/n-1 with `{node:"pipeline", status:"error", message:"<safe
text>"}`; cancellation and **deadline expiry** (§5.5) with `status:"warn"`.

> **`pipeline` wrapper events are emitted by the use case, not a graph node**
> (LG-4). They bracket the graph run purely to drive the UI state machine, so a
> future topology change cannot break them.

### 4.3 Why no token streaming (G-4)

The UI's `streaming` stage derives from a **node-level** event
(`node:"explainer"`); the completed text arrives in one `final` event. Neither
approved contract defines a delta event type and `LLMClient` has no streaming
method. Adding it would change both the API contract (`06` C-1) and frontend
behavior (`06` C-2). **Out of scope; not a deficiency.**

### 4.4 Execution timeline (research, typical run)

```
t=0s    ├─ pipeline/start ──────────────────────────────► UI: "AI Thinking"
        │
0.1–3s  ├─ retriever ────► Mongo query + BM25 + dense + cross-encoder
        │                  (cold start: +30–40s for ONNX model load)
        ├─ retriever/ok ─────────────────────────────────► UI: "AI Thinking"
        │
3–12s   ├─ extractor  ─┐  light model, parallel
        ├─ tone       ─┘  light model, parallel
        ├─ extractor/ok, tone/ok  (order nondeterministic — LR-7)
        │
12–30s  ├─ synthesizer ──► heavy model
        ├─ synthesizer/ok ───────────────────────────────► UI: "AI Streaming"
        │
30–42s  ├─ fact_checker ─► heavy model
        │   ├─ all claims supported ──► accept
        │   └─ flagged ──► retry ──► synthesizer (≤2×, G-3) ── adds ~25s each
        │
~42s    ├─ persist report + scorecard
        ├─ final  (carries the full report document)
        ├─ pipeline/ok
        └─ event: end ───────────────────────────────────► UI: "completed"
```

Learning collapses this to `pipeline/start → retriever → explainer → final →
pipeline/ok → end`, typically **4–8 s** warm.

---

## 5. Execution Limits, Retry Budgets & Timeout Policy

The system's current bounds are **local** — each retry loop and each network
call is individually capped, but nothing caps their product. §5.3 computes what
that composition actually allows. §5.4 introduces the one missing control.

### 5.1 Inventory of existing limits

| # | Limit | Current value | Source | Scope |
|---|---|---|---|---|
| X-1 | LangGraph `recursion_limit` | 25 supersteps | `server.py:720` | per graph run |
| X-2 | `chat_text` attempts | **4** | `llm.py:312` | per LLM call site |
| X-3 | `chat_text` backoff | `2·(n+1)` s, capped 30 s; provider `retry_delay` honored when parsed | `llm.py:321-324` | between attempts |
| X-4 | Provider SDK internal retries | **0** (deliberate — `chat_text` owns retries) | `llm.py:196, 224` | per attempt |
| X-5 | Per-call network timeout `LLM_REQUEST_TIMEOUT` | **120 s** | `llm.py:154` | per attempt |
| X-6 | Fact-check re-synthesis | **≤2** (G-3) | `nodes.py:308` | per research run |
| X-7 | Output cap `LLM_MAX_OUTPUT_TOKENS` | 2048 (OpenAI-compatible); 4096 (Anthropic); unbounded (Gemini) | `llm.py:207, 226` | per call |
| X-8 | Retrieval chunk cap | 2000 newest | `retrieval.py:161` | per retrieval |
| X-9 | Rerank candidate cap | `candidate_k=24` | `retrieval.py:147` | per retrieval |
| X-10 | Concurrent jobs `MAX_ACTIVE_JOBS` | 8 | `server.py:58` | server-wide |
| X-11 | Job registry history | 200 | `server.py:59` | server-wide |
| X-12 | SSE keepalive interval | 120 s → **15 s** with Redis `XREAD block` | `server.py:991`; [`09`](09_Redis_Architecture.md) §4.3 | per connection |
| X-13 | External HTTP timeouts | EDGAR 30 s · BSE 25 s · SEC index 15 s · Resend 10 s | `ingest.py:37,221`, `company_index.py:41`, `notify.py:36` | per fetch |
| X-14 | **Mongo query timeout** | ❌ **none set** | — | — |
| X-15 | **Whole-job wall clock** | ❌ **none** | — | — |

### 5.2 ⚠️ Two gaps

**X-14 — no `maxTimeMS` on any Mongo operation.** The retrieval query
(`filing_chunks.find({ticker}).sort(created_at,-1).limit(2000)`) is a collection
scan today ([`08`](08_MongoDB_Data_Architecture.md) §1) with no server-side
bound. A pathological corpus or a locked collection blocks the node
indefinitely, and `retriever` has no timeout of its own.

**X-15 — nothing caps total job duration.** Every individual limit holds while
their composition does not, which §5.3 quantifies.

### 5.3 Worst-case composition (current)

One LLM call, fully exhausted: `4 attempts × 120 s` + backoff `(2+4+6)` =
**492 s ≈ 8.2 min**.

| Stage | Calls | Composition | Worst case |
|---|---|---|---|
| `retriever` | 0 | unbounded (X-14) + up to 40 s cold model load | **unbounded** |
| `extractor` ‖ `tone` | 2 | parallel → `max`, not sum | 492 s |
| `synthesizer` | ×3 (X-6) | sequential | 1,476 s |
| `fact_checker` | ×3 | sequential | 1,476 s |
| **Total** | **6** | | **≈ 3,444 s ≈ 57 min** |

**A single research job can occupy a concurrency slot for ~57 minutes** while
the SSE connection keepalives through it and the user sees "AI Thinking". With
`MAX_ACTIVE_JOBS=8`, eight such jobs deadlock intake for an hour.

> **Inter-document inconsistency this surfaced (resolved in v1.0-rc1).**
> [`09`](09_Redis_Architecture.md) §6.2 originally set `MAX_JOB_LIFETIME =
> 900 s (15 min)` for the self-healing active-set ZSET. Against a 57-minute
> worst case that would reclaim the slot of a **still-running** job, allowing
> over-admission beyond `MAX_ACTIVE_JOBS`. §5.4 reconciles the two by bounding
> the job rather than raising the reaper's window; [`09`](09_Redis_Architecture.md)
> §6.2 now reads **600 s**, and the invariant is asserted at startup (LR-9).

### 5.4 Deadline policy (the missing control)

**A single wall-clock budget per job, set at admission, carried in state,
checked at every node boundary.**

```
POST /reports/generate
   └─ deadline_at = monotonic() + JOB_DEADLINE[kind]
        │
        ▼
   asyncio.wait_for(graph.astream(state), timeout=JOB_DEADLINE[kind] + GRACE)
        │                                    └─ hard outer bound (backstop only)
        ▼
   each node (N-6):  if monotonic() > state["deadline_at"]:
                         return {"trace": [event(node, "warn", "deadline exceeded")]}
                     # degrade, don't crash — partial results still persist
        │
        ▼
   each LLM call:    per-attempt timeout = min(X-5, remaining_budget)
                     retries stop when remaining_budget < one attempt
```

| Budget | Value | Rationale |
|---|---|---|
| `JOB_DEADLINE.research` | **300 s** (5 min) | ~7× the ~42 s typical run; absorbs one cold model load + one full retry cycle |
| `JOB_DEADLINE.learning` | **120 s** (2 min) | ~15× the ~8 s typical run; single LLM call |
| `GRACE` (outer `wait_for`) | +30 s | lets a node finish its current await and emit its warn event before the hard cut |
| `MAX_JOB_LIFETIME` ([`09`](09_Redis_Architecture.md) §6.2) | **600 s** (10 min) | now strictly greater than `research deadline + grace` (330 s), resolving §5.3's inconsistency |

**Node-boundary checks (N-6), not hard cancellation.** A node that finds the
budget spent returns its degraded value and a `warn` event, so the graph
completes normally and whatever was produced still persists. The outer
`wait_for` exists only as a backstop against a node that blocks without an await
point.

### 5.5 Revised retry budget

| Control | Current | **Proposed** | Why |
|---|---|---|---|
| X-2 `chat_text` attempts | 4 | **3** | Attempt 4 costs 120 s + 6 s backoff for a call that has already failed three times. Empirically, a transient provider fault clears by attempt 2–3 or is not transient. |
| X-3 backoff | 2/4/6 s | **2/4 s** + jitter | Jitter prevents the two parallel light-model calls from synchronizing their retries into the same provider rate-limit window. |
| Per-attempt timeout | fixed 120 s | **`min(120, remaining_budget)`** | A call cannot outlive the job that owns it. |
| **Per-job LLM-call ceiling** | ∅ | **12 attempts total** | Hard backstop across all nodes and retries (6 calls × 2 typical attempts); a runaway loop stops burning quota even if a deadline check is somehow bypassed. |
| X-6 re-synthesis | ≤2 (G-3) | **≤2 — unchanged** | Frozen contract; `retry_count` is user-visible. |
| X-14 Mongo | none | **`maxTimeMS = 10_000`** on retrieval; 5 s elsewhere | Bounds the one currently-unbounded node. |

**Worst case after these changes:** `3 × 120 s + 6 s` = 366 s per call site,
but the 300 s job deadline binds first. **Research ≤ 330 s, Learning ≤ 150 s**,
guaranteed by two independent mechanisms (node checks + outer `wait_for`).

### 5.6 Timeout policy summary

| Layer | Bound | Enforced by | On expiry |
|---|---|---|---|
| Whole job | 300 s / 120 s | deadline in state + outer `wait_for` | `pipeline/warn` → UI `cancelled` stage → retry offered |
| Single node | remaining budget | N-6 check at entry | degraded return + `warn` event; graph continues |
| Single LLM attempt | `min(120 s, remaining)` | `asyncio.wait_for` in the adapter | counts as one attempt, retried if budget allows |
| Retry sequence | 3 attempts / 12 per job | `chat_text` + job counter | raise → node's N-2 handler |
| Mongo op | 10 s / 5 s | `maxTimeMS` | node's N-2 handler |
| External HTTP | 10–30 s (X-13) | `httpx` | `None` return, best-effort fallback (`06` C-8) |
| SSE connection | unbounded, 15 s keepalive | client + `XREAD block` | client reconnects, replays |
| Job slot reclamation | 600 s | Redis ZSET score ([`09`](09_Redis_Architecture.md) §6.2) | slot freed; job already terminal by then |

### 5.7 ⚠️ Behavior change — requires sign-off

Deadlines mean **a job that would previously have run for up to 57 minutes now
terminates at ~5 minutes** with `pipeline/warn`.

- **Not an API contract change** (`06` C-1): paths, request/response shapes, and
  status codes are untouched.
- **Not a frontend redesign** (`06` C-2): `warn` already maps to the
  `cancelled` stage, which the UI renders with a retry affordance.
- **It is a user-visible behavior change** on a live endpoint, so it is listed
  in §13 for explicit ratification rather than treated as a bug fix.

No production run has ever been observed near this bound — the harness in
`eval_scorecard.py` reports typical runs in the tens of seconds — so the
practical effect is bounding a pathological tail, not truncating normal work.

---

## 6. Cancellation

### 6.1 Mechanism

`asyncio.Task.cancel()` on the task running `_run()`. `CancelledError`
propagates out of `astream`; the use case sets status `cancelled`, emits
`{node:"pipeline", status:"warn"}`, and closes the stream. This is the existing,
working mechanism (`server.py:768-778`) and it does not change.

### 6.2 What cancellation actually interrupts

| In flight | Interrupted? | Note |
|---|---|---|
| Between nodes | ✅ immediately | `astream` yields are cancellation points |
| Inside `chat_text` backoff `asyncio.sleep` | ✅ immediately | |
| Inside a provider HTTP call | ⚠️ **only when it returns** | Provider calls run in `asyncio.to_thread`; a thread cannot be cancelled. Worst case ≈ one attempt timeout (X-5). |
| Inside a Mongo query | ✅ | motor is natively async |

The `to_thread` limitation is inherent to the current LLM adapter, not
introduced here: a cancelled job may burn one more provider call, bounded by
X-5. An async-native provider client is the upgrade path; it is larger than this
milestone.

### 6.3 Multi-instance cancellation (Phase 7)

Once Redis is the `EventBus`, the SSE connection and the owning task may live on
different instances:

```
POST /learning/{id}/cancel  (instance B)
   ├─ HSET  as:v1:job:{id} status=cancelled      # authoritative regardless of delivery
   └─ PUBLISH as:v1:cancel {"job_id": id}
          └─ every instance subscribes; the owner matches its local task
             registry and calls .cancel(); non-owners ignore it.
```

Detail in [`09`](09_Redis_Architecture.md) §5. The graph layer is unaffected —
it still only sees `CancelledError`.

### 6.4 Contract note

The Learning UI fires cancel **fire-and-forget and never reads the response**
(`useExplanationJob.ts:107-112`). The endpoint must be idempotent, tolerate
unknown/finished ids, and never be the only mechanism that stops server work —
which §5.4's deadline now guarantees.

---

## 7. Instrumentation (OpenTelemetry + Prometheus)

Per `06 AD-13`, instrumentation lives in a decorator and the composition root —
never in node bodies, which stay import-clean for the `06 AD-5` dependency rule.

### 7.1 Trace hierarchy

```
span  http.server  POST /api/reports/generate           (auto — FastAPI instrumentation)
 └─ span  pipeline.research      job_id, ticker, user_id, cached, deadline_s
     ├─ span  node.retriever     chunks_scanned, chunks_returned, stages, degraded
     │   └─ span  db.find        (auto — pymongo instrumentation)
     ├─ span  node.extractor
     │   └─ span  llm.call       provider, model, tier, attempt, tokens_in/out, budget_left_s
     ├─ span  node.tone
     ├─ span  node.synthesizer   retry=0
     ├─ span  node.fact_checker  claims, flagged
     └─ span  persist.report
```

`job_id` is set as a span attribute **and** injected into every log record
([`04`](04_Observability_Audit.md) O-1), so a trace and its logs join. Node spans
come from a `@traced_node` decorator applied at graph-build time (§2.2); the
node function is untouched.

### 7.2 Metrics

| Metric | Type | Labels | Answers |
|---|---|---|---|
| `alphascribe_pipeline_runs_total` | Counter | `graph`, `status` | success / failure / cancel / **deadline** rate |
| `alphascribe_pipeline_duration_seconds` | Histogram | `graph` | median report time — the release gate that is currently uncomputable ([`04`](04_Observability_Audit.md) §3.2) |
| `alphascribe_node_duration_seconds` | Histogram | `graph`, `node` | which node is slow (fixes O-8) |
| `alphascribe_node_failures_total` | Counter | `graph`, `node` | which node fails most (fixes O-9) |
| `alphascribe_deadline_exceeded_total` | Counter | `graph`, `node` | ✅ is the §5.4 budget correctly sized? |
| `alphascribe_llm_calls_total` | Counter | `provider`, `model`, `tier`, `outcome` | provider health, retry rate (fixes O-11) |
| `alphascribe_llm_duration_seconds` | Histogram | `provider`, `tier` | provider latency |
| `alphascribe_llm_attempts` | Histogram | `provider` | ✅ validates the X-2 4→3 reduction |
| `alphascribe_llm_tokens_total` | Counter | `provider`, `model`, `direction` | per-report cost, currently discarded |
| `alphascribe_retrieval_chunks` | Histogram | `stages` | retrieval scale, degraded-mode detection |
| `alphascribe_retrieval_degraded` | Gauge | — | ✅ BM25-only mode (fixes O-7) |
| `alphascribe_fact_check_flagged_total` | Counter | — | grounding-quality trend |
| `alphascribe_synthesis_retries_total` | Counter | — | G-3 retry pressure |

`retrieval_ms` is additionally written into the existing `meta` dict, so it flows
into the `retriever` trace event and becomes visible in the UI trace *and*
queryable in Mongo at no cost.

### 7.3 Degraded-mode visibility

Embedder/reranker load failures are currently swallowed with **no log line at
all** (`retrieval.py:32-38, 49-55` — [`04`](04_Observability_Audit.md) O-7),
leaving an instance permanently in BM25-only mode with no signal. Phase 3 adds a
WARN log, the `alphascribe_retrieval_degraded` gauge, and surfaces
`retrieval_status()` on the readiness probe.

---

## 8. Testing Strategy

Enabled by `06 AD-7` — none of this is possible today.

| Layer | What | Hermetic |
|---|---|---|
| Node unit | Each node vs. fake ports: happy path, empty upstream state (N-5), port raising (N-2), correct `node` name (N-3), deadline-exceeded path (N-6) | ✅ |
| State merge | Parallel `extractor`/`tone` merge without clobbering; `trace` accumulates via `add`; §2.3 disjoint-key rule | ✅ |
| Graph topology | Compiled node set and edges match; `fact_check_router` returns `accept`/`retry`/`give_up` per state | ✅ |
| **Event envelope** | A full fake run emits exactly the §4.2 sequence; every `node` value ∈ the G-1 allowed set for that graph | ✅ |
| Retry budget | Call count ≤ 3/attempt-site and ≤ 12/job; backoff sequence; budget-aware early stop (§5.5) | ✅ |
| **Deadline** | Expired budget → `warn` event, graph completes, partial results persist; outer `wait_for` backstop fires | ✅ |
| Retry loop | `fact_check_status=False` re-enters `synthesizer` ≤2× then `give_up` (G-3) | ✅ |
| Cancellation | `CancelledError` mid-`astream` → `warn` + `cancelled` status, no partial persistence | ✅ |
| E2E | Existing `backend_test*.py` unchanged (`06` C-6) | ❌ live |

The **event-envelope test is the highest-value one**: it is the automated guard
on G-1, the constraint most likely to be broken by a future topology change and
least likely to be caught by review.

---

## 9. Design Decisions

| ID | Decision | Rationale | Rejected |
|---|---|---|---|
| **LG-1** | Two graphs, shared node library | Learning is 1 LLM call; research up to 6. A parameterized graph with skip-flags would put fact-check/retry vocabulary into a state the Learning UI has no stage for (G-1). | One graph with `mode` conditionals — reintroduces `01 V-1` coupling elsewhere |
| **LG-2** | `retriever` shared verbatim; Learning adapts the *input*, not the node | Zero new retrieval code, zero divergence risk between the features' retrieval quality | A `learning_retriever_node` fork |
| **LG-3** | Separate state TypedDicts per graph | Prevents a Learning node reading research-only keys and typechecking | Shared `total=False` state |
| **LG-4** | `pipeline` wrapper events emitted by the use case, not a node | Decouples the UI state machine from graph topology | `pipeline_start`/`pipeline_end` nodes |
| **LG-5** | **No checkpointer in v1** (restates `06 AD-12`) | Retry issues a **new job id** per the frozen contract, so resume has no UI surface. A checkpointer costs a dependency + a write per node for a capability nothing can invoke. | `langgraph-checkpoint-mongodb` now |
| **LG-6** | **No fact-checker in the Learning graph** | The contract has no `fact_check_status`/`scorecard` field and SCR-08's loading behavior is exactly two stages. The existing checker verifies **numeric** claims only (`nodes.py:200-205`, `ponytail:`) — precisely the class a learner explanation mostly is not. Grounding via prompt + deterministic citation validation. | Reuse `fact_checker` — doubles latency, adds a stage with no vocabulary, catches little |
| **LG-7** | `stream_mode` = updates (default) | `values` re-emits the whole state (incl. all `source_documents`) per step | `values` / `messages` |
| **LG-8** | `recursion_limit=25` retained | Worst case is 8 supersteps (retriever 1 + parallel pair 1 + 3×(synth+check) 6); 25 is margin, not a tuning knob | Tightening it — buys nothing, risks a spurious abort |
| **LG-9** | Instrumentation via decorator at graph-build time | Nodes stay import-clean; spans added in one place | `with tracer.start_as_current_span(...)` in each node |
| **LG-10** | Graphs compiled once in the composition root | Removes the last import-time side effect (`server.py:77`, `01 B-6`) | Module-level `graph = build_graph(db)` |
| **LG-11** | ✅ **One wall-clock deadline per job, checked at node boundaries** (§5.4) — not per-node timeouts | A single budget composes correctly; N per-node timeouts multiply into the same unbounded product they were meant to prevent (§5.3). Node-boundary checks degrade gracefully where a hard cancel would lose partial work. | Per-node `asyncio.wait_for`; no bound (status quo) |
| **LG-12** | ✅ **Retry attempts reduced 4 → 3, plus a 12-attempt per-job ceiling** (§5.5) | Attempt 4 costs 126 s to re-confirm a fault that three attempts already established. The per-job ceiling is the backstop that does not depend on any deadline check being reached. | Keep 4; add nothing |

---

## 10. Risks

| ID | Risk | Sev | Likelihood | Mitigation |
|---|---|---|---|---|
| **LR-1** | **A node rename or new node breaks the UI silently** — an unrecognized `node` leaves it in "AI Thinking" forever, with no error (G-1) | **High** | Medium | §8 event-envelope test asserts every emitted `node` ∈ the allowed set; the set is a constant mirroring `streamStages.ts` and cited in both files |
| **LR-2** | **New parallel branch clobbers state** — two nodes writing one key without a reducer, silently losing one (§2.3) | **High** | High without the test | State-merge test; rule restated as a `state.py` docstring |
| **LR-3** | **Cancellation does not stop an in-flight provider call** (§6.2) | Medium | Medium | Bounded by X-5; documented ceiling; async-native client is the upgrade path |
| **LR-4** | **Deadline set too tight** — legitimate slow runs (cold model load + a genuine retry) fail at 300 s | Medium | Low | `alphascribe_deadline_exceeded_total` is the tuning signal; the budget is env-configurable, not a literal; 300 s is ~7× the observed typical run |
| **LR-5** | **`to_thread` executor saturation** — PDF extraction, audio transcription, and every LLM call share the default executor. Under load the pipeline starves behind a 50 MB PDF parse | Medium | Medium | Bounded by X-10; Phase 7 sizes an explicit executor and adds a saturation metric; PDF extraction gains its own timeout ([`10`](10_Backend_Security_Architecture.md) §6.2) |
| **LR-6** | **Retrieval degradation is silent** (O-7) — BM25-only produces measurably worse briefs with no signal | Medium | Medium | §7.3 gauge + WARN log + readiness probe |
| **LR-7** | **Fan-in nondeterminism** makes event-order assertions flaky | Low | Medium | §8 asserts *set* membership and the position of the `pipeline`/`final` bookends, never the relative order of the parallel pair |
| **LR-8** | **Graph and UI stage machine drift** as features are added by different people | Medium | Medium | G-1 recorded here and in `streamStages.ts`; any node-name change requires frontend sign-off |
| **LR-9** | ✅ **Deadline and job-reaper windows drift apart again** — the §5.3 inconsistency recurs after a future tuning change | Medium | Medium | The invariant `MAX_JOB_LIFETIME > max(JOB_DEADLINE) + GRACE` is asserted at startup, not just documented |

---

## 11. Implementation Order

| Step | Work | Migration phase | Gate |
|---|---|---|---|
| 1 | Extract pure logic → `domain/` (`claims.py`, `chunking.py`, `citations.py`) | Ph 2 | Unit tests green |
| 2 | Port injection (`06 AD-7`); `build_research_graph(container)` | Ph 3 | Node unit tests pass against fakes |
| 3 | `maxTimeMS` on Mongo ops (X-14) | Ph 3 | Retrieval bounded |
| 4 | Move `pipeline` wrapper events into the use case (LG-4); event-envelope test | Ph 4 | Envelope test green; E2E `test_sse_stream` unchanged |
| 5 | **Deadline policy (§5.4) + retry budget (§5.5) + LR-9 startup assertion** | Ph 4 | Deadline and retry-budget tests green |
| 6 | `@traced_node` + node/LLM metrics (§7) | Ph 7 | Spans visible; `/metrics` exposes node + deadline series |
| 7 | `LearningState`, `explainer`, `build_learning_graph` | Ph L | 4 contract tests vs. the frozen Zod shapes |
| 8 | Redis cancellation propagation (§6.3) | Ph 7 | Two-instance cancel drill |

**Ordering constraint:** step 7 requires steps 2 and 4. Building the Learning
graph before the port conversion means writing a second node that takes a `db`
handle, doubling the `01 B-2` violation.

---

## 12. Cross-Reference Index

| Referenced here | Target |
|---|---|
| `01 B-2`, `01 B-6`, `01 D-1`, `01 V-1` | [`01_Backend_Architecture_Review.md`](01_Backend_Architecture_Review.md) §2.1, §4, §6 |
| `02 F-1` | [`02_API_Coverage_Audit.md`](02_API_Coverage_Audit.md) §5 |
| `03` §2 R-1, §4, §6.2 | [`03_Learning_Backend_Design.md`](03_Learning_Backend_Design.md) |
| `04` O-1, O-7, O-8, O-9, O-11, §3.2 | [`04_Observability_Audit.md`](04_Observability_Audit.md) |
| `06` C-1, C-2, C-6, C-8, AD-3, AD-5, AD-7, AD-12, AD-13; Ph 2/3/4/7/L | [`06_Clean_Architecture_Migration_Plan.md`](06_Clean_Architecture_Migration_Plan.md) §0, §3, §5.1 |
| `08` §1 | [`08_MongoDB_Data_Architecture.md`](08_MongoDB_Data_Architecture.md) |
| `09` §4.3, §5, §6.2 | [`09_Redis_Architecture.md`](09_Redis_Architecture.md) |
| `10` §6.2 | [`10_Backend_Security_Architecture.md`](10_Backend_Security_Architecture.md) |

---

## 13. Ratification

Sign-off required on the following; everything else in this document is
descriptive of already-approved constraints or is an internal implementation
choice.

| # | Item | Position | Impact if approved |
|---|---|---|---|
| 1 | **G-1 node vocabulary is a cross-team contract** — changing a node name requires frontend sign-off, like an API shape change | Binding | Process |
| 2 | **§2.3 reducer rule** — disjoint keys or an explicit reducer — as a review gate | Binding | Process |
| 3 | **LG-6** — no fact-checker in Learning; grounding via prompt + deterministic citation validation | Proposed | Reversing it adds a UI stage with no frozen vocabulary |
| 4 | **LG-5 / `06 AD-12`** — no checkpointer | Proposed | Revisit only if a resume affordance is specified |
| 5 | **LG-11 — job deadlines (300 s research / 120 s learning).** ⚠️ **User-visible behavior change** (§5.7): a pathological job now fails at ~5 min instead of running ~57 min. No contract or frontend change. | **Recommended** | Bounds the tail; `deadline_exceeded` metric is the tuning signal |
| 6 | **LG-12 — retry attempts 4 → 3, plus a 12-attempt per-job ceiling** | Recommended | Cuts worst-case latency and quota burn |
| 7 | **`MAX_JOB_LIFETIME` raised to 600 s** to satisfy `MAX_JOB_LIFETIME > max(JOB_DEADLINE) + GRACE` (§5.3, LR-9) — amends [`09`](09_Redis_Architecture.md) §6.2 | Required for consistency | Resolves an inter-document conflict |

**On ratification:** change the status header to 🔒 **FROZEN**, record the date
and approver, and treat all subsequent changes as numbered amendments appended
below rather than edits in place.

---

*Companion documents:* [`06`](06_Clean_Architecture_Migration_Plan.md) ·
[`08`](08_MongoDB_Data_Architecture.md) · [`09`](09_Redis_Architecture.md) ·
[`10`](10_Backend_Security_Architecture.md) · index:
[`00_README.md`](00_README.md)
