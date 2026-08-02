import { Footer } from "./Footer";

/**
 * SetupTemplate (09 Component Inventory Templates) — "GlobalHeader · Main
 * (setup) · Footer; global nav suppressed". Structurally identical to
 * PublicTemplate today (both: root-shell header, contained main, footer, no
 * GlobalNav) — its own named component because the frozen doc treats it as a
 * distinct context (authenticated + mid-setup vs. pre-session), so it can
 * diverge later (e.g. an account menu in the header) without touching Public.
 */
export function SetupTemplate({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-full flex-1 flex-col">
      <div className="mx-auto w-full max-w-md flex-1 px-4 py-12 sm:px-6">{children}</div>
      <Footer />
    </div>
  );
}
