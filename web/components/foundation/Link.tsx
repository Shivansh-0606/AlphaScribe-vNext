import NextLink from "next/link";
import type { ComponentProps } from "react";
import { cn } from "@/lib/utils";

/**
 * Link — the frozen link styling (02_Color_System.md: "Source references use
 * link/brand styling so evidence is always visibly reachable"): `--color-brand`
 * text, underline reinforces the link (never color alone, §17 no-color-only).
 *
 * Internal paths (starting with `/`) render Next's `Link` (client-side
 * navigation); anything else renders a plain `<a>` with `target="_blank"` +
 * `rel="noopener noreferrer"` and an accessible "(opens in new tab)" suffix.
 */
type InternalLinkProps = ComponentProps<typeof NextLink>;
type ExternalLinkProps = Omit<ComponentProps<"a">, "href"> & { href: string };

export type LinkProps = InternalLinkProps | ExternalLinkProps;

function isInternalHref(href: LinkProps["href"]): boolean {
  const path = typeof href === "string" ? href : (href?.pathname ?? "");
  return path.startsWith("/") || path.startsWith("#");
}

const linkClassName = "text-brand underline underline-offset-2 hover:opacity-80 rounded-sm";

export function Link({ href, className, children, ...props }: LinkProps) {
  if (isInternalHref(href)) {
    // Next's `typedRoutes` narrows `href` to known static routes; this
    // component accepts a dynamic prop, so the runtime check above (not the
    // type system) is what guarantees this is actually an internal path.
    return (
      <NextLink
        href={href as InternalLinkProps["href"]}
        className={cn(linkClassName, className)}
        {...props}
      >
        {children}
      </NextLink>
    );
  }

  return (
    <a
      href={href as string}
      target="_blank"
      rel="noopener noreferrer"
      className={cn(linkClassName, className)}
      {...(props as ComponentProps<"a">)}
    >
      {children} <span className="sr-only">(opens in new tab)</span>
    </a>
  );
}
