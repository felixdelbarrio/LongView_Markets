import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import { Card } from "../design-system/components/Card";
import { DataTable } from "../design-system/components/DataTable";
import { MetricCard } from "../design-system/components/MetricCard";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";

export function DataQuality() {
  const quality = useQuery({ queryKey: ["data-quality"], queryFn: api.quality });
  const data = quality.data?.data ?? {};
  const byTicker = Object.entries(
    (data.by_ticker ?? {}) as Record<string, Record<string, unknown>>,
  );
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Calidad real"
        title="Calidad de datos"
        description="Si no hay ingesta observada, la calidad global es 0% y el estado queda como sin datos suficientes."
        source={quality.data?.source ?? "backend"}
      >
        <div className="grid gap-3 md:grid-cols-3">
          <MetricCard label="Global" value={`${String(data.global_score ?? 0)}%`} />
          <MetricCard label="Estado" value={String(data.status ?? "sin datos suficientes")} />
          <MetricCard label="Tipo" value={String(data.data_kind ?? "no_data")} />
        </div>
      </PageHeader>
      <Section title="Cobertura por valor">
        <Card>
          <DataTable
            rows={byTicker.map(([ticker, row]) => ({
              ticker,
              score: row.score,
              estado: row.status,
              precios: row.prices_available,
            }))}
          />
        </Card>
      </Section>
      <Section title="Proveedores">
        <Card>
          <DataTable
            rows={
              Array.isArray(data.provider_status)
                ? (data.provider_status as Array<Record<string, unknown>>)
                : []
            }
          />
        </Card>
      </Section>
    </div>
  );
}
