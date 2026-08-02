import { describe, expect, it } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { MetricStat } from "./MetricStat";

describe("MetricStat", () => {
  it("renders label and value", () => {
    renderWithProviders(<MetricStat label="Revenue" value="$100B" />);
    expect(screen.getByText("Revenue")).toBeInTheDocument();
    expect(screen.getByText("$100B")).toBeInTheDocument();
  });

  it("omits the direction indicator when not given (never a guessed sign)", () => {
    renderWithProviders(<MetricStat label="Guidance" value="Raised" />);
    expect(screen.queryByText("increase", { exact: false })).not.toBeInTheDocument();
    expect(screen.queryByText("decrease", { exact: false })).not.toBeInTheDocument();
  });

  it("shows an up indicator with an accessible word, not color alone", () => {
    renderWithProviders(<MetricStat label="Revenue YoY" value="+8.2%" direction="up" />);
    expect(screen.getByText("increase", { exact: false })).toBeInTheDocument();
  });

  it("shows a down indicator with an accessible word", () => {
    renderWithProviders(<MetricStat label="Revenue YoY" value="-3%" direction="down" />);
    expect(screen.getByText("decrease", { exact: false })).toBeInTheDocument();
  });

  it("renders the optional meaning caption", () => {
    renderWithProviders(<MetricStat label="EPS" value="$1.23" meaning="Beat consensus by $0.05" />);
    expect(screen.getByText("Beat consensus by $0.05")).toBeInTheDocument();
  });
});
