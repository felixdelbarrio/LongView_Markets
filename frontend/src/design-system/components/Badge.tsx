import type { ReactNode } from "react";

export function Badge({
  children,
  tone = "info",
}: {
  children: ReactNode;
  tone?: "info" | "success" | "warning" | "danger";
}) {
  const toneClass = {
    info: "border-accent/40 bg-accent/10 text-accent",
    success: "border-teal/40 bg-teal/10 text-teal",
    warning: "border-amber/40 bg-amber/10 text-amber",
    danger: "border-red-400/40 bg-red-400/10 text-red-300",
  }[tone];
  return (
    <span className={`inline-flex rounded-md border px-2 py-1 text-xs font-bold ${toneClass}`}>
      {children}
    </span>
  );
}
