# 87 — M16 API Contract Proposal — Filing Q&A (FQA v1)

**Status:** 🟡 **M16 API CONTRACT PROPOSAL — DRAFT / PENDING CTO REVIEW
(REVISION 2). NOT RATIFIED.** This document proposes the **externally
observable** request/response, citation, error, state, and job semantics
for **M16 = Filing Q&A (FQA v1)**, formally selected by
[Document 84](84_M16_Milestone_Selection_Record.md) and ratified by
[Document 86](86_Document84_CTO_Ratification_Record.md), under the scope
ratified by [Document 83](83_Filing_QA_Scope_Pre_Decision.md) /
[Document 85](85_Document83_CTO_Ratification_Record.md). Nothing here
ratifies itself, decides M16 architecture, authorizes implementation, or
authorizes a commit — each is a separate, subsequent CTO act (§22).

**Type:** API / contract proposal artifact (research / design / governance
only — no source code, test, schema / migration / index, endpoint, route,
LangGraph node, retrieval / RAG change, MongoDB collection, Redis usage,
provider selection, evaluation infrastructure, or frontend file created or
modified to produce it; `.gitignore` untouched. Documents 67–86 read, not
modified. The only file this task creates / revises is this document.

**Structural precedent (cited, unmodified):**
[70_M15_What_Changed_API_Contract_Proposal.md](70_M15_What_Changed_API_Contract_Proposal.md)
(the most recent ratified API contract — its §4 convention-dependency
table, its §5.1 contract-vs-architecture boundary rule, its §15
zero-new-error-class discipline, its §10.3 async-route-family shape, and
its §22 OAQ register are reused here) and
[64_M14_Filing_Analysis_API_Contract.md](64_M14_Filing_Analysis_API_Contract.md)
(the most recent **filing-scoped** async LLM surface — its `(ticker,
doc_id)` identity, its flat cited-narrative response shape `{narrative,
sources[], cited_source_indices, state}` + `coverage_boundaries`, its
deterministic server-built citation validator, and its 4-route async
family are the direct reuse basis).

**Date:** 2026-09-09.

**Revision 1 (2026-09-09) — CTO-directed correction pass, pre-ratification.**
CTO review result: **BLOCKED PENDING CORRECTION — CONTRACT-LEVEL ITEMS
LEFT OPEN AND INTERNAL CONTRADICTIONS REQUIRE RESOLUTION BEFORE
RATIFICATION.** This revision:
(1) **resolves the `state` vocabulary at the contract level** — `state ∈
{answered, insufficient_evidence}`, a closed two-value enum, with precise
deterministic definitions (§9), removing the contradiction where §6.3 /
§18 called `state` a closed enum while §9 left the choice open;
(2) **resolves the route family at the contract level** — the four-route
async family **includes** the SSE stream route; **route inventory is
frozen at `51 → 55`** (§3.1, §14), removing the "55 vs 54 depending on
SSE" hedge;
(3) **freezes the external source-reference locator shape** as exactly
`{index, doc_id, chunk_start, chunk_end}` (1-based unique `index`,
server-constructed, deterministic), reusing the M14 contract shape
unmodified — the architecture may choose the internal retrieval / storage
representation, but the external API locator shape is fixed by this
contract (§8);
(4) **explicitly defines zero-content-filing behaviour** — a *resolved*
filing with zero usable persisted content completes successfully as
`state = insufficient_evidence`, never a 404 and never an infrastructure
failure (§9, §11, §12);
(5) **makes the `answered` vs `insufficient_evidence` boundary
deterministic** and consistent with (1) (§7, §9, §18);
(6) **clarifies "one LLM generation"** as **one logical answer-generation
request per FQA job** — no iterative refinement and no second
answer-generation pass; implementation-level transport retries that
produce no additional model completion are not prohibited; a
structured-output-repair completion is an additional model completion and
is **not** permitted by this contract as drafted (§13.1, §17);
(7) **reclassifies the numeric bounds** — the contract fixes **no numeric
literal**; question length, answer length, and `sources[]` count are
**operational configuration**, and the observable validation behaviour is
defined **against the deployed configuration** (§5, §17, §21);
(8) **reclassifies the OAQ register** — the four contract-level items
above are removed from the architecture register (§20); only genuinely
architecture-owned questions (retrieval mechanism, `JobKind` realization,
retention mechanism, evaluation gate, prompt construction, model tier,
single-generation enforcement, future reuse) remain;
(9) **reconciles §21 testing requirements** to the now-frozen contract —
no test requirement depends on unresolved behaviour;
(10) **preserves every governance boundary** — DRS BLOCKED, AH-1 / AH-2
preserved, M15 closed, no implementation authorization, no architecture
decision, no new error class, no `git` mutation.
**A second CTO correction pass (2026-09-09) applied three further fixes:**
(11) **resolves the question-normalization contradiction** — surrounding
whitespace is trimmed before processing and the completed
`answer.question` echoes the **normalized** value; the term "verbatim" is
no longer used for it (§3.2, §5, §6.3);
(12) **replaces the raw output-truncation rule with a citation-safe
bounded-output rule** — output bounds stay operational configuration, but
the returned answer is always citation-structurally valid (refined to the
§8-A invariant set in Revision 2, item 14) or the result deterministically
degrades to `insufficient_evidence`; zero new error class (§17.2, §7, §8,
§9, §18, §21);
(13) **distinguishes deterministic citation-structure validation from
semantic grounding assessment** — the contract deterministically enforces
citation *structure* and the *in-filing* grounding invariants on every
response, while *semantic* answer-quality / support evaluation remains the
evaluation-architecture concern deferred to §20 OAQ-4; the product
requirement that substantive factual claims be grounded in the identified
filing is **not** weakened (§7, §8, §9, §18, §20).
**No scope change beyond corrections 1–13. FQA v1 remains single-turn +
stateless + single-filing. Status unchanged: 🟡 DRAFT / PENDING CTO
REVIEW. NOT RATIFIED.**

**Revision 2 (2026-09-09) — CTO conditional-pass correction pass,
pre-ratification.** CTO re-review result: **🟠 CONDITIONAL PASS — NOT YET
APPROVED FOR RATIFICATION.** This revision makes two surgical corrections:
(14) **sharpens the deterministic-vs-semantic grounding boundary** (§7,
§8, §18, §21) — the runtime deterministically enforces only a bounded set
of **citation-structure invariants** (markers map to declared, valid,
unique indices; frozen `{index, doc_id, chunk_start, chunk_end}` locator
shape; every locator resolves to the *identified* filing and never
another; `cited_source_indices` is the exact structural subset; no
orphaned markers; citation-safe output bounding; zero surviving valid
citations ⇒ `insufficient_evidence`). Whether a cited passage
*substantiates* a claim, and whether unrestricted natural-language prose
*contains* a substantive factual claim that requires a citation, are
**semantic** questions — **not** deterministically decidable at runtime —
that remain the §20 OAQ-4 evaluation-architecture concern. The product
requirement that every substantive factual claim be grounded in the
identified filing and carry a valid citation is **preserved**: met by
prompt-construction design (OAQ-5) and verified by the OAQ-4 evaluation
architecture, not by a new runtime capability, error class, or state;
(15) **resolves the logical state-classification wording in §9.2** —
`insufficient_evidence` is now defined as the deterministic outcome
whenever the server cannot return a bounded `answer` object satisfying
**all** of §9.1's `answered` conditions (covering: no surviving grounded
claim; no surviving citation; unsatisfiable §8-A citation / in-filing
grounding invariants; unsatisfiable required coverage disclosure;
citation-safe output-bounding failure; zero usable persisted filing
content). It is no longer worded as if every `insufficient_evidence`
result necessarily means no substantive claim was grounded. The
zero-content success shape (`200 / completed / insufficient_evidence /
sources=[] / cited_source_indices=[]`) is preserved.
**Closed two-value `state` enum unchanged (`{answered,
insufficient_evidence}`); no third state, no new error class, no new
citation mechanism. No scope change — FQA v1 remains single-turn +
stateless + single-filing; the route family and count `51 → 55`, the
external locator shape, the BYOK / SSRF boundaries, the async lifecycle,
the one-logical-generation rule, the numeric-bound treatment, the DRS
boundary, AH-1 / AH-2, M15 closure, and the non-authorization statements
are all unchanged. Status unchanged: 🟡 DRAFT / PENDING CTO REVIEW. NOT
RATIFIED.**

---

## 0. What This Document Is and Is Not

**Is:** a **proposed** M16 API contract for Filing Q&A v1 — its identity
and auth model, its request shape, the meaning of its one question input,
its response shape and cited-answer semantics, its citation / provenance
requirement, its insufficient-evidence and error behaviour, its
async-job / SSE behaviour, its BYOK / SSRF posture, its output bounds, its
deterministic-vs-model-dependent guarantees, its non-goals, and a register
of what remains open for the M16 Architecture Decision Pack.

**Is not:**

- a ratified contract — ratification is a separate, subsequent CTO act
  (§22);
- an **architecture decision** — it selects no FastAPI structure, no
  service/repository class layout, no LangGraph topology, no retrieval
  implementation, no internal storage/passage representation, no
  embedding/vector design, no MongoDB collection/index/migration, no Redis
  mechanism, no prompt architecture, no specific LLM/model, no deployment
  topology. Where a question is architecture-owned it is filed in §20 as
  an **Open Architecture Question**, never silently resolved;
- multi-turn conversation, Durable Research Sessions, cross-filing
  comparison, corpus synthesis, portfolio research, or any general
  persistent research state (§19);
- a reopening of M14, M15, or any earlier milestone, or an amendment to
  Documents 67–86.

---

## 1. Purpose and Scope  *(contract area 1)*

**Purpose.** Give a user the ability to ask **one natural-language
question about one explicitly identified filing** and receive **one
grounded, cited answer drawn from that filing's own content** — deeper
than the four fixed M14 Filing Analysis outputs, without needing to read
the raw text.

**In scope for this proposal (externally observable behaviour only):**

1. A backend capability that, given a `(ticker, doc_id)` filing identity
   and one question string, produces a **single bounded answer**, cited to
   the identified filing's own persisted content (§3–§8).
2. An authenticated HTTP surface for requesting that answer and retrieving
   its result — a **four-route async family**, additive to the existing
   route inventory (**`51 → 55`**), `current_user` gated, using the
   existing `{detail, type}` error envelope (§3, §12, §13, §14).
