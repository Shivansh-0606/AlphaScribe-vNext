# AlphaScribe vNext — Information Architecture

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.0 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | CTO |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For information organization |

**Downstream Dependencies:** PRDs · UX Specifications · Navigation Structure ·
Wireframes · Design Specifications · Content Model · QA Test Plans

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial Information Architecture derived from the frozen Product Discovery baseline. Awaiting review and approval. |
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft (review refinements) | First-review minor changes: made Saved Exports explicit in the Research Library hierarchy, reinforced Comparison's dependency on Company Research, and adopted the canonical **Resume Session** term. No scope, structure, or new domains changed. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Product Strategy](../master-plan/01_Product_Strategy.md), [Product Vision](../master-plan/02_Product_Vision.md), [User Personas](01_User_Personas.md), [User Journeys](02_User_Journeys.md) |
| **Used By** | Navigation Structure, UX Specifications, Wireframes, Design Specifications, and PRDs (as the content-organization reference). |
| **Related Documents** | [Feature Roadmap](../master-plan/03_Feature_Roadmap.md), [Requirements Traceability Matrix](../governance/Requirements_Traceability_Matrix.md), [Documentation Governance](../governance/Documentation_Governance.md) |

> This document organizes **information**. It deliberately does not define
> navigation, layout, components, or implementation. Those are downstream artifacts
> that consume this one.

---

# Introduction

Information Architecture (IA) defines how information is organized, grouped, and
related inside AlphaScribe vNext. It is the structural bridge between *why* the
product exists and *how* any future interface will present it.

The frozen [Product Vision](../master-plan/02_Product_Vision.md) establishes an
AI-native research workspace, and the [User Journeys](02_User_Journeys.md) describe
the paths users take through it. This document translates those approved decisions
into a **logical product structure**: the domains of information, how they nest,
how they relate, and where AI participates. It answers "what information exists and
how is it arranged?" — never "what does the screen look like?"

IA is authoritative for content organization and subordinate to the frozen product
baseline. Where this document and an approved product document appear to differ,
the product document governs.

---

# Design Principles

The architecture is governed by the following principles, derived from the approved
Vision, Strategy, and Journeys.

| Principle | Meaning for the architecture |
|-----------|------------------------------|
| **Information before interface** | Structure is defined by what information means and how it relates, independent of any presentation. |
| **AI integrated into research** | AI is organized *within* the research information it supports, not isolated as a separate destination. |
| **Minimize cognitive load** | Related information is co-located; unrelated information is separated, so the user holds less in mind at once. |
| **Progressive disclosure** | Information is layered from summary to detail; depth is available on demand, never forced up front. |
| **Source transparency** | Every insight is organized alongside a path back to its underlying evidence. |
| **Consistency** | The same kind of information is structured the same way wherever it appears. |
| **Scalability** | The structure accommodates more companies, sessions, and research over time without reorganization. |
| **Accessibility** | Information is organized in a clear, logical order that can be understood and traversed by any user, independent of ability. |

---

# Information Architecture Goals

The IA exists to achieve concrete structural objectives.

- **Reduce navigation complexity** — a small number of clear information domains
  rather than a sprawling tree.
- **Group related information logically** — everything about a company sits within
  one coherent domain.
- **Support research workflows** — the structure mirrors how the primary personas
  actually research (J-02 through J-06), minimizing structural friction.
- **Reduce context switching** — a research task can be completed within a domain
  without scattering across unrelated areas.
- **Preserve continuity** — durable research is organized so prior work is
  retrievable and resumable (J-06).
- **Keep evidence adjacent to insight** — grounded, explainable AI is only possible
  if sources are structurally attached to conclusions.

---

# Application Hierarchy

The application is organized into a small set of top-level information domains
under a single research workspace. This is an **information hierarchy**, not a
navigation menu.

```
Workspace
├── Account & AI Setup
│   ├── Session / Identity
│   └── AI Access (BYOK / Managed AI)
│
├── Workspace Home
│   ├── Entry & Company Search
│   └── Recent Research
│
├── Company Research
│   ├── Company Overview
│   ├── Business Summary
│   ├── Financial Metrics
│   ├── Financial Statements
│   ├── SEC Filings
│   └── AI Insights (Summary · Copilot · Filing Analysis)
│
├── Comparison
│   ├── Selected Companies
│   └── Comparative Metrics & Summaries
│
├── Learning
│   ├── Concept Explanations (in company context)
│   └── Worked Analysis & Self-Check
│
└── Research Library
    ├── Research Sessions (saved reasoning · saved sources)
    ├── Research Reports (grounded, source-backed, exportable)
    ├── Saved Exports (exported research artifacts)
    └── Research History
```

Each top-level domain corresponds to an approved MVP capability set and is detailed
in the next section. Cross-cutting capabilities — **Trusted AI** (source
transparency) and the **AI Copilot** — are not separate domains; they are woven
through the domains where research happens (see *AI Integration Points*).

---

# Primary Information Domains

Each domain is described by its purpose, the information it holds, how it relates to
other domains, and the journeys and personas it serves. No new capabilities are
introduced; every domain maps to the frozen Roadmap and Journeys.

