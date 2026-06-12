"use client";

import { Fragment, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  ArrowUpDown,
  Bot,
  Check,
  Clock3,
  ExternalLink,
  LockKeyhole,
  Play,
  RadioTower,
  ShieldCheck,
  TriangleAlert,
  UnlockKeyhole
} from "lucide-react";
import {
  Button,
  Card,
  CardHeader,
  MiniBarChart,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
  Tag,
  TextCallout,
  ThemeProvider,
  createTheme
} from "@openuidev/react-ui";
import {
  buySheet,
  getCandidates,
  getLatestBrief,
  getLatestRun,
  isUsingMock,
  startRun
} from "@/lib/api";
import { openUICoreRuntime } from "@/lib/openui-core";
import type { Brief, Candidate, Run, Stage } from "@/lib/types";

type SortKey =
  | "ticker"
  | "side"
  | "strike"
  | "expiry"
  | "bid"
  | "premium_yield_ann"
  | "iv_pct"
  | "open_interest"
  | "score";

type SortState = {
  key: SortKey;
  direction: "asc" | "desc";
};

const thetaTheme = createTheme({
  background: "oklch(0.11 0.018 165 / 1)",
  foreground: "oklch(0.16 0.018 165 / 1)",
  popoverBackground: "oklch(0.18 0.018 165 / 1)",
  sunk: "oklch(0.12 0.016 165 / 1)",
  sunkDeep: "oklch(0.085 0.014 165 / 1)",
  elevated: "oklch(0.18 0.02 165 / 1)",
  elevatedStrong: "oklch(0.24 0.026 165 / 1)",
  highlight: "oklch(0.7 0.17 150 / 0.12)",
  highlightStrong: "oklch(0.78 0.18 150 / 0.2)",
  overlay: "oklch(0.08 0.01 165 / 0.72)",
  textNeutralPrimary: "oklch(0.93 0.02 150 / 1)",
  textNeutralSecondary: "oklch(0.78 0.018 150 / 0.72)",
  textNeutralTertiary: "oklch(0.78 0.018 150 / 0.42)",
  textNeutralLink: "oklch(0.82 0.14 205 / 1)",
  textSuccessPrimary: "oklch(0.82 0.18 150 / 1)",
  textAlertPrimary: "oklch(0.84 0.15 84 / 1)",
  textDangerPrimary: "oklch(0.76 0.18 24 / 1)",
  textInfoPrimary: "oklch(0.82 0.12 220 / 1)",
  interactiveAccentDefault: "oklch(0.78 0.18 150 / 1)",
  interactiveAccentHover: "oklch(0.84 0.18 150 / 1)",
  interactiveAccentPressed: "oklch(0.72 0.17 150 / 1)",
  borderDefault: "oklch(0.72 0.04 150 / 0.14)",
  borderInteractive: "oklch(0.72 0.04 150 / 0.2)",
  borderInteractiveEmphasis: "oklch(0.82 0.16 150 / 0.48)",
  borderInteractiveSelected: "oklch(0.82 0.18 150 / 1)",
  borderSuccess: "oklch(0.72 0.18 150 / 0.22)",
  borderSuccessEmphasis: "oklch(0.82 0.18 150 / 1)",
  borderAlert: "oklch(0.84 0.15 84 / 0.2)",
  borderAlertEmphasis: "oklch(0.84 0.15 84 / 1)",
  defaultChartPalette: [
    "oklch(0.78 0.18 150 / 1)",
    "oklch(0.84 0.15 84 / 1)",
    "oklch(0.82 0.12 220 / 1)"
  ],
  barChartPalette: ["oklch(0.78 0.18 150 / 1)", "oklch(0.84 0.15 84 / 1)"],
  radialChartPalette: ["oklch(0.78 0.18 150 / 1)", "oklch(0.84 0.15 84 / 1)"],
  radiusM: "8px",
  radiusL: "8px",
  radiusXl: "8px",
  fontBody:
    "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
  fontHeading:
    "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
  fontNumbers:
    "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace",
  fontCode:
    "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, monospace"
});

