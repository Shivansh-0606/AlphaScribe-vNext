import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import Home from "./page";

const replace = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace }),
}));

// Mocked at the network boundary (the account-setup feature's own integration
// module), same technique as AuthGate.test.tsx — exercises the real
// useAuthStatus -> useIdentity chain and the real ReturningUserRedirect,
// rather than stubbing the feature's public surface.
const fetchIdentity = vi.fn();
vi.mock("@/features/account-setup/integration/api", () => ({
  fetchIdentity: (...args: unknown[]) => fetchIdentity(...args),
}));

describe("Home", () => {
  beforeEach(() => {
    replace.mockClear();
    fetchIdentity.mockReset();
    fetchIdentity.mockRejectedValue(new Error("unauthenticated"));
  });

  it("renders exactly one heading naming the product", () => {
    renderWithProviders(<Home />);
    const headings = screen.getAllByRole("heading");
    expect(headings).toHaveLength(1);
    expect(headings[0]).toHaveTextContent("AlphaScribe");
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<Home />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  // 06 SCR-01 Information Hierarchy: "value proposition -> trust positioning
  // -> entry action".
  it("renders the value proposition, then the three trust labels, then the entry actions, in that order", () => {
    renderWithProviders(<Home />);
    const text = document.body.textContent ?? "";
    const valueIndex = text.indexOf("AI-native Equity Research Workspace");
    const groundedIndex = text.indexOf("Grounded");
    const explainableIndex = text.indexOf("Explainable");
    const sourceTraceableIndex = text.indexOf("Source-traceable");
    const ctaIndex = text.indexOf("Get started");

    expect(valueIndex).toBeGreaterThan(-1);
    expect(groundedIndex).toBeGreaterThan(valueIndex);
    expect(explainableIndex).toBeGreaterThan(groundedIndex);
    expect(sourceTraceableIndex).toBeGreaterThan(explainableIndex);
    expect(ctaIndex).toBeGreaterThan(sourceTraceableIndex);
  });

  // 06 SCR-01 Edge Cases: "Returning authenticated user is routed onward
  // rather than shown marketing."
  it("routes a returning authenticated visitor to /workspace", async () => {
    fetchIdentity.mockReset();
    fetchIdentity.mockResolvedValueOnce({
      id: "u1",
      email: "a@b.com",
      created_at: "now",
      verified: true,
    });
    renderWithProviders(<Home />);
    await waitFor(() => expect(replace).toHaveBeenCalledWith("/workspace"));
  });

  // 06: "Content-first; entry action available as soon as rendered" / "If the
  // page cannot fully load, the entry action still functions" — Landing must
  // never gate behind a spinner the way AuthGate gates protected routes.
  it("renders the page in full with both working CTAs while identity is still loading", () => {
    fetchIdentity.mockReset();
    fetchIdentity.mockImplementation(() => new Promise(() => {}));
    renderWithProviders(<Home />);
    expect(screen.getByRole("link", { name: "Get started" })).toHaveAttribute("href", "/signup");
    expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute("href", "/login");
    expect(replace).not.toHaveBeenCalled();
  });

  it("renders the page in full with both working CTAs when signed out, without redirecting", async () => {
    renderWithProviders(<Home />);
    expect(screen.getByRole("link", { name: "Get started" })).toHaveAttribute("href", "/signup");
    expect(screen.getByRole("link", { name: "Sign in" })).toHaveAttribute("href", "/login");
    await waitFor(() => expect(fetchIdentity).toHaveBeenCalled());
    expect(replace).not.toHaveBeenCalled();
  });
});
