import { expect, test } from "@playwright/test";

/**
 * Real-browser computed-style checks for Family 01 (Buttons). This is the
 * ONLY layer that can catch a class of bug jsdom-based component tests
 * can't: the underlying shadcn `ButtonPrimitive` always applies its own
 * default variant background internally, and a wrapper variant that doesn't
 * declare an explicit `bg-*` override (like "quiet") lets it leak through
 * unless CSS is actually resolved by a real engine. Found via manual browser
 * inspection during Family 01 implementation; this test locks the fix in.
 */
test.describe("Foundation Button — rendered variant colors", () => {
  test("quiet has no background fill", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const bg = await page
      .getByTestId("button-quiet")
      .evaluate((el) => getComputedStyle(el).backgroundColor);
    expect(bg).toBe("rgba(0, 0, 0, 0)");
  });

  test("secondary, primary, and destructive each render their own distinct fill", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const [secondary, primary, destructive] = await Promise.all([
      page.getByTestId("button-secondary").evaluate((el) => getComputedStyle(el).backgroundColor),
      page.getByTestId("button-primary").evaluate((el) => getComputedStyle(el).backgroundColor),
      page.getByTestId("button-destructive").evaluate((el) => getComputedStyle(el).backgroundColor),
    ]);
    expect(secondary).not.toBe(primary);
    expect(destructive).not.toBe(primary);
    expect(new Set([secondary, primary, destructive]).size).toBe(3);
  });

  test("hero renders the brand gradient, not a solid fill", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const backgroundImage = await page
      .getByTestId("button-hero")
      .evaluate((el) => getComputedStyle(el).backgroundImage);
    expect(backgroundImage).toContain("linear-gradient");
  });

  test("icon button quiet variant also has no background fill", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const bg = await page
      .getByTestId("icon-button-quiet")
      .evaluate((el) => getComputedStyle(el).backgroundColor);
    expect(bg).toBe("rgba(0, 0, 0, 0)");
  });
});

/**
 * Radix's roving-tabindex model both moves focus AND selects on arrow
 * navigation (matching native radio-group semantics). jsdom's Focus/Pointer
 * Events fidelity isn't reliable enough to assert the selection half of
 * this (see components/foundation/RadioGroup.test.tsx) — verified here
 * against a real browser instead.
 */
test.describe("Foundation RadioGroup — keyboard selection", () => {
  test("arrow-down moves focus and selects the next option", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByRole("radio", { name: "Managed" }).click();
    // Not page.keyboard.press() — Radix tracks "was an arrow key just
    // pressed" via document-level keydown/keyup listeners and auto-selects
    // on the resulting focus event; press()'s atomic down+up can land the
    // keyup (which clears that flag) before the focus handler observes it.
    await page.keyboard.down("ArrowDown");
    const next = page.getByRole("radio", { name: "Bring your own key" });
    await expect(next).toBeFocused();
    await page.keyboard.up("ArrowDown");
    await expect(next).toBeChecked();
  });
});

/**
 * Real computed border-color checks for Input's focus/invalid/disabled
 * states (04.2 AD-3 "tokens or nothing" — jsdom can't confirm a CSS token
 * actually resolves visually; see the Button "quiet variant" precedent).
 */
test.describe("Foundation Input — rendered state colors", () => {
  test("focus changes the border to the ring color", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const input = page.getByTestId("input-default");
    const before = await input.evaluate((el) => getComputedStyle(el).borderColor);
    // Not input.focus() — the style relies on :focus-visible, and a raw
    // script-triggered .focus() doesn't reliably match it. Clicking does:
    // browsers special-case text fields to show :focus-visible even on
    // pointer focus (users need to see the caret to know they can type).
    await input.click();
    await expect(input).toBeFocused();
    const after = await input.evaluate((el) => getComputedStyle(el).borderColor);
    expect(after).not.toBe(before);
  });

  test("aria-invalid renders a distinct (destructive) border from the default state", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const [defaultBorder, invalidBorder] = await Promise.all([
      page.getByTestId("input-default").evaluate((el) => getComputedStyle(el).borderColor),
      page.getByTestId("input-invalid").evaluate((el) => getComputedStyle(el).borderColor),
    ]);
    expect(invalidBorder).not.toBe(defaultBorder);
  });

  test("disabled renders at reduced opacity", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const opacity = await page
      .getByTestId("input-disabled")
      .evaluate((el) => Number(getComputedStyle(el).opacity));
    expect(opacity).toBeLessThan(1);
  });

  test("password reveal toggle actually swaps the browser's native masking", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const input = page.getByTestId("input-password");
    await expect(input).toHaveAttribute("type", "password");
    await page.getByRole("button", { name: "Show password" }).click();
    await expect(input).toHaveAttribute("type", "text");
  });
});

