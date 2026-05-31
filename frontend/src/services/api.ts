import type { DashboardData } from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api/v1";

export type ApiResult<T> = {
  data: T | null;
  status: "ok" | "warning" | "error";
  source: "backend" | "cache" | "mock" | "none";
  dataKind: "observed" | "cached" | "estimated" | "mock" | "simulation" | "generative_inference";
  error?: string;
  warnings?: string[];
};

async function request<T>(path: string, init?: RequestInit): Promise<ApiResult<T>> {
  try {
    const response = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      ...init,
    });
    if (!response.ok) {
      return {
        data: null,
        status: "error",
        source: "none",
        dataKind: "observed",
        error: `Request failed: ${response.status}`,
      };
    }
    return {
      data: (await response.json()) as T,
      status: "ok",
      source: "backend",
      dataKind: "observed",
    };
  } catch (error) {
    return {
      data: null,
      status: "error",
      source: "none",
      dataKind: "observed",
      error: error instanceof Error ? error.message : "Network error",
    };
  }
}

function jsonPost(payload: Record<string, unknown>): RequestInit {
  return { method: "POST", body: JSON.stringify(payload) };
}

function jsonPatch(payload: Record<string, unknown>): RequestInit {
  return { method: "PATCH", body: JSON.stringify(payload) };
}

export const api = {
  dashboard: () => request<DashboardData>("/dashboard"),
  portfolio: () => request<Record<string, unknown>>("/portfolio"),
  portfolioTransactions: () => request<Array<Record<string, unknown>>>("/portfolio/transactions"),
  createPortfolioTransaction: (payload: Record<string, unknown>) =>
    request<Record<string, unknown>>("/portfolio/transactions", jsonPost(payload)),
  updatePortfolioTransaction: (id: string, payload: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/portfolio/transactions/${id}`, jsonPatch(payload)),
  deletePortfolioTransaction: (id: string) =>
    request<Record<string, unknown>>(`/portfolio/transactions/${id}`, { method: "DELETE" }),
  portfolioHistory: () => request<Record<string, unknown>>("/portfolio/history"),
  portfolioAnnual: () => request<Record<string, unknown>>("/portfolio/annual"),
  portfolioMonthly: () => request<Record<string, unknown>>("/portfolio/monthly"),
  simulatedPortfolio: () => request<Record<string, unknown>>("/simulated-portfolio"),
  simulatedTransactions: () =>
    request<Array<Record<string, unknown>>>("/simulated-portfolio/transactions"),
  createSimulatedTransaction: (payload: Record<string, unknown>) =>
    request<Record<string, unknown>>("/simulated-portfolio/transactions", jsonPost(payload)),
  dividends: () => request<Array<Record<string, unknown>>>("/dividends/opportunities"),
  taxRelevantEvents: () => request<Record<string, unknown>>("/tax/relevant-events"),
  taxRules: () => request<Array<Record<string, unknown>>>("/tax/rules"),
  forecasting: (ticker = "MSFT") =>
    request<Record<string, unknown>>(`/forecasting/instruments/${ticker}`),
  portfolioForecast: () => request<Record<string, unknown>>("/forecasting/portfolio"),
  quality: () => request<Record<string, unknown>>("/data-quality"),
  screener: () => request<Record<string, unknown>>("/screener"),
  watchlists: () => request<Array<Record<string, unknown>>>("/watchlists"),
  createWatchlist: (payload: Record<string, unknown>) =>
    request<Record<string, unknown>>("/watchlists", jsonPost(payload)),
  addWatchlistItem: (watchlistId: string, payload: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/watchlists/${watchlistId}/items`, jsonPost(payload)),
  journal: () => request<Array<Record<string, unknown>>>("/journal"),
  createJournal: (payload: Record<string, unknown>) =>
    request<Record<string, unknown>>("/journal", jsonPost(payload)),
  instruments: () => request<Array<Record<string, unknown>>>("/instruments"),
  instrument: (ticker = "MSFT") => request<Record<string, unknown>>(`/instruments/${ticker}`),
  alerts: () => request<Array<Record<string, unknown>>>("/alerts"),
  news: () => request<Array<Record<string, unknown>>>("/news"),
  portfolioNews: () => request<Array<Record<string, unknown>>>("/news/portfolio"),
  markets: () => request<Array<Record<string, unknown>>>("/markets"),
  settings: () => request<Record<string, unknown>>("/settings"),
  saveSettings: (payload: Record<string, unknown>) =>
    request<Record<string, unknown>>("/settings", jsonPost(payload)),
  universes: () => request<Array<Record<string, unknown>>>("/universes"),
  ingestionJobs: () => request<Array<Record<string, unknown>>>("/ingestion/jobs"),
  syncMarkets: () =>
    request<Record<string, unknown>>("/ingestion/sync-default-universes", jsonPost({})),
  syncFx: () => request<Record<string, unknown>>("/ingestion/sync-fx", jsonPost({})),
  syncNews: () => request<Record<string, unknown>>("/ingestion/sync-news", jsonPost({})),
  syncPortfolio: () => request<Record<string, unknown>>("/ingestion/sync-portfolio", jsonPost({})),
  runDailyClose: () => request<Record<string, unknown>>("/ingestion/run-daily-close", jsonPost({})),
  syncTicker: (ticker: string) =>
    request<Record<string, unknown>>("/ingestion/sync-ticker", jsonPost({ ticker })),
  generativePrompts: () => request<Array<Record<string, unknown>>>("/generative/prompts"),
  generativeJobs: () => request<Array<Record<string, unknown>>>("/generative/jobs"),
  createGenerativeJob: (payload: Record<string, unknown>) =>
    request<Record<string, unknown>>("/generative/jobs", jsonPost(payload)),
  validateGenerativeResponse: (jobId: string, response: string) =>
    request<Record<string, unknown>>(
      `/generative/jobs/${jobId}/validate-response`,
      jsonPost({ response }),
    ),
  repairGenerativeResponse: (jobId: string, response: string) =>
    request<Record<string, unknown>>(
      `/generative/jobs/${jobId}/repair-json`,
      jsonPost({ response }),
    ),
  importGenerativeResponse: (jobId: string, response: string) =>
    request<Record<string, unknown>>(
      `/generative/jobs/${jobId}/import-response`,
      jsonPost({ response }),
    ),
  prepareDailyGenerativeContext: () =>
    request<Array<Record<string, unknown>>>(
      "/generative/batch/prepare-daily-context",
      jsonPost({}),
    ),
  generativeHistory: () => request<Array<Record<string, unknown>>>("/generative/history"),
};
