import { z } from "zod";

/**
 * Typed, validated environment configuration (05.4).
 *
 * Configuration is data, not scattered `process.env` reads (AD-1): it is parsed
 * once, here, against an explicit schema, and consumed through this single typed
 * contract (AD-6). Invalid/missing config FAILS FAST with a clear diagnostic at
 * module load (AD-5, §4.13) rather than surfacing as a confusing runtime error.
 *
 * PUBLIC/SECRET BOUNDARY (AD-2, absolute): only `NEXT_PUBLIC_*` values are
 * client-safe. Server-only secrets belong in `serverSchema` and must NEVER be
 * given a `NEXT_PUBLIC_` prefix. Do not read secrets from this module in code
 * that can run on the client.
 */

const clientSchema = z.object({
  NEXT_PUBLIC_APP_URL: z.url().default("http://localhost:3001"),
  NEXT_PUBLIC_API_BASE_URL: z.url().default("http://localhost:8001"),
});

const serverSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  // Server-only secrets go here (never NEXT_PUBLIC_*). None required yet —
  // backend owns authentication and session issuance (03.3 AD-7).
});

/**
 * Next inlines `process.env.NEXT_PUBLIC_*` only at literal reference sites, so
 * each client var must be named explicitly rather than spread from process.env.
 */
const clientResult = clientSchema.safeParse({
  NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
});

if (!clientResult.success) {
  throw new Error(
    `Invalid public environment configuration:\n${z.prettifyError(clientResult.error)}`,
  );
}

/** Parse server config only where there is no client bundle to leak into. */
function parseServerEnv(): z.infer<typeof serverSchema> {
  const result = serverSchema.safeParse(process.env);
  if (!result.success) {
    throw new Error(`Invalid server environment configuration:\n${z.prettifyError(result.error)}`);
  }
  return result.data;
}

/** Client-safe configuration. Safe to import anywhere. */
export const clientEnv = clientResult.data;

/**
 * Server-only configuration. Importing this from client code is a boundary
 * violation; it throws to fail fast rather than shipping server config to the
 * browser.
 */
export const serverEnv =
  typeof window === "undefined"
    ? parseServerEnv()
    : (new Proxy({} as z.infer<typeof serverSchema>, {
        get() {
          throw new Error("serverEnv must not be accessed on the client (05.4 AD-2).");
        },
      }) as z.infer<typeof serverSchema>);

export type ClientEnv = typeof clientEnv;
export type ServerEnv = z.infer<typeof serverSchema>;
