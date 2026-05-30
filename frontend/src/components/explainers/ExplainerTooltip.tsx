import { HelpCircle } from "lucide-react";

export function ExplainerTooltip({ label, body }: { label: string; body: string }) {
  return (
    <span className="group relative inline-flex">
      <button
        type="button"
        aria-label={`Explain ${label}`}
        className="text-muted hover:text-accent"
      >
        <HelpCircle size={15} />
      </button>
      <span className="pointer-events-none absolute bottom-full left-0 z-20 mb-2 w-64 rounded-md border border-line bg-panel p-3 text-left text-xs leading-relaxed text-text opacity-0 shadow-xl transition group-hover:opacity-100">
        <strong className="block text-sm">{label}</strong>
        {body}
      </span>
    </span>
  );
}
