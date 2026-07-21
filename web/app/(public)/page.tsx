import NextLink from "next/link";
import { Button } from "@/components/foundation/Button";
import { Heading } from "@/components/foundation/Heading";
import { Text } from "@/components/foundation/Text";

export default function Home() {
  return (
    <div className="max-w-2xl">
      <Heading level="h1">AlphaScribe</Heading>
      <Text variant="body" className="text-muted-foreground mt-4 text-lg leading-relaxed">
        AlphaScribe is an AI-native Equity Research Workspace designed to help investors understand,
        analyze, compare, and monitor publicly traded companies without spending hours searching
        through financial filings, earnings calls, news articles, and financial statements.
      </Text>
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
