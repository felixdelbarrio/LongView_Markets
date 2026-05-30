import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function Alerts() {
  return (
    <FeaturePage
      config={{
        title: "Alerts",
        eyebrow: "Acciones prudentes",
        description:
          "Alertas por precio, drawdown, dividendos, forecast, calidad de dato y cartera.",
        dataKind: "mock",
        queryKey: "alerts",
        queryFn: () => api.alerts(),
        highlights: ["Severidad", "Evidencia", "Estado", "Accion sugerida"],
      }}
    />
  );
}
