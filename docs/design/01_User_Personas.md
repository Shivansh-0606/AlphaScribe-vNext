# AlphaScribe vNext — User Personas

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 1.0.0 |
| **Phase** | Product Discovery |
| **Owner** | Product Team |
| **Approved By** | CTO Review |
| **Approval Date** | 2026-07-18 |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | Yes |

**Downstream Dependencies:** PRDs · UX Flows · Wireframes · Design Specifications ·
System Architecture · API Contracts · Database Design · AI Architecture ·
Engineering Tasks · QA Test Plans · Acceptance Criteria

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 1.0.0 | 2026-07-18 | Product Team | ✅ Approved Baseline | Initial frozen product baseline after cross-document review and consistency verification (consolidates prior discovery-phase drafts). |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Product Vision](../master-plan/02_Product_Vision.md) — source of truth for audience, MVP goals, and out-of-scope scope. |
| **Used By** | UX & design specs, roadmap prioritization, feature scoping, and engineering trade-off decisions. |
| **Related Documents** | [Product Strategy](../master-plan/01_Product_Strategy.md), [Feature Roadmap](../master-plan/03_Feature_Roadmap.md) |

---

# Introduction

This document defines the primary users of AlphaScribe. Personas exist to ground
future UX, engineering, and product decisions in observed user behavior rather
than assumptions. When a design debate arises, the question is not "what do we
prefer?" but "which persona does this serve, and how?"

Personas will be referenced throughout the project lifecycle:

- **Product** uses them to prioritize the roadmap and reject scope that serves no
  one.
- **Design** uses them to shape workflows around real research tasks.
- **Engineering** uses them to understand who feels the cost of a slow endpoint,
  a confusing state, or a missing feature.

These personas describe **behaviors, workflows, and goals—not demographics**. Age,
gender, location, and job title are deliberately excluded. What matters is how a
person researches a company, where their current process breaks down, and what
"done" looks like for them. A retired individual and a graduate student can share
the same persona if they research the same way.

This document is aligned with, and does not duplicate, the approved
[Product Vision](../master-plan/02_Product_Vision.md). Where the Vision names the
primary audience as retail and self-directed investors, this document explains
*how those users work* so we can build for them.

The five personas below are ordered by priority. The two Primary personas define
the MVP; the remaining three are supported where their needs overlap with the
Primary set, and inform—but do not drive—v1 scope.

| ID | Persona | Priority | Defines MVP? |
|----|---------|----------|--------------|
| P-01 | Retail Investor | Primary | Yes |
| P-02 | Student / Learner | Primary | Yes |
| P-03 | Professional Analyst | Secondary | No |
| P-04 | Long-Term Investor | Secondary | No |
| P-05 | Content Creator / Finance Writer | Secondary | No |

---

# P-01 · Retail Investor

## Overview

A self-directed investor who manages their own money and makes buy, hold, and
sell decisions without a professional research desk behind them. They are
capable and curious but time-constrained, and they research companies in the
gaps of a busy schedule. They want to understand a business before committing
capital, not just receive a stock tip.

## Goals

- Understand what a company actually does and how it makes money.
- Assess whether a company is financially healthy before investing.
- Get to a confident decision without reading a full 10-K end to end.
- Compare a few candidate companies before allocating.

## Current Workflow

1. Hears about a company from news, a podcast, or a peer.
2. Opens a brokerage app and a few finance websites in separate tabs.
3. Skims headlines and a handful of metrics, often without context.
4. Attempts to read parts of a filing, then abandons it as too dense.
5. Makes a decision with partial information and lingering uncertainty.

## Pain Points

- Filings are long, dense, and written for professionals.
- Financial data is scattered across many tabs and platforms.
- Hard to separate signal from noise in financial news.
- No structured way to compare two companies side by side.

## AlphaScribe Value

AlphaScribe collapses the multi-tab, multi-hour process into a single workspace.
The user searches a company, reads an AI summary grounded in real filings, asks
follow-up questions in plain language, and compares candidates—reaching an
informed decision in minutes instead of an evening. Every insight is explainable
and traceable back to source, which builds the trust this user needs before
committing capital.

## Key Features Used

| Feature | Why it matters to this persona |
|---------|-------------------------------|
| Company search & overview | Fast entry point to any public company |
| AI financial copilot (chat) | Plain-language answers to "is this a good business?" |
| AI-generated summaries | Replaces reading dense filings end to end |
| Company comparison | Decide between candidates before allocating |
| Key financial metrics | Health check without a spreadsheet |
| Research report export | Keep a record of the decision rationale |

## Success Metrics

