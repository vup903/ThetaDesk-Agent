export type Stage = {
  status: "pending" | "running" | "done" | "failed";
  detail?: string;
};

export type Run = {
  run_id: string;
  started_at: string;
  mode: "live" | "replay";
  status: "running" | "done" | "failed";
  stages: {
    ingest: Stage;
    screen: Stage;
    analyze: Stage;
    publish: Stage;
  };
  universe_size?: number;
  brief_url?: string | null;
};

export type Candidate = {
  run_id: string;
  ticker: string;
  expiry: string;
  strike: number;
  side: "csp" | "cc";
  bid: number;
  spot: number;
  premium_yield_ann: number;
  iv: number;
  iv_pct: number;
  delta_est?: number | null;
  open_interest: number;
  earnings_ok: boolean;
  next_earnings?: string | null;
  score: number;
};

export type Brief = {
  run_id: string;
  date: string;
  title: string;
  summary?: string;
  candidates: Candidate[];
  analyses: { ticker: string; analysis: string; citations: string[] }[];
  status: "draft" | "published" | "failed";
  cited_url?: string | null;
  price_usd: number;
};
