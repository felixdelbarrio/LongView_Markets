import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function TaxAdvisor() {
  return (
    <FeaturePage
      config={{
        title: "Tax advisor",
        eyebrow: "Fiscalidad orientativa",
        description:
          "Estimaciones configurables por pais con reglas YAML, vigencia, fuente placeholder y confianza.",
        dataKind: "mock",
        queryKey: "tax",
        queryFn: () => api.taxRules(),
        highlights: ["Residencia fiscal", "Retencion origen", "Doble imposicion", "Disclaimer"],
      }}
    />
  );
}
