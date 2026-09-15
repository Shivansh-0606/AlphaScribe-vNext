# 97 — Document 94 Revision 1 CTO Ratification Record

**Status:** 🟢 **DOCUMENT 94, REVISION 1 — CTO RATIFIED / ACCEPTED. M16 =
FILING Q&A (FQA v1) IMPLEMENTATION IS NOW AUTHORIZED, STRICTLY WITHIN THE
SCOPE DOCUMENT 94 REVISION 1 ALREADY DEFINES.** This document records the
CTO's ratification of
[94_M16_Filing_QA_Implementation_Authorization_Decision.md](94_M16_Filing_QA_Implementation_Authorization_Decision.md),
**at Revision 1** — the current, and only current, text of that document
(no Revision 2 exists). It is a **separate governance act**, distinct
from Document 94 itself: it accepts the implementation-authorization
proposal Document 94 Revision 1 already made — it does not redesign that
proposal, does not add to it, does not narrow it, and does not
reinterpret it. **This is the formal, terminal ratification act for
Document 94 Revision 1** — the established mechanism this repository has
used for every prior ratification (Documents 74/76/78/80/82/85/86/88/89/
91/92/93/96): a new, separately-numbered, self-effective record. **No
Document 98 is created or required to make this ratification effective.**

**Type:** Governance / ratification decision record (documentation only
— no source code, test, configuration, schema, migration, index, route,
LangGraph node, MongoDB collection/schema, Redis usage, provider,
evaluation-infrastructure, or frontend file created or modified to
produce it; Documents 63–96 read, not modified. The only file this task
creates is this document.

**Date:** 2026-09-12.

**Precedent / lineage.** This record follows the same standalone
terminal-ratification form established by
[Document 76](76_Document75_CTO_Implementation_Authorization_Ratification_Record.md)
(the direct precedent for **ratifying an implementation-authorization
decision** for a prior milestone, M15) and, most recently, by
[Document 96](96_Document95_Candidate_Selection_Architecture_Amendment_Ratification_Record.md)
(a self-effective, terminal ratification record that does not defer its
own effect to a further wrapper). It performs exactly one governance act:
ratifying Document 94 Revision 1 as the M16 implementation authorization.
It does not reinterpret Document 87 Revision 2, Document 90, Document 95,
Document 96, or any of Document 90's own ratification chain (Documents
91, 93) — all are cited as frozen context, not amended.

---

## 1. Purpose

Document 94 Revision 1 proposed the exact, bounded terms under which M16
= Filing Q&A (FQA v1) implementation would be authorized, aligned with
the now-ratified Document 95/96 candidate-selection amendment and
hardened through two further CTO-review correction passes (the §18
candidate-count contradiction, and the non-`assert` `K ≥ 2` enforcement
requirement). Document 94 Revision 1 was CTO-reviewed and received **🟢
PASS — APPROVED FOR RATIFICATION**, but was **not yet ratified**. This
document performs that ratification — **exactly one governance act** —
and records precisely what does, and does not, follow from it:

- Document 94 Revision 1's already-defined implementation scope becomes
  the authoritative M16 implementation authorization (§6, §7);
- the ratified Document 95/96 candidate-selection algorithm, and every
  other Document 90/95/96 architecture decision Document 94 Revision 1
  incorporates, remains exactly as those documents specify (§8, §10);
- the Document 87 Revision 2 contract remains authoritative and
  unmodified, with implementation subordinate to it (§9);
- commit, push, merge, and deployment/release each remain separately
  gated, not granted by this record (§15);
- no implementation work is begun, and no implementation file is created,
  by this record itself.

---

## 2. Exact Ratification Target

**Target: Document 94, Revision 1 — M16 Filing Q&A v1 Implementation
Authorization Decision, as published in
[94_M16_Filing_QA_Implementation_Authorization_Decision.md](94_M16_Filing_QA_Implementation_Authorization_Decision.md).**

Verified this session, read-only, before recording this ratification:

