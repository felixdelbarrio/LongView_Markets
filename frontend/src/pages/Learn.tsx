import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function Learn() {
  return (
    <FeaturePage
      config={{
        title: "Learn",
        eyebrow: "Glosario visual",
        description:
          "Explica CAGR, drawdown, volatilidad, Sharpe, dividend yield, benchmark, forecasts, fiscalidad y calidad.",
        dataKind: "mock",
        queryKey: "playbooks",
        queryFn: () => api.playbooks(),
        highlights: ["CAGR", "Sharpe", "Ex-dividend", "Data quality"],
      }}
    />
  );
}
