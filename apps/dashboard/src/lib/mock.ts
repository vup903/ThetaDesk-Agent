import type { Brief, Candidate, Run, Stage } from "./types";

type StageKey = keyof Run["stages"];

type ControllerState = {
  runId: string;
  startedAtMs: number;
  startedAtIso: string;
  mode: Run["mode"];
  active: boolean;
};

type MockRunController = {
  start: (mode: Run["mode"]) => Run;
  getRun: () => Run;
  subscribe: (listener: (run: Run) => void) => () => void;
};

const CITED_URL = "https://cited.md/article/52408c9d-a9a4-43f1-992a-70f3f44d52f1";
const TOTAL_DURATION_MS = 12_000;

const stageTimeline: Array<{
  key: StageKey;
  durationMs: number;
  detail: string;
}> = [
  { key: "ingest", durationMs: 3_000, detail: "10/10 chains fetched" },
  { key: "screen", durationMs: 2_000, detail: "10 candidates pass 5 factor gates" },
  { key: "analyze", durationMs: 4_000, detail: "Claude writing 5 risk briefs..." },
  { key: "publish", durationMs: 3_000, detail: "Live on cited.md - $0.01 paywall" }
];

export const universe = [
  "AAPL",
  "MSFT",
  "NVDA",
  "AMD",
  "TSLA",
  "GOOGL",
  "AMZN",
  "META",
  "PLTR",
  "SOFI"
] as const;

const MOCK_RUN_ID = "theta-2026-06-12-demo";

const baseCandidates: Candidate[] = [
  {
    run_id: MOCK_RUN_ID,
    ticker: "SOFI",
    expiry: "2026-06-26",
    strike: 16,
    side: "csp",
    bid: 0.47,
    spot: 16.58,
    premium_yield_ann: 0.7658,
    iv: 0.5527,
    iv_pct: 0.894,
    delta_est: null,
    open_interest: 3272,
    earnings_ok: true,
    next_earnings: "2026-07-28",
    score: 86.7
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "AMD",
    expiry: "2026-06-26",
    strike: 495,
    side: "csp",
    bid: 20.9,
    spot: 511.57,
    premium_yield_ann: 1.1008,
    iv: 0.7166,
    iv_pct: 0.87,
    delta_est: null,
    open_interest: 193,
    earnings_ok: true,
    next_earnings: "2026-08-04",
    score: 85.8
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "TSLA",
    expiry: "2026-06-26",
    strike: 392.5,
    side: "csp",
    bid: 10.55,
    spot: 406.43,
    premium_yield_ann: 0.7008,
    iv: 0.5172,
    iv_pct: 1,
    delta_est: null,
    open_interest: 190,
    earnings_ok: true,
    next_earnings: "2026-07-22",
    score: 78.2
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "PLTR",
    expiry: "2026-06-26",
    strike: 124,
    side: "csp",
    bid: 2.78,
    spot: 127.99,
    premium_yield_ann: 0.5845,
    iv: 0.4602,
    iv_pct: 0.856,
    delta_est: null,
    open_interest: 493,
    earnings_ok: true,
    next_earnings: "2026-08-03",
    score: 67.6
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "NVDA",
    expiry: "2026-06-26",
    strike: 197.5,
    side: "csp",
    bid: 3.1,
    spot: 205.19,
    premium_yield_ann: 0.4092,
    iv: 0.3879,
    iv_pct: 0.998,
    delta_est: null,
    open_interest: 430,
    earnings_ok: true,
    next_earnings: "2026-08-26",
    score: 66.3
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "AMZN",
    expiry: "2026-06-26",
    strike: 230,
    side: "csp",
    bid: 2.84,
    spot: 238.55,
    premium_yield_ann: 0.3219,
    iv: 0.3347,
    iv_pct: 0.928,
    delta_est: null,
    open_interest: 1143,
    earnings_ok: true,
    next_earnings: "2026-07-30",
    score: 59.2
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "META",
    expiry: "2026-06-26",
    strike: 545,
    side: "csp",
    bid: 6.55,
    spot: 566.98,
    premium_yield_ann: 0.3133,
    iv: 0.3494,
    iv_pct: 0.9001,
    delta_est: null,
    open_interest: 398,
    earnings_ok: true,
    next_earnings: "2026-07-29",
    score: 50.6
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "MSFT",
    expiry: "2026-06-26",
    strike: 375,
    side: "csp",
    bid: 3.6,
    spot: 390.74,
    premium_yield_ann: 0.2503,
    iv: 0.3176,
    iv_pct: 0.94,
    delta_est: null,
    open_interest: 904,
    earnings_ok: true,
    next_earnings: "2026-07-29",
    score: 46.9
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "GOOGL",
    expiry: "2026-07-02",
    strike: 345,
    side: "csp",
    bid: 4.3,
    spot: 359.68,
    premium_yield_ann: 0.2275,
    iv: 0.3132,
    iv_pct: 0.914,
    delta_est: null,
    open_interest: 1248,
    earnings_ok: true,
    next_earnings: "2026-07-23",
    score: 40.6
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "AAPL",
    expiry: "2026-06-26",
    strike: 280,
    side: "csp",
    bid: 1.73,
    spot: 291.13,
    premium_yield_ann: 0.1611,
    iv: 0.2509,
    iv_pct: 0.944,
    delta_est: null,
    open_interest: 1685,
    earnings_ok: true,
    next_earnings: "2026-07-30",
    score: 36.4
  }
];

