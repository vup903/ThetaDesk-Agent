# 🛞 Theta Desk — Autonomous Options-Income Research Desk

An autonomous agent that does the daily homework of an options wheel-strategy
trader — and sells it for a penny.

Every day it scans US options chains, screens cash-secured-put candidates with
quantitative factors computed in ClickHouse, has Claude write cited risk
analyses, and publishes the action sheet to **cited.md** behind an **x402**
micro-paywall — where humans *and other trading bots* pay $0.01 to unlock it.

> Built for the Context Engineering Challenge (Harness Engineering Hackathon).

## Sponsor tools used

| Tool | Role |
|---|---|
| **Airbyte (PyAirbyte)** | price-history pipelines into the warehouse |
| **ClickHouse** | options time-series storage + factor screening SQL |
| **Senso / cited.md** | grounded generation + agent-citable publishing |
| **x402** | per-fetch micro-paywall on the published brief |
| **OpenUI (thesys)** | generative dashboard UI |
| **Render** | deployment (web service + daily cron) |

## Layout

```
contracts/           JSON Schema contracts (single source of truth)
services/pipeline/   Python: ingest → screen → analyze → publish (FastAPI)
apps/dashboard/      Next.js + OpenUI dashboard
docs/                demo script & pitch notes
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design.

*Not financial advice. Demo uses delayed/free market data.*
