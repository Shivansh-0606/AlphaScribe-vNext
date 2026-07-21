# AlphaScribe vNext — Component Inventory

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.1 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | CTO |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For the reusable component catalogue |

**Downstream Dependencies:** Interaction Patterns · Responsive Behavior · Accessibility ·
States · Frontend implementation · PRDs

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial Atomic-Design component catalogue for the MVP screens. |
| 0.1.1 | 2026-07-18 | Product & Design | 📝 Draft | Experiential alignment to the Design Constitution (v1.1): added an Experiential Contract (interaction, motion intent, loading, focus, transition, accessibility, AI behavior) required of every component. No new components or scope. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Design Constitution](00_Design_Constitution.md), [Design System](08_Design_System.md), [Wireframes](07_Wireframes.md), [Screen Inventory](05_Screen_Inventory.md), [UX Specifications](06_UX_Specifications.md) |
| **Used By** | [Interaction Patterns](10_Interaction_Patterns.md), [States](13_States.md), [Accessibility](12_Accessibility.md), Frontend implementation. |
| **Related Documents** | [Navigation Structure](04_Navigation_Structure.md), [Responsive Behavior](11_Responsive_Behavior.md) |

> Components are described by **role and behavior**, using the naming rule and tokens
> from the [Design System](08_Design_System.md). This is a catalogue, not code. No
> component introduces product capability beyond the frozen baseline; component
> *States* reference [States](13_States.md) rather than redefining them.

---

# Introduction

Components are organized with **Atomic Design**: Atoms → Molecules → Organisms →
Templates. Each entry lists Purpose, Variants, Properties, States, Accessibility,
Screens Used, Dependencies, and Usage Rules. "Screens Used" references
[Screen Inventory](05_Screen_Inventory.md) IDs. Component *State* names reference the
canonical [States](13_States.md) catalogue.

## Experiential Contract (applies to every component)

Per the [Design Constitution](00_Design_Constitution.md), every component must feel crafted
and alive, not merely functional. These **experiential expectations** are required of each
component in addition to its listed attributes — stated once here to avoid repetition, and
enforceable in review:

- **Interaction behavior:** acknowledges the user immediately and proportionately (an alive,
  responsive feel — §6, §19); the same acknowledgment vocabulary across components.
- **Motion intent:** any motion communicates, guides, or reassures, is subtle and refined,
  and never distracts (§14); motion that is removable without losing meaning is not added.
- **Loading behavior:** loading feels *alive and productive* — skeletons/progress scoped to
  the component, never an inert blank (§19; [States](13_States.md)).
- **Focus behavior:** a clear, calm, visible focus state; predictable focus on interaction
  ([Accessibility](12_Accessibility.md)).
- **Transition expectations:** state changes are continuous and legible, preserving context
  (§14) — nothing snaps jarringly.
- **Accessibility expectations:** meets the WCAG AA contract in [Accessibility](12_Accessibility.md).
- **AI behavior (where applicable):** AI-bearing components (`CopilotPanel`, `AISummary`,
  `FilingViewer`) read as a partner *thinking and gathering evidence*, streaming naturally
  with sources attaching — never a generic spinner (§9).

Individual entries below note only where a component's experiential behavior is distinctive;
this contract is otherwise assumed.

---

# Atoms

## Button
- **Purpose:** Trigger an action.
- **Variants:** Primary, Secondary, Quiet/Text, Destructive.
- **Properties:** label, icon (optional), disabled, loading, size.
- **States:** Default, Hover, Focus, Active, Disabled, Loading.
- **Accessibility:** Accessible name always present; focus-visible; operable by keyboard; icon-only buttons carry a label.
- **Screens Used:** All.
- **Dependencies:** `color.*`, `type.*`, `radius.*`, `icon.*`.
- **Usage Rules:** One Primary per view context; Destructive only for irreversible actions.

## Input
- **Purpose:** Capture a single value.
- **Variants:** Text, Password (masked), Search.
- **Properties:** label, value, placeholder, disabled, invalid, help text.
- **States:** Default, Focus, Filled, Invalid, Disabled.
- **Accessibility:** Programmatic label; error text associated; masked values never announced back.
- **Screens Used:** SCR-02, SCR-03, SCR-04, SCR-05, SCR-11.
- **Dependencies:** `color.*`, `type.*`, `space.*`, `radius.*`.
- **Usage Rules:** Always labeled; validation shown inline (see Interaction Patterns → Forms).

