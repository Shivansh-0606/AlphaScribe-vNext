import { AuthGate } from "@/features/account-setup";

/**
 * `(research)` route group — SCR-06/07/08 (Company Research, Comparison,
 * Learning). Login wall enforced once, here (02.3 AD-6 / 03.6 AD-4),
 * mirroring `(workspace)/layout.tsx`. `ResearchTemplate` composition
 * (including the per-screen `SectionNav`) is owned by each screen rather
 * than this layout, since the section nav content differs per screen.
 */
export default function ResearchLayout({ children }: { children: React.ReactNode }) {
  return <AuthGate>{children}</AuthGate>;
}
