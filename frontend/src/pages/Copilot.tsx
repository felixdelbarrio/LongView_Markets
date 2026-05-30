import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function Copilot() {
  return (
    <FeaturePage
      config={{
        title: "Copilot",
        eyebrow: "GPT externo configurable",
        description:
          "Construye contexto estructurado para GPT externo sin usar API: argumentos, riesgos, checklist y preguntas.",
        dataKind: "mock",
        queryKey: "copilot",
        queryFn: () => api.copilot("MSFT"),
        highlights: ["Copiar contexto", "Abrir GPT", "Riesgos", "Checklist"],
      }}
    />
  );
}
