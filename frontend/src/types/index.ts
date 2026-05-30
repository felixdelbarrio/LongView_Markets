export type Lineage = {
  source: string;
  data_kind: "mock" | "observed" | "simulation" | "forecast";
  confidence: number;
  as_of?: string;
};

export type DashboardData = {
  hero: {
    portfolio_value: number;
    total_return: number;
    ytd_return: number;
    aggregate_risk: string;
    upcoming_dividends: number;
    critical_alerts: number;
    data_status: string;
  };
  market_pulse: Array<{
    market: string;
    change: number;
    members: number;
    leaders: Array<{ ticker: string; change: number }>;
  }>;
  opportunities: Array<Record<string, string | number>>;
  risk: { top5_concentration: number; positions: Array<Record<string, string | number>> };
  discipline: {
    journal_reviews: Array<Record<string, unknown>>;
    watchlists: Array<Record<string, unknown>>;
    simulations: Array<Record<string, unknown>>;
  };
  copilot: {
    questions: string[];
    tickers_to_review: string[];
    explained_alerts: Array<Record<string, unknown>>;
  };
  narrative: string;
  lineage: Lineage;
};
