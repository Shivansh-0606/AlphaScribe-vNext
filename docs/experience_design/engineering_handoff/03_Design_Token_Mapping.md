# AlphaScribe vNext — Design Token Mapping

| Field | Value |
|-------|-------|
| **Document Status** | 📝 Draft |
| **Milestone / Doc** | M3 · Design Token Mapping (03) |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |
| **Canonical source** | [Design Tokens](../10_Design_Tokens.md) (frozen) — this doc maps, never redefines |

## Purpose

Map **every** frozen design token to its intended **engineering implementation** in the vNext stack
(CSS variables + Tailwind CSS v4 `@theme` + shadcn/ui theming), so Engineering consumes tokens with
zero interpretation. Values are **not** restated authoritatively here — [Design Tokens](../10_Design_Tokens.md)
owns them; this document says **where each token lives and how it is used**.

## Scope

**In scope:** the delivery mechanism and usage intent for all token families — Color, Typography,
Spacing, Grid, Radius, Border, Elevation, Shadow, Opacity, Layer (z-index), Motion, Focus, Interaction
State. **Out of scope:** the values themselves (frozen upstream) and framework code (this is intent).

## Decision Rationale

- **Two-tier token model** (primitive → semantic) is the industry-standard way to keep meaning stable
  while allowing the delivery layer to change. It also makes the CR-VIS stack uncertainty irrelevant to
  design: values are frozen; only tier-3 plumbing differs by stack.
- **CSS variables as the runtime source** matches the existing, proven theme (HSL vars consumed via
  `hsl(var(--token))`) and Tailwind v4's CSS-first design — so the token layer is one artifact, not two.
- **shadcn maps onto our variables** (shadcn already expects CSS-variable theming), so adopting it costs
  no divergence from the frozen palette.

## Token Delivery Model (how all tokens are implemented)

```
Tier 1 — Primitive values      the frozen numbers/hex/HSL in 10_Design_Tokens.md (the ONLY place raw values exist)
        ↓ declared once as CSS custom properties
Tier 2 — Semantic CSS variables  :root { --background, --foreground, --brand-from, --space-4, … }   (Tailwind v4 @theme)
        ↓ referenced by name
Tier 3 — Consumption            Tailwind utilities (bg-background, text-foreground, p-4) · shadcn theme vars · component styles
```

**Rules for every family below:**
- Tier-1 values live **only** in [Design Tokens](../10_Design_Tokens.md); the generated Tier-2 layer is
  single-sourced from it and never hand-edited.
- Components reference **Tier-2 names** (via Tailwind utility or `var(--token)`), never Tier-1 literals.
- A needed value that doesn't exist → **new token in the owning M1 doc via CR**, never an inline literal.

---

## 1. Color Tokens

