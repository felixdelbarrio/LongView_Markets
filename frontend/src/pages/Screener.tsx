import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { Button } from "../design-system/components/Button";
import { Card } from "../design-system/components/Card";
import { DataTable } from "../design-system/components/DataTable";
import { EmptyState } from "../design-system/components/EmptyState";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";

export function Screener() {
  const [tab, setTab] = useState("Oportunidades próximas");
  const queryClient = useQueryClient();
  const screener = useQuery({ queryKey: ["screener"], queryFn: api.screener });
  const sync = useMutation({
    mutationFn: api.syncMarkets,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["screener"] }),
  });
  const data = screener.data?.data ?? {};
  const results = Array.isArray(data.results)
    ? (data.results as Array<Record<string, unknown>>)
    : [];
  const expired = Array.isArray(data.expired)
    ? (data.expired as Array<Record<string, unknown>>)
    : [];
  const presets = Array.isArray(data.presets) ? (data.presets as string[]) : [];
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Screener operativo"
        title="Screener"
        description="Recomendaciones medibles basadas en datos observados o cacheados. Las recomendaciones vencidas se evalúan contra precio real."
        source={screener.data?.source ?? "backend"}
      >
        <Button onClick={() => sync.mutate()} disabled={sync.isPending}>
          <RefreshCw size={17} /> Sincronizar universo
        </Button>
      </PageHeader>
      <div className="flex flex-wrap gap-2">
        {["Oportunidades próximas", "Recomendaciones vencidas", "Presets"].map((item) => (
          <Button
            key={item}
            className={tab === item ? "" : "bg-elevated text-text"}
            onClick={() => setTab(item)}
          >
            {item}
          </Button>
        ))}
      </div>
      {tab === "Oportunidades próximas" ? (
        <Section title="Oportunidades próximas">
          <Card>
            {results.length ? (
              <DataTable
                rows={results.map((row) => ({
                  ticker: row.ticker,
                  tesis: row.momentum,
                  precio: row.current_price,
                  calidad: row.data_quality_score,
                  cagr: row.cagr,
                  volatilidad: row.volatility,
                  confianza: row.confidence,
                  fuente: row.source,
                }))}
              />
            ) : (
              <EmptyState
                message={String(
                  data.message ?? "Sin recomendaciones hasta sincronizar datos reales.",
                )}
              />
            )}
          </Card>
        </Section>
      ) : null}
      {tab === "Recomendaciones vencidas" ? (
        <Section title="Evaluación histórica">
          <Card>
            {expired.length ? (
              <DataTable rows={expired} />
            ) : (
              <EmptyState message="No hay recomendaciones vencidas todavía." />
            )}
          </Card>
        </Section>
      ) : null}
      {tab === "Presets" ? (
        <Section title="Presets">
          <Card>
            <DataTable rows={presets.map((preset) => ({ preset, estado: "disponible" }))} />
          </Card>
        </Section>
      ) : null}
    </div>
  );
}
