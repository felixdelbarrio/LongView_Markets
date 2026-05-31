import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus } from "lucide-react";
import { api } from "../services/api";
import { Button } from "../design-system/components/Button";
import { Card } from "../design-system/components/Card";
import { DataTable } from "../design-system/components/DataTable";
import { EmptyState } from "../design-system/components/EmptyState";
import { FormField } from "../design-system/components/FormField";
import { Input } from "../design-system/components/Input";
import { MetricCard } from "../design-system/components/MetricCard";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";
import { formatMoney, formatPercent } from "../lib/utils";

export function SimulatedPortfolio() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState({
    ticker: "",
    quantity: "1",
    price: "",
    trade_date: new Date().toISOString().slice(0, 10),
    currency: "USD",
  });
  const portfolio = useQuery({
    queryKey: ["simulated-portfolio"],
    queryFn: api.simulatedPortfolio,
  });
  const transactions = useQuery({
    queryKey: ["simulated-transactions"],
    queryFn: api.simulatedTransactions,
  });
  const create = useMutation({
    mutationFn: api.createSimulatedTransaction,
    onSuccess: () =>
      Promise.all([
        queryClient.invalidateQueries({ queryKey: ["simulated-portfolio"] }),
        queryClient.invalidateQueries({ queryKey: ["simulated-transactions"] }),
      ]),
  });
  const valuation = portfolio.data?.data ?? {};
  const rows = transactions.data?.data ?? [];
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Simulación"
        title="Cartera simulada"
        description="Arranca vacía. Cada compra simulada puede usar precio sugerido desde yfinance/cache y lanza análisis en background."
        source={portfolio.data?.source ?? "backend"}
      >
        {rows.length ? (
          <div className="grid gap-3 md:grid-cols-3">
            <MetricCard
              label="Valor simulado"
              value={formatMoney(Number(valuation.total_market_value_base ?? 0))}
            />
            <MetricCard
              label="Inversión"
              value={formatMoney(Number(valuation.total_invested_base ?? 0))}
            />
            <MetricCard
              label="Rentabilidad"
              value={formatPercent(Number(valuation.total_return_pct ?? 0))}
            />
          </div>
        ) : (
          <EmptyState message="Aún no hay compras simuladas." />
        )}
      </PageHeader>
      <Section title="Añadir compra simulada">
        <Card>
          <div className="grid gap-3 md:grid-cols-5">
            <FormField label="Ticker">
              <Input
                value={form.ticker}
                onChange={(event) => setForm({ ...form, ticker: event.target.value.toUpperCase() })}
              />
            </FormField>
            <FormField label="Fecha">
              <Input
                type="date"
                value={form.trade_date}
                onChange={(event) => setForm({ ...form, trade_date: event.target.value })}
              />
            </FormField>
            <FormField label="Títulos">
              <Input
                type="number"
                value={form.quantity}
                onChange={(event) => setForm({ ...form, quantity: event.target.value })}
              />
            </FormField>
            <FormField label="Precio">
              <Input
                type="number"
                value={form.price}
                placeholder="sugerido si existe cache"
                onChange={(event) => setForm({ ...form, price: event.target.value })}
              />
            </FormField>
            <FormField label="Divisa">
              <Input
                value={form.currency}
                onChange={(event) =>
                  setForm({ ...form, currency: event.target.value.toUpperCase() })
                }
              />
            </FormField>
          </div>
          <Button
            className="mt-4"
            onClick={() =>
              create.mutate({
                ...form,
                transaction_type: "buy",
                quantity: Number(form.quantity),
                price: form.price ? Number(form.price) : undefined,
              })
            }
          >
            <Plus size={17} /> Añadir compra simulada
          </Button>
        </Card>
      </Section>
      <Section title="Operaciones simuladas">
        <Card>
          <DataTable
            rows={rows.map((row) => ({
              fecha: row.trade_date,
              ticker: row.ticker,
              titulos: row.quantity,
              precio: row.price,
              divisa: row.currency,
            }))}
          />
        </Card>
      </Section>
    </div>
  );
}
