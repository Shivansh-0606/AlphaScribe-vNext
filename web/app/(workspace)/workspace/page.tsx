import type { Metadata } from "next";
import { Heading } from "@/components/foundation/Heading";
import { CompanySearch, RecentResearch } from "@/features/workspace-home";

export const metadata: Metadata = { title: "Workspace Home" };

/** SCR-04 Workspace Home: search entry (primary) -> recent research -> global navigation. */
export default function WorkspaceHomePage() {
  return (
    <div className="flex max-w-2xl flex-col gap-8">
      <Heading level="h1">Workspace Home</Heading>
      <CompanySearch />
      <RecentResearch />
    </div>
  );
}
