# 96 — Document 95 CTO Ratification Record

**Status:** 🟢 **DOCUMENT 95 — CTO RATIFIED / ACCEPTED. THE M16 FILING Q&A
(FQA v1) CANDIDATE-SELECTION ARCHITECTURE IS AMENDED AS DOCUMENT 95
SPECIFIES.** This document records the CTO's ratification of
[95_D90_Candidate_Selection_Architecture_Amendment_Decision.md](95_D90_Candidate_Selection_Architecture_Amendment_Decision.md)
— the narrow architecture amendment correcting exactly one mechanism in
[Document 90](90_M16_Filing_QA_Architecture_Decision_Pack.md) §5 (the
deterministic candidate-selection algorithm for `N > K`). It is a
**separate governance act**, distinct from Document 95 itself: it
accepts the corrected algorithm Document 95 already proposed and proved
— it does not re-derive the mathematics, does not redesign the
algorithm, does not reopen any other part of Document 90, and makes no
additional governance decision. **This is the formal ratification act
for Document 95** — the established terminal-ratification convention
this repository has used for every prior amendment/ratification cycle
(Documents 74/76/78/80/82/85/86/88/89/91/92/93): a new, separately-
numbered, self-effective record, not itself dependent on any further
ratification-of-this-document wrapper. **No Document 97 is created or
required to make this ratification effective.**

**The ratified decision is: Document 95's corrected candidate-selection
algorithm — the closed-form integer formula in §6 below — is now the
authoritative candidate-selection mechanism for Document 90 §5,
superseding the original `stride = ceil(N/K)` mechanism Document 95
proved defective.** This record does **not** modify Document 95, does
**not** modify Document 90, does **not** modify Document 91, Document 93,
or Document 94, and does **not** authorize implementation of any kind.