| Metric | Target |
|--------|--------|
| Time to a confident research conclusion | < 15 minutes per company |
| Filings read manually per decision | Reduced to near zero |
| Return usage as primary research tool | Weekly active on research days |
| Self-reported confidence in decisions | Increases vs. prior workflow |

## Frustrations

- AI answers that sound authoritative but cite nothing.
- Being shown data without an explanation of what it means.
- Interfaces that assume finance fluency the user doesn't have.

## AI Expectations

- Every claim should be grounded in and traceable to a real filing.
- Plain-language explanations, not jargon.
- Honest "I don't know" over a confident hallucination.
- The AI assists the workflow; it does not give personalized buy/sell advice.

## Priority

**Primary.** This persona defines the MVP and is the platform's core audience.

---

# P-02 · Student / Learner

## Overview

Someone learning equity research and financial analysis—a finance student, a
career switcher, or a self-taught investor building fluency. They value
AlphaScribe as much for what it teaches as for what it answers. They are willing
to read and explore, provided the material meets them at their level.

## Goals

- Learn how to read financial statements and filings.
- Understand *why* a metric matters, not just its value.
- Build a repeatable framework for analyzing any company.
- Practice on real companies with real data.

## Current Workflow

1. Reads a textbook or online course covering a concept in isolation.
2. Tries to apply the concept to a real filing and gets lost in the detail.
3. Searches term by term to decode unfamiliar language.
4. Struggles to connect an isolated metric to the whole business.

## Pain Points

- A large gap between textbook theory and real-world filings.
- No guided way to practice analysis on live companies.
- Financial terminology is a constant barrier to comprehension.
- Hard to know whether their own analysis is correct.

## AlphaScribe Value

AlphaScribe turns any public company into a live, explainable case study. The
learner asks the copilot to explain a metric or a section of a filing in context,
sees how professionals frame an analysis via generated summaries, and repeats the
loop across many companies. Because every insight is explainable, the tool
doubles as a tutor—closing the gap between theory and real filings.

## Key Features Used

| Feature | Why it matters to this persona |
|---------|-------------------------------|
| AI financial copilot (chat) | Ask "what does this mean and why does it matter?" |
| AI-generated summaries | See a worked example of good analysis |
| SEC filing analysis | Practice on real primary sources |
| Key financial metrics | Learn the vocabulary of financial health |
| Company comparison | Understand a metric by contrast across firms |

## Success Metrics

| Metric | Target |
|--------|--------|
| Concepts understood without leaving the tool | Increasing over sessions |
| Companies analyzed independently | Growing breadth over time |
| Repeat learning sessions | Regular return usage |
| Reliance on external glossaries | Decreasing over time |

## Frustrations

- Explanations pitched above the learner's current level.
- Answers that give a number without teaching the concept.
- Being treated as an expert who already knows the terminology.

## AI Expectations

- Explanations that adapt to a learner, not a professional.
- Concepts tied back to the specific company being studied.
- Grounded, correct answers they can trust while learning.
- Encouragement to explore, not just a final answer.

## Priority

**Primary.** This persona defines the MVP alongside the Retail Investor.

---

# P-03 · Professional Analyst

## Overview

An equity research analyst or investment researcher who performs deep analysis as
part of their job. They are fluent in financial statements and already
productive, so AlphaScribe competes with established professional tools. For this
persona, the value is speed and coverage—reducing the manual gathering that
precedes real analysis.

## Goals

- Accelerate the routine gathering and summarization phase of research.
- Cover more companies in less time without losing rigor.
- Quickly surface risks and material changes across filings.
- Produce well-structured research artifacts for others.

## Current Workflow

1. Pulls filings, transcripts, and financial data from multiple sources.
2. Manually reads and extracts the relevant figures and passages.
3. Builds models and comparison tables by hand.
4. Writes up findings into a structured research note.

## Pain Points

- The gathering-and-summarizing phase is slow and repetitive.
- Professional platforms are powerful but expensive and heavy.
- Cross-company comparison requires manual assembly.
- Hard to scale coverage without proportionally more hours.

## AlphaScribe Value

AlphaScribe removes the low-value gathering work that front-loads every analysis.
Grounded summaries, instant metrics, and side-by-side comparison give the analyst
a running start on each company, so their expert time is spent on judgment rather
than collection. Exportable reports fit into an existing deliverable workflow.

## Key Features Used

| Feature | Why it matters to this persona |
|---------|-------------------------------|
| SEC filing analysis | Fast extraction from primary sources |
| AI-generated summaries | A first-pass draft to refine, not write from scratch |
| Company comparison | Assemble peer sets without manual tables |
| Key financial metrics | Immediate health snapshot per company |
| Research report export | Feeds existing deliverable formats |

