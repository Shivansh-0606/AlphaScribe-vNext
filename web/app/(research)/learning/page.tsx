import type { Metadata } from "next";
import { LearningScreen } from "@/features/learning";

export const metadata: Metadata = { title: "Learning" };

export default async function LearningPage({
  searchParams,
}: {
  searchParams: Promise<{ ticker?: string; job?: string }>;
}) {
  const { ticker, job } = await searchParams;
  return <LearningScreen initialTicker={ticker} contextReportId={job} />;
}
