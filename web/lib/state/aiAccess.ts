import { create } from "zustand";
import { persist } from "zustand/middleware";

/**
 * BYOK AI-access config (03.6 AD-3 credential boundary: browser-local only,
 * never sent anywhere except the single request that uses it — same
 * accepted model as the legacy app's `localStorage`-only key). Genuinely
 * global/cross-cutting (Settings, Setup, and eventually Company Research's
 * request payload all read this), so it lives here rather than inside a
 * single feature (03.1 — lib/state is for exactly this).
 *
 * `validated` is true only for the exact provider/apiKey/baseUrl/model
 * combination that last passed a live `/api/llm/validate` call — changing
 * any of those fields resets it, so a stale "valid" badge can never survive
 * an edited key.
 */
export interface AiAccessConfig {
  mode: "managed" | "byok";
  provider: string;
  apiKey: string;
  baseUrl: string;
  model: string;
  validated: boolean;
}

interface AiAccessState extends AiAccessConfig {
  setManaged: () => void;
  setByokFields: (
    fields: Partial<Pick<AiAccessConfig, "provider" | "apiKey" | "baseUrl" | "model">>,
  ) => void;
  markValidated: () => void;
  clear: () => void;
}

const DEFAULTS: AiAccessConfig = {
  mode: "managed",
  provider: "gemini",
  apiKey: "",
  baseUrl: "",
  model: "",
  validated: false,
};

export const useAiAccessStore = create<AiAccessState>()(
  persist(
    (set) => ({
      ...DEFAULTS,
      setManaged: () => set({ mode: "managed" }),
      setByokFields: (fields) => set({ mode: "byok", ...fields, validated: false }),
      markValidated: () => set({ validated: true }),
      clear: () => set({ ...DEFAULTS }),
    }),
    { name: "alphascribe:ai-access" },
  ),
);
