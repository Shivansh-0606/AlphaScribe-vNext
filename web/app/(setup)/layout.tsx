import { AuthGate } from "@/features/account-setup";
import { SetupTemplate } from "@/components/layouts/SetupTemplate";

/** SetupTemplate group — reached only once signed in (post-signup), same login wall as (workspace). */
export default function SetupLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGate>
      <SetupTemplate>{children}</SetupTemplate>
    </AuthGate>
  );
}
