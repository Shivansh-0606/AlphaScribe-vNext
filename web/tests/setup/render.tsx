import { QueryClientProvider } from "@tanstack/react-query";
import { render, type RenderOptions } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement, ReactNode } from "react";
import { createQueryClient } from "@/lib/api/query-client";
import { TooltipProvider } from "@/components/ui/tooltip";

/**
 * Render helper that wraps components in the same providers the app composes
 * at the root (providers/AppProviders.tsx), so component tests exercise
 * realistic context (05.1 AD-3 — test at the right boundary) without
 * duplicating that composition in every test file. Also returns a ready
 * `user` (userEvent) instance — keyboard/pointer interaction is how most
 * component tests exercise behavior, so every caller needs one.
 */
function AllProviders({ children }: { children: ReactNode }) {
  return (
    <QueryClientProvider client={createQueryClient()}>
      <TooltipProvider delayDuration={300}>{children}</TooltipProvider>
    </QueryClientProvider>
  );
}

export function renderWithProviders(ui: ReactElement, options?: Omit<RenderOptions, "wrapper">) {
  return {
    user: userEvent.setup(),
    ...render(ui, { wrapper: AllProviders, ...options }),
  };
}

export * from "@testing-library/react";
