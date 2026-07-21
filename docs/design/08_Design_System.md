# AlphaScribe vNext — Design System

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Version** | 0.1.1 |
| **Phase** | Design (pre-PRD) |
| **Owner** | Product & Design |
| **Approved By** | CTO |
| **Last Updated** | 2026-07-18 |
| **Source of Truth** | For visual/design foundations |

**Downstream Dependencies:** Component Inventory · Interaction Patterns · Responsive
Behavior · Accessibility · Design Specifications · Frontend implementation

---

# Revision History

| Version | Date | Author | Status | Description |
|---------|------|--------|--------|-------------|
| 0.1.0 | 2026-07-18 | Product & Design | 📝 Draft | Initial design system aligned to the established warm-light editorial-fintech theme. Dark Mode flagged for CTO review. |
| 0.1.1 | 2026-07-18 | Product & Design | 📝 Draft | Experiential alignment to the Design Constitution (v1.1): added Motion & Interaction Token philosophy, Animation, Depth, Experience Consistency, and Craftsmanship principles; added `interaction.*` and `depth.*` token families. No implementation values defined; theme unchanged. |

---

# Document Traceability

| Relationship | Documents |
|--------------|-----------|
| **Depends On** | [Design Constitution](00_Design_Constitution.md), [Product Vision](../master-plan/02_Product_Vision.md), [Product Strategy](../master-plan/01_Product_Strategy.md), [Wireframes](07_Wireframes.md), [Information Architecture](03_Information_Architecture.md) |
| **Used By** | [Component Inventory](09_Component_Inventory.md), [Interaction Patterns](10_Interaction_Patterns.md), [Accessibility](12_Accessibility.md), [Responsive Behavior](11_Responsive_Behavior.md), Frontend implementation. |
| **Related Documents** | [Navigation Structure](04_Navigation_Structure.md), [States](13_States.md) |

> This document defines **design foundations** (principles and tokens), not code. It
> is expressed as **design tokens** — named, semantic values — so engineering can map
> them to implementation without this document prescribing a framework.

> ⚠️ **CONFLICT FLAGGED FOR CTO REVIEW — Dark Mode.** The prompt requests a *Dark
> Mode* section, but the established product direction is a **single light theme with
> deliberately no dark mode and no theme toggle**. "Dark Mode" was previously removed
> from the Feature Roadmap on that basis. This document documents the direction as-is
> and treats Dark Mode as **out of MVP scope**, rather than introducing a second theme
> that would contradict the approved baseline. See the *Dark Mode* section.

---

# Design Principles

The system expresses the product's trust-first, research-first philosophy visually.

| Principle | Meaning for the design system |
|-----------|-------------------------------|
| **Editorial clarity** | A calm, reading-oriented aesthetic suited to research; content leads, chrome recedes. |
| **Trust made visible** | Sources and evidence are always visually reachable; AI insight is never styled as unquestionable authority. |
| **Progressive disclosure** | Visual hierarchy surfaces summary first, detail on demand. |
| **Consistency** | One token set; the same meaning always renders the same way. |
| **Restraint** | Minimal accent use; emphasis reserved for what matters (the research and its sources). |
| **Accessibility by default** | Contrast, focus, and motion respect WCAG AA and user preferences. |

---

# Foundational Theme

AlphaScribe uses a **single, warm-light editorial-fintech theme**: a cream paper
canvas, ink-navy type, and an emerald→teal signature accent. There is exactly one
token set; semantic colors are consumed as design tokens. This matches the
established, approved product identity and must not be forked into a second theme.

---

# Typography

Defined as semantic type tokens (roles), not fonts-as-implementation.

| Token | Role |
|-------|------|
| `type.display` | Landing/hero emphasis. |
| `type.heading.1–3` | Section and screen headings; establish hierarchy. |
| `type.body` | Primary reading text (research content, explanations). |
| `type.body.strong` | Emphasis within body. |
| `type.caption` | Metadata, dates, source labels. |
| `type.mono` | Figures/tabular numerals where alignment aids reading. |

