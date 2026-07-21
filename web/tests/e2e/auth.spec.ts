import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

/**
 * Real-browser coverage for the auth pages' shell and client-side behavior
 * (05.1 AD-1 journey tier). Deliberately does NOT exercise real login/signup
 * submissions — that needs a live backend process this config doesn't boot
 * (see playwright.config.ts's webServer, a static `next build`/`next start`
 * only) — those paths are covered by the mocked vitest component tests
 * (LoginForm/SignupForm/ForgotPasswordForm/SettingsPanel .test.tsx). This
 * file only proves what's true regardless of a backend: the page renders,
 * has no a11y violations, and RHF+Zod validation (100% client-side) fires.
 */
test.describe("Login page", () => {
  test("loads with the expected heading and form", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveTitle(/Sign in/);
    await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();
    await expect(page.getByRole("button", { name: "Continue" })).toBeVisible();
  });

  test("shows inline validation errors on an empty submit, without a network round-trip", async ({
    page,
  }) => {
    await page.goto("/login");
    await page.getByRole("button", { name: "Continue" }).click();
    await expect(page.getByText("Enter a valid email address.")).toBeVisible();
    await expect(page.getByText("Enter your password.")).toBeVisible();
  });

  test("shows the connection-reason banner only when AuthGate's ?reason=connection is present", async ({
    page,
  }) => {
    await page.goto("/login");
    await expect(page.getByText(/couldn't verify your session/i)).toHaveCount(0);

    await page.goto("/login?reason=connection");
    await expect(
      page.getByRole("alert").filter({ hasText: /couldn't verify your session/i }),
    ).toBeVisible();
  });

  test("has no detectable accessibility violations", async ({ page }) => {
    await page.goto("/login");
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(results.violations).toEqual([]);
  });
});

test.describe("Signup page", () => {
  test("loads with the expected heading and form", async ({ page }) => {
    await page.goto("/signup");
    await expect(page).toHaveTitle(/Sign up/);
    await expect(page.getByRole("heading", { name: "Create your account" })).toBeVisible();
  });

  test("flags a mismatched confirmation password inline", async ({ page }) => {
    await page.goto("/signup");
    await page.getByLabel(/^Email/).fill("a@b.com");
    await page.getByLabel(/^Password/).fill("password123");
    await page.getByLabel(/^Confirm password/).fill("different123");
    await page.getByRole("button", { name: "Continue" }).click();
    await expect(page.getByText("Passwords don't match.")).toBeVisible();
  });

  test("has no detectable accessibility violations", async ({ page }) => {
    await page.goto("/signup");
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(results.violations).toEqual([]);
  });
});

test.describe("Forgot password page", () => {
  test("loads with the expected heading and request-step form", async ({ page }) => {
    await page.goto("/forgot-password");
    await expect(page).toHaveTitle(/Reset your password/);
    await expect(page.getByRole("button", { name: "Send reset code" })).toBeVisible();
  });

  test("has no detectable accessibility violations", async ({ page }) => {
    await page.goto("/forgot-password");
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(results.violations).toEqual([]);
  });
});
