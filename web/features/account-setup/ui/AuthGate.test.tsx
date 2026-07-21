import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { AppError } from "@/lib/errors/app-error";
import { AuthGate } from "./AuthGate";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
  usePathname: () => "/workspace",
}));

const fetchIdentity = vi.fn();
vi.mock("../integration/api", () => ({
  fetchIdentity: (...args: unknown[]) => fetchIdentity(...args),
  login: vi.fn(),
  register: vi.fn(),
  logout: vi.fn(),
  logoutEverywhere: vi.fn(),
  forgotPassword: vi.fn(),
  resetPassword: vi.fn(),
  changePassword: vi.fn(),
  deleteAccount: vi.fn(),
}));

describe("AuthGate", () => {
  beforeEach(() => {
    replace.mockClear();
    fetchIdentity.mockReset();
  });

  it("renders protected content once the identity query resolves authenticated", async () => {
    fetchIdentity.mockResolvedValueOnce({
      id: "u1",
      email: "a@b.com",
      created_at: "now",
      verified: true,
    });
    renderWithProviders(
      <AuthGate>
        <div>Protected content</div>
      </AuthGate>,
    );
    expect(await screen.findByText("Protected content")).toBeInTheDocument();
    expect(replace).not.toHaveBeenCalled();
  });

  it("redirects to /login preserving the intended destination when unauthenticated", async () => {
    fetchIdentity.mockRejectedValueOnce(new AppError("auth_required", "Authentication required."));
    renderWithProviders(
      <AuthGate>
        <div>Protected content</div>
      </AuthGate>,
    );
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login?next=%2Fworkspace"));
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
  });

  it("does not tack on a connection reason for a plain/unclassified rejection", async () => {
    fetchIdentity.mockRejectedValueOnce(new Error("boom"));
    renderWithProviders(
      <AuthGate>
        <div>Protected content</div>
      </AuthGate>,
    );
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/login?next=%2Fworkspace"));
  });

  it("tells Login it's a connectivity failure, not a plain sign-out, for a network/server error", async () => {
    fetchIdentity.mockRejectedValueOnce(new AppError("server", "Server error."));
    renderWithProviders(
      <AuthGate>
        <div>Protected content</div>
      </AuthGate>,
    );
    await waitFor(() =>
      expect(replace).toHaveBeenCalledWith("/login?next=%2Fworkspace&reason=connection"),
    );
    expect(screen.queryByText("Protected content")).not.toBeInTheDocument();
  });
});
