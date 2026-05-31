import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../services/api";
import { Button } from "../design-system/components/Button";
import { Card } from "../design-system/components/Card";
import { DataTable } from "../design-system/components/DataTable";
import { FormField } from "../design-system/components/FormField";
import { Input } from "../design-system/components/Input";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";
import { Select } from "../design-system/components/Select";

export function Settings() {
  const queryClient = useQueryClient();
  const { data } = useQuery({ queryKey: ["settings"], queryFn: api.settings });
  const settings = (data?.data ?? {}) as Record<string, unknown>;
  const [language, setLanguage] = useState(String(settings.language ?? "es"));
  const [theme, setTheme] = useState(String(settings.theme ?? "dark"));
  const [provider, setProvider] = useState(String(settings.default_market_provider ?? "yfinance"));
  const [externalGptUrl, setExternalGptUrl] = useState(
    String(settings.external_gpt_url ?? "https://chatgpt.com/g/g-longview-markets"),
  );
  const save = useMutation({
    mutationFn: api.saveSettings,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["settings"] }),
  });
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Configuración operativa"
        title="Settings"
        description="Persistencia real en SQLite para idioma, tema, proveedores, FX, sincronización, modo generativo y privacidad."
        source="backend"
      />
      <Section title="Preferencias principales">
        <Card>
          <div className="grid gap-3 md:grid-cols-4">
            <FormField label="Idioma">
              <Select value={language} onChange={(event) => setLanguage(event.target.value)}>
                <option value="es">Español</option>
                <option value="en">English</option>
              </Select>
            </FormField>
            <FormField label="Tema">
              <Select value={theme} onChange={(event) => setTheme(event.target.value)}>
                <option value="dark">Oscuro</option>
                <option value="light">Claro</option>
              </Select>
            </FormField>
            <FormField label="Proveedor mercado">
              <Select value={provider} onChange={(event) => setProvider(event.target.value)}>
                <option value="yfinance">yfinance</option>
                <option value="stooq">stooq</option>
                <option value="alpha_vantage">alpha_vantage</option>
                <option value="finnhub">finnhub</option>
                <option value="twelve_data">twelve_data</option>
                <option value="polygon">polygon</option>
                <option value="bloomberg">bloomberg</option>
                <option value="refinitiv">refinitiv</option>
                <option value="factset">factset</option>
              </Select>
            </FormField>
            <FormField label="GPT externo">
              <Input
                value={externalGptUrl}
                onChange={(event) => setExternalGptUrl(event.target.value)}
              />
            </FormField>
          </div>
          <Button
            className="mt-4"
            onClick={() =>
              save.mutate({
                language,
                theme,
                default_market_provider: provider,
                external_gpt_url: externalGptUrl,
              })
            }
          >
            Guardar configuración
          </Button>
        </Card>
      </Section>
      <Section title="Valores persistidos">
        <Card>
          <DataTable rows={Object.entries(settings).map(([key, value]) => ({ key, value }))} />
        </Card>
      </Section>
    </div>
  );
}
