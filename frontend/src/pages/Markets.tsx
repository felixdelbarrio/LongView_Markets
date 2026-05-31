import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { Button } from "../design-system/components/Button";
import { Card } from "../design-system/components/Card";
import { DataTable } from "../design-system/components/DataTable";
import { EmptyState } from "../design-system/components/EmptyState";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";

export function Markets() {
  const queryClient = useQueryClient();
  const markets = useQuery({ queryKey: ["markets"], queryFn: api.markets });
  const jobs = useQuery({ queryKey: ["ingestion-jobs"], queryFn: api.ingestionJobs });
  const sync = useMutation({
    mutationFn: api.syncMarkets,
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: ["markets"] }),
        queryClient.invalidateQueries({ queryKey: ["ingestion-jobs"] }),
      ]),
  });
  const rows = markets.data?.data ?? [];
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Mercados"
        title="Mercados"
        description="Universos sincronizables con proveedor configurado. Los datos de cartera no se mezclan con mercados hasta que el usuario registra operaciones reales."
        source={markets.data?.source ?? "backend"}
      >
        <Button onClick={() => sync.mutate()} disabled={sync.isPending}>
          <RefreshCw size={17} /> Sincronizar mercados
        </Button>
      </PageHeader>
      <Section title="Universos">
        <Card>
          {rows.length ? (
            <DataTable
              rows={rows.map((row) => ({
                mercado: row.market,
                universo: row.universe_id,
                miembros: row.members,
                estado: row.status,
                precios: row.rows_prices,
                proveedor: row.provider,
                actualizado: row.last_updated_at,
              }))}
            />
          ) : (
            <EmptyState message="No hay universos disponibles." />
          )}
        </Card>
      </Section>
      <Section title="Progreso de ingesta">
        <Card>
          <DataTable
            rows={(jobs.data?.data ?? []).slice(0, 20).map((row) => ({
              tipo: row.type,
              proveedor: row.provider,
              universo: row.universe_id,
              ticker: row.ticker,
              estado: row.status,
              precios: row.rows_prices,
              dividendos: row.rows_dividends,
              noticias: row.rows_news,
              warnings: Array.isArray(row.warnings) ? row.warnings.length : 0,
              errores: Array.isArray(row.errors) ? row.errors.length : 0,
            }))}
          />
        </Card>
      </Section>
    </div>
  );
}