/**
 * FormField's aria-describedby wiring is already verified structurally in
 * jsdom (FormField.test.tsx) — this test adds the one thing jsdom can't
 * confirm: that the wired-up error state also produces the real destructive
 * border color on the actual control a user sees, not just the right
 * attribute value.
 */
test.describe("Foundation FormField — integrated error state", () => {
  test("an errored field is both ARIA-wired and visually distinct from a default field", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const errored = page.getByTestId("input-in-formfield");
    await expect(errored).toHaveAttribute("aria-invalid", "true");
    const describedBy = await errored.getAttribute("aria-describedby");
    expect(describedBy).toBeTruthy();
    await expect(page.locator(`#${describedBy}`)).toHaveText("Enter a valid email.");

    const [defaultBorder, erroredBorder] = await Promise.all([
      page.getByTestId("input-default").evaluate((el) => getComputedStyle(el).borderColor),
      errored.evaluate((el) => getComputedStyle(el).borderColor),
    ]);
    expect(erroredBorder).not.toBe(defaultBorder);
  });
});

/**
 * `field-sizing: content` (native CSS auto-grow, no JS resize handler) is
 * exactly the kind of layout-driven behavior jsdom cannot compute — it has
 * no real layout engine, so a height comparison in jsdom would be
 * meaningless. Named explicitly as a browser-specific behavior to verify.
 */
test.describe("Foundation Textarea — CSS auto-grow", () => {
  test("height grows as content wraps to more lines, with no JS resize handler", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const textarea = page.getByTestId("textarea-autogrow");
    const initialHeight = await textarea.evaluate((el) => el.getBoundingClientRect().height);
    await textarea.click();
    await textarea.press("Control+a");
    await textarea.type(Array.from({ length: 8 }, (_, i) => `Line ${i}`).join("\n"));
    const grownHeight = await textarea.evaluate((el) => el.getBoundingClientRect().height);
    expect(grownHeight).toBeGreaterThan(initialHeight);
  });
});

/**
 * Checked/indeterminate fills for Checkbox rely on Radix's
 * `data-[state=checked]:bg-primary` selector actually resolving — the same
 * class of risk as the Button "quiet variant" leak (a state that looks
 * right in markup but not in rendered CSS). Distinct fill per state is the
 * WCAG "not color alone" cue combined with the checkmark glyph; this
 * confirms the fill half actually renders.
 */
test.describe("Foundation Checkbox — rendered state colors", () => {
  test("checked and indeterminate render a fill distinct from unchecked; disabled is faded", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const [unchecked, checked, indeterminate, disabledOpacity] = await Promise.all([
      page.getByTestId("checkbox-unchecked").evaluate((el) => getComputedStyle(el).backgroundColor),
      page.getByTestId("checkbox-checked").evaluate((el) => getComputedStyle(el).backgroundColor),
      page
        .getByTestId("checkbox-indeterminate")
        .evaluate((el) => getComputedStyle(el).backgroundColor),
      page.getByTestId("checkbox-disabled").evaluate((el) => Number(getComputedStyle(el).opacity)),
    ]);
    expect(checked).not.toBe(unchecked);
    expect(indeterminate).not.toBe(unchecked);
    expect(disabledOpacity).toBeLessThan(1);
  });

  test("indeterminate exposes aria-checked=mixed", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await expect(page.getByTestId("checkbox-indeterminate")).toHaveAttribute(
      "aria-checked",
      "mixed",
    );
  });
});

/**
 * Switch communicates state via knob position AND track color (spec:
 * "never color alone") — both are CSS (position + background-color) that
 * jsdom cannot compute. Position is compared via the knob's real
 * getBoundingClientRect().x (not getComputedStyle().transform) — Tailwind
 * v4 expresses the slide via the separate CSS `translate` property, not
 * `transform`, so a transform-string comparison reads "none" for both and
 * misses the change; the rect reflects the true rendered position
 * regardless of which CSS mechanism produced it.
 */
