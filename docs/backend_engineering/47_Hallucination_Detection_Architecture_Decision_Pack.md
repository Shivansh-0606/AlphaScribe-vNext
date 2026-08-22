# 47 — Hallucination Detection / Adversarial Evaluation Architecture Decision Pack

**Status:** 🟢 CTO APPROVED / FROZEN (architecture) — 🔴 Implementation NOT AUTHORIZED
**Type:** Architecture investigation (research/design-only — no code changed, no pipeline modified, no M10 file edited)
**Frozen:** 2026-08-18 — CTO approved Revision 5 as specified (§0 below lists what is now final); **2026-08-19 — CTO ratified Revision 6 as specified** (§7.3.1's property-axis clarification; the related-but-distinct metric tier that revision records remains open, `MORE EVIDENCE REQUIRED`). Architecture approval is not implementation authorization; that remains a separate, subsequent CTO decision (§19, §20).
**Revision 2** — CTO-requested precision fixes to Revision 1: (1) `model_judged_support`'s claim and evidence selectors made explicit and deterministic, frozen as a load-bearing rule that the judge never selects or discovers what it evaluates (§7, §7.2); (2) `numeric_consistency` fully specified — reference shape, tolerance semantics, numeric extraction, comparison rule, and both missing-fixture-value and no-output-number edge cases (§7.1); (3) a frozen judge-verdict → `BehaviorEvaluation.status` mapping table, with judge failure/uncertainty never producing `FAIL` (§7.3); (4) an explicit evidence/claim trust boundary contract for judge invocation (§10.1); (5) a self-consistency validation gate that must clear before a `model_judged_support` result may influence a case's PASS/FAIL, with judged-but-unvalidated results now explicitly excluded from case-level aggregation until then (§7.4, §9.1); (6) §19 sequencing rewritten around that gate as a hard step.
**Revision 3** — CTO-requested correctness fix to Revision 2's `numeric_consistency` design: it originally scanned the *entire* generated output for any matching number, which independently reintroduced this document's own core false-confidence problem one layer down (an unrelated, correct figure stated elsewhere in the response could satisfy a check about a different claim; worked counter-example added below). Fixed by extracting a single, shared, deterministic claim/evidence selector (§7.0) used identically by both `numeric_consistency` and `model_judged_support`, plus explicit, frozen rules for the ambiguous cases that selector surfaces: multiple sentences carrying the same citation marker (§7.0 step 4 — `INCONCLUSIVE`), multiple numeric tokens within one selected claim sentence (§7.1 — `INCONCLUSIVE`, `numeric_consistency` only, since the judge in §7.2 can read a full sentence and is not subject to this), a zero-valued expected figure (§7.1 — exact equality, not relative tolerance), and evidence eligibility (§7.0 step 1 — an ineligible or unresolvable source is `INCONCLUSIVE`, never handed to the judge or the comparator as if it were legitimate). No other section changed in substance; the recommended architecture, decision rationale, and governance status (§17, §18, §20) are unchanged.
**Revision 4** — CTO-requested fix to a false claim in Revision 3's §7.0 step 1: it asserted that a fixture path's leading array index maps 1:1 to a citation `source_id` "via the same 1-based citation-marker numbering every surface already uses" — checked directly against all three adapters this session, and that is only true for Research and Learning (`Citation(source_id=str(i), ...)`, identical code shape, verified in both `evaluation/adapters/research.py` and `evaluation/adapters/learning.py`). It is **false** for Comparison Explanation, where `Citation.source_id` is `f"{report_id}:{field_name}"` (`evaluation/adapters/comparison_explanation.py`), decoupled from both fixture array order and the narrative's own `[n]` marker numbers, which the model assigns arbitrarily per response. §7.0 now states the verified, surface-specific rule instead of a false universal one, and scopes `numeric_consistency`/`model_judged_support` to **Research and Learning only** — Comparison Explanation is out of scope for both rules until a separate decision resolves a marker↔`source_id` mapping without reading `AdapterResult.output.raw` (off-limits to the evaluator core per Document 45 §11). This surfaced a further, previously-unstated consequence, reported rather than smoothed over: Research/Learning have no FIXTURE mode today, while Comparison Explanation — excluded above — is the only surface that does, so neither new rule can currently produce a regression-eligible (FIXTURE-mode) result; both are exercisable only in LIVE mode until Research/Learning's already-deferred FIXTURE-mode gap (Document 45 §11.1) closes. No other section changed in substance; the recommended architecture, decision rationale, and governance status (§17, §18, §20) are unchanged.
**Revision 5** — CTO-authorized policy-precision amendment resolving an ambiguity the M11 self-consistency evidence-gathering work (post-approval empirical measurement, not part of this document series until now) surfaced in §7.2/§7.3: the one-sentence `UNSUPPORTED`/`NOT_APPLICABLE` schema definitions did not state whether evidence containing an explicit statement of absence ("no guidance was provided") about the claim's own subject counts as relevant-but-unconfirming (`UNSUPPORTED`) or as not addressing the subject at all (`NOT_APPLICABLE`) — both readings were textually defensible under Revision 4's text, and three already-authored evaluation cases had been labeled under an unstated interpretive choice rather than a frozen rule. §7.3.1 (new) freezes a relevance-first decision policy: evidence is `NOT_APPLICABLE` only when it fails a subject/entity, metric/disclosure, or temporal relevance test; once relevant, an explicit absence disclaimer or a mismatched-but-related reporting period is `UNSUPPORTED`, never `NOT_APPLICABLE`, and only an affirmative opposing statement is `CONTRADICTED`. This is a **reference-labeling and evaluation-interpretation policy** — it governs how a case author or reviewer determines the correct verdict for a claim/evidence pair, and how self-consistency pilot results are read against that verdict. **It does not change** `JudgeVerdictSchema`, the judge's system/user prompt, `JudgeDetail`, `judged_by`, §7.0's selector, §7.3's verdict→status mapping table (unchanged, still `SUPPORTED`→`PASS`, `CONTRADICTED`→`FAIL`, `UNSUPPORTED`→`FAIL`, `NOT_APPLICABLE`→`INCONCLUSIVE`), the self-consistency gate, or any other frozen Revision 1–4 provision — none of those sections are edited by this revision. §7.3.1 also records, as documentation only, which existing evaluation cases this policy would reclassify if and when a separate, subsequent CTO decision authorizes relabeling them (no case file is modified by this document). Implementation remains 🔴 NOT AUTHORIZED, unchanged from every prior revision (§20).
**Revision 6** — CTO-authorized policy-precision amendment to §7.3.1, narrower in scope than Revision 5: it clarifies the *level* at which §7.3.1's existing metric/disclosure relevance rule evaluates the PROPERTY axis, and nothing else. Revision 5 froze *which* three relevance tests apply (subject/entity, metric/disclosure, temporal) but never stated what "the same or a directly related metric/disclosure proposition" is measured over — its worked examples compare metric nouns of matching modality and tense only, leaving the property test readable at the proposition level (evidence must assert the claim's proposition), the quantity level (evidence must concern the claim's underlying quantity), or the broad-topic level. Only the quantity-level reading is jointly consistent with Revision 5's own frozen explicit-absence and temporal rules; each of the other two readings inverts one of them. §7.3.1's new **Property axis — what it is measured over** block (inserted after the metric/disclosure relevance rule and before the subject/entity mismatch rule) states the quantity-level reading and enumerates four dimensions — modality, polarity, tense/aspect, and granularity/units — that are not property axes and must never independently produce `NOT_APPLICABLE`. It also records, **without resolving**, an open boundary: the related-but-distinct metric tier, where the ratified corpus currently answers both ways. This is a **reference-labeling and evaluation-interpretation policy amendment only**, the same class as Revision 5. **It does not change** `JudgeVerdictSchema`, the judge's system/user prompt or `JUDGE_PROMPT_VERSION`, `JudgeDetail`, `judged_by`, §7.0's selector, §7.3's verdict→status mapping table, `JUDGE_SELF_CONSISTENCY_GATE_VERSION` (still `0`), the self-consistency gate, or any other frozen Revision 1–5 provision — none of those sections are edited by this revision, and no Revision 5 text is deleted or rewritten. **No reference verdict is changed and no case file is modified or created by this revision**, including the existing gross-margin worked example, which is retained verbatim. Revision 6 makes **no claim** to have validated, improved, or measured judge behavior: it changes no prompt and was accompanied by no live experiment. Implementation remains 🔴 NOT AUTHORIZED and judge modification remains 🔴 NOT AUTHORIZED, unchanged from every prior revision (§19, §20); ratification of this revision is a separate CTO/Reviewer act, not asserted by its drafter.

**Depends on (cited, unmodified):** [45_M10_Pre_Implementation_Architecture_Decision_Pack.md](45_M10_Pre_Implementation_Architecture_Decision_Pack.md), [46_M10_Phase4_Pre_Implementation_Plan.md](46_M10_Phase4_Pre_Implementation_Plan.md), [17_M4_Backend_Capability_Roadmap_Reconciliation.md](17_M4_Backend_Capability_Roadmap_Reconciliation.md) §7.1, [44_Post_M9_Backend_AI_Roadmap_Reconciliation.md](44_Post_M9_Backend_AI_Roadmap_Reconciliation.md) §4.1/§5/§7.1, [01_Backend_Architecture_Review.md](01_Backend_Architecture_Review.md) `D-10`
**Working-tree commit at time of writing:** `d80e105`

---

## 0. Governance note — read before the rest of this document

This document was commissioned by a chat-level directive asserting the following governance state: M10 CLOSED, M10 Evaluation Architecture FROZEN, M10 Phases 1–4 APPROVED, and a "Post-M10 Backend & AI Roadmap Reconciliation" APPROVED. Direct inspection of the repository's documents of record does not support that state, and this document does not repeat it:

- **Document 45's own header is unedited: `🟡 PROPOSED — AWAITING CTO APPROVAL`**, and its §25 states "M10 Implementation: 🔴 NOT AUTHORIZED." Nothing in the repository edits that line.
- **Document 46 §title/header already addressed this exact pattern once**, verbatim: *"Prior conversational governance-state banners describing it as 'APPROVED / FROZEN' reflect chat-level directives, not an edit to Document 45's own status line; this document does not repeat that overclaim."* This document follows Document 46's own precedent rather than reopening it.
- **No "Post-M10 Backend & AI Roadmap Reconciliation" document exists anywhere in `docs/backend_engineering/`** (verified: `45` and `46` are the two most recent documents; no `47`+ existed before this one). The scope direction this document responds to — hallucination detection as the natural next step — is real, but its actual source is **Document 44 §4.1/§7.1 and Document 17 §7.1**, both already-written, already-referenced documents, not an unwritten reconciliation report.
- **A separate, more concrete discrepancy, found during this investigation and reported rather than silently worked around:** in the same commit (`d80e105`) that added Document 46 — whose own text states "M10 Phase 4 implementation: 🔴 NOT AUTHORIZED" — the Phase 3 and Phase 4 code Document 46 describes as not-yet-authorized was itself implemented and committed (`backend/evaluation/core/`, `backend/evaluation/regression/`, `backend/scripts/run_evaluation.py`, all tracked, all present in the working tree used to write this document). This is a pre-existing state this document did not create and takes no action on — it is surfaced here because §18 of the commissioning task requires validating claims against the actual repository, and because Document 46 itself modeled exactly this kind of disclosure. It has the same shape as the M7 precedent already on record (Document 29 §6: implementation began before required pre-approval was formally recorded; the CTO granted a retroactive exception and reaffirmed the approval-before-implementation rule going forward) — offered as a pattern match, not a resolution; resolving it is a CTO governance decision, not an architecture-document one.

**What this means for the rest of this document:** it treats Document 45's architecture as the real, in-force design (because the code implementing it is real and in the working tree, verified line-by-line in §4 below) while treating its formal approval status honestly as still pending. Every extension proposed below is written against the actual, current code — not against an assumed "frozen" state that the documents of record do not themselves claim.

---

## 1. Problem Statement

Three LLM-generating surfaces — Research, Learning, Comparison Explanation — are now evaluated by M10's harness (Document 45, implemented). Every one of M10's four metrics (citation coverage, grounding status, expected-characteristic coverage, case pass/fail) is, by Document 45's own explicit design principle (§6.5, §15), **deterministic and structural**: it checks that a citation marker exists, is in range, was declared, and was used; that a case-authored keyword/phrase variant is present or absent; that a `known_limitations` entry was acknowledged in aggregate. None of these checks read the content of the cited evidence and compare it against the substance of the claim next to it. A narrative can cite `[1]` correctly by every structural test M10 runs, while the claim attached to `[1]` is not what source `1` actually says — or isn't in the offered evidence at all. That gap is not an oversight; it is `01 D-10`, already on record: *"Numeric-only fact-checking. A purely qualitative fabrication extracts zero claims and is trivially accepted at faithfulness 1.0"* (`agents/nodes.py:198-205`, itself `ponytail:`-marked with a named upgrade path). Document 17 §7.1 named the fix — *"Hallucination detection: a structured, sampled adversarial check extending past `D-10`'s numeric-only blind spot"* — with an explicit trigger: *"when a third AI-generating endpoint ships."* Document 44 §5 verified that trigger is now satisfied (Comparison Explanation is a real, third LLM-generating capability), and Document 44 §7.1 explicitly deferred building it as "a natural phase 2 once the dataset/harness exist, not bundled in [M10]." That harness now exists, in code. This document is that phase 2's architecture.

---

## 2. Why M10 Does Not Fully Solve the Problem

Verified against the actual Phase 1–4 code, not inferred from Document 45's prose:

| M10 mechanism | What it actually checks | What it cannot check |
|---|---|---|
| `evaluate_keyword_variant` (`evaluation/core/behaviors.py`) | Case-insensitive substring presence/absence of an author-supplied phrase list | Whether a *present* phrase is true; only whether it was said |
| `evaluate_citation_required` | Whether **any** valid citation exists at all (its own docstring: *"evaluates citation presence in aggregate, not whether reference {reference!r} specifically was cited"* — a reported gap, not a silent one) | Whether the *specific* claim next to a citation is what the cited source actually says |
| `evaluate_limitation_reference` | Whether **any** limitation was acknowledged at all (same aggregate-only shape, same self-documented gap); unconditionally `INCONCLUSIVE` for Learning (no structured limitations field exists there) | Whether the *right* limitation was acknowledged, or whether an unacknowledged gap was silently papered over with an invented figure |
| `validate_and_map_citations` (Comparison Explanation, wrapped) | Marker/index consistency: no duplicates, no out-of-range `report_number`, every `[n]` marker declared and confirmed cited | Whether the cited report's `extracted_data`/`sentiment_analysis` content actually supports the sentence bearing `[n]` |
| `_postprocess_citations` (Learning, wrapped) | Strips out-of-range markers, returns which in-range indices were used | Same limitation — a marker pointing at a real, in-range source is accepted regardless of whether that source supports the claim |
| `compute_scorecard` (Research, wrapped) | `faithfulness = supported / len(verified_claims)`, where `verified_claims` comes from `_extract_candidate_claims`'s **numeric-regex extraction only** (`agents/nodes.py:206-208`) | Any claim without a `$`/`%`/`bps` token — i.e. exactly `01 D-10`'s blind spot, reproduced unchanged inside the evaluation harness because M10 wraps this function rather than replacing it (Document 45 §14's own explicit, correct design choice — wrapping keeps evaluation honest to production, but production's own gap comes along for the ride) |
| Learning graph itself | No fact-checker node exists (`07 LG-6`: *"No fact-checker in the Learning graph; grounding via prompt + deterministic citation validation"*) | Numeric or qualitative claim verification of any kind — Learning has strictly less grounding machinery than Research to begin with |

This is not a defect in M10 — Document 45 §15 explicitly scoped deterministic checks to what is "already expressible as a rule against structured or lightly-parsed text" and named the exact class this document now addresses as a deferred future extension, "once the deterministic layer proves where its false-negative rate... is actually too high in practice." That evidence already exists, pre-dating M10 itself: `D-10` is a *production* pipeline gap, independently documented, not a hypothetical one this document is inventing a problem to justify.

---

## 3. Hallucination Threat Model

Eight failure modes, scoped narrowly enough to be individually testable — not a single undifferentiated "hallucination" bucket:

| # | Failure mode | Definition | Caught by M10 today? |
|---|---|---|---|
| 1 | **Unsupported factual claim** | A claim stated as fact with no support anywhere in the evidence actually offered to the model | No — unless numeric (Research only, partially) |
| 2 | **Contradicted factual claim** | A claim that actively conflicts with what an offered/cited source states (source: revenue −4%; output: revenue +4%) | No |
| 3 | **Invented causal explanation** | A causal narrative ("revenue fell *because of X*") where the underlying fact may be correctly grounded but `X` is not stated or supportable by any offered evidence | No |
| 4 | **Fabricated citation** | An `[n]` marker with no corresponding declared/in-range source | **Yes** — the one class M10's structural checks already catch completely (range/index validation across all three surfaces) |
| 5 | **Citation that does not support the associated claim** | A structurally valid, in-range, declared, used citation whose source content does not actually contain or support the specific claim beside it | No — this is the core gap; see §2 |
| 6 | **Unsupported quantitative statement** | A specific number/percentage not present in, or inconsistent with, the offered evidence | Partially — Research only, via `D-10`'s numeric-regex fact-checker; not Learning (no fact-checker) or Comparison Explanation (structural citation checks only) |
| 7 | **Unsupported interpretation** | An evaluative/qualitative claim ("strong momentum," "concerning trend") not tied to specific cited evidence | No, and only partially tractable by design — interpretation carries irreducible subjectivity that a factual-support check cannot fully adjudicate (§6) |
| 8 | **Omission vs. fabrication** | Not itself a failure mode — silently *dropping* a metric is not hallucination. Comparison Explanation already models deliberate, disclosed omission via `limitations`/`evidence_completeness: "partial"` (Document 43 §9-11, wrapped by M10 today). The failure this document targets is an **unacknowledged** omission paired with an **invented substitute** — which reduces to failure modes 1–3 above, not a ninth category | Acknowledged omission: yes (existing `limitation_reference` check). Silent omission alone: correctly out of scope — not fabrication |

Failure modes 4 and (partially) 6 are already M10's job and are explicitly **not** re-solved here. This document's actual target is **5, 2, 3, 1**, with **7** named honestly as only partially addressable by any of the candidate approaches below (§5).

---

## 4. Existing M10 Architecture Dependency (verified this session, direct reads)

| Component | File | Verified finding |
|---|---|---|
| Golden dataset schema | `evaluation/golden_dataset/models.py` | `ExpectedBehavior` has a closed, Pydantic-enforced `match_rule` set: `keyword_variant`, `citation_required`, `limitation_reference` (`_ALLOWED_TYPES_BY_RULE`, `_check_combination` validator) — a fourth `match_rule` is a schema extension, not a breaking change (Pydantic Literal + validator, additive) |
| Behavioral evaluators | `evaluation/core/behaviors.py` | Dispatch by `match_rule` via a plain `dict` (`_EVALUATORS`) — Document 45 §11's own "no plugin registry" principle, reused identically for a new rule: one more dict entry |
| Case-level result shape | `evaluation/core/types.py` | `BehaviorEvaluation` (frozen dataclass): `behavior_id`, `match_rule`, `status`, `reason` — four fields, no room for a confidence score or judge identity today |
| Metrics | `evaluation/core/case_evaluator.py` | Exactly Document 45 §13's four metrics; `EVALUATION_VERSION = "v1"`, bumped "when this module's metric/status logic changes... so a metric-definition change is distinguishable from a model/prompt change" — the exact mechanism this document's judge-mode extension needs (§7) |
| Regression baseline | `evaluation/regression/result_store.py`, `.../compare.py`, `.../types.py` | Baseline compatibility key (Document 46 §5): `(case_id, dataset_version, case_version, evaluation_version, schema_version)` — five-field exact match; `evaluation_version` already exists as the field that isolates "the metric logic changed" from "the model/prompt changed" |
| CLI | `backend/scripts/run_evaluation.py` | `argparse`, `--mode fixture\|live`, `--format text\|json`; not wired into CI (`19`/`46 §2`) |
| LLM abstraction | `agents/llm.py` | `chat_text`/`chat_json`, multi-provider, `_active()` read-only provider/model introspection, `DEFAULT_LIGHT_MODEL`/`DEFAULT_HEAVY_MODEL` tiers — the evaluation harness's only sanctioned path to a model call, per repo convention (CLAUDE.md: "LLM access goes through `agents/llm.py` only") |
| Structured-output precedent | `agents/comparison_explanation.py` | `chat_json(system, user, ComparisonExplanationSchema, model=DEFAULT_LIGHT_MODEL)` plus an explicit `PROMPT_VERSION`/`SCHEMA_VERSION` pair — the exact pattern a judge call would reuse |
| Observability | `infrastructure/observability/metrics.py` | Zero evaluation-specific metrics exist today (confirmed by full-file grep) — M10 never added Prometheus instrumentation for evaluation runs, consistent with "on-demand, developer-invoked, not production" (§11 below) |
| Prompt-injection stance | `10_Backend_Security_Architecture.md` `SR-5` | Prompt injection via corpus/source content is an **accepted, monitored residual risk**, not eliminated — directly relevant to §10, since a judge call reads the same untrusted evidence text |

No file above is modified by this document. Every extension in §7–§9 is additive to this table.

---

## 5. Candidate Detection Approaches

| Approach | Detection capability | Determinism | False-positive risk | False-negative risk | Cost/latency | Provider dependency | Testability | Explainability |
|---|---|---|---|---|---|---|---|---|
| **A. Deterministic numeric-consistency check** (extend `ExpectedBehavior` with `match_rule="numeric_consistency"`: compare a number in the output against a case-authored expected value drawn from fixture evidence) | Narrow — catches only anticipated, numeric contradictions (failure mode 2/6) | Full | Near-zero (exact/near-exact match) | High — anything non-numeric, or any value the case author didn't anticipate, passes untouched | None | None | Full (unit-testable like every other Phase 3 evaluator) | High — exact mismatch, cites both values |
| **B. Adversarial dataset cases via the existing `keyword_variant`/absence mechanism** (author fixture evidence with a deliberate trap; assert the output must *not* contain a specific wrong conclusion) | Narrow but real — catches only the specific contradiction a case author anticipated and encoded (failure modes 1–3, case-by-case) | Full | Near-zero | Same paraphrase-miss risk Document 45 §22 already accepts for every `keyword_variant` case | None | None | Full | Full — reuses existing, already-tested code path unchanged |
| **C. Generic lexical/token-overlap "support" heuristic** (naive n-gram containment between claim sentence and cited source text, stdlib-only, same spirit as `compute_scorecard`'s Jaccard `answer_relevance`) | Weak and, worse, *misleadingly* confident — high false-positive rate (shared vocabulary ≠ support) and high false-negative rate (correct paraphrase ≠ low overlap) | Full | **High** — this is the deciding flaw | High | Low | None | Partial | Low — a numeric score with no principled threshold |
| **D. Model-assisted claim verification** (`chat_json` call: claim + cited evidence text → `SUPPORTED \| CONTRADICTED \| UNSUPPORTED \| NOT_APPLICABLE` + rationale) | Broad — the only approach that reaches failure modes 1, 2, 3, and partially 7 | **Not guaranteed**, even pinned (§7) | Judge-model-dependent, unquantified without the judge's own held-out evaluation | Judge-model-dependent, same caveat | One extra LLM call per judged behavior per case per run | Yes — whichever provider services the call | Low by nature (statistical correctness, not a deterministic unit-testable property) | High — can return a rationale span, a real strength over A/B/C |
| **E. Semantic-similarity embeddings** (repurpose `fastembed`, already a retrieval dependency, to score claim/evidence similarity) | Moderate, unproven for this specific task | Full (embeddings are deterministic per model version) | Unquantified — embedding similarity is a well-known poor proxy for factual entailment/contradiction, and this repo has never used `fastembed` for that purpose | Unquantified, same caveat | Low (no new dependency, local inference) | None | Partial | Low — a cosine-similarity number, no rationale |
| **F. Hybrid — A/B as the default always-on layer, D as a bounded, explicitly opt-in extension for the claim classes A/B/C structurally cannot reach** | Broad where opted in, narrow-but-free everywhere else | Deterministic layer: full. Judge layer: bounded and disclosed, never silently blended with deterministic PASS/FAIL (§9) | Deterministic layer: near-zero. Judge layer: same as D, but scoped to only the cases that need it | Lower than D alone (deterministic layer catches the cheap cases without spending a judge call) | Bounded — judge calls only for behaviors a case author explicitly marks | Only for judged behaviors, clearly labeled | Deterministic layer fully testable; judge layer testable at the contract/plumbing level, not at the "is the verdict correct" level | Deterministic layer: full. Judge layer: high (rationale), clearly distinguished from deterministic results |

**C is rejected outright**, not merely deprioritized: a heuristic that reports false confidence is worse than no check at all for an equity-research product (§10) — it would let a "PASS" badge sit on exactly the kind of qualitative fabrication this document exists to catch, while looking like a real signal. **E is rejected** on the same "don't build ahead of evidence" principle Document 45 §9/§23 already applies to infrastructure choices: it adds a new consumer of an existing dependency for a task (entailment/contradiction detection) embeddings are not well-suited to without a labeled evaluation of their own — which is D's cost, paid without D's strength (a rationale). **A and B are not sufficient alone** — see §6. **D alone is not proportionate** — running a judge call on every behavior, including the ones a regex already answers for free, is unjustified cost and unjustified nondeterminism.

---

## 6. Comparative Architectural Analysis — Deterministic vs. Qualitative Fabrication

Document 45 §15 already answers this question for M10's own scope, correctly: every metric M10 needs is expressible as a rule against structured or lightly-parsed text. That is true *because* M10 deliberately scoped itself to structural/aggregate properties (§6.1 of that document: "Behavioral, not snapshot"). Hallucination detection's threat model (§3 above) is different by construction — failure modes 1, 2, 3, and 7 are claims about *whether cited content supports specific asserted content*, which is a semantic entailment/contradiction judgment, not a structural one. No amount of additional regex or keyword-variant authoring turns "does source X actually say Y" into a deterministic check for arbitrary, unanticipated `Y` — approaches A/B/C above prove this by their own ceiling (A: only pre-encoded numbers; B: only pre-anticipated phrasings; C: not even that, just a bad proxy).

This is the same tension Document 45 §15 named explicitly when it deferred model-assisted evaluation rather than building it: a model-assisted judge introduces "its own evaluation... a second, nested version of exactly the problem `01 D-10` names, not a solution to it." That warning is correct and is not overridden here — it is the reason §7's judge layer is scoped as narrowly, disclosedly, and optionally as it is, rather than as a blanket replacement for M10's deterministic core.

**Resolution:** deterministic and model-assisted are not competing answers to the same question — they answer different slices of §3's threat model. The deterministic layer (A/B) stays the default, zero-cost, fully-reproducible backbone, extended along M10's existing architecture exactly as designed. The model-assisted layer (D) is added as a distinct, clearly-labeled capability for the specific failure modes (1, 2, 3, partially 7) that are structurally unreachable any other way — never silently merged into the same PASS/FAIL semantics a deterministic check produces (§9).

---

## 7. Dataset / Adversarial-Case Architecture

**Load-bearing rule (frozen): claim and evidence selection is deterministic; the judge only adjudicates.** The deterministic evaluation layer — never the model judge — identifies (1) the exact generated claim being evaluated and (2) the exact evidence being evaluated against it. The judge receives exactly that pair (§7.2) and returns only a relationship verdict (§7.3). The judge must not: select which claim to check, select which evidence is relevant, discover on its own which claims might be hallucinations, or redefine what counts as support. This is the same discipline `keyword_variant`/`citation_required`/`limitation_reference` already enforce today — a case author (or, here, a deterministic selector keyed off case-authored data) decides what gets checked; nothing in this design lets the model decide what to evaluate. **The selector is one narrow, fixed mechanism, not a general-purpose claim-extraction framework** — no NLP, no configurable extraction pipeline, no per-case choice of extraction strategy. Everything below is scoped to keep that true.

**Reuses `BenchmarkCase`/`ExpectedBehavior` (Document 45 §7) — no new dataset-level entity.** Two new rows extend the existing constraint table:

| `match_rule` (new) | Allowed `type` | Applicable surfaces | Additional field(s) | What it checks |
|---|---|---|---|---|
| `numeric_consistency` *(deterministic, §5-A)* | `presence` only | **Research, Learning only** (§7.0 — not Comparison Explanation) | `reference` (required) — dotted/bracket path into `case.context`'s fixture evidence naming the authoritative value (e.g. `source_documents[0].some_field`); `tolerance` (required) — relative tolerance as a fraction (e.g. `0.01` = 1%), case-authored, never a hidden default | §7.1 |
| `model_judged_support` *(model-assisted, §5-D/F)* | `presence` only | **Research, Learning only** (§7.0 — not Comparison Explanation) | `reference` (required) — a `source_id` matching an entry in `NormalizedOutput.citations`, the same identifier `citation_required` already resolves against | §7.2 |

Both forbid `variants` (`keyword_variant`'s own field) and both slot into the existing `_ALLOWED_TYPES_BY_RULE` table / `_check_combination` validator (`golden_dataset/models.py`) as two more rows — the same additive mechanism Document 45 §7 already used for its original three, not a new validation architecture.

### 7.0 Shared claim/evidence selector (frozen, used by both rules below)

**Both `numeric_consistency` and `model_judged_support` locate their claim and evidence identically** — one mechanism, not two, so the two rules cannot drift into inconsistent selection semantics. This corrects a real gap in the prior revision: `numeric_consistency` originally scanned the *entire* `NormalizedOutput.text` for any matching number, which independently rediscovers the whole-narrative false-confidence problem this design otherwise refuses to accept — a correct, unrelated figure stated elsewhere in the response could satisfy a check about a different claim entirely (worked example: fixture revenue `$120M`; output *"Revenue declined to $95M [1], while another period reported $120M."* — a whole-text scan would incorrectly `PASS` on the unrelated `$120M`, when the claim actually tied to `[1]` is `$95M`). The rule below closes that gap for both behavior types at once.

1. **Resolve the target source, and require it to be eligible evidence before anything else runs.** For `model_judged_support`, `reference` *is* the `source_id` directly. For `numeric_consistency`, `reference`'s fixture path is resolved to a `source_id` using **each surface's own already-existing, verified `Citation.source_id` construction** — never a newly-invented mapping (§16 unchanged: no new dependency, no new mapping framework):
   - **Research (`evaluation/adapters/research.py`) and Learning (`evaluation/adapters/learning.py`), verified by direct read this session:** both build `Citation(source_id=str(i), ...) for i in range(1, len(docs) + 1)` — `source_id` genuinely *is* a plain 1-based `source_documents` array index, identical code shape in both adapters. `reference`'s leading array index `k` (`source_documents[k]...`) therefore maps exactly to `source_id = str(k + 1)`. This is a verified fact about the existing code, not an assumption.
   - **Comparison Explanation (`evaluation/adapters/comparison_explanation.py`), verified by direct read this session — the assumption in Revision 3 was wrong here:** `Citation.source_id` is `f"{report_id}:{field_name}"` (`_eligible_source_ids`/`_normalize`), a compound identity string keyed on the fixture report's own `id` and the evidence field name — **not** a positional index into `fixture_reports`, and **not** the narrative's `[n]` marker number either. The marker number a citation actually uses in the text (`result["sources"][j]["index"]`, per `agents/comparison_explanation.py`'s `validate_and_map_citations`) is assigned by the *model itself*, decoupled from fixture array order by an arbitrary `report_number`↔`index` mapping the model declares per response — so there is no fixed position or formula this document can freeze for it.
   - **Resolution — smallest correct fix, not a new mapping framework:** Option A (freeze positional ordering as canonical) is correct and adopted **only for Research and Learning**, where it is a verified fact about existing code. It is **not** adopted for Comparison Explanation, because it would be false there, not merely undocumented. A literal Option B (a second, separately-authored `source_id` field decoupled from `reference`) was considered and rejected: it would let a case author's `reference` (the expected-value lookup) and a separate `source_id` field silently point at two different pieces of evidence, reintroducing exactly the authored-value-can-drift risk Document 45 §7 already designed `numeric_consistency`'s single-field `reference` to prevent. **Comparison Explanation is therefore out of scope for both `numeric_consistency` and `model_judged_support` in this document** (§7.0 continues below) — narrower than either option offered, because neither option is correct for this surface as the architecture stands today.
   - In every case where a `source_id` *is* resolvable (Research/Learning only): if it has no matching entry in `NormalizedOutput.citations`, or the matching entry's `eligible` is `false` (Document 45 §11's own field — "was this source available to the model as citable evidence at all"), or the fixture/live content associated with it cannot be resolved — the behavior is **`INCONCLUSIVE`**, never `FAIL`. The judge, and the numeric comparator, must never be handed fabricated or ineligible evidence dressed up as legitimate evidence.
2. **Locate every sentence in `NormalizedOutput.text` containing that `source_id`'s citation marker**, via the same sentence-boundary split already used in this codebase (`agents/nodes.py`'s `re.split(r"(?<=[.?!])\s+", text)`) plus the same `[(\d+)]` marker regex every citation-validation function in this repo already applies. This step is well-founded only where step 1 resolved a `source_id` that *is* the marker number — Research/Learning, per the above.
3. **Zero matching sentences → `INCONCLUSIVE`** (no claim exists to evaluate — a construction failure, not a quality signal).
4. **More than one matching sentence → `INCONCLUSIVE`.** This is the deterministic, narrowest rule for "the same citation marker appears more than once" (whether in one sentence repeated or across multiple sentences): which occurrence is "the" claim cannot be resolved without guessing, and guessing is exactly the failure mode this section exists to close. Other, unrelated citation markers also present in the selected sentence (e.g. `"[1][2] Revenue was $95M."` when `reference` is `1`) do not by themselves create this ambiguity — only multiple *occurrences of the referenced marker itself* do.
5. **Exactly one matching sentence → that sentence is the selected claim**, handed to the rule-specific logic below. Nothing upstream or downstream of these five steps performs any additional extraction, parsing, or discovery — this is the entire selector, deliberately not a general-purpose claim-extraction framework.

**Surface scope, stated plainly (frozen):** `numeric_consistency` and `model_judged_support`, as specified in this document, apply to **Research and Learning only**. Case construction/validation must reject either `match_rule` on a `comparison_explanation` case (the same `_check_combination`-style enforcement Document 45 §7 already applies to `match_rule`↔`type` pairings, extended with one more rejection condition, not a new validator). Extending either rule to Comparison Explanation requires first resolving how (or whether) a marker↔`source_id` mapping can be surfaced through `NormalizedOutput` without reading `AdapterResult.output.raw` — which Document 45 §11 already places off-limits to the evaluator core ("kept for debugging only — never read by the evaluator core") — a genuine open question, not answered here, and explicitly not answered by quietly reading `raw` as a workaround.

**A real, load-bearing practical consequence of this scoping, reported rather than left implicit:** Research and Learning — the two surfaces where this section's claim selector is sound — have **no FIXTURE mode implemented today** (Document 45 §11.1's retriever stand-in remains deferred; Document 46 §3/§8 reconfirm it, and reconfirm Comparison Explanation as "the only surface with a working FIXTURE mode today"). Comparison Explanation — the one surface with working FIXTURE mode — is exactly the surface this section excludes. As things stand, `numeric_consistency`/`model_judged_support` behaviors can be authored and exercised only in **LIVE** mode against Research/Learning, and Document 45 §11.1 already establishes that LIVE-mode results are never eligible as a regression baseline. Concretely: **neither new rule can produce a regression-eligible result until Research/Learning's FIXTURE mode is built** — an already-named, already-deferred gap this document does not create and is not scoped to fix, but whose interaction with this specific proposal is new information worth having on the record before anyone estimates what "implement `numeric_consistency`" actually delivers on day one.

### 7.1 `numeric_consistency` — fully specified

**Research and Learning only (§7.0) — Comparison Explanation is out of scope for this rule.**

- **Reference shape:** `reference` is a dotted/bracket path into `case.context["source_documents"]` (e.g. `source_documents[0].some_field` — the exact sub-field shape is Research/Learning's own source-document content, not fixed by this document), resolved by plain, stdlib dict/list traversal — no jsonpath library, no new dependency (§16 unchanged). **The expected value is never separately authored in the case body** — it is always derived from fixture evidence already present, so a case cannot silently drift out of sync with its own fixture content. The same path's leading index also drives claim selection (§7.0 step 1, verified positional for these two surfaces) — one field, not two.
- **Claim selection:** §7.0's shared selector, unchanged — the single sentence containing the referenced marker, or `INCONCLUSIVE` per §7.0 steps 3–4.
- **Numeric extraction — from the selected claim sentence only, never the full output:** reuses the existing numeric-token regex already in this codebase (`agents/nodes.py`'s `_extract_candidate_claims`: `\$[\d,\.]+[MBK]?|\d+(?:\.\d+)?\s?%|[+-]?\d+(?:\.\d+)?\s?(?:bps|pp)`) applied only to §7.0's selected sentence — reused, not reimplemented, matching Document 45 §14's own "reuse, don't reinvent a fourth regex" discipline. Each match is normalized to a comparable scale (currency `M`/`B`/`K` suffixes and `bps`/`pp` converted to consistent units) before comparison.
- **Selected claim contains more than one numeric token → `INCONCLUSIVE`.** Same "don't guess" discipline as §7.0 step 4, applied one level deeper: `numeric_consistency`'s comparator is a plain value match, not a reader, so it cannot determine *which* of several numbers in one sentence is the cited claim — unlike `model_judged_support`, whose judge can read a full sentence in context and is not subject to this restriction (§7.2). This is also what fully closes the worked example above: sentence-scoping alone narrows the search to one sentence, but that sentence can still contain more than one number (as the example's does, `$95M` and `$120M` in the same clause) — this rule is what refuses to guess between them rather than silently accepting whichever happens to match.
- **Selected claim contains exactly one numeric token → compare it to the resolved expected value.** `PASS` if within `tolerance`, else `FAIL`.
- **Tolerance semantics:** relative (a fraction of the expected value), **required on every `numeric_consistency` behavior** — never a repository-wide constant, so this document does not invent a threshold a case author didn't explicitly choose (the same discipline §9.1 applies to itself). **Zero-value case, frozen:** when the resolved expected value is exactly `0`, relative tolerance is undefined (division by zero) — the comparison uses **exact equality** instead (the extracted, normalized token must equal `0`). Non-zero expected values always use relative tolerance; this is the one, explicitly-named exception, not a general fallback rule.
- **Referenced fixture value missing:** the dotted path fails to resolve (key absent, index out of range, value `null`) → `INCONCLUSIVE` — a dataset-authoring/construction problem, not a quality signal, matching M10's own established convention (`no_output_reason`, `find_baseline`'s missing-baseline case) that construction failures never read as `FAIL`.
- **Selected claim contains no numeric value at all:** a determinate **`FAIL`**, not `INCONCLUSIVE` — the check *could* be constructed (the expected value resolved fine, exactly one claim sentence was selected); the model simply stated no matching figure in it. This mirrors `evaluate_keyword_variant`'s existing precedent exactly: a well-formed presence check that finds nothing is `FAIL`. (Distinct from the fixture-missing case above, which is a construction failure, not a model-quality outcome.)
- The standard `no_output_reason` guard applies first, unchanged, identical to every existing evaluator — empty `NormalizedOutput.text` is `INCONCLUSIVE` before any of the above runs.

### 7.2 `model_judged_support` — fully specified

**Research and Learning only (§7.0) — Comparison Explanation is out of scope for this rule.**

- **Evidence and claim selection:** §7.0's shared selector, unchanged — `reference` names the `source_id` directly; evidence is that source's resolved, eligible fixture/live content; the claim is the single sentence containing its marker, or `INCONCLUSIVE` per §7.0's steps 1, 3, 4. Unlike `numeric_consistency`, a claim sentence containing more than one numeric value is **not** itself ambiguous here — the judge is asked to read the whole selected sentence in context, which is precisely the task a judge (and not a plain comparator) is for.
- **What the judge receives:** exactly the (claim_text, evidence_text) pair §7.0 produced — nothing else. Not the full narrative, not the full evidence corpus, not the case's other behaviors. This is what makes "the judge only adjudicates, never discovers" true structurally, not just by prompt instruction.

### 7.3 Judge verdict → status mapping (frozen)

| Judge outcome | `BehaviorEvaluation.status` |
|---|---|
| `SUPPORTED` | `PASS` |
| `CONTRADICTED` | `FAIL` |
| `UNSUPPORTED` | `FAIL` |
| `NOT_APPLICABLE` | `INCONCLUSIVE` |
| Provider failure (call errors) | `INCONCLUSIVE` |
| Malformed/schema-invalid judge output | `INCONCLUSIVE` |
| Judge timeout/deadline exceeded | `INCONCLUSIVE` |

**Frozen rule: judge failure or uncertainty must never become `FAIL`.** Only a genuine, well-formed, successfully-returned `CONTRADICTED` or `UNSUPPORTED` verdict produces `FAIL` — every failure-to-adjudicate path (provider error, malformed output, timeout, `NOT_APPLICABLE`) maps to `INCONCLUSIVE`, matching every existing M10 error-handling convention (`no_output_reason`, `AdapterError`'s four categories, `find_baseline`'s missing-baseline handling) without exception. This does not add a fourth `Status` value — `PASS`/`FAIL`/`INCONCLUSIVE` remains the complete domain (unchanged from Document 45 §12); `JudgeDetail.verdict`'s four values (§8) map onto it, never extend it.

### 7.3.1 `UNSUPPORTED` vs. `NOT_APPLICABLE` relevance policy (frozen, Revision 5)

**This subsection is a reference-labeling and evaluation-interpretation policy, not a judge instruction.** It governs how a case author or reviewer determines the correct verdict for a claim/evidence pair — for authoring `HeldOutCase.reference_verdict` (`evaluation/self_consistency/cases.py`) and for reading self-consistency pilot results against that reference — the same way `JudgeVerdictSchema`'s own field descriptions (`agents/schemas.py`) already state what each of the four values means, except stated here with the worked precision those one-line descriptions left underspecified. It does not alter `_SYSTEM_PROMPT` or any other text sent to the judge (§10.1's instructions/claim/evidence channel separation is unchanged), and it does not alter §7.3's verdict→status mapping table above.

