# AlphaScribe vNext — Responsive Behavior

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.1 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | CTO |
| **Last Updated** | 2026-07-21 |
| **Source of Truth** | For responsive behavior |

**Downstream Dependencies:** Accessibility · Frontend implementation · PRDs · QA Test Plans

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial responsive behavior specification across desktop, tablet, and mobile. |
| 0.1.1 | 2026-07-18 | Product & Design | 📝 Draft | Experiential alignment to the Design Constitution (v1.1): added the Responsive Experience Principle (behavior adapts, experience does not — the same premium, living, AI-native product at every size). Structure unchanged. |
| 0.1.1 | 2026-07-21 | CTO | 🧊 Frozen | CTO confirms Product Design approved and frozen (Governance Recovery Execution, Phase 0 evidence for GRA-006). No content change. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Design Constitution](00_Design_Constitution.md), [Navigation Structure](04_Navigation_Structure.md), [Screen Inventory](05_Screen_Inventory.md), [Wireframes](07_Wireframes.md), [Design System](08_Design_System.md), [Interaction Patterns](10_Interaction_Patterns.md) |
| **Used By** | [Accessibility](12_Accessibility.md), Frontend implementation, QA. |
| **Related Documents** | [Component Inventory](09_Component_Inventory.md), [States](13_States.md) |

> Responsive **behavior**, not visual design. The rule from
> [Navigation Structure](04_Navigation_Structure.md) holds throughout: **structure and
> destinations are constant across contexts; only presentation density adapts.** No
> destination exists in one context and not another.

---

# Responsive Experience Principle

Per the [Design Constitution](00_Design_Constitution.md), **behavior adapts; experience does
not.** AlphaScribe must feel like the *same premium, living product* on desktop, tablet, and
mobile — equally calm, responsive, crafted, and collaborative. Responsive design here is not
only about where regions go; it is about preserving the *feeling* across contexts:

- The product feels equally **alive and responsive** at every size — inputs acknowledged
  instantly, motion equally refined, nothing more sluggish or more static on smaller contexts.
- **AI remains an embedded partner** everywhere — thinking, streaming, and gathering evidence
  identically, never downgraded to a plainer "mobile" treatment.
- **Craftsmanship is constant** — spacing rhythm, depth, and interaction polish are preserved,
  only their density adapts.
- **Continuity is constant** — context and work are preserved across sizes; resuming on one
  device feels like the same workspace.

What changes across sizes is *presentation density and arrangement*; what never changes is the
premium, trustworthy, living experience.

---

# Breakpoint Principles

- **Content-first, mobile-up:** the research reading experience is primary at every
  size; larger contexts add concurrency, they don't add destinations.
- **Structure invariant:** the IA and Navigation structure are identical across
  contexts; adaptation changes density and disclosure, never the map.
- **Progressive disclosure by size:** smaller contexts prioritize the current task and
  condense (not remove) secondary movements.
- **Token-driven:** breakpoints are design tokens (`grid.*`) owned by the
  [Design System](08_Design_System.md); this document specifies behavior at three
  representative contexts — **Desktop**, **Tablet**, **Mobile** — not pixel values.
- **Touch and keyboard parity:** every context is fully operable by its primary input
  and by keyboard.

Facets per screen: **Layout Changes · Navigation Changes · Content Priority · Touch
Behaviour · Keyboard Behaviour · AI Behaviour.**

---

# Global Behavior (applies to all screens)

| Facet | Desktop | Tablet | Mobile |
|-------|---------|--------|--------|
| **Navigation Changes** | Full global navigation visible. | Global navigation condensed but complete. | Global navigation condensed to an accessible control; all destinations reachable. |
| **AI Behaviour** | Embedded AI (copilot/summary) visible alongside content. | AI beside or below content, still embedded. | AI embedded within the flow, reachable in context; never a separate chatbot. |
| **Touch** | Pointer-first; touch supported. | Touch-first targets. | Touch-first; adequate target sizing (tokens). |
| **Keyboard** | Full operability. | Full operability. | Full operability. |

Screens below note only where they differ from this global behavior.

---

# SCR-01 Landing / SCR-02 Authentication / SCR-03 Onboarding & AI Setup

- **Layout Changes:** Single-column, centered content at all sizes; density increases with width.
- **Navigation Changes:** Minimal/suppressed (pre-workspace); unchanged by size.
- **Content Priority:** Value/entry (SCR-01); form (SCR-02/03) always primary.
- **Touch:** Large, single primary action; comfortable field targets on mobile.
- **Keyboard:** Logical field order; Enter submits at all sizes.
- **AI Behaviour:** SCR-03 access validation identical across contexts; SCR-01/02 none.

