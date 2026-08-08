# M6 — Fast-Follow Execution Review

**Milestone:** Backend Engineering M6 (Observability Hardening) · **Date:** 2026-08-08
**Status:** Execution review of fixes landed *after* [`26`](26_M6_Observability_Architecture_Review.md)'s
approval. **Document 26 is not modified by this document** — its findings,
verdict, and text stand exactly as approved. This document records what
happened next: closure of 26's three findings, additional scope a later
brief requested, and — separately — a newly discovered defect this review's
own implementation work found and fixed, which 26 never evaluated.

---

## 1. What changed after Document 26's approval

Two separate rounds of work landed after 26 was approved:

- **Round 1** (2026-08-08, earlier): closed 26's A1/A2/A3 findings, plus
  implemented the additional metrics/tracing scope a follow-up brief
  requested beyond 26's own findings (token usage, retrieval duration,
  cache hit/miss, SSE session metrics, LLM retry-attempt spans, a
  job-level parent span). Recorded in [`19` §5a](19_M6_Observability_Implementation_Report.md#5a-addendum-2026-08-08--doc-26-fixes--briefs-expanded-metricstracing-list).
- **Round 2** (this document): a fifth, independent review of Round 1's own
  output found a real defect in the job-level parent span Round 1 had just
  added (§4 below), plus two narrower correctness gaps. Fixed here.

## 2. A1 / A2 / A3 closure verification (Document 26's historical findings)

| Finding | 26's description | Verified fixed |
|---|---|---|
| A1 | Correlation IDs never reach emitted application logs — filter attached to the wrong object | ✅ `install_correlation_filter()` now attaches to handlers; regression test exercises a real child logger through real propagation (`tests/unit/test_observability.py::test_correlation_id_reaches_a_real_child_logger_via_propagation`) |
| A2 | `/health/ready` doesn't verify Redis under `JOB_BACKEND=redis` | ✅ Conditional check added (`Container.job_backend`/`redis_client`); confirmed live: `{"ready":true,"mongo":true,"redis":null,"job_backend":"memory"}` under the default backend |
| A3 | Two docstrings assert false live-wiring states | ✅ `app/container.py`, `infrastructure/streaming/sse.py` corrected |

These were re-verified in the *current* code state for this document, not
carried forward from Round 1's own claims.

## 3. Additional observability scope implemented (beyond Document 26)

`retrieval_duration_seconds`, `llm_tokens_total`, `report_cache_lookups_total`,
`sse_sessions_total`/`_duration_seconds`, LLM retry-attempt spans (`llm.attempt`),
and a job-level parent span (`pipeline.{graph}`). Full detail: `19` §5a, `20`, `21`.

## 4. Newly discovered finding — job-level span never reports failure (this review)

**Not in Document 26** — the job-level parent span didn't exist when 26 was
written; it was Round 1's own addition, and Round 1 did not catch this.

**The defect:** `_job_span_cm.__exit__(None, None, None)` was called
unconditionally in the shared `finally` block of both `_run_pipeline`
(research) and `_run_explanation` (learning). Because the `except` branches
already handle every failure mode internally (`CancelledError`, `TimeoutError`,
generic `Exception`) — none of them re-raise — no exception ever reaches the
span's `__exit__`, so OTel's automatic error-detection never fires. Every job
span, regardless of actual outcome, was closed as if it had succeeded.

**Root cause, not just symptom:** the span is entered/exited manually (not
via `with`) specifically so it can wrap the pre-existing `try/except/finally`
without reindenting it (`19` §5a explains why). That's a legitimate reason
to manage the context manager by hand — but it forfeits the one thing `with`
would have given for free: automatic status-from-exception. The fix restores
that signal explicitly, at its source, rather than working around the
symptom in `finally`.

**Fix:** each `except` branch that already determines a terminal
non-success outcome now calls `_job_span.set_status(Status(StatusCode.ERROR, ...))`
directly, using the span object captured from `_job_span_cm.__enter__()`'s
return value (previously discarded). The description reuses the same
already-redacted `err` string each branch already computes for the client/DB
— no new content, no raw exception text on the span. Cancellation is marked
`ERROR` with description `"Job cancelled"` (OTel's status model has no native
`CANCELLED` value; `ERROR` + a distinct description is the correct
representation — a cancelled job is not a successful one, and this keeps it
queryable as "not OK" without conflating it with a provider/timeout failure
in the description text). The success path is untouched — no explicit `OK`
override, matching OTel convention (absence of an error status already
means "not known to have failed").

**Verified NOT a pre-existing Document 26 finding:** 26 was written before
the job-level parent span existed at all (26 predates Round 1). This is
newly discovered by this review's own implementation pass, confirmed by
reading Round 1's diff directly — not something 26 missed.

## 5. Retrieval-duration correction

`retrieval_duration_seconds` was only observed at `retrieve()`'s two normal
`return` points (empty corpus, and the final ranked result) — an exception
anywhere in between (BM25 indexing, embedding lookup, reranking) left that
attempt's duration silently unrecorded. Restructured into a single
`try/finally` wrapping the whole function body; the two ad-hoc `.observe()`
calls at the return points were removed (superseded by the `finally`, not
left alongside it — the requested "smallest correct structure," not the
largest one that still passes). No label, name, or type change; retrieval
behavior (return values, exception propagation) is unchanged — verified by
`test_retrieve_records_duration_even_when_it_raises` asserting both the
metric increment *and* that the original `RuntimeError` still propagates.

## 6. SSE cancellation regression coverage

Document 26's own fix (mid-2026-08-08) corrected an outcome-classification
bug where every *normal* stream completion was counted as `"cancelled"`
(closing right after the terminal `event: end` frame raises `GeneratorExit`
at that suspended yield, indistinguishable from a real disconnect unless
`outcome` is set *before* the terminal yield). That fix had tests for
`"completed"` and `"error"` but none for the actual `"cancelled"` path that
motivated it. Added: a real `InMemoryEventBus`, no terminal event ever
published, one frame consumed, then `body_iterator.aclose()` — the exact
mechanism Starlette's `StreamingResponse` uses on a genuine client
disconnect, not a synthetic exception. Asserts `outcome="cancelled"` is
recorded and `outcome="completed"` is *not* — the specific regression this
guards against.

## 7. Repository cleanup

Three zero-byte, untracked, never-committed files at repo root (`Container`,
`str`, `the`) — confirmed accidental (empty, no git history, timestamped
during this session's own tool use) and removed. **One more of the same
class was found during final verification and was not in the original
list:** `pure` (zero bytes, untracked, no git history, timestamped mid-way
through this round's work). Removed for the same reason. All four were
almost certainly produced by a shell-quoting/redirection artifact in this
session's own tool invocations, not by application code — worth the
operator's attention if it recurs, but out of scope to root-cause further
here (no application code path writes to the repository root).

## 8. `/health` — CTO decision (not reopened)

Unchanged, as directed. `/health`'s response shape and dependency profile
are exactly as they were after Round 1's O-12/O-13 fixes (cheap
`estimated_document_count()`, no new I/O). `/health/ready`'s conditional
Redis check (§2, A2) is the only readiness-side change, and it was already
compliant with this ruling before this round started.

## 9. Exact test results

| Suite | Result |
|---|---|
| Hermetic (`pytest -m "not live"`) | **180/180 passing** (173 prior + 5 job-span-status tests + 1 SSE cancellation test + 1 retrieval-exception test) |
| Contract (`tests/contract/`) | **8/8 passing** — route inventory and SSE event-shape contracts both re-confirmed unchanged |
| Live, fresh instance (`:8004`) | **43/49 passing** — identical failure set to every prior baseline this milestone (`test_get_report`, `test_delete_account_scopes_report_cascade`, `test_samples_visible_to_any_authed_user`, 3× `test_password_reset.py`) — zero regressions |
| Real-traffic metric confirmation | `/api/metrics` after the live run: `retrieval_duration_seconds_count 2.0`, `sse_sessions_total{outcome="completed",...} 1.0`, `sse_sessions_total{outcome="cancelled",...} 1.0` — the fixed code observed in actual use, not only in unit tests |

No test was skipped or could not be executed — the full requested set (hermetic, contract, new span-status tests, retrieval-duration test, SSE cancellation test, and the full live suite) ran to completion.

## 10. Remaining risks

- The zero-byte stray-file issue (§7) recurred once during this very round after being "fixed" earlier — if it recurs again, it's worth tracing to its actual cause (a specific tool-call pattern) rather than repeatedly cleaning up after it.
- `ratelimit_degraded` and exhaustive per-method Redis error coverage remain open items already tracked in `19`/`20`/`25` — unchanged by this round, not newly introduced.
- No OTLP collector is configured in this environment, so span *status* was verified via in-memory exporters in unit tests and via successful, error-free live-suite execution — not by inspecting a real trace backend's UI. This is the same posture the rest of M6's tracing has always had (`21` §1).

## 11. Final production-readiness assessment

**READY FOR CTO REVIEW.** Evidence: 180/180 hermetic+contract, 43/49 live
with zero regressions (confirmed against the established baseline), a
newly-discovered defect found and fixed with test coverage proving both the
break and the fix, no API contract change (route inventory + SSE event
shape both re-verified), `/health` untouched per the standing CTO ruling,
repository left clean.

## 12. CTO verdict recommendation

**✅ Approved** — recommend closing this fast-follow round. All six required
items landed, tested, and verified against the real code path rather than
an isolated helper. No further action items beyond the pre-existing,
already-tracked ones in §10.
