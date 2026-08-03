import { Badge } from "@/components/foundation/Badge";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Loader } from "@/components/foundation/Loader";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/foundation/Table";
import type { ComparisonReport, ExtractedFinancials } from "../integration/schemas";

const METRIC_FIELDS: { key: keyof ExtractedFinancials; label: string }[] = [
  { key: "revenue", label: "Revenue" },
  { key: "revenue_yoy", label: "Revenue YoY" },
  { key: "eps", label: "EPS" },
  { key: "net_income", label: "Net Income" },
  { key: "operating_margin", label: "Operating Margin" },
  { key: "free_cash_flow", label: "Free Cash Flow" },
];

/** All 7 fields null/empty — retrieval returned zero docs for this report (`agents/nodes.py`), not merely a few gaps. */
function hasNoExtractedData(data: ExtractedFinancials | undefined): boolean {
  return !data || Object.values(data).every((value) => !value);
}

/**
 * ComparisonTable (09_Component_Inventory.md) — SCR-07's frozen component:
 * `companies, metrics, comparability flags` properties; states `Default,
 * Empty, Partial Failure, Loading`. Usage rule: "flags gaps rather than
 * hiding them" — realized via `TableCell`'s `unavailable` prop (the same
 * Partial Failure mechanism `Table` already implements) for every missing
 * metric, and a "Limited data" `Badge` on any member with none at all,
 * rather than omitting that company's column.
 */
export function ComparisonTable({
  reports,
  isLoading,
  isError,
  onRetry,
}: {
  reports: ComparisonReport[] | undefined;
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
}) {
  if (isLoading) {
    return <Loader label="Loading comparison…" />;
  }

  if (isError) {
    return (
      <Banner
        tone="error"
        action={
          <Button variant="secondary" size="sm" onClick={onRetry}>
            Retry
          </Button>
        }
      >
        Couldn&apos;t load the comparison.
      </Banner>
    );
  }

  if (!reports || reports.length === 0) {
    return null;
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Metric</TableHead>
            {reports.map((report) => (
              <TableHead key={report.id} numeric>
                <div className="flex flex-col items-end gap-1">
                  <span>{report.company_name ?? report.ticker}</span>
                  <div className="flex gap-1">
                    {report.is_sample && <Badge variant="neutral">Sample</Badge>}
                    {hasNoExtractedData(report.extracted_data) && (
                      <Badge variant="warning">Limited data</Badge>
                    )}
                  </div>
                </div>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {METRIC_FIELDS.map((field) => (
            <TableRow key={field.key}>
              <TableCell>{field.label}</TableCell>
              {reports.map((report) => {
                const value = report.extracted_data?.[field.key];
                return (
                  <TableCell key={report.id} numeric unavailable={!value}>
                    {value}
                  </TableCell>
                );
              })}
            </TableRow>
          ))}
          <TableRow>
            <TableCell>Sentiment</TableCell>
            {reports.map((report) => (
              <TableCell key={report.id} unavailable={!report.sentiment_analysis?.sentiment}>
                {report.sentiment_analysis?.sentiment}
              </TableCell>
            ))}
          </TableRow>
        </TableBody>
      </Table>
    </div>
  );
}