3. A **contract-level citation / provenance requirement** — the answer is
   grounded and cited to real locations in the identified filing, using
   the established `[n]` / `sources[]` / `cited_source_indices` convention
   with no new syntax and a **frozen external locator shape** `{index,
   doc_id, chunk_start, chunk_end}` (§8).
4. A **closed two-value `state` vocabulary** — `answered` |
   `insufficient_evidence` (§9) — with deterministic semantics, distinct
   from a **filing-not-found** 404 (§11) and from an **invalid-request**
   422 (§10), and with explicit zero-content-filing behaviour (§9).
5. Reuse of the established async-job family and job lifecycle for an
   LLM-generating surface, without prescribing a specific `JobKind`
   identifier or retention mechanism (§13, §20).

**Authoritative product boundary (ratified — Documents 83 / 85 / 84 / 86;
not re-decided here):** FQA v1 is **single-turn**, **stateless with
respect to durable conversational / research state**, **single-filing**,
with filing identity **exactly `(ticker, doc_id)`**. FQA v1 must not
become multi-turn conversation, Durable Research Sessions, cross-filing
comparison, corpus synthesis, portfolio research, or general persistent
research state. **DRS remains BLOCKED and outside M16.**

### 1.1 Contract-vs-architecture boundary (Document 70 §5.1's rule, reused verbatim)

This proposal **fixes** only *externally observable* behaviour: the
capability boundary and exclusions (§1, §19); the request shape (§3–§5);
the response shape and per-field meaning (§6); the answer/evidence
relationship (§7); the citation convention **and the external
source-reference locator shape** (§8); the closed `state` vocabulary and
insufficient-evidence / zero-content behaviour (§9); empty-question and
filing-not-found behaviour (§10, §11); validation, status codes, and the
error envelope (§12); the async-job route family, its **route count
(`51 → 55`)**, and its lifecycle to the extent the platform contract makes
it observable (§13, §14); the BYOK / SSRF posture (§15, §16); the
one-logical-answer-generation rule and output bounds (§17); the
client-observable determinism guarantees (§18); and the validation /
testing requirements at the contract level (§21).

It does **not** fix, and the M16 Architecture Decision Pack remains the
sole authority for: the retrieval mechanism within the filing; the
internal retrieval / storage / passage representation *behind* the frozen
external locator shape (§8); the `JobKind` realization; the transient
result-retention mechanism; prompt-construction discipline; model tier;
and the **numeric values** of every operational bound (§17, §20). Where
this proposal names a precedent, that precedent is cited as the
established convention, not as an implementation directive.

### 1.2 "Stateless" — the AH-2 distinction (preserved, not weakened)

"Stateless" in this contract means **stateless with respect to durable
user / conversational / research-session state**: no per-user Q&A history
store, no saved conversation, no resumable session, no watchlist, no
"since your last question". It does **not** prohibit the **transient
operational job state** the existing platform already uses — a job record
in the `JobStatus` lifecycle, and a bounded, best-effort mechanism for
holding a completed answer between the completing `POST` and a client's
`GET`. That transient execution state is the M15 **AH-2** class of
mechanism (process-local, TTL-bounded, single-backend-process `POST → GET`
lifecycle) and is preserved here as a distinct, already-ratified concept.
The contract's only constraint on it (§13.4): whatever the architecture
selects must **not** become a durable, cross-request, per-user Q&A store —
that would reopen DRS.

---

## 2. Authoritative Governance Lineage  *(contract area 2)*

```text
D67  — Post-M14 Backend & AI Roadmap Reconciliation        🟢 CTO-RATIFIED
D68 / D69 — M15 Milestone Selection = C-4 + Ratification    🟢 CTO-RATIFIED
D70 R4 / D72 — M15 / C-4 API Contract + Ratification        🟢 CTO-RATIFIED
D73 R1 / D74 — M15 / C-4 Architecture Pack + Ratification   🟢 CTO-RATIFIED (AH-1, AH-2)
D75 / D76 — M15 Implementation Authorization + Ratification 🟢 CTO-RATIFIED
D77 / D78 — D75 §14 Testing-Floor Clarification + Ratif.    🟢 CTO-RATIFIED
D79 / D80 — M15 / C-4 Milestone Closure + Ratification      🟢 CTO-RATIFIED — M15 / C-4 CLOSED
D81 / D82 — Post-M15 Roadmap Reconciliation + Ratification  🟢 CTO-RATIFIED — Filing Q&A recommended
D83 / D85 — Filing Q&A Scope Pre-Decision + Ratification    🟢 CTO-RATIFIED — single-turn + stateless + single-filing
D84 / D86 — M16 Milestone Selection + Ratification          🟢 CTO-RATIFIED — M16 = Filing Q&A (FQA v1)
D87 (THIS) — M16 API Contract Proposal (Revision 2)         🟡 DRAFT / PENDING CTO REVIEW
       ↓  CTO contract ratification                          NOT PERFORMED
M16 Architecture Decision Pack                               NOT CREATED
       ↓
M16 Implementation Authorization → implementation → review → commit → push → closure
```

Documents 67–86 are cited, not reinterpreted. The FQA v1 scope (Documents
83 / 85) and the M16 selection (Documents 84 / 86) are treated as **frozen
input** to this proposal.

---

## 3. Request Semantics  *(contract area 3)*

### 3.1 Endpoint family (frozen)

Following the repo-wide, uncontested convention that **every
LLM-generating surface** (Research, Learning, Comparison-Explanation,
Filing Analysis M14, Change Brief M15) is an **async job + status + stream
+ cancel** route family (never a synchronous call), and following the
established **filing-scoped path prefix**
`/api/companies/{ticker}/filings/{doc_id}/...` used by M13 (`/content`)
and M14 (`/analysis`), this contract **fixes** the following four routes:

```
POST   /api/companies/{ticker}/filings/{doc_id}/qa
GET    /api/companies/{ticker}/filings/{doc_id}/qa/{id}
GET    /api/companies/{ticker}/filings/{doc_id}/qa/{id}/stream
POST   /api/companies/{ticker}/filings/{doc_id}/qa/{id}/cancel
```

