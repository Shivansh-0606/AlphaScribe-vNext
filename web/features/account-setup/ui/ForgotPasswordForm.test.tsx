import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { AppError } from "@/lib/errors/app-error";
import { ForgotPasswordForm } from "./ForgotPasswordForm";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

const forgotPassword = vi.fn();
const resetPassword = vi.fn();
vi.mock("../integration/api", () => ({
  fetchIdentity: vi.fn(),
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  logoutEverywhere: vi.fn(),
  forgotPassword: (...args: unknown[]) => forgotPassword(...args),
  resetPassword: (...args: unknown[]) => resetPassword(...args),
  changePassword: vi.fn(),
  deleteAccount: vi.fn(),
}));

describe("ForgotPasswordForm — request step", () => {
  beforeEach(() => {
    replace.mockClear();
    forgotPassword.mockClear();
    resetPassword.mockClear();
  });

  it("shows a validation error and does not submit for an invalid email", async () => {
    const { user } = renderWithProviders(<ForgotPasswordForm />);
    await user.click(screen.getByRole("button", { name: "Send reset code" }));
    expect(await screen.findByText("Enter a valid email address.")).toBeInTheDocument();
    expect(forgotPassword).not.toHaveBeenCalled();
  });

  it("advances to the code-entry step on success", async () => {
    forgotPassword.mockResolvedValueOnce({ ok: true });
    const { user } = renderWithProviders(<ForgotPasswordForm />);
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.click(screen.getByRole("button", { name: "Send reset code" }));
    expect(await screen.findByRole("button", { name: "Reset password" })).toBeInTheDocument();
    expect(screen.getByText(/a 6-digit code was sent/i)).toBeInTheDocument();
  });

  it("regression: a failed request must surface a Banner — this used to fail completely silently", async () => {
    forgotPassword.mockRejectedValueOnce(new AppError("network", "Unable to reach the server."));
    const { user } = renderWithProviders(<ForgotPasswordForm />);
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.click(screen.getByRole("button", { name: "Send reset code" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Unable to reach the server.");
    // And it must NOT silently advance to the code-entry step as if it worked.
    expect(screen.queryByRole("button", { name: "Reset password" })).not.toBeInTheDocument();
  });

  it("disables the submit button while the request is in flight", async () => {
    let resolveRequest!: (value: unknown) => void;
    forgotPassword.mockReturnValueOnce(new Promise((resolve) => (resolveRequest = resolve)));
    const { user } = renderWithProviders(<ForgotPasswordForm />);
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    const button = screen.getByRole("button", { name: "Send reset code" });
    await user.click(button);
    expect(button).toBeDisabled();
    resolveRequest({ ok: true });
    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Reset password" })).toBeInTheDocument(),
    );
  });
});

describe("ForgotPasswordForm — reset step", () => {
  beforeEach(() => {
    replace.mockClear();
    forgotPassword.mockClear();
    resetPassword.mockClear();
  });

  async function advanceToResetStep(user: ReturnType<typeof renderWithProviders>["user"]) {
    forgotPassword.mockResolvedValueOnce({ ok: true });
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.click(screen.getByRole("button", { name: "Send reset code" }));
    await screen.findByRole("button", { name: "Reset password" });
  }

  it("shows validation errors for a short code and mismatched passwords", async () => {
    const { user } = renderWithProviders(<ForgotPasswordForm />);
    await advanceToResetStep(user);

    await user.type(screen.getByLabelText(/^6-digit code/), "123");
    await user.type(screen.getByLabelText(/^New password/), "password123");
    await user.type(screen.getByLabelText(/^Confirm new password/), "different123");
    await user.click(screen.getByRole("button", { name: "Reset password" }));

    expect(await screen.findByText("Enter the 6-digit code.")).toBeInTheDocument();
    expect(screen.getByText("Passwords don't match.")).toBeInTheDocument();
    expect(resetPassword).not.toHaveBeenCalled();
  });

  it("submits and redirects to /login on success", async () => {
    const { user } = renderWithProviders(<ForgotPasswordForm />);
    await advanceToResetStep(user);
    resetPassword.mockResolvedValueOnce({ ok: true });

    await user.type(screen.getByLabelText(/^6-digit code/), "123456");
    await user.type(screen.getByLabelText(/^New password/), "password123");
    await user.type(screen.getByLabelText(/^Confirm new password/), "password123");
    await user.click(screen.getByRole("button", { name: "Reset password" }));

    await waitFor(() => expect(resetPassword).toHaveBeenCalledOnce());
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
  });

  it("shows a Banner (not a toast) when the code is invalid or expired", async () => {
    const { user } = renderWithProviders(<ForgotPasswordForm />);
    await advanceToResetStep(user);
    resetPassword.mockRejectedValueOnce(new AppError("unknown", "Invalid or expired code."));

    await user.type(screen.getByLabelText(/^6-digit code/), "000000");
    await user.type(screen.getByLabelText(/^New password/), "password123");
    await user.type(screen.getByLabelText(/^Confirm new password/), "password123");
    await user.click(screen.getByRole("button", { name: "Reset password" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid or expired code.");
    expect(replace).not.toHaveBeenCalled();
  });
});