## Label / Text
- **Purpose:** Present textual content and metadata.
- **Variants:** Heading (1–3), Body, Caption, Mono.
- **Properties:** role/level, emphasis.
- **States:** Static.
- **Accessibility:** Sequential heading order; sufficient contrast.
- **Screens Used:** All.
- **Dependencies:** `type.*`, `color.ink*`.
- **Usage Rules:** Headings follow document order; captions for metadata/sources.

## Icon
- **Purpose:** Reinforce meaning of an action or item.
- **Variants:** By meaning (source, export, compare, AI, search, etc.).
- **Properties:** name, size.
- **States:** Static (inherits interactive state from parent).
- **Accessibility:** Decorative icons hidden from assistive tech; meaningful icons labeled.
- **Screens Used:** All.
- **Dependencies:** `icon.*`, `color.*`.
- **Usage Rules:** Never the sole carrier of a critical label.

## Badge / Tag
- **Purpose:** Convey a small status or category (e.g. document status, "not comparable").
- **Variants:** Neutral, Bullish, Bearish, Warning.
- **Properties:** label, tone.
- **States:** Static.
- **Accessibility:** Meaning conveyed by text, not color alone.
- **Screens Used:** SCR-06, SCR-07, SCR-09.
- **Dependencies:** `color.*`, `type.caption`.
- **Usage Rules:** Bullish/Bearish only for genuine financial meaning.

## Link
- **Purpose:** Navigate or reveal a source.
- **Variants:** Inline, Standalone, Source link.
- **Properties:** label, destination/target context.
- **States:** Default, Hover, Focus, Visited.
- **Accessibility:** Descriptive text (never "click here"); focusable.
- **Screens Used:** All.
- **Dependencies:** `color.*`, `type.*`.
- **Usage Rules:** Source links always describe what they point to.

## Spinner / Progress
- **Purpose:** Indicate ongoing work.
- **Variants:** Indeterminate, Determinate.
- **Properties:** context/label.
- **States:** Active.
- **Accessibility:** Announced as busy; not the only signal of progress for long waits.
- **Screens Used:** All (per Loading/Timeout states).
- **Dependencies:** `motion.*`, `color.*`.
- **Usage Rules:** Pair with skeleton for content regions (see States).

---

# Molecules

## SearchField
- **Purpose:** Enter and submit a search intent.
- **Variants:** Global, Company.
- **Properties:** query, suggestions (recent), on-submit context.
- **States:** Default, Focus, Loading, No Results.
- **Accessibility:** Labeled; results/count announced; keyboard submit.
- **Screens Used:** SCR-04, SCR-05 (shared global header).
- **Dependencies:** Input, Button, Icon.
- **Usage Rules:** Primary focus target on Workspace Home.

## FormField
- **Purpose:** Labeled input with validation messaging.
- **Variants:** Text, Password, Choice.
- **Properties:** label, input, help, error.
- **States:** Default, Invalid, Disabled.
- **Accessibility:** Label + error programmatically linked; focus to first error.
- **Screens Used:** SCR-02, SCR-03, SCR-11.
- **Dependencies:** Input, Label.
- **Usage Rules:** Validation inline; see Interaction Patterns → Forms.

## MetricStat
- **Purpose:** Present a financial metric with its meaning.
- **Variants:** Neutral, Bullish, Bearish.
- **Properties:** name, value, meaning/explanation, source ref.
- **States:** Default, Empty (no data), Loading (skeleton).
- **Accessibility:** Value and meaning read together; tone not color-only.
- **Screens Used:** SCR-06, SCR-07.
- **Dependencies:** Label, Badge, SourceReference.
- **Usage Rules:** Never a number without its meaning (Design System: explain before quantify).

## SourceReference
- **Purpose:** Link an insight to its underlying evidence (Trusted AI).
- **Variants:** Inline citation, Source list item.
- **Properties:** source label, target.
- **States:** Default, Focus, Unavailable (flagged).
- **Accessibility:** Descriptive, focusable; unavailable state announced.
- **Screens Used:** SCR-06, SCR-08, SCR-10.
- **Dependencies:** Link, Icon.
- **Usage Rules:** Present wherever an AI insight appears; never omitted.

## ListItem
- **Purpose:** A selectable entry in a list (recent research, results, library items).
- **Variants:** Company, Research Session (with Resume Session), Report, Export, History.
- **Properties:** title, subtitle/date, primary action.
- **States:** Default, Hover, Focus, Selected.
- **Accessibility:** Full item focusable; labeled with subject and date.
- **Screens Used:** SCR-04, SCR-05, SCR-09.
- **Dependencies:** Label, Button, Badge.
- **Usage Rules:** Session items expose **Resume Session**.

