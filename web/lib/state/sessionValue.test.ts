import { beforeEach, describe, expect, it } from "vitest";
import { readSessionValue, removeSessionValue, writeSessionValue } from "./sessionValue";

describe("sessionValue", () => {
  beforeEach(() => {
    sessionStorage.clear();
  });

  it("round-trips a value through write/read", () => {
    writeSessionValue("k", "hello");
    expect(readSessionValue("k")).toBe("hello");
  });

  it("returns null for a key that was never written", () => {
    expect(readSessionValue("missing")).toBeNull();
  });

  it("remove clears a previously written value", () => {
    writeSessionValue("k", "hello");
    removeSessionValue("k");
    expect(readSessionValue("k")).toBeNull();
  });

  it("removing a key that was never written is a safe no-op", () => {
    expect(() => removeSessionValue("missing")).not.toThrow();
  });

  it("never throws when the underlying storage throws (private browsing / quota)", () => {
    const throwing: Pick<Storage, "getItem" | "setItem" | "removeItem"> = {
      getItem: () => {
        throw new Error("blocked");
      },
      setItem: () => {
        throw new Error("blocked");
      },
      removeItem: () => {
        throw new Error("blocked");
      },
    };
    const original = window.sessionStorage;
    Object.defineProperty(window, "sessionStorage", { value: throwing, configurable: true });

    try {
      expect(() => writeSessionValue("k", "v")).not.toThrow();
      expect(readSessionValue("k")).toBeNull();
      expect(() => removeSessionValue("k")).not.toThrow();
    } finally {
      Object.defineProperty(window, "sessionStorage", { value: original, configurable: true });
    }
  });
});