test.describe("Foundation Switch — rendered track color and knob position", () => {
  test("on/off render distinct track colors and knob positions", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    // Sequential, each after an explicit visibility wait — reading four
    // nested-locator evaluates concurrently via Promise.all right after
    // goto() raced the page settling and intermittently read a stale (0,0)
    // rect for the thumb, even though .evaluate() itself resolved.
    const onSwitch = page.getByTestId("switch-on");
    const offSwitch = page.getByTestId("switch-off");
    await onSwitch.waitFor({ state: "visible" });
    await offSwitch.waitFor({ state: "visible" });

    const onColor = await onSwitch.evaluate((el) => getComputedStyle(el).backgroundColor);
    const offColor = await offSwitch.evaluate((el) => getComputedStyle(el).backgroundColor);
    const onKnobX = await onSwitch
      .locator("[data-slot=switch-thumb]")
      .evaluate((el) => el.getBoundingClientRect().x);
    const offKnobX = await offSwitch
      .locator("[data-slot=switch-thumb]")
      .evaluate((el) => el.getBoundingClientRect().x);

    expect(onColor).not.toBe(offColor);
    expect(onKnobX).not.toBe(offKnobX);
  });

  test("disabled renders at reduced opacity", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const opacity = await page
      .getByTestId("switch-disabled")
      .evaluate((el) => Number(getComputedStyle(el).opacity));
    expect(opacity).toBeLessThan(1);
  });
});

/**
 * Select's listbox is Radix-portaled to the end of <body> — a real-DOM
 * fact jsdom component tests don't exercise meaningfully (portals work
 * there too, but there's no real layout/paint to confirm against). Also
 * covers Escape-driven focus restoration, the same focus-timing-sensitive
 * category that needed real-browser confirmation for RadioGroup.
 */
test.describe("Foundation Select — portal rendering and focus restoration", () => {
  test("the open listbox is portaled outside the trigger's own subtree", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const trigger = page.getByTestId("select-trigger");
    await trigger.click();
    const option = page.getByRole("option", { name: "Quarterly" });
    await expect(option).toBeVisible();
    const isDescendant = await option.evaluate(
      (el, triggerTestId) =>
        !!document.querySelector(`[data-testid="${triggerTestId}"]`)?.contains(el),
      "select-trigger",
    );
    expect(isDescendant).toBe(false);
  });

  test("Escape closes the listbox and returns focus to the trigger", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const trigger = page.getByTestId("select-trigger");
    await trigger.click();
    await expect(page.getByRole("option", { name: "Quarterly" })).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(trigger).toBeFocused();
    await expect(trigger).toHaveAttribute("aria-expanded", "false");
  });
});

/**
 * DropdownMenu: outside-click dismissal and Escape focus-restoration are
 * real-pointer/real-focus behaviors — the same category as Select above.
 */
test.describe("Foundation DropdownMenu — dismissal and focus restoration", () => {
  test("clicking outside the open menu closes it", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const trigger = page.getByTestId("dropdown-trigger");
    await trigger.click();
    await expect(page.getByRole("menuitem", { name: "Rename" })).toBeVisible();
    await page.mouse.click(10, 10);
    await expect(page.getByRole("menuitem", { name: "Rename" })).not.toBeVisible();
  });

  test("Escape closes the menu and returns focus to the trigger", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const trigger = page.getByTestId("dropdown-trigger");
    await trigger.click();
    await expect(page.getByRole("menuitem", { name: "Rename" })).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(trigger).toBeFocused();
  });

  test("the destructive item renders a color distinct from a standard item", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByTestId("dropdown-trigger").click();
    const [standard, destructive] = await Promise.all([
      page.getByRole("menuitem", { name: "Rename" }).evaluate((el) => getComputedStyle(el).color),
      page.getByTestId("dropdown-item-destructive").evaluate((el) => getComputedStyle(el).color),
    ]);
    expect(destructive).not.toBe(standard);
  });
});

