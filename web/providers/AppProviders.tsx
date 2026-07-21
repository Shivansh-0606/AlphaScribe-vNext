"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { Toaster } from "sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { createQueryClient } from "@/lib/api/query-client";

/**
 * Global client providers, composed once at the root (Phase 3).
 *
 * No Theme Provider: the product ships a single frozen light theme with no
 * runtime switching (04.3 AD-3) — the token layer applied in globals.css IS
 * the theme; there is no state to provide.
 *
 * `TooltipProvider` (Phase 5, Family 06): `delayDuration={300}` realizes the
 * spec's "slight delay on hover-in (avoid flicker)" — the generated
 * default (0ms) shows a tooltip on every incidental pointer pass.
 */
export function AppProviders({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(createQueryClient);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider delayDuration={300}>{children}</TooltipProvider>
      <Toaster
        position="bottom-right"
        theme="light"
        toastOptions={{
          classNames: {
            toast: "bg-surface! text-foreground! border-border!",
            title: "text-foreground!",
            description: "text-muted-foreground!",
          },
        }}
      />
    </QueryClientProvider>
  );
}
