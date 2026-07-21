# AlphaScribe vNext — Component Family 02: Text Inputs

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Phase** | M2 · Phase 2 — Core Components |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Inherits** | [Component System Foundation](00_Component_System.md) |
| **Frozen mapping** | [`Input`](../../design/09_Component_Inventory.md#input), [`SearchField`](../../design/09_Component_Inventory.md#searchfield), [`FormField`](../../design/09_Component_Inventory.md#formfield) |

> Distinctive detail only; shared contract inherited from the [foundation](00_Component_System.md).
> All three components live inside a **FormField** wrapper (label + control + help/error) in forms.

---

## Input ⟶ maps to: `Input` (Inventory Atom)

### Purpose
Capture a single line of text — email, password, filter, a company name. The workhorse control;
its calm, warm off-white field and clear focus are the tactile proof the interface is "alive."

### Anatomy
`[ optional leading icon ] · value / placeholder · [ optional trailing affordance ]` on
`--input-bg` (warm off-white) with a `--input`/`--border` hairline and `--radius-md` corners.
In a FormField it is preceded by a **label** and followed by **help text** and/or an **error
message** region (reserved height so validation doesn't shift layout).

- **Label** (`type.small`, always present) · **Control** (`type.body`, `--foreground`) ·
  **Placeholder** (`--muted-foreground`, an example not a label) · **Help text** (`type.caption`,
  `--muted-foreground`) · **Error text** (`type.caption`, `--destructive`, with icon).

### Variants
Per Inventory: **Text**, **Password (masked)**, **Search**. (Search is documented as its own
component below; Password is a Text input with a masked value + reveal toggle.)

- **Password:** masked dots; an icon-button reveal toggle (`aria-pressed`, "Show/Hide password");
  the value is **never announced back** by assistive tech (Inventory a11y rule; §17).
- **With leading icon** (e.g. a mono `@` or search glyph) / **with trailing affordance** (clear ✕,
  reveal 👁, unit suffix).

### Sizes
`sm` / `md` (default) / `lg` per foundation §3. Match the size of adjacent buttons in a row.

### States
Per foundation §4, with the Inventory's set: **Default · Focus · Filled · Invalid · Disabled**
(plus Loading where the field triggers async validation). Distinctive:
- **Focus:** field border → `--ring`, plus the focus ring — a calm, unmistakable "you are here."
- **Filled:** `--foreground` value; clear ✕ affordance appears (pointer) / persists (touch).
- **Invalid:** `--destructive` border + associated error text (never color alone); `aria-invalid`;
  on submit, focus moves to the first invalid field (§ foundation §4).
- **Disabled/Read-only:** `--opacity-disabled` + `aria-disabled`; read-only keeps text selectable.

### Accessibility (distinctive)
- Programmatic label always (visible `<label for>`); placeholder is **never** the label.
- Error text is `aria-describedby`-linked; help text likewise.
- Masked values never spoken; reveal toggle is a labeled control, keyboard operable.
- Input purpose (email, current-password) exposed for autofill where appropriate.

### Responsive (distinctive)
Full-width within its form column; label stacks above the control on all sizes (never label-inside
as the only label). Touch: 44px effective height; native keyboard type hints (email/number) via the
appropriate input semantics.

### Token usage
`--input-bg`, `--input`/`--border`, `--ring`, `--foreground`, `--muted-foreground`,
`--destructive`, `--radius-md`, `type.body`/`type.small`/`type.caption`, `--space-2/3`,
`--focus-ring-*`, `--opacity-disabled`, `--motion-duration-fast/base`.

### Motion (signature)
Focus border/ring transitions in `--motion-duration-fast`; error text reveals in
`--motion-duration-base` (slide/fade into its reserved region — no layout jump). Reduced motion →
instant border change, error text appears instantly.

### Usage guidelines
- **Do** always pair with a visible label and reserve space for help/error (no layout shift).
- **Do** validate inline and specifically; keep prior input on error (never clear the field).
- **Do** use placeholder for an *example* format, not instructions.

### Anti-patterns
- ✗ Placeholder-as-label (disappears on input; fails a11y).
- ✗ Color-only invalid state; clearing the user's input on error (loses work — Law 6).
- ✗ Pure-white/cold field (breaks warm-paper identity — Color §Anti-patterns).
- ✗ Announcing masked password characters.

---

## Search ⟶ maps to: `SearchField` (Inventory Molecule)

### Purpose
Enter and submit a search intent — the **primary focus target on Workspace Home** and the global
header's company/topic search. This is the front door to research (§7.1).

### Anatomy
Input with a **leading search glyph**, a **clear (✕)** trailing affordance, and an attached
**suggestions/recents** popover (see [Overlays](06_Overlays.md)). Optionally an inline submit or
scope selector. In the global header it is compact; on Workspace Home it is the hero control.

### Variants
Per Inventory: **Global** (header, cross-domain) and **Company** (scoped to company lookup).
Difference is scope + suggestion source, not visual identity.

### Sizes
`md` in the header; `lg` on Workspace Home (hero). Touch: 44px.

### States
Per foundation §4, with Inventory: **Default · Focus · Loading · No Results.** Distinctive:
- **Focus:** opens recent/suggested list (Progressive reveal); arrow-key navigable; Esc closes.
- **Loading:** in-field busy indicator while suggestions/results resolve — scoped, not blocking.
- **No Results:** the [No Results state](../../design/13_States.md#no-results) — shows the active
  query and offers refine/broaden/clear; never a blank dropdown.
- **Empty (Workspace Home):** invites the first search with a calm prompt, not a dead field.

### Accessibility (distinctive)
- `role="combobox"` pattern: field + listbox of suggestions; `aria-expanded`, `aria-activedescendant`.
- Result count announced on submit; suggestions keyboard operable; Enter submits, Esc closes.
- Clear button labeled ("Clear search"); focus returns to the field after clear.

### Responsive (distinctive)
Header search may collapse to an icon-button that expands to a full-width field/sheet on mobile
(navigation parity preserved — the capability never disappears, foundation §6). Suggestions become
a full-width sheet on mobile.

### Token usage
As Input, plus overlay tokens for the suggestions popover (`--elevation-3`, `--shadow-md`,
`--z-overlay`) — see [Overlays](06_Overlays.md).

### Motion (signature)
Suggestions reveal `--motion-duration-base`, `--motion-ease-out`; clear/submit micro-feedback
`--motion-duration-fast`. Reduced motion → instant open/close.

### Usage guidelines
- **Do** make it the single obvious primary target on Workspace Home.
- **Do** show recent research as first suggestions (continuity, §13).
- **Do** preserve the query on No Results and offer refine/broaden/clear.

### Anti-patterns
- ✗ Competing CTAs beside the hero search (breaks §7.1 one primary intent).
- ✗ A search that clears the query or context on empty results (loses intent).
- ✗ Suggestions reachable only by pointer (fails keyboard combobox pattern).

---

## Textarea ⟶ maps to: `Input` (multi-line) / composer base

### Purpose
Capture multi-line free text — notably the **AI Prompt Composer** base (see
[AI Components](08_AI_Components.md)) and any longer note/feedback field.

### Anatomy
Multi-line field on `--input-bg` with hairline border, `--radius-md`; optional character/context
counter (`type.caption`), auto-grow up to a max height then scroll, and (in composer use) an
attached AI action toolbar / send affordance.

### Variants
**Plain** (notes/feedback) · **Composer** (AI prompt — with send + suggestions; full spec in
[AI Components](08_AI_Components.md), this is its text base) · **Auto-grow** vs **fixed-rows**.

### Sizes
Defined by rows (min 2–3, auto-grow to a max), not the height ladder; padding from `--space-3`.
Touch: comfortable tap area, 44px min send target.

### States
Per foundation §4: **Default · Focus · Filled · Invalid · Disabled**, plus (composer)
**AI Thinking/Streaming** handled by the composer, not the textarea itself. Distinctive:
- **Auto-grow:** height changes are smooth and never push content the user is reading off-screen
  abruptly.
- **Max length / limit:** counter warns near the limit (text + color), never silently truncates.

### Accessibility (distinctive)
- Labeled; `aria-multiline`; Enter inserts newline, an explicit Send control submits (in composer,
  Enter-to-send vs Shift+Enter-newline is documented in [AI Components](08_AI_Components.md)).
- Counter changes announced politely near the limit, not on every keystroke.

### Responsive (distinctive)
Full-width; on mobile the composer send affordance stays reachable above the keyboard; auto-grow
capped so the field never consumes the whole viewport.

### Token usage
As Input; auto-grow uses no new tokens (spacing-driven).

### Motion (signature)
Auto-grow height transition `--motion-duration-fast`, `--motion-ease-standard` (subtle, never
janky). Reduced motion → instant resize.

### Usage guidelines
- **Do** auto-grow with a sensible max + internal scroll.
- **Do** show a limit counter before the user hits it.

### Anti-patterns
- ✗ Fixed tiny textarea forcing scroll for normal input.
- ✗ Silent truncation at a hidden max length.
- ✗ Enter-to-send without a documented, discoverable newline gesture.

---

## Family cross-references
- Validation & form behavior: [Interaction Patterns → Forms](../../design/10_Interaction_Patterns.md).
- Suggestions/recents overlay: [Overlays](06_Overlays.md); Composer: [AI Components](08_AI_Components.md).
- Canonical Loading/No Results/Error/Success: [States](../../design/13_States.md).

*Family 02 of 09 · Phase 2 · Milestone 2*