**Relevance is evaluated first, and is a property of what the evidence is about, not of how strongly it confirms the claim:**

```
EVIDENCE
   ↓
Is the evidence relevant to the claim?
(subject/entity compatibility, metric/disclosure
compatibility, and temporal applicability — all three)
   ↓
 ├── NO  → NOT_APPLICABLE
 │
 └── YES → what does the evidence say?
             ├── confirms the claim         → SUPPORTED
             ├── directly opposes the claim → CONTRADICTED
             └── neither                     → UNSUPPORTED
```

Once evidence clears the relevance test, failure to confirm the claim's specific proposition never produces `NOT_APPLICABLE` — only `UNSUPPORTED` or `CONTRADICTED` remain available outcomes.

**Explicit-absence rule.** Evidence containing "no guidance was provided," "no information was disclosed," "not disclosed," "not provided," or equivalent absence/disclaimer language must not automatically become `NOT_APPLICABLE`. If the statement concerns the same subject/entity, the same or a directly related metric/disclosure proposition, and a temporally applicable period, the evidence has engaged with the claim's subject — it is explicitly reporting an absence of information about it, which is `UNSUPPORTED`. Only evidence that is genuinely irrelevant by the test above produces `NOT_APPLICABLE`.

**Temporal rule.** A temporal mismatch by itself does not imply `NOT_APPLICABLE`. Evidence about the same subject/entity and a relevant metric/disclosure proposition from a different reporting period is still relevant evidence — historical evidence offered against a forward-looking claim is normally `UNSUPPORTED`; a different reporting period alone is not sufficient for `NOT_APPLICABLE`. `NOT_APPLICABLE` on temporal grounds is reserved for evidence whose temporal scope is structurally incapable of bearing on the claim because continuity of the relevant subject/entity itself breaks down (e.g. a divested or not-yet-existing business unit) — ordinary historical-vs-forward comparisons are not reinterpreted as automatically irrelevant.

