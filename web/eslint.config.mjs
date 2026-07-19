import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { FlatCompat } from "@eslint/eslintrc";

/**
 * ESLint (flat config) — AlphaScribe vNext.
 *
 * `eslint-config-next` (v15) ships legacy eslintrc-style configs, so we bridge
 * them into flat config via FlatCompat. `next/core-web-vitals` and
 * `next/typescript` bundle the React, React-Hooks, jsx-a11y (accessibility
 * linting is a merge gate — 04.5 AD-5), and TypeScript rule sets. Formatting is
 * owned by Prettier, not ESLint.
 */
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const compat = new FlatCompat({ baseDirectory: __dirname });

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    rules: {
      // Type safety at boundaries (§4.9 / 05.8 AD-4): no implicit escape hatches.
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/consistent-type-imports": [
        "warn",
        { prefer: "type-imports", fixStyle: "inline-type-imports" },
      ],
    },
  },
  {
    ignores: [
      ".next/**",
      "out/**",
      "build/**",
      "coverage/**",
      "playwright-report/**",
      "test-results/**",
      "next-env.d.ts",
    ],
  },
];

export default eslintConfig;
