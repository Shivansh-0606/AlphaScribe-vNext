import { describe, expect, it } from "vitest";
import {
  ACCOUNT_SETUP,
  APP,
  COMPANY_RESEARCH,
  COMPARISON,
  LEARNING,
  RESEARCH_LIBRARY,
  WORKSPACE_HOME,
} from "./testIds";

const DOMAINS = {
  APP,
  WORKSPACE_HOME,
  COMPANY_RESEARCH,
  COMPARISON,
  RESEARCH_LIBRARY,
  LEARNING,
  ACCOUNT_SETUP,
};

/** Dynamic-ID factories (functions) are excluded — a collision only exists
 * once a factory produces a concrete string, which is the caller's concern,
 * not this file's. */
function staticValues(): string[] {
  return Object.values(DOMAINS).flatMap((domain) =>
    Object.values(domain).filter((value): value is string => typeof value === "string"),
  );
}

describe("testIds", () => {
  it("has no duplicate static test ID values across any domain", () => {
    const values = staticValues();
    expect(values).toHaveLength(new Set(values).size);
  });
});
