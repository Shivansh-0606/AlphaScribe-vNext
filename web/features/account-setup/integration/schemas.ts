import { z } from "zod";

/**
 * Response/request shapes for the `account-setup` feature's backend contract
 * (backend/server.py `/auth/*`, stdlib session auth — project guide). Mirrors
 * the Pydantic request models and `auth.public_user()` field-for-field; this
 * is the trust boundary (03.3 AD-3) — nothing beyond this module assumes the
 * response shape without validating it first.
 */

export const userSchema = z.object({
  id: z.string(),
  email: z.string(),
  created_at: z.string(),
  verified: z.boolean(),
  is_admin: z.boolean().default(false),
});
export type User = z.infer<typeof userSchema>;

export const okSchema = z.object({ ok: z.literal(true) });

export const loginRequestSchema = z.object({
  email: z.string().max(254),
  password: z.string().max(256),
  remember: z.boolean(),
});
export type LoginRequestBody = z.infer<typeof loginRequestSchema>;

export const registerRequestSchema = z.object({
  email: z.string().max(254),
  password: z.string().min(8).max(256),
});
export type RegisterRequestBody = z.infer<typeof registerRequestSchema>;

export const forgotPasswordRequestSchema = z.object({ email: z.string().max(254) });
export type ForgotPasswordRequestBody = z.infer<typeof forgotPasswordRequestSchema>;

export const resetPasswordRequestSchema = z.object({
  email: z.string().max(254),
  otp: z.string().length(6),
  new_password: z.string().min(8).max(256),
});
export type ResetPasswordRequestBody = z.infer<typeof resetPasswordRequestSchema>;

export const changePasswordRequestSchema = z.object({
  current_password: z.string().max(256),
  new_password: z.string().min(8).max(256),
});
export type ChangePasswordRequestBody = z.infer<typeof changePasswordRequestSchema>;

export const deleteAccountRequestSchema = z.object({ email: z.string().max(254) });
export type DeleteAccountRequestBody = z.infer<typeof deleteAccountRequestSchema>;
