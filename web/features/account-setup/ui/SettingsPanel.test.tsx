import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { AppError } from "@/lib/errors/app-error";
import { SettingsPanel } from "./SettingsPanel";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

const toastSuccess = vi.fn();
const toastError = vi.fn();
vi.mock("sonner", () => ({
  toast: {
    success: (...args: unknown[]) => toastSuccess(...args),
    error: (...args: unknown[]) => toastError(...args),
  },
}));

const fetchIdentity = vi.fn();
const changePassword = vi.fn();
const logout = vi.fn();
const logoutEverywhere = vi.fn();
const deleteAccount = vi.fn();
vi.mock("../integration/api", () => ({
  fetchIdentity: (...args: unknown[]) => fetchIdentity(...args),
  login: vi.fn(),
  register: vi.fn(),
  logout: (...args: unknown[]) => logout(...args),
  logoutEverywhere: (...args: unknown[]) => logoutEverywhere(...args),
  forgotPassword: vi.fn(),
  resetPassword: vi.fn(),
  changePassword: (...args: unknown[]) => changePassword(...args),
  deleteAccount: (...args: unknown[]) => deleteAccount(...args),
}));

const CURRENT_USER = { id: "u1", email: "a@b.com", created_at: "now", verified: true };

describe("SettingsPanel", () => {
  beforeEach(() => {
    replace.mockClear();
    toastSuccess.mockClear();
    toastError.mockClear();
    fetchIdentity.mockReset().mockResolvedValue(CURRENT_USER);
    changePassword.mockReset();
    logout.mockReset();
    logoutEverywhere.mockReset();
    deleteAccount.mockReset();
  });

  it("shows the signed-in account's email", async () => {
    renderWithProviders(<SettingsPanel />);
    expect(await screen.findByText("Signed in as a@b.com")).toBeInTheDocument();
  });

  describe("change password", () => {
    it("validates and does not submit a mismatched confirmation", async () => {
      const { user } = renderWithProviders(<SettingsPanel />);
      await user.type(screen.getByLabelText(/^Current password/), "old-password");
      await user.type(screen.getByLabelText(/^New password/), "password123");
      await user.type(screen.getByLabelText(/^Confirm new password/), "different123");
      await user.click(screen.getByRole("button", { name: "Update password" }));
      expect(await screen.findByText("Passwords don't match.")).toBeInTheDocument();
      expect(changePassword).not.toHaveBeenCalled();
    });

    it("shows a single success toast and resets the form — no banner on success", async () => {
      changePassword.mockResolvedValueOnce({ ok: true });
      const { user } = renderWithProviders(<SettingsPanel />);
      await user.type(screen.getByLabelText(/^Current password/), "old-password");
      await user.type(screen.getByLabelText(/^New password/), "password123");
      await user.type(screen.getByLabelText(/^Confirm new password/), "password123");
      await user.click(screen.getByRole("button", { name: "Update password" }));

      await waitFor(() => expect(toastSuccess).toHaveBeenCalledWith("Password updated."));
      expect(screen.getByLabelText(/^Current password/)).toHaveValue("");
    });

    it("shows exactly one failure message — a Banner, never also a toast", async () => {
      changePassword.mockRejectedValueOnce(
        new AppError("unknown", "Current password is incorrect."),
      );
      const { user } = renderWithProviders(<SettingsPanel />);
      await user.type(screen.getByLabelText(/^Current password/), "wrong");
      await user.type(screen.getByLabelText(/^New password/), "password123");
      await user.type(screen.getByLabelText(/^Confirm new password/), "password123");
      await user.click(screen.getByRole("button", { name: "Update password" }));

      const banner = await screen.findByRole("alert");
      expect(banner).toHaveTextContent("Current password is incorrect.");
      expect(toastError).not.toHaveBeenCalled();
    });
  });

  describe("sign out", () => {
    it("redirects to /login on success", async () => {
      logout.mockResolvedValueOnce({ ok: true });
      const { user } = renderWithProviders(<SettingsPanel />);
      await user.click(screen.getByRole("button", { name: "Sign out" }));
      await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
    });

    it("regression: a failed sign-out must surface a Banner — this used to fail completely silently", async () => {
      logout.mockRejectedValueOnce(new AppError("network", "Unable to reach the server."));
      const { user } = renderWithProviders(<SettingsPanel />);
      await user.click(screen.getByRole("button", { name: "Sign out" }));

      expect(await screen.findByRole("alert")).toHaveTextContent("Unable to reach the server.");
      expect(replace).not.toHaveBeenCalled();
    });
  });

  describe("sign out everywhere", () => {
    it("regression: a failed sign-out-everywhere must surface a Banner — this used to fail completely silently", async () => {
      logoutEverywhere.mockRejectedValueOnce(new AppError("server", "Server error."));
      const { user } = renderWithProviders(<SettingsPanel />);
      await user.click(screen.getByRole("button", { name: "Sign out everywhere" }));

      expect(await screen.findByRole("alert")).toHaveTextContent("Server error.");
      expect(replace).not.toHaveBeenCalled();
    });
  });

  describe("delete account", () => {
    it("shows the confirmation dialog and validates the email field", async () => {
      const { user } = renderWithProviders(<SettingsPanel />);
      await user.click(screen.getByRole("button", { name: "Delete account" }));
      await user.click(screen.getByRole("button", { name: "Permanently delete" }));
      expect(await screen.findByText("Enter your account email to confirm.")).toBeInTheDocument();
      expect(deleteAccount).not.toHaveBeenCalled();
    });

    it("shows the failure Banner inline inside the dialog, not a toast (toast reliability under a modal isn't guaranteed)", async () => {
      deleteAccount.mockRejectedValueOnce(
        new AppError("unknown", "Email confirmation does not match."),
      );
      const { user } = renderWithProviders(<SettingsPanel />);
      await user.click(screen.getByRole("button", { name: "Delete account" }));
      const dialog = screen.getByRole("dialog");
      await user.type((await screen.findByLabelText(/^Email/)) as HTMLElement, "wrong@b.com");
      await user.click(screen.getByRole("button", { name: "Permanently delete" }));

      const banner = await waitFor(() => {
        const found = dialog.querySelector('[role="alert"]');
        expect(found).not.toBeNull();
        return found!;
      });
      expect(banner).toHaveTextContent("Email confirmation does not match.");
      expect(toastError).not.toHaveBeenCalled();
      expect(replace).not.toHaveBeenCalled();
    });

    it("redirects to /login on successful deletion", async () => {
      deleteAccount.mockResolvedValueOnce({ ok: true });
      const { user } = renderWithProviders(<SettingsPanel />);
      await user.click(screen.getByRole("button", { name: "Delete account" }));
      await user.type(await screen.findByLabelText(/^Email/), "a@b.com");
      await user.click(screen.getByRole("button", { name: "Permanently delete" }));

      await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
    });
  });
});
