import { Badge } from "./Badge";

export function SourceBadge({ source }: { source: string }) {
  return <Badge tone={source === "mock" ? "warning" : "success"}>{source}</Badge>;
}
