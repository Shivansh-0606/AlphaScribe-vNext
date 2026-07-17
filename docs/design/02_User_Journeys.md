# AlphaScribe vNext — User Journeys

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
| **Depends On** | [Product Vision](../master-plan/02_Product_Vision.md), [User Personas](01_User_Personas.md) |
| **Used By** | UX & design specs, prototype flows, usability testing scripts, roadmap prioritization. |
| **Related Documents** | [Product Strategy](../master-plan/01_Product_Strategy.md), [Feature Roadmap](../master-plan/03_Feature_Roadmap.md) |

---

# Introduction

This document models the end-to-end workflows of AlphaScribe's **Primary
personas**—P-01 Retail Investor and P-02 Student / Learner—as defined in the
[User Personas](01_User_Personas.md) document. A journey describes how a persona
moves from an initial trigger to a satisfying outcome, including the paths that
diverge and the points where the experience can break down.

The document is deliberately **implementation-agnostic**. It describes *what the
user is trying to do and experience*, not screens, components, endpoints, or
architecture. Those belong to the design and technical specs that consume this
document. The goal here is a shared understanding of user intent that any future
UI can be measured against.

Journeys are scoped to the MVP capabilities named in the
[Product Vision](../master-plan/02_Product_Vision.md): search and explore
companies, chat with an AI copilot, analyze filings, read grounded summaries,
compare companies, view key metrics, and export research.

## Journey-to-Persona Matrix

This matrix provides quick visual traceability, mapping each journey to the
personas it primarily supports.

| Journey | P-01 | P-02 | P-03 | P-04 | P-05 |
|---------|:----:|:----:|:----:|:----:|:----:|
| J-01 Getting Set Up for Research | ✓ | ✓ |   |   |   |
| J-02 Researching a Company for the First Time | ✓ |   |   |   |   |
| J-03 Comparing Candidate Companies | ✓ |   |   |   |   |
| J-04 Learning a Financial Concept in Context |   | ✓ |   |   |   |
| J-05 Analyzing a Real Filing as Practice |   | ✓ |   |   |   |
| J-06 Capturing and Returning to Research | ✓ | ✓ |   |   |   |

## Journey Index

| Journey ID | Journey | Persona ID(s) |
|------------|---------|---------------|
| J-01 | Getting Set Up for Research | P-01, P-02 |
| J-02 | Researching a Company for the First Time | P-01 |
| J-03 | Comparing Candidate Companies | P-01 |
| J-04 | Learning a Financial Concept in Context | P-02 |
| J-05 | Analyzing a Real Filing as Practice | P-02 |
| J-06 | Capturing and Returning to Research | P-01, P-02 |

---

# Design Principles Derived from User Journeys

The journeys below share a set of recurring expectations. These principles are
extracted from those journeys and should guide any design that implements them.

- **Every journey should minimize cognitive load.** The user's attention belongs
  on the company, not on operating the tool.
- **Research should begin within seconds.** The path from intent to first insight
  must be short.
- **AI responses must always be explainable.** No answer is acceptable that the
  user cannot understand.
- **Every conclusion must be traceable to its source.** Trust depends on the
  user's ability to inspect where a claim comes from.
- **Recovery from failure should always be possible.** Every failure state is a
  guided, recoverable step—never a dead end.
- **Users should never lose completed research.** Work the user has done is
  durable by default.
- **Returning users should resume instead of restarting.** Re-entry reuses prior
  work rather than rebuilding it.

---

# J-01 · Getting Set Up for Research

| Field | Detail |
|-------|--------|
| **Journey ID** | J-01 |
| **Persona ID(s)** | P-01, P-02 |
| **Priority** | Primary MVP |
| **Frequency** | Medium — setup occurs roughly once per user, with occasional re-authentication, rather than on every research session. |

## Goal

Get from arrival to a working research session with the least possible friction,
choosing an AI usage model without being blocked by configuration.

## Journey Overview

```
Arrival
↓
Understand Value
↓
Sign In
↓
Choose AI Model (BYOK or Managed)
↓
Confirm It Works
↓
Enter Workspace
```

## Trigger

The user decides to try AlphaScribe for a specific research need.

## Preconditions

- The user has access to the platform.
- The user has, or can obtain, either their own AI provider key (BYOK) or a
  managed subscription.

## Main Flow

1. The user arrives and understands, within moments, what AlphaScribe is for.
2. The user creates a session / signs in behind the login wall.
3. The user is offered two clear paths: bring their own API key, or use managed
   AI with zero setup.
4. The user picks a path and confirms it works.
5. The user lands in the workspace, ready to search for a company.

## Alternate Flows

- **Managed AI chosen:** the user skips key configuration entirely and reaches
  the workspace immediately.
- **BYOK chosen:** the user supplies a key and receives quick confirmation that
  it is valid before proceeding.
