import type { Transition } from "motion/react";
import { motionDuration, motionEase } from "./tokens";

/**
 * The three motion "moments" named in Component System Foundation §7. Every
 * component's motion is one of these — never a bespoke duration/curve.
 */
export type MotionMoment = "micro" | "state" | "reveal";

const MOMENT_TRANSITION: Record<MotionMoment, Transition> = {
  micro: { duration: motionDuration.fast, ease: motionEase.standard },
  state: { duration: motionDuration.base, ease: motionEase.standard },
  reveal: { duration: motionDuration.slow, ease: motionEase.out },
};

/**
 * Resolves a motion moment to a `motion`-library Transition, collapsing to
 * instant when the user prefers reduced motion (04.6; foundation §7 — "no
 * information loss", never just "no motion"). Pass the value from
 * `useReducedMotion()`.
 */
export function getTransition(moment: MotionMoment, reducedMotion: boolean): Transition {
  if (reducedMotion) {
    return { duration: motionDuration.instant };
  }
  return MOMENT_TRANSITION[moment];
}
