import NextLink from "next/link";
import { Button } from "@/components/foundation/Button";
import { Heading } from "@/components/foundation/Heading";
import { Text } from "@/components/foundation/Text";
import { ReturningUserRedirect } from "@/features/account-setup";

/** SCR-01's three trust-positioning attributes, verbatim (05_Screen_Inventory.md
 * SCR-01) — labels only, no explanatory sentences (brief §5 OQ-1 decision). */
const TRUST_LABELS = ["Grounded", "Explainable", "Source-traceable"] as const;

export default function Home() {
  return (
    <div className="max-w-2xl">
      <ReturningUserRedirect />
      <Heading level="h1">AlphaScribe</Heading>
      <Text variant="body" className="text-muted-foreground mt-4 text-lg leading-relaxed">
        AlphaScribe is an AI-native Equity Research Workspace designed to help investors understand,
        analyze, compare, and monitor publicly traded companies without spending hours searching
        through financial filings, earnings calls, news articles, and financial statements.
      </Text>
      <ul className="mt-6 flex flex-row flex-wrap gap-x-6 gap-y-2">
        {TRUST_LABELS.map((label) => (
          <li key={label}>
            <Text variant="label">{label}</Text>
          </li>
        ))}
      </ul>
      <div className="mt-8 flex items-center gap-4">
        <Button asChild hero>
          <NextLink href="/signup">Get started</NextLink>
        </Button>
        <Button asChild variant="quiet">
          <NextLink href="/login">Sign in</NextLink>
        </Button>
      </div>
    </div>
  );
}