# SCR-04 Workspace Home

- **Layout Changes:** Search prominent at all sizes; recent research reflows from multi-column (desktop) to single-column (mobile).
- **Navigation Changes:** Global nav condenses on smaller contexts.
- **Content Priority:** Search first; recent research second.
- **Touch:** Search and recent items are large touch targets on mobile.
- **Keyboard:** Focus lands on search; recent list navigable.
- **AI Behaviour:** None (routes onward).

# SCR-05 Search Results

- **Layout Changes:** Results list full-width on mobile; filters move from beside (desktop) to a condensed control (mobile).
- **Navigation Changes:** Global nav condensed on mobile.
- **Content Priority:** Query + results first; filters and recent searches secondary.
- **Touch:** Results are large tappable items; filter opens in a condensed surface.
- **Keyboard:** Results navigable/selectable; filter operable.
- **AI Behaviour:** None.

# SCR-06 Company Research (critical)

- **Layout Changes:** Desktop shows content with an embedded AI/source side panel concurrently. Tablet may place the AI panel beside or below content. Mobile stacks: content first, AI and sources reachable in-flow (e.g. a condensed embedded surface). Tables and charts scroll within their own region, never the page.
- **Navigation Changes:** Secondary (section) navigation stays available; condenses to a compact control on mobile without dropping sections.
- **Content Priority:** Overview/summary and key metrics first; statements/filings and deeper detail via progressive disclosure on smaller contexts.
- **Touch:** Section navigation, source links, and copilot entry are touch-sized; charts reveal values on tap.
- **Keyboard:** All sections, copilot, and source links keyboard reachable at every size.
- **AI Behaviour:** AI remains **embedded** at all sizes — beside content on desktop, in-flow on mobile — never relocated to a separate destination. Streaming behavior identical (see [Interaction Patterns](10_Interaction_Patterns.md)).

# SCR-07 Comparison

- **Layout Changes:** Comparison table shows more companies/metrics concurrently on desktop; on mobile it scrolls horizontally within its region and/or prioritizes the metric axis; AI difference explanation moves below the table on mobile.
- **Navigation Changes:** Global nav condensed on mobile.
- **Content Priority:** The comparison table first; AI explanation second.
- **Touch:** Add/remove company and horizontal table scroll are touch-friendly.
- **Keyboard:** Table and add/remove operable by keyboard at all sizes.
- **AI Behaviour:** Embedded difference explanation reachable in all contexts.

# SCR-08 Learning

- **Layout Changes:** Explanation is single-column reading at all sizes; company context reference condenses on mobile.
- **Navigation Changes:** Global nav condensed on mobile.
- **Content Priority:** Concept explanation first; related concepts/self-check second.
- **Touch:** Ask/explain and source/company links touch-sized.
- **Keyboard:** Concept, source, and company links reachable.
- **AI Behaviour:** Learning assistance embedded and identical across contexts.

# SCR-09 Research Library

- **Layout Changes:** Multi-group lists (sessions/reports/exports/history) sit side by side or sectioned on desktop; stack on mobile; filters condense.
- **Navigation Changes:** Global nav condensed on mobile.
- **Content Priority:** Sessions (with Resume Session) first; then reports, exports, history.
- **Touch:** List items and Resume Session are large touch targets.
- **Keyboard:** Lists and filters fully operable.
- **AI Behaviour:** None (routes back to research).

# SCR-10 Report View

- **Layout Changes:** Report is single-column linear reading at all sizes; source panel is beside (desktop) or inline/below (mobile); export always reachable.
- **Navigation Changes:** Global nav condensed on mobile.
- **Content Priority:** Conclusion → reasoning → detail → sources.
- **Touch:** Export and source links touch-sized.
- **Keyboard:** Linear navigation; export and sources reachable.
- **AI Behaviour:** Report content (AI-generated upstream) unchanged by size; sources reachable everywhere.

# SCR-11 Settings

- **Layout Changes:** Grouped settings in columns (desktop) → stacked sections (mobile).
- **Navigation Changes:** Global nav condensed on mobile.
- **Content Priority:** Account → AI access → session.
- **Touch:** Controls and re-validate/sign-out touch-sized.
- **Keyboard:** Grouped controls operable; save via keyboard.
- **AI Behaviour:** Access validation identical across contexts.
