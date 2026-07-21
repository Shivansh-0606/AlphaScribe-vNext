import { z } from "zod";

/**
 * Form-level validation (03.8/03.9 — RHF + Zod, typed schemas). Distinct from
 * `integration/schemas.ts` (the wire contract): these add client-only rules
 * (confirmation fields, friendly messages) that never cross the API boundary.
 */

export const loginFormSchema = z.object({
  email: z.email("Enter a valid email address."),
  password: z.string().min(1, "Enter your password."),
  remember: z.boolean(),
});
export type LoginFormValues = z.infer<typeof loginFormSchema>;

export const signupFormSchema = z
  .object({
    email: z.email("Enter a valid email address."),
    password: z.string().min(8, "Use at least 8 characters."),
    confirmPassword: z.string(),
  })
  .refine((v) => v.password === v.confirmPassword, {
    message: "Passwords don't match.",
    path: ["confirmPassword"],
  });
export type SignupFormValues = z.infer<typeof signupFormSchema>;

export const forgotPasswordRequestFormSchema = z.object({
  email: z.email("Enter a valid email address."),
});
export type ForgotPasswordRequestFormValues = z.infer<typeof forgotPasswordRequestFormSchema>;

export const resetPasswordFormSchema = z
  .object({
    otp: z.string().length(6, "Enter the 6-digit code."),
    newPassword: z.string().min(8, "Use at least 8 characters."),
    confirmPassword: z.string(),
  })
  .refine((v) => v.newPassword === v.confirmPassword, {
    message: "Passwords don't match.",
    path: ["confirmPassword"],
  });
export type ResetPasswordFormValues = z.infer<typeof resetPasswordFormSchema>;

export const changePasswordFormSchema = z
  .object({
    currentPassword: z.string().min(1, "Enter your current password."),
    newPassword: z.string().min(8, "Use at least 8 characters."),
    confirmNewPassword: z.string(),
  })
  .refine((v) => v.newPassword === v.confirmNewPassword, {
    message: "Passwords don't match.",
    path: ["confirmNewPassword"],
  });
export type ChangePasswordFormValues = z.infer<typeof changePasswordFormSchema>;

export const deleteAccountFormSchema = z.object({
  email: z.email("Enter your account email to confirm."),
});
export type DeleteAccountFormValues = z.infer<typeof deleteAccountFormSchema>;
