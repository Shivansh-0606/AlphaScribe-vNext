import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { useAiAccessStore } from "@/lib/state/aiAccess";
import { AIAccessSelector } from "./AIAccessSelector";

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

const validateLlmKey = vi.fn();
vi.mock("../integration/llm-api", () => ({
  validateLlmKey: (...args: unknown[]) => validateLlmKey(...args),
}));

const NON_ADMIN_USER = {
  id: "u1",
  email: "a@b.com",
  created_at: "now",
  verified: true,
  is_admin: false,
};
const ADMIN_USER = { ...NON_ADMIN_USER, is_admin: true };

describe("AIAccessSelector", () => {
  beforeEach(() => {
    useAiAccessStore.getState().clear();
    fetchIdentity.mockReset().mockResolvedValue(NON_ADMIN_USER);
    validateLlmKey.mockReset();
  });

  it("defaults to Managed AI — Continue is enabled with zero setup (onboarding variant)", async () => {
    const onContinue = vi.fn();
    renderWithProviders(<AIAccessSelector variant="onboarding" onContinue={onContinue} />);
    expect(screen.getByRole("radio", { name: /Managed AI/ })).toBeChecked();
    expect(screen.queryByLabelText(/^API key/)).not.toBeInTheDocument();
    const continueButton = screen.getByRole("button", { name: "Continue" });
    expect(continueButton).toBeEnabled();
  });

  it("switching to BYOK hides Continue's default-enabled state until a key validates", async () => {
    const { user } = renderWithProviders(<AIAccessSelector variant="onboarding" />);
    await user.click(screen.getByRole("radio", { name: /Bring your own key/ }));
    expect(screen.getByLabelText(/^API key/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continue" })).toBeDisabled();
  });

  it("validating a real key shows success and enables Continue", async () => {
    validateLlmKey.mockResolvedValueOnce({ valid: true });
    const { user } = renderWithProviders(<AIAccessSelector variant="onboarding" />);
    await user.click(screen.getByRole("radio", { name: /Bring your own key/ }));
    await user.type(screen.getByLabelText(/^API key/), "test-key-123");
    await user.click(screen.getByRole("button", { name: "Validate key" }));

    expect(await screen.findByText("Key validated.")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: "Continue" })).toBeEnabled());
    expect(validateLlmKey).toHaveBeenCalledWith(
      expect.objectContaining({ provider: "gemini", api_key: "test-key-123" }),
    );
  });

  it("shows the provider's rejection reason and keeps Continue disabled on an invalid key", async () => {
    validateLlmKey.mockResolvedValueOnce({ valid: false, error: "Invalid API key." });
    const { user } = renderWithProviders(<AIAccessSelector variant="onboarding" />);
    await user.click(screen.getByRole("radio", { name: /Bring your own key/ }));
    await user.type(screen.getByLabelText(/^API key/), "bad-key");
    await user.click(screen.getByRole("button", { name: "Validate key" }));

    expect(await screen.findByText("Invalid API key.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continue" })).toBeDisabled();
  });

  it("surfaces a submission-level failure (e.g. network) as a Banner too", async () => {
    validateLlmKey.mockRejectedValueOnce(new Error("Unable to reach the server."));
    const { user } = renderWithProviders(<AIAccessSelector variant="onboarding" />);
    await user.click(screen.getByRole("radio", { name: /Bring your own key/ }));
    await user.type(screen.getByLabelText(/^API key/), "test-key-123");
    await user.click(screen.getByRole("button", { name: "Validate key" }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Unable to reach the server.");
  });

  it("settings variant has no Continue button and shows the managed-default note", () => {
    renderWithProviders(<AIAccessSelector variant="settings" />);
    expect(screen.queryByRole("button", { name: "Continue" })).not.toBeInTheDocument();
    expect(screen.getByText("Using the managed default — no key needed.")).toBeInTheDocument();
  });

  it("hides the admin-only Custom provider for a non-admin user", async () => {
    const { user } = renderWithProviders(<AIAccessSelector variant="settings" />);
    await user.click(screen.getByRole("radio", { name: /Bring your own key/ }));
    await user.click(screen.getByRole("combobox"));
    // "Google Gemini" appears twice once the popover is open (the trigger's
    // current-value display + the listbox option) — scope to the option role.
    expect(await screen.findByRole("option", { name: "Google Gemini" })).toBeInTheDocument();
    expect(
      screen.queryByRole("option", { name: "Custom (OpenAI-compatible)" }),
    ).not.toBeInTheDocument();
  });

  it("shows the admin-only Custom provider, with its own base-url/model fields, for an admin user", async () => {
    fetchIdentity.mockReset().mockResolvedValue(ADMIN_USER);
    const { user } = renderWithProviders(<AIAccessSelector variant="settings" />);
    await user.click(screen.getByRole("radio", { name: /Bring your own key/ }));
    await user.click(screen.getByRole("combobox"));
    const customOption = await screen.findByRole("option", { name: "Custom (OpenAI-compatible)" });
    await user.click(customOption);

    // Required fields render a trailing (aria-hidden) "*" inside the <label>, so the
    // label's raw text content is "Base URL*"/"Model*" — match by prefix, not exact.
    expect(screen.getByLabelText(/^Base URL/)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Model/)).toBeInTheDocument();
    // Custom needs base_url + model too, not just the key.
    expect(screen.getByRole("button", { name: "Validate key" })).toBeDisabled();
  });

  it("marks Base URL and Model as required once Custom is selected (same affordance as API key)", async () => {
    fetchIdentity.mockReset().mockResolvedValue(ADMIN_USER);
    const { user } = renderWithProviders(<AIAccessSelector variant="settings" />);
    await user.click(screen.getByRole("radio", { name: /Bring your own key/ }));
    await user.click(screen.getByRole("combobox"));
    await user.click(await screen.findByRole("option", { name: "Custom (OpenAI-compatible)" }));

    for (const label of ["Base URL", "Model", "API key"]) {
      const field = screen.getByText(label).closest("label");
      expect(field?.querySelector('[aria-hidden="true"]')).toHaveTextContent("*");
    }
  });

  it("regression: editing the key after a successful validation resets to not-yet-validated", async () => {
    validateLlmKey.mockResolvedValueOnce({ valid: true });
    const { user } = renderWithProviders(<AIAccessSelector variant="onboarding" />);
    await user.click(screen.getByRole("radio", { name: /Bring your own key/ }));
    await user.type(screen.getByLabelText(/^API key/), "test-key-123");
    await user.click(screen.getByRole("button", { name: "Validate key" }));
    expect(await screen.findByText("Key validated.")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByRole("button", { name: "Continue" })).toBeEnabled());

    await user.type(screen.getByLabelText(/^API key/), "-edited");

    expect(screen.queryByText("Key validated.")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Continue" })).toBeDisabled();
  });

  it("regression: editing the key after a rejected validation clears the stale error immediately", async () => {
    validateLlmKey.mockResolvedValueOnce({ valid: false, error: "Invalid API key." });
    const { user } = renderWithProviders(<AIAccessSelector variant="onboarding" />);
    await user.click(screen.getByRole("radio", { name: /Bring your own key/ }));
    await user.type(screen.getByLabelText(/^API key/), "bad-key");
    await user.click(screen.getByRole("button", { name: "Validate key" }));
    expect(await screen.findByText("Invalid API key.")).toBeInTheDocument();

    await user.type(screen.getByLabelText(/^API key/), "-edited");

    expect(screen.queryByText("Invalid API key.")).not.toBeInTheDocument();
  });
});
