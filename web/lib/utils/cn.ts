import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/** Merge conditional class names, resolving Tailwind class conflicts. The
 * standard className helper shadcn/ui components expect at this path. */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
