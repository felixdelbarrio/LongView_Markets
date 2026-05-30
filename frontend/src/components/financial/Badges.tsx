import { ShieldCheck, Signal, Sparkles } from "lucide-react";

const toneMap: Record<string, string> = {
  high: "border-red-400/50 bg-red-500/10 text-red-300",
  critical: "border-red-500 bg-red-500/15 text-red-200",
  medium: "border-amber/60 bg-amber/10 text-amber",
  low: "border-teal/60 bg-teal/10 text-teal",
  mock: "border-accent/50 bg-accent/10 text-accent",
  forecast: "border-amber/60 bg-amber/10 text-amber",
  simulation: "border-teal/60 bg-teal/10 text-teal",
};

export function RiskBadge({ value }: { value: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-1 text-xs font-semibold ${toneMap[value] ?? toneMap.medium}`}
    >
      <Signal size={13} />
      {value}
    </span>
  );
}

export function ConfidenceBadge({ value }: { value: number }) {
  const label = `${Math.round(value * 100)}%`;
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-teal/50 bg-teal/10 px-2 py-1 text-xs font-semibold text-teal">
      <ShieldCheck size={13} />
      {label}
    </span>
  );
}

export function SourceBadge({ kind = "mock" }: { kind?: string }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full border px-2 py-1 text-xs font-semibold ${toneMap[kind] ?? toneMap.mock}`}
    >
      <Sparkles size={13} />
      {kind}
    </span>
  );
}
