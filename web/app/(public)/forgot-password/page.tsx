import type { Metadata } from "next";
import { Heading } from "@/components/foundation/Heading";
import { ForgotPasswordForm } from "@/features/account-setup";

export const metadata: Metadata = { title: "Reset your password" };

export default function ForgotPasswordPage() {
  return (
    <div className="mx-auto w-full max-w-md">
      <Heading level="h1" className="mb-6">
        Reset your password
      </Heading>
      <ForgotPasswordForm />
    </div>
  );
}
