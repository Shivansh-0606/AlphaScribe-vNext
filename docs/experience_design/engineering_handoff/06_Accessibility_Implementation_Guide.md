# AlphaScribe vNext — Accessibility Implementation Guide

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Doc** | M3 · Accessibility Implementation Guide (06) |
| **Owner** | Experience Design Department |
| **Design source (frozen)** | [Accessibility](../../design/12_Accessibility.md) · Constitution §17 (Immutable Law 10) |
| **Last Updated** | 2026-07-18 |

## Purpose

Define the **implementation contract** for accessibility so Engineering builds AlphaScribe to **WCAG 2.1
AA** by default, not as a later pass. Accessibility is an **Immutable Law** (Constitution §17, Law 10):
experience is never traded against inclusivity. This document turns the frozen Accessibility spec into
concrete, testable engineering obligations.

## Scope

WCAG AA, keyboard navigation, focus management, screen readers, contrast, color-blindness, reduced
motion, zoom/reflow, touch targets, semantic expectations. Applies to **every** component and screen.
**Out of scope:** re-stating the frozen [Accessibility](../../design/12_Accessibility.md) spec (linked);
this is its implementation lens.

## Decision Rationale

- **A11y in the foundation, enforced in CI** is the only way it survives a multi-year build; retrofitting
  is expensive and always incomplete.
- **shadcn primitives** are chosen partly because their Radix base ships correct roles/keyboard behavior —
  the wrapper's job is to not break them and to bind tokens/labels.

## 1. WCAG 2.1 AA — the target

AA is the **baseline**, not the aspiration. Every success criterion at A and AA applies; the ones this
product touches most are called out below. **CI gate:** automated axe checks on every component and
screen; automated checks catch ~30–40%, so the manual checklist ([10 Design QA](10_Design_QA_Process.md))
covers the rest (keyboard, focus, SR, meaning).

## 2. Keyboard Navigation

- **Everything operable by keyboard**, no pointer-only paths, no keyboard traps (except intentional,
  escapable modal focus traps).
- **Documented key maps** (from the M2 families): Button/IconButton Enter/Space; Tabs/Segmented/Radio
  Arrow keys (roving tabindex) + Home/End; Select/Combobox Arrow/Home/End/type-ahead, Enter select, Esc
  close; Menu Arrow + Enter/Space, Esc + return focus to trigger; Dialog/Drawer Esc close + focus trap;
  Table row/column navigation; Chip remove via its labeled control.
- **Logical tab order** matches reading/visual order; no positive `tabindex`.
- **Skip link** to main content after the header.

## 3. Focus Management

- **Visible focus always** — `--focus-ring-*` (2px deep-emerald AA ring + 2px offset) via `:focus-visible`
  on **every** interactive element. Focus is **styled, never removed** (no `outline:none` without a
  replacement).
- **Predictable movement:** on dialog/drawer open → focus moves in (to the panel / least-destructive
  action); on close → **returns to the trigger**; on route change → focus to the new page's `h1`/main; on
  submit error → focus the **first invalid field**.
- **Focus trap** in modal dialogs and the mobile nav drawer; the **non-modal AI companion does not trap**
  (user moves freely between content and companion).
- Background is **`inert`** when a modal is open.

## 4. Screen Readers

- **Correct semantics first** (native elements/roles), ARIA only to fill genuine gaps. Every interactive
  element has an **accessible name**; state exposed via `aria-pressed`/`-expanded`/`-selected`/`-checked`/
  `-current`/`-invalid`/`-disabled`/`-busy`.
- **Landmarks:** `banner` (header), `nav` (global/section, each named), `main`, `complementary` (AI
  companion), `contentinfo` (footer).
- **Live regions:** loading/error/toast/AI announced at the right politeness — **polite** for success/
  info/streaming, **assertive** for blocking errors. **AI streaming announced considerately** (batched/
  debounced, not per-character); **completion announced**; sources reachable.
- **Financial data:** tables use `<caption>`, `<th scope>`, header association; values read **with their
  meaning**; charts provide an **accessible data-table equivalent** (never chart-only).
- **Icon-only controls** carry a real `aria-label` (the glyph is `aria-hidden`); tooltip is not the sole
  name source.

## 5. Contrast

