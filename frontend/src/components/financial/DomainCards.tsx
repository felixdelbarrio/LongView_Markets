import {
  CalendarDays,
  FileText,
  FlaskConical,
  Gauge,
  Landmark,
  ListChecks,
  NotebookPen,
  Radar,
  Rocket,
  ShieldAlert,
} from "lucide-react";
import { Card } from "../ui/card";
import { SourceBadge } from "./Badges";

const iconMap = [
  CalendarDays,
  FileText,
  FlaskConical,
  Gauge,
  Landmark,
  ListChecks,
  NotebookPen,
  Radar,
  Rocket,
  ShieldAlert,
];

export function DomainCards({
  title,
  items,
}: {
  title: string;
  items: Array<Record<string, unknown>>;
}) {
  return (
    <Card>
      <div className="mb-4 flex items-center justify-between gap-3">
        <h2 className="text-xl font-bold">{title}</h2>
        <SourceBadge kind="mock" />
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {items.slice(0, 9).map((item, index) => {
          const Icon = iconMap[index % iconMap.length];
          const titleText = String(
            item.title ?? item.name ?? item.ticker ?? item.headline ?? `Item ${index + 1}`,
          );
          const detail = String(
            item.description ??
              item.summary ??
              item.thesis ??
              item.explanation ??
              item.sector ??
              "Evidence-backed demo data with source, date and confidence.",
          );
          return (
            <article
              key={`${titleText}-${index}`}
              className="rounded-md border border-line/80 bg-canvas/50 p-4"
            >
              <Icon className="mb-3 text-accent" size={20} />
              <h3 className="font-semibold">{titleText}</h3>
              <p className="mt-2 text-sm leading-6 text-muted">{detail}</p>
            </article>
          );
        })}
      </div>
    </Card>
  );
}