const stageDefs: Array<{ key: keyof Run["stages"]; label: string }> = [
  { key: "ingest", label: "Ingest" },
  { key: "screen", label: "Screen" },
  { key: "analyze", label: "Analyze" },
  { key: "publish", label: "Publish" }
];

const sponsorChips = ["Airbyte", "ClickHouse", "Senso", "cited.md", "x402", "OpenUI", "Render"];

function formatCurrency(value: number) {
  return `$${value.toFixed(2)}`;
}

function formatPercent(value: number, digits = 1) {
  return `${(value * 100).toFixed(digits)}%`;
}

function formatExpiry(date: string) {
  const [, month, day] = date.split("-");
  return `${month}/${day}`;
}

function formatTimestamp(value?: string) {
  if (!value) {
    return "--";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    timeZoneName: "short"
  }).format(new Date(value));
}

function compareCandidates(a: Candidate, b: Candidate, sort: SortState) {
  const left = a[sort.key];
  const right = b[sort.key];
  const modifier = sort.direction === "asc" ? 1 : -1;

  if (typeof left === "number" && typeof right === "number") {
    return (left - right) * modifier;
  }

  return String(left).localeCompare(String(right)) * modifier;
}

function useEasternClock() {
  const [clock, setClock] = useState("--:--:-- ET");

  useEffect(() => {
    const format = () => {
      setClock(
        `${new Intl.DateTimeFormat("en-US", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false,
          timeZone: "America/New_York"
        }).format(new Date())} ET`
      );
    };

    format();
    const interval = setInterval(format, 1_000);
    return () => clearInterval(interval);
  }, []);

  return clock;
}

export function DashboardClient() {
  const [run, setRun] = useState<Run | null>(null);
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [brief, setBrief] = useState<Brief | null>(null);
  const [tableReady, setTableReady] = useState(false);
  const [briefReady, setBriefReady] = useState(false);
  const [unlocked, setUnlocked] = useState(false);
  const [mocking, setMocking] = useState(isUsingMock());

  const refreshRun = useCallback(async () => {
    const latestRun = await getLatestRun();
    setRun(latestRun);
    setMocking(isUsingMock());
    return latestRun;
  }, []);

  const loadCandidates = useCallback(async () => {
    const latestCandidates = await getCandidates();
    setCandidates(latestCandidates);
    setTableReady(true);
    setMocking(isUsingMock());
  }, []);

  const loadBrief = useCallback(async () => {
    const latestBrief = await getLatestBrief();
    setBrief(latestBrief);
    setBriefReady(true);
    setMocking(isUsingMock());
  }, []);

  useEffect(() => {
    let mounted = true;

    const loadInitial = async () => {
      const [latestRun, latestCandidates, latestBrief] = await Promise.all([
        getLatestRun(),
        getCandidates(),
        getLatestBrief()
      ]);

      if (!mounted) {
        return;
      }

      setRun(latestRun);
      setCandidates(latestCandidates);
      setBrief(latestBrief);
      setTableReady(latestRun.stages.screen.status === "done");
      setBriefReady(latestRun.stages.publish.status === "done");
      setMocking(isUsingMock());
    };

    void loadInitial();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (run?.status !== "running") {
      return;
    }

    const interval = setInterval(() => {
      void refreshRun();
    }, 1_500);

    return () => clearInterval(interval);
  }, [refreshRun, run?.run_id, run?.status]);

  useEffect(() => {
    if (!run) {
      return;
    }

    if (run.stages.screen.status === "done" && !tableReady) {
      void loadCandidates();
    }

    if (run.stages.publish.status === "done" && !briefReady) {
      void loadBrief();
    }
  }, [briefReady, loadBrief, loadCandidates, run, tableReady]);

  const handleStartRun = async () => {
    setUnlocked(false);
    setCandidates([]);
    setBrief(null);
    setTableReady(false);
    setBriefReady(false);

    const startedRun = await startRun("live");
    setRun(startedRun);
    setMocking(isUsingMock());
  };

  const handleBriefUnlocked = (sheet: Brief) => {
    setBrief(sheet);
    setBriefReady(true);
    setUnlocked(true);
    setMocking(isUsingMock());
  };

  return (
    <ThemeProvider mode="dark" darkTheme={thetaTheme}>
      <div className="dashboard-shell" data-openui-core={openUICoreRuntime}>
        <HeaderBar run={run} onStartRun={handleStartRun} />
        <PipelineTracker run={run} />
        <main className="content-grid" aria-label="Theta Desk scan output">
          <CandidateTable
            candidates={candidates}
            isVisible={tableReady}
            isLoading={Boolean(run && run.status === "running" && !tableReady)}
          />
          <BriefPanel brief={brief} isReady={briefReady} unlocked={unlocked} />
        </main>
        <ConsumerBotPanel onBriefUnlocked={handleBriefUnlocked} unlocked={unlocked} />
        <FooterBar run={run} usingMock={mocking} />
      </div>
    </ThemeProvider>
  );
}

