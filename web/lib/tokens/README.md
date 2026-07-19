# `lib/tokens` — Design token consumption (TS surface)

Typed accessors for the frozen design tokens (motion/z-index/etc.) where TS needs them. Raw values live ONLY in `styles/` (Tier-1/2) — this is a read-only consumption surface (04.2). Never redefine token values here.
