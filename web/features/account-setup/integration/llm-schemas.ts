import { z } from "zod";

/** Request/response shapes for `POST /api/llm/validate` (backend/server.py). */

export const validateLlmKeyRequestSchema = z.object({
  provider: z.string(),
  api_key: z.string().min(1),
  base_url: z.string().optional(),
  model: z.string().optional(),
});
export type ValidateLlmKeyRequestBody = z.infer<typeof validateLlmKeyRequestSchema>;

export const validateLlmKeyResponseSchema = z.object({
  valid: z.boolean(),
  error: z.string().optional(),
});
export type ValidateLlmKeyResponse = z.infer<typeof validateLlmKeyResponseSchema>;
