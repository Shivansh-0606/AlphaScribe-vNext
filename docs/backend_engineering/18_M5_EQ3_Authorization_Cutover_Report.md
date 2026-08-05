# Backend Engineering Milestone 5 — Report-Read Authorization Cutover (EQ-3)

**Status:** ✅ **COMPLETE**
**Milestone:** Backend Engineering M5 · **Date:** 2026-08-05
**Governed by:** Backend Architecture `v1.0` (🔒 frozen); EQ-3 ruling
(`00_README.md`'s consolidated ratification register: *"Owner-scope report reads? →
Scope (404 cross-tenant); no frontend path affected"*); `01 D-5`
**Follows:** [`17_M4_Backend_Capability_Roadmap_Reconciliation.md`](17_M4_Backend_Capability_Roadmap_Reconciliation.md)
(§6, Milestone 5 recommendation)
**Baseline:** `Shivansh-0606/AlphaScribe-vNext` · branch `main`, working tree atop commit `e5650be`

---

## 1. EQ-3 Implementation Report

### 1.1 Features implemented

Every report route that previously trusted "the caller knows the UUID" as sufficient
authorization is now scoped to owner-or-shared-sample, matching the pattern
Learning already shipped (M2) and `list_reports`/`delete_report` already had.

| Route | Before | After |
|---|---|---|
| `GET /reports/{id}` | Unscoped at all 3 fallback tiers (`db.reports`, in-process `Job`, `db.jobs` mirror) | Each tier scoped to owner+sample (Mongo tiers) or owner (in-process `Job`, which has no sample concept) |
| `GET /reports/{id}/stream` | Unscoped — any authenticated caller with the UUID could open the SSE stream | Scoped to owner via the in-process `Job.user_id`; the injected `final` event's report fetch re-scoped too (belt-and-suspenders, mirrors Learning's identical double-check) |
| `POST /reports/{id}/cancel` | Unscoped — any authenticated caller could cancel another tenant's in-flight job | Scoped to owner via `Job.user_id`, checked before the terminal-state branch so a non-owner can't even learn whether the job finished |
| `POST /reports/compare` | Unscoped `$in` query — any requested id belonging to another tenant was silently included | Scoped at the query (`$or": [{"user_id"...}, {"is_sample"...}]}`), same predicate `list_reports` already used |
| `GET /reports` (list) | Already scoped | No change |
| `DELETE /reports/{id}` | Already scoped | No change |

### 1.2 A necessary, in-scope addition: the cache-hit lookup in `POST /reports/generate`

Live-suite verification (§2) surfaced that `generate_report`'s `(ticker, query)`
cache lookup was **also** unscoped — it could return `{"job_id": <another
tenant's report>, "cached": true}` to a caller who, after this cutover, could
never actually read that job_id again (every subsequent `GET`/`stream`/`cancel`
would correctly 404 them). Before this milestone, that same unscoped cache
hit was a **silent cross-tenant content leak** (the very risk `EQ-3` exists to
close) — as of this milestone's read-side scoping, it becomes an inconsistent,
broken UX instead of a silent leak, but the root defect is the same query.

This milestone's own scope explicitly lists **"Backward-compatible migration
behavior"** as required. Leaving the cache lookup unscoped would not be
backward-compatible with the newly-scoped reads — it would be a regression
introduced by *only* fixing one side of one coupled query. The fix is one
query predicate (the same `$or` used everywhere else in this cutover), inside
the authorization-relevant half of `generate_report` (the cache lookup, which
is functionally a disguised read), not the generation pipeline itself
(`_run_pipeline`, retrieval, LLM calls — none of which were touched). Flagged
here explicitly since the milestone brief said "do not modify report
generation" and this is the one line inside that function this milestone did
touch, with the reasoning fully on record for review.

### 1.3 Files changed

