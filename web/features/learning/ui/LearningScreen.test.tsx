import { axe } from "jest-axe";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders, screen, waitFor } from "@/tests/setup/render";
import { useAiAccessStore } from "@/lib/state/aiAccess";
import type { ExplanationDoc } from "../integration/schemas";
import { LearningScreen } from "./LearningScreen";

const push = vi.fn();
vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
  usePathname: () => "/learning",
}));

const requestExplanation = vi.fn();
const fetchExplanation = vi.fn();
const cancelExplanation = vi.fn();
const openExplanationStream = vi.fn();

vi.mock("../integration/api", () => ({
  requestExplanation: (...args: unknown[]) => requestExplanation(...args),
  fetchExplanation: (...args: unknown[]) => fetchExplanation(...args),
  cancelExplanation: (...args: unknown[]) => cancelExplanation(...args),
  openExplanationStream: (...args: unknown[]) => openExplanationStream(...args),
}));

interface StreamHandlers {
  onEvent: (event: Record<string, unknown>) => void;
  onEnd: () => void;
  onError: (error: unknown) => void;
}

function lastStreamHandlers(): StreamHandlers {
  const call = openExplanationStream.mock.calls.at(-1) as [string, StreamHandlers] | undefined;
  if (!call) throw new Error("openExplanationStream was never called");
  return call[1];
}

const EXPLANATION: ExplanationDoc = {
  id: "job-2",
  ticker: "MSFT",
  concept: "What is operating margin?",
  explanation: "Operating margin is operating income divided by revenue [1].",
  source_documents: [
    { doc_id: "d1", ticker: "MSFT", source: "10-Q FY24 Q4", chunk_idx: 0, text: "…", score: 0.9 },
  ],
  created_at: "2026-01-01T00:00:00Z",
};

describe("LearningScreen", () => {
  beforeEach(() => {
    useAiAccessStore.getState().clear();
    push.mockReset();
    requestExplanation.mockReset();
    fetchExplanation.mockReset();
    cancelExplanation.mockReset().mockResolvedValue({ id: "job-2", status: "cancelled" });
    openExplanationStream.mockReset().mockReturnValue(vi.fn());
  });

  // Empty Behaviour (06_UX_Specifications.md SCR-08): "missing company context → prompt to choose an example".
  it("prompts to choose an example company when there is no ticker context", async () => {
    const { user } = renderWithProviders(<LearningScreen />);
    expect(screen.getByText(/choose an example/)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Ask" })).not.toBeInTheDocument();

    await user.type(screen.getByLabelText("Example company ticker"), "msft");
    await user.click(screen.getByRole("button", { name: "Continue" }));
    expect(push).toHaveBeenCalledWith("/learning?ticker=MSFT");
  });

  it("routes to Settings instead of rendering a dead composer when AI access isn't set up", () => {
    useAiAccessStore.getState().setByokFields({});
    renderWithProviders(<LearningScreen initialTicker="MSFT" />);
    expect(screen.getByRole("link", { name: "Set up AI access" })).toHaveAttribute(
      "href",
      "/settings",
    );
    expect(screen.queryByRole("button", { name: "Ask" })).not.toBeInTheDocument();
  });

  it("asks for an explanation and renders the grounded answer", async () => {
    requestExplanation.mockResolvedValueOnce({ id: "job-2" });
    const { user } = renderWithProviders(
      <LearningScreen initialTicker="MSFT" contextReportId="job-1" />,
    );

    await user.type(
      screen.getByLabelText(/What concept do you want explained/),
      "What is operating margin?",
    );
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(requestExplanation).toHaveBeenCalledWith(
      expect.objectContaining({ ticker: "MSFT", context_report_id: "job-1" }),
    );
    await waitFor(() => expect(openExplanationStream).toHaveBeenCalled());

    lastStreamHandlers().onEvent({ node: "final", status: "ok", explanation: EXPLANATION });
    lastStreamHandlers().onEnd();

    expect(await screen.findByText("What is operating margin?")).toBeInTheDocument();
    expect(screen.getByText(/operating income divided by revenue/)).toBeInTheDocument();
  });

  it("cancel stops the run and shows feedback immediately", async () => {
    requestExplanation.mockResolvedValueOnce({ id: "job-2" });
    const { user } = renderWithProviders(<LearningScreen initialTicker="MSFT" />);
    await user.type(screen.getByLabelText(/What concept do you want explained/), "EPS?");
    await user.click(screen.getByRole("button", { name: "Ask" }));
    await waitFor(() => expect(openExplanationStream).toHaveBeenCalled());

    await user.click(screen.getByRole("button", { name: "Stop generating" }));

    expect(cancelExplanation).toHaveBeenCalledWith("job-2");
    expect(await screen.findByText("Cancelled.")).toBeInTheDocument();
  });

  // The honest point of Phase 8: the proposed backend doesn't exist yet, so
  // a real 404/network failure is the expected live behavior, not a crash.
  it("surfaces a real request failure honestly instead of crashing", async () => {
    requestExplanation.mockRejectedValueOnce(new Error("404: no such endpoint"));
    const { user } = renderWithProviders(<LearningScreen initialTicker="MSFT" />);
    await user.type(screen.getByLabelText(/What concept do you want explained/), "EPS?");
    await user.click(screen.getByRole("button", { name: "Ask" }));

    expect(await screen.findByText(/404: no such endpoint/)).toBeInTheDocument();
  });

  it("has no detectable accessibility violations in the composer state", async () => {
    const { container } = renderWithProviders(<LearningScreen initialTicker="MSFT" />);
    expect(await axe(container)).toHaveNoViolations();
  });
});
