import { useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { CloudDownload, DatabaseZap, Moon, Search, Settings, SunMedium, X } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { BrandMark } from "./BrandMark";
import { navItems } from "../../app/navigation";
import { api } from "../../services/api";
import { Button } from "../../design-system/components/Button";
import { DataTable } from "../../design-system/components/DataTable";
import { usePreferences } from "../../stores/preferences";

export function AppShell() {
  const { t } = useTranslation();
  const { theme, setTheme } = usePreferences();
  const [syncOpen, setSyncOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const jobs = useQuery({
    queryKey: ["ingestion-jobs", syncOpen],
    queryFn: api.ingestionJobs,
    enabled: syncOpen,
  });
  const settings = useQuery({
    queryKey: ["settings", settingsOpen],
    queryFn: api.settings,
    enabled: settingsOpen,
  });
  const syncMarkets = useMutation({ mutationFn: api.syncMarkets });
  const syncFx = useMutation({ mutationFn: api.syncFx });
  const syncNews = useMutation({ mutationFn: api.syncNews });
  const syncPortfolio = useMutation({ mutationFn: api.syncPortfolio });
  const dailyClose = useMutation({ mutationFn: api.runDailyClose });
  const syncRows = jobs.data?.data ?? [];
  const settingsRows = Object.entries(settings.data?.data ?? {}).map(([key, value]) => ({
    key,
    value,
  }));
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[280px_1fr]">
      <aside className="border-line/80 bg-panel/95 p-4 lg:sticky lg:top-0 lg:h-screen lg:border-r">
        <BrandMark />
        <nav className="mt-6 grid grid-cols-2 gap-1 lg:grid-cols-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex min-h-10 items-center gap-3 rounded-md px-3 text-sm font-semibold transition ${isActive ? "bg-accent text-white" : "text-muted hover:bg-canvas hover:text-text"}`
              }
            >
              <item.icon size={17} />
              <span>{t(item.key)}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
      <main>
        <header className="sticky top-0 z-10 flex flex-wrap items-center justify-between gap-3 border-b border-line/80 bg-canvas/85 px-5 py-4 backdrop-blur">
          <div className="flex min-w-0 flex-1 items-center gap-3 rounded-md border border-line bg-panel px-3 py-2 text-muted">
            <Search size={17} />
            <input
              aria-label="Global search"
              className="min-w-0 flex-1 bg-transparent outline-none"
              placeholder="MSFT, dividendos, drawdown..."
            />
          </div>
          <Button aria-label="Sincronización global" onClick={() => setSyncOpen(true)}>
            <CloudDownload size={17} />
          </Button>
          <Button aria-label="Configuración global" onClick={() => setSettingsOpen(true)}>
            <Settings size={17} />
          </Button>
          <Button
            aria-label="Toggle theme"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? <SunMedium size={17} /> : <Moon size={17} />}
          </Button>
        </header>
        <div className="mx-auto max-w-[1500px] px-5 py-6">
          <Outlet />
        </div>
      </main>
      {syncOpen ? (
        <div className="fixed inset-0 z-30 bg-canvas/80 p-4 backdrop-blur">
          <section className="mx-auto max-h-[92vh] max-w-5xl overflow-auto rounded-lg border border-line bg-panel p-5 shadow-glow">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-normal text-accent">
                  Sincronización global
                </p>
                <h2 className="mt-2 text-2xl font-black">Progreso de ingesta</h2>
              </div>
              <Button aria-label="Cerrar sincronización" onClick={() => setSyncOpen(false)}>
                <X size={17} />
              </Button>
            </div>
            <div className="mt-5 grid gap-2 md:grid-cols-3">
              <Button onClick={() => syncMarkets.mutate()}>
                <DatabaseZap size={17} /> Sincronizar mercados
              </Button>
              <Button onClick={() => syncFx.mutate()}>Sincronizar divisas</Button>
              <Button onClick={() => syncNews.mutate()}>Sincronizar noticias</Button>
              <Button onClick={() => syncPortfolio.mutate()}>Sincronizar cartera</Button>
              <Button onClick={() => dailyClose.mutate()}>Ejecutar daily close</Button>
              <Button onClick={() => syncMarkets.mutate()}>Preparar inteligencia proactiva</Button>
            </div>
            <div className="mt-5">
              <DataTable
                rows={syncRows.map((row) => ({
                  proveedor: row.provider,
                  estado: row.status,
                  tipo: row.type,
                  ticker: row.ticker,
                  universo: row.universe_id,
                  precios: row.rows_prices,
                  dividendos: row.rows_dividends,
                  noticias: row.rows_news,
                  errores: Array.isArray(row.errors) ? row.errors.length : 0,
                  warnings: Array.isArray(row.warnings) ? row.warnings.length : 0,
                  actualizacion: row.finished_at ?? row.started_at,
                }))}
              />
            </div>
          </section>
        </div>
      ) : null}
      {settingsOpen ? (
        <div className="fixed inset-0 z-30 bg-canvas/80 p-4 backdrop-blur">
          <section className="mx-auto max-h-[92vh] max-w-5xl overflow-auto rounded-lg border border-line bg-panel p-5 shadow-glow">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-normal text-accent">
                  Configuración global
                </p>
                <h2 className="mt-2 text-2xl font-black">Proveedores y privacidad</h2>
              </div>
              <Button aria-label="Cerrar configuración" onClick={() => setSettingsOpen(false)}>
                <X size={17} />
              </Button>
            </div>
            <div className="mt-5 grid gap-3 md:grid-cols-3">
              {[
                "General",
                "Proveedores",
                "Mercados e ingesta",
                "Cartera",
                "Divisas",
                "Noticias",
                "Inteligencia generativa",
                "Fiscalidad",
                "Privacidad",
                "Calidad de datos",
              ].map((item) => (
                <div
                  key={item}
                  className="rounded-md border border-line bg-canvas p-3 text-sm font-bold"
                >
                  {item}
                </div>
              ))}
            </div>
            <div className="mt-5">
              <DataTable rows={settingsRows} />
            </div>
          </section>
        </div>
      ) : null}
    </div>
  );
}