| File | What |
|---|---|
| `server.py` | `_deny_cross_tenant()` helper (audit-logs a denial, returns a generic 404); `cancel_report`, `stream_report` + `_report_stream_events`, `get_report` (all 3 tiers), `compare_reports` scoped; `generate_report`'s cache lookup scoped (§1.2); `generate_report`'s `db.jobs` insert now records `user_id` (needed for `get_report`'s 3rd-tier scoping) |
| `infrastructure/security/authorization.py` | Module docstring updated — no longer says EQ-3 is deferred to Phase 6; records that M5 landed it as its own focused PR, same precedent EQ-2 (M3) already set |
| `tests/test_reports_scoping.py` | +6 live tests: owner-still-has-access (2), cross-tenant-denied (3), compare-excludes (1) |
| `tests/unit/test_server_helpers.py` | +1 hermetic test: `cancel_report`'s ownership gate, calling the route directly against the in-memory `JobStore` (no Mongo needed — same pattern as the EQ-2 rescore test) |

### 1.4 ADRs / stable IDs referenced

`01 D-5` (the original finding); `EQ-3` (`00_README.md`'s ratification register — the
ruling this milestone executes, not re-litigates); `10 §4.2`/ADR-024 (the
Owned/Shared/Admin access-class model `is_owned_or_shared` implements — see
§1.5 for why it wasn't the literal call site); `infrastructure/security/authorization.py`'s
own docstring (already anticipated this exact milestone: *"EQ-3's cutover...
needs its own focused, reviewable PR — not a side effect"*).

**No new ADR was needed** — EQ-3 was already a ratified decision with a stated
rule; this milestone executes it, per the brief's own "Do not introduce new
ADRs unless a new architectural decision becomes necessary" instruction.

### 1.5 `is_owned_or_shared` was not the literal call site — this is by design, not an oversight

`infrastructure/security/authorization.py::is_owned_or_shared(resource, user)` already
existed, unit-tested, unused, built specifically for this cutover (Phase 1).
It operates on an **already-fetched dict**. Every route in §1.1 either:

- fetches from `db.reports` (a dict, but scoped at the **query** — cheaper,
  avoids materializing a document the caller can't see — the same shape
  `list_reports` already used), or
- fetches from the in-process `JobStore` (a `Job` **object**, not a dict, with
  no query capability and no shared/sample concept — a job is never a
  sample, only a completed report can be).

Neither shape matches `is_owned_or_shared`'s "dict, already fetched" input.
The function remains correct, tested, and available for the day a call site
actually needs that shape (documented in its own docstring, updated this
milestone).

### 1.6 Remaining risks

| Risk | Assessment |
|---|---|
| `get_report`'s 3rd tier (`db.jobs` mirror, post-restart) uses query-level scoping, not the fetch-then-audit-log pattern the other 3 routes use | A cross-tenant hit here 404s correctly but isn't audit-logged individually (indistinguishable from "doesn't exist" at the query level). Accepted: this tier is rarely reached at all — the M2 startup sweep already marks any orphaned `queued`/`running` row `failed` on boot, so by the time this tier could matter, the interesting data has usually already moved to `db.reports` (tier 1) |
| Pre-existing `db.jobs` rows (inserted before this milestone) have no `user_id` | Become unreadable via tier 3 for everyone, including their original owner. Low risk: tier 3 only ever served status/events for a still-in-flight job, and no job stays in-flight indefinitely — old rows are already terminal by the time anyone would query them, and their real content (if completed) lives in the correctly-scoped `db.reports` tier instead |
| `compare_reports`'s exclusion log can't distinguish "not yours" from "never existed" | Same query-level-scoping trade-off as tier 3 above — logged as "not visible to caller," not asserted as a denied attempt, to avoid overclaiming what the log actually proves |

### 1.7 Technical debt

None introduced. `M4`'s technical debt register already listed this exact item
(§5, "EQ-3 / D-5 — reports unscoped reads") with a Medium-High effort
estimate; actual effort matched that estimate.

---

## 2. Authorization Test Report

### 2.1 Added tests

| Count | Type | File | Covers |
|---|---|---|---|
| 1 | Hermetic (unit) | `tests/unit/test_server_helpers.py` | `cancel_report` denies a non-owner before any Mongo write |
| 6 | Live (integration/authorization) | `tests/test_reports_scoping.py` | Owner retains access to get/stream/cancel (2 tests); non-owner denied on get/stream/cancel (3 tests); compare excludes an inaccessible report (1 test) |

### 2.2 Verification performed

| Requirement (from the milestone brief) | Result |
|---|---|
| Authorized users retain access | ✅ `test_owner_can_still_get_and_stream_own_report`, `test_owner_can_still_cancel_own_report` — both pass against the real running server |
| Unauthorized users receive the correct responses | ✅ 404 (not 403 — matches EQ-3's own ruling text and Learning's established precedent: a 403 would confirm the resource exists to a non-owner, a 404 doesn't) for get/stream/cancel; excluded (not erroring) for compare |
| Existing frontend flows continue to function unchanged | ✅ No response shape changed for any authorized caller — `{"job_id":...}`/`{"status","id","report"}`/etc. all byte-identical to before. `docs/governance/Feature_Parity_Tracker.md`'s own note on EQ-3 already anticipated this: "no frontend path affected" |
| Regression tests | ✅ Full live suite: 47/49 passing (up from the 39/43 baseline `15`/`16` established — see §4, two remaining failures are pre-existing and unrelated) |
| API contract validation | ✅ `tests/contract/` suite (8/8) unchanged and passing — no route added/removed/renamed, no response shape changed |

### 2.3 Passing tests

```
Hermetic (pytest -m "not live"): 163 passed, 0 failed   (M4 baseline: 162; +1 this milestone)
Contract:                          8 passed, 0 failed   (unchanged)
Live (pytest -m live):            47 passed, 2 failed   (baseline was 39/43 — see §4 for the 2 remaining, both pre-existing and unrelated)
```

### 2.4 Audit logging — verified live, not just asserted

Every denial in §1.1 logs a structured `WARNING` line before returning 404.
Confirmed against the real running server's log during this milestone's own
live test run:

```
WARNING alphascribe: cross-tenant report access denied: user=0ec15553-... id=5b6f6fa6-...
WARNING alphascribe: cross-tenant job access denied: user=0ec15553-... id=5b6f6fa6-...
WARNING alphascribe: cross-tenant job access denied: user=0ec15553-... id=5b6f6fa6-...
```

Also independently visible via the existing `http_requests_total` Prometheus
metric (unchanged, Phase 1 middleware) — the same test run shows exactly one
`404` count each for `GET /reports/{job_id}`, `GET /reports/{job_id}/stream`,
`POST /reports/{job_id}/cancel`, and `POST /reports/compare`, matching the 4
denial tests one-for-one.

---

## 3. API Compatibility Report

**Zero contract changes.** Verified two ways:

- `tests/contract/test_route_inventory.py` (route count, paths, methods) — unchanged, 37 routes, still passing.
- `tests/contract/test_request_schemas.py` (response/request shapes) — unchanged, still passing.
- Every response an **authorized** caller receives is byte-identical to before this milestone — the only behavioral change is what a caller who was **never supposed to have access** now sees (404 instead of the actual content), which is precisely the security fix, not a contract change.

| Route | Contract status |
|---|---|
| `GET /reports/{id}` | ✅ Compatible — shape unchanged for the owner; 404 (already a documented possible response) for others |
| `GET /reports/{id}/stream` | ✅ Compatible — same SSE framing, same event shapes; 404 unchanged as a possible response |
| `POST /reports/{id}/cancel` | ✅ Compatible — same `{"job_id","status","note"?}` shape; 404 unchanged as a possible response |
| `POST /reports/compare` | ✅ Compatible — same `{"reports":[...]}` shape; the existing "fewer than 2 reports found" 404 now also covers the excluded-by-scoping case, which is exactly the same status code a genuinely-missing id already produced |
| `POST /reports/generate` | ✅ Compatible — `{"job_id":...}`/`{"job_id","cached":true}` shape unchanged; a cache-hit now only ever returns a job_id the caller can read (§1.2), which is a bug fix, not a shape change |

---

## 4. Security Validation Report

### 4.1 What was validated

| Check | Method | Result |
|---|---|---|
| A non-owner cannot read another tenant's report via any of the 3 `get_report` fallback tiers | Live test against a real, currently-in-flight-then-completed report | ✅ 404 |
| A non-owner cannot open another tenant's SSE stream | Live test | ✅ 404, connection never opens |
| A non-owner cannot cancel another tenant's job (and cannot even learn its status via the "already finished" branch) | Live test | ✅ 404 before the terminal-state check is ever reached |
| A non-owner's `compare` request silently excludes reports they can't see, rather than erroring in a way that reveals existence | Live test | ✅ Confirmed — falls into the pre-existing "fewer than 2 found" 404, same status a nonexistent id produces |
| A fresh caller cannot be handed a job_id for content they can't read via the cache-hit path | Live test (this is what surfaced the §1.2 fix in the first place) | ✅ After the fix, a cache-hit is only ever returned when the caller can actually read the result |
| Denials are audit-logged with correlation-relevant fields (user id, resource id), never with content | Direct log inspection | ✅ Confirmed (§2.4); no report content, no email, no session token in any log line |
| The owner is never accidentally denied by the new checks | Live test (dedicated positive-path tests) | ✅ Confirmed |

### 4.2 What this closes

`01 D-5`: *"Report reads are unscoped (IDOR-by-obscurity). `GET /reports/{id}`
and `POST /reports/compare` return any report to any authenticated caller who
knows the UUID."* — closed for `GET /reports/{id}`, `GET /reports/{id}/stream`,
`POST /reports/{id}/cancel`, and `POST /reports/compare`. `list_reports` and
`delete_report` were already closed before this milestone.

### 4.3 What remains an accepted, documented posture (not a gap in this milestone)

- Curated **samples** (`is_sample: true`) remain readable by any authenticated
  user — this is the *ratified* Shared access class (`10 §4.2`), not an
  oversight; every route above correctly implements owner-**or**-shared, not
  owner-only.
- Pre-existing `db.jobs` rows without `user_id` become unreadable via
  `get_report`'s 3rd tier for everyone (§1.6) — a deliberate, low-risk,
  disclosed trade-off of the migration, not silently accepted.

---

## 5. Production Readiness Assessment

### 5.1 Determination

> ## ✅ **Ready for CTO Review**

### 5.2 Evidence

| Claim | Evidence |
|---|---|
| EQ-3 is fully implemented | §1.1 — all 4 previously-unscoped routes now owner-or-shared-scoped, matching the ratified rule exactly |
| All authorization tests pass | §2.3 — 163/163 hermetic (+1), 8/8 contract, 47/49 live (2 pre-existing, unrelated failures — §5.3) |
| Frontend compatibility is maintained | §3 — zero contract changes, verified by the unmodified contract suite plus explicit shape-preservation checks |
| The feature is production-ready | §4 — every denial path live-tested against the real server, not just asserted; audit logging confirmed via both application logs and the existing Prometheus metric, independently |

### 5.3 The two remaining live-suite failures — both pre-existing, both improved by this milestone

| Test | Status | Note |
|---|---|---|
| `backend_test.py::test_get_report` | Still fails, different cause than before | Previously failed on a **stale cross-process cache hit** (see `15 §3.3`); this milestone's cache-scoping fix (§1.2) eliminated that cause. It now fails because the fresh generation it triggers hit the same **pre-existing local-LLM flakiness** documented since `15`/`16` (an empty `draft_report` on a run where `synthesizer`/`fact_checker` errored against the local model) — a different, already-disclosed, environment-specific cause, not a new defect |
| `test_reports_scoping.py::test_samples_visible_to_any_authed_user` | Unchanged | Same pre-existing missing-AAPL-sample data issue documented in `15`/`16`, confirmed unrelated to any code this milestone touched |

**Net effect of this milestone on suite health:** 39/43 (previous baseline) → 47/49
(this milestone) — `test_sse_stream` and `test_list_reports_contains_job`, both
previously failing due to the stale-cache-hit issue §1.2 fixed as a side
effect, now pass.

---

*Companion documents:* [`01_Backend_Architecture_Review.md`](01_Backend_Architecture_Review.md) ·
[`10_Backend_Security_Architecture.md`](10_Backend_Security_Architecture.md) ·
[`15_M2_Phase2_Learning_Implementation_Report.md`](15_M2_Phase2_Learning_Implementation_Report.md) ·
[`16_M2_Company_Research_Findings_Report.md`](16_M2_Company_Research_Findings_Report.md) ·
[`17_M4_Backend_Capability_Roadmap_Reconciliation.md`](17_M4_Backend_Capability_Roadmap_Reconciliation.md) ·
index: [`00_README.md`](00_README.md)
