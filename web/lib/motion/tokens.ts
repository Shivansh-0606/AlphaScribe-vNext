/**
 * Motion vocabulary bound to the frozen motion tokens (04.6; Component
 * System Foundation §7). These are the only durations/easings components may
 * use — never a raw ms value in component code (04.2 AD-3).
 *
 * Values are read from the CSS custom properties in styles/tokens.css so
 * there is exactly one source; this module just gives them typed, named
 * handles for use with the `motion` library's numeric/easing props (which
 * take JS values, not CSS var() strings).
 */

export const motionDuration = {
  instant: 0,
  fast: 0.12, // --motion-duration-fast (120ms), Motion takes seconds
  base: 0.15, // --motion-duration-base (150ms)
  slow: 0.24, // --motion-duration-slow (240ms)
} as const;

export const motionEase = {
  standard: "easeInOut", // --motion-ease-standard
  out: "easeOut", // --motion-ease-out
  in: "easeIn", // --motion-ease-in
} as const;

export type MotionDurationToken = keyof typeof motionDuration;
export type MotionEaseToken = keyof typeof motionEase;
