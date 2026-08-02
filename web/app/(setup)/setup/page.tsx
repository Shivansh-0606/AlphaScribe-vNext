import type { Metadata } from "next";
import { Heading } from "@/components/foundation/Heading";
import { OnboardingContent } from "./OnboardingContent";

export const metadata: Metadata = { title: "Onboarding & AI Setup" };

/** SCR-03 Onboarding & AI Setup — reached once, right after signup (SCR-02 UX spec's "new" branch). */
export default function SetupPage() {
  return (
    <div className="flex flex-col gap-6">
      <Heading level="h1">Set up AI access</Heading>
      <OnboardingContent />
    </div>
  );
}
