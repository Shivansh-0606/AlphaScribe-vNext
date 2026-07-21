import type { Metadata } from "next";
import { Suspense } from "react";
import { Heading } from "@/components/foundation/Heading";
import { Loader } from "@/components/foundation/Loader";
import { LoginForm } from "@/features/account-setup";

export const metadata: Metadata = { title: "Sign in" };

export default function LoginPage() {
  return (
    <div className="mx-auto w-full max-w-md">
      <Heading level="h1" className="mb-6">
        Sign in
      </Heading>
      {/* LoginForm reads `?next=` via useSearchParams — needs a Suspense boundary (Next.js App Router). */}
      <Suspense fallback={<Loader />}>
        <LoginForm />
      </Suspense>
    </div>
  );
}