- Document 94's own banner reads: *"**Revision:** 🟡 **REVISION 1** — a
  narrow, targeted correction of §6, §9, §16, §18, and the
  cross-referencing metadata..."* and its Status line reads: *"🟡
  PROPOSED M16 IMPLEMENTATION AUTHORIZATION DECISION — DRAFT / PENDING
  CTO REVIEW. NOT YET RATIFIED..."*
- Document 94's own §19 ("CTO Authorization Decision") records: *"this
  document's own ratification — if it occurs — is expected to be
  recorded by a separate, subsequent, explicit CTO act, not performed by
  this document itself, and not performed by Document 96..."* **This
  document is that separate, subsequent, explicit CTO act.**
- Document 94 carries **no "Revision 2"** — its Revision 1 Note lists
  eight corrections (the original candidate-selection realignment, plus
  three CTO-review correction items: the §18 count-invariant fix, the
  §7 enforcement-site identification, and the §7 non-`assert` guard
  requirement), all folded into the single Revision 1 text now in front
  of this record. **This record ratifies exactly that text — Revision
  1, as it stands today — and no earlier or later revision.**
- `docs/backend_engineering/` was listed in full: the highest-numbered
  file prior to this task was
  `96_Document95_Candidate_Selection_Architecture_Amendment_Ratification_Record.md`.
  Document number 97 was verified free before creation.

**No discrepancy was found. This record ratifies Document 94 Revision 1
exactly, as published, and does not extend to any prior or future
revision.**

---

## 3. Document 94 Revision 1 Identity

Document 94 Revision 1 is **not** the document's original, unrevised
text — that text was CTO-reviewed and found **BLOCKED** (§5 below).
Revision 1 is the single, in-place correction of that original text,
absorbing three distinct correction passes without ever changing its
revision number upward again:

1. the original candidate-selection realignment with the newly-ratified
   Document 95/96 formula (replacing the defective `stride = ceil(N/K)`
   mechanism);
2. a CTO-review correction fixing §18's contradictory candidate-count
   wording ("bounded at exactly `MAX_CANDIDATE_CHUNKS`" vs. the `N ≤ K`
   "select every chunk" branch);
3. a further CTO-review correction requiring the `K ≥ 2` enforcement
   guard to be an unconditional, non-`assert`-based import-time check at
   the identified `agents/filing_qa.py` definition site, and
   distinguishing that authorized site from the unrelated, unvalidated
   `agents/filing_analysis.py` precedent it follows in kind only.

**This record ratifies the cumulative result of all three passes as one
text — Document 94, Revision 1 — not any intermediate state along the
way.**

---

## 4. Governance Prerequisites (verified this session, read-only)

| Fact | Source | Verified state |
|---|---|---|
| FQA v1 scope | Documents 83 / 85 | 🟢 CTO-RATIFIED |
| M16 milestone selection | Documents 84 / 86 | 🟢 CTO-RATIFIED — M16 = Filing Q&A (FQA v1) |
| API contract | Document 87 Revision 2, via Documents 88 / 89 / 92 | 🟢 RATIFIED — re-confirmed via Document 92's own status banner, unchanged |
| Architecture | Document 90, via Documents 91 / 93 | 🟢 RATIFIED — re-confirmed via Document 93's own status banner, unchanged |
| Candidate-selection amendment | Document 95, via Document 96 | 🟢 RATIFIED — re-confirmed via Document 96's own status banner, unchanged. Amends **only** Document 90 §5's `N > K` selection algorithm. |
| Implementation authorization (Document 94, Revision 1) | this document's target | 🟢 **CTO-reviewed, APPROVED FOR RATIFICATION** — not yet ratified prior to this record |

No governance state above is changed by this document. It is cited, not
re-decided. The only question this record answers is whether Document 94
Revision 1 is now ratified — it is, as of this record (§16).

---

## 5. Document 94's Previous Blocker and the Document 95/96 Resolution (recorded, not reopened)

