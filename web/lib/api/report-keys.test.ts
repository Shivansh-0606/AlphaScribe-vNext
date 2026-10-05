import { QueryClient } from "@tanstack/react-query";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { reportKeys } from "./report-keys";

/**
 * The factory's whole job is prefix relationships, so these tests seed a real
 * `QueryClient` cache and ask TanStack Query itself which entries a prefix
 * reaches — the same matching `invalidateQueries`/`removeQueries` use — rather
 * than re-implementing prefix matching in the test.
 */
const SEEDED = {
  libraryList: reportKeys.list("research-library", "MSFT"),
  researchList: reportKeys.list("company-research", "MSFT"),
  comparisonList: reportKeys.list("comparison", ""),
  homeList: reportKeys.list("workspace-home", "recent", 10),
  libraryDetail: reportKeys.detail("r1", "research-library"),
  researchDetail: reportKeys.detail("r1", "company-research"),
  researchStatus: reportKeys.status("r1", "company-research"),
  otherDetail: reportKeys.detail("r2", "research-library"),
  otherStatus: reportKeys.status("r2", "company-research"),
  compare: reportKeys.compare(["r1", "r2"]),
} as const;

function seededClient() {
  const client = new QueryClient();
  for (const key of Object.values(SEEDED)) client.setQueryData(key, {});
  return client;
}

function reachedBy(client: QueryClient, prefix: readonly unknown[]) {
  return client
    .getQueryCache()
    .findAll({ queryKey: prefix })
    .map((query) => JSON.stringify(query.queryKey))
    .sort();
}

function keysOf(...names: Array<keyof typeof SEEDED>) {
  return names.map((name) => JSON.stringify(SEEDED[name])).sort();
}

describe("reportKeys", () => {
  let client: QueryClient;
  beforeEach(() => {
    client = seededClient();
  });
  afterEach(() => client.clear());

  it("has the documented shapes (brief §3.3), so the keys are a stable contract", () => {
    expect(reportKeys.list("comparison", "MSFT")).toEqual([
      "reports",
      "list",
      "comparison",
      "MSFT",
    ]);
    expect(reportKeys.lists()).toEqual(["reports", "list"]);
    expect(reportKeys.detail("r1", "research-library")).toEqual([
      "reports",
      "detail",
      "r1",
      "research-library",
    ]);
    expect(reportKeys.detailsFor("r1")).toEqual(["reports", "detail", "r1"]);
    expect(reportKeys.status("r1", "company-research")).toEqual([
      "reports",
      "status",
      "r1",
      "company-research",
    ]);
    expect(reportKeys.statusFor("r1")).toEqual(["reports", "status", "r1"]);
    expect(reportKeys.compare(["a", "b"])).toEqual(["reports", "compare", "a", "b"]);
    expect(reportKeys.compares()).toEqual(["reports", "compare"]);
  });

  it("lists() reaches every feature's list and nothing else", () => {
    expect(reachedBy(client, reportKeys.lists())).toEqual(
      keysOf("libraryList", "researchList", "comparisonList", "homeList"),
    );
  });

  it("detailsFor(id) reaches that report's detail in every feature, and no other report's", () => {
    expect(reachedBy(client, reportKeys.detailsFor("r1"))).toEqual(
      keysOf("libraryDetail", "researchDetail"),
    );
  });

  it("statusFor(id) reaches that report's status only — not its detail, not another report's status", () => {
    expect(reachedBy(client, reportKeys.statusFor("r1"))).toEqual(keysOf("researchStatus"));
  });

  it("compares() reaches cached compares and nothing else", () => {
    expect(reachedBy(client, reportKeys.compares())).toEqual(keysOf("compare"));
  });

  it("compare() is order-insensitive: the same selection is one cache entry", () => {
    expect(reportKeys.compare(["b", "a", "c"])).toEqual(reportKeys.compare(["c", "a", "b"]));
  });

  it("compare() does not reorder the caller's array", () => {
    const ids = ["b", "a"];
    reportKeys.compare(ids);
    expect(ids).toEqual(["b", "a"]);
  });
});