**Source:** [Color System](../02_Color_System.md) · [Design Tokens §1](../10_Design_Tokens.md#1-color-tokens).
**Mechanism:** HSL components stored per token; consumed as `hsl(var(--token))` so opacity/lightness
stay tunable. Tailwind v4 `@theme` maps semantic color utilities to these variables; shadcn's
`--background`/`--foreground`/`--primary`/`--ring`/etc. are **bound to the same variables** (not a
parallel palette).

| Token group | Tokens | Tailwind/shadcn intent | Usage rule |
|-------------|--------|------------------------|------------|
| Surfaces/text | `--background`, `--surface`, `--surface-hover`, `--card(-foreground)`, `--popover(-foreground)`, `--foreground`, `--muted(-foreground)`, `--border`, `--input`, `--input-bg`, `--code-bg` | `bg-background`, `bg-surface`, `text-foreground`, `text-muted-foreground`, `border-border` … | Warm paper + ink; never pure white/black; `--muted-foreground` for secondary text only |
| Primary/secondary/accent | `--primary(-foreground)`, `--secondary(-foreground)`, `--accent(-foreground)` | shadcn `primary`/`secondary`/`accent` bound here | `--primary` = ink-navy solid actions; `--accent` = quiet emerald tint (never body text on it) |
| Signature signal | `--brand-from`, `--brand-to`, `--ring` | a gradient utility (from/to) + `ring` = `--ring` | **Reserved**: primary action, AI/verified/evidence, focus — nowhere else (dilutes signal) |
| Financial/semantic | `bullish` `#059669`, `bearish` `#DC2626`, `warning` `#D97706`, `--destructive(-foreground)`, `brand` `#047857` | `text-bullish`/`text-bearish`/`text-warning`, shadcn `destructive` | **Meaning only, never decoration**; always with a non-color cue (sign/arrow/text) |
| Data-viz ramp | `--chart-1`…`--chart-5` | chart series colors (recharts) | **Series distinction only**; series must also be distinguishable without color (label/pattern) |

**Contrast is frozen AA** — do not re-tune a color for aesthetics; a change is a CR against Color +
Accessibility. **No new accent hue** outside the chart ramp without a CR.

---

## 2. Typography Tokens

**Source:** [Typography](../03_Typography_System.md) · [Tokens §2](../10_Design_Tokens.md#2-typography-tokens).
**Mechanism:** font families via `--font-sans` (IBM Plex Sans) / `--font-mono` (IBM Plex Mono) loaded
with `next/font` (self-hosted, no layout shift); size/weight/leading/tracking as CSS variables mapped
into Tailwind's type scale; semantic roles (`type.h1`…`type.figure`) implemented as small composition
classes/utilities.

| Family | Tokens | Intent |
|--------|--------|--------|
| Families | `--font-sans`, `--font-mono` | Sans = body/UI/headings; Mono = figures, `type.label`, code. Load with `next/font`; set `font-feature-settings` `ss01,ss02,cv01` on sans; tabular figures on mono |
| Sizes | `--text-2xs`…`--text-display` (10→48) | Tailwind `text-*` mapped to these; **rem-based** (respect user zoom) |
| Weights | `--font-weight-regular/medium/semibold/bold` (400/500/600/700) | Mono ships 400/500/600 — **never synthesize** absent weights |
| Line height | `--leading-tight/snug/normal/relaxed` | `--leading-normal` (1.55) body; `--leading-relaxed` long-form learning |
| Tracking | `--tracking-tight/normal/label` | `--tracking-label` (0.22em) only for uppercase `label-mono` |
| Roles | `type.display/h1/h2/h3/body/body-strong/small/caption/label/figure/code` | Implement as composition utilities; **hierarchy from role, not ad-hoc sizes** |

**`type.figure` (tabular mono) for all financial values**, decimal-aligned. Headings sequential (h1→h3,
no skips) — semantic *and* visual.

---

## 3. Spacing Tokens

**Source:** [Spacing](../04_Spacing_System.md) · [Tokens §3](../10_Design_Tokens.md#3-spacing-tokens).
**Mechanism:** `--space-0`…`--space-10` (0,4,8,12,16,24,32,40,48,64,96) as CSS vars mapped to Tailwind's
spacing scale so `p-4`, `gap-3`, `mt-6` resolve to tokens. **All** padding/margin/gap uses this scale;
no arbitrary `p-[13px]`.

| Token | px | Common use |
|-------|----|-----------| 
| `--space-1…4` | 4/8/12/16 | Control padding, tight gaps, component internals |
| `--space-5…7` | 24/32/40 | Section gaps, card padding, group separation |
| `--space-8…10` | 48/64/96 | Page rhythm, major regions, hero spacing |

Rhythm is 4/8-based; the sizing ladder in [Component System §3](../Components/00_Component_System.md#3-sizing-system)
composes control heights from these.

---

## 4. Grid Tokens

**Source:** [Grid](../05_Grid_System.md) · [Tokens §4](../10_Design_Tokens.md#4-grid-tokens).
**Mechanism:** breakpoints `--bp-mobile/tablet/desktop/wide` map to Tailwind screens; `--grid-columns`
(12/8/4), `--grid-gutter`, `--grid-margin`, `--grid-max-content`, `--reading-max` (~68–75ch) drive
CSS grid/container. Full behavior in [04 Responsive Guide](04_Responsive_Implementation_Guide.md).

---

## 5. Radius Tokens

**Source:** [Shape](../07_Shape_Radius_System.md) · [Tokens §5](../10_Design_Tokens.md#5-radius-tokens).
`--radius` (0, base sharp) · `--radius-sm` (2) · `--radius-md` (4) · `--radius-pill` (9999) → Tailwind
`rounded-*`; shadcn's `--radius` bound to `--radius-md`. **Sharp/editorial identity** — `--radius-pill`
only for chips/avatars/switch track; do not soften the system.

## 6. Border Tokens

**Source:** [Shape](../07_Shape_Radius_System.md) · [Tokens §6](../10_Design_Tokens.md#6-border-tokens).
`--border-width` (1) · `--border-color` (→ `--border`) · `--border-strong` · `--focus-ring-width` (2).
Hairline borders + whitespace carry structure (not heavy boxes).

## 7. Elevation Tokens

**Source:** [Elevation](../06_Elevation_Shadow_System.md) · [Tokens §7](../10_Design_Tokens.md#7-elevation-tokens).
`--elevation-0`(canvas)…`-4`(modal). **Direction C rule:** surfaces are flat (`-0`) at rest; elevation
is *summoned* on interaction/for transient/active content, then recedes. Elevation pairs with a shadow
token (§8) and a z-index token (§10).

## 8. Shadow Tokens

**Source:** [Elevation](../06_Elevation_Shadow_System.md) · [Tokens §8](../10_Design_Tokens.md#8-shadow-tokens).
`--shadow-none/sm/md/lg` (soft, warm-neutral, low-opacity) → Tailwind `shadow-*`. Mapping: `-sm`→
elevation-2 (contextual), `-md`→elevation-3 (overlays), `-lg`→elevation-4 (modals). **Never colored/hard
shadows.**

## 9. Opacity Tokens

**Source:** [Tokens §9](../10_Design_Tokens.md#9-opacity-tokens). `--opacity-disabled` (0.45),
`--opacity-muted` (0.65), `--opacity-scrim` (0.55), `--opacity-full` (1). **Disabled is never opacity
alone** — always plus `aria-disabled` + removed affordance.

## 10. Layer (Z-index) Tokens

**Source:** [Tokens §10](../10_Design_Tokens.md#10-layering-z-index-tokens). `--z-base`(0) · `-raised`(10)
· `-nav`(100) · `-drawer`(200) · `-overlay`(300) · `-modal`(400) · `-toast`(500). **Only these** — no
ad-hoc `z-[9999]`. Overlays ([06 Overlays](../Components/06_Overlays.md)) consume these + matching shadow.

## 11. Motion Tokens

**Source:** [Motion §11](../10_Design_Tokens.md#11-motion-tokens) · Constitution §14. Durations
`--motion-duration-instant/fast/base/slow/stream` (0/120/150/240/contextual); easings
`--motion-ease-standard/out/in/emphasis`. **Mechanism:** exposed as CSS variables *and* consumed by the
**Motion** library (target stack) for orchestrated animation; reduced-motion collapses durations to
`instant`. Full per-animation spec: [05 Motion Specifications](05_Motion_Specifications.md).

## 12. Focus Tokens

**Source:** [Tokens §12](../10_Design_Tokens.md#12-focus-ring-tokens). `--focus-ring-color` (→ `--ring`,
deep emerald AA) · `--focus-ring-width` (2) · `--focus-ring-offset` (2). Applied on **all** interactive
elements via `:focus-visible`; shadcn `ring` bound to these. **Focus is styled, never removed.**

## 13. Interaction State Tokens

**Source:** [Tokens §13](../10_Design_Tokens.md#13-interaction-state-tokens). `--state-hover-surface`,
`--state-hover-emphasis`, `--state-active`, `--state-selected` (accent + non-color cue), `--state-focus`
(composes focus tokens), `--state-disabled` (opacity + non-opacity cue). These implement the shared
state model in [Component System §4](../Components/00_Component_System.md#4-universal-state-model).

---

## Token Compliance (how "no raw values" is enforced)

1. **Generated Tier-2 layer** single-sourced from [Design Tokens](../10_Design_Tokens.md).
2. **Lint rule**: fail CI on raw hex/px/ms/z-index in component styles (allow only in the token layer).
3. **Design QA** ([10](10_Design_QA_Process.md)) includes a token-compliance pass.

## References to Previous Milestones

[Design Tokens](../10_Design_Tokens.md) (canonical) + all M1 foundations (02–09) + [Color](../02_Color_System.md)/[Type](../03_Typography_System.md)/[Spacing](../04_Spacing_System.md)/[Elevation](../06_Elevation_Shadow_System.md)/[Shape](../07_Shape_Radius_System.md); Constitution §11/§12/§14/§17.

## Best Practices

- Single-source the generated layer; treat Tier-1 as read-only frozen data.
- Bind shadcn theme variables to our tokens at setup so primitives inherit the palette for free.
- Prefer semantic utilities (`bg-surface`) over `var()` in components for readability.

## Anti-patterns

- ✗ Raw literals in components. ✗ A parallel shadcn palette. ✗ Introducing a token value inline.
- ✗ Re-tuning a frozen color/contrast for looks. ✗ Ad-hoc z-index/opacity.

## Engineering Considerations

- Tailwind v4 `@theme` is the natural home for the Tier-2 layer; if the stack stays CRA (CR-VIS-01/03),
  the same variables live in a global stylesheet + Tailwind 3 config — mapping intent is unchanged.
- Fonts via `next/font` (or self-hosted in CRA) to preserve tabular figures and avoid CLS.

## Accessibility Considerations

Focus, contrast-safe color pairings, and non-opacity-only disabled states are **encoded as tokens** so
the accessible path is the default. Never override a token's contrast locally. Full contract: [06](06_Accessibility_Implementation_Guide.md).

## Future Maintenance

New value → add a token in its owning M1 doc via CR, regenerate the layer. Never diverge the generated
layer from [Design Tokens](../10_Design_Tokens.md). Governed by [13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 03 of 14*
