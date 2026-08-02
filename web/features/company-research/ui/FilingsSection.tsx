"use client";

import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Card, CardContent } from "@/components/foundation/Card";
import { Skeleton, SkeletonGroup } from "@/components/foundation/Skeleton";
import { Text } from "@/components/foundation/Text";
import { useFilings } from "../application/useFilings";

/**
 * SCR-06 Filings. Same progressive-enhancement principle the CTO approved
 * for Financials (Phase 4B), applied here too: `GET /filings` only ever
 * returns metadata (`backend/agents/ingest.py` persists chunked text +
 * metadata, never a reconstructed full document) — no endpoint serves a
 * filing's actual content. The real list renders; `FilingViewer`'s split
 * reading pane (content + anchored AI analysis) is placeholder-only. No
 * backend scope was added for this phase.
 */
export function FilingsSection({ ticker }: { ticker: string }) {
  const filings = useFilings(ticker);

  if (filings.isPending) {
    return (
      <SkeletonGroup label="Loading filings" className="flex flex-col gap-3">
        <Skeleton className="h-14 w-full" />
        <Skeleton className="h-14 w-full" />
      </SkeletonGroup>
    );
  }
  if (filings.isError) {
    return (
      <Banner
        tone="error"
        action={
          <Button variant="secondary" size="sm" onClick={() => filings.refetch()}>
            Retry
          </Button>
        }
      >
        Couldn&apos;t load filings.
      </Banner>
    );
  }

  const list = filings.data?.filings ?? [];
  if (list.length === 0) {
    return (
      <Banner tone="info">
        No filings ingested for {ticker} yet — the Overview tab offers ingest actions for tickers
        with none.
      </Banner>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <ul className="flex flex-col gap-2">
        {list.map((f) => (
          <li key={f.doc_id}>
            <Card>
              <CardContent className="flex flex-col gap-1">
                <Text variant="body-strong">{f.source}</Text>
                <Text variant="caption">
                  {new Date(f.created_at).toLocaleDateString()} · {f.num_chunks} chunks ·{" "}
                  {f.char_count.toLocaleString()} chars
                </Text>
              </CardContent>
            </Card>
          </li>
        ))}
      </ul>
      <Banner tone="info">
        Reading a filing&apos;s full content side-by-side with AI analysis isn&apos;t available yet
        — this section will support it once a per-filing content endpoint exists.
      </Banner>
    </div>
  );
}