- **Returning user:** the user signs back in and resumes without repeating setup.

## Failure States

- The chosen AI path fails (invalid key, managed service unavailable) and the
  user is stuck without a clear recovery step.
- Setup requires finance or technical fluency the user does not have.
- The value of the product is unclear before the user is asked to commit.

## Success Criteria

- The user reaches a usable workspace on the first attempt.
- Setup completes in minutes, not a lengthy configuration exercise.
- The user understands which AI model they are using and why.

## UX Opportunities

- Communicate value before asking for commitment, so setup feels justified.
- Make Managed AI the frictionless default while keeping BYOK a first-class
  option.
- Turn any setup failure into a guided, recoverable step rather than a dead end.

## User Emotional Journey

- **Before:** Interested but cautious about commitment and setup effort.
- **During:** Reassured as the path stays simple and choices are clear.
- **Failure:** Discouraged when blocked by a configuration error with no way out.
- **Success:** Ready and unblocked, confident the tool is set up correctly.

## Future Feature Mapping

Supports Future Features:

- F-002 AI Copilot

*These are placeholder Feature IDs for future PRDs; they are referenced here for
traceability only and define no implementation.*

---

# J-02 · Researching a Company for the First Time

| Field | Detail |
|-------|--------|
| **Journey ID** | J-02 |
| **Persona ID(s)** | P-01 |
| **Priority** | Primary MVP |
| **Frequency** | Very High — this is the platform's core loop, performed every time a user evaluates a company; most sessions include it. |

## Goal

Move from hearing about a company to a confident, informed view of the business
in minutes, without reading a full filing.

## Journey Overview

```
Arrival
↓
Search Company
↓
Company Overview
↓
AI Summary
↓
Key Metrics
↓
Ask Questions
↓
Inspect Sources
↓
Reach Conclusion
```

## Trigger

The user encounters a company (news, a peer, a podcast) and wants to understand
it before considering an investment.

## Preconditions

- The user has an active research session (see J-01).
- The company is publicly traded and covered by the platform.

## Main Flow

1. The user searches for the company and opens its overview.
2. The user reads a grounded AI summary of what the business does and how it
   makes money.
3. The user reviews key financial-health metrics at a glance.
4. The user asks the copilot follow-up questions in plain language.
5. Each answer is explainable and traceable to a source the user can inspect.
6. The user reaches a confident conclusion about whether to investigate further.

## Alternate Flows

- **Deeper dig:** the user drills into specific filing sections via the copilot.
- **Not a fit:** the user concludes early that the company is not of interest and
  exits without further work.
- **Hand-off to comparison:** the user decides to weigh this company against
  peers, continuing into J-03.

## Failure States

- The company is not covered, and the user is left without an alternative.
- A summary or answer sounds authoritative but cites nothing, eroding trust.
- Data is shown without explanation, leaving the user unable to interpret it.
- The user cannot trace a claim back to its source.

## Success Criteria

- The user reaches a confident conclusion in under ~15 minutes.
- No manual reading of a full filing is required.
- Every insight the user relied on was explainable and sourced.

## UX Opportunities

- Lead with a plain-language business summary before any numbers.
- Make source-tracing effortless, so trust is the default, not an extra step.
- Meet finance-fluency gaps with explanation-on-demand, never assumed knowledge.

## User Emotional Journey

- **Before:** Curious but uncertain, unsure whether the company is worth the time.
- **During:** Focused and exploring, following the business story with growing
  understanding.
- **Failure:** Frustrated and distrustful when an answer is unsourced or a
  company is uncovered.
- **Success:** Confident and informed, with a grounded view reached quickly.

## Future Feature Mapping

Supports Future Features:

- F-001 Company Search
- F-002 AI Copilot
- F-003 Company Overview
- F-004 Financial Metrics
- F-006 Filing Analysis

*These are placeholder Feature IDs for future PRDs; they are referenced here for
traceability only and define no implementation.*

---

# J-03 · Comparing Candidate Companies

| Field | Detail |
|-------|--------|
| **Journey ID** | J-03 |
| **Persona ID(s)** | P-01 |
| **Priority** | Primary MVP |
| **Frequency** | High — comparison recurs whenever a user weighs candidates before allocating, though slightly less often than single-company research. |

## Goal

Decide between a small set of candidate companies before allocating capital.

## Journey Overview

```
Active Session
↓
Select Companies
↓
Side-by-Side View
↓
Compare Metrics & Summaries
↓
Ask About Differences
↓
Rank Candidates
↓
Reach Decision
```

## Trigger

The user has two or more companies in mind and needs to choose.

## Preconditions

- The user has an active research session.
- The candidate companies are covered by the platform.

## Main Flow

