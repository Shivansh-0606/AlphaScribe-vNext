import { afterEach, describe, expect, it, vi } from "vitest";
import { deleteReport } from "./api";

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("deleteReport", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("sends DELETE /api/reports/{id} with the session cookie and returns the parsed body", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, { deleted: "r1" }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(deleteReport("r1")).resolves.toEqual({ deleted: "r1" });

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toMatch(/\/api\/reports\/r1$/);
    expect(init.method).toBe("DELETE");
    expect(init.credentials).toBe("include");
  });

  it("rejects with a validation error when the body isn't {deleted: string} (trust boundary)", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(200, { ok: true })));

    await expect(deleteReport("r1")).rejects.toMatchObject({ kind: "validation" });
  });

  it("surfaces a 404 as an error with status 404 — the shape the delete hook treats as 'already gone'", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(jsonResponse(404, { detail: "report not found" })),
    );

    await expect(deleteReport("r1")).rejects.toMatchObject({
      kind: "unknown",
      status: 404,
      message: "report not found",
    });
  });
});
