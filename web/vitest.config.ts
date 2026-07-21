import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  resolve: {
    // Mirror tsconfig's "@/*" -> "./*" alias — no need for a tsconfig-paths
    // plugin dependency for a single, static alias.
    alias: {
      "@": path.resolve(__dirname, "."),
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup/vitest-setup.ts"],
    globals: false,
    css: false,
    // The default 5000ms is too tight for a click/focus-then-findBy
    // interaction once the full suite (130+ tests, real userEvent + Radix
    // effects) runs together on a loaded machine — this doesn't fail any
    // single file in isolation, only intermittently under full-suite
    // concurrency, and rotates across unrelated test files run-to-run
    // (Dialog/Drawer/DropdownMenu one run, Tooltip/Popover the next) —
    // resource contention, not a component defect. Same class of fix as the
    // Playwright suite's `expect.poll()` additions for Card/Chip.
    testTimeout: 10000,
    exclude: ["node_modules", ".next", "tests/e2e"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html"],
      include: ["app/**", "components/**", "features/**", "lib/**", "providers/**"],
      exclude: ["**/*.d.ts", "**/*.config.*", "**/README.md"],
    },
  },
});
