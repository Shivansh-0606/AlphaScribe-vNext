"use client";

import { CaretDown, CaretUp } from "@phosphor-icons/react/dist/ssr";
import type { ComponentProps } from "react";
import {
  Table as TablePrimitive,
  TableBody,
  TableCaption,
  TableFooter,
  TableHeader as TableHeaderPrimitive,
  TableRow,
} from "@/components/ui/table";
import { cn } from "@/lib/utils";

/**
 * Table (Family 05) — docs/experience_design/Components/05_Content_Data_Display.md.
 * `Table`/`TableBody`/`TableFooter`/`TableCaption`/`TableRow` re-exported as
 * generated (native `<table>` semantics + the horizontal-scroll container
 * shadcn already wraps it in — the frozen "scroll within the region, not the
 * page" rule). Only `TableHeader` (sticky), `TableHead` (numeric + sort), and
 * `TableCell` (numeric + partial-failure) are wrapped, to add the
 * distinctive finance-table behavior the spec calls out.
 */
export function TableHeader({
  sticky,
  className,
  ...props
}: ComponentProps<"thead"> & { sticky?: boolean }) {
  return (
    <TableHeaderPrimitive
      className={cn(sticky && "bg-surface sticky top-0 z-[var(--z-raised)]", className)}
      {...props}
    />
  );
}

export interface TableHeadProps extends ComponentProps<"th"> {
  /** Right-aligns + `type.figure` (tabular mono) — for numeric columns. */
  numeric?: boolean;
  /** Sets `aria-sort`; pass `onSort` to render an interactive sort trigger with a direction caret. */
  sortDirection?: "ascending" | "descending" | "none";
  onSort?: () => void;
}

export function TableHead({
  numeric,
  sortDirection,
  onSort,
  className,
  children,
  ...props
}: TableHeadProps) {
  return (
    <th
      scope="col"
      aria-sort={sortDirection}
      className={cn(
        "text-muted-foreground h-10 px-2 align-middle font-medium whitespace-nowrap",
        numeric ? "text-right font-mono tabular-nums" : "text-left",
        className,
      )}
      {...props}
    >
      {onSort ? (
        <button
          type="button"
          onClick={onSort}
          className="hover:text-foreground inline-flex items-center gap-1"
        >
          {children}
          {sortDirection === "ascending" && <CaretUp className="size-3" aria-hidden="true" />}
          {sortDirection === "descending" && <CaretDown className="size-3" aria-hidden="true" />}
        </button>
      ) : (
        children
      )}
    </th>
  );
}

export interface TableCellProps extends ComponentProps<"td"> {
  /** Right-aligns + `type.figure` (tabular mono, decimal-aligned) — for numeric columns. */
  numeric?: boolean;
  /**
   * Renders explicit "unavailable" text instead of the cell going silently
   * blank (Inventory Partial Failure rule). `true` → "Not available";
   * a string → that exact label (e.g. "Not comparable").
   */
  unavailable?: boolean | string;
}

export function TableCell({ numeric, unavailable, className, children, ...props }: TableCellProps) {
  return (
    <td
      className={cn(
        "p-2 align-middle whitespace-nowrap",
        numeric && "text-right font-mono tabular-nums",
        unavailable && "text-muted-foreground italic",
        className,
      )}
      {...props}
    >
      {unavailable ? (typeof unavailable === "string" ? unavailable : "Not available") : children}
    </td>
  );
}

export { TableBody, TableCaption, TableFooter, TablePrimitive as Table, TableRow };
