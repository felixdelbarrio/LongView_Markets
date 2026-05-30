import type { ReactNode } from "react";
import { cn } from "../../lib/utils";

export function Card({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <section className={cn("rounded-lg border border-line bg-panel p-5 shadow-glow", className)}>
      {children}
    </section>
  );
}
