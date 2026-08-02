"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Heading } from "@/components/foundation/Heading";
import { Loader } from "@/components/foundation/Loader";
import { Text } from "@/components/foundation/Text";
import { ConfidenceIndicator, confidenceLabel } from "@/components/research/ConfidenceIndicator";
import { SourceReference } from "@/components/research/SourceReference";
import remarkCitations from "@/lib/markdown/citations";
import type { ReportDoc } from "../integration/schemas";
import { downloadReportExport } from "../internal/exportMarkdown";

/**
 * ReportDocument (09_Component_Inventory.md) — SCR-10 Report View's frozen
 * component: `conclusion, reasoning, content, sources, export action`.
 * States: Default, Loading, Error, Success (export), Timeout. Renders the
 * identical `draft_report`/citations/confidence/sources rendering pattern as
 * `company-research`'s `AIResponseCard` (same `ReportDoc` shape, same "never
 * shown without sources" Law 3 guarantee) — a separate component, not the
 * same instance, since this feature owns its own trust boundary (02.2 AD-3)
 * and doesn't render the financial-metrics/sentiment extras Overview does
 * (out of SCR-10's frozen scope).
 */
export function ReportDocument({
  report,
  isLoading,
  error,
  onRetry,
}: {
  report: ReportDoc | null | undefined;
  isLoading: boolean;
  error: Error | null;
  onRetry: () => void;
}) {
  if (isLoading) {
    return <Loader label="Loading the report…" />;
  }

  if (error || !report) {
    return (
      <Banner
        tone="error"
        action={
          <Button variant="secondary" size="sm" onClick={onRetry}>
            Retry
          </Button>
        }
      >
        Couldn&apos;t load this report — it may not exist, or you may not have access to it.
      </Banner>
    );
  }

  const isUsable = report.draft_report.trim().length > 0 && report.source_documents.length > 0;
  if (!isUsable) {
    return (
      <Banner tone="error">
        This report finished without producing a usable result — there&apos;s no trustworthy content
        or sources to show.
      </Banner>
    );
  }

  const confidence = confidenceLabel(report.scorecard.overall);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-2">
          <Heading level="h1">{report.company_name ?? report.ticker}</Heading>
          <ConfidenceIndicator label={confidence} />
        </div>
        <Text variant="small" className="text-muted-foreground">
          {report.query}
        </Text>
      </div>

      <div className="[&_a]:text-primary text-foreground font-sans text-base leading-normal [&_h1]:font-sans [&_h2]:font-sans [&_h3]:font-sans [&_li]:my-1 [&_p]:my-3 [&_ul]:my-3 [&_ul]:list-disc [&_ul]:pl-5">
        <ReactMarkdown remarkPlugins={[remarkCitations]}>{report.draft_report}</ReactMarkdown>
      </div>

      <div className="flex flex-col gap-2">
        <Heading level="h2">Sources</Heading>
        <ol className="flex flex-col gap-2">
          {report.source_documents.map((source, i) => (
            <SourceReference
              key={`${source.doc_id}-${source.chunk_idx}`}
              index={i + 1}
              source={source.source}
              excerpt={source.text}
            />
          ))}
        </ol>
      </div>

      <div className="flex justify-end">
        <ExportButton report={report} />
      </div>
    </div>
  );
}

function ExportButton({ report }: { report: ReportDoc }) {
  const [exported, setExported] = useState(false);

  return (
    <Button
      variant="secondary"
      onClick={() => {
        downloadReportExport(report);
        setExported(true);
        setTimeout(() => setExported(false), 2000);
      }}
    >
      {exported ? "Exported" : "Export"}
    </Button>
  );
}