## Tab / SectionNav
- **Purpose:** Secondary navigation across content levels within a domain.
- **Variants:** Company sections (Overview/Financials/Filings/AI Insights/Export).
- **Properties:** items, active item.
- **States:** Default, Active, Focus.
- **Accessibility:** Exposed as a navigation set; active item indicated non-color-only; keyboard operable.
- **Screens Used:** SCR-06.
- **Dependencies:** Link/Button, Label.
- **Usage Rules:** Reflects IA content levels only; introduces no new destination.

## Notification / Toast
- **Purpose:** Communicate transient outcomes (success, error, info).
- **Variants:** Success, Error, Info, Warning.
- **Properties:** message, tone, optional action.
- **States:** Enter, Visible, Dismiss.
- **Accessibility:** Announced politely/assertively per severity; dismissible; not motion-only.
- **Screens Used:** All.
- **Dependencies:** Icon, Button.
- **Usage Rules:** For outcomes, not for critical blocking errors (use Error state).

## Tooltip
- **Purpose:** Reveal supplementary explanation on demand.
- **Variants:** Text, Definition (for learner terms).
- **Properties:** trigger, content.
- **States:** Hidden, Visible.
- **Accessibility:** Keyboard/focus reachable; not the only place for essential info.
- **Screens Used:** SCR-06, SCR-07, SCR-08.
- **Dependencies:** Label.
- **Usage Rules:** Supplementary only; never hides critical content.

---

# Organisms

## GlobalHeader
- **Purpose:** Persistent identity, global search, and account access.
- **Variants:** Public (pre-auth), Authenticated.
- **Properties:** brand, search, account menu.
- **States:** Default.
- **Accessibility:** Landmark region; consistent across screens.
- **Screens Used:** All.
- **Dependencies:** SearchField, Button, Icon, Link.
- **Usage Rules:** Identical placement/behavior everywhere (Navigation Structure).

## GlobalNavigation
- **Purpose:** Persistent movement between top-level domains.
- **Variants:** Full (desktop), Condensed (tablet/mobile).
- **Properties:** destinations, current location.
- **States:** Default, Current, Focus.
- **Accessibility:** Navigation landmark; current location exposed; keyboard operable.
- **Screens Used:** All authenticated (SCR-04…SCR-11).
- **Dependencies:** Link, Icon, Label.
- **Usage Rules:** Destinations exactly match Global Navigation; no new destinations.

## CopilotPanel
- **Purpose:** Embedded, contextual AI question-and-answer anchored to the current subject.
- **Variants:** Company context, Comparison context, Learning context.
- **Properties:** context (company/comparison/concept), conversation region, source links.
- **States:** Idle, AI Thinking, AI Streaming, Error.
- **Accessibility:** Streaming output announced considerately; sources reachable; keyboard operable.
- **Screens Used:** SCR-06, SCR-07, SCR-08.
- **Dependencies:** SourceReference, Notification, Button, Label.
- **Usage Rules:** Embedded only (never a standalone chatbot); every answer sourced.

## AISummary
- **Purpose:** Present a grounded, plain-language summary at the top of company insights.
- **Variants:** Company summary.
- **Properties:** summary content, source refs.
- **States:** AI Thinking, AI Streaming, Loaded, Error.
- **Accessibility:** Readable linearly; sources reachable.
- **Screens Used:** SCR-06.
- **Dependencies:** SourceReference, Label.
- **Usage Rules:** Precedes figures; never presented without sources.

## StatementTable
- **Purpose:** Present financial statements as accessible tabular data.
- **Variants:** Income, Balance, Cash Flow; annual/quarterly.
- **Properties:** rows, periods, values.
- **States:** Default, Loading (skeleton), Empty, Partial Failure.
- **Accessibility:** Proper headers, row/column navigation, scope; not color-only.
- **Screens Used:** SCR-06.
- **Dependencies:** Label, MetricStat, Badge.
- **Usage Rules:** Raw data follows summary/metrics in the hierarchy.

## ComparisonTable
- **Purpose:** Present companies side by side on comparable terms.
- **Variants:** Metric comparison.
- **Properties:** companies, metrics, comparability flags.
- **States:** Default, Empty (no members), Partial Failure (not comparable), Loading.
- **Accessibility:** Header-anchored navigation; "not comparable" announced.
- **Screens Used:** SCR-07.
- **Dependencies:** MetricStat, Badge, Button (add/remove), SourceReference.
- **Usage Rules:** Members come from Company Research (derived domain); flags gaps rather than hiding them.

