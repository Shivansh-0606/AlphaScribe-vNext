# AlphaScribe vNext — Accessibility Specification

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Version** | 0.1.1 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | _Pending_ |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For accessibility requirements (pending approval) |

**Downstream Dependencies:** Frontend implementation · QA Test Plans · PRDs · Acceptance Criteria

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial WCAG 2.1 AA accessibility specification for the MVP. |
| 0.1.1 | 2026-07-18 | Product & Design | 📝 Draft | Experiential alignment to the Design Constitution (v1.1): added the "experience never at the cost of accessibility" principle governing liveness, motion, spatial depth, and AI streaming. Requirements unchanged. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Design Constitution](00_Design_Constitution.md), [Navigation Structure](04_Navigation_Structure.md), [Screen Inventory](05_Screen_Inventory.md), [Design System](08_Design_System.md), [Component Inventory](09_Component_Inventory.md), [Interaction Patterns](10_Interaction_Patterns.md), [Responsive Behavior](11_Responsive_Behavior.md) |
| **Used By** | [States](13_States.md), Frontend implementation, QA Test Plans, Acceptance Criteria. |
| **Related Documents** | [User Personas](01_User_Personas.md), [UX Specifications](06_UX_Specifications.md) |

> Accessibility is a **structural requirement**, established as a principle in the
> Navigation Structure and Design System and consolidated here. Requirements are
> behavior/standard-level, not implementation. **Target: WCAG 2.1 AA.**

---

# Introduction

This specification consolidates the accessibility requirements distributed across the
design blueprint into one authoritative reference. It applies to every screen
([Screen Inventory](05_Screen_Inventory.md)), component
([Component Inventory](09_Component_Inventory.md)), interaction
([Interaction Patterns](10_Interaction_Patterns.md)), and state
([States](13_States.md)). The conformance target is **WCAG 2.1 Level AA**; individual
docs reference this one rather than restating rules.

---

# Global Standard

- **Target:** WCAG 2.1 AA for all MVP screens and states.
- **Input independence:** every action is operable by pointer, touch, and keyboard.
- **No information by color alone:** meaning (including financial bullish/bearish and
  "not comparable") is always carried by text or shape as well as color.
- **Respect user preferences:** reduced motion and OS/browser text settings are honored.

> **Experience never at the cost of accessibility.** The [Design Constitution](00_Design_Constitution.md)
> raises the experiential bar — alive, spatial, motion-rich, streaming AI — but accessibility
> is an *immutable law* (§17, §25), not a trade-off. Every experiential enhancement must
> satisfy the requirements below: liveness and depth must never rely on motion or color alone,
> AI streaming must be announced considerately without stealing focus, spatial depth must
> preserve contrast, and every "premium" interaction must be fully keyboard operable. Where
> experience and accessibility appear to conflict, accessibility wins.

---

# Keyboard Navigation

- Every interactive element and every navigational movement (global, secondary,
  contextual, Resume Session) is fully keyboard operable — no pointer-only paths.
- A logical tab order matches the reading order and the information hierarchy from the
  [Information Architecture](03_Information_Architecture.md).
- Standard keys behave conventionally: Enter/Space activate; Escape closes overlays;
  arrow keys move within composite widgets (tables, section navigation, lists).
- A "skip to main content" path is available so keyboard users can bypass persistent
  navigation.
- No keyboard traps; focus can always move out of any region (dialogs/modals return
  focus on close).

# Focus Management

- A visible focus indicator (`color.focus`) is present on every focusable element and
  meets contrast requirements.
- On navigation between screens/contexts, focus moves predictably to a sensible target
  (e.g. main heading or primary action), never lost to the page body.
- On validation error, focus moves to the first error (Forms pattern).
- Overlays (dialogs, modals, drawers) trap focus while open and restore focus to the
  triggering element on close.
- Streaming AI updates do not steal focus from the user's current task.

# Screen Readers

- All content and controls are exposed with correct roles, names, and states.
- Landmarks identify Header, Global Navigation, Main, and Footer regions.
- Headings are sequential and descriptive, reflecting the content hierarchy.
- Dynamic changes (results loaded, state transitions, notifications, AI streaming
  completion) are announced via appropriate live regions with suitable politeness.
- Icon-only controls and source links have descriptive accessible names.

# ARIA Expectations

- Prefer native semantics; use ARIA only to fill genuine gaps (ARIA is a supplement,
  not a substitute for correct structure).
