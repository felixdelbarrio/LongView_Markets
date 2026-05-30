import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function Insights() {
  return (
    <FeaturePage
      config={{
        title: "Insights",
        eyebrow: "Explicabilidad",
        description:
          "Insights prudentes con criterio aplicado, evidencia, fecha, fuente, confianza y limitaciones.",
        dataKind: "mock",
        queryKey: "alerts",
        queryFn: () => api.alerts(),
        highlights: [
          "Cerca de maximos",
          "Drawdown relevante",
          "Volumen anomal",
          "Riesgo concentracion",
        ],
      }}
    />
  );
}
