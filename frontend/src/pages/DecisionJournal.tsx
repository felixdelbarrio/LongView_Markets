import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import { Card } from "../design-system/components/Card";
import { DataTable } from "../design-system/components/DataTable";
import { EmptyState } from "../design-system/components/EmptyState";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";

export function DecisionJournal() {
  const journal = useQuery({ queryKey: ["journal"], queryFn: api.journal });
  const rows = journal.data?.data ?? [];
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Disciplina"
        title="Diario de decisiones"
        description="Solo muestra operaciones reales: compras, ventas, dividendos y estrategias ejecutadas."
        source={journal.data?.source ?? "backend"}
      />
      <Section title="Entradas">
        <Card>
          {rows.length ? (
            <DataTable
              rows={rows.map((row) => ({
                fecha: row.created_at,
                ticker: row.ticker,
                estado: row.status,
                motivo: row.thesis ?? row.notes,
                impacto: row.impact,
              }))}
            />
          ) : (
            <EmptyState message="No hay decisiones reales registradas todavía." />
          )}
        </Card>
      </Section>
    </div>
  );
}
