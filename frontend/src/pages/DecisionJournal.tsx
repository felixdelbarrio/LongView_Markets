import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function DecisionJournal() {
  return (
    <FeaturePage
      config={{
        title: "Decision journal",
        eyebrow: "Disciplina inversora",
        description:
          "Registra tesis, hipotesis, riesgos, precio, horizonte, snapshot y revision posterior.",
        dataKind: "mock",
        queryKey: "journal",
        queryFn: () => api.journal(),
        highlights: ["Tesis", "Riesgos", "Snapshot", "Revision"],
      }}
    />
  );
}
