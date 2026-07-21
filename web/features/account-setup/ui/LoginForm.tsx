"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import type { Route } from "next";
import { useRouter, useSearchParams } from "next/navigation";
import { Controller, useForm } from "react-hook-form";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Checkbox } from "@/components/foundation/Checkbox";
import { FormField } from "@/components/foundation/FormField";
import { Input } from "@/components/foundation/Input";
import { Link } from "@/components/foundation/Link";
import { useLogin } from "../application/useAuth";
import { loginFormSchema, type LoginFormValues } from "../application/form-schemas";

/** SCR-02 Authentication (sign-in mode): fields -> submit -> recovery link. */
export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const login = useLogin();
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginFormSchema),
    defaultValues: { email: "", password: "", remember: false },
  });

  const onSubmit = handleSubmit((values) => {
    login.mutate(values, {
      onSuccess: () => {
        const next = searchParams.get("next");
        // Only accept an in-app relative path (never "//host" — a protocol-relative
        // URL browsers treat as absolute) to guard against an open-redirect via `next`.
        const destination =
          next && next.startsWith("/") && !next.startsWith("//") ? next : "/workspace";
        router.replace(destination as Route);
      },
    });
  });

  // Distinct from a submission-error Banner below: this explains *why the user
  // landed here* (AuthGate bounced them for a connectivity/server reason, not
  // because they're simply signed out), shown once on arrival, before any
  // submit attempt. A failed submit adds its own Banner alongside it — two
  // different true facts, not the same failure said twice.
  const bouncedForConnectivity = searchParams.get("reason") === "connection";

  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
      {bouncedForConnectivity && (
        <Banner tone="warning">
          We couldn&apos;t verify your session — this looks like a connection issue, not a sign-out.
          Please sign in again.
        </Banner>
      )}
      {/* Every submission failure (bad credentials, rate limiting, network, server) surfaces
          exactly one way: this Banner, driven directly by the mutation's own state — never
          also a toast (see the Settings/Signup forms for the same rule). */}
      {login.isError && (
        <Banner tone="error">
          {login.error instanceof Error ? login.error.message : "Sign in failed."}
        </Banner>
      )}
      <FormField label="Email" error={errors.email?.message} required>
        <Input type="email" autoComplete="email" {...register("email")} />
      </FormField>
      <FormField label="Password" error={errors.password?.message} required>
        <Input type="password" autoComplete="current-password" {...register("password")} />
      </FormField>
      <Controller
        control={control}
        name="remember"
        render={({ field }) => (
          <Checkbox
            label="Remember me"
            checked={field.value}
            onCheckedChange={(checked) => field.onChange(checked === true)}
          />
        )}
      />
      <Button type="submit" loading={login.isPending} className="w-full">
        Continue
      </Button>
      <div className="flex items-center justify-between text-sm">
        <Link href="/forgot-password">Forgot password?</Link>
        <Link href="/signup">Create an account</Link>
      </div>
    </form>
  );
}
