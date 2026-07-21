"use client";

import { Eye, EyeSlash } from "@phosphor-icons/react/dist/ssr";
import { cva, type VariantProps } from "class-variance-authority";
import { useState, type ComponentProps, type ReactNode } from "react";
import { Input as InputPrimitive } from "@/components/ui/input";
import { cn } from "@/lib/utils";

/**
 * Input (Family 02) — docs/experience_design/Components/02_Text_Inputs.md.
 * Typically used inside `FormField`, which supplies id/aria-describedby/
 * aria-invalid automatically.
 */
const inputVariants = cva(
  "bg-input-bg placeholder:text-muted-foreground w-full rounded-md border border-input px-3 text-foreground outline-none transition-[border-color,box-shadow] duration-[var(--motion-duration-fast)] ease-standard focus-visible:border-ring aria-invalid:border-destructive disabled:pointer-events-none disabled:opacity-disabled",
  {
    variants: {
      size: {
        sm: "h-8 text-sm",
        md: "h-9 text-sm",
        lg: "h-11 text-base",
      },
    },
    defaultVariants: {
      size: "md",
    },
  },
);

export interface InputProps
  extends Omit<ComponentProps<"input">, "size" | "type">, VariantProps<typeof inputVariants> {
  /** "password" gets a mandatory reveal toggle; the value is never announced by assistive tech. */
  type?: "text" | "email" | "password" | "tel" | "url" | "number";
  leadingIcon?: ReactNode;
  trailingAddon?: ReactNode;
}

export function Input({
  type = "text",
  size = "md",
  leadingIcon,
  trailingAddon,
  className,
  ...props
}: InputProps) {
  const [revealed, setRevealed] = useState(false);
  const isPassword = type === "password";
  const resolvedType = isPassword ? (revealed ? "text" : "password") : type;

  if (!leadingIcon && !isPassword && !trailingAddon) {
    return (
      <InputPrimitive
        type={resolvedType}
        className={cn(inputVariants({ size }), className)}
        {...props}
      />
    );
  }

  return (
    <div className="relative flex items-center">
      {leadingIcon && (
        <span aria-hidden="true" className="text-muted-foreground absolute left-3 flex size-4">
          {leadingIcon}
        </span>
      )}
      <InputPrimitive
        type={resolvedType}
        className={cn(
          inputVariants({ size }),
          leadingIcon && "pl-9",
          (isPassword || trailingAddon) && "pr-9",
          className,
        )}
        {...props}
      />
      {isPassword && (
        <button
          type="button"
          aria-label={revealed ? "Hide password" : "Show password"}
          aria-pressed={revealed}
          onClick={() => setRevealed((v) => !v)}
          className="text-muted-foreground hover:text-foreground absolute right-3 flex size-4 items-center justify-center"
        >
          {revealed ? <EyeSlash aria-hidden="true" /> : <Eye aria-hidden="true" />}
        </button>
      )}
      {!isPassword && trailingAddon && (
        <span className="absolute right-3 flex items-center">{trailingAddon}</span>
      )}
    </div>
  );
}
