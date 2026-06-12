# Devpost Submission Draft — Theta Desk

> Paste-ready copy for each Devpost field. Tone: quantified, confident, no fluff.

## Tagline (one-liner)

An autonomous options-research desk that does a trader's 2-hour daily homework
in 90 seconds — and sells it to other robots for $0.01 via x402.

## Inspiration

Wheel-strategy options traders do the same homework every single morning: scan
chains, compute annualized premium yield, check IV percentile, avoid earnings
dates, rank candidates. It's mechanical, quantitative, and perfect for an
agent. But the more interesting question was economic: if an agent produces
research, who buys it? Our answer — other agents. We wanted to build the
smallest complete specimen of the agent economy: one agent autonomously
produces a paid information product, another agent autonomously buys it.

## What it does

Theta Desk scans 10 US tickers every weekday, snapshots ~4,000 option
contracts into ClickHouse Cloud, and screens cash-secured-put candidates with
five factor gates — annualized premium yield, IV percentile vs 1-year history,
liquidity floor, earnings-date avoidance, cross-sectional score — all computed
in ClickHouse SQL. Claude then writes a cited risk brief for each top-5 pick,
and Senso publishes the action sheet to cited.md behind a $0.01 x402 paywall.
Finally, Wheeler — a consumer trading bot — hits the endpoint, receives HTTP
402, pays a penny in USDC, unlocks the sheet, and queues a simulated
cash-secured put. The whole loop runs itself on Render at 13:45 UTC daily.

## How we built it

A Python/FastAPI pipeline (`ingest → screen → analyze → publish`) with JSON
Schema contracts as the single source of truth between workstreams. Market
data flows in via yfinance and a PyAirbyte price pipeline; factor math lives
entirely in ClickHouse window functions rather than pandas. Claude
(claude-fable-5) writes the risk analyses grounded against a 12-document Senso
knowledge base, and the publisher pushes to cited.md — a format designed to be
cited by AI agents. The paywall implements the x402 flow natively in the API.
The dashboard is Next.js + OpenUI with a mock-first design: if any backend
fails, it silently switches to simulation mode so the demo can never crash.
Built solo in a harness-engineering setup: one Claude agent owned the backend
and contracts, Codex built the dashboard against mocks, a second Claude agent
handled deploy and docs — coordinated through a handoff file (PLAN.md).

## Challenges we ran into

Free market-data sources are hostile to autonomy — chains arrive with missing
IVs and stale quotes, so the screener had to be defensive at every gate.
Demo reliability shaped the architecture: we added a replay mode that re-runs
the day's real snapshot (no live network dependency on stage) and a dashboard
that degrades to mock data rather than ever showing an error. And coordinating
three AI workstreams in parallel without merge collisions required strict
territory rules: contracts owned by one agent, everyone else builds inside
them.

## Accomplishments that we're proud of

The loop is real end-to-end: real market data (4,015 contracts, 2,510 price
rows in ClickHouse), a real published artifact (live on cited.md), a real
402-then-pay flow, and a genuinely autonomous daily schedule on Render. Five
sponsor tools each do load-bearing work — none is decorative. Today's top pick
(AMD 495P, 110% annualized yield, 72nd IV percentile) came out of the live
pipeline, not a fixture file.

## What we learned

Factor math belongs in the warehouse — ClickHouse window functions made IV
percentile vs 1-year history a one-query problem. Grounded generation
(Senso) materially changes the quality bar for agent-written research: cited
claims read like analysis, not vibes. And x402's "402 + retry with payment
header" flow is shockingly little code — machine-priced content is closer than
it looks.

## What's next

Live x402 settlement on mainnet instead of simulated payment; a public
subscription feed where any trading bot can buy the daily sheet; expanding the
universe from 10 tickers to the full optionable S&P 500; covered-call (the
other half of the wheel) and assignment-tracking so the desk follows positions
through the full wheel cycle; and Langfuse tracing over the analyst calls.

## Built with

`python` · `fastapi` · `clickhouse` · `pyairbyte` · `anthropic-claude` ·
`senso` · `cited.md` · `x402` · `next.js` · `openui` · `render` · `yfinance`

## Links

- Dashboard: https://thetadesk-agent.onrender.com
- API: https://thetadesk-api-jpll.onrender.com/healthz
- Published brief: https://cited.md/article/47e2fb3c-7ff0-4f1c-a3a2-c40673ee6e33
- Repo: https://github.com/vup903/ThetaDesk-Agent
