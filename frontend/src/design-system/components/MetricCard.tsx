import { Card } from "./Card";

export function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail?: string;
}) {
  return (
    <Card>
      <p className="text-xs font-bold uppercase tracking-normal text-muted">{label}</p>
      <p className="mt-2 text-3xl font-black">{value}</p>
      {detail ? <p className="mt-2 text-sm leading-6 text-muted">{detail}</p> : null}
    </Card>
  );
}
