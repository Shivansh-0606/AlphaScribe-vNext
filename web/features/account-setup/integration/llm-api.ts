import { apiFetch } from "@/lib/api/fetch-client";
import {
  validateLlmKeyRequestSchema,
  validateLlmKeyResponseSchema,
  type ValidateLlmKeyRequestBody,
} from "./llm-schemas";

export function validateLlmKey(body: ValidateLlmKeyRequestBody) {
  return apiFetch("/api/llm/validate", validateLlmKeyResponseSchema, {
    method: "POST",
    body: validateLlmKeyRequestSchema.parse(body),
  });
}
