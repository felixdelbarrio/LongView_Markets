import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Plus, RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { Button } from "../design-system/components/Button";
import { Card } from "../design-system/components/Card";
import { DataQualityBadge } from "../design-system/components/DataQualityBadge";
import { DataTable } from "../design-system/components/DataTable";
import { EmptyState } from "../design-system/components/EmptyState";
import { FormField } from "../design-system/components/FormField";
import { Input } from "../design-system/components/Input";
import { MetricCard } from "../design-system/components/MetricCard";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";
import { Select } from "../design-system/components/Select";
import { formatMoney, formatPercent } from "../lib/utils";

type TransactionForm = {
  ticker: string;
  transaction_type: "buy" | "sell" | "dividend";
  trade_date: string;
  quantity: string;
  price: string;
  currency: string;
  fees: string;
  taxes: string;
  broker: string;
  notes: string;
};

const initialForm: TransactionForm = {
  ticker: "",
  transaction_type: "buy",
  trade_date: new Date().toISOString().slice(0, 10),
  quantity: "1",
  price: "0",
  currency: "USD",
  fees: "0",
  taxes: "0",
  broker: "",
  notes: "",
};

export function MyPortfolio() {
  const queryClient = useQueryClient();
  const [form, setForm] = useState<TransactionForm>(initialForm);
  const portfolio = useQuery({ queryKey: ["portfolio"], queryFn: api.portfolio });
  const transactions = useQuery({
    queryKey: ["portfolio-transactions"],
    queryFn: api.portfolioTransactions,
  });
  const history = useQuery({ queryKey: ["portfolio-history"], queryFn: api.portfolioHistory });
  const sync = useMutation({ mutationFn: api.syncPortfolio });
  const createTransaction = useMutation({
    mutationFn: api.createPortfolioTransaction,
    onSuccess: async () => {
      setForm(initialForm);
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["portfolio"] }),
        queryClient.invalidateQueries({ queryKey: ["portfolio-transactions"] }),
        queryClient.invalidateQueries({ queryKey: ["portfolio-history"] }),
      ]);
    },
  });
  const valuation = (portfolio.data?.data ?? {}) as Record<string, unknown>;
  const positions = Array.isArray(valuation.positions)
    ? (valuation.positions as Array<Record<string, unknown>>)
    : [];
  const txRows = transactions.data?.data ?? [];
  const isEmpty = txRows.length === 0;
  const historyRows = useMemo(() => {
    const rows = history.data?.data?.history;
    return Array.isArray(rows) ? (rows.slice(-12) as Array<Record<string, unknown>>) : [];
  }, [history.data]);
  function submit() {
    createTransaction.mutate({
      ...form,
      quantity: Number(form.quantity),
      price: Number(form.price),
      fees: Number(form.fees),
      taxes: Number(form.taxes),
      gross_amount: Number(form.quantity) * Number(form.price),
    });
  }
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Cartera real"
        title="Mi cartera"
        description="Aún no has añadido operaciones. Para reconstruir tu histórico introduce cada compra, venta y dividendo con su fecha real."
        source={portfolio.data?.source ?? "backend"}
      >
        {isEmpty ? (
          <EmptyState message="Añadir primera compra activará la ingesta asíncrona de perfil, precios, dividendos, FX, noticias, forecasting, alertas y calidad de datos." />
        ) : (
          <div className="grid gap-3 md:grid-cols-4">
            <MetricCard
              label="Valor total"
              value={formatMoney(
                Number(valuation.total_market_value_base ?? 0),
                String(valuation.base_currency ?? "EUR"),
              )}
            />
            <MetricCard
              label="Inversión"
              value={formatMoney(
                Number(valuation.total_invested_base ?? 0),
                String(valuation.base_currency ?? "EUR"),
              )}
            />
            <MetricCard
              label="Rentabilidad"
              value={formatPercent(Number(valuation.total_return_pct ?? 0))}
            />
            <MetricCard
              label="Dividendos"
              value={formatMoney(
                Number(valuation.dividends_received_base ?? 0),
                String(valuation.base_currency ?? "EUR"),
              )}
            />
          </div>
        )}
      </PageHeader>

      <Section title="Guía de entrada manual">
        <Card>
          <ol className="grid gap-2 text-sm leading-6 text-muted md:grid-cols-2">
            <li>1. Compra antigua: fecha, títulos, precio, divisa y comisión.</li>
            <li>2. Compra sucesiva: repite la operación con su fecha real.</li>
            <li>3. Venta parcial: LongView consume lotes por FIFO.</li>
            <li>4. Dividendo: registra importe, retención e impuesto por separado.</li>
          </ol>
        </Card>
      </Section>

      <Section title="Nueva operación">
        <Card>
          <div className="grid gap-3 md:grid-cols-4">
            <FormField label="Ticker">
              <Input
                value={form.ticker}
                onChange={(event) => setForm({ ...form, ticker: event.target.value.toUpperCase() })}
              />
            </FormField>
            <FormField label="Tipo">
              <Select
                value={form.transaction_type}
                onChange={(event) =>
                  setForm({
                    ...form,
                    transaction_type: event.target.value as TransactionForm["transaction_type"],
                  })
                }
              >
                <option value="buy">Compra</option>
                <option value="sell">Venta</option>
                <option value="dividend">Dividendo</option>
              </Select>
            </FormField>
            <FormField label="Fecha">
              <Input
                type="date"
                value={form.trade_date}
                onChange={(event) => setForm({ ...form, trade_date: event.target.value })}
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
            <FormField label="Títulos">
              <Input
                type="number"
                value={form.quantity}
                onChange={(event) => setForm({ ...form, quantity: event.target.value })}
              />
            </FormField>
            <FormField label="Precio unitario">
              <Input
                type="number"
                value={form.price}
                onChange={(event) => setForm({ ...form, price: event.target.value })}
              />
            </FormField>
            <FormField label="Comisiones">
              <Input
                type="number"
                value={form.fees}
                onChange={(event) => setForm({ ...form, fees: event.target.value })}
              />
            </FormField>
            <FormField label="Impuestos">
              <Input
                type="number"
                value={form.taxes}
                onChange={(event) => setForm({ ...form, taxes: event.target.value })}
              />
            </FormField>
            <FormField label="Broker">
              <Input
                value={form.broker}
                onChange={(event) => setForm({ ...form, broker: event.target.value })}
              />
            </FormField>
            <FormField label="Notas">
              <Input
                value={form.notes}
                onChange={(event) => setForm({ ...form, notes: event.target.value })}
              />
            </FormField>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button onClick={submit} disabled={createTransaction.isPending}>
              <Plus size={17} /> {isEmpty ? "Añadir primera compra" : "Añadir operación"}
            </Button>
            <Button onClick={() => sync.mutate()} disabled={sync.isPending}>
              <RefreshCw size={17} /> Sincronizar precios
            </Button>
          </div>
        </Card>
      </Section>

      <Section title="Posiciones y lotes">
        <div className="grid gap-4 xl:grid-cols-[1.2fr_0.8fr]">
          <Card>
            <div className="mb-3 flex justify-between gap-3">
              <h3 className="text-lg font-bold">Posiciones</h3>
              <DataQualityBadge flags={valuation.quality_flags as string[] | undefined} />
            </div>
            <DataTable
              rows={positions.map((row) => ({
                ticker: row.ticker,
                titulos: row.quantity,
                valor_eur: row.market_value_base,
                coste_eur: row.invested_amount_base,
                plusvalia: row.unrealized_pnl_base,
                rentabilidad: row.total_return_pct,
                divisa: row.currency,
                fx: row.fx_rate,
              }))}
            />
          </Card>
          <Card>
            <h3 className="text-lg font-bold">Últimas operaciones</h3>
            <DataTable
              rows={txRows.slice(-8).map((row) => ({
                fecha: row.trade_date,
                ticker: row.ticker,
                tipo: row.transaction_type,
                titulos: row.quantity,
                precio: row.price,
                divisa: row.currency,
              }))}
            />
          </Card>
        </div>
      </Section>

      <Section title="Histórico fin de día">
        <Card>
          <DataTable
            rows={historyRows.map((row) => ({
              fecha: row.date,
              valor: row.market_value_base,
              inversion: row.invested_capital_base,
              plusvalia: row.total_return_base,
              pyg_diario: row.daily_pnl_base,
              dividendos: row.dividends_base,
              flags: Array.isArray(row.data_quality_flags) ? row.data_quality_flags.join(", ") : "",
            }))}
          />
        </Card>
      </Section>
    </div>
  );
}