1. The user selects the companies to compare.
2. The user views them side by side across key metrics and business summaries.
3. The user asks the copilot to explain differences that matter to a decision.
4. The user forms a ranked view grounded in comparable, sourced data.

## Alternate Flows

- **Refine the set:** the user adds or removes a candidate mid-comparison.
- **Single winner emerges early:** the user shortcuts to a decision and moves on.
- **Inconclusive:** the user saves the comparison to revisit later (see J-06).

## Failure States

- One or more candidates lack comparable data, making the comparison misleading.
- Differences are shown without context, so the user cannot judge their
  significance.
- The comparison is hard to assemble, defeating its time-saving purpose.

## Success Criteria

- The user assembles a meaningful comparison without manual data gathering.
- The user can articulate why one company ranks above another, with sources.
- The decision is reached faster than the user's prior multi-tab process.

## UX Opportunities

- Make like-for-like comparison the default, flagging where data is not
  comparable rather than hiding the gap.
- Let the copilot narrate the *meaning* of differences, not just the numbers.
- Preserve the comparison so an inconclusive session can resume, not restart.

## User Emotional Journey

- **Before:** Torn between options and wary of choosing wrongly.
- **During:** Analytical and engaged, weighing candidates on comparable terms.
- **Failure:** Uneasy when data is not comparable or differences lack context.
- **Success:** Decisive and assured, able to justify the ranking with sources.

## Future Feature Mapping

Supports Future Features:

- F-001 Company Search
- F-002 AI Copilot
- F-004 Financial Metrics
- F-005 Company Comparison

*These are placeholder Feature IDs for future PRDs; they are referenced here for
traceability only and define no implementation.*

---

# J-04 · Learning a Financial Concept in Context

| Field | Detail |
|-------|--------|
| **Journey ID** | J-04 |
| **Persona ID(s)** | P-02 |
| **Priority** | Primary MVP |
| **Frequency** | High — learners invoke this loop repeatedly within a session, encountering unfamiliar concepts often as they build fluency. |

## Goal

Understand *why* a financial metric or concept matters by applying it to a real
company, closing the gap between theory and practice.

## Journey Overview

```
Active Session
↓
Pick Example Company
↓
Ask to Explain Concept
↓
Learner-Level Explanation
↓
Follow-Up Questions
↓
Concept Clear
↓
Repeat Across Companies
```

## Trigger

The user encounters a concept—in a course, a filing, or a summary—that they do
not yet fully understand.

## Preconditions

- The user has an active research session.
- A real company is available as a live example.

## Main Flow

1. The user picks a real company as a working example.
2. The user asks the copilot to explain the concept in the context of that
   company.
3. The explanation is pitched to a learner, tied to the company's actual figures.
4. The user asks follow-up questions until the concept is clear.
5. The user repeats the concept across other companies to reinforce it.

## Alternate Flows

