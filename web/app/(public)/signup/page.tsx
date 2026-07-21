import type { Metadata } from "next";
import { Heading } from "@/components/foundation/Heading";
import { SignupForm } from "@/features/account-setup";

export const metadata: Metadata = { title: "Sign up" };

export default function SignupPage() {
  return (
    <div className="mx-auto w-full max-w-md">
      <Heading level="h1" className="mb-6">
        Create your account
      </Heading>
      <SignupForm />
    </div>
  );
}
