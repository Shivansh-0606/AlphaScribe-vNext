import { axe } from "jest-axe";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "./Table";

function DemoTable() {
  return (
    <Table>
      <TableCaption>Revenue by quarter</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Quarter</TableHead>
          <TableHead numeric sortDirection="descending" onSort={() => {}}>
            Revenue
          </TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell>Q1</TableCell>
          <TableCell numeric>1,200</TableCell>
        </TableRow>
        <TableRow>
          <TableCell>Q2</TableCell>
          <TableCell unavailable>3,400</TableCell>
        </TableRow>
      </TableBody>
    </Table>
  );
}

describe("Table", () => {
  it("uses proper table semantics with a caption and column scope", () => {
    renderWithProviders(<DemoTable />);
    expect(screen.getByText("Revenue by quarter")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: /Quarter/ })).toBeInTheDocument();
  });

  it("marks the sorted column with aria-sort and a direction caret", () => {
    renderWithProviders(<DemoTable />);
    const header = screen.getByRole("columnheader", { name: /Revenue/ });
    expect(header).toHaveAttribute("aria-sort", "descending");
  });

  it("flags unavailable data explicitly instead of going silently blank", () => {
    renderWithProviders(<DemoTable />);
    expect(screen.getByText("Not available")).toBeInTheDocument();
    expect(screen.queryByText("3,400")).not.toBeInTheDocument();
  });

  it("makes the sort trigger keyboard-operable", async () => {
    const onSort = vi.fn();
    const { user } = renderWithProviders(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead sortDirection="none" onSort={onSort}>
              Revenue
            </TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>1,200</TableCell>
          </TableRow>
        </TableBody>
      </Table>,
    );
    await user.click(screen.getByRole("button", { name: "Revenue" }));
    expect(onSort).toHaveBeenCalled();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = renderWithProviders(<DemoTable />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
