import { PublicTemplate } from "@/components/layouts/PublicTemplate";

export default function PublicLayout({ children }: { children: React.ReactNode }) {
  return <PublicTemplate>{children}</PublicTemplate>;
}
