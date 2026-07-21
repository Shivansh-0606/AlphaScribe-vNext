# AlphaScribe vNext — Component Family 03: Selection Controls

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Phase** | M2 · Phase 2 — Core Components |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Inherits** | [Component System Foundation](00_Component_System.md) |
| **Frozen mapping** | [`FormField`](../../design/09_Component_Inventory.md#formfield) (choice), [`Input`](../../design/09_Component_Inventory.md#input), [`AIAccessSelector`](../../design/09_Component_Inventory.md#aiaccessselector) composes these |

> Distinctive detail only. **Shared rule for this family:** every selected/checked state carries a
> **non-color cue** (check mark, filled dot, knob position, weight) — never color alone (§17). All
> are native form controls or ARIA equivalents, fully keyboard operable.

---

## Checkbox ⟶ maps to: `FormField` (choice)

### Purpose
Toggle an independent boolean, or select multiple items from a set (filters, "remember me",
multi-select lists).

### Anatomy
`[ box (with check/indeterminate glyph) ] · label · [ optional help text ]`. Box is a sharp
`--radius-sm` square; checked fill uses `--primary` (ink) with a cream check, or the `--ring`
emerald for AI/verified affinity where semantically apt.

### Variants
**Single** (standalone boolean) · **Group** (multi-select list) · **Indeterminate** (parent of a
partially-selected group).

### Sizes
`sm` (16px box, dense lists/tables) · `md` (20px, default forms). Effective touch target 44px via
label+box hit area.

### States
Per foundation §4: **Default · Hover · Focus · Checked · Indeterminate · Disabled · Invalid**
(group-level required). Distinctive:
- **Checked / Indeterminate:** distinct glyphs (✓ vs –); both carry the non-color cue.
- **Group invalid:** error associated with the group (e.g. "select at least one").

### Accessibility (distinctive)
Native `<input type=checkbox>`; Space toggles; label clickable; `aria-checked` incl. `mixed` for
indeterminate; group wrapped in a labeled `fieldset`/group with `aria-describedby` for errors.

### Responsive
Label wraps beside the box; box never shrinks below 16px; touch target ≥ 44px.

### Token usage
`--primary`/`--ring`, `--input`/`--border`, `--radius-sm`, `--foreground`/`--muted-foreground`,
`--focus-ring-*`, `--state-hover-surface`, `--opacity-disabled`, `--motion-duration-fast`.

### Motion (signature)
Check glyph draws/fades in `--motion-duration-fast`, `--motion-ease-out` — a crisp, satisfying
"selected" (§19 selection feels intentional). Reduced motion → instant glyph.

### Usage guidelines
- **Do** use for independent booleans and multi-select; label the outcome.
- **Do** use indeterminate for parent-of-partial groups.

### Anti-patterns
- ✗ Checkbox where only one option is valid (use Radio).
- ✗ Color-only checked state; unlabeled checkbox.

---

## Radio ⟶ maps to: `FormField` (choice)

### Purpose
Choose **exactly one** option from a small, mutually-exclusive set (e.g. AI access mode:
Managed vs BYOK in `AIAccessSelector`).

### Anatomy
`[ circle (filled dot when selected) ] · label · [ optional description ]`, within a labeled radio
**group**. For richer choices (AI access), each option may be a **selectable card** (see
[Cards](05_Content_Data_Display.md)) wrapping the radio semantics.

### Variants
**Standard** (dot + label) · **Card radio** (selectable card, e.g. Managed AI vs BYOK, with
description and a selected outline).

### Sizes
`sm` / `md`. Card radios follow card padding.

### States
Per foundation §4: **Default · Hover · Focus · Selected · Disabled · Invalid (group).** Distinctive:
- **Selected:** filled dot **+** (card variant) `--ring` outline and non-color cue; only one
  selected per group.
- **Group required/invalid:** error at the group level; focus to the group on error.

### Accessibility (distinctive)
Native `<input type=radio>` in a `role=radiogroup`/`fieldset` with legend; **Arrow keys** move and
select within the group; Tab enters/exits the group (roving tabindex). Card radios keep this exact
keyboard model.

### Responsive
Options stack vertically on narrow widths; card radios go full-width and stack; selection model
unchanged.

### Token usage
As Checkbox, plus `--ring`/`--accent` for card-selected outline; card elevation only on
hover/focus per Direction C (flat at rest).

### Motion (signature)
Dot scales/fades in `--motion-duration-fast`; card selection outline transitions
`--motion-duration-base`. Reduced motion → instant.

### Usage guidelines
- **Do** use for one-of-few exclusive choices; show all options (don't hide behind a Select if ≤ 5).
- **Do** default to the recommended option (Managed AI is the frictionless default — Inventory rule).

### Anti-patterns
- ✗ Radio for independent booleans (use Checkbox/Switch).
- ✗ No default in a required single-choice where one is clearly recommended.
- ✗ Breaking the arrow-key group model with custom card markup.

---

## Switch ⟶ primitive (composes `FormField` semantics)

### Purpose
Toggle a setting that takes effect **immediately** (a stateful on/off), typically in Settings —
distinct from a Checkbox, which stages a value for form submission.

### Anatomy
`[ track with knob ] · label`. Off = `--muted`/neutral track, knob left; On = `--primary` or
`--brand` track, knob right. A textual On/Off or state label reinforces (non-color cue).

### Variants
**Setting switch** (immediate effect) · with optional inline "saving…/saved" acknowledgment
(Saving Research facet — quiet, reassuring).

### Sizes
`sm` / `md`. Touch target ≥ 44px including label.

### States
Per foundation §4: **Off · On · Hover · Focus · Disabled · Pending (saving).** Distinctive:
- **On/Off:** knob position **and** a state label — never color alone.
- **Pending:** brief inline busy while the change persists; reverts with a clear message on failure
  (never a silent lie about state) (§20 error philosophy; Law 6).

### Accessibility (distinctive)
`role=switch` with `aria-checked`; Space/Enter toggles; label associated; the on/off state is
programmatically and textually available. Failure to persist is announced.

### Responsive
Label left, switch right; both reachable; state label persists on all sizes.

### Token usage
`--muted`/`--primary`/`--brand-from`, `--radius-pill` (track/knob), `--focus-ring-*`,
`--motion-duration-base`, `--state-*`.

### Motion (signature)
Knob slides `--motion-duration-base`, `--motion-ease-standard` — the one place `--radius-pill` and
a sliding motion are intentional (a switch reads as physical). Reduced motion → instant position
change, no slide.

### Usage guidelines
- **Do** use only for immediate-effect settings; confirm persistence quietly.
- **Do** pair with a textual state; keep the label describing the *on* meaning.

### Anti-patterns
- ✗ Switch inside a form that requires a separate Save (use Checkbox).
- ✗ Optimistic "On" that silently fails to persist (breaks trust; §20).
- ✗ Color-only state.

---

## Select ⟶ maps to: `Input` (choice) / `FormField`

### Purpose
Choose one option from a **longer** list where showing all radios would be heavy (e.g. period
selector, currency, a settings dropdown of many values).

### Anatomy
A field (like Input) with a trailing caret; opens a **listbox** popover of options (see
[Overlays](06_Overlays.md)); selected option shown in the field; optional grouping/section headers.

### Variants
**Native-backed select** (default, best a11y/mobile) · **Custom listbox** (when grouping/rich
options needed) · **Searchable** (type-ahead filter for long lists).

### Sizes
`sm` / `md` / `lg` per §3. Menu width ≥ field width.

### States
Per foundation §4: **Default · Focus · Open · Selected · Disabled · Invalid · Loading (async
options).** Distinctive:
- **Open:** listbox elevates (`--elevation-3`), arrow-navigable; selected option marked with a
  check (non-color cue).
- **Loading options:** in-menu skeleton/spinner, not a blank menu.

### Accessibility (distinctive)
Prefer native `<select>` for robustness. Custom uses `role=listbox`/`option`, `aria-expanded`,
`aria-activedescendant`; Arrow/Home/End navigate, Enter selects, Esc closes, type-ahead jumps.
Selected communicated by `aria-selected` + check.

### Responsive (distinctive)
On mobile, opens as a native picker or a full-width bottom sheet (foundation §6); type-ahead
becomes a search field within the sheet.

### Token usage
As Input, plus overlay tokens (`--elevation-3`, `--shadow-md`, `--z-overlay`), `--state-selected`,
`--accent` (selected tint) with a check glyph.

### Motion (signature)
Menu reveal `--motion-duration-base`, `--motion-ease-out`; caret rotates `--motion-duration-fast`.
Reduced motion → instant open/close, no caret spin.

### Usage guidelines
- **Do** prefer Radio/Segmented for ≤ 5 visible options; Select for longer lists.
- **Do** make long lists searchable; mark the selected option with a check.

### Anti-patterns
- ✗ Select for 2–3 options (use Segmented/Radio — hides choices needlessly).
- ✗ Custom listbox that abandons the native keyboard model.
- ✗ Blank menu while options load.

---

## Dropdown menu ⟶ primitive (action menu; not a value input)

### Purpose
Present a list of **actions** (not values) triggered from a button/icon-button — e.g. a row's
"more" actions, an account menu, export options. (Value selection = Select above.)

### Anatomy
Trigger (button/icon-button) → **menu** popover (`--elevation-3`) of action items, optional
separators, section labels (`type.label`), destructive items styled distinctly, optional leading
icons.

### Variants
**Action menu** · **Account/overflow menu** · with a **destructive** section (confirmed separately).

### Sizes
Menu items at `sm`/`md`; menu width fits content.

### States
Per foundation §4 for items: **Default · Hover · Focus · Disabled.** Menu: **Closed · Open.**
Distinctive: destructive item uses `--destructive` label + confirmation for irreversible actions.

### Accessibility (distinctive)
`role=menu`/`menuitem`; opens on the trigger's `aria-haspopup`/`aria-expanded`; Arrow keys move,
Enter/Space activate, Esc closes and **returns focus to the trigger**; focus trapped within while
open; first item focused on open.

### Responsive (distinctive)
Becomes a bottom sheet on mobile; items get 44px targets; destructive confirmation unchanged.

### Token usage
Overlay tokens (`--elevation-3`, `--shadow-md`, `--z-overlay`), `--state-hover-surface`,
`--destructive`, `type.small`/`type.label`, `--radius-md`, `--focus-ring-*`.

### Motion (signature)
Menu reveal `--motion-duration-base`, `--motion-ease-out`, subtle origin from the trigger
(continuity). Reduced motion → instant.

### Usage guidelines
- **Do** use for actions; keep destructive actions visually distinct and confirmed.
- **Do** return focus to the trigger on close.

### Anti-patterns
- ✗ Mixing value-selection and actions in one menu ambiguously.
- ✗ Losing focus (focus goes to `<body>`) on close.
- ✗ A "more" menu hiding the *primary* action (§7.1 — primary actions stay visible).

---

## Family cross-references
- Menus/listboxes elevate via [Overlays](06_Overlays.md); selectable cards in [Content & Data Display](05_Content_Data_Display.md).
- `AIAccessSelector` composes Radio (card) + Input (key) + Notification: [AI setup flow, Component Inventory](../../design/09_Component_Inventory.md#aiaccessselector).
- Form validation: [Interaction Patterns → Forms](../../design/10_Interaction_Patterns.md).

*Family 03 of 09 · Phase 2 · Milestone 2*
