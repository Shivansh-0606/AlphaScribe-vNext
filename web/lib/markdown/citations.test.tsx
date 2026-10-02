import ReactMarkdown from "react-markdown";
import { describe, expect, it } from "vitest";
import { render } from "@/tests/setup/render";
import remarkCitations from "@/lib/markdown/citations";

/**
 * Port of the legacy `frontend/src/lib/remarkCitations.selfcheck.mjs`
 * (read-only reference) — same five assertions, plus the code-span/block and
 * non-digit edges. Rendered through `react-markdown`, the plugin's real
 * consumer, so markdown is genuinely parsed (a real link is a real `link`
 * node, code is a real `code`/`inlineCode` node) instead of hand-built trees.
 */
function renderMarkdown(markdown: string) {
  const { container } = render(
    <ReactMarkdown remarkPlugins={[remarkCitations]}>{markdown}</ReactMarkdown>,
  );
  const links = Array.from(container.querySelectorAll("a"));
  return {
    container,
    hrefs: links.map((a) => a.getAttribute("href")),
    linkTexts: links.map((a) => a.textContent),
  };
}

describe("remarkCitations", () => {
  it("links each [n] marker to #source-n, keeping the surrounding text", () => {
    const { container, hrefs, linkTexts } = renderMarkdown("Revenue grew [1] a lot [2].");
    expect(hrefs).toEqual(["#source-1", "#source-2"]);
    expect(linkTexts).toEqual(["[1]", "[2]"]);
    expect(container.textContent).toBe("Revenue grew [1] a lot [2].");
  });

  it("adds no links when the text has no markers", () => {
    const { container, hrefs } = renderMarkdown("No citations here.");
    expect(hrefs).toEqual([]);
    expect(container.textContent).toBe("No citations here.");
  });

  it("links adjacent markers", () => {
    expect(renderMarkdown("[1][2]").hrefs).toEqual(["#source-1", "#source-2"]);
  });

  it("links multi-digit markers", () => {
    expect(renderMarkdown("See [99] for details").hrefs).toEqual(["#source-99"]);
  });

  it("leaves a real markdown link untouched", () => {
    const { hrefs, linkTexts } = renderMarkdown("Already a [link](https://example.com)");
    expect(hrefs).toEqual(["https://example.com"]);
    expect(linkTexts).toEqual(["link"]);
  });

  it("wraps each marker exactly once (no double-wrapping of the inserted link's own text)", () => {
    const { container, hrefs } = renderMarkdown("Grew [1] and [2].");
    expect(hrefs).toHaveLength(2);
    expect(container.querySelectorAll("a a")).toHaveLength(0);
  });

  it("links markers inside emphasis", () => {
    expect(renderMarkdown("**Revenue grew [3]**").hrefs).toEqual(["#source-3"]);
  });

  it("leaves markers inside inline code untouched", () => {
    const { container, hrefs } = renderMarkdown("Use `[1]` literally");
    expect(hrefs).toEqual([]);
    expect(container.querySelector("code")?.textContent).toBe("[1]");
  });

  it("leaves markers inside a fenced code block untouched", () => {
    const { container, hrefs } = renderMarkdown("```\nvalues[1] = [2]\n```");
    expect(hrefs).toEqual([]);
    expect(container.querySelector("pre code")?.textContent).toContain("values[1] = [2]");
  });

  it("ignores brackets that are not purely digits", () => {
    expect(renderMarkdown("Not [a] or [] or [1a] or [ 1 ] markers").hrefs).toEqual([]);
  });
});