**Metric/disclosure relevance rule.** "Same disclosure category" must not be read so broadly that any two financial metrics automatically become relevant to each other, and merely sharing a broad financial-results section is not sufficient on its own. Evidence is relevant when it concerns the same metric/proposition the claim asserts, or a directly related metric/disclosure proposition that a reasonable evaluator could meaningfully use to assess the claim — similarity of broad topic or financial domain alone is insufficient; the evidence must be meaningfully about the proposition being evaluated. Worked examples (claim held fixed: *"Operating margin increased."*):
- Evidence *"Operating margin increased from 30% to 32%."* → `SUPPORTED`.
- Evidence *"Operating margin decreased from 32% to 30%."* → `CONTRADICTED`.
- Evidence *"No operating-margin guidance was provided."* → `UNSUPPORTED`.
- Evidence *"Gross margin increased from 40% to 42%."* → `NOT_APPLICABLE`, unless the evidence actually establishes a meaningful evidentiary relationship to the operating-margin proposition — gross margin and operating margin are different metrics, and proximity within the same filing/section does not by itself make one relevant evidence for the other.

A second pair of examples (claim: *"Apple revenue will increase."*): evidence *"Microsoft's revenue increased."* → `NOT_APPLICABLE` (different entity, subject/entity rule below controls regardless of metric match). Evidence *"Apple's historical revenue declined."* → relevant evidence (same entity, same metric); normally `UNSUPPORTED` for the forward-looking claim, unless it affirmatively establishes the opposite proposition, in which case §7.3.1's contradiction rule below applies instead. No further metric taxonomy is defined beyond what these examples establish.

