import type { Metadata } from "next";
import { CompanyResearchScreen } from "@/features/company-research";

export const metadata: Metadata = { title: "Research" };

export default async function ResearchPage({
  searchParams,
}: {
  searchParams: Promise<{ ticker?: string; job?: string }>;
}) {
  const { ticker, job } = await searchParams;
  return <CompanyResearchScreen ticker={ticker} jobId={job} />;
}
