import type { Metadata } from "next";
import { ComingSoon } from "@/components/layouts/ComingSoon";

export const metadata: Metadata = { title: "Learning" };

export default function LearningPage() {
  return (
    <ComingSoon
      title="Learning"
      note="Learning is not built yet — learner-level concept explanations land in a later phase."
    />
  );
}