Document 94's **original, unrevised text** was CTO-reviewed and found
**BLOCKED** because its candidate-selection requirement faithfully
restated Document 90 §5's `stride = ceil(N/K)` algorithm with a
conditional highest-`chunk_idx` rescue — a mechanism Document 95 proved
does not, in general, guarantee last-chunk coverage (e.g. `N=10,K=3` and
`N=8,K=3` both drop the true last chunk). Document 95 proposed a
corrected, closed-form algorithm; Document 96 formally ratified it as the
binding amendment to Document 90 §5. **Document 94 Revision 1 then
realigned the implementation-authorization proposal with that corrected,
ratified architecture — and nothing else.** This record does not
re-derive, re-litigate, or reopen that defect or its resolution; it
accepts Document 95's mathematics and Document 96's ratification exactly
as they stand, and it ratifies Document 94 Revision 1's faithful
incorporation of them.

---

## 6. Implementation Authorization Being Ratified

**Ratified exactly as Document 94 Revision 1 §4 scopes it — nothing
broader:**

M16 = Filing Q&A (FQA v1) implementation is now authorized, and **only**
within the boundaries Document 94 Revision 1 already fixes:

- the four-route async `qa` family under
  `/api/companies/{ticker}/filings/{doc_id}/qa`;
- the `agents/filing_qa.py` module (Document 90 §4.2/§6/§10/§11, as
  amended by Documents 95/96 for candidate selection);
- the one additive `JobKind.FILING_QA` enum member;
- the operational-configuration set Document 90 §9/§13/§21 names, plus
  the `K ≥ 2` enforcement guard Document 94 Revision 1 §7 requires;
- the one additive `filing_qa_runs_total{outcome}` metrics counter;
- the corresponding hermetic unit tests, contract tests, and one
  additive `backend_test_iterN.py` live-HTTP suite.

**Governance lineage this authorization sits atop (both branches feed
Document 94 Revision 1; neither is bypassed):**

```text
D83 → D85 (FQA scope)              🟢 CTO-RATIFIED
D84 → D86 (M16 selection)          🟢 CTO-RATIFIED
D87 R2 → D88 → D89 → D92           🟢 RATIFIED (API contract chain)
D90 → D91 → D93                    🟢 RATIFIED (architecture chain)
D95 → D96                          🟢 RATIFIED (candidate-selection amendment to D90)
                                       │
                                       ▼
D94 Revision 1 (implementation authorization proposal,
                incorporating D90 as amended by D95/D96)   🟡 → 🟢
                                       │
                                       ▼
D97 (THIS)                          🟢 CTO-RATIFIED — the act that ratifies D94 Revision 1
```

**This record does not narrate this scope beyond the summary above —
Document 94 Revision 1's own §4–§18 remain the authoritative, complete
statement of what is authorized (§7–§14 below point to, and do not
restate beyond, those sections).**

---

## 7. Authorized Implementation Boundary (summarized from Document 94 Revision 1 §5 — not expanded)

**The exhaustive file/module boundary is exactly Document 94 Revision
1's §5.1/§5.2/§5.3 — reproduced here as a summary pointer, not an
independent or expanded grant:**

- **New files (§5.1):** `backend/agents/filing_qa.py`;
  `backend/tests/unit/test_filing_qa.py`;
  `backend/tests/unit/test_filing_qa_endpoint.py`;
  `backend/tests/unit/test_filing_qa_result_buffer.py`; one additive
  `backend/tests/backend_test_iterN.py` (next free number, verified at
  implementation time).
- **Existing files modified, additively only (§5.2):**
  `backend/domain/models.py` (one `JobKind` member);
  `backend/app/settings.py` (the FQA operational-config fields);
  `backend/server.py` (the `FilingQARequest` model, the `_FILING_QA_RESULTS`
  buffer, the `_run_filing_qa` wrapper, the `_filing_qa_stream_events`
  generator, and the four new routes — no existing route, function, or
  class modified); `backend/infrastructure/observability/metrics.py`
  (one counter); `backend/tests/contract/test_route_inventory.py` (four
  new route tuples, `51 → 55`).