function HeaderBar({
  run,
  onStartRun
}: {
  run: Run | null;
  onStartRun: () => Promise<void>;
}) {
  const clock = useEasternClock();
  const running = run?.status === "running";
  const mode = run?.mode ?? "replay";

  return (
    <header className="header-bar">
      <div className="brand-block">
        <div className="brand-mark">
          <RadioTower size={18} />
        </div>
        <div>
          <h1>THETA DESK</h1>
          <p>Autonomous Options Income Research</p>
        </div>
      </div>

      <div className="header-actions">
        <span className="clock-chip">
          <Clock3 size={15} />
          {clock}
        </span>
        <span className={`mode-chip ${mode === "live" ? "mode-live" : "mode-replay"}`}>
          {mode.toUpperCase()}
        </span>
        <Button
          className="run-scan-button"
          variant="primary"
          size="medium"
          iconLeft={<Play size={16} />}
          disabled={running}
          onClick={() => void onStartRun()}
        >
          {running ? "Scan Running" : "Run Daily Scan"}
        </Button>
      </div>
    </header>
  );
}

function PipelineTracker({ run }: { run: Run | null }) {
  const stages = run?.stages;
  const doneCount = stageDefs.filter(({ key }) => stages?.[key].status === "done").length;

  return (
    <Card className="pipeline-card panel-card" variant="card" width="full">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Daily Scan Pipeline</p>
          <h2>Ingest to publication in four observable stages</h2>
        </div>
        <div className="pipeline-meta">
          <span>{run?.universe_size ?? 10} tickers</span>
          <strong>{doneCount}/4 complete</strong>
        </div>
      </div>

      <div className="pipeline-track">
        {stageDefs.map((stage, index) => {
          const current = stages?.[stage.key] ?? ({ status: "pending" } satisfies Stage);
          const status = current.status;

          return (
            <Fragment key={stage.key}>
              <div className={`stage-tile stage-${status}`}>
                <div className="stage-orb" aria-hidden="true">
                  {status === "done" ? (
                    <Check size={18} />
                  ) : status === "failed" ? (
                    <TriangleAlert size={18} />
                  ) : status === "running" ? (
                    <Activity size={18} />
                  ) : (
                    <Clock3 size={18} />
                  )}
                </div>
                <div className="stage-copy">
                  <span>{stage.label}</span>
                  <small>{current.detail ?? (status === "running" ? "running..." : "queued")}</small>
                </div>
              </div>
              {index < stageDefs.length - 1 ? (
                <div
                  className={`stage-connector ${
                    status === "done" ? "connector-done" : status === "running" ? "connector-active" : ""
                  }`}
                  aria-hidden="true"
                />
              ) : null}
            </Fragment>
          );
        })}
      </div>
    </Card>
  );
}

