import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, RefreshCw } from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../services/api";
import { Button } from "../design-system/components/Button";
import { Card } from "../design-system/components/Card";
import { DataQualityBadge } from "../design-system/components/DataQualityBadge";
import { DataTable } from "../design-system/components/DataTable";
import { EmptyState } from "../design-system/components/EmptyState";
import { MetricCard } from "../design-system/components/MetricCard";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";
import { formatMoney, formatPercent } from "../lib/utils";

export function Dashboard() {
  const queryClient = useQueryClient();
  const { data: result } = useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard });
  const syncMarkets = useMutation({
    mutationFn: api.syncMarkets,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["dashboard"] }),
  });
  const data = result?.data;
  if (!data) {
    return (
      <PageHeader
        eyebrow="Operativa"
        title="Centro de decisiones"
        description="Backend no disponible. Revisa make run y vuelve a cargar la aplicación."
        source="none"
      />
    );
  }
  const emptyPortfolio = Boolean(data.empty_portfolio);
  const risk = (data.risk ?? {}) as Record<string, unknown>;
  const hero = data.hero;
  const marketRows = data.market_pulse ?? [];
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Operativa real"
        title="Centro de decisiones"
        description={String(data.narrative)}
        source={String(data.lineage?.source ?? "backend")}
      >
        {emptyPortfolio ? (
          <div className="flex flex-wrap gap-2">
            <Link to="/my-portfolio">
              <Button>
                <Plus size={17} /> Añade tu primera operación
              </Button>
            </Link>
            <Button onClick={() => syncMarkets.mutate()} disabled={syncMarkets.isPending}>
              <RefreshCw size={17} /> Sincronizar mercados
            </Button>
          </div>
        ) : (
          <div className="grid gap-3 md:grid-cols-4">
            <MetricCard
              label="Valor total"
              value={formatMoney(Number(hero.portfolio_value ?? 0))}
            />
            <MetricCard
              label="Rentabilidad"
              value={formatPercent(Number(hero.total_return ?? 0))}
            />
            <MetricCard
              label="PyG diario"
              value={formatPercent(Number(risk.daily_change_pct ?? 0))}
            />
            <MetricCard label="Dividendos" value={String(hero.upcoming_dividends ?? 0)} />
          </div>
        )}
      </PageHeader>

      {emptyPortfolio ? (
        <EmptyState message="Todavía no hay cartera. LongView usará tus operaciones reales para calcular valoración, histórico, PyG, dividendos y riesgo." />
      ) : null}

      <Section title="Market Pulse">
        <Card>
          {data.market_pulse_status === "pending_sync" ? (
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm font-semibold text-muted">Mercados pendientes de sincronizar</p>
              <Button onClick={() => syncMarkets.mutate()} disabled={syncMarkets.isPending}>
                <RefreshCw size={17} /> Sincronizar mercados
              </Button>
            </div>
          ) : null}
          <div className="mt-4">
            <DataTable
              rows={marketRows.slice(0, 12).map((row) => ({
                mercado: row.market,
                universo: row.universe_id,
                miembros: row.members,
                estado: row.status,
                precios: row.rows_prices,
                proveedor: row.provider,
                actualizado: row.last_updated_at,
              }))}
            />
          </div>
        </Card>
      </Section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Calidad de datos" value={String(hero.data_status)} />
        <MetricCard label="Alertas" value={String(hero.critical_alerts)} />
        <MetricCard label="Universos" value={String(marketRows.length)} />
        <MetricCard label="Modo cartera" value={emptyPortfolio ? "vacía" : "calculada"} />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.8fr]">
        <Section title="Inteligencia proactiva">
          <Card>
            <p className="text-sm leading-6 text-muted">
              {String(data.proactive_intelligence?.summary ?? "")}
            </p>
            <div className="mt-4 grid gap-2">
              {(data.proactive_intelligence?.questions ?? []).map((question: string) => (
                <div key={question} className="rounded-md border border-line bg-canvas p-3 text-sm">
                  {question}
                </div>
              ))}
            </div>
          </Card>
        </Section>
        <Section title="Datos y trazabilidad">
          <Card>
            <div className="flex flex-wrap items-center gap-2">
              <DataQualityBadge flags={risk.quality_flags as string[] | undefined} />
            </div>
            <DataTable
              rows={[
                { campo: "fuente", valor: data.lineage?.source },
                { campo: "tipo", valor: data.lineage?.data_kind },
                { campo: "confianza", valor: data.lineage?.confidence },
                { campo: "generativa", valor: data.generative_context?.summary },
              ]}
            />
          </Card>
        </Section>
      </section>
    </div>
  );
}
