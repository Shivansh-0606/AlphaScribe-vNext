# 42 — M9 Product Decision Record: "AI Explanation of Differences" Semantics

**Status:** 🟡 Draft — Product/UX decision, pending CTO ratification
**Type:** Product Decision Record (semantics only — no architecture, no contract)
**Revision 2** — resolves item 11 (partial/non-comparable data handling), left open in Revision 1, via the reviewer-directed Option C (Partial Explanation with Explicit Evidence Boundaries). Items 1–10 and the recommended semantic level (Level 2 — Semantic Interpretation) are unchanged from Revision 1.
**Scope:** Resolves the one open item left by [41_M9_Pre_Implementation_Architecture_Decision_Pack.md §19.2](41_M9_Pre_Implementation_Architecture_Decision_Pack.md) — what "AI explanation of differences" means. Does not touch, reopen, or depend on any architecture decision in Document 41 (all frozen there — comparison stays deterministic, explanation is a separate async capability, BYOK/managed-AI inheritance, Mongo persistence, idempotency). Does not define an API endpoint, JSON schema, Mongo schema, prompt template, model, provider, job implementation, SSE, cancellation, or repository interface — those belong to the subsequent M9 API/Contract Decision Pack.

---

## Sources consulted (primary, all frozen/CTO-approved)

- [`docs/design/00_Design_Constitution.md`](../design/00_Design_Constitution.md) — §8 AI Integration Philosophy, §22 Trust & Transparency, §25 Immutable Laws (esp. Laws 3, 4, 8). 🧊 Frozen, CTO-approved 2026-07-21.
- [`docs/design/05_Screen_Inventory.md`](../design/05_Screen_Inventory.md) — SCR-07 Comparison.
- [`docs/design/06_UX_Specifications.md`](../design/06_UX_Specifications.md) — SCR-07 AI Behaviour.
- [`docs/design/02_User_Journeys.md`](../design/02_User_Journeys.md) — J-03 Comparing Candidate Companies.
- [`docs/experience_design/Components/08_AI_Components.md`](../experience_design/Components/08_AI_Components.md) — 🧊 Frozen. AI Family Contract; `AI Response Card`, `Citation Card`, `Confidence Indicator`.
- `backend/agents/learning_nodes.py` — the one AI-explanation capability already shipped in this repository (Learning), inspected as the functioning precedent for grounding/citation enforcement, not as a product-artifact source.

No document defines comparison-explanation semantics more precisely than SCR-07's own line, quoted below. This record does not invent beyond that line — it resolves the four candidate semantic levels the architecture pack deliberately left open, against it and the surrounding frozen constitution.

---

## 1. Recommended explanation semantic level

**Level 2 — Semantic Interpretation, grounded in the deterministic comparison data — is the required level.** Not raw delta alone, not materiality ranking as a separate structured feature, and not causal analysis as a general capability (see items 5–6 below for the precise, narrow exception).

This is not a new definition — it is the **existing, frozen product decision**, stated verbatim in [`06_UX_Specifications.md`, SCR-07 AI Behaviour](../design/06_UX_Specifications.md):

> "Copilot narrates the *meaning* of differences, grounded and sourced; never a buy/sell verdict."

"Narrates the meaning" is semantic interpretation by definition — explaining what the observed numerical/qualitative differences signify in a research context, not merely restating them (Level 1) and not issuing a standalone importance ranking (Level 3) or an independent causal theory (Level 4).

## 2. Why it provides measurable user value

