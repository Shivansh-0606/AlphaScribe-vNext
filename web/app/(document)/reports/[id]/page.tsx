import type { Metadata } from "next";
import { ReportViewScreen } from "@/features/research-library";

export const metadata: Metadata = { title: "Report" };

export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <ReportViewScreen reportId={id} />;
}
