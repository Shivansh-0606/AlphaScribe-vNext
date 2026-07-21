import { apiFetch } from "@/lib/api/fetch-client";
import {
  changePasswordRequestSchema,
  deleteAccountRequestSchema,
  forgotPasswordRequestSchema,
  loginRequestSchema,
  okSchema,
  registerRequestSchema,
  resetPasswordRequestSchema,
  userSchema,
  type ChangePasswordRequestBody,
  type DeleteAccountRequestBody,
  type ForgotPasswordRequestBody,
  type LoginRequestBody,
  type RegisterRequestBody,
  type ResetPasswordRequestBody,
} from "./schemas";

/**
 * Feature-scoped API access (02.2 AD-1) — the only place `account-setup`
 * touches the shared `apiFetch` (03.3 AD-1). Every call validates its own
 * request body against the same schema the backend's Pydantic model defines,
 * so a mismatch fails at the boundary instead of as a 422 surprise.
 */

export function fetchIdentity() {
  return apiFetch("/api/auth/me", userSchema);
}

export function login(body: LoginRequestBody) {
  return apiFetch("/api/auth/login", userSchema, {
    method: "POST",
    body: loginRequestSchema.parse(body),
  });
}

export function register(body: RegisterRequestBody) {
  return apiFetch("/api/auth/register", userSchema, {
    method: "POST",
    body: registerRequestSchema.parse(body),
  });
}

export function logout() {
  return apiFetch("/api/auth/logout", okSchema, { method: "POST" });
}

export function logoutEverywhere() {
  return apiFetch("/api/auth/logout-all", okSchema, { method: "POST" });
}

export function forgotPassword(body: ForgotPasswordRequestBody) {
  return apiFetch("/api/auth/forgot-password", okSchema, {
    method: "POST",
    body: forgotPasswordRequestSchema.parse(body),
  });
}

export function resetPassword(body: ResetPasswordRequestBody) {
  return apiFetch("/api/auth/reset-password", okSchema, {
    method: "POST",
    body: resetPasswordRequestSchema.parse(body),
  });
}

export function changePassword(body: ChangePasswordRequestBody) {
  return apiFetch("/api/auth/password", okSchema, {
    method: "POST",
    body: changePasswordRequestSchema.parse(body),
  });
}

export function deleteAccount(body: DeleteAccountRequestBody) {
  return apiFetch("/api/auth/me", okSchema, {
    method: "DELETE",
    body: deleteAccountRequestSchema.parse(body),
  });
}