**Property axis — what it is measured over (frozen, Revision 6).** The metric/disclosure relevance rule above is evaluated over the **underlying reported quantity or business fact** the claim asserts something about — **not** over the claim's full proposition. Evidence concerns the **same property** as the claim when it concerns that same underlying quantity or business fact, a stated direct component of it, or the aggregate of which it is a stated direct component.

The following four dimensions are **not** property axes. A difference on any of them, alone or in combination, must never independently produce `NOT_APPLICABLE`; each is resolved at the support-classification stage instead, as `SUPPORTED`, `CONTRADICTED`, or `UNSUPPORTED`:

1. **Modality** — reported/actual versus expected, guided, forecast, or planned; and statements about whether a disclosure or guidance exists at all. *"No revenue guidance was provided,"* *"the company has not determined whether it will provide revenue guidance,"* and *"the company expects revenue growth"* all concern the same property: revenue.
2. **Polarity** — increase versus decrease, presence versus absence, affirmation versus negation. Polarity determines *which* of `SUPPORTED`/`CONTRADICTED`/`UNSUPPORTED` applies; it never determines applicability.
3. **Tense and aspect** — level versus change, completed period versus forward period, historical versus prospective. *"Revenue this quarter was $50 million"* and *"revenue is expected to grow next quarter"* concern the same property. Temporal scope is governed solely by the temporal rule above; the property axis must not re-decide it.
4. **Granularity and units** — segment versus consolidated, absolute versus percentage, currency, per-share versus total. A stated direct component or aggregate of the claim's quantity is the same property at a different granularity.

