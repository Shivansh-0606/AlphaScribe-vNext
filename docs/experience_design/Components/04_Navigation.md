# AlphaScribe vNext — Component Family 04: Navigation & Wayfinding

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Phase** | M2 · Phase 2 — Core Components |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Inherits** | [Component System Foundation](00_Component_System.md) |
| **Frozen mapping** | [`Tab/SectionNav`](../../design/09_Component_Inventory.md#tab--sectionnav), [`GlobalNavigation`](../../design/09_Component_Inventory.md#globalnavigation), [`GlobalHeader`](../../design/09_Component_Inventory.md#globalheader) |

> **Governing constraint (frozen):** navigation components **introduce no new destinations**. They
> present exactly the destinations in [Navigation Structure](../../design/04_Navigation_Structure.md)
> and content levels in [Information Architecture](../../design/03_Information_Architecture.md).
> Structure and destinations are **identical across all breakpoints** — only density/presentation
> adapts (§18; no hidden-navigation anti-pattern). Current location is always exposed by more than
> color (§17).

---

## Global Navigation ⟶ maps to: `GlobalNavigation` (Inventory Organism)

### Purpose
Persistent movement between the top-level domains (Workspace, Company Research, Comparison,
Research Library, Settings, per Navigation Structure). The user's stable orientation anchor.

### Anatomy
A labeled navigation landmark listing each destination as `[ icon · label ]`, with the **current
destination** clearly marked (indicator bar/weight + `aria-current`). Sits within the persistent
app frame (WorkspaceTemplate).

### Variants
Per Inventory: **Full** (desktop — labeled items, often a left rail or header nav) · **Condensed**
(tablet — icons with labels on hover/expand) · **Drawer/sheet** (mobile — same destinations behind
a labeled menu button; see Drawer in [Overlays](06_Overlays.md)).

### Sizes
Rail width adapts (full/condensed); items follow `md` control height; touch targets ≥ 44px.

### States
**Default · Current · Hover · Focus.** Distinctive:
- **Current:** persistent indicator + `aria-current="page"` + non-color cue (weight/indicator).
- Never a "selected but ambiguous" item — exactly one current per context.

### Accessibility (distinctive)
`<nav>` landmark with an accessible name; list semantics; `aria-current` on the active destination;
fully keyboard operable; consistent tab order everywhere (Inventory rule: identical placement/behavior).

### Responsive (distinctive)
Desktop rail → tablet condensed → mobile menu button → labeled drawer. **Every destination exists
at every size** (parity); only presentation changes (§18). The drawer is a labeled dialog with
focus management (see [Overlays](06_Overlays.md)).

### Token usage
`--surface`/`--background`, `--foreground`/`--muted-foreground`, `--brand`/`--ring` (current
indicator, used sparingly), `--state-hover-surface`, `--focus-ring-*`, `--z-nav`, `icon.*`,
`type.small`.

### Motion (signature)
Current-indicator slides between items `--motion-duration-base`, `--motion-ease-standard`
(continuity). Drawer open/close per [Overlays](06_Overlays.md). Reduced motion → instant indicator move.

### Usage guidelines
- **Do** keep destinations 1:1 with Navigation Structure; mark current with `aria-current`.
- **Do** keep placement and order identical across screens and sizes.

### Anti-patterns
- ✗ Adding a destination not in Navigation Structure (scope creep — CR required).
- ✗ Hiding primary destinations behind an unlabeled menu (hidden-navigation anti-pattern §23).
- ✗ Current state by color alone.

---

## Global Header ⟶ maps to: `GlobalHeader` (Inventory Organism)

### Purpose
Persistent identity, global search entry, and account access — the same everywhere.

### Anatomy
`[ brand ] · [ SearchField (global) ] · [ account menu / notifications ]`, in a header landmark.
Two variants of contents but one placement.

### Variants
Per Inventory: **Public** (pre-auth — brand + sign-in) · **Authenticated** (brand + global search +
account/dropdown).

### States
**Default** (Inventory). Search/menu states owned by [Search](02_Text_Inputs.md) /
[Dropdown menu](03_Selection_Controls.md).

### Accessibility (distinctive)
`<header>`/`banner` landmark; consistent across screens; contains the global search combobox and a
labeled account menu; skip-link target follows it.

### Responsive
Search may collapse to an expandable control on mobile (parity preserved); brand + account remain;
header height adapts, placement constant.

### Token usage
`--surface`/`--border` (subtle bottom hairline), `--z-nav`, header composes SearchField + Dropdown
menu + Button tokens.

### Motion (signature)
None at rest (calm). Sub-components animate per their specs. Reduced motion: unaffected.

### Usage guidelines / Anti-patterns
- **Do** keep the header identical in placement/behavior on every screen (Inventory rule).
- ✗ Per-screen bespoke headers; ✗ moving global search location between screens.

---

## Tabs / Section Nav ⟶ maps to: `Tab/SectionNav` (Inventory Molecule)

### Purpose
Secondary navigation **across content levels within one domain** — the company sections
(Overview / Financials / Filings / AI Insights / Export on SCR-06). Reflects IA content levels only;
introduces no new destination.

### Anatomy
A horizontal tablist of section labels with an **active indicator** (underline/weight), optional
icons, and a linked panel region below.

### Variants
**Underline tabs** (default, editorial) · **Scrollable tabs** (overflow on narrow widths, with
affordance) · (a *Segmented Control* is the compact selector cousin — see below.)

### Sizes
`md` default; `sm` in dense contexts. Touch: 44px; horizontal scroll on overflow (never wrap into
ambiguity).

### States
Per Inventory: **Default · Active · Focus.** Distinctive:
- **Active:** indicator + weight + `aria-selected` + non-color cue.
- Panel below reflects the active tab; switching preserves each panel's scroll/context where the
  user expects (continuity).

### Accessibility (distinctive)
`role=tablist`/`tab`/`tabpanel`; Arrow keys move between tabs (roving tabindex), Enter/Space
activate (or automatic activation on focus, documented consistently), `aria-controls` links tab↔panel.

### Responsive (distinctive)
Overflow → horizontal scroll with a gradient/affordance; on mobile may become a scrollable strip or
a Select-style section picker — **all sections remain reachable** (parity).

### Token usage
`--foreground`/`--muted-foreground`, `--brand`/`--ring` (active indicator, sparing),
`--border` (rail), `--state-hover-surface`, `--focus-ring-*`, `type.small`, `--motion-duration-base`.

### Motion (signature)
Active indicator slides between tabs `--motion-duration-base`, `--motion-ease-standard`; panel
cross-fades `--motion-duration-base` (continuity, not spectacle). Reduced motion → instant switch.

### Usage guidelines
- **Do** map tabs to IA content levels only; mark active with `aria-selected` + indicator.
- **Do** keep all sections reachable at every size.

### Anti-patterns
- ✗ Tabs as top-level navigation (that's Global Navigation).
- ✗ A tab that opens a different domain/destination (scope creep).
- ✗ Active state by color alone; tabs that wrap ambiguously instead of scrolling.

---

## Segmented Control ⟶ primitive (compact exclusive selector)

### Purpose
A compact, inline **one-of-few** selector for switching a view's mode/scope — e.g. Annual/Quarterly,
Income/Balance/Cash Flow, chart range. Radio semantics in a compact, connected form.

### Anatomy
A connected group of 2–5 segments in a track; the selected segment is filled/raised; labels
(`type.small`) optionally with icons.

### Variants
**2–3 segment** (view toggle) · **up to 5** (scope). Icon-only segments require labels (a11y).

### Sizes
`sm` / `md`. Touch: each segment ≥ 44px.

### States
**Default · Hover · Focus · Selected · Disabled (segment).** Selected = fill/raise **+** non-color
cue; only one selected.

### Accessibility (distinctive)
`role=radiogroup` with `role=radio` segments (or tablist where it switches panels); Arrow keys move
and select; group labeled; selected via `aria-checked`/`aria-selected`.

### Responsive
Stays compact; if too many segments for width, promote to a Select (foundation §6). Selection model
unchanged.

### Token usage
`--muted`/`--surface` track, `--primary`/`--surface` selected fill, `--border`, `--radius-md`,
`--focus-ring-*`, `--state-*`, `type.small`.

### Motion (signature)
Selected fill slides between segments `--motion-duration-fast`, `--motion-ease-standard` — a crisp,
satisfying switch. Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** use for 2–5 exclusive, related view modes; keep labels short.
- ✗ More than ~5 segments (use Select); ✗ using it for independent toggles (use Switch/Checkbox);
  ✗ selected by color alone.

---

## Breadcrumbs ⟶ primitive (hierarchical wayfinding)

### Purpose
Show the user's location in a hierarchy and offer one-click return to an ancestor (e.g. Library ›
Reports › [Report title]; Company › Filings › [Filing]). Wayfinding, not primary navigation.

### Anatomy
An ordered trail of ancestor links separated by a `/` or `›`, ending in the current
(non-link) location.

### Variants
**Standard trail** · **Truncated** (collapse middle with an overflow "…" that expands) for deep/long
paths.

### Sizes
`sm` default (`type.caption`/`type.small`), `--muted-foreground` with the current item in
`--foreground`.

### States
**Default · Hover · Focus** (links); current item is static, marked `aria-current="page"`.

### Accessibility (distinctive)
`<nav aria-label="Breadcrumb">` + ordered list; the last item is `aria-current` and not a link;
truncation overflow is keyboard reachable.

### Responsive (distinctive)
On mobile, collapse to `‹ Parent` (a single back-to-parent affordance) — still exposing the
hierarchy path via the expandable overflow (parity of information).

### Token usage
`--muted-foreground`/`--foreground`, `--brand` (link), `type.caption`/`type.small`,
`--focus-ring-*`, `icon.*` (separator, decorative/`aria-hidden`).

### Motion (signature)
None (static wayfinding). Truncation expand: `--motion-duration-base`. Reduced motion → instant.

### Usage guidelines / Anti-patterns
- **Do** reflect the true IA hierarchy; make ancestors clickable; mark current with `aria-current`.
- ✗ Breadcrumbs that don't match the real hierarchy; ✗ a clickable current item; ✗ replacing
  primary navigation with breadcrumbs.

---

## Pagination ⟶ primitive (segmenting long lists)

### Purpose
Move through a long, segmented result/list set (Library lists, search results) without loading
everything at once (performance-aware, §21).

### Anatomy
`[ ‹ Prev ] · page markers / range · [ Next › ]`, optionally a "showing X–Y of N" summary and a
per-page selector. Alternatively a "Load more" button or infinite-scroll sentinel where more apt.

### Variants
**Numbered pagination** · **Prev/Next only** · **Load more** · **Infinite scroll** (with an
accessible "load more" fallback). Choice documented per screen; lists never lose the user's place.

### Sizes
`sm` / `md`. Touch: 44px controls.

### States
**Default · Hover · Focus · Current page · Disabled (Prev on first / Next on last) · Loading (page
fetch).** Current page marked non-color + `aria-current`.

### Accessibility (distinctive)
`<nav aria-label="Pagination">`; current page `aria-current="page"`; Prev/Next labeled and disabled
at bounds; page changes announced (result range); focus managed so the user lands at the new
content start, not scrolled away.

### Responsive (distinctive)
Numbered → Prev/Next + "page X of N" on mobile; "Load more" is often the mobile-friendly default.
No capability lost.

### Token usage
Button/Icon-button tokens; `--brand`/`--ring` current marker (sparing); `--muted-foreground`
range text; `--focus-ring-*`.

### Motion (signature)
New page content reveals via skeleton→content (`--motion-duration-base`); no whole-page jump.
Reduced motion → instant content swap.

### Usage guidelines / Anti-patterns
- **Do** keep the user's place and prior filters across pages; announce the new range.
- ✗ Resetting filters/scroll on page change (loses context); ✗ infinite scroll with no accessible
  "load more"; ✗ current page by color alone.

---

## Sidebar ⟶ primitive (persistent contextual rail)

### Purpose
A persistent contextual rail holding **Global Navigation** and/or contextual controls (e.g. filters
on Library, section nav in a workspace). Structural container, not a new destination set.

### Anatomy
A vertical region (left rail) containing nav and/or contextual groups, with an optional collapse
toggle; separated from content by a `--border` hairline (flat, per Direction C — elevated only when
it becomes an overlay drawer).

### Variants
**Navigation sidebar** (holds Global Navigation) · **Contextual sidebar** (filters/section tools) ·
**Collapsible** (expand/collapse, remembers state).

### Sizes
Expanded / collapsed (icon-rail) widths; content reflows accordingly.

### States
**Expanded · Collapsed · Hover (items) · Focus.** Collapse state persists across sessions
(continuity). Collapsed rail shows labels on hover/focus (never hides meaning).

### Accessibility (distinctive)
Contains landmark(s) (`nav`/`complementary`); collapse toggle labeled with `aria-expanded`;
collapsed icons retain accessible names; keyboard operable.

### Responsive (distinctive)
Desktop persistent rail → tablet collapsed icon-rail → mobile off-canvas **Drawer** (see
[Overlays](06_Overlays.md)) opened by a labeled menu button. Contents/destinations identical (parity).

### Token usage
`--surface`/`--background`, `--border`, `--state-hover-surface`, `--focus-ring-*`, `--z-nav`
(persistent) / `--z-drawer` (mobile overlay), `--motion-duration-base`.

### Motion (signature)
Collapse/expand width transition `--motion-duration-base`, `--motion-ease-standard`; mobile drawer
per Overlays. Reduced motion → instant width change / instant drawer.

### Usage guidelines / Anti-patterns
- **Do** persist collapse state; keep labels reachable when collapsed; maintain destination parity
  across sizes.
- ✗ A sidebar that hides destinations with no equivalent at another size (hidden-navigation §23);
  ✗ elevated/shadowed rail at rest (breaks Direction C flatness — elevate only as a mobile overlay).

---

## Family cross-references
- Mobile drawer behavior & focus management: [Overlays](06_Overlays.md).
- Destinations & hierarchy source: [Navigation Structure](../../design/04_Navigation_Structure.md),
  [Information Architecture](../../design/03_Information_Architecture.md).
- Global search within the header: [Text Inputs → Search](02_Text_Inputs.md).

*Family 04 of 09 · Phase 2 · Milestone 2*
