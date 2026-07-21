import type { Metadata } from "next";
import { ComingSoon } from "@/components/layouts/ComingSoon";

export const metadata: Metadata = { title: "Research" };

export default async function ResearchPage({
  searchParams,
}: {
  searchParams: Promise<{ ticker?: string }>;
}) {
  const { ticker } = await searchParams;
  return (
    <ComingSoon
      title="Research"
      note={
        ticker
          ? `Company Research for ${ticker.toUpperCase()} is not built yet — this destination is reachable now so navigation matches the frozen structure; the research workflow (Overview, Financials, Filings, AI Insights) lands in a later phase.`
          : "Company Research is not built yet — this destination is reachable now so navigation matches the frozen structure; the research workflow (Overview, Financials, Filings, AI Insights) lands in a later phase."
      }
    />
  );
}
