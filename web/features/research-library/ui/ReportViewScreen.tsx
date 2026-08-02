"use client";

import { DocumentTemplate } from "@/components/layouts/DocumentTemplate";
import { useReport } from "../application/useReport";
import { ReportDocument } from "./ReportDocument";

/** SCR-10 Report View — the feature's public screen composition. */
export function ReportViewScreen({ reportId }: { reportId: string }) {
  const report = useReport(reportId);

  return (
    <DocumentTemplate>
      <ReportDocument
        report={report.data}
        isLoading={report.isPending}
        error={report.error}
        onRetry={() => report.refetch()}
      />
    </DocumentTemplate>
  );
}
