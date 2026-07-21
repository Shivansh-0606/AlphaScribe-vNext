import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { Text } from "./Text";

describe("Text", () => {
  it("defaults to a paragraph for body text", () => {
    renderWithProviders(<Text>Reading text</Text>);
    const el = screen.getByText("Reading text");
    expect(el.tagName).toBe("P");
  });

  it("renders the label variant as an uppercase mono micro-label element", () => {
    renderWithProviders(<Text variant="label">Metadata</Text>);
    const el = screen.getByText("Metadata");
    expect(el.tagName).toBe("SPAN");
    expect(el.className).toContain("uppercase");
  });

  it("renders the code variant as a <code> element", () => {
    renderWithProviders(<Text variant="code">const x = 1</Text>);
    expect(screen.getByText("const x = 1").tagName).toBe("CODE");
  });

  it("allows overriding the element via `as` regardless of variant", () => {
    renderWithProviders(
      <Text variant="body" as="span">
        Inline body text
      </Text>,
    );
    expect(screen.getByText("Inline body text").tagName).toBe("SPAN");
  });

  it("has no detectable accessibility violations across variants", async () => {
    const { container } = renderWithProviders(
      <div>
        <Text variant="body">Body</Text>
        <Text variant="body-strong">Strong</Text>
        <Text variant="small">Small</Text>
        <Text variant="caption">Caption</Text>
        <Text variant="label">Label</Text>
        <Text variant="figure">$1,234.56</Text>
        <Text variant="code">code</Text>
      </div>,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
