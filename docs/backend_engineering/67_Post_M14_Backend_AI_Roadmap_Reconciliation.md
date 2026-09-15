# 67 — Post-M14 Backend & AI Roadmap Reconciliation

**Status:** 🟢 **CTO-RATIFIED (2026-09-03) — AUTHORITATIVE POST-M14 BACKEND &
AI ROADMAP POSITION.** This document is a roadmap reconciliation. It records
the actual post-M14 repository and governance state, classifies every known
remaining Backend & AI candidate against that state and the project's
existing governance framework, and recommends **one** preferred next
Backend & AI direction. The CTO ratified it on 2026-09-03 (§14).
**Ratification adopts its findings (§1–§6); it authorizes no implementation,
freezes no architecture, creates no contract, does not formally select the
M15 milestone, and grants no commit or push authorization** — see §9, §14.
**C-4 "What Changed Since Last Review" is the ratified preferred next
Backend & AI direction; formal M15 milestone selection remains a separate,
subsequent CTO decision** (§7, §8).

**Type:** Roadmap reconciliation (research / governance only — no source
code changed, no test changed, no schema / index / migration / configuration
/ infrastructure changed, no architecture decided, no milestone authorized,
no frozen document edited, no LangGraph / MongoDB / Redis / frontend touched,
no deployment change, `.gitignore` untouched). The only file this task
creates is this document.

**Pattern / genre:** same as
[17_M4_Backend_Capability_Roadmap_Reconciliation.md](17_M4_Backend_Capability_Roadmap_Reconciliation.md),
[28_Post_M6_Roadmap_Reconciliation.md](28_Post_M6_Roadmap_Reconciliation.md),
[44_Post_M9_Backend_AI_Roadmap_Reconciliation.md](44_Post_M9_Backend_AI_Roadmap_Reconciliation.md),
[51_Post_M11_Backend_AI_Roadmap_Reconciliation.md](51_Post_M11_Backend_AI_Roadmap_Reconciliation.md),
[58_Post_M12_Backend_AI_Roadmap_Reconciliation.md](58_Post_M12_Backend_AI_Roadmap_Reconciliation.md),
and
[62_Post_M13_Backend_AI_Roadmap_Reconciliation.md](62_Post_M13_Backend_AI_Roadmap_Reconciliation.md).
Reconciles current repository / governance state and recommends what comes
next. Does not itself ratify anything.

**Relationship to Document 62.** Document 62 is the CTO-RATIFIED
(2026-08-30) authoritative **Post-M13** position. It named the C-1…C-5
candidate pool, recommended **C-1 Filing Analysis** as the preferred
direction, and left the chunk-vs-section architectural question open.
C-1 was formally selected as M14 (Document 63), contracted (Document 64),
architected (Document 65), authorized (Document 66 §18), implemented,
validated, committed, and pushed (§2). **This document is the Post-M14
successor.** Document 62 is **not modified** here; its still-live registers
(the surviving candidates C-2…C-5, the blocked/deferred items, the
governance-hygiene table) are carried forward and updated, not deleted.

**Date:** 2026-09-03.

---

## 0. What This Document Is and Is Not

**Is:** a factual reconstruction of the post-M14 baseline; a status pass
over the governance record; an evidence-based, independent classification of
the remaining Backend & AI candidates using the project's existing
governance framework; one recommended next direction (with its alternatives
and open questions stated); and a statement of the governance gates that
must be cleared before that direction could enter implementation.

**Is not:** an implementation; an implementation authorization; a contract;
an architecture decision pack; a scope freeze; a formal M15 milestone
selection; an amendment to any frozen document; a reopening of M14, M13,
H-1, or G8. It resolves no open architectural or product question — where
one exists (notably the C-4 reference-semantics question, §4.C-4 / §10), it
**surfaces** the question for a later phase rather than answering it. It
invents no candidate, no roadmap decision, and no authorization.

---

## 1. Purpose

M14 Filing Analysis — the direction Document 62 recommended and Document 63
formally selected — is **closed and delivered** (§2). Under the project's
governance framework, the transition from one Backend & AI milestone to the
next runs through a **Post-M{N} Backend & AI Roadmap Reconciliation** that is
CTO-ratified and then followed by a *separate* formal milestone-selection
act (Document 62 §13; Document 63 §4). Documents 28, 44, 51, 58, and 62 are
the precedent instances of that reconciliation for M6, M9, M11, M12, and
M13 respectively. **No Post-M14 reconciliation exists** — the highest
Backend & AI governance document prior to this one is Document 66 (M14
implementation authorization).

This document performs that reconciliation for the M14→M15 transition. It
answers one question:

> **After M14, what should AlphaScribe's next Backend & AI direction be?**

It does **not** assume the answer is C-4. C-4 is the strongest candidate
from a prior read-only discovery review, but it remains only a candidate;
this reconciliation evaluates the whole pool independently against
repository evidence and the existing governance record.

---

## 2. Authoritative Baseline

Reconstructed this session by direct read-only inspection of `git`
(`status`, `rev-parse`, `rev-list`, `log`, `show`, `ls-remote`, `branch`)
and reads of source, tests, evidence files, and governance documents. **No
mutation performed.**

### 2.1 M14 delivery

| Fact | Value / evidence |
|---|---|
| M14 — Filing Analysis | **DELIVERED.** |
| M14 implementation commit | **`be4949b5b33ea73cfedf81c03bebbdaa953772b8`** (short `be4949b`), subject `feat(m14): implement filing analysis`, parent `f1c18c3` (M13 governance), single-parent / non-merge, **30 files** (7 modified, 23 added), +16 036 / −23. |
| Publication state | **PUBLISHED.** `HEAD` = local `origin/main` = **true remote** (`git ls-remote origin refs/heads/main` = `be4949b…`) = `be4949b`; ahead/behind `0 / 0`. History `be4949b → f1c18c3 → 244ca5c → b4e90a0` is linear. |
| Push / post-push verification | The CTO directive records M14 as having passed implementation, validation, commit, push, and post-push verification. The push occurred **outside this reconciliation task** and is **corroborated by the remote ref** (`ls-remote` above). No conflict with repository state. |
| M14 committed governance chain | Documents 58, 62, 63, 64, 65, 66 are now **version-controlled** (added by `be4949b`) — previously untracked (Document 62 §16 recording note; Document 63 §10). |

### 2.2 M14 contract and architecture remain authoritative

| Artifact | Status |
|---|---|
| **Document 64 — M14 Filing Analysis API Contract** | **🟢 CTO-RATIFIED (2026-08-31) / FROZEN.** The externally observable M14 contract: exactly four outputs, always all four (Filing Summary, Risk Factors Digest, MD&A Digest, Important Changes; CQ-1 / CQ-2 — no selection parameter); each a flat cited narrative `{narrative, sources[], cited_source_indices, state}` + `coverage_boundaries`; `state ∈ {complete, partial, insufficient_evidence}`; INV-IC (§8.1, Important Changes is filing-local only); citation representation frozen (§11); async 4-route family (§9.1); error taxonomy reuse, zero additions (§10). Unchanged by implementation. |
| **Document 65 — M14 Filing Analysis Architecture Decision Pack** | **🟢 CTO-RATIFIED (2026-08-31, §27) / FROZEN.** Per-OAQ status (§27.2): OAQ-3/4/6/7/8/9/10 **RATIFIED**; OAQ-1 / OAQ-2 **CONDITIONAL** (the §20.1 STOP/CONTINUE gate preserved; C-2 not a proven prerequisite); OAQ-5 **RATIFIED LOGICAL DECISION ONLY** (two-collection pattern `filing_analyses` / `filing_analysis_jobs`; physical realization owed to the separate `08_MongoDB_Data_Architecture.md` + ADR chain). |
| **Document 66 — M14 Implementation Authorization Proposal** | **🟢 §18 IMPLEMENTATION AUTHORIZED (2026-09-02).** Commit / push were further separate CTO acts (§12.3 / §12.4). MongoDB schema realization **not** granted. |

### 2.3 M14 accepted architectural ceilings (ceilings, not defects)

The following are **accepted, disclosed limits** of the M14 architecture as
ratified and implemented. Existing evidence establishes **no defect** in
any of them; they are not to be reinterpreted as defects here.

- **§20.1 bounded OAQ-1(D) validation PASSED.** The section-location
  realization (deterministic heuristic heading detection + TOC
  discrimination + structural end-boundary detection over the existing
  unstructured `filing_chunks`, with a K=3 majority-vote LLM classification
  only for genuinely ambiguous heuristic candidates) cleared the §20.1
  STOP/CONTINUE gate on 2026-09-01: **0 false positives, 0 false negatives**
  across the validated corpus (EDGAR 10-K, EDGAR 10-Q, BSE annual report,
  plain-text `POST /ingest/text`), **byte-identical across N=5 repeated
  runs** per validated filing, LLM **not invoked at all** for the four-file
  corpus, evidence reviewer-checkable
  (`backend/evaluation/m14_section_location_spike/latest.{json,md}`).
