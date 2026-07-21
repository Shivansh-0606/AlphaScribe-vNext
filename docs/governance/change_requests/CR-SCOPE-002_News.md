# Change Request — CR-SCOPE-002: News (News Card / News Intelligence)

| Field | Value |
|-------|-------|
| **CR ID** | CR-SCOPE-002 |
| **Title** | Company news capability (surfaced via "News Card" component) |
| **Status** | 🟢 Resolved — Deferred to V1.1 |
| **Raised By** | Experience Design Department (Milestone 2, Phase 2) |
| **Raised On** | 2026-07-18 |
| **Type** | Product scope change (adds capability beyond frozen MVP baseline) |
| **Affects** | Component Inventory · Screen Inventory · IA · Feature Roadmap |
| **Decision** | ☐ Approve ☑ Defer ☐ Reject — **Defer to V1.1**, decided by CTO, 2026-07-21 |

> Raised because Milestone 2's component brief lists a **News Card**, but the frozen MVP sources only
> primary filings/statements, and "News Intelligence" is roadmapped to a later release. No news design
> will be produced until this CR is explicitly approved.

---

## 1. Feature Description

A **Company News** capability surfaces recent news/events relevant to a company, optionally with an
AI news summary, sentiment, and "important events". In the Milestone 2 brief this surfaces as a
**News Card** (a news item with headline, source, date, snippet). It implies a news-ingestion source
distinct from the MVP's primary-source data (SEC/BSE filings, financial statements, earnings).

## 2. Why It Was Flagged

While composing Family 09 (Research Components), the News Card could not be traced to any frozen MVP
capability. The MVP's grounding model is built on **primary sources** (filings, statements). "News"
is a *secondary, third-party* source type the MVP does not ingest, and introducing it silently would
(a) expand data scope and (b) risk weakening the trust-first "grounded in primary sources"
differentiator if news is treated as evidence.

## 3. Current Traceability Against Frozen Baseline

| Baseline document | Finding | Verdict |
|-------------------|---------|---------|
| **Product Strategy** | News appears only in the **problem statement** ("scattered across filings, statements, transcripts, and **news**") — i.e. a problem AlphaScribe helps with, **not** a listed MVP feature. | ➖ Context only, not a feature |
| **Product Vision** | MVP Goals and Our Solution center on filings, statements, summaries, comparison, reports. "News Intelligence" appears under **Long-Term Vision** (ecosystem), not MVP. | ❌ Not MVP |
| **Information Architecture** | News is **not** an IA domain or content level. Company Research content = overview, business summary, metrics, statements, SEC filings, AI insights. No news. | ❌ Not in IA |
| **Navigation Structure** | No news destination; AI navigation patterns are anchored to company/filing sources, not news feeds. | ❌ No destination |
| **Feature Roadmap** | **Version 1.1 → "News Intelligence"**: Company News, AI News Summary, Sentiment Analysis, Important Events. | ✅ Already roadmapped to **V1.1** |

**Summary:** News is excluded from the MVP and already scheduled in **Version 1.1**. Not a gap — a
boundary.

## 4. User Value

- **P-01 (Retail Investor):** medium-high — news context is genuinely useful for understanding
  recent moves. But it is *supplementary* to the MVP's core job of understanding fundamentals.
- **P-02 (Student/Learner):** low-medium — news can distract from fundamentals-first learning.
- Net: real value, but adjacent to the MVP's fundamentals-and-filings research core.

## 5. Business Value

- **Near-term (V1.1):** high — news + sentiment increases engagement and daily return visits; it is a
  natural "increase research productivity" addition, which is exactly V1.1's stated goal.
- **MVP:** low and risky — competes for scope and could dilute the "grounded in primary sources"
  trust position if rushed. Better delivered as a focused V1.1 module with its own quality bar.

## 6. Engineering Complexity

**Medium-high.**
- New third-party news data source(s), ingestion, dedup, and per-company association.
- Freshness/staleness handling, source reliability tiering, licensing/attribution constraints.
- If AI news summary/sentiment is included: additional AI pipeline, and sentiment is an
  opinion-shaped output that needs careful, non-recommendation framing.
- New states (stale news, source unavailable, no recent news).

## 7. UX Impact

- Adds a content type to Company Research (or a new surface) with its own card, list, and states.
- Must be **visually and semantically distinct from primary-source evidence** so users never mistake
  a news item for a grounded filing citation (trust boundary).
- Risk of turning the calm research surface into a busier feed if not disciplined (§23 clutter).

## 8. AI Impact

- **Sentiment analysis** is the sharp edge: it is an AI *judgment* that can read as a
  recommendation ("negative sentiment → sell signal"). Must be fenced to descriptive, sourced,
  non-directional framing to stay within **Law 4 (no recommendations)** and **Law 8 (confidence ≤
  evidence)**.
- News-derived AI claims must carry the same traceability as primary-source claims, and be clearly
  labeled as news-derived (weaker evidentiary weight than filings).

## 9. Dependencies

- A news data provider/integration (new).
- Trusted-AI model extension to handle secondary-source provenance and clearly rank it below primary
  sources.
- Coordinated with V1.1 "News Intelligence" (Company News, AI News Summary, Sentiment, Important
  Events) so the News Card is designed once, correctly, as part of that module.

## 10. Risks

- **Trust dilution:** conflating news with primary-source evidence undermines the core differentiator.
- **Recommendation drift** via sentiment (Law 4).
- **Noise:** a news feed can erode the calm, research-first experience.
- **Licensing/attribution** obligations for third-party news content.
- **Rework:** a News Card designed now, without the V1.1 news model, would likely be redesigned.

## 11. Recommended Release

**Version 1.1** — where the Roadmap already places "News Intelligence." No roadmap change required.

## 12. CTO Recommendation

### → **Defer** (to Version 1.1)

**Rationale:** News is not an MVP gap; it is an intentional boundary already scheduled for **V1.1**.
Introducing it in the MVP would add a new data source, dilute the primary-source trust position, and
create sentiment/recommendation risk — for value that is adjacent to the MVP's core job.
**Recommendation: Defer.** The "News Card" is withdrawn from the MVP component library and re-raised
inside the V1.1 News Intelligence design, where its trust boundary (news ≠ primary evidence) and
non-directional sentiment framing can be designed properly.

**If the CTO wants news context in the MVP:** consider the *minimal* form — surfacing "important
events" strictly as pointers into primary sources (e.g. filing dates), with **no** third-party news
feed, no sentiment, and clear labeling — which may stay within the primary-source model. That
minimal form would still require amending IA and Roadmap and should be sized by Engineering first.

---

*Change Request raised under the [Documentation Governance](../Documentation_Governance.md) process.
Frozen baseline remains authoritative until this CR is explicitly approved.*