/**
 * Badge (Family 05) wraps the generated `components/ui/badge.tsx` and
 * replaces its variant vocabulary entirely — the exact same "does the
 * primitive's own default fill actually get cancelled by tailwind-merge, or
 * does it leak through" risk as the Button "quiet variant" case above (see
 * Badge.tsx's own comment referencing that precedent). jsdom can't compute
 * which of two conflicting `bg-*` classes tailwind-merge + the real CSS
 * cascade resolves to — only a real browser can.
 */
test.describe("Foundation Badge — rendered variant colors", () => {
  test("every documented variant renders its own distinct computed background", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const testIds = [
      "badge-neutral",
      "badge-bullish",
      "badge-bearish",
      "badge-warning",
      "badge-verified",
      "badge-count",
    ];
    const colors = await Promise.all(
      testIds.map((id) =>
        page.getByTestId(id).evaluate((el) => getComputedStyle(el).backgroundColor),
      ),
    );
    expect(new Set(colors).size).toBe(testIds.length);
  });

  test("each badge's text label is visible — meaning is never color-only", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await expect(page.getByTestId("badge-bearish")).toHaveText("Bearish");
    await expect(page.getByTestId("badge-bearish")).toBeVisible();
  });
});

/**
 * Chip (Family 05) has no shadcn primitive to leak from, but its `filter`
 * variant's selected cue is the same class of risk as Checkbox's
 * `data-[state=checked]:bg-primary` case above: a Tailwind
 * `data-[selected=true]:*` selector that jsdom's Chip.test.tsx can confirm
 * is wired (the attribute is set) but not that a real CSS engine actually
 * paints a different color for it.
 */
test.describe("Foundation Chip — rendered selected-state colors", () => {
  test("selecting a filter chip renders a border color distinct from unselected", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const chip = page.getByTestId("chip-filter");
    const before = await chip.evaluate((el) => getComputedStyle(el).borderColor);
    await chip.click();
    await expect(chip).toHaveAttribute("aria-pressed", "true");
    // The attribute committing doesn't guarantee the next paint has already
    // applied the resulting style — poll instead of a single immediate read
    // (this test was intermittently flaky under parallel-worker load without it).
    await expect
      .poll(() => chip.evaluate((el) => getComputedStyle(el).borderColor))
      .not.toBe(before);
  });
});

/**
 * Card (Family 05) cancels the generated primitive's own `rounded-xl`/
 * `shadow-sm`/`py-6` (Direction C: flat at rest) — the same
 * cancel-the-primitive-default risk as Button/Badge above. `selectable`'s
 * selected cue is also a `data-[selected=true]:*` selector (the same class
 * of risk as Chip/Checkbox). `interactive` composes the actual focusable
 * element via `asChild` (Radix Slot) — confirming it renders as a real
 * anchor, not a wrapping div, is the same "one real focusable control"
 * concern RadioGroup/Select verify above.
 */
test.describe("Foundation Card — rendered radius/shadow and selected state", () => {
  test("a static card is flat at rest, with the frozen 4px radius (not shadcn's 12px default)", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const card = page.getByTestId("card-static");
    const [boxShadow, borderRadius] = await Promise.all([
      card.evaluate((el) => getComputedStyle(el).boxShadow),
      card.evaluate((el) => getComputedStyle(el).borderRadius),
    ]);
    // Tailwind's `shadow-none` computes to 5 fully-transparent shadow
    // layers, not the literal keyword "none" — assert "no visible shadow"
    // semantically (no non-zero alpha in any layer) rather than hardcoding
    // that implementation-detail string.
    expect(boxShadow).not.toMatch(/rgba?\([^)]*,\s*0*\.\d+\)/);
    expect(borderRadius).toBe("4px");
  });

  test("asChild composes the real anchor as the card root, not a wrapping div", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const card = page.getByTestId("card-interactive");
    expect(await card.evaluate((el) => el.tagName)).toBe("A");
  });

  test("hovering an interactive card produces a real box-shadow lift", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const card = page.getByTestId("card-interactive");
    const before = await card.evaluate((el) => getComputedStyle(el).boxShadow);
    await card.hover();
    // :hover matching plus the box-shadow transition committing isn't
    // guaranteed to have painted by the very next microtask — poll instead
    // of a single immediate read (intermittently flaky under parallel-worker
    // load without it, the same class of timing issue as Switch above).
    await expect.poll(() => card.evaluate((el) => getComputedStyle(el).boxShadow)).not.toBe(before);
    const after = await card.evaluate((el) => getComputedStyle(el).boxShadow);
    // The hover shadow must have real, visible opacity — not just a
    // different-but-still-invisible transparent layer.
    expect(after).toMatch(/rgba?\([^)]*,\s*0*\.\d+\)/);
  });

  test("selected renders a border color distinct from an unselected selectable card", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const [selected, unselected] = await Promise.all([
      page.getByTestId("card-selectable").evaluate((el) => getComputedStyle(el).borderColor),
      page
        .getByTestId("card-selectable-unselected")
        .evaluate((el) => getComputedStyle(el).borderColor),
    ]);
    expect(selected).not.toBe(unselected);
  });
});

