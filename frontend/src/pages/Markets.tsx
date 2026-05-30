import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function Markets() {
  return (
    <FeaturePage
      config={{
        title: "Markets",
        eyebrow: "Pulse global",
        description:
          "Indices, lideres, rezagados, heatmap sectorial, volatilidad agregada y noticias destacadas.",
        dataKind: "mock",
        queryKey: "markets",
        queryFn: () => api.markets(),
        highlights: [
          "Indices principales",
          "Mejores y peores valores",
          "Heatmap por sector",
          "Noticias destacadas",
        ],
      }}
    />
  );
}
