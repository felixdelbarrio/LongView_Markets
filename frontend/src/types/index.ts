export type Lineage = {
  source: string;
  data_kind: "empty" | "observed" | "cached" | "simulation" | "forecast" | "generative_inference";
  confidence: number;
  as_of?: string;
};

export type DashboardData = {
  empty_portfolio: boolean;
  hero: {
    portfolio_value: number;
    total_return: number;
    ytd_return: number;
    aggregate_risk: string;
    upcoming_dividends: number;
    critical_alerts: number;
    data_status: string;
  };
  market_pulse_status: string;
  market_pulse: Array<Record<string, string | number | null | undefined>>;
  opportunities: Array<Record<string, string | number>>;
  risk: Record<string, unknown> & {
    top5_concentration?: number;
    positions?: Array<Record<string, string | number>>;
  };
  discipline: {
    journal_reviews: Array<Record<string, unknown>>;
    watchlists: Array<Record<string, unknown>>;
    simulations: Array<Record<string, unknown>>;
  };
  copilot?: {
    questions: string[];
    tickers_to_review: string[];
    explained_alerts: Array<Record<string, unknown>>;
  };
  proactive_intelligence?: {
    summary: string;
    questions: string[];
    status: string;
  };
  generative_context?: Record<string, unknown>;
  narrative: string;
  lineage: Lineage;
};
