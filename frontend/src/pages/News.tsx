import { api } from "../services/api";
import { FeaturePage } from "./FeaturePage";

export function News() {
  return (
    <FeaturePage
      config={{
        title: "News",
        eyebrow: "Eventos y contexto",
        description:
          "Noticias por mercado y ticker con fuente, fecha, sentimiento y etiqueta mock/demo.",
        dataKind: "mock",
        queryKey: "news",
        queryFn: () => api.news(),
        highlights: ["Noticias por ticker", "Earnings", "Dividendos", "Sentimiento"],
      }}
    />
  );
}
