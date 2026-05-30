import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function DividendFisher() {
  return (
    <FeaturePage
      config={{
        title: "Dividend fisher",
        eyebrow: "Captura explicable",
        description:
          "Calendario, fechas ex-dividend, fiscalidad, regularidad, simulacion y riesgos visibles.",
        dataKind: "mock",
        queryKey: "dividends",
        queryFn: () => api.dividends(),
        highlights: ["Calendario", "Yield neto", "Riesgo recorte", "Simulacion"],
      }}
    />
  );
}
