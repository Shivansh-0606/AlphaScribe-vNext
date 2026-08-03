"use client";

import { useState } from "react";
import { Button } from "@/components/foundation/Button";
import { Chip } from "@/components/foundation/Chip";
import { FormField } from "@/components/foundation/FormField";
import { Text } from "@/components/foundation/Text";
import { Textarea } from "@/components/foundation/Textarea";

/** A few grounded starting points for the Empty state ("No concept chosen → prompt with a starting point", `06_UX_Specifications.md`). Generic financial-literacy concepts, not fabricated per-company suggestions (no backend call exists to generate real ones). */
const STARTER_CONCEPTS = [
  "What is operating margin?",
  "What does YoY mean?",
  "What is free cash flow?",
];

/**
 * "Ask for a concept explanation" (05_Screen_Inventory.md Available
 * Actions) — the Prompt Composer, scoped to Learning: no filing-ingest UI
 * (that's Company Research's concern), just the concept question. Loading/
 * error/response states live in the caller (`LearningScreen`), matching
 * `CopilotPanel`'s structure — this component is the form only.
 */
export function ConceptComposer({
  ticker,
  isRunning,
  isStarting,
  onAsk,
}: {
  ticker: string;
  isRunning: boolean;
  isStarting: boolean;
  onAsk: (concept: string) => void;
}) {
  const [concept, setConcept] = useState("");

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!concept.trim() || isRunning) return;
    onAsk(concept);
  };

  return (
    <div className="flex flex-col gap-4">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <Chip className="self-start">About {ticker}</Chip>
        <FormField label="What concept do you want explained?" required>
          <Textarea
            value={concept}
            onChange={(event) => setConcept(event.target.value)}
            placeholder="e.g. What is operating margin?"
            maxLength={500}
            showCounter
            disabled={isRunning}
          />
        </FormField>
        <Button
          type="submit"
          loading={isStarting}
          disabled={!concept.trim() || isRunning}
          className="self-start"
        >
          Ask
        </Button>
      </form>

      {!isRunning && (
        <div className="flex flex-col gap-2">
          <Text variant="caption" className="text-muted-foreground">
            Or start with:
          </Text>
          <div className="flex flex-wrap gap-2">
            {STARTER_CONCEPTS.map((starter) => (
              <Chip key={starter} variant="choice" onClick={() => onAsk(starter)}>
                {starter}
              </Chip>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