- **The §20.1 corpus is bounded and the check is deterministic, not
  statistical.** It is 4 hand-selected real filings + N=5 repeats — **not**
  a population-level accuracy claim. **No universal section-detection claim
  was established or authorized.** Heading shapes outside that corpus can
  still mis-locate; the conservative fallbacks bound the damage
  (`ponytail:` marker in `backend/agents/filing_sections.py`).
- **One honest partial-boundary case is recorded, not a failure.** The MSFT
  10-K MD&A end boundary could not be structurally established; the locator
  collapsed to `[start, start]` with `end_established = False` and the
  output is represented as `partial` (Document 64 §11.7), never `complete`.
  The §20.1 verdict for this case is "correct start / partial-boundary
  (end not established, honestly flagged)", `false_positive = false`,
  `false_negative = false`.
- **Persistence is fallback C — process-local.** No `filing_analyses` /
  `filing_analysis_jobs` collection was created; the completed analysis is
  held only for the job's lifetime in an in-process buffer
  (`_FILING_ANALYSIS_RESULTS`, peer of `RUNNING_TASKS`), then evicted;
  `reused` is always `false`. No durability, no cross-instance sharing, no
  crash-restart recovery (`ponytail:` marker in `backend/server.py`). This
  is the Document 65 §12 last-resort path, pre-authorized by Document 66
  §5 C-l — an accepted operational ceiling within its documented L-2 / L-3
  bounds, not a defect.
- **MongoDB physical schema realization was not part of M14.** No
  collection, no index, no migration; `backend/infrastructure/mongo/` is
  unchanged by `be4949b`. The Document 65 OAQ-5 durable two-collection
  pattern remains a **RATIFIED LOGICAL DECISION ONLY**; its physical
  realization requires the separate `08_MongoDB_Data_Architecture.md` + ADR
  governance chain (Document 65 §12.1 / §27.2).
- **C-2 Structured Filing Extraction remains neither selected nor
  rejected.** Document 65 §27.2 / §27.3: a §20.1 **PASS** does not select,
  reject, or trigger C-2; and a §20.1 **FAIL** would not have authorized
  C-2 either — only a separate CTO governance decision can insert or
  re-sequence it. The §20.1 gate **passed**; this governance fact is
  preserved.
- **Filing Q&A remains excluded from M14** and reserved for a later,
  separately scoped capability (Document 64 §4; Document 65 §27.3;
  Document 63 §7).
- **Frontend "Filing analysis" `FilingViewer` variant is not built.**
  Frontend work was explicitly out of M14 *backend* scope (Document 64
  AH-6). This is a standing gap on the frontend track, not an M14 defect.

### 2.4 Current architectural capabilities (post-M14, additive to Document 62 §1.3)

- **Backend API surface: 47 approved routes** (`backend/tests/contract/test_route_inventory.py`,
  exact-set guard, `assert len(APPROVED_ROUTES) == 47`) — the 43 post-M13
  routes plus the 4 additive M14 Filing Analysis routes
  (`POST /api/companies/{ticker}/filings/{doc_id}/analysis`, `GET …/analysis/{id}`,
  `GET …/analysis/{id}/stream`, `POST …/analysis/{id}/cancel`).
- **A fourth async LLM surface** — Filing Analysis — after report generation,
  comparison-explanation (M9.1), and learning. Out-of-graph orchestration
  (`server.py::_run_filing_analysis`, mirroring `_run_comparison_explanation`);
  **the frozen research LangGraph is unchanged** (Document 65 OAQ-7).
- `JobKind.FILING_ANALYSIS`; `job_deadline_filing_analysis_s` (180 s,
  operational config); `alphascribe_filing_analysis_runs_total{outcome}`
  metric; `pipeline.filing_analysis` OTel span.
- **`agents/retrieval.py::retrieve(..., doc_id=…)`** — an additive, opt-in
  `doc_id` filter on `filing_chunks`. The report pipeline's `retriever`
  node passes no `doc_id`; its behaviour is byte-for-byte unchanged.
- `agents/filing_sections.py` — the §20.1-cleared analysis-time section
  locator (production home; the spike imports it).
- `agents/filing_analysis.py` — the four-output grounded analysis: numbered
  candidates → one HEAVY `chat_json` call per output → a **deterministic**
  OAQ-9 citation validator that builds every `{doc_id, chunk_start,
  chunk_end}` anchor and assigns state (never trusts the model for
  anchors).
- **MongoDB collections in play — unchanged from Document 62 §1.3:**
  `sessions`, `companies`, `filings`, `filing_chunks`, `reports`,
  `financial_statements`, `acquisition_states`, learning jobs,
  `comparison_explanations` / `comparison_explanation_jobs`. **M14 added
  none.**

### 2.5 Governance state (recorded, not decided)

```text
M12 (Financial Research Data Completion)   COMPLETE / ACCEPTED / COMMITTED (b4e90a0) / PUSHED
M13 (Filing Content Reading)              COMPLETE / REVIEWED PASS / COMMITTED (244ca5c) / GOV-RECONCILED (f1c18c3) / PUSHED
M14 (Filing Analysis)                     COMPLETE / VALIDATED (§20.1 PASS) / IMPLEMENTATION-AUTHORIZED (Doc 66 §18) /
                                           COMMITTED (be4949b) / PUSHED / post-push verified (per CTO directive; remote-corroborated)

Document 62 (Post-M13 Roadmap Reconc.)    🟢 CTO-RATIFIED (2026-08-30); now version-controlled (be4949b)
Document 63 (M14 Formal Selection)        🟢 M14 FORMALLY SELECTED = C-1; now version-controlled (be4949b)
Document 64 (M14 API Contract)            🟢 CTO-RATIFIED / FROZEN (2026-08-31); implemented; now version-controlled
Document 65 (M14 Architecture Pack)       🟢 CTO-RATIFIED / FROZEN (2026-08-31 §27); implemented; now version-controlled
Document 66 (M14 Impl. Auth. Proposal)    🟢 §18 IMPLEMENTATION AUTHORIZED (2026-09-02); now version-controlled
Document 67 (THIS)                        🟢 CTO-RATIFIED (2026-09-03) — AUTHORITATIVE POST-M14 ROADMAP POSITION (§14); NOT a formal M15 selection

C-2 Structured Filing Extraction          NEITHER SELECTED NOR REJECTED (Doc 62 §6 C-2; Doc 63 §6; Doc 64 §16; Doc 65 §27.2/§27.3)
Filing Q&A                                EXCLUDED FROM M14; reserved as a later, separately scoped capability
Durable Research Sessions                 BLOCKED (product/CTO decision + new ADR + new collection required — Doc 58 §10; Doc 62 §6 C-4)
G8 remediation                            BLOCKED / CARRIED FORWARD (no CTO authorization for any pathway step)
H-1                                       CLOSED WITH GOVERNANCE FOLLOW-UP
JUDGE_SELF_CONSISTENCY_GATE_VERSION       0 (unchanged)
G7                                        NO ARCHITECTURE CHANGE (unchanged)
Document 58 §28 disposition               OPEN CTO governance-hygiene decision (Doc 62 §3.3) — unchanged
NEXT MILESTONE (M15)                      NONE selected; NONE implementation-authorized
```

### 2.6 The authorization ladder is preserved and not collapsed

Distinct governance acts, none substituting for another:

```text
roadmap reconciliation  ≠  CTO roadmap ratification  ≠  formal milestone selection  ≠
contract proposal  ≠  contract ratification  ≠  architecture decision pack  ≠
architecture ratification  ≠  implementation authorization  ≠
technical review PASS (a validation fact)  ≠  commit authorization  ≠  push authorization
```

M14 traversed the full ladder. **M15 stands near the first rung:** this
reconciliation is CTO-ratified (§14), so its `CTO roadmap ratification` step
is done; the next distinct act — **formal M15 milestone selection** — has
**not** occurred. Ratification of this reconciliation is not that act.

---

## 3. Post-M14 Candidate Pool

Only candidates supported by existing project evidence are listed. **No
candidate is invented.** All originate in Document 62 §6 (the CTO-ratified
Post-M13 pool) except where a different ratified/frozen document is cited.

