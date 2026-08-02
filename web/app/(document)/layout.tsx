import { AuthGate } from "@/features/account-setup";

/**
 * `(document)` route group — SCR-10 Report View. Login wall enforced once,
 * here, mirroring `(research)/layout.tsx` and `(workspace)/layout.tsx`
 * (02.3 AD-6 / 03.6 AD-4).
 */
export default function DocumentLayout({ children }: { children: React.ReactNode }) {
  return <AuthGate>{children}</AuthGate>;
}
