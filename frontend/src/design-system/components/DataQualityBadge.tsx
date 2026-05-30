import { Badge } from "./Badge";

export function DataQualityBadge({ flags }: { flags?: string[] }) {
  return (
    <Badge tone={flags?.length ? "warning" : "success"}>
      {flags?.length ? flags.join(", ") : "datos ok"}
    </Badge>
  );
}
