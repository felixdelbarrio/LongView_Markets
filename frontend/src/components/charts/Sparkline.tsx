import { Line, LineChart, ResponsiveContainer } from "recharts";

export function Sparkline({ data }: { data: Array<{ value: number }> }) {
  return (
    <div className="h-16 w-full">
      <ResponsiveContainer>
        <LineChart data={data}>
          <Line
            type="monotone"
            dataKey="value"
            stroke="rgb(var(--color-teal))"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
