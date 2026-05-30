import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function Settings() {
  return (
    <FeaturePage
      config={{
        title: "Settings",
        eyebrow: "Configuracion premium",
        description:
          "Tema, idioma, fiscalidad, proveedor, API keys locales, GPT externo, benchmarks, riesgo y alertas.",
        dataKind: "mock",
        queryKey: "settings",
        queryFn: () => api.settings(),
        highlights: ["Tema", "Idioma", "Proveedor", "Exportar config"],
      }}
    />
  );
}
