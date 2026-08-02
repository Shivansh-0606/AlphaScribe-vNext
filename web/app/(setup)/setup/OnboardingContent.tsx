"use client";

import { useRouter } from "next/navigation";
import { AIAccessSelector } from "@/features/account-setup";

export function OnboardingContent() {
  const router = useRouter();
  return <AIAccessSelector variant="onboarding" onContinue={() => router.push("/workspace")} />;
}
