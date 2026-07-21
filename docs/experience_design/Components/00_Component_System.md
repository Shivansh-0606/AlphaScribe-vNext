# AlphaScribe vNext — Component System Foundation

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.0 |
| **Milestone** | M2 — Production Design System |
| **Phase** | Phase 2 — Core Component Design |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For the production component library contract |

**Governing input:** Direction **C — "The Study"** (Phase 1). *"A well-set page on a living desk: content is an editorial reading core on flat paper; elevation, motion, and the AI companion are summoned only when they carry meaning, then recede."*

---

## Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On (frozen)** | [Component Inventory](../../design/09_Component_Inventory.md) · [States](../../design/13_States.md) · [Interaction Patterns](../../design/10_Interaction_Patterns.md) · [Accessibility](../../design/12_Accessibility.md) · [Design Tokens](../10_Design_Tokens.md) · [Design System](../../design/08_Design_System.md) · [Design Constitution](../../design/00_Design_Constitution.md) |
| **Governed input** | [Creative Exploration → Direction C](../Creative_Exploration/00_Creative_Exploration.md) |
| **Used By** | Every component family spec in this folder · Phase 3 Layouts · Phase 4 Screens |

> **This document states, once, everything true of *every* component** — the universal
> contract, the shared state model, sizes, tokens, motion, accessibility, responsive rules,
> naming, and the per-component documentation template. Family specs (`01_*`…`09_*`) then
> document only what is **distinctive** to each component, inheriting this contract. This is
> deliberate DRY: it keeps 55 specs consistent and prevents drift (Constitution §7.5).

---

## 1. Component Philosophy (Direction C applied)

Every AlphaScribe component obeys five rules derived from the selected direction and the
Constitution. A component that breaks any of these is rejected in review.

1. **Calm at rest, alive on interaction.** The default state is quiet and flat (paper). Life —
   elevation, motion, the signal color — appears *in response to the user or the AI*, then
   recedes. Nothing animates or lifts for decoration. (Constitution §5–6, §14; Laws 16–17.)
