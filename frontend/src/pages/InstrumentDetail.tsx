import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../services/api";
import { Button } from "../design-system/components/Button";
import { Card } from "../design-system/components/Card";
import { DataQualityBadge } from "../design-system/components/DataQualityBadge";
import { DataTable } from "../design-system/components/DataTable";
import { EmptyState } from "../design-system/components/EmptyState";
import { FormField } from "../design-system/components/FormField";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";
import { Select } from "../design-system/components/Select";

const tabs = [
  "Resumen",
  "Histórico",
  "Noticias",
  "Insights",
  "Alertas",
  "Forecasting",
  "Dividendos",
  "Operaciones",
  "Calidad de datos",
];

export function InstrumentDetail() {
  const { ticker = "MSFT" } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState(tabs[0]);
  const instruments = useQuery({ queryKey: ["instruments"], queryFn: api.instruments });
  const instrument = useQuery({
    queryKey: ["instrument", ticker],
    queryFn: () => api.instrument(ticker),
  });
  const sync = useMutation({
    mutationFn: () => api.syncTicker(ticker),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["instrument", ticker] }),
  });
  const data = instrument.data?.data ?? {};
  const item = (data.instrument ?? {}) as Record<string, unknown>;
  const latest = (data.latest_price ?? {}) as Record<string, unknown> | null;
  const rows = (key: string) =>
    Array.isArray(data[key]) ? (data[key] as Array<Record<string, unknown>>) : [];
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Instrumentos"
        title={`${String(item.ticker ?? ticker).toUpperCase()} · ${String(item.name ?? ticker)}`}
        description="Noticias, insights, alertas, forecasting, dividendos, operaciones y calidad viven dentro del instrumento, no como pantallas globales."
        source={String(item.provider ?? "backend")}
      >
        <div className="grid gap-3 md:grid-cols-[1fr_auto]">
          <FormField label="Seleccionar instrumento">
            <Select
              value={ticker.toUpperCase()}
              onChange={(event) => navigate(`/instruments/${event.target.value}`)}
            >
              {(instruments.data?.data ?? []).slice(0, 250).map((row) => (
                <option key={String(row.ticker)} value={String(row.ticker)}>
                  {String(row.ticker)} · {String(row.name ?? row.market ?? "")}
                </option>
              ))}
            </Select>
          </FormField>
          <Button onClick={() => sync.mutate()} disabled={sync.isPending}>
            <Search size={17} /> Sincronizar instrumento
          </Button>
        </div>
      </PageHeader>
      <div className="flex flex-wrap gap-2">
        {tabs.map((itemTab) => (
          <Button
            key={itemTab}
            className={tab === itemTab ? "" : "bg-elevated text-text"}
            onClick={() => setTab(itemTab)}
          >
            {itemTab}
          </Button>
        ))}
      </div>
      {tab === "Resumen" ? (
        <section className="grid gap-4 md:grid-cols-3">
          <Card>
            <h2 className="text-lg font-bold">Precio actual</h2>
            <p className="mt-2 text-3xl font-black">{String(latest?.close ?? "Sin datos")}</p>
            <p className="mt-2 text-sm text-muted">
              {String(latest?.date ?? "Pendiente de sincronizar")}
            </p>
          </Card>
          <Card>
            <h2 className="text-lg font-bold">Moneda</h2>
            <p className="mt-2 text-3xl font-black">{String(item.currency ?? "USD")}</p>
            <p className="mt-2 text-sm text-muted">{String(item.exchange ?? "unknown")}</p>
          </Card>
          <Card>
            <h2 className="text-lg font-bold">Calidad</h2>
            <DataQualityBadge flags={latest ? ["observed_or_cached"] : ["sin_datos"]} />
          </Card>
        </section>
      ) : null}
      {tab === "Histórico" ? (
        <Section title="Histórico mínimo objetivo 2 años">
          <Card>
            <DataTable
              rows={rows("prices")
                .slice(-40)
                .map((row) => ({
                  fecha: row.date,
                  cierre: row.close,
                  volumen: row.volume,
                  fuente: row.provider,
                }))}
            />
          </Card>
        </Section>
      ) : null}
      {tab === "Noticias" ? (
        <Section title="Noticias y sentimiento">
          <Card>
            {rows("news").length ? (
              <DataTable
                rows={rows("news").map((row) => ({
                  fecha: row.published_at,
                  fuente: row.source,
                  titular: row.headline,
                  sentimiento: row.sentiment,
                  gpt: row.gpt_status,
                  url: row.url,
                }))}
              />
            ) : (
              <EmptyState message="No hay noticias ingeridas. Si GPT externo no está configurado, el sentimiento queda pendiente." />
            )}
          </Card>
        </Section>
      ) : null}
      {tab === "Insights" ? <InstrumentRows title="Insights" rows={rows("insights")} /> : null}
      {tab === "Alertas" ? <InstrumentRows title="Alertas" rows={rows("alerts")} /> : null}
      {tab === "Forecasting" ? (
        <Section title="Forecasting">
          <Card>
            <DataTable
              rows={
                Array.isArray((data.forecast as Record<string, unknown>)?.scenarios)
                  ? ((data.forecast as Record<string, unknown>).scenarios as Array<
                      Record<string, unknown>
                    >)
                  : []
              }
            />
          </Card>
        </Section>
      ) : null}
      {tab === "Dividendos" ? <InstrumentRows title="Dividendos" rows={rows("dividends")} /> : null}
      {tab === "Operaciones" ? (
        <InstrumentRows title="Operaciones" rows={rows("operations")} />
      ) : null}
      {tab === "Calidad de datos" ? (
        <Section title="Calidad de datos">
          <Card>
            <DataTable rows={[(data.data_quality ?? {}) as Record<string, unknown>]} />
          </Card>
        </Section>
      ) : null}
    </div>
  );
}

function InstrumentRows({ title, rows }: { title: string; rows: Array<Record<string, unknown>> }) {
  return (
    <Section title={title}>
      <Card>
        {rows.length ? <DataTable rows={rows} /> : <EmptyState message="Sin datos suficientes." />}
      </Card>
    </Section>
  );
}
