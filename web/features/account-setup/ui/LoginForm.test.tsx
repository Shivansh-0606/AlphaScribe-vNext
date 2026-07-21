import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { AppError } from "@/lib/errors/app-error";
import { LoginForm } from "./LoginForm";

const replace = vi.fn();
let searchParams = new URLSearchParams();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  useSearchParams: () => searchParams,
}));

const toastError = vi.fn();
const toastSuccess = vi.fn();
vi.mock("sonner", () => ({
  toast: {
    error: (...args: unknown[]) => toastError(...args),
    success: (...args: unknown[]) => toastSuccess(...args),
  },
}));

const login = vi.fn();
vi.mock("../integration/api", () => ({
  fetchIdentity: vi.fn(),
  login: (...args: unknown[]) => login(...args),
  register: vi.fn(),
  logout: vi.fn(),
  logoutEverywhere: vi.fn(),
  forgotPassword: vi.fn(),
  resetPassword: vi.fn(),
  changePassword: vi.fn(),
  deleteAccount: vi.fn(),
}));

describe("LoginForm", () => {
  beforeEach(() => {
    replace.mockClear();
    login.mockClear();
    toastError.mockClear();
    toastSuccess.mockClear();
    searchParams = new URLSearchParams();
  });

  it("shows validation errors and does not submit when the form is empty", async () => {
    const { user } = renderWithProviders(<LoginForm />);
    await user.click(screen.getByRole("button", { name: "Continue" }));
    expect(await screen.findByText("Enter a valid email address.")).toBeInTheDocument();
    expect(screen.getByText("Enter your password.")).toBeInTheDocument();
    expect(login).not.toHaveBeenCalled();
  });

  it("submits credentials and redirects to /workspace on success", async () => {
    login.mockResolvedValueOnce({
      id: "u1",
      email: "a@b.com",
      created_at: "now",
      verified: true,
    });
    const { user } = renderWithProviders(<LoginForm />);
    // Required fields render a trailing (aria-hidden) "*" inside the <label>, so the
    // label's raw text content is "Email*"/"Password*" — match by prefix, not exact.
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.type(screen.getByLabelText(/^Password/), "password123");
    await user.click(screen.getByRole("button", { name: "Continue" }));

    await waitFor(() => expect(login).toHaveBeenCalledOnce());
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/workspace"));
  });

  it("shows exactly one failure message on a rejected submission — a Banner, never also a toast", async () => {
    login.mockRejectedValueOnce(new AppError("unknown", "Invalid email or password."));
    const { user } = renderWithProviders(<LoginForm />);
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.type(screen.getByLabelText(/^Password/), "wrong-password");
    await user.click(screen.getByRole("button", { name: "Continue" }));

    const banner = await screen.findByRole("alert");
    expect(banner).toHaveTextContent("Invalid email or password.");
    // Regression guard: this exact failure must never also fire a toast.
    expect(toastError).not.toHaveBeenCalled();
    expect(replace).not.toHaveBeenCalled();
  });

  it("disables the submit button while the request is in flight (no duplicate submits)", async () => {
    let resolveLogin!: (value: unknown) => void;
    login.mockReturnValueOnce(new Promise((resolve) => (resolveLogin = resolve)));
    const { user } = renderWithProviders(<LoginForm />);
    await user.type(screen.getByLabelText(/^Email/), "a@b.com");
    await user.type(screen.getByLabelText(/^Password/), "password123");
    const button = screen.getByRole("button", { name: "Continue" });
    await user.click(button);

    expect(button).toBeDisabled();
    expect(login).toHaveBeenCalledOnce();

    resolveLogin({ id: "u1", email: "a@b.com", created_at: "now", verified: true });
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/workspace"));
  });

  it("shows a connection-reason Banner when AuthGate bounced the user here for a non-auth failure", () => {
    searchParams = new URLSearchParams({ reason: "connection" });
    renderWithProviders(<LoginForm />);
    expect(screen.getByText(/couldn't verify your session/i, { exact: false })).toBeInTheDocument();
  });

  it("shows no connection-reason Banner on a plain arrival at /login", () => {
    renderWithProviders(<LoginForm />);
    expect(screen.queryByText(/couldn't verify your session/i)).not.toBeInTheDocument();
  });
});
