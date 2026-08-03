"use client";

import ReactMarkdown from "react-markdown";
import { Card, CardContent } from "@/components/foundation/Card";
import { Heading } from "@/components/foundation/Heading";
import { Text } from "@/components/foundation/Text";
import { SourceReference } from "@/components/research/SourceReference";
import remarkCitations from "@/lib/markdown/citations";
import type { ExplanationDoc } from "../integration/schemas";

/**
 * The grounded explanation surface — same rendering pattern as
 * `AIResponseCard`/`ReportDocument` (markdown + `[n]` citation markers +
 * a Sources list, Law 3 — never shown without sources), but no Confidence
 * Indicator: the proposed contract has no scorecard concept for an
 * explanation (unlike a research report), so one isn't fabricated here.
 */
export function LearningExplanation({ explanation }: { explanation: ExplanationDoc }) {
  return (
    <div className="flex flex-col gap-6">
      <Card>
        <CardContent className="flex flex-col gap-4">
          <Text variant="body-strong">{explanation.concept}</Text>
          <div className="[&_a]:text-primary text-foreground font-sans text-base leading-normal [&_h1]:font-sans [&_h2]:font-sans [&_h3]:font-sans [&_li]:my-1 [&_p]:my-3 [&_ul]:my-3 [&_ul]:list-disc [&_ul]:pl-5">
            <ReactMarkdown remarkPlugins={[remarkCitations]}>
              {explanation.explanation}
            </ReactMarkdown>
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-col gap-2">
        <Heading level="h2">Sources</Heading>
        <ol className="flex flex-col gap-2">
          {explanation.source_documents.map((source, i) => (
            <SourceReference
              key={`${source.doc_id}-${source.chunk_idx}`}
              index={i + 1}
              source={source.source}
              excerpt={source.text}
            />
          ))}
        </ol>
      </div>
    </div>
  );
}
