import { useMemo, useState } from "react";
import { Card } from "../design-system/components/Card";
import { Input } from "../design-system/components/Input";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";

const guides = [
  [
    "Dashboard",
    "Muestra cartera real solo cuando existen operaciones; Market Pulse funciona con mercados sincronizados.",
  ],
  [
    "Añadir cartera",
    "Introduce compras, ventas y dividendos con fecha real para reconstruir FIFO, PyG, FX y dividendos.",
  ],
  [
    "Sincronizar mercados",
    "El botón global crea jobs de ingesta para precios, divisas, noticias, cartera, watchlists y daily close.",
  ],
  [
    "Calidad de datos",
    "0% significa que no hay ingesta observada; los scores suben con precios, FX, dividendos, noticias y forecast.",
  ],
  [
    "InstrumentDetail",
    "Centraliza resumen, histórico, noticias, insights, alertas, forecasting, dividendos y operaciones.",
  ],
  [
    "Screener",
    "Ordena oportunidades con datos reales/cacheados y evalúa recomendaciones vencidas.",
  ],
  ["Dividendos", "Separa propuestas y acciones realizadas con seguimiento neto y fiscalidad."],
  [
    "Cartera simulada",
    "Permite probar compras sin mezclarlas con cartera real y lanza el mismo análisis de fondo.",
  ],
  ["FX", "Las conversiones se calculan en backend con moneda base y fecha de operación."],
  [
    "Rentabilidad",
    "La rentabilidad se calcula en backend con coste, comisiones, impuestos, dividendos y precio cacheado.",
  ],
  [
    "Forecast",
    "Escenarios informativos con limitaciones explícitas; no son predicciones garantizadas.",
  ],
  [
    "Sentimiento generativo",
    "El análisis queda pendiente si no hay GPT externo configurado y se valida con JSON estricto.",
  ],
  [
    "No asesoramiento",
    "LongView es soporte informativo y educativo; no sustituye asesoramiento financiero.",
  ],
];

export function OperationalGuides() {
  const [query, setQuery] = useState("");
  const rows = useMemo(
    () =>
      guides.filter(([title, body]) =>
        `${title} ${body}`.toLowerCase().includes(query.toLowerCase()),
      ),
    [query],
  );
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="FAQ"
        title="Guías operativas"
        description="Guías de negocio para usar LongView sin depender de pantallas de demo ni copilot independiente."
        source="docs"
      />
      <Section title="Buscar">
        <Card>
          <Input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="calidad, forecast, dividendos..."
          />
        </Card>
      </Section>
      <Section title="Preguntas frecuentes">
        <div className="grid gap-3 md:grid-cols-2">
          {rows.map(([title, body]) => (
            <Card key={title}>
              <h2 className="text-lg font-bold">{title}</h2>
              <p className="mt-2 text-sm leading-6 text-muted">{body}</p>
            </Card>
          ))}
        </div>
      </Section>
    </div>
  );
}
