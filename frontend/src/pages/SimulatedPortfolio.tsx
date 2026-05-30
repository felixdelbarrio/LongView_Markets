import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function SimulatedPortfolio() {
  return (
    <FeaturePage
      config={{
        title: "Simulated portfolio",
        eyebrow: "Laboratorio de inversion",
        description:
          "Simula tesis, compras, ventas, dividendos, escenarios y conversion prudente a cartera real.",
        dataKind: "simulation",
        queryKey: "simulated",
        queryFn: () => api.simulatedPortfolio(),
        highlights: ["Tesis", "Escenarios", "Comparar con real", "Convertir a real"],
      }}
    />
  );
}
