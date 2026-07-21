# AlphaScribe vNext — Screen Inventory

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.1 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | CTO |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For the MVP screen set |

**Downstream Dependencies:** UX Specifications · Wireframes · Component Inventory ·
Interaction Patterns · Responsive Behavior · Accessibility · States · PRDs · QA Test Plans

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial MVP screen inventory derived from the frozen Information Architecture and Navigation Structure. |
| 0.1.1 | 2026-07-18 | Product & Design | 📝 Draft | Experiential alignment to the approved Design Constitution (v1.1): added per-screen Experiential Profile (emotional goal, experience goal, AI presence, motion opportunities, continuity). No structural or scope change. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Design Constitution](00_Design_Constitution.md), [Information Architecture](03_Information_Architecture.md), [Navigation Structure](04_Navigation_Structure.md), [User Journeys](02_User_Journeys.md), [User Personas](01_User_Personas.md) |
| **Used By** | [UX Specifications](06_UX_Specifications.md), [Wireframes](07_Wireframes.md), [Component Inventory](09_Component_Inventory.md), [Responsive Behavior](11_Responsive_Behavior.md), [States](13_States.md), and PRDs. |
| **Related Documents** | [Product Vision](../master-plan/02_Product_Vision.md), [Feature Roadmap](../master-plan/03_Feature_Roadmap.md), [Requirements Traceability Matrix](../governance/Requirements_Traceability_Matrix.md) |

> This inventory names the MVP screens and their responsibilities. It introduces no
> new product capability; every screen realizes information domains and movements
> already defined in the frozen IA and Navigation Structure.

---

# Introduction

A **screen** is a distinct destination a user occupies while moving through the
product, as defined by the [Navigation Structure](04_Navigation_Structure.md). Each
screen presents one or more information areas from the
[Information Architecture](03_Information_Architecture.md) and serves specific
[User Journeys](02_User_Journeys.md) and [Personas](01_User_Personas.md).

