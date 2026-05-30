import { demoDashboard, demoList } from "./demoFallback";
import type { DashboardData } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

async function getJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE}${path}`);
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export const api = {
  dashboard: () => getJson<DashboardData>("/dashboard", demoDashboard),
  portfolio: () => getJson<Record<string, unknown>>("/portfolio", demoDashboard.risk),
  simulatedPortfolio: () =>
    getJson<Record<string, unknown>>("/simulated-portfolio", demoDashboard.risk),
  dividends: () => getJson<Array<Record<string, unknown>>>("/dividends/opportunities", demoList),
  taxRules: () => getJson<Array<Record<string, unknown>>>("/tax/rules", demoList),
  forecasting: (ticker = "MSFT") =>
    getJson<Record<string, unknown>>(`/forecasting/${ticker}`, { scenarios: [] }),
  quality: () =>
    getJson<Record<string, unknown>>("/data-quality", { global_score: 91, issues: [] }),
  screener: () => getJson<Record<string, unknown>>("/screener", { results: demoList, presets: [] }),
  watchlists: () => getJson<Array<Record<string, unknown>>>("/watchlists", demoList),
  journal: () => getJson<Array<Record<string, unknown>>>("/journal", demoList),
  playbooks: () => getJson<Array<Record<string, unknown>>>("/playbooks", demoList),
  copilot: (ticker = "MSFT") =>
    getJson<Record<string, unknown>>(`/copilot/context/${ticker}`, { copyable_context: "{}" }),
  instruments: () => getJson<Array<Record<string, unknown>>>("/instruments", demoList),
  instrument: (ticker = "MSFT") =>
    getJson<Record<string, unknown>>(`/instruments/${ticker}`, { instrument: demoList[0] }),
  alerts: () => getJson<Array<Record<string, unknown>>>("/alerts", demoList),
  news: () => getJson<Array<Record<string, unknown>>>("/news", demoList),
  markets: () => getJson<Array<Record<string, unknown>>>("/markets", demoList),
  settings: () =>
    getJson<Record<string, unknown>>("/settings", { language: "es", theme: "system" }),
};
