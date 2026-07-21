# AlphaScribe vNext — Component Family 06: Overlays

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Phase** | M2 · Phase 2 — Core Components |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Inherits** | [Component System Foundation](00_Component_System.md) |
| **Frozen mapping** | [`Tooltip`](../../design/09_Component_Inventory.md#tooltip) (Popover/Dialog/Drawer are presentation primitives — no new capability) |

> **Overlays are where Direction C legitimately elevates.** They are transient, contextual, active
> content — exactly what §12 says *should* read as elevated. Shared overlay rules: they sit above
> content via the [layering + shadow tokens](../10_Design_Tokens.md#10-layering-z-index-tokens),
> manage focus, close on Esc, and **preserve the user's underlying work** (Law 6). None traps the user.

---

## Shared overlay contract (applies to all four)

| Facet | Rule |
|-------|------|
| **Layering** | `--z-overlay` (menus/popovers/tooltips) · `--z-drawer` · `--z-modal`; shadow per elevation (`--shadow-md`/`--shadow-lg`). |
| **Dismissal** | Esc closes; click/tap outside closes (except modal dialogs requiring a choice); a labeled close control exists. |
| **Focus** | Opening moves focus appropriately; **modal dialogs and drawers trap focus**; on close, focus **returns to the trigger**. |
| **Scrim** | Modal surfaces use `--opacity-scrim` backdrop; non-modal (tooltip/popover/menu) use none. |
| **Motion** | Reveal `--motion-duration-base/slow`, `--motion-ease-out`, subtle origin from trigger (continuity); reduced motion → instant appear/disappear, no slide. |
| **Work preservation** | Underlying research is never discarded by opening/closing an overlay. |

---

## Tooltip ⟶ maps to: `Tooltip` (Inventory Molecule)

### Purpose
Reveal **supplementary** explanation on demand — a definition for a learner term (P-02), a control's
name, a metric's meaning hint. Never holds essential or interactive content.

### Anatomy
A small `--elevation-3` bubble with `type.caption` text, an arrow to its trigger, on `--popover`
surface. Text/definition only.

### Variants
Per Inventory: **Text** (label/hint) · **Definition** (financial-term explanation for learners).

### Sizes
Compact; wraps to a comfortable max width; never a paragraph-heavy panel (use a Popover for that).

### States
**Hidden · Visible** (Inventory). Appears on hover **and** keyboard focus; dismiss on blur/Esc.

### Accessibility (distinctive)
Reachable by keyboard focus (not hover-only); associated via `aria-describedby`; **never the only
place essential info lives** (Inventory rule); does not trap focus; remains long enough to read;
dismissible with Esc.

### Responsive (distinctive)
On touch (no hover), the trigger is tap-to-reveal (or the info is a Popover); never hover-only on
touch. Repositions to stay on-screen.

### Token usage
`--popover(-foreground)`, `--elevation-3`, `--shadow-md`, `--z-overlay`, `type.caption`,
`--radius-md`, `--motion-duration-base`.

### Motion (signature)
Fade/scale-in `--motion-duration-base`, slight delay on hover-in (avoid flicker), quick out.
Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** use for supplementary hints and learner definitions; make keyboard-reachable.
- ✗ Interactive content or essential info in a tooltip; ✗ hover-only (fails keyboard/touch);
  ✗ hiding a required label behind a tooltip.

---

## Popover ⟶ primitive (contextual panel)

### Purpose
A small, **interactive** contextual panel anchored to a trigger — search suggestions, a filter
panel, a select listbox, a source preview, a "details" card. Richer than a tooltip, lighter than a
dialog; non-modal.

### Anatomy
An `--elevation-3` panel (`--popover` surface, `--shadow-md`) with an arrow/anchor, arbitrary
interactive content (inputs, lists, links), and optional header/footer.

### Variants
**Menu/listbox** (see [Selection Controls](03_Selection_Controls.md)) · **Suggestions**
(see [Search](02_Text_Inputs.md)) · **Info/preview panel** (e.g. Source Preview — full spec in
[AI Components](08_AI_Components.md)) · **Filter panel.**

### Sizes
Content-driven, with a sensible max; scrolls internally if tall; width ≥ trigger where it's a
field's menu.

### States
**Closed · Open · Focus-within.** Opening moves focus to the panel (or first item); Esc/outside-click
closes; focus returns to trigger. Non-modal: underlying content stays visible/scrollable.

### Accessibility (distinctive)
Trigger has `aria-haspopup` + `aria-expanded`; the panel is associated; keyboard operable (Tab
within, Esc to close, Arrow for listbox variants); not focus-trapped (non-modal) unless it's a menu.
Positioned to stay in viewport.

### Responsive (distinctive)
On mobile, promotes to a **bottom sheet** (a light drawer) for reach; content and behavior preserved.

### Token usage
`--popover`, `--elevation-3`, `--shadow-md`, `--z-overlay`, `--radius-md`, `--border`,
`--focus-ring-*`, `--motion-duration-base`, `--motion-ease-out`.

### Motion (signature)
Reveal from trigger origin `--motion-duration-base`, `--motion-ease-out` (continuity); caret/anchor
aligns. Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** use for contextual interactive content; anchor to and return focus to the trigger.
- ✗ Using a popover where a modal decision is required (use Dialog); ✗ stacking many popovers;
  ✗ content that should be a persistent panel crammed into a transient popover.

---

## Dialog ⟶ primitive (modal / focused task or decision)

### Purpose
Interrupt for a **focused decision or short task** that needs resolution — confirm an irreversible
action, a short form, a required choice. Used sparingly (interruption is a cost).

### Anatomy
`scrim (--opacity-scrim) · panel (--elevation-4, --shadow-lg) [ title · body · actions ] · close`.
Actions area: a clear primary + secondary (Cancel); destructive confirmations style the primary
`--destructive`.

### Variants
**Confirmation** (esp. destructive) · **Form dialog** (short task) · **Alert** (must acknowledge).
Prefer **undo over confirmation** where feasible (§19) — reserve dialogs for genuinely irreversible
or blocking choices.

### Sizes
`sm` (confirmation) / `md` (form) / responsive full-screen on mobile.

### States
**Closed · Open · Loading (submit) · Error (inline) · Success.** Distinctive:
- **Loading/Error on submit:** handled **inside** the dialog (inline), preserving entered data;
  never closes-and-loses on error (Law 6).

### Accessibility (distinctive — critical)
`role=dialog` + `aria-modal=true`; labeled by its title (`aria-labelledby`); **focus trapped** while
open; focus moves to the dialog (first focusable / the least-destructive action) on open and
**returns to the trigger** on close; Esc closes (unless a required decision); background inert.

### Responsive (distinctive)
Full-screen sheet on mobile; actions remain reachable above the keyboard; scrim on larger screens.

### Token usage
`--elevation-4`, `--shadow-lg`, `--opacity-scrim`, `--z-modal`, `--popover`/`--surface`,
`--radius-md`, Button tokens, `--focus-ring-*`, `--motion-duration-slow`.

### Motion (signature)
Scrim fades + panel scales/fades in `--motion-duration-slow`, `--motion-ease-out` (a considered
entrance, never bouncy). Reduced motion → instant appear, scrim instant.

### Usage guidelines
- **Do** reserve for focused decisions/short tasks; keep entered data on error; default focus to the
  safe action.
- **Do** prefer undo/reversible flows over confirm dialogs where feasible.

### Anti-patterns
- ✗ Dialogs for content that belongs on a page/drawer; ✗ dialog stacks; ✗ no focus trap / focus
  lost on close; ✗ destructive primary as the default-focused action; ✗ closing on error and losing
  input.

---

## Drawer ⟶ primitive (edge-anchored panel / companion surface)

### Purpose
An edge-anchored panel for **contextual content or the mobile navigation menu**, and the desktop
**AI companion** surface (Direction C's "summoned companion"). Larger and more persistent than a
popover; may be modal (mobile nav) or non-modal (companion alongside content).

### Anatomy
A panel sliding from an edge (right for the AI companion; left for mobile nav) with a header
(title · close), scrollable body, optional footer (e.g. the Prompt Composer for the AI companion).
Modal drawers use a scrim; the non-modal companion does not.

### Variants
**Navigation drawer** (mobile nav — modal, focus-trapped) · **Contextual drawer** (filters/details)
· **AI companion drawer** (the summoned AI partner; non-modal on desktop, sheet on mobile — full
behavior in [AI Components](08_AI_Components.md)).

### Sizes
Desktop companion: a fixed-width right panel (content reflows, not overlaps, when non-modal). Mobile:
full-width sheet. Contextual: content-sized.

### States
**Closed · Open · Loading · Focus.** The AI companion adds **AI Thinking/Streaming** (owned by the AI
components). Companion open/collapsed state persists per context (continuity — "summoned, then
recedes").

### Accessibility (distinctive)
Modal drawer (mobile nav): `role=dialog`/`aria-modal`, focus trapped, Esc closes, returns focus to
the menu button. Non-modal companion: a labeled `complementary`/region, keyboard reachable, Esc
collapses, does not trap focus (the user moves between content and companion freely). AI streaming
announced considerately.

### Responsive (distinctive)
Desktop right-side companion → mobile bottom/side **sheet** (may become modal for reach). Mobile nav
drawer is the condensed form of [Global Navigation](04_Navigation.md) — destination parity preserved.

### Token usage
`--surface`, `--border`, `--elevation-3`/`-4`, `--shadow-md`/`-lg`, `--z-drawer`, `--opacity-scrim`
(modal only), `--radius` (0/sharp edges), `--focus-ring-*`, `--motion-duration-slow`.

### Motion (signature)
Slide-in from edge `--motion-duration-slow`, `--motion-ease-out` (the "companion arrives" moment —
continuity, calm). Collapse slides out. Reduced motion → instant show/hide, no slide.

### Usage guidelines
- **Do** use a non-modal companion drawer for the summoned AI (present when needed, recedes when
  not); use a modal drawer for the mobile nav menu.
- **Do** persist the companion's open/collapsed state per context.

### Anti-patterns
- ✗ An always-open AI drawer that becomes a persistent chatbot sidebar (breaks Law 5 / Direction C —
  it must be *summoned* and *recede*).
- ✗ A non-modal companion that traps focus; a modal drawer that doesn't.
- ✗ Overlapping (rather than reflowing) primary content with a non-modal companion on desktop.

---

## Family cross-references
- Menus/listboxes/suggestions: [Selection Controls](03_Selection_Controls.md), [Text Inputs](02_Text_Inputs.md).
- The AI companion drawer's internal behavior: [AI Components](08_AI_Components.md) (`CopilotPanel`).
- Canonical states (Loading/Error/Success/Timeout): [States](../../design/13_States.md).

*Family 06 of 09 · Phase 2 · Milestone 2*
