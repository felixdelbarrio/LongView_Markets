import type { SelectHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      className={cn(
        "min-h-10 rounded-md border border-line bg-canvas px-3 outline-none focus:border-accent",
        props.className,
      )}
    />
  );
}
