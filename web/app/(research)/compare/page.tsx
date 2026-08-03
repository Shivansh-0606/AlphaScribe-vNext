import type { Metadata } from "next";
import { ComparisonScreen } from "@/features/comparison";

export const metadata: Metadata = { title: "Compare" };

export default async function ComparePage({
  searchParams,
}: {
  searchParams: Promise<{ ids?: string }>;
}) {
  const { ids } = await searchParams;
  const initialIds = ids ? ids.split(",").filter(Boolean) : [];
  return <ComparisonScreen initialIds={initialIds} />;
}
