"use client";

import { useState } from "react";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { Card, CardContent } from "@/components/foundation/Card";
import { Skeleton, SkeletonGroup } from "@/components/foundation/Skeleton";
import { Text } from "@/components/foundation/Text";
import { FilingViewer } from "@/components/research/FilingViewer";
import { cn } from "@/lib/utils";
import { useFilingContent } from "../application/useFilingContent";
import { useFilings } from "../application/useFilings";
import { FilingAnalysisPanel } from "./FilingAnalysisPanel";

type FilingView = "content" | "analysis";

/** Same `aria-current` toggle-button convention as `SectionNav` — no ARIA
 * tablist semantics needed for a two-way, non-nested switch. */
function FilingViewSwitch({
  view,
  onChange,
}: {
  view: FilingView;
  onChange: (v: FilingView) => void;
}) {
  const options: { key: FilingView; label: string }[] = [
    { key: "content", label: "Content" },
    { key: "analysis", label: "Analysis" },
  ];
  return (
    <div role="group" aria-label="Filing view" className="flex flex-row gap-1">
      {options.map((option) => (
        <button
          key={option.key}
          type="button"
          aria-current={view === option.key ? "true" : undefined}
          onClick={() => onChange(option.key)}
          className={cn(
            "rounded-md px-3 py-1 text-sm font-medium transition-colors",
            view === option.key
              ? "bg-surface-hover text-foreground"
              : "text-muted-foreground hover:bg-surface-hover",
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}

/**
 * SCR-06 Filings. The real filing list renders from `GET /filings`
 * (metadata only). Selecting a filing reads its persisted text via M13's
 * `GET /companies/{ticker}/filings/{doc_id}/content` (Document 59/60,
 * CTO-ratified 2026-08-27) and shows it in the frozen `FilingViewer`
 * "Filing content" variant. A Content/Analysis switch (Component Inventory
 * §FilingViewer variants) additionally exposes M14 Filing Analysis (Document
 * 64/65) via `FilingAnalysisPanel`, which owns its own job lifecycle — the
 * content pane's own loading/error/empty states are unchanged.
 */
export function FilingsSection({ ticker }: { ticker: string }) {
  const filings = useFilings(ticker);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [view, setView] = useState<FilingView>("content");
  const content = useFilingContent(ticker, selectedDocId);

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

  const selected = list.find((f) => f.doc_id === selectedDocId) ?? null;

  return (
    <div className="flex flex-col gap-4">
      <ul className="flex flex-col gap-2">
        {list.map((f) => {
          const isOpen = f.doc_id === selectedDocId;
          return (
            <li key={f.doc_id}>
              <Card>
                <CardContent className="flex flex-col gap-2">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex flex-col gap-1">
                      <Text variant="body-strong">{f.source}</Text>
                      <Text variant="caption">
                        {new Date(f.created_at).toLocaleDateString()} · {f.num_chunks} chunks ·{" "}
                        {f.char_count.toLocaleString()} chars
                      </Text>
                    </div>
                    <Button
                      variant="secondary"
                      size="sm"
                      aria-expanded={isOpen}
                      onClick={() => setSelectedDocId(isOpen ? null : f.doc_id)}
                    >
                      {isOpen ? "Hide content" : "Read content"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </li>
          );
        })}
      </ul>

      {selected && (
        <div className="flex flex-col gap-3">
          <FilingViewSwitch view={view} onChange={setView} />

          {view === "content" ? (
            content.isPending ? (
              <SkeletonGroup
                label={`Loading content for ${selected.source}`}
                className="flex flex-col gap-2"
              >
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-4 w-4/6" />
              </SkeletonGroup>
            ) : content.isError ? (
              <Banner
                tone="error"
                action={
                  <Button variant="secondary" size="sm" onClick={() => content.refetch()}>
                    Retry
                  </Button>
                }
              >
                Couldn&apos;t load this filing&apos;s content.
              </Banner>
            ) : (
              <FilingViewer chunks={content.data?.content.chunks ?? []} source={selected.source} />
            )
          ) : (
            // M14 — key={selected.doc_id} resets the job to idle on filing change.
            <FilingAnalysisPanel
              key={selected.doc_id}
              ticker={ticker}
              docId={selected.doc_id}
              source={selected.source}
              chunks={content.data?.content.chunks ?? []}
            />
          )}
        </div>
      )}
    </div>
  );
}