## Success Metrics

| Metric | Target |
|--------|--------|
| Time from filing to first-pass summary | Materially reduced |
| Companies covered per analyst per week | Increased |
| Manual data-gathering hours | Reduced |
| Fact-check corrections on AI output | Low and trending down |

## Frustrations

- Any inaccuracy that must be caught and corrected downstream.
- Summaries that miss material risks or omit context.
- Tools that add workflow overhead instead of removing it.

## AI Expectations

- High factual precision with citations to source.
- Transparent reasoning that can be audited quickly.
- Output structured enough to drop into professional deliverables.
- Speed without sacrificing accuracy—trust over raw pace.

## Priority

**Secondary.** Supported where needs overlap the Primary personas; informs but
does not drive v1 scope.

---

# P-04 · Long-Term Investor

## Overview

A buy-and-hold investor who commits to companies for years and monitors them over
time. Their research cadence is periodic rather than reactive: an initial deep
evaluation, followed by ongoing checkpoints at earnings and on material news.
Continuity and durability of thesis matter more than speed.

## Goals

- Evaluate the long-term durability of a business before buying.
- Track how a held company evolves over multiple periods.
- Be alerted when something material changes the thesis.
- Revisit prior research and reasoning without rebuilding it.

## Current Workflow

1. Performs a deep initial evaluation of a candidate company.
2. Buys and largely steps back from active monitoring.
3. Re-reads each new earnings report when it arrives.
4. Struggles to recall the original thesis and what has changed since.

## Pain Points

- No persistent record of why they invested in the first place.
- Re-evaluating a company each quarter repeats prior work.
- Easy to miss material changes between infrequent check-ins.
- Historical context is scattered and hard to reconstruct.

## AlphaScribe Value

AlphaScribe gives long-term positions a durable research home. Saved reports and
watchlists preserve the original thesis; period-over-period metrics and summaries
make each earnings check-in a quick "what changed?" rather than a full re-read.
The user maintains conviction over years without redoing the analysis every time.

## Key Features Used

| Feature | Why it matters to this persona |
|---------|-------------------------------|
| Watchlists | Track held and candidate companies over time |
| Saved research reports | Preserve the original thesis and rationale |
| AI-generated summaries | Fast "what changed this quarter" check-ins |
| Historical performance view | See multi-period trends at a glance |
| Key financial metrics | Confirm durability against prior periods |

## Success Metrics

| Metric | Target |
|--------|--------|
| Time to re-evaluate a held company | Sharply reduced per period |
| Material changes caught at earnings | Consistently surfaced |
| Prior research reused vs. rebuilt | High reuse |
| Continuity of thesis over time | Maintained across periods |

## Frustrations

- Losing the original reasoning behind a long-held position.
- Redoing analysis that was already done last quarter.
- Missing a material change because nothing flagged it.

## AI Expectations

- Reliable period-over-period comparison grounded in filings.
- Summaries that emphasize change, not just current state.
- Persistence—research that is there when they return months later.
- No pressure toward short-term trading behavior.

## Priority

**Secondary.** Supported where needs overlap the Primary personas; several needs
(watchlists, saved research) align naturally with the MVP.

---

# P-05 · Content Creator / Finance Writer

## Overview

Someone who researches companies in order to explain them to an audience—a
newsletter writer, educator, or independent finance commentator. Their output is
communication, so they need not only accurate analysis but clearly structured,
citable material they can adapt. Credibility with their audience depends on the
research being correct and traceable.

## Goals

- Research companies quickly enough to publish on a regular cadence.
- Ground every claim in a verifiable source to protect credibility.
- Turn dense financial material into clear, structured narrative.
- Cover a broad set of companies without deep expertise in each.

## Current Workflow

1. Chooses a company or theme to write about.
2. Gathers filings, metrics, and news across many sources.
3. Manually distills the material into an accurate narrative.
4. Fact-checks every figure before publishing.

## Pain Points

- Research volume is high relative to publishing deadlines.
- Fact-checking every claim is slow but non-negotiable.
- Translating financial density into readable prose is laborious.
- Broad topic coverage outpaces personal expertise.

## AlphaScribe Value

AlphaScribe compresses the research-and-verify phase that precedes every piece.
Grounded, citable summaries and metrics give the writer a factual backbone with
sources already attached, so they can focus on narrative and voice. Because every
insight traces back to a filing, fact-checking becomes verification rather than
reconstruction.

## Key Features Used

