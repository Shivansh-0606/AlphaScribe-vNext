# AlphaScribe vNext — Navigation Structure

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.0 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | _Pending_ |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For navigation behavior (pending approval) |

**Downstream Dependencies:** PRDs · UX Specifications · Wireframes · Interaction
Specifications · Design Specifications · QA Test Plans

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial Navigation Structure derived from the frozen Information Architecture and Product Discovery baseline. Awaiting review and approval. |
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft (review refinements) | First-review minor changes: standardized the canonical **Resume Session** term for reopening previously saved work (kept "Continue Research" for active in-progress work). No new destinations, scope, or structure changed. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Information Architecture](03_Information_Architecture.md), [User Journeys](02_User_Journeys.md), [User Personas](01_User_Personas.md), [Product Vision](../master-plan/02_Product_Vision.md) |
| **Used By** | UX Specifications, Wireframes, Interaction Specifications, and PRDs (as the navigation-behavior reference). |
| **Related Documents** | [Product Strategy](../master-plan/01_Product_Strategy.md), [Feature Roadmap](../master-plan/03_Feature_Roadmap.md), [Documentation Governance](../governance/Documentation_Governance.md) |

> This document defines **how users move** through the product. It does not define
> what information exists (that is the Information Architecture) nor what anything
> looks like (that is UX/visual design).

---

# Introduction

Navigation Structure defines how users move between and within the information
domains of AlphaScribe vNext. Where the
[Information Architecture](03_Information_Architecture.md) (IA) defines *what
information exists and how it is organized*, this document defines *how a user
travels through that organization* to complete the approved
[User Journeys](02_User_Journeys.md).

The relationship is strict and one-directional: navigation is subordinate to the
IA. Every navigable destination corresponds to an information domain or level
already defined in the IA; navigation introduces no new places, only movement
between existing ones. Where this document and the IA appear to differ, the IA
governs.

This document is behavior-level and implementation-agnostic. It describes movement,
context, and expected behavior — not layouts, components, or technology.

---

# Navigation Principles

Navigation is governed by the following principles, derived from the approved
Vision, Strategy, Personas, and IA.

