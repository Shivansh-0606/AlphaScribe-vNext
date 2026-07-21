import { AuthGate } from "@/features/account-setup";
import { WorkspaceTemplate } from "@/components/layouts/WorkspaceTemplate";

/** WorkspaceTemplate group — the login wall is enforced once, here (02.3 AD-6 / 03.6 AD-4). */
export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGate>
      <WorkspaceTemplate>{children}</WorkspaceTemplate>
    </AuthGate>
  );
}
