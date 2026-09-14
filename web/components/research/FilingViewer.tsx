import ReactMarkdown from "react-markdown";
import { Badge } from "@/components/foundation/Badge";
import { Text } from "@/components/foundation/Text";
import remarkCitations from "@/lib/markdown/citations";
import { cn } from "@/lib/utils";
import { SourceReference } from "./SourceReference";

export interface FilingViewerChunk {
  chunk_idx: number;
  text: string;
}

export interface FilingViewerProps {
  /** Persisted filing text chunks, already ordered `chunk_idx` ascending by the backend (M13, Document 59 §6). */
  chunks: FilingViewerChunk[];
  /** The filing's `source` label, used to name the reading region for assistive tech. */
  source: string;
  className?: string;
}

/**
 * FilingViewer — "Filing content" variant (docs/design/09_Component_Inventory.md
 * §FilingViewer). Renders an ingested filing's persisted text for reading, for
 * the first time in M13 (Document 60 §3.5). Presentational only: the caller
 * owns loading / error / retry (Document 60 §5); this renders the loaded
 * content, or an honest "no readable content" state when a known filing has
 * zero persisted chunks (Document 59 §8 / OD-7) — never fabricated text.
 *
 * Chunks are the navigable sections (they carry no headings of their own —
 * each is a ~900-char slice of the source document). They are rendered as an
 * ordered list inside a labelled, keyboard-focusable scroll region so the
 * text can be read and navigated without leaving the page. Chunk text is
 * shown verbatim, exactly as persisted (Document 59 §5.1 / OD-2) — no
 * reconstruction, trimming, or reformatting.
 */
export function FilingViewer({ chunks, source, className }: FilingViewerProps) {
  if (chunks.length === 0) {
    return (
      <Text variant="small" className="text-muted-foreground" data-slot="filing-viewer-empty">
        No readable content is stored for this filing.
      </Text>
    );
  }

  return (
    <div
      data-slot="filing-viewer"
      role="region"
      aria-label={`Filing content: ${source}`}
      tabIndex={0}
      className={cn(
        "border-border bg-surface max-h-[28rem] overflow-y-auto rounded-md border p-4",
        className,
      )}
    >
      <ol className="flex flex-col gap-4">
        {chunks.map((chunk) => (
          <li key={chunk.chunk_idx} data-chunk-idx={chunk.chunk_idx}>
            <Text variant="small" className="whitespace-pre-wrap">
              {chunk.text}
            </Text>
          </li>
        ))}
      </ol>
    </div>
  );
}

// ---------------------------------------------------------------------------
// "Filing analysis" variant (M14, Document 64/65) — grounded, cited digests
// of one filing, always anchored to its own text (Component Inventory usage
// rule: "Analysis always anchored to the filing"). Reuses SourceReference /
// remarkCitations exactly as `AIResponseCard` does for the research brief.
// ---------------------------------------------------------------------------

export interface FilingAnalysisSourceAnchor {
  /** 1-based, unique only *within* its own output (Document 64 §8.2) — never globally. */
  index: number;
  doc_id: string;
  chunk_start: number;
  chunk_end: number;
}

export interface FilingAnalysisOutputData {
  narrative: string;
  sources: FilingAnalysisSourceAnchor[];
  cited_source_indices: number[];
  state: "complete" | "partial" | "insufficient_evidence";
  coverage_boundaries: string[];
}

export interface FilingAnalysisViewerProps {
  /** Keyed by exact output label ("Filing Summary", "Risk Factors Digest", "MD&A Digest",
   * "Important Changes" — Document 64 §8), in the fixed order the backend already
   * returns them in (JSON object key order, relied on rather than re-sorted here). */
  outputs: Record<string, FilingAnalysisOutputData>;
  /** This filing's persisted content chunks (M13) — used only to resolve each anchor's
   * `chunk_start..chunk_end` range into a readable excerpt for its SourceReference popover. */
  chunks: FilingViewerChunk[];
  source: string;
  className?: string;
}

function excerptForRange(chunks: FilingViewerChunk[], start: number, end: number): string {
  return chunks
    .filter((c) => c.chunk_idx >= start && c.chunk_idx <= end)
    .map((c) => c.text)
    .join(" ");
}

