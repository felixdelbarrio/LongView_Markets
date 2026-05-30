import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function MyPortfolio() {
  return (
    <FeaturePage
      config={{
        title: "My portfolio",
        eyebrow: "Cartera real demo",
        description:
          "Posiciones, rentabilidad realizada y no realizada, dividendos, asignacion, riesgo agregado y alertas.",
        dataKind: "observed",
        queryKey: "portfolio",
        queryFn: () => api.portfolio(),
        highlights: ["Anadir compra", "Importar CSV", "Asignacion", "Benchmark"],
      }}
    />
  );
}
