import { ArrowUpRight, Info } from "lucide-react";
import { Card } from "../ui/card";
import { ExplainerTooltip } from "../explainers/ExplainerTooltip";

export function MetricCard({
  label,
  value,
  detail,
  tone = "accent",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "accent" | "teal" | "amber";
}) {
  return (
    <Card className="min-h-[132px]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted">{label}</p>
          <p className="mt-3 text-3xl font-bold text-text">{value}</p>
        </div>
        <div className={`rounded-md bg-${tone}/10 p-2 text-${tone}`}>
          <ArrowUpRight size={18} />
        </div>
      </div>
      <div className="mt-4 flex items-center gap-2 text-sm text-muted">
        <ExplainerTooltip label={label} body={detail} />
        <Info size={14} /> {detail}
      </div>
    </Card>
  );
}
