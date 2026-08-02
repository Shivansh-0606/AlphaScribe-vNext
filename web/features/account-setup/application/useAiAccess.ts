import { useMutation } from "@tanstack/react-query";
import type { AiAccessStatus } from "@/lib/types/authorization";
import { useAiAccessStore } from "@/lib/state/aiAccess";
import { validateLlmKey } from "../integration/llm-api";
import type { ValidateLlmKeyRequestBody } from "../integration/llm-schemas";

/**
 * Derives the frozen `AiAccessStatus` (03.7 AD-5 — reflected, not
 * authoritative) from the local BYOK config. Managed AI is the frictionless
 * default (Component Inventory `AIAccessSelector` usage rule): valid the
 * instant it's selected, no round-trip, since the server already carries its
 * own default key. BYOK is valid only once `validated` — the exact fields
 * that last passed a live `/api/llm/validate` call.
 */
export function useAiAccessStatus(): AiAccessStatus {
  const { mode, apiKey, validated } = useAiAccessStore();
  if (mode === "managed") return { state: "valid", mode: "managed" };
  if (!apiKey) return { state: "not_configured" };
  if (validated) return { state: "valid", mode: "byok" };
  return { state: "not_configured" };
}

export function useValidateLlmKey() {
  const markValidated = useAiAccessStore((s) => s.markValidated);
  return useMutation({
    mutationFn: (body: ValidateLlmKeyRequestBody) => validateLlmKey(body),
    onSuccess: (data) => {
      if (data.valid) markValidated();
    },
  });
}
