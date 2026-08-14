import { afterEach, describe, expect, it, vi } from "vitest";
import { z } from "zod";
import { apiFetch } from "./fetch-client";

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

const SCHEMA = z.object({ ok: z.boolean() });

describe("apiFetch error normalization", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("reads the backend's real {detail, type} envelope (domain_error_handler), not {message}", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          jsonResponse(429, {
            detail: "Too many acquisition requests for this ticker. Retry in a moment.",
            type: "rate_limited",
          }),
        ),
    );

    await expect(
      apiFetch("/api/companies/AAPL/financials/acquire", SCHEMA, { method: "POST" }),
    ).rejects.toMatchObject({
      message: "Too many acquisition requests for this ticker. Retry in a moment.",
    });
  });

  it("reads FastAPI's array-shaped detail from RequestValidationError (missing/invalid query param)", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        jsonResponse(422, {
          detail: [{ type: "missing", loc: ["query", "period_type"], msg: "Field required" }],
        }),
      ),
    );

    await expect(apiFetch("/api/companies/AAPL/financials/acquire", SCHEMA)).rejects.toMatchObject({
      message: "Field required",
    });
  });

  it("falls back to the generic status-derived message when the error body has no detail", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(500, { oops: true })));

    await expect(apiFetch("/api/x", SCHEMA)).rejects.toMatchObject({
      message: "Server error.",
    });
  });

  it("falls back to the generic status-derived message on a non-JSON error body", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(new Response("<html>502 Bad Gateway</html>", { status: 502 })),
    );

    await expect(apiFetch("/api/x", SCHEMA)).rejects.toMatchObject({
      message: "Server error.",
    });
  });

  it("maps 401 to auth_required with the backend's own message", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue(
          jsonResponse(401, { detail: "Not authenticated", type: "unauthenticated" }),
        ),
    );

    await expect(apiFetch("/api/x", SCHEMA)).rejects.toMatchObject({
      kind: "auth_required",
      message: "Not authenticated",
    });
  });

  it("still validates and returns a successful response unchanged", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(200, { ok: true })));

    await expect(apiFetch("/api/x", SCHEMA)).resolves.toEqual({ ok: true });
  });

  it("surfaces a network failure as a network AppError, unaffected by the detail-parsing change", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("fetch failed")));

    await expect(apiFetch("/api/x", SCHEMA)).rejects.toMatchObject({
      kind: "network",
      message: "Unable to reach the server.",
    });
  });
});