| Feature | Why it matters to this persona |
|---------|-------------------------------|
| AI-generated summaries | A sourced first draft of the facts |
| SEC filing analysis | Primary-source grounding for claims |
| AI financial copilot (chat) | Clarify and expand specific points |
| Key financial metrics | Accurate figures with provenance |
| Research report export | Reusable structured material for drafting |

## Success Metrics

| Metric | Target |
|--------|--------|
| Research time per published piece | Reduced |
| Factual corrections after publishing | Low and declining |
| Companies covered per period | Increased |
| Claims backed by a traceable source | Approaching all |

## Frustrations

- Any unsourced claim that could undermine credibility if wrong.
- Reformatting AI output into something usable.
- Summaries that flatten the nuance an audience expects.

## AI Expectations

- Citations attached to every factual claim.
- Structured, adaptable output rather than a wall of text.
- High accuracy—published mistakes carry a reputational cost.
- A factual assistant, not a ghostwriter that invents a narrative.

## Priority

**Secondary.** Supported where needs overlap the Primary personas; benefits
directly from the same grounded-summary and citation capabilities.

---

# MVP Feature Coverage Matrix

This matrix maps major platform features to the personas they serve. It confirms
that every MVP feature earns its place by serving at least one persona, and that
the Primary personas (P-01, P-02) are well covered.

| Feature | P-01 | P-02 | P-03 | P-04 | P-05 |
|---------|:----:|:----:|:----:|:----:|:----:|
| Company search & overview | ✓ | ✓ | ✓ | ✓ | ✓ |
| AI financial copilot (chat) | ✓ | ✓ | ✓ |   | ✓ |
| AI-generated summaries | ✓ | ✓ | ✓ | ✓ | ✓ |
| SEC filing analysis |   | ✓ | ✓ |   | ✓ |
| Company comparison | ✓ | ✓ | ✓ |   |   |
| Key financial metrics | ✓ | ✓ | ✓ | ✓ | ✓ |
| Historical performance view |   |   |   | ✓ |   |
| Watchlists |   |   |   | ✓ |   |
| Saved research reports |   |   |   | ✓ |   |
| Research report export | ✓ |   | ✓ |   | ✓ |

---

# Out of Scope for v1

The following user groups are intentionally **not** targeted by the MVP. Their
workflows center on execution speed, real-time market data, proprietary models,
or institutional infrastructure that fall outside AlphaScribe's research-first
mission. This aligns with the Out of Scope section of the
[Product Vision](../master-plan/02_Product_Vision.md), which excludes live
trading, execution, and brokerage integrations from v1.

| User group | Why out of scope for v1 |
|------------|-------------------------|
| Day Traders | Need real-time execution and intraday signals, not deep research |
| High Frequency Traders | Require ultra-low-latency data and automated execution |
| Hedge Funds | Depend on proprietary models, alternative data, and bespoke tooling |
| Quantitative Trading Firms | Build their own signal pipelines; need data feeds, not summaries |
| Investment Banks | Require enterprise workflows, compliance, and deal-specific tooling |
| Institutional Portfolio Managers | Need portfolio-level risk, mandates, and integrations beyond MVP scope |

Excluding these groups is a deliberate focus decision, not a permanent one. It
keeps v1 solving one problem exceptionally well—reducing hours of manual equity
research into minutes—for the personas above.

---

# Future Personas (Post-v1)

These personas are recognized on the roadmap but are **intentionally not
supported yet**. They depend on capabilities beyond the MVP and should not
influence v1 scope. They are recorded here so future prioritization has a
starting point once product-market fit is achieved.

| ID | Persona | Depends On (not in v1) |
|----|---------|------------------------|
| F-01 | Wealth Manager / Advisor | Client-portfolio views, multi-account research, shareable client reports |
| F-02 | Team / Collaborative Researcher | Shared workspaces, comments, and collaboration features |
| F-03 | Global Markets Investor | Non-US exchange coverage and multi-region filing sources |
| F-04 | Passive / Casual Investor | Simplified, notification-driven experience and curated digests |

---

# How Personas Guide Product Decisions

Personas are a decision filter, not a reference document to be read once and
shelved.

- **Every proposed feature must map to at least one persona.** If a feature does
  not clearly serve a defined persona's goals or workflow, that is a signal to
  question it before any implementation begins.
- **Priority follows persona priority.** When trade-offs arise, the two Primary
  personas—Retail Investor and Student / Learner—take precedence, as they define
  the MVP.
- **Unsupported features should be challenged, not built by default.** A feature
  that serves only an out-of-scope group, or no persona at all, should be
  deferred until the need is demonstrated.
- **Personas evolve with evidence.** As real usage data arrives, these personas
  should be revised to match observed behavior—keeping decisions grounded in how
  users actually research, not how we assumed they would.