- **Contrast to learn:** the user compares two companies to understand a metric
  by difference (bridges into J-03's mechanics for a learning purpose).
- **Guided exploration:** the user follows the copilot's prompts to explore
  related concepts.

## Failure States

- Explanations are pitched above the learner's level, deepening confusion.
- An answer gives a number without teaching the underlying concept.
- The user is treated as an expert who already knows the terminology.

## Success Criteria

- The user understands the concept without leaving the tool for external
  glossaries.
- The user can apply the concept to a new company independently.
- The user returns to learn further concepts over multiple sessions.

## UX Opportunities

- Let explanations adapt to a learner's level rather than a single fixed depth.
- Always tie a concept back to the specific company being studied.
- Encourage exploration—invite the next question rather than closing the topic.

## User Emotional Journey

- **Before:** Confused by a concept that theory alone hasn't made clear.
- **During:** Curious and absorbed, connecting the idea to a real company.
- **Failure:** Discouraged when an explanation talks over their head.
- **Success:** Enlightened and capable, able to apply the concept independently.

## Future Feature Mapping

Supports Future Features:

- F-002 AI Copilot
- F-004 Financial Metrics
- F-010 Learning Mode

*These are placeholder Feature IDs for future PRDs; they are referenced here for
traceability only and define no implementation.*

---

# J-05 · Analyzing a Real Filing as Practice

| Field | Detail |
|-------|--------|
| **Journey ID** | J-05 |
| **Persona ID(s)** | P-02 |
| **Priority** | Primary MVP |
| **Frequency** | Medium — deep filing practice is deliberate and time-intensive, undertaken periodically rather than in every session. |

## Goal

Practice reading and interpreting a real filing, using the tool as a tutor that
models how a professional analysis is framed.

## Journey Overview

```
Active Session
↓
Open Filing Analysis
↓
Read Grounded Summary
↓
Ask About Sections & Terms
↓
Form Own Reading
↓
Check Against Sources
↓
Build Repeatable Framework
```

## Trigger

The user wants hands-on practice on primary sources, not just textbook theory.

## Preconditions

- The user has an active research session.
- The chosen company's filing is covered by the platform.

## Main Flow

1. The user opens a real company's filing analysis.
2. The user reads a grounded summary that models good analytical framing.
3. The user asks the copilot to explain unfamiliar sections and terminology in
   context.
4. The user forms their own reading, checking it against explainable, sourced
   answers.
5. The user repeats across companies to build a repeatable framework.

## Alternate Flows

- **Section-by-section:** the user works through the filing in parts rather than
  as a whole.
- **Self-check:** the user proposes an interpretation and asks the copilot to
  confirm or correct it against the source.

## Failure States

- The filing is too dense and the tool offers no accessible entry point.
- Terminology remains a barrier because explanations assume expertise.
- The user cannot tell whether their own interpretation is correct.

## Success Criteria

- The user analyzes a real filing without abandoning it as too dense.
- The user's reliance on external references decreases over sessions.
- The user builds a framework they reuse on new companies.

## UX Opportunities

- Provide an accessible entry point into an otherwise intimidating filing.
- Show worked framing as a teaching example, not just an answer.
- Support self-checking, so the learner can validate their own reasoning.

## User Emotional Journey

- **Before:** Intimidated by a dense, unfamiliar primary source.
- **During:** Determined and studious, working through the filing with guidance.
- **Failure:** Overwhelmed when terminology blocks progress with no way in.
- **Success:** Empowered and fluent, with a framework they can reuse.

## Future Feature Mapping

Supports Future Features:

- F-002 AI Copilot
- F-003 Company Overview
- F-006 Filing Analysis
- F-010 Learning Mode

*These are placeholder Feature IDs for future PRDs; they are referenced here for
traceability only and define no implementation.*

---

# J-06 · Capturing and Returning to Research

| Field | Detail |
|-------|--------|
| **Journey ID** | J-06 |
| **Persona ID(s)** | P-01, P-02 |
| **Priority** | Secondary MVP |
| **Frequency** | High — saving and returning wraps most productive sessions and recurs whenever a user revisits or updates prior work. |

## Goal

Preserve the outcome of a research session—decision, rationale, or learning—and
return to it later without rebuilding the work.

## Journey Overview

```
Completed Session
↓
Save or Export Research
↓
Reasoning & Sources Preserved
↓
Return Later
↓
Reopen Saved Research
↓
Resume or Update
```

## Trigger

The user completes a piece of research they will want again: a decision record,
a comparison, or study material.

## Preconditions

- The user has completed a research or learning session.

## Main Flow

1. The user saves or exports the research they have produced.
2. The record preserves the reasoning and its sources, not just a conclusion.
3. Later, the user returns and reopens the saved research.
4. The user resumes from where they left off, or updates it with new information.

## Alternate Flows

- **Export out:** the user takes a research report into their own workflow.
- **Ongoing tracking:** the user keeps a company on a watchlist to revisit at the
  next earnings update (aligns with the Long-Term Investor's needs, P-04).
- **Refresh:** the user re-opens saved research to check what has changed since.

## Failure States

- Saved research loses the reasoning or sources, leaving only a bare conclusion.
- The user cannot find or reopen prior work when they return.
- Returning requires redoing analysis that was already completed.

## Success Criteria

- The user reliably retrieves prior research on return.
- Reasoning and sources survive the save, not just the final answer.
- Re-entry reuses prior work rather than restarting it.

## UX Opportunities

- Treat research as durable by default, so nothing valuable is lost on exit.
- Preserve the *why*, not only the *what*, in any saved or exported record.
- Make returning feel like resuming, emphasizing what changed since last time.

## User Emotional Journey

- **Before:** Invested in work they don't want to lose or repeat.
- **During:** Reassured as research is captured with its reasoning intact.
- **Failure:** Frustrated when prior work is lost or must be rebuilt.
- **Success:** Secure and in control, resuming exactly where they left off.

## Future Feature Mapping

Supports Future Features:

- F-007 Saved Research
- F-008 Export Reports
- F-009 Watchlists

*These are placeholder Feature IDs for future PRDs; they are referenced here for
traceability only and define no implementation.*

---

# How Journeys Guide Design

Journeys are the behavioral bridge between personas and any future interface.

- **Every design should serve a journey.** A screen or flow that advances no
  journey should be questioned before it is built.
- **Failure states are requirements, not edge cases.** Each named failure state
  is a moment where trust—the platform's core currency—can be lost, and must be
  designed for.
- **Success criteria are testable.** Usability testing and success metrics should
  measure whether a journey's success criteria are actually met.
- **Journeys evolve with evidence.** As real usage reveals how users move through
  the product, these journeys should be revised to match observed behavior.
