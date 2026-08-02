import type { Link, Root, Text } from "mdast";
import type { Parent } from "unist";
import { SKIP, visit } from "unist-util-visit";

/**
 * Ported from `frontend/src/lib/remarkCitations.js` (read-only legacy
 * reference — not modified) to TypeScript. Rewrites literal "[1]", "[2]"
 * citation markers (as emitted by the synthesizer prompt, `agents/nodes.py`)
 * into real mdast link nodes pointing at "#source-N", so `react-markdown`'s
 * `a` component override can turn them into citation anchors — no manual
 * markdown string rewriting.
 *
 * Shared (`web/lib/`), not feature-internal: both `company-research`
 * (AI Response Card) and `research-library` (Report View) render the same
 * `draft_report` citation-marker convention, so this lives next to the
 * other cross-feature primitives rather than being duplicated per feature.
 */

const CITATION_RE = /\[(\d+)\]/g;

export default function remarkCitations() {
  return (tree: Root) => {
    visit(tree, "text", (node: Text, index, parent: Parent | undefined) => {
      if (!parent || index == null || !CITATION_RE.test(node.value)) return;
      CITATION_RE.lastIndex = 0;

      const parts: (Text | Link)[] = [];
      let last = 0;
      let match: RegExpExecArray | null;
      while ((match = CITATION_RE.exec(node.value))) {
        if (match.index > last) {
          parts.push({ type: "text", value: node.value.slice(last, match.index) });
        }
        parts.push({
          type: "link",
          url: `#source-${match[1]}`,
          children: [{ type: "text", value: match[0] }],
        });
        last = match.index + match[0].length;
      }
      if (last < node.value.length) parts.push({ type: "text", value: node.value.slice(last) });

      parent.children.splice(index, 1, ...parts);
      // SKIP: without it, visit() descends into the inserted link nodes and
      // re-matches their own "[n]" text child, double-wrapping every citation.
      return [SKIP, index + parts.length] as const;
    });
  };
}
