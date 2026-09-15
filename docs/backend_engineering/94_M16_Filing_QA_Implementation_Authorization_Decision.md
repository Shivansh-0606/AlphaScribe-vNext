# 94 — M16 Implementation Authorization Decision — Filing Q&A (FQA v1)

**Revision:** 🟡 **REVISION 1** — a narrow, targeted correction of §6, §9,
§16, §18, and the cross-referencing metadata below, following CTO review
that found the **original, unrevised text of this document BLOCKED**
because §9 faithfully restated Document 90 §5's `stride = ceil(N/K)`
candidate-selection algorithm, which
[Document 95](95_D90_Candidate_Selection_Architecture_Amendment_Decision.md)
proved mathematically incapable of guaranteeing last-chunk coverage for
all valid `(N, K)` pairs, and which
[Document 96](96_Document95_Candidate_Selection_Architecture_Amendment_Ratification_Record.md)
has since formally, ratifiedly corrected. **This revision aligns this
document's candidate-selection requirements with the Document 95/96-
ratified algorithm and nothing else** — no other requirement in this
document is redesigned, reinterpreted, or extended by this revision (see
the Revision 1 Note below and §9).

**Status:** 🟡 **PROPOSED M16 IMPLEMENTATION AUTHORIZATION DECISION —
DRAFT / PENDING CTO REVIEW. NOT YET RATIFIED. THIS REVISION HAS NOT ITSELF
BEEN REVIEWED AND REQUIRES A FRESH CTO REVIEW** — the BLOCKED verdict
against the original text does not carry forward as an approval of this
corrected text, and this document does not claim to have already passed
review. This document proposes the terms under which implementation of
M16 = Filing Q&A (FQA v1) **would** be authorized against the
already-ratified API contract
([Document 87 Revision 2](87_M16_Filing_QA_API_Contract_Proposal.md),
ratified through
[Document 88](88_Document87_CTO_Ratification_Record.md) /
[Document 89](89_Document88_CTO_Ratification_Record.md) /
[Document 92](92_Document89_CTO_Ratification_Record.md)) and the
already-ratified architecture
([Document 90](90_M16_Filing_QA_Architecture_Decision_Pack.md), ratified
through
[Document 91](91_Document90_Architecture_Ratification_Record.md) /
[Document 93](93_Document91_CTO_Ratification_Record.md), **and, for its
candidate-selection mechanism only, as amended by
[Document 95](95_D90_Candidate_Selection_Architecture_Amendment_Decision.md)
/ [Document 96](96_Document95_Candidate_Selection_Architecture_Amendment_Ratification_Record.md)**).
**Creating or revising this document does NOT authorize implementation.**
It remains a proposal, submitted for a fresh CTO review; a separate,
subsequent CTO **ratification** of this document (this revision) is
required before any implementation work may begin (§17, §19).

