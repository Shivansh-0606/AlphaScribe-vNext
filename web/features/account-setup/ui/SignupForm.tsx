"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { FormField } from "@/components/foundation/FormField";
import { Input } from "@/components/foundation/Input";
import { Link } from "@/components/foundation/Link";
import { useSignup } from "../application/useAuth";
import { signupFormSchema, type SignupFormValues } from "../application/form-schemas";

/** SCR-02 Authentication (sign-up mode). */
export function SignupForm() {
  const router = useRouter();
  const signup = useSignup();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupFormValues>({
    resolver: zodResolver(signupFormSchema),
    defaultValues: { email: "", password: "", confirmPassword: "" },
  });

  const onSubmit = handleSubmit((values) => {
    signup.mutate(values, {
      onSuccess: () => router.replace("/workspace"),
    });
  });

  return (
    <form onSubmit={onSubmit} noValidate className="flex flex-col gap-4">
      {/* Single-channel submission feedback (see LoginForm) — Banner only, no toast. */}
      {signup.isError && (
        <Banner tone="error">
          {signup.error instanceof Error ? signup.error.message : "Sign up failed."}
        </Banner>
      )}
      <FormField label="Email" error={errors.email?.message} required>
        <Input type="email" autoComplete="email" {...register("email")} />
      </FormField>
      <FormField
        label="Password"
        error={errors.password?.message}
        required
        helpText="At least 8 characters."
      >
        <Input type="password" autoComplete="new-password" {...register("password")} />
      </FormField>
      <FormField label="Confirm password" error={errors.confirmPassword?.message} required>
        <Input type="password" autoComplete="new-password" {...register("confirmPassword")} />
      </FormField>
      <Button type="submit" loading={signup.isPending} className="w-full">
        Continue
      </Button>
      <div className="text-sm">
        <Link href="/login">Already have an account? Sign in</Link>
      </div>
    </form>
  );
}