- **Explicitly not authorized to touch (§5.3):** every other named file,
  including `agents/filing_analysis.py`, `agents/change_brief_*.py`,
  `agents/comparison_explanation.py`, `agents/retrieval.py`,
  `agents/llm.py`, `agents/scoring.py`, `domain/errors.py`,
  `application/jobs.py`, `infrastructure/security/authorization.py`,
  `infrastructure/streaming/sse.py`, any MongoDB or Redis infrastructure
  file, any frontend file, `20_M6_Metrics_Catalog.md`,
  `08_MongoDB_Data_Architecture.md`, and `pytest.ini`.

**This record does not invent, add, or imply any file, module,
infrastructure component, or product feature beyond this list.** No
broadening of this boundary is authorized by this ratification act.

---

## 8. Ratified Candidate-Selection Algorithm (Document 94 Revision 1 §9, incorporating Documents 95/96 — reproduced verbatim, not altered)

**For `N ≤ K`:** select all candidate chunks (every chunk in the ordered
universe `U`) — unaffected by the amendment.

**For `N > K`** (precondition `K ≥ 2`):

```text
m = K - 1
h = floor(m / 2)

pos(i) = floor( (i · (N - 1) + h) / m )     for i = 0, 1, …, K-1
```

using integer arithmetic only. The selected candidates are
`{ U[pos(0)], U[pos(1)], …, U[pos(K-1)] }`.

**Ratified result, unchanged from Document 94 Revision 1 §9:** exactly
`K` candidates; the first candidate `U[0]` always included
(`pos(0) = 0`, exactly); the last candidate `U[N-1]` always included
(`pos(K-1) = N-1`, exactly); no duplicates; deterministic; reproducible;
independent of model output; the result already sorted by `chunk_idx`;
bounded by `MAX_CANDIDATE_CHUNKS`.

**`K ≥ 2` enforcement (Document 94 Revision 1 §7, unchanged):** `K = 1`
is invalid for `N > K` — mathematically incompatible with simultaneous
first/last coverage whenever `N > 1`, and undefined in the formula
(division by zero). The enforcement site is the new
`MAX_CANDIDATE_CHUNKS` definition in `backend/agents/filing_qa.py` — not
the pre-existing, unvalidated `agents/filing_analysis.py` constant, which
is cited only as a precedent for the *kind* of site (a module-level
constant, not a `Settings` field). The guard at that site must be an
**unconditional, import-time check that rejects `K < 2`**, placed
immediately after the constant's definition, and must **not** rely on
Python `assert` semantics or any construct disable-able under an
optimized execution mode (`-O`/`-OO`/`PYTHONOPTIMIZE`).

**This record does not alter this algorithm, its proofs, its boundary
conditions, or its enforcement requirement in any way.** It ratifies
Document 94 Revision 1's incorporation of Document 95/96's mathematics
exactly as written.

---

## 9. Contract Preservation

**Document 87 Revision 2 remains the ratified, unmodified M16 API
contract**, and the implementation authorization this record ratifies
remains strictly subordinate to it. Every externally observable
behaviour it fixes — request/response shapes, the closed `state` enum
and its §9.1/§9.2 determination, the citation convention, the nine-class
error taxonomy, the job/SSE semantics — is untouched. This record does
not modify, weaken, extend, or reinterpret Document 87 Revision 2,
Document 88, Document 89, or Document 92 in any way.

---

## 10. Architecture Preservation

**Preserved exactly as Document 90 (amended only for candidate selection
by Documents 95/96) and Document 94 Revision 1 already specify — none of
the following is reinterpreted, weakened, extended, or newly introduced
by this record:**

- the candidate universe definition (ordered, `chunk_idx`-ascending
  `filing_chunks`);
- coverage disclosure (`coverage_boundaries`);
- partial-coverage semantics — never proof of exhaustiveness;
- **partial coverage does NOT itself imply `insufficient_evidence`** —
  `state` remains governed solely by Document 87 R2 §9.1/§9.2;
- recoverable retrieval degradation (BM25-only fallback; empty-result
  deterministic sampling);
- unrecoverable infrastructure failure → existing `502
  infrastructure_error`;
