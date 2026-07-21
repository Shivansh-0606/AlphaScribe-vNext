import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

test.describe("Home shell", () => {
  test("loads with correct title and one heading", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle("AlphaScribe");
    await expect(page.getByRole("heading")).toHaveCount(1);
    await expect(page.getByRole("heading")).toHaveText("AlphaScribe");
  });

  test("skip link moves focus to main content", async ({ page }) => {
    await page.goto("/");
    await page.keyboard.press("Tab");
    await expect(page.getByRole("link", { name: "Skip to main content" })).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(page.locator("#main-content")).toBeFocused();
  });

  test("header wordmark is a keyboard-reachable link to the app root", async ({ page }) => {
    await page.goto("/");
    const wordmark = page.getByRole("link", { name: "AlphaScribe home" });
    await expect(wordmark).toHaveAttribute("href", "/");
    await page.keyboard.press("Tab"); // skip link
    await page.keyboard.press("Tab"); // wordmark
    await expect(wordmark).toBeFocused();
  });

  test("has no detectable accessibility violations", async ({ page }) => {
    await page.goto("/");
    const results = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze();
    expect(results.violations).toEqual([]);
  });
});