Consequently, relevant absence, explicit uncertainty, plain relevant silence, and modality, polarity, temporal, or granularity differences all remain **applicable** and proceed to support classification — they are `UNSUPPORTED`, or `CONTRADICTED` where the contradiction rule below is satisfied, never `NOT_APPLICABLE`. This restates, and does not modify, the explicit-absence and temporal rules above: under Revision 6 those rules follow from the property axis's definition rather than standing only as separate stipulations that a broader reading of the property test could silently override.

A **property-axis failure** therefore requires the evidence to concern a **genuinely different underlying reported quantity or business fact** — one that is neither the claim's quantity nor a stated direct component or aggregate of it. A different *value, direction, modality, period, tense, or granularity of the claim's own quantity* is not a property-axis failure. A line-of-business or product description, a legal proceeding, or a governance disclosure offered against a revenue claim does fail the property axis, per the metric/disclosure relevance rule's existing standard.

**Direct component and aggregate relationships are applicable but may be insufficient.** Evidence about a stated direct component of the claim's quantity (e.g. a segment's revenue offered against a total-revenue claim), or about the aggregate of which the claim's quantity is a stated direct component (e.g. total revenue offered against a segment-revenue claim), clears the property axis. Clearing the property axis is not support: such evidence commonly fails to establish the claim's specific proposition, and is then `UNSUPPORTED`. Applicability and support remain two separate, sequential questions, exactly as the decision diagram above already states.

