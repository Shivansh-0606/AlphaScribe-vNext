"use client";

import { Badge } from "@/components/foundation/Badge";
import { cn } from "@/lib/utils";

/**
 * SCR-06 section nav (Overview → Business Summary → Financial Metrics →
 * Financial Statements → SEC Filings → AI Insights → Export are IA content
 * *levels* within one screen, not separate routes — 05_Screen_Inventory.md).
 * Overview (4A), Financials/Filings (4B), AI Insights (4C), and Export
 * (4D — an honest hand-off to the not-yet-built Report View, not a
 * disabled stub; CTO-resolved) are all enabled. There is no remaining
 * disabled section — the "Soon"/disabled-Badge pattern (used for the
 * sibling Compare/Library/Learning stubs) stays supported here for
 * whichever section needs it next.
 */
const SECTIONS = [
  { key: "overview", label: "Overview" },
  { key: "financials", label: "Financials" },
  { key: "filings", label: "Filings" },
  { key: "ai-insights", label: "AI Insights" },
  { key: "export", label: "Export" },
] as const;

export type SectionKey = (typeof SECTIONS)[number]["key"];

const ENABLED: readonly SectionKey[] = [
  "overview",
  "financials",
  "filings",
  "ai-insights",
  "export",
];

export function SectionNav({
  active,
  onSelect,
}: {
  active: SectionKey;
  onSelect: (key: SectionKey) => void;
}) {
  return (
    <nav
      aria-label="Company Research sections"
      className="flex flex-row gap-1 overflow-x-auto lg:flex-col"
    >
      {SECTIONS.map((section) => {
        const enabled = ENABLED.includes(section.key);
        const isActive = active === section.key;
        return (
          <button
            key={section.key}
            type="button"
            disabled={!enabled}
            aria-current={isActive ? "page" : undefined}
            onClick={() => onSelect(section.key)}
            className={cn(
              "flex items-center justify-between gap-2 rounded-md px-3 py-2 text-left text-sm font-medium whitespace-nowrap transition-colors",
              isActive
                ? "bg-surface-hover text-foreground"
                : "text-foreground hover:bg-surface-hover",
              !enabled &&
                "text-muted-foreground opacity-disabled pointer-events-none hover:bg-transparent",
            )}
          >
            {section.label}
            {!enabled && <Badge variant="neutral">Soon</Badge>}
          </button>
        );
      })}
    </nav>
  );
}
