"use client";

import { CircleNotch, MagnifyingGlass, X } from "@phosphor-icons/react/dist/ssr";
import { Command as CommandPrimitive } from "cmdk";
import { Popover as PopoverPrimitive } from "radix-ui";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { IconButton } from "./IconButton";

/**
 * SearchField (Family 02, deferred to Phase 5 since it composes Popover) —
 * docs/experience_design/Components/02_Text_Inputs.md. Presentational only
 * (02.5): `suggestions` are supplied by the caller (not fetched here — no
 * TanStack Query dependency), matching every other foundation control.
 *
 * Built on `cmdk` directly (not the generated `components/ui/command.tsx`,
 * whose `CommandInput` hardcodes a `lucide-react` search icon and its own
 * styling — the same reason `Checkbox`/`Progress`/`Dialog` bypass their
 * generated primitives) + the raw `radix-ui` Popover for floating
 * positioning, anchored to the field via `PopoverAnchor`.
 *
 * cmdk's `Input`/`List`/`Item` already implement the full ARIA combobox
 * pattern out of the box (`role="combobox"`, `aria-controls`,
 * `aria-activedescendant`, `role="listbox"`/`"option"`) — verified from its
 * source, not assumed; nothing here hand-wires that. **Known limitation**:
 * cmdk hardcodes `aria-expanded="true"` on its input unconditionally (not
 * tied to whether the panel is actually showing) — a cmdk library
 * constraint, not something this wrapper can override (props are spread
 * before cmdk's own hardcoded value, so passing a different one is a
 * no-op).
 *
 * `shouldFilter={false}` on the root: `suggestions` already come pre-scoped
 * from the caller (Global vs Company source) — this component does not
 * re-filter them client-side.
 *
 * **Second known cmdk limitation** (traced via its source, confirmed via
 * real-browser testing, not assumed): `aria-activedescendant` only updates
 * when arrow-key navigation actually *changes* the highlighted item.
 * cmdk auto-highlights the first suggestion on load/filter (`aria-selected`
 * + `data-selected` are correctly `true` on it, and Enter correctly selects
 * it), but doesn't set `aria-activedescendant` for that initial highlight —
 * only for a subsequent, real move. With exactly one suggestion, ArrowDown
 * has nowhere to move to, so `aria-activedescendant` never gets set even
 * though the single option is genuinely selected. Verified this is cmdk's
 * own behavior, not a regression from anchoring it in a Popover: with 2+
 * suggestions, arrow-key navigation updates `aria-activedescendant`
 * correctly on the very first press.
 */
export interface SearchFieldSuggestion {
  id: string;
  label: string;
  description?: string;
}

export interface SearchFieldProps {
  /** Accessible name — cmdk wires this to the input via a visually-hidden label, not aria-label directly. */
  label: string;
  placeholder?: string;
  size?: "md" | "lg";
  value: string;
  onValueChange: (value: string) => void;
  suggestions: SearchFieldSuggestion[];
  loading?: boolean;
  /** No Results copy — always shown with the active query still visible in the field (spec: never a blank dropdown, query preserved). */
  emptyMessage?: string;
  onSelect: (suggestion: SearchFieldSuggestion) => void;
  /** Enter with no suggestion highlighted. */
  onSubmit?: (value: string) => void;
  /** Focus lands here on arrival (e.g. SCR-04 Workspace Home's "search is the primary focus"). */
  autoFocus?: boolean;
  className?: string;
}

const SIZE_CLASSNAME: Record<NonNullable<SearchFieldProps["size"]>, string> = {
  md: "h-9 text-sm",
  lg: "h-11 text-base",
};

export function SearchField({
  label,
  placeholder,
  size = "md",
  value,
  onValueChange,
  suggestions,
  loading = false,
  emptyMessage = "No results — try a different term.",
  onSelect,
  onSubmit,
  autoFocus = false,
  className,
}: SearchFieldProps) {
  const [open, setOpen] = useState(false);
  const showPanel = open && (loading || suggestions.length > 0 || value.length > 0);

  return (
    <CommandPrimitive
      data-slot="foundation-search-field"
      label={label}
      shouldFilter={false}
      className="w-full overflow-visible bg-transparent"
    >
      <PopoverPrimitive.Root open={showPanel} onOpenChange={setOpen}>
        <PopoverPrimitive.Anchor asChild>
          <div
            className={cn(
              "border-input bg-input-bg ease-standard focus-within:border-ring flex items-center gap-2 rounded-md border px-3 transition-[border-color,box-shadow] duration-[var(--motion-duration-fast)]",
              SIZE_CLASSNAME[size],
              className,
            )}
          >
            <MagnifyingGlass className="text-muted-foreground size-4 shrink-0" aria-hidden="true" />
            <CommandPrimitive.Input
              autoFocus={autoFocus}
              placeholder={placeholder}
              value={value}
              onValueChange={(next) => {
                onValueChange(next);
                setOpen(true);
              }}
              onFocus={() => setOpen(true)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && onSubmit) {
                  onSubmit(value);
                  setOpen(false);
                }
              }}
              className="text-foreground placeholder:text-muted-foreground h-full flex-1 bg-transparent outline-none"
            />
            {loading && (
              <CircleNotch
                className="text-muted-foreground size-4 shrink-0 animate-spin"
                weight="bold"
                aria-hidden="true"
              />
            )}
            {value && !loading && (
              <IconButton
                label="Clear search"
                icon={<X />}
                size="sm"
                variant="quiet"
                className="-mr-1.5 size-6"
                onClick={() => {
                  onValueChange("");
                  setOpen(false);
                }}
              />
            )}
          </div>
        </PopoverPrimitive.Anchor>
        <PopoverPrimitive.Portal>
          <PopoverPrimitive.Content
            align="start"
            sideOffset={4}
            onOpenAutoFocus={(event) => event.preventDefault()}
            className="border-border bg-popover text-popover-foreground z-[var(--z-overlay)] w-[var(--radix-popper-anchor-width)] rounded-md border p-1 shadow-md"
          >
            <CommandPrimitive.List>
              {loading ? (
                <div className="text-muted-foreground px-3 py-6 text-center font-sans text-sm">
                  Searching…
                </div>
              ) : suggestions.length === 0 ? (
                <CommandPrimitive.Empty className="text-muted-foreground px-3 py-6 text-center font-sans text-sm">
                  {emptyMessage}
                </CommandPrimitive.Empty>
              ) : (
                suggestions.map((suggestion) => (
                  <CommandPrimitive.Item
                    key={suggestion.id}
                    value={suggestion.id}
                    onSelect={() => {
                      onSelect(suggestion);
                      setOpen(false);
                    }}
                    className="data-[selected=true]:bg-accent data-[selected=true]:text-accent-foreground flex cursor-pointer flex-col gap-0.5 rounded-sm px-3 py-2 font-sans text-sm outline-none"
                  >
                    <span>{suggestion.label}</span>
                    {suggestion.description && (
                      <span className="text-muted-foreground text-xs">
                        {suggestion.description}
                      </span>
                    )}
                  </CommandPrimitive.Item>
                ))
              )}
            </CommandPrimitive.List>
          </PopoverPrimitive.Content>
        </PopoverPrimitive.Portal>
      </PopoverPrimitive.Root>
    </CommandPrimitive>
  );
}