**Type:** Governance / implementation-authorization proposal
(documentation only — no source code, test, schema, migration, index,
route, LangGraph node, MongoDB collection, Redis usage, configuration, or
frontend file created or modified to produce it; Documents 63–96 read,
none modified — this revision touches only this document. The only file
this task modifies is this document; no file is created.

**Date:** 2026-09-12 (original). **Revision 1 recorded:** 2026-09-12
(same-day correction pass following CTO review of the original text).

**Revision 1 Note (this revision, in full — nothing else in this
document is changed):**

1. §6 item 1's cross-reference wording ("stride-selection capping") is
   corrected to remove the obsolete algorithm's name.
2. §9 ("Deterministic Retrieval / Candidate Requirements") — the
   `stride = ceil(N/K)` / conditional-highest-chunk-append algorithm is
   replaced with the exact Document 95/96-ratified formula (§9 below).
3. §16 ("Explicit Exclusions") — Documents 95 and 96 are added to the
   list of governance documents this authorization must not reopen or
   reinterpret.
4. §18 ("Implementation Completion Criteria") — the candidate-curation
   testing-floor bullet is expanded to enumerate the specific
   `(N, K)` regression cases and properties Document 95/96 require, and
   its candidate-**count** wording is corrected (item 6 below).
5. The cross-references in this banner, §2, and §3 are updated so it is
   clear the candidate-selection requirement is now governed by
   **Document 90 as amended by Documents 95/96** — not by treating
   Documents 95/96 as having changed any other part of Document 90.
6. **(CTO-review correction, same revision)** §18's candidate-count
   wording ("bounded at exactly `MAX_CANDIDATE_CHUNKS`") contradicted the
   `N ≤ K` branch's own "select every chunk" requirement whenever
   `N < K`. Corrected to the precise invariant: candidate count never
   exceeds `K`; `N > K` selects exactly `K`; `N ≤ K` selects exactly `N`
   (every chunk). No change to the ratified algorithm itself.
7. **(CTO-review correction, same revision)** §7's `MAX_CANDIDATE_CHUNKS
   ≥ 2` requirement did not identify *where* that precondition is
   enforced. §7 is corrected to identify the existing enforcement
   boundary (a plain, unvalidated module-level constant, per the
   `agents/filing_analysis.py` precedent — verified read-only this
   session) and to authorize the minimum validation necessary there — no
   new configuration surface, no default change, no broadened file
   boundary. §9's cross-reference is updated to match.
8. **(CTO re-review correction, same revision)** §7 permitted the
   `K ≥ 2` guard to be satisfied by "e.g., an assertion," which is not
   acceptable for a hard invariant — a Python `assert` is compiled out
   entirely under `-O`/`-OO`/`PYTHONOPTIMIZE`. §7 is corrected to
   require an **unconditional, non-`assert`-based import-time guard**,
   placed immediately after the `MAX_CANDIDATE_CHUNKS` definition in
   `backend/agents/filing_qa.py`, rejecting `K < 2` before any request
   can reach the `N > K` branch. §7's wording is also tightened to
   distinguish the **existing configuration precedent**
   (`agents/filing_analysis.py`, unvalidated) from the **authorized FQA
   enforcement site** (the not-yet-existing `MAX_CANDIDATE_CHUNKS`
   definition in `agents/filing_qa.py`) so that this document does not
   imply FQA validation already exists. §9's cross-reference is updated
   to match.

**No other requirement, boundary, table row, or sentence in this document
is altered by this revision.** Every other section (§1, §4, §5, §8,
§10–§15, §17, §19 except the note added there, §20) is preserved exactly
as originally written, per this revision's narrow scope. (§7 and §18 are
corrected as items 6–8 above record; §9 receives only the matching
cross-reference updates.)

**Precedent / lineage.** This document follows the same proposal-then-
ratification pattern already established for every prior milestone in
this chain — Document 66 (M14), Document 75 (M15) — one governance step
further down the M16 ladder than Documents 90/91/93 already closed: an
**implementation-authorization proposal**, preceding its own future,
separate ratification. This revision follows the same targeted-
correction-then-fresh-review pattern Document 73's own Revision R1
established (a proposal revised once, in place, following CTO review,
without a new document number). It does not redesign or reinterpret
Document 87 R2, Document 90, Document 95, Document 96, or any of the
ratification records (Documents 88 / 89 / 92 / 91 / 93) — it is bounded
strictly to realigning this document's candidate-selection requirements
with the now-ratified amendment.

---

## 1. Purpose

M16 = Filing Q&A (FQA v1) has cleared every governance gate up to and
including architecture ratification: scope (Documents 83 / 85), milestone
selection (Documents 84 / 86), API contract (Document 87 R2, ratified
through Documents 88 / 89 / 92), and architecture (Document 90, ratified
through Documents 91 / 93). **No implementation authorization exists
yet.** This document exists to propose exactly one thing: the bounded set
of concrete engineering work that would be authorized, strictly within
the already-ratified contract and architecture, **if and only if** this
proposal is itself separately reviewed and ratified by the CTO.

This document:

- defines the exact implementation boundary — the concrete files/modules
  that need changes, and nothing broader (§5–§8);
- restates, without weakening, every D90 invariant implementation must
  preserve (§9–§10);
- states explicitly what remains unauthorized regardless of ratification
  — commit, push, deployment, DRS, new architecture, and more (§16);
- states explicitly that **implementation authorization ≠ commit
  authorization ≠ push authorization ≠ deployment authorization** (§17);
- does **not** create new product scope, does **not** modify the API
  contract or the architecture, and does **not** reopen Documents 83–93
  (§2, §16).

---

## 2. Governance Prerequisites (verified this session, read-only)

| Fact | Source | Verified state |
|---|---|---|
| FQA v1 scope | Documents 83 / 85 | 🟢 CTO-RATIFIED — single-turn, stateless w.r.t. durable conversational/research state, single-filing, `(ticker, doc_id)` identity, no cross-filing/corpus/portfolio research, DRS outside M16 |
| M16 milestone selection | Documents 84 / 86 | 🟢 CTO-RATIFIED — M16 = Filing Q&A (FQA v1) |
| API contract | Document 87 Revision 2, via Documents 88 / 89 / 92 | 🟢 **RATIFIED** — Document 92's own status banner reads *"🟢 DOCUMENT 89 — CTO RATIFIED / ACCEPTED... DOCUMENT 88 FORMALLY RATIFIED THROUGH DOCUMENT 89... DOCUMENT 87 REVISION 2 IS THE RATIFIED M16 API CONTRACT."* Re-read this session, unchanged. |
| Architecture | Document 90, via Documents 91 / 93 | 🟢 **RATIFIED** — Document 93's own status banner reads *"🟢 DOCUMENT 91 — CTO RATIFIED... DOCUMENT 90 — M16 ARCHITECTURE DECISION PACK — FILING Q&A (FQA v1) IS THEREFORE FORMALLY, FULLY ARCHITECTURE-RATIFIED."* Re-read this session, unchanged. |
| Candidate-selection amendment | Document 95, via Document 96 | 🟢 **RATIFIED** — Document 96's own status banner reads *"🟢 DOCUMENT 95 — CTO RATIFIED / ACCEPTED. THE M16 FILING Q&A (FQA v1) CANDIDATE-SELECTION ARCHITECTURE IS AMENDED AS DOCUMENT 95 SPECIFIES."* Re-read this session. Amends **only** Document 90 §5's `N > K` selection algorithm (§9 below) — no other Document 90 decision. |
| Implementation authorization | none prior | **NONE proposed or ratified before this document.** This document (this revision) is the implementation-authorization **proposal** — not yet reviewed, not ratified. The prior, unrevised text of this document was CTO-reviewed and found **BLOCKED** on the candidate-selection defect Document 95/96 now correct; that review does not carry forward as approval of this revised text, which requires its own fresh CTO review. |

No governance state above is changed by this document. It is cited, not
re-decided. The only question genuinely open at this stage of the ladder
is the one this document proposes an answer to: whether implementation
may now proceed within the already-fixed contract and architecture, and
exactly what that implementation may touch.

---

## 3. Authoritative Contract and Architecture References

**Frozen inputs this document does not reinterpret, weaken, or extend:**

| Input | Role |
|---|---|
| [Document 87 Revision 2](87_M16_Filing_QA_API_Contract_Proposal.md) | The externally observable request/response, citation, error, state, job, and SSE semantics for FQA v1. Ratified (§2). |
| [Document 90](90_M16_Filing_QA_Architecture_Decision_Pack.md) | The implementation architecture realizing that contract — retrieval, evidence representation, `JobKind` realization, transient retention (AH-2), generation, citation validation, model/BYOK, output bounding, evaluation requirement, security, observability, performance, failure/retry, M14/M15 reuse, testing architecture, deployment. Ratified (§2). **As amended below**, for its candidate-selection mechanism only. |
| [Document 95](95_D90_Candidate_Selection_Architecture_Amendment_Decision.md) / [Document 96](96_Document95_Candidate_Selection_Architecture_Amendment_Ratification_Record.md) | The narrow, ratified amendment to Document 90 §5's candidate-selection algorithm (§9 below) — the **only** part of Document 90 they touch. Ratified (§2). |
| [Document 65](65_M14_Filing_Analysis_Architecture_Decision_Pack.md) | Cited by Document 90 as direct structural precedent (OAQ-1 section location, OAQ-3 retrieval reuse, OAQ-9 deterministic anchor discovery, fallback-C retention). |
| [Document 73 Revision R1](73_M15_Architecture_Decision_Pack.md) | Cited by Document 90 for AH-1/AH-2 handling and zero-new-error-class discipline, reused here. |

**This document authorizes implementation strictly within these
documents' already-fixed boundaries — Document 90 as amended by
Documents 95/96 for candidate-selection, and otherwise exactly as
originally ratified.** Any implementation detail not already fixed by
Document 87 R2 or Document 90 (as amended) remains an ordinary
engineering decision made *during* implementation, not a new governance
grant made here. **Documents 95/96 are authoritative only for the
candidate-selection amendment named above — this document does not treat
them as having changed, or as license to reinterpret, any other Document
90 decision.**

---

## 4. Implementation Scope

**If ratified, this decision would authorize implementation only for:**

**M16 — Filing Q&A (FQA v1)**, and **only** within the boundaries already
fixed by Document 87 R2 (contract) and Document 90 (architecture):

- the four-route async `qa` family under
  `/api/companies/{ticker}/filings/{doc_id}/qa`;
- the `agents/filing_qa.py` module Document 90 §4.2/§6/§10/§11 specifies;
- the one additive `JobKind.FILING_QA` enum member (Document 90 §7);
- the operational-configuration set Document 90 §9/§13/§21 names;
- the one additive `filing_qa_runs_total{outcome}` metrics counter
  (Document 90 §16);
- the corresponding hermetic unit tests, contract tests, and one additive
  `backend_test_iterN.py` live-HTTP suite (Document 90 §20; §8, §14
  below).

**Not in scope, at any point in this document:** any capability outside
the single-turn, stateless, single-filing FQA v1 boundary — no
conversational continuation, no durable research state, no cross-filing
research, no corpus synthesis, no portfolio research (Documents 83/85,
carried forward unchanged by Document 90 §2 and this document).

---

## 5. Concrete Authorized File/Module Boundary (repository-inspected)

**Verified this session by direct inspection** (not assumed) of the
current M14/M15 infrastructure Document 90 requires reusing. The
following is the **complete, exhaustive** list of files this decision
would authorize creating or modifying. **No file outside this list is
authorized, regardless of how reasonable a related change might seem.**

### 5.1 New files (create)

| Path | Purpose | Modeled on |
|---|---|---|
| `backend/agents/filing_qa.py` | Pure module: candidate curation (`build_candidates`/equivalent), generation (`generate_answer`), deterministic citation validator (`resolve_and_validate`), orchestrator (`answer_question`) — Document 90 §4.2, §5–§11 | `backend/agents/filing_analysis.py` (492 lines, read in full this session) — same structural shape: module docstring stating the frozen contract/architecture it realizes, `PROMPT_VERSION`/`SCHEMA_VERSION` constants, a module-internal marker exception, numbered-candidate curation, one `chat_json` generation call, a deterministic `resolve_and_validate` |
| `backend/tests/unit/test_filing_qa.py` | Hermetic pure-function unit tests, fake `chat_fn`, no DB/network | `backend/tests/unit/test_filing_analysis.py` (exists) |
| `backend/tests/unit/test_filing_qa_endpoint.py` | Hermetic fake-Mongo + real ASGI contract tests for the four routes | `backend/tests/unit/test_filing_analysis_endpoint.py` (exists) |
| `backend/tests/unit/test_filing_qa_result_buffer.py` | AH-2 buffer-specific unit tests: owner-scoped read, TTL expiry, oldest-first eviction, pop-on-cancel/failure | `backend/tests/unit/test_change_brief_result_buffer.py` (exists — direct AH-2 precedent) |
| `backend/tests/backend_test_iterN.py` (next free number — **`iter8`** at the time of this proposal; verify free again at implementation time, per the project's own additive-suite convention) | Additive live-HTTP suite against a running server | `backend/tests/backend_test_iter7.py` (highest existing at the time of this proposal) |

### 5.2 Existing files (modify — additive edits only, named exactly)

| Path | Exact change authorized |
|---|---|
| `backend/domain/models.py` | Add **one** additive `JobKind` member: `FILING_QA = "filing_qa"` — mirroring the existing `FILING_ANALYSIS`/`CHANGE_BRIEF` lines (currently lines 20–25). No other change to this file. |
| `backend/app/settings.py` | Add **one** additive field `job_deadline_filing_qa_s: float = Field(default=120.0, validation_alias="JOB_DEADLINE_FILING_QA_S")` (mirroring the existing `job_deadline_change_brief_s` pattern, currently lines 60–71) and **one** additive entry `"filing_qa": self.job_deadline_filing_qa_s` in the `job_deadline_s` property (currently lines 130–138). Add the `fqa_*` operational-config fields Document 90 §13 names (`FQA_MAX_QUESTION_CHARS`, `FQA_MAX_ANSWER_CHARS`, `FQA_MAX_SOURCES`, optional `FQA_RATE_LIMIT`) as additive `Settings` fields with recommended defaults, same pattern. No other change to this file. |
| `backend/server.py` | Additive only, mirroring the existing `# M14 — Filing Analysis` block (currently lines 2280–2544) and the `# M15 — C-4` block (currently lines 2547 onward) verbatim in shape: one `FilingQARequest` BaseModel (BYOK fields + `question: str`); one `_FILING_QA_RESULTS: dict[str, tuple[str, dict, float]]` buffer + `_store_filing_qa_result`/`_get_filing_qa_result` + a `_FQA_MAX_ENTRIES` cap (mirroring `_FILING_ANALYSIS_RESULTS` at lines 2303–2332); one `_run_filing_qa(...)` job-wrapper coroutine (mirroring `_run_filing_analysis` at lines 2345–2438); one `_filing_qa_stream_events(...)` async generator (mirroring `_filing_analysis_stream_events` at lines 2506–2516); and exactly **four** new routes: `POST /companies/{ticker}/filings/{doc_id}/qa`, `GET .../qa/{id}`, `GET .../qa/{id}/stream`, `POST .../qa/{id}/cancel` (mirroring lines 2441–2544). **No existing route, function, or class in `server.py` is modified.** |
| `backend/infrastructure/observability/metrics.py` | Add **one** additive `Counter`, `filing_qa_runs_total`, `alphascribe_filing_qa_runs_total`, `{outcome}` label — mirroring `filing_analysis_runs_total` / `change_brief_runs_total` (currently lines 133–145). No other change to this file. |
| `backend/tests/contract/test_route_inventory.py` | Add **exactly four** new `(METHOD, path)` tuples to the literal `APPROVED_ROUTES` set (currently a 51-member set starting at line 69) for the four FQA routes named above, and change the assertion `assert len(APPROVED_ROUTES) == 51` (currently line 154) to `== 55`. Update the module docstring's "PLUS N routes" narrative with one additional clause for the M16/FQA addition, in the same style as the existing M12/M13 clauses. **No existing entry in `APPROVED_ROUTES` is removed or altered.** |

### 5.3 Explicitly NOT authorized to touch

`backend/agents/filing_analysis.py`, `backend/agents/change_brief_financial.py`,
`backend/agents/change_brief_narrative.py`, `backend/agents/comparison_explanation.py`,
`backend/agents/retrieval.py`, `backend/agents/llm.py`, `backend/agents/scoring.py`,
`backend/domain/errors.py`, `backend/application/jobs.py`,
`backend/infrastructure/security/authorization.py`,
`backend/infrastructure/streaming/sse.py`, any file under
`backend/infrastructure/mongo/` or `backend/infrastructure/redis/`, any
frontend file, `docs/backend_engineering/20_M6_Metrics_Catalog.md`
(Document 90 §16 already defers this edit as a separate documentation
task), `docs/backend_engineering/08_MongoDB_Data_Architecture.md`, and
`pytest.ini`. **Reuse of all of these is authorized (§6); modification of
any of them is not**, per Document 90 §4.1/§19's explicit "no change"
list, verified against the actual current file contents this session, not
assumed.

---

## 6. Permitted Source Changes

**If ratified, source-code implementation is authorized strictly to:**

1. create `backend/agents/filing_qa.py` implementing, exactly as
   Document 90 (as amended by Documents 95/96) specifies and nothing
   more:
   - the deterministic ordered-candidate-universe capping, per the
     Document 95/96-ratified algorithm (§9 below);
   - the at-most-one-generation orchestrator (§10 below);
   - the deterministic citation-structure validator (§10 below);
2. add the one additive `JobKind.FILING_QA` member to
   `backend/domain/models.py` (§5.2);
3. add the FQA operational-config fields to `backend/app/settings.py`
   (§5.2, §7);
4. add the `FilingQARequest` model, the `_FILING_QA_RESULTS` buffer, the
   `_run_filing_qa` job wrapper, the `_filing_qa_stream_events` generator,
   and the four routes to `backend/server.py` (§5.2, §11), reusing
   `container.job_lifecycle`, `RUNNING_TASKS`, `sse_response`,
   `require_admin`, `assert_public_url`, `_load_ordered_filing_chunks`,
   `db.filings.find_one`, and `agents.retrieval.retrieve` **unmodified**,
   exactly as `_run_filing_analysis` already does;
5. add the one additive `filing_qa_runs_total` counter to
   `backend/infrastructure/observability/metrics.py` (§5.2, §13).

**No other source file is authorized to change.** Reuse of every other
existing module named in §5.3 is authorized **only as an unmodified
import/call** — never as a target of edits.

---

## 7. Permitted Configuration Changes

**Only additive configuration directly required by M16 is authorized —
no unrelated operational default may be altered:**

- `MAX_CANDIDATE_CHUNKS` (the candidate-cap `K` used by §9's amended
  selection algorithm) is **not a new configuration surface, and this
  decision does not authorize creating one.** Two distinct things must
  not be conflated:

  - **The existing configuration precedent** — verified this session by
    direct, read-only inspection: `backend/agents/filing_analysis.py`'s
    `MAX_CANDIDATE_CHUNKS = 60` (line 63) is a plain **module-level
    Python constant**, not a `Settings`/`pydantic` field, not
    environment-configurable, and carrying **no runtime validation of
    its value today** (confirmed: no `field_validator`, no `assert`, no
    startup check exists anywhere in the repository for it — a literal
    integer, nothing more). This precedent establishes *the kind of
    site* — a module-level constant, not a `Settings` field — but it is
    filing-analysis-specific, does not itself validate anything, and
    **this decision does not claim FQA validation already exists
    because of it.**
  - **The authorized FQA enforcement site** — a `MAX_CANDIDATE_CHUNKS`
    constant `agents/filing_qa.py` (§5.1, already authorized; the file
    does not exist yet) is expected to define, at the same kind of site
    as the precedent above. **This is where the `K ≥ 2` guard required
    below must be authored** — it does not exist until implementation
    creates it; this decision authorizes creating it there and nowhere
    else.

  Because no existing validation rejects `K < 2` today (per the
  precedent above), and the Document 95/96-ratified algorithm makes
  `K ≥ 2` a hard mathematical precondition (§9), **this decision
  authorizes, and requires, the minimum validation necessary at that one
  site** — subject to the following explicit constraints:

  - the guard must be an **unconditional import-time validation
    guard** — it must execute every time the module is imported, with
    no condition (debug flag, environment check, or otherwise) able to
    skip it;
  - it must be placed **immediately following the `MAX_CANDIDATE_CHUNKS`
    definition in `backend/agents/filing_qa.py`**;
  - it must **reject `K < 2`** — the misconfiguration must be caught at
    definition/import time, **before any request can reach the `N > K`
    branch** (§9);
  - **it must NOT rely on Python `assert` semantics or any construct
    whose execution can be disabled under an optimized execution mode**
    (`assert` statements are compiled out entirely when Python runs with
    `-O`/`-OO` or `PYTHONOPTIMIZE` set, which would silently remove this
    guard in that mode — unacceptable for a hard invariant). A plain
    unconditional conditional-and-raise (for example, `if K < 2: raise
    ValueError(...)` immediately after the constant's definition, or
    any other construct with the same unconditional, non-optimizable
    property) satisfies this; an `assert K >= 2` statement does not, and
    is not authorized as sufficient on its own.

  **This authorizes only that one guard, at that one already-authorized
  file (§5.1) — it does NOT authorize**: a new `Settings` field; a new
  environment variable; any change to `MAX_CANDIDATE_CHUNKS`'s
  recommended default (Document 90's `≈ 60`, which already satisfies
  `K ≥ 2` by a wide margin, is unchanged); or any broadening of the §5
  file-authorization boundary;
- `job_deadline_filing_qa_s` (`JOB_DEADLINE_FILING_QA_S`, recommended
  default 120s per Document 90 §7/§17 — an implementation-time
  operational choice, not fixed by this document any more precisely than
  Document 90 already does);
- `fqa_max_question_chars` (`FQA_MAX_QUESTION_CHARS`);
- `fqa_max_answer_chars` (`FQA_MAX_ANSWER_CHARS`);
- `fqa_max_sources` (`FQA_MAX_SOURCES`);
- optionally `fqa_rate_limit` (`FQA_RATE_LIMIT`) — Document 90 §13
  explicitly leaves this optional; implementation may omit it.

**No existing `Settings` field's default, validation, or meaning may be
changed.** No `.env` file in any real environment is touched by this
authorization (that remains a separate deployment concern, §16/§17).

---

## 8. Permitted Test Changes

**If ratified, test changes are authorized strictly to:**

1. **new** `backend/tests/unit/test_filing_qa.py` — hermetic, fake
   `chat_fn`, no network/DB — covering the properties in §14;
2. **new** `backend/tests/unit/test_filing_qa_endpoint.py` — hermetic
   fake-Mongo + real ASGI — covering the route family's contract shape;
3. **new** `backend/tests/unit/test_filing_qa_result_buffer.py` — AH-2
   buffer-specific behavior (§11);
4. **new**, additive `backend/tests/backend_test_iterN.py` (next free
   number at implementation time) — live-HTTP suite, run under the
   **existing, unmodified** `pytest.ini` (`-n 2 --dist loadscope`, per
   `CLAUDE.md`'s explicit instruction, re-verified this session — the
   file is not to be touched);
5. **modify** `backend/tests/contract/test_route_inventory.py` exactly as
   §5.2 specifies (four new tuples, `51 → 55`, one added docstring
   clause) — **no other line in this file changes**.

**No existing test file is authorized to be modified, weakened, skipped,
or deleted**, other than the one named, additive edit to
`test_route_inventory.py` above. The M14/M15 additive-suite convention
(`backend_test_iter*.py` files are additive per-feature, never superseded
snapshots — `CLAUDE.md`) is followed exactly, not deviated from.

---

## 9. Deterministic Retrieval / Candidate Requirements (Document 90 §5, §5.1, §5.2, as amended by Documents 95/96 — the amendment applies only to the `N > K` selection procedure below; every other requirement in this section is preserved exactly)

Implementation, if authorized, **must**:

- construct the **ordered candidate universe** from the filing's ordered
  chunks (`chunk_idx` ascending, as `_load_ordered_filing_chunks`
  returns them);
- with universe size `N` and cap `K = MAX_CANDIDATE_CHUNKS`: **`N ≤ K` →
  every chunk is a candidate**, in order — unchanged, unaffected by the
  amendment below;
- **`N > K` → the Document 95/96-ratified deterministic selection
  algorithm exactly** (superseding the original `stride = ceil(N/K)` /
  conditional-highest-chunk-append mechanism, which Document 95 proved
  does not guarantee last-chunk coverage for all valid `(N, K)` — e.g.
  `N=10,K=3` and `N=8,K=3`):

  **Precondition:** `K ≥ 2`. (`K = 1` is **not** a valid
  `MAX_CANDIDATE_CHUNKS` configuration: for `N > K` with `K = 1`, i.e.
  `N > 1`, the first (`U[0]`) and last (`U[N-1]`) chunks are two distinct
  required values that cannot both occupy one selected slot, and the
  formula below is undefined at `K = 1` (division by zero). **§7
  distinguishes the existing configuration precedent
  (`agents/filing_analysis.py`'s module-level constant, carrying no
  validation today) from the authorized FQA enforcement site** (the new
  `MAX_CANDIDATE_CHUNKS` definition in `agents/filing_qa.py`) and
  requires, at that site, an unconditional import-time guard rejecting
  `K < 2` — explicitly **not** a Python `assert` (§7).)

  ```text
  m = K - 1
  h = floor(m / 2)

  pos(i) = floor( (i · (N - 1) + h) / m )     for i = 0, 1, …, K-1
  ```

  using **integer arithmetic only** (floor/truncating integer division
  throughout — no floating-point number or platform-dependent rounding
  anywhere in the computation). The selected candidates are
  `{ U[pos(0)], U[pos(1)], …, U[pos(K-1)] }`.

  This produces, for every `N > K` and `K ≥ 2` (ratified, proven,
  Document 95 §10 / Document 96 §7): **exactly `K`** distinct candidates;
  **`U[0]` always included** (`pos(0) = 0`, exactly); **`U[N-1]` always
  included** (`pos(K-1) = N-1`, exactly); **no duplicates**; the
  selection is **deterministic**, **reproducible**, and **independent of
  model output** (a pure function of `N` and `K` alone, computed before
  generation); and the resulting positions are already **strictly
  ascending**, so ordering by `chunk_idx` requires no additional work
  beyond the defensive re-sort step below.

  **No implementation-defined head/tail truncation, no stride-based
  approximation, no random sampling, and no algorithm other than the
  one above is authorized** for the `N > K` case.
- **re-sort the selected set by `chunk_idx`** and **deterministically
  number** it `1..K` for the model — unchanged from the original
  requirement; a defensive no-op given the amended algorithm's output is
  already sorted;
- ensure the selection is a **pure function of `(U, K)`** —
  **independent of any model output**, reproducible run-to-run;
- **bound by `MAX_CANDIDATE_CHUNKS`**, each excerpt trimmed to
  `MAX_CANDIDATE_CHARS`;
- guarantee **first and last coverage** — the filing's first and last
  chunk always represented — **by construction of the amended formula
  above, not as a conditional rescue**;
- emit an **explicit partial-coverage disclosure** (`coverage_boundaries`)
  whenever content is omitted by the cap, retrieval-scoping, or
  degradation (below);
- ensure **partial coverage does NOT itself imply
  `insufficient_evidence`** — `state` is decided **solely** by Document
  87 R2 §9.1 / §9.2, never by the candidate cap alone;
- for filings above the full-filing-candidate threshold, use
  **retrieval-scoped selection** (`retrieve(db, ticker, question,
  doc_id=doc_id, top_k=MAX_CANDIDATE_CHUNKS,
  candidate_k=MAX_CANDIDATE_CHUNKS*2)`), reusing `agents/retrieval.py`
  **unmodified** — confirmed this session: its existing `doc_id` opt-in
  filter and BM25+dense+rerank pipeline already support this call shape
  with no code change;
- implement **recoverable retrieval degradation** exactly as Document 90
  §5/§5.1 specifies: dense embedder/cross-encoder reranker unavailable →
  **BM25-only** ranking (already the automatic behavior of
  `agents/retrieval.py`'s `_get_embedder`/`_get_reranker` lazy-load-with-
  fallback, confirmed this session); an empty ranked list → a
  **deterministic evenly-spaced sample** across the ordered filing (same
  selection shape as the capping above);
- treat **unrecoverable** failure — the database/persistence layer
  unreachable, `_load_ordered_filing_chunks` or `db.filings.find_one`
  raising, or `retrieve()` raising an unhandled infrastructure exception
  (confirmed this session: `retrieve()` does **not** catch a Mongo-layer
  exception internally — only embedder/reranker load failures degrade
  gracefully; a `db.filing_chunks.find(...)` failure propagates) — as
  **not** degradation: the job `fails` and maps to the existing `502
  infrastructure_error` (Document 87 R2 §12) — **no new error class**;
- treat a **resolved filing with zero usable persisted content** as a
  **data condition**, not a failure: `200 / completed /
  state == "insufficient_evidence"` — **never** a 404, **never** a 502.

**No implementation-defined head/tail truncation, no random sampling, and
no algorithm other than the Document 95/96-ratified formula above is
authorized** for the `N > K` case; the `N ≤ K` case remains "select every
chunk," unchanged.

---

## 10. Generation / Citation Requirements (Document 90 §10, §11 — preserved exactly)

Implementation, if authorized, **must** enforce:

- **at most one logical answer-generation request per FQA job** — never
  more than one model completion for the purpose of producing the
  answer;
- **exactly one generation call** when generation is required and
  candidates exist — one `chat_json` call (reusing `agents/llm.py`
  **unmodified** — `chat_json`, `DEFAULT_HEAVY_MODEL`, `set_llm_context`/
  `reset_llm_context`, `assert_public_url` all confirmed present and
  unchanged this session), HEAVY tier, low temperature, a Pydantic output
  schema whose **only** field is `answer_text` (mirroring
  `OutputNarrativeSchema`'s pattern exactly — `sources` /
  `cited_source_indices` / `state` / `coverage_boundaries` are **never**
  taken from the model);
- **zero model calls** on the deterministic empty-candidate / zero-
  content `insufficient_evidence` paths;
- **no repair generation** — malformed/unparseable `chat_json` output
  surfaces as the existing `502 llm_provider_error`, **never** a second
  model call;
- **no refinement loop** — the orchestrator calls the generation function
  **at most once**, no iterative-refinement branch, no "generate more"
  path;
- **transport-level retries inside `agents/llm.py`** (unmodified) that
  produce no additional model completion remain permitted and are **not**
  a second logical generation;
- a **deterministic structural citation validator**
  (`resolve_and_validate`, mirroring `agents/filing_analysis.py`'s
  function of the same name **in structure**, not copied verbatim) that
  runs on **every** returned answer: parses `[n]` markers, keeps only
  in-range markers, coalesces **strictly contiguous** cited `chunk_idx`
  into inclusive ranges, builds 1-based unique `sources[]` in the frozen
  `{index, doc_id, chunk_start, chunk_end}` shape (every `doc_id` equal
  to the path `doc_id`), rewrites `[n] → [source_index]`, strips orphan
  markers, computes `cited_source_indices` as the exact structural
  subset, and enforces the structural invariants;
- a **module-internal** `FilingQACitationStructureError(ValueError)` —
  mirroring `FilingAnalysisGroundingError`'s role exactly — raised only on
  a structurally unrepairable result, caught by the orchestrator, and
  degraded to `insufficient_evidence`; **never published as an error**;
  **no expansion of the external, nine-class error taxonomy**
  (`backend/domain/errors.py`, confirmed this session to remain
  untouched and to already contain exactly the nine classes Document 90
  cites: `NotFoundError`, `ValidationError`, `ConflictError`,
  `AuthorizationError`, `RateLimitedError`, `DeadlineExceededError`,
  `InfrastructureError`, `LLMProviderError`, `StreamingError`);
- **`state` computed only against Document 87 R2 §9.1 / §9.2** —
  `answered` requires all §9.1 conditions; `insufficient_evidence` is the
  deterministic §9.2 outcome whenever a bounded `answer` object
  satisfying §9.1 cannot be returned;
- **semantic grounding is NOT a runtime gate** — whether a cited passage
  substantiates its claim is evaluated offline (§15), never asserted or
  guaranteed as "proven" by the runtime validator, which checks
  **structure only**.

---

## 11. Job / SSE / Result-Buffer Requirements (AH-2, Document 90 §7–§9 — preserved exactly)

Implementation, if authorized, **must**:

- add **only** the one additive `JobKind.FILING_QA` member (§5.2, §6);
  reuse the existing `JobStatus` lifecycle and the shared
  `MAX_ACTIVE_JOBS` admission budget **unmodified** — confirmed this
  session: `container.job_lifecycle` (`start`/`mark_running`/`publish`/
  `complete`/`fail`/`cancel`/`is_past_deadline`) is called verbatim by
  `_run_filing_analysis` and must be called the same way by
  `_run_filing_qa`;
- implement `_FILING_QA_RESULTS: dict[str, tuple[str, dict, float]]` as a
  **process-local, TTL-bounded, in-process buffer** — a direct structural
  peer of `_FILING_ANALYSIS_RESULTS` (confirmed this session at
  `server.py:2303`) and `_CHANGE_BRIEF_RESULTS` (confirmed at
  `server.py:2575`): written on `completed`, TTL =
  `settings.max_job_lifetime_s`, oldest-first eviction above a
  `_FQA_MAX_ENTRIES` cap (mirroring `_FA_MAX_ENTRIES = 256`),
  owner-scoped read (a non-owner `user_id` → `None`), popped on cancel
  and on every failure path;
- ensure `GET` after expiry returns `{status: "completed"}` with **no
  `answer` key** — never reconstructed from any other source;
- construct the SSE `final` frame from **this same buffer and no other
  mechanism** — mirroring `_filing_analysis_stream_events` exactly: if the
  buffer entry is expired/unavailable when the terminal frame is reached,
  the stream emits **no `final` frame**;
- ensure `reused` is **always `false`** in the create response — no
  identity-keyed result reuse;
- preserve the **AH-2 deployment invariant, unweakened**: the completed
  result exists only in the backend process that executed the job;
  cross-process `GET` is unsupported; a restart may lose the result;
  **no sticky-session workaround**; **no Redis final-result persistence**
  (the existing `RedisEventBus`'s cross-process-capable trace-event
  transport, when `JOB_BACKEND=redis`, must **not** be extended or
  repurposed to carry the completed answer payload cross-process); **no
  MongoDB final-result persistence** (no new collection, document shape,
  or write path for the completed `answer` payload); **no cross-process
  reconstruction** of a result by any means.
- add **one** additive entry per job to `RUNNING_TASKS`
  (`server.py:116`), popped in the wrapper's `finally` block, exactly as
  every existing job kind already does;
- build the four routes' request/response shapes to match Document 87 R2
  exactly: create → `200 {id, status:"queued", reused:false}`; the
  completed `answer` object's frozen shape `{ticker, doc_id, question,
  answer_text, sources[], cited_source_indices, state,
  coverage_boundaries, created_at, prompt_version, schema_version}`;
  `answer` key omitted unless `completed`; idempotent cancellation; SSE
  `final`-frame semantics (once, only on `completed`, including
  `insufficient_evidence`, never on `failed`/`cancelled`).

**This is the single most load-bearing boundary in this authorization**,
exactly as Document 75 §8 stated for M15's AH-2 and Document 90 §9
restates for M16. An implementation that quietly reaches for a shared
store to make the lifecycle "just work" across processes would violate
this decision even if every other boundary here were respected.

---

## 12. Security Requirements (preserved exactly — not weakened for implementation convenience)

If authorized, implementation must preserve, unweakened, every security
boundary Document 87 R2 and Document 90 already establish, reusing
existing infrastructure **unmodified**, confirmed this session:

- **Authentication** — `current_user` dependency on all four routes
  (existing middleware, no body change);
- **SSRF** — `require_admin(user)` (from
  `infrastructure/security/authorization.py`, confirmed unmodified) for
  any custom `llm_provider == "custom"` or `llm_base_url` by a
  non-admin; `assert_public_url(url)` (from `agents/llm.py`, confirmed
  unmodified) for any custom `llm_base_url`, with the established `400`
  response carrying **no `type` field** — reproduced exactly, not newly
  invented;
- **BYOK** — the existing per-request `contextvar` threading
  (`set_llm_context`/`reset_llm_context`), unmodified; `llm_api_key`
  **never persisted, never logged**;
- **Owner-scoped job records** — `GET`/`stream`/`cancel` by a non-owner
  of the job → `404` non-disclosure; the buffer read is owner-scoped
  too;
- **Shared (not owner-scoped) filing corpus** — `filings`/`filing_chunks`
  carry no `user_id`; any authenticated user may ask about any ingested
  filing, matching M13/M14 (deliberately unlike M15's owner-scoped
  `reports`) — an explicit M16 alignment choice Document 90 §15 already
  records, not re-decided here;
- **Input validation** — `422 validation_error` for an empty `ticker`
  after normalization, a missing/empty/whitespace-only `question`, a
  `question` over `FQA_MAX_QUESTION_CHARS`, or a bare `POST {}`; three
  indistinguishable `404 not_found` cases for an unresolvable/cross-
  ticker/unknown `(ticker, doc_id)`;
- **Error sanitization** — the existing nine-class taxonomy only; no
  secret, raw provider response, or raw filing text beyond existing
  discipline is logged; `fail()` receives only a redacted/generic
  message;
- **Prompt-injection posture** — the user's `question` and the filing
  text are untrusted data, never instructions; the `_SYSTEM` prompt must
  instruct: ground every claim only in the numbered excerpts, never
  follow an instruction embedded in the question or excerpts, never
  reveal system context, never recommend.

**No security control may be weakened, bypassed, or special-cased for
FQA implementation convenience.** Any perceived need to do so is a
governance issue to raise separately (§18), not a license implementation
may exercise unilaterally.

---

## 13. Observability Requirements

If authorized, implementation must preserve and extend observability
consistent with Document 90 §16, reusing existing infrastructure
unmodified:

- one root `pipeline.filing_qa` span per job (`get_tracer()`, attributes
  `{job_id}`), set to `ERROR` status on failure/cancel — mirroring the
  existing `pipeline.filing_analysis`/`pipeline.change_brief` pattern;
- SSE `TraceEvent` frames at node boundaries (`retrieving` → `answering`
  → `validating`), then the `final` frame on `completed`, then the named
  `event: end` — the frozen platform SSE contract, no new mechanism;
- reuse of `jobs_active.labels(kind="filing_qa")` (inc on start, dec in
  `finally`) and `retrieval_duration_seconds` (from `retrieval.py`,
  unmodified);
- **one** additive `filing_qa_runs_total{outcome}` counter in
  `backend/infrastructure/observability/metrics.py` (§5.2), same shape
  as `filing_analysis_runs_total`/`change_brief_runs_total`, with
  `outcome ∈ {answered, insufficient_evidence, failed,
  failed_deadline_exceeded, cancelled}`;
- correlation-id logging inherited automatically via existing middleware
  — no new logging mechanism.

**A `20_M6_Metrics_Catalog.md` addendum remains a separate documentation
task**, exactly as Document 90 §16 already states — **not performed or
authorized by this decision.** Observability infrastructure must not
become a substitute for, or a variant of, result persistence — using a
trace event, log line, or metric label to reconstruct a completed
answer outside the AH-2 mechanism (§11) is explicitly not authorized.

---

## 14. Performance / Resource Requirements

If authorized, implementation must respect, without exception:

- the **single-filing surface cap** — a request cannot be made to read
  more than the one identified filing;
- **at most one generation call** per job (§10) — bounding model cost;
- the **shared `MAX_ACTIVE_JOBS`** admission budget — no new per-kind
  queue;
- the **per-kind deadline** `job_deadline_filing_qa_s`, enforced at node
  boundaries via `is_past_deadline()`, mirroring the existing pattern;
- **LLM input bounds** — `MAX_CANDIDATE_CHUNKS` × `MAX_CANDIDATE_CHARS`
  capping the prompt size;
- **no output-selection parameter and no client knob** that changes what
  work the job does;
- the **inherited stale-job reaper** (`JobLifecycle.reap_stale` /
  `max_job_lifetime_s`), unmodified;
- **no unbounded retrieval, generation, or evidence processing** — every
  bound above is enforced, not merely suggested;
- **no unnecessary repeated model calls** — the at-most-one-generation
  rule (§10) is the hard ceiling.

---

## 15. Evaluation Requirements

**Preserving the Document 77 / Document 78 governance outcome exactly —
not reopened, not extended, not weakened by this document:**

- the held-out FQA semantic-evaluation concern (does a cited passage
  substantiate its claim; is any substantive claim left uncited; does
  `insufficient_evidence` fire when and only when it should) is
  **recorded as a requirement, not built**, exactly as Document 90 §14
  states;
- **golden-dataset semantic evaluation remains evaluation evidence, not
  an automatic per-request implementation-completion gate** — mirroring
  the D77/D78 precedent this document does not reopen;
- `agents/scoring.py` (RAGAS-lite, dependency-free, confirmed unmodified
  and unchanged this session) is available as a scoring primitive if a
  small evidence set is exercised as part of the testing floor (§8
  item 4/§14 general testing pattern), but **no evaluation dataset,
  harness, CI gate, or `backend/evaluation/` addition is created or
  authorized by this decision**;
- this document **does not claim semantic grounding is fully proven by
  hermetic runtime tests** — the deterministic citation-**structure**
  validator (§10) is a runtime guarantee; whether a citation
  *substantiates* a claim is, and remains, an evaluation-time concern.

---

## 16. Explicit Exclusions

**This decision — even once ratified — would NOT authorize:**

- changing Document 87 Revision 2;
- changing Document 90 (including the candidate-selection amendment
  itself — implementation applies the Document 95/96-ratified algorithm,
  it does not further amend it);
- changing Document 95 or Document 96;
- changing, reopening, or reinterpreting Documents 83, 84, 85, 86, 88,
  89, 91, 92, or 93;
- any MongoDB schema, collection, index, or migration change — **the
  existing persisted `filings`/`filing_chunks` structures must be reused
  exactly as-is**; any new MongoDB work requires separate, explicit
  governance authorization (a `08_MongoDB_Data_Architecture.md`
  amendment + ADR), not implied here;
- durable FQA result persistence, of any kind;
- Redis result persistence — the existing `RedisEventBus` trace-event
  transport must not be extended to carry final-result payloads
  cross-process;
- a sticky-session architecture, or any equivalent routing workaround for
  cross-process unavailability;
- cross-process result reconstruction, by any means;
- new LangGraph architecture — **Document 90 does not require LangGraph
  involvement, and this decision does not introduce it merely because it
  exists in the platform's preferred stack**; M16 remains out-of-graph
  orchestration exactly as M14/M15 already are;
- Durable Research Sessions, in any form;
- multi-turn FQA, or any conversational continuation;
- multi-filing FQA, cross-filing retrieval, corpus synthesis, or
  portfolio research;
- **frontend implementation** — Document 87 R2 and Document 90 name no
  existing frontend integration point requiring an additive change for
  FQA v1 to be implementable server-side; no frontend file is authorized
  by this decision. (If a future review finds an existing frontend
  integration Document 87/90 explicitly requires, that finding — with
  the exact additive boundary — is a separate governance matter, not
  something this document pre-authorizes by omission.)
- evaluation infrastructure beyond the explicitly authorized test files
  in §8;
- deployment or release, in any environment;
- commit;
- push;
- merge;
- cleanup of any unrelated working-tree artifact (§20);
- any refactor of existing routes, modules, or infrastructure not
  strictly required to add the four new FQA routes — **if a file is not
  required for M16 implementation, this decision does not authorize
  modifying it for cleanup or refactoring, however reasonable that
  cleanup might seem.**

---

## 17. Commit / Push / Deployment Gates (governance boundary, restated because collapsing it is the single most likely failure mode here)

**IMPLEMENTATION AUTHORIZATION ≠ COMMIT AUTHORIZATION.**
**IMPLEMENTATION AUTHORIZATION ≠ PUSH AUTHORIZATION.**
**IMPLEMENTATION AUTHORIZATION ≠ DEPLOYMENT AUTHORIZATION.**

These are four distinct, sequential CTO acts. **Even after this document
is formally ratified:**

- implementation may proceed **only** within the explicitly authorized
  scope in §4–§16 — nothing broader;
- **commit requires a separate, subsequent, explicit CTO authorization**
  — not granted by ratifying this document;
- **push requires a further, separate, explicit CTO authorization** —
  not granted by ratifying this document or by a commit authorization
  alone;
- **deployment / release requires a further, separate, explicit CTO
  authorization** — not granted by any of the above.

No act described in this document, including its own eventual
ratification, collapses any of these stages into another.

---

## 18. Implementation Completion Criteria

**Implementation would be considered complete for the purposes of a
future commit-authorization request only once:**

1. every file in §5.1/§5.2 exists/is modified exactly as scoped, and no
   file outside §5 (or listed in §5.3) has been touched;
2. every requirement in §9 (retrieval/candidate), §10
   (generation/citation), §11 (job/SSE/buffer), §12 (security), §13
   (observability), and §14 (performance) is implemented without
   deviation;
3. the testing floor below is fully green:

   - **candidate curation** — full-filing candidate mode vs
     retrieval-scoped. **The precise candidate-count invariant** (both
     branches together, no contradiction between them): candidate count
     **never exceeds** `K = MAX_CANDIDATE_CHUNKS`; when `N > K`,
     **exactly `K`** candidates are selected (the Document 95/96-ratified
     formula, §9); when `N ≤ K`, **exactly `N`** candidates are selected,
     because every chunk is selected (§9's unchanged `N ≤ K` branch) —
     `N` and `K` are never conflated, and "bounded by `K`" means a
     ceiling, not a claim that exactly `K` are always produced. For the
     `N > K` case, the selected set is additionally (i) **reproducible**
     across repeated runs with identical `(N,K)`, (ii) always contains
     the **first** candidate `U[0]` and the **last** candidate `U[N-1]`,
     (iii) contains **no duplicates**, (iv) is **sorted** by `chunk_idx`,
     and (v) is **independent of `chat_fn` output** — verified at
     minimum against `N=7,K=3`; `N=8,K=3`; `N=10,K=3`; `N=11,K=4`; at
     least one `N % K ≠ 0` case beyond those; the minimum valid `K=2`
     case (must yield exactly `{U[0], U[N-1]}`); the `N ≤ K` case (must
     select every one of the `N` chunks, not `K`); and a case confirming
     `K=1` is rejected as an invalid `MAX_CANDIDATE_CHUNKS` configuration
     by the guard §7 authorizes at its existing definition site, rather
     than silently handled or left to fail unpredictably at request
     time;
   - **request/response contract** — create/status/stream/cancel shapes
     match Document 87 R2 exactly;
   - **filing identity** — `(ticker, doc_id)` resolution, three
     indistinguishable 404s;
   - **single-filing boundary** — no code path can read a second
     filing's content;
   - **partial coverage with valid evidence → `answered`** — a capped/
     partially-covered candidate set that still yields a well-grounded
     answer produces `state == "answered"` **with** a
     `coverage_boundaries` entry, not a downgrade;
   - **no usable evidence → `insufficient_evidence`** — zero surviving
     valid citations produce empty `sources`/`cited_source_indices`, a
     short honest `answer_text`, and a reason string;
   - **zero-content filing** — `200 / completed / insufficient_evidence`,
     zero model calls, never 404, never 502;
   - **recoverable retrieval degradation** — BM25-only fallback and
     empty-result sampling both continue the job with a
     `coverage_boundaries` disclosure, no error;
   - **hard infrastructure failures** — DB/persistence/chunk-load/filing-
     resolution failure → `502 infrastructure_error`, job `failed`;
   - **single-generation invariant** — exactly one `chat_json` call when
     generation runs, zero on deterministic empty/zero-content paths, no
     second call under any tested condition;
   - **citation structure validation** — marker parse, in-range keep,
     contiguous coalescing, `[n] → [source_index]` rewrite, orphan strip,
     `cited_source_indices` exact-subset, structural-invariant
     enforcement, `FilingQACitationStructureError` → degrade, never an
     error response;
   - **error mapping** — every row of Document 90 §18's failure table
     reproduced exactly;
   - **BYOK** — custom provider/base URL threading, key never logged;
   - **SSRF / security boundaries** — non-admin custom provider → 403;
     unsafe custom base URL → 400 with no `type`;
   - **owner-scoped access** — non-owner `GET`/`stream`/`cancel` → 404;
   - **SSE / job lifecycle** — `TraceEvent` sequencing, `final` frame
     semantics (once, only on `completed`, including
     `insufficient_evidence`, never on `failed`/`cancelled`);
   - **AH-2 process-local result behavior** — same-process `GET`;
     post-expiry `{status:"completed"}` with no `answer`; simulated
     post-restart unavailability (fresh buffer instance); simulated
     cross-instance unavailability (two independent buffer instances);
     `reused` always `false`;
   - **regression against M14/M15** — the route-inventory guard moves
     `51 → 55` (exactly four new entries, no more, no fewer); the
     existing `/analysis` and `/changes` route families' own tests are
     confirmed unaffected (run, not modified) by FQA's additions;
4. the additive `backend_test_iterN.py` live-HTTP suite passes against a
   running server;
5. `pytest.ini`'s `addopts` remains byte-for-byte unchanged.

**This bounded suite does not, by itself, constitute a claim of universal
production-grade correctness or of semantic-grounding correctness** —
per §15, that remains an evaluation-evidence concern, not a claim this
testing floor makes. Anything beyond the specific, bounded properties
listed above (load behavior at production scale, long-tail data-quality
issues, adversarial inputs beyond what these tests construct) is not
claimed to be covered by clearing this floor.

---

## 19. CTO Authorization Decision (not performed here — this section records the pending act)

**This document does not decide this section — it names the act a future,
separate CTO review would perform.**

| Field | Value |
|---|---|
| Decision requested | A **fresh** CTO review of this Revision 1, and ratification of this Implementation Authorization Decision (Document 94, as revised) as written, or return it for further revision |
| Decision NOT requested | Approval of any commit, push, merge, or deployment (§17); re-approval by inheritance of the original text's review — the original review's BLOCKED verdict applied to the pre-revision text and does not carry forward to this revision either as approval or as a standing objection to what has since changed |
| If ratified | Implementation may begin, strictly within §4–§16's boundaries (as revised); §18's completion criteria govern when implementation may be considered complete for a future commit-authorization request |
| If not ratified / returned for revision | No implementation of any kind is authorized; this document (or a further revision of it) remains the only path to authorization |
| Current status | 🟡 **DRAFT / PENDING CTO REVIEW. NOT RATIFIED. NOT SELF-RATIFYING. THIS REVISION HAS NOT YET BEEN REVIEWED.** |

Consistent with the established mechanism this governance chain has used
for every prior stage (Documents 66/72/74/76/88/89/91/92/93/95/96), this
document's own ratification — if it occurs — is expected to be recorded
by a **separate, subsequent, explicit CTO act**, not performed by this
document itself, and not performed by Document 96 (which ratifies
Document 95's architecture amendment only, and explicitly does not
ratify this document — Document 96 §10/§12).

---

## 20. Repository / Working-Tree State and Provenance

Recorded by **read-only** inspection this session on 2026-09-12 (original
creation), with a further read-only re-verification on 2026-09-12 for
this Revision 1. **No `git` mutation was performed at either point** —
no `add`/stage, no `commit`, no `push`, no `amend`, no `rebase`, no
`merge`, no `reset`, no `restore`, no `stash`, no `clean`. **No source
code was modified.** No implementation branch or worktree was created.
No mutating command was run.

- `git rev-parse HEAD` = `git rev-parse origin/main` =
  `f8c06649e94f45c388bbecf3eeedb9e5340f2024` (`f8c0664`, *"feat(m15):
  implement change brief"*); ahead/behind `0 / 0` — clean upstream
  tracking, no divergence — **re-confirmed unchanged for this revision.**
- Document number 94 was verified free before original creation (highest
  existing Backend & AI governance document was 93; no Document 94
  existed prior to that task). This revision **modifies this document in
  place — it creates no new document number.**
- **Documents 63–93 were read, not modified, at original creation.**
  Document 87 Revision 2 and Document 90 are the frozen contract/
  architecture input; Documents 83/85/84/86/88/89/92/91/93 are cited, not
  reopened, not reinterpreted.
- **Revision 1 provenance (this task):** Document 90 §5, Document 95 (in
  full), and Document 96 (in full) were re-read to confirm the exact
  ratified algorithm, its proofs, its boundary conditions (including the
  `K ≥ 2` precondition and the `K = 1` resolution), and its worked
  examples, before transcribing them into §9 above verbatim from Document
  95/96 — no alternative algorithm was substituted and none of Document
  95/96's reasoning was reinterpreted. Documents 91 and 93 were
  re-confirmed unchanged and were not touched. `git status --short`,
  `HEAD`, and the upstream relationship were re-inspected before and
  after this revision's edits (below).
- **Backend source files were read read-only for grounding, not
  modified, this session**: `backend/agents/filing_analysis.py` (in
  full), `backend/domain/models.py` (in full), `backend/domain/errors.py`
  (in full), `backend/app/settings.py` (in full),
  `backend/agents/retrieval.py` (in full), `backend/agents/scoring.py`
  (in full), `backend/agents/llm.py` (function signatures grepped),
  `backend/server.py` (the M14 `/analysis` and M15 `/changes` route
  families, `RUNNING_TASKS`, `_load_ordered_filing_chunks`, and the
  `_FILING_ANALYSIS_RESULTS`/`_CHANGE_BRIEF_RESULTS` buffer blocks read
  directly), `backend/infrastructure/observability/metrics.py` (counter
  definitions grepped), `backend/tests/contract/test_route_inventory.py`
  (read — confirms `APPROVED_ROUTES == 51` today), `backend/pytest.ini`
  (confirmed `addopts = -n 2 --dist loadscope`, unchanged), and the
  `backend/tests/unit/` directory listing (confirms the
  `test_filing_analysis*.py` / `test_change_brief*.py` naming convention
  this document's §5/§8 rely on).
- No source, test, schema, index, migration, route, handler, LangGraph
  node, prompt, retrieval/RAG code, MongoDB collection, Redis component,
  provider, configuration, evaluation-infrastructure, metrics-catalog,
  deployment, or frontend file was created or modified. `.gitignore` was
  not modified.
- The working tree is **not** Git-clean. It contains known, pre-existing,
  unrelated items this document does **not** stage, modify, rename,
  delete, or clean:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated — not touched)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/  (untracked, M11 evidence — not touched)
  ?? both / NOT / expect / empty) / current_period_end` / K,      (untracked, stray shell-tooling artifacts predating this task — not touched)
  ?? 1` / {p}                                                     (untracked, 0-byte stray artifacts observed as of this revision —
                                                                     inadvertent byproducts of prior sessions' own shell-based
                                                                     arithmetic verification steps, not created by this task and not
                                                                     touched by it; flagged for transparency, not silently absorbed)
  ?? docs/backend_engineering/67_...md through 96_...md           (pre-existing untracked governance documents — not modified)
  ```