| Principle | Meaning for navigation |
|-----------|------------------------|
| **Simple** | A small, learnable set of movements; no hidden or exotic paths. |
| **Predictable** | The same action always leads to the same place; users can anticipate where they will land. |
| **Consistent** | Movement works the same way across every domain. |
| **Minimal clicks** | The path from intent to information is as short as the task allows (research-time is the product's core value). |
| **Research-first** | Navigation is organized around the research task, keeping the user in flow rather than in menus. |
| **AI-first** | AI is reachable in context wherever research happens, never a place the user must leave to reach. |
| **Accessible** | Every path is operable by any user, independent of input method or ability. |
| **Keyboard friendly** | All navigation is fully operable without a pointing device. |
| **Responsive** | Navigation adapts its presentation across contexts without changing its structure or destinations. |
| **Context-preserving** | Moving does not discard the user's research state. |

---

# Global Navigation

Global (persistent) navigation provides constant access to the top-level
information domains defined in the IA. It is available throughout the workspace and
its destinations do not change with context.

| Global destination | IA domain it enters | Journeys |
|---------------------|---------------------|----------|
| **Workspace Home** | Workspace Home (entry, company search, recent research) | J-01, J-02 |
| **Research** | Company Research | J-02, J-05 |
| **Compare** | Comparison | J-03 |
| **Learning** | Learning | J-04, J-05 |
| **Research Library** | Research Library (sessions, reports, history) | J-06 |
| **Settings** | Account & AI Setup | J-01 |

> **Terminology note:** Global destinations use the IA's domain names. The product
> uses **Workspace Home** rather than a generic "Dashboard," and **Research
> Library** as the home of saved research and reports, consistent with the frozen
> IA. No destination exists here that the IA does not define.

Global navigation is persistent and flat: each destination is reachable directly,
without traversing another domain first.

---

# Primary Navigation

Primary navigation is movement **between** the major application areas listed in
Global Navigation. Its defining characteristics:

- **Direct** — any top-level domain is reachable from any other in a single move.
- **Non-destructive** — moving between domains preserves the active research
  context (see *Back Navigation* and *Contextual Navigation*).
- **Journey-shaped** — the common cross-domain paths mirror the approved journeys,
  for example: Workspace Home → Research (J-02), Research → Compare (J-03),
  Research → Research Library to preserve work (J-06), and Research Library → prior
  work via **Resume Session** (J-06).

Primary navigation does not force a linear order. A user may enter research, branch
into comparison or learning, and return, without being routed through intermediate
domains.

---

# Secondary Navigation

Secondary navigation is movement **within** a major domain, across the content
levels the IA defines for it. It does not leave the domain.

Within the **Company Research** domain, secondary navigation moves across the
company's content hierarchy:

```
Company
├── Overview
├── Business Summary
├── Financials (Metrics · Statements)
├── Filings (SEC Filings)
├── AI Insights
└── Export
```

Secondary navigation follows the IA's *overview-before-detail* ordering: a user can
move directly to any level, but the default progression runs from summary toward
detail and evidence. Equivalent within-domain movement exists for other domains
(e.g. within Comparison: selected companies → comparative view; within Research
Library: sessions → reports → history), always across IA-defined levels only.

---

# Contextual Navigation

Contextual navigation changes the available movements based on the user's current
research context. It does not add new destinations; it surfaces the movements that
are relevant *now*.

| Context | What contextual navigation offers | Journeys |
|---------|-----------------------------------|----------|
| **Research session** | Movement to continue an active session, save it, or **Resume Session** for previously saved work, and back to its subject company. | J-02, J-06 |
| **Company context** | Movement across that company's content levels and into comparison or learning *for that company*. | J-02, J-03, J-04, J-05 |
| **Comparison context** | Movement to add or remove a company from the set, and into any member company's research. | J-03 |
| **Learning context** | Movement between a concept and the company example it is explained against. | J-04, J-05 |

Context determines *which* movements are relevant, while global and primary
navigation remain constantly available. Context is carried with the user as they
move, so returning to a prior context restores its relevant options.

---

# Search Navigation

Search is the primary way users reach information, organized around the company as
the primary unit of research (per the IA's Search & Discovery architecture).

| Search element | Navigational role |
|----------------|-------------------|
| **Global Search** | The fastest entry into the information space from anywhere; resolves intent to a company or prior research and moves the user there. |
| **Company Search** | The focused path to a specific public company — the most common discovery action. |
| **Search Results** | An intermediate set from which the user moves to a chosen destination; results lead into domains, never to new places. |
| **Recent Searches** | Quick return to recently expressed intents, reducing repeated typing. |
| **Search History** | Rediscovery of prior search intent over time, complementing Research History as a way back to earlier work (J-06). |

Search favors recall over reconstruction: it lets users return directly to a company
or prior research rather than navigating there manually.

---

# Breadcrumb Strategy

Breadcrumbs express the user's position within a domain's content hierarchy and
provide upward movement along it.

**Breadcrumbs should appear when:**

- The user is within a multi-level domain (most notably Company Research), where
  showing the path from company → level clarifies location and enables a direct move
  back up the hierarchy.
- The user has drilled from a summary level toward detail or evidence and benefits
  from a clear route back to the broader context.

**Breadcrumbs should not appear when:**

- The user is at a top-level domain reached through global navigation (there is no
  meaningful hierarchy above it).
- The context is a single-level surface (e.g. Workspace Home) where a breadcrumb
  would imply depth that does not exist.
- A conversational or contextual flow would be better served by back navigation than
  by a positional trail.

Breadcrumbs reflect the IA hierarchy; they never introduce a path that the IA does
not define.

---

# Back Navigation

Back navigation returns the user to their previous meaningful location while
**preserving research context**. Its expected behavior:

- **Context-preserving** — returning to a prior company, session, or comparison
  restores that context and its relevant contextual navigation, not a blank state.
- **Non-destructive** — back navigation never discards in-progress research;
  reasoning, sources, and the active session persist (aligned with J-06's promise
  that users never lose completed research).
- **Predictable** — "back" returns along the path the user actually took, so the
  outcome is anticipable.
- **Resumable** — where a user leaves and later returns, back navigation and
  Research History together allow a **Resume Session** rather than restarting.

The guiding rule: **no navigation action, including back, may cause loss of work.**

---

# AI Navigation Patterns

AI is reached **in context**, embedded within the domains where research happens.
These are movements *to AI assistance about the current subject*, not a separate AI
destination. Consistent with the Vision, AI is an embedded assistant, never a place
the user must leave research to visit.

| Pattern | Navigational meaning | Journeys |
|---------|---------------------|----------|
| **Ask AI** | Move into contextual question-and-answer about the current company or filing, without leaving its context. | J-02, J-04, J-05 |
| **Continue Research** | Move forward within the *active, in-progress* research session, carrying context. (Reopening *previously saved* work is **Resume Session**, per Contextual and Back Navigation.) | J-02 |
| **Jump to Source** | Move from an AI insight directly to the evidence it derives from (source traceability). | J-02, J-05 |
| **Related Companies** | Move from the current company to a related one, or into a comparison. | J-02, J-03 |
| **Explain This** | Move into a learner-level explanation of the current concept in context. | J-04, J-05 |

These patterns are embedded within existing domains and introduce no chatbot-style
standalone navigation. Every AI movement remains anchored to the research subject
and, for any insight, to its source.

---

# Responsive Navigation

Navigation structure is constant across contexts; only its *presentation density*
adapts. Destinations, hierarchy, and behavior do not change by context. Visual
design is out of scope for this document.

| Context | Navigation expectation |
|---------|------------------------|
| **Desktop** | Full global and contextual navigation available concurrently; the widest set of movements visible at once. |
| **Tablet** | The same structure and destinations, with navigation presented more compactly; no loss of reachable destinations. |
| **Mobile** | The same structure and destinations, prioritizing the current research context; secondary movements remain reachable, condensed rather than removed. |

Across all contexts the rule holds: **structure is preserved; only presentation
adapts.** No destination is available on one context and absent on another.

---

# Accessibility

Navigation must be fully operable by any user, independent of input method or
ability. Expectations:

| Requirement | Expectation |
|-------------|-------------|
| **Keyboard navigation** | Every navigational movement is fully operable via keyboard, with no pointer-only paths. |
| **Screen readers** | Navigable regions and destinations are programmatically identified and announced. |
| **Focus order** | Focus moves in a logical, predictable order that matches the visible/reading order; moving between contexts moves focus sensibly. |
| **ARIA expectations** | Navigation regions, current location, and state are exposed through appropriate roles and properties. |
| **WCAG AA** | Navigation meets WCAG 2.1 AA as the baseline conformance target. |

Accessibility is a structural requirement of navigation, not an enhancement layered
on afterward.

---

# Navigation States

Navigation must behave predictably in every state, always protecting research
context and never trapping the user.

| State | Expected navigation behavior |
|-------|------------------------------|
| **Loading** | Navigation remains available and responsive; the user is never blocked from moving while content loads. |
| **Empty** | When a destination has no content yet (e.g. no saved research), navigation offers a clear onward path rather than a dead end. |
| **Error** | The user can always move away from an errored destination; the error never removes global or back navigation. |
| **Offline** | Navigation degrades gracefully; the user is informed of limits without losing their place or in-progress work. |
| **Permission denied** | Restricted destinations are handled with a clear, recoverable path back to permitted areas, never a hard stop. |
| **No results** | Search and filtered views offer a clear next move (refine, broaden, or return) rather than a terminal empty state. |

The unifying rule across states: **the user can always move, and never loses
context or work.**

---

# Navigation Validation Checklist

| Check | Status | Basis |
|-------|--------|-------|
| Consistent with Information Architecture | ✅ | Every destination maps to an IA domain/level; no new places introduced. |
| Supports User Journeys | ✅ | Global, primary, and contextual paths map to J-01–J-06. |
| Supports Personas | ✅ | Movements serve P-01 and P-02 research and learning workflows. |
| AI integrated | ✅ | AI reached in context and embedded; no standalone chatbot navigation. |
| Context preserved (no lost work) | ✅ | Back and cross-domain movement are non-destructive. |
| Accessible | ✅ | Keyboard, screen-reader, focus order, ARIA, WCAG AA specified. |
| Responsive | ✅ | Structure constant; only presentation density adapts. |
| Implementation agnostic | ✅ | No layouts, components, or technology described. |

---

# Document Maintenance

This Navigation Structure is subordinate to the frozen Information Architecture and
the Product Discovery baseline. It should be revised only when the IA or an approved
product decision changes (via the governance Change Request process), and it should
be reviewed and approved before downstream UX and wireframe work treats it as
authoritative. Downstream detailing must align to this structure but must not
silently alter it.
