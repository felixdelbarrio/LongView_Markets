import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function Playbooks() {
  return (
    <FeaturePage
      config={{
        title: "Playbooks",
        eyebrow: "Guias de decision",
        description:
          "Playbooks para largo plazo, dividendos, DCA, rebalanceo, concentracion, drawdown y forecasts.",
        dataKind: "mock",
        queryKey: "playbooks",
        queryFn: () => api.playbooks(),
        highlights: ["Largo plazo", "DCA", "Rebalanceo", "Drawdown"],
      }}
    />
  );
}