## Domain 1 — Account & AI Setup

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Establish an authenticated research session and a working AI access model with minimal friction. |
| **Primary Content** | Session/identity information; AI access choice (Bring-Your-Own-Key or Managed AI) and its validated status. |
| **Relationship to other domains** | A precondition for all other domains; every research action assumes an established session and AI access. |
| **Primary Journeys Supported** | J-01 |
| **Primary Personas Supported** | P-01, P-02 |

## Domain 2 — Workspace Home

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Provide the entry point into research and a path back to recent work. |
| **Primary Content** | Company search entry; recent research activity. |
| **Relationship to other domains** | Routes into Company Research and back into the Research Library; the starting node for most sessions. |
| **Primary Journeys Supported** | J-01, J-02 |
| **Primary Personas Supported** | P-01, P-02 |

## Domain 3 — Company Research

| Attribute | Detail |
|-----------|--------|
| **Purpose** | The core research domain: everything needed to understand a single company in one coherent place. |
| **Primary Content** | Company overview; business summary; financial metrics; financial statements; SEC filings; AI insights grounded in those sources. |
| **Relationship to other domains** | Feeds Comparison (as a selected company), Learning (as a live example), and the Research Library (as saved output); consumes AI throughout. |
| **Primary Journeys Supported** | J-02, J-05 |
| **Primary Personas Supported** | P-01, P-02 |

## Domain 4 — Comparison

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Evaluate a small set of companies side by side on comparable terms. It is a **derived** domain: it exists to relate companies that already come from research, not to originate new company information. |
| **Primary Content** | The selected company set; comparative metrics and summaries; AI explanation of differences. All of this is drawn from the underlying companies rather than held independently. |
| **Relationship to other domains** | Consumes companies selected from Company Research and therefore cannot exist independently of it — a comparison always references companies that already exist as research subjects. A comparison can be preserved into the Research Library. |
| **Primary Journeys Supported** | J-03 |
| **Primary Personas Supported** | P-01 |

## Domain 5 — Learning

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Turn real companies and filings into explainable, learner-level material. |
| **Primary Content** | Concept explanations set in a company's context; worked analytical framing; interpretation self-check. |
| **Relationship to other domains** | Overlays Company Research and SEC Filings with learner-oriented explanation; reuses the same underlying information rather than duplicating it. |
| **Primary Journeys Supported** | J-04, J-05 |
| **Primary Personas Supported** | P-02 |

## Domain 6 — Research Library

| Attribute | Detail |
|-----------|--------|
| **Purpose** | Preserve the outcome of research so it is durable, retrievable, and resumable. |
| **Primary Content** | Research sessions (with saved reasoning and saved sources); research reports (grounded, source-backed, exportable); saved exports (the exportable research artifacts, retained as a durable record); research history. |
| **Relationship to other domains** | Receives output from Company Research and Comparison; returns the user to prior work to resume it (the **Resume Session** action in navigation) or update it. |
| **Primary Journeys Supported** | J-06 |
| **Primary Personas Supported** | P-01, P-02 |

---

# Content Hierarchy

Within the Company Research domain, information flows from the most summarized level
to the most detailed and evidentiary, reflecting the *progressive disclosure* and
*overview-before-detail* principles.

```
Company
↓
Overview
↓
Business Summary
↓
Financial Metrics
↓
Financial Statements
↓
SEC Filings
↓
AI Insights (grounded in the above)
↓
Preserved / Exported Research
```

The ordering is intentional: a user meets the company as a whole before any number,
understands the business before the figures, sees figures before raw statements, and
reaches primary filings and AI insight last — with every insight resolvable back down
the hierarchy to its source. Preserved and exported research sit at the end of the
flow, capturing the conclusion together with its reasoning and evidence.

---

# Information Relationships

The following are **conceptual** relationships between information entities. This is
not a data model and defines no schema — only how entities relate in meaning.

| Entity | Relates to | Nature of relationship |
|--------|-----------|------------------------|
| **Company** | Research Session, Comparison, Report, AI Conversation | A company is the subject that research, comparison, reporting, and conversation are *about*. |
| **Research Session** | Company, AI Conversation, Report, Saved Research | A session is a unit of research on one or more companies; it accumulates reasoning and sources and can produce a report. |
| **AI Conversation** | Company, Research Session, Sources | A conversation is contextual to a company and its session, and its statements are anchored to sources. |
| **Comparison** | Company (multiple), Research Session | A comparison relates two or more companies within a research context. |
| **Report** | Research Session, Company, Sources | A report is a preserved, source-backed artifact derived from a session. |
| **Saved Research** | Research Session, Report | Saved research is the durable form of a session and its outputs, enabling resume. |
| **Watchlist** | Company | A conceptual grouping of companies a user chooses to track *(post-MVP; see Scope Boundaries)*. |

Two overarching relationship rules hold everywhere:

- **Insight is always related to its source.** No AI-produced entity exists without a
  relationship back to the evidence it derives from.
- **Research relates to a subject.** Sessions, reports, conversations, and comparisons
  are always anchored to one or more companies.

---

# AI Integration Points