- zero-content filing as a data condition, never 404/502;
- at-most-one logical answer-generation request per job;
- zero generation on deterministic empty/zero-content paths;
- no repair generation; no refinement loop;
- deterministic structural citation validation
  (`resolve_and_validate`/`FilingQACitationStructureError`, module-
  internal, never published as an error);
- semantic grounding remains an evaluation concern, never a runtime
  gate.

---

## 11. AH-1 / AH-2

**AH-1** (the M15 `report`-mode structured-schema resolution) is
untouched and not reinterpreted — it was never in this authorization's
scope.

**AH-2** (the process-local, TTL-bounded, in-process `_FILING_QA_RESULTS`
buffer) is preserved exactly as Document 90 §8/§9 and Document 94
Revision 1 §11 specify: written on `completed`, owner-scoped read,
oldest-first eviction, popped on cancel/failure, `GET` after expiry
returns `{status:"completed"}` with no `answer` key, the SSE `final`
frame built from the same buffer and no other mechanism, `reused` always
`false`. **No cross-process reconstruction, no sticky-session
workaround, no Redis-backed final-result persistence, and no MongoDB
final-result persistence are authorized** — this record does not
introduce, or license implementation to introduce, any of them.

---

## 12. DRS Boundary

**Durable Research Sessions remain BLOCKED and outside M16.** This
ratification does not authorize DRS in any form. FQA remains, exactly as
Documents 83/85 and Document 90 already fix: single-turn; stateless with
respect to durable conversational/research state; single-filing;
identified by `(ticker, doc_id)`. **No multi-turn, multi-filing, corpus,
or portfolio-research expansion is authorized by this record.**

---

## 13. Security and Ownership

**Preserved exactly, unweakened, as Document 87 R2, Document 90, and
Document 94 Revision 1 §12 already establish:**

- SSRF controls (`require_admin` + `assert_public_url`, the established
  `400`-with-no-`type` response, reproduced exactly);
- BYOK restrictions (per-request `contextvar` threading, `llm_api_key`
  never persisted or logged);
- owner-scoped authorization (job records owner-scoped; the filing
  corpus remains shared, matching M13/M14, not owner-scoped — an
  existing, not newly-decided, alignment choice);
- input validation (the `422`/`404` rules Document 87 R2 fixes);
- secret handling (no BYOK material, raw provider response, or raw
  filing text beyond existing discipline logged);
- error sanitization (the existing nine-class taxonomy only; zero new
  error classes).

**No security control is weakened, bypassed, or special-cased by this
ratification.**

---

## 14. Testing / Evaluation Boundary

**The tests Document 94 Revision 1 §8/§18 require become, by this
ratification, part of the authorized implementation scope — no more, no
fewer:**

candidate selection for `N ≤ K` and `N > K`; the required regression
cases `N=7,K=3`; `N=8,K=3`; `N=10,K=3`; `N=11,K=4`; at least one
`N % K ≠ 0` case; the minimum valid `K=2` case; the invalid `K=1` case
(rejected by the §7 guard, not silently handled); exact-`K` count
verification; first/last endpoint coverage; no duplicates; deterministic
repeated execution; model-output independence; the `MAX_CANDIDATE_CHUNKS`
bound; partial-coverage-compatible-with-`answered` semantics; recoverable
retrieval degradation; hard infrastructure failures; zero-content
behavior; the single-generation invariant; citation-structure validation;
security (BYOK, SSRF); ownership; SSE/job-lifecycle behavior; AH-2
process-local result behavior; and regression confirmation against the
existing M14/M15 route families and their own tests.

**This record does not add any test beyond Document 94 Revision 1's
authorized boundary, however useful an additional test might seem.**

**Evaluation (Document 77/78 governance preserved):** golden-dataset
semantic evaluation remains evaluation **evidence**, not an automatic
per-request implementation- or commit-completion gate. No evaluation
dataset, harness, CI gate, or `backend/evaluation/` addition is
authorized beyond what Document 94 Revision 1 §8/§15 already names (the
existing, unmodified `agents/scoring.py` primitive, if exercised as
testing-floor evidence).

