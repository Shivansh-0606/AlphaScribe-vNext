# 81 — Post-M15 Backend & AI Roadmap Reconciliation

**Status:** 🟡 **PROPOSED — CTO DECISION REQUIRED.** This document is a
roadmap reconciliation. It records the actual post-M15 repository and
governance state, classifies every known remaining Backend & AI candidate
against that state and the project's existing governance framework, and
**recommends one preferred next Backend & AI direction.** It is a
**recommendation, not a milestone-selection authorization** — formal M16
milestone selection is a separate, subsequent CTO governance act
(§7, §8). Ratification of this document would adopt its findings (§1–§6)
and may record a **preferred next direction**; it would authorize no
implementation, no contract, no architecture, and no `git` mutation (§9).

**Type:** Roadmap reconciliation (research / governance only — no source
code, test, schema, index, migration, route, LangGraph node/topology,
MongoDB collection, Redis usage, provider, configuration, infrastructure,
evaluation-infrastructure, deployment, or frontend file created or
modified to produce it; `.gitignore` untouched. Documents 62–80 read, not
modified. The only file this task creates is this document.

**Pattern / genre:** the same "Post-M{N} Backend & AI Roadmap
Reconciliation" form as
[17_M4_Backend_Capability_Roadmap_Reconciliation.md](17_M4_Backend_Capability_Roadmap_Reconciliation.md),
[28_Post_M6_Roadmap_Reconciliation.md](28_Post_M6_Roadmap_Reconciliation.md),
[44_Post_M9_Backend_AI_Roadmap_Reconciliation.md](44_Post_M9_Backend_AI_Roadmap_Reconciliation.md),
[51_Post_M11_Backend_AI_Roadmap_Reconciliation.md](51_Post_M11_Backend_AI_Roadmap_Reconciliation.md),
[58_Post_M12_Backend_AI_Roadmap_Reconciliation.md](58_Post_M12_Backend_AI_Roadmap_Reconciliation.md),
[62_Post_M13_Backend_AI_Roadmap_Reconciliation.md](62_Post_M13_Backend_AI_Roadmap_Reconciliation.md),
and its direct predecessor
[67_Post_M14_Backend_AI_Roadmap_Reconciliation.md](67_Post_M14_Backend_AI_Roadmap_Reconciliation.md).
Reconciles current repository / governance state and recommends what comes
next. Does not itself ratify or select anything.

**Relationship to Document 67.** Document 67 is the 🟢 CTO-RATIFIED
(2026-09-03) authoritative **Post-M14** position. It named the C-2…C-5 +
Filing Q&A + Durable Research Sessions candidate pool and recommended
**C-4 "What Changed Since Last Review"** as the preferred next direction.
C-4 was formally selected as **M15** (Document 68, ratified Document 69),
contracted (Document 70 R4, ratified Document 72), architected (Document
73 R1, ratified Document 74), implementation-authorized (Document 75,
ratified Document 76; §14 testing-floor amended by Document 77, ratified
Document 78), implemented, reviewed, committed
(`f8c06649e94f45c388bbecf3eeedb9e5340f2024`), pushed to `origin/main`, and
formally closed (Document 79, ratified Document 80). **This document is the
Post-M15 successor.** Document 67 is **not modified** here; its still-live
registers (the surviving candidates C-2, C-3, C-5, Filing Q&A, Durable
Research Sessions; the blocked/deferred items; the governance-hygiene
table; OD-2…OD-13) are carried forward and updated, not deleted.

**Date:** 2026-09-08.

---

## 0. What This Document Is and Is Not

**Is:** a factual reconstruction of the post-M15 baseline; a status pass
over the governance record; an evidence-based classification of the
remaining Backend & AI candidates using the project's existing governance
framework; one recommended next direction (with its alternatives, risks,
dependencies, and open questions stated); and a statement of the
governance gates that must be cleared before that direction could enter
implementation.

**Is not:** an implementation; an implementation authorization; a
contract; an architecture decision pack; a scope freeze; a **formal M16
milestone selection**; an amendment to any prior document; a reopening of
M15, M14, or any earlier milestone; a reopening of the D77/D78
testing-floor position; a promotion of Durable Research Sessions; a
promotion of C-2 as remediation of any M14 or M15 accepted ceiling. It
resolves no open product/architecture question — where one exists
(notably the Filing Q&A single-turn-vs-conversational scope question), it
**surfaces** it for a later phase rather than answering it. It invents no
candidate.

---

## 1. Purpose

M15 / C-4 — the direction Document 67 recommended and Document 68 formally
selected — is **closed and delivered** (§2). Under the project's
governance framework, the transition from one Backend & AI milestone to
the next runs through a **Post-M{N} Backend & AI Roadmap Reconciliation**
that is CTO-ratified and then followed by a *separate* formal
milestone-selection act (Document 62 §13; Document 67 §8 / §14.3;
Document 68 §1). **No Post-M15 reconciliation exists** — the highest
Backend & AI governance document prior to this one is Document 80
(Document 79 CTO Ratification Record).

This document performs that reconciliation for the M15→M16 transition. It
answers one question:

> **After M15 / C-4, what should AlphaScribe's next Backend & AI direction
> be?**

It does **not** assume the answer. Every candidate is evaluated
independently against repository evidence and the existing governance
record. **C-4 is removed from the active candidate set** — it is
completed work (§2.1, §3, §6).

---

## 2. Authoritative Post-M15 Baseline

Reconstructed this session by direct read-only inspection of `git`
(`status`, `rev-parse`, `rev-list`, `log`, `show`, `reflog`) and reads of
source, tests, and governance documents. **No mutation performed.**

### 2.1 M15 delivery

| Fact | Value / evidence |
|---|---|
| M15 — C-4 "What Changed Since Last Review" | **DELIVERED and CLOSED** (Document 79, ratified Document 80). |
| M15 implementation commit | **`f8c06649e94f45c388bbecf3eeedb9e5340f2024`** (short `f8c0664`), subject `feat(m15): implement change brief`, single parent `be4949b` (M14), non-merge, 13 files (7 modified, 6 added), `+2181 / −3`. |
| Publication state | **PUBLISHED.** `git rev-parse HEAD` = `git rev-parse origin/main` = `f8c06649e94f45c388bbecf3eeedb9e5340f2024`; ahead/behind `0 / 0`; `origin/main` reflog `update by push` (2026-09-08 14:18:40 +0530), linear fast-forward `be4949b → f8c0664`, no force push, no additional commit. |
| CTO reviews | Post-commit technical review **PASS**; post-push review **PASS** (Document 79 §3–§4; Document 80 §4). |
| M15 committed governance chain | Documents 67–80 are **untracked / not version-controlled** (`git status` `??`). Committing them is a separate, subsequently CTO-authorized step (the model Documents 61 `f1c18c3` and the M14 chain `be4949b` followed) — a governance-hygiene item, not an M15 defect (§6). |

### 2.2 M15 contract and architecture remain authoritative

| Artifact | Status |
|---|---|
| **Document 70 R4 — M15 / C-4 API Contract** | **🟢 CTO-RATIFIED (Document 72).** Two mutually-exclusive modes (`period` financial, `report` narrative); distinct financial `{index, statement_type, period_end, metric}` and narrative `{index, report_id, field}` citation shapes, never merged; mandatory both-sides narrative grounding; `complete` / `partial` / `insufficient_evidence` state vocabulary; zero new error classes; four-route async family under `/api/companies/{ticker}/changes`; `reused` always `false`; caller-supplied comparison points only. |
| **Document 73 R1 — M15 / C-4 Architecture Decision Pack** | **🟢 CTO-RATIFIED (Document 74).** Two independent engines sharing only the orchestration shell; `period` mode pure/LLM-free; `report` mode one `chat_json` call. **AH-1** resolved (structured schema extension, not text decomposition). **AH-2** resolved (see §2.3). |
| **Document 75 / 76 — Implementation Authorization** | **🟢 CTO-RATIFIED.** Scope: one additive `JobKind.CHANGE_BRIEF`, one additive `job_deadline_change_brief_s`, the four routes, the §14 tests, doc updates — nothing broader. |
| **Document 77 / 78 — D75 §14 Testing-Floor Amendment** | **🟢 CTO-RATIFIED.** The golden-dataset `report`-mode evaluation set is **evaluation / validation evidence and tracked future work**, not a completion or commit-review gate. The first seven §14 floor items remain mandatory. |
| **Document 79 / 80 — Milestone Closure** | **🟢 CTO-RATIFIED.** M15 / C-4 engineering delivery formally CLOSED. Deployment, release, and M16 selection each remain separate, unauthorized acts. |

### 2.3 M15 accepted architectural ceilings (ceilings, not defects — not reinterpreted here)

- **AH-2 — process-local, TTL-bounded, in-process job-result buffer.**
  `_CHANGE_BRIEF_RESULTS` in `backend/server.py` (peer of M14's
  `_FILING_ANALYSIS_RESULTS`): a completed change brief is retrievable
  only from the one backend process that ran the job, only before its TTL
  / 256-entry eviction, and **not** across a process restart or a second
  backend instance. `reused` is always `false`. **No `change_brief` /
  `changes` MongoDB collection, index, schema, or migration was created**
  (`git show HEAD:backend/server.py` `db.*` references: `companies`,
  `filings`, `filing_chunks`, `reports`, `comparison_explanation*`,
  `explanation*`, `jobs`, `users` — no M15 addition). **No Redis
  final-result persistence; no cross-process reconstruction; no
  sticky-session mechanism.** The SSE `final` frame is built from the same
  process-local buffer.
- **Single-backend-process is the supported deployment model for the
  `POST → completion → GET` lifecycle** (Document 73 R1 §12.1 / §12.2,
  ratified Document 74 §10). Horizontal multi-instance support for that
  lifecycle is **explicitly out of M15 scope** (AAQ-3) and would require a
  separate architecture decision plus schema/infrastructure governance.
  **This is now a standing constraint every future async-job Backend & AI
  candidate must either accept (as M14 and M15 did) or explicitly
  supersede through the `08_MongoDB_Data_Architecture.md` + ADR chain.**
- **`report`-mode narrative determinism is not guaranteed bit-identical
  across runs** (Document 70 R4 §17) — an accepted, contract-sanctioned
  property, since no identity-keyed result reuse was adopted. `period`
  mode is fully deterministic.
- **Golden-dataset `report`-mode evaluation evidence has not been
  generated**, and the framework to generate it (a `change_brief` surface
  in `evaluation/golden_dataset/`, an adapter, loader exact-set test
  updates, a case corpus) is **outside** the M15 authorized scope. Per
  Documents 77 / 78 this is **tracked future work, not a gate** and **not
  an M15 defect**. It is **not** a Backend & AI milestone candidate and is
  **not** reopened here.
- **Deadline value `job_deadline_change_brief_s = 60.0`** is an
  operational parameter (OCD-4 / AAQ-1), retunable without a contract
  change.
- **OCD-1 … OCD-6 and AAQ-1 … AAQ-4 remain open** exactly as Documents
  75 / 76 leave them. This document resolves and reinterprets none of them.

### 2.4 Current architectural capabilities (post-M15, additive to Document 67 §2.4)

- **Backend API surface: 51 approved routes**
  (`backend/tests/contract/test_route_inventory.py`, exact-set guard,
  `assert len(APPROVED_ROUTES) == 51`) — the 47 post-M14 routes plus the 4
  additive M15 change-brief routes (`POST /api/companies/{ticker}/changes`,
  `GET …/changes/{id}`, `GET …/changes/{id}/stream`,
  `POST …/changes/{id}/cancel`).
- **A fifth async LLM/data surface** — Change Brief — after report
  generation, comparison-explanation (M9.1), learning, and Filing
  Analysis (M14). Out-of-graph orchestration
  (`server.py::_run_change_brief`, branching on `comparison_type`); **the
  frozen research LangGraph is unchanged**.
- `JobKind ∈ {RESEARCH, LEARNING, COMPARISON_EXPLANATION, FILING_ANALYSIS,
  CHANGE_BRIEF}`; `job_deadline_change_brief_s` (60 s);
  `alphascribe_change_brief_runs_total{outcome, comparison_type}` metric;
  `pipeline.change_brief` OTel span.
- `agents/change_brief_financial.py` — pure, deterministic, LLM-free
  period-over-period metric delta (style peer of `agents/scoring.py`).
- `agents/change_brief_narrative.py` — one bounded `chat_json` call over
  two `reports`, reusing `comparison_explanation.py`'s evidence extraction
  unmodified plus a **new per-item both-sides citation validator**.
- **MongoDB collections in play — unchanged from Document 67 §2.4.**
  **M15 added none.** `reports` and `financial_statements` are read-only
  inputs to C-4.
- **734 hermetic backend tests green** (full `tests/unit` + `tests/contract`,
  `-m "not live"`), including the M15 route family, financial-engine unit
  tests, narrative grounding/citation tests, and the AH-2
  deployment-invariant tests.

### 2.5 Governance state (recorded, not decided)

```text
M12 (Financial Research Data Completion)  COMPLETE / ACCEPTED / COMMITTED (b4e90a0) / PUSHED
M13 (Filing Content Reading)             COMPLETE / REVIEWED PASS / COMMITTED (244ca5c) / GOV-RECONCILED (f1c18c3) / PUSHED
M14 (Filing Analysis)                    COMPLETE / VALIDATED (§20.1 PASS) / COMMITTED (be4949b) / PUSHED
M15 (C-4 "What Changed Since Last Review") COMPLETE / POST-COMMIT + POST-PUSH REVIEW PASS / COMMITTED (f8c0664) / PUSHED / CLOSED (D79, ratified D80)

Document 67 (Post-M14 Roadmap Reconc.)   🟢 CTO-RATIFIED (2026-09-03)
Document 68 / 69 (M15 selection)          🟢 M15 FORMALLY SELECTED = C-4 / RATIFIED
Document 70 R4 / 72 (M15 API contract)    🟢 CTO-RATIFIED
Document 71 (blocked D70 review)          🔴 BLOCKED (historical — superseded by D72)
Document 73 R1 / 74 (M15 architecture)    🟢 CTO-RATIFIED (AH-1, AH-2 resolved)
Document 75 / 76 (impl authorization)     🟢 CTO-RATIFIED
Document 77 / 78 (D75 §14 amendment)      🟢 CTO-RATIFIED (golden-dataset eval = tracked future work, not a gate)
Document 79 / 80 (M15 closure)            🟢 CTO-RATIFIED — M15 / C-4 ENGINEERING DELIVERY CLOSED
Document 81 (THIS)                        🟡 PROPOSED — CTO DECISION REQUIRED; NOT a formal M16 selection

C-4 "What Changed Since Last Review"      COMPLETED — DELIVERED AS M15 (f8c0664); removed from the active candidate set (§3, §6)
C-2 Structured Filing-Section Extraction  FUTURE CANDIDATE — not selected, not rejected, not promoted as M14/M15 remediation (Doc 67 §4.C-2 / §6; Doc 68 §5)
C-3 Financial Visualization               FRONTEND / PRODUCT TRACK — not a Backend & AI milestone (Doc 58 §9; Doc 62 §6 C-3; Doc 67 §4.C-3)
Filing Q&A                                SEPARATELY SCOPED — FUTURE CANDIDATE gated on a prior CTO/product scope decision (Doc 67 §4.FQA / OD-9)
Durable Research Sessions                 BLOCKED — product decision + new ADR + new collection all still missing (Doc 58 §10; Doc 62 §6 C-4(5); Doc 67 §4.DRS)
C-5 Governance / register hygiene         GOVERNANCE MAINTENANCE — not a Backend & AI milestone (Doc 62 §6 C-5; Doc 67 §4.C-5)
G8 remediation / gate-version items       BLOCKED / CARRIED FORWARD — no CTO authorization for any step
Document 58 §28 disposition               OPEN CTO governance-hygiene decision (Doc 67 OD-11) — unchanged
NEXT MILESTONE (M16)                       NONE selected; NONE implementation-authorized
```

### 2.6 The authorization ladder is preserved and not collapsed

```text
roadmap reconciliation  ≠  CTO roadmap ratification  ≠  formal milestone selection  ≠
contract proposal  ≠  contract ratification  ≠  architecture decision pack  ≠
architecture ratification  ≠  implementation authorization  ≠  implementation-authorization ratification  ≠
technical review PASS (a validation fact)  ≠  commit authorization  ≠  push authorization  ≠  milestone closure  ≠  closure ratification
```

M15 traversed the full ladder (Documents 67 → 80). **M16 stands before
the first rung:** this reconciliation is not yet ratified; the next
distinct act after its ratification — **formal M16 milestone selection** —
has **not** occurred and is **not** performed here.

---

## 3. Post-M15 Candidate Pool

Only candidates supported by existing project evidence are listed. **No
candidate is invented.** All originate in Document 62 §6 / Document 67 §3
except where a different ratified document is cited. **C-4 is not in this
pool — it is completed work (§6).**

| # | Candidate | Origin (evidence) | One-line |
|---|---|---|---|
| **C-2** | Structured Filing-Section Extraction | Doc 62 §6 C-2; Doc 64 §16; Doc 65 §20 / §27.2; Doc 67 §4.C-2; Doc 68 §5 | Persist section boundaries / labels for `filing_chunks` (Risk Factors / MD&A / …) as first-class data. |
| **C-3** | Financial Visualization | Doc 58 §9; Doc 62 §6 C-3; Doc 67 §4.C-3; `master-plan/03_Feature_Roadmap.md` §"Data Visualization" | Charts over the M12 `financials` `periods[]` series. |
| **C-5** | Governance closure + register hygiene | Doc 58 §14; Doc 62 §6 C-5; Doc 67 §4.C-5 | Bring stale governance registers/indices current; commit the D67–D80 chain; resolve Document 58 §28. |
| **FQA** | Filing Q&A (bounded, single-filing) | `master-plan/03_Feature_Roadmap.md` §"Filing Q&A" (AI Financial Copilot); Doc 62 §6 C-1(2); Doc 64 §4; Doc 67 §4.FQA | Ask targeted questions of one ingested filing, grounded in its own text. |
| **DRS** | Durable Research Sessions | `master-plan/03_Feature_Roadmap.md` §"Research Sessions"; Doc 58 §10; Doc 62 §6 C-4(5); Doc 67 §4.DRS | Persistent, resumable research sessions with saved reasoning / sources. |

**Adjacent items noted but not admitted as candidates** (no ratified
governance slot; recorded for completeness, unchanged from Document 67 §3):
Learning backend build-out (OD-13); a narrative diff for the base
`POST /reports/compare` (small unscoped gap); Google Social Auth vs.
`CLAUDE.md` (needs a product ruling, not code).

---

## 4. Candidate-by-Candidate Reconciliation

Roadmap/reconciliation level only. **No implementation design.**

### C-2 — Structured Filing-Section Extraction

- **User value.** *Medium.* Better in-filing navigation ("jump to Risk
  Factors", read a clean MD&A) over ~900-char label-less `filing_chunks`.
  Document 62 / Document 67 both rate this "navigation, not analysis" —
  **lower standalone value** than an analysis or copilot capability.
- **Strategic value.** *Medium–High as an enabler.* A persisted section
  representation is infrastructure a richer Filing Analysis and Filing Q&A
  could build on. Its value is forward leverage, not the feature itself.
- **Architectural leverage.** Would replace M14's analysis-time heuristic
  + optional K=3 LLM section locator (`agents/filing_sections.py`) with a
  persisted label source for future capabilities.
- **Dependencies.** None on M14 or M15. Reuses `filing_chunks`, the ingest
  pipeline, the M13 read envelope.
- **Implementation complexity.** *High.* New persisted representation for
  section boundaries/labels; a probable re-ingest / backfill of the
  existing `filing_chunks` corpus; a section-aware read or an M13-envelope
  addition; a likely section-boundary accuracy gate analogous to M14 §20.1.
- **Risk.** *Medium–High.* If implemented as a graph node → a
  **frozen-LangGraph-architecture change / stop-and-CR**. Schema +
  migration surface. "Which sections, how identified, stored where" is a
  real design space (Doc 62 §6 C-2(6)).
- **Repository readiness.** *Partial.* Data (`filing_chunks`) and the M14
  heuristics exist; **no** persistence layer, re-ingest path, or contract
  exists.
- **Relationship to M14/M15.** Independent; an enabler for future filing
  work, not a dependency of anything shipped.
- **Persistence implications.** **New durable collection + schema
  required** — triggers the `08_MongoDB_Data_Architecture.md` + ADR chain
  — plus a probable migration of the existing corpus.
- **Interaction with AH-2.** **None.** C-2's store is durable
  filing-derived structural data (a peer of `filings` / `filing_chunks`),
  not transient job-result retention. It neither uses nor challenges the
  AH-2 process-local buffer.
- **Durable Research Sessions leakage.** **No.** Filing-scoped structural
  data carries no per-user or session state.
- **Frontend/backend coordination.** Backend-led; a frontend section view
  would follow but is not required for the backend milestone.
- **New contract required.** Yes (section representation, envelope changes).
- **New persistence architecture required.** **Yes.**
- **Maintenance vs. milestone.** A **milestone** if selected — it is
  substantial Backend & AI product/infrastructure work, not maintenance.
- **Disposition.** **FUTURE CANDIDATE — eligible now, unchanged from
  Document 67 §4.C-2 / Document 68 §5.** Not a prerequisite for anything
  shipped; **not** promoted as remediation of M14's accepted §20.1
  section-location ceiling (which **passed** and remains an accepted
  ceiling, not a defect — §2.3, Document 65 §27.2/§27.3). If chosen, it is
  justified **only** by its forward infrastructure value, never by
  reframing an accepted limitation as a defect.

### C-3 — Financial Visualization

- **User value.** *Medium–High, "highly visible"* — a direct MVP roadmap
  line ("Data Visualization"). Financial statements render as tables only
  today.
- **Strategic value.** *Medium.* Completes a visible MVP surface.
- **Architectural leverage.** None on the Backend & AI track.
- **Dependencies.** None. The data blocker was removed by M12:
  `GET /companies/{ticker}/financials` already returns the multi-period
  `periods[]` series. `recharts` is the roadmap-designated library, not
  yet installed in `web/`.
- **Implementation complexity.** *Low — frontend only.*
- **Risk.** *Low.*
- **Repository readiness.** *High* on the data side; frontend work
  unstarted.
- **Relationship to M14/M15.** None.
- **Persistence implications.** **None.**
- **Interaction with AH-2.** **None.**
- **Durable Research Sessions leakage.** **No.**
- **Frontend/backend coordination.** **Frontend only** — Document 58 §9
  and Document 62 §6 C-3 both record "any remaining work is frontend
  (`recharts`), not a Backend & AI milestone".
- **New contract required.** No ("no backend change; no new endpoint" —
  Doc 62 §6 C-3(8)).
- **New persistence architecture required.** No.
- **Maintenance vs. milestone.** A **frontend milestone**, on the frontend
  governance track.
- **Disposition.** **INELIGIBLE AS THE NEXT BACKEND & AI MILESTONE —
  frontend-track initiative.** Unchanged from Document 58 §9 / Document 62
  §6 C-3 / Document 67 §4.C-3 / Document 68 §5. May proceed under frontend
  governance independently of this reconciliation. Recorded so its absence
  from the Backend & AI recommendation is explicit, not an oversight.

### C-5 — Governance closure + register hygiene

- **User value.** **None user-facing.** Value is governance integrity.
- **Strategic value.** *Medium* — prevents a future document citing a
  stale register as evidence that shipped M8–M15 work "does not exist".
- **Architectural leverage.** None — documentation only.
- **Dependencies.** None.
- **Implementation complexity.** *Low.* Documentation edits + a
  governance-doc commit.
- **Risk.** *Low.*
- **Repository readiness.** N/A. **Backlog confirmed this session:**
  `docs/backend_engineering/00_README.md` is still "Last updated:
  2026-08-09", index stops at Document 29 (M7), header milestone line
  stops at M6, "Phase 5 next" — does not reflect M8–M15 (Documents 30–80);
  `docs/planning/07-Roadmap-Milestones.md` remains a pre-M-series draft;
  **Documents 67–80 (the entire M15 governance chain, plus the Post-M14
  reconciliation) are untracked / uncommitted** (`git status` `??`);
  Document 58 §28 ratification block remains `(pending)` (Document 67
  OD-11); stray 0-byte working-tree artifacts (`both`,
  `` current_period_end` ``, `NOT`, `expect`, `empty)`) and the
  pre-existing unrelated `web/features/workspace-home/ui/CompanySearch.test.tsx`
  modification remain in the tree.
- **Relationship to M14/M15.** It would tidy the record *of* M14/M15,
  including version-controlling their governance chains.
- **Persistence implications.** None.
- **Interaction with AH-2.** None.
- **Durable Research Sessions leakage.** No.
- **Frontend/backend coordination.** None.
- **New contract required.** No.
- **New persistence architecture required.** No.
- **Maintenance vs. milestone.** **Maintenance.** Executed via
  `docs/governance/Documentation_Governance.md`'s numbered-amendment / CR
  chain and a CTO-authorized governance-doc commit — **not** a milestone
  contract or architecture pack.
- **Disposition.** **GOVERNANCE MAINTENANCE / PARALLEL WORK — NOT a
  Backend & AI milestone.** Unchanged from Document 62 §6 C-5 / Document 67
  §4.C-5 / Document 68 §5. Recommended to run *before or alongside* M16, as
  a short hygiene pass that also version-controls Documents 67–80.

### FQA — Filing Q&A (bounded, single-filing)

- **User value.** *High.* A user cannot ask targeted questions of one
  filing ("what's the customer-concentration risk here?") — only the four
  fixed M14 outputs, the M15 change brief, and raw text exist. Named line
  in `master-plan/03_Feature_Roadmap.md` under **AI Financial Copilot →
  Filing Q&A**.
- **Strategic value.** *High.* It is the capability M14 was repeatedly
  described as "establishing the foundation for" (Doc 62 §6 C-1(2);
  Doc 64 §4), and the natural M12 → M13 → M14 → M15 continuation into the
  Copilot group.
- **Architectural leverage.** *High reuse.* M14 + M15 have de-risked most
  of the infrastructure: the out-of-graph async-job + SSE + cancel route
  family, the deterministic citation validator
  (`agents/filing_analysis.py`), `agents/filing_sections.py` section
  location, the `agents/retrieval.py::retrieve(..., doc_id=…)` filing-scope
  hook, the BYOK/SSRF boundary, and the AH-2 process-local result-buffer
  pattern for a single-turn answer job.
- **Dependencies.** **Builds directly on M14** (and reuses M15 patterns).
  Also depends on **a prior CTO/product scope decision** (below).
- **Implementation complexity.** *Medium* for a **single-turn, stateless,
  single-filing** design (a sixth LLM surface, filing-scoped retrieval,
  one route family, one contract). *High* for a **multi-turn
  conversational** design (conversation persistence, drift control).
- **Risk.** *Medium (single-turn) → High (conversational).* Document 62
  R-1 names "Filing Analysis → chatbot" as the top scope-creep vector.
- **Repository readiness.** *High* for the single-turn design — the
  retrieval hook, citation validator, and async pattern already exist and
  are hardened; **no** contract exists and the scope pre-decision is
  absent.
- **Relationship to M14/M15.** The most direct continuation of both.
- **Persistence implications.** **None** for a single-turn stateless
  design (the answer job can use an AH-2-style transient buffer).
  **Conversation persistence** for a multi-turn design.
- **Interaction with AH-2.** A single-turn answer job **inherits AH-2
  unchanged** (process-local transient result, single-process `POST → GET`
  lifecycle). A multi-turn design would need durable conversation storage
  — a different persistence class that AH-2 does not cover.
- **Durable Research Sessions leakage — explicit boundary.** A
  **single-turn** Filing Q&A carries **no** per-user durable state and
  does **not** brush DRS. A **multi-turn conversational** Filing Q&A would
  require a per-user, durable, resumable conversation store — which is
  **structurally the same class of state as Durable Research Sessions**
  (per-user saved reasoning / sources / resumable threads). **The boundary
  is exactly the scope pre-decision:** single-turn stays clear of DRS;
  conversational overlaps it and must not be selected without the DRS
  product decision + ADR that Document 58 §10 requires. This document does
  **not** cross that boundary.
- **Frontend/backend coordination.** Backend-led contract + engine; a
  frontend Q&A surface follows.
- **New contract required.** **Yes** — request/response, filing-scope
  boundary, citation-shape reuse, statelessness/persistence boundary, an
  explicit DRS-non-overlap restatement.
- **New persistence architecture required.** **No** for single-turn;
  **yes** for conversational.
- **Maintenance vs. milestone.** A **milestone** if selected.
- **Disposition.** **FUTURE CANDIDATE — the strongest *product* direction,
  gated on one prior CTO/product scope decision** (single-turn structured
  vs. multi-turn conversational — Document 67 OD-9). It is **not eligible
  for a *now* selection** while that pre-decision is absent; it becomes the
  recommended direction the moment the pre-decision is made in favour of a
  single-turn, stateless, single-filing scope (§7).

### DRS — Durable Research Sessions

- **User value.** *High* for retention and a "Research Library" surface —
  research is not saved/resumable today.
- **Strategic value.** *High* long-term; unlocks the whole "Research
  Sessions" roadmap group.
- **Architectural leverage.** Low reuse — it is a new first-class stateful
  entity, not an analytical capability.
- **Dependencies.** Independent of M14/M15, but **cannot be scoped**
  without a prior product/CTO decision **and** a new ADR **and** an
  authorized new collection (Document 58 §10; Document 62 §6 C-4(5)). None
  of the three exists.
- **Implementation complexity.** *High* — session lifecycle, new
  collection + schema, read/write API, multiple frontend surfaces.
- **Risk.** *High* — cannot be bounded without prior governance; largest
  persistence surface in the pool.
- **Repository readiness.** *None* — no entity, no collection, no contract,
  no ADR.
- **Relationship to M14/M15.** M15 / C-4 was deliberately built **not** to
  brush DRS (explicit, unweakened, caller-supplied comparison points only;
  no last-visit state — Document 70 R4 §9 / §16 / §20). That boundary
  stands.
- **Persistence implications.** **A new durable collection + schema is the
  core of the work.**
- **Interaction with AH-2.** DRS is the opposite of AH-2 — it is
  *deliberately durable, cross-session state*. Selecting DRS would mean
  standing up exactly the persistence layer AH-2 avoids.
- **Durable Research Sessions leakage.** N/A — it **is** DRS.
- **Frontend/backend coordination.** Extensive.
- **New contract required.** Yes — after the ADR and product decision.
- **New persistence architecture required.** **Yes — the largest in the
  pool.**
- **Maintenance vs. milestone.** A **milestone**, once unblocked.
- **Disposition.** **BLOCKED — INELIGIBLE as M16.** Unchanged from
  Document 58 §10 / Document 62 §6 C-4(5) / Document 67 §4.DRS / Document 68
  §5. Recorded so its exclusion is explicit. **Not silently promoted.**

---

## 5. Cross-Candidate Comparison

Each candidate is scored against seven evidence-anchored criteria
(**+** favourable / **0** neutral / **−** unfavourable), the same frame
Document 67 §5 used. No composite number; the ranking follows from the
pattern plus the two decisive gates (K1 named MVP line; K2 free of a block
/ missing prerequisite decision). **C-4 is omitted — it is completed
work.**

| Criterion | C-2 | C-3 | C-5 | FQA | DRS |
|---|:--:|:--:|:--:|:--:|:--:|
| **K1 — Named line in the frozen MVP product roadmap** (`master-plan/03`) | 0 (enabler, not a standalone line) | **+** ("Data Visualization") | **−** (no user-facing line) | **+** ("Filing Q&A", AI Financial Copilot) | **+** ("Research Sessions") |
| **K2 — Free of a governance block / missing prerequisite decision** | **+** (none blocked) | **+** (none) | **+** (none) | **−** (needs the single-turn-vs-conversational scope pre-decision) | **−** (BLOCKED: product decision + ADR + collection all missing) |
| **K3 — Is a Backend & AI milestone** (vs. frontend / governance track) | **+** | **−** (frontend track) | **−** (governance maintenance) | **+** | **+** |
| **K4 — Reuses hardened infrastructure without new heavy infra** | **−** (new schema + probable re-ingest) | **+** (M12 `periods[]` ready; frontend lib only) | **+** (docs only) | **+** for single-turn (async/citation/retrieval hooks all exist; AH-2-style transient buffer) / **−** for conversational | **−** (new collection is the core) |
| **K5 — Standalone user value** | 0 ("navigation, not analysis") | **+** ("highly visible") | **−** ("none user-facing") | **+** (deep Copilot capability) | **+** (retention / Research Library) |
| **K6 — Low scope risk** | 0 ("which sections, how, stored where") | **+** ("Low") | **+** ("Low") | 0 single-turn / **−** conversational (Doc 62 R-1 chatbot drift) | **−** (cannot be bounded without prior governance) |
| **K7 — Low architectural load on frozen boundaries** | **−** (schema + likely a frozen-LangGraph node → stop-and-CR; `08` + ADR) | **+** (frontend only) | **+** (none) | **+** single-turn (out-of-graph, AH-2-consistent, no forced schema) / **−** conversational (conversation store) | **−** (new entity + collection + lifecycle) |

**Reading the table.**

- **C-3** scores well but fails **K3** by explicit ratified classification
  — a **frontend-track** initiative, not a Backend & AI milestone. Not
  eligible for this reconciliation's Backend & AI recommendation; may
  proceed independently on the frontend track.
- **C-5** fails **K1** and **K3** — no user-facing roadmap line;
  governance maintenance, not a milestone.
- **DRS** fails **K2** outright (BLOCKED) and is heavy on **K4 / K6 / K7**.
  Not eligible now; a credible *later* milestone only once its product
  decision + ADR exist.
- **FQA** fails **K2** *only* on a single, small, well-defined pre-decision
  (single-turn vs. conversational). In its **single-turn** form it is
  favourable on **K1, K3, K4, K5, K7** and neutral on **K6** — the
  strongest profile in the pool once that one gate is cleared. In its
  **conversational** form it collapses on **K4 / K6 / K7** and brushes DRS
  (§4.FQA).
- **C-2** is the only candidate that passes **K1 (weakly), K2, and K3**
  *today* with no missing decision — but it is **unfavourable on K4 and
  K7** (new schema, probable re-ingest, likely a frozen-architecture node
  change, the `08` + ADR chain) and only neutral on **K5** ("navigation,
  not analysis"). Document 67 / Document 68 both rank C-2 below an analysis
  capability for exactly this reason.

**Result of the comparison:** the highest-value, highest-leverage,
best-roadmap-aligned eligible Backend & AI direction is **Filing Q&A in a
single-turn, stateless, single-filing scope** — blocked only by one
pending CTO/product scope pre-decision. **C-2 Structured Filing-Section
Extraction** is the credible **eligible-today** alternative if the CTO
prefers infrastructure-first or does not want to make the FQA pre-decision
now. DRS remains blocked; C-3 is frontend-track; C-5 is maintenance.

---

## 6. Completed / Active / Blocked / Maintenance / Future

| Bucket | Items |
|---|---|
| **Completed work** | **C-4 "What Changed Since Last Review" — DELIVERED AS M15** (commit `f8c06649e94f45c388bbecf3eeedb9e5340f2024`, reviewed, pushed, CLOSED via Documents 79 / 80). Removed from the active candidate set. **No second C-4 phase is proposed; M15 is not reopened.** The golden-dataset `report`-mode evaluation is **M15 tracked follow-up** (Documents 77 / 78), not a candidate and not a reopening. |
| **Active candidates** (eligible Backend & AI milestones) | **C-2 Structured Filing-Section Extraction** — eligible today. **Filing Q&A (single-turn, single-filing)** — eligible *after* one CTO/product scope pre-decision. |
| **Blocked work** | **Durable Research Sessions** — product decision + ADR + new collection all missing (Document 58 §10). **Filing Q&A (conversational form)** — needs the same scope pre-decision *and* would then require the DRS-class governance. **G8 remediation / `JUDGE_SELF_CONSISTENCY_GATE_VERSION` change / formal M9 closure / H-1 Run 2 / G7** — carried forward; no CTO authorization; not dependencies of M16 selection. |
| **Maintenance** (not a milestone) | **C-5 governance / register hygiene** — `00_README` stale to M7; `planning/07` pre-M-series; **Documents 67–80 uncommitted**; Document 58 §28 `(pending)`; stray working-tree artifacts. Run via the numbered-amendment / CR chain + a CTO-authorized governance-doc commit. |
| **Future possibilities** (no ratified slot) | Learning backend build-out (OD-13); a narrative diff for base `POST /reports/compare`; Google Social Auth vs. `CLAUDE.md` ruling. Not evaluated as candidates. |
| **Frontend track** (not a Backend & AI milestone) | **C-3 Financial Visualization** — proceeds under frontend governance; needs no artifact from this chain. |

---

## 7. Recommended Next Direction

**On the evidence, a recommendation is supported.**

### 7.1 Ranked candidate list (eligible Backend & AI directions)

1. **Filing Q&A — bounded, single-turn, single-filing** — highest user and
   strategic value, strongest roadmap alignment ("AI Financial Copilot"),
   and the heaviest reuser of the M14 + M15 hardened stack (async job
   family, deterministic citation validator, `doc_id` retrieval hook,
   BYOK/SSRF, AH-2-style transient result buffer). **Gated on one prior
   CTO/product scope pre-decision** (single-turn structured vs. multi-turn
   conversational). Recommended as the **target direction**, with that
   pre-decision as the immediate next governance act.
2. **C-2 Structured Filing-Section Extraction** — the **eligible-today**
   alternative with no missing prerequisite decision. Lower standalone
   value ("navigation, not analysis"); needs a new durable schema, the
   `08_MongoDB_Data_Architecture.md` + ADR chain, a probable `filing_chunks`
   re-ingest, and possibly a frozen-LangGraph node change (stop-and-CR).
   A deliberate "pay down structural debt / harden the section layer now"
   choice — **not** a response to any M14 or M15 defect.
3. **Durable Research Sessions** — **BLOCKED / ineligible** until the CTO
   issues the product decision and the ADR that Document 58 §10 requires.

*(C-3 Financial Visualization and C-5 governance hygiene are not ranked
here — C-3 is a frontend-track milestone, C-5 is maintenance. Both are
recommended to proceed in parallel, independent of the M16 track — §8.)*

### 7.2 Recommendation

> **Filing Q&A — in a bounded, single-turn, stateless, single-filing
> scope — is recommended as the next Backend & AI direction, contingent on
> the CTO first issuing the single-turn-vs-conversational scope
> pre-decision as its own short governance record.** If the CTO prefers
> not to make that pre-decision now, **C-2 Structured Filing-Section
> Extraction** is the recommended eligible-today alternative.

**In parallel and independent of the M16 track:** a short **C-5 governance
hygiene pass** (bring `00_README` current, resolve Document 58 §28, and
version-control Documents 67–80 under a separate CTO-authorized commit) and
**C-3 Financial Visualization** on the frontend governance track.

### 7.3 Why it is preferable to the alternatives

1. **Roadmap alignment and value.** Filing Q&A is a **named line** in the
   frozen product roadmap's Copilot group and delivers *analysis-grade*
   user value; C-2 is an enabler ("navigation, not analysis"), C-3 is
   frontend-track, C-5 is maintenance, DRS is blocked.
2. **Infrastructure leverage.** M14 + M15 have already built and hardened
   the async out-of-graph LLM surface, the deterministic citation
   validator, filing-scoped retrieval, and the AH-2 result-buffer pattern.
   A single-turn Filing Q&A is a **sixth instance of a proven pattern**,
   not new infrastructure. C-2, by contrast, forces a new schema + ADR +
   re-ingest.
3. **Frozen-boundary load.** Single-turn Filing Q&A is **AH-2-consistent**
   (process-local transient answer, single-process `POST → GET`), needs
   **no** LangGraph topology change, **no** new provider, **no** forced
   MongoDB collection. C-2 likely needs a frozen-LangGraph node change and
   the `08` + ADR chain.
4. **The blocker is small and well-defined.** FQA's only gate is a single
   binary product-scope pre-decision — cheaper to clear than C-2's schema
   + ADR + migration design space, and it is the same pre-decision
   Document 67 OD-9 already flagged.
5. **DRS boundary is clean in the recommended scope.** A single-turn
   Filing Q&A carries no per-user durable state and does **not** brush
   Durable Research Sessions (§4.FQA). The recommendation explicitly
   **excludes** the conversational form, which would overlap DRS.

### 7.4 Key risks

- **R-1 — Scope drift toward "chatbot".** Filing Analysis → conversational
  copilot is the named top scope-creep vector (Document 62 R-1). The
  contract must fix single-turn, stateless, single-filing scope and
  restate the DRS non-overlap boundary.
- **R-2 — Retrieval-quality / answerability gate.** Whether a §20.1-style
  validation gate applies to Q&A grounding quality is an architecture-phase
  decision, not assumed here.
- **R-3 — AH-2 inheritance.** The single-process `POST → GET` deployment
  constraint carries forward; if Filing Q&A ever needs durable or
  cross-instance answer retention, that is a separate `08` + ADR decision,
  not a silent extension.
- **R-4 — If C-2 is chosen instead:** frozen-LangGraph node change
  (stop-and-CR), schema + migration surface, re-ingest of the existing
  corpus, and the standing instruction that C-2 must be justified by
  forward value, never by reinterpreting M14's accepted §20.1 ceiling as a
  defect.
- **R-5 — DRS pressure.** Any request to "remember the conversation" or
  "resume the thread" converts Filing Q&A into DRS-class work and must be
  routed to the DRS governance path, not folded into M16.

### 7.5 Dependencies

- **For Filing Q&A (recommended):** (a) a CTO/product **scope pre-decision**
  (single-turn structured vs. multi-turn conversational) — the gating
  dependency; (b) M14's shipped filing infrastructure (present); (c) the
  M15 async/citation/AH-2 patterns (present). No new dependency on any
  unbuilt system for the single-turn scope.
- **For C-2 (alternative):** the `08_MongoDB_Data_Architecture.md` + ADR
  chain; a re-ingest / backfill plan; a section-boundary accuracy-gate
  decision.
- **For both:** none of G8 / gate-version / M9-closure items are
  dependencies of M16 selection.

### 7.6 Governance artifacts required before implementation

**If the recommended Filing Q&A direction is pursued** (each a distinct,
uncollapsed CTO act):

1. **Filing Q&A scope pre-decision record** — single-turn structured vs.
   multi-turn conversational (resolves Document 67 OD-9; a short
   CTO/product governance record).
2. **Formal M16 milestone-selection record** — a separate CTO act (this
   document does **not** perform it).
3. **M16 API contract** — request/response, filing-scope boundary,
   citation-shape reuse, error-taxonomy reuse (zero new classes),
   statelessness / persistence boundary, explicit DRS-non-overlap
   restatement — followed by its CTO ratification.
4. **M16 architecture decision pack** — retrieval scoping over the `doc_id`
   hook, out-of-graph orchestration (M9.1 / M14 / M15 precedent),
   AH-2-consistent transient result retention, evaluation-gate decision —
   followed by its CTO ratification.
5. **M16 implementation authorization decision** — followed by its CTO
   ratification; includes a testing floor.
6. Implementation → technical review → **commit authorization** → **push
   authorization** → milestone closure → closure ratification.

**If C-2 is pursued instead:** formal M16 selection; an M16 API contract
(section representation, envelope changes) + ratification; an M16
architecture decision pack (heuristic-vs-LLM, ingest-node-vs-pipeline —
frozen-LangGraph stop-and-CR if a node) + ratification; an
`08_MongoDB_Data_Architecture.md` amendment + a new ADR for the
section-boundary schema; a re-ingest / backfill plan; an implementation
authorization + ratification; then the same implementation → review →
commit → push → closure ladder.

---

## 8. Proposed Governance Sequence

Each arrow is a distinct CTO governance act that does **not** confer the
next — the same uncollapsed ladder Documents 62 §13, 67 §8, and the full
M15 chain (Documents 68 → 80) define.

```text
M15 / C-4 CLOSED (f8c0664, pushed; Documents 79 / 80)
        ↓
Post-M15 Backend & AI Roadmap Reconciliation        ← THIS DOCUMENT (81). 🟡 PROPOSED — CTO DECISION REQUIRED.
        ↓  CTO roadmap ratification  (adopts §1–§6; may record a PREFERRED next DIRECTION; selects nothing)
        ↓
[If Filing Q&A] Filing Q&A scope pre-decision record  (single-turn structured vs. multi-turn conversational — OD-9)
        ↓  CTO scope decision
Formal M16 milestone-selection record                 (a separate CTO act — NOT performed here; a new short decision-record artifact)
        ↓  CTO milestone-selection decision
M16 API Contract proposal → CTO contract ratification
        ↓
M16 Architecture Decision Pack → CTO architecture ratification
        ↓
M16 Implementation Authorization Decision → CTO ratification
        ↓
engineering implementation → technical review (a validation fact) →
commit authorization → push authorization → milestone closure → closure ratification
```

**In parallel, independent of the M16 track:**
- **C-5 governance/register hygiene** (`00_README`, `planning/07`,
  `11_ADR_Index`, `Feature_Parity_Tracker`, Document 58 §28) **and**
  version-controlling Documents 67–80 — via
  `docs/governance/Documentation_Governance.md`'s numbered-amendment / CR
  chain plus a separate CTO-authorized governance-doc commit.
- **C-3 Financial Visualization** — under frontend governance; needs no
  artifact from this chain.

---

## 9. Explicit Non-Authorization

**Document 81 authorizes nothing.** It does **NOT** authorize, and must
not be read as authorizing:

- formal M16 milestone selection (a separate, subsequent CTO act);
- M16 implementation, or any implementation;
- an M16 API contract, or any contract;
- an M16 architecture decision pack, or any architecture decision;
- the Filing Q&A scope pre-decision (it is *recommended*, not *made*, here);
- source-code, test, or configuration changes;
- MongoDB schema realization — no collection, index, migration, schema
  change, or `08_MongoDB_Data_Architecture.md` amendment;
- any Redis, LangGraph, retrieval, provider-layer, or frozen-pipeline
  change;
- any frontend implementation;
- any evaluation-infrastructure work (including the M15 golden-dataset
  `report`-mode follow-up, which remains tracked future work per
  Documents 77 / 78 and is not reopened);
- any deployment or release;
- C-2, Filing Q&A, or Durable Research Sessions implementation;
- a commit, a push, a merge, or any `git` mutation.

CTO **roadmap ratification** of this document would adopt its
reconciliation findings (§1–§6) as the authoritative Post-M15 Backend & AI
roadmap position and may record a **preferred next direction**. It would
**not** constitute formal M16 milestone selection, contract approval,
architecture approval, implementation authorization, commit authorization,
or push authorization — each remains a separate, subsequent CTO act (§8).

---

## 10. Open Decisions

| ID | Open decision | Owner / phase | Notes |
|---|---|---|---|
| **OD-1** | **Is the next Backend & AI direction Filing Q&A (single-turn), C-2, or "defer"?** | CTO — roadmap ratification / formal M16 selection | §5 / §7 recommend Filing Q&A (single-turn), contingent on OD-2; C-2 is the eligible-today alternative. |
| **OD-2** | **Filing Q&A scope pre-decision:** single-turn structured vs. multi-turn conversational. | CTO / product — before any M16 selection of FQA | Carried from Document 67 OD-9. Single-turn stays clear of DRS; conversational overlaps DRS (§4.FQA). **Required before FQA can be selected.** |
| **OD-3** | **Filing Q&A grounding-quality gate:** does a §20.1-style validation gate apply? | M16 architecture phase | Not assumed here. |
| **OD-4** | **Confirm Filing Q&A (single-turn) introduces no durable per-user state** — no conversation collection, no history store. | CTO — M16 contract / architecture | The contract must restate the DRS non-overlap boundary. |
| **OD-5** | **C-2 status:** eligible-today alternative (this document's finding) vs. re-sequenced ahead of Filing Q&A vs. parallel infrastructure track. | CTO — roadmap ratification | §5 finding: eligible-today alternative; not a prerequisite; **not** promoted as M14/M15 remediation. |
| **OD-6** | **Durable Research Sessions unblock:** issue the product decision + ADR that Document 58 §10 requires, or keep DRS BLOCKED. | CTO / product — separate decision | DRS remains **BLOCKED / ineligible as M16** until then. |
| **OD-7** | **C-5 hygiene pass + D67–D80 governance-doc commit:** authorize and sequence (before M16 / in parallel / folded into the M16 cycle). | CTO — governance | Includes `00_README` (stale to M7), `planning/07` (pre-M-series), Document 58 §28 (OD-8), and the 14 uncommitted M15-chain documents. |
| **OD-8** | **Document 58 §28 disposition** — complete it as a historical-record ratification, or leave it a permanently unratified historical proposal. | CTO — governance hygiene | Carried unresolved from Document 67 OD-11. |
| **OD-9** | **C-3 Financial Visualization** — authorize on the frontend governance track (independent of this chain). | CTO — frontend governance | Not a Backend & AI milestone; recorded so its status is explicit. |
| **OD-10** | **Learning backend build-out** — elevate to a formal Backend & AI candidate, or leave unscheduled. | CTO — roadmap | Carried from Document 67 OD-13; not evaluated as a §4 candidate. |
| **OD-11** | **Stray working-tree artifacts** (`both`, `` current_period_end` ``, `NOT`, `expect`, `empty)`, and the unrelated `CompanySearch.test.tsx` modification) — disposition. | CTO / engineering — working-tree hygiene | 0-byte tooling artifacts; outside M15 and M16 scope; not cleaned by this task. |

None of these blocks roadmap ratification on its own — each is a bounded,
explicitly flagged item for a downstream decision. This document answers
none of them.

---

## 11. Repository / Working-Tree State and Provenance

Recorded by read-only inspection this session on 2026-09-08. **No `git`
mutation was performed** — no `add` / stage, `commit`, `push`, `amend`,
`rebase`, `merge`, `reset`, `restore`, `stash`, or `clean`.

- `HEAD = origin/main = f8c06649e94f45c388bbecf3eeedb9e5340f2024`
  (`f8c0664`), ahead/behind `0 / 0`.
- Document number 81 was verified free before creation (highest existing
  Backend & AI governance document was 80).
- **Documents 62–80 were read, not modified.** Documents 70 R4 / 72,
  73 R1 / 74, 75 / 76, 77 / 78, 79 / 80 remain 🟢 CTO-RATIFIED and are
  cited, not restated as new interpretations. Documents 79 and 80 are
  **not** modified.
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval / RAG code, MongoDB collection, Redis
  component, provider, configuration, evaluation-infrastructure,
  deployment, or frontend file was created or modified. `.gitignore` was
  not modified.
- Known pre-existing, unrelated working-tree items — **not** staged,
  modified, renamed, deleted, or cleaned by this task:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated — not touched)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/  (untracked, M11 evidence — not touched)
  ?? both                                                          (untracked, 0-byte stray shell-tooling artifact — not touched)
  ?? current_period_end`                                          (untracked, 0-byte stray shell-tooling artifact — not touched)
  ?? NOT                                                           (untracked, 0-byte stray shell-tooling artifact — not touched)
  ?? expect                                                        (untracked, 0-byte stray shell-tooling artifact — not touched)
  ?? empty)                                                        (untracked, 0-byte stray shell-tooling artifact — not touched)
  ?? docs/backend_engineering/67_...md through 80_...md            (pre-existing untracked governance documents — not modified)
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/81_Post_M15_Backend_AI_Roadmap_Reconciliation.md`).
  It is untracked and not yet version-controlled. Staging or committing it
  is a separate, subsequently CTO-authorized step.