- The path segment is **`qa`** — fixed here (mirroring the roadmap term
  "Filing Q&A"; consistent with M14's `/analysis`).
- The family is **four routes** (create / status / stream / cancel).
- **The route-inventory guard moves from `51` to `55`** — additive-only,
  exactly four new entries.

This is a **contract-level decision** (sync-vs-async, the route set, and
the route count are all externally observable to a client); it is not
left open.

### 3.2 Request body

| Input | Type | Required | Notes |
|---|---|---|---|
| `ticker` | `str` (path) | required | Normalized `.strip().upper()`, matching every existing company-scoped route. Empty after normalization → 422 `validation_error`. |
| `doc_id` | `str` (path) | required | Together with `ticker` forms the filing identity (§4). |
| `question` | `str` (body) | required | One natural-language question. The entire meaningful input. **Surrounding whitespace is trimmed before processing (§5); this normalized value is what the job operates on and what the completed `answer.question` echoes (§6.3) — it is not a verbatim echo of the raw body.** Empty / whitespace-only after trimming → 422 (§10). Longer than the **deployed maximum-length configuration** → 422 (§10, §17). |
| BYOK fields | `str \| None` | optional | `llm_provider`, `llm_api_key`, `llm_base_url`, `llm_model` — reused **verbatim** from every prior contract (§15). `llm_api_key` never persisted. Custom provider / `llm_base_url` → `require_admin` + `assert_public_url` SSRF guard (§16). |
| *(no output-selection parameter)* | — | n/a | The response always contains the one answer the request produces — no client-selectable filter, mirroring the M14 CQ-2 / M15 fixed-output-set precedent. |

A bare `POST {}` (no body, or a body without `question`) is **not**
accepted — the `question` is the entire point of the request. Missing
`question` → 422 `validation_error` (§10).

### 3.3 No conversational input

The request carries **no** prior-turn history, no conversation id, no
thread id, and none is accepted. Every request is self-contained. A user
asking a second question issues a second, independent request that shares
no server-side state with the first (§1, §19).

---

## 4. Filing Identity and Validation  *(contract area 4)*

- **Filing identity is exactly `(ticker, doc_id)` together** — the
  established, CTO-resolved identity (Document 59 §3.1; Document 64 §2).
  There is no default `doc_id`, no "most recent filing", no `ticker`-only
  form.
- **`(ticker, doc_id)` must resolve to an existing ingested filing.** If
  it does not → 404 `not_found` (§11).
- **`doc_id` that exists under a *different* `ticker` than the path
  `ticker` is treated identically to a nonexistent `doc_id`** → 404
  `not_found`, non-disclosure — the caller cannot learn that the `doc_id`
  exists elsewhere (Document 59 / Document 64 discipline).
- **Unknown `ticker` entirely** (no company / no filings) → 404
  `not_found`.
- All three cases return the identical `{detail, type: "not_found"}`
  envelope (§11, §12).
- **A filing that *resolves* but has zero usable persisted content is not
  a 404** — it completes successfully as `state == "insufficient_evidence"`
  (§9). "Resolves" (identity matched) and "has usable content" are
  distinct: the former governs the 404 boundary; the latter governs the
  `state` boundary.
- **The filing corpus (`filings`, `filing_chunks`) is shared, not
  owner-scoped** — matching M13 / M14 (these collections carry no
  `user_id`). Any authenticated user may ask a question about any ingested
  filing. **This deliberately differs from M15**, which read owner-scoped
  `reports`; FQA reads the shared filing corpus like M13 / M14. Recorded
  as an explicit M16 alignment decision, not an oversight (§16).

---

## 5. Question Semantics  *(contract area 5)*

- The `question` is a **single natural-language string** — a query *about*
  the identified filing.
- **Surrounding whitespace is trimmed before processing.** This trimmed
  (normalized) value is what the job operates on and what the completed
  `answer.question` field echoes (§6.3); the raw request body is not
  echoed. Empty / whitespace-only after trimming → 422 (§10).
- **It is treated as data, never as instructions to the system.** The
  established prompt-injection posture (Document 64 §15; Document 70 §18)
  is extended: neither the user's question nor the filing's text is
  executable instruction; the answer must remain grounded in the filing's
  content regardless of any instruction embedded in the question or the
  filing (§16, §18).
- **The answer is drawn only from the identified filing's own persisted
  content.** v1 does not answer from the model's general knowledge, from
  other filings, from `financial_statements`, from `reports`, or from the
  web. If the filing does not contain content that grounds an answer, the
  result is `state == "insufficient_evidence"` (§9) — never a fabricated
  answer and never an answer sourced from outside the filing.
- **The `question` has a maximum length set as operational
  configuration** at deployment. **The contract fixes no numeric
  literal.** The observable behaviour is defined against the deployed
  configuration: a `question` longer than the **deployed** maximum → 422
  `validation_error` (§10); a `question` within it is accepted (§17, §20
  OAQ-6). Empty / whitespace-only → 422 (§10).
- A syntactically well-formed question that the filing simply cannot
  answer is **not** a 422 — it is a 200 with `state ==
  "insufficient_evidence"` (§9, §10).

---

## 6. Response Shape and Externally Observable Fields  *(contract area 6)*

### 6.1 Create response

`POST .../qa` → HTTP **`200`** (verified repository precedent: no existing
async-job creation route declares a `status_code=` override; M14 and M15
both return `200` on create — Document 70 §10.3):

```jsonc
{"id": "<job id>", "status": "queued", "reused": false}
```

`reused` is **always `false`** for v1 — this contract requires no
identity-keyed result reuse, so every request performs fresh work. A firm,
externally observable commitment (matching M14 fallback-C / M15). Whether
identity-keyed reuse (`reused: true` ever) is introduced in a later
version is §20 OAQ-8.

### 6.2 Status / result response

`GET .../qa/{id}`:

- while `status ∈ {"queued", "running"}`: `{"id": "...", "status": "..."}`
  — the `answer` key is **omitted entirely** (not present, not `null`),
  matching the M14 / M15 precedent;
- while `status == "completed"`: `{"id": "...", "status": "completed",
  "answer": {...}}` — the object in §6.3;
- while `status ∈ {"failed", "cancelled"}`: `{"id": "...", "status":
  "..."}` — no `answer` key;
- an unknown or foreign-owned job id → 404 `not_found` (§11, §12, §16).

### 6.3 The completed `answer` object (frozen shape)

```jsonc
{
  "ticker": "AAPL",                 // echoes the resolved filing identity
  "doc_id": "<doc id>",
  "question": "…",                  // echoes the NORMALIZED question — surrounding whitespace trimmed (§3.2 / §5); bounded — §17
  "answer_text": "…[1]… [2]…",      // grounded natural-language answer with inline [n] markers;
                                    //   a short honest statement when state == "insufficient_evidence"
  "sources": [
    {"index": 1, "doc_id": "<doc id>", "chunk_start": 12, "chunk_end": 14}
  ],                                // frozen shape — §8; [] when state == "insufficient_evidence"
  "cited_source_indices": [1, 2],   // subset of sources indices actually referenced by [n] markers;
                                    //   [] when state == "insufficient_evidence"
  "state": "answered",              // closed enum: "answered" | "insufficient_evidence" — §9
  "coverage_boundaries": [],        // externally observable notes on what the answer could not cover
  "created_at": "2026-09-09T12:00:00Z",
  "prompt_version": "v1",           // non-null — FQA performs a model generation (unlike M15 `period` mode)
  "schema_version": "v1"            // versions the response schema itself
}
```

Field notes:

- **`question`** — the request's `question` **after normalization**
  (surrounding whitespace trimmed, §3.2 / §5). Not a verbatim echo of the
  raw request body; the normalized value is what was processed and is
  what appears here.
- **`answer_text`** — the model-generated answer. Bounded in principle by
  the single generation call's output-token budget; any hard length cap
  is **operational configuration**, not a contract literal, and is
  applied **citation-safely** — the returned `answer_text` (with its
  `sources[]` and `cited_source_indices`) always satisfies every §8
  invariant, or the result degrades to `insufficient_evidence` (§17.2).
  Every substantive factual claim carries an inline `[n]` marker (§8). On
  `insufficient_evidence` it is a **short, honest, bounded** statement
  that the filing does not address the question (optionally a bounded,
  cited partial statement of what *is* present).
- **`sources[]`** — an indexed list of evidence locators, each of the
  **frozen shape `{index, doc_id, chunk_start, chunk_end}`** (§8):
  `index` is 1-based and unique within the list; `doc_id` is the
  identified filing's `doc_id`; `chunk_start`/`chunk_end` bound a real,
  retrievable range within that filing. Every entry is
  **server-constructed and deterministic**; never taken from the model
  verbatim; never a `report_id`; never a cross-filing reference; never an
  external URL. **`[]` when `state == "insufficient_evidence"`.**
- **`cited_source_indices`** — the deterministically computed subset of
  `sources` indices referenced by `[n]` markers in `answer_text`. Every
  `[n]` in `answer_text` appears here; every entry here is a valid
  `sources` index. **`[]` when `state == "insufficient_evidence"`.**
- **`state`** — a **closed two-value enum**: `"answered"` |
  `"insufficient_evidence"` (§9). No third value in v1.
- **`coverage_boundaries`** — a list of short, externally observable
  strings naming sub-questions / topics the answer could not ground, or
  where the filing's coverage was thin, or (for the zero-content case,
  §9) explaining the lack of usable filing content. Empty for a clean
  full answer.
- **`prompt_version` / `schema_version`** — plain strings (established
  M14 / M15 envelope fields). `prompt_version` is non-null for FQA (it
  performs a model generation step). `schema_version` versions this
  response schema.

The `answer` object's shape (field names, types, and the closed `state`
enum) is **stable across requests** even though `answer_text` and the
specific citations vary run-to-run (§18).

---

## 7. Answer / Evidence Relationship  *(contract area 7)*

- **Every substantive factual claim in `answer_text` must be grounded in,
  and cite, the identified filing's own content.** The citation *is* the
  evidence: each `sources[]` entry is a real, retrievable
  `{doc_id, chunk_start, chunk_end}` range in the `(ticker, doc_id)`
  filing (§8).
- **Zero grounded citations for a produced answer is a failed
  generation**, never a fabricated answer — Document 42 §7's grounding law,
  reused verbatim (established across M9.1 / M14 / M15). It surfaces as
  `state == "insufficient_evidence"` with an honest, bounded `answer_text`
  and `sources == []`, `cited_source_indices == []` (§9), not as a
  confident unsupported answer.