Rules: a limited, consistent type scale; generous line length and spacing for
readability (research is a reading task); headings follow a strict, sequential order
for accessibility.

---

# Spacing

A single spacing scale expressed as tokens (`space.0` … `space.n`), applied
consistently for rhythm and grouping. Related information uses tighter spacing;
distinct groups use larger spacing. No ad-hoc spacing outside the scale.

---

# Grid

A responsive content grid with a comfortable maximum reading width for text-heavy
research. Structure is defined by tokens (`grid.columns`, `grid.gutter`,
`grid.max-content-width`). Exact breakpoint behavior is specified in
[Responsive Behavior](11_Responsive_Behavior.md); this document owns the token names.

---

# Color System

Semantic color tokens (single light theme). Values are the established palette; token
names are canonical for downstream use.

| Token | Role |
|-------|------|
| `color.canvas` | Cream paper background. |
| `color.surface` | Raised content surfaces. |
| `color.ink` | Primary ink-navy text. |
| `color.ink.muted` | Secondary text, captions. |
| `color.border` | Dividers and quiet separation. |
| `color.brand-from` / `color.brand-to` | Emerald→teal signature gradient (primary accent). |
| `color.bullish` | Positive financial signal. |
| `color.bearish` | Negative financial signal. |
| `color.warning` | Caution / needs-attention. |
| `color.focus` | Focus indicator. |

Rules: accent used sparingly for primary emphasis; `bullish`/`bearish` reserved for
genuine financial meaning (never decoration); every text/background pairing meets
WCAG AA contrast (see [Accessibility](12_Accessibility.md)).

---

# Elevation

A small, semantic elevation scale (`elevation.flat`, `elevation.raised`,
`elevation.overlay`) distinguishing base content, raised surfaces, and transient
overlays (dialogs, drawers). Elevation communicates layering, not decoration.

---

# Radius

A limited radius scale (`radius.sm`, `radius.md`, `radius.lg`, `radius.pill`) applied
consistently to related element families. Consistent rounding reinforces the calm,
editorial feel.

---

# Iconography

A single, consistent icon family used at consistent sizes (`icon.sm/md/lg`). Icons
support meaning (e.g. source, export, comparison, AI) and always pair with an
accessible label; icon-only controls carry an accessible name. Icons never replace a
required text label for critical actions.

---

# Illustrations

Illustration is used sparingly, primarily for empty and onboarding states, in the
theme palette. Illustrations are supportive, never load-bearing for meaning; any
information they convey is also available as text.

---

# Motion

Motion is functional and expressive within restraint, defined by tokens
(`motion.duration.*`, `motion.easing.*`). Per the [Design Constitution](00_Design_Constitution.md)
§14, motion must **communicate and must never distract from research**: it creates
continuity, guides attention, reinforces hierarchy, improves perceived performance, and
provides *subtle delight* that expresses craftsmanship. It is never ornament or spectacle.
All motion respects reduced-motion preferences (see *Motion Reduction* in
[Accessibility](12_Accessibility.md)). AI streaming uses motion to signal a partner *thinking
and gathering evidence*, not a generic spinner.

## Motion & Interaction Token Philosophy

Tokens make the *feel* of the product consistent and craftsmanlike. This section defines the
**philosophy and token families**, not implementation values (durations, curves, and
distances are set downstream and tuned in build).

- **Motion tokens** (`motion.duration.*`, `motion.easing.*`, `motion.distance.*`): a small,
  shared scale so every transition shares one cadence. Short, calm durations by default;
  natural easing that feels organic rather than mechanical. One vocabulary of motion across
  the product creates emotional continuity.
- **Interaction tokens** (`interaction.feedback.*`, `interaction.hover.*`,
  `interaction.press.*`, `interaction.focus.*`): the standard responses to input, so every
  component acknowledges the user in the same proportionate, refined way. Feedback is
  immediate and never exaggerated.
- **Depth tokens** (`depth.layer.*`, mapped to the semantic `elevation.*` scale): express
  spatial layering — foreground work, contextual surfaces, transient overlays — as *meaning*,
  not decoration. Depth communicates relationship and focus (Constitution §12), never applies
  ornamental blur/shadow for its own sake.

