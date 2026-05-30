import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function InstrumentDetail() {
  return (
    <FeaturePage
      config={{
        title: "Instrument detail",
        eyebrow: "Ficha completa",
        description:
          "Cabecera, precio, historico, metricas, insights, senales, noticias, dividendos, forecast y acciones de disciplina.",
        dataKind: "mock",
        queryKey: "instrument",
        queryFn: () => api.instrument("MSFT"),
        highlights: ["Grafico historico", "Metricas clave", "Copiar contexto GPT", "Crear tesis"],
      }}
    />
  );
}
