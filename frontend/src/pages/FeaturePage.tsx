import { useQuery } from "@tanstack/react-query";
import { motion } from "framer-motion";
import { Card } from "../components/ui/card";
import { DomainCards } from "../components/financial/DomainCards";
import { ConfidenceBadge, SourceBadge } from "../components/financial/Badges";
import { QualityScoreRing } from "../components/financial/QualityScoreRing";

export type FeaturePageConfig = {
  title: string;
  eyebrow: string;
  description: string;
  dataKind: "mock" | "simulation" | "forecast" | "observed";
  queryKey: string;
  queryFn: () => Promise<unknown>;
  highlights: string[];
};

function normalizeItems(data: unknown): Array<Record<string, unknown>> {
  if (Array.isArray(data)) return data as Array<Record<string, unknown>>;
  if (data && typeof data === "object") {
    const record = data as Record<string, unknown>;
    if (Array.isArray(record.results)) return record.results as Array<Record<string, unknown>>;
    if (Array.isArray(record.scenarios)) return record.scenarios as Array<Record<string, unknown>>;
    if (Array.isArray(record.issues)) return record.issues as Array<Record<string, unknown>>;
    if (Array.isArray(record.positions)) return record.positions as Array<Record<string, unknown>>;
    return Object.entries(record)
      .slice(0, 8)
      .map(([key, value]) => ({
        name: key,
        description:
          typeof value === "object" ? JSON.stringify(value).slice(0, 160) : String(value),
      }));
  }
  return [];
}

export function FeaturePage({ config }: { config: FeaturePageConfig }) {
  const { data } = useQuery({ queryKey: [config.queryKey], queryFn: config.queryFn });
  const items = normalizeItems(data);
  return (
    <div className="space-y-6">
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-lg border border-line bg-panel p-6"
      >
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-accent">
              {config.eyebrow}
            </p>
            <h1 className="mt-3 text-4xl font-black">{config.title}</h1>
            <p className="mt-3 max-w-3xl text-lg leading-8 text-muted">{config.description}</p>
          </div>
          <div className="flex items-center gap-2">
            <SourceBadge kind={config.dataKind} />
            <ConfidenceBadge value={0.84} />
          </div>
        </div>
      </motion.section>
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {config.highlights.map((highlight, index) => (
          <Card key={highlight} className="min-h-[132px]">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-muted">
              Capability {index + 1}
            </p>
            <p className="mt-3 text-lg font-bold">{highlight}</p>
          </Card>
        ))}
      </section>
      {config.queryKey === "quality" ? (
        <Card className="flex flex-wrap items-center gap-6">
          <QualityScoreRing
            score={Number((data as Record<string, unknown> | undefined)?.global_score ?? 91)}
          />
          <div>
            <h2 className="text-2xl font-bold">Semaforo de confianza</h2>
            <p className="mt-2 max-w-2xl text-muted">
              Valida faltantes, duplicados, OHLC, datos obsoletos y estado por proveedor antes de
              usar cualquier insight.
            </p>
          </div>
        </Card>
      ) : null}
      <DomainCards
        title="Datos y acciones disponibles"
        items={items.length ? items : config.highlights.map((item) => ({ name: item }))}
      />
      <Card>
        <h2 className="text-xl font-bold">Disclaimer</h2>
        <p className="mt-2 text-sm leading-6 text-muted">
          LongView Markets es una herramienta informativa y educativa. No proporciona asesoramiento
          financiero, fiscal ni legal. Las predicciones y simulaciones no garantizan resultados
          futuros.
        </p>
      </Card>
    </div>
  );
}
