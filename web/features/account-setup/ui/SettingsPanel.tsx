"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/foundation/Card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/foundation/Dialog";
import { FormField } from "@/components/foundation/FormField";
import { Input } from "@/components/foundation/Input";
import { Text } from "@/components/foundation/Text";
import {
  useChangePassword,
  useDeleteAccount,
  useIdentity,
  useLogout,
  useLogoutEverywhere,
} from "../application/useAuth";
import {
  changePasswordFormSchema,
  deleteAccountFormSchema,
  type ChangePasswordFormValues,
  type DeleteAccountFormValues,
} from "../application/form-schemas";

/**
 * SCR-11 Settings, account section only. AI access (Managed/BYOK) is a
 * separate authorization concern (03.7) — its key-management UI is not built
 * here; Feature Parity Tracker keeps that row as its own line item.
 */
export function SettingsPanel() {
  const router = useRouter();
  const identity = useIdentity();
  const changePassword = useChangePassword();
  const logout = useLogout();
  const logoutEverywhere = useLogoutEverywhere();
  const deleteAccount = useDeleteAccount();

  const passwordForm = useForm<ChangePasswordFormValues>({
    resolver: zodResolver(changePasswordFormSchema),
    defaultValues: { currentPassword: "", newPassword: "", confirmNewPassword: "" },
  });

  const deleteForm = useForm<DeleteAccountFormValues>({
    resolver: zodResolver(deleteAccountFormSchema),
    defaultValues: { email: "" },
  });

  const onChangePassword = passwordForm.handleSubmit((values) => {
    changePassword.mutate(
      { current_password: values.currentPassword, new_password: values.newPassword },
      {
        // Success toast is warranted here (and only here, in this component): the
        // form stays on screen with nothing else changing, so a lightweight toast is
        // the only signal the user gets that it worked. Failure stays Banner-only
        // (below, driven by mutation state) — no duplicate toast.
        onSuccess: () => {
          toast.success("Password updated.");
          passwordForm.reset();
        },
      },
    );
  });

  const onSignOut = () => logout.mutate(undefined, { onSuccess: () => router.replace("/login") });

  const onSignOutEverywhere = () =>
    logoutEverywhere.mutate(undefined, { onSuccess: () => router.replace("/login") });

  const onDeleteAccount = deleteForm.handleSubmit((values) => {
    deleteAccount.mutate({ email: values.email }, { onSuccess: () => router.replace("/login") });
  });

  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          {/* Previously silent on failure (no Banner, no onError) — fixed, same
              mutation-state-driven pattern as every other action here. */}
          {logout.isError && (
            <Banner tone="error">
              {logout.error instanceof Error ? logout.error.message : "Could not sign you out."}
            </Banner>
          )}
          <Text variant="small" className="text-muted-foreground">
            Signed in as {identity.data?.email ?? "…"}
          </Text>
          <Button
            variant="secondary"
            onClick={onSignOut}
            loading={logout.isPending}
            className="w-fit"
          >
            Sign out
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Change password</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={onChangePassword} noValidate className="flex flex-col gap-4">
            {changePassword.isError && (
              <Banner tone="error">
                {changePassword.error instanceof Error
                  ? changePassword.error.message
                  : "Could not update password."}
              </Banner>
            )}
            <FormField
              label="Current password"
              error={passwordForm.formState.errors.currentPassword?.message}
              required
            >
              <Input
                type="password"
                autoComplete="current-password"
                {...passwordForm.register("currentPassword")}
              />
            </FormField>
            <FormField
              label="New password"
              error={passwordForm.formState.errors.newPassword?.message}
              required
              helpText="At least 8 characters."
            >
              <Input
                type="password"
                autoComplete="new-password"
                {...passwordForm.register("newPassword")}
              />
            </FormField>
            <FormField
              label="Confirm new password"
              error={passwordForm.formState.errors.confirmNewPassword?.message}
              required
            >
              <Input
                type="password"
                autoComplete="new-password"
                {...passwordForm.register("confirmNewPassword")}
              />
            </FormField>
            <Button type="submit" loading={changePassword.isPending} className="w-fit">
              Update password
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Sessions</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          {logoutEverywhere.isError && (
            <Banner tone="error">
              {logoutEverywhere.error instanceof Error
                ? logoutEverywhere.error.message
                : "Could not sign out other devices."}
            </Banner>
          )}
          <Text variant="small" className="text-muted-foreground">
            Sign out of every other device signed in to this account.
          </Text>
          <Button
            variant="secondary"
            onClick={onSignOutEverywhere}
            loading={logoutEverywhere.isPending}
            className="w-fit"
          >
            Sign out everywhere
          </Button>
        </CardContent>
      </Card>

      <Card className="border-destructive/30">
        <CardHeader>
          <CardTitle>Danger zone</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-3">
          <Text variant="small" className="text-muted-foreground">
            Permanently delete your account and research history. This cannot be undone.
          </Text>
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="destructive" className="w-fit">
                Delete account
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Delete account</DialogTitle>
                <DialogDescription>
                  Type your account email to confirm. This permanently deletes your account and
                  research history.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={onDeleteAccount} noValidate className="flex flex-col gap-4">
                {/* Inline, not a toast: this dialog traps focus (Radix modal), and a
                    toast portal's reliability while a modal is open is not
                    guaranteed — the failure must be visible inside the dialog itself. */}
                {deleteAccount.isError && (
                  <Banner tone="error">
                    {deleteAccount.error instanceof Error
                      ? deleteAccount.error.message
                      : "Could not delete your account."}
                  </Banner>
                )}
                <FormField
                  label="Email"
                  error={deleteForm.formState.errors.email?.message}
                  required
                >
                  <Input type="email" autoComplete="email" {...deleteForm.register("email")} />
                </FormField>
                <DialogFooter>
                  <Button type="submit" variant="destructive" loading={deleteAccount.isPending}>
                    Permanently delete
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </CardContent>
      </Card>
    </div>
  );
}