The MVP consists of **eleven screens**. Where the IA defines content *levels* within
a domain (e.g. a company's Overview → Financials → Filings), those levels are
**sections within a screen** reached by secondary navigation, not separate screens —
consistent with the IA, which treats them as levels of one domain.

Every screen inherits the [Design Constitution](00_Design_Constitution.md): it must feel
calm, alive, premium, and collaborative — a living research workspace, never a static
dashboard. The **Experiential Profile** below states, for each screen, the feeling it must
create — not how to build it. It complements (does not replace) the structural attributes in
each screen definition.

## Experiential Profile (per screen)

| Screen | Primary Emotional Goal | Experience Goal | AI Presence | Motion Opportunities | Continuity Expectations |
|--------|------------------------|-----------------|-------------|----------------------|-------------------------|
| SCR-01 Landing | Assured, intrigued | Understand the value calmly, without hype | — | Gentle entrance that guides the eye to the value and the way in | Carries a confident first impression into sign-in |
| SCR-02 Authentication | Safe, unhurried | Getting in feels effortless and trustworthy | — | Feedback that acknowledges each input; smooth transition onward | Remembers intended destination; no restart on error |
| SCR-03 Onboarding & AI Setup | Reassured, in control | Setup feels light; validation feels alive, not a spinner | Access validation reads as active checking, calmly | Progress that makes validation feel underway | Flows seamlessly into the workspace, ready to research |
| SCR-04 Workspace Home | Focused, invited | A calm, ready starting point that invites the next question | — | Recent research reveals progressively; search responds instantly | Returning feels like resuming, not re-entering |
| SCR-05 Search Results | Efficient, oriented | Finding feels fast and recall-driven | — | Results settle in without jarring; refine feels continuous | Selecting preserves the originating context |
| SCR-06 Company Research | Confident, curious, calm | The core loop feels intelligent and effortless; evidence is always near | Summary, Copilot, Filing Analysis feel like a partner thinking and gathering evidence | Progressive reveal of content levels; AI thinking→streaming; source appears attached to insight | Section moves and AI never lose the company context |
| SCR-07 Comparison | Decisive, clear-headed | Weighing candidates feels honest and comparable | AI explains differences as a collaborator | Members add/remove fluidly; comparison updates continuously | Members trace back to their research; comparison is preservable |
| SCR-08 Learning | Encouraged, capable | Learning feels rewarding and unhurried | Learning assistance feels like a patient tutor thinking with the user | Explanations stream naturally; concepts reveal in context | Concept↔company↔source movement stays oriented |
| SCR-09 Research Library | Reassured, in command | Prior work feels safe, retrievable, and alive | — | Lists reveal progressively; Resume Session feels like stepping back in | Resume Session restores full prior context |
| SCR-10 Report View | Confident, satisfied | A grounded report that feels authoritative yet transparent | Presents grounded content with evidence felt | Report reveals in reading order; export confirms with quiet satisfaction | Sources and subject company remain one move away |
| SCR-11 Settings | Calm, in control | Adjusting feels safe and considered | Access validation reads as active, calm checking | Changes confirm with proportionate, reassuring feedback | Changes never disrupt research in progress |

These experiential goals are governed by the Constitution's Emotional Design (§5), Living
Interface (§6), AI Experience (§9), Motion (§14), and Micro-interaction (§19) philosophies.

## Screen Set (at a glance)

| Screen ID | Screen Name | IA Domain |
|-----------|-------------|-----------|
| SCR-01 | Landing Page | Workspace (public entry) |
| SCR-02 | Authentication | Account & AI Setup |
| SCR-03 | Onboarding & AI Setup | Account & AI Setup |
| SCR-04 | Workspace Home | Workspace Home |
| SCR-05 | Search Results | Workspace Home / Search & Discovery |
| SCR-06 | Company Research | Company Research |
| SCR-07 | Comparison | Comparison |
| SCR-08 | Learning | Learning |
| SCR-09 | Research Library | Research Library |
| SCR-10 | Report View | Research Library |
| SCR-11 | Settings | Account & AI Setup |

---

# Screen Definitions

## SCR-01 — Landing Page

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-01 |
| **Screen Name** | Landing Page |
| **Purpose** | Communicate what AlphaScribe is and its trust-first value before any commitment. |
| **Primary Persona(s)** | P-01, P-02 |
| **Supported Journey(s)** | J-01 |
| **Supported IA Section** | Workspace (public entry, precedes Account & AI Setup) |
| **Entry Points** | Direct/external arrival. |
| **Exit Points** | Authentication (SCR-02). |
| **Primary User Goal** | Understand the product's value and decide to begin. |
| **Available Actions** | Proceed to sign in / sign up; read value proposition. |
| **Information Displayed** | Product value proposition; trust positioning (grounded, explainable, source-traceable). |
| **AI Features Used** | None (marketing surface). |
| **Related Components** | Global header, primary action, value sections, footer. |
| **Responsive Priority** | High (first impression across all contexts). |
| **Accessibility Notes** | Clear heading order; single obvious entry action; keyboard reachable. |
| **Required States** | Loading, Error (per [States](13_States.md)). |
| **Dependencies** | None upstream. |

## SCR-02 — Authentication

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-02 |
| **Screen Name** | Authentication (Sign In · Sign Up · Password Reset) |
| **Purpose** | Establish an authenticated session behind the login wall. |
| **Primary Persona(s)** | P-01, P-02 |
| **Supported Journey(s)** | J-01 |
| **Supported IA Section** | Account & AI Setup → Session / Identity |
| **Entry Points** | Landing (SCR-01); any protected screen when unauthenticated. |
| **Exit Points** | Onboarding & AI Setup (SCR-03) for new/unconfigured users; Workspace Home (SCR-04) for returning users. |
| **Primary User Goal** | Sign in or create a session quickly. |
| **Available Actions** | Sign in; sign up; request password reset; submit reset. |
| **Information Displayed** | Identity fields; validation feedback; reset flow guidance. |
| **AI Features Used** | None. |
| **Related Components** | Form, input, validation message, primary action, inline notification. |
| **Responsive Priority** | High. |
| **Accessibility Notes** | Labeled fields; error text tied to fields; focus to first error; no credential auto-actions. |
| **Required States** | Loading, Error, Authentication Required, Success. |
| **Dependencies** | Session establishment (Account & AI Setup domain). |

## SCR-03 — Onboarding & AI Setup

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-03 |
| **Screen Name** | Onboarding & AI Setup |
| **Purpose** | Let the user choose and validate an AI access model (BYOK or Managed AI) with minimal friction. |
| **Primary Persona(s)** | P-01, P-02 |
| **Supported Journey(s)** | J-01 |
| **Supported IA Section** | Account & AI Setup → AI Access |
| **Entry Points** | Authentication (SCR-02) first run; Settings (SCR-11) when re-configuring. |
| **Exit Points** | Workspace Home (SCR-04) on validated access. |
| **Primary User Goal** | Reach a working AI access state and enter the workspace. |
| **Available Actions** | Choose Managed AI; choose BYOK and provide a key; validate; continue. |
| **Information Displayed** | AI access options; validation status; guidance. |
| **AI Features Used** | AI access validation (setup only, not research). |
| **Related Components** | Choice control, form, input, validation message, primary action. |
| **Responsive Priority** | High. |
| **Accessibility Notes** | Options announced as a group; validation status announced; key entry never spoken back. |
| **Required States** | Loading, Error, Success, Permission Denied. |
| **Dependencies** | Authenticated session (SCR-02). |

## SCR-04 — Workspace Home

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-04 |
| **Screen Name** | Workspace Home |
| **Purpose** | The entry point into research and a path back to recent work. |
| **Primary Persona(s)** | P-01, P-02 |
| **Supported Journey(s)** | J-01, J-02 |
| **Supported IA Section** | Workspace Home (entry & company search, recent research) |
| **Entry Points** | Post-auth/onboarding; global navigation from any screen. |
| **Exit Points** | Search Results (SCR-05); Company Research (SCR-06); Research Library (SCR-09). |
| **Primary User Goal** | Start a new research task or resume recent work. |
| **Available Actions** | Search a company; open recent research; navigate to any global domain. |
| **Information Displayed** | Company search entry; recent research activity. |
| **AI Features Used** | None directly (routes into AI-bearing screens). |
| **Related Components** | Global navigation, global search, recent-research list, empty state. |
| **Responsive Priority** | High. |
| **Accessibility Notes** | Search is the primary focus target; recent items are a navigable list. |
| **Required States** | Loading, Empty (no recent research), Error. |
| **Dependencies** | Session; Research Library for recent items. |

## SCR-05 — Search Results

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-05 |
| **Screen Name** | Search Results |
| **Purpose** | Resolve a search intent to a company or prior research and move the user there. |
| **Primary Persona(s)** | P-01, P-02 |
| **Supported Journey(s)** | J-02, J-06 |
| **Supported IA Section** | Search & Discovery |
| **Entry Points** | Global/company search from any screen. |
| **Exit Points** | Company Research (SCR-06); a Research Library item (SCR-09/SCR-10). |
| **Primary User Goal** | Find and select the intended company or prior work. |
| **Available Actions** | Refine query; filter results; select a result. |
| **Information Displayed** | Matching companies; matching prior research; recent searches. |
| **AI Features Used** | None (discovery surface). |
| **Related Components** | Search field, results list, filter, empty/no-results state. |
| **Responsive Priority** | High. |
| **Accessibility Notes** | Results announced with count; keyboard-selectable; clear no-results messaging. |
| **Required States** | Loading, No Results, Error. |
| **Dependencies** | Search & Discovery; Company Research; Research Library. |

## SCR-06 — Company Research

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-06 |
| **Screen Name** | Company Research |
| **Purpose** | Everything needed to understand one company, in one coherent place. |
| **Primary Persona(s)** | P-01, P-02 |
| **Supported Journey(s)** | J-02, J-05 |
| **Supported IA Section** | Company Research (Overview → Business Summary → Financial Metrics → Financial Statements → SEC Filings → AI Insights → Export) |
| **Entry Points** | Workspace Home (SCR-04); Search Results (SCR-05); Comparison (SCR-07); Research Library (SCR-09). |
| **Exit Points** | Comparison (SCR-07); Learning (SCR-08); Report View (SCR-10); Research Library (SCR-09). |
| **Primary User Goal** | Reach a confident, sourced understanding of the company (J-02). |
| **Available Actions** | Move across content sections; ask the copilot; jump to source; add to comparison; save/export research; enter learning. |
| **Information Displayed** | Overview; business summary; financial metrics; financial statements; SEC filings; grounded AI insights. |
| **AI Features Used** | AI Summary; AI Copilot; Filing Analysis (all grounded, source-traceable). |
| **Related Components** | Secondary navigation, content sections, metric displays, statement tables, filing viewer, AI insight panel, source references, charts. |
| **Responsive Priority** | Critical (core research loop). |
| **Accessibility Notes** | Section order follows content hierarchy; every insight has a keyboard-reachable source path; tables and charts have accessible equivalents. |
| **Required States** | Loading, Skeleton, Empty, Error, Partial Failure, AI Thinking, AI Streaming. |
| **Dependencies** | Company Research domain; Trusted AI; Data visualization. |

## SCR-07 — Comparison

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-07 |
| **Screen Name** | Comparison |
| **Purpose** | Evaluate a small set of companies side by side on comparable terms. |
| **Primary Persona(s)** | P-01 |
| **Supported Journey(s)** | J-03 |
| **Supported IA Section** | Comparison (a derived domain; consumes companies from Company Research) |
| **Entry Points** | Company Research (SCR-06); Research Library (SCR-09, a saved comparison). |
| **Exit Points** | Company Research (SCR-06) for a member; Research Library (SCR-09) to preserve. |
| **Primary User Goal** | Reach a ranked view across candidates (J-03). |
| **Available Actions** | Add/remove a company; view comparative metrics/summaries; ask the copilot about differences; save comparison. |
| **Information Displayed** | Selected company set; comparative metrics and summaries; AI explanation of differences. |
| **AI Features Used** | AI Company Comparison (explanation of differences). |
| **Related Components** | Comparison table, company chips, metric displays, AI insight panel, empty state. |
| **Responsive Priority** | High. |
| **Accessibility Notes** | Comparison table is navigable by row/column with headers; "not comparable" states clearly announced. |
| **Required States** | Loading, Empty (no companies selected), Partial Failure (uncomparable member), Error, AI Thinking/Streaming. |
| **Dependencies** | **Requires Company Research** (cannot exist independently, per IA). |

## SCR-08 — Learning

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-08 |
| **Screen Name** | Learning |
| **Purpose** | Turn a real company and its filings into explainable, learner-level material. |
| **Primary Persona(s)** | P-02 |
| **Supported Journey(s)** | J-04, J-05 |
| **Supported IA Section** | Learning (overlays Company Research / Filings with learner explanation) |
| **Entry Points** | Company Research (SCR-06, "Explain This"); global navigation (Learning). |
| **Exit Points** | Company Research (SCR-06); Research Library (SCR-09). |
| **Primary User Goal** | Understand a concept in a company's context and apply it (J-04). |
| **Available Actions** | Ask for a concept explanation; follow guided exploration; self-check an interpretation; return to the company. |
| **Information Displayed** | Concept explanations set in the company's context; worked framing; self-check. |
| **AI Features Used** | Learning Assistance (learner-level explanation); AI Copilot. |
| **Related Components** | AI insight panel, concept explanation, source references, company context reference. |
| **Responsive Priority** | Medium-High. |
| **Accessibility Notes** | Explanations linearly readable; concept-to-source and concept-to-company links keyboard reachable. |
| **Required States** | Loading, Empty, Error, AI Thinking, AI Streaming. |
| **Dependencies** | Company Research (as the live example). |

## SCR-09 — Research Library

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-09 |
| **Screen Name** | Research Library |
| **Purpose** | Preserve, retrieve, and resume durable research. |
| **Primary Persona(s)** | P-01, P-02 |
| **Supported Journey(s)** | J-06 |
| **Supported IA Section** | Research Library (Research Sessions · Research Reports · Saved Exports · Research History) |
| **Entry Points** | Global navigation; Workspace Home (SCR-04). |
| **Exit Points** | Report View (SCR-10); Company Research (SCR-06) via Resume Session; Comparison (SCR-07). |
| **Primary User Goal** | Retrieve prior work and resume or update it (J-06). |
| **Available Actions** | Browse/filter sessions, reports, saved exports, history; open a report; **Resume Session**; open a saved export. |
| **Information Displayed** | Research sessions (with saved reasoning/sources); research reports; saved exports; research history. |
| **AI Features Used** | None directly (routes back into AI-bearing research). |
| **Related Components** | Library lists, filters, list items, empty state, history list. |
| **Responsive Priority** | High. |
| **Accessibility Notes** | Lists navigable with clear item labels and dates; filters keyboard operable. |
| **Required States** | Loading, Empty (no saved research), No Results (filtered), Error. |
| **Dependencies** | Receives output from Company Research and Comparison. |

## SCR-10 — Report View

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-10 |
| **Screen Name** | Report View |
| **Purpose** | Present a single grounded, source-backed research report and allow export. |
| **Primary Persona(s)** | P-01, P-02 |
| **Supported Journey(s)** | J-02, J-06 |
| **Supported IA Section** | Research Library → Research Reports / Saved Exports |
| **Entry Points** | Research Library (SCR-09); Company Research (SCR-06) after generating a report. |
| **Exit Points** | Research Library (SCR-09); Company Research (SCR-06) via source/company links. |
| **Primary User Goal** | Read a report with its reasoning and sources, and export it (J-06). |
| **Available Actions** | Read the report; inspect sources; export; return to subject company. |
| **Information Displayed** | Report content; preserved reasoning; source references. |
| **AI Features Used** | Presents AI-generated, grounded report content (produced upstream). |
| **Related Components** | Report content, source references, export action, primary/secondary actions. |
| **Responsive Priority** | High. |
| **Accessibility Notes** | Report is linear and readable; every claim has a reachable source; export announced. |
| **Required States** | Loading, Error, Success (export), Timeout. |
| **Dependencies** | Research Library; report generation upstream. |

## SCR-11 — Settings

| Attribute | Detail |
|-----------|--------|
| **Screen ID** | SCR-11 |
| **Screen Name** | Settings |
| **Purpose** | Manage account and AI access after onboarding. |
| **Primary Persona(s)** | P-01, P-02 |
| **Supported Journey(s)** | J-01 |
| **Supported IA Section** | Account & AI Setup |
| **Entry Points** | Global navigation. |
| **Exit Points** | Any global destination; Onboarding & AI Setup (SCR-03) for re-configuration. |
| **Primary User Goal** | Adjust account details and AI access model. |
| **Available Actions** | View/update account details; change AI access (BYOK/Managed); re-validate; sign out. |
| **Information Displayed** | Account information; current AI access model and status. |
| **AI Features Used** | AI access validation (setup only). |
| **Related Components** | Settings sections, form, input, validation message, primary action. |
| **Responsive Priority** | Medium. |
| **Accessibility Notes** | Grouped settings with headings; changes confirmed; sensitive values never spoken back. |
| **Required States** | Loading, Error, Success, Authentication Required. |
| **Dependencies** | Authenticated session. |

---

# Screen Traceability Matrix

Every screen traces to at least one persona and one approved journey, and to an IA
domain. No screen exists without this trace.

| Screen | Personas | Journeys | IA Domain | Primary AI Feature |
|--------|----------|----------|-----------|--------------------|
| SCR-01 Landing Page | P-01, P-02 | J-01 | Workspace (public) | — |
| SCR-02 Authentication | P-01, P-02 | J-01 | Account & AI Setup | — |
| SCR-03 Onboarding & AI Setup | P-01, P-02 | J-01 | Account & AI Setup | Access validation |
| SCR-04 Workspace Home | P-01, P-02 | J-01, J-02 | Workspace Home | — |
| SCR-05 Search Results | P-01, P-02 | J-02, J-06 | Search & Discovery | — |
| SCR-06 Company Research | P-01, P-02 | J-02, J-05 | Company Research | Summary · Copilot · Filing Analysis |
| SCR-07 Comparison | P-01 | J-03 | Comparison | Comparison explanation |
| SCR-08 Learning | P-02 | J-04, J-05 | Learning | Learning Assistance · Copilot |
| SCR-09 Research Library | P-01, P-02 | J-06 | Research Library | — |
| SCR-10 Report View | P-01, P-02 | J-02, J-06 | Research Library | Grounded report content |
| SCR-11 Settings | P-01, P-02 | J-01 | Account & AI Setup | Access validation |

**Coverage check:** J-01 (SCR-01/02/03/04/11) · J-02 (SCR-04/05/06/10) · J-03 (SCR-07) ·
J-04 (SCR-08) · J-05 (SCR-06/08) · J-06 (SCR-05/09/10). All six journeys covered; both
Primary personas served; no screen maps outside the frozen IA.
