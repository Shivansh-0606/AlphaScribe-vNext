import type { Metadata } from "next";
import { LibraryScreen } from "@/features/research-library";

export const metadata: Metadata = { title: "Research Library" };

export default function LibraryPage() {
  return <LibraryScreen />;
}
