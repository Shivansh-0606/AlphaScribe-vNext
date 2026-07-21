"use client";

import {
  BookmarkSimple,
  GearSix,
  GraduationCap,
  House,
  Scales,
} from "@phosphor-icons/react/dist/ssr";
import type { Route } from "next";
import NextLink from "next/link";
import { usePathname } from "next/navigation";
import type { ReactElement } from "react";
import { cn } from "@/lib/utils";

/**
 * Global navigation (04_Navigation_Structure "Global Navigation" — persistent,
 * flat, six destinations). Research/Compare/Learning/Research Library route
 * to scaffolded placeholders until their own feature/template lands (only
 * Workspace Home + Settings are real in this phase) — the destinations stay
 * reachable per the frozen structure rather than being hidden.
 */
// Every href below is a known, hardcoded internal route (not user input) —
// cast once here rather than at each Link usage.
const DESTINATIONS: { href: Route; label: string; icon: ReactElement }[] = [
  { href: "/workspace", label: "Workspace Home", icon: <House aria-hidden="true" /> },
  {
    href: "/research",
    label: "Research",
    icon: <Scales aria-hidden="true" className="rotate-90" />,
  },
  { href: "/compare", label: "Compare", icon: <Scales aria-hidden="true" /> },
  { href: "/learning", label: "Learning", icon: <GraduationCap aria-hidden="true" /> },
  { href: "/library", label: "Research Library", icon: <BookmarkSimple aria-hidden="true" /> },
  { href: "/settings", label: "Settings", icon: <GearSix aria-hidden="true" /> },
];

export function GlobalNav() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Global"
      className="border-border flex flex-col gap-1 border-r px-2 py-4 sm:w-56"
    >
      {DESTINATIONS.map((d) => {
        const active = pathname === d.href || pathname.startsWith(`${d.href}/`);
        return (
          <NextLink
            key={d.href}
            href={d.href}
            aria-current={active ? "page" : undefined}
            className={cn(
              "text-foreground flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              active ? "bg-surface-hover" : "hover:bg-surface-hover",
            )}
          >
            <span className="size-4 shrink-0">{d.icon}</span>
            {d.label}
          </NextLink>
        );
      })}
    </nav>
  );
}