## FilingViewer
- **Purpose:** Present SEC filings and their grounded AI analysis.
- **Variants:** Filing content, Filing analysis.
- **Properties:** filing sections, analysis, source anchors.
- **States:** Default, Loading, Empty (uncovered), Error, AI Thinking/Streaming.
- **Accessibility:** Navigable sections; analysis linked to source anchors.
- **Screens Used:** SCR-06, SCR-08.
- **Dependencies:** AISummary/CopilotPanel, SourceReference, Label.
- **Usage Rules:** Analysis always anchored to the filing (source traceability).

## ChartFigure
- **Purpose:** Visualize financial data.
- **Variants:** Revenue, Profit, Margin, Growth, Ratio.
- **Properties:** series, periods, labels.
- **States:** Default, Loading, Empty, Partial Failure.
- **Accessibility:** Accessible text/table equivalent; not color-only; described in [Accessibility](12_Accessibility.md).
- **Screens Used:** SCR-06, SCR-07.
- **Dependencies:** Label, tokens.
- **Usage Rules:** Always paired with an accessible data equivalent.

## LibraryList
- **Purpose:** Browse durable research (sessions, reports, exports, history).
- **Variants:** Sessions, Reports, Saved Exports, History.
- **Properties:** items, filters.
- **States:** Default, Empty, No Results, Loading, Error.
- **Accessibility:** Labeled list; filters operable; items focusable.
- **Screens Used:** SCR-09.
- **Dependencies:** ListItem, Input (filter), Button.
- **Usage Rules:** Session items expose Resume Session.

## ReportDocument
- **Purpose:** Present a grounded, source-backed report with export.
- **Variants:** Report view.
- **Properties:** conclusion, reasoning, content, sources, export action.
- **States:** Default, Loading, Error, Success (export), Timeout.
- **Accessibility:** Linear reading order; sources reachable; export announced.
- **Screens Used:** SCR-10.
- **Dependencies:** SourceReference, Button, Label.
- **Usage Rules:** Export preserves reasoning and sources (J-06).

## AIAccessSelector
- **Purpose:** Choose and validate AI access (BYOK / Managed AI).
- **Variants:** Onboarding, Settings.
- **Properties:** options, key entry (conditional), validation status.
- **States:** Default, Validating, Valid, Invalid, Error.
- **Accessibility:** Options grouped; status announced; key never spoken back.
- **Screens Used:** SCR-03, SCR-11.
- **Dependencies:** FormField, Button, Notification.
- **Usage Rules:** Managed AI is the frictionless default; continue enabled only on valid access.

---

# Templates

Templates define region composition (from [Wireframes](07_Wireframes.md)); they hold
no data and introduce no new regions.

| Template | Composition | Screens |
|----------|-------------|---------|
| **PublicTemplate** | GlobalHeader (public) · Main · Footer. | SCR-01, SCR-02 |
| **SetupTemplate** | GlobalHeader · Main (setup) · Footer; global nav suppressed. | SCR-03 |
| **WorkspaceTemplate** | GlobalHeader · GlobalNavigation · Main · Footer. | SCR-04, SCR-05, SCR-09, SCR-11 |
| **ResearchTemplate** | WorkspaceTemplate + SectionNav + embedded AI side panel. | SCR-06, SCR-07, SCR-08 |
| **DocumentTemplate** | WorkspaceTemplate + linear document + source panel + export. | SCR-10 |

---

# Component → Screen Coverage

| Screen | Key organisms/molecules |
|--------|-------------------------|
| SCR-01 | GlobalHeader, Button, Label |
| SCR-02 | FormField, Button, Notification |
| SCR-03 | AIAccessSelector, FormField, Notification |
| SCR-04 | GlobalHeader, SearchField, ListItem (recent) |
| SCR-05 | SearchField, ListItem, Badge |
| SCR-06 | Tab/SectionNav, AISummary, CopilotPanel, MetricStat, StatementTable, FilingViewer, ChartFigure, SourceReference |
| SCR-07 | ComparisonTable, CopilotPanel, MetricStat, Badge |
| SCR-08 | CopilotPanel, SourceReference, Tooltip (definitions) |
| SCR-09 | LibraryList, ListItem, Input (filter) |
| SCR-10 | ReportDocument, SourceReference, Button (export) |
| SCR-11 | AIAccessSelector, FormField, Button |
