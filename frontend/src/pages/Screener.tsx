import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function Screener() {
  return (
    <FeaturePage
      config={{
        title: "Screener",
        eyebrow: "Filtro largo plazo",
        description:
          "Filtra por pais, sector, divisa, dividend yield, volatilidad, drawdown, CAGR, momentum y confianza.",
        dataKind: "mock",
        queryKey: "screener",
        queryFn: () => api.screener(),
        highlights: ["Presets", "Metricas", "Senales", "Watchlist"],
      }}
    />
  );
}