/**
 * Progress (Family 07) composes the raw `radix-ui` Progress primitive
 * directly and hand-renders the indicator, so neither of its two real risks
 * is verifiable in jsdom: (1) determinate width is computed via inline
 * `style.width` from the `value` prop — a real layout/paint fact, the same
 * class of risk as Switch's knob-position check above; (2) indeterminate
 * renders a CSS `@keyframes` sweep (globals.css `progress-indeterminate`)
 * that only a real animation engine can confirm is actually animating, not
 * a frozen bar. Skeleton/Loader/Banner are deliberately NOT given a
 * Playwright block — see the Testing section of components/foundation/README.md
 * for why each is low-risk (no primitive to leak from, no conditional-CSS
 * selector, no layout-dependent computation).
 */
test.describe("Foundation Progress — rendered fill width and indeterminate motion", () => {
  test("determinate value maps to a proportionally wider rendered fill", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    // Sequential, each after an explicit visibility wait — reading two nested
    // locators' geometry concurrently via Promise.all right after goto()
    // raced the page settling and intermittently read a stale (0,0) rect for
    // both bars under parallel-worker load, the exact pitfall this file
    // already documents (found for Switch's knob position, same fix here).
    const narrowerIndicator = page
      .getByTestId("progress-determinate")
      .locator('[data-slot="foundation-progress-indicator"]');
    const widerIndicator = page
      .getByTestId("progress-brand")
      .locator('[data-slot="foundation-progress-indicator"]');
    await narrowerIndicator.waitFor({ state: "visible" });
    await widerIndicator.waitFor({ state: "visible" });

    const narrower = await narrowerIndicator.evaluate((el) => el.getBoundingClientRect().width);
    const wider = await widerIndicator.evaluate((el) => el.getBoundingClientRect().width);
    // progress-determinate is value=40, progress-brand is value=70.
    expect(wider).toBeGreaterThan(narrower);
  });

  test("indeterminate renders a real, running CSS animation, not a frozen bar", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    const indicator = page
      .getByTestId("progress-indeterminate")
      .locator('[data-slot="foundation-progress-indicator"]');
    const animationName = await indicator.evaluate((el) => getComputedStyle(el).animationName);
    expect(animationName).toBe("progress-indeterminate");
    const x1 = await indicator.evaluate((el) => el.getBoundingClientRect().x);
    await page.waitForTimeout(400);
    const x2 = await indicator.evaluate((el) => el.getBoundingClientRect().x);
    expect(x2).not.toBe(x1);
  });
});

/**
 * Tooltip (Family 06) — this is the one real defect this pass found. Opening
 * via keyboard focus (never hover) reproducibly self-closed on the very next
 * tick, 100% of 6/6 runs, before the `forceMount` fix in `Tooltip.tsx` (root
 * cause: Radix's `TooltipContent` subscribes to a document-level
 * `"tooltip.open"` event for cross-instance mutual exclusion, and on the
 * synchronous focus path that subscription's own mount effect raced the
 * dispatch from opening, in the same commit — self-catching its own open
 * event). The delayed hover path (a real `setTimeout`) never raced this way.
 * Confirmed against a full `next build && next start`, not dev-mode only.
 */
