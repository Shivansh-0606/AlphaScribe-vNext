import "@testing-library/jest-dom/vitest";
import { cleanup } from "@testing-library/react";
import { toHaveNoViolations } from "jest-axe";
import { afterEach, expect } from "vitest";

// `globals: false` in vitest.config.ts keeps test globals explicit (05.8 AD-4
// strong typing / explicitness) — so cleanup and matcher registration are
// wired here rather than relying on ambient globals.
expect.extend(toHaveNoViolations);
afterEach(() => {
  cleanup();
});

// jsdom doesn't implement the Pointer Capture API or scrollIntoView — Radix
// Select/RadioGroup/Menu primitives call these during pointer interaction and
// throw without them. Not a component bug; a known jsdom gap every Radix-based
// test suite needs to polyfill. https://github.com/radix-ui/primitives/issues/1822
if (typeof window !== "undefined") {
  if (!window.HTMLElement.prototype.hasPointerCapture) {
    window.HTMLElement.prototype.hasPointerCapture = () => false;
  }
  if (!window.HTMLElement.prototype.setPointerCapture) {
    window.HTMLElement.prototype.setPointerCapture = () => {};
  }
  if (!window.HTMLElement.prototype.releasePointerCapture) {
    window.HTMLElement.prototype.releasePointerCapture = () => {};
  }
  if (!window.HTMLElement.prototype.scrollIntoView) {
    window.HTMLElement.prototype.scrollIntoView = () => {};
  }
  // jsdom has no layout engine, so it doesn't implement ResizeObserver either
  // — Radix Tooltip's arrow sizing (`useSize`) and cmdk's `CommandList` both
  // call it on mount (Family 06, Phase 5) and throw without it.
  if (!window.ResizeObserver) {
    window.ResizeObserver = class ResizeObserver {
      observe() {}
      unobserve() {}
      disconnect() {}
    };
  }
}