2. **Depth is a verb, not a texture.** Surfaces sit flat on the canvas until a reason to
   elevate exists (focus, transient overlay, active AI). Elevation is spent from
   [`--elevation-*`](../10_Design_Tokens.md#7-elevation-tokens), never invented. (§12.)
3. **One signal, spent sparingly.** The emerald→teal signal marks only: the primary action,
   AI presence/verified/evidence, and focus. Everywhere else is ink + paper. (Color §Anti-patterns.)
4. **Type and space carry hierarchy; color carries meaning.** Rank comes from the type scale
   and spacing rhythm; color is reserved for genuine signal. (Typography §Usage; §11.)
5. **Evidence is always reachable.** Any component surfacing an AI-derived or financial claim
   exposes a keyboard-reachable path to its source. (Law 3; §7.3, §22.)

---

## 2. Universal Component Contract (the "Experiential Contract")

Inherited from [Component Inventory §Experiential Contract](../../design/09_Component_Inventory.md).
Assumed of every component; family specs note only distinctive behavior.

| Facet | The contract every component meets |
|-------|-------------------------------------|
| **Interaction** | Acknowledges input immediately and proportionately, using the shared state vocabulary (§4). The same gesture yields the same response everywhere. |
| **Motion** | Any motion communicates, guides, or reassures; subtle, brief, removable without losing meaning; honors reduced-motion (§7). |
| **Loading** | Loading is scoped to the component and feels productive — skeleton or progress, never an inert blank (§6, [States](../../design/13_States.md)). |
| **Focus** | A visible, calm focus ring (`--focus-ring-*`) on every interactive element; focus is styled, never removed; predictable focus on open/close/error (§6). |
| **Transition** | State changes are continuous and legible; context is preserved; nothing snaps jarringly (§7). |
| **Accessibility** | Meets the WCAG 2.1 AA contract in [Accessibility](../../design/12_Accessibility.md): keyboard-operable, correct role/name/state, AA contrast, no meaning by color alone. |
| **AI behavior** | AI-bearing components read as a partner *thinking and gathering evidence*, streaming at a human pace with sources attaching — never a generic spinner (§9). |
| **Work preservation** | No component action discards in-progress or saved work without explicit, confirmed intent (Law 6; §7.4). |

---

## 3. Sizing System

A single sizing ladder, shared across interactive components so density stays consistent.
Heights are composed from spacing tokens; never hardcoded.

| Size | Control height | Padding (inline) | Text role | Primary use |
|------|----------------|------------------|-----------|-------------|
| `sm` | 28px | `--space-2` (8) | `type.small` (14) | Dense tables, inline actions, toolbars |
| `md` **(default)** | 36px | `--space-3` (12) | `type.small`/`body` | Default for all forms and actions |
| `lg` | 44px | `--space-4` (16) | `type.body` (16) | Primary CTAs, touch-primary contexts, empty-state actions |

- **Touch:** on touch contexts, the *effective* target is ≥ 44×44px regardless of visual size
  (hit-area padding), per [Accessibility](../../design/12_Accessibility.md) and Constitution §18.
- **Icon-only controls** follow the same ladder as square dimensions (28/36/44).
- Radius per size comes from [Shape](../07_Shape_Radius_System.md): `--radius-md` (4) default;
  the system is sharp/structural — no pill except intentional `--radius-pill` chips/avatars.

---

## 4. Universal State Model

Every interactive component expresses states from this canonical set (names reference the frozen
[States](../../design/13_States.md) catalogue). Family specs list only states that differ or add.

| State | Trigger | Standard expression (tokens) |
|-------|---------|------------------------------|
| **Default** | Rest | Flat on canvas/surface; no elevation, no signal. |
| **Hover** | Pointer over (pointer devices only) | `--state-hover-surface` fill or `--state-hover-emphasis`; `--motion-duration-fast`. Never reveals *essential* info on hover alone. |
| **Focus (focus-visible)** | Keyboard/programmatic focus | `--focus-ring-color` 2px + 2px offset; always visible; identical everywhere. |
| **Active/Pressed** | Pointer/key down | `--state-active`; brief, proportionate acknowledgment. |
| **Selected** | Chosen in a set | `--state-selected` (accent tint) **+** a non-color cue (check, weight, indicator). |
| **Disabled** | Not currently available | `--opacity-disabled` (0.45) **+** removed affordance + `aria-disabled`; never opacity alone; explains why when non-obvious. |
| **Loading** | Async work pending | Scoped skeleton/progress; control shows in-place busy, stays in layout (no reflow). |
| **Invalid** | Failed validation | `--destructive` border + associated text message (never color alone); focus moves to first error. |
| **Empty** | No content yet | Explains the emptiness + offers a first step (Law 13; §20). |
| **Error** | Operation failed | Specific, non-blaming text + recovery action; preserves work. |
| **Success** | Operation completed | Brief, quiet confirmation; then let the user continue (§20). |
| **AI Thinking** | AI considering (AI components) | Visible "thinking" presence, not a spinner; calm, embedded (§9). |
| **AI Streaming** | AI producing output | Output emerges at readable pace; sources attach as content resolves. |

> **No state may trap the user or lose work** (Law 13). Every non-happy state offers a way forward.

---

## 5. Token Usage Rules

- **Tokens or nothing.** Every visual value references a token from [Design Tokens](../10_Design_Tokens.md).
  A raw hex/px/ms/z-index in a spec or in code is a defect.
- **Color:** surfaces from `--background`/`--surface`; text `--foreground`/`--muted-foreground`;
  the signal only via `--brand-from`/`--brand-to`/`--ring`; financial meaning via
  `bullish`/`bearish`/`warning`/`--destructive` (always with a non-color cue).
- **Space:** the 4/8 ladder (`--space-*`) for all padding, gaps, and rhythm.
- **Type:** semantic roles (`type.h1`…`type.label`/`type.figure`) — never raw sizes.
- **Radius/Border/Elevation/Shadow/Z/Motion/Focus/State:** the named token families only.
- **New value needed?** Add a token to its owning foundation doc (reviewed) — never a local literal.

---

## 6. Responsive Behavior (shared rules)

Per [Responsive Behavior](../../design/11_Responsive_Behavior.md) and Constitution §18. Breakpoints:
`--bp-mobile` · `--bp-tablet` · `--bp-desktop` · `--bp-wide`; grid columns 4 / 8 / 12.

- **Identity is constant.** Paper, ink, signal, type, rhythm never change by size — only density
  and arrangement adapt (Visual Language §Responsive).
- **Interaction adapts to input, not capability.** Touch gets larger targets and tap-to-open in
  place of hover; nothing becomes *unavailable* at any size.
- **Navigation parity.** Every destination exists at every size; only presentation density
  adapts (§18; no hidden-navigation anti-pattern).
- **Overlays adapt:** popovers/menus may become bottom sheets on mobile; dialogs may go full-screen;
  the drawer may become a full-width sheet. Documented per family.
- **Reading measure preserved:** content respects `--reading-max` at every size.

---

## 7. Motion (shared rules)

Governed by Constitution §14 and [Motion tokens](../10_Design_Tokens.md#11-motion-tokens).
Family specs list only a component's *signature* motion.

| Motion moment | Token | Rule |
|---------------|-------|------|
| Micro-feedback (hover/press) | `--motion-duration-fast` (120ms), `--motion-ease-standard` | Confirms input; never draws attention to itself. |
| State transition | `--motion-duration-base` (150ms), `--motion-ease-standard` | Loading→loaded, closed→open; continuous, legible. |
| Reveal / elevation change | `--motion-duration-slow` (240ms), `--motion-ease-out` | Overlays, progressive reveal, surfaces lifting. |
| AI streaming | `--motion-duration-stream` (contextual) | Human, readable pace; the "alive" signature. |
| **Reduced motion** | `--motion-duration-instant` (0ms) | All of the above collapse to instant state changes with **no information loss**. |

**Rule:** if a motion can be removed without losing meaning, it should not be added. Motion exists
to communicate continuity, feedback, hierarchy, or AI liveness — nothing else (§14).

---

## 8. Accessibility (shared baseline)

Every component inherits the full [Accessibility](../../design/12_Accessibility.md) contract. The
non-negotiable baseline, assumed everywhere:

- **Keyboard:** fully operable; logical focus order matching reading order; no keyboard traps;
  documented key bindings per family (e.g. Tab/Arrow/Enter/Esc).
- **Semantics:** correct native element or role; accessible name always present; state
  (`aria-pressed`, `aria-expanded`, `aria-selected`, `aria-disabled`, `aria-invalid`) exposed.
- **Contrast:** text ≥ 4.5:1 (≥ 3:1 large/UI); focus ring AA-contrast; verified against tokens.
- **No color-only meaning:** every color-coded state carries text, icon, or shape reinforcement.
- **Announcements:** dynamic changes (loading, errors, toasts, AI streaming) announced at the
  correct politeness; streaming announced considerately, not per-character.
- **Reduced motion / zoom:** honored; layout reflows to 200% zoom without clipping.

---

## 9. Naming Conventions

- **Component names** use the frozen [Component Inventory](../../design/09_Component_Inventory.md)
  role names where one exists (e.g. `SearchField`, `MetricStat`, `SourceReference`, `CopilotPanel`).
  Generic primitives not named there (Popover, Drawer, Breadcrumbs, Pagination, Segmented Control,
  Avatar, Switch) use conventional names and are containers/controls, **not new product capability**.
- **Figma layer/variant naming** (Phase 5 contract, previewed here for consistency):
  `Component / Variant=… , Size=… , State=…` (e.g. `Button / Variant=Primary, Size=md, State=Hover`).
- **Tokens** follow `--<domain>-<role>[-<variant>]` (Design Tokens §Naming).
- **No synonyms for frozen product vocabulary** — use *Company Research, Research Session, Resume
  Session, Trusted AI* verbatim (§15).

---

## 10. Per-Component Documentation Template

Every component in every family spec is documented with exactly these headings, in order (the
attribute set the M2 brief requires). Where a facet is fully covered by this foundation doc, the
family spec writes *"Per foundation §X"* rather than repeating it.

```
### <ComponentName>   ⟶ maps to: <frozen Inventory role, if any>
- Purpose
- Anatomy            (parts, in composition order)
- Variants           (the meaningful kinds)
- Sizes              (from the §3 ladder, or N/A)
- States             (only those differing/added beyond §4)
- Accessibility      (only distinctive; baseline per §8)
- Responsive         (only distinctive; rules per §6)
- Token usage        (the specific tokens this component consumes)
- Motion             (signature motion only; shared per §7)
- Usage guidelines    (do)
- Anti-patterns      (don't — tied to Constitution where relevant)
```

---

## 11. Phase 2 Component Index & Family Map

The full production library, grouped into family specs. Each row maps to its frozen Inventory role
(or notes "primitive" for generic containers introducing no product capability).

### Foundation families

| # | Family spec | Components | Frozen mapping |
|---|-------------|-----------|----------------|
| 01 | **Buttons & Icon Buttons** | Button, Icon Button | `Button`, `Icon` |
| 02 | **Text Inputs** | Input, Search, Textarea | `Input`, `SearchField` |
| 03 | **Selection Controls** | Checkbox, Radio, Switch, Select, Dropdown menu | `FormField`, `Input` (choice) |
| 04 | **Navigation & Wayfinding** | Tabs, Segmented Control, Breadcrumbs, Pagination, Sidebar, Global Navigation | `Tab/SectionNav`, `GlobalNavigation`, `GlobalHeader` |
| 05 | **Content & Data Display** | Card, Table, Chip, Badge, Avatar | `Badge/Tag`, `StatementTable`, `ListItem` |
| 06 | **Overlays** | Tooltip, Popover, Dialog, Drawer | `Tooltip` (+ primitives) |
| 07 | **Feedback & Status** | Toast, Notification, Progress, Skeleton, Loader | `Notification/Toast`, `Spinner/Progress` |

### AI families

| # | Family spec | Components | Frozen mapping |
|---|-------------|-----------|----------------|
| 08 | **AI Components** | AI Chat Bubble, AI Response Card, Citation Card, Source Preview, Evidence Card, Confidence Indicator, Thinking State, Streaming Response, AI Action Toolbar, AI Suggestions, Prompt Composer | `CopilotPanel`, `AISummary`, `SourceReference` |

### Research families

| # | Family spec | Components | Frozen mapping |
|---|-------------|-----------|----------------|
| 09 | **Research Components** | Company Card, Company Header, Financial Metric Card, KPI Tiles, Financial Tables, Chart Container, Research Timeline, Watchlist Item, Portfolio Card, Comparison Card, News Card, Filing Viewer, Report Viewer, Analyst Summary Card | `MetricStat`, `StatementTable`, `ComparisonTable`, `ChartFigure`, `FilingViewer`, `ReportDocument`, `ListItem`, `AISummary` |

> **No family introduces product capability beyond the frozen baseline.** Generic primitives
> (Popover, Drawer, Segmented Control, Avatar, Switch, Breadcrumbs, Pagination) are presentation
> containers/controls that compose existing behavior; they add no new destination or capability
> (Component Inventory §intro rule).

---

## 12. Governance

- A component that cannot be expressed with existing tokens, or that would introduce a new product
  capability, is **out of scope** and requires a Change Request — not a local invention.
- Family specs are the detailed contract; where they and this foundation disagree, **this document
  wins** and the family spec is corrected.

---

*Prepared by the Experience Design Department · Milestone 2 · Phase 2 of 7 · Foundation*
