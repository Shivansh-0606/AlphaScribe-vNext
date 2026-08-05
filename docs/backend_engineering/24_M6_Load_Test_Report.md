# M6 — Load Test Report

**Milestone:** Backend Engineering M6 · **Date:** 2026-08-05
**Tool:** `backend/scripts/load_test.py` — stdlib `asyncio` + `httpx`, no new
dependency (`httpx` is already a runtime dependency via provider calls).
**Target:** a live local backend instance (already running against real
Mongo — 37 filings, 2372 chunks), fixed-concurrency GET loop over
`/api/health`, `/api/health/ready`, `/api/metrics`, `/api/` (public,
no-auth, no LLM cost — see the script's own docstring for why
`/reports/generate` is deliberately excluded).

---

## Run 1 — Load (concurrency 20, 15s)

```
requests=2978  rps=198.5  errors=0 (0.00%)
p50=78.0ms  p95=156.0ms  p99=375.0ms  max=453.0ms
```

## Run 2 — Stress (concurrency 75, 12s)

```
requests=2252  rps=187.7  errors=0 (0.00%)
p50=328.0ms  p95=672.0ms  p99=750.0ms  max=860.0ms
```

## Observations

1. **Zero errors at both concurrency levels** — no 5xx, no connection
   failures, across 5,230 total requests. The request-timing middleware and
   the now-cheaper `/health` (O-12 fix — `estimated_document_count` instead
   of `count_documents({})`) held up under sustained concurrent load.
2. **Throughput plateaus (~190-200 rps) while concurrency increases
   3.75×** (20 → 75) — p50 latency roughly **4×'d** (78ms → 328ms) instead
   of staying flat. This is the expected signature of a single-process
   bottleneck: `uvicorn` here runs one worker, and every request in this mix
   still does at least one Mongo round-trip (`/health`'s two
   `estimated_document_count()` calls, `/health/ready`'s ping). The service
   is not failing under this load, but it is not horizontally scaling
   within one process either — expected, not a defect this milestone
   introduced or is scoped to fix.
3. **No metrics-collection overhead spike observed** — `/api/metrics`
   was one of the four endpoints in the rotation at both concurrency
   levels; `render_latest()`'s registry serialization did not visibly
   dominate the tail latencies (max stayed within ~2x of p99 at both runs,
   not an order of magnitude).

## What this run does NOT validate

| Not covered | Why |
|---|---|
| The AI pipeline under load (`/reports/generate`) | Deliberately excluded — real LLM provider calls cost real money/quota per request; a load generator must not spend that without an explicit, separate opt-in the operator controls. `MAX_ACTIVE_JOBS` (default 8, `07` §5) already bounds concurrent pipeline load independently of this test. |
| Multi-process / multi-instance scaling | This environment runs a single `uvicorn` worker (`scripts/run.py`'s default). Horizontal scaling behavior (shared Redis job state, `EQ-1`) is untested here — it is exactly the trigger `09`/`06` already name for revisiting the Redis cutover. |
| Sustained (>15s) load | Both runs are short smoke-level validations, not a soak test. No memory-leak or connection-pool-exhaustion signal was sought. |

## Reproduction

```bash
python backend/scripts/load_test.py --base-url http://localhost:8001 --concurrency 20 --duration 15
python backend/scripts/load_test.py --base-url http://localhost:8001 --concurrency 75 --duration 12
```
