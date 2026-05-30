import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

const colors = ["#2C71E8", "#14A491", "#D38E29", "#7C89B5", "#B54A6A"];

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
