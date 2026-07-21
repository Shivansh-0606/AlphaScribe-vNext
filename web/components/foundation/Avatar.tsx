"use client";

import type { ComponentProps } from "react";
import {
  Avatar as AvatarPrimitive,
  AvatarBadge,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar";
import { cn } from "@/lib/utils";

/**
 * Avatar (Family 05) — docs/experience_design/Components/05_Content_Data_Display.md.
 * The generated primitive already ships Image/Fallback/Badge/Group — this
 * wrapper only binds `name` as the mandatory accessible name (never
 * "avatar") and its initials source, and maps the frozen `sm`/`md`/`lg` size
 * vocabulary onto shadcn's `sm`/`default`/`lg`.
 */
function initialsFrom(name: string): string {
  const words = name.trim().split(/\s+/).filter(Boolean);
  if (words.length === 0) return "";
  if (words.length === 1) return words[0]!.slice(0, 2).toUpperCase();
  return (words[0]![0] + words[words.length - 1]![0]).toUpperCase();
}

const SIZE_TO_PRIMITIVE = { sm: "sm", md: "default", lg: "lg" } as const;

export interface AvatarProps extends Omit<
  ComponentProps<typeof AvatarPrimitive>,
  "size" | "children"
> {
  /** The user/entity's real name — the accessible name and the initials source. */
  name: string;
  src?: string;
  size?: "sm" | "md" | "lg";
  /** Status meaning as text (e.g. "Online") — never color alone; omit for no status dot. */
  statusLabel?: string;
}

export function Avatar({ name, src, size = "md", statusLabel, className, ...props }: AvatarProps) {
  return (
    <AvatarPrimitive
      data-slot="foundation-avatar"
      size={SIZE_TO_PRIMITIVE[size]}
      role="img"
      aria-label={name}
      className={cn(className)}
      {...props}
    >
      {src && <AvatarImage src={src} alt="" />}
      <AvatarFallback aria-hidden="true">{initialsFrom(name)}</AvatarFallback>
      {statusLabel && <AvatarBadge role="img" aria-label={statusLabel} />}
    </AvatarPrimitive>
  );
}
