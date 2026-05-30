import type { DashboardData } from "../types";

export const demoDashboard: DashboardData = {
  hero: {
    portfolio_value: 128420,
    total_return: 18.4,
    ytd_return: 9.8,
    aggregate_risk: "medium",
    upcoming_dividends: 42,
    critical_alerts: 1,
    data_status: "ready",
  },
  market_pulse: [
    { market: "NASDAQ", change: 0.74, members: 9, leaders: [{ ticker: "NVDA", change: 2.1 }] },
    { market: "BME", change: 0.28, members: 5, leaders: [{ ticker: "BBVA.MC", change: 1.2 }] },
    { market: "XETRA", change: -0.12, members: 2, leaders: [{ ticker: "SAP.DE", change: 0.4 }] },
  ],
  opportunities: [
    {
      ticker: "MSFT",
      name: "Microsoft",
      cagr: 14.2,
      volatility: 22.1,
      confidence: 0.91,
      dividend_yield: 0.8,
    },
    {
      ticker: "BBVA.MC",
      name: "BBVA",
      cagr: 8.9,
      volatility: 24.6,
      confidence: 0.86,
      dividend_yield: 5.2,
    },
    {
      ticker: "ASML.AS",
      name: "ASML",
      cagr: 16.1,
      volatility: 27.8,
      confidence: 0.88,
      dividend_yield: 1.1,
    },
  ],
  risk: {
    top5_concentration: 72,
    positions: [
      { ticker: "MSFT", weight: 24, sector: "Technology", market_value: 40200 },
      { ticker: "NVDA", weight: 20, sector: "Technology", market_value: 33500 },
      { ticker: "KO", weight: 11, sector: "Consumer Staples", market_value: 14200 },
    ],
  },
  discipline: {
    journal_reviews: [{ ticker: "MSFT" }],
    watchlists: [{ name: "Dividendos" }],
    simulations: [{ ticker: "NVO" }],
  },
  copilot: {
    questions: ["What changed?", "What risk matters?", "Which thesis needs review?"],
    tickers_to_review: ["NVDA", "BBVA.MC", "MSFT"],
    explained_alerts: [{ title: "High volatility", severity: "high" }],
  },
  narrative: "Hoy LongView ha detectado 5 eventos relevantes para tu cartera.",
  lineage: { source: "frontend fallback", data_kind: "mock", confidence: 0.7 },
};

export const demoList = [
  { ticker: "MSFT", name: "Microsoft", sector: "Technology", country: "US", confidence: 0.9 },
  { ticker: "BBVA.MC", name: "BBVA", sector: "Financials", country: "ES", confidence: 0.84 },
  { ticker: "ASML.AS", name: "ASML", sector: "Technology", country: "NL", confidence: 0.88 },
];
