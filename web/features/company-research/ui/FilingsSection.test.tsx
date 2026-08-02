import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen } from "@/tests/setup/render";
import { FilingsSection } from "./FilingsSection";

const fetchFilings = vi.fn();
vi.mock("../integration/api", () => ({
  fetchFilings: (...args: unknown[]) => fetchFilings(...args),
}));

describe("FilingsSection", () => {
  beforeEach(() => {
    fetchFilings.mockReset();
  });

  it("shows an empty state pointing to Overview's ingest actions when there are no filings", async () => {
    fetchFilings.mockResolvedValueOnce({ filings: [] });
    renderWithProviders(<FilingsSection ticker="AAPL" />);
    expect(await screen.findByText(/No filings ingested for AAPL yet/)).toBeInTheDocument();
  });

  it("renders the real filing list plus the content-viewing placeholder", async () => {
    fetchFilings.mockResolvedValueOnce({
      filings: [
        {
          doc_id: "d1",
          ticker: "AAPL",
          company_name: "Apple Inc.",
          source: "10-Q FY24 Q3",
          num_chunks: 12,
          char_count: 45000,
          created_at: "2026-01-01T00:00:00Z",
        },
      ],
    });
    renderWithProviders(<FilingsSection ticker="AAPL" />);
    expect(await screen.findByText("10-Q FY24 Q3")).toBeInTheDocument();
    // The content-viewing placeholder is always present — never fabricated content.
    expect(screen.getByText(/Reading a filing's full content/)).toBeInTheDocument();
  });

  it("surfaces a load failure with retry", async () => {
    fetchFilings.mockRejectedValueOnce(new Error("network"));
    renderWithProviders(<FilingsSection ticker="AAPL" />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't load filings.");
  });

  it("has no detectable accessibility violations with a filing rendered", async () => {
    fetchFilings.mockResolvedValueOnce({
      filings: [
        {
          doc_id: "d1",
          ticker: "AAPL",
          company_name: "Apple Inc.",
          source: "10-Q FY24 Q3",
          num_chunks: 12,
          char_count: 45000,
          created_at: "2026-01-01T00:00:00Z",
        },
      ],
    });
    const { container } = renderWithProviders(<FilingsSection ticker="AAPL" />);
    await screen.findByText("10-Q FY24 Q3");

    expect(await axe(container)).toHaveNoViolations();
  });
});
