# AlphaScribe vNext — Interaction Patterns

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.0 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | _Pending_ |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For reusable interaction behavior (pending approval) |

**Downstream Dependencies:** Responsive Behavior · Accessibility · States · Frontend
implementation · PRDs · QA Test Plans

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial reusable interaction pattern library. Uploads flagged as non-MVP. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Component Inventory](09_Component_Inventory.md), [UX Specifications](06_UX_Specifications.md), [Navigation Structure](04_Navigation_Structure.md), [Design System](08_Design_System.md) |
| **Used By** | [Responsive Behavior](11_Responsive_Behavior.md), [Accessibility](12_Accessibility.md), [States](13_States.md), Frontend implementation. |
| **Related Documents** | [Screen Inventory](05_Screen_Inventory.md), [User Journeys](02_User_Journeys.md) |

> Reusable interaction behaviors, defined once and referenced by screens and
> components. Behavior only — no implementation. Where an interaction produces a
> state, that state is defined in [States](13_States.md) and referenced here.

---

# Introduction

These patterns describe *how interactions behave* consistently across the product.
Each pattern lists Purpose, Behaviour, Expected User Experience, Accessibility, and
Failure Handling. Patterns compose the components in
[Component Inventory](09_Component_Inventory.md) and serve the screens in
[Screen Inventory](05_Screen_Inventory.md).

---

# Navigation
- **Purpose:** Move between and within domains (per [Navigation Structure](04_Navigation_Structure.md)).
- **Behaviour:** Global navigation is persistent and direct; secondary navigation moves across content levels within a domain; movement preserves research context; **Resume Session** reopens saved work.
- **Expected UX:** Predictable, low-click movement; the user always knows where they are and can get back.
- **Accessibility:** Navigation landmarks; current location exposed; full keyboard operability; logical focus on transition.
- **Failure Handling:** A failed destination never removes global/back navigation; context is retained.

# Search
- **Purpose:** Resolve intent to a company or prior research.
- **Behaviour:** Query updates results responsively; recent searches offered; selecting a result preserves origin context.
- **Expected UX:** Fast recall over reconstruction; typing yields relevant matches.
- **Accessibility:** Labeled field; result count announced; keyboard selection.
- **Failure Handling:** No matches → No Results with refine/broaden guidance; search error → retry without losing the query.

# Filtering
- **Purpose:** Narrow a set (results, library, comparison members).
- **Behaviour:** Filters apply immediately and are combinable; active filters are visible and clearable.
- **Expected UX:** Reduces what the user must consider without hiding the path back to the full set.
- **Accessibility:** Filter controls labeled; applied filters announced; keyboard operable.
- **Failure Handling:** Over-filtering to empty → No Results with a clear "clear filters" path.

# Sorting
- **Purpose:** Order a set for easier scanning (e.g. library items, comparison metrics).
- **Behaviour:** Sort is explicit, reversible, and the current order is indicated.
- **Expected UX:** Predictable reordering; the choice persists within the context.
- **Accessibility:** Sort control labeled; current sort state announced.
- **Failure Handling:** Sort never hides data; on error, prior order is retained.

# Pagination
- **Purpose:** Traverse long sets (history, results) without overload.
- **Behaviour:** Sets load in manageable segments (paged or incremental); position is clear.
- **Expected UX:** Controlled progress through a large set; no loss of place.
- **Accessibility:** Page/segment controls labeled; new content announced; keyboard operable.
- **Failure Handling:** A failed segment offers retry without losing loaded content.

# Tables
- **Purpose:** Present structured data (statements, comparisons).
- **Behaviour:** Row/column structure with clear headers; horizontal overflow scrolls within its own region, never the page.
- **Expected UX:** Scannable, aligned data; meaning tied to headers.
- **Accessibility:** Header association and scope; row/column navigation; not color-only.
- **Failure Handling:** Missing cells shown as explicit "no data"; partial data flagged (Partial Failure).

# Charts
- **Purpose:** Visualize financial trends.
- **Behaviour:** Render series with labels; interaction reveals values on demand.
- **Expected UX:** Trends readable at a glance; detail available without clutter.
- **Accessibility:** Accessible data equivalent (table/text); not color-only; described in [Accessibility](12_Accessibility.md).
- **Failure Handling:** Data unavailable → Empty/Partial Failure with the equivalent table still offered.