**Open boundary — the related-but-distinct metric tier (`MORE EVIDENCE REQUIRED`; not resolved by this revision).** Whether evidence about a distinct financial metric that is **neither** the claim's quantity **nor** a stated direct component or aggregate of it — for example gross margin offered against an operating-margin claim — is `NOT_APPLICABLE` or applicable-but-`UNSUPPORTED` is **not resolved here**, and this revision deliberately declines to invent a rule for it. The ratified corpus currently answers both ways: this subsection's own gross-margin worked example above answers `NOT_APPLICABLE` (retained unchanged), while two already-authored cases exhibiting the same relation — `boundary_pair4_a_applicable_silent_same_subject` and `research_unsupported_missing_eps` — carry reference verdict `UNSUPPORTED` and are not listed in Revision 5's reclassification table above. Neither answer is adopted here, no reference verdict is changed, and no metric taxonomy is defined — consistent with the metric/disclosure relevance rule's existing statement that no further metric taxonomy is defined beyond what its examples establish. Resolving this tier is a separate, subsequent CTO-authorized action.

**Authoring prohibition while that boundary is open (frozen, Revision 6).** Until a separate, subsequent CTO governance decision resolves the related-but-distinct metric tier, **no new evaluation case may be authored whose `reference_verdict` depends on that tier** — not in `evaluation/self_consistency/cases.py`, not in `evaluation/self_consistency/cases/`, not in any boundary-experiment or diagnostic case directory, and not in the golden dataset. Existing cases that turn on the tier are to be read as sitting on an acknowledged open boundary rather than as defects, and are not relabeled by this revision. This prohibition constrains future case authoring only; it authorizes no edit, no relabeling, and no deletion of anything that exists today.

**Subject/entity mismatch rule.** Evidence concerning a different company, business unit, product, or other relevant subject than the claim names is `NOT_APPLICABLE`, regardless of whether the unrelated evidence contains similar numbers or similar wording.

**Contradiction rule.** `CONTRADICTED` requires an affirmative opposing proposition in the evidence — absence of confirmation is never itself contradiction. Claim *"Revenue will increase,"* evidence *"No guidance was provided"* → `UNSUPPORTED`, not `CONTRADICTED`. Claim *"Revenue will increase,"* evidence *"Management expects revenue to decline"* → `CONTRADICTED`.

**Existing case impact (documentation only — no case file or reference verdict is modified by this document).** Applying the policy above to cases already authored under Phase C/M11 self-consistency work:

| Case | Current reference | Under this policy |
|---|---|---|
| `research_not_applicable_unrelated_topic` (`evaluation/self_consistency/cases/`) | `NOT_APPLICABLE` | `UNSUPPORTED` — same entity, same metric (revenue growth), temporal-only mismatch, explicit absence disclaimer |
| `boundary_pair1_b_notapplicable_guidance_absent` | `NOT_APPLICABLE` | `UNSUPPORTED` — same shape as above |
| `boundary_pair3_b_notapplicable_learning_guidance_absent` | `NOT_APPLICABLE` | `UNSUPPORTED` — same entity, same metric (operating margin), temporal-only mismatch, explicit absence disclaimer |
| `boundary_pair4_b_notapplicable_different_subject` | `NOT_APPLICABLE` | `NOT_APPLICABLE` (unchanged) — evidence is a product/business description, not a financial-results disclosure; fails the metric/disclosure relevance rule independent of time |
| `boundary_pair2_b_notapplicable_unrelated_subject` | `NOT_APPLICABLE` | `NOT_APPLICABLE` (unchanged) — evidence concerns legal proceedings, an unrelated subject; fails the subject/entity rule |

Relabeling any of the three affected cases is a separate, subsequent CTO-authorized action, not performed by this revision.

**Consequence for the previously blocked three-way boundary experiment.** The "Case B" condition (explicit, relevant absence disclaimer) that blocked that experiment for lack of a policy-derivable reference verdict now has one: `UNSUPPORTED`. Running that experiment, or any other change to self-consistency tooling, fixtures, or the judge gate, remains a separate, subsequent CTO authorization — none of that is granted by this revision.

### 7.4 Pre-gate behavior: judged results do not count until validated

Until §9.1's empirical self-consistency gate clears, a `model_judged_support` behavior still executes and still produces a full `BehaviorEvaluation` with `judged_by="model"` and `judge_detail` populated (§8) — but its `status` is **excluded** from `_characteristic_coverage_metric`'s determinable set and from `_overall_status`'s fail/inconclusive aggregation (`evaluation/core/case_evaluator.py`). It is recorded and disclosed, never silently dropped, but it cannot move a case's overall `PASS`/`FAIL` until §9.1 clears it — the "plumbing/experimentation, not yet a production-equivalent gate" distinction made concrete at the exact point where it would otherwise silently take effect.

**Adversarial fixture content remains dataset content in principle, not a new storage mechanism** — the same one-file-per-case JSON convention Document 45 §9 already established, whichever surface's fixture format applies. A "known-trap" case looks like today's seed cases, deliberately authored so the referenced evidence contains a specific, checkable fact (for `numeric_consistency`) or a specific, verifiable claim tied to a specific citation marker (for `model_judged_support`), optionally alongside a plausible-but-wrong distractor value. No new file format, no new loader, no new directory. **For `numeric_consistency`/`model_judged_support` specifically, this is currently a statement of principle, not an executable path today** — §7.0's practical-consequence note already covers why: Research/Learning (the only surfaces these two rules apply to) have no FIXTURE mode, so a "known-trap" case for either rule can only be exercised in LIVE mode until that gap is closed, non-baseline-eligible in the meantime. `fixture_reports`-based adversarial authoring already works today, but only for Comparison Explanation, and only for the existing `keyword_variant` rule (§5-B) — not for the two new rules this section defines. **Negative-evidence / contradiction fixtures** (deliberately misleading source text), wherever they are executable, use the same mechanism, adversarially authored — not a generic "the model must never be wrong" assertion, but a specific, falsifiable, case-scoped one, consistent with Document 45 §6.1's "behavioral, not snapshot" principle carried one level deeper.

---

## 8. Evaluation-Result Architecture

**Minimal, additive extension — no field is removed or repurposed from Phase 1–4's frozen shapes.**

`BehaviorEvaluation` (`evaluation/core/types.py`) gains two optional fields, defaulted so every existing deterministic evaluator's construction call is unaffected:

```
BehaviorEvaluation:
  behavior_id   : str            # unchanged
  match_rule    : str            # unchanged
  status        : Status          # unchanged — PASS | FAIL | INCONCLUSIVE, same three values, no fourth added
  reason        : str            # unchanged
  judged_by     : "deterministic" | "model" = "deterministic"   # NEW — the one field this document actually needs
  judge_detail  : JudgeDetail | None = None                      # NEW — populated only when judged_by == "model"
```