**Type:** Governance / ratification decision record (documentation only
— no source code, test, configuration, schema, migration, index, route,
LangGraph node, MongoDB collection/schema, Redis usage, provider,
evaluation-infrastructure, or frontend file created or modified to
produce it; Documents 63–95 read, not modified. The only file this task
creates is this document.

**Date:** 2026-09-12.

**Precedent / lineage.** This record follows the same standalone
terminal-ratification form established by
[Document 78](78_Document77_CTO_D75_Section14_Amendment_Ratification_Record.md)
(the direct precedent for **ratifying a narrow amendment decision to a
prior architecture document**, rather than the original architecture
pack or contract) and, one governance track over, by
[Document 92](92_Document89_CTO_Ratification_Record.md) /
[Document 93](93_Document91_CTO_Ratification_Record.md) (self-effective,
terminal ratification records that do not defer their own effect to a
further wrapper document). It performs exactly one governance act:
ratifying Document 95 as the M16 candidate-selection architecture
amendment. It does not reinterpret Document 90 (the architecture being
amended), Document 91 or Document 93 (the architecture's own,
unaffected, prior ratification chain), or Document 94 (the blocked
implementation-authorization proposal) — all are cited as frozen context,
not amended.

---

## 1. Purpose

Document 95 proposed a narrow, mathematically rigorous correction to
Document 90 §5's deterministic candidate-selection algorithm, after CTO
review of Document 94 traced Document 94's block to a genuine
architectural defect inherited from Document 90 (not a defect in
Document 94's own restatement of it). Document 95 was itself
CTO-reviewed and received **🟢 PASS — APPROVED FOR RATIFICATION**, but
was **not yet ratified**. This document performs that ratification —
**exactly one governance act** — and records precisely what does, and
does not, follow from it:

- Document 95's corrected algorithm becomes the authoritative amendment
  to Document 90 §5 (§5, §6, §11);
- every other part of Document 90 remains exactly as ratified through
  Documents 91/93, untouched (§9, §13–§16);
- Document 94 remains **BLOCKED** — this ratification does not lift that
  block, does not ratify Document 94, and does not authorize
  implementation (§10, §12);
- the next legitimate governance acts are named, in order, without being
  performed here (§19).

---

## 2. Exact Ratification Target

**Target: Document 95 — D90 Candidate-Selection Architecture Amendment
Decision, as published in
[95_D90_Candidate_Selection_Architecture_Amendment_Decision.md](95_D90_Candidate_Selection_Architecture_Amendment_Decision.md).**

Verified this session, read-only, before recording this ratification:

- Document 95's top-line Status banner reads: *"🟡 DRAFT / PENDING CTO
  REVIEW — PROPOSED NARROW ARCHITECTURE AMENDMENT TO DOCUMENT 90. NOT
  RATIFIED. THIS DOCUMENT DOES NOT RATIFY ITSELF AND DOES NOT AUTHORIZE
  IMPLEMENTATION. DOCUMENT 94 REMAINS BLOCKED."*
- Document 95 §17 ("Ratification Requirement") states explicitly that it
  "does not ratify itself, and does not ratify the amendment it
  proposes," and that the amendment "becomes the authoritative, binding
  correction to Document 90 §5 only through a separate, subsequent,
  explicit CTO ratification act." **This document is that act.**
- `docs/backend_engineering/` was listed in full: the highest-numbered
  file prior to this task was
  `95_D90_Candidate_Selection_Architecture_Amendment_Decision.md`.
  Document number 96 was verified free before creation.

**No discrepancy was found. Document 95, as published, is confirmed as
the correct and only ratification target.**

---

## 3. Document 95 Revision Identity

Document 95 carries **no revision marker** — it is a single, un-revised
proposal, exactly as Document 90 and Document 91 also carry none
(re-verified against this pattern this session; Document 95's own text
introduces no `Revision R1`/`Revision 2`/`Revision N` block anywhere).
This record ratifies Document 95 **as-published**, and makes no claim
about, and does not ratify, any later revision. If a Document 95 revision
is ever introduced, it requires its own separate CTO review and
ratification; this record does not, and cannot, extend to it.

---

## 4. Triggering Document 94 Blocker

Document 94 — the M16 Implementation Authorization Decision — was
reviewed and found **BLOCKED** because its §9 faithfully restated
Document 90 §5's `stride = ceil(N/K)` candidate-selection procedure,
which Document 95 §4 proved does not, in general, guarantee the
last-chunk coverage Document 90 itself claims. Document 95 §4's two
counterexamples are accepted here without re-derivation:

- **`N = 10, K = 3`**: `stride = 4`; striding selects `U[0], U[4], U[8]`
  — three points, so the rescue clause never fires; `U[9]` (the true
  last chunk) is never selected.
- **`N = 8, K = 3`**: `stride = 3`; striding selects `U[0], U[3], U[6]`
  — three points, rescue clause never fires; `U[7]` is never selected.

Document 94's block is correctly attributed to Document 90, not to
Document 94's own restatement — a faithful restatement of a defective
architecture is not itself a defect in the restating document. This
record does not re-litigate that finding; it accepts Document 95's
diagnosis and ratifies Document 95's correction.

---

## 5. Architecture Amendment Being Ratified

**Ratified exactly as Document 95 §5 scopes it — nothing broader:**

This amendment replaces **only** Document 90 §5 steps 2–3 (the selection
procedure invoked when the candidate universe size `N` exceeds
`MAX_CANDIDATE_CHUNKS`, `K`). It does not touch:

- Document 90 §5 step 1 (the `N ≤ K` branch: select every chunk) —
  unchanged;
- Document 90 §5 step 4 (re-sort by `chunk_idx`, number `1..K`, trim to
  `MAX_CANDIDATE_CHARS`) — unchanged, and shown by Document 95 §7.3/§10
  to remain a defensive no-op given the corrected algorithm's output is
  already sorted;
- the empty-retrieval-result degradation fallback ("a deterministic
  evenly-spaced sample across the ordered filing") — Document 90 already
  defines this as sharing the capping mechanism's shape, so correcting
  the shared mechanism consistently and necessarily corrects that named
  call site too, without this being a new design decision or a new call
  site beyond the two Document 90 §5 already names;
- any other section of Document 90 (§9 below).

---

## 6. Exact Corrected Candidate-Selection Algorithm (ratified verbatim from Document 95 — not restated, reinterpreted, or simplified)

**Preconditions:** `N > K`, `K ≥ 2` (§8 addresses `K = 1` and `N ≤ K`
separately; this formula is defined only under these preconditions).

```text
m = K - 1
h = floor(m / 2)

pos(i) = floor( (i·(N - 1) + h) / m )     for i = 0, 1, …, K-1
```

- All arithmetic is **integer arithmetic only** — floor (truncating)
  integer division throughout every step. No floating-point number,
  library-specific rounding mode, or platform-dependent behavior
  participates anywhere in this computation (Document 95 §7.3).
- The selected candidates are `{ U[pos(0)], U[pos(1)], …, U[pos(K-1)] }`
  — `K` real chunks from the ordered candidate universe `U`.
- Selected chunks are numbered `1..K` in ascending `pos(i)` (equivalently
  ascending `chunk_idx`) order, and each excerpt trimmed to
  `MAX_CANDIDATE_CHARS` — Document 90 §5 step 4, unchanged (§5 above).

**This record ratifies this formula exactly as Document 95 §7 defines
it.** No alternative algorithm is substituted, and no term is simplified
or reinterpreted. The two alternatives Document 95 §7.4 evaluated and
rejected — endpoint reservation with a separately-parameterized interior
fill, and a hash/reservoir-based strategy requiring its own endpoint-
forcing step — are not adopted here either; this record ratifies exactly
the third: deterministic evenly-spaced index selection over the complete
`[0, N-1]` interval, formalized with exact integer arithmetic.

---

## 7. Correctness Properties (ratified — Document 95's proofs accepted without re-derivation)

**Accepted from Document 95 §10, verified this session to be
mathematically sound and not re-derived independently by this record:**

- **Lemma 1 (exact endpoints).** For every `K ≥ 2` and `N > K`:
  `pos(0) = 0` and `pos(K-1) = N-1`, **exactly**, by direct algebraic
  consequence of the formula — not as a fallback, not approximately.
- **Lemma 2 (strict monotonicity).** `pos(i+1) > pos(i)` for every
  `i = 0, …, K-2`, because `N - 1 ≥ K = m + 1` (a consequence of the
  `N > K` precondition), which forces each successive integer-division
  quotient to strictly increase.
- **Corollary.** From Lemmas 1–2: exactly `K` distinct integer positions
  are produced, in strictly ascending order, with no duplicate, already
  sorted, always including position `0` and position `N-1`.
- **Determinism / reproducibility.** Every operation is integer addition,
  multiplication, and floor division — exactly specified, with no
  floating point, no locale, no hash seed, no wall-clock or random input.
  Identical `(N, K)` produces bit-identical output on every invocation,
  on every platform.
- **Model-output independence.** `pos(i)` is a pure function of `i`, `N`,
  `K` alone; no model response or generation output appears anywhere in
  the formula, and candidate selection precedes generation in the
  pipeline (Document 90 §4.2/§10), so no such value could even be
  available at this step.
- **Bound.** No more than `K` candidates are ever produced (`i` ranges
  over exactly `K` values).

**These properties satisfy, in full, every invariant Document 90 already
required of candidate selection** (ordered universe, `N ≤ K` → all
chunks, `N > K` → exactly `K`, first/last coverage, determinism,
reproducibility, model-output independence, the `MAX_CANDIDATE_CHUNKS`
bound, sorted output, deterministic numbering) — **ratified as satisfied
by this corrected algorithm, not by the original one.**

---

## 8. Boundary Conditions (ratified from Document 95 §8)

- **`N ≤ K`** (including `N = 0` and `N = 1`): unchanged from Document 90
  §5 step 1 — every chunk in `U` is selected. This branch never invokes
  §6's formula.
- **`N = K` exactly**: falls into the `N ≤ K` branch; the `N > K`
  procedure is never invoked.
- **Minimum valid `K`**: **`K = 2`** is the minimum value for which the
  `N > K` procedure is defined and satisfies both endpoint invariants.
  With `K = 2`: `m = 1`, `h = 0`, giving `pos(0) = 0` and `pos(1) = N-1`
  exactly — i.e., `K = 2` always yields precisely `{0, N-1}`.
- **`K = 1` — the conflict, resolved explicitly, not left ambiguous**:
  `K = 1` is **not a valid `MAX_CANDIDATE_CHUNKS` configuration** under
  this amendment. Two independent reasons, both ratified from Document
  95 §8.2: (a) mathematically, a single selected slot cannot hold two
  distinct required values (`U[0]` and `U[N-1]`) whenever `N > 1`, so no
  algorithm — this one or any other — could satisfy the first/last
  invariant with `K = 1` and `N > 1`; (b) mechanically, §6's formula sets
  `m = K - 1 = 0` when `K = 1`, making the division in `pos(i)`
  **undefined**. Document 90 itself states no minimum value for `K`
  anywhere (confirmed absent by direct search of its text, both in
  Document 95's own provenance and re-confirmed by this record, §17)
  — this amendment closes that gap by establishing, as part of the
  ratified architecture, that **`MAX_CANDIDATE_CHUNKS` (`K`) must be
  configured as an integer `≥ 2`**, globally, independent of any
  particular filing's `N` (because `K` is a single, fixed,
  deployment-wide operational-configuration constant, not chosen per
  request). This floor does not change Document 90's recommended
  operational value (`≈ 60`), which already satisfies it by a wide
  margin — it only makes explicit a precondition Document 90 left
  unstated.

---

## 9. Preservation of Unaffected Document 90 Architecture

**Ratified as unchanged, exactly as Document 90 already specifies and
exactly as Document 95 §12 scoped this amendment — none of the following
is reinterpreted, weakened, extended, or reopened by this record:**

| Preserved element | Status |
|---|---|
| Candidate universe definition (ordered `chunk_idx`-ascending `filing_chunks`) | Unchanged |
| Coverage disclosure (`coverage_boundaries` machine-readable strings) | Unchanged |
| Partial coverage semantics — never proof of exhaustiveness | Unchanged |
| Partial coverage does **not**, by itself, imply `insufficient_evidence` | Unchanged |
| `state` governed solely by Document 87 Revision 2 §9.1/§9.2 | Unchanged |
| Recoverable retrieval degradation (BM25-only; empty-result sampling) | Unchanged (its shared selection shape now uses the §6 formula, per §5 above) |
| Unrecoverable infrastructure failure → existing `502 infrastructure_error` | Unchanged |
| Zero-content filing as a data condition, never 404/502 | Unchanged |
| At-most-one logical answer-generation request | Unchanged |
| Zero generation on deterministic empty/zero-content paths | Unchanged |
| No repair generation; no refinement loop | Unchanged |
| Deterministic citation-structure validation; `FilingQACitationStructureError` module-internal | Unchanged |
| Semantic grounding as an evaluation concern, not a runtime gate | Unchanged |
| AH-1 | Unchanged, untouched (§14) |
| AH-2 | Unchanged, untouched (§14) |
| DRS boundary (blocked, outside M16) | Unchanged (§15) |
| BYOK | Unchanged (§16) |
| SSRF | Unchanged (§16) |
| Owner-scoped jobs; shared filing corpus | Unchanged (§16) |
| SSE (`TraceEvent` framing, `final`-frame semantics) | Unchanged |
| Output bounds (operational config, citation-safe degradation) | Unchanged |
| Observability | Unchanged (§16) |
| Security posture generally | Unchanged (§16) |
| Testing-architecture boundaries | Unchanged |
| Deployment constraints (no topology change, single-instance invariant) | Unchanged |

---

## 10. Document 94 Status and Required Subsequent Revision

**Explicitly, and without ambiguity:**

- **Document 94 remains BLOCKED.** This ratification does not lift that
  block.
- **This record does NOT ratify Document 94.**
- **This ratification does NOT itself authorize implementation** — of
  any kind, in any scope.
- **Document 94 must be separately revised** — a narrow, targeted
  revision limited to updating its §9 candidate-selection restatement so
  it exactly matches the algorithm ratified in §6 above. No other part
  of Document 94 is presumed to need change by this record; that
  determination belongs to the revision task itself.
- **The revised Document 94 must undergo a fresh CTO review** — the
  original review that blocked Document 94 does not carry forward to a
  revised text; a revision is reviewed on its own.
- **Document 94 must then be separately ratified** — via the same
  established mechanism (a new ratification record) — before
  implementation authorization becomes effective.

**None of these steps is performed, implied, or pre-approved by this
record.**

---

## 11. Governance Act Performed

**DOCUMENT 95 — D90 CANDIDATE-SELECTION ARCHITECTURE AMENDMENT DECISION
IS FORMALLY RATIFIED**, exactly as reviewed and approved. This is the
**single** governance act this record performs. It:

- **confirms** the corrected algorithm and its proofs exactly as
  Document 95 §6–§10 already recorded;
- **does not** re-derive, redesign, extend, or reinterpret that
  algorithm;
- **does not** modify Document 95, Document 90, Document 91, Document
  93, or Document 94 — each stands exactly as previously written;
- **does not** create any new architecture decision beyond what Document
  95 already proposed;
- **does not** authorize implementation, Document 94's ratification, or
  any later governance stage (§12, §19).

**This record is self-effective upon its own CTO sign-off** — it does
not defer its own effect to a further, subsequent ratification-of-
Document-96 wrapper. No Document 97 is created or required.

---

## 12. Explicit Implementation Non-Authorization

**Ratifying Document 95 does NOT authorize, and must not be read to
authorize, any of the following:**

- M16 implementation, of any kind;
- source-code changes;
- test changes;
- configuration changes;
- MongoDB schema, collection, index, or migration work;
- Redis persistence or any Redis component;
- LangGraph node or topology changes;
- frontend implementation;
- evaluation infrastructure;
- deployment or release;
- commit;
- push;
- merge;
- Document 94's ratification (§10);
- any revision of Document 94 (§10) — that revision is a separate,
  future task, not performed here;
- any new architecture decision beyond the one Document 95 already
  proposed and this record ratifies.

**Architecture-amendment ratification does not constitute implementation
authorization.** These remain two distinct, sequential governance acts;
this record performs only the first, for the amendment, and does not
even perform the second for Document 90 as a whole — Document 94's own,
separate, still-blocked authorization gate is untouched.

---

## 13. Contract / API Preservation

**The Document 87 Revision 2 API contract (ratified through Documents
88/89/92) is untouched by this record — it was never in this amendment's
scope.** Document 95's amendment operates entirely **behind** the
contract line, on an internal candidate-selection mechanism with no
externally observable effect: the request/response shapes, the closed
`state` enum and its Document 87 R2 §9.1/§9.2 determination, the citation
convention, the error taxonomy, the job/SSE semantics, and every other
contract term remain exactly as ratified. This record does not alter,
weaken, extend, or reinterpret Document 87 Revision 2, Document 88,
Document 89, or Document 92 in any way.

---

## 14. AH-1 / AH-2 Preservation

**AH-1** (the M15 `report`-mode structured-schema resolution) is
untouched and not reinterpreted by Document 95 or by this record — it
was never in scope.

**AH-2** (the process-local, TTL-bounded, in-process transient result
buffer) is likewise untouched: this amendment concerns only how
candidates are *selected* before generation, not how a completed answer
is *retained* after it. No change to the buffer mechanism, its
deployment invariant, its owner-scoped read, its TTL/eviction behavior,
or its "no cross-process reconstruction" constraint is made, implied, or
authorized by this record.

---

## 15. DRS Boundary

**Durable Research Sessions remain BLOCKED and outside M16**, exactly as
Document 90 §2/§25 and every prior ratification in this chain already
establish. This amendment concerns a deterministic, stateless selection
computation over a single filing's already-loaded chunks — it introduces
no state, no persistence, and no research-session concept of any kind.
This record does not resolve, pre-empt, schedule, or authorize any DRS
work.

---

## 16. Security / Operational Boundaries

**Unaffected, unchanged, not reinterpreted by this record:**

- **BYOK** — per-request contextvar threading; `llm_api_key` never
  persisted or logged; this amendment touches no LLM-call code path.
- **SSRF** — `require_admin` + `assert_public_url`, and the established
  `400`-with-no-`type` SSRF-guard response, all unchanged; this
  amendment touches no BYOK/base-URL handling.
- **Owner-scoped jobs; shared filing corpus** — unchanged; this
  amendment touches no authorization or ownership logic.
- **Observability** — the `pipeline.filing_qa` span and
  `filing_qa_runs_total{outcome}` counter Document 90 §16 specifies are
  unaffected; this amendment adds no new telemetry and removes none.
- **Deployment** — no topology change; the single-instance operational
  invariant (§14's AH-2, `RUNNING_TASKS`, the auth rate-limiter) is
  carried forward unchanged; this amendment is a pure, in-process,
  stateless computation change with no deployment implication.

---

## 17. Provenance

Recorded by **read-only** `git` inspection this session on 2026-09-12.
**No `git` mutation was performed** — no `add`/stage, no `commit`, no
`push`, no `amend`, no `rebase`, no `merge`, no `reset`, no `restore`, no
`stash`, no `clean`.

- `git rev-parse HEAD` = `git rev-parse origin/main` =
  `f8c06649e94f45c388bbecf3eeedb9e5340f2024` (`f8c0664`, *"feat(m15):
  implement change brief"*); `git rev-list --left-right --count
  origin/main...HEAD` = `0	0` — clean upstream tracking, no divergence.
- Document number 96 was verified free before creation (highest existing
  Backend & AI governance document was 95; no Document 96 existed prior
  to this task).
- **Documents 63–95 were read (or, for documents authored earlier this
  session, re-confirmed from session state), not modified.** Document
  90's §5 text and its absence of any minimum-`K` statement were
  re-confirmed; Document 91, Document 93, and Document 94 were
  re-confirmed to record the architecture-ratification chain and the
  blocked implementation-authorization proposal respectively, neither
  reopened nor reinterpreted here.
- No source code, test, schema, index, migration, route, handler,
  LangGraph node, prompt, retrieval/RAG code, MongoDB collection, Redis
  component, provider, configuration, evaluation-infrastructure,
  metrics-catalog, deployment, or frontend file was created or modified.
  `.gitignore` was not modified.
- The working tree is **not** Git-clean. It contains known, pre-existing,
  unrelated items this document does **not** stage, modify, rename,
  delete, or clean:

  ```text
   M web/features/workspace-home/ui/CompanySearch.test.tsx        (pre-existing, unrelated — not touched)
  ?? backend/evaluation/self_consistency/phase_h1_generalization_matrix/  (untracked, M11 evidence — not touched)
  ?? both / NOT / expect / empty) / current_period_end` / K,      (untracked, stray shell-tooling artifacts predating this task — not touched)
  ?? docs/backend_engineering/67_...md through 95_...md           (pre-existing untracked governance documents — not modified)
  ```

- **One additional stray artifact was observed and is flagged, not
  silently absorbed into the list above**: an empty, 0-byte file named
  `{p}` is present in the repository root. It was not present before this
  session's prior task (Document 95's creation) and appears to be an
  inadvertent byproduct of that task's own shell-based arithmetic
  verification step, not a pre-existing user artifact and not created by
  this task. **This record does not delete, modify, or otherwise touch
  it** — this task authorizes no cleanup, and removing even a
  self-inflicted stray file is outside this record's narrow scope; it is
  named here for transparency and left for the user's own disposal.
- This document adds one further untracked file — itself
  (`docs/backend_engineering/96_Document95_Candidate_Selection_Architecture_Amendment_Ratification_Record.md`).
  It is untracked and not yet version-controlled. Staging or committing
  it is a separate, subsequently CTO-authorized step, not performed here.

---

## 18. Resulting Governance State

- **Document 95 stands formally ratified**, effective immediately upon
  this record.
- **The candidate-selection portion of Document 90 §5 is amended**
  exactly as ratified in §6–§8 above; **all other Document 90 decisions
  remain exactly as previously ratified** through Documents 91/93 (§9).
- **Document 94 remains BLOCKED.** It is not ratified, not revised, and
  not implementable by virtue of this record (§10, §12).
- **M16 implementation remains NOT authorized.**
- The Document 87 Revision 2 API contract (through Documents 88/89/92)
  is unaffected and remains ratified exactly as before (§13).
- AH-1, AH-2, the DRS boundary, and every security/operational
  constraint named in §14–§16 remain preserved exactly as before.

---

## 19. Next Governance Artifact

**In strict order, none collapsed, none performed here:**

1. A **separate, narrowly scoped revision of Document 94**, updating
   only its candidate-selection restatement (§9) to reference the
   algorithm ratified in §6 above.
2. **A fresh CTO review of that revised Document 94.**
3. **A separate ratification of the revised Document 94** — via the same
   established mechanism, a new ratification record.
4. **Only then** does M16 implementation authorization actually take
   effect, and only then may implementation begin — strictly within
   whatever scope that ratified, revised Document 94 ultimately
   authorizes.

**This record performs none of steps 1–4.** It performs exactly one
governance act — ratifying Document 95 — and stops there.

---

**🟢 DOCUMENT 95 — CTO RATIFIED / ACCEPTED. THE CORRECTED CANDIDATE-
SELECTION ALGORITHM — `m = K-1`, `h = floor(m/2)`,
`pos(i) = floor((i·(N-1)+h)/m)` FOR `i = 0..K-1`, DEFINED FOR `N > K` AND
`K ≥ 2` — IS NOW THE RATIFIED AMENDMENT TO DOCUMENT 90 §5, PROVEN (LEMMA
1: EXACT ENDPOINTS `pos(0)=0`, `pos(K-1)=N-1`; LEMMA 2: STRICT
MONOTONICITY ⇒ EXACTLY `K` DISTINCT, SORTED, DUPLICATE-FREE POSITIONS) TO
SATISFY EVERY INVARIANT DOCUMENT 90 REQUIRES: `N ≤ K` SELECTS ALL CHUNKS
(UNCHANGED); `N > K` SELECTS EXACTLY `K`, ALWAYS INCLUDING THE FIRST AND
LAST CHUNK, DETERMINISTICALLY, REPRODUCIBLY, INDEPENDENTLY OF MODEL
OUTPUT, BOUNDED BY `MAX_CANDIDATE_CHUNKS`, ORDERED BY `chunk_idx`. `K = 1`
IS EXPLICITLY RESOLVED AS AN INVALID CONFIGURATION (MATHEMATICALLY
INCOMPATIBLE WITH DUAL-ENDPOINT COVERAGE WHENEVER `N > 1`, AND UNDEFINED
IN THE FORMULA); `K = 2` IS THE MINIMUM VALID CONFIGURATION, YIELDING
EXACTLY `{0, N-1}`. EVERY OTHER DOCUMENT 90 DECISION — CANDIDATE UNIVERSE
DEFINITION, COVERAGE DISCLOSURE, PARTIAL-COVERAGE SEMANTICS AND ITS
NON-DETERMINATION OF `insufficient_evidence`, DOCUMENT 87 R2 §9.1/§9.2
STATE GOVERNANCE, RECOVERABLE/UNRECOVERABLE RETRIEVAL DEGRADATION HANDLING,
ZERO-CONTENT DATA-CONDITION BEHAVIOR, THE AT-MOST-ONE-GENERATION INVARIANT,
NO REPAIR/REFINEMENT GENERATION, DETERMINISTIC CITATION-STRUCTURE
VALIDATION, SEMANTIC GROUNDING AS AN EVALUATION CONCERN, AH-1, AH-2, THE
DRS BOUNDARY, BYOK, SSRF, OWNER-SCOPED JOBS, SSE, OUTPUT BOUNDS,
OBSERVABILITY, SECURITY, TESTING BOUNDARIES, AND DEPLOYMENT CONSTRAINTS —
REMAINS EXACTLY AS PREVIOUSLY RATIFIED, UNTOUCHED BY THIS RECORD. DOCUMENT
90, DOCUMENT 91, DOCUMENT 93, AND DOCUMENT 94 ARE NOT MODIFIED. **DOCUMENT
94 REMAINS BLOCKED** — THIS RECORD DOES NOT RATIFY DOCUMENT 94 AND DOES
NOT AUTHORIZE M16 IMPLEMENTATION, SOURCE-CODE CHANGES, TESTS,
CONFIGURATION CHANGES, MONGODB, REDIS, LANGGRAPH, FRONTEND, EVALUATION
INFRASTRUCTURE, DEPLOYMENT, RELEASE, COMMIT, PUSH, OR MERGE. DOCUMENT 94
MUST BE SEPARATELY, NARROWLY REVISED TO REFERENCE THIS RATIFIED ALGORITHM,
MUST UNDERGO ITS OWN FRESH CTO REVIEW, AND MUST BE SEPARATELY RATIFIED
BEFORE IMPLEMENTATION AUTHORIZATION BECOMES EFFECTIVE — NONE OF THAT IS
PERFORMED, IMPLIED, OR PRE-APPROVED HERE. NO DOCUMENT 97 IS CREATED; THIS
RECORD IS THE SELF-EFFECTIVE, TERMINAL RATIFICATION ACT FOR DOCUMENT 95.
NO GIT STATE WAS STAGED, COMMITTED, PUSHED, MERGED, REBASED, RESET,
CLEANED, STASHED, OR AMENDED. `HEAD = origin/main = f8c0664`, `0	0`
DIVERGENCE. DOCUMENTS 63–95 WERE READ, NOT MODIFIED; THE ONLY FILE THIS
TASK CREATES IS THIS DOCUMENT.**

DOCUMENT 96 D95 CANDIDATE-SELECTION ARCHITECTURE AMENDMENT RATIFICATION RECORD COMPLETE — AWAITING CTO REVIEW
