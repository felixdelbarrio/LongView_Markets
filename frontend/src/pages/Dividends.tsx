import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../services/api";
import { Button } from "../design-system/components/Button";
import { Card } from "../design-system/components/Card";
import { DataTable } from "../design-system/components/DataTable";
import { EmptyState } from "../design-system/components/EmptyState";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";

export function Dividends() {
  const [tab, setTab] = useState("Propuestas");
  const dividends = useQuery({ queryKey: ["dividends"], queryFn: api.dividends });
  const rows = dividends.data?.data ?? [];
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Dividendos"
        title="Dividendos"
        description="Propuestas y acciones realizadas con seguimiento de inversión, retención, salida y resultado neto."
        source={dividends.data?.source ?? "backend"}
      />
      <div className="flex flex-wrap gap-2">
        {["Propuestas", "Acciones realizadas"].map((item) => (
          <Button
            key={item}
            className={tab === item ? "" : "bg-elevated text-text"}
            onClick={() => setTab(item)}
          >
            {item}
          </Button>
        ))}
      </div>
      {tab === "Propuestas" ? (
        <Section title="Propuestas">
          <Card>
            {rows.length ? (
              <DataTable
                rows={rows.map((row) => ({
                  ticker: row.ticker,
                  ex_date: row.ex_dividend_date,
                  payment: row.payment_date,
                  importe: row.amount,
                  divisa: row.currency,
                  yield_bruto: row.estimated_gross_yield,
                  yield_neto: row.estimated_net_yield,
                  riesgo: row.cut_risk,
                }))}
              />
            ) : (
              <EmptyState message="No hay propuestas de dividendos hasta sincronizar precios y dividendos reales/cacheados." />
            )}
          </Card>
        </Section>
      ) : (
        <Section title="Acciones realizadas">
          <Card>
            <EmptyState message="No hay estrategias de dividendos ejecutadas todavía." />
          </Card>
        </Section>
      )}
    </div>
  );
}