- **The model is never trusted with real evidence anchors.** It works with
  model-facing handles (e.g. numbered candidates) that the server maps to
  real filing locations **after deterministic validation** — exactly as
  M14's `resolve_and_validate` builds every `{doc_id, chunk_start,
  chunk_end}` anchor server-side and M9.1 / M15 map a model-facing number
  to a real id server-side.
- **Two distinct kinds of grounding check — the contract makes only the
  first a deterministic runtime guarantee:**
  - **A. Deterministically enforceable runtime citation-structure
    invariants** — checked on every returned (bounded) `answer` object,
    regardless of model output (§8, §18):
    - every `[n]` marker in `answer_text` maps to a **declared** `sources[]`
      index;
    - `sources[]` indices are **valid and unique**;
    - every `sources[]` entry uses the frozen `{index, doc_id,
      chunk_start, chunk_end}` shape (§8);
    - every `sources[]` locator **resolves to the identified filing**
      (`doc_id` equals the path `doc_id`) — **never another filing**,
      never a `report_id`, never an external reference;
    - `cited_source_indices` is **exactly the structural subset** of
      `sources[]` indices referenced by surviving `[n]` markers;
    - **no dangling / orphaned citation marker** remains (a marker with no
      declared valid source is dropped);
    - **output bounding is citation-safe** — bounding never introduces an
      orphaned marker or a cross-filing citation (§17.2);
    - **zero surviving valid citations ⇒ `state == "insufficient_evidence"`**
      (`sources == []`, `cited_source_indices == []`).
  - **B. Semantic grounding — not a deterministic runtime capability.**
    Whether a cited passage *actually substantiates* a natural-language
    factual claim; whether a stretch of unrestricted `answer_text` prose
    *contains* a substantive factual claim that requires a citation; and
    semantic answer quality generally. **None of B is deterministically
    decidable and none is a runtime gate or an error path.** B is the
    **evaluation-architecture concern deferred to §20 OAQ-4** (a held-out
    evaluation set, not a per-request check — D77 / D78 precedent).
  **The product requirement is not weakened.** FQA **must** return answers
  in which every substantive factual claim is grounded in the identified
  filing and carries a valid citation. That requirement is met by design
  (prompt construction — §20 OAQ-5) and verified by the B evaluation
  architecture; the runtime deterministically guarantees the **A**
  invariants (in particular: nothing is cited from outside the filing, no
  marker is orphaned, and an answer with no surviving valid citation
  becomes `insufficient_evidence`). This contract does **not** claim that
  a structural validator can, at runtime, identify every substantive
  factual claim in free prose or judge whether its citation semantically
  supports it.
- **The `answered` vs `insufficient_evidence` decision is a deterministic
  function of the A invariants and the citation-safe-bounding outcome**
  (§9), never a model self-report and never a semantic judgement.
- **Output bounding is citation-safe** (§17.2): applying an operational
  length / count bound never leaves an orphaned `[n]` marker or a
  cross-filing citation; if the **A** invariants cannot be preserved
  within the bound, the result degrades to `insufficient_evidence`, not a
  truncated or partially-cited factual answer.
- The answer must not assert a figure, date, fact, or characterisation
  that is not present in the identified filing (the M14 `_SYSTEM` rule,
  extended to FQA).

---

## 8. Citation Representation and Requirements  *(contract area 8)*

- **The established governing citation convention is reused as the sole
  mechanism** — inline `[n]` markers in `answer_text`, a parallel indexed
  `sources[]` list, and a `cited_source_indices` subset of indices
  actually referenced. **No new citation syntax, no new citation
  mechanism, no parallel evidence representation.**
- **The external source-reference shape is frozen by this contract as
  exactly** `{index, doc_id, chunk_start, chunk_end}` — the M14
  filing-analysis contract shape, reused unmodified:
  1. **`index`** — 1-based; unique within `sources[]`;
  2. **`doc_id`** — the identified filing's `doc_id` (never another
     filing's; never a `report_id`);
  3. **`chunk_start`, `chunk_end`** — an inclusive range identifying
     **real, retrievable content** within that filing;
  4. every entry is **server-constructed and deterministic** — never
     taken from the model verbatim.
  **The architecture phase may choose any internal retrieval / storage /
  passage representation *behind* this locator, but the externally
  observable locator shape is fixed here and is not an architecture
  decision** (§20).
- **A. Deterministically enforced citation-structure invariants** —
  runtime, on every returned (bounded) `answer` object:
  - every `[n]` marker in the returned `answer_text` maps to a declared
    `sources[]` index and appears in `cited_source_indices`;
  - `sources[]` indices are **valid and unique**;
  - every `sources[]` entry uses the frozen `{index, doc_id, chunk_start,
    chunk_end}` shape and its locator **resolves to the identified
    filing** (`doc_id` equals the path `doc_id`) — **never another
    filing**, never a `report_id`, never an external reference;
  - `cited_source_indices` is exactly `{ the sources index of each
    surviving [n] marker }`, and `⊆ { s.index for s in sources }`;
  - **no dangling / orphaned citation marker** remains — a marker with no
    declared valid source is dropped; if that leaves no surviving valid
    citation, the result is `insufficient_evidence`;
  - output bounding is **citation-safe** — it never introduces an orphaned
    marker or a cross-filing citation (§17.2);
  - an `answered` result has **at least one surviving valid citation**; an
    `insufficient_evidence` result has `sources == []` and
    `cited_source_indices == []` (§9).
- **B. Not deterministically enforced at runtime.** Whether a cited
  passage *substantiates* its claim, and whether a stretch of
  unrestricted `answer_text` prose *contains* a substantive factual claim
  that should carry a citation, are **semantic** questions — not a runtime
  gate and not an error path. They are the evaluation architecture
  deferred to §20 OAQ-4. **No new error class and no new contract
  mechanism is introduced.** The product requirement that every
  substantive factual claim be grounded in the identified filing and
  cited (§7) is met by prompt-construction design (§20 OAQ-5) and verified
  by that evaluation architecture — the contract does not claim a runtime
  validator can do it.
- **Frontend rendering** of a `sources[]` entry (a design concern, not
  fixed here) is expected to reuse the existing citation-target component;
  no new component is required by this contract.

---

## 9. State Vocabulary and Insufficient-Evidence Behaviour  *(contract area 9)*

**`state` is a closed two-value enum, fixed by this contract:
`state ∈ {answered, insufficient_evidence}`. No third value exists in
v1.** (This resolves the initial draft's OAQ-3 at the contract level.)

### 9.1 `answered` — definition

`state == "answered"` **iff**, after the single answer generation and the
deterministic server-side citation-structure validation (§7, §8), the
server can return a **bounded** `answer` object on which **all** of the
following deterministic conditions hold:

- **at least one surviving valid citation** — `cited_source_indices` is
  non-empty and every entry maps to a validated `sources[]` locator (a
  real range in the identified `doc_id`);
- **all §8-A citation-structure invariants hold** on the returned object
  — markers map to declared, valid, unique indices; every locator
  resolves to the identified filing and never another; `cited_source_indices`
  is the exact structural subset; no orphaned markers; no cross-filing
  citation;
- **the citation-safe output bound was satisfied without degrading**
  (§17.2) — bounding did not have to fall back to `insufficient_evidence`;
- **the required `coverage_boundaries` disclosure is present and
  well-formed** — the field is a (possibly empty) list of strings that the
  server was able to emit.

An `answered` result therefore always has `sources != []`,
`cited_source_indices != []`, a citation-structurally valid `answer_text`,
and a well-formed `coverage_boundaries`. Partial coverage (some of the
question answered, some not) is still `answered`, with the gaps disclosed
in `coverage_boundaries` — there is **no separate `partial` state**.

**Product requirement (design + evaluation, not a deterministic runtime
branch).** Within an `answered` result, every substantive factual claim in
`answer_text` must be grounded in the identified filing and cited, and
`coverage_boundaries` must disclose genuine uncovered portions. That
requirement is enforced by prompt-construction design (§20 OAQ-5) and
verified by the §20 OAQ-4 evaluation architecture — the runtime does not,
and this contract does not claim it can, deterministically identify every
substantive factual claim in free prose or judge the semantic
completeness of its grounding.

### 9.2 `insufficient_evidence` — definition

`state == "insufficient_evidence"` is the **deterministic outcome
whenever the server cannot return a bounded `answer` object satisfying
all of §9.1's `answered` conditions** — i.e. whenever a citation-valid
grounded answer meeting the required contract invariants cannot be
produced. When this state is returned, deterministically:

- `sources == []`;
- `cited_source_indices == []`;
- `answer_text` is a **short, honest, bounded** statement (that the filing
  does not address the question, that no usable filing content exists, or
  that a grounded answer could not be produced within the configured
  bound — as applicable), without asserting anything not in the filing;
- `coverage_boundaries` names the reason.

The conditions that produce `insufficient_evidence` include, as
applicable:

- **no substantive grounded claim survives** validation;
- **no `[n]` citation survives** validation — zero surviving valid
  citations (§7, §8);
- **the required §8-A citation-structure / in-filing grounding invariants
  cannot be satisfied** on any returnable object;
- **the required `coverage_boundaries` disclosure cannot be produced**
  well-formed;
- **citation-safe output bounding cannot preserve a valid grounded
  answer** within the deployed `answer_text` / `sources[]` maximum
  (§17.2) — the result degrades here rather than returning a truncated or
  partially-cited factual answer;
- **the identified filing has zero usable persisted content** (§9.3).

This state is **not an error** — it is a successful `200 / completed`
result; the zero-new-error-class rule (§12) is preserved. **It does not
imply that no substantive claim was ever generated or grounded** — only
that the server could not return an `answer` object meeting §9.1's
required invariants for one of the reasons above.

### 9.3 Zero-content filing — explicit behaviour

**A filing that *resolves* (identity `(ticker, doc_id)` matched) but has
zero usable persisted content** (no readable filing text available to
ground any answer) **completes successfully** as:

```jsonc
{"id": "...", "status": "completed",
 "answer": {"ticker": "...", "doc_id": "...", "question": "...",
            "answer_text": "<honest bounded statement that no usable filing content is available>",
            "sources": [], "cited_source_indices": [],
            "state": "insufficient_evidence",
            "coverage_boundaries": ["no usable persisted content is available for this filing"],
            "created_at": "...", "prompt_version": "v1", "schema_version": "v1"}}
