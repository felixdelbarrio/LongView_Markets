import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function ExecutiveDemo() {
  return (
    <FeaturePage
      config={{
        title: "Executive demo",
        eyebrow: "Narrativa en 2 minutos",
        description:
          "Estado global, evento, impacto cartera, riesgo, dividendo, simulacion, forecast y decision documentada.",
        dataKind: "mock",
        queryKey: "dashboard-demo",
        queryFn: () => api.dashboard(),
        highlights: ["Evento detectado", "Impacto", "Forecast prudente", "Journal"],
      }}
    />
  );
}