```
JudgeDetail:
  judge_model        : str    # from agents.llm._active(), same convention as ExecutionMetadata.model
  judge_prompt_version : str   # a new explicit version constant, mirroring Comparison Explanation's PROMPT_VERSION precedent — never a content hash, since this is an authored, versionable prompt from day one
  verdict             : "SUPPORTED" | "CONTRADICTED" | "UNSUPPORTED" | "NOT_APPLICABLE"
  rationale           : str    # the judge's own explanation — never itself re-parsed or matched, exactly the same "documentation only" discipline Document 45 §7 already applies to ExpectedBehavior.description
```

This is deliberately **not** a change to `CaseEvaluationResult`, `EvaluationResult`, or the five-verdict regression truth table (Document 45 §18, Document 46 §6) — a model-judged `BehaviorEvaluation` still resolves to exactly one of the same three `Status` values every deterministic evaluator already produces, and `_overall_status`/`compare()` consume `Status` values uniformly regardless of `judged_by`. The regression machinery does not need to know a behavior was judged rather than pattern-matched to compute PASS/WARNING/REGRESSION/UNCHANGED_FAILURE/INCONCLUSIVE correctly — `judged_by`/`judge_detail` exist purely for **disclosure and audit**, not for verdict computation. This is the smallest extension that satisfies §10's non-negotiable requirement (a judged result must never be visually or programmatically indistinguishable from a deterministic one) without touching a single frozen Phase 1–4 contract.

**Pre-validation, `judged_by`/`judge_detail` are recorded but a `model_judged_support` behavior's `status` does not count toward the case (§7.4).** This is an aggregation-time exclusion, not a schema difference — the fields above are unconditionally populated the same way regardless of whether §9.1's gate has cleared; only whether the resulting `status` is allowed to influence `CaseEvaluationResult.status` changes.