| # | Candidate | Origin (evidence) | One-line |
|---|---|---|---|
| **C-2** | Structured Filing-Section Extraction | Document 62 §6 C-2; Document 63 §6; Document 64 §16; Document 65 §20 / §27.2 | Persist section boundaries / labels for `filing_chunks` (Risk Factors / MD&A / etc.) as first-class data. |
| **C-3** | Financial Visualization | Document 62 §6 C-3; Document 58 §9; `docs/master-plan/03_Feature_Roadmap.md` §"Data Visualization" | Charts (Revenue / Profit / Margin / Growth / Ratio) over the M12 `financials` `periods[]` series. |
| **C-4** | "What Changed Since Last Review" | Document 62 §6 C-4; `docs/master-plan/03_Feature_Roadmap.md` §"Company Research" | A grounded change brief for one company against a prior reference point. |
| **C-5** | Governance closure + register hygiene | Document 62 §6 C-5; Document 58 §14 GH-1/2/4/5/6 | Bring stale governance registers/indices current; resolve Document 58 §28. |
| **FQA** | Filing Q&A (bounded, single-filing) | `docs/master-plan/03_Feature_Roadmap.md` §"AI Financial Copilot → Filing Q&A"; Document 62 §6 C-1(2); Document 64 §4 | Ask questions of one ingested filing, grounded in its own text. Named as the capability M14 "establishes the foundation for". |
| **DRS** | Durable Research Sessions | `docs/master-plan/03_Feature_Roadmap.md` §"Research Sessions"; Document 58 §10; Document 62 §6 C-4 | Persistent, resumable research sessions with saved reasoning / sources. |

**Adjacent items noted but not admitted as candidates** (no ratified
governance slot; recorded for completeness):

- **Learning backend build-out.** `docs/governance/Feature_Parity_Tracker.md`
  (🔒 FROZEN) calls the unimplemented Learning backend "a reasonable next
  milestone, though not itself a parity gap". It is **not** in Document 62's
  §6 pool and has no ratified Backend & AI roadmap slot; the Learning
  *pipeline* itself already shipped in M2 Phase L (Document 15). Recorded as
  a possible future candidate the CTO may separately elevate; not evaluated
  as a §4 candidate here.
- **Comparison "explanation of differences".** The Feature Parity Tracker
  records that `compare_reports` "never calls an LLM"; M9.1
  comparison-explanation is a *separate* surface. Whether the base
  `POST /reports/compare` should gain a narrative diff is a small, unscoped
  gap — not a Document 62 candidate; recorded, not evaluated.
- **Google Social Auth vs. `CLAUDE.md`.** The one unresolved product/CTO
  document conflict carried since Document 17 §1 / Document 28. Explicitly
  "not a milestone candidate — needs a product/CTO ruling, not code"
  (Document 28). Recorded, not evaluated.

---

## 4. Candidate-by-Candidate Reconciliation

Roadmap/reconciliation level only. **No implementation design.** "Systems
affected" and "governance artifacts required" describe the *shape* of the
work, not how to build it.

### C-2 — Structured Filing-Section Extraction

- **Product value.** *User problem:* `filing_chunks` are ~900-char slices
  with no section identity; a user cannot jump to "just the Risk Factors"
  or read a clean MD&A; `FilingViewer` calls a chunk a "section" only as a
  navigation convenience (Document 62 §6 C-2(1)). *Measurable value:*
  better in-filing navigation; and it would give M14's section-location
  layer a persisted label source instead of an analysis-time heuristic +
  LLM pass. Document 62 rated it **Med–High** value but flagged that it
  "delivers navigation, not analysis" — **lower standalone user value** than
  an analysis or change feature.
- **Dependencies.** Does **not** depend on M14. Reuses `filing_chunks`, the
  ingest pipeline, the M13 read-envelope shape. M14's `agents/filing_sections.py`
  heuristics could inform the extraction logic but are not required.
- **Architecture implications.** *Systems eventually affected:* ingest
  (`agents/ingest.py`) or a new pipeline node; a new persisted
  representation for section boundaries/labels; a probable re-ingest /
  backfill path for already-ingested filings; the M13/M14 read paths would
  gain an optional section view. *New persistence:* **yes — new
  collection/schema** (section boundaries + labels), which triggers the
  `08_MongoDB_Data_Architecture.md` + ADR chain. *API changes:* likely — a
  section-aware read or an addition to the M13 content envelope.
- **AI implications.** *Retrieval:* not required. *AI/LLM reasoning:*
  optional — heading heuristics vs. an LLM section classifier is a design
  fork (Document 62 §6 C-2(6)). *Structured extraction:* this **is** the
  candidate. *New quality gate:* a section-boundary accuracy gate analogous
  to M14 §20.1 would likely be warranted.
- **Persistence implications.** New durable store required; a re-ingest /
  migration for the existing `filing_chunks` corpus is probable.
- **Governance implications if selected.** Formal M15 selection record; an
  M15 API contract (section representation, envelope changes); an M15
  architecture decision pack (heuristic-vs-LLM, ingest-vs-node — a
  **frozen-architecture change / stop-and-CR** if it adds a graph node);
  an `08` amendment + a new ADR for the schema; a re-ingest/backfill plan;
  a separate implementation authorization.
- **Risks.** Frozen-LangGraph-architecture change if implemented as a node
  (Document 62 R-9); schema + migration surface; "which sections, how
  identified, stored where" is a real design space (Document 62 §6 C-2(6));
  standalone value is navigation, not analysis.
- **Current disposition.** **FUTURE CANDIDATE.** See §5 for the explicit
  determination (not a prerequisite; not the recommended next direction;
  could run parallel but is heavier than C-2's standalone value warrants).

### C-3 — Financial Visualization

- **Product value.** *User problem:* financial statements render as tables
  only; the roadmap's "Data Visualization" line (Revenue / Profit / Margin /
  Growth / Ratio charts) is unbuilt (Document 62 §6 C-3(1)). *Measurable
  value:* Medium–High, "highly visible" (Document 62 §6 C-3(2)) — a direct
  MVP roadmap line.
- **Dependencies.** Does **not** depend on M14. The data blocker was
  removed by M12: `GET /companies/{ticker}/financials` already returns the
  multi-period `periods[]` metric series (Document 62 §6 C-3(3); Document 58
  §9). `recharts` is the roadmap-designated library, not yet installed in
  `web/`.
- **Architecture implications.** *Systems affected:* **frontend only.**
  Document 58 §9 and Document 62 §6 C-3(4)/(8) both record explicitly:
  "any remaining work is frontend (`recharts`), not a Backend & AI
  milestone". *New persistence:* no. *Retrieval:* no. *API changes:* no
  ("no backend change; no new endpoint; no derived / aggregated metrics
  beyond what `financials` returns" — Document 62 §6 C-3(8)).
- **AI implications.** None. No LLM reasoning; no structured extraction; no
  evaluation infrastructure.
- **Persistence implications.** None.
- **Governance implications if selected.** Frontend governance track only
  (frontend architecture docs + the frontend milestone process). **It would
  not be numbered in the Backend & AI M-series.**
- **Risks.** Low (Document 62 §6 C-3(6)).
- **Current disposition.** **INELIGIBLE AS THE NEXT BACKEND & AI
  MILESTONE — frontend-track initiative.** Recorded so its absence from the
  Backend & AI recommendation is explicit, not an oversight. It may proceed
  under frontend governance independently of this reconciliation (Document
  62 §13).

### C-4 — "What Changed Since Last Review"

- **Product value.** *User problem:* a returning user re-reads a full brief
  to find out "what's new" instead of getting a scoped change read; the
  frozen product roadmap names **"What Changed Since Last Review" under
  Company Research** (`docs/master-plan/03_Feature_Roadmap.md`; Document 62
  §6 C-4(1)). *Measurable value:* Medium–High for **retention / repeat
  engagement** (Document 62 §6 C-4(2)) — it gives a user a reason to return
  between full research cycles, and replaces a manual re-read with a
  grounded delta.
- **Dependencies.** Does **not** hard-depend on M14. Reuses (Document 62 §6
  C-4(3)): the `reports` collection (prior briefs), the `financial_statements`
  `periods[]` series (M12), and the **M9.1 comparison-explanation diff
  pattern** (an out-of-graph async LLM job that already produces a grounded
  narrative comparison). It **may optionally** consume M14 filing analyses
  as one change source, but does not require them.
- **Architecture implications.** *Systems eventually affected:* a new async
  read-style surface (likely one route family), reading `reports` +
  `financial_statements` (both exist). *New persistence:* **open** — the
  same on-demand-vs-persisted fork M14 faced (fallback-C precedent exists;
  a durable collection would face the "no new collection" scrutiny +
  `08` + ADR). Document 62 §6 C-4(8) **explicitly excludes** "no new
  collection". *Retrieval:* likely **not required** — inputs are already
  structured stored artifacts; a diff-then-summarise pass is plausible
  without RAG (open, architecture-phase decision). *API changes:* yes —
  new route(s), route inventory 47 → 48+; a new contract document.
- **AI implications.** *AI/LLM reasoning:* yes — delta identification +
  a plain-language change narrative is generative (one HEAVY `chat_json`
  call, M14/M9.1-style). *Structured extraction:* modest — numeric
  period-over-period deltas are deterministic (`agents/scoring.py`-style);
  narrative change detection is LLM. *Reranking:* no. *Evaluation
  infrastructure / new quality gate:* a grounding check (every stated change
  cites a real prior artifact / period), analogous to M14's citation
  validator; whether a §20.1-style validation gate applies is an
  architecture-phase decision — **not assumed here**.
- **Persistence implications.** Reads only, in the minimal form. Any
  persistence of the change brief itself is deferred to the contract phase;
  the minimal MVP can follow the M14 fallback-C precedent (no new
  collection).
- **Governance implications if selected.** Formal M15 selection record; an
  M15 API contract (envelope, error taxonomy reuse, **reference-semantics
  decision**, on-demand-vs-persisted, citation representation, "what
  changed" breadth freeze); an M15 architecture decision pack (data-access,
  RAG-or-not, LangGraph treatment — expected **out-of-graph, no topology
  change** on the M9.1/M14 precedent, frontend integration pattern);
  possibly an `08` amendment + ADR **only if** persistence is chosen; a CTO
  ruling that C-4 does not brush the BLOCKED Durable Research Sessions
  entity; a separate implementation authorization.
- **Risks.**
  - **R-C4-1 — Reference-semantics ambiguity.** "Last Review" is not
    resolved by project material (see below). Left unresolved, it could
    drift toward durable session state.
  - **R-C4-2 — "What changed" scope creep.** Financials-only vs. narrative
    vs. both must be bounded in the contract (Document 62 §6 C-4(6)).
  - **R-C4-3 — Durable-Research-Sessions adjacency.** C-4 is "adjacent to
    (but not) Durable Research Sessions, which is BLOCKED" (Document 62 §6
    C-4(5)). C-4 **must not** be a backdoor for durable research state
    (§7).
  - **R-C4-4 — Value is retention, not a new analytical primitive** — a
    narrower capability than M14.
