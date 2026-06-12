# Theta Desk — 自治選擇權收益研究台

> An autonomous options-income research desk. It scans US options chains 24/7,
> screens wheel-strategy candidates with quantitative factors, has Claude write
> cited risk analyses, publishes a daily action sheet to cited.md behind an
> x402 micro-paywall — and trading bots pay to read it.

**Hackathon:** Context Engineering Challenge (Harness Engineering Hackathon)
**Mode:** 精簡版 (P0 golden path + P1 if time allows) · Solo dev + Claude Code + Codex Max

---

## 1. System Overview

```
┌─ DATA ────────────────────────────────────────────────────────────┐
│ yfinance (options chains, prices, earnings dates)                 │
│   ├─ PyAirbyte: Yahoo-Finance price source ──► ClickHouse Cloud  │  [Airbyte]
│   └─ chain_fetcher.py (options snapshots)  ──► ClickHouse Cloud  │  [ClickHouse]
└───────────────────────────────────────────────────────────────────┘
                                │
┌─ BRAIN (services/pipeline, Python + FastAPI) ─────────────────────┐
│ 1. screener.sql  — ClickHouse factor queries:                     │
│      annualized premium yield · IV percentile · delta band ·      │
│      OI/volume liquidity floor · earnings-date avoidance          │
│ 2. analyst.py    — Claude writes per-ticker risk brief w/ cites   │  [Claude]
│ 3. publisher.py  — Senso ingest+generate → cited.md + x402 wall   │  [Senso/cited.md/x402]
│ 4. scheduler     — daily cron + REPLAY MODE (demo fuse)           │
└───────────────────────────────────────────────────────────────────┘
                                │ REST (JSON contracts in /contracts)
┌─ FACE (apps/dashboard, Next.js + OpenUI) ─────────────────────────┐
│ live scan animation · today's action sheet · publish status ·     │  [OpenUI]
│ P1: consumer-bot panel (pays x402, queues simulated trade)        │
└───────────────────────────────────────────────────────────────────┘
                 all deployed on Render (web service + cron)           [Render]
```

**Sponsor count:** Airbyte, ClickHouse, Senso(+cited.md+x402), OpenUI, Render = **5** (P1: +TrueFoundry gateway/Langfuse = 6).

## 2. Repo Layout (monorepo)

```
/contracts/            JSON Schemas — single source of truth, Claude-owned
   candidate.schema.json   brief.schema.json   run.schema.json
/services/pipeline/    Python 3.11 + FastAPI
   ingest/   (chain_fetcher.py, airbyte_prices.py)
   screener/ (factors.sql, screener.py)
   analyst/  (analyst.py — Claude API)
   publish/  (senso_client.py, publisher.py)
   api.py    (REST: see §4)   replay/ (frozen real snapshots)
/apps/dashboard/       Next.js 14 + @openuidev/react-ui
/docs/                 demo script, pitch notes
```

## 3. ClickHouse Data Model

```sql
prices        (ticker, ts, open, high, low, close, volume)            -- via PyAirbyte
option_chain  (snapshot_ts, ticker, expiry, strike, side, bid, ask,
               iv, oi, volume, spot)                                  -- via chain_fetcher
candidates    (run_id, ticker, expiry, strike, premium_yield_ann,
               iv_pct, delta_est, earnings_ok, score)                 -- screener output
runs          (run_id, started_at, mode live|replay, status, brief_url)
```

Factor math lives in ClickHouse SQL (not Python) — that's the "real use" story
for the ClickHouse prize: window functions for IV percentile vs 1y history,
cross-sectional ranking for score.

## 4. Internal API (pipeline → dashboard)

| Endpoint | Purpose |
|---|---|
| `POST /runs?mode=live\|replay` | trigger a full scan→analyze→publish run |
| `GET  /runs/{id}` | run status (per-stage, drives dashboard animation) |
| `GET  /candidates/today` | screened action sheet |
| `GET  /briefs/latest` | published brief metadata + cited.md URL |
| `POST /consumer/buy` (P1) | consumer bot pays x402, returns unlocked sheet |

## 5. Feature Triage

**P0 (golden path)**
1. ✅ Data spike: yfinance chains/earnings/history verified (2026-06-12)
2. chain_fetcher + PyAirbyte prices → ClickHouse
3. Screener SQL (yield, IV pct, liquidity, earnings filter, score)
4. Analyst: Claude risk brief per top-5 candidate, with citations
5. Publisher: Senso → cited.md + x402 paywall
6. OpenUI dashboard + Render deploy
7. Replay mode (frozen real data, compressed timeline — demo fuse)

**P1** — consumer trading bot (pays x402 live on stage) · TrueFoundry gateway + Langfuse tracing
**P2** — Pioneer news classification · backtest page · Composio Discord alerts

## 6. Build Order & AI Dispatch

| # | Module | Owner | Est |
|---|---|---|---|
| 1 | contracts/ + repo scaffold | Claude | 1h |
| 2 | ClickHouse Cloud setup + ingest (fetcher + PyAirbyte) | Claude | 3h |
| 3 | Screener SQL + /candidates API | Claude | 3h |
| 4 | Replay snapshot generator | **Codex** (spec by Claude) | 2h |
| 5 | Analyst (Claude API) | Claude | 2h |
| 6 | Senso publisher → cited.md + x402 | Claude | 3h |
| 7 | OpenUI dashboard shell + components | **Codex** (spec by Claude) | 4h |
| 8 | Dashboard ↔ API wiring + polish | Claude | 2h |
| 9 | Render deploy (web + cron) | Claude | 2h |
| 10 | P1 consumer bot | Claude | 3h |
| 11 | Demo script + fallback drills | Claude | 2h |

Rule: cross-module contracts live in `/contracts` and are edited only by Claude;
Codex builds inside them against mock data, so the two lines never collide.

## 7. Accounts / Keys Needed (user action)

- [ ] ClickHouse Cloud trial (free credits) → host/user/password
- [ ] Senso API key (docs.senso.ai — $100 free credits)
- [ ] Anthropic API key (or TrueFoundry gateway key, P1)
- [ ] Render account (GitHub repo connect)
- [ ] GitHub public repo (submission requirement)

## 8. Demo Beat Sheet (3 min, draft)

1. **0:00** Hook: "選擇權研究員每天花 2 小時做的功課,這個 agent 用 90 秒做完,而且只賣 1 美分。"
2. **0:20** Dashboard: live scan kicks off — chains stream in, ClickHouse factor
   ranking animates, top-5 sheet materializes.
3. **1:20** Claude's cited risk brief appears → one click shows it live on
   cited.md behind the x402 paywall.
4. **2:00** (P1 高潮) Consumer trading bot wakes up, **pays $0.01 via x402 on
   stage**, unlocks the sheet, queues a simulated cash-secured put.
5. **2:40** Close: 5 sponsor tools, fully autonomous daily loop on Render,
   "this is what the agent economy looks like."
