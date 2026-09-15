import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import type { AppError } from "@/lib/errors/app-error";
import { FilingQAPanel } from "./FilingQAPanel";

const createFilingQA = vi.fn();
const fetchFilingQA = vi.fn();
const cancelFilingQA = vi.fn();
const openFilingQAStream = vi.fn();

vi.mock("../integration/api", () => ({
  createFilingQA: (...args: unknown[]) => createFilingQA(...args),
  fetchFilingQA: (...args: unknown[]) => fetchFilingQA(...args),
  cancelFilingQA: (...args: unknown[]) => cancelFilingQA(...args),
  openFilingQAStream: (...args: unknown[]) => openFilingQAStream(...args),
}));

interface StreamHandlers {
  onEvent: (event: Record<string, unknown>) => void;
  onEnd: () => void;
  onError: (error: AppError) => void;
}

function lastStreamHandlers(): StreamHandlers {
  const call = openFilingQAStream.mock.calls.at(-1) as
    [string, string, string, StreamHandlers] | undefined;
  if (!call) throw new Error("openFilingQAStream was never called");
  return call[3];
}

const CHUNKS = [{ chunk_idx: 0, text: "The filing discloses supply-chain concentration risk." }];

function answer(overrides: Record<string, unknown> = {}) {
  return {
    ticker: "AAPL",
    doc_id: "d1",
    question: "What are the key risks?",
    answer_text: "The filing discloses supply-chain concentration risk [1].",
    sources: [{ index: 1, doc_id: "d1", chunk_start: 0, chunk_end: 0 }],
    cited_source_indices: [1],
    state: "answered",
    coverage_boundaries: [],
    created_at: "2026-01-01T00:00:00Z",
    prompt_version: "v1",
    schema_version: "v1",
    ...overrides,
  };
}

async function askQuestion(user: ReturnType<typeof renderWithProviders>["user"], text: string) {
  await user.type(
    screen.getByLabelText(/Ask a question about this filing|Ask another question/),
    text,
  );
  await user.click(screen.getByRole("button", { name: "Ask" }));
}

