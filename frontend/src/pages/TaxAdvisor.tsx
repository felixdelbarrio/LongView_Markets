import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import { Card } from "../design-system/components/Card";
import { DataTable } from "../design-system/components/DataTable";
import { EmptyState } from "../design-system/components/EmptyState";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";

export function TaxAdvisor() {
  const events = useQuery({ queryKey: ["tax-relevant-events"], queryFn: api.taxRelevantEvents });
  const data = events.data?.data ?? {};
  const rows = Array.isArray(data.rows) ? (data.rows as Array<Record<string, unknown>>) : [];
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Fiscalidad"
        title="Asesor fiscal"
        description="Solo trabaja con ventas reales, dividendos cobrados y acciones de dividendos ejecutadas."
        source={events.data?.source ?? "backend"}
      />
      <Section title="Eventos fiscalmente relevantes">
        <Card>
          {rows.length ? (
            <DataTable
              rows={rows.map((row) => ({
                fecha: row.trade_date,
                ticker: row.ticker,
                tipo: row.transaction_type,
                importe: row.gross_amount,
                impuestos: row.taxes,
                divisa: row.currency,
              }))}
            />
          ) : (
            <EmptyState
              message={String(data.message ?? "No hay operaciones fiscalmente relevantes todavía")}
            />
          )}
        </Card>
      </Section>
      <Section title="Aviso">
        <Card>
          <p className="text-sm leading-6 text-muted">
            {String(
              data.disclaimer ??
                "Estimación orientativa; no sustituye asesoramiento fiscal profesional.",
            )}
          </p>
        </Card>
      </Section>
    </div>
  );
}