AI is organized *inside* the research information it supports, consistent with the
Vision's principle that AI enhances every workflow rather than being a separate
destination. Each integration point below describes *where AI appears in the
information hierarchy*, not how it is implemented.

| AI Integration Point | Where it lives in the IA | Journeys |
|----------------------|--------------------------|----------|
| **AI Summary** | Within Company Research, as a grounded summarization of the company's information. | J-02 |
| **AI Copilot** | Cross-cutting within Company Research (and Learning), as contextual question-and-answer anchored to the company and its sources. | J-02, J-04, J-05 |
| **Filing Analysis** | Within the SEC Filings level of Company Research, as grounded interpretation of primary sources. | J-05 |
| **Company Comparison (AI)** | Within the Comparison domain, as explanation of what differences mean. | J-03 |
| **Learning Assistance** | Within the Learning domain, as learner-level explanation set in a company's context. | J-04, J-05 |

Across all points, **Trusted AI** is the cross-cutting organizing constraint: every
AI insight is structured with source traceability and an explainable path back to
evidence. AI is never organized as an authority that stands apart from the
information; it is organized as an assistant embedded in it.

---

# Search & Discovery Architecture

Users reach information through discovery mechanisms organized around the company as
the primary unit of research.

| Mechanism | Role in the architecture |
|-----------|--------------------------|
| **Global Search** | The primary entry into the information space; resolves a user's intent to a company or a piece of prior research. |
| **Company Search** | The focused path to a specific public company, the most common discovery action. |
| **Filtering** | Narrowing within a set — for example, refining a comparison set or a list of prior research — to reduce what the user must consider. |
| **Browsing** | Moving through an already-scoped set of information (e.g. the levels of a company's content hierarchy) without a targeted query. |
| **Research History** | Rediscovery of the user's own prior work, making past research a first-class discovery surface (J-06). |

Discovery favors *recall over reconstruction*: search and history let users return to
intent and prior work directly, rather than rebuilding them.

---

# Content Organization Principles

These rules govern how content is arranged wherever it appears. They operationalize
the Design Principles at the level of individual information.

| Rule | Rationale |
|------|-----------|
| **Overview before detail** | Users orient to the whole before the parts. |
| **Summary before raw data** | A plain-language summary precedes the figures it describes. |
| **Explain before quantify** | The meaning of a metric accompanies its value, never a number alone. |
| **Always show sources** | Every insight is organized with a path to its evidence; nothing authoritative is source-less. |
| **Avoid duplicated information** | Each piece of information has one home and is referenced elsewhere, never copied (single source of truth). |
| **Related information stays together** | Everything about one company lives within one domain. |

---

# MVP Scope Boundaries

The IA is scoped to the frozen MVP. It organizes only information that the approved
Roadmap places in the first release, for the two Primary personas (P-01, P-02).

## In Scope (MVP)

- Account & AI Setup (session; BYOK and Managed AI access).
- Workspace Home (entry, company search, recent research).
- Company Research (overview, business summary, financial metrics, financial
  statements, SEC filings, AI insights).
- Comparison of companies.
- Learning (concept explanation in context, worked framing, self-check).
- Research Library (research sessions with saved reasoning and sources, research
  reports, research history, export).
- Trusted AI and the AI Copilot as cross-cutting integration within the above.

## Intentionally Excluded (Not MVP)

Consistent with the approved Vision and Roadmap, the IA does **not** organize
information for:

- **Watchlists and alerting** — deferred to a later release; referenced conceptually
  only, not structured for MVP.
- **AI Conversation Lifecycle** (continuity, retention, conversation history as a
  managed structure) — deferred to future documentation, not organized here.
- **Secondary-persona workflows** (P-03 Professional Analyst, P-04 Long-Term
  Investor, P-05 Content Creator) — recognized but not the MVP focus.
- **Live trading, execution, brokerage, portfolio, options, crypto, and social
  investing** — out of scope by Vision.

No future features are invented in this document; excluded items are named only to
mark the boundary.

---

# Architecture Validation Checklist

| Check | Status | Basis |
|-------|--------|-------|
| Consistent with Product Vision | ✅ | AI-native research workspace; trust-first, grounded, explainable organization. |
| Supports User Journeys | ✅ | Every domain maps to J-01–J-06. |
| Supports Personas | ✅ | Every domain serves P-01 and/or P-02. |
| AI integrated throughout | ✅ | AI organized within domains, not as a separate destination. |
| Minimal cognitive load | ✅ | Few domains; related information co-located; progressive disclosure. |
| Source transparency preserved | ✅ | Insight always related to its evidence. |
| Accessibility considered | ✅ | Logical, ordered, presentation-independent structure. |
| Implementation agnostic | ✅ | No layout, components, navigation, or technical detail. |
| No new scope introduced | ✅ | Organizes only frozen-baseline information. |

---

# Document Maintenance

This Information Architecture is subordinate to the frozen Product Discovery baseline.
It should be revised when the approved information set changes (via the governance
Change Request process), and it should be reviewed and approved before downstream
navigation, UX, and wireframe work treats it as authoritative. Routine downstream
detailing must align to this structure but must not silently alter it.
