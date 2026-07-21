import type { Metadata } from "next";
import { Heading } from "@/components/foundation/Heading";
import { SettingsPanel } from "@/features/account-setup";

export const metadata: Metadata = { title: "Settings" };

export default function SettingsPage() {
  return (
    <div className="flex flex-col gap-6">
      <Heading level="h1">Settings</Heading>
      <SettingsPanel />
    </div>
  );
}
