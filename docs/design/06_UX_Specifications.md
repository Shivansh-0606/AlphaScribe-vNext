# AlphaScribe vNext — UX Specifications

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.0 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | _Pending_ |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For per-screen UX behavior (pending approval) |

**Downstream Dependencies:** Wireframes · Component Inventory · Interaction Patterns ·
Responsive Behavior · Accessibility · States · PRDs · QA Test Plans

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial behavioral UX specifications for the eleven MVP screens. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Screen Inventory](05_Screen_Inventory.md), [Navigation Structure](04_Navigation_Structure.md), [Information Architecture](03_Information_Architecture.md), [User Journeys](02_User_Journeys.md) |
| **Used By** | [Wireframes](07_Wireframes.md), [Interaction Patterns](10_Interaction_Patterns.md), [States](13_States.md), and PRDs. |
| **Related Documents** | [User Personas](01_User_Personas.md), [Product Vision](../master-plan/02_Product_Vision.md) |

> This document specifies **behavior** per screen — what happens and what the user
> experiences — not layout or implementation. Layout is in
> [Wireframes](07_Wireframes.md); reusable behaviors are in
> [Interaction Patterns](10_Interaction_Patterns.md); state definitions are in
> [States](13_States.md) and referenced here rather than re-specified.

---

# Introduction

Each screen from the [Screen Inventory](05_Screen_Inventory.md) is specified below
across a fixed set of behavioral facets. Cross-cutting behaviors (state definitions,
interaction patterns, accessibility rules) are defined once in their own documents and
referenced here to avoid duplication. Universal rules that apply to every screen are
stated once in *Global UX Rules* and not repeated per screen.

---

# Global UX Rules

These apply to all screens and are assumed in every specification below.

- **Trust-first:** every AI insight is presented with a path to its source; nothing
  authoritative is source-less (Vision; Trusted AI).
- **Context preservation:** no navigation action, including back, may lose in-progress
  work (Navigation Structure; J-06).
- **Progressive disclosure:** summary precedes detail; explanation precedes raw figures.
- **State coverage:** every screen implements its Required States from
  [States](13_States.md); those behaviors are not re-specified per facet unless the
  screen deviates.
- **Accessibility floor:** WCAG AA, full keyboard operability, logical focus order
  (see [Accessibility](12_Accessibility.md)).
- **Performance intent:** perceived responsiveness favored over completeness; long or
  AI-bound operations reveal progress immediately (see per-screen Performance).

---

# SCR-01 — Landing Page

- **Objective:** Convey value and trust positioning; move the user to begin.
- **User Goals:** Understand what AlphaScribe does and why it can be trusted.
- **Primary Tasks:** Read value; proceed to authentication.
- **User Flow:** Arrive → understand value → proceed to Sign In/Sign Up (J-01).
- **Information Hierarchy:** Value proposition → trust positioning → entry action.
- **AI Behaviour:** None.
- **Interaction Rules:** A single, unambiguous entry action; value communicated before commitment.
- **Validation Rules:** None (no input).
- **Edge Cases:** Returning authenticated user is routed onward rather than shown marketing.
- **Loading Behaviour:** Content-first; entry action available as soon as rendered.
- **Empty Behaviour:** N/A.
- **Error Behaviour:** If the page cannot fully load, the entry action still functions.
- **Success Behaviour:** User proceeds to SCR-02.
- **Keyboard Behaviour:** Entry action reachable and operable by keyboard.
- **Accessibility Behaviour:** Logical heading order; descriptive entry action.
- **Performance Expectations:** Fast first render; no blocking on non-essential content.

---

# SCR-02 — Authentication

- **Objective:** Establish a session with minimal friction.
- **User Goals:** Sign in, sign up, or recover access.
- **Primary Tasks:** Enter identity; submit; recover password.
- **User Flow:** Choose sign in/up → enter details → validate → proceed to SCR-03 (new) or SCR-04 (returning) (J-01).
- **Information Hierarchy:** Mode (sign in/up) → fields → submit → recovery link.
- **AI Behaviour:** None.
- **Interaction Rules:** One primary action; recovery is secondary; no credential is ever echoed back.
- **Validation Rules:** Required-field and format validation; errors shown inline, tied to the field; submission blocked until resolvable.
- **Edge Cases:** Rate-limited attempts communicated calmly with recovery guidance; expired reset handled with a clear re-request path.
- **Loading Behaviour:** Submit shows progress; the form disables re-submission while pending.
- **Empty Behaviour:** N/A.
- **Error Behaviour:** See [States](13_States.md) Error/Authentication Required; messages are specific and recoverable, never blaming.
- **Success Behaviour:** Session established; user routed onward.
- **Keyboard Behaviour:** Logical field order; Enter submits; focus moves to first error on failure.
- **Accessibility Behaviour:** Labeled fields; programmatic error association; focus management on error.
- **Performance Expectations:** Immediate validation feedback; prompt submit response.