```

- It **must not** become a **404** (the filing identity *did* resolve —
  §4, §11).
- It **must not** become an **infrastructure failure / 502** (`
  infrastructure_error`) — the absence of usable content is a data
  condition, handled as a state, not an error (§12).
- It is one instance of `insufficient_evidence` (§9.2); the distinguishing
  detail is carried in `coverage_boundaries`.

### 9.4 Distinctness

`insufficient_evidence` is **categorically distinct** from:

- **filing-not-found (404)** — the filing identity did not resolve (§11);
- **invalid request (422)** — the request was malformed (§10).

A client can rely on `state == "insufficient_evidence"` (HTTP 200) to mean
"we resolved and read the filing (or found it has no usable content) and
could not safely ground an answer", never "the identifier was wrong" and
never "the request was malformed".

---

## 10. Empty / Invalid Question Behaviour  *(contract area 10)*

| Situation | Result |
|---|---|
| `question` field missing | 422 `validation_error` |
| `question` empty string, or whitespace-only after trim | 422 `validation_error` |
| `question` longer than the **deployed maximum-length configuration** (§5, §17) | 422 `validation_error` |
| bare `POST {}` (no body) | 422 `validation_error` |
| empty `ticker` after normalization | 422 `validation_error` |
| `question` is well-formed but nonsensical / not answerable from the filing | **not** 422 — a `200` with `state == "insufficient_evidence"` (§9) |

The contract draws a hard line between **"malformed request" (422)** and
**"well-formed request the filing cannot answer" (200 + `state ==
"insufficient_evidence"`)**. A well-formed request is never rejected for
the *content* of its question.

---

## 11. Filing-Not-Found Behaviour  *(contract area 11)*

| Situation | HTTP | `type` |
|---|---|---|
| `(ticker, doc_id)` has no matching ingested filing | 404 | `not_found` |
| `doc_id` exists but under a different `ticker` than the path | 404 | `not_found` (non-disclosure — indistinguishable from nonexistent) |
| Unknown `ticker` entirely (no company / no filings) | 404 | `not_found` |
| `(ticker, doc_id)` **resolves** but the filing has zero usable persisted content | **200** | — (`state == "insufficient_evidence"` — §9.3; **not** a 404, **not** a 502) |

The three 404 cases return the identical `{detail, type: "not_found"}`
envelope with a non-committal message — the established non-disclosure
discipline (Documents 59, 64). The zero-content case is a successful
completion, not a not-found (§9.3).

---

## 12. Error Taxonomy and Externally Observable Error Behaviour  *(contract area 12)*

**Zero new error classes.** Every FQA failure maps onto the existing
nine-class `backend/domain/errors.py` taxonomy
(`NotFoundError` 404 `not_found`, `ValidationError` 422
`validation_error`, `ConflictError` 409 `conflict`, `AuthorizationError`
403 `forbidden`, `RateLimitedError` 429 `rate_limited`,
`DeadlineExceededError` 504 `deadline_exceeded`, `InfrastructureError`
502 `infrastructure_error`, `LLMProviderError` 502 `llm_provider_error`,
`StreamingError` 500 `streaming_error`) — same discipline as Documents 59,
43, 64, 70 ("split a kind when it needs its own logic, not before").

| Situation | HTTP | `type` |
|---|---|---|
| Unauthenticated | 401 | — (no body change; existing auth middleware) |
| Empty `ticker` after normalization | 422 | `validation_error` |
| Missing / empty / whitespace `question`, or `question` over the deployed maximum length | 422 | `validation_error` |
| `(ticker, doc_id)` unresolvable / cross-ticker / unknown ticker | 404 | `not_found` (non-disclosure — §11) |
| Job admission budget exceeded | 429 | `rate_limited` |
| Custom LLM provider / `llm_base_url` by a non-admin | 403 | `forbidden` |
| Custom `llm_base_url` failing the SSRF guard | 400 | *(established M14 / M15 deviation: `HTTPException(400, detail=…)` with a message and **no** `type` field — reproduced here exactly, not newly invented)* |
| Provider call failure | 502 | `llm_provider_error` (redacted message; raw provider text never surfaced) |
| Malformed / unrepairable structured model output | 502 | `llm_provider_error` |
| Processing deadline exceeded | — | job `failed`, outcome `failed_deadline_exceeded`; `GET` returns `200 {"status": "failed"}` — the established async mapping (M14 / M15): the taxonomy's 504 `deadline_exceeded` is the *synchronous-style* code; an async job surfaces it as job state, not a live HTTP 504 |
| Cancel on unknown / foreign job id | 404 | `not_found` (non-disclosure) |
| Cancel on a terminal job | 200 | idempotent, current unchanged `status`, never an error |
| Database / infrastructure failure | 502 | `infrastructure_error` |

**Not errors — a `200` with the state:**

- **`insufficient_evidence`** (§9.2), including the **zero-content filing**
  case (§9.3) — never a 404, never a 502;
- an `answered` result with non-empty `coverage_boundaries` (partial
  coverage) — still a normal `200` (§9.1).

**No distinct "unanswerable question" code** — a well-formed question the
filing cannot answer is the `insufficient_evidence` *state* (§9), not a
new taxonomy member. **No distinct "filing withdrawn / unavailable / empty"
split** — a non-resolving identity is `not_found` (§11); a resolving
identity with no usable content is `insufficient_evidence` (§9.3).

---

## 13. Async / Job Behaviour  *(contract area 13 — required by the existing externally observable platform contract)*

### 13.1 Analysis: is async required?

**Yes, at the contract level.** Every existing LLM-generating surface in
the platform (Research, Learning, Comparison-Explanation, Filing Analysis
M14, Change Brief M15) is realized as an **async job with a
create/status/stream/cancel route family — none is synchronous** (Document
70 §4, §10.1; verified against `backend/server.py`'s route decorators this
session). Sync-vs-async is **externally observable to a client** (job
envelope + polling/streaming vs. a direct response body), so it is a
contract-stage decision. FQA performs **one logical answer-generation
request** over one bounded filing input (§17) — structurally the same
class as M15 `report` mode. **FQA v1 therefore follows the same async job
model.** A synchronous variant is a non-goal (§19).

### 13.2 Job lifecycle (reused, unchanged)

- **`JobStatus` vocabulary reused verbatim**: `queued` → `running` →
  `completed` | `failed` | `cancelled`.
- **Shared `MAX_ACTIVE_JOBS` admission budget** applies with no new
  per-kind gate (the established "deliberately not parameterized by kind"
  design). Exceeded → 429 `rate_limited` (§12, §17).
- **A dedicated FQA job-deadline configuration must exist**, following the
  established per-`JobKind` `job_deadline_<kind>_s` convention exposed via
  the `job_deadline_s` dict property. The **numeric value is operational
  configuration**, not fixed by this contract (§17, §20 OAQ-6).
- **Whether FQA uses a new `JobKind` enum member or another realization is
  an architecture decision** — §20 OAQ-2 (Document 70 §23 made exactly
  this deferral for M15). The externally observable requirement is only
  that FQA jobs participate in the existing `JobStatus` lifecycle and the
  shared admission budget.

### 13.3 Route contract (per route)

- **`POST .../qa`** (create) — `200 {id, status: "queued", reused:
  false}` (§6.1).
- **`GET .../qa/{id}`** (status/result) — §6.2; `answer` key present only
  while `completed`; unknown/foreign id → 404.
- **`POST .../qa/{id}/cancel`** — a `queued`/`running` job → `200 {"id":
  "...", "status": "cancelled"}`; a terminal job → **idempotent** `200`
  with its current unchanged `status`; unknown/foreign id → 404
  non-disclosure.
- **`GET .../qa/{id}/stream`** — §14 (included in the family).

### 13.4 Transient result retention (the AH-2 distinction — §1.2)

Holding a completed `answer` between the completing `POST` and a client's
`GET` (or the SSE `final` frame) is **transient execution state, not
durable research state.** This contract does **not** select the retention
mechanism. It fixes only the externally observable constraint: whatever
bounded, best-effort mechanism the architecture selects, **it must not
become a durable, cross-request, per-user Q&A-history store** (that would
reopen DRS). The M15 **AH-2** in-process, TTL-bounded, single-backend-
process buffer is an available precedent and, if adopted, carries the same
single-process `POST → GET` deployment invariant M15 already operates
under; the mechanism choice is §20 OAQ-3. **`reused` is always `false`
regardless** (§6.1).

---

## 14. SSE Behaviour  *(contract area 14 — analysed; resolved at the contract level)*

**Analysis.** M14 and M15 each expose a `.../stream` SSE route because
their jobs run multi-second LLM work and clients want progress and a
push-delivered final result. FQA runs one answer generation over one
filing — comparable latency to M15 `report` mode, which *has* a stream
route. Every other async LLM surface in the platform exposes the full
four-route family including `stream`; omitting it would make FQA the lone
exception and force every client to poll.

**Contract decision:** the FQA route family **includes the
`.../qa/{id}/stream` SSE route** (§3.1). The route inventory is **`51 →
55`**. The stream uses the **established `sse_response()` framing
verbatim** — no new SSE mechanism:

1. **Normal trace frames** — an unnamed SSE frame `data: <json>\n\n` whose
   body is a `TraceEvent` (`{node, status, message?, ts?}`) with `node`
   set to any pipeline stage name other than `"final"`. Identical framing
   to every existing stream. (Which pipeline-stage `node` *names* appear
   is an architecture detail; the *frame shape* is fixed by the platform
   SSE contract.)
2. **The completed `final` payload** — one more unnamed `data: <json>\n\n`
   frame whose body is `{"node": "final", "status": "ok", "answer":
   {...}}`, where `answer` is the completed object from §6.3. **Not a
   distinct SSE event type** — a client distinguishes it solely by `node
   == "final"`. Emitted exactly once, immediately after the terminal
   processing trace frame, **only** when the job reaches `completed`
   (including the `insufficient_evidence` / zero-content completion — §9).
   The `final` payload is constructed from the **same transient result
   buffer as `GET`** — it carries the identical §13.4 constraint, not an
   exemption.
3. **The terminal frame** — the named SSE event `event: end\ndata:
   {}\n\n`, identical to every existing stream.

A job that reaches `failed`/`cancelled` emits **no** `final` frame — only
the preceding trace frames, then the terminal frame. `: keepalive\n\n`
comment lines may appear at any point before the terminal frame, exactly
as in every existing stream.

---

## 15. BYOK Boundaries  *(contract area 15)*

- The BYOK fields `llm_provider`, `llm_api_key`, `llm_base_url`,
  `llm_model` are reused **verbatim** from every prior contract (Documents
  43, 64, 70). All are optional; omitting them uses the server's
  configured key.
- **`llm_api_key` is never persisted and never logged.**
- All LLM access is through the established `chat_*` boundary (the
  externally observable part is that the same BYOK fields govern provider
  selection identically to every prior surface).
- A per-request custom provider / base URL is threaded per-request and not
  retained after the job completes.

---

## 16. SSRF / Security Boundaries  *(contract area 16)*

- **`current_user` gating on every route** — reused verbatim; one
  dependency, identical everywhere. Unauthenticated → 401.
- **Custom `llm_provider` (`"custom"`) or a custom `llm_base_url` from a
  non-admin → 403 `forbidden`** (established `require_admin`).
- **A custom `llm_base_url` → the established `assert_public_url` SSRF
  guard applies unchanged**; a loopback / private / link-local address →
  `HTTPException(400, …)` with the established message (reproduced exactly
  from M14 / M15, §12).
- **Job records are owner-scoped** exactly like every existing `JobKind` —
  `GET`, `stream`, and `cancel` by a non-owner → 404 non-disclosure.
- **The filing corpus is shared, not owner-scoped** (§4) — FQA does not
  add a per-user filing-ownership check; it reads `filings` /
  `filing_chunks` like M13 / M14. Recorded explicitly as an M16 alignment
  choice.
- **Prompt-injection posture** — the user's `question` and the filing's
  text are **untrusted data**, not executable instructions (Document 64
  §15; Document 70 §18). The contract requires: the answer stays grounded
  in the identified filing and never follows an instruction embedded in
  the question or filing text to fabricate, to answer from outside the
  filing, or to reveal system context. Whatever prompt-construction
  discipline enforces this is an architecture concern (§20 OAQ-5); the
  externally observable requirement is grounding integrity under
  adversarial input (§21).
- **No secret, no raw provider response, and no raw filing text beyond
  what existing routes already log** is written to logs on any path.

---

## 17. One Answer Generation, and Output Bounds  *(contract area 17)*

### 17.1 One logical answer-generation request

**One `question` per request. One *logical answer-generation request* per
FQA job.** The job issues **exactly one answer-generation request to the
model** and does **not** perform iterative answer refinement, a second
answer-generation pass, or a "generate more" loop — this is the
*single-turn* boundary made a contract-level guarantee.

- **Implementation-level transport retries** — network / timeout retries
  of the *same* request that do **not** produce an additional model
  completion — are **not** prohibited by this rule.
- **Structured-output repair that requires an additional model
  completion** is an additional model completion and is **not permitted by
  this contract as drafted.** If the architecture phase concludes such a
  repair completion is necessary, that requires an **explicit contract
  amendment**, not a silent implementation choice (§20 OAQ-7). It is not
  silently permitted.

### 17.2 Output bounds — operational configuration, applied citation-safely

The contract fixes **no numeric literal** for any bound below. Each is
**operational configuration** set at deployment; the **observable
behaviour is defined against the deployed configuration**:

| Bound | Observable behaviour |
|---|---|
| Maximum `question` length | A `question` longer than the **deployed** maximum → 422 `validation_error` (§10); a `question` within it is accepted. |
| Maximum `answer_text` length | The returned `answer_text` never exceeds the **deployed** maximum, **and** the returned `answer` object still satisfies every §8-A citation-structure invariant: bounding is applied so that **no orphaned `[n]` marker and no cross-filing citation** is introduced. If the §8-A invariants cannot be preserved within the deployed maximum, the result **degrades to `state == "insufficient_evidence"`** (§9.2) — it is **never** a raw-truncated or partially-cited factual answer, and **never** an error (zero new error class — §12). Absent an explicit cap, `answer_text` is bounded in principle by the single generation call's output-token budget. |
| Maximum `sources[]` count | The returned `sources[]` never exceeds the **deployed** maximum, **and** capping never orphans a cited marker: if the cap cannot be applied while keeping every `cited_source_indices` entry backed by a `sources[]` locator (§8), the result **degrades to `insufficient_evidence`** (§9.2), not a partially-cited answer and not an error. Absent an explicit cap, `sources[]` is bounded in principle by the finite evidence available from one filing plus the single generation call's output-token budget (the M15 AH-1 "bounded in principle" basis). |
| FQA job deadline | On exceeding the **deployed** deadline, the job transitions to `failed` (outcome `failed_deadline_exceeded`); `GET` returns `200 {"status": "failed"}` (§12). |
| Any FQA-specific rate limit | If configured, exceeding it → 429 `rate_limited`; the shared `MAX_ACTIVE_JOBS` admission budget always applies (§13.2). |

**Citation-safe bounding rule (summary).** Output bounding is a
**deterministic, structure-preserving** operation on the returned object:
after bounding, every §8-A citation-structure invariant still holds
(markers declared / valid / unique; locators in the identified filing; no
orphaned markers; no cross-filing citation), or `state` is
`insufficient_evidence`. Bounding never returns an orphaned marker, a
cross-filing citation, or an otherwise §8-A-invalid answer. This is
consistent with §§7, 8, 9, 18, and 21.

The contract does **not** claim a testable numeric threshold whose value
is unknown. Tests exercise these behaviours **against the configured
values**, not against a contract literal (§21).

### 17.3 Abuse controls

- **Single-filing scope caps the retrieval / work surface** — a request
  cannot be made to read more than the one identified filing.
- **No output-selection parameter** and no client knob that changes what
  work the job does (§3.2, §19).
- The one-generation rule (§17.1) bounds model cost per job.

---

## 18. Deterministic vs Model-Dependent Behaviour  *(contract area 18 — at the contract level, no implementation selected)*

**Model-dependent (run-to-run variation expected and acceptable):**

- the wording of `answer_text`;
- the specific set of citations chosen and their order;
- the **semantic quality** with which each cited passage supports its
  claim, **and whether a stretch of `answer_text` prose contains a
  substantive factual claim that requires a citation** — both are
  semantic questions, assessed offline by the §20 OAQ-4 evaluation
  architecture, not at runtime;
- since no identity-keyed reuse is adopted, **every request recomputes
  fresh** and `reused` is always `false` (Document 64 §12 / Document 70
  §17 stance, reused).

**Deterministic (contract guarantees, independent of model output):**

- **the response *schema*** — field names, types, and the closed `state`
  enum (`"answered"` | `"insufficient_evidence"`) never vary between
  requests;
- **the `answered` vs `insufficient_evidence` decision** — a deterministic
  function of the §8-A citation-structure invariants and the
  citation-safe-bounding outcome per §9.1 / §9.2, never a model
  self-report and never a semantic judgement;
- **citation-structure validation (§8-A)** — `[n]` markers must map to
  declared, valid, unique `sources[]` indices; every `sources[]` entry is
  a well-formed `{index, doc_id, chunk_start, chunk_end}` locator that
  resolves to the identified `doc_id` and never another filing;
  `cited_source_indices` is the deterministically computed structural
  subset; orphaned / undeclared / duplicate citations are rejected (§8).
  This is a **structural** check only; whether a cited passage
  *substantiates* its claim, and whether prose *contains* a substantive
  factual claim needing a citation, are **out of scope for runtime** and
  are the evaluation-architecture concern of §20 OAQ-4;
- **citation-safe output bounding** — applying an operational length /
  count bound (§17.2) never introduces an orphaned marker or a
  cross-filing citation; the §8-A invariants always hold on the returned
  object, or the result is `insufficient_evidence` (§9.2) — never a
  raw-truncated or partially-cited factual answer, never an error;
- **the grounding law** — zero surviving grounded citations ⇒
  `state == "insufficient_evidence"` with `sources == []` and
  `cited_source_indices == []`, never a fabricated answer (§7, §9);
- **the zero-content-filing completion** — a resolved filing with no
  usable content deterministically completes as `insufficient_evidence`,
  never a 404 or 502 (§9.3);
- **`sources[]` locators are server-constructed** in the frozen shape
  `{index, doc_id, chunk_start, chunk_end}`, never taken from the model
  verbatim (§7, §8);
- **filing resolution and the 404 non-disclosure behaviour** (§11);
- **request validation** — the 422 rules (§10), evaluated against the
  deployed configuration for length (§17.2);
- **job-lifecycle transitions and the create-response shape** (§6, §13);
- **the route set and route count (`51 → 55`)** (§3.1, §14).

The contract does **not** decide whether *retrieval* within the filing is
deterministic (a fixed chunk set) or model-influenced — that is §20
OAQ-1. It fixes that the *validation* of whatever the model returns, and
the externally observable response contract, are deterministic.

---

## 19. Non-Goals  *(contract area 19)*

M16 / FQA v1 **does NOT include, and this contract does NOT define:**

- **Multi-turn conversation** — no follow-up turns, no conversation id, no
  server-remembered exchange, no answer-refinement loop, no second
  answer-generation pass.
- **Durable Research Sessions** — remains BLOCKED (Document 58 §10;
  Documents 83 / 85 / 84 / 86). No saved Q&A history, no "resume", no
  per-user research state, no watchlist.
- **Cross-filing question answering, filing-to-filing comparison,
  corpus-wide synthesis, portfolio-level research** — v1 answers from
  exactly one `(ticker, doc_id)` filing.
- **Answering from anything other than the one identified filing's own
  content** — no `financial_statements`, no `reports`, no other filings,
  no web, no model general knowledge as a source.
- **A new citation syntax, a new error class, a third `state` value, a new
  SSE mechanism, a new job protocol.**
- **A synchronous variant.**
- **An output-selection parameter** or any client knob that changes what
  work the job does.
- **Frontend implementation** — out of backend-contract scope entirely.
- **Any MongoDB collection / index / schema / migration, Redis
  persistence, LangGraph topology change, embedding/vector store, or a new
  LLM provider dependency** — none is authorized or presumed by this
  contract.
- **Numeric SLA, throughput, or concurrency figures** — no repository
  evidence grounds a specific number.
- **Reopening M14, M15, or any earlier milestone.**

---

## 20. Open Architecture Questions  *(contract area 20 — for the M16 Architecture Decision Pack)*

**Resolved at the contract level in Revision 1, and preserved / refined
(not reopened, no ownership change) in Revision 2 — no longer architecture
questions:** the `state` vocabulary (`{answered, insufficient_evidence}`,
§9 — the `answered` / `insufficient_evidence` wording was sharpened in
Revision 2, the two-value enum unchanged); the external source-reference
locator shape (`{index, doc_id, chunk_start, chunk_end}`, §8); the route
path segment (`qa`) and the four-route family including SSE, with route
count `51 → 55` (§3.1, §14).

**The genuinely architecture-owned questions that remain open:**

| # | Question | Owner | Bounded note |
|---|---|---|---|
| **OAQ-1** | Retrieval mechanism within the filing — whole-filing context vs. chunk-retrieval (reuse `agents/retrieval.py` with the additive `doc_id` filter; BM25 / dense / hybrid) vs. section-scoped; and the internal passage / storage representation behind the frozen `{doc_id, chunk_start, chunk_end}` locator | ADP | Externally observable requirement: the answer is grounded in the identified filing and every `sources[]` entry is a real range in it (§7, §8). |
| **OAQ-2** | `JobKind` realization — a new `JobKind.FILING_QA` enum member vs. another mechanism | ADP | Externally observable requirement: FQA jobs use the existing `JobStatus` lifecycle + shared admission budget (§13.2). |
| **OAQ-3** | Transient result-retention mechanism — the M15 AH-2 in-process buffer vs. another bounded on-demand mechanism | ADP | Must not become a durable, cross-request, per-user Q&A store (§13.4). |
| **OAQ-4** | The **semantic** answer-quality / grounding evaluation architecture — whether a held-out evaluation set assessing (a) that cited passages actually substantiate their natural-language claims and (b) that no substantive factual claim in the `answer_text` prose is left uncited (both distinct from the deterministic runtime citation-*structure* validation of §7 / §8) is produced, and whether it is a hard ship gate | CTO — following the D77 / D78 precedent (such evidence need not be a hard commit gate) | Not assumed here; not a runtime gate and not an error path (§7, §8, §21). |
| **OAQ-5** | Prompt-construction discipline that enforces §16's grounding-under-adversarial-input requirement | ADP / implementation | Externally observable requirement stated in §16; mechanism deferred. |
| **OAQ-6** | Numeric **operational-configuration** values — max `question` length, max `answer_text` length, max `sources[]` count, FQA job deadline, any FQA-specific rate limit — and their defaults | ADP / operational | The contract fixes **behaviour against the deployed configuration** (§17.2), not a literal. |
| **OAQ-7** | Model tier (light vs. heavy); and the architectural enforcement of "exactly one logical answer-generation request, no second answer-generation pass" (§17.1) — including confirming that no structured-output-repair completion is introduced without an explicit contract amendment | ADP | The single-turn contract boundary made mechanically enforceable. |
| **OAQ-8** | Whether identity-keyed result reuse (`reused: true` ever) is introduced in a later FQA version | Future contract revision | v1 commits `reused: false` (§6.1). |

None blocks contract ratification on its own — each is a bounded,
explicitly flagged item for the ADP or a later decision. This document
answers none of them.

---

## 21. Validation / Testing Requirements  *(contract area 21 — at the contract level; not an implementation or a test design; every item reflects now-frozen behaviour)*

A future implementation satisfies this contract when, at minimum:

**Route mechanics.**
- The route-inventory guard (`backend/tests/contract/test_route_inventory.py`)
  is updated by **exactly four** new FQA entries — from `51` to **`55`**,
  no more, no fewer: `POST /api/companies/{ticker}/filings/{doc_id}/qa`,
  `GET .../qa/{id}`, `GET .../qa/{id}/stream`,
  `POST .../qa/{id}/cancel`.
- `POST .../qa` returns exactly `{id, status: "queued", reused: false}`
  with HTTP `200`; `reused` is `false` on every request.
- `GET .../qa/{id}` omits the `answer` key while `status ∈
  {queued, running, failed, cancelled}` and includes it only while
  `completed`.
- `cancel` on a terminal job is idempotent (`200`, unchanged status, no
  error); on a `queued`/`running` job it transitions to `cancelled`.
- The SSE `final` payload is an unnamed `data:` frame with `node ==
  "final"` (never a distinct `event:` type), emitted **once** immediately
  before the terminal `event: end` for a `completed` job — including a
  `completed` job whose `state == "insufficient_evidence"`; a
  `failed`/`cancelled` job emits no `final` frame.

**Request validation.**
- Missing / empty / whitespace-only `question` → 422 `validation_error`;
  bare `POST {}` → 422; empty `ticker` → 422.
- A `question` longer than the **deployed** maximum-length configuration
  → 422; a `question` within the deployed maximum is accepted. (Exercised
  against the configured value, **not** a contract literal.)
- A well-formed but unanswerable-from-the-filing `question` → `200` with
  `state == "insufficient_evidence"` — **distinct in tests from a 422 and
  from a 404**.

**Filing resolution.**
- `(ticker, doc_id)` not found, `doc_id` under a different `ticker`, and
  unknown `ticker` each → 404 `not_found`, and the three responses are
  **indistinguishable** (non-disclosure).
- A `(ticker, doc_id)` that **resolves** but has **zero usable persisted
  content** → `200`, `status == "completed"`, `state ==
  "insufficient_evidence"`, `sources == []`, `cited_source_indices ==
  []`, a non-empty `coverage_boundaries`, and a bounded honest
  `answer_text` — **not** a 404 and **not** a 502.

**Answer / citation contract (citation *structure* and in-filing grounding
invariants — not semantic support, which is §20 OAQ-4).**
- The completed `answer` object has exactly the §6.3 field set; `state ∈
  {"answered", "insufficient_evidence"}` and no other value.
- **`answered`** (structural §8-A conditions on the returned object):
  `sources != []`; `cited_source_indices != []`; every `[n]` marker in
  `answer_text` maps to a declared, valid, unique `sources[]` index and
  appears in `cited_source_indices`; `cited_source_indices ⊆ { s.index
  for s in sources }`; every `sources[]` locator resolves to the
  identified `doc_id` and no citation resolves to another filing; **no
  orphaned marker remains**; the citation-safe bound was satisfied
  without degrading; `coverage_boundaries` is a present, well-formed
  (possibly empty) list.
- **`insufficient_evidence`**: `sources == []`; `cited_source_indices ==
  []`; `answer_text` is a short bounded honest statement;
  `coverage_boundaries` is non-empty and names the reason. May arise from
  any §9.2 trigger (no surviving grounded claim; no surviving citation;
  unsatisfiable §8-A invariants; unsatisfiable required coverage
  disclosure; citation-safe-bounding failure; zero usable filing
  content) — a test need only assert the resulting shape and HTTP `200 /
  completed`, not which trigger fired.
- **`answer.question`** echoes the **normalized** (whitespace-trimmed,
  §3.2 / §5) question, not the raw request body.
- Every `sources[]` entry has the frozen shape `{index, doc_id,
  chunk_start, chunk_end}` with `index` 1-based and unique, `doc_id`
  equal to the identified filing's `doc_id`, and `chunk_start/chunk_end`
  resolving to real content within that filing — **never** a `report_id`,
  a cross-filing reference, or an external URL.
- A duplicate `sources` index, or an `[n]` marker referencing an
  undeclared index, is rejected by the deterministic validator.
- An answer whose citations do not survive validation degrades to
  `insufficient_evidence` — never a confident unsupported answer.
- **Citation-safe bounding**: with a deployed `answer_text` / `sources[]`
  bound configured so small that a §8-valid grounded answer cannot fit,
  the result is `200`, `state == "insufficient_evidence"`, `sources ==
  []`, `cited_source_indices == []`, a `coverage_boundaries` entry naming
  the bound — **not** a raw-truncated factual answer, **not** an error.
- These tests exercise the §8-A citation-*structure* and in-filing
  grounding invariants only. **Semantic** questions — whether a cited
  passage substantiates its claim, and whether the `answer_text` prose
  contains a substantive factual claim that is left uncited — are out of
  scope for the contract test floor and are the evaluation-architecture
  concern of §20 OAQ-4.

**Error taxonomy.**
- No error response uses a `type` value outside the nine
  `domain/errors.py` classes (grep-verifiable); **zero new exception
  classes**. The one established `400`-without-`type` SSRF-guard response
  matches M14 / M15 exactly.
- Provider failure / malformed model output → `502 llm_provider_error`
  with a **redacted** message; raw provider text never surfaces.
- Deadline exceeded → job `failed` (outcome `failed_deadline_exceeded`),
  `GET` returns `200 {"status": "failed"}`.

**Security.**
- Custom provider / base URL by a non-admin → 403; custom `llm_base_url`
  private address → the established SSRF-guard `400`.
- `GET` / `stream` / `cancel` by a non-owner of the job → 404
  non-disclosure.
- Adversarial input (an instruction embedded in the `question` or in the
  filing text telling the model to fabricate, to answer from outside the
  filing, or to reveal system context) does **not** break grounding — the
  answer stays cited to the filing or degrades to
  `insufficient_evidence`.

**One answer generation.**
- The job issues **exactly one logical answer-generation request** to the
  model. A transport-level retry that produces **no** additional model
  completion is permitted. **No** second answer-generation pass and **no**
  structured-output-repair completion occurs (a repair completion would
  require a contract amendment — §17.1).

**Determinism.**
- The response schema (field names, types, the `state` enum) is stable
  across repeated identical requests even though `answer_text` and the
  citation set vary.
- The `answered` / `insufficient_evidence` decision follows §9.1 / §9.2
  from the validated output, not from a model self-report.

**Regression.**
- The M13 filing-content-read and M14 filing-analysis route families and
  their tests are unaffected (run, not modified); the shared
  `MAX_ACTIVE_JOBS` budget is unchanged.

**Evaluation.**
- A small answer-grounding / answerability evaluation set for FQA is
  **desirable as tracked evidence**, **not** a hard commit gate — its
  status follows the D77 / D78 precedent and is left to §20 OAQ-4, not
  fixed here.

---

## 22. Explicit Non-Authorization Statement  *(contract area 22)*

**This document does not ratify itself.** The current artifact submitted
for CTO review is **Revision 2** (Revision 1 and the intervening
correction pass are retained in the header revision notes as historical
provenance). As a proposal, it does **NOT** authorize:

- M16 API contract ratification (a separate, subsequent CTO act);
- an M16 Architecture Decision Pack, or any architecture decision —
  including FastAPI structure, service/repository classes, LangGraph,
  MongoDB collections/indexes/migrations, Redis persistence, prompt
  architecture, a specific LLM/model, retrieval implementation, the
  internal representation behind the frozen locator shape,
  embedding/vector architecture, frontend implementation, or deployment
  topology;
- M16 implementation, or any source-code, test, or configuration change;
- any MongoDB collection, index, schema, or migration; any Redis usage;
  any LangGraph change; any new provider dependency;
- any evaluation-infrastructure work (the M15 golden-dataset `report`-mode
  follow-up remains tracked future work per Documents 77 / 78 and is not
  reopened);
- any frontend implementation;
- any deployment, release, commit, push, or merge.

**Revision history (provenance).** *Revision 1* resolved four
contract-level items (`state` vocabulary, the external locator shape, the
route segment, SSE inclusion / route count). A *second correction pass*
added the question-normalization, citation-safe output-bounding, and
initial deterministic-vs-semantic distinctions. ***Revision 2*** — the
artifact currently submitted for CTO review — sharpened the
deterministic-vs-semantic grounding boundary (§7-A / §8-A: the runtime
enforces only citation-*structure* invariants; semantic assessment is the
§20 OAQ-4 evaluation concern) and reworded the §9.2 `insufficient_evidence`
classification, while preserving the product grounding requirement.
**No revision makes an architecture decision or a scope change, and none
changes OAQ ownership.** It does not select or change a model. FQA v1
remains **single-turn + stateless + single-filing**. DRS remains BLOCKED
and outside M16. AH-1 and AH-2 remain preserved. M15 / C-4 remains closed.
Zero new error classes.

**The next legitimate governance gate, if the CTO accepts this proposal,
is this document's own ratification** — a distinct act from drafting it —
followed by a separate **M16 Architecture Decision Pack**, then a separate
implementation-authorization decision, then implementation, then a
technical review, then commit and push authorizations — each a distinct
CTO act, none collapsed.

---

## 23. Repository / Working-Tree State and Provenance

Recorded by read-only inspection this session on 2026-09-09. **No `git`
mutation was performed** — no `add` / stage, `commit`, `push`, `amend`,
`rebase`, `merge`, `reset`, `restore`, `stash`, or `clean`.

- `git rev-parse HEAD` = `git rev-parse origin/main` =
  `f8c06649e94f45c388bbecf3eeedb9e5340f2024` (`f8c0664`, "feat(m15):
  implement change brief"); `git rev-list --left-right --count
  origin/main...HEAD` = `0	0`.
- Document number 87 was verified free before its initial creation
  (highest existing Backend & AI governance document was 86). Revision 1,
  the intervening correction pass, Revision 2, and this metadata-only
  correction pass each edit **this same document in place** — the current
  artifact is **Revision 2**; **no `git` mutation was performed by any of
  them; Document 88 was not created.**
- Read-only, to identify established externally observable conventions:
  `backend/server.py` (the M13 `/content` and M14 `/analysis` filing-scoped
  route families; the M14 / M15 async create/get/stream/cancel handlers),
  `backend/agents/filing_analysis.py` (the M14 deterministic citation
  validator and `{index, doc_id, chunk_start, chunk_end}` anchor shape),
  `backend/domain/errors.py` (the nine-class taxonomy), and Documents
  64 / 70 (the closest ratified contract precedents). **None modified.**
- **Documents 67–86 were read, not modified.** The M15 chain and the M16
  selection / scope chain (Documents 83 / 85 / 84 / 86) are cited as
  frozen input, not reinterpreted.
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
  ?? docs/backend_engineering/67_...md through 86_...md            (pre-existing untracked governance documents — not modified)
  ```

