import type { Metadata } from "next";
import { ComingSoon } from "@/components/layouts/ComingSoon";

export const metadata: Metadata = { title: "Research Library" };

export default function LibraryPage() {
  return (
    <ComingSoon
      title="Research Library"
      note="Research Library is not built yet — saved sessions, reports, and history land in a later phase."
    />
  );
}