---

# SCR-03 — Onboarding & AI Setup

- **Objective:** Reach a validated AI access state with least friction.
- **User Goals:** Choose an AI model and confirm it works.
- **Primary Tasks:** Select Managed AI, or select BYOK and provide a key; validate; continue.
- **User Flow:** Choose access model → (BYOK: provide key) → validate → enter Workspace Home (J-01).
- **Information Hierarchy:** Access choice → (conditional key entry) → validation status → continue.
- **AI Behaviour:** Validation of access only; no research AI here.
- **Interaction Rules:** Managed AI is the frictionless default; BYOK is a first-class equal; continue is enabled only on validated access.
- **Validation Rules:** BYOK key presence and validity checked before continue; failure explained with a recovery step.
- **Edge Cases:** Managed AI unavailable → offer BYOK path; invalid key → guided correction (J-01 failure states).
- **Loading Behaviour:** Validation shows progress; continue reflects validated status.
- **Empty Behaviour:** N/A.
- **Error Behaviour:** Setup failure is a guided, recoverable step, never a dead end (Navigation States; J-01).
- **Success Behaviour:** Access validated; user enters SCR-04.
- **Keyboard Behaviour:** Options selectable by keyboard; key field labeled; Enter validates.
- **Accessibility Behaviour:** Options exposed as a group; validation status announced; key never spoken back.
- **Performance Expectations:** Validation feedback is prompt; the user is never left uncertain of status.

---

# SCR-04 — Workspace Home

- **Objective:** Start research fast or return to recent work.
- **User Goals:** Search a company; resume recent research.
- **Primary Tasks:** Enter a search; open a recent item; navigate to a domain.
- **User Flow:** Arrive → search a company (→ SCR-05/06) or open recent research (→ SCR-06/09) (J-01, J-02).
- **Information Hierarchy:** Search entry (primary) → recent research → global navigation.
- **AI Behaviour:** None directly; routes into AI-bearing screens.
- **Interaction Rules:** Search is the primary focus; recent research offers one-move return.
- **Validation Rules:** Search tolerates partial input; no hard validation.
- **Edge Cases:** No recent research → Empty state guiding a first search.
- **Loading Behaviour:** Recent research may load progressively; search is available immediately.
- **Empty Behaviour:** Empty recent-research state prompts starting a search (see [States](13_States.md)).
- **Error Behaviour:** Recent-research load failure is non-blocking; search remains usable.
- **Success Behaviour:** User moves into research.
- **Keyboard Behaviour:** Focus lands on search; recent items are a navigable list.
- **Accessibility Behaviour:** Search labeled; recent list announced with counts and dates.
- **Performance Expectations:** Search entry instantly usable; recent items load without blocking.

---

# SCR-05 — Search Results

- **Objective:** Resolve intent to a destination.
- **User Goals:** Find the intended company or prior research.
- **Primary Tasks:** Refine query; filter; select a result.
- **User Flow:** Enter/adjust query → review results → select → move to destination (J-02, J-06).
- **Information Hierarchy:** Query → results (companies, prior research) → recent searches.
- **AI Behaviour:** None.
- **Interaction Rules:** Results lead only to existing destinations; selecting a result preserves the originating context.
- **Validation Rules:** Empty query handled gracefully; no error for short input.
- **Edge Cases:** No matches → No Results with refine/broaden guidance.
- **Loading Behaviour:** Results show progressive/loading feedback; prior results remain until replaced.
- **Empty Behaviour:** Pre-search prompt; recent searches offered.
- **Error Behaviour:** Search failure offers retry without losing the query.
- **Success Behaviour:** User reaches the chosen company or research item.
- **Keyboard Behaviour:** Results navigable and selectable by keyboard; Enter opens focused result.
- **Accessibility Behaviour:** Result count announced; no-results message explicit.
- **Performance Expectations:** Responsive feedback as the query changes.

---

# SCR-06 — Company Research