## Animation Philosophy

Animation exists to serve understanding and confidence: to preserve continuity between
states, to make AI feel alive, to reveal information progressively, and to reward interaction
subtly. Test for each animation: if it can be removed without losing meaning, it is
decoration and should be cut. Reduced-motion is always honored with no loss of information.

## Depth Philosophy

The interface is **spatial**: surfaces relate through layering and elevation so the user reads
structure and focus at a glance. Depth is applied with restraint (*ambient polish*) — enough
to give the workspace a sense of place, never enough to distract, reduce contrast, or
compromise accessibility. Foreground carries the active research; supporting context sits
behind without competing.

## Experience Consistency

One motion cadence, one interaction feel, one depth language — applied uniformly. The same
action feels the same everywhere; the same kind of surface layers the same way everywhere.
Consistency of *feel* is as much a part of the system as consistency of color and type, and is
what makes the product read as one crafted whole.

## Craftsmanship Principles

Premium quality is built, not decorated. The system encodes craftsmanship as: proportionate
feedback, refined and consistent motion, thoughtful spatial hierarchy, visual and temporal
rhythm, restraint (emphasis is scarce and meaningful), and attention to every state and edge.
A component is not "done" until its resting, hover, focus, loading, transition, and error
moments all feel considered.

---

# Dark Mode

⚠️ **Out of MVP scope — flagged for CTO review.** The approved product direction is a
**single light theme**; there is deliberately no dark theme and no theme toggle. This
system therefore defines **one** token set. Introducing a dark theme would:

- contradict the frozen product identity, and
- reintroduce a capability previously removed from the Roadmap.

**Recommendation:** keep the single light theme for MVP. If a dark theme is desired
later, it should enter via a governance Change Request, not this document. No dark
palette is defined here.

---

# Accessibility Standards

The system targets **WCAG 2.1 AA** as a floor. Color contrast, visible focus
(`color.focus`), motion reduction, and non-color-dependent meaning are built into the
tokens and rules above. Full requirements live in [Accessibility](12_Accessibility.md);
this document guarantees the token-level foundations they depend on.

---

# Component Naming

Components use clear, semantic PascalCase names describing role, not appearance
(e.g. `SourceReference`, `MetricStat`, `CopilotPanel`, `ComparisonTable`). Variants
are expressed as properties, not new names. The canonical catalogue is
[Component Inventory](09_Component_Inventory.md); this document sets the naming rule.

---

# Design Tokens

Tokens are the single source of truth for design values, grouped by semantic role:
`color.*`, `type.*`, `space.*`, `grid.*`, `elevation.*`, `radius.*`, `icon.*`,
`motion.*`, `interaction.*`, `depth.*` (see *Motion & Interaction Token Philosophy*). Rules:

- Components consume **tokens**, never raw values.
- One token set (light theme); no per-component overrides of token meaning.
- New values require a new token, reviewed for consistency — not an inline value.

---

# Content Guidelines

- **Plain language first** — explain before quantifying; define terms for learners (P-02).
- **Neutral, non-hype tone** — informative, never promotional (Strategy: free of marketing language).
- **No recommendations** — content informs decisions; it never issues buy/sell advice (Strategy: research before recommendations).
- **Source-attributed** — insights are phrased so their evidence is clear and reachable.
- **Consistent terminology** — use the vocabulary of the frozen baseline (e.g. Resume Session, Research Session, Company Research).

---

# AI Design Principles

How AI is presented, consistent with the Vision and Trusted-AI positioning.

- **Embedded, not separate** — AI appears within research contexts, never as a
  standalone chatbot destination.
- **Grounded and sourced** — every AI insight is visually accompanied by a path to its
  source (Jump to Source).
- **Explainable** — AI output is presented as reasoning the user can follow, not a verdict.
- **Assistant, not authority** — visual treatment keeps the user as decision-maker; AI
  is styled as support.
- **Progress made visible** — AI thinking/streaming states are clearly signaled
  (see [States](13_States.md)) without overwhelming the reading experience.
