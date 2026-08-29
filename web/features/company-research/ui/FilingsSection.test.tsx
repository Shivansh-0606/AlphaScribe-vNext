import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, within } from "@/tests/setup/render";
import { FilingsSection } from "./FilingsSection";

const fetchFilings = vi.fn();
const fetchFilingContent = vi.fn();
vi.mock("../integration/api", () => ({
  fetchFilings: (...args: unknown[]) => fetchFilings(...args),
  fetchFilingContent: (...args: unknown[]) => fetchFilingContent(...args),
}));

const FILING = {
  doc_id: "d1",
  ticker: "AAPL",
  company_name: "Apple Inc.",
  source: "10-Q FY24 Q3",
  num_chunks: 12,
  char_count: 45000,
  created_at: "2026-01-01T00:00:00Z",
};

function contentResponse(chunks: { chunk_idx: number; text: string }[]) {
  return {
    doc_id: "d1",
    ticker: "AAPL",
    company_name: "Apple Inc.",
    source: "10-Q FY24 Q3",
    created_at: "2026-01-01T00:00:00Z",
    num_chunks: chunks.length,
    char_count: 45000,
    content: { chunks },
  };
}

describe("FilingsSection", () => {
  beforeEach(() => {
    fetchFilings.mockReset();
    fetchFilingContent.mockReset();
  });

  it("shows an empty state pointing to Overview's ingest actions when there are no filings", async () => {
    fetchFilings.mockResolvedValueOnce({ filings: [] });
    renderWithProviders(<FilingsSection ticker="AAPL" />);
    expect(await screen.findByText(/No filings ingested for AAPL yet/)).toBeInTheDocument();
  });

  it("renders the real filing list with a per-filing Read content control", async () => {
    fetchFilings.mockResolvedValueOnce({ filings: [FILING] });
    renderWithProviders(<FilingsSection ticker="AAPL" />);
    expect(await screen.findByText("10-Q FY24 Q3")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Read content" })).toBeInTheDocument();
  });

  it("surfaces a filings load failure with retry", async () => {
    fetchFilings.mockRejectedValueOnce(new Error("network"));
    renderWithProviders(<FilingsSection ticker="AAPL" />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Couldn't load filings.");
  });

  it("reads a filing's content and renders its chunks in order on demand", async () => {
    fetchFilings.mockResolvedValueOnce({ filings: [FILING] });
    fetchFilingContent.mockResolvedValueOnce(
      contentResponse([
        { chunk_idx: 0, text: "First chunk." },
        { chunk_idx: 1, text: "Second chunk." },
      ]),
    );
    const { user } = renderWithProviders(<FilingsSection ticker="AAPL" />);
    await user.click(await screen.findByRole("button", { name: "Read content" }));

    const region = await screen.findByRole("region", { name: /Filing content: 10-Q FY24 Q3/ });
    const items = within(region).getAllByRole("listitem");
    expect(items.map((li) => li.getAttribute("data-chunk-idx"))).toEqual(["0", "1"]);
    expect(items[0]).toHaveTextContent("First chunk.");
    expect(fetchFilingContent).toHaveBeenCalledWith("AAPL", "d1");
  });

  it("shows an honest empty state for a known filing with no stored chunks", async () => {
    fetchFilings.mockResolvedValueOnce({ filings: [FILING] });
    fetchFilingContent.mockResolvedValueOnce(contentResponse([]));
    const { user } = renderWithProviders(<FilingsSection ticker="AAPL" />);
    await user.click(await screen.findByRole("button", { name: "Read content" }));
    expect(
      await screen.findByText("No readable content is stored for this filing."),
    ).toBeInTheDocument();
  });

  it("surfaces a content load failure with retry, without touching the list", async () => {
    fetchFilings.mockResolvedValueOnce({ filings: [FILING] });
    fetchFilingContent.mockRejectedValueOnce(new Error("boom"));
    const { user } = renderWithProviders(<FilingsSection ticker="AAPL" />);
    await user.click(await screen.findByRole("button", { name: "Read content" }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Couldn't load this filing's content.",
    );
    // the list is still there
    expect(screen.getByText("10-Q FY24 Q3")).toBeInTheDocument();
  });

  it("has no detectable accessibility violations with content open", async () => {
    fetchFilings.mockResolvedValueOnce({ filings: [FILING] });
    fetchFilingContent.mockResolvedValueOnce(
      contentResponse([{ chunk_idx: 0, text: "Readable filing text." }]),
    );
    const { user, container } = renderWithProviders(<FilingsSection ticker="AAPL" />);
    await user.click(await screen.findByRole("button", { name: "Read content" }));
    await screen.findByRole("region", { name: /Filing content/ });

    expect(await axe(container)).toHaveNoViolations();
  });
});
