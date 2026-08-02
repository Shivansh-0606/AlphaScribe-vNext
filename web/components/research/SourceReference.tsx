"use client";

import { Popover, PopoverContent, PopoverTrigger } from "@/components/foundation/Popover";
import { Text } from "@/components/foundation/Text";

/**
 * Citation Card / Source Preview (08_AI_Components.md) — the "source list
 * item" variant: a descriptive, focusable link (never bare "source"/"click
 * here" — Law 3 requires the source path be reachable and namable) that
 * opens a Source Preview popover showing the cited excerpt in place, so the
 * user can verify evidence without losing their research context.
 */
export function SourceReference({
  index,
  source,
  excerpt,
}: {
  /** 1-based — matches the `[n]` inline citation markers (`@/lib/markdown/citations`). */
  index: number;
  source: string;
  excerpt: string;
}) {
  return (
    <li id={`source-${index}`}>
      <Popover>
        <PopoverTrigger asChild>
          <button
            type="button"
            className="text-primary text-left text-sm underline decoration-dotted underline-offset-2"
          >
            [{index}] {source}
          </button>
        </PopoverTrigger>
        <PopoverContent>
          <Text variant="label">{source}</Text>
          <Text variant="small" className="text-muted-foreground mt-2 line-clamp-6">
            {excerpt}
          </Text>
        </PopoverContent>
      </Popover>
    </li>
  );
}