describe("FilingQAPanel", () => {
  beforeEach(() => {
    createFilingQA.mockReset();
    fetchFilingQA.mockReset();
    cancelFilingQA.mockReset().mockResolvedValue({ id: "job-1", status: "cancelled" });
    openFilingQAStream.mockReset().mockReturnValue(vi.fn());
  });

  it("starts idle with a question form, never creating a job until submitted", () => {
    renderWithProviders(
      <FilingQAPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    expect(screen.getByLabelText("Ask a question about this filing")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Ask" })).toBeDisabled();
    expect(createFilingQA).not.toHaveBeenCalled();
  });

  it("runs the answering → completed lifecycle and renders the grounded answer", async () => {
    createFilingQA.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const { user } = renderWithProviders(
      <FilingQAPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    await askQuestion(user, "What are the key risks?");
    expect(createFilingQA).toHaveBeenCalledWith("AAPL", "d1", {
      question: "What are the key risks?",
    });

    await waitFor(() =>
      expect(openFilingQAStream).toHaveBeenCalledWith("AAPL", "d1", "job-1", expect.anything()),
    );
    expect(screen.getByText("Answering the question…")).toBeInTheDocument();

    const handlers = lastStreamHandlers();
    handlers.onEvent({ node: "pipeline", status: "start", message: "Answering question" });
    handlers.onEvent({
      node: "retrieving",
      status: "ok",
      message: "Selecting relevant filing excerpts",
    });
    expect(await screen.findByText("Selecting relevant filing excerpts")).toBeInTheDocument();

    handlers.onEvent({ node: "pipeline", status: "ok" });
    handlers.onEvent({ node: "final", status: "ok", answer: answer() });
    handlers.onEnd();

    const region = await screen.findByRole("region", { name: "Answer" });
    expect(region).toHaveTextContent("supply-chain concentration risk");
    expect(screen.getByText("Q: What are the key risks?")).toBeInTheDocument();
    // Honest complete state — no "Partial"/"Insufficient evidence" badge.
    expect(screen.queryByText("Partial")).not.toBeInTheDocument();
    expect(screen.queryByText("Insufficient evidence")).not.toBeInTheDocument();
  });

  it("derives the viewer's partial state from non-empty coverage_boundaries on an answered result", async () => {
    createFilingQA.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const { user } = renderWithProviders(
      <FilingQAPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    await askQuestion(user, "What are the key risks?");
    await waitFor(() => expect(openFilingQAStream).toHaveBeenCalled());

    lastStreamHandlers().onEvent({
      node: "final",
      status: "ok",
      answer: answer({
        state: "answered",
        coverage_boundaries: ["only part of the risk section could be located"],
      }),
    });

    expect(await screen.findByText("Partial")).toBeInTheDocument();
    expect(screen.getByText(/only part of the risk section could be located/)).toBeInTheDocument();
  });

  it("renders an honest insufficient_evidence result, never a fabricated answer", async () => {
    createFilingQA.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const { user } = renderWithProviders(
      <FilingQAPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    await askQuestion(user, "What is the CEO's favorite color?");
    await waitFor(() => expect(openFilingQAStream).toHaveBeenCalled());

    lastStreamHandlers().onEvent({
      node: "final",
      status: "ok",
      answer: answer({
        answer_text: "",
        sources: [],
        cited_source_indices: [],
        state: "insufficient_evidence",
        coverage_boundaries: ["the filing's persisted excerpts do not address this question"],
      }),
    });

    expect(await screen.findByText("Insufficient evidence")).toBeInTheDocument();
    expect(screen.getByText(/Not enough grounded evidence/)).toBeInTheDocument();
  });

  it("a 422 (e.g. empty question) shows an inline form error without creating a job", async () => {
    const { AppError } = await import("@/lib/errors/app-error");
    createFilingQA.mockRejectedValueOnce(new AppError("validation", "question is required"));
    const { user } = renderWithProviders(
      <FilingQAPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    await askQuestion(user, "?");

    expect(await screen.findByRole("alert")).toHaveTextContent("question is required");
    // Still idle — the form is still there, no stream was ever opened.
    expect(screen.getByLabelText("Ask a question about this filing")).toBeInTheDocument();
    expect(openFilingQAStream).not.toHaveBeenCalled();
  });

  it("surfaces a failed run honestly, with retry", async () => {
    createFilingQA.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const { user } = renderWithProviders(
      <FilingQAPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    await askQuestion(user, "What are the key risks?");
    await waitFor(() => expect(openFilingQAStream).toHaveBeenCalled());

    lastStreamHandlers().onEvent({
      node: "pipeline",
      status: "error",
      message: "Filing Q&A failed. See server logs for details.",
    });

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Filing Q&A failed. See server logs for details.",
    );
    expect(screen.getByRole("button", { name: "Retry" })).toBeInTheDocument();
  });

  it("cancelling stops the run and reports it honestly, without waiting on the server", async () => {
    createFilingQA.mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false });
    const closeStream = vi.fn();
    openFilingQAStream.mockReturnValue(closeStream);
    const { user } = renderWithProviders(
      <FilingQAPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    await askQuestion(user, "What are the key risks?");
    await waitFor(() => expect(openFilingQAStream).toHaveBeenCalled());

    await user.click(screen.getByRole("button", { name: "Stop" }));

    expect(closeStream).toHaveBeenCalled();
    expect(cancelFilingQA).toHaveBeenCalledWith("AAPL", "d1", "job-1");
    expect(await screen.findByText("Question was cancelled.")).toBeInTheDocument();
  });

  it("asking another question after a completed answer shows only the new result, never the old one", async () => {
    createFilingQA
      .mockResolvedValueOnce({ id: "job-1", status: "queued", reused: false })
      .mockResolvedValueOnce({ id: "job-2", status: "queued", reused: false });
    const { user } = renderWithProviders(
      <FilingQAPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    await askQuestion(user, "What are the key risks?");
    await waitFor(() => expect(openFilingQAStream).toHaveBeenCalledTimes(1));
    lastStreamHandlers().onEvent({
      node: "final",
      status: "ok",
      answer: answer({ question: "What are the key risks?" }),
    });
    expect(await screen.findByText("Q: What are the key risks?")).toBeInTheDocument();

    await askQuestion(user, "What is the revenue guidance?");
    await waitFor(() => expect(openFilingQAStream).toHaveBeenCalledTimes(2));
    expect(openFilingQAStream).toHaveBeenLastCalledWith("AAPL", "d1", "job-2", expect.anything());
    // Old answer's question text is gone the moment a new job starts — no history.
    expect(screen.queryByText("Q: What are the key risks?")).not.toBeInTheDocument();

    lastStreamHandlers().onEvent({
      node: "final",
      status: "ok",
      answer: answer({
        question: "What is the revenue guidance?",
        answer_text: "Management expects modest revenue growth [1].",
      }),
    });
    expect(await screen.findByText("Q: What is the revenue guidance?")).toBeInTheDocument();
    expect(screen.queryByText("Q: What are the key risks?")).not.toBeInTheDocument();
  });

  it("has no detectable accessibility violations in the idle state", async () => {
    const { container } = renderWithProviders(
      <FilingQAPanel ticker="AAPL" docId="d1" source="10-Q FY24 Q3" chunks={CHUNKS} />,
    );
    expect(await axe(container)).toHaveNoViolations();
  });
});
