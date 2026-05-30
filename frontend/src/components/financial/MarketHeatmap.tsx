export function MarketHeatmap({ rows }: { rows: Array<Record<string, string | number>> }) {
  return (
    <div className="grid grid-cols-2 gap-2 md:grid-cols-4">
      {rows.slice(0, 12).map((row, index) => {
        const value = Number(row.cagr ?? row.change ?? index);
        const positive = value >= 0;
        return (
          <div
            key={`${String(row.ticker ?? row.market)}-${index}`}
            className={`min-h-20 rounded-md border p-3 ${positive ? "border-teal/40 bg-teal/10" : "border-red-400/40 bg-red-500/10"}`}
          >
            <p className="text-sm font-bold">{String(row.ticker ?? row.market)}</p>
            <p className="text-xs text-muted">{String(row.name ?? row.sector ?? "Market")}</p>
            <p className={positive ? "text-teal" : "text-red-300"}>{value.toFixed(2)}%</p>
          </div>
        );
      })}
    </div>
  );
}
