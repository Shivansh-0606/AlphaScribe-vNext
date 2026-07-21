import { Footer } from "./Footer";

/**
 * PublicTemplate (09 Component Inventory Templates) — public header (root
 * shell), footer, no global nav (pre-session). Owns the page container width
 * previously on the root shell's `<main>`; content picks its own max-width
 * within it (Landing wants wide, Auth wants narrow — that's a content
 * decision, not a template one).
 */
export function PublicTemplate({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-full flex-1 flex-col">
      <div className="mx-auto w-full max-w-6xl flex-1 px-4 py-12 sm:px-6 lg:px-8">{children}</div>
      <Footer />
    </div>
  );
}
