# 95 — D90 Candidate-Selection Architecture Amendment Decision

**Status:** 🟡 **DRAFT / PENDING CTO REVIEW — PROPOSED NARROW ARCHITECTURE
AMENDMENT TO DOCUMENT 90. NOT RATIFIED. THIS DOCUMENT DOES NOT RATIFY
ITSELF AND DOES NOT AUTHORIZE IMPLEMENTATION. DOCUMENT 94 REMAINS
BLOCKED.** This document proposes a narrowly scoped correction to exactly
one architectural mechanism in
[Document 90](90_M16_Filing_QA_Architecture_Decision_Pack.md) §5 — the
deterministic candidate-selection algorithm used when a filing's ordered
chunk universe `U` (size `N`) exceeds `MAX_CANDIDATE_CHUNKS` (`K`). The
existing mechanism does not mathematically guarantee the last-chunk
coverage it claims (§4). This document proposes a replacement algorithm,
proves it satisfies every invariant Document 90 already requires, and
does **not** touch any other part of Document 90, any other governance
document, or any source code.

**Type:** Governance / architecture amendment proposal (documentation
only — no source code, test, configuration, schema, migration, index,
route, LangGraph node, MongoDB collection, Redis usage, provider, or
frontend file created or modified to produce it; Documents 63–94 read,
not modified. The only file this task creates is this document.

**Date:** 2026-09-12.

**Precedent / lineage.** This document follows the same standalone,
narrowly-scoped amendment-decision form already established by
[Document 77](77_D75_Section14_Testing_Floor_Clarification_and_Amendment_Decision.md)
(a targeted correction to one section of a prior, already-ratified
decision, proposed for its own separate CTO review and ratification,
without reopening or redesigning the rest of that decision). Document 77
amended Document 75 §14; this document amends Document 90 §5 — one
mechanism, nothing broader. It does not reinterpret Document 87 Revision
2, Document 88, Document 89, Document 91, Document 92, or Document 93,
and it does not modify Document 90's text directly — an architecture
amendment, like every prior ratification act in this chain, is recorded
as a separate document, not a silent edit to the document it amends.

---

## 1. Purpose

Document 94 — the M16 Filing Q&A Implementation Authorization Decision —
was reviewed and found **BLOCKED**: it faithfully carried forward
Document 90 §5's deterministic candidate-selection requirement, and that
requirement contains a mathematical defect (§4). Implementation cannot be
authorized against an architecture that does not actually guarantee what
it claims to guarantee. This document exists to:

1. name the exact defect and prove it is real (§2–§4);
2. propose a corrected, mathematically valid, implementation-unambiguous
   replacement algorithm, and prove its correctness (§7, §10);
3. state precisely what is, and is not, changed (§5, §12);
4. record the resulting effect on Document 94 without modifying it (§13);
5. state explicitly that this document does not itself ratify anything,
   does not authorize implementation, and does not lift Document 94's
   blocked status (§14, §17).

---

## 2. Triggering Defect

Document 94 §9 ("Deterministic Retrieval / Candidate Requirements")
restated Document 90 §5's capping algorithm verbatim, as its purpose
requires — an implementation-authorization decision must faithfully
carry forward the ratified architecture, not silently correct it.
**Faithfully carrying forward a defective requirement makes the
authorization itself defective.** CTO review of Document 94 traced the
requirement back to its source and found the defect originates in
Document 90 §5, not in Document 94's restatement of it. Document 94 is
therefore correctly blocked, and the fix belongs at the architecture
layer (this document), not inside Document 94.

---

## 3. Exact D90 Requirement Being Amended

Quoted verbatim from
[Document 90 §5](90_M16_Filing_QA_Architecture_Decision_Pack.md), the
"deterministic capping when the universe exceeds `MAX_CANDIDATE_CHUNKS`"
steps 1–3 (re-verified against the current file this session):

> 1. let `U` = the ordered candidate universe, `N = len(U)`,
>    `K = MAX_CANDIDATE_CHUNKS`; if `N ≤ K`, every chunk is a candidate;
> 2. else `stride = ceil(N / K)`; select `U[0], U[stride],
>    U[2·stride], …` while fewer than `K` are chosen;
> 3. if integer striding yields fewer than `K`, append the
>    not-yet-selected chunks with the **highest `chunk_idx`** in order
>    until exactly `K` are selected — this guarantees the filing's
>    **first and last chunk are always represented** (head-and-tail
>    coverage, never a silently dropped tail);

Document 90 asserts this "guarantees the filing's first and last chunk
are always represented." **§4 shows this assertion is false in general.**

**Step 1 (the `N ≤ K` branch) is not defective and is not amended by this
document** — see §5.

---

## 4. Mathematical Inconsistency

**Claim.** Steps 2–3 above do not guarantee `U[N-1]` (the last chunk) is
selected, even though they always correctly select `U[0]` (the first
chunk, trivially, as the first stride point).

**Proof by counterexample.**

- **`N = 10, K = 3`**: `stride = ceil(10/3) = 4`. Striding selects
  `U[0], U[4], U[8]` — after `U[8]`, three candidates have already been
  chosen (`0, 4, 8` — three indices), so striding stops. Step 3's
  "append if fewer than `K`" clause **does not fire**, because exactly
  `K = 3` were already selected by striding alone. **`U[9]` (the last
  chunk, `N−1 = 9`) is never selected.**
- **`N = 8, K = 3`**: `stride = ceil(8/3) = 3`. Striding selects
  `U[0], U[3], U[6]` — three candidates, step 3 does not fire.
  **`U[7]` (the last chunk, `N−1 = 7`) is never selected.**

**General characterization of when the defect fires.** Step 3's rescue
clause only triggers when strided selection alone produces **fewer**
than `K` points before it would naturally reach or pass `U[N-1]`. But
striding a fixed step size from `0` can land **exactly** on `K` points
strictly before index `N-1` whenever `(K-1) · stride < N-1`, i.e.
whenever `stride = ⌈N/K⌉` is large enough that `K` full strides fit
inside `[0, N-1)` without needing to reach the endpoint. This is a
common case, not a rare edge case — it occurs for a large fraction of
`(N, K)` pairs, including the two counterexamples above and, as §9's
worked examples show, several of the required test cases.

**Conclusion.** Document 90 §5 steps 2–3, as written, are internally
inconsistent: they claim an invariant (last-chunk coverage) that the
stated procedure does not, in general, produce. This is an architectural
defect, not an implementation bug — no implementation could satisfy
Document 90 §5 as literally written and also satisfy its own stated
head-and-tail-coverage invariant, for the `(N, K)` pairs identified
above. **This is the sole defect this document addresses.**

---

## 5. Scope of Amendment

**This amendment changes exactly one thing: Document 90 §5's steps 2–3
(the selection procedure used when `N > K`).** Nothing else in Document
90 §5, and nothing in any other section of Document 90, is redesigned,
reinterpreted, narrowed, or extended by this document.

**Explicitly unchanged, restated only for continuity (not amended):**

- Document 90 §5 step 1 (`N ≤ K` → every chunk is a candidate) —
  unchanged;
- Document 90 §5 step 4 (re-sort by `chunk_idx`, number `1..K`, trim to
  `MAX_CANDIDATE_CHARS`) — unchanged; §7 below shows the new algorithm
  already produces its output pre-sorted, so this step remains a
  defensive no-op, exactly as before;
- the **same selection shape** is reused, per Document 90 §5's own
  cross-reference, for the empty-retrieval-result degradation fallback
  ("a deterministic evenly-spaced sample across the ordered filing") —
  since Document 90 already defines that fallback as sharing the capping
  mechanism's shape, correcting the shared mechanism necessarily and
  consistently corrects both call sites named in Document 90 §5 without
  this being a new design decision; **no new call site beyond the two
  Document 90 §5 already names is introduced.**
- every other Document 90 decision (§6–§24) — unaffected; restated in
  full in §12.

---

## 6. Candidate-Selection Invariants (unchanged from D90 — restated as the amendment's acceptance criteria)

The amended algorithm (§7) must satisfy every one of the following,
exactly as Document 90 already requires:

| # | Invariant |
|---|---|
| I-1 | `N ≤ K` → select every candidate chunk. |
| I-2 | `N > K` → select **exactly** `K` candidate chunks. |
| I-3 | `N > K` → the **first** chunk `U[0]` is always selected. |
| I-4 | `N > K` → the **last** chunk `U[N-1]` is always selected. |
| I-5 | Selection is **deterministic** — a pure function of `(N, K)` (equivalently of `(U, K)`, since `U`'s size is `N`). |
| I-6 | Selection is **reproducible** — identical output on every repeated invocation with the same `(N, K)`. |
| I-7 | Selection is **independent of model output** — no model call, model response, or randomness participates in the computation. |
| I-8 | Selection is **bounded** by `K = MAX_CANDIDATE_CHUNKS` — never more than `K` candidates. |
| I-9 | Selected chunks are **sorted by `chunk_idx`** in the final candidate list. |
| I-10 | **Deterministic numbering** (`1..K`, ascending `chunk_idx` order) is preserved. |
| I-11 | **No duplicate** chunk is selected. |

---

## 7. Candidate-Selection Algorithm (proposed amendment — implementation-unambiguous)

### 7.1 Inputs

- `U` — the ordered candidate universe: `U[0], U[1], …, U[N-1]`, the
  filing's persisted chunks in ascending `chunk_idx` order (unchanged
  definition, Document 90 §5 / §6). `U[i]` denotes the chunk at ordinal
  position `i`; each carries its own real `chunk_idx` value, itself
  strictly increasing in `i`.
- `N = len(U)`, a non-negative integer.
- `K = MAX_CANDIDATE_CHUNKS`, a fixed, positive, operationally-configured
  integer (Document 90 §13/§21; unchanged as an operational-configuration
  concept — only its **minimum permitted value** is newly constrained by
  this amendment, §8.2).

### 7.2 Branch selection (unchanged, restated)

- If `N ≤ K`: select every chunk in `U`, in order. (Document 90 §5 step
  1 — not amended.)
- If `N > K`: apply the procedure below. **This is the only branch this
  amendment changes.**

### 7.3 The amended procedure (`N > K`)

**Precondition:** `K ≥ 2` (established as a hard architectural
precondition by this amendment — §8.2). If this precondition is
violated, the configuration itself is invalid; the procedure below is
not defined for `K < 2` and must not be run against such a
configuration.

1. Let `m = K − 1`. (`m ≥ 1`, by the precondition.)
2. Let `h = m div 2` (integer floor division; `h` is a fixed rounding
   offset with `0 ≤ h < m`).
3. For each `i = 0, 1, …, K−1`, compute the ordinal position:

   ```text
   pos(i) = ( i · (N − 1) + h )  div  m
   ```

   using **integer arithmetic only** — floor (truncating) integer
   division throughout, at every step. No floating-point number,
   library-specific rounding mode, or platform-dependent behavior
   participates anywhere in this computation.
4. The selected ordinal-position set is `{ pos(0), pos(1), …, pos(K−1) }`.
   By Lemma 1 and Lemma 2 (§10), this set already contains **exactly
   `K`** distinct integers, **strictly increasing** in `i`, with
   `pos(0) = 0` and `pos(K−1) = N−1` **exactly** (not approximately, not
   as a fallback — proven, §10).
5. The selected candidates are `{ U[pos(0)], U[pos(1)], …, U[pos(K-1)] }`
   — already in ascending `chunk_idx` order (Lemma 2), so the Document 90
   §5 step 4 "re-sort by `chunk_idx`" is a defensive no-op, unchanged in
   its place in the pipeline.
6. Number the selected chunks `1..K` in that (already-ascending) order,
   and trim each excerpt to `MAX_CANDIDATE_CHARS` — Document 90 §5 step 4,
   unchanged.

**This procedure entirely replaces Document 90 §5 steps 2–3.** It
introduces no new external dependency, no model call, and no
non-determinism.

### 7.4 Why this algorithm, and not the other two considered

Three classes of algorithm were evaluated, as required:

1. **Endpoint reservation** — reserve `U[0]` and `U[N-1]`, then
   deterministically fill the remaining `K−2` interior positions. This
   is mathematically viable but requires **three separate sub-cases**
   to avoid its own new edge-case defects: `K = 2` (zero interior
   points — trivial), `K = 3` (exactly **one** interior point — an
   evenly-spaced *ratio* formula over 1 point is undefined, so this case
   needs its own "take the midpoint" special rule), and `K ≥ 4`
   (interior points spaced by a `(K−2)`-term formula over the *open*
   interior range `(0, N−1)`, which itself is a second, differently-
   parameterized instance of the same rounding problem this amendment
   already has to solve once). Adopting this approach would mean solving
   the identical rounding problem **twice**, with an extra special case
   at `K = 3`, for no additional guarantee — Document 90's own invariants
   (§6) do not ask for interior evenness that this approach delivers any
   better than option 2.
2. **Deterministic evenly-spaced index selection over the complete
   `[0, N−1]` interval** (the amendment's chosen approach, formalized in
   §7.3 with exact integer arithmetic rather than a floating-point
   `linspace`-and-round). This is the textbook technique for selecting
   `K` evenly-spaced points over a closed interval that always includes
   both endpoints **by construction of the formula itself**, not as a
   post-hoc fallback: setting `i = 0` and `i = K−1` in the linear formula
   `pos(i) = i·(N−1)/(K−1)` yields exactly `0` and exactly `N−1` for
   **every** valid `K ≥ 2`, with **one** formula, **no** special-cased
   `K` value, and **no** second rounding problem to solve. This is why
   it is preferred over option 1 — not because it is simpler to *state*,
   but because it has **strictly fewer cases to prove correct** (one
   proof, §10, covers every `K ≥ 2` uniformly) while delivering every
   invariant §6 requires.
3. **A different deterministic bounded strategy** (e.g., a hash-based or
   reservoir-sampling selection) was considered and rejected: any such
   strategy would need its own explicit endpoint-forcing step (since
   generic reservoir/hash sampling has no notion of "always keep index
   0 and N−1"), reintroducing exactly the kind of fallback-shaped
   mechanism that produced the original defect (§4). No such strategy
   offers any advantage over option 2 for this problem, which is a
   coverage-selection problem, not a randomized-sampling problem.

**Option 2, formalized with exact integer arithmetic, is adopted.**

---

## 8. Boundary Conditions

### 8.1 `N ≤ K` (including `N = 0` and `N = 1`)

Unchanged from Document 90 §5 step 1: every chunk in `U` is selected.
When `N = 0`, the selected set is empty (a zero-content filing — handled
entirely outside this amendment, by Document 90 §5/§18's zero-content
data-condition path, unaffected). When `N = 1`, the single chunk is both
"first" and "last" simultaneously; the invariant is trivially satisfied.
**This branch never invokes §7.3's formula and is never subject to the
`K ≥ 2` precondition below** — but see §8.2 on why the precondition is
nonetheless set globally, not only for this branch.

### 8.2 Minimum valid `K`

**The amended algorithm requires `K ≥ 2` whenever the `N > K` branch
executes.** This is not a design preference — it is a **mathematical
necessity**: with `K = 1`, the `N > K` branch can only be reached when
`N > 1` (i.e., at least two distinct chunks exist), and a single
selected slot **cannot simultaneously hold two distinct required
values** (`U[0]` and `U[N-1]`, which are different chunks whenever
`N > 1`). No algorithm — this one or any other — can satisfy invariants
I-3 and I-4 with `K = 1` and `N > 1`. Separately, §7.3's formula sets
`m = K − 1 = 0` when `K = 1`, making step 3's division **undefined**
(division by zero) — the formula is not merely suboptimal at `K = 1`, it
is not defined there.

**Resolution — explicit, not left ambiguous:** `MAX_CANDIDATE_CHUNKS`
(`K`) **must be configured as an integer `≥ 2`.** This is a new,
explicit architectural precondition this amendment adds to Document 90's
operational-configuration requirements (Document 90 §13/§21) — Document
90 itself never states a minimum value for `K` (re-verified this session
by direct search of the current file text; no `K ≥ …` or minimum-`K`
statement exists anywhere in it), which is precisely the gap this
amendment closes. Because `K` is a single, fixed, deployment-wide
operational-configuration constant (not chosen per request or per
filing), and essentially every real filing has `N > 1` chunks, a
misconfigured `K = 1` would make the `N > K` branch undefined for nearly
every request — the precondition is therefore stated **globally**
(`K ≥ 2`, independent of any particular `N`), not merely "for filings
larger than `K`," so that a configuration-time check can reject it
before any request-time failure occurs. **`K = 1` is not a valid
`MAX_CANDIDATE_CHUNKS` configuration under this amendment.** Document
90's own recommended operational value (`≈ 60`) already satisfies
`K ≥ 2` by a wide margin — this precondition does not change the
recommended value, only formalizes a floor beneath it that was
previously unstated.

**How `N ≤ K` behaves under this floor:** unaffected — §8.1's branch has
no lower bound on `K` of its own (even a hypothetical, disallowed `K = 1`
would behave coherently in the `N ≤ K` branch alone, selecting whatever
`U` contains), but because `K` is configured once, globally, the `K ≥ 2`
floor is enforced regardless of which branch a given request happens to
take.

### 8.3 `N = K` exactly

Falls into the `N ≤ K` branch (§8.1) — every chunk selected, trivially
satisfying both endpoints. The `N > K` procedure is never invoked when
`N = K`.

---

## 9. Worked Examples

All values computed by hand, by direct application of §7.3
(`m = K−1`, `h = m div 2`, `pos(i) = (i·(N−1)+h) div m`).

| Case | `N` | `K` | `m` | `h` | `pos(0..K-1)` | Selected `chunk_idx` (0-based ordinal) | Notes |
|---|---|---|---|---|---|---|---|
| Required | 7 | 3 | 2 | 1 | `0, 3, 6` | `{0, 3, 6}` | last index `N−1=6` ✓ |
| Required (original counterexample) | 8 | 3 | 2 | 1 | `0, 4, 7` | `{0, 4, 7}` | last index `N−1=7` ✓ — **previously missing under the old algorithm (§4)** |
| Required (original counterexample) | 10 | 3 | 2 | 1 | `0, 5, 9` | `{0, 5, 9}` | last index `N−1=9` ✓ — **previously missing under the old algorithm (§4)**; also an `N % K ≠ 0` case (`10 % 3 = 1`) |
| Required | 11 | 4 | 3 | 1 | `0, 3, 7, 10` | `{0, 3, 7, 10}` | last index `N−1=10` ✓; `N % K ≠ 0` (`11 % 4 = 3`) |
| `N % K = 0` contrast (not required, shown for completeness) | 9 | 3 | 2 | 1 | `0, 4, 8` | `{0, 4, 8}` | last index `N−1=8` ✓; exact-division case behaves identically well |
| Minimum valid `K` | 6 | 2 | 1 | 0 | `0, 5` | `{0, 5}` | `K=2` always yields exactly `{0, N−1}` — proven generally in §10 |
| `N ≤ K` | 3 | 5 | — | — | *(branch not entered)* | `{0, 1, 2}` | every chunk selected (§8.1) |

**Every required example demonstrates first-chunk coverage (`pos(0)=0`),
last-chunk coverage (`pos(K-1)=N-1`), exactly `K` distinct ordinal
positions, and strictly ascending order** — including both of the exact
`(N, K)` pairs the triggering defect (§4) named as counterexamples to the
old algorithm.

---

## 10. Correctness / Reproducibility Reasoning

**Lemma 1 (exact endpoints).** For every `K ≥ 2` and every `N > K`:
`pos(0) = 0` and `pos(K−1) = N−1`, exactly.

*Proof.* `pos(0) = (0·(N−1)+h) div m = h div m`. Since `h = m div 2` and
`m ≥ 1`, we have `0 ≤ h < m` (integer floor division of `m` by `2`
always yields a value strictly less than `m` for `m ≥ 1`), so
`h div m = 0`. Hence `pos(0) = 0`.
`pos(K−1) = ((K−1)·(N−1)+h) div m = (m·(N−1)+h) div m`. Since
`m·(N−1)` is exactly divisible by `m` with quotient `N−1`, and
`0 ≤ h < m`, standard integer-division identity gives
`(m·(N−1)+h) div m = (N−1) + (h div m) = (N−1) + 0 = N−1`. Hence
`pos(K−1) = N−1`. ∎

**Lemma 2 (strict monotonicity ⇒ exactly `K` distinct, sorted values).**
For every `K ≥ 2` and every `N > K`: `pos(i+1) > pos(i)` for every
`i = 0, …, K−2`.

*Proof.* Let `a_i = i·(N−1) + h`, so `pos(i) = a_i div m`. Then
`a_{i+1} − a_i = (N−1)`. Because `N > K`, we have `N − 1 ≥ K = m + 1`,
i.e. `N−1 ≥ m+1`, so `a_{i+1} = a_i + (N−1) ≥ a_i + m + 1`. For any
non-negative integer `a` and integer `c ≥ m+1` (with `m ≥ 1`):
`(a+c) div m ≥ (a div m) + 1` — because writing `a = q·m + r` with
`0 ≤ r < m` gives `a + c ≥ q·m + r + m + 1 = (q+1)·m + (r+1)`, and
`r + 1 ≥ 1 > 0`, so `(a+c) div m ≥ q+1`. Applying this with `a = a_i`,
`c = N−1 ≥ m+1` gives `pos(i+1) = a_{i+1} div m ≥ (a_i div m) + 1 =
pos(i) + 1 > pos(i)`. ∎

**Corollary (I-2, I-5, I-6, I-8, I-9, I-11 — all follow from Lemmas 1–2).**
`i ↦ pos(i)` is defined for exactly `K` values of `i` (`0` through
`K−1`), is strictly increasing (Lemma 2), and hence produces **exactly
`K` distinct integers** in **strictly ascending order**, with **no
duplicate** (I-11), already **sorted** (I-9), **bounded** at `K` members
(I-8, since no more than `K` values of `i` are ever evaluated), and
**exactly `K`** are selected (I-2) — every one of these properties is a
direct mathematical consequence of the closed-form definition, not an
emergent or probabilistic property.

**I-3, I-4 (endpoints)** follow directly from Lemma 1.

**I-1** is unchanged (§8.1) and untouched by this proof.

**I-7 (model-output independence)** holds because `pos(i)` is defined
purely in terms of `i`, `N`, `K` (equivalently `m`, `h`) — no model
response, generation output, or any value produced during answer
generation appears anywhere in §7.3's formula. Candidate selection
**precedes** generation in the pipeline (Document 90 §4.2/§10), so no
such value could even be available at this step.

**I-5, I-6 (determinism, reproducibility)** hold because every operation
in §7.3 is integer arithmetic (addition, multiplication, floor
division) — operations that are exactly specified by the language
runtime for arbitrary-precision or fixed-width integers alike, with no
floating-point rounding mode, no locale, no hash-seed, and no wall-clock
or random input anywhere in the computation. The same `(N, K)` pair
produces bit-identical `pos(0..K-1)` on every invocation, on every
platform, forever.

**I-10 (numbering)** is unchanged from Document 90 §5 step 4, applied to
an already-sorted input (Lemma 2), so it behaves exactly as before.

---

## 11. Test Requirements (architecture-level — not implemented by this document)

**This document specifies the following as required test properties for
a future implementation to satisfy (Document 90 §20's testing-
architecture pattern, extended to cover this corrected algorithm) — it
does not write, generate, or execute any test.**

A future hermetic test suite for the corrected algorithm must verify:

1. `N ≤ K` selects **every** chunk in `U`, for representative `N` from
   `0` up to and including `K`.
2. `N > K` selects **exactly `K`** chunks, for a range of `(N, K)` pairs
   including at least the required cases in §9.
3. The **first** chunk (`pos(0) = 0`) is selected for every tested
   `(N, K)` with `N > K`.
4. The **last** chunk (`pos(K-1) = N-1`) is selected for every tested
   `(N, K)` with `N > K` — **explicitly including the two original
   counterexamples** (`N=10,K=3` and `N=8,K=3`) that the prior algorithm
   failed on.
5. **No duplicate** ordinal position appears in the selected set, for
   every tested `(N, K)`.
6. The selected set, listed in selection order, is already **sorted**
   ascending by `chunk_idx` — no case requires the defensive re-sort
   step to actually reorder anything.
7. **Deterministic repeated execution** — invoking the algorithm twice
   with identical `(N, K)` produces byte-identical output both times.
8. **Model-output independence** — the algorithm's output does not
   change when invoked with a fake `chat_fn` that returns different
   values across runs (there being no code path by which it could).
9. The **`MAX_CANDIDATE_CHUNKS` bound** is never exceeded — the selected
   set size never exceeds `K` for any tested `N`.
10. **The specific problematic `(N, K)` combinations from §4 and §9** are
    exercised as named regression cases, not merely covered incidentally
    by a general property test.
11. **Minimum valid `K` (`K = 2`)** — verified to always yield exactly
    `{0, N−1}` for every tested `N > 2`, and a configuration-time (or
    equivalent fail-fast) check rejecting `K < 2` is verified separately.
12. **Partial coverage remains compatible with `answered`** — a test
    exercising a capped/partially-covered candidate set (`N > K`) for
    which a fake `chat_fn` returns a well-grounded answer must still
    yield `state == "answered"` (per Document 90 §5.1/§5.2, unaffected
    by this amendment) **with** a `coverage_boundaries` entry — i.e., the
    corrected candidate-selection mechanism must not change, weaken, or
    interact with the separately-governed `state` determination in
    Document 87 R2 §9.1/§9.2.

---

## 12. Preservation of All Unaffected D90 Architecture

**Every one of the following remains exactly as Document 90 already
specifies, untouched by this amendment:**

| Preserved element | D90 source |
|---|---|
| Candidate universe definition (ordered `chunk_idx`-ascending `filing_chunks`) | §5, §6 |
| Coverage disclosure (`coverage_boundaries` machine-readable strings) | §5.1 |
| Partial coverage semantics — never proof of exhaustiveness | §5.1 |
| Partial coverage does **not**, by itself, imply `insufficient_evidence` | §5.1, §5.2 |
| `state` governed solely by Document 87 R2 §9.1/§9.2 | §5.1, §11 |
| Recoverable retrieval degradation (BM25-only; empty-result sampling) | §5 |
| Unrecoverable infrastructure failure → existing `502 infrastructure_error` | §5, §18 |
| Zero-content filing as a data condition, never 404/502 | §5, §18 |
| At-most-one logical answer-generation request | §10 |
| Zero generation on deterministic empty/zero-content paths | §10 |
| No repair generation; no refinement loop | §10 |
| Deterministic citation-structure validation; `FilingQACitationStructureError` module-internal | §11 |
| Semantic grounding as an evaluation concern, not a runtime gate | §11, §14 |
| AH-1 (untouched) / AH-2 (process-local, TTL-bounded buffer) | §8, §9 |
| DRS boundary (blocked, outside M16) | §2, §25 |
| BYOK (contextvar threading, key never logged) | §12 |
| SSRF (`require_admin` + `assert_public_url`) | §15 |
| Owner-scoped jobs; shared filing corpus | §15 |
| SSE (`TraceEvent` framing, `final`-frame semantics) | §16 |
| Output bounds (operational config, citation-safe degradation) | §13 |
| Observability (`pipeline.filing_qa` span, `filing_qa_runs_total`) | §16 |
| Security posture generally | §15 |
| Testing-architecture boundaries (semantic support out of the floor) | §20 |
| Deployment constraints (no topology change, single-instance invariant) | §21 |

**None of the above is reinterpreted, weakened, extended, or reopened by
this document.** The amendment's blast radius is exactly Document 90 §5
steps 2–3, as scoped in §5 above.

---

## 13. Impact on Document 94

- **Document 94 remains BLOCKED.** This document does not unblock it.
- **No implementation may begin** — Document 94 was never ratified, and
  this document does not ratify it, amend it, or supersede its blocked
  status.
- **After this amendment is itself reviewed and ratified**, Document 94
  will require a **separate, narrowly scoped revision** so that its
  candidate-selection requirements (Document 94 §9, which restates the
  now-superseded algorithm) exactly match the corrected algorithm in §7
  above. That revision is not performed here.
- **That Document 94 revision is a separate governance act**, requiring
  its own CTO review and its own ratification, exactly like every other
  stage in this chain — it is not implied, pre-approved, or fast-tracked
  by this document's eventual ratification.
- **This document does not itself authorize Document 94, does not
  authorize implementation, and does not authorize any further stage.**
  It is bounded strictly to proposing the corrected architecture.

---

## 14. Non-Authorization Boundary

**This document does NOT:**

- change Document 87 (Revision 2);
- change Document 88;
- change Document 89;
- change Document 90 outside the narrow candidate-selection amendment
  scoped in §5 (and even that change is *proposed*, not yet made — see
  §17);
- change Document 91;
- change Document 92;
- change Document 93;
- change Document 94;
- authorize implementation, of any kind;
- modify source code;
- modify tests;
- modify configuration;
- modify MongoDB (schema, collection, index, or migration);
- modify Redis;
- modify LangGraph;
- modify frontend code;
- modify evaluation infrastructure;
- authorize deployment;
- authorize release;
- authorize commit;
- authorize push;
- authorize merge;
- create Document 96 or any other new governance document beyond itself.

**This document also does NOT ratify itself, or the amendment it
proposes.** See §17.

---

## 15. Governance Lineage (preserved, not collapsed)

```text
D83 / 85     — FQA v1 scope + ratification                 🟢 CTO-RATIFIED
  ↓
D84 / 86     — M16 selection + ratification                🟢 CTO-RATIFIED
  ↓
D87 R2 → D88 → D89 → D92                                    🟢 RATIFIED — API contract chain (unchanged,
                                                                not touched by this document)
  ↓
D90          — M16 Architecture Decision Pack (original)    🟢 ARCHITECTURE-RATIFIED (via D91/D93) —
                                                                CONTAINS THE §5 DEFECT THIS DOCUMENT
                                                                ADDRESSES; NOT EDITED BY THIS DOCUMENT
  ↓
D91 → D93    — Architecture ratification chain              🟢 CTO-RATIFIED (unchanged, not touched)
  ↓
D94          — M16 Implementation Authorization Decision    🔴 BLOCKED — inherited D90 §5's defect;
                                                                NOT MODIFIED by this document
  ↓
D95 (THIS)   — D90 Candidate-Selection Architecture          🟡 DRAFT / PENDING CTO REVIEW — PROPOSED
                Amendment Decision                              ONLY. DOES NOT SELF-RATIFY.
  ↓
STOP — no ratification, no implementation authorization, no D94 correction is performed by this
       document
  ↓
[future, separate] Amendment ratification record             NOT CREATED HERE (next free document
                                                                number at the time of this proposal is
                                                                96 — subject to re-verification at the
                                                                time that record is actually created)
  ↓
[future, separate] Document 94 revision (candidate-selection  NOT CREATED HERE
                    requirements corrected to match §7)
  ↓
[future, separate] Document 94 revision's own CTO review      NOT CREATED HERE
                    and ratification
  ↓
Implementation authorization actually in effect               NOT REACHED
```

These are eight distinct governance acts and this document performs
exactly one of them: **proposing** the amendment. It does not perform, or
imply, any of the others.

---

## 16. Provenance

Recorded by **read-only** inspection this session on 2026-09-12. **No
`git` mutation was performed** — no `add`/stage, no `commit`, no `push`,
no `amend`, no `rebase`, no `merge`, no `reset`, no `restore`, no
`stash`, no `clean`. **No source code, test, configuration, or evaluation
artifact was modified.**

- `git rev-parse HEAD` = `git rev-parse origin/main` =
  `f8c06649e94f45c388bbecf3eeedb9e5340f2024` (`f8c0664`, *"feat(m15):
  implement change brief"*); `git rev-list --left-right --count
  origin/main...HEAD` = `0	0` — clean upstream tracking, no divergence.
- Document number 95 was verified free before creation (highest existing
  Backend & AI governance document was 94; no Document 95 existed prior
  to this task).
- **Document 90** was re-inspected this session: its §5 steps 1–4 were
  grepped and quoted verbatim (§3); a search for any existing minimum-`K`
  statement (`K ≥ …`, `K=1`, etc.) returned **no matches anywhere in the
  file**, confirming §8.2's finding that Document 90 states no such
  floor today.
- **Document 91, Document 93** were re-confirmed (from this session's own
  authorship) to record Document 90's architecture ratification without
  amendment — cited, not reopened, not reinterpreted.
- **Document 94** was re-confirmed (from this session's own authorship)
  to restate Document 90 §5's algorithm in its own §9 — the inherited
  defect this document traces (§2).
- **Documents 87 Revision 2, 88, 89, 92** — the API-contract chain — were
  confirmed unaffected; this document makes no claim about, and performs
  no action on, any of them.
- **Documents 63–94 were read (or, for documents authored earlier this
  session, re-confirmed from session state), not modified.**
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
  ?? both / NOT / expect / empty) / current_period_end` / K,      (untracked, stray shell-tooling artifacts — not created by this task, not touched)
  ?? docs/backend_engineering/67_...md through 94_...md           (pre-existing untracked governance documents — not modified)
  ```

- This document adds one further untracked file — itself
  (`docs/backend_engineering/95_D90_Candidate_Selection_Architecture_Amendment_Decision.md`).
  It is untracked and not yet version-controlled. Staging or committing
  it is a separate, subsequently CTO-authorized step, not performed here.

---

## 17. Ratification Requirement

**This document does not ratify itself, and does not ratify the
amendment it proposes.** The candidate-selection algorithm in §7 becomes
the authoritative, binding correction to Document 90 §5 **only** through
a separate, subsequent, explicit CTO ratification act — following the
identical established mechanism this governance chain has used for every
prior stage (a new, separately-numbered ratification record: Documents
74/76/78/80/82/85/86/88/89/91/92/93 all follow this pattern without
exception). Until that ratification occurs:

- Document 90 §5, as originally written, remains the document-of-record
  (defect and all) — this proposal does not silently supersede it;
- the algorithm in §7 is a **proposal only**, with no binding effect;
- Document 94 remains blocked;
- no implementation of any kind is authorized.

The next free document number at the time of this proposal is **96** —
this document does not create it, and the exact number belongs to
whichever future task creates that ratification record, verified free at
that time exactly as this document verified 95 free before creation
(§16).

---

## 18. Next Governance Act

**In strict order, none collapsed, none performed here:**

1. **CTO review of this document (Document 95).**
2. **If approved:** a separate, subsequent **ratification record**
   (anticipated as Document 96, subject to re-verification) formally
   ratifying the corrected candidate-selection algorithm as the binding
   amendment to Document 90 §5.
3. **A separate, narrowly scoped revision of Document 94**, updating only
   its §9 candidate-selection restatement to reference the corrected
   algorithm — no other part of Document 94 is expected to require
   change, but that determination belongs to the revision task itself,
   not this document.
4. **That Document 94 revision's own CTO review and ratification** — a
   further, separate act.
5. **Only then** does implementation authorization for M16 = Filing Q&A
   (FQA v1) actually take effect, and only then may implementation begin
   — strictly within whatever scope that ratified, revised Document 94
   ultimately authorizes.

**This document performs none of steps 1–5.** It is the input to step 1,
nothing more.

---

**🟡 DOCUMENT 95 — DRAFT / PENDING CTO REVIEW. NOT RATIFIED. THIS DOCUMENT
DOES NOT SELF-RATIFY AND DOES NOT AUTHORIZE IMPLEMENTATION. IT PROPOSES A
NARROWLY SCOPED CORRECTION TO EXACTLY ONE MECHANISM — DOCUMENT 90 §5's
DETERMINISTIC CANDIDATE-SELECTION ALGORITHM FOR `N > K` — REPLACING THE
`stride = ceil(N/K)` PROCEDURE, WHICH DOES NOT MATHEMATICALLY GUARANTEE
LAST-CHUNK COVERAGE (PROVEN BY COUNTEREXAMPLE AT `N=10,K=3` AND `N=8,K=3`,
§4), WITH A CLOSED-FORM INTEGER FORMULA `pos(i) = (i·(N−1)+h) div m`
(`m=K−1`, `h=m div 2`) THAT IS PROVEN (§10, TWO LEMMAS) TO SELECT EXACTLY
`K` DISTINCT, STRICTLY ASCENDING ORDINAL POSITIONS WITH `pos(0)=0` AND
`pos(K−1)=N−1` EXACTLY, FOR EVERY `K ≥ 2` AND `N > K` — SATISFYING EVERY
INVARIANT DOCUMENT 90 ALREADY REQUIRES (DETERMINISM, REPRODUCIBILITY,
MODEL-OUTPUT INDEPENDENCE, THE `MAX_CANDIDATE_CHUNKS` BOUND, SORTED
OUTPUT, NO DUPLICATES, FIRST-AND-LAST COVERAGE) WITHOUT ANY FALLBACK OR
SPECIAL CASE. THIS AMENDMENT ALSO ESTABLISHES, FOR THE FIRST TIME, THE
EXPLICIT PRECONDITION THAT `MAX_CANDIDATE_CHUNKS` (`K`) MUST BE `≥ 2` —
`K=1` IS MATHEMATICALLY INCOMPATIBLE WITH SIMULTANEOUS FIRST-AND-LAST
COVERAGE WHENEVER `N>1` AND IS UNDEFINED IN THE PROPOSED FORMULA (DIVISION
BY ZERO); DOCUMENT 90 TODAY STATES NO SUCH FLOOR (VERIFIED BY SEARCH, §16),
WHICH THIS AMENDMENT EXPLICITLY CLOSES. THE `N ≤ K` BRANCH IS UNCHANGED
AND UNAFFECTED BY THIS FLOOR. SEVEN REQUIRED WORKED EXAMPLES ARE SHOWN
(§9), INCLUDING BOTH ORIGINAL COUNTEREXAMPLES NOW CORRECTLY COVERING THE
LAST CHUNK. EVERY OTHER DOCUMENT 90 DECISION — COVERAGE DISCLOSURE,
PARTIAL-COVERAGE SEMANTICS, DOCUMENT 87 R2 STATE SEMANTICS, RETRIEVAL
DEGRADATION HANDLING, ZERO-CONTENT BEHAVIOR, THE SINGLE-GENERATION
INVARIANT, CITATION-STRUCTURE VALIDATION, AH-1/AH-2, THE DRS BOUNDARY,
BYOK, SSRF, OWNER-SCOPED JOBS, SSE, OUTPUT BOUNDS, OBSERVABILITY,
SECURITY, TESTING BOUNDARIES, AND DEPLOYMENT CONSTRAINTS — IS PRESERVED
EXACTLY, UNTOUCHED (§12). DOCUMENTS 87 REVISION 2, 88, 89, 90 (OUTSIDE
THIS NARROW SCOPE), 91, 92, 93, AND 94 ARE NOT MODIFIED BY THIS DOCUMENT.
**DOCUMENT 94 REMAINS BLOCKED** — NO IMPLEMENTATION MAY BEGIN; AFTER THIS
AMENDMENT IS SEPARATELY RATIFIED, DOCUMENT 94 WILL REQUIRE ITS OWN
NARROWLY SCOPED REVISION AND ITS OWN SEPARATE CTO REVIEW AND RATIFICATION
BEFORE IMPLEMENTATION AUTHORIZATION CAN TAKE EFFECT. THIS DOCUMENT DOES
NOT AUTHORIZE IMPLEMENTATION, SOURCE-CODE CHANGES, TEST CHANGES,
CONFIGURATION CHANGES, MONGODB, REDIS, LANGGRAPH, FRONTEND, EVALUATION
INFRASTRUCTURE, DEPLOYMENT, RELEASE, COMMIT, PUSH, OR MERGE, AND IT DOES
NOT CREATE DOCUMENT 96 OR ANY OTHER GOVERNANCE DOCUMENT. NO GIT STATE WAS
STAGED, COMMITTED, PUSHED, MERGED, REBASED, RESET, CLEANED, STASHED, OR
AMENDED. `HEAD = origin/main = f8c0664`, `0	0` DIVERGENCE. THE NEXT
GOVERNANCE ACT IS CTO REVIEW OF THIS PROPOSAL — NOT RATIFICATION (A
SEPARATE FUTURE ACT), NOT A DOCUMENT 94 REVISION, AND NOT IMPLEMENTATION.**

DOCUMENT 95 D90 CANDIDATE-SELECTION ARCHITECTURE AMENDMENT DECISION COMPLETE — AWAITING CTO REVIEW
