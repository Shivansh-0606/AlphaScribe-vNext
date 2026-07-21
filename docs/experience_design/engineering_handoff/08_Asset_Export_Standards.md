# AlphaScribe vNext — Asset Export Standards

| Field | Value |
|-------|-------|
| **Document Status** | 🧊 Frozen |
| **Milestone / Doc** | M3 · Asset Export Standards (08) |
| **Owner** | Experience Design Department |
| **Last Updated** | 2026-07-18 |

## Purpose

Specify the **mechanics** of exporting and storing design assets — SVG/PNG standards, naming, folder
organization, and version control — so assets land in the repo consistently, optimized, and traceable to
their design source. Complements [07 Asset Guide](07_Icon_Illustration_Asset_Guide.md) (what the assets
are) with **how they are produced and stored**.

## Scope

SVG standards, PNG/raster usage and export, naming conventions, folder organization, version-control
strategy. **Out of scope:** asset meaning/usage ([07]) and Figma export configuration UI ([09]).

## Decision Rationale

- **SVG-first** keeps assets crisp at every DPI, themeable via `currentColor`, and tiny — matching the
  precise, editorial identity and performance-aware design (§21).
- **Deterministic naming + folders** make assets discoverable and diff-able in git, and let tooling
  (SVGO, sprite generation) run predictably.

## 1. SVG Standards

- **Optimized on export** (SVGO): strip editor metadata, comments, hidden layers, and absolute positions;
  round coordinates sensibly.
- **`currentColor`** for icons and monochrome marks (inherits token color); multi-color illustrations use
  the frozen token hex values only.
- **`viewBox` present**, no fixed pixel `width`/`height` baked in (size via CSS); square icon viewboxes.
- **Accessibility:** decorative → `aria-hidden`/empty `<title>` omitted; meaningful standalone SVG → a
  `<title>`/labelled wrapper. No raster embedded inside "SVG".
- **No scripts, no external refs** inside SVG (security + portability).

## 2. PNG / Raster Usage

- **Raster is the exception**, used only where vector genuinely can't represent the asset (rare
  illustrations, platform app-icon/favicon slots, social share images).
- **Export at 1×/2×/3×** (or a single high-DPI where appropriate); provide `srcset` for responsive raster.
- Optimize (lossless for UI, appropriate compression for photos); prefer modern formats (WebP/AVIF) for
  large raster where supported, with fallbacks.
- **Never** rasterize an icon or a mark that could be SVG.

## 3. Naming Conventions

- **`kebab-case`, semantic by role** (not appearance): `icon-source.svg`, `empty-research.svg`,
  `logo-alphascribe.svg`, `illustration-onboarding-ai.svg`.
- **Prefix by kind:** `icon-`, `illustration-`, `logo-`; state/context suffix where needed
  (`empty-comparison`, `error-generic`).
- **DPI suffix for raster:** `-1x`, `-2x`, `-3x`. **No spaces, no camelCase, no version numbers in the
  filename** (git holds history).

## 4. Folder Organization

Design sources under `design/`, production exports under the app's `public/assets/` (per
[01 Handoff Guide §Folder Org](01_Handoff_Guide.md#2-folder-organization-expected-shape-not-mandated-code)):

```
design/                             (design sources — read-only to Engineering)
├── icons/                          custom/source icons (if any beyond Phosphor)
├── illustrations/                  illustration masters
├── assets/                         logo, brand marks
└── exports/                        generated export drop (staging)

public/assets/                      (production, consumed by the app)
├── icons/                          (mostly Phosphor components; static SVG only if needed)
├── illustrations/
├── logo/
└── favicon/  (app-icon/favicon raster set)
```

Icons are primarily **Phosphor React components** (no file per icon); this tree is for the *custom* and
*brand* assets that aren't Phosphor.

## 5. Version Control Strategy

- **Assets live in git** alongside code; changes go through **PR + Design QA** ([10](10_Design_QA_Process.md)).
- **Figma is the design source of truth** ([09](09_Figma_Organization_Guide.md)); repo assets are
  **exported from it**, never hand-edited in the repo (an edited-in-repo asset diverges from the source).
- **Traceability:** an asset PR references the Figma frame/component it came from.
- **Large binaries:** keep raster small; use Git LFS only if genuinely large assets appear (prefer SVG so
  this rarely arises).
- **Deprecation:** removing an asset follows the deprecation flow in [13 Governance](13_Design_System_Governance.md)
  (mark deprecated → confirm no references → remove).

## References to Previous Milestones

[Iconography](../08_Iconography_Guidelines.md) · [Illustration](../09_Illustration_Guidelines.md) ·
[07 Asset Guide](07_Icon_Illustration_Asset_Guide.md) · Constitution §21 (performance-aware).

## Best Practices

- Run SVGO in the export pipeline; verify `currentColor`/`viewBox` survive optimization.
- Keep one export drop (`design/exports/`) → reviewed → moved to `public/assets/` so staging is visible.
- Reference the Figma source in every asset PR for traceability.

## Anti-patterns

- ✗ Hand-editing exported assets in the repo (diverges from Figma). ✗ Raster where SVG works. ✗ Version
  numbers in filenames. ✗ Unoptimized SVG with editor cruft. ✗ Scripts/external refs in SVG.

## Engineering Considerations

- Consider an SVG sprite or per-component import for custom icons; Phosphor handles the icon bulk.
- Favicon/app-icon set generated once from the SVG master into the required platform sizes.
- Next.js `Image`/static import for raster with proper sizing; SVGs inlined where `currentColor` theming
  is needed.

## Accessibility Considerations

- Exported meaningful assets keep their `<title>`/label; decorative ones export `aria-hidden`-ready. No
  asset conveys state without an accompanying text cue ([06](06_Accessibility_Implementation_Guide.md)).

## Future Maintenance

Update when the asset pipeline or hosting changes; keep naming/folder rules stable (they're referenced by
tooling). Governed by [13](13_Design_System_Governance.md).

---

*Experience Design Department · Milestone 3 · Document 08 of 14*
