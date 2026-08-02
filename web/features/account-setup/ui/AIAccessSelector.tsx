"use client";

import { useState } from "react";
import { Banner } from "@/components/foundation/Banner";
import { Button } from "@/components/foundation/Button";
import { FormField } from "@/components/foundation/FormField";
import { Input } from "@/components/foundation/Input";
import { RadioGroup, RadioGroupItem } from "@/components/foundation/RadioGroup";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/foundation/Select";
import { Text } from "@/components/foundation/Text";
import { useAiAccessStore } from "@/lib/state/aiAccess";
import { useAiAccessStatus, useValidateLlmKey } from "../application/useAiAccess";
import { useIdentity } from "../application/useAuth";

const BYOK_PROVIDERS = [
  { id: "gemini", label: "Google Gemini" },
  { id: "groq", label: "Groq (Llama)" },
  { id: "anthropic", label: "Anthropic Claude" },
  { id: "openai", label: "OpenAI (GPT-4o)" },
  { id: "openrouter", label: "OpenRouter" },
  { id: "deepseek", label: "DeepSeek" },
  { id: "mistral", label: "Mistral" },
  // Bring-your-own OpenAI-compatible endpoint — admin-only, mirrors the
  // backend's /reports/generate + /llm/validate restriction exactly.
  { id: "custom", label: "Custom (OpenAI-compatible)", adminOnly: true },
];

/**
 * AIAccessSelector (Component Inventory) — "Variants: Onboarding, Settings".
 * One component, not two: both screens choose+validate the same access, the
 * only difference is the primary action (Continue-and-advance vs. Save-in-place).
 */
export function AIAccessSelector({
  variant,
  onContinue,
}: {
  variant: "onboarding" | "settings";
  onContinue?: () => void;
}) {
  const identity = useIdentity();
  const store = useAiAccessStore();
  const validate = useValidateLlmKey();
  const status = useAiAccessStatus();

  const [provider, setProvider] = useState(store.provider);
  const [apiKey, setApiKey] = useState(store.apiKey);
  const [baseUrl, setBaseUrl] = useState(store.baseUrl);
  const [model, setModel] = useState(store.model);

  const isCustom = provider === "custom";
  const visibleProviders = BYOK_PROVIDERS.filter((p) => !p.adminOnly || identity.data?.is_admin);

  // Every field syncs into the store on every change (not just on Validate) —
  // setByokFields always resets `validated`, so editing anything after a
  // validated (or rejected) key immediately drops the stale valid/invalid
  // state instead of letting it survive an edit (aiAccess.ts's own contract).
  // Also clears the mutation's own success/error data so its Banner doesn't
  // linger describing a key that's no longer what's in the field.
  const updateField = (
    patch: Partial<{ provider: string; apiKey: string; baseUrl: string; model: string }>,
  ) => {
    if (patch.provider !== undefined) setProvider(patch.provider);
    if (patch.apiKey !== undefined) setApiKey(patch.apiKey);
    if (patch.baseUrl !== undefined) setBaseUrl(patch.baseUrl);
    if (patch.model !== undefined) setModel(patch.model);
    store.setByokFields({ provider, apiKey, baseUrl, model, ...patch });
    validate.reset();
  };

  const onValidate = () => {
    validate.mutate({
      provider,
      api_key: apiKey,
      base_url: isCustom ? baseUrl : undefined,
      model: isCustom ? model : undefined,
    });
  };

  const onClear = () => {
    store.clear();
    setApiKey("");
    setBaseUrl("");
    setModel("");
  };

  const canContinue = status.state === "valid";

  return (
    <div className="flex flex-col gap-4">
      <RadioGroup
        label="Choose AI access"
        value={store.mode}
        onValueChange={(value) => {
          if (value === "managed") store.setManaged();
          else store.setByokFields({ provider, apiKey, baseUrl, model });
          validate.reset();
        }}
      >
        <RadioGroupItem value="managed" label="Managed AI — zero setup" />
        <RadioGroupItem value="byok" label="Bring your own key (BYOK)" />
      </RadioGroup>

      {store.mode === "byok" && (
        <div className="border-border flex flex-col gap-4 border-l pl-4">
          {validate.isError && (
            <Banner tone="error">
              {validate.error instanceof Error
                ? validate.error.message
                : "Could not validate the key."}
            </Banner>
          )}
          {validate.data && !validate.data.valid && (
            <Banner tone="error">{validate.data.error ?? "That key didn't validate."}</Banner>
          )}
          {status.state === "valid" && status.mode === "byok" && (
            <Banner tone="success">Key validated.</Banner>
          )}

          <FormField label="Provider">
            <Select value={provider} onValueChange={(value) => updateField({ provider: value })}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {visibleProviders.map((p) => (
                  <SelectItem key={p.id} value={p.id}>
                    {p.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </FormField>

          {isCustom && (
            <>
              {/* Only mandatory once Custom is selected — same required affordance as API key below. */}
              <FormField
                label="Base URL"
                required
                helpText="An OpenAI-compatible endpoint, e.g. https://aipipe.org/openai/v1"
              >
                <Input
                  value={baseUrl}
                  onChange={(e) => updateField({ baseUrl: e.target.value })}
                  placeholder="https://aipipe.org/openai/v1"
                  disabled={validate.isPending}
                />
              </FormField>
              <FormField label="Model" required>
                <Input
                  value={model}
                  onChange={(e) => updateField({ model: e.target.value })}
                  placeholder="gpt-4o-mini"
                  disabled={validate.isPending}
                />
              </FormField>
            </>
          )}

          <FormField label="API key" required>
            <Input
              type="password"
              value={apiKey}
              onChange={(e) => updateField({ apiKey: e.target.value })}
              placeholder="Paste your key"
              disabled={validate.isPending}
            />
          </FormField>

          <div className="flex gap-2">
            <Button
              variant="secondary"
              onClick={onValidate}
              loading={validate.isPending}
              disabled={!apiKey.trim() || (isCustom && (!baseUrl.trim() || !model.trim()))}
              className="w-fit"
            >
              Validate key
            </Button>
            {store.apiKey && (
              <Button variant="quiet" onClick={onClear} className="w-fit">
                Clear
              </Button>
            )}
          </div>
        </div>
      )}

      {variant === "onboarding" && (
        <Button onClick={onContinue} disabled={!canContinue} className="w-fit">
          Continue
        </Button>
      )}

      {variant === "settings" && store.mode === "managed" && (
        <Text variant="small" className="text-muted-foreground">
          Using the managed default — no key needed.
        </Text>
      )}
    </div>
  );
}