# Forms
- **Purpose:** Capture input (auth, AI setup, settings).
- **Behaviour:** Inline validation; submission blocked until resolvable; progress on submit; no double-submit.
- **Expected UX:** Errors are specific, adjacent, and recoverable; the user is never blamed.
- **Accessibility:** Labels and errors programmatically linked; focus moves to first error; sensitive values never echoed.
- **Failure Handling:** Submit failure preserves entered values (except secrets) and explains the recovery step.

# Dialogs
- **Purpose:** Request a focused decision inline (e.g. confirm a discard).
- **Behaviour:** Interrupts minimally; a clear primary and cancel; dismissible.
- **Expected UX:** Quick, contained decision without losing context.
- **Accessibility:** Focus trapped within; return focus on close; labeled.
- **Failure Handling:** Cancel is always safe and non-destructive.

# Modals
- **Purpose:** A larger focused task overlaying the current context.
- **Behaviour:** Overlays without navigating away; background inert; explicit close.
- **Expected UX:** Deep focus without losing the underlying research state.
- **Accessibility:** Focus management, escape to close, labeled; background not reachable.
- **Failure Handling:** Closing never discards underlying work.

# Drawers
- **Purpose:** Contextual side surfaces (e.g. embedded copilot, sources).
- **Behaviour:** Slide in beside content; content remains visible; dismissible.
- **Expected UX:** AI/sources available *beside* research, not replacing it (embedded AI).
- **Accessibility:** Reachable and dismissible by keyboard; focus order sensible.
- **Failure Handling:** Drawer failure never blocks the main content.

# Notifications
- **Purpose:** Communicate transient outcomes.
- **Behaviour:** Appear briefly, dismissible, non-blocking; severity-appropriate.
- **Expected UX:** Awareness without interruption.
- **Accessibility:** Announced politely or assertively per severity; not motion-only; dismissible.
- **Failure Handling:** Critical failures escalate to an Error state rather than a transient toast.

# Tooltips
- **Purpose:** On-demand supplementary explanation (incl. learner definitions).
- **Behaviour:** Reveal on hover/focus; never contain essential-only content.
- **Expected UX:** Help when wanted, invisible otherwise.
- **Accessibility:** Keyboard/focus reachable; content also available another way.
- **Failure Handling:** N/A (supplementary).

# AI Streaming
- **Purpose:** Reveal AI output progressively as it is produced.
- **Behaviour:** *AI Thinking* → *AI Streaming* → complete; partial output is readable as it arrives; sources attach as/after content resolves; user can stop.
- **Expected UX:** Immediate sense of progress; reading can begin before completion; never a frozen wait.
- **Accessibility:** Streaming announced considerately (not character-by-character spam); completion announced; sources reachable.
- **Failure Handling:** Interruption/Timeout leaves partial content with a retry; prior content retained (see [States](13_States.md)).

# AI Chat
- **Purpose:** Contextual question-and-answer with the embedded copilot.
- **Behaviour:** Anchored to the current subject (company/comparison/concept); each answer grounded and source-linked; follow-ups retain context within the session.
- **Expected UX:** A research assistant in context — not a separate chatbot destination (Vision).
- **Accessibility:** Input labeled; responses and sources reachable; streaming handled per above.
- **Failure Handling:** Failed answer offers retry; prior conversation retained; never loses the research context.

# Uploads
- **Purpose / status:** ⚠️ **Not an MVP interaction — flagged.** No approved journey or IA element requires uploading files (BYOK is key entry, not a file; SEC filings are retrieved, not uploaded). This pattern is intentionally **not defined** for MVP to avoid inventing scope. If a future capability requires uploads, it enters via a governance Change Request.

# Downloads
- **Purpose:** Export research artifacts (J-06).
- **Behaviour:** Export produces a research artifact preserving reasoning and sources; progress shown; completion confirmed; the exported artifact is retained as a Saved Export.
- **Expected UX:** A dependable way to take research out, with its evidence intact.
- **Accessibility:** Export control labeled; progress and completion announced.
- **Failure Handling:** Failure/Timeout offers retry without losing the report (see [States](13_States.md)).

# Comparison
- **Purpose:** Assemble and evaluate companies side by side (J-03).
- **Behaviour:** Add/remove members drawn from Company Research; like-for-like by default; non-comparable data flagged; AI explains differences; the set can be preserved.
- **Expected UX:** A meaningful, honest comparison assembled without manual gathering.
- **Accessibility:** Table navigation with headers; add/remove keyboard operable; "not comparable" announced.
- **Failure Handling:** A member's failure doesn't break the comparison; empty set → Empty; needs ≥2 members to be meaningful.
