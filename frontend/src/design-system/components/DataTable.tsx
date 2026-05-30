export function DataTable({ rows }: { rows: Array<Record<string, unknown>> }) {
  const columns = Array.from(new Set(rows.flatMap((row) => Object.keys(row)))).slice(0, 10);
  if (!rows.length) {
    return (
      <p className="rounded-md border border-line bg-canvas p-4 text-sm text-muted">Sin datos.</p>
    );
  }
  return (
    <div className="overflow-x-auto rounded-lg border border-line">
      <table className="min-w-full border-collapse text-sm">
        <thead className="bg-canvas text-left text-xs uppercase tracking-normal text-muted">
          <tr>
            {columns.map((column) => (
              <th key={column} className="px-3 py-2">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr key={String(row.id ?? index)} className="border-t border-line">
              {columns.map((column) => (
                <td key={column} className="max-w-[240px] px-3 py-2">
                  {String(row[column] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