- Composite widgets (tables, section/secondary navigation, comparison table, library
  lists) expose correct roles and relationships (e.g. header/scope associations).
- Current location in navigation is programmatically indicated.
- Live regions are used for asynchronous updates (search results, AI streaming, state
  changes) with politeness matched to urgency (polite for progress, assertive for
  blocking errors).
- Form fields expose label, description, invalid state, and error association.

# Contrast

- Text and meaningful non-text elements meet WCAG AA contrast against
  `color.canvas`/`color.surface` (normal text ≥ 4.5:1; large text and essential UI
  elements/graphics ≥ 3:1).
- Focus indicators, financial signal colors (`bullish`/`bearish`), and status tones
  meet contrast and are never the sole signal.
- The single light theme's token pairings are validated for contrast in the
  [Design System](08_Design_System.md).

# Forms

- Every field has a persistent, programmatically associated label.
- Errors are specific, adjacent, text-based, and associated with their field; focus
  moves to the first error on failure.
- Required and invalid states are conveyed non-visually as well as visually.
- Sensitive values (passwords, BYOK keys) are never announced back.
- Applies to SCR-02 (Authentication), SCR-03 (Onboarding & AI Setup), SCR-11 (Settings).

# Charts

- Every chart (`ChartFigure`) has an accessible equivalent: an associated data table or
  text summary conveying the same information.
- Trends and values are not conveyed by color alone; series are distinguishable by
  label/pattern.
- Interactive value reveal is keyboard operable.
- Applies to SCR-06, SCR-07.

# Tables

- Financial statement and comparison tables (`StatementTable`, `ComparisonTable`) use
  proper header cells and scope so relationships are clear to assistive tech.
- Row/column navigation is supported; header context is available while navigating.
- Missing or non-comparable cells are announced explicitly (not blank-by-implication).
- Wide tables scroll within their own region without breaking page navigation.

# AI Responses

- AI summaries, copilot answers, filing analysis, and learning explanations are
  presented as linear, readable text with correct reading order.
- Streaming output is announced considerately — progress and completion are signaled
  without character-by-character noise or focus theft (AI Streaming pattern).
- Every AI insight's **source path** (`SourceReference`) is keyboard reachable and
  descriptively labeled — accessibility of source traceability is mandatory, not
  optional (Trusted AI).
- AI thinking/waiting is announced as a busy state (see [States](13_States.md)).

# Motion Reduction

- All motion (`motion.*`, transitions, streaming animation) respects the user's
  reduced-motion preference; when reduced, motion is minimized or replaced with
  instant state change.
- No essential information is conveyed only through motion.
- Nothing flashes in a way that risks seizure (within WCAG thresholds).

# Error Messaging

- Errors are specific, human, and recoverable; they state what happened and the next
  step, and never blame the user (consistent with [UX Specifications](06_UX_Specifications.md)).
- Errors are conveyed by text (not color/icon alone) and associated with the relevant
  region or field.
- Blocking errors are announced assertively; transient issues politely.
- Aligns with the Error, Partial Failure, and Timeout definitions in [States](13_States.md).

# Responsive Accessibility

- Accessibility is preserved identically across Desktop, Tablet, and Mobile — no
  destination or control loses operability at any size
  ([Responsive Behavior](11_Responsive_Behavior.md)).
- Touch targets meet minimum sizing; spacing prevents mis-taps.
- Condensed navigation on smaller contexts remains fully keyboard and screen-reader
  operable, exposing the same destinations.
- Orientation is not locked; content reflows without loss of information or function.

---

# Accessibility Acceptance Checklist

| Requirement | Applies to |
|-------------|-----------|
| Full keyboard operability, logical order, skip link, no traps | All screens |
| Visible focus + predictable focus management | All screens |
| Correct roles/names/states; landmarks; sequential headings | All screens |
| Live-region announcements for async changes & AI streaming | SCR-05, SCR-06, SCR-07, SCR-08 |
| WCAG AA contrast; no meaning by color alone | All screens |
| Form labels/errors associated; secrets never echoed | SCR-02, SCR-03, SCR-11 |
| Chart accessible equivalents | SCR-06, SCR-07 |
| Table headers/scope; non-comparable announced | SCR-06, SCR-07 |
| Source paths keyboard-reachable & labeled | SCR-06, SCR-08, SCR-10 |
| Reduced-motion honored | All screens |
| Responsive parity of accessibility | All screens |
