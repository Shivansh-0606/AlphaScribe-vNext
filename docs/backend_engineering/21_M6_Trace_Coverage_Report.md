# M6 — Trace Coverage Report

**Milestone:** Backend Engineering M6 · **Date:** 2026-08-05

---

## 1. Exporter posture

`setup_tracing()` (`infrastructure/observability/tracing.py`) always creates
spans; it only **exports** them when `OTEL_EXPORTER_OTLP_ENDPOINT` is set
(`Settings.otel_exporter_endpoint`). With no collector configured (the
default — no collector exists in `scripts/run.py`'s local stack), spans are
created and immediately discarded — instrumentation stays exercised (and
tested — see `tests/unit/test_tracing_setup.py`) in every environment, at
zero cost, with nothing to fail if a collector is never stood up. Confirmed
empirically (Phase 1 report; unchanged this milestone): an OTLP exporter
with nothing listening on the far end logs a background-thread warning, not
a startup failure or a blocked request.

## 2. Span inventory

| Span source | Instrumentor | Scope | Since |
|---|---|---|---|
| Every inbound HTTP request | `FastAPIInstrumentor` | request → response, auto | M2 Phase 1 |
| Every outbound `httpx` call | `HTTPXClientInstrumentor` | LLM providers, EDGAR/BSE/yfinance (via `httpx`), Resend | M2 Phase 1 |
| Every MongoDB command | `PymongoInstrumentor` | motor's underlying pymongo driver | M2 Phase 1 |
| Every Redis command | `RedisInstrumentor` | `redis-py`; **no-op under `JOB_BACKEND=memory`** (RR-10 default — no client constructed) | **M6** |
| Each LangGraph node | `instrument_node()` — manual span, `{graph}.{node}` | research (5 nodes) + learning (2 nodes) | **M6** |
| Each SSE stream session | manual span, `sse.{stream_name}` | `/reports/{id}/stream`, `/learning/{id}/stream` | **M6** |
| Each `chat_text` retry attempt | manual span, `llm.attempt` (attributes: `attempt`, `provider`, `model`, `tier`) | closes the gap row 3 below used to describe | **M6 (2026-08-08)** |
| Job lifecycle (admission → terminal) | manual span, `pipeline.{graph}` (attributes: `job_id`) | wraps `graph.astream()` in both pipeline task functions — node spans now nest under this instead of each rooting its own trace, since the background task outlives the initiating request's own span | **M6 (2026-08-08)** |

## 3. What is still NOT traced

| Gap | Why it's out of scope |
|---|---|
| Cross-job aggregate queries (`04` O-9) | Out of scope — this is a metrics/dashboard concern (`20`/`22`), not a per-request trace gap. |
| External source fetch breakdown (EDGAR/BSE/yfinance — `04` O-10) | Each already gets an `HTTPXClientInstrumentor` span per call; a parent span grouping the 3 sequential BSE calls (naming which one was slow) does not exist. Small, deferred — no operator complaint yet motivating it. |

## 4. Why spans, not just the existing domain trace

`04` §4.1 already documents a high-quality **domain** trace (`_event()` →
`AgentState["trace"]` → SSE + Mongo) — stage boundaries, retrieval
composition, retry counts. It answers "what happened in job X." OTel spans
answer a different question: "how long did node Y take, correlated with the
Mongo/HTTP/Redis spans it triggered, across every job" — the two are
complementary, not redundant. `04` O-8 ("no timing in the trace... breaks
for the two parallel nodes") is specifically fixed by spans, not by adding
timing to `_event()`, because the domain trace's ordering is inherently
nondeterministic for `extractor`/`tone` (LangGraph fans them out in
parallel) while each span's own start/end is exact regardless.

## 5. Verification

`tests/unit/test_observability.py::test_instrument_node_records_duration_and_returns_value`
and `::test_instrument_node_propagates_exceptions` confirm the wrapper
creates a span, always records `node_duration_seconds` (including on
exception, via the wrapper's `finally`), and never swallows a node's return
value or exception. `test_tracing_creates_real_spans` (pre-existing)
confirms span creation against a real `TracerProvider` independent of
process-global state.