---

## 15. Commit / Push / Merge / Deployment Separation

**M16 implementation is now authorized, strictly within Document 94
Revision 1's scope. This is the only stage this record advances.**

**IMPLEMENTATION AUTHORIZATION ≠ COMMIT AUTHORIZATION.**
**IMPLEMENTATION AUTHORIZATION ≠ PUSH AUTHORIZATION.**
**IMPLEMENTATION AUTHORIZATION ≠ MERGE AUTHORIZATION.**
**IMPLEMENTATION AUTHORIZATION ≠ DEPLOYMENT / RELEASE AUTHORIZATION.**

Each of the following remains a **separate, subsequent, explicit CTO
act**, not granted by this record:

- **commit** — requires its own, later authorization;
- **push** — requires its own, later authorization, not implied by a
  commit authorization;
- **merge** — requires its own, later authorization;
- **deployment / release** — requires its own, later authorization, not
  implied by any of the above.

**No act in this record collapses any of these stages into another.**

---

## 16. Governance Act Performed

**DOCUMENT 94, REVISION 1 IS FORMALLY RATIFIED**, exactly as reviewed and
approved. This is the **single** governance act this record performs. It:

- **confirms** the implementation-authorization scope already recorded in
  Document 94 Revision 1 §§1–20;
- **does not** re-derive, redesign, extend, or reinterpret that scope;
- **does not** modify Document 94, Document 90, Document 95, Document 96,
  Document 91, Document 93, or Document 87 Revision 2 — each stands
  exactly as previously written;
- **does not** introduce any new implementation requirement, file,
  module, or product feature beyond what Document 94 Revision 1 already
  authorizes;
- **does not** authorize commit, push, merge, deployment, or release
  (§15);
- **does not** begin implementation, and creates no implementation file.

**This record is self-effective upon its own CTO sign-off** — it does
not defer its own effect to a further, subsequent ratification-of-
Document-97 wrapper. **No Document 98 is created or required.**

---

## 17. Resulting Governance State

- **Document 94, Revision 1 stands formally ratified**, effective
  immediately upon this record.
- **M16 = Filing Q&A (FQA v1) implementation is now authorized**,
  strictly within the scope Document 94 Revision 1 §4–§18 already
  defines (§6, §7 above) — nothing broader.
- The Document 87 Revision 2 API contract (through Documents 88/89/92),
  the Document 90 architecture (through Documents 91/93), and the
  Document 95/96 candidate-selection amendment remain exactly as
  previously ratified — unaffected, unmodified.
- **Commit, push, merge, and deployment/release remain separately
  gated** — none is authorized by this record (§15).
- AH-1, AH-2, the DRS boundary, and every security/testing/evaluation
  constraint named in §10–§14 remain preserved exactly as before.

---

## 18. Provenance

Recorded by **read-only** `git` inspection this session on 2026-09-12.
**No `git` mutation was performed** — no `add`/stage, no `commit`, no
`push`, no `amend`, no `rebase`, no `merge`, no `reset`, no `restore`, no
`stash`, no `clean`.

