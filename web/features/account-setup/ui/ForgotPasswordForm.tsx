"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { FormField } from "@/components/foundation/FormField";
import { Input } from "@/components/foundation/Input";
import { Link } from "@/components/foundation/Link";
import { useForgotPassword, useResetPassword } from "../application/useAuth";
import {
  forgotPasswordRequestFormSchema,
  resetPasswordFormSchema,
  type ForgotPasswordRequestFormValues,
  type ResetPasswordFormValues,
} from "../application/form-schemas";

/**
 * SCR-02 password recovery. Two steps against two backend endpoints
 * (`/auth/forgot-password` request, `/auth/reset-password` verify): request
 * always resolves the same way regardless of account existence (backend
 * anti-enumeration), so the UI advances to the code-entry step unconditionally.
 */
export function ForgotPasswordForm() {
  const [email, setEmail] = useState<string | null>(null);
  const router = useRouter();
  const forgotPassword = useForgotPassword();
  const resetPassword = useResetPassword();

  const requestForm = useForm<ForgotPasswordRequestFormValues>({
    resolver: zodResolver(forgotPasswordRequestFormSchema),
    defaultValues: { email: "" },
  });

  const resetForm = useForm<ResetPasswordFormValues>({
    resolver: zodResolver(resetPasswordFormSchema),
    defaultValues: { otp: "", newPassword: "", confirmPassword: "" },
  });

  const onRequest = requestForm.handleSubmit((values) => {
    forgotPassword.mutate(values, { onSuccess: () => setEmail(values.email) });
  });

  const onReset = resetForm.handleSubmit((values) => {
    if (!email) return;
    resetPassword.mutate(
      { email, otp: values.otp, new_password: values.newPassword },
      { onSuccess: () => router.replace("/login") },
    );
  });

  if (!email) {
    return (
      <form onSubmit={onRequest} noValidate className="flex flex-col gap-4">
        {/* Was previously silent on failure (no Banner, no onError) — fixed: this
            mutation's own isError state now always surfaces here, same as every
            other auth form. */}
        {forgotPassword.isError && (
          <Banner tone="error">
            {forgotPassword.error instanceof Error
              ? forgotPassword.error.message
              : "Could not send the reset code."}
          </Banner>
        )}
        <FormField label="Email" error={requestForm.formState.errors.email?.message} required>
          <Input type="email" autoComplete="email" {...requestForm.register("email")} />
        </FormField>
        <Button type="submit" loading={forgotPassword.isPending} className="w-full">
          Send reset code
        </Button>
        <div className="text-sm">
          <Link href="/login">Back to sign in</Link>
        </div>
      </form>
    );
  }

  return (
    <form onSubmit={onReset} noValidate className="flex flex-col gap-4">
      <Banner tone="info">
        If an account exists for {email}, a 6-digit code was sent to that address.
      </Banner>
      {resetPassword.isError && (
        <Banner tone="error">
          {resetPassword.error instanceof Error
            ? resetPassword.error.message
            : "Could not reset your password."}
        </Banner>
      )}
      <FormField label="6-digit code" error={resetForm.formState.errors.otp?.message} required>
        <Input inputMode="numeric" autoComplete="one-time-code" {...resetForm.register("otp")} />
      </FormField>
      <FormField
        label="New password"
        error={resetForm.formState.errors.newPassword?.message}
        required
        helpText="At least 8 characters."
      >
        <Input type="password" autoComplete="new-password" {...resetForm.register("newPassword")} />
      </FormField>
      <FormField
        label="Confirm new password"
        error={resetForm.formState.errors.confirmPassword?.message}
        required
      >
        <Input
          type="password"
          autoComplete="new-password"
          {...resetForm.register("confirmPassword")}
        />
      </FormField>
      <Button type="submit" loading={resetPassword.isPending} className="w-full">
        Reset password
      </Button>
    </form>
  );
}
