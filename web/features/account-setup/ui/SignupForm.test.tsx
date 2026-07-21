import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { AppError } from "@/lib/errors/app-error";
import { SignupForm } from "./SignupForm";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

const toastError = vi.fn();
vi.mock("sonner", () => ({
  toast: { error: (...args: unknown[]) => toastError(...args), success: vi.fn() },
}));

const register = vi.fn();
vi.mock("../integration/api", () => ({
  fetchIdentity: vi.fn(),
  login: vi.fn(),
  register: (...args: unknown[]) => register(...args),
  logout: vi.fn(),
  logoutEverywhere: vi.fn(),
  forgotPassword: vi.fn(),
  resetPassword: vi.fn(),
  changePassword: vi.fn(),
  deleteAccount: vi.fn(),
}));

describe("SignupForm", () => {
  beforeEach(() => {
    replace.mockClear();
    register.mockClear();
    toastError.mockClear();
  });

  it("shows validation errors and does not submit when the form is empty", async () => {
    const { user } = renderWithProviders(<SignupForm />);
    await user.click(screen.getByRole("button", { name: "Continue" }));
    expect(await screen.findByText("Enter a valid email address.")).toBeInTheDocument();
    expect(screen.getByText("Use at least 8 characters.")).toBeInTheDocument();
    expect(register).not.toHaveBeenCalled();
  });

  it("flags a mismatched confirmation password inline, without submitting", async () => {
    const { user } = renderWithProviders(<SignupForm />);
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.type(screen.getByLabelText(/^Password/), "password123");
    await user.type(screen.getByLabelText(/^Confirm password/), "different123");
    await user.click(screen.getByRole("button", { name: "Continue" }));
    expect(await screen.findByText("Passwords don't match.")).toBeInTheDocument();
    expect(register).not.toHaveBeenCalled();
  });

  it("submits and redirects to /workspace on success", async () => {
    register.mockResolvedValueOnce({
      id: "u1",
      email: "a@b.com",
      created_at: "now",
      verified: false,
    });
    const { user } = renderWithProviders(<SignupForm />);
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.type(screen.getByLabelText(/^Password/), "password123");
    await user.type(screen.getByLabelText(/^Confirm password/), "password123");
    await user.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() => expect(register).toHaveBeenCalledOnce());
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/workspace"));
  });

  it("shows exactly one failure message on a rejected submission — a Banner, never also a toast", async () => {
    register.mockRejectedValueOnce(new AppError("unknown", "Email already registered."));
    const { user } = renderWithProviders(<SignupForm />);
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.type(screen.getByLabelText(/^Password/), "password123");
    await user.type(screen.getByLabelText(/^Confirm password/), "password123");
    await user.click(screen.getByRole("button", { name: "Continue" }));

    const banner = await screen.findByRole("alert");
    expect(banner).toHaveTextContent("Email already registered.");
    expect(toastError).not.toHaveBeenCalled();
    expect(replace).not.toHaveBeenCalled();
  });

  it("simulates a network failure and still tells the user, not just resetting silently", async () => {
    register.mockRejectedValueOnce(new AppError("network", "Unable to reach the server."));
    const { user } = renderWithProviders(<SignupForm />);
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.type(screen.getByLabelText(/^Password/), "password123");
    await user.type(screen.getByLabelText(/^Confirm password/), "password123");
    await user.click(screen.getByRole("button", { name: "Continue" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Unable to reach the server.");
  });

  it("disables the submit button while the request is in flight", async () => {
    let resolveRegister!: (value: unknown) => void;
    register.mockReturnValueOnce(new Promise((resolve) => (resolveRegister = resolve)));
    const { user } = renderWithProviders(<SignupForm />);
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.type(screen.getByLabelText(/^Password/), "password123");
    await user.type(screen.getByLabelText(/^Confirm password/), "password123");
    const button = screen.getByRole("button", { name: "Continue" });
    await user.click(button);

    expect(button).toBeDisabled();
    resolveRegister({ id: "u1", email: "a@b.com", created_at: "now", verified: false });
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/workspace"));
  });
});
