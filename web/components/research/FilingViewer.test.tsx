import { axe } from "jest-axe";
import { describe, expect, it } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { FilingViewer } from "./FilingViewer";

describe("FilingViewer (Filing content variant)", () => {
  it("renders chunks verbatim, in the order given, as a labelled scroll region", () => {
    render(
      <FilingViewer
        source="10-Q FY24 Q3"
        chunks={[
          { chunk_idx: 0, text: "  leading & trailing spaces kept  " },
          { chunk_idx: 1, text: "line one\nline two" },
        ]}
      />,
    );
    const region = screen.getByRole("region", { name: "Filing content: 10-Q FY24 Q3" });
    expect(region).toHaveAttribute("tabindex", "0");
    const items = within(region).getAllByRole("listitem");
    expect(items).toHaveLength(2);
    expect(items[0]).toHaveAttribute("data-chunk-idx", "0");
    // verbatim text — no trim, no reflow
    expect(items[0]).toHaveTextContent("leading & trailing spaces kept");
    expect(items[1].textContent).toBe("line one\nline two");
  });

  it("shows an honest no-content state for zero chunks, never fabricated text", () => {
    render(<FilingViewer source="10-K FY23" chunks={[]} />);
    expect(screen.getByText("No readable content is stored for this filing.")).toBeInTheDocument();
    expect(screen.queryByRole("region")).not.toBeInTheDocument();
  });

  it("has no detectable accessibility violations", async () => {
    const { container } = render(
      <FilingViewer source="10-Q FY24 Q3" chunks={[{ chunk_idx: 0, text: "Some filing text." }]} />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
