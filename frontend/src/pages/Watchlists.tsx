import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function Watchlists() {
  return (
    <FeaturePage
      config={{
        title: "Watchlists",
        eyebrow: "Seguimiento inteligente",
        description:
          "Listas con motivo, precio de referencia, alerta rapida, evolucion, insights agregados y journal.",
        dataKind: "mock",
        queryKey: "watchlists",
        queryFn: () => api.watchlists(),
        highlights: ["Dividendos", "Tecnologia calidad", "Europa defensiva", "Drawdown"],
      }}
    />
  );
}