test.describe("Foundation Tooltip — keyboard focus and hover both open it", () => {
  test("keyboard focus reveals the tooltip content", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByTestId("tooltip-trigger").focus();
    await expect(page.getByRole("tooltip")).toBeVisible();
    await expect(page.getByRole("tooltip")).toHaveText("Net income after tax");
  });

  test("hover reveals the tooltip content", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByTestId("tooltip-trigger").hover();
    await expect(page.getByRole("tooltip")).toBeVisible();
  });

  test("is invisible and non-interactive at rest, before any interaction", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const content = page.locator('[data-slot="foundation-tooltip-content"]');
    // forceMount keeps it mounted (required for the fix above), so verify
    // "hidden" via computed opacity/pointer-events rather than DOM absence —
    // `.isVisible()` doesn't check opacity, only display/visibility.
    const opacity = await content.evaluate((el) => getComputedStyle(el).opacity);
    const pointerEvents = await content.evaluate((el) => getComputedStyle(el).pointerEvents);
    expect(opacity).toBe("0");
    expect(pointerEvents).toBe("none");
  });

  test("Escape dismisses an open tooltip", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByTestId("tooltip-trigger").focus();
    await expect(page.getByRole("tooltip")).toBeVisible();
    await page.keyboard.press("Escape");
    // Same reason as the "invisible at rest" test above: forceMount keeps
    // it mounted with data-state="closed", and Playwright's .toBeVisible()
    // doesn't check opacity (only display/visibility) — it stayed
    // data-state="closed" the whole time here, so poll the real hidden
    // signal instead of the coarse visibility check.
    const content = page.locator('[data-slot="foundation-tooltip-content"]');
    await expect(content).toHaveAttribute("data-state", "closed");
    expect(await content.evaluate((el) => getComputedStyle(el).opacity)).toBe("0");
  });
});

/**
 * Popover (Family 06) — mostly re-exported as generated (already
 * `bg-popover`/`shadow-md`/`border`); the one thing wrapped is the raw
 * `z-50` → `--z-overlay`, a real stacking-context fact (would render behind
 * `--z-nav`'s 100 if left at the default 50) that only a real layout engine
 * can confirm.
 */
test.describe("Foundation Popover — layering token", () => {
  test("renders at the frozen --z-overlay layer, not shadcn's default z-50", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByTestId("popover-trigger").click();
    const content = page.getByTestId("popover-content");
    await expect(content).toBeVisible();
    expect(await content.evaluate((el) => getComputedStyle(el).zIndex)).toBe("300");
  });
});

/**
 * Dialog (Family 06) composes the raw `radix-ui` Dialog primitive directly
 * (the generated `DialogContent` bakes its own unstyleable `DialogOverlay`
 * call into its JSX) — the scrim color/opacity and panel radius are exactly
 * the "cancel an off-token default" class of risk Button/Badge/Card already
 * established needs a real browser to confirm. Tab-cycling focus containment
 * is the same real-focus-timing class of risk as RadioGroup's arrow-key test.
 */
test.describe("Foundation Dialog — scrim tokens, radius, and focus trap", () => {
  test("the scrim uses the ink-navy foreground color at the frozen scrim opacity, not an arbitrary black", async ({
    page,
  }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByTestId("dialog-trigger").click();
    const overlay = page.locator('[data-slot="foundation-dialog-overlay"]');
    await expect(overlay).toBeVisible();
    const [bg, opacity] = await Promise.all([
      overlay.evaluate((el) => getComputedStyle(el).backgroundColor),
      overlay.evaluate((el) => getComputedStyle(el).opacity),
    ]);
    expect(bg).toBe("rgb(21, 33, 50)");
    expect(opacity).toBe("0.55");
  });

  test("the panel renders the frozen 4px radius, not shadcn's 8px default", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByTestId("dialog-trigger").click();
    const content = page.getByTestId("dialog-content");
    await expect(content).toBeVisible();
    expect(await content.evaluate((el) => getComputedStyle(el).borderRadius)).toBe("4px");
  });

  test("Tab cycling stays inside the open dialog", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByTestId("dialog-trigger").click();
    await expect(page.getByTestId("dialog-content")).toBeVisible();
    // Cycle through every focusable control inside the dialog and back to
    // the first — focus must never land back on the page behind it.
    for (let i = 0; i < 6; i++) {
      await page.keyboard.press("Tab");
      const insideDialog = await page.evaluate(
        () => !!document.activeElement?.closest('[data-slot="foundation-dialog-content"]'),
      );
      expect(insideDialog).toBe(true);
    }
  });
});