function CandidateTable({
  candidates,
  isVisible,
  isLoading
}: {
  candidates: Candidate[];
  isVisible: boolean;
  isLoading: boolean;
}) {
  const [sort, setSort] = useState<SortState>({ key: "score", direction: "desc" });
  const sortedCandidates = useMemo(
    () => [...candidates].sort((a, b) => compareCandidates(a, b, sort)),
    [candidates, sort]
  );
  const chartData = sortedCandidates.slice(0, 8).map((candidate) => ({
    value: Number((candidate.premium_yield_ann * 100).toFixed(1)),
    label: candidate.ticker
  }));

  const toggleSort = (key: SortKey) => {
    setSort((current) => ({
      key,
      direction: current.key === key && current.direction === "desc" ? "asc" : "desc"
    }));
  };

  return (
    <Card className="candidate-card panel-card" variant="card" width="full">
      <CardHeader
        className="compact-card-header"
        icon={<ShieldCheck size={17} />}
        title="Candidate Screen"
        subtitle={isVisible ? `${sortedCandidates.length} contracts passed factor gates` : "Awaiting screen stage"}
      />

      <div className="candidate-table-shell">
        <div className="table-microbar">
          <span>Yield curve</span>
          <div className="yield-spark" aria-label="Annualized yield mini chart">
            <MiniBarChart
              data={chartData.length > 0 ? chartData : [0, 0, 0, 0]}
              size={74}
              radius={2}
              isAnimationActive
              barColor="#5ee787"
            />
          </div>
        </div>
        <Table className="candidate-table" containerClassName="candidate-table-wrap">
          <TableHeader>
            <TableRow>
              <SortableHead label="Ticker" sortKey="ticker" activeSort={sort} onSort={toggleSort} />
              <SortableHead label="Side" sortKey="side" activeSort={sort} onSort={toggleSort} />
              <SortableHead label="Strike" sortKey="strike" activeSort={sort} onSort={toggleSort} align="right" />
              <SortableHead label="Expiry" sortKey="expiry" activeSort={sort} onSort={toggleSort} />
              <SortableHead label="Premium" sortKey="bid" activeSort={sort} onSort={toggleSort} align="right" />
              <SortableHead
                label="Ann. Yield %"
                sortKey="premium_yield_ann"
                activeSort={sort}
                onSort={toggleSort}
                align="right"
              />
              <SortableHead label="IV %ile" sortKey="iv_pct" activeSort={sort} onSort={toggleSort} />
              <SortableHead label="OI" sortKey="open_interest" activeSort={sort} onSort={toggleSort} align="right" />
              <TableHead align="center">Earnings</TableHead>
              <SortableHead label="Score" sortKey="score" activeSort={sort} onSort={toggleSort} />
            </TableRow>
          </TableHeader>
          <TableBody>
            {!isVisible || sortedCandidates.length === 0 ? (
              <TableRow>
                <TableCell colSpan={10}>
                  <div className="empty-table-state">
                    {isLoading ? "Screening contracts..." : "Run the scan to reveal today's wheel sheet."}
                  </div>
                </TableCell>
              </TableRow>
            ) : (
              sortedCandidates.map((candidate, index) => (
                <TableRow
                  key={`${candidate.ticker}-${candidate.strike}-${candidate.expiry}`}
                  className={`candidate-row ${index === 0 ? "top-pick-row" : ""}`}
                  style={{ animationDelay: `${index * 70}ms` }}
                >
                  <TableCell>
                    <div className="ticker-cell">
                      <strong>{candidate.ticker}</strong>
                      {index === 0 ? <span>TOP PICK</span> : null}
                    </div>
                  </TableCell>
                  <TableCell>
                    <span className={`side-pill side-${candidate.side}`}>{candidate.side.toUpperCase()}</span>
                  </TableCell>
                  <TableCell align="right" className="number-cell">
                    ${candidate.strike.toFixed(0)}
                  </TableCell>
                  <TableCell className="number-cell">{formatExpiry(candidate.expiry)}</TableCell>
                  <TableCell align="right" className="number-cell">
                    {formatCurrency(candidate.bid)}
                  </TableCell>
                  <TableCell align="right" className="yield-cell">
                    {formatPercent(candidate.premium_yield_ann)}
                  </TableCell>
                  <TableCell>
                    <div className="mini-bar-cell">
                      <span className="mini-bar">
                        <span style={{ width: `${Math.round(candidate.iv_pct * 100)}%` }} />
                      </span>
                      <span className="number-cell">{Math.round(candidate.iv_pct * 100)}</span>
                    </div>
                  </TableCell>
                  <TableCell align="right" className="number-cell">
                    {candidate.open_interest.toLocaleString("en-US")}
                  </TableCell>
                  <TableCell align="center">
                    {candidate.earnings_ok ? (
                      <Check className="ok-icon" size={16} aria-label="Earnings clear" />
                    ) : (
                      <TriangleAlert className="warn-icon" size={16} aria-label="Earnings risk" />
                    )}
                  </TableCell>
                  <TableCell>
                    <div className="score-cell">
                      <span className="score-track">
                        <span style={{ width: `${Math.min(100, Math.max(0, candidate.score))}%` }} />
                      </span>
                      <strong>{candidate.score.toFixed(1)}</strong>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </Card>
  );
}

function SortableHead({
  label,
  sortKey,
  activeSort,
  onSort,
  align
}: {
  label: string;
  sortKey: SortKey;
  activeSort: SortState;
  onSort: (key: SortKey) => void;
  align?: "left" | "center" | "right";
}) {
  const active = activeSort.key === sortKey;

  return (
    <TableHead align={align}>
      <button
        type="button"
        className={`sort-button ${active ? "sort-active" : ""}`}
        onClick={() => onSort(sortKey)}
      >
        <span>{label}</span>
        <ArrowUpDown size={13} />
      </button>
    </TableHead>
  );
}

function BriefPanel({
  brief,
  isReady,
  unlocked
}: {
  brief: Brief | null;
  isReady: boolean;
  unlocked: boolean;
}) {
  const analyses = brief?.analyses ?? [];
  const topNames = brief?.candidates.slice(0, 5).map((candidate) => candidate.ticker) ?? [];

  return (
    <Card className="brief-card panel-card" variant="card" width="full">
      <CardHeader
        className="compact-card-header"
        icon={unlocked ? <UnlockKeyhole size={17} /> : <LockKeyhole size={17} />}
        title="Today's Brief"
        subtitle={brief?.status ?? (isReady ? "published" : "publishing")}
        actions={[
          <Button
            key="cited"
            className="secondary-action"
            variant="secondary"
            size="small"
            iconRight={<ExternalLink size={14} />}
            disabled={!brief?.cited_url}
            onClick={() => {
              if (brief?.cited_url) {
                window.open(brief.cited_url, "_blank", "noopener,noreferrer");
              }
            }}
          >
            View on cited.md
          </Button>
        ]}
      />

      <div className="brief-body">
        <div className="brief-title-block">
          <h2>{brief?.title ?? "Theta Desk Daily Wheel Sheet"}</h2>
          <p>{brief?.date ?? "2026-06-12"} - ${brief?.price_usd.toFixed(2) ?? "0.01"} x402 unlock</p>
        </div>

        <TextCallout
          className="summary-callout"
          variant="success"
          title="Free Summary"
          description={
            brief?.summary ??
            "The daily sheet will publish after Analyze and Publish complete. Candidate rows are available once Screen finishes."
          }
        />

        <Tabs className="brief-tabs" defaultValue="risk">
          <TabsList variant="title">
            <TabsTrigger value="risk" text="Risk Notes" />
            <TabsTrigger value="sheet" text="Sheet" />
          </TabsList>

          <div className="locked-region">
            <div className={`locked-content ${unlocked ? "is-unlocked" : "is-locked"}`}>
              <TabsContent value="risk">
                <div className="analysis-list">
                  {analyses.length === 0 ? (
                    <p className="muted-copy">Risk narratives publish at the final pipeline stage.</p>
                  ) : (
                    analyses.map((item) => (
                      <article className="analysis-item" key={item.ticker}>
                        <div className="analysis-heading">
                          <strong>{item.ticker}</strong>
                          <span>{item.citations.length} citations</span>
                        </div>
                        <p>{item.analysis}</p>
                      </article>
                    ))
                  )}
                </div>
              </TabsContent>

              <TabsContent value="sheet">
                <div className="sheet-summary">
                  {topNames.map((ticker) => (
                    <span key={ticker}>{ticker}</span>
                  ))}
                </div>
                <p className="sheet-copy">
                  The locked action sheet includes strikes, premiums, event-risk flags, and citation-backed
                  assignment notes for the top five trades.
                </p>
              </TabsContent>
            </div>

            {!unlocked ? (
              <div className="paywall-overlay" aria-label="Locked paywall overlay">
                <LockKeyhole size={22} />
                <strong>Unlock for $0.01 - x402</strong>
                <span>Waiting for an autonomous buyer</span>
              </div>
            ) : null}
          </div>
        </Tabs>
      </div>
    </Card>
  );
}

function ConsumerBotPanel({
  onBriefUnlocked,
  unlocked
}: {
  onBriefUnlocked: (sheet: Brief) => void;
  unlocked: boolean;
}) {
  const terminalLogRef = useRef<HTMLDivElement | null>(null);
  const [lines, setLines] = useState<string[]>([
    "standby: watching cited.md action sheets",
    "risk limits loaded: max collateral $25,000"
  ]);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    const log = terminalLogRef.current;
    if (!log) {
      return;
    }

    log.scrollTop = log.scrollHeight;
  }, [lines]);

  const typeLine = async (line: string) => {
    setLines((current) => [...current, ""]);

    for (let index = 0; index < line.length; index += 1) {
      await sleep(13);
      setLines((current) => {
        const next = [...current];
        next[next.length - 1] = line.slice(0, index + 1);
        return next;
      });
    }

    await sleep(240);
  };

  const runBot = async () => {
    if (running) {
      return;
    }

    setRunning(true);
    setLines([]);

    await typeLine("GET /briefs/today \u2192 402 Payment Required");
    const purchase = await buySheet();
    const shortTx = `${purchase.tx.slice(0, 6)}...${purchase.tx.slice(-4)}`;

    const scriptedLines = [
      `paying $0.01 via x402... tx ${shortTx} \u2713`,
      `sheet unlocked \u00b7 parsing ${purchase.sheet.candidates.length} candidates`,
      "risk check: NVDA $165P collateral $16,500 \u2264 limit \u2713",
      "queued paper order: SELL 1x NVDA 2026-07-17 165P @ 3.85"
    ];

    for (const line of scriptedLines) {
      await typeLine(line);
    }

    onBriefUnlocked(purchase.sheet);
    setRunning(false);
  };

  return (
    <Card className="bot-card panel-card" variant="card" width="full">
      <CardHeader
        className="compact-card-header bot-header"
        icon={<Bot size={17} />}
        title="WHEELER - autonomous trading bot"
        subtitle={unlocked ? "sheet unlocked" : "consumer agent idle"}
        actions={[
          <Button
            key="wake"
            className="wake-button"
            variant="primary"
            size="small"
            disabled={running}
            iconLeft={<Activity size={14} />}
            onClick={() => void runBot()}
          >
            {running ? "Wheeler Awake" : "Wake Wheeler"}
          </Button>
        ]}
      />
      <div className="terminal-log" aria-live="polite" ref={terminalLogRef}>
        {lines.map((line, index) => (
          <div className="terminal-line" key={`${line}-${index}`}>
            <span className="terminal-prompt">$</span>
            <span>{line}</span>
            {running && index === lines.length - 1 ? <span className="cursor" /> : null}
          </div>
        ))}
      </div>
    </Card>
  );
}

function FooterBar({ run, usingMock }: { run: Run | null; usingMock: boolean }) {
  return (
    <footer className="footer-bar">
      <div className="sponsor-strip">
        {sponsorChips.map((name) => (
          <Tag key={name} size="sm" variant="neutral" text={name} />
        ))}
      </div>
      <div className="footer-meta">
        <span>Data {formatTimestamp(run?.started_at)}</span>
        <span>Research, not financial advice</span>
        {usingMock ? <Tag size="sm" variant="warning" text="SIM" /> : null}
      </div>
    </footer>
  );
}

function sleep(ms: number) {
  return new Promise((resolve) => {
    setTimeout(resolve, ms);
  });
}