- **Objective:** Deliver a confident, sourced understanding of one company.
- **User Goals:** Understand the business and its health; ask questions; verify sources (J-02); practice on filings (J-05).
- **Primary Tasks:** Read the summary and metrics; move across content sections; ask the copilot; jump to source; add to comparison; save/export.
- **User Flow:** Enter company → overview → business summary → metrics → statements → filings → AI insights → (compare / learn / save / export) (J-02, J-05).
- **Information Hierarchy:** Follows the IA content hierarchy: Company → Overview → Business Summary → Financial Metrics → Financial Statements → SEC Filings → AI Insights → Export.
- **AI Behaviour:** AI Summary presented first and grounded; Copilot answers in context and anchored to sources; Filing Analysis interprets primary sources; every insight offers *Jump to Source*. AI never presents a recommendation; it informs (Strategy).
- **Interaction Rules:** Summary precedes figures; every metric carries its meaning; sources always reachable; adding to comparison carries the company into SCR-07.
- **Validation Rules:** Copilot input is free-form; empty queries are ignored gracefully.
- **Edge Cases:** Company not covered → Empty/No-coverage guidance with an alternative path (J-02 failure); a data source unavailable → Partial Failure showing what is available (Vision: best-effort sources).
- **Loading Behaviour:** Skeleton for content regions; AI insight shows *AI Thinking* then *AI Streaming* (see [States](13_States.md)).
- **Empty Behaviour:** Sections with no data show an explicit, non-dead-end empty state.
- **Error Behaviour:** A failed section degrades locally without taking down the screen; sources and other sections remain usable.
- **Success Behaviour:** User reaches a sourced conclusion; can save/export/compare.
- **Keyboard Behaviour:** Section (secondary) navigation operable by keyboard; copilot reachable; source links focusable.
- **Accessibility Behaviour:** Content order matches the hierarchy; tables/charts have accessible equivalents; streaming AI output is announced without overwhelming (see [Accessibility](12_Accessibility.md)).
- **Performance Expectations:** Overview and summary appear quickly; AI output streams progressively rather than blocking; source inspection is immediate.

---

# SCR-07 — Comparison

- **Objective:** Produce a ranked, comparable view across candidates.
- **User Goals:** Decide between companies on comparable terms (J-03).
- **Primary Tasks:** Assemble the set; read comparative metrics/summaries; ask about differences; save.
- **User Flow:** Add companies (from research) → view side by side → ask copilot about differences → rank → save/preserve (J-03).
- **Information Hierarchy:** Selected set → comparative metrics/summaries → AI explanation of differences.
- **AI Behaviour:** Copilot narrates the *meaning* of differences, grounded and sourced; never a buy/sell verdict.
- **Interaction Rules:** Members are drawn from Company Research (derived domain); like-for-like by default; non-comparable data is flagged, not hidden (IA/Journeys).
- **Validation Rules:** A comparison needs at least two members to be meaningful; below that, guidance to add more.
- **Edge Cases:** A member lacks comparable data → Partial Failure flags the gap; removing all members → Empty.
- **Loading Behaviour:** Comparative view loads progressively; AI explanation streams.
- **Empty Behaviour:** No members → Empty prompting selection from research.
- **Error Behaviour:** A single member's failure does not break the comparison.
- **Success Behaviour:** User forms a justified ranking; can preserve it.
- **Keyboard Behaviour:** Table navigable by row/column; add/remove operable by keyboard.
- **Accessibility Behaviour:** Comparison table has clear headers; "not comparable" announced.
- **Performance Expectations:** Adding/removing a member updates promptly; AI explanation streams.

---

# SCR-08 — Learning

- **Objective:** Make concepts understandable in a company's real context.
- **User Goals:** Understand *why* a concept matters and apply it (J-04); practice on filings (J-05).
- **Primary Tasks:** Ask for an explanation; explore related concepts; self-check an interpretation.
- **User Flow:** Pick/carry a company example → ask to explain a concept → learner-level answer → follow-ups → self-check → repeat (J-04, J-05).
- **Information Hierarchy:** Concept → explanation in company context → related concepts / self-check → source.
- **AI Behaviour:** Learning Assistance pitches explanations to a learner, tied to the company's figures, grounded and sourced; invites the next question rather than closing the topic (Personas P-02; Journeys).
- **Interaction Rules:** Explanations adapt to a learner; always tied back to the specific company; sources reachable.
- **Validation Rules:** Free-form questions; empty input ignored gracefully.
- **Edge Cases:** Explanation pitched too high → user can request simpler; missing company context → prompt to choose an example.
- **Loading Behaviour:** *AI Thinking* → *AI Streaming*.
- **Empty Behaviour:** No concept chosen → prompt with a starting point.
- **Error Behaviour:** AI failure offers retry; prior explanation retained.
- **Success Behaviour:** User understands and can apply the concept independently.
- **Keyboard Behaviour:** Concept/company/source links focusable; question entry reachable.
- **Accessibility Behaviour:** Explanations linearly readable; streaming announced considerately.
- **Performance Expectations:** Explanations stream; follow-ups feel continuous.

