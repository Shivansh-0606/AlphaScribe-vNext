import { Text } from "@/components/foundation/Text";

/**
 * Shared footer — "Legal · Support" per every wireframe's Footer row. Plain
 * text, not links: `/docs` (Docs) has no route yet (Feature Parity Tracker
 * §1, Not Started) and there is no legal-copy source to link to — inventing
 * either destination now would be a dead link, not a real one.
 */
export function Footer() {
  return (
    <footer className="border-border border-t" role="contentinfo">
      <div className="mx-auto max-w-6xl px-4 py-4 sm:px-6 lg:px-8">
        <Text variant="caption">Legal · Support</Text>
      </div>
    </footer>
  );
}