- **Frozen AA pairings** ([Color System](../02_Color_System.md)): body text ≥ 4.5:1; large text / essential
  UI ≥ 3:1; focus ring AA-contrast. `--muted-foreground` only where its contrast remains AA at the size
  used.
- **Do not re-tune** a color for aesthetics — contrast is frozen; a change is a CR against Color +
  Accessibility. Validate every text/background pair before shipping (QA token pass).

## 6. Color Blindness / No Color-Only Meaning

- **No meaning by color alone** (§17, Law 10): every color-coded state carries a **non-color cue** —
  financial direction = sign + ▲/▼ + text; status/badges = text; selected = check/weight/indicator;
  disabled = opacity **+** removed affordance + `aria-disabled`; chart series = label/pattern/marker in
  addition to the chart ramp.
- Verify designs under deuteranopia/protanopia simulation (bullish-green vs bearish-red must remain
  distinguishable by their non-color cues).

## 7. Reduced Motion

- `prefers-reduced-motion: reduce` honored **globally and losslessly** — all motion collapses to instant
  state changes; essential progress (determinate bars, streaming chunks) remains ([05 Motion](05_Motion_Specifications.md)).
- Motion is **never** the sole carrier of information.

## 8. Zoom & Reflow

- **Reflow to 320px width and to 200% zoom** with no loss of content/functionality and **no horizontal
  page scroll** (WCAG 1.4.10). Rem-based type scales with user font-size settings.
- **Text spacing** overrides (line-height/letter/word spacing) don't clip content (1.4.12).
- Wide tables/charts scroll **within their own container**, not the page.

## 9. Touch Targets

- **≥ 44×44px effective target** on touch contexts (hit-area padding where the visual is smaller);
  adequate spacing to avoid mis-taps. Hover-only affordances become tap-to-reveal on touch.

## 10. Semantic Expectations

- Sequential headings (one `h1` per screen = the primary subject, e.g. company name; then h2→h3, no
  skips). Lists are lists; buttons are `<button>`; links are `<a>`; forms use `<label for>` + fieldset/
  legend for groups. Never a `<div>` with a click handler where a semantic element exists.
- Form errors are **text**, specific, and programmatically associated (`aria-describedby`,
  `aria-invalid`); focus moves to the first error.

## Enforcement (how a11y stays true)

1. **CI:** axe/eslint-jsx-a11y as a merge gate.
2. **Component tests:** keyboard interaction + role/name/state assertions per component.
3. **Design QA manual pass** ([10](10_Design_QA_Process.md)): keyboard-only walkthrough, SR spot-check
   (NVDA/VoiceOver), contrast + color-blind simulation, 200%/320px reflow, reduced-motion.
4. **No component/screen merges with a11y deferred.**

## References to Previous Milestones

[Accessibility](../../design/12_Accessibility.md) (authoritative) · Constitution §17 / Law 10 ·
[Color System](../02_Color_System.md) · [States](../../design/13_States.md) · each [M2 family](../Components/00_Component_System.md) a11y section · [05 Motion](05_Motion_Specifications.md).

## Best Practices

- Lean on shadcn/Radix semantics; the wrapper adds names/tokens and must not remove roles/keyboard behavior.
- Build the keyboard path first; if it works keyboard-only, pointer is easy.
- Announce dynamic change through one shared live-region utility (consistent politeness).

## Anti-patterns

- ✗ `outline:none` without a visible replacement. ✗ Color-only meaning. ✗ Placeholder-as-label.
- ✗ Icon buttons without `aria-label`. ✗ Per-character streaming announcements. ✗ Charts with no data
  equivalent. ✗ Focus lost to `<body>` on overlay close. ✗ Treating a11y as a post-launch pass.

## Engineering Considerations

- A shared `<VisuallyHidden>`, focus-trap, live-region, and `useReducedMotion` utility set is foundation
  work ([11](11_Engineering_Implementation_Guidelines.md)) — build before components.
- TanStack Query error/empty/partial states must each render an **accessible** message ([States]).

## Accessibility Considerations

(This document *is* the accessibility contract.) Its own success measure: a keyboard-only and
screen-reader-only user can complete every approved journey (J-01…J-06) with no dead ends and no lost
work.

## Future Maintenance

Re-run the full manual pass per screen when M2 Phase 4 lands. Update when the frozen Accessibility spec
changes via CR. Governed by [13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 06 of 14*