- **This revision modifies exactly one file** —
  `docs/backend_engineering/94_M16_Filing_QA_Implementation_Authorization_Decision.md`
  (this document, in place). It creates no new file and no new document
  number. Staging or committing it remains a separate, subsequently
  CTO-authorized step, not performed here.

---

**🟡 DOCUMENT 94, REVISION 1 — PROPOSED M16 IMPLEMENTATION AUTHORIZATION
DECISION — DRAFT / PENDING CTO REVIEW. NOT YET RATIFIED. THIS REVISION
HAS NOT ITSELF BEEN REVIEWED AND REQUIRES A FRESH CTO REVIEW. REVISING
THIS DOCUMENT DOES NOT AUTHORIZE IMPLEMENTATION.** THE ORIGINAL,
UNREVISED TEXT OF THIS DOCUMENT WAS CTO-REVIEWED AND FOUND **BLOCKED**
BECAUSE ITS §9 FAITHFULLY RESTATED DOCUMENT 90 §5's `stride = ceil(N/K)`
CANDIDATE-SELECTION ALGORITHM, WHICH DOCUMENT 95 PROVED INCAPABLE OF
GUARANTEEING LAST-CHUNK COVERAGE FOR ALL VALID `(N,K)` PAIRS (e.g.
`N=10,K=3` AND `N=8,K=3`), AND WHICH DOCUMENT 96 HAS SINCE FORMALLY
RATIFIED A CORRECTION FOR. **THAT BLOCKED VERDICT DOES NOT CARRY FORWARD
AS APPROVAL OF THIS REVISION** — this revision realigns §9 (and the
cross-referencing metadata in the banner, §2, §3, §6, §7, §16, §18, §19)
with the Document 95/96-ratified algorithm ONLY, and changes nothing
else. IF RATIFIED BY A SEPARATE, SUBSEQUENT CTO ACT, THIS DECISION WOULD
AUTHORIZE FQA V1 IMPLEMENTATION STRICTLY WITHIN THE RATIFIED DOCUMENT 87
REVISION 2 API CONTRACT AND RATIFIED DOCUMENT 90 ARCHITECTURE **AS
AMENDED, FOR CANDIDATE SELECTION ONLY, BY DOCUMENTS 95/96** — AN
EXHAUSTIVE, REPOSITORY-INSPECTED FILE BOUNDARY OF ONE NEW PURE MODULE
(`agents/filing_qa.py`), FOUR NEW ROUTES AND THEIR SUPPORTING
BUFFER/WRAPPER CODE IN `server.py`, ONE ADDITIVE `JobKind` MEMBER, ONE
ADDITIVE METRICS COUNTER, ADDITIVE `Settings` CONFIGURATION, AND ONE
UNCONDITIONAL, NON-`assert`-BASED IMPORT-TIME GUARD AUTHORIZED AT THE NEW
`MAX_CANDIDATE_CHUNKS` DEFINITION SITE IN `agents/filing_qa.py` —
DISTINCT FROM THE UNVALIDATED `agents/filing_analysis.py` PRECEDENT IT
FOLLOWS IN KIND ONLY (NOT A NEW CONFIGURATION SURFACE, NOT A `Settings`
FIELD, NO DEFAULT CHANGE — §7), AND FIVE TEST FILES (§5); THE DOCUMENT
95/96-RATIFIED DETERMINISTIC CANDIDATE-SELECTION FORMULA — `m=K-1`,
`h=floor(m/2)`, `pos(i)=floor((i(N-1)+h)/m)` FOR `i=0..K-1`, `N>K`,
`K≥2` — WITH FIRST/LAST COVERAGE GUARANTEED BY CONSTRUCTION (NOT A
CONDITIONAL RESCUE); CANDIDATE COUNT NEVER EXCEEDS `K`, WITH **EXACTLY
`K`** SELECTED WHEN `N>K` AND **EXACTLY `N`** SELECTED (EVERY CHUNK) WHEN
`N≤K` — THE TWO BRANCHES ARE NEVER CONFLATED (§18); DISTINCT SORTED
CANDIDATES, MODEL-OUTPUT INDEPENDENCE, AND `K=1` UNCONDITIONALLY
REJECTED FOR `N>K` BY THE §7 GUARD, WHICH MUST NOT RELY ON `assert` OR
ANY DISABLE-ABLE EXECUTION MODE (§9); PARTIAL COVERAGE THAT NEVER ITSELF
FORCES
`insufficient_evidence`, `state` GOVERNED SOLELY BY DOCUMENT 87 R2
§9.1/§9.2, RECOVERABLE-VS-UNRECOVERABLE RETRIEVAL DEGRADATION, AND
ZERO-CONTENT AS A DATA CONDITION (§9, UNCHANGED); AT-MOST-ONE LOGICAL
GENERATION WITH NO REPAIR OR REFINEMENT, AND DETERMINISTIC
CITATION-STRUCTURE VALIDATION WITH SEMANTIC GROUNDING LEFT TO EVALUATION
(§10, UNCHANGED); THE AH-2 PROCESS-LOCAL, TTL-BOUNDED, SINGLE-INSTANCE
RESULT INVARIANT, UNWEAKENED (§11, UNCHANGED); EXISTING SECURITY, BYOK,
SSRF, AND OWNERSHIP BOUNDARIES REUSED UNMODIFIED (§12, UNCHANGED);
OBSERVABILITY EXTENDED BY EXACTLY ONE COUNTER (§13, UNCHANGED);
PERFORMANCE BOUNDS RESPECTED (§14, UNCHANGED); AND EVALUATION TREATED AS
RECORDED-REQUIREMENT-ONLY, CONSISTENT WITH DOCUMENTS 77/78, NEVER A
PER-REQUEST GATE AND NEVER CLAIMED PROVEN BY HERMETIC TESTS (§15,
UNCHANGED). THIS DECISION — EVEN ONCE RATIFIED — WOULD NOT AUTHORIZE
CHANGING DOCUMENT 87 R2, DOCUMENT 90 (INCLUDING ITS DOCUMENTS 95/96
AMENDMENT ITSELF), DOCUMENT 95, OR DOCUMENT 96; REOPENING DOCUMENTS
83–93; ANY MONGODB SCHEMA/COLLECTION/INDEX/MIGRATION WORK; REDIS OR
DURABLE RESULT PERSISTENCE; A STICKY-SESSION ARCHITECTURE; CROSS-PROCESS
RECONSTRUCTION; NEW LANGGRAPH ARCHITECTURE; DRS; MULTI-TURN OR
MULTI-FILING FQA; CORPUS/PORTFOLIO RESEARCH; FRONTEND IMPLEMENTATION;
EVALUATION INFRASTRUCTURE BEYOND THE NAMED TEST FILES; DEPLOYMENT OR
RELEASE; COMMIT; PUSH; MERGE; OR CLEANUP OF ANY UNRELATED WORKING-TREE
ARTIFACT (§16). **IMPLEMENTATION AUTHORIZATION ≠ COMMIT AUTHORIZATION ≠
PUSH AUTHORIZATION ≠ DEPLOYMENT AUTHORIZATION** — EACH REMAINS A FURTHER,
SEPARATE, DISTINCT CTO ACT, NONE GRANTED BY THIS DOCUMENT OR BY ITS OWN
FUTURE RATIFICATION (§17). DOCUMENTS 63–96 WERE READ, NOT MODIFIED; THE
BACKEND SOURCE FILES NAMED IN §20 WERE READ READ-ONLY FOR GROUNDING AT
ORIGINAL CREATION, NOT MODIFIED; NO SOURCE, TEST, SCHEMA, CONFIGURATION,
OR INFRASTRUCTURE FILE WAS CREATED OR MODIFIED BY THIS REVISION; NO
IMPLEMENTATION BRANCH OR WORKTREE WAS CREATED; NO MUTATING COMMAND WAS
RUN. NO STAGE. NO COMMIT. NO PUSH. NO MERGE / REBASE / RESET / AMEND.
ONLY THIS DOCUMENT WAS MODIFIED — NO NEW DOCUMENT NUMBER WAS CREATED. THE
NEXT LEGITIMATE GOVERNANCE ACTION IS A **FRESH** CTO REVIEW AND
RATIFICATION OF THIS REVISION — NOT IMPLEMENTATION, AND NOT AN
INHERITANCE OF THE ORIGINAL TEXT'S BLOCKED REVIEW.**

DOCUMENT 94 REVISION COMPLETE — D95/D96 CANDIDATE ALGORITHM ALIGNED — AWAITING CTO REVIEW
