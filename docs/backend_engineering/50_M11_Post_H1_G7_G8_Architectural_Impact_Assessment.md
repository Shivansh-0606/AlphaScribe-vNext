# 50 — M11 Post-H-1: G7 / G8 Architectural Impact Assessment

**Status:** 🟢 **ACCEPTED — CTO RATIFIED (§16). Implements nothing.**
This document is an architecture/governance assessment, not an implementation
authorization and not an amendment. Acceptance of this assessment does not
modify Document 47 (frozen), does not modify Document 48 (draft, unratified),
does not modify Document 49 (ratified H-1 closure record), does not modify
`judge.py`, `judge_gate.py`, `schemas.py`, the H-1 runner, or any historical
experiment artifact, and does not authorize a new experiment. Follows the
same "options + recommendation, no implementation" convention as
[47_Hallucination_Detection_Architecture_Decision_Pack.md](47_Hallucination_Detection_Architecture_Decision_Pack.md).
**Date:** 2026-08-23. **Ratified:** 2026-08-23.

---

## 1. Context

M11 Phase H-1 is formally closed
([Document 49](49_M11_Phase_H1_Generalization_Evidence_and_Closure_Package.md),
CTO disposition `CLOSE WITH GOVERNANCE FOLLOW-UP`). Two findings were
explicitly carried forward rather than resolved: **G7** (causal-prerequisite
applicability, unresolved) and **G8** (inferred geographic membership treated
as explicitly stated, carried forward). This document performs the follow-up
architectural assessment Document 49 named as a separate, subsequent
authorization — it does not reopen H-1 itself.

## 2. H-1 Closure Reference

Authoritative state, taken as given and not re-litigated: Reviewer 3
`CONDITIONAL`; 4 ratified controls × 5 repetitions = 20 matching trial-level
observations (not 20 independent controls); CTO `CLOSE WITH GOVERNANCE
FOLLOW-UP`; Run 2 not required; no implementation authorized by H-1. Source:
Document 49 §5, §8, §21.

## 3. G7 Analysis

**Trace:**

```
H-1 observation:        5/5 NOT_APPLICABLE on a causal-prerequisite case
                         (capacity expansion vs. production output)
        ↓
underlying behavior:    the Stage 1 applicability judge classifies a
                         causal-prerequisite relationship as NOT_APPLICABLE,
                         consistently
        ↓
existing system
boundary:                Document 48 §4 already PROPOSES "causal
                         prerequisites" as explicitly out of scope for the
                         applicability rule ("evidence establishing a
                         precondition for the claim's quantity, not a part
                         of it") — unratified, but already drafted and on
                         record before H-1 ran
        ↓
architectural
responsibility:          Stage 1 applicability judge prompt
                         (`_APPLICABILITY_SYSTEM_PROMPT`,
                         `backend/evaluation/core/judge.py`), which already
                         states the rule matches: "This covers only a
                         literal, stated part-whole relationship, not a
                         merely related, correlated, or prerequisite fact"
        ↓
potential product
consequence:              none — this judge has no production consumer (§5)
```

1. **What behavior did G7 expose?** The judge, presented with a
   causal-prerequisite claim/evidence pair, returned `NOT_APPLICABLE` in
   all 5 trials.
2. **Reproducible from existing evidence?** Yes, within the narrow bounds of
   one case × 5 repetitions (Document 49 §13).
3. **What kind of limitation?** None of the four candidate categories the
   task's own framework offers (model/workflow/evaluation/architectural)
   applies cleanly, because the observed behavior **matches the
   already-proposed rule** rather than violating it. This is closer to a
   confirmatory data point than a limitation.
4. **Does the existing architecture already have a boundary?** Yes, at two
   levels: the judge prompt's own text already excludes prerequisite
   relationships from applicability, and Document 48 §4 already names this
   exact exclusion as a proposed (not yet ratified) boundary.
5. **Frozen product requirement implicated?** None found — Document 47 §14
   already establishes no Product/UX dependency exists for this evaluation
   capability, and nothing in `docs/experience_design/` or
   `docs/frontend_architecture/` touches evidence classification.
6. **Is a new architecture decision required?** No. G7 is consistent with,
   not contrary to, the boundary the architecture already anticipates.

