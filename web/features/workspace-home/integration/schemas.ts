import { z } from "zod";

/**
 * Response shapes for the `workspace-home` feature's backend contract
 * (backend/server.py `GET /companies/search`, `GET /reports`). Both are
 * real, already-implemented, authenticated endpoints — validated at the
 * trust boundary the same way `account-setup` validates auth responses
 * (03.3 AD-3): nothing beyond this module assumes the shape without parsing it.
 */

export const companyResultSchema = z.object({
  ticker: z.string(),
  name: z.string(),
  has_filings: z.boolean().optional(),
});
export type CompanyResult = z.infer<typeof companyResultSchema>;

export const companySearchResponseSchema = z.object({
  results: z.array(companyResultSchema),
});

export const reportSchema = z.object({
  id: z.string(),
  ticker: z.string(),
  query: z.string(),
  created_at: z.string(),
  is_sample: z.boolean().optional(),
});
export type Report = z.infer<typeof reportSchema>;

export const reportsResponseSchema = z.object({
  reports: z.array(reportSchema),
});
