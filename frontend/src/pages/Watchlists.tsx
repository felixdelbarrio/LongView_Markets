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
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";

export function Watchlists() {
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [ticker, setTicker] = useState("");
  const watchlists = useQuery({ queryKey: ["watchlists"], queryFn: api.watchlists });
  const create = useMutation({
    mutationFn: api.createWatchlist,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["watchlists"] }),
  });
  const addItem = useMutation({ mutationFn: () => api.addWatchlistItem("manual", { ticker }) });
  const rows = watchlists.data?.data ?? [];
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Seguimiento"
        title="Listas de seguimiento"
        description="Crea listas, añade tickers, sincroniza histórico de 2 años, forecasting, noticias y sentimiento."
        source={watchlists.data?.source ?? "backend"}
      />
      <Section title="Crear y añadir valores">
        <Card>
          <div className="grid gap-3 md:grid-cols-[1fr_auto_1fr_auto]">
            <FormField label="Lista">
              <Input value={name} onChange={(event) => setName(event.target.value)} />
            </FormField>
            <Button onClick={() => create.mutate({ name })} disabled={!name}>
              <Plus size={17} /> Crear lista
            </Button>
            <FormField label="Ticker">
              <Input
                value={ticker}
                onChange={(event) => setTicker(event.target.value.toUpperCase())}
              />
            </FormField>
            <Button onClick={() => addItem.mutate()} disabled={!ticker}>
              <Plus size={17} /> Añadir ticker
            </Button>
          </div>
        </Card>
      </Section>
      <Section title="Listas">
        <Card>
          {rows.length ? (
            <DataTable
              rows={rows.map((row) => ({
                id: row.id,
                nombre: row.name,
                elementos: Array.isArray(row.items) ? row.items.length : 0,
                actualizado: row.updated_at,
              }))}
            />
          ) : (
            <EmptyState message="No hay listas todavía." />
          )}
        </Card>
      </Section>
    </div>
  );
}
