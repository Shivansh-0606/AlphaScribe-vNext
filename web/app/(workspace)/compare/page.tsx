import type { Metadata } from "next";
import { ComingSoon } from "@/components/layouts/ComingSoon";

export const metadata: Metadata = { title: "Compare" };

export default function ComparePage() {
  return (
    <ComingSoon
      title="Compare"
      note="Comparison is not built yet — side-by-side company comparison lands in a later phase."
    />
  );
}