- No date, decision number, or authorization wording was fabricated. This
  document authorizes nothing; it is a decision artifact for CTO review.

---

**🟡 PROPOSED — CTO DECISION REQUIRED. THIS DOCUMENT IS THE POST-M15
BACKEND & AI ROADMAP RECONCILIATION. IT IS A RECOMMENDATION, NOT A
MILESTONE-SELECTION AUTHORIZATION — FORMAL M16 SELECTION IS A SEPARATE,
SUBSEQUENT CTO ACT AND IS NOT PERFORMED HERE. C-4 "WHAT CHANGED SINCE LAST
REVIEW" IS COMPLETE AND DELIVERED AS M15 (COMMIT
`f8c06649e94f45c388bbecf3eeedb9e5340f2024`, REVIEWED, PUSHED, CLOSED VIA
DOCUMENTS 79 / 80); IT IS REMOVED FROM THE ACTIVE NEXT-MILESTONE CANDIDATE
SET, NO SECOND C-4 PHASE IS PROPOSED, AND M15 IS NOT REOPENED. THE
GOLDEN-DATASET `report`-MODE EVALUATION REMAINS M15 TRACKED FUTURE WORK
PER DOCUMENTS 77 / 78 — NOT A CANDIDATE, NOT REOPENED, NOT RESTORED AS AN
M15 COMPLETION GATE. AH-2 (PROCESS-LOCAL, TTL-BOUNDED, IN-PROCESS
JOB-RESULT BUFFER; SINGLE-BACKEND-PROCESS `POST → GET` LIFECYCLE; NO NEW
MONGODB COLLECTION; NO REDIS OR CROSS-PROCESS FINAL-RESULT PERSISTENCE)
REMAINS THE RATIFIED CONSTRAINT AND IS NOW A STANDING REQUIREMENT ON EVERY
FUTURE ASYNC-JOB CANDIDATE. RECOMMENDATION: **FILING Q&A — BOUNDED,
SINGLE-TURN, STATELESS, SINGLE-FILING — AS THE NEXT BACKEND & AI
DIRECTION, CONTINGENT ON A PRIOR CTO/PRODUCT SCOPE PRE-DECISION
(SINGLE-TURN STRUCTURED VS. MULTI-TURN CONVERSATIONAL)**; IF THAT
PRE-DECISION IS NOT MADE NOW, **C-2 STRUCTURED FILING-SECTION EXTRACTION**
IS THE ELIGIBLE-TODAY ALTERNATIVE. C-2 IS NOT PROMOTED AS REMEDIATION OF
ANY M14 OR M15 ACCEPTED CEILING — THE §20.1 SECTION-LOCATION BAR PASSED
AND REMAINS AN ACCEPTED CEILING, NOT A DEFECT. A SINGLE-TURN FILING Q&A
CARRIES NO PER-USER DURABLE STATE AND DOES NOT BRUSH DURABLE RESEARCH
SESSIONS; A MULTI-TURN CONVERSATIONAL FILING Q&A WOULD REQUIRE A
DRS-CLASS CONVERSATION STORE AND MUST NOT BE SELECTED WITHOUT THE DRS
PRODUCT DECISION + ADR THAT DOCUMENT 58 §10 REQUIRES. DURABLE RESEARCH
SESSIONS REMAINS **BLOCKED** AND IS NOT SILENTLY PROMOTED. C-3 FINANCIAL
VISUALIZATION IS A FRONTEND-TRACK INITIATIVE, NOT A BACKEND & AI
MILESTONE. C-5 GOVERNANCE / REGISTER HYGIENE IS MAINTENANCE, NOT A
MILESTONE — AND NOW INCLUDES VERSION-CONTROLLING THE UNCOMMITTED
DOCUMENTS 67–80. NO SOURCE, TEST, SCHEMA, INDEX, MIGRATION, ROUTE,
LANGGRAPH, MONGODB, REDIS, PROVIDER, CONFIGURATION, EVALUATION-
INFRASTRUCTURE, DEPLOYMENT, OR FRONTEND FILE CREATED OR MODIFIED.
`.gitignore` UNTOUCHED. DOCUMENTS 62–80 READ, NOT MODIFIED — DOCUMENTS 79
AND 80 NOT ALTERED. NO STAGE. NO COMMIT. NO PUSH. NO MERGE / REBASE /
RESET / AMEND. THE NEXT GOVERNANCE ACT IS CTO ROADMAP RATIFICATION OF
THIS DOCUMENT, FOLLOWED BY A SEPARATE CTO DECISION ON FORMAL M16
MILESTONE SELECTION (§8).**
