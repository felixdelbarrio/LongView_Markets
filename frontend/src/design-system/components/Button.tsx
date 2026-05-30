import type { ButtonHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

export function Button(props: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      className={cn(
        "inline-flex min-h-10 items-center justify-center gap-2 rounded-md bg-accent px-3 py-2 text-sm font-bold text-white transition hover:opacity-90 disabled:opacity-50",
        props.className,
      )}
    />
  );
}