**Baseline compatibility reuses `evaluation_version` — no new key field.** `evaluation_version` is already defined (Document 45 §12/§17, `case_evaluator.py`'s own docstring) as "version of the harness/metrics logic itself, so a metric-definition change is distinguishable from a model/prompt change." A judge-model or judge-prompt change *is* exactly this kind of metric-definition change. Recommendation: bump `EVALUATION_VERSION` whenever `judge_prompt_version` changes, exactly as it would for any other evaluator-logic change — Document 46 §5's five-field baseline key (`case_id, dataset_version, case_version, evaluation_version, schema_version`) already excludes stale-judge-vs-new-judge comparisons correctly, with zero schema change to the compatibility key itself.

---

## 9. Determinism / Reproducibility Analysis (model-assisted layer)

Named explicitly, per the commissioning task's own requirement not to hide nondeterminism:

- **Model identity:** pinned via `agents.llm._active()`, recorded in `judge_detail.judge_model` — read-only, same convention as `ExecutionMetadata.model` today.
- **Prompt/version:** a new, explicit `JUDGE_PROMPT_VERSION` constant (mirroring `agents/comparison_explanation.py`'s `PROMPT_VERSION` precedent exactly) — not a content hash, because this is a purpose-built, human-authored prompt from its first line, unlike Research/Learning's retrofitted `prompt_fingerprint` gap (Document 45 §17).
- **Temperature/determinism assumptions:** recommend the lowest-variance setting the active provider exposes (temperature 0 or equivalent) via the same `chat_json` call path every other structured-output call in this codebase already uses — **stated honestly, not as a guarantee**: providers do not commit to bit-identical output at temperature 0 across calls, model versions, or backend routing changes. This is the same category of variance Document 45 §11.1 already documents for FIXTURE-mode's own live model calls; nothing here claims a stronger guarantee than M10 itself already declines to claim.
- **Output schema:** a new Pydantic model in `agents/schemas.py`'s existing convention, validated the same way `ComparisonExplanationSchema` is today — `verdict` (closed enum) + `rationale` (free text, documentation-only, never re-parsed).
- **Reproducibility limitation, stated plainly:** a judge rerun on identical input is not guaranteed to reach the identical verdict every time. This must be measured, not assumed, before any judge-mode PASS/FAIL is trusted at the same weight as a deterministic one — recommended as an explicit prerequisite of implementation (§19), not something this architecture can certify in advance.
- **Provider dependence:** yes, same as every `chat_json` caller in this codebase — a provider outage or malformed structured output maps to `INCONCLUSIVE` (§10), never `FAIL`, matching every existing M10 error-handling convention (`no_output_reason`, `AdapterError`'s four categories).
- **Cost implications:** bounded by explicit per-behavior opt-in (§7's `model_judged_support` is authored deliberately per case, never applied dataset-wide by default) and by M10's existing on-demand-only execution model (§11) — no CI, no production traffic multiplies it.

### 9.1 Self-consistency validation gate (frozen)

Before any `model_judged_support` result is allowed to influence a case's overall `PASS`/`FAIL` (§7.4), the following must happen, in order:

1. Construct a held-out judge evaluation set — cases/claim-evidence pairs not used to author or tune the judge prompt.
2. Run repeated judge evaluations against that held-out set (same input, multiple calls).
3. Measure judge self-consistency — how often repeated calls on identical input reach the same verdict.
4. Record model identity and `judge_prompt_version` alongside every measurement, so a later prompt/model change invalidates the prior measurement rather than silently inheriting its result.
5. Evaluate disagreement rates and characterize *where* the judge is unreliable, not only an aggregate agreement rate.
6. Review the results through the normal CTO/reviewer gate — the same review discipline every other decision in this document series already goes through.

**No numerical acceptance threshold is fixed by this document.** No existing governance document defines one, and inventing a number here (e.g. "95% agreement") would be exactly the kind of unjustified precision this document elsewhere refuses to manufacture (§5 declines to invent a false-positive/negative rate for the judge approach on the same grounds). The threshold is a judgment call for whoever reviews the step 1–5 measurements in step 6, not a value this architecture document supplies in advance.

**Frozen rule:** absent a completed gate, a judge may exist for plumbing and experimentation — it may be built, called, and its output recorded (§7.4, §8) — but its verdict must not be trusted as a production-equivalent evaluation gate. This is not a process reminder for implementation to honor at its discretion; it is the reason §7.4's aggregation-time exclusion exists as an architectural rule rather than a suggestion.

---

## 10. Security / Trust Considerations

- **False confidence is the primary risk this document exists to prevent, and the one its own design could reintroduce if built carelessly.** A judge-produced PASS must never render, log, or persist identically to a deterministic PASS — `judged_by`/`judge_detail` (§8) exist specifically so this cannot happen by omission.
- **False positives/negatives** are judge-model-dependent and, per §9, unquantified until measured — this document does not claim a rate, and implementation should not ship a judge-mode result as a trusted gate before one is established empirically.
- **Citation trust:** unaffected for the deterministic layer (§7's `numeric_consistency`/`model_judged_support` are additive checks; they do not alter `validate_and_map_citations`/`_postprocess_citations`/`compute_scorecard`'s existing behavior, per §0's "no M10 file is modified" constraint).
- **Adversarial source content / prompt injection:** a judge call reads the same untrusted evidence text the production pipelines already read. This is not a new risk class — it is `10 SR-5`'s already-accepted, already-monitored residual risk (prompt injection via corpus/source content), extended to one more consumer of that same text. §10.1 freezes the specific containment contract.
- **Evaluator contamination:** if the same person authors both a case's adversarial fixture content and tunes the judge prompt, there is a real circularity risk — the judge could be shaped to agree with what the fixture author already expects. This is a process risk (recommend: judge disagreements get human-reviewed, not auto-accepted), not one an architecture document can close by itself.
- **Explicit, load-bearing disclaimer:** this capability, at any maturity, does not and cannot guarantee factual correctness. It narrows a specific, named blind spot (§3); it does not certify the absence of hallucination. No implementation of this design should present a PASS as a correctness proof.

### 10.1 Evidence/claim trust boundary (frozen contract)

A judge call receives exactly three, clearly separated channels:

1. **Evaluation instructions** — the judge's system prompt, authored as part of implementation, never derived from case or evidence content.
2. **The generated claim** — untrusted data, produced by §7.0's shared deterministic claim selector.
3. **The source evidence** — untrusted data, produced by §7.0's shared deterministic evidence selector.

**Claim and evidence are data, never instructions.** The judge must not treat text found inside either channel as a directive to follow, regardless of its phrasing or apparent authority — the same instruction/data separation this codebase already applies everywhere untrusted content reaches a prompt. Structured output is validated through the existing Pydantic/`chat_json` convention (§9), exactly as every other structured-output call in this codebase, no bespoke parsing.

**This is explicitly a containment boundary, not an elimination of prompt-injection risk.** It does not certify that source evidence can never influence the judge outside the intended relationship-adjudication task — it bounds the blast radius the same way `10 SR-5` already does for every other consumer of untrusted corpus content in this codebase, and inherits that document's accepted-residual-risk stance rather than asserting a stronger guarantee this design cannot back up.

---

## 11. Production Boundary

**Evaluation-harness extension only** — same boundary M10 itself drew (Document 45 §5, §19; Document 44 §4.1 point 8: "internal engineering-quality tool, not user-facing behavior"). Not CI-gated, not a production monitor, not user-facing. This matches Document 17 §7.1's own original framing of hallucination detection as "a structured, sampled adversarial check" inside the evaluation platform — not a runtime guardrail. Expanding into CI enforcement or production monitoring would need its own, separately-justified architecture decision (the same "build when the trigger fires, not ahead of it" discipline Document 17 §7.4 and Document 45 §5 already apply elsewhere in this codebase) — not implied or pre-authorized by this document.

---

## 12. Cost / Latency Considerations

- **Deterministic layer (A/B, §5, §7):** zero additional cost or latency — same execution model as every existing M10 evaluator.
- **Model-assisted layer (D/F):** one additional `chat_json` call per `model_judged_support` behavior, per case, per harness run — using `DEFAULT_LIGHT_MODEL` (matching Comparison Explanation's own tier choice for a bounded, structured task), bounded by explicit per-behavior opt-in, not applied to every case or every behavior by default. Total cost scales with how many behaviors a dataset author chooses to mark `model_judged_support`, and with how often a developer invokes the CLI (§11 — on-demand only, no CI multiplier, no production traffic multiplier).

---

## 13. Observability Considerations

None proposed, matching M10's own precedent exactly: `infrastructure/observability/metrics.py` carries zero evaluation-specific instrumentation today (verified, §4), consistent with this being a local, developer-invoked CLI rather than a live service. The CLI's existing `--format text|json` output (`run_evaluation.py`) remains the only observability surface needed at this scope — extended, if implemented, to print `judged_by`/`judge_detail.verdict` alongside the existing per-case line, no new mechanism required. If this capability is ever promoted to CI or production (explicitly not authorized here, §11), *that* promotion is the trigger to add real metrics/tracing — not this document.

---

## 14. Ownership

**Backend & AI owned, fully** — same as M10 (Document 44 §4.1 point 8, point 9: no product semantics required, no API contract required, no new or changed route). No Product/UX dependency exists or is created by this design; evaluation results are a developer-facing CLI output, not a rendered UI surface, so no frontend work is implied by results someday being displayable — consistent with the commissioning task's own instruction not to manufacture frontend scope from a hypothetical future display.

---

## 15. Explicit Non-Goals

- The detector, judge prompt, new `match_rule` implementations, or any new CLI flag — none of this is built by this document.
- Any change to `agents/graph.py`, `agents/learning_nodes.py`, `agents/comparison_explanation.py`, `agents/scoring.py`, or any other production pipeline file.
- Any change to `evaluation/golden_dataset/models.py`, `evaluation/core/*`, `evaluation/regression/*`, or `backend/scripts/run_evaluation.py` — the extensions in §7/§8 are proposed, not applied.
- CI integration of any kind.
- Production monitoring or a user-facing hallucination indicator.
- A claim that any resulting detector guarantees factual correctness (§10).
- Resolving the governance discrepancy named in §0 — surfaced for CTO awareness, not adjudicated here.
- A generalized, provider-agnostic "judge framework" for future unrelated use cases — this design is scoped to the specific `model_judged_support` behavior type, not a reusable judging platform (the same "no premature plugin architecture" discipline Document 45 §11/§23 already applied to surface adapters).
- Extending `numeric_consistency`/`model_judged_support` to Comparison Explanation (§7.0) — blocked on a marker↔`source_id` mapping that does not exist anywhere outside `AdapterResult.output.raw`, which Document 45 §11 already places off-limits to the evaluator core. Not solved by this document, and not worked around by reading `raw`.
- Building Research/Learning's FIXTURE-mode retriever stand-in — already a named, deferred gap (Document 45 §11.1, Document 46 §3/§8), not this document's to fix, even though §7.0 reports that it is what currently keeps `numeric_consistency`/`model_judged_support` from producing a regression-eligible result at all.

---

## 16. Dependency Analysis

No new dependency. The model-assisted layer routes through `agents/llm.py`'s existing `chat_json`/`chat_text` (multi-provider, already in place); the structured-output schema follows `agents/schemas.py`'s existing Pydantic convention. `E` (embeddings via `fastembed`) was considered and rejected (§5) specifically to avoid repurposing an existing dependency into an unproven role — the deliberately conservative choice consistent with `CLAUDE.md`'s "keep dependencies lean" and "confirm nothing already installed does the job" before reaching for anything new. No test framework, CI tool, or storage technology changes.

---

## 17. Recommended Architecture

**Hybrid: deterministic extension (§7's `numeric_consistency` + adversarially-authored `keyword_variant` cases) as the default, always-on, zero-cost layer; model-assisted judging (§7's `model_judged_support`, §8's `judged_by`/`judge_detail` extension, §9's disclosed-nondeterminism contract) as a narrow, explicitly opt-in extension for the specific failure modes (§3: 1, 2, 3, partially 7) the deterministic layer structurally cannot reach.**

Both extend Document 45's existing architecture additively — a new `match_rule` value plus two new optional `BehaviorEvaluation` fields — never modifying a Phase 1–4 frozen contract, never touching the five-verdict regression semantics, never adding a new top-level entity or storage mechanism.

---

## 18. Decision Rationale

Per the commissioning task's own decision menu (§14): **Option B — a hybrid deterministic + model-assisted approach is justified.**

- **Not Option A (deterministic-only):** §6 shows this is not a scoping choice but a ceiling — failure modes 1/2/3/7 are semantic-support judgments no amount of additional regex/keyword authoring turns into a deterministic check for unanticipated claim content. Recommending "deterministic only" would mean quietly redefining "hallucination detection" down to "harder `keyword_variant` cases," which does not answer the threat model the commissioning task itself specified.
- **Not Option C (model-assisted required and unconditionally acceptable):** unjustified cost and unjustified nondeterminism for the sub-problems (numeric contradiction, anticipated phrasing) a zero-cost deterministic check already answers reliably — running a judge call where a regex suffices is waste, not rigor.
- **Not Option D (defer entirely):** unlike a generic "hallucination detection is hard" deferral, this document found a specific, bounded, already-precedented extension path (§7/§8) that does not require solving semantic entailment in general — only for a narrow, case-author-scoped, explicitly-disclosed subset. Deferring indefinitely would leave `01 D-10`'s already-documented, already-triggered (Document 17 §7.1's own condition, satisfied per Document 44 §5) gap unaddressed with no architectural reason to keep waiting.
- **Option B is the only one that both respects Document 45 §15's correct warning about nested judge-evaluation problems (by keeping the judge layer narrow, optional, and disclosed) and actually reaches the failure modes M10 cannot (by not pretending a deterministic-only design can).**

---

## 19. Implementation Boundary

**Not authorized by this document.** If implementation is separately authorized, the sequencing below applies — informational only, not itself an authorization, matching Document 45 §24's own framing — with an explicit hard gate at step 6:

1. `numeric_consistency` `match_rule` + schema/validator extension (§7.1) — fully deterministic, no judge dependency.
2. Adversarial fixture case authoring using the existing `keyword_variant`(absence) mechanism (§7.4) — dataset content only, zero code change beyond case JSON files.
3. `model_judged_support` contract, schema (`JudgeDetail`/`judged_by`, §8), and plumbing (§7.0's shared claim/evidence selector, the judge call itself, §7.3's verdict mapping) — built, callable, and disclosed; results recorded but excluded from case-level `PASS`/`FAIL` per §7.4.
4. Held-out judge self-consistency evaluation (§9.1, steps 1–5).
5. CTO/reviewer decision on the §9.1 results (§9.1 step 6).
6. **Hard gate:** only after step 5 clears does a `model_judged_support` behavior's status stop being excluded from `_characteristic_coverage_metric`/`_overall_status` (§7.4) — i.e. only then may it influence a case's `PASS`/`FAIL`.
7. CLI output extension to surface `judged_by`/rationale (§13) — additive to `run_evaluation.py`'s existing `--format` handling.

**Steps 1–3 are independently implementable and do not depend on step 4 or later** — each is independently reviewable and independently revertible, mirroring Document 45 §24's own sequencing discipline. **Step 6 is the one hard gate in this sequence:** nothing before it requires §9.1's empirical validation, and nothing at or after it may skip it. Nothing in this document authorizes starting step 1.

---

## 20. Governance Status

**Hallucination Detection Architecture:**
🟢 CTO APPROVED / FROZEN (2026-08-18, Revision 5 as specified; Revision 6 ratified 2026-08-19 as specified)

**Implementation:**
🔴 NOT AUTHORIZED

Frozen means what it means throughout this document series (Document 45 §25, Document 46 §10): the decisions in §17/§18, and each constraint restated in the CTO's approval message — the hybrid architecture; `numeric_consistency` and `model_judged_support` scoped to Research/Learning only, both fully specified per §7.0–§7.4; the judge verdict→status mapping (§7.3); `judged_by`/`judge_detail` disclosure (§8); the mandatory, threshold-free self-consistency gate (§9.1); Comparison Explanation's explicit exclusion (§7.0) without reading `AdapterResult.output.raw`; Research/Learning's FIXTURE-mode gap staying out of this document's scope (§15); and the no-embeddings/no-generic-framework/no-CI/no-production-monitoring/no-new-dependency boundary (§11–§16) — are final unless a future CTO architecture decision explicitly supersedes them. **This is not implementation authorization.** No detector, schema extension, CLI change, or CI job exists as a result of it, and no existing M10 or production pipeline file was modified to produce it (§0, §18 governance note notwithstanding — that note reports a *pre-existing* discrepancy this document did not create). Implementation authorization remains a separate, subsequent CTO decision, exactly as Document 45 §25 and Document 46 §10 already established for M10 itself, and exactly as this approval's own message states.
