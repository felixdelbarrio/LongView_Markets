import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { api } from "../services/api";
import { MetricCard } from "../components/financial/MetricCard";
import { ConfidenceBadge, RiskBadge, SourceBadge } from "../components/financial/Badges";
import { Card } from "../components/ui/card";
import { formatMoney, formatPercent } from "../lib/utils";
import { MarketHeatmap } from "../components/financial/MarketHeatmap";
import { PortfolioAllocationChart } from "../components/charts/PortfolioAllocationChart";
import { Sparkline } from "../components/charts/Sparkline";

export function Dashboard() {
  const { t } = useTranslation();
  const { data } = useQuery({ queryKey: ["dashboard"], queryFn: api.dashboard });
  if (!data) {
    return <div className="h-96 animate-pulse rounded-lg bg-panel" />;
  }
  const spark = data.opportunities.map((item, index) => ({
    value: Number(item.cagr ?? index) + 20,
  }));
  return (
    <div className="space-y-6">
      <motion.section
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        className="overflow-hidden rounded-lg border border-line bg-panel p-6 shadow-glow"
      >
        <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <SourceBadge kind={data.lineage.data_kind} />
              <ConfidenceBadge value={data.lineage.confidence} />
              <RiskBadge value={data.hero.aggregate_risk} />
            </div>
            <h1 className="mt-6 max-w-4xl text-4xl font-black tracking-normal md:text-6xl">
              {t("dashboard.title")}
            </h1>
            <p className="mt-4 max-w-3xl text-lg leading-8 text-muted">{t("app.subtitle")}</p>
            <p className="mt-5 rounded-md border border-amber/40 bg-amber/10 p-4 text-sm font-semibold text-amber">
              {data.narrative}
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
            <MetricCard
              label="Valor cartera"
              value={formatMoney(data.hero.portfolio_value)}
              detail="Total calculado en backend con datos seed y precios diarios."
            />
            <MetricCard
              label="Rentabilidad total"
              value={formatPercent(data.hero.total_return)}
              detail="No promete resultados futuros; usa coste y precio de cierre demo."
              tone="teal"
            />
          </div>
        </div>
      </motion.section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="YTD"
          value={formatPercent(data.hero.ytd_return)}
          detail="Rentabilidad desde inicio de año calculada en backend."
        />
        <MetricCard
          label="Dividendos próximos"
          value={String(data.hero.upcoming_dividends)}
          detail="Eventos mock del calendario de dividendos."
          tone="amber"
        />
        <MetricCard
          label="Alertas críticas"
          value={String(data.hero.critical_alerts)}
          detail="Alertas explicables con evidencia y confianza."
          tone="amber"
        />
        <MetricCard
          label="Datos"
          value={data.hero.data_status}
          detail="Estado de Parquet, SQLite y proveedores locales."
          tone="teal"
        />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1fr_0.85fr]">
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-2xl font-bold">Market Pulse</h2>
            <SourceBadge kind="mock" />
          </div>
          <MarketHeatmap rows={data.opportunities} />
        </Card>
        <Card>
          <h2 className="text-2xl font-bold">Riesgo de cartera</h2>
          <PortfolioAllocationChart positions={data.risk.positions} />
          <p className="text-sm text-muted">
            Concentración top 5: {formatPercent(data.risk.top5_concentration)}
          </p>
        </Card>
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <Card>
          <h2 className="text-xl font-bold">Oportunidades</h2>
          <Sparkline data={spark} />
          <div className="mt-4 space-y-3">
            {data.opportunities.slice(0, 5).map((item) => (
              <div
                key={String(item.ticker)}
                className="rounded-md border border-line bg-canvas/50 p-3"
              >
                <div className="flex items-center justify-between gap-3">
                  <strong>{String(item.ticker)}</strong>
                  <ConfidenceBadge value={Number(item.confidence ?? 0.78)} />
                </div>
                <p className="mt-1 text-sm text-muted">
                  {String(item.name ?? item.sector)} · CAGR {String(item.cagr ?? "n/a")}% · Vol{" "}
                  {String(item.volatility ?? "n/a")}%
                </p>
              </div>
            ))}
          </div>
        </Card>
        <Card>
          <h2 className="text-xl font-bold">Disciplina inversora</h2>
          <ul className="mt-4 space-y-3 text-sm text-muted">
            <li>{data.discipline.journal_reviews.length} tesis pendientes de revisar</li>
            <li>{data.discipline.watchlists.length} watchlists activas</li>
            <li>{data.discipline.simulations.length} simulaciones abiertas</li>
          </ul>
        </Card>
        <Card>
          <h2 className="text-xl font-bold">Copiloto externo</h2>
          <div className="mt-4 space-y-3">
            {data.copilot.questions.map((question) => (
              <p key={question} className="rounded-md border border-line bg-canvas/50 p-3 text-sm">
                {question}
              </p>
            ))}
          </div>
        </Card>
      </section>
    </div>
  );
}