const baseAnalyses: Brief["analyses"] = [
  {
    ticker: "SOFI",
    analysis:
      "SOFI leads the current wheel sheet because the $16 put keeps collateral light while still paying 76.6% annualized over the 14-day window. IV sits near the 89th percentile, so the premium is rich relative to the stock's own trailing volatility. The main risk is assignment if fintech beta sells off with rates or broader risk sentiment.",
    citations: [
      "https://www.nasdaq.com/market-activity/stocks/sofi/option-chain",
      "https://investors.sofi.com/financials/sec-filings/default.aspx"
    ]
  },
  {
    ticker: "AMD",
    analysis:
      "AMD is the high-yield alternative: the $495 put bids $20.90, or 110.1% annualized, but it requires $49,500 of cash-secured collateral per contract. The score stays just below SOFI because liquidity is thinner and the notional risk is larger. Earnings are outside the expiry window, so the main risk is assignment after a fast semiconductor reversal.",
    citations: [
      "https://www.nasdaq.com/market-activity/stocks/amd/option-chain",
      "https://ir.amd.com/financial-information/sec-filings"
    ]
  },
  {
    ticker: "TSLA",
    analysis:
      "TSLA offers 70.1% annualized premium at the $392.50 strike, with IV at the top of its one-year range. The cushion is only a few percent below spot, so a single adverse session can turn the contract into assignment risk. Earnings are clear of expiry, but sentiment-driven moves around the Musk ecosystem remain the core hazard.",
    citations: [
      "https://www.nasdaq.com/market-activity/stocks/tsla/option-chain",
      "https://ir.tesla.com/sec-filings"
    ]
  },
  {
    ticker: "PLTR",
    analysis:
      "PLTR remains attractive on premium but carries headline and technical-risk sensitivity. The $124 put yields 58.5% annualized with IV in the upper part of its trailing range. The assignment case is less about earnings and more about whether a failed breakout keeps pressure on the stock before expiry.",
    citations: [
      "https://www.nasdaq.com/market-activity/stocks/pltr/option-chain",
      "https://investors.palantir.com/financials/sec-filings/default.aspx"
    ]
  },
  {
    ticker: "NVDA",
    analysis:
      "NVDA's $197.50 put pays 40.9% annualized and keeps earnings outside this expiry, but open interest is modest and semiconductor beta can move quickly. IV is historically stretched, which is good for premium collection and also a warning that the market expects a wide range of outcomes. The trade is useful as a liquid mega-cap reference point, not the lowest-risk idea in the sheet.",
    citations: [
      "https://www.nasdaq.com/market-activity/stocks/nvda/option-chain",
      "https://www.sec.gov/ixviewer/doc/action?doc=/Archives/edgar/data/1045810/latest"
    ]
  }
];

