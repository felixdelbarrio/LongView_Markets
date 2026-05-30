import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function DataQuality() {
  return (
    <FeaturePage
      config={{
        title: "Data quality",
        eyebrow: "Confianza operacional",
        description:
          "Estado global, proveedor, ticker, incidencias, semaforo y explicaciones claras.",
        dataKind: "mock",
        queryKey: "quality",
        queryFn: () => api.quality(),
        highlights: ["Faltantes", "Duplicados", "OHLC", "Datos obsoletos"],
      }}
    />
  );
}