**Why Document 49 still calls G7 "unresolved," and why that is correct and
not overridden here:** the diagnostic question H-1 set out to test was
narrower than "is the verdict right" — it was whether a specific
pre-registered failure mode (modality-conflation, i.e. confusing a causal
condition with a statement about likelihood/expectation) would appear in the
rationale text. Because every trial exited at `NOT_APPLICABLE` before that
distinction could ever become live, the specific risk was never exercised.
That is a **narrow evaluation-coverage gap** (one case, one wording, an
oracle-free probe by design — Document 49 §13), not an architectural one.
This document does not resolve G7 and does not reclassify it; it only
adds that the consistent 5/5 result observed is the behavior the current
prompt design and Document 48 §4's proposed rule both already predict.

## 4. G8 Analysis

**The authoritative observation** (Document 49 §14): in 5 of 5 trials, the
Stage 1 applicability judge returned `APPLICABLE` for a claim about "total
North American sales" given evidence about "western United States" sales,
asserting the region is a "stated" or "direct" component of the aggregate —
when no such statement exists in the evidence text at all. Zero hedging in
any of the 5 rationales.

**Does the existing architecture distinguish explicit from inferred
evidence?**

- **In the judge prompt** (`_APPLICABILITY_SYSTEM_PROMPT`,
  `_SYSTEM_PROMPT`, `backend/evaluation/core/judge.py`): partially, and
  deliberately. The granularity clause — added specifically in response to
  the earlier M-04/M-05 finding (Document 47 §7.3.1 Revision 6, Document
  48) — already says the component/aggregate exception covers "only a
  **literal, stated** part-whole relationship, not a merely related,
  correlated, or prerequisite fact" (`judge.py` lines 97–105, 263–271). The
  word "stated" is already load-bearing in the prompt text. What the prompt
  does **not** yet do is give a worked example distinguishing a **stated**
  part-whole relationship (e.g. "the Hardware segment, part of our three
  reportable segments...") from a **plausible-but-unstated real-world**
  containment relationship (e.g. "western United States" as a geographic
  subset of "North America," true in reality but never asserted by the
  text) — exactly the gap the M-04/M-05 fix closed for *numeric* segment/total
  pairs, not yet closed for this different shape of inference.
- **In production** (`agents/nodes.py::fact_checker_node`,
  `_extract_candidate_claims`): no distinction exists, because no
  qualitative/relational grounding check exists there at all — the
  production fact-checker is scoped, by longstanding and already-documented
  design (`01 D-10`), to numeric-token matching only. G8 does not newly
  expose this; `D-10` already fully documents it, independently of H-1.
- **In evidence/claim/citation representation**
  (`agents/schemas.py`, `Citation` construction in
  `evaluation/adapters/*.py`): no field anywhere records whether a cited
  relationship was stated or inferred. `JudgeVerdictSchema.rationale` and
  `ApplicabilityVerdictSchema.rationale` are free text, "documentation
  only, never re-parsed or matched" (Document 47 §7.3, §8) — so even where
  the judge's own reasoning states its inference was assumptive, nothing
  downstream reads that.

**Is this distinction currently at the appropriate architectural
boundary?** The prompt (interpretive/rubric layer) is the correct and
sufficient place for it — not retrieval, not evidence representation, not
the schema, not the API contract, not persistence. Reasoning quoted from
`judge.py` itself: the applicability decision is defined entirely as a
semantic judgment made inside one `chat_json` call against exactly two text
channels (claim, evidence) — there is no upstream or downstream layer in
this design that participates in that judgment at all (§10.1's frozen
three-channel trust boundary). A representational fix (a new schema field)
cannot substitute for a rubric fix, because the underlying problem is what
the model concludes from the text it already receives, not what data it is
missing.

## 5. Existing Architecture Assessment

| Mechanism | File | Verdict | Why |
|---|---|---|---|
| Stage 1 applicability judge prompt | `evaluation/core/judge.py` (`_APPLICABILITY_SYSTEM_PROMPT`) | **EXTEND** | Correct boundary, already partway there ("stated" is already load-bearing text); lacks a worked example for the inferred-real-world-containment case G8 surfaced, the same shape of gap the Rev 6 granularity clause already closed for numeric component/aggregate pairs |
| Legacy single-call judge prompt | `evaluation/core/judge.py` (`_SYSTEM_PROMPT`) | **EXTEND, mirrored** | Same rubric text duplicated for the v3-naN path; any Stage 1 fix should mirror here for consistency, per the same duplication Rev 6 already required across both prompts |
| Self-consistency gate | `evaluation/core/judge_gate.py` (`JUDGE_SELF_CONSISTENCY_GATE_VERSION`) | **PRESERVE** | Already functioning exactly as designed — G8 is precisely the kind of "characterize where the judge is unreliable" evidence Document 47 §9.1 step 5 exists to gather. Gate is at `0`; no judge verdict, reliable or not, currently influences anything |
| `JudgeVerdictSchema` / `ApplicabilityVerdictSchema` / `SupportVerdictSchema` | `agents/schemas.py` | **PRESERVE** | The existing closed verdict enums are structurally sufficient; `UNSUPPORTED` already exists and could house "relevant evidence that only implies, but does not state, the claim" if a future policy ever chose that resolution, without a schema change |
| Production fact-checker | `agents/nodes.py::fact_checker_node`, `_extract_candidate_claims` | **NO CHANGE** | Numeric-only by longstanding, independently-documented design (`01 D-10`, `ponytail:`-marked). Not touched by, and has no coupling to, the evaluation judge (verified: no `evaluation.*` import anywhere under `agents/`, no `agents.*` import in `agents/graph.py` pulls in judge code) |
| Retrieval / evidence acquisition | `agents/retrieval.py` | **NO CHANGE** | Not implicated — G7/G8 are judge-reasoning findings, not retrieval-quality findings; the evidence text in both cases was exactly what the case author supplied |
| Citation schema / provenance | `agents/schemas.py` `Citation`, adapter `source_id` construction | **NO CHANGE** | No representational gap identified; the problem is what the judge concludes from text it already has, not a missing field |
| API contract / MongoDB / Redis / LangGraph state | n/a | **NO CHANGE** | This judge is not wired into `AgentState`, any LangGraph node, or any API response — confirmed by direct import-graph inspection |

## 6. Explicit vs. Inferred Evidence Assessment

Three categories, and where each currently lands:

- **Explicit evidence** (source directly states the fact) — already handled
  correctly per H-1's ratified controls (G1/G2/G4a, Document 49 §8).
- **Unsupported assertion** (no source support at all) — already a defined
  outcome (`UNSUPPORTED`) in both `JudgeVerdictSchema` and
  `SupportVerdictSchema`.
- **Inferred evidence** (derived from a source fact via outside/world
  knowledge, not stated by the source) — **not currently a distinct
  category anywhere in the architecture.** G8's case was routed to
  `APPLICABLE` (Stage 1) as if it were explicit. The architecturally
  interesting question this raises for a *future* decision, not answered
  here, is not "add a fourth verdict value" (Document 47 §7.3's
  `PASS`/`FAIL`/`INCONCLUSIVE` domain and the four-way judge-verdict enum
  are both frozen, and nothing about G8 requires a fifth verdict) but
  **whether "inferred-only" membership should route to `UNSUPPORTED`
  rather than `APPLICABLE`/`SUPPORTED`** under the existing enum — i.e. a
  rubric decision, expressible entirely in prompt text, not a schema
  change.

## 7. Trust / Grounding Implications

- **Source trust, citation correctness, provenance:** unaffected today —
  this judge produces no citation, no persisted claim, and no user-facing
  output of any kind.
- **Claim reliability / user interpretation:** unaffected today, for the
  same reason — no production surface reads this judge's verdicts.
- **Auditability:** intact. `judge_detail`/`judged_by` (Document 47 §8) and
  `JUDGE_SELF_CONSISTENCY_GATE_VERSION` together make the judge's
  unreliability inspectable and its non-trust explicit and versioned, not
  silent.
- **Regulatory/compliance risk:** none assessed — no technical basis in the
  inspected code or docs for a compliance claim, and none is made here.
- **Where this *would* matter:** only if `model_judged_support` is ever
  wired into a production-facing feature (a separate, future,
  Document-47-§19-gated decision, not proposed here). At that point G8
  becomes directly relevant to Document 47 §10's "false confidence is the
  primary risk this document exists to prevent" framing. Today, prior to
  any such authorization, it is a contained finding about an
  evaluation-only component.

## 8. Architectural Options

No architectural action is strictly required — see §5/§9. If the CTO elects
to act on G8 in a future, separately authorized step, two credible options:

**Option 1 — Bounded prompt-precision extension (recommended if action is
taken).**
- *Architecture:* add one explicit clause + worked example to
  `_APPLICABILITY_SYSTEM_PROMPT` (mirrored in `_SYSTEM_PROMPT`)
  distinguishing a stated part-whole relationship from a plausible-but-unstated
  real-world containment relationship — the same shape of fix as the
  Revision 6 granularity clause.
- *Responsibility boundary:* stays entirely inside the Stage 1 judge
  prompt; no other layer touched.
- *Data flow:* unchanged — still one `chat_json` call, same two channels.
- *Advantages:* smallest possible change; reuses a proven pattern
  (`JUDGE_PROMPT_VERSION`/`APPLICABILITY_PROMPT_VERSION` already exist for
  exactly this kind of versioned wording bump); fully reversible.
- *Disadvantages:* prompt wording fixes are not guaranteed to generalize —
  the same risk every prior `v3-naN` iteration already carries; requires a
  fresh, separate diagnostic measurement (not H-1 Run 2, not this task) to
  confirm it actually closes the gap before any trust weight changes.
- *Latency/cost:* zero change (no new call, no new model).
- *Reliability:* unverified until re-measured through Document 47 §9.1.
- *Complexity:* minimal — one prompt constant, one version bump.
- *Migration:* none — additive version bump only, no case data or schema
  touched.

**Option 2 — Defer; bundle into a future batched self-consistency round.**
- *Architecture:* no immediate prompt change. G8 is recorded (as it already
  is, in Document 49) and left for a future, broader §9.1 measurement round
  that may address several findings at once.
- *Responsibility boundary:* unchanged.
- *Advantages:* avoids prompt-version churn — `JUDGE_PROMPT_VERSION` is
  already at `v3-na5`, `APPLICABILITY_PROMPT_VERSION` at `v1`; each
  single-issue bump has a real audit-trail and re-measurement cost
  (Document 47 §9.1 step 4).
- *Disadvantages:* leaves a known, named blind spot in the prompt for
  longer, un-remediated (though still fully contained by the gate, §5).
- *Latency/cost/reliability/complexity/migration:* all unchanged from
  today, by definition — this option changes nothing.

**Recommendation:** Option 1, but only as a future, separately CTO-authorized
action — not performed, and not proposed as urgent, by this document. The
containment already in place (§5, §9.1 gate at `0`, no production coupling)
means there is no time pressure forcing a choice between these options now.

## 9. Recommended Architecture (this assessment's conclusion)

**No architectural change is warranted today.** The smallest correct
boundary for both G7 and G8 is the one that already exists: the Stage 1
applicability judge's prompt text, inside `evaluation/core/judge.py`,
gated from any trust by `judge_gate.py`'s versioned constant. G7 confirms
that boundary is working as intended for causal-prerequisite relationships.
G8 identifies a specific, narrow precision gap in that same boundary for
inferred-geographic-membership relationships — a gap the architecture's own
containment mechanism (the gate) already prevents from having any effect,
exactly as Document 47 §9.1 designed it to.

## 10. Data / API Implications

None justified. No change to claim schema, evidence schema, citation
schema, provenance schema, research result schema, API response contracts,
MongoDB documents, Redis state, or LangGraph state. `ApplicabilityVerdictSchema`
/ `SupportVerdictSchema` / `JudgeVerdictSchema`'s existing enums are
sufficient to express any future resolution (§6).

## 11. Performance and Cost Implications

None today (no change made). If Option 1 (§8) is later authorized: zero
latency/cost delta — same single `chat_json` call, same model tier
(`DEFAULT_LIGHT_MODEL`), no new provider dependency, no new call added.

## 12. Migration Implications

None today. If Option 1 is later authorized: an additive prompt-version bump
(`APPLICABILITY_PROMPT_VERSION` → a new value), fully backward compatible —
no existing case file, fixture, or persisted result requires modification,
consistent with how every prior `v3-naN`/Revision 6 wording change was
applied.

## 13. Risks

- **Scope-creep risk:** this assessment must not be read as authorizing
  the Option 1 prompt change itself, or as reopening H-1. It is a
  recommendation for a future, separate CTO decision only.
- **Under-reaction risk:** if `model_judged_support` is ever wired into a
  production-facing feature without first closing G8 and re-clearing it
  through Document 47 §9.1, the false-confidence risk that document's §10
  already names as its central concern would materialize for real users.
  Today that risk is inert because no production consumer exists.
- **Over-reaction risk (named in the commissioning task, §8):** building a
  new agent, node, microservice, database, or evaluator to address G8 would
  be disproportionate to a single-case, oracle-free, evaluation-harness-only
  finding already contained by an existing gate. This document does not
  recommend any of those.

## 14. Governance Boundary

- **Established by H-1:** G7 — 5/5 `NOT_APPLICABLE` on one causal-prerequisite
  case, oracle-free. G8 — 5/5 `APPLICABLE` on one inferred-geographic-membership
  case, zero hedging, oracle-free. Both single-case, non-generalizing
  observations (Document 49 §9–§14).
- **Architectural inference (this document):** G7 is consistent with an
  already-proposed (Document 48 §4, unratified) exclusion boundary and
  requires no architecture change. G8 identifies a narrow precision gap in
  the Stage 1 applicability prompt's existing "stated, not inferred"
  language, fully contained today by the self-consistency gate and by the
  judge's total absence from any production code path.
- **Proposed requirement (not approved):** Option 1 (§8) — a bounded
  worked-example addition to the Stage 1 (and mirrored legacy) applicability
  prompt. Not implemented, not authorized, by this document.
- **CTO decision required:** whether to authorize, as a separate,
  subsequent action, (a) the Option 1 prompt-wording revision, and (b) a
  follow-up diagnostic + Document 47 §9.1 self-consistency measurement to
  validate it before any change to `JUDGE_SELF_CONSISTENCY_GATE_VERSION`.
  Nothing here is self-authorizing.

## 15. CTO Decision Required

1. Whether to authorize a future, bounded Stage-1-applicability-prompt
   precision fix for the explicit-vs-inferred distinction G8 surfaced
   (Option 1, §8) — and if so, whether to also formally ratify Document 48
   §4's proposed causal-prerequisite exclusion at the same time, citing G7
   as consistent supporting evidence.
2. Whether any such future prompt change requires its own new diagnostic
   experiment (a new identity, a new immutable output path — not a Run 2 of
   H-1, and not authorized here) before `JUDGE_SELF_CONSISTENCY_GATE_VERSION`
   could ever move past `0`.
3. Whether to select Option 1 or Option 2 (§8) — or neither, given §9's
   finding that no action is strictly required now.

## 16. CTO Ratification

Recorded 2026-08-23, under CTO governance authority, following independent
Reviewer 3 assessment (`CONDITIONAL — ARCHITECTURE ASSESSMENT ACCEPTED FOR
CTO DECISION`).

```text
Document 50:
ACCEPTED

Reviewer 3:
CONDITIONAL

H-1:
CLOSED WITH GOVERNANCE FOLLOW-UP

G7:
NO ARCHITECTURE CHANGE TODAY

G8:
CARRIED FORWARD

G8 interpretation:
Narrow prompt/rubric precision gap; not infrastructure deficiency

Gate:
0

Implementation:
NOT AUTHORIZED

New experiment:
NOT AUTHORIZED

Future G8 pathway:
Bounded prompt/rubric revision
-> diagnostic experiment
-> independent review
-> evidence
-> separate gate decision
```

**Governance interpretation (mandatory separation).** *Accepted:* this
document's architectural assessment — G7 requires no architecture change
today; G8 is a narrow prompt/rubric precision gap, not an infrastructure
deficiency; no new agent, service, database, retrieval layer, or redesign is
justified by either finding. *Not accepted as implementation authorization:*
§8 Option 1's proposed prompt/rubric revision. *Not authorized:* the
diagnostic experiment that would validate that revision. *Not authorized:*
any production rollout based on G8. Accepting this document's analysis and
authorizing action on it are two different acts; this ratification performs
only the first.

**Architecture boundary.** This acceptance authorizes no implementation. Any
future change to prompts, rubrics, evaluation methodology, grounding
behavior, or claim/evidence semantics requires its own separate
authorization; any change to frozen architecture or product behavior
escalates to the CTO. `JUDGE_SELF_CONSISTENCY_GATE_VERSION` remains `0`,
unchanged by this ratification.

M11 G7/G8 work stops as of this ratification. Control returns to the CTO for
the next separately authorized task.

---

**No implementation, schema change, API change, new experiment, model
change, prompt change, or production rollout is authorized by this
document.**