function clone<T>(value: T): T {
  return JSON.parse(JSON.stringify(value)) as T;
}

function emptyStages(): Run["stages"] {
  return {
    ingest: { status: "pending" },
    screen: { status: "pending" },
    analyze: { status: "pending" },
    publish: { status: "pending" }
  };
}

function buildRun(state: ControllerState, nowMs = Date.now()): Run {
  const stages = emptyStages();
  const elapsedMs = state.active ? Math.max(0, nowMs - state.startedAtMs) : TOTAL_DURATION_MS;
  let cursor = 0;

  for (const stage of stageTimeline) {
    const start = cursor;
    const end = cursor + stage.durationMs;
    const current: Stage = stages[stage.key];

    if (elapsedMs >= end) {
      current.status = "done";
      current.detail = stage.detail;
    } else if (elapsedMs >= start) {
      current.status = "running";
    }

    cursor = end;
  }

  const isDone = elapsedMs >= TOTAL_DURATION_MS;

  return {
    run_id: state.runId,
    started_at: state.startedAtIso,
    mode: state.mode,
    status: isDone ? "done" : "running",
    stages,
    universe_size: universe.length,
    brief_url: isDone ? CITED_URL : null
  };
}

export function createMockRunController(): MockRunController {
  const listeners = new Set<(run: Run) => void>();
  let timer: ReturnType<typeof setInterval> | undefined;
  let state: ControllerState = {
    runId: MOCK_RUN_ID,
    startedAtMs: Date.now() - TOTAL_DURATION_MS - 60_000,
    startedAtIso: new Date(Date.now() - TOTAL_DURATION_MS - 60_000).toISOString(),
    mode: "replay",
    active: false
  };

  const notify = () => {
    const run = buildRun(state);
    if (run.status === "done") {
      state = { ...state, active: false };
      if (timer) {
        clearInterval(timer);
        timer = undefined;
      }
    }
    listeners.forEach((listener) => listener(clone(run)));
  };

  return {
    start(mode) {
      if (timer) {
        clearInterval(timer);
      }

      const now = Date.now();
      state = {
        runId: `theta-${new Date(now).toISOString().slice(0, 10)}-${Math.floor(now / 1000)}`,
        startedAtMs: now,
        startedAtIso: new Date(now).toISOString(),
        mode,
        active: true
      };

      timer = setInterval(notify, 250);
      notify();
      return clone(buildRun(state, now));
    },

    getRun() {
      const run = buildRun(state);
      if (run.status === "done" && state.active) {
        state = { ...state, active: false };
      }
      return clone(run);
    },

    subscribe(listener) {
      listeners.add(listener);
      listener(clone(buildRun(state)));
      return () => {
        listeners.delete(listener);
      };
    }
  };
}

export const mockRunController = createMockRunController();

export function getMockCandidates(runId = mockRunController.getRun().run_id): Candidate[] {
  return clone(baseCandidates.map((candidate) => ({ ...candidate, run_id: runId })));
}

export function getMockBrief(runId = mockRunController.getRun().run_id): Brief {
  return clone({
    run_id: runId,
    date: "2026-06-12",
    title: "Theta Desk Daily Wheel Sheet - June 12, 2026",
    summary:
      "Ten option-income candidates survived liquidity, yield, IV percentile, earnings, and assignment-quality gates. SOFI leads on risk-adjusted premium and low collateral, while AMD offers the sheet's highest annualized yield.",
    candidates: getMockCandidates(runId),
    analyses: baseAnalyses,
    status: "published",
    cited_url: CITED_URL,
    price_usd: 0.01
  });
}

export function getMockBuySheet() {
  return {
    paid: true,
    tx: "0x3f8a7b19d43fc2e1",
    sheet: getMockBrief()
  };
}
