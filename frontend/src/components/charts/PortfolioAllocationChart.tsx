import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const colors = [
  "rgb(var(--color-accent))",
  "rgb(var(--color-teal))",
  "rgb(var(--color-amber))",
  "rgb(var(--color-muted))",
  "rgb(var(--color-danger))",
];

export function PortfolioAllocationChart({
  positions,
}: {
  positions: Array<Record<string, string | number>>;
}) {
  return (
    <div className="h-72">
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={positions}
            dataKey="weight"
            nameKey="ticker"
            innerRadius={58}
            outerRadius={92}
            paddingAngle={3}
          >
            {positions.map((position, index) => (
              <Cell key={String(position.ticker)} fill={colors[index % colors.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