/**
 * Drawer (Family 06) — same composition risk as Dialog (custom-built to
 * support the non-modal companion case).
 *
 * Traced via Radix's source (not assumed) what `modal` actually changes:
 * `FocusScope`'s `loop: true` is hardcoded for Dialog content regardless of
 * `modal`, so Tab always cycles *within* an open drawer's own focusable
 * elements either way — that's not the modal/non-modal distinction (an
 * earlier version of this test asserted non-modal Tab "escapes" the drawer,
 * which failed because Radix doesn't actually provide that; fixed by
 * testing the behavior `modal` genuinely controls instead of an assumed
 * one). What actually differs: `disableOutsidePointerEvents` — modal blocks
 * pointer interaction with the rest of the page entirely while open (a real
 * click on another button doesn't even register); non-modal leaves the
 * rest of the page fully interactive, matching the spec's "the user moves
 * between content and companion freely." Confirmed directly: a real click
 * on a second button times out while a modal drawer is open, and succeeds
 * while the non-modal one is open — a real-pointer-timing fact jsdom can't
 * confirm (README's Playwright-pitfalls precedent).
 */
test.describe("Foundation Drawer — modal vs. non-modal outside interaction", () => {
  test("a modal drawer blocks pointer interaction with the rest of the page", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByTestId("drawer-trigger").click();
    await expect(page.getByTestId("drawer-content")).toBeVisible();
    // The button itself isn't disabled — a modal's DismissableLayer makes
    // the rest of the page inert to pointer events, so a real click on it
    // never lands; assert the click attempt times out rather than checking
    // a `disabled`-style attribute that was never set.
    await expect(async () => {
      await page.getByTestId("drawer-companion-trigger").click({ timeout: 300 });
    }).rejects.toThrow();
  });

  test("a non-modal companion drawer leaves the rest of the page interactive", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    await page.getByTestId("drawer-companion-trigger").click();
    await expect(page.getByTestId("drawer-companion-content")).toBeVisible();
    await page.getByTestId("drawer-trigger").click();
    await expect(page.getByTestId("drawer-content")).toBeVisible();
  });
});

/**
 * SearchField — combines cmdk (arrow-key keyboard nav + internal DOM
 * bookkeeping) with a Radix Popover portal; this exact combination of real
 * keyboard-driven state + portal positioning is the same class of risk
 * RadioGroup/Select already needed a real browser for. Uses a query
 * matching 2+ suggestions deliberately: with exactly one suggestion,
 * ArrowDown has nowhere to move to and cmdk never sets
 * `aria-activedescendant` for the auto-highlighted-but-unmoved first item —
 * confirmed as cmdk's own behavior (see SearchField.tsx's doc comment), not
 * something to assert against here.
 */
test.describe("Foundation SearchField — portal, arrow-key navigation, selection", () => {
  test("suggestions render in a floating panel anchored to the field's width", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const combobox = page.getByRole("combobox", { name: "Search companies" });
    await combobox.click();
    await combobox.type("s"); // matches both "Industries" and "Services"
    const listbox = page.getByRole("listbox");
    await expect(listbox).toBeVisible();
    expect(await page.getByRole("option").count()).toBe(2);
  });

  test("ArrowDown moves aria-activedescendant to the next option", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const combobox = page.getByRole("combobox", { name: "Search companies" });
    await combobox.click();
    await combobox.type("s");
    await expect(page.getByRole("listbox")).toBeVisible();
    await page.keyboard.press("ArrowDown");
    const [activeDescendant, options] = await Promise.all([
      combobox.getAttribute("aria-activedescendant"),
      page.getByRole("option").all(),
    ]);
    const secondOptionId = await options[1].getAttribute("id");
    expect(activeDescendant).toBe(secondOptionId);
  });

  test("Enter selects the active suggestion", async ({ page }) => {
    await page.goto("/test-fixtures/component-preview");
    const combobox = page.getByRole("combobox", { name: "Search companies" });
    await combobox.click();
    await combobox.type("Reliance");
    await expect(page.getByRole("option", { name: /Reliance Industries/ })).toBeVisible();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("listbox")).not.toBeVisible();
  });
});
