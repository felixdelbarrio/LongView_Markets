import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Clipboard, FileJson, RefreshCw } from "lucide-react";
import { api } from "../services/api";
import { Button } from "../design-system/components/Button";
import { Card } from "../design-system/components/Card";
import { DataTable } from "../design-system/components/DataTable";
import { FormField } from "../design-system/components/FormField";
import { PageHeader } from "../design-system/components/PageHeader";
import { Section } from "../design-system/components/Section";
import { Select } from "../design-system/components/Select";

export function GenerativeIngestion() {
  const queryClient = useQueryClient();
  const [entityType, setEntityType] = useState("portfolio");
  const [entityId, setEntityId] = useState("real");
  const [selectedJob, setSelectedJob] = useState<Record<string, unknown> | null>(null);
  const [response, setResponse] = useState("");
  const jobs = useQuery({ queryKey: ["generative-jobs"], queryFn: api.generativeJobs });
  const history = useQuery({ queryKey: ["generative-history"], queryFn: api.generativeHistory });
  const createJob = useMutation({
    mutationFn: api.createGenerativeJob,
    onSuccess: async (result) => {
      setSelectedJob(result.data ?? null);
      await queryClient.invalidateQueries({ queryKey: ["generative-jobs"] });
    },
  });
  const prepareBatch = useMutation({
    mutationFn: api.prepareDailyGenerativeContext,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["generative-jobs"] }),
  });
  const validate = useMutation({
    mutationFn: () => api.validateGenerativeResponse(String(selectedJob?.id), response),
  });
  const repair = useMutation({
    mutationFn: () => api.repairGenerativeResponse(String(selectedJob?.id), response),
  });
  const importResponse = useMutation({
    mutationFn: () => api.importGenerativeResponse(String(selectedJob?.id), response),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: ["generative-jobs"] }),
        queryClient.invalidateQueries({ queryKey: ["generative-history"] }),
      ]);
    },
  });
  const rows = jobs.data?.data ?? [];
  const historyRows = history.data?.data ?? [];
  const prompt = String(selectedJob?.prompt_text ?? rows[0]?.prompt_text ?? "");
  async function copyPrompt() {
    await navigator.clipboard.writeText(prompt);
  }
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Ingesta generativa"
        title="GPT en JSON estricto"
        description="LongView prepara contexto estructurado, genera prompts versionados, valida respuestas JSON, repara errores controlados y almacena histórico como generative_inference."
        source="backend"
      />
      <Section title="Preparar prompts">
        <Card>
          <div className="grid gap-3 md:grid-cols-[180px_1fr_auto_auto]">
            <FormField label="Entidad">
              <Select value={entityType} onChange={(event) => setEntityType(event.target.value)}>
                <option value="portfolio">Cartera</option>
                <option value="instrument">Instrumento</option>
              </Select>
            </FormField>
            <FormField label="ID">
              <input
                className="min-h-10 rounded-md border border-line bg-canvas px-3"
                value={entityId}
                onChange={(event) => setEntityId(event.target.value)}
              />
            </FormField>
            <Button
              onClick={() =>
                createJob.mutate({
                  entity_type: entityType,
                  entity_id: entityId,
                  job_type: "manual_review",
                })
              }
            >
              <FileJson size={17} /> Crear job
            </Button>
            <Button onClick={() => prepareBatch.mutate()}>
              <RefreshCw size={17} /> Batch diario
            </Button>
          </div>
        </Card>
      </Section>
      <Section title="Cola generativa">
        <Card>
          <DataTable
            rows={rows.map((row) => ({
              id: row.id,
              entidad: `${row.entity_type}:${row.entity_id}`,
              prompt: row.prompt_id,
              estado: row.status,
              schema: row.schema_id,
              fecha: row.created_at,
            }))}
          />
        </Card>
      </Section>
      <Section title="Prompt y respuesta">
        <div className="grid gap-4 xl:grid-cols-2">
          <Card>
            <div className="mb-3 flex items-center justify-between gap-3">
              <h3 className="text-lg font-bold">Prompt JSON estricto</h3>
              <Button onClick={copyPrompt}>
                <Clipboard size={17} /> Copiar
              </Button>
            </div>
            <pre className="max-h-[420px] overflow-auto rounded-md border border-line bg-canvas p-3 text-xs leading-5">
              {prompt}
            </pre>
          </Card>
          <Card>
            <h3 className="text-lg font-bold">Pegar respuesta JSON</h3>
            <textarea
              className="mt-3 min-h-[220px] w-full rounded-md border border-line bg-canvas p-3 text-sm"
              value={response}
              onChange={(event) => setResponse(event.target.value)}
            />
            <div className="mt-3 flex flex-wrap gap-2">
              <Button onClick={() => validate.mutate()} disabled={!selectedJob}>
                Validar
              </Button>
              <Button onClick={() => repair.mutate()} disabled={!selectedJob}>
                Reparar
              </Button>
              <Button onClick={() => importResponse.mutate()} disabled={!selectedJob}>
                Importar
              </Button>
            </div>
            <pre className="mt-3 max-h-[180px] overflow-auto rounded-md bg-canvas p-3 text-xs">
              {JSON.stringify(
                validate.data?.data ?? repair.data?.data ?? importResponse.data?.data ?? {},
                null,
                2,
              )}
            </pre>
          </Card>
        </div>
      </Section>
      <Section title="Histórico generativo">
        <Card>
          <DataTable
            rows={historyRows.map((row) => ({
              fecha: row.generated_at,
              entidad: `${row.entity_type}:${row.entity_id}`,
              schema: row.schema_id,
              confianza: row.confidence,
              reparada: row.was_repaired,
              tipo: row.data_kind,
            }))}
          />
        </Card>
      </Section>
    </div>
  );
}
