import type { NextConfig } from "next";

/**
 * Next.js configuration — AlphaScribe vNext.
 *
 * Kept intentionally lean (Constitution §4.11). Only options that encode a
 * frozen architectural decision live here:
 *  - `reactStrictMode`   — surfaces unsafe lifecycles early (fail-fast, §4.13).
 *  - `poweredByHeader`    — disabled; no framework fingerprint leaked.
 *  - `typedRoutes`        — strong typing at the routing boundary (§4.9).
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  typedRoutes: true,
};

export default nextConfig;
