import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function Forecasting() {
  return (
    <FeaturePage
      config={{
        title: "Forecasting",
        eyebrow: "Escenarios, no certezas",
        description:
          "Baseline naive, medias moviles, regresion simple, drawdown, regimen e intervalos de confianza.",
        dataKind: "forecast",
        queryKey: "forecasting",
        queryFn: () => api.forecasting("MSFT"),
        highlights: ["Optimista", "Central", "Adverso", "Backtesting"],
      }}
    />
  );
}
