import { Badge } from "./Badge";

export function RiskBadge({ value }: { value: string }) {
  return <Badge tone={value.includes("high") ? "danger" : "info"}>{value}</Badge>;
}
