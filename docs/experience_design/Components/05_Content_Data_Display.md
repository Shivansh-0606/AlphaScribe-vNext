# AlphaScribe vNext — Component Family 05: Content & Data Display

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Milestone / Phase** | M2 · Phase 2 — Core Components |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Inherits** | [Component System Foundation](00_Component_System.md) |
| **Frozen mapping** | [`Badge/Tag`](../../design/09_Component_Inventory.md#badge--tag), [`StatementTable`](../../design/09_Component_Inventory.md#statementtable), [`ListItem`](../../design/09_Component_Inventory.md#listitem) |

> Distinctive detail only. **Direction C rule for containers:** cards and rows sit **flat on the
> canvas at rest**; elevation appears only on interaction (hover/focus/active/selected) or for
> transient/active content. Depth is a verb, not a texture.

---

## Card ⟶ primitive (content container; base for Research cards)

### Purpose
Group related content into a single, scannable unit — the base container for Company Card, Metric
Card, News Card, Portfolio Card, etc. (composed in [Research Components](09_Research_Components.md)).

### Anatomy
`[ optional header (title · meta · action) ] · body · [ optional footer (actions / source ref) ]`
on `--surface` with a `--border` hairline and `--radius-md`. Flat at rest.

### Variants
**Static card** (display) · **Interactive card** (whole card is a link/selectable — e.g. a company
result) · **Selectable card** (radio/checkbox semantics — e.g. AI access options) · **Media/figure
card** (holds a chart or illustration).

### Sizes
Padding `--space-4` (comfortable) or `--space-3` (dense grids); width driven by the grid.

### States
Per foundation §4: **Default · Hover · Focus · Active · Selected · Loading (skeleton) · Empty ·
Error.** Distinctive:
- **Interactive/selectable:** hover/focus lifts to `--elevation-1`/`-2` + `--shadow-sm` and/or a
  `--ring` outline — the "alive on interaction" moment; selected keeps a non-color cue.
- **Loading:** a card-shaped [Skeleton](07_Feedback_Status.md) preserving layout; no fabricated data.

### Accessibility (distinctive)
An interactive card is a single focusable control with one clear accessible name and, ideally, one
primary action (avoid nested competing click targets; if secondary actions exist, they are separate
focusable controls). Selectable cards carry radio/checkbox semantics (see
[Selection Controls](03_Selection_Controls.md)).

### Responsive
Reflows within the grid (12/8/4); padding steps down on mobile; cards stack; no loss of content.

### Token usage
`--surface`/`--card`, `--border`, `--radius-md`, `--elevation-1/-2` + `--shadow-sm` (interaction
only), `--ring`/`--accent` (selected), `--state-hover-surface`, `--space-3/4`, `--focus-ring-*`.

### Motion (signature)
Hover/focus lift `--motion-duration-base`, `--motion-ease-out` (subtle, ≤ a couple px + soft
shadow). Reduced motion → instant state, no lift.

### Usage guidelines
- **Do** keep cards flat at rest; lift only on interaction; one primary action per interactive card.
- **Do** use `--surface` (warm off-white), never pure white.

### Anti-patterns
- ✗ Elevated/shadowed cards at rest (breaks Direction C calm; §12 depth-as-verb).
- ✗ Nested clickable regions with ambiguous focus/targets.
- ✗ Card grids at equal weight that become a "dashboard of everything" (§23).

---

## Table ⟶ maps to: `StatementTable` base / data tables

### Purpose
Present structured tabular data — financial statements, comparison grids, library lists — as
**accessible, scannable data** (never a "wall of numbers", §16). Base for
[Financial Tables](09_Research_Components.md).

### Anatomy
`caption/title · column headers (scope) · rows · [ optional row header column ] · [ footer/totals ]`.
Numeric cells use `type.figure` (tabular mono), decimal-aligned; sticky header (and often first
column) on scroll. Zebra/rhythm via spacing and hairlines, not heavy fills.

### Variants
**Data table** (generic) · **Financial statement** (Income/Balance/Cash Flow; annual/quarterly) ·
**Comparison table** (companies × metrics) · **Sortable** · **Selectable rows** (multi-select).

### Sizes
Row height `sm` (dense financials) / `md` (default). Column widths content-aware; numeric columns
right-aligned and decimal-aligned.

### States
Per Inventory: **Default · Loading (skeleton) · Empty · Partial Failure**, plus **Sort · Row
hover/focus/selected.** Distinctive:
- **Partial Failure:** failed cells/sections flagged explicitly (e.g. "unavailable", "not
  comparable") — **never silently blank** (Inventory rule; Partial Results facet).
- **Sort:** sorted column marked with direction + `aria-sort`.
- **Loading:** row-shaped skeletons preserving column structure.

### Accessibility (distinctive — critical for finance)
Proper `<table>` semantics: `<caption>`, `<th scope=col/row>`, header association; row/column
keyboard navigation; `aria-sort` on sorted headers; numeric meaning never color-only (▲/▼ + sign +
`bullish`/`bearish`). Large tables provide an accessible summary; charts pair with a table equivalent
(see [Chart Container](09_Research_Components.md)).

### Responsive (distinctive)
Wide tables scroll horizontally within their container (sticky header/first column) rather than
breaking layout; on mobile, dense statements may reflow to stacked "record" rows (label: value)
where clearer — **no data dropped**, only reformatted (§16, §18).

### Token usage
`--surface`/`--background`, `--border` (hairlines), `--muted-foreground` (headers/meta),
`type.figure` (mono tabular), `type.caption`, `bullish`/`bearish`/`warning`, `--state-hover-surface`,
`--state-selected`, `--focus-ring-*`, `--z-raised` (sticky header).

### Motion (signature)
Sort reorders with a brief `--motion-duration-base` settle (optional, removable); skeleton→data
cross-fade. Reduced motion → instant reorder/swap.

### Usage guidelines
- **Do** align figures on the decimal in tabular mono; pair every value with meaning; flag gaps.
- **Do** follow summary/metrics in the IA hierarchy (raw data comes *after* summary).

### Anti-patterns
- ✗ Silently omitting failed/unavailable data (breaks Partial Failure honesty).
- ✗ Color-only up/down; proportional-figure fonts for numbers; heavy grid lines/fills.
- ✗ A statement table shown *before* the summary/metrics (violates summary-before-detail).

---

## Chip ⟶ primitive (compact token: filter / input / choice)

### Purpose
A compact, interactive token — a filter selection, an applied search facet, a removable member
(e.g. a company added to a comparison), or a quick-choice (AI suggestion chips live in
[AI Components](08_AI_Components.md)).

### Anatomy
`[ optional icon ] · label · [ optional remove ✕ / caret ]` in a `--radius-pill` (or `--radius-md`)
token; `type.small`/`type.caption`.

### Variants
**Filter chip** (toggle on/off) · **Input/removable chip** (with ✕) · **Choice/suggestion chip**
(single-select action) · **Static/count chip** (non-interactive count).

### Sizes
`sm` / `md`. Touch: 44px effective for interactive chips; the ✕ is its own labeled target.

### States
**Default · Hover · Focus · Selected (filter) · Disabled.** Selected filter carries a non-color cue
(check/fill). Removable chip's ✕ is separately focusable and labeled ("Remove [X]").

### Accessibility (distinctive)
Filter chips: `aria-pressed`/checkbox semantics; choice chips: button/radio; removable chip's ✕ is a
labeled control; group of chips is labeled; keyboard operable (Enter toggles, remove via the ✕ or a
documented key).

### Responsive
Chips wrap to multiple rows; remain individually reachable; horizontal scroll for a single-line chip
bar where apt.

### Token usage
`--muted`/`--surface`/`--accent`, `--border`, `--radius-pill`/`--radius-md`, `type.small`/`caption`,
`--state-selected`, `--focus-ring-*`, `icon.*`.

### Motion (signature)
Selection/removal micro-feedback `--motion-duration-fast`; removed chip fades/collapses
`--motion-duration-base` (removable without meaning loss). Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** label removable chips' ✕; show applied filters as chips the user can clear.
- ✗ Chips as primary navigation; ✗ color-only selected; ✗ a remove target too small to hit.

---

## Badge ⟶ maps to: `Badge/Tag` (Inventory Atom)

### Purpose
Convey a **small status or category** — document status, "not comparable", a count, a financial
signal. Meaning-bearing, not decorative.

### Anatomy
`[ optional dot/icon ] · short label` in a compact token; `type.caption`/`type.label`. Non-interactive.

### Variants
Per Inventory: **Neutral · Bullish · Bearish · Warning** (+ a **Verified/AI** neutral-emerald where
semantically apt, and a **count** badge). Bullish/Bearish **only for genuine financial meaning**
(Inventory rule).

### Sizes
`sm` / `md`. Text remains legible; count badges are circular/pill.

### States
**Static** (Inventory). Inherits parent interactive state when attached to an interactive element.

### Accessibility (distinctive)
Meaning conveyed by **text, not color alone** (§17): a Bearish badge reads "Bearish"/"−" not just
red. Decorative dot is `aria-hidden`; the label carries meaning. Count badges have an accessible
name ("3 unread").

### Responsive
Constant; never truncates its (already short) label; wraps with its host.

### Token usage
`--muted`/`--surface` (neutral), `bullish`/`bearish`/`warning` (+ text), `brand`/`--ring`
(verified/AI), `type.caption`/`type.label`, `--radius-sm`/`--radius-pill`.

### Motion (signature)
Generally none. A count badge may briefly pulse on increment (`--motion-duration-fast`, removable).
Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** reserve Bullish/Bearish for real financial direction; always include a text label.
- ✗ Decorative colored badges; ✗ color-only status; ✗ long sentences in a badge (use a Chip/text).

---

## Avatar ⟶ primitive (identity mark)

### Purpose
Represent a user (account menu) or an entity where a compact identity mark helps — kept minimal, as
AlphaScribe is research-, not social-, centric.

### Anatomy
A circular (`--radius-pill`) mark showing initials on a neutral tint, or a monogram; optional small
status dot. No decorative photography by default.

### Variants
**Initials** (default) · **Icon** (generic account) · **With status dot.** Sizes `sm`/`md`/`lg`.

### States
**Static**; inherits interactive state when it is a menu trigger (then it's an Icon Button carrying
the avatar — labeled).

### Accessibility (distinctive)
Accessible name = the user/entity name (not "avatar"); when a menu trigger, labeled as such; status
dot meaning is textual too, not color-only.

### Responsive
Constant sizing per context; scales with the header.

### Token usage
`--muted`/`--secondary` (tint), `--foreground` (initials), `--radius-pill`, `type.small`,
`--focus-ring-*` (when interactive).

### Motion (signature)
None. Menu-open handled by [Dropdown menu](03_Selection_Controls.md). Reduced motion: unaffected.

### Usage guidelines / Anti-patterns
- **Do** keep avatars minimal and neutral (research product, not social); give a real accessible name.
- ✗ Decorative avatars everywhere; ✗ color-only status dot; ✗ "avatar" as the accessible name.

---

## Family cross-references
- Cards compose the Research components: [Research Components](09_Research_Components.md).
- Skeleton/loading behavior: [Feedback & Status](07_Feedback_Status.md).
- Financial tables detail & chart-equivalent tables: [Research Components](09_Research_Components.md);
  canonical states: [States](../../design/13_States.md).

*Family 05 of 09 · Phase 2 · Milestone 2*
