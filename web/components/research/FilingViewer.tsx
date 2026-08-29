import { Text } from "@/components/foundation/Text";
import { cn } from "@/lib/utils";

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