- This document (`docs/backend_engineering/87_M16_Filing_QA_API_Contract_Proposal.md`)
  is untracked and not yet version-controlled. Staging or committing it is
  a separate, subsequently CTO-authorized step, not performed here.

---

**🟡 M16 API CONTRACT PROPOSAL — DRAFT / PENDING CTO REVIEW (REVISION 2).
NOT RATIFIED. THE CURRENT ARTIFACT SUBMITTED FOR CTO REVIEW IS REVISION 2;
REVISION 1 AND THE INTERVENING SECOND CORRECTION PASS ARE RETAINED IN THIS
ATTESTATION AND IN THE HEADER REVISION NOTES AS HISTORICAL PROVENANCE.
THIS DOCUMENT PROPOSES, BUT DOES NOT RATIFY, THE EXTERNALLY OBSERVABLE
REQUEST / RESPONSE, CITATION, ERROR, STATE, AND ASYNC-JOB SEMANTICS FOR
M16 = FILING Q&A (FQA v1). REVISION 1 RESOLVED FOUR CONTRACT-LEVEL ITEMS:
(A) `state` IS A CLOSED TWO-VALUE ENUM
`{answered, insufficient_evidence}` WITH DETERMINISTIC DEFINITIONS —
`answered` = AT LEAST ONE SUBSTANTIVE FILING-GROUNDED CLAIM, EVERY
FACTUAL CLAIM CITED, UNCOVERED PORTIONS IN `coverage_boundaries`;
`insufficient_evidence` = NO SUBSTANTIVE CLAIM CAN BE SAFELY GROUNDED,
`sources == []`, `cited_source_indices == []`; (B) THE FOUR-ROUTE ASYNC
FAMILY INCLUDES THE SSE STREAM ROUTE AND THE ROUTE INVENTORY IS FROZEN AT
`51 → 55`; (C) THE EXTERNAL SOURCE-REFERENCE LOCATOR SHAPE IS FROZEN AS
EXACTLY `{index, doc_id, chunk_start, chunk_end}` (1-BASED UNIQUE `index`,
SERVER-CONSTRUCTED, DETERMINISTIC — INTERNAL RETRIEVAL / STORAGE
REPRESENTATION REMAINS ARCHITECTURAL); (D) THE ROUTE SEGMENT IS `qa`. A
`(ticker, doc_id)` THAT *RESOLVES* BUT HAS ZERO USABLE PERSISTED CONTENT
COMPLETES SUCCESSFULLY AS `state == "insufficient_evidence"` WITH EMPTY
`sources` / `cited_source_indices`, A BOUNDED HONEST `answer_text`, AND A
`coverage_boundaries` ENTRY — NEVER A 404, NEVER A 502. "ONE LLM
GENERATION" MEANS ONE LOGICAL ANSWER-GENERATION REQUEST PER FQA JOB — NO
ITERATIVE REFINEMENT, NO SECOND ANSWER-GENERATION PASS; TRANSPORT RETRIES
THAT PRODUCE NO ADDITIONAL MODEL COMPLETION ARE NOT PROHIBITED; A
STRUCTURED-OUTPUT-REPAIR COMPLETION IS AN ADDITIONAL COMPLETION AND IS NOT
PERMITTED BY THIS CONTRACT AS DRAFTED (IT WOULD REQUIRE AN EXPLICIT
AMENDMENT). NUMERIC BOUNDS (MAX QUESTION LENGTH, MAX ANSWER LENGTH, MAX
`sources[]` COUNT, JOB DEADLINE, ANY FQA RATE LIMIT) ARE OPERATIONAL
CONFIGURATION — THE CONTRACT FIXES NO NUMERIC LITERAL AND DEFINES THE
OBSERVABLE VALIDATION BEHAVIOUR AGAINST THE DEPLOYED CONFIGURATION.
A SECOND CORRECTION PASS RESOLVED THREE FURTHER ITEMS: (E) THE COMPLETED
`answer.question` ECHOES THE **NORMALIZED** (SURROUNDING-WHITESPACE-TRIMMED)
QUESTION — NOT A VERBATIM ECHO OF THE RAW BODY; (F) OUTPUT BOUNDING IS
CITATION-SAFE — BOUNDING NEVER INTRODUCES AN ORPHANED MARKER OR A
CROSS-FILING CITATION, AND THE RETURNED OBJECT SATISFIES EVERY §8-A
CITATION-STRUCTURE INVARIANT OR THE RESULT DETERMINISTICALLY DEGRADES TO
`insufficient_evidence`, NEVER A RAW-TRUNCATED OR PARTIALLY-CITED FACTUAL
ANSWER AND NEVER A NEW ERROR CLASS; (G) THE CONTRACT DETERMINISTICALLY
ENFORCES ONLY CITATION *STRUCTURE* AND THE IN-FILING GROUNDING INVARIANTS
AT RUNTIME. A THIRD PASS (REVISION 2, CTO 🟠 CONDITIONAL PASS) SHARPENED
THIS: (H) THE RUNTIME DETERMINISTICALLY GUARANTEES ONLY A BOUNDED SET OF
CITATION-STRUCTURE INVARIANTS (§8-A: MARKERS MAP TO DECLARED / VALID /
UNIQUE INDICES; FROZEN LOCATOR SHAPE; EVERY LOCATOR RESOLVES TO THE
IDENTIFIED FILING AND NEVER ANOTHER; EXACT STRUCTURAL `cited_source_indices`
SUBSET; NO ORPHANED MARKERS; CITATION-SAFE BOUNDING; ZERO SURVIVING VALID
CITATIONS ⇒ `insufficient_evidence`). WHETHER A CITED PASSAGE SUBSTANTIATES
A CLAIM, AND WHETHER UNRESTRICTED PROSE CONTAINS A SUBSTANTIVE FACTUAL
CLAIM REQUIRING A CITATION, ARE *SEMANTIC* QUESTIONS — NOT DETERMINISTICALLY
DECIDABLE AT RUNTIME — DEFERRED TO §20 OAQ-4. THE PRODUCT REQUIREMENT THAT
EVERY SUBSTANTIVE FACTUAL CLAIM BE GROUNDED IN THE IDENTIFIED FILING AND
CITED IS PRESERVED (MET BY PROMPT-CONSTRUCTION DESIGN, OAQ-5; VERIFIED BY
THE OAQ-4 EVALUATION ARCHITECTURE); AND (I) §9.2 IS REWORDED SO
`insufficient_evidence` IS THE DETERMINISTIC OUTCOME WHENEVER THE SERVER
CANNOT RETURN A BOUNDED `answer` OBJECT SATISFYING ALL OF §9.1'S CONDITIONS
(NO SURVIVING GROUNDED CLAIM; NO SURVIVING CITATION; UNSATISFIABLE §8-A
INVARIANTS; UNSATISFIABLE REQUIRED COVERAGE DISCLOSURE; CITATION-SAFE
BOUNDING FAILURE; ZERO USABLE FILING CONTENT) — NO LONGER WORDED AS IF
EVERY `insufficient_evidence` RESULT MEANS NO SUBSTANTIVE CLAIM WAS
GROUNDED; THE ZERO-CONTENT SUCCESS SHAPE (`200 / completed /
insufficient_evidence / sources=[] / cited_source_indices=[]`) IS
PRESERVED. NO NEW STATE, NO NEW ERROR CLASS, NO NEW CITATION MECHANISM. FQA
v1 REMAINS SINGLE-TURN + STATELESS + SINGLE-FILING WITH FILING IDENTITY
EXACTLY `(ticker, doc_id)`; THE ANSWER IS DRAWN ONLY FROM THE IDENTIFIED
FILING'S OWN CONTENT; THE ESTABLISHED `[n]` / `sources[]` /
`cited_source_indices` CONVENTION IS REUSED WITH NO NEW SYNTAX; ZERO
GROUNDED CITATIONS ⇒ `insufficient_evidence`, NEVER A FABRICATED ANSWER.
ZERO NEW ERROR CLASSES — EVERY FAILURE MAPS TO THE EXISTING NINE-CLASS
TAXONOMY; THE ONE `400`-WITHOUT-`type` SSRF-GUARD RESPONSE REPRODUCES
M14 / M15 EXACTLY. BYOK FIELDS AND THE `require_admin` +
`assert_public_url` SSRF BOUNDARY ARE REUSED VERBATIM; THE FILING CORPUS
IS SHARED (NOT OWNER-SCOPED) LIKE M13 / M14, WHILE JOB RECORDS ARE
OWNER-SCOPED; THE USER'S QUESTION AND THE FILING TEXT ARE UNTRUSTED DATA,
NEVER INSTRUCTIONS. THIS DOCUMENT DECIDES NO ARCHITECTURE — RETRIEVAL
MECHANISM, `JobKind` REALIZATION, RETENTION MECHANISM, PROMPT
CONSTRUCTION, MODEL TIER, SINGLE-GENERATION ENFORCEMENT, THE EVALUATION
GATE, THE OPERATIONAL NUMERIC VALUES, AND FUTURE RESULT REUSE REMAIN IN
THE ADP / LATER-DECISION REGISTER (§20). IT AUTHORIZES NO CONTRACT
RATIFICATION, ARCHITECTURE, IMPLEMENTATION, DATABASE / REDIS / LANGGRAPH /
FRONTEND / EVALUATION-INFRASTRUCTURE WORK, DEPLOYMENT, RELEASE, COMMIT,
PUSH, OR MERGE, AND IT DOES NOT BROADEN FQA BEYOND THE RATIFIED v1 SCOPE.
DRS REMAINS BLOCKED AND OUTSIDE M16. M15 / C-4 REMAINS CLOSED; AH-1 AND
AH-2 REMAIN PRESERVED; DOCUMENTS 77 / 78 REMAIN AUTHORITATIVE. DOCUMENTS
67–86 WERE READ, NOT MODIFIED. DOCUMENT 88 WAS NOT CREATED. NO SOURCE,
TEST, OR CONFIGURATION FILE WAS CREATED OR MODIFIED. NO STAGE. NO COMMIT.
NO PUSH. NO MERGE / REBASE / RESET / AMEND. THE NEXT LEGITIMATE GOVERNANCE
GATE IS THIS PROPOSAL'S OWN CTO RATIFICATION, FOLLOWED BY A SEPARATE M16
ARCHITECTURE DECISION PACK.**

DOCUMENT 87 M16 FILING Q&A API CONTRACT PROPOSAL COMPLETE — AWAITING CTO REVIEW
