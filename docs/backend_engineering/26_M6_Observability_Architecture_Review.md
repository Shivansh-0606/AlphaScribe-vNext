# M6 — Observability Architecture Review

**Milestone:** Backend Engineering M6 (Observability Hardening) · **Date:** 2026-08-05
**Reviews:** [`19`](19_M6_Observability_Implementation_Report.md)–[`25`](25_M6_Production_Readiness_Assessment.md)
**Verdict:** 🟡 **Approved with Changes**

> This document is the architecture review of the M6 Observability
> Hardening implementation as delivered (`19`–`25`) — it evaluates that
> implementation directly, not a separate prior review artifact. Findings,
> priorities, and the verdict below apply to the implementation itself.

---

## Verdict rationale

The implementation is evidence-based and sound: 167/167 hermetic tests,
8/8 contract tests (zero API-contract change, verified by the route-inventory
exact-set guard), a live-suite regression check run against a parallel
instance proving the same pre-existing failures reproduce identically on
old and new code, and real load/stress runs (0 errors, 5,230 requests) — see
`25` for the full evidence trail. Implementation discipline is strong: every
new metric/span sits at a genuine single choke point (`instrument_node()`,
`track_redis_errors()`, `_deny_cross_tenant()`) rather than scattered
call-site edits.

Set against that: this review's own verification pass (below) found one
functional defect the original M6 work shipped without catching, plus two
documentation defects and one readiness-semantics gap. None of these
invalidate the milestone's substance — all are fixable in isolation, none
touch the API contract or the frozen architecture — which is what
"Approved with Changes" means here: ship the milestone, land the fixes as
a fast-follow, don't re-scope M6 to absorb them.

---

## 1. Architecture

Findings that affect correctness or mislead a future engineer's
understanding of what's actually live — not deployment state, not cosmetic
docs.

### A1 — Correlation IDs do not reach emitted application logs (High)

`install_correlation_filter()` (`infrastructure/observability/logging.py`)
attaches `CorrelationIdFilter` to the **root `Logger`'s** filter list via
`target.addFilter(f)`. Python's logging propagation walks up the logger
hierarchy invoking each **handler's** filters, not each ancestor **logger's**
filters — a `Logger.filters` list is only consulted by that logger's own
`.handle()`, i.e. only for records logged directly through that logger
object. Every real log call in this app goes through
`logging.getLogger("alphascribe")` or `.getLogger("alphascribe.notify")` —
child loggers, never the root logger directly. Reproduced:

```
logging.getLogger("alphascribe").info("...")   # with a format string
# referencing %(correlation_id)s → ValueError: Formatting field not found
# in record: 'correlation_id'
```

The feature is built and the id is computed correctly
(`set_correlation_id()`/`get_correlation_id()` work, proven by
`test_correlation_id_round_trips`), but it never lands in an emitted log
line for the application's actual loggers. Today's format string
(`"%(asctime)s %(levelname)s %(name)s: %(message)s"`) doesn't reference the
field, so there's no visible crash — but the correlation-id feature this
milestone's report (`19`) listed as "✅ Live" is, for the app's real
loggers, silently inert.

**Why the existing test didn't catch it:** `test_correlation_filter_injects_the_active_id`
constructs a bare `CorrelationIdFilter()` and calls `.filter(record)`
directly — correct in isolation, but it bypasses the logger-hierarchy
wiring entirely, so it cannot detect that the filter is attached to the
wrong object.

**Fix:** attach the filter to the handler(s), not the logger:
```python
target = logger or logging.getLogger()
for h in target.handlers:
    h.addFilter(f)
```
(Handlers are configured by `logging.basicConfig()` before this runs, so
they exist by the time `install_correlation_filter()` is called at
startup.)

### A2 — Readiness does not verify the configured execution backend (Medium)

