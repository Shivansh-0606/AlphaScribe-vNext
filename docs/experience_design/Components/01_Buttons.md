# AlphaScribe vNext — Component Family 01: Buttons & Icon Buttons

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Milestone / Phase** | M2 · Phase 2 — Core Components |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Inherits** | [Component System Foundation](00_Component_System.md) — universal contract, sizes, states, tokens, motion, a11y, responsive |
| **Frozen mapping** | [`Button`](../../design/09_Component_Inventory.md#button), [`Icon`](../../design/09_Component_Inventory.md#icon) |

> Only what is **distinctive** to these components is documented here; everything else is
> inherited from the [foundation](00_Component_System.md) (cited as *"per foundation §N"*).

---

## Button ⟶ maps to: `Button` (Inventory Atom)

### Purpose
Trigger a single, discrete action. The button is the product's primary unit of agency; its
restraint (one Primary per context) is what makes the primary action unmistakable (§7.1).

### Anatomy
`[ optional leading icon ] · Label · [ optional trailing icon ]`, inside a padded container with
`--radius-md` corners. Optional: loading spinner (replaces leading icon in-place), keyboard focus
ring (foundation §4). Label is **always present in the accessibility tree** even when visually
icon-only (see Icon Button).

- **Label** — `type.small`/`type.body` (per size), action-oriented, names the outcome
  ("Export report", not "OK") (§15).
- **Icon** (optional) — a Phosphor glyph reinforcing meaning, `icon` sized to the text
  ([Iconography](../08_Iconography_Guidelines.md)); decorative, never the sole label carrier.
- **Container** — padding from the §3 size ladder; fill/border per variant.

### Variants
Exactly the four frozen variants — no more (Inventory: Primary, Secondary, Quiet/Text, Destructive).

| Variant | Fill / border | Use | Signal spend |
|---------|---------------|-----|--------------|
| **Primary** | Solid `--primary` (ink-navy) **or** the `--brand-from→--brand-to` signal gradient for the single most important action in context | The one main action per view/region | Navy default; gradient reserved for the single hero action (never both competing) |
| **Secondary** | `--surface`/`--secondary` fill, `--border` hairline | Supporting actions beside a Primary | None |
| **Quiet / Text** | No fill, ink label; hover → `--state-hover-surface` | Low-emphasis/tertiary, toolbar actions, "Cancel" | None |
| **Destructive** | `--destructive` fill (solid) or ink label with `--destructive` on confirm | **Irreversible** actions only | Red = meaning, not decoration |

**One Primary per context** (Inventory Usage Rule; §7.1). Prefer reversible actions + undo over
Destructive where feasible (§19).

### Sizes
`sm` / `md` (default) / `lg` per foundation §3. `lg` for primary CTAs and touch-primary contexts;
`sm` for dense tables/toolbars.

### States
Per foundation §4. Distinctive notes:

- **Loading:** the label stays, a spinner replaces the leading icon **in place**; the button keeps
  its width (no reflow) and becomes `aria-busy`, non-activatable. Loading is scoped to the button —
  the rest of the screen stays interactive (§21).
- **Disabled:** `--opacity-disabled` **plus** removed hover/press affordance and `aria-disabled`;
  when the reason is non-obvious, an adjacent text/tooltip explains why (never a dead, unexplained
  control).
- **Active/Pressed:** `--state-active`, brief and proportionate — the tactile "heard you" moment.

### Accessibility (distinctive)
- Native `<button>`; Enter/Space activate; not a `<div>` with a click handler.
- Accessible name always present (visible label, or `aria-label` for icon-only).
- Loading announces busy; disabled communicates unavailability by more than color/opacity.
- Focus ring per foundation §8; visible on keyboard focus.

### Responsive (distinctive)
- Touch: effective target ≥ 44px (foundation §3). On mobile, a primary form action may go
  full-width for reach; label never truncates — it wraps to `sm` size or shortens with an
  equivalent accessible name, never to an ambiguous glyph.

### Token usage
`--primary(-foreground)`, `--secondary(-foreground)`, `--brand-from`/`--brand-to` (hero only),
`--destructive(-foreground)`, `--surface`, `--state-hover-surface`, `--state-active`,
`--border`, `--radius-md`, `type.small`/`type.body`, `--space-2/3/4`, `--focus-ring-*`,
`--opacity-disabled`, `--motion-duration-fast`.

### Motion (signature)
- Hover/press: `--motion-duration-fast` (120ms) fill/emphasis shift — the acknowledgment.
- Loading enter: spinner cross-fades in `--motion-duration-base`; label unchanged.
- Reduced motion: instant fill change, static busy indicator (foundation §7). No pulse/bounce.

### Usage guidelines
- **Do** keep exactly one Primary per view/region; demote the rest to Secondary/Quiet.
- **Do** name the outcome on the label; pair a meaning-reinforcing icon where it aids scanning.
- **Do** use Destructive only for irreversible actions, ideally with undo or confirmation.
- **Do** keep the button in layout during loading (reserve its width).

### Anti-patterns
- ✗ Two Primary buttons competing in one context (breaks §7.1). 
- ✗ The signal gradient on non-primary or multiple buttons (dilutes the one signal — Color §Anti-patterns).
- ✗ Color-only disabled/destructive (fails §17 no-color-only).
- ✗ Vague labels ("OK", "Go", "Submit") (§15 action-oriented labels).
- ✗ A spinner that resizes or removes the button on load (layout shift; loses the "heard you").
- ✗ A `<div>`/link styled as a button (breaks keyboard + semantics).

---

## Icon Button ⟶ maps to: `Button` (icon-only) + `Icon` (Inventory Atoms)

### Purpose
Trigger an action in space too tight for a text label — toolbars, table rows, dense AI action bars,
close affordances. It is a Button whose label is visually an icon but **semantically still a name**.

### Anatomy
Square container (§3 ladder: 28/36/44) · centered Phosphor glyph · focus ring · **mandatory
accessible name** (`aria-label`) · optional tooltip echoing that name on hover/focus.

### Variants
Mirror Button emphasis, minus text: **Quiet** (default — no fill, hover surface), **Secondary**
(hairline), **Primary** (solid, rare — e.g. a composer "send"), **Destructive** (e.g. remove).
Toggle icon buttons (e.g. add/remove from watchlist) expose `aria-pressed` and change glyph +
accessible name between states.

### Sizes
`sm` (28) toolbars/rows · `md` (36) default · `lg` (44) touch-primary. Icon glyph scales with the
container per [Iconography](../08_Iconography_Guidelines.md).

### States
Per foundation §4. Distinctive:
- **Toggle selected:** glyph and `aria-label` both change (e.g. "Add to watchlist" ⇄ "Remove from
  watchlist"); selected also carries a non-color cue (fill/weight), never color alone.
- **Loading:** glyph → spinner in place; `aria-busy`.

### Accessibility (distinctive — critical)
- **An `aria-label` (or equivalent) is mandatory** — an icon-only button with no name is a defect
  (Inventory: "icon-only buttons carry a label"; §17).
- The glyph is `aria-hidden`; the name comes from the label, not the icon.
- Tooltip is supplementary, never the *only* source of the name (a screen-reader/keyboard user must
  get the name without hovering).
- Meaningful icon is never the sole carrier of a critical label (Inventory `Icon` rule) — pair with
  text where the action is critical and space allows.

### Responsive (distinctive)
Touch: 44px effective target minimum; tooltips (hover) are replaced by tap-to-reveal or an adjacent
label on touch (foundation §6).

### Token usage
As Button, plus `icon.*` sizing; typically `--state-hover-surface` for the default Quiet variant.

### Motion (signature)
Hover/press micro-feedback (`--motion-duration-fast`); toggle glyph cross-fades in
`--motion-duration-base`. Reduced motion → instant glyph swap.

### Usage guidelines
- **Do** give every icon button a clear `aria-label` naming the outcome.
- **Do** reserve icon-only for genuinely space-constrained, universally-understood actions
  (close, more, add/remove, expand).
- **Do** provide a tooltip echoing the name for sighted pointer users.

### Anti-patterns
- ✗ Icon-only for an unfamiliar/ambiguous action where a mistap is costly.
- ✗ Missing/duplicated `aria-label` (e.g. every row's "more" labeled identically with no context).
- ✗ Tooltip as the sole name source (fails keyboard/SR users).
- ✗ Sub-44px touch targets in touch contexts.

---

## Family cross-references
- Loading/error/success semantics: [States](../../design/13_States.md); foundation §4.
- Icon meanings and sizing: [Iconography](../08_Iconography_Guidelines.md).
- Where buttons appear per screen: [Component→Screen Coverage](../../design/09_Component_Inventory.md#component--screen-coverage).

*Family 01 of 09 · Phase 2 · Milestone 2*
