import { defineConfig, devices } from "@playwright/test";

/**
 * End-to-end / journey-level testing (05.1 AD-1 "End-to-end (journey)" tier).
 * M1 foundation has no journeys yet (J-01..J-06 land with their features) —
 * this config plus one smoke test establish the harness so a journey test
 * only needs to be written, not scaffolded, when a feature lands.
 *
 * Runs on a dedicated, non-default port (not 3001) with
 * `reuseExistingServer: false` always — this app is frequently run via
 * `npm run dev` on 3001 in parallel (including by other sessions on this
 * machine), and reusing whatever happens to already be listening there
 * silently tests the WRONG server, producing confusing false failures
 * (confirmed firsthand: a stale/foreign server on the dev port was reused
 * and returned non-token colors). Isolation costs one full build+start per
 * run; that's worth never getting a misleading result again.
 */
const PORT = 4300;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: "html",
  use: {
    baseURL: `http://localhost:${PORT}`,
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: `npm run build && npx next start -p ${PORT}`,
    url: `http://localhost:${PORT}`,
    reuseExistingServer: false,
    // Was 120s, sized for the M1-era build. The component library has grown
    // enough (Families 01-07 + Overlays/SearchField, Radix/cmdk deps) that a
    // clean `next build` alone now takes ~90-160s on this machine — bumped
    // with headroom rather than re-tuning every time the build grows again.
    timeout: 300_000,
  },
});