`GET /health/ready` (`server.py`) computes `ready = mongo_ok` only — it
never checks Redis, **regardless of `JOB_BACKEND`**. Under
`JOB_BACKEND=redis` (`app/container.py`'s adapter switch), the actual job
lifecycle depends on Redis being reachable, but readiness has no way to
reflect that: an instance can report `ready: true` while its real
execution backend is down.

This is **not** a recommendation to make Redis a mandatory readiness
dependency — `JOB_BACKEND=memory` is the documented default
(`09` RR-10) for the no-Docker developer path, and readiness must not
regress to requiring infrastructure that mode deliberately doesn't need.
The fix is conditional, matching the existing pluggable-backend design:

> If `JOB_BACKEND=redis`, readiness should also verify Redis availability,
> so readiness semantics stay consistent with whichever execution backend
> is actually configured. Under `JOB_BACKEND=memory`, readiness is
> unaffected — there is no external dependency to check.

### A3 — Two docstrings assert states that are no longer true (High)

Both are safety-relevant (they'd cause a reviewer to misjudge blast radius
or live-wiring), not cosmetic:

- `app/container.py`'s module docstring: *"Nothing in server.py constructs
  this yet."* False — `server.py:90` does `container = build_container(settings)`
  at import time, and `container.job_lifecycle.*` is called on every job
  admission, publish, and terminal transition in both pipelines.
- `infrastructure/streaming/sse.py`'s pre-existing module docstring (before
  this milestone's edit): *"NOT wired into server.py's live `GET
  /reports/{job_id}/stream` this phase... that handler still uses its own
  single-`asyncio.Queue` generator."* False — `stream_report` already calls
  `sse_response()` (confirmed at `server.py`'s route handler); this module
  has been the live SSE path since a prior phase's cutover, not this one's.

Both read as historically-accurate-when-written and simply never got a
follow-up edit once the described future state became the present — the
exact drift class that makes a docstring actively misleading rather than
merely stale.

---

## 2. Operations

Operational-maturity items, not architectural deficiencies — the
architecture delivers the specifications, metrics, and instrumentation;
deploying them is separate, later work.

- **O1 — Dashboards and alert rules are specifications, not a deployed
  stack.** `20`–`23` are ready-to-import PromQL panels and Prometheus
  alerting YAML. No Grafana or Alertmanager instance exists in this repo's
  deployment target (`scripts/run.py`'s local stack is backend + frontend +
  a portable Mongo — no monitoring stack). This is a deployment/operations
  milestone's job, not an architectural gap in what M6 built.
- **O2 — Load testing covered public, no-auth endpoints only, not the AI
  pipeline under load.** `24`'s runs (concurrency 20/75, 12–15s, 0 errors)
  validate the request-timing middleware and the now-cheap `/health` under
  concurrency. `/reports/generate` was deliberately excluded — a load
  generator hitting it would burn real LLM provider quota/cost per request
  without an operator's explicit opt-in. Full pipeline-under-load
  validation, and any multi-instance/Redis-backend scaling test, is future
  scope, not a defect in this milestone.
- **O3 — `ratelimit_degraded` has no call site.** Its natural home is the
  `RedisRateLimiter` port, which is built and tested standalone but not yet
  cut into the live `/auth/login` path (that cutover is a separate
  milestone). Wiring a gauge for a code path that isn't live yet would be a
  fabricated signal, not an early one.

---

## 3. Implementation Hygiene

Minor, non-misleading documentation drift — moved out of the architectural
risk section on purpose; these don't affect anyone's understanding of what's
live or safe to touch.

- `infrastructure/observability/metrics.py`'s module docstring undercounts
  actual coverage: it still describes `pipeline_runs_total`/`llm_calls_total`
  as belonging to "Phases 3/4+", when Phase L already wired both. Understates
  rather than overstates — doesn't create the "I can safely ignore this" risk
  A3's cases do, just needs a cleanup pass.

---

## 4. Prioritized Recommendations

**High Priority**
1. Fix `install_correlation_filter()` to attach to handlers, not the
   logger's own filter list, so correlation IDs actually appear in emitted
   application log lines (A1). Add a regression test that exercises a real
   application child logger (e.g. `logging.getLogger("alphascribe")`) and
   verifies the correlation id reaches the emitted `LogRecord` through the
   normal handler-propagation path, not by constructing a bare `Filter` and
   calling it directly — the existing test's isolation is exactly what let
   A1 ship uncaught, so the regression test's job is to exercise the real
   logger hierarchy, ensuring it stays correctly instrumented going forward.
2. Correct the two stale docstrings in `app/container.py` and
   `infrastructure/streaming/sse.py` so they describe what's actually live
   (A3).

**Medium Priority**
3. Make `/health/ready` conditionally verify Redis only when
   `JOB_BACKEND=redis` — readiness semantics tracking the configured
   backend, not a new mandatory dependency (A2).

**Low Priority**
4. Deploy Grafana/Alertmanager and import `20`–`23`'s specifications —
   belongs to a future operations/deployment milestone (O1).
5. Expand load testing to cover the AI pipeline under an explicit,
   operator-approved LLM-cost budget, and multi-instance/Redis-backend
   scaling (O2).
6. Refresh `metrics.py`'s module docstring to reflect Phase L's actual
   coverage (Implementation Hygiene item).

No additional architectural changes are recommended beyond the prioritized
actions above. The six items reflect the full set of findings this review's
verification pass surfaced against the implementation evidence in `19`–`25`
and should remain unchanged absent new evidence.

---

## 5. Scope note

This review is retrospective verification of the M6 deliverables
(`19`–`25`), not a re-implementation. A1–A3 were not caught during the
original M6 implementation pass — A1 in particular is a pre-existing defect
from M2 Phase 1's original `logging.py`, exposed here rather than
introduced by M6. None of the four fixes above require touching the API
contract, the frozen architecture (`06`–`10`), or reopening any ratified
decision — each is a self-contained, low-blast-radius change ready to pick
up as its own focused PR, matching the precedent EQ-2/EQ-3/M5 already set
for this kind of narrow, reviewable follow-up.

Upon CTO approval, this document becomes the canonical architecture-review
record for M6 Observability Hardening. Future implementation changes that
materially affect the underlying architecture should trigger a new review
rather than modifying this approved assessment.
