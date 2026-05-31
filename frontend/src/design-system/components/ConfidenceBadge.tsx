import { Badge } from "./Badge";

export function ConfidenceBadge({ value }: { value: number }) {
  return (
    <Badge tone={value >= 0.7 ? "success" : "warning"}>{Math.round(value * 100)}% confianza</Badge>
  );
}
