import { QueryClient } from "@tanstack/react-query";

/**
 * The single TanStack Query client (03.2 Server State Strategy) — the one
 * cache for all server state. No business queries are defined at this
 * foundation stage; this factory only sets sane, conservative defaults.
 *
 * `retry: false` for now — this app has no endpoints yet, so there is nothing
 * to retry against; a feature's data-fetching strategy (03.4) tunes retry/
 * staleTime per query when real queries are introduced.
 */
export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        refetchOnWindowFocus: false,
      },
    },
  });
}