- **Reference-semantics — the material does not fully resolve it.**
  Possible reference points for "since last review":
  1. **Prior research artifact** — the user's most recent (or a
     user-selected) prior `reports` brief for that company. *Supported by:*
     Document 62 §6 C-4(3) ("the `reports` collection (prior briefs)"),
     §6 C-4(4) ("needs prior-report … selection").
  2. **Prior reporting period** — the previous fiscal period in
     `financial_statements.periods[]`. *Supported by:* Document 62 §6
     C-4(3)/(4) ("the financials `periods[]` series", "period … selection"),
     §6 C-4(7) ("multi-period financial data now exist for a diff to be
     meaningful").
  3. **Explicitly selected comparison point** — the user picks two artifacts
     / periods to diff. *Supported by:* the M9.1 comparison-explanation
     pattern C-4 is told to reuse (it compares an explicitly chosen pair of
     reports).
  4. **User / session state** — "since you last looked", tracked per user
     over time. *Contra-indicated by:* Document 62 §6 C-4(8) ("**No durable
     sessions; … no new collection; no watchlist**") and §6 C-4(5) (C-4 is
     *not* Durable Research Sessions). The roadmap places "What Changed
     Since Last Review" under **Company Research**, not under **Research
     Sessions**.

  **Determination:** the existing material **points toward semantics 1–3
  (artifact / period / explicitly-selected pair) and away from semantics 4
  (durable user/session state)**, but it does **not conclusively fix** which
  of 1–3 is the product intent. The one phrase that leans toward "since your
  last visit" (Document 62 §6 C-4(1) "what's new since last time") is
  contradicted by that same candidate's own exclusion list (§6 C-4(8)).
  **This is a CTO/product decision required** (§10 OD-2). It is **not**
  resolved here by inventing a design.
- **Current disposition.** **RECOMMENDED next Backend & AI direction,
  subject to formal M15 selection** — see §5 and §7. The recommendation is
  conditional on the CTO resolving the reference-semantics question and the
  "what changed" breadth in the subsequent contract phase.

### C-5 — Governance closure + register hygiene

- **Product value.** **None user-facing.** Value is governance integrity:
  it prevents a future document citing a stale register as evidence that
  shipped M8–M14 work "does not exist" or "is unapproved" (Document 62 §6
  C-5(2)).
- **Dependencies.** None. Documentation only.
- **Architecture implications.** None — no source, test, schema, or
  infrastructure change (Document 62 §6 C-5(3)/(8)).
- **AI implications.** None.
- **Persistence implications.** None.
- **Governance implications if selected.** It **is** governance work: it
  would be executed via `docs/governance/Documentation_Governance.md`'s
  numbered-amendment / change-request chain — **not** a milestone contract
  or architecture pack.
- **Discrepancies confirmed this session (evidence for the C-5 backlog):**
  - `docs/backend_engineering/00_README.md` — "**Last updated: 2026-08-09**",
    header reads "M1 … → M2 … → M5 … → M6", "Phase 5 next"; the document
    index table stops at **Document 29 (M7)**. It does not reflect M8–M14
    (Documents 30–66) or this document. **Materially stale.**
  - `docs/planning/07-Roadmap-Milestones.md` — a "Living draft · Last
    updated: 2026-07-12" using a Phase 0/1/2/3 + "Monetization sessions"
    model that **predates the entire M-series** and does not mention any
    M-numbered milestone. Stale / superseded by the Document 17/28/44/51/58/62
    reconciliation series.
  - `docs/backend_engineering/11_ADR_Index.md`, `docs/governance/Feature_Parity_Tracker.md`
    Phase-4B note — recorded stale by Document 62 §6 C-5(2) / §13; not
    exhaustively re-verified here (Document 62, CTO-ratified, is the
    authoritative record of these).
  - Document 58 §28 ratification block remains `(pending)`; its disposition
    is an open CTO governance-hygiene decision (Document 62 §3.3).
- **Current disposition.** **GOVERNANCE MAINTENANCE / PARALLEL WORK —
  NOT a Backend & AI milestone.** See §6 and §8. Recommended to run
  *alongside* whatever M15 is (or before it, as a short hygiene pass), not
  *as* M15. This document (Doc 67) is itself the Post-M14 half of the
  Document 62 §6 C-5 scope.

### FQA — Filing Q&A (bounded, single-filing)

- **Product value.** *User problem:* a user cannot ask targeted questions
  of one filing ("what's the customer concentration risk here?") — only the
  four fixed M14 outputs and the raw text exist. *Measurable value:* high
  for the "AI Financial Copilot" roadmap group; deeper than fixed outputs.
- **Dependencies.** **Depends on / builds directly on M14.** Reuses
  `agents/filing_sections.py` (section location), `agents/filing_analysis.py`'s
  deterministic citation validator, the out-of-graph async-job pattern, the
  `doc_id` retrieval hook, and the fallback-C precedent. Named repeatedly
  as the capability M14 "establishes the foundation for" (Document 62 §6
  C-1(2); Document 64 §4).
- **Architecture implications.** *Systems eventually affected:* a fifth LLM
  surface; likely retrieval-scoped over one filing (the `doc_id` hook
  exists); a new route family; a new contract. *New persistence:* open
  (conversation history if multi-turn — which brushes durable state).
  *API changes:* yes.
- **AI implications.** *Retrieval:* yes (filing-scoped). *LLM reasoning:*
  yes. *Structured extraction:* reuses M14's. *Evaluation:* a grounding /
  answerability gate likely warranted.
- **Persistence implications.** None for a stateless single-turn design;
  a multi-turn conversational design would need conversation persistence —
  which collides with the durable-state exclusions.
- **Governance implications if selected.** **A prior product-scope
  decision is required first** — fixed/structured single-turn vs. multi-turn
  conversational ("chatbot"). Then the full chain: formal M15 selection, M15
  contract, M15 architecture pack, implementation authorization. Document 62
  R-1 names "Filing Analysis → chatbot" as the top scope-creep vector;
  Document 63 §7 and Document 65 §27.3 restate "Filing Q&A remains excluded
  from M14".
- **Risks.** Highest scope risk of the pool (conversational drift);
  requires a product decision that has not been made; never entered
  Document 62 §6 as a formal candidate (it appears only as "a later,
  separately scoped capability").
- **Current disposition.** **FUTURE CANDIDATE — gated on a prior CTO/product
  scope decision** (single-turn vs. conversational). Credible as a *later*
  milestone; not eligible for a recommendation now because the prerequisite
  product decision is absent.

### DRS — Durable Research Sessions

- **Product value.** *User problem:* research is not saved/resumable; the
  roadmap's "Research Sessions" group (Durable Research Sessions, Saved
  Reasoning, Saved Sources, Resume Research, Research History) is unbuilt.
  *Measurable value:* high for retention and the "Research Library" surface.
- **Dependencies.** Independent of M14.
- **Architecture implications.** A new first-class entity; **a new
  collection**; session lifecycle; read/write API; frontend surfaces.
- **AI implications.** Minimal directly (it is a state/persistence
  capability, not an analytical one).
- **Persistence implications.** **New durable collection + schema — the
  core of the work.**
- **Governance implications if selected.** Document 58 §10 / Document 62 §6
  C-4(5): it "needs a **product/CTO decision + a new ADR + a new
  collection** before scoping". None of those three exists.
- **Risks.** Cannot even be scoped without prior governance; largest
  persistence surface in the pool.
- **Current disposition.** **BLOCKED — INELIGIBLE as M15** until the CTO
  issues the product decision and the ADR that Document 58 §10 requires.
  Recorded so its exclusion is explicit (§6).

---

## 5. Cross-Candidate Comparison

**Method.** Each candidate is scored against seven explicit, evidence-anchored
criteria. Ratings are ordinal (**+** favourable / **0** neutral / **−**
unfavourable), each with its evidence. No composite number; the ranking
follows from the pattern of ratings plus the two decisive gates (named MVP
roadmap line; free of a governance block / missing prerequisite).

| Criterion | C-2 | C-3 | C-4 | C-5 | FQA | DRS |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| **K1 — Named line in the frozen MVP product roadmap** (`master-plan/03`) | 0 (implied by "Filing Summaries/Risk Factors" but not a standalone line) | **+** ("Data Visualization") | **+** ("What Changed Since Last Review", Company Research) | **−** (no user-facing line) | **+** ("Filing Q&A", AI Financial Copilot) | **+** ("Research Sessions") |
| **K2 — Free of a governance block / missing prerequisite decision** | **+** (none blocked) | **+** (none) | **+** (none blocked; reference-semantics is a *contract-phase* decision, not a block) | **+** (none) | **−** (needs a prior single-turn-vs-conversational product decision) | **−** (BLOCKED: product decision + ADR + collection all missing) |
| **K3 — Is a Backend & AI milestone** (vs. frontend / governance track) | **+** | **−** (Doc 58 §9 / Doc 62 §6 C-3: "not a Backend & AI milestone") | **+** | **−** (governance maintenance) | **+** | **+** |
| **K4 — Reuses hardened infrastructure without new heavy infra** | 0 (needs new schema + probable re-ingest) | **+** (M12 `periods[]` ready; frontend lib only) | **+** (`reports` + `financials` + M9.1 diff pattern + M14 async/citation pattern; minimal form needs no new collection) | **+** (docs only) | 0 (fifth LLM surface; retrieval-scoped) | **−** (new collection is the core) |
| **K5 — Standalone user value** (Doc 62 §8 ranking + §6 notes) | 0 ("navigation, not analysis"; "lower standalone value" — Doc 62 §6 C-2) | **+** ("highly visible") | **+** ("Med–High for retention") | **−** ("Low for users") | **+** (deep Copilot capability) | **+** (retention) |
| **K6 — Low scope risk** | 0 ("which sections, how identified, stored where") | **+** ("Low") | 0 ("Medium" — breadth + reference-semantics must be bounded) | **+** ("Low") | **−** (conversational drift — Doc 62 R-1) | **−** (cannot be bounded without prior governance) |
| **K7 — Low architectural load on frozen boundaries** | **−** (schema + likely a frozen-LangGraph node → stop-and-CR; `08` + ADR) | **+** (frontend only) | **+** (out-of-graph, no topology change on M9.1/M14 precedent; no forced schema) | **+** (none) | 0 (fifth LLM surface; retrieval into a new surface) | **−** (new entity + collection + lifecycle) |

**Reading the table.**

- **C-3** scores well but fails **K3** by explicit ratified classification
  (Document 58 §9; Document 62 §6 C-3): it is a **frontend-track**
  initiative, not a Backend & AI milestone. It is therefore **not eligible**
  for this reconciliation's Backend & AI recommendation, regardless of its
  merits, and can proceed independently on the frontend track.
- **DRS** fails **K2** outright (BLOCKED) and **FQA** fails **K2** (a prior
  product-scope decision is missing). Neither is eligible for a *now*
  recommendation; both are credible *later* milestones once their
  prerequisite decisions exist.
- **C-5** fails **K1** and **K3**: it has no user-facing roadmap line and is
  governance maintenance, not a milestone (§6, §8).
- **C-2** is the only *eligible Backend & AI* alternative to C-4. It passes
  **K1** weakly, **K2**, **K3**, and **K5** at best neutrally, and is
  **unfavourable on K4 and K7** (new schema, probable re-ingest, likely a
  frozen-architecture node change, the `08` + ADR chain). Document 62's own
  ranking placed C-2 **below** C-1 precisely because it "delivers
  navigation, not analysis … heavier … for lower standalone value".
- **C-4** is the only candidate that is **favourable or neutral on every
  criterion**, favourable on the two decisive gates (**K1** named MVP line;
  **K2** no block / no missing prerequisite decision), an eligible Backend &
  AI milestone (**K3**), a heavy reuser of hardened infrastructure with **no
  forced new persistence** in its minimal form (**K4**, **K7**), and a
  direct continuation of the M12 → M13 → M14 application-capability track.
  Its one open area is **K6** (scope + reference-semantics must be bounded
  in the contract phase) — a contract-phase task, not a blocker.

**Result of the comparison:** on the evidence, **C-4 is the strongest
eligible Backend & AI candidate**, with **C-2 the credible alternative** and
FQA / DRS as future candidates pending their own prerequisite decisions.
This is not asserted — it is the pattern the seven criteria produce.

---

## 6. Blocked / Ineligible Work (must NOT become the next Backend & AI milestone)

| Item | Why it must not be M15 | Authoritative source |
|---|---|---|
| **Durable Research Sessions (DRS)** | **BLOCKED.** Requires a prior product/CTO decision **and** a new ADR **and** a new collection *before it can be scoped*. None exists. | Document 58 §10; Document 62 §6 C-4(5) |
| **Filing Q&A as a conversational surface** | Requires a prior CTO/product scope decision (single-turn structured vs. multi-turn conversational). "Filing Analysis → chatbot" is the named top scope-creep risk; Filing Q&A was **deliberately excluded from M14**. | Document 62 R-1, §6 C-1(2); Document 63 §7; Document 65 §27.3 |
| **C-3 Financial Visualization** | Explicitly **"not a Backend & AI milestone"** — a frontend-track initiative. May proceed under frontend governance independently. | Document 58 §9; Document 62 §6 C-3(4)/(8), §13 |
| **C-5 Governance / register hygiene** | **"Not a product milestone."** Governance maintenance, executed via the numbered-amendment / CR chain, not a milestone contract/architecture. | Document 62 §6 C-5(1)/(8) |
| **G8 remediation (any pathway step)** | **BLOCKED.** No CTO authorization for bounded revision, diagnostic experiment, review, evidence, or gate decision. Non-production; out of every candidate's scope. | Document 58 §10; Document 62 §4.2 |
| **`JUDGE_SELF_CONSISTENCY_GATE_VERSION` change past `0`** | Document 47 §19 step-6 hard gate — not cleared; no §9.1 validation authorized. | Document 58 §10; Document 62 §4 |
| **Formal M9 closure / H-1 Run 2 / G7 change** | Standing debt the CTO may separately address; not a milestone, not a dependency of M15 selection. | Document 62 §4; Document 63 §9 |
| **C-2 promoted on the basis of M14's OAQ-1(D) ceilings** | The §20.1 bar **PASSED**. A PASS does not select, trigger, or require C-2 (§2.3; Document 65 §27.2/§27.3). Promoting C-2 to "fix" an *accepted* ceiling would be a reinterpretation of a limitation as a defect — which the evidence does not support. | Document 65 §27.2 (OAQ-1/OAQ-2), §27.3 |

---

## 7. Recommended Next Direction

**On the evidence, a recommendation is supported.**

> **C-4 — "What Changed Since Last Review" is recommended as the next
> Backend & AI direction, subject to formal M15 selection.**

**Basis (each point is evidence, not preference):**

1. **It is a named line in the frozen product Source-of-Truth roadmap**
   (`docs/master-plan/03_Feature_Roadmap.md` → Company Research → "What
   Changed Since Last Review"). C-2 is an enabler/infrastructure item, not a
   standalone named line; C-3 is a frontend-track line; C-5 has no
   user-facing line.
2. **It is free of any governance block and needs no missing prerequisite
   decision to *begin the contract phase*.** DRS is BLOCKED; FQA needs a
   prior product-scope decision; C-2 needs the `08` + ADR chain and a
   probable re-ingest.
3. **It is an eligible Backend & AI milestone** (unlike C-3) with **real
   standalone user value** — retention / repeat engagement (Document 62 §8:
   "Med–High for retention") — and it replaces a manual re-read with a
   grounded delta.
4. **It is the direct continuation of the M12 → M13 → M14
   application-capability track** and a **heavy reuser of hardened
   infrastructure**: `reports`, the M12 `financials` `periods[]` series, the
   M9.1 comparison-explanation diff pattern, and the M14 out-of-graph
   async-job + deterministic-citation pattern — with **no forced new
   persistence** in its minimal form (the M14 fallback-C precedent applies).
5. **It carries no frozen-boundary architectural load** in its expected
   shape: out-of-graph orchestration (M9.1 / M14 precedent), **no LangGraph
   topology change**, no new provider, no new Redis, no forced schema.

**Alternative, if the CTO prefers infrastructure-first:** **C-2 Structured
Filing-Section Extraction** is the credible eligible alternative. It has
lower standalone user value ("navigation, not analysis"), needs a new
schema + the `08` + ADR chain + a probable re-ingest, and likely a
frozen-architecture change — but it would harden the section representation
that every future filing capability (including a better Filing Analysis and
a future Filing Q&A) depends on. Selecting C-2 would be a deliberate
"pay down structural debt now" choice, not a response to any M14 defect.

**This recommendation:**
- **is for the *direction*, not the milestone.** It does **not** say
  "M15 is C-4". No formal M15 selection authorization exists; that is a
  separate, subsequent CTO act (§8).
- **is conditional** on the CTO resolving, in the subsequent contract
  phase, the C-4 reference-semantics question (§4.C-4, §10 OD-2) and the
  "what changed" breadth (§10 OD-3), and confirming C-4 does not introduce
  durable research-session state (§10 OD-4).
- **selects nothing, contracts nothing, architects nothing, authorizes
  nothing.**

---

## 8. Proposed Governance Sequence

Each arrow is a distinct CTO governance act that does **not** confer the
next — the same uncollapsed ladder Documents 62 §13 and 63 §4 define, and
that M14 traversed in full.

```text
M14 CLOSED / PUBLISHED (be4949b, pushed)
        ↓
Post-M14 Backend & AI Roadmap Reconciliation      ← THIS DOCUMENT (67). 🟢 CTO-RATIFIED 2026-09-03 (§14).
        ↓  CTO roadmap ratification  — DONE 2026-09-03 (§14)
          (adopted §1–§6; recorded C-4 as the PREFERRED next Backend & AI DIRECTION;
           the Document 58 §28 disposition and the C-5 hygiene pass remain open — OD-11 / OD-12)
        ↓
Formal M15 milestone-selection record             (a separate CTO act — NOT performed by roadmap ratification;
                                                   C-4 is not "M15" until this step; a new short decision-record artifact)
        ↓  CTO milestone-selection decision
M15 API Contract proposal                          (a new "M15 … API Contract" artifact — NOT created here;
                                                   must resolve reference-semantics, "what changed" breadth,
                                                   on-demand-vs-persisted, citation representation)
        ↓  CTO contract ratification
M15 Architecture Decision Pack                     (a new "M15 … Architecture Decision Pack" — NOT created here;
                                                   data-access, RAG-or-not, LangGraph treatment (expected out-of-graph),
                                                   persistence path, frontend integration, exclusions;
                                                   any LangGraph change is a stop-and-CR item)
        ↓  CTO architecture ratification
Separate M15 implementation authorization          (its own distinct, scope-bound CTO governance act —
                                                   NOT this document, NOT roadmap ratification, NOT contract ratification,
                                                   NOT architecture ratification)
        ↓
engineering implementation
        ↓
technical review (a validation fact — not an authorization)
        ↓
commit authorization  (separate CTO act)   →   push authorization  (separate CTO act)
```

**In parallel, independent of the M15 track:**
- **C-5 governance/register hygiene** (`00_README` index, `11_ADR_Index`,
  `Feature_Parity_Tracker` Phase-4B note, `planning/07-Roadmap-Milestones.md`,
  Document 58 §28) — via `docs/governance/Documentation_Governance.md`'s
  numbered-amendment / CR chain. This document is the Post-M14 half of that
  scope.
- **C-3 Financial Visualization** — under frontend governance; needs no
  artifact from this chain (Document 62 §13).

---

## 9. Explicit Non-Authorization

**Document 67 authorizes nothing.** It does **NOT** authorize, and must not
be read as authorizing:

- M15 implementation, or any implementation;
- an M15 API contract, or any contract;
- an M15 architecture decision pack, or any architecture decision;
- formal M15 milestone selection (a separate, subsequent CTO act);
- MongoDB physical schema realization — no collection, index, migration,
  schema change, or `08_MongoDB_Data_Architecture.md` amendment;
- any change to Redis, LangGraph, retrieval, the provider layer, or the
  frozen research pipeline;
- any frontend implementation;
- any deployment or infrastructure change;
- C-2, C-4, Filing Q&A, or Durable Research Sessions implementation;
- a commit, a push, or any `git` mutation (`add` / `commit` / `push` /
  `reset` / `rebase` / `amend` / `merge`).

CTO **roadmap ratification** of this document would adopt its reconciliation
findings (§1–§6) as the authoritative Post-M14 Backend & AI roadmap
position and may record **C-4 as the preferred next Backend & AI
direction**. It would **not** constitute formal M15 milestone selection,
contract approval, architecture approval, implementation authorization,
commit authorization, or push authorization — each remains a separate,
subsequent CTO governance act (§8).

---

## 10. Open Decisions

Unresolved product / architecture / governance questions that must be
answered **after** this reconciliation is ratified and **before or during**
the corresponding downstream governance phase. This document does not
answer any of them.

| ID | Open decision | Owner / phase | Notes |
|---|---|---|---|
| **OD-1** | **Is the next Backend & AI direction C-4, C-2, or "defer"?** | CTO — roadmap ratification / formal M15 selection | §5/§7 recommend C-4; C-2 is the eligible alternative. The reconciliation supports a recommendation; the selection is the CTO's. |
| **OD-2** | **C-4 reference semantics:** prior research artifact, prior reporting period, explicitly-selected comparison point, or (contra-indicated) user/session state? | CTO / product — before the M15 contract | Material points to artifact / period / explicit-pair and **away from** durable session state (§4.C-4). Not conclusively fixed. **CTO/product decision required.** |
| **OD-3** | **C-4 "what changed" breadth:** financials-only, narrative-only, or both? | CTO / product — M15 contract | Document 62 §6 C-4(6) flags this as the scope-risk that must be bounded. |
| **OD-4** | **Confirm C-4 introduces no durable research-session state** (no new session collection, no per-user history store, no watchlist). | CTO — M15 contract / architecture | Document 62 §6 C-4(8) already excludes these; the contract must restate the boundary so C-4 is not a DRS backdoor (§7). |
| **OD-5** | **C-4 persistence:** on-demand (M14 fallback-C precedent, no new collection) vs. a durable store (triggers `08` + ADR + "no new collection" scrutiny). | CTO — M15 architecture | Same fork M14 faced; the minimal MVP can be on-demand. |
| **OD-6** | **Does C-4 introduce retrieval into a new surface**, or operate whole-input over stored artifacts? | M15 architecture phase | Likely not needed (§4.C-4); an architecture-phase call, not assumed. |
| **OD-7** | **Does C-4 warrant a §20.1-style validation gate** for change-detection quality? | M15 architecture phase | Not assumed here; decide in the architecture pack. |
| **OD-8** | **C-2 status confirmation:** future candidate (this document's finding) vs. parallel infrastructure track vs. re-sequenced ahead of C-4. | CTO — roadmap ratification | §5 finding: future candidate; not a prerequisite (§20.1 passed); not promoted on the basis of M14 ceilings. |
| **OD-9** | **Filing Q&A scope pre-decision:** single-turn structured vs. multi-turn conversational — required before FQA can be a candidate for any milestone. | CTO / product — separate decision | FQA is otherwise a credible *later* milestone (§4.FQA). |
| **OD-10** | **Durable Research Sessions unblock:** issue the product decision + the ADR that Document 58 §10 requires, or keep DRS BLOCKED. | CTO / product — separate decision | DRS remains **BLOCKED / ineligible as M15** until then (§6). |
| **OD-11** | **Document 58 §28 disposition:** complete it as a historical-record ratification, or leave it a permanently unratified historical proposal. | CTO — governance hygiene | Carried unresolved from Document 62 §3.3. |
| **OD-12** | **C-5 hygiene pass authorization and sequencing:** run it before M15, in parallel, or fold the amendments into the M15 governance cycle. | CTO — governance | Includes `00_README` (stale to M7), `planning/07` (pre-M-series), `11_ADR_Index`, `Feature_Parity_Tracker`. Governance maintenance, not a milestone (§6, §8). |
| **OD-13** | **Learning backend build-out** — elevate to a formal Backend & AI candidate, or leave as an unscheduled item. | CTO — roadmap | Mentioned by the Feature Parity Tracker as "a reasonable next milestone"; not in Document 62's pool; not evaluated as a §4 candidate here. |

---

## 11. Evidence Discipline — Conflicts and Discrepancies

Per the reconciliation method (Documents 28 / 44 / 51 / 58 / 62): existing
project documents are the primary authority; terminology is preserved, not
silently corrected; where evidence conflicts, the conflict is named and the
authoritative source identified, or the item is marked unresolved.

| # | Item | Finding |
|---|---|---|
| D-1 | **Push / post-push state.** CTO directive: M14 "passed … commit, push, and post-push verification." | **No conflict.** `git ls-remote origin refs/heads/main` = `be4949b…`; local `origin/main` = `HEAD` = `be4949b`; ahead/behind `0 / 0`. The push occurred outside this task and is corroborated by the remote. Recorded as fact (§2.1). |
| D-2 | **`00_README.md` staleness.** | **Discrepancy (known, C-5 scope).** "Last updated: 2026-08-09"; index stops at Document 29 (M7); header milestone line stops at M6; "Phase 5 next". Does not reflect M8–M14 (Documents 30–66) or this document. Authoritative record of shipped work: the individual milestone documents + Document 62 (CTO-ratified). Classify as **governance maintenance** (§4.C-5, §6, OD-12). **Not corrected here.** |
| D-3 | **`planning/07-Roadmap-Milestones.md` staleness.** | **Discrepancy (known, C-5 scope).** "Living draft · Last updated: 2026-07-12"; Phase/Session model; no M-numbered milestone. Superseded in practice by the Document 17/28/44/51/58/62 reconciliation series. Classify as governance maintenance (OD-12). **Not corrected here.** |
| D-4 | **C-4 name vs. reference semantics.** "What Changed Since Last **Review**" / "since last time" (Document 62 §6 C-4(1)) vs. the same candidate's exclusion of durable sessions / new collection / watchlist (Document 62 §6 C-4(8)). | **Internal tension within one ratified document, not a cross-document conflict.** The exclusion list (§6 C-4(8)) is the more specific, operative text and governs: durable user/session state is **out**. Which of artifact / period / explicit-pair is the intent is **unresolved** → OD-2, **CTO/product decision required**. Not resolved by inventing a design. |
| D-5 | **Feature Parity Tracker "reasonable next milestone" (Learning backend).** | **Not a conflict.** It is an informal aside in a frontend-parity document, not a Backend & AI roadmap decision, and Learning is absent from Document 62's §6 pool. Recorded as OD-13; not admitted as a §4 candidate. |
| D-6 | **Document 58 §28 still `(pending)`.** | **Known open item**, carried from Document 62 §3.3. → OD-11. Not resolved here; Document 58 is not modified. |

No missing roadmap decision is invented. No candidate is admitted on the
basis that it is "technically reasonable" absent a governance slot.

---

## 12. Provenance and Constraints Honoured

- Created: 2026-09-03. Sole new file:
  `docs/backend_engineering/67_Post_M14_Backend_AI_Roadmap_Reconciliation.md`.
  Document number 67 was verified free before creation (highest existing
  Backend & AI governance document was 66). The `backend_engineering/`
  series uses sequential integers; the "Post-M{N} … Roadmap Reconciliation"
  naming matches Documents 58 and 62.
- **No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval / RAG code, MongoDB collection, Redis
  component, provider, configuration, infrastructure, deployment, or
  frontend file was created or modified.** `.gitignore` untouched.
- **Documents 58–66 were read, not modified.** Documents 64 and 65 remain
  🟢 CTO-RATIFIED / FROZEN; Document 66 §18 remains the recorded M14
  implementation authorization; Document 62 remains the CTO-RATIFIED
  Post-M13 position and is cited, not restated as a new interpretation.
- The M14 implementation commit `be4949b` was inspected read-only
  (`show --stat`, `ls-remote`), not altered. **No `git` mutation was
  performed** — no `add` / stage, `commit`, `push`, `amend`, `rebase`,
  `merge`, `reset`, `restore`, `stash`, or `clean`. Nothing was staged.
- Known unrelated working-tree items were **not** touched, staged, modified,
  renamed, deleted, or cleaned:
  `web/features/workspace-home/ui/CompanySearch.test.tsx` (H-2, `M`,
  unstaged) and
  `backend/evaluation/self_consistency/phase_h1_generalization_matrix/`
  (M11 Phase H-1, untracked).
- No date, decision number, or authorization wording was fabricated. No
  retroactive authorization is claimed. This document authorizes nothing;
  it is a decision artifact for CTO review.

---

## 13. Revision History

| Rev | Date | Change |
|---|---|---|
| Draft 1 | 2026-09-03 | Initial Post-M14 Backend & AI Roadmap Reconciliation. Establishes the M14 baseline (delivered `be4949b`, pushed, remote-corroborated; Documents 64/65 authoritative; §20.1 PASS; accepted ceilings recorded, not reinterpreted as defects; no MongoDB schema realization; no universal section-detection claim). Reconciles the candidate pool (C-2, C-3, C-4, C-5, Filing Q&A, Durable Research Sessions; adjacent items noted, not admitted). Determines: C-2 = **future candidate** (not a prerequisite — §20.1 passed; not promoted on M14 ceilings); C-3 = **frontend-track, ineligible** as a Backend & AI milestone; C-5 = **governance maintenance / parallel work**; Filing Q&A = **future candidate gated on a prior product decision**; Durable Research Sessions = **BLOCKED / ineligible**. Cross-candidate comparison on seven explicit criteria. **Recommendation: C-4 "What Changed Since Last Review" as the next Backend & AI direction, subject to formal M15 selection** — not "M15 is C-4"; C-2 the eligible alternative. C-4 reference-semantics marked **CTO/product decision required** (OD-2), not resolved by design. Governance sequence and non-authorization stated. Discrepancies D-1…D-6 recorded (notably `00_README` / `planning/07` staleness — C-5 scope, not corrected here). **Status: 🟡 PROPOSED — CTO DECISION REQUIRED.** |
| Ratified | 2026-09-03 | **CTO ratification recorded in §14** (same session; §0–§13 unchanged in substance). Status transition `🟡 PROPOSED — CTO DECISION REQUIRED` → `🟢 CTO-RATIFIED (2026-09-03) — AUTHORITATIVE POST-M14 BACKEND & AI ROADMAP POSITION`. The CTO adopts §1–§6: the M14 `be4949b` completed/published baseline, M14's delivered capability boundary and accepted architectural ceilings, the reconciled candidate pool, the C-2 / C-3 / C-5 classifications, the separate treatment of Filing Q&A, the BLOCKED status of Durable Research Sessions, **C-4 as the strongest / recommended next Backend & AI direction**, the unresolved C-4 reference-semantics questions, and the proposed governance sequence. **Ratification is NOT formal M15 selection** — C-4 remains the recommended direction / candidate and does not become M15 through this ratification; formal M15 selection is a separate, subsequent CTO governance decision (§14). Ratification authorizes no M15 implementation, no C-4 implementation, no M15 contract, no M15 architecture, no MongoDB schema realization, no Redis / LangGraph / frontend change, no implementation authorization, and no commit / push / merge / deployment. Recording the ratification changed only this document in the working tree; nothing staged, committed, or pushed. |

---

## 14. CTO Ratification (2026-09-03)

Recorded from the CTO's ratification decision of 2026-09-03. **§0–§13 above
are unchanged in substance;** this section records the decision and the
status transition (`🟡 PROPOSED — CTO DECISION REQUIRED` →
`🟢 CTO-RATIFIED (2026-09-03) — AUTHORITATIVE POST-M14 BACKEND & AI ROADMAP
POSITION`). Doc 67 completed CTO substantive review and was determined
**🟢 APPROVED FOR RATIFICATION — NO REVISIONS REQUIRED**.

### 14.1 Decision

**🟢 DOC 67 — CTO RATIFIED.** The CTO formally accepts the findings and
reconciliation contained in Document 67 as the authoritative Post-M14
Backend & AI roadmap position.

### 14.2 What the ratification accepts

Recorded from the decision:

- **M14 `be4949b`** (`be4949b5b33ea73cfedf81c03bebbdaa953772b8`) as the
  **completed / published** baseline (§2.1) — committed and pushed;
  `HEAD` = `origin/main` = true remote, `0 / 0`.
- **M14's delivered capability boundary** (§2.2, §2.4): the frozen
  Document 64 four-output contract (Filing Summary, Risk Factors Digest,
  MD&A Digest, Important Changes; no selection parameter; flat cited
  narratives; INV-IC), the ratified Document 65 architecture, the four
  additive routes (inventory 43 → 47), and the fourth async out-of-graph
  LLM surface with the frozen research LangGraph unchanged.
- **M14's accepted architectural ceilings** (§2.3) — **as ceilings, not
  defects**: the §20.1 bounded OAQ-1(D) validation **PASSED** (0 false
  positives / 0 false negatives on the validated corpus; byte-identical
  over N=5 per validated filing); the §20.1 corpus is bounded and the check
  is deterministic, **not** a universal section-detection claim; the one
  MSFT-10-K MD&A partial-boundary case is an honest `partial`, not a
  failure; **fallback-C persistence is process-local** (no
  `filing_analyses` / `filing_analysis_jobs` collection; `reused` always
  `false`); **MongoDB physical schema realization was not part of M14**;
  C-2 remains **neither selected nor rejected**; Filing Q&A remains
  **excluded from M14**.
- **The reconciled candidate pool** (§3): C-2, C-3, C-4, C-5, Filing Q&A,
  Durable Research Sessions — no candidate invented; adjacent items noted,
  not admitted.
- **The classification of C-2** — **FUTURE CANDIDATE.** Not a prerequisite
  (the §20.1 bar **passed**; a PASS does not select, trigger, or require
  C-2). **Not promoted on the basis of M14's accepted OAQ-1(D) ceilings.**
  The credible eligible infrastructure-first alternative to C-4 if the CTO
  prefers to pay down structural debt first (§5, §7).
- **The classification of C-3** — **INELIGIBLE as the next Backend & AI
  milestone; a frontend-track initiative** that may proceed under frontend
  governance independently (Document 58 §9; Document 62 §6 C-3).
- **The classification of C-5** — **GOVERNANCE MAINTENANCE / PARALLEL WORK,
  not a Backend & AI milestone**, executed via the numbered-amendment / CR
  chain. Doc 67 is itself the Post-M14 half of that scope. The recorded
  discrepancies (`00_README.md` stale to M7; `planning/07-Roadmap-Milestones.md`
  a pre-M-series draft; Document 58 §28 still `(pending)`) are C-5 scope
  and were **not** corrected in Doc 67.
- **The separate treatment of Filing Q&A** — a **FUTURE CANDIDATE gated on
  a prior CTO / product scope decision** (single-turn structured vs.
  multi-turn conversational). It never entered Document 62 §6 as a formal
  candidate and remains excluded from M14.
- **The BLOCKED status of Durable Research Sessions** — **INELIGIBLE as
  M15** until the CTO issues the product decision **and** the ADR **and**
  authorizes the new collection that Document 58 §10 requires. Doc 67's C-4
  treatment is **not** a backdoor for durable research-session state
  (§4.C-4, §7, OD-4).
- **C-4 "What Changed Since Last Review" as the strongest / recommended
  next Backend & AI direction** (§5, §7), subject to formal M15 selection.
- **The unresolved C-4 reference-semantics questions** — which of {prior
  research artifact / prior reporting period / explicitly-selected
  comparison point} is the product intent is **NOT resolved**; the material
  points **away from** durable user/session state but does not fix the
  choice. Recorded as **CTO / product decision required** (§4.C-4, OD-2),
  to be answered in the subsequent contract phase — **not** by inventing a
  design.
- **The proposed governance sequence** (§8) and its uncollapsed gates.

### 14.3 Critical governance distinction — ratification is NOT M15 selection

**Doc 67 ratification does not constitute formal M15 selection.**

- **C-4 remains the recommended candidate / direction.** It does **not**
  become M15 through this ratification alone.
- **Formal M15 selection remains a separate CTO governance decision** — its
  own distinct, scope-bound act, subsequent to this ratification (§8; the
  same un-folded step Document 63 performed for M14 after Document 62's
  ratification).
- The project's terminology distinction is preserved:
  **candidate** → **recommended direction** (C-4 is here now) →
  **selected milestone** (a separate CTO act — not done) →
  **implementation-authorized milestone** (a further separate CTO act —
  not done).

### 14.4 Explicit non-authorization

This ratification does **NOT** authorize, and must not be read as
authorizing:

- M15 implementation, or any implementation;
- C-4 implementation;
- creation of an M15 API contract;
- creation of an M15 architecture decision pack / document;
- MongoDB schema realization — no collection, index, migration, schema
  change, or `08_MongoDB_Data_Architecture.md` amendment;
- any Redis change;
- any LangGraph implementation or topology change;
- any frontend implementation;
- a separate implementation-authorization decision;
- a commit, a push, a merge, or any `git` mutation;
- any deployment or infrastructure change.

### 14.5 Governance sequence (next steps — no gate skipped or collapsed)

```text
M14 CLOSED
    ↓
Doc 67 CTO RATIFIED                     ← THIS SECTION (§14). AUTHORITATIVE POST-M14 ROADMAP POSITION.
    ↓
Formal M15 Selection                    (a separate, scope-bound CTO governance decision — NOT performed here;
                                        C-4 is not "M15" until this step; a new short milestone-selection record)
    ↓
M15 Contract                            (a new "M15 … API Contract" artifact — NOT created here;
                                        resolves reference-semantics (OD-2), "what changed" breadth (OD-3),
                                        on-demand-vs-persisted (OD-5), citation representation)
    ↓
M15 Architecture                        (a new "M15 … Architecture Decision Pack" — NOT created here;
                                        data-access, RAG-or-not, LangGraph treatment (expected out-of-graph),
                                        persistence path, frontend integration, exclusions)
    ↓
Implementation Authorization            (its own distinct, scope-bound CTO governance act)
    ↓
engineering implementation → technical review → commit authorization → push authorization
```

**In parallel, independent of the M15 track:** the C-5 governance/register
hygiene pass (Open Decision OD-12) and C-3 Financial Visualization (frontend
governance track) — neither requires an artifact from the M15 chain.

### 14.6 Recording note

This section records a decision already issued by the CTO; it creates no
authorization of its own. Adding it, flipping the status header, and adding
the §13 "Ratified" row changed **only this document, in the working tree** —
nothing was staged, committed, or pushed, and no source, test, schema,
route, LangGraph, MongoDB, Redis, frontend, or configuration file was
touched. Committing Document 67 to version control is a separate,
subsequently CTO-authorized step (the model Documents 61 `f1c18c3` and the
M14 chain `be4949b` followed). The known unrelated working-tree items
(`web/features/workspace-home/ui/CompanySearch.test.tsx`;
`backend/evaluation/self_consistency/phase_h1_generalization_matrix/`) were
not touched.

---

**NO IMPLEMENTATION PERFORMED. NO SOURCE, TEST, SCHEMA, INDEX, MIGRATION,
ROUTE, HANDLER, LANGGRAPH NODE, PROMPT, RETRIEVAL / RAG, MONGODB COLLECTION,
REDIS, PROVIDER, CONFIGURATION, INFRASTRUCTURE, DEPLOYMENT, OR FRONTEND FILE
CREATED OR MODIFIED. `.gitignore` UNTOUCHED. DOCUMENTS 58–66 READ, NOT
MODIFIED. DOCUMENTS 64 / 65 REMAIN 🟢 CTO-RATIFIED / FROZEN. THE M14 COMMIT
`be4949b` NOT ALTERED. THIS DOCUMENT IS 🟢 CTO-RATIFIED (2026-09-03) AS THE
AUTHORITATIVE POST-M14 BACKEND & AI ROADMAP POSITION (§14). RATIFICATION
DOES NOT FORMALLY SELECT M15, DOES NOT CREATE AN M15 CONTRACT OR
ARCHITECTURE PACK, AND GRANTS NO IMPLEMENTATION, C-4 IMPLEMENTATION,
IMPLEMENTATION AUTHORIZATION, MONGODB SCHEMA REALIZATION, REDIS / LANGGRAPH
/ FRONTEND CHANGE, DEPLOYMENT, COMMIT, PUSH, OR MERGE AUTHORIZATION. C-4 IS
THE RATIFIED RECOMMENDED NEXT BACKEND & AI DIRECTION — NOT M15; FORMAL M15
SELECTION IS A SEPARATE, SUBSEQUENT CTO DECISION. C-2 REMAINS NEITHER
SELECTED NOR REJECTED AND IS NOT PROMOTED ON THE BASIS OF M14'S ACCEPTED
OAQ-1(D) CEILINGS; THE §20.1 BAR PASSED AND THAT GOVERNANCE FACT IS
PRESERVED. DURABLE RESEARCH SESSIONS REMAINS BLOCKED. FILING Q&A REMAINS
EXCLUDED FROM M14 AND GATED ON A PRIOR PRODUCT DECISION. C-3 IS A
FRONTEND-TRACK INITIATIVE, NOT A BACKEND & AI MILESTONE. C-5 IS GOVERNANCE
MAINTENANCE, NOT A MILESTONE. NO STAGE. NO COMMIT. NO PUSH. NO MERGE /
REBASE / RESET / AMEND. THE NEXT GOVERNANCE ACT IS A SEPARATE CTO DECISION
ON FORMAL M15 MILESTONE SELECTION (§8, §14.5).**
