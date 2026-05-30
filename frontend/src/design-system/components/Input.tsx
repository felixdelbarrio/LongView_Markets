import type { InputHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={cn(
        "min-h-10 rounded-md border border-line bg-canvas px-3 outline-none focus:border-accent",
        props.className,
      )}
    />
  );
}