---

# SCR-09 — Research Library

- **Objective:** Retrieve and resume durable research.
- **User Goals:** Find prior work and resume or update it (J-06).
- **Primary Tasks:** Browse/filter sessions, reports, saved exports, history; open; **Resume Session**.
- **User Flow:** Open library → browse/filter → select session/report/export → Resume Session or open report (J-06).
- **Information Hierarchy:** Research Sessions → Research Reports → Saved Exports → Research History.
- **AI Behaviour:** None directly; Resume Session returns to AI-bearing research with context intact.
- **Interaction Rules:** Resume Session restores prior reasoning and sources; nothing is lost on return (J-06).
- **Validation Rules:** Filters tolerate empty/!partial input.
- **Edge Cases:** No saved research → Empty; filtered to nothing → No Results.
- **Loading Behaviour:** Lists load progressively.
- **Empty Behaviour:** First-time empty state explains how research is saved.
- **Error Behaviour:** Load failure offers retry without losing filters.
- **Success Behaviour:** User resumes or opens prior work.
- **Keyboard Behaviour:** Lists and filters keyboard operable; Enter opens focused item.
- **Accessibility Behaviour:** Items labeled with subject and date; filter controls labeled.
- **Performance Expectations:** Library is quick to browse; Resume Session restores promptly.

---

# SCR-10 — Report View

- **Objective:** Present a grounded, source-backed report and enable export.
- **User Goals:** Read a report with reasoning and sources; export it (J-06).
- **Primary Tasks:** Read; inspect sources; export; return to subject company.
- **User Flow:** Open report → read → inspect sources → export → (return to company) (J-02, J-06).
- **Information Hierarchy:** Report conclusion/summary → reasoning → detailed content → sources → export.
- **AI Behaviour:** Presents AI-generated grounded content produced upstream; every claim traces to a source.
- **Interaction Rules:** Export preserves reasoning and sources, not just a conclusion (J-06); sources always reachable.
- **Validation Rules:** N/A (read/export).
- **Edge Cases:** Export unsupported/interrupted → clear recovery; source unavailable → flagged inline.
- **Loading Behaviour:** Report loads progressively; export shows progress.
- **Empty Behaviour:** N/A (a report always has content).
- **Error Behaviour:** Export failure offers retry without losing the report; see Timeout in [States](13_States.md).
- **Success Behaviour:** Report read; export completes with confirmation.
- **Keyboard Behaviour:** Sources and export operable by keyboard; report is linearly navigable.
- **Accessibility Behaviour:** Linear reading order; export result announced; sources reachable.
- **Performance Expectations:** Report renders promptly; export feedback is immediate.

---

# SCR-11 — Settings

- **Objective:** Manage account and AI access after onboarding.
- **User Goals:** Update account details; change AI access model.
- **Primary Tasks:** Edit account; change/validate AI access; sign out.
- **User Flow:** Open settings → adjust account or AI access → validate/save → confirmation (J-01).
- **Information Hierarchy:** Account → AI access → session (sign out).
- **AI Behaviour:** AI access validation only.
- **Interaction Rules:** Changes are explicit and confirmed; AI access re-validates on change; sensitive values never echoed.
- **Validation Rules:** Field validation on account changes; BYOK key validated before it takes effect.
- **Edge Cases:** Invalid new key → prior working access retained until a valid one is confirmed.
- **Loading Behaviour:** Save/validate shows progress.
- **Empty Behaviour:** N/A.
- **Error Behaviour:** Change failure is recoverable and non-destructive.
- **Success Behaviour:** Change saved and confirmed.
- **Keyboard Behaviour:** Grouped controls keyboard operable; save via keyboard.
- **Accessibility Behaviour:** Settings grouped with headings; confirmations announced.
- **Performance Expectations:** Changes save promptly with clear confirmation.
