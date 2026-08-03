# Observability Audit

**Status:** Audit · **Milestone:** Backend Engineering M1 · **Date:** 2026-08-03
**Scope:** `backend/` @ `7404b67`. No code was modified.

---

## 1. Summary

| Pillar | State | Verdict |
|---|---|---|
| Logging | One `basicConfig`, two named loggers, ~10 call sites | ⚠️ **Minimal but disciplined** — the redaction hygiene is genuinely good; the correlation story is absent |
| Metrics | None | ❌ **Absent** — no counters, no timers, no `/metrics`, and the data needed for the release gates in `docs/planning/06-Testing-QA-Plan.md` §4 is not persisted |
| Tracing | None (distributed); node-level pipeline events persisted per job | ⚠️ **Domain trace only** — rich per-job, unqueryable across jobs |
| Health | One endpoint, unconsumed | ⚠️ **Present with three defects** |

The system is **debuggable after the fact for a single known job** (the event
trail is excellent) and **blind in aggregate** (no way to answer "how many
report generations failed today", "what is p95 latency", "which provider is
erroring").

---

## 2. Logging

### 2.1 Configuration

```python
# server.py:79-80
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("alphascribe")
```

Plus `logging.getLogger("alphascribe.notify")` (`notify.py:14`). That is the
entire logging configuration.

### 2.2 Call-site inventory

| Level | Site | Content |
|---|---|---|
| INFO | `server.py:85` | startup: active LLM provider, light/heavy models, key present/missing |
| INFO | `server.py:1194` | "retrieval warmup complete" |
| INFO | `server.py:1199` | "company index loaded (N rows)" |
| WARNING | `server.py:600, 621, 638` | EDGAR / BSE / yfinance fetch failure per ticker (best-effort sources) |
| WARNING | `server.py:836` | LLM key validation failure, provider + error |
| WARNING | `server.py:1196, 1201` | warmup / index load failure |
| WARNING | `notify.py:29` | **`INSECURE:` — OTP written to the log** when `RESEND_API_KEY` is unset |
| ERROR | `server.py:450` | `logger.exception("gemini transcription failed")` |
| ERROR | `server.py:494` | `logger.exception("pdf extraction failed")` |
| ERROR | `server.py:783` | `logger.exception("pipeline failed")` |
| ERROR | `notify.py:45` | `logger.exception("Failed to send password reset email")` |

### 2.3 What is right

- **Secret redaction is consistently correct**, and it is the thing most
  codebases get wrong. Provider exceptions are logged in full but **never
  returned to the client** (`server.py:447-451`, `:779-795`) precisely because
  Gemini embeds the API key as a `?key=…` URL parameter.
  `llm.redact_key_from_error` (`llm.py:288-299`) strips both the literal key
  and any `key=` param before a validation error reaches a response body. The
  422 handler strips pydantic's `input` field app-wide so a rejected password
  never appears in a response (`server.py:1157-1165`).
- **`logger.exception` (not `logger.error`) at all four failure sites** —
  stack traces are preserved.
- **The `INSECURE:` OTP log is WARNING, not INFO, by explicit design**
  (`notify.py:22-29`) so a production deployment missing `RESEND_API_KEY` trips
  log-level alerting rather than silently degrading. Correctly reasoned.

### 2.4 Gaps

| ID | Gap | Impact |
|---|---|---|
| **O-1** | **No correlation identifier.** No request id, no `job_id` in any log line. `logger.exception("pipeline failed")` cannot be tied to the job, ticker, user, or provider that failed. | With concurrent jobs, a stack trace in the log is unattributable. This is the highest-value logging fix and costs one `extra={}` per call site. |
| **O-2** | **The pipeline's own event trail never reaches the logs.** Every node emits a structured `{node, status, message, ts}` event; those go to the SSE queue and Mongo, never to `logger`. The richest signal in the system is invisible to any log-based tool. | One `logger.info` inside `push()` would make every pipeline observable in the log stream at zero design cost. |
| **O-3** | **Unstructured, human-format logs.** `"%(asctime)s %(levelname)s %(name)s: %(message)s"` is not machine-parseable; no JSON formatter. | No log aggregation, no field-based querying. Acceptable for local dev, blocking for any hosted deployment. |
| **O-4** | **Log level is hard-coded to INFO.** No `LOG_LEVEL` env var, despite ~20 other env-configurable settings (`MAX_ACTIVE_JOBS`, `LLM_REQUEST_TIMEOUT`, `LLM_MAX_OUTPUT_TOKENS`, `CORS_ORIGINS`…). | Cannot raise verbosity to debug an incident without a code change. ~2 LOC. |
| **O-5** | **No access log configuration.** uvicorn's default access log is used as-is; it is not correlated with the application logger and is not mentioned in `scripts/run.py`. | Request-level latency/status data exists but is unjoined to anything. |
| **O-6** | **No log rotation or retention.** `scripts/run.py` starts uvicorn directly. | Unbounded growth on a long-running instance. |
| **O-7** | **Silent failure paths.** `agents/retrieval.py:32-38, 49-55` swallow embedder/reranker load exceptions into a `_STATUS` string with **no log line at all**. `_get_embedder` failing is the difference between hybrid and BM25-only retrieval — a silent, permanent quality degradation. `retrieval.py:98-101` (`rerank_pairs`) likewise catches and returns `None` without logging. | A production instance can silently run in degraded retrieval mode indefinitely. `/health` exposes the status string, but nothing alerts and nobody polls it (§4). |

---

## 3. Metrics

**There are none.** No metrics library in `requirements.txt`, no counters, no
histograms, no `/metrics` endpoint, no StatsD/Prometheus/OTel emission.

### 3.1 What is *almost* metrics

`GET /api/health` returns three gauges as a side effect: `filings` count,
`chunks` count, and the retrieval subsystem status. `compute_scorecard`
produces per-report quality numbers (`faithfulness`, `context_precision`,
`answer_relevance`) persisted on every report — genuinely valuable data, but
per-document, never aggregated except by the offline `eval_scorecard.py`
harness.

### 3.2 The data that is not captured

`docs/planning/06-Testing-QA-Plan.md` §4 defines four performance benchmarks as
release gates. **Three of them cannot be computed from what the system
persists:**

| Required benchmark | Computable today? | Blocker |
|---|---|---|
| Median report time | ❌ | Jobs record `created_at` but **no `completed_at` and no duration** (`server.py:751-757`). The only timing signal is the `ts` of the first vs. last event, and events are `$push`ed without a terminal marker guaranteed to exist on failure. → Architecture Review **D-8** |
| Cold model load time | ❌ | `_warmup` logs "retrieval warmup complete" with no elapsed time (`server.py:1194`) |
| Retrieval latency per query | ❌ | `retrieve()` returns a `meta` dict describing *which stages ran*, never how long they took (`retrieval.py:162`) |
| Avg faithfulness / ctx-precision / answer-relevance | ✅ | Persisted per report; aggregated by `eval_scorecard.py` |
| Per-report LLM token cost | ❌ | Provider responses' usage fields are discarded — `_gen_gemini`, `_gen_openai_compatible`, `_gen_anthropic` all return `str` only (`llm.py:163-232`). Token counts are available in every SDK response and thrown away. |

### 3.3 Recommended minimum (not a monitoring stack)

Four fields, no dependency, in the modules already being touched for the
Learning build:

1. `completed_at` + `duration_ms` on job completion → unlocks median report
   time and, with `status`, a success rate.
2. `retrieval_ms` into `retrieve()`'s existing `meta` dict → already flows into
   the trace event (`nodes.py:61-64`), so it becomes visible in the UI trace
   *and* queryable in Mongo for free.
3. `llm_ms` + `provider` + `model` per LLM call, recorded on the job.
4. Token usage from the provider response, if present.

Everything above lands in the existing Mongo documents. A Mongo aggregation
answers every §4 benchmark. **No metrics backend, no Prometheus, no new
dependency** — which is the right call at single-instance scale and consistent
with `CLAUDE.md`'s dependency discipline. Revisit a real metrics pipeline when
a second instance exists (same trigger as EQ-1's Redis question).

---

## 4. Tracing

**No distributed tracing.** No OpenTelemetry, no span propagation, no trace
context on outbound HTTP (EDGAR, BSE, yfinance, Resend, LLM providers), no
`traceparent` header handling on inbound requests.

### 4.1 The domain trace that does exist

Each node emits `_event(node, status, message, ts, **extra)`
(`nodes.py:11-18`), accumulated into `AgentState["trace"]` via
`Annotated[list[dict], add]` (`state.py:58`), fanned out by `push()` to three
sinks, and persisted on both the job and the report document.

This is a **high-quality per-job execution trace**: stage boundaries, retrieval
stage composition (`bm25+dense+cross-encoder`), chunk counts, sentiment
confidence, fact-check flagged/total counts, retry counts. It is what makes the
"AI Thinking → AI Streaming" UX possible and it is genuinely better than what
most systems this size have.

### 4.2 Gaps

| ID | Gap |
|---|---|
| **O-8** | **No timing in the trace.** Events carry a wall-clock `ts` but no duration; per-node latency requires differencing consecutive `ts` values, which breaks for the two parallel nodes (`extractor` ‖ `tone`) whose events interleave nondeterministically. |
| **O-9** | **Trace is per-job, not cross-job queryable.** Events are `$push`ed into an array inside each job document. Answering "which node fails most often" requires `$unwind` over every job; there is no index and no aggregation view. |
| **O-10** | **External calls are untraced.** EDGAR / BSE / yfinance / Resend / provider calls emit no timing, no status code, and (for the best-effort sources) log only a WARNING on failure. `fetch_bse_annual_report` makes three sequential HTTP calls with a 25s timeout each and reports nothing about which one was slow. |
| **O-11** | **The retry loop is invisible.** `chat_text` retries up to 4× with backoff (`llm.py:310-325`) and logs **nothing** — not the attempt number, not the wait, not the error. A request that silently takes 4× longer because of provider throttling is indistinguishable from a slow one. This is the single most valuable place to add a log line in the codebase. |

---

## 5. Health Endpoints

### 5.1 Current implementation

```python
# server.py:187-198
@api.get("/health")
async def health():
    llm_key = bool(os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))
    docs   = await db.filings.count_documents({})
    chunks = await db.filing_chunks.count_documents({})
    return {"ok": True, "llm_key_configured": llm_key,
            "filings": docs, "chunks": chunks, "retrieval": retrieval_status()}
```

Public (no `current_user` dependency) — correct for a probe. Tested by four
tests across `backend_test.py` and `backend_test_iter2.py`.

### 5.2 Defects

| ID | Severity | Defect |
|---|---|---|
| **O-12** | Medium | **Two unindexed full-collection counts per call.** `count_documents({})` on `filings` and `filing_chunks` is O(collection) in MongoDB (unlike `estimated_document_count`). A liveness probe at 10s intervals is a self-inflicted, monotonically growing load — the very thing a health check must not be. → Architecture Review **D-7** |
| **O-13** | Medium | **`llm_key_configured` only checks Gemini.** It reads `GEMINI_API_KEY`/`GOOGLE_API_KEY` and ignores the six other supported providers' env keys (`llm.py:87-92`). An instance correctly configured for Anthropic or Groq reports `llm_key_configured: false`. The endpoint contradicts the startup log line at `server.py:85`, which resolves the *active* provider correctly. |
| **O-14** | Medium | **No liveness/readiness split.** One endpoint conflates "the process is up" with "models are loaded and the corpus is populated". During the 30-40s warmup an orchestrator cannot distinguish "still starting" from "broken", and there is no signal for "ready to serve a pipeline". |
| **O-15** | Low | **`"ok": True` is a literal.** It is not derived from anything and cannot ever be `False`; if Mongo is unreachable the `count_documents` await raises and the endpoint 500s with an unstructured body rather than returning a structured unhealthy response. |
| **O-16** | Low | **Unconsumed.** No `web/` module calls `/health` (API Coverage Audit §3.1), no probe is configured anywhere, and no alerting exists. `retrieval_status()` — the only signal that would reveal the silent degradation of **O-7** — is therefore never read by anything. |

### 5.3 Recommendation

Split, and make the expensive part optional:

- `GET /api/health` → **liveness**: `{"ok": true}`, no I/O. Cheap enough for any
  probe interval.
- `GET /api/health/ready` → **readiness**: Mongo ping (`admin.command("ping")`,
  not a collection count), `retrieval_status()`, and the *resolved active*
  provider's key presence via `llm._active()` — fixing O-13 by reusing the
  function the startup log already uses. Returns 503 when not ready.
- Keep corpus counts, but behind `?stats=1` and using
  `estimated_document_count()` (metadata read, O(1)).

~20 LOC, no new dependency, fixes O-12/O-13/O-14/O-15 together.

---

## 6. Prioritized Recommendations

| # | Action | Fixes | Cost |
|---|---|---|---|
| 1 | Log the retry loop in `chat_text` (attempt, wait, redacted error) | O-11 | 2 LOC |
| 2 | Log embedder/reranker load failure and rerank failure in `retrieval.py` | O-7 | 3 LOC |
| 3 | Add `job_id` (+ ticker, user) to every pipeline log line via `extra=` | O-1 | ~6 LOC |
| 4 | `logger.info` inside `push()` so pipeline events reach the log stream | O-2 | 1 LOC |
| 5 | Persist `completed_at`, `duration_ms`, `retrieval_ms` | §3.3, D-8 | ~6 LOC |
| 6 | Split liveness/readiness; use `estimated_document_count`; resolve the real provider | O-12…O-15 | ~20 LOC |
| 7 | `LOG_LEVEL` env var | O-4 | 2 LOC |
| 8 | JSON log formatter | O-3 | deferred — needed at first hosted deploy, not before |
| 9 | OpenTelemetry / metrics backend | §3, §4 | **deferred** — same trigger as EQ-1 (a second instance). Adding either now would be a dependency ahead of its need. |

Items 1–7 total roughly 40 lines, add no dependencies, and touch modules the
Learning build already opens.

---

*Cross-references: `01_Backend_Architecture_Review.md` (D-7, D-8),
`02_API_Coverage_Audit.md` §3.1, `05_Testing_Audit.md` (coverage measurement).*
