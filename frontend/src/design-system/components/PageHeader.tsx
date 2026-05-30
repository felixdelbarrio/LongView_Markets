import type { ReactNode } from "react";
import { SourceBadge } from "./SourceBadge";

export function PageHeader({
  eyebrow,
  title,
  description,
  source = "backend",
  children,
}: {
  eyebrow: string;
  title: string;
  description: string;
  source?: string;
  children?: ReactNode;
}) {
  return (
    <section className="rounded-lg border border-line bg-panel p-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-bold uppercase tracking-normal text-accent">{eyebrow}</p>
          <h1 className="mt-3 text-4xl font-black tracking-normal">{title}</h1>
          <p className="mt-3 max-w-4xl text-base leading-7 text-muted">{description}</p>
        </div>
        <SourceBadge source={source} />
      </div>
      {children ? <div className="mt-5">{children}</div> : null}
    </section>
  );
}