const STATE_BADGE: Record<
  FilingAnalysisOutputData["state"],
  { label: string; variant: "warning" | "neutral" } | null
> = {
  complete: null,
  partial: { label: "Partial", variant: "warning" },
  insufficient_evidence: { label: "Insufficient evidence", variant: "neutral" },
};

/**
 * FilingViewer — "Filing analysis" variant. Presentational only, same
 * discipline as the "Filing content" variant above: the caller owns
 * starting the analysis job and its loading/error states (§5 of Document
 * 60's precedent) — this renders an already-completed result, honestly,
 * including the `insufficient_evidence` / `partial` states Document 64 §11
 * requires (never fabricated, never silently upgraded to "complete").
 *
 * Each output's `sources[].index` is only unique within that output
 * (Document 64 §8.2), so citation markers/anchors are renumbered to a
 * page-wide-unique index here before rendering — SourceReference and
 * remarkCitations are reused completely unmodified (both assume one flat,
 * globally-unique source list, which is true for every other AI surface
 * that renders them today).
 */
export function FilingAnalysisViewer({
  outputs,
  chunks,
  source,
  className,
}: FilingAnalysisViewerProps) {
  const entries = Object.entries(outputs);
  if (entries.length === 0) {
    return (
      <Text variant="small" className="text-muted-foreground" data-slot="filing-analysis-empty">
        No analysis is available for this filing.
      </Text>
    );
  }

  let offset = 0;

  return (
    <div data-slot="filing-analysis-viewer" className={cn("flex flex-col gap-6", className)}>
      {entries.map(([label, output]) => {
        const badge = STATE_BADGE[output.state];
        const localOffset = offset;
        offset += output.sources.length;

        // Renumber this output's (locally-unique) source indices to a
        // page-wide-unique range and rewrite its narrative's `[n]` markers
        // to match, so every SourceReference on the page gets a distinct
        // `id="source-N"` (duplicate ids would otherwise break both HTML
        // validity and the `#source-N` anchors — see the doc comment above).
        const renumbered = output.sources.map((s, i) => ({
          ...s,
          globalIndex: localOffset + i + 1,
        }));
        const globalByLocal = new Map(renumbered.map((s) => [s.index, s.globalIndex]));
        const narrative = output.narrative.replace(/\[(\d+)\]/g, (match, n: string) => {
          const g = globalByLocal.get(Number(n));
          return g ? `[${g}]` : match;
        });

        return (
          <section key={label} aria-label={label} className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <Text variant="body-strong">{label}</Text>
              {badge && <Badge variant={badge.variant}>{badge.label}</Badge>}
            </div>

            {output.state === "insufficient_evidence" ? (
              <Text
                variant="small"
                className="text-muted-foreground"
                data-slot="filing-analysis-insufficient"
              >
                Not enough grounded evidence in this filing to produce {label.toLowerCase()}.
                {output.coverage_boundaries.length > 0 &&
                  ` ${output.coverage_boundaries.join("; ")}.`}
              </Text>
            ) : (
              <>
                <div className="[&_a]:text-primary text-foreground font-sans text-sm leading-normal [&_p]:my-2">
                  <ReactMarkdown remarkPlugins={[remarkCitations]}>{narrative}</ReactMarkdown>
                </div>
                {output.state === "partial" && output.coverage_boundaries.length > 0 && (
                  <Text variant="caption" className="text-muted-foreground">
                    Partial coverage: {output.coverage_boundaries.join("; ")}
                  </Text>
                )}
                {renumbered.length > 0 && (
                  <ol className="flex flex-col gap-1">
                    {renumbered.map((s) => (
                      <SourceReference
                        key={`${label}-${s.index}`}
                        index={s.globalIndex}
                        source={`${source} (chunks ${s.chunk_start}–${s.chunk_end})`}
                        excerpt={excerptForRange(chunks, s.chunk_start, s.chunk_end)}
                      />
                    ))}
                  </ol>
                )}
              </>
            )}
          </section>
        );
      })}
    </div>
  );
}
