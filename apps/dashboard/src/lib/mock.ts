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

const CITED_URL = "https://cited.md/theta-desk/2026-06-12-wheel-sheet";
const TOTAL_DURATION_MS = 12_000;

const stageTimeline: Array<{
  key: StageKey;
  durationMs: number;
  detail: string;
}> = [
  { key: "ingest", durationMs: 3_000, detail: "10/10 chains fetched" },
  { key: "screen", durationMs: 2_000, detail: "8 candidates pass 5 factor gates" },
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
    ticker: "NVDA",
    expiry: "2026-07-17",
    strike: 165,
    side: "csp",
    bid: 3.85,
    spot: 178.2,
    premium_yield_ann: 0.247,
    iv: 0.52,
    iv_pct: 0.81,
    delta_est: -0.27,
    open_interest: 14211,
    earnings_ok: true,
    next_earnings: "2026-08-26",
    score: 91.4
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "AMD",
    expiry: "2026-07-17",
    strike: 145,
    side: "csp",
    bid: 3.1,
    spot: 156.4,
    premium_yield_ann: 0.221,
    iv: 0.49,
    iv_pct: 0.74,
    delta_est: -0.3,
    open_interest: 9834,
    earnings_ok: true,
    next_earnings: "2026-08-04",
    score: 87.8
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "PLTR",
    expiry: "2026-07-17",
    strike: 122,
    side: "csp",
    bid: 3.45,
    spot: 134.6,
    premium_yield_ann: 0.292,
    iv: 0.58,
    iv_pct: 0.88,
    delta_est: -0.32,
    open_interest: 18762,
    earnings_ok: true,
    next_earnings: "2026-08-03",
    score: 85.9
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "MSFT",
    expiry: "2026-07-17",
    strike: 485,
    side: "csp",
    bid: 5.65,
    spot: 511.8,
    premium_yield_ann: 0.121,
    iv: 0.25,
    iv_pct: 0.42,
    delta_est: -0.22,
    open_interest: 6220,
    earnings_ok: true,
    next_earnings: "2026-07-28",
    score: 82.6
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "AAPL",
    expiry: "2026-07-17",
    strike: 190,
    side: "csp",
    bid: 2.38,
    spot: 202.3,
    premium_yield_ann: 0.129,
    iv: 0.28,
    iv_pct: 0.47,
    delta_est: -0.24,
    open_interest: 11204,
    earnings_ok: true,
    next_earnings: "2026-07-30",
    score: 80.2
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "META",
    expiry: "2026-07-17",
    strike: 665,
    side: "csp",
    bid: 10.4,
    spot: 701.2,
    premium_yield_ann: 0.162,
    iv: 0.33,
    iv_pct: 0.61,
    delta_est: -0.25,
    open_interest: 5488,
    earnings_ok: false,
    next_earnings: "2026-07-16",
    score: 73.5
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "TSLA",
    expiry: "2026-07-17",
    strike: 295,
    side: "csp",
    bid: 7.85,
    spot: 318.7,
    premium_yield_ann: 0.274,
    iv: 0.63,
    iv_pct: 0.84,
    delta_est: -0.34,
    open_interest: 20118,
    earnings_ok: true,
    next_earnings: "2026-07-22",
    score: 72.1
  },
  {
    run_id: MOCK_RUN_ID,
    ticker: "GOOGL",
    expiry: "2026-07-17",
    strike: 175,
    side: "cc",
    bid: 2.1,
    spot: 169.4,
    premium_yield_ann: 0.143,
    iv: 0.3,
    iv_pct: 0.55,
    delta_est: 0.26,
    open_interest: 7036,
    earnings_ok: true,
    next_earnings: "2026-07-24",
    score: 69.7
  }
];

const baseAnalyses: Brief["analyses"] = [
  {
    ticker: "NVDA",
    analysis:
      "NVDA screens as the highest-quality cash-secured-put candidate because the $165 strike sits roughly 7.4% below spot while still paying 24.7% annualized. Open interest is deep enough for a one-lot demo order, and the post-expiry earnings date keeps event risk outside the holding window.",
    citations: [
      "https://www.nasdaq.com/market-activity/stocks/nvda/option-chain",
      "https://www.sec.gov/ixviewer/doc/action?doc=/Archives/edgar/data/1045810/latest"
    ]
  },
  {
    ticker: "AMD",
    analysis:
      "AMD offers a similar semiconductor volatility premium with less nominal collateral than mega-cap peers. The screen favors the $145 put because IV percentile is elevated without forcing the strike inside the expected move.",
    citations: [
      "https://www.nasdaq.com/market-activity/stocks/amd/option-chain",
      "https://ir.amd.com/financial-information/sec-filings"
    ]
  },
  {
    ticker: "PLTR",
    analysis:
      "PLTR has the richest annualized yield in the sheet, but the premium is compensation for a higher-beta name. Theta Desk keeps it below NVDA because the drawdown history and 0.88 IV percentile imply a wider risk band.",
    citations: [
      "https://www.nasdaq.com/market-activity/stocks/pltr/option-chain",
      "https://investors.palantir.com/financials/sec-filings/default.aspx"
    ]
  },
  {
    ticker: "MSFT",
    analysis:
      "MSFT is the defensive ballast in the list: lower premium, lower IV percentile, and stronger mega-cap liquidity. The $485 strike yields only 12.1% annualized, but it is attractive for accounts prioritizing assignment quality over headline yield.",
    citations: [
      "https://www.nasdaq.com/market-activity/stocks/msft/option-chain",
      "https://www.microsoft.com/en-us/investor/sec-filings.aspx"
    ]
  },
  {
    ticker: "AAPL",
    analysis:
      "AAPL passes the wheel screen on liquidity and assignment quality, with a muted 12.9% annualized premium. The setup is a lower-volatility reserve candidate rather than the primary trade for accounts seeking maximum income.",
    citations: [
      "https://www.nasdaq.com/market-activity/stocks/aapl/option-chain",
      "https://investor.apple.com/sec-filings/default.aspx"
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
      "Eight option-income candidates survived liquidity, yield, IV percentile, earnings, and assignment-quality gates. NVDA leads on risk-adjusted premium, while MSFT and AAPL provide lower-volatility alternates for conservative accounts.",
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
