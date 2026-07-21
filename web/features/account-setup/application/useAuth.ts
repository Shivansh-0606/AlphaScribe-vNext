import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { AuthStatus } from "@/lib/types/auth";
import * as authApi from "../integration/api";
import type {
  ChangePasswordRequestBody,
  DeleteAccountRequestBody,
  ForgotPasswordRequestBody,
  LoginRequestBody,
  RegisterRequestBody,
  ResetPasswordRequestBody,
  User,
} from "../integration/schemas";

/**
 * Auth status is derived server state, never mirrored into a client store
 * (03.6 AD-5) — this query is the single source every consumer (AuthGate,
 * nav account menu, Settings) reads through.
 */
export const identityQueryKey = ["auth", "identity"] as const;

export function useIdentity() {
  return useQuery({
    queryKey: identityQueryKey,
    queryFn: authApi.fetchIdentity,
    retry: false,
    staleTime: 60_000,
  });
}

/** Collapses the identity query's tri-state into the frozen `AuthStatus` contract. */
export function useAuthStatus(): AuthStatus {
  const { data, isPending, isError } = useIdentity();
  if (isPending) return { state: "loading" };
  if (isError || !data) return { state: "unauthenticated" };
  return { state: "authenticated", userId: data.id };
}

function useSetIdentity() {
  const queryClient = useQueryClient();
  return (user: User) => queryClient.setQueryData(identityQueryKey, user);
}

/** Ends the session client-side: clears every session-scoped cache entry and client state (03.6 AD-2). */
function useClearSession() {
  const queryClient = useQueryClient();
  return () => queryClient.clear();
}

export function useLogin() {
  const setIdentity = useSetIdentity();
  return useMutation({
    mutationFn: (body: LoginRequestBody) => authApi.login(body),
    onSuccess: setIdentity,
  });
}

export function useSignup() {
  const setIdentity = useSetIdentity();
  return useMutation({
    mutationFn: (body: RegisterRequestBody) => authApi.register(body),
    onSuccess: setIdentity,
  });
}

export function useLogout() {
  const clearSession = useClearSession();
  return useMutation({
    mutationFn: authApi.logout,
    onSuccess: clearSession,
  });
}

export function useLogoutEverywhere() {
  const clearSession = useClearSession();
  return useMutation({
    mutationFn: authApi.logoutEverywhere,
    onSuccess: clearSession,
  });
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: (body: ForgotPasswordRequestBody) => authApi.forgotPassword(body),
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: (body: ResetPasswordRequestBody) => authApi.resetPassword(body),
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: (body: ChangePasswordRequestBody) => authApi.changePassword(body),
  });
}

export function useDeleteAccount() {
  const clearSession = useClearSession();
  return useMutation({
    mutationFn: (body: DeleteAccountRequestBody) => authApi.deleteAccount(body),
    onSuccess: clearSession,
  });
}