- `git rev-parse HEAD` = `git rev-parse origin/main` =
  `f8c06649e94f45c388bbecf3eeedb9e5340f2024` (`f8c0664`, *"feat(m15):
  implement change brief"*); `git rev-list --left-right --count
  origin/main...HEAD` = `0	0` — clean upstream tracking, no divergence.
- Document number 97 was verified free before creation (highest existing
  Backend & AI governance document was 96; no Document 97 existed prior
  to this task).
- **Documents 63–96 were read (or, for documents authored earlier this
  session, re-confirmed from session state), not modified.** Document 94
  was re-read **in full, at its current Revision 1 text**, immediately
  before this ratification was recorded (§2, §3) — confirmed to carry no
  "Revision 2" and to incorporate all eight Revision 1 Note items.
  Document 90 §5, Document 95, and Document 96 were re-confirmed
  unchanged. Documents 91 and 93 were re-confirmed to record the
  architecture-ratification chain, neither reopened nor reinterpreted
  here.
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval/RAG code, MongoDB collection, Redis
  component, provider, configuration, evaluation-infrastructure,
  metrics-catalog, deployment, or frontend file was created or modified.
  `.gitignore` was not modified. No implementation branch or worktree was
  created; no mutating command was run.
- The working tree is **not** Git-clean. It contains known, pre-existing,
  unrelated items this document does **not** stage, modify, rename,
  delete, or clean:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated — not touched)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/  (untracked, M11 evidence — not touched)
  ?? both / NOT / expect / empty) / current_period_end` / K, / 1` / K` / {p}  (untracked, 0-byte stray
                                                                     shell-tooling artifacts observed across prior sessions'
                                                                     read-only inspection commands — not created by this task,
                                                                     not touched by it)
  ?? docs/backend_engineering/67_...md through 96_...md           (pre-existing untracked governance documents — not modified)
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/97_Document94_Revision1_CTO_Ratification_Record.md`).
  It is untracked and not yet version-controlled. Staging or committing
  it is a separate, subsequently CTO-authorized step, not performed here.

---

## 19. Final Attestation

**🟢 DOCUMENT 94, REVISION 1 — CTO RATIFIED / ACCEPTED. THIS RECORD
PERFORMS THE SEPARATE, TERMINAL CTO REVIEW AND RATIFICATION THAT DOCUMENT
94's OWN §19 NAMED AS THE CONDITION FOR ITS EFFECT, WITHOUT MODIFYING
DOCUMENT 94, DOCUMENT 90, DOCUMENT 95, DOCUMENT 96, OR ANY EARLIER
DOCUMENT. DOCUMENT 94's PREVIOUS BLOCKER — THE OBSOLETE `stride =
ceil(N/K)` CANDIDATE-SELECTION ALGORITHM'S FAILURE TO GUARANTEE
LAST-CHUNK COVERAGE — WAS RESOLVED AT THE ARCHITECTURE LAYER BY DOCUMENTS
95/96, AND DOCUMENT 94 REVISION 1 ALIGNED THE IMPLEMENTATION-
AUTHORIZATION PROPOSAL WITH THAT CORRECTED, RATIFIED ARCHITECTURE; THIS
RECORD DOES NOT REOPEN THAT ISSUE. **M16 = FILING Q&A (FQA v1)
IMPLEMENTATION IS NOW AUTHORIZED, STRICTLY WITHIN DOCUMENT 94 REVISION
1's ALREADY-DEFINED SCOPE** — ONE NEW PURE MODULE
(`agents/filing_qa.py`), FOUR NEW ROUTES AND THEIR SUPPORTING
BUFFER/WRAPPER CODE IN `server.py`, ONE ADDITIVE `JobKind` MEMBER,
ADDITIVE `Settings` CONFIGURATION, ONE ADDITIVE METRICS COUNTER, ONE
UNCONDITIONAL NON-`assert` IMPORT-TIME GUARD AT THE NEW
`MAX_CANDIDATE_CHUNKS` DEFINITION SITE IN `agents/filing_qa.py`
REJECTING `K < 2`, AND FIVE TEST FILES — NO FILE, MODULE, OR PRODUCT
FEATURE BEYOND THIS LIST IS AUTHORIZED. THE RATIFIED DOCUMENT 95/96
CANDIDATE-SELECTION FORMULA (`m=K-1`, `h=floor(m/2)`,
`pos(i)=floor((i(N-1)+h)/m)` FOR `i=0..K-1`, `N>K`, `K≥2`) IS REPRODUCED
UNALTERED: EXACTLY `K` CANDIDATES FOR `N>K`, EXACTLY `N` (EVERY CHUNK)
FOR `N≤K`, FIRST AND LAST ENDPOINTS ALWAYS INCLUDED BY CONSTRUCTION, NO
DUPLICATES, DETERMINISTIC, REPRODUCIBLE, MODEL-OUTPUT-INDEPENDENT, SORTED
BY `chunk_idx`, BOUNDED BY `MAX_CANDIDATE_CHUNKS`. THE DOCUMENT 87
REVISION 2 API CONTRACT REMAINS AUTHORITATIVE AND UNMODIFIED; THE
IMPLEMENTATION AUTHORIZATION REMAINS SUBORDINATE TO IT. EVERY OTHER
DOCUMENT 90/95/96 ARCHITECTURE DECISION — CANDIDATE UNIVERSE, COVERAGE
DISCLOSURE, PARTIAL-COVERAGE SEMANTICS AND ITS NON-DETERMINATION OF
`insufficient_evidence`, RECOVERABLE/UNRECOVERABLE RETRIEVAL DEGRADATION,
ZERO-CONTENT AS A DATA CONDITION, THE AT-MOST-ONE-GENERATION INVARIANT,
NO REPAIR/REFINEMENT GENERATION, DETERMINISTIC CITATION-STRUCTURE
VALIDATION, SEMANTIC GROUNDING AS AN EVALUATION CONCERN, AH-1, AH-2, THE
DRS BOUNDARY, BYOK, SSRF, OWNER-SCOPED JOBS, SSE, OUTPUT BOUNDS,
OBSERVABILITY, SECURITY, AND DEPLOYMENT CONSTRAINTS — REMAINS EXACTLY AS
PREVIOUSLY RATIFIED, UNTOUCHED. THIS RECORD DOES NOT AUTHORIZE ANY
MONGODB SCHEMA/COLLECTION/INDEX/MIGRATION WORK, REDIS-BACKED FINAL-RESULT
PERSISTENCE, CROSS-PROCESS RESULT RECONSTRUCTION, A STICKY-SESSION
WORKAROUND, A NEW LANGGRAPH ARCHITECTURE, DURABLE RESEARCH SESSIONS,
MULTI-TURN OR MULTI-FILING FQA, ANY FRONTEND SCOPE BEYOND WHAT DOCUMENT
94 REVISION 1 EXPLICITLY AUTHORIZES (NONE), OR ANY EVALUATION
INFRASTRUCTURE BEYOND ITS NAMED TEST FILES. **IMPLEMENTATION
AUTHORIZATION ≠ COMMIT AUTHORIZATION ≠ PUSH AUTHORIZATION ≠ MERGE
AUTHORIZATION ≠ DEPLOYMENT/RELEASE AUTHORIZATION** — EACH REMAINS A
FURTHER, SEPARATE, DISTINCT CTO ACT, NONE GRANTED BY THIS RECORD. NO
DOCUMENT 98 IS CREATED; THIS RECORD IS THE SELF-EFFECTIVE, TERMINAL
RATIFICATION ACT FOR DOCUMENT 94 REVISION 1. NO IMPLEMENTATION WAS
BEGUN AND NO IMPLEMENTATION FILE WAS CREATED BY THIS TASK. NO GIT STATE
WAS STAGED, COMMITTED, PUSHED, MERGED, REBASED, RESET, CLEANED, STASHED,
OR AMENDED. `HEAD = origin/main = f8c0664`, `0	0` DIVERGENCE. DOCUMENTS
63–96 WERE READ, NOT MODIFIED; THE ONLY FILE THIS TASK CREATES IS THIS
DOCUMENT. THE NEXT LEGITIMATE GOVERNANCE ACTION IS A SEPARATE,
SUBSEQUENT IMPLEMENTATION PROMPT — ISSUED SEPARATELY, NOT PART OF THIS
RECORD — FOLLOWED, IN DUE COURSE, BY SEPARATE COMMIT, PUSH, MERGE, AND
DEPLOYMENT/RELEASE AUTHORIZATIONS, NONE OF WHICH THIS RECORD GRANTS.**

DOCUMENT 97 — D94 REVISION 1 IMPLEMENTATION AUTHORIZATION RATIFICATION RECORD — CTO RATIFIED / ACCEPTED. This record is the self-effective terminal ratification act for Document 94 Revision 1. No Document 98 is required.