Raw delta alone (Level 1) is not a capability worth an LLM call — the user can already read the numbers directly from the side-by-side comparison table `/reports/compare` already renders (Document 41 §2, §4: `compare_reports` already returns the full deterministic data for every compared report). An AI feature that only restates numbers already on screen fails Design Constitution §7.1 ("One primary intent per screen" / nothing exists that doesn't earn its place, Law 14) — it would be AI theater, not AI value.

Semantic interpretation earns its place because it does what the raw table cannot: turns "Company A's operating margin is 3.1pp higher than Company B's" into research-usable understanding — *why that gap is the kind of thing a researcher would want to know about*, phrased so a P-01 (portfolio-comparing user) or P-02 (learner) can act on it without independently re-deriving significance from the raw figures. This is exactly J-03's stated need: *"the user weighs candidates before allocating"* — weighing requires interpretation, not just numbers.

## 3. What the explanation MUST include

- **Grounding in the actual resolved comparison data** — the same financials/sentiment/scorecard data `/reports/compare` already returns (Document 41 §12.2, §13.2), not open-ended model knowledge. This is Constitution Law 3 and §7.3 applied to this capability, not a new rule.
- **Plain-language narration of what the differences mean**, not a bare restatement of numbers (§8: "as reasoning the user can follow... never a bare verdict").
- **Source attribution for every claim** — every stated difference traces back to the specific reports/figures it came from (§7.3, §22, `08_AI_Components.md`'s Citation Card: "never omitted").
- **Honest uncertainty** where the underlying data is thin, missing for one member, or non-comparable — stated plainly, not glossed over (§8 "How AI handles uncertainty"; Constitution Law 8; SCR-07's own "Edge Cases: A member lacks comparable data → Partial Failure flags the gap, not hidden").
- **Explicit naming of any evidence gap** — when one or more members/metrics lack comparable data, the explanation states plainly which member and which metric is incomplete or non-comparable, rather than silently narrowing scope (§11's resolved Option C).
- **Visible distinction from primary source/deterministic data** — the explanation must read as AI interpretation layered on top of the comparison table, never presented as if it *were* the deterministic data (§22, AI Response Card contract).

## 4. What the explanation MUST NOT include

- **Buy/sell/financial recommendations or investment advice**, in any form — Constitution Immutable Law 4, §8's explicit prohibition, `08_AI_Components.md`'s AI Family Contract ("No recommendations... the AI assists thinking, it does not decide"), and `01_User_Personas.md`: *"The AI assists the workflow; it does not give personalized buy/sell advice."* This is the single most repeated, most frozen rule across every product artifact reviewed.
- **Unsupported causal claims** — a statement like "Revenue increased because of X" is prohibited unless X is itself grounded in and citable to the compared reports' own source material (see item 6). An inferred or synthesized cause the model reasons its way to, without a citable source stating it, is fabrication — prohibited by Constitution Law 8 ("confidence never exceeds the evidence") regardless of how plausible it sounds.
- **Invented financial facts or figures** not present in the deterministic comparison data — the explanation may only speak to numbers/facts that are actually in the resolved report set (Law 3; matches `financial_extractor_node`'s existing "only what's in the text" grounding discipline, cited as precedent in Document 41 §13.1).
- **Inferred, estimated, interpolated, or fabricated values for data missing from one or more compared members** — when a member/metric lacks comparable data, the gap is named (item 3), never filled in; and no claim is made that would require the missing value to support it (§11's resolved Option C).
- **A verdict, ranking of "better/worse," or an authoritative conclusion presented without its reasoning** — §8: "never a bare verdict... shows how a conclusion was reached." The explanation may describe what differs and why it might matter; it must never resolve to "Company A is the better investment."
- **Any claim without a reachable source** — a source-less AI statement is, per the AI Component family contract, "a defect," not a degraded-but-acceptable output.

## 5. Whether materiality ranking is required

**Not required as a separate, structured feature.** No product artifact reviewed (Screen Inventory, UX Specifications, Journeys, Component family) calls for a ranked/scored materiality output for comparison. SCR-07 asks for narration of "meaning," not a "most important differences" list or scoring UI — inventing one here would be exactly the kind of undirected product behavior this task explicitly warns against deciding silently.

That said, *prose-level emphasis* is a natural, unavoidable consequence of "narrating meaning" well — a narrative that mentions a 40% revenue swing in the same breath as a 0.1pp margin rounding difference, with equal weight, would itself read as poor-quality interpretation. This is a writing-quality expectation inherent to Level 2, not a separate Level 3 capability, and it requires no additional product decision, schema, or ranking mechanism.

## 6. Whether causal analysis is permitted

**Permitted only in the narrow case where the cause is itself stated in and citable to the compared reports' own grounded source content — never as independently inferred or synthesized reasoning.**

Reasoning: the deterministic comparison result does not establish causal drivers between two companies' financials — it is extracted data (financials, sentiment, scorecard), not causal analysis. A model asked to freely explain *why* a difference exists, without a citable source stating that reason, would be fabricating causality exactly as the CTO's stated product principle warns against ("Revenue increased because of X" when the comparison doesn't establish X). This would also violate Constitution Law 8 (confidence must never exceed evidence) and the Component family's citation contract (no claim without a reachable source).

However, the compared reports already contain grounded, sourced content that sometimes *does* state a cause — e.g. a report's extracted `guidance` text or `sentiment_analysis` drivers, themselves already grounded in filing/earnings-call excerpts (Document 41 §5, §13.2's grounding-input discussion). If one compared report's own sourced content already attributes a cause (e.g. management's stated reason for a margin change, already captured and cited in that report), the explanation may *cite that existing, sourced attribution* — it is reporting a grounded fact from the source material, not inventing a causal theory. It may never extend, generalize, or infer a cause beyond what a citable source in the resolved report set actually states.

## 7. Citation/source attribution expectations

Every material claim in the explanation must carry a reachable source, matching this repository's one existing shipped precedent for AI-explanation citation enforcement: Learning's `_postprocess_citations`/Law 3 pattern (`backend/agents/learning_nodes.py`), where an explanation that resolves with **zero** grounded citations is treated as a failed generation, not a success with no sources. The same standard — not a new one — should govern comparison explanation: an explanation with no citable grounding in the resolved comparison data is not a degraded output to persist and show; it is a failed generation (Document 41 §14 already establishes that explanation failure must not corrupt the deterministic comparison — this record does not change that; it defines *what counts as* a valid vs. failed explanation at the product level, which the eventual failure-handling implementation should apply).

Consistent with the frozen `Citation Card`/`Evidence Card`/`Confidence Indicator` component contracts (`08_AI_Components.md`): sources should be reachable per-claim (not just one blanket "sources" link for the whole explanation), and where evidence for a particular difference is thin, that should be stated honestly (a `Confidence Indicator`-style qualitative signal — "well-supported" / "limited evidence" — rather than a fabricated precise figure), not silently omitted.

## 8. Example acceptable explanation

> "Infosys reported a 3.2pp higher operating margin than TCS this quarter (18.4% vs. 15.2%, per each company's most recent extracted financials). Infosys's own earnings commentary attributes this to lower subcontractor costs in the quarter [cited]. Revenue growth is comparable between the two (Infosys +6.1% YoY vs. TCS +5.8% YoY, both from extracted guidance figures) — the larger difference between these two companies this period is in cost structure, not top-line growth. Sentiment analysis for TCS notes a flagged risk around a client concentration issue not present for Infosys [cited]; this is not reflected in either company's headline margin figures. This is not investment guidance — it describes what changed and, where the companies' own sourced commentary explains it, why."

Why this is acceptable: every figure traces to the resolved comparison data; the one causal statement ("lower subcontractor costs") is attributed to and cited from Infosys's own sourced commentary, not inferred; it flags a qualitative signal without ranking who is "better"; it explicitly disclaims recommendation.

## 9. Example unacceptable explanation

> "Infosys is clearly the stronger investment this quarter — its margin expansion shows better cost discipline and management execution, which should continue driving outperformance. TCS's slower growth is likely due to weaker demand in its key verticals. Investors comparing these two names should favor Infosys."

Why this is unacceptable: "the stronger investment... should favor Infosys" is a direct buy/sell recommendation (Law 4, absolute prohibition); "likely due to weaker demand in its key verticals" is an inferred causal claim with no cited source establishing it (fabricated causality, item 6); "should continue driving outperformance" is a forward-looking, unsupported claim the deterministic comparison data cannot establish; nothing in the passage carries a reachable citation.

## 10. Expected user-facing behavior

Not a UI/API specification (out of scope, per this task), but the behavioral expectations any subsequent design/implementation must satisfy, per the already-frozen AI Component family (`08_AI_Components.md`) and States (`13_States.md`) this capability should present *as*, consistent with every other AI surface in the product rather than inventing a new pattern (Constitution §7.5 "Predictable and consistent"; this task's own instruction not to invent a new UX pattern where an approved one exists):

- Presented as an `AI Response Card` variant (the same family Company AI Summary, Copilot answers, and Learning explanations already use) — labeled as AI, on a distinct AI surface, never styled as if it were the deterministic comparison table itself.
- Goes through the same `AI Thinking` → `AI Streaming`/progressive-reveal → `Complete` state sequence every other AI surface in the product uses (§9; SCR-07 already states "AI explanation streams" in its own Loading Behaviour) — not a new loading pattern.
- Every claim carries inline citations via the existing `Citation Card`/`SourceReference` pattern, opening the existing `Source Preview` — reusing the mechanism J-02/SCR-06 already ship, not a comparison-specific citation UI.
- An `Insufficient-evidence` state (already defined for `AI Response Card`) applies only when the resolved comparison data cannot support *any* grounded claim at all (item 7's zero-citation case) — states so honestly, offers what is possible, per Constitution §20 ("AI cannot answer: say so honestly... never fabricate a confident answer"). A *partial* data gap (some members/metrics comparable, some not) is not this state — it is handled inline, per §11's resolved Option C: explain what's supported, name what isn't, within the same response.
- Never renders without at least one reachable citation — matching Learning's zero-citation-reject precedent (item 7) surfaced at the product/UX level as: no explanation content is ever shown to the user without grounding, full stop.

## 11. Partial/non-comparable data handling — resolved

SCR-07 already defines the deterministic-comparison-table behavior for this case
("A member lacks comparable data → Partial Failure flags the gap, not hidden"), but
left the AI explanation's own behavior undefined in the prior revision of this
record. **Resolved: Option C — Partial Explanation with Explicit Evidence
Boundaries.**

When one or more comparison members lack comparable data for a given metric:

- The explanation is generated for whatever claims the *available* resolved data
  actually supports — a data gap in one member/metric does not block the entire
  explanation. This follows Constitution §7.6 ("Recovery over failure... every
  dead-end state offers a way forward") and §20 ("AI cannot answer: say so
  honestly; offer what is possible") applied at the claim level rather than the
  whole-explanation level: blocking the entire explanation over a partial gap
  would itself be the "AI cannot answer" anti-pattern the Constitution already
  rejects, applied to a case where *some* of the answer is in fact groundable.
- Every gap is stated explicitly, naming which member and which metric is
  incomplete or non-comparable — never silently dropped. This is the same
  "flag the gap, not hidden" standard SCR-07 already applies to the deterministic
  table, extended to the explanation (§7.6, §20, and `08_AI_Components.md`'s
  `Evidence Card`/`Citation Card` "Partial (some unavailable, flagged)" state).
- Missing values are never inferred, estimated, interpolated, or fabricated to
  fill the gap — this is Constitution Law 8 (confidence never exceeds evidence)
  and item 4's "no invented financial facts" rule applied to this specific case,
  not a new rule.
- No claim is made that depends on the missing evidence — if a metric isn't
  resolvable for a member, the explanation doesn't reason about that metric
  across the full set at all; it explains what *is* supported and separately,
  explicitly, states what isn't.

```text
Supported comparison   → explain it (item 3's grounding/citation standard applies unchanged)
Unsupported comparison → explicit, named limitation ("Company C's operating margin
                          isn't available this period, so this comparison covers
                          margin for A and B only")
Missing evidence        → never inferred, estimated, interpolated, or fabricated
```

This does not change item 7's citation standard: a **fully** ungroundable
explanation (nothing in the resolved set supports any claim at all) is still a
failed generation, not a partial one with zero content — Option C governs the
*partial*-data case (some claims supported, some not); the *zero*-data case
remains governed by item 7's existing zero-citation-reject standard.

---

## Summary for the next gate

```text
Explanation semantic level:      Level 2 — Semantic Interpretation (grounded, sourced)
Raw delta:                       Required as grounding input, not the deliverable itself
Materiality ranking:             Not required as a separate feature (prose-level emphasis only)
Causal analysis:                 Permitted only when itself cited from the reports' own sourced
                                  content — never independently inferred
Citation standard:               Zero-citation output = failed generation (Learning precedent)
Recommendations:                 Absolutely prohibited (Law 4) — no exceptions
UX pattern:                      Reuses existing AI Response Card / Citation Card / States family
                                  — no new pattern invented
Partial/non-comparable data:     Resolved — Option C: explain what's supported, explicitly name
                                  what isn't, never infer/estimate/interpolate the gap (§11)
Unresolved:                      None remaining in this record
```

This record resolves [Document 41 §19.2](41_M9_Pre_Implementation_Architecture_Decision_Pack.md)'s remaining product-semantics item, including the partial/non-comparable-data question this record's prior revision had itself left open. It does not reopen, alter, or depend on any architectural decision Document 41 already froze. The next step is the M9 API/Contract Decision Pack, which may now proceed against an unambiguous semantic target with no outstanding product-semantics gaps.
